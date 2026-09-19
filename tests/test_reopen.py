from fastapi.testclient import TestClient
from aml.api import create_app


def test_reopen_preserves_decision_and_allows_new_review(pipeline, case):
    client = TestClient(create_app(pipeline.settings, pipeline))
    approved = client.post(f"/api/cases/{case['id']}/review",
                           json={'decision': 'approve', 'notes': 'prototype approval', 'expected_revision': case['revision']})
    assert approved.status_code == 200 and approved.json()['status'] == 'approved'
    approved_rev = approved.json()['revision']

    # a reason is required
    assert client.post(f"/api/cases/{case['id']}/reopen",
                       json={'reason': '  ', 'expected_revision': approved_rev}).status_code == 422

    reopened = client.post(f"/api/cases/{case['id']}/reopen",
                           json={'reason': 'new information requires review', 'expected_revision': approved_rev})
    assert reopened.status_code == 200
    body = reopened.json()
    assert body['status'] == 'awaiting_review'
    assert body['revision'] == approved_rev + 1
    # previous APPROVE decision preserved as history
    assert len(body['reviews']) == 1 and body['reviews'][0]['decision'] == 'approve'
    # audit intact and records both events
    audit = client.get(f"/api/cases/{case['id']}/audit").json()
    assert audit['valid']
    actions = [e['action'] for e in audit['events']]
    assert 'approve' in actions and 'reopened_for_review' in actions

    # reopened revision is actionable again
    changed = client.post(f"/api/cases/{case['id']}/review",
                          json={'decision': 'request_changes', 'notes': 'please revise the draft', 'expected_revision': body['revision']})
    assert changed.status_code == 200 and changed.json()['status'] == 'changes_requested'
    assert len(changed.json()['reviews']) == 2


def test_reopen_requires_decided_case(pipeline, case):
    client = TestClient(create_app(pipeline.settings, pipeline))
    r = client.post(f"/api/cases/{case['id']}/reopen",
                    json={'reason': 'premature reopen attempt', 'expected_revision': case['revision']})
    assert r.status_code == 409
