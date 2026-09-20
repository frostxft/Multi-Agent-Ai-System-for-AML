"""Run real local constrained generation against a persisted benchmark dossier."""
from dataclasses import replace
from pathlib import Path
import json
import time
from aml.config import Settings
from aml.agents import NarrativeAgent, ComplianceAgent
from aml.model import seed_everything
from aml.store import Store

seed_everything(17)
store=Store(Path('artifacts/cases.db'))
case=next(c for c in store.list() if len(c['outputs']['detection']['subgraph']['nodes'])>=3)
settings=replace(Settings(),llm_provider='local')
t=time.perf_counter()
narrative=NarrativeAgent(settings).run(case['outputs']['investigation'])
validation=ComplianceAgent().run(case['outputs']['detection'],case['outputs']['investigation'],narrative)
assert narrative['synthesis'] and validation['status']=='review_ready',validation
report={'case_source':case['id'],'provider':'local','model':settings.llm_model,'seconds':time.perf_counter()-t,
        'synthesis':narrative['synthesis'],'synthesis_status':narrative['synthesis_status'],'compliance':validation}
Path('artifacts/benchmark/local_llm_validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
