"""Save measured reports into a small reviewable documentation artifact."""
from pathlib import Path
import json
from aml.store import Store

docs=Path('docs')
docs.mkdir(exist_ok=True)
evaluation=json.loads(Path('artifacts/benchmark/evaluation.json').read_text())
(docs/'benchmark_evaluation.json').write_text(json.dumps(evaluation,indent=2),encoding='utf-8')
store=Store(Path('artifacts/cases.db'))
summary=[]
for case in store.list():
    d=case['outputs'].get('detection',{})
    n=case['outputs'].get('narrative',{})
    summary.append({'id':case['id'],'transaction_id':case['transaction_id'],'status':case['status'],
        'data_kind':case['data_kind'],'nodes':len(d.get('subgraph',{}).get('nodes',[])),
        'edges':len(d.get('subgraph',{}).get('edges',[])),'score':d.get('score'),
        'narrative_provider':n.get('provider'),'synthesis_status':n.get('synthesis_status'),
        'evidence_count':len(case['outputs'].get('investigation',{}).get('evidence',[])),
        'compliance_status':case['outputs'].get('compliance',{}).get('status'),
        'audit_valid':store.audit(case['id'])['valid'],'review_count':len(case['reviews']),
        'timings':case['timings'],'error':case['error']})
(docs/'case_validation.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
print(json.dumps(summary,indent=2))
