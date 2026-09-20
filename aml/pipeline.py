import threading
import time
import uuid
from .agents import DetectionAgent, TriageAgent, InvestigationAgent, NarrativeAgent, ComplianceAgent
from .schemas import Review, Narrative
from .store import Store, Conflict, now, digest
from .reference import SyntheticSnapshotProvider
from .data import describe
from pathlib import Path

class Pipeline:
    stages = ('detection', 'triage', 'investigation', 'narrative', 'compliance')

    def __init__(self, graph, settings):
        self.settings = settings
        self.graph = graph
        self.store = Store(settings.db_path, settings.encryption_key)
        if settings.reference_fixture and graph.kind != 'synthetic_test':
            raise ValueError('Synthetic reference fixtures are prohibited for benchmark/unverified data')
        self.detector = DetectionAgent(graph, settings.artifact_dir, settings.detection_threshold)
        self.triage = TriageAgent(settings)
        reference = SyntheticSnapshotProvider(Path(settings.reference_fixture)) if settings.reference_fixture else None
        self.investigation = InvestigationAgent(graph, reference)
        self.narrative = NarrativeAgent(settings)
        self.compliance = ComplianceAgent(graph)
        self.lock = threading.RLock()
        self.data_profile = describe(graph)

    def create(self, transaction_id, actor='local-demo'):
        if transaction_id not in self.detector.index:
            raise ValueError('Transaction ID not found')
        case = {'id': 'ZEN-' + uuid.uuid4().hex[:12], 'created_at': now(), 'status': 'processing',
                'transaction_id': transaction_id, 'data_kind': self.graph.kind, 'revision': 0,
                'outputs': {}, 'timings': {}, 'reviews': [], 'error': None}
        self.store.save(case, 'intake', actor, 'case_created', expected_revision=0,
                        details={'dataset_fingerprint': self.graph.fingerprint, 'source': self.graph.source})
        return self.run(case['id'])

    def run(self, case_id):
        with self.lock:
            case = self.store.get(case_id)
            if case['status'] not in {'processing', 'failed'}:
                raise Conflict('Only an incomplete or failed case can be resumed')
            if not self.store.audit(case_id)['valid']:
                raise Conflict('Audit integrity failed; investigate before proceeding')
            case['error'] = None
            case['status'] = 'processing'
            start = time.perf_counter()
            for stage in self.stages:
                if stage in case['outputs']:
                    continue
                t = time.perf_counter()
                inputs = digest(case['outputs'])
                self.store.save(case, stage, stage + '_agent', 'started', case['revision'], {'input_hash': inputs})
                try:
                    o = case['outputs']
                    if stage == 'detection':
                        output = self.detector.run(case_id, case['transaction_id'])
                    elif stage == 'triage':
                        output = self.triage.run(o['detection'])
                    elif stage == 'investigation':
                        output = self.investigation.run(o['detection'], o['triage'])
                    elif stage == 'narrative':
                        output = self.narrative.run(o['investigation'])
                    else:
                        output = self.compliance.run(o['detection'], o['investigation'], o['narrative'])
                    case['outputs'][stage] = output
                    case['timings'][stage] = time.perf_counter() - t
                    self.store.save(case, stage, stage + '_agent', 'completed', case['revision'],
                        {'input_hash': inputs, 'output_hash': digest(output), 'seconds': case['timings'][stage]})
                except Exception as exc:
                    case['status'] = 'failed'
                    case['error'] = {'stage': stage, 'type': type(exc).__name__, 'message': str(exc)}
                    self.store.save(case, stage, stage + '_agent', 'failed', case['revision'], case['error'])
                    return case
            case['status'] = 'awaiting_review'
            case['timings']['pipeline_last_run_seconds'] = time.perf_counter() - start
            self.store.save(case, 'human_review', 'orchestrator', 'review_requested', case['revision'])
            return case

    def review(self, case_id, request: Review, actor):
        with self.lock:
            case = self.store.get(case_id)
            if case['revision'] != request.expected_revision:
                raise Conflict('Case changed; reload before review')
            if case['status'] not in {'awaiting_review', 'changes_requested'}:
                raise Conflict('Case is not open for review')
            if not self.store.audit(case_id)['valid']:
                raise Conflict('Audit integrity failed')
            o = case['outputs']
            validation = self.compliance.run(o['detection'], o['investigation'], o['narrative'])
            if request.decision == 'approve' and validation['issues']:
                raise Conflict('Approval blocked by compliance findings; request changes and revise draft')
            case['outputs']['compliance'] = validation
            case['reviews'].append({**request.model_dump(exclude={'expected_revision'}), 'actor': actor,
                'timestamp': now(), 'provenance': 'human_decision', 'reviewed_revision': case['revision'],
                'reviewed_output_hash': digest(o)})
            case['status'] = {'approve': 'approved', 'reject': 'rejected', 'request_changes': 'changes_requested'}[request.decision]
            return self.store.save(case, 'human_review', actor, request.decision, request.expected_revision,
                                   {'filing_status': 'not_filed', 'notes': request.notes})

    def reopen(self, case_id, reason, expected_revision, actor):
        with self.lock:
            case = self.store.get(case_id)
            if case['revision'] != expected_revision:
                raise Conflict('Case changed; reload before reopening')
            if case['status'] not in {'approved', 'rejected'}:
                raise Conflict('Only an approved or rejected case can be reopened for review')
            if not self.store.audit(case_id)['valid']:
                raise Conflict('Audit integrity failed')
            reopened_from = case['status']
            preserved = [{'decision': r['decision'], 'actor': r['actor'], 'timestamp': r['timestamp'],
                          'reviewed_revision': r['reviewed_revision']} for r in case['reviews']]
            # Existing decisions stay in case['reviews']; only the status changes and a new revision is written.
            case['status'] = 'awaiting_review'
            return self.store.save(case, 'human_review', actor, 'reopened_for_review', expected_revision,
                                   {'reason': reason, 'reopened_from_status': reopened_from,
                                    'preserved_decisions': preserved, 'filing_status': 'not_filed'})

    def revise(self, case_id, narrative: Narrative, revision, actor):
        with self.lock:
            case = self.store.get(case_id)
            if case['status'] not in {'awaiting_review', 'changes_requested'}:
                raise Conflict('Case is not editable')
            if not self.store.audit(case_id)['valid']:
                raise Conflict('Audit integrity failed')
            o = case['outputs']
            original = o['narrative']
            revised = narrative.model_dump()
            # A draft editor cannot rewrite the history of which model/prompt generated it.
            revised['provider'] = original['provider']
            revised['generation_metadata'] = original.get('generation_metadata', {})
            revised['revision_metadata'] = {'actor': actor, 'timestamp': now(), 'previous_revision': case['revision'],
                                            'previous_narrative_hash': digest(original), 'kind': 'post_generation_edit'}
            revised['synthesis_status'] = original.get('synthesis_status', 'not_generated')
            if revised.get('synthesis') != original.get('synthesis'):
                revised['synthesis_status'] = 'edited_requires_revalidation'
            o['narrative'] = revised
            o['compliance'] = self.compliance.run(o['detection'], o['investigation'], o['narrative'])
            case['status'] = 'awaiting_review'
            return self.store.save(case, 'narrative', actor, 'draft_revised_and_revalidated', revision)
