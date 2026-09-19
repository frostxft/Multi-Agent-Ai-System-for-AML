from dataclasses import replace
from fastapi.testclient import TestClient
from aml.api import create_app
from aml.demo_enrichment import demo_enrichment


def test_demo_enrichment_is_deterministic_synthetic_and_labelled():
    a = demo_enrichment('106776627')
    assert a == demo_enrichment('106776627')
    assert a['not_model_input'] is True
    assert a['label'] == 'DEMO / SYNTHETIC PROTOTYPE ENRICHMENT'
    assert a['kyc']['status'] == 'synthetic_profile' and a['kyc']['customer_id'].startswith('DEMO-CUST-')
    assert a['sanctions']['status'] in {'synthetic_no_match', 'synthetic_match'}
    assert a['sanctions']['screened_at'] and a['sanctions']['reference'] and a['sanctions']['match_status']
    assert demo_enrichment('106776627') != demo_enrichment('218047279')


def test_demo_enrichment_endpoint_returns_labelled_data(pipeline, case):
    client = TestClient(create_app(pipeline.settings, pipeline))
    result = client.get(f"/api/cases/{case['id']}/demo-enrichment")
    assert result.status_code == 200
    body = result.json()
    assert body['transaction_id'] == case['transaction_id']
    assert body['kyc']['label'] == 'DEMO / SYNTHETIC KYC'
    assert body['sanctions']['label'] == 'DEMO / SYNTHETIC SANCTIONS SCREENING'
    assert 'not a real' in body['note'].lower()
