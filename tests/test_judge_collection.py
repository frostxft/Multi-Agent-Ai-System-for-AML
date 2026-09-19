import copy
import json
from dataclasses import replace
from fastapi.testclient import TestClient
from aml.api import create_app
from aml.collection import demo_collection


def manifest_for(pipeline, case):
    return {'cases': [{'id': case['id']}], 'canonical_case_id': case['id'],
            'transactions': [case['transaction_id']], 'canonical_transaction': case['transaction_id'],
            'dataset_fingerprint': pipeline.graph.fingerprint, 'model_id': pipeline.detector.model_id,
            'selection_rule': 'Explicit synthetic fixture for collection tests; no labels used.'}


def test_collection_is_read_only_and_rejects_wrong_provenance(pipeline, case, tmp_path):
    # Redirect only the manifest lookup, leaving shared trained model artifacts untouched.
    pipeline.settings = replace(pipeline.settings, artifact_dir=tmp_path)
    path = tmp_path / 'demo_manifest.json'
    assert demo_collection(pipeline)['status'] == 'unavailable'
    before = copy.deepcopy(pipeline.store.get(case['id']))
    manifest = manifest_for(pipeline, case)
    path.write_text(json.dumps(manifest))
    result = demo_collection(pipeline)
    assert result['case_ids'] == [case['id']] and result['canonical_case_id'] == case['id']
    assert pipeline.store.get(case['id']) == before
    for key, value in [('dataset_fingerprint', 'wrong'), ('model_id', 'wrong'), ('transactions', ['wrong']), ('canonical_transaction', 'wrong')]:
        path.write_text(json.dumps({**manifest, key: value}))
        assert demo_collection(pipeline)['status'] == 'unavailable'
    path.write_text(json.dumps({**manifest, 'cases': manifest['cases'] * 2}))
    assert demo_collection(pipeline)['case_ids'] == []


def test_collection_endpoint_auth_and_operational_counts(pipeline, case, tmp_path):
    pipeline.settings = replace(pipeline.settings, artifact_dir=tmp_path)
    (tmp_path / 'demo_manifest.json').write_text(json.dumps(manifest_for(pipeline, case)))
    client = TestClient(create_app(replace(pipeline.settings, analyst_token='TEST-ONLY-ANALYST'), pipeline))
    assert client.get('/api/demo-collection').status_code == 401
    headers = {'Authorization': 'Bearer TEST-ONLY-ANALYST'}
    result = client.get('/api/demo-collection', headers=headers)
    assert result.status_code == 200 and result.json()['canonical_case_id'] == case['id']
    row = client.get('/api/cases', headers=headers).json()[0]
    assert row['evidence_traceable'] and row['blocking_findings'] == 0
    assert row['evidence_count'] == len(case['outputs']['investigation']['evidence'])
