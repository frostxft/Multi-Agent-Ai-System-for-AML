import copy
import numpy as np
import pytest
from pydantic import ValidationError
from aml.demo import select_transactions
from aml.schemas import Review, Narrative
from aml.store import Conflict
from scripts.evaluate_seeds import summarize


def test_declared_dataset_checksum_is_enforced(tmp_path):
    import json
    from aml.data import synthetic_fixture, load_graph, FILES
    synthetic_fixture(tmp_path)
    (tmp_path / 'manifest.json').write_text(json.dumps({'kind': 'synthetic_test', 'files': {FILES[0]: {'sha256': 'wrong'}}}))
    with pytest.raises(ValueError, match='hash mismatch'):
        load_graph(tmp_path)


def test_seed_summary_uses_sample_sd():
    reports = [{'seed': seed, **{model: {'test': {metric: v for metric in ('precision', 'recall', 'average_precision')}}
                               for model in ('gat', 'baseline')}} for seed, v in [(17, .2), (29, .4), (43, .6)]]
    summary = summarize(reports)['gat']['precision']
    assert summary['mean'] == pytest.approx(.4)
    assert summary['sample_standard_deviation'] == pytest.approx(.2)
    with pytest.raises(ValueError):
        summarize([reports[0], reports[0]])


def test_demo_selection_is_label_independent_and_fails_shortfall(trained):
    graph, _ = trained
    scores = np.full(len(graph.ids), .9)
    targets = select_transactions(graph, scores, .5, 4)
    changed = copy.deepcopy(graph)
    changed.labels[:] = -1
    assert targets == select_transactions(changed, scores, .5, 4)
    with pytest.raises(ValueError, match='Only 0'):
        select_transactions(graph, scores, .99, 4)
    with pytest.raises(ValueError):
        select_transactions(graph, scores, .5, 0)


def test_source_tampering_detected_even_when_narrative_matches(pipeline, case):
    o = copy.deepcopy(case['outputs'])
    e = next(e for e in o['investigation']['evidence'] if e['kind'] == 'synthetic_test')
    previous = e['fact']
    e['fact'] = 'An invented source fact copied consistently into the narrative.'
    for claims in o['narrative']['sections'].values():
        for claim in claims:
            if claim['text'] == previous:
                claim['text'] = e['fact']
    result = pipeline.compliance.run(o['detection'], o['investigation'], o['narrative'])
    assert result['source_validation']['issues']
    assert not result['approval_eligible']
    assert not result['readiness']['checks']['evidence_traceable']


def test_claim_trace_and_summary_citations_recomputed(pipeline, case):
    o = copy.deepcopy(case['outputs'])
    facts = o['investigation']['evidence'][:2]
    o['narrative']['synthesis'] = ' '.join(e['fact'] for e in facts)
    o['narrative']['retrieved_evidence_ids'] += [e['id'] for e in facts]
    result = pipeline.compliance.run(o['detection'], o['investigation'], o['narrative'])
    assert result['synthesis_evidence_ids'] == [e['id'] for e in facts]
    assert all(c['status'] == 'grounded' and c['sources'] for c in result['claim_validation'])
    assert result['readiness']['label'] == 'Internal Prototype Readiness Score'
    assert sum(f['weight'] for f in result['readiness']['factors']) == 6


def test_whitespace_notes_rejected():
    with pytest.raises(ValidationError):
        Review(decision='approve', notes='     ', expected_revision=1)


def test_removing_scope_evidence_and_its_claim_does_not_bypass_review(pipeline, case):
    o = copy.deepcopy(case['outputs'])
    evidence = o['investigation']['evidence']
    removed = next(e for e in evidence if 'KYC are unavailable' in e['fact'])
    evidence.remove(removed)
    n = o['narrative']
    n['retrieved_evidence_ids'].remove(removed['id'])
    for title in n['sections']:
        n['sections'][title] = [c for c in n['sections'][title] if removed['id'] not in c['evidence_ids']]
    result = pipeline.compliance.run(o['detection'], o['investigation'], n)
    assert 'Missing mandatory dataset-scope evidence' in result['issues']


def test_final_states_reject_revision_and_retry(pipeline, case):
    approved = pipeline.review(case['id'], Review(decision='approve', notes='SYNTHETIC TEST ONLY', expected_revision=case['revision']), 'test')
    with pytest.raises(Conflict):
        pipeline.revise(approved['id'], Narrative.model_validate(approved['outputs']['narrative']), approved['revision'], 'test')
    with pytest.raises(Conflict):
        pipeline.run(approved['id'])


def test_security_headers(pipeline):
    from fastapi.testclient import TestClient
    from aml.api import create_app
    with TestClient(create_app(pipeline.settings, pipeline)) as client:
        for path in ('/', '/assets/app.js', '/api/cases'):
            response = client.get(path)
            assert response.headers['cache-control'] == 'no-store'
            assert "script-src 'self'" in response.headers['content-security-policy']
            assert response.headers['x-content-type-options'] == 'nosniff'


def test_overview_rejects_study_for_another_dataset(pipeline, tmp_path):
    import json
    from dataclasses import replace
    from fastapi.testclient import TestClient
    from aml.api import create_app
    settings = replace(pipeline.settings, artifact_dir=tmp_path)
    (tmp_path / 'multiseed_evaluation.json').write_text(json.dumps({'dataset_fingerprint': 'different'}))
    with TestClient(create_app(settings, pipeline)) as client:
        assert client.get('/api/overview').status_code == 422
