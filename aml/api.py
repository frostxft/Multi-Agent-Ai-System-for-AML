from pathlib import Path
import hashlib
import json
import secrets
import threading
from fastapi import FastAPI, Depends, HTTPException, Header, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from .config import Settings
from .data import load_graph
from .model import seed_everything
from .pipeline import Pipeline
from .schemas import CreateCase, Review, Narrative, Reopen
from .store import Conflict
from .collection import demo_collection
from .demo_enrichment import demo_enrichment

class RevisionRequest(BaseModel):
    expected_revision: int
    narrative: Narrative

def create_app(settings=None, pipeline=None):
    s = settings or Settings()
    init_lock = threading.Lock()
    state = {'pipeline': pipeline}
    app = FastAPI(title='Team Zen AML', version='0.2.0')
    if not s.reviewer_token and not s.analyst_token:
        from starlette.middleware.trustedhost import TrustedHostMiddleware
        app.add_middleware(TrustedHostMiddleware, allowed_hosts=['127.0.0.1', 'localhost', '[::1]', 'testserver'])

    def get_pipeline():
        with init_lock:
            if state['pipeline'] is None:
                try:
                    seed_everything(17)
                    state['pipeline'] = Pipeline(load_graph(s.data_dir), s)
                except Exception as exc:
                    raise HTTPException(503, f'Pipeline unavailable: {type(exc).__name__}: {exc}') from exc
        return state['pipeline']

    def principal(request: Request, authorization: str = Header(default='')):
        scheme, _, token = authorization.partition(' ')
        if s.reviewer_token or s.analyst_token:
            if scheme.lower() != 'bearer' or not token or not token.isascii():
                raise HTTPException(401, 'Valid bearer token required')
            if s.reviewer_token and secrets.compare_digest(token.encode(), s.reviewer_token.encode()):
                return {'actor': 'reviewer', 'role': 'reviewer'}
            if s.analyst_token and secrets.compare_digest(token.encode(), s.analyst_token.encode()):
                return {'actor': 'analyst', 'role': 'analyst'}
            raise HTTPException(401, 'Valid bearer token required')
        if request.client and request.client.host not in {'127.0.0.1', '::1', 'localhost', 'testclient'}:
            raise HTTPException(403, 'Local demo mode accepts loopback connections only; configure role tokens for remote use')
        return {'actor': 'local-demo-reviewer', 'role': 'reviewer'}

    def reviewer(user=Depends(principal)):
        if user['role'] != 'reviewer':
            raise HTTPException(403, 'Reviewer role required')
        return user

    @app.middleware('http')
    async def security_headers(request, call_next):
        # Same-origin browser mutations; bearer tokens remain required in secured mode.
        origin = request.headers.get('origin')
        if request.method not in {'GET', 'HEAD', 'OPTIONS'} and origin and origin != str(request.base_url).rstrip('/'):
            from fastapi.responses import JSONResponse
            return JSONResponse({'detail': 'Cross-origin mutation rejected'}, status_code=403)
        response = await call_next(request)
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'"
        response.headers['Cache-Control'] = 'no-store'
        return response

    @app.exception_handler(Conflict)
    async def conflict_handler(request, exc):
        from fastapi.responses import JSONResponse
        return JSONResponse({'detail': str(exc)}, status_code=409)

    @app.exception_handler(KeyError)
    async def not_found(request, exc):
        from fastapi.responses import JSONResponse
        return JSONResponse({'detail': 'Case not found'}, status_code=404)

    @app.exception_handler(ValueError)
    async def invalid(request, exc):
        from fastapi.responses import JSONResponse
        return JSONResponse({'detail': str(exc)}, status_code=422)

    @app.get('/api/health')
    def health(user=Depends(principal)):
        return {'status': 'ok', 'mode': 'token_rbac' if s.reviewer_token or s.analyst_token else 'loopback_demo',
                'encrypted_case_payloads': bool(s.encryption_key), 'llm_provider': s.llm_provider, 'role': user['role']}

    @app.get('/api/status')
    def system_status(user=Depends(principal)):
        p = state['pipeline']
        return {'build_version': '0.2.0', 'dataset_loaded': p is not None, 'model_loaded': p is not None,
                'model_id': p.detector.model_id if p else None,
                'dataset_fingerprint': p.graph.fingerprint if p else None,
                'database': {'engine': 'SQLite', 'exists': s.db_path.is_file(), 'encrypted_payloads': bool(s.encryption_key)},
                'narrative_provider': s.llm_provider,
                'configuration': {'medium_threshold': s.medium_threshold, 'high_threshold': s.high_threshold,
                                  'detection_threshold': p.detector.threshold_policy if p else s.detection_threshold,
                                  'synthetic_reference_configured': bool(s.reference_fixture)},
                'security_mode': 'token_rbac' if s.reviewer_token or s.analyst_token else 'loopback_demo',
                'tests': 'See docs/VALIDATION.md; this endpoint does not run tests or assert a passing build'}

    @app.get('/api/model')
    def model_provenance(user=Depends(principal), p=Depends(get_pipeline)):
        checkpoint = s.artifact_dir / 'gat.pt'
        report = json.loads((s.artifact_dir / 'evaluation.json').read_text())
        if report['model_id'] != p.detector.model_id or report['data']['fingerprint'] != p.graph.fingerprint:
            raise ValueError('Model/evaluation provenance mismatch')
        return {'model_id': p.detector.model_id, 'checkpoint_sha256': hashlib.sha256(checkpoint.read_bytes()).hexdigest(),
                'seed': p.detector.checkpoint['seed'], 'best_epoch': p.detector.checkpoint['best_epoch'],
                'configuration': report.get('configuration', {'features': 93, 'hidden': 16, 'heads': 2, 'layers': 2, 'dropout': .1}),
                'dataset_fingerprint': p.graph.fingerprint, 'threshold_policy': p.detector.threshold_policy,
                'checkpoint_file_modified_at': checkpoint.stat().st_mtime,
                'timestamp_caveat': 'Filesystem modification time, not an independently verified training creation timestamp',
                'evaluation': report}

    @app.get('/api/overview')
    def overview(user=Depends(principal), p=Depends(get_pipeline)):
        import json
        study_path = s.artifact_dir / 'multiseed_evaluation.json'
        study = json.loads(study_path.read_text()) if study_path.exists() else None
        if study and study['dataset_fingerprint'] != p.graph.fingerprint:
            raise ValueError('Multi-seed report/dataset mismatch')
        analysis_path = s.artifact_dir / 'validation_analysis.json'
        analysis = json.loads(analysis_path.read_text()) if analysis_path.exists() else None
        if analysis and (analysis['dataset_fingerprint'] != p.graph.fingerprint or analysis['model_id'] != p.detector.model_id):
            raise ValueError('Validation analysis provenance mismatch')
        return {'data': p.data_profile, 'evaluation': json.loads((s.artifact_dir / 'evaluation.json').read_text()),
                'multiseed': study,
                'validation_analysis': analysis,
                'case_count': p.store.count(), 'model_id': p.detector.model_id}

    @app.get('/api/demo-collection')
    def collection(user=Depends(principal), p=Depends(get_pipeline)):
        return demo_collection(p)

    @app.get('/api/cases')
    def cases(user=Depends(principal), p=Depends(get_pipeline)):
        return [{'id': c['id'], 'transaction_id': c['transaction_id'], 'status': c['status'], 'created_at': c['created_at'],
                 'data_kind': c['data_kind'], 'revision': c['revision'], 'score': c['outputs'].get('detection', {}).get('score'),
                 'severity': c['outputs'].get('triage', {}).get('severity'), 'error': c['error'],
                 'evidence_traceable': c['outputs'].get('compliance', {}).get('readiness', {}).get('checks', {}).get('evidence_traceable', False),
                 'blocking_findings': len(c['outputs'].get('compliance', {}).get('issues', [])),
                 'evidence_count': len(c['outputs'].get('investigation', {}).get('evidence', [])),
                 'node_count': len(c['outputs'].get('detection', {}).get('subgraph', {}).get('nodes', [])),
                 'explanation_available': c['outputs'].get('detection', {}).get('explanation', {}).get('status') == 'available',
                 'compliance_status': c['outputs'].get('compliance', {}).get('status', 'pending'),
                 'readiness': c['outputs'].get('compliance', {}).get('readiness', {}).get('score'),
                 'readiness_score': c['outputs'].get('compliance', {}).get('readiness', {}).get('score'),
                 'narrative_provider': c['outputs'].get('narrative', {}).get('provider', 'pending')} for c in p.store.list()]

    @app.post('/api/cases', status_code=201)
    def create(body: CreateCase, user=Depends(principal), p=Depends(get_pipeline)):
        return p.create(body.transaction_id, user['actor'])

    @app.get('/api/cases/{case_id}')
    def detail(case_id: str, user=Depends(principal), p=Depends(get_pipeline)):
        return p.store.get(case_id)

    @app.get('/api/cases/{case_id}/audit')
    def audit(case_id: str, user=Depends(principal), p=Depends(get_pipeline)):
        return p.store.audit(case_id)

    @app.get('/api/cases/{case_id}/narrative-history')
    def narrative_history(case_id: str, user=Depends(principal), p=Depends(get_pipeline)):
        return p.store.narrative_history(case_id)

    @app.get('/api/cases/{case_id}/transactions/{transaction_id}')
    def source_transaction(case_id: str, transaction_id: str, user=Depends(principal), p=Depends(get_pipeline)):
        c = p.store.get(case_id); d = c['outputs'].get('detection', {})
        if d.get('dataset_fingerprint') != p.graph.fingerprint:
            raise ValueError('Case/source dataset mismatch')
        if transaction_id not in {n['id'] for n in d.get('subgraph', {}).get('nodes', [])}:
            raise HTTPException(404, 'Transaction is not in this case')
        i = p.detector.index[transaction_id]
        return {'transaction_id': transaction_id, 'time_step': int(p.graph.times[i]),
                'data_kind': p.graph.kind, 'dataset_fingerprint': p.graph.fingerprint,
                'source': 'elliptic_txs_features.csv',
                'attributes': [{'name': f'anonymous_feature_{j+1}', 'value': float(v), 'model_input': j < 93} for j,v in enumerate(p.graph.features[i])],
                'limitation': 'Anonymous numerical attributes; no reconstructed identity, currency amount, calendar date or benchmark label exposed.'}

    @app.get('/api/cases/{case_id}/demo-enrichment')
    def demo_enrichment_view(case_id: str, user=Depends(principal), p=Depends(get_pipeline)):
        c = p.store.get(case_id)
        return demo_enrichment(c['transaction_id'])

    @app.post('/api/cases/{case_id}/retry')
    def retry(case_id: str, user=Depends(principal), p=Depends(get_pipeline)):
        return p.run(case_id)

    @app.post('/api/cases/{case_id}/review')
    def review(case_id: str, body: Review, user=Depends(reviewer), p=Depends(get_pipeline)):
        return p.review(case_id, body, user['actor'])

    @app.post('/api/cases/{case_id}/reopen')
    def reopen(case_id: str, body: Reopen, user=Depends(reviewer), p=Depends(get_pipeline)):
        return p.reopen(case_id, body.reason, body.expected_revision, user['actor'])

    @app.put('/api/cases/{case_id}/narrative')
    def revise(case_id: str, body: RevisionRequest, user=Depends(principal), p=Depends(get_pipeline)):
        return p.revise(case_id, body.narrative, body.expected_revision, user['actor'])

    ui = Path(__file__).resolve().parent.parent / 'web'
    app.mount('/assets', StaticFiles(directory=ui), name='assets')

    @app.get('/')
    def index():
        return FileResponse(ui / 'index.html')

    return app

app = create_app()
