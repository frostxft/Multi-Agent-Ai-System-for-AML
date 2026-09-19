import copy
import json
from dataclasses import replace
from pathlib import Path
import numpy as np
import pytest
from fastapi.testclient import TestClient
from aml.api import create_app
from aml.diagnostics import threshold_table, operating_points, reliability, calibration_experiment
from aml.structure import summarize_network
from aml.reference import SyntheticSnapshotProvider, reference_context
from aml.retrieval import retrieve
from aml.schemas import Narrative
from aml.pipeline import Pipeline
from aml.store import Conflict


def test_threshold_counts_and_calibration_inputs():
    y, p = np.array([0,0,1,1]), np.array([.1,.6,.7,.9])
    rows = threshold_table(y,p)
    assert len(rows) == 91
    row = min(rows,key=lambda r:abs(r['threshold']-.5))
    assert (row['tp'],row['fp'],row['fn'],row['tn']) == (2,1,0,1)
    assert all(a['recall'] >= b['recall'] for a,b in zip(rows,rows[1:]))
    assert operating_points(rows)['recall_emphasis']['f2'] == max(r['f2'] for r in rows)
    r = reliability(y,p)
    assert sum(b['count'] for b in r['bins']) == 4
    with pytest.raises(ValueError): calibration_experiment(y,p,[30,31,35,49])
    with pytest.raises(ValueError): threshold_table(y,[.1,.2,.3,float('nan')])


def test_temporal_calibration_disjoint_fit_and_diagnostic_status():
    y=np.array([0,1,0,1,0,1,0,1]); p=np.array([.1,.8,.3,.9,.2,.7,.4,.6])
    r=calibration_experiment(y,p,[30,30,32,32,33,33,34,34])
    assert r['fit_count']==4 and r['assessment_count']==4 and not r['deployed']
    assert r['raw']['n']==4


def test_structure_counts_cycles_and_time_are_real():
    graph={'nodes':[{'id':str(i),'target':i==2,'time_step':44,'model_score':v} for i,v in enumerate([.2,.9,.8])],
           'edges':[{'source':'0','target':'1'},{'source':'1','target':'2'}]}
    s=summarize_network(graph,.7)
    assert s['directed_density']==pytest.approx(2/6)
    assert s['above_threshold_nodes']==2 and s['weak_components']==1 and not s['has_directed_cycle']
    assert s['node_metrics'][0]['distance_to_target']==2
    assert s['timeline']==[{'time_step':44,'transactions':3}]
    graph['edges'].append({'source':'2','target':'0'})
    assert summarize_network(graph,.7)['has_directed_cycle']


def test_derived_findings_are_grounded_and_tampering_rejected(pipeline,case):
    o=copy.deepcopy(case['outputs'])
    assert o['investigation']['network_summary']['scored_nodes'] == len(o['detection']['subgraph']['nodes'])
    assert len(o['investigation']['findings'])==4
    ev=next(e for e in o['investigation']['evidence'] if e['source']=='StructureAnalyzer')
    ev['fact']='Invented structural concentration'
    assert any('structural evidence mismatch' in i for i in pipeline.compliance.run(o['detection'],o['investigation'],o['narrative'])['issues'])


def test_synthetic_reference_boundary(trained,tmp_path):
    graph,settings=trained
    path=Path('tests/fixtures/reference_snapshot.json')
    provider=SyntheticSnapshotProvider(path)
    synthetic=reference_context('synthetic_test','3500',provider)
    assert synthetic['kyc']['status']=='synthetic_profile'
    assert synthetic['sanctions']['status']=='synthetic_match'
    assert 'SYNTHETIC' in synthetic['kyc']['label']
    assert reference_context('benchmark','3500',provider)['kyc']['status']=='unavailable'
    assert reference_context('synthetic_test','no-link',provider)['kyc']['status']=='unavailable'
    benchmark=copy.copy(graph); benchmark.kind='benchmark'
    with pytest.raises(ValueError,match='prohibited'):
        Pipeline(benchmark,replace(settings,reference_fixture=str(path),db_path=tmp_path/'ref.db'))
    p=Pipeline(graph,replace(settings,reference_fixture=str(path),db_path=tmp_path/'synthetic.db'))
    c=p.create('3500','synthetic-test')
    assert c['status']=='awaiting_review'
    assert c['outputs']['investigation']['kyc']['status']=='synthetic_profile'
    assert not any('Demo Entity' in e['fact'] for e in c['outputs']['investigation']['evidence'])


def test_retrieval_scoping_filters_and_deduplication(case):
    evidence=case['outputs']['investigation']['evidence']
    e=evidence[0]; duplicate={**e,'id':'DUPLICATE-FACT'}
    selected=retrieve(evidence+[duplicate],'Transaction',source_records={e['source_record']},k=100)
    assert 'DUPLICATE-FACT' not in [r['evidence_id'] for r in selected]
    assert all(r['source_record']==e['source_record'] for r in selected)
    assert retrieve(evidence,'zzzzzznonexistentterm')==[]
    with pytest.raises(ValueError,match='one requested case'):
        retrieve(evidence+[{**e,'case_id':'another-case','id':'X'}],'Transaction')


def test_revision_provenance_and_history_are_server_owned(pipeline,case):
    n=copy.deepcopy(case['outputs']['narrative'])
    n['provider']='fake-provider';n['generation_metadata']={'fabricated':True};n['synthesis_status']='forged_validated'
    revised=pipeline.revise(case['id'],Narrative.model_validate(n),case['revision'],'synthetic-analyst')
    rn=revised['outputs']['narrative']
    assert rn['provider']==case['outputs']['narrative']['provider']
    assert rn['synthesis_status']==case['outputs']['narrative']['synthesis_status']
    assert rn['generation_metadata']==case['outputs']['narrative']['generation_metadata']
    assert rn['revision_metadata']['actor']=='synthetic-analyst'
    history=pipeline.store.narrative_history(case['id'])
    assert len(history)==2 and history[0]['narrative']==case['outputs']['narrative']
    with pytest.raises(Conflict): pipeline.revise(case['id'],Narrative.model_validate(n),case['revision'],'stale')


def test_status_source_history_authorization_and_secret_exclusion(pipeline,case):
    settings=replace(pipeline.settings,reviewer_token='REVIEW-SECRET',analyst_token='ANALYST-SECRET')
    client=TestClient(create_app(settings,pipeline));headers={'Authorization':'Bearer ANALYST-SECRET'}
    for endpoint in ['/api/status','/api/model',f'/api/cases/{case["id"]}/narrative-history',f'/api/cases/{case["id"]}/transactions/3500']:
        assert client.get(endpoint).status_code==401
        response=client.get(endpoint,headers=headers)
        assert response.status_code==200,response.text
        assert 'REVIEW-SECRET' not in response.text and 'ANALYST-SECRET' not in response.text
    assert client.get('/api/health',headers={'Authorization':'ANALYST-SECRET'}).status_code==401
    source=client.get(f'/api/cases/{case["id"]}/transactions/3500',headers=headers).json()
    assert len(source['attributes'])==165 and 'labels' not in source
    assert client.get(f'/api/cases/{case["id"]}/transactions/100',headers=headers).status_code==404
    status=client.get('/api/status',headers=headers).json()
    assert status['dataset_loaded'] and status['model_loaded']


def test_threshold_override_recorded_without_changing_checkpoint(trained,tmp_path):
    graph,s=trained
    p=Pipeline(graph,replace(s,db_path=tmp_path/'cases.db',detection_threshold=.99))
    c=p.create('3500','synthetic-test');d=c['outputs']['detection']
    assert d['threshold']==.99 and not d['flagged']
    assert d['threshold_policy']['source']=='explicit_configuration_override'
    with pytest.raises(ValueError): replace(s,detection_threshold=float('nan'))
    with pytest.raises(ValueError): replace(s,ollama_url='http://user:secret@localhost:11434')


def test_validation_diagnostics_do_not_read_test_targets(trained):
    from scripts.analyze_detection import analyze
    graph,settings=trained
    original=analyze(graph,settings.artifact_dir)
    changed=copy.deepcopy(graph)
    changed.labels[changed.times>=35]=-1
    changed.features[changed.times>=35]*=-100
    result=analyze(changed,settings.artifact_dir)
    assert result['models']==original['models']
    assert result['topology_intervention']==original['topology_intervention']
