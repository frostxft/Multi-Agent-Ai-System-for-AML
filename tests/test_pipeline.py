import copy
import json
import sqlite3
from dataclasses import replace
import numpy as np
import pandas as pd
import pytest
import torch
from cryptography.fernet import Fernet
from fastapi.testclient import TestClient
from aml.agents import ComplianceAgent, NarrativeAgent
from aml.api import create_app
from aml.data import load_graph, synthetic_fixture, describe
from aml.model import load_model
from aml.schemas import Review, Narrative
from aml.store import Store, Conflict
from aml.retrieval import retrieve

def test_ingestion_and_temporal_split(trained):
    g, _ = trained
    assert g.kind == 'synthetic_test'
    assert g.features.shape == (180, 165)
    assert g.edges.shape == (2, 225)
    masks = [g.mask(s) for s in ['train', 'validation', 'test']]
    assert not any(np.any(a & b) for i,a in enumerate(masks) for b in masks[i+1:])
    assert all(np.all(g.labels[m] >= 0) for m in masks)
    assert max(g.times[masks[0]]) < min(g.times[masks[1]])
    assert max(g.times[masks[1]]) < min(g.times[masks[2]])

@pytest.mark.parametrize('mutation', ['unknown_edge', 'duplicate_node', 'missing_label', 'nonfinite', 'bad_time'])
def test_malformed_data_rejected(tmp_path, mutation):
    synthetic_fixture(tmp_path)
    if mutation == 'unknown_edge':
        p = tmp_path / 'elliptic_txs_edgelist.csv'
        d = pd.read_csv(p); d.iloc[0,0] = 999999; d.to_csv(p,index=False)
    elif mutation == 'missing_label':
        p = tmp_path / 'elliptic_txs_classes.csv'
        d = pd.read_csv(p); d.iloc[1:].to_csv(p,index=False)
    else:
        p = tmp_path / 'elliptic_txs_features.csv'
        d = pd.read_csv(p,header=None)
        if mutation == 'duplicate_node': d.iloc[1,0] = d.iloc[0,0]
        elif mutation == 'nonfinite': d.iloc[0,4] = float('inf')
        else: d.iloc[0,1] = 50
        d.to_csv(p,index=False,header=False)
    with pytest.raises(ValueError): load_graph(tmp_path)

def test_model_uses_topology_and_train_only_scaling(trained):
    g,s = trained
    m,x,c,_ = load_model(g,s.artifact_dir)
    assert np.allclose(c['mean'].numpy(),g.features[g.times<=29,:93].mean(0))
    with torch.no_grad():
        original=m(x,torch.tensor(g.edges)).numpy()
        isolated=m(x,torch.empty((2,0),dtype=torch.long)).numpy()
    assert np.isfinite(original).all()
    assert not np.allclose(original,isolated)

def test_model_rejects_different_data(trained):
    g,s=trained
    changed=copy.copy(g);changed.fingerprint='different'
    with pytest.raises(ValueError,match='fingerprint'):load_model(changed,s.artifact_dir)

def test_full_lifecycle_persists_review_and_audit(pipeline,case):
    o=case['outputs']
    assert list(o)==list(pipeline.stages)
    assert o['detection']['data_kind']=='synthetic_test'
    assert o['detection']['explanation']['status']=='available'
    assert o['detection']['explanation']['edges']
    shap=o['detection']['explanation']['baseline_shap']
    assert abs(shap['sum']-shap['logit'])<1e-4
    assert o['investigation']['retrieval']
    assert o['narrative']['status']=='DRAFT'
    assert o['compliance']['status']=='review_ready'
    assert o['compliance']['review_required']
    assert o['compliance']['readiness']['autonomy']=='human_only'
    evidence={e['id']:e for e in o['investigation']['evidence']}
    for claims in o['narrative']['sections'].values():
        for claim in claims:
            assert claim['text']==evidence[claim['evidence_ids'][0]]['fact']
    result=pipeline.review(case['id'],Review(decision='approve',notes='SYNTHETIC TEST decision only.',expected_revision=case['revision']),'synthetic-test-reviewer')
    restored=Store(pipeline.settings.db_path).get(case['id'])
    assert restored==result and restored['status']=='approved'
    audit=pipeline.store.audit(case['id'])
    assert audit['valid']
    assert audit['events'][-1]['action']=='approve'
    assert {e['stage'] for e in audit['events']}>=set(pipeline.stages)
    assert all(v>=0 for v in result['timings'].values())

@pytest.mark.parametrize('decision,status',[('reject','rejected'),('request_changes','changes_requested')])
def test_other_dispositions(pipeline,case,decision,status):
    c=pipeline.review(case['id'],Review(decision=decision,notes='SYNTHETIC review rationale',expected_revision=case['revision']),'test-reviewer')
    assert c['status']==status and pipeline.store.audit(c['id'])['valid']

def test_unsupported_narrative_blocks_approval_and_revision_repairs(pipeline,case):
    original=copy.deepcopy(case['outputs']['narrative'])
    edited=copy.deepcopy(original)
    edited['sections']['Activity and chronology'][0]['text']='Alice transferred USD 100000 to a sanctioned entity.'
    c=pipeline.revise(case['id'],Narrative.model_validate(edited),case['revision'],'test-analyst')
    assert c['outputs']['compliance']['unsupported_claims']
    with pytest.raises(Conflict,match='Approval blocked'):
        pipeline.review(c['id'],Review(decision='approve',notes='Attempt unsupported approval',expected_revision=c['revision']),'test-reviewer')
    fixed=pipeline.revise(c['id'],Narrative.model_validate(original),c['revision'],'test-analyst')
    assert fixed['outputs']['compliance']['status']=='review_ready'

def test_untrusted_synthesis_status_cannot_bypass_validator(pipeline,case):
    o=copy.deepcopy(case['outputs'])
    o['narrative']['synthesis']='This person is definitely a criminal.'
    o['narrative']['synthesis_status']='validated_constrained_extraction'
    v=pipeline.compliance.run(o['detection'],o['investigation'],o['narrative'])
    assert v['status']=='issues_found'

def test_missing_evidence_and_model_contradiction(pipeline,case):
    o=copy.deepcopy(case['outputs'])
    o['narrative']['sections']['Activity and chronology'][0]['evidence_ids']=['NONEXISTENT']
    o['detection']['score']=.123456
    v=pipeline.compliance.run(o['detection'],o['investigation'],o['narrative'])
    assert any('Missing evidence' in x for x in v['issues'])
    assert any('model mismatch' in x for x in v['issues'])

def test_failure_preserved_and_retry_resumes(pipeline,monkeypatch):
    original=pipeline.narrative.run
    def fail(_):raise RuntimeError('Injected synthetic failure')
    monkeypatch.setattr(pipeline.narrative,'run',fail)
    c=pipeline.create('3500','test-actor')
    assert c['status']=='failed' and c['error']['stage']=='narrative'
    assert 'investigation' in c['outputs'] and 'narrative' not in c['outputs']
    detection=copy.deepcopy(c['outputs']['detection'])
    monkeypatch.setattr(pipeline.narrative,'run',original)
    resumed=pipeline.run(c['id'])
    assert resumed['status']=='awaiting_review'
    assert resumed['outputs']['detection']==detection
    assert sum(e['stage']=='detection' and e['action']=='completed' for e in pipeline.store.audit(c['id'])['events'])==1

def test_stale_review_rejected(pipeline,case):
    req=Review(decision='request_changes',notes='SYNTHETIC review',expected_revision=case['revision'])
    pipeline.review(case['id'],req,'test-reviewer')
    with pytest.raises(Conflict):pipeline.review(case['id'],req,'test-reviewer')

def test_audit_detects_snapshot_and_current_tamper(pipeline,case):
    assert pipeline.store.audit(case['id'])['valid']
    altered=copy.deepcopy(case);altered['transaction_id']='tampered'
    with pipeline.store.connect() as db:
        db.execute('UPDATE cases SET payload=? WHERE id=?',(pipeline.store.encode(altered),case['id']))
    assert not pipeline.store.audit(case['id'])['valid']
    with pytest.raises(Conflict,match='integrity'):
        pipeline.review(case['id'],Review(decision='approve',notes='Tampered review attempt',expected_revision=case['revision']),'test-reviewer')

def test_encrypted_persistence(tmp_path):
    key=Fernet.generate_key().decode()
    path=tmp_path/'encrypted.db'
    store=Store(path,key)
    c={'id':'encrypted-case','status':'created','private_fact':'SENSITIVE-TEST-MARKER'}
    store.save(c,'intake','test','created',0)
    assert b'SENSITIVE-TEST-MARKER' not in path.read_bytes()
    assert Store(path,key).get(c['id'])['private_fact']=='SENSITIVE-TEST-MARKER'
    assert store.audit(c['id'])['valid']

def test_retrieval_scoped_and_deterministic(case):
    ev=case['outputs']['investigation']['evidence']
    a=retrieve(ev,'sanctions reference screening',k=1)
    assert a==retrieve(ev,'sanctions reference screening',k=1)
    assert 'sanctions' in next(e for e in ev if e['id']==a[0]['evidence_id'])['fact'].lower()
    with pytest.raises(ValueError):retrieve([],'query')

def test_api_real_case_and_rbac(pipeline):
    settings=replace(pipeline.settings,reviewer_token='test-reviewer-secret',analyst_token='test-analyst-secret')
    client=TestClient(create_app(settings,pipeline))
    analyst={'Authorization':'Bearer test-analyst-secret'}
    reviewer={'Authorization':'Bearer test-reviewer-secret'}
    assert client.get('/api/cases').status_code==401
    assert client.get('/').status_code==200
    assert client.get('/assets/app.js').status_code==200
    assert client.post('/api/cases',headers={**analyst,'Origin':'https://untrusted.invalid'},json={'transaction_id':'3500'}).status_code==403
    created=client.post('/api/cases',headers=analyst,json={'transaction_id':'3500'})
    assert created.status_code==201,created.text
    c=created.json();assert c['status']=='awaiting_review'
    body={'decision':'approve','notes':'SYNTHETIC API TEST decision','expected_revision':c['revision']}
    assert client.post(f'/api/cases/{c["id"]}/review',headers=analyst,json=body).status_code==403
    approved=client.post(f'/api/cases/{c["id"]}/review',headers=reviewer,json=body)
    assert approved.status_code==200 and approved.json()['status']=='approved'
    assert client.get(f'/api/cases/{c["id"]}/audit',headers=analyst).json()['valid']
    assert client.post(f'/api/cases/{c["id"]}/review',headers=reviewer,json=body).status_code==409
    assert client.post('/api/cases',headers=analyst,json={'transaction_id':'missing'}).status_code==422
    assert client.get('/api/cases/missing',headers=analyst).status_code==404

def test_local_model_missing_is_failure_not_fallback(case,tmp_path):
    from aml.config import Settings
    agent=NarrativeAgent(Settings(llm_provider='local',llm_model=str(tmp_path/'missing')))
    with pytest.raises(Exception):agent.run(case['outputs']['investigation'])

def test_section_heading_cannot_introduce_unsupported_claim(pipeline,case):
    o=copy.deepcopy(case['outputs'])
    n=o['narrative']
    n['sections']['Alice is a criminal']=n['sections'].pop('Activity and chronology')
    assert pipeline.compliance.run(o['detection'],o['investigation'],n)['status']=='issues_found'

def test_loopback_demo_rejects_dns_rebinding_host(pipeline):
    client=TestClient(create_app(pipeline.settings,pipeline))
    assert client.get('/api/cases',headers={'Host':'attacker.example'}).status_code==400

def test_role_tokens_must_be_distinct(pipeline):
    with pytest.raises(ValueError,match='distinct'):
        replace(pipeline.settings,reviewer_token='same',analyst_token='same')
