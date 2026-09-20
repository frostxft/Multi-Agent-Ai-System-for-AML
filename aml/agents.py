"""Five components with real responsibilities; orchestration owns persistence."""
import hashlib
import json
from functools import lru_cache
from pathlib import Path
import numpy as np
import torch
from .schemas import Detection, Evidence, Narrative, Claim
from .store import now
from .model import load_model
from .explain import explain_case
from .retrieval import retrieve
from .traceability import source_issues, trace_claim, synthesis_citations, SourceIndex
from .structure import summarize_network, structural_facts, VERSION as STRUCTURE_VERSION
from .reference import reference_context

SCOPE_FACTS = ['Customer identities and KYC are unavailable.',
               'No sanctions reference or screening result is available.',
               'Exact calendar dates and interpretable monetary amounts are unavailable.',
               'A human investigator must review this draft; it is not a filed SAR.']

class DetectionAgent:
    def __init__(self, graph, artifact_dir, threshold=None):
        self.graph, self.artifact_dir = graph, artifact_dir
        self.model, self.x, self.checkpoint, self.model_id = load_model(graph, artifact_dir)
        self.index = {v: i for i, v in enumerate(graph.ids)}
        self.threshold = self.checkpoint['threshold'] if threshold is None else threshold
        self.threshold_policy = {'value': self.threshold, 'checkpoint_default': self.checkpoint['threshold'],
                                 'source': 'checkpoint_validation_F2' if threshold is None else 'explicit_configuration_override',
                                 'scope': 'Case alert threshold; triage priority uses separate configured cutoffs. Not regulatory.'}

    def run(self, case_id, transaction_id):
        if transaction_id not in self.index:
            raise ValueError('Transaction ID not found')
        i, g = self.index[transaction_id], self.graph
        # Inference only sees relationships available by target time step.
        available = (g.times[g.edges[0]] <= g.times[i]) & (g.times[g.edges[1]] <= g.times[i])
        edges = torch.tensor(g.edges[:, available], dtype=torch.long)
        with torch.no_grad():
            snapshot_scores = self.model(self.x, edges).sigmoid().numpy()
            score = float(snapshot_scores[i])
        explanation = explain_case(self.model, self.x, edges, i, g.ids, self.artifact_dir / 'baseline.npz')
        if abs(explanation['fidelity']['original_score'] - score) > 1e-4:
            raise RuntimeError('Subgraph explanation does not reproduce target inference')
        times = {n['id']: int(g.times[self.index[n['id']]]) for n in explanation['nodes']}
        subgraph = {'nodes': [{**n, 'time_step': times[n['id']], 'model_score': float(snapshot_scores[self.index[n['id']]])} for n in explanation['nodes']],
                    'edges': explanation['edges'], 'semantics': 'Transaction nodes and directed payment-flow edges; 2-hop incoming computational neighborhood'}
        subgraph['structure'] = summarize_network(subgraph, self.threshold)
        subgraph['score_scope'] = f'All node scores from full graph available through dataset time step {g.times[i]}; context-node scores are not predictions on the truncated case graph.'
        return Detection(case_id=case_id, model_id=self.model_id, dataset_fingerprint=g.fingerprint, data_kind=g.kind,
                         seed_transaction=transaction_id, score=score, threshold=self.threshold, threshold_policy=self.threshold_policy,
                         flagged=score >= self.threshold, inference_at=now(), subgraph=subgraph,
                         explanation=explanation).model_dump()

class TriageAgent:
    def __init__(self, settings):
        self.settings = settings

    def run(self, detection):
        d = Detection.model_validate(detection)
        severity = 'high' if d.score >= self.settings.high_threshold else 'medium' if d.score >= self.settings.medium_threshold else 'low'
        return {'risk_score': d.score, 'severity': severity, 'priority': {'high': 1, 'medium': 2, 'low': 3}[severity],
                'contributing_factors': [f'GAT model score {d.score:.6f}', f'Neighborhood contains {len(d.subgraph["nodes"])} transaction nodes',
                                         'Explanation available' if d.explanation.get('status') == 'available' else 'Explanation unavailable; escalate'],
                'uncertainty': 'Score is uncalibrated; unknown labels and anonymous features limit interpretation',
                'review_required': True, 'policy': {'medium': self.settings.medium_threshold, 'high': self.settings.high_threshold,
                                                   'basis': 'Configurable prototype prioritization thresholds; not regulatory standards'}}

class InvestigationAgent:
    def __init__(self, graph, reference_provider=None):
        self.graph = graph
        self.reference_provider = reference_provider

    def run(self, detection, triage):
        d = Detection.model_validate(detection)
        g, evidence = self.graph, []
        def add(kind, source, record, fact, version=None):
            evidence.append(Evidence(id=f'E{len(evidence)+1:04d}', case_id=d.case_id, kind=kind, source=source,
                source_record=record, version=version or g.fingerprint, fact=fact).model_dump())
        for node in sorted(d.subgraph['nodes'], key=lambda n: (n['time_step'], n['id'])):
            add(g.kind, g.source + '/elliptic_txs_features.csv', node['id'], f'Transaction {node["id"]} occurs in dataset time step {node["time_step"]}.')
        for edge in d.subgraph['edges']:
            add(g.kind, g.source + '/elliptic_txs_edgelist.csv', edge['source'] + '->' + edge['target'],
                f'A directed payment-flow edge links transaction {edge["source"]} to transaction {edge["target"]}.')
        add('model_output', 'GAT checkpoint', d.seed_transaction,
            f'Model {d.model_id} assigned transaction {d.seed_transaction} an uncalibrated illicit-class score of {d.score:.6f}.', d.model_id)
        add('derived_value', 'TriageAgent', d.case_id, f'Prototype triage assigns {triage["severity"]} priority using configured thresholds.')
        add('model_output', 'GNNExplainer', d.seed_transaction,
            f'GNNExplainer produced local feature and edge masks for transaction {d.seed_transaction}; these are model attributions, not proof of laundering.', d.model_id)
        for missing in SCOPE_FACTS:
            add('missing_information', 'Dataset scope / prototype policy', 'scope', missing)
        structure = summarize_network(d.subgraph, d.threshold)
        for record, fact in structural_facts(structure).items():
            add('derived_value', 'StructureAnalyzer', record, fact, STRUCTURE_VERSION + ':' + g.fingerprint)
        query = f'Transaction {d.seed_transaction} illicit-class model score directed payment-flow edge masks priority customer KYC sanctions calendar human draft'
        retrieved = retrieve(evidence, query, k=min(14, len(evidence)), case_id=d.case_id)
        references = reference_context(g.kind, d.seed_transaction, self.reference_provider)
        return {'case_id': d.case_id, 'evidence': evidence, 'retrieval': retrieved,
                'summary': {'seed_transaction': d.seed_transaction, 'model_score': d.score,
                            'why_flagged': f'Model score {d.score:.6f} {"meets" if d.flagged else "is below"} case threshold {d.threshold:.6f}.',
                            'priority_reason': f'{triage["severity"]} priority uses medium {triage["policy"]["medium"]:.2f} / high {triage["policy"]["high"]:.2f}; this differs from the model alert threshold.',
                            'classification': 'MODEL OUTPUT / DERIVED CONTEXT; not a finding of laundering'},
                'network_summary': structure,
                'findings': [{'evidence_id': e['id'], 'text': e['fact'], 'classification': 'DERIVED STRUCTURAL CONTEXT'} for e in evidence if e['source'] == 'StructureAnalyzer'],
                'open_questions': ['What verified entity owns each transaction, if any?', 'Are genuine KYC and sanctions records available through an authorized source?',
                                   'Do original transaction records provide interpretable amounts or exact timestamps?', 'Does independent evidence corroborate the model flag?'],
                'reference_context': references,
                'chronology': sorted(d.subgraph['nodes'], key=lambda n: (n['time_step'], n['id'])),
                'relationships': d.subgraph['edges'], 'facts_vs_interpretation': 'Dataset records are facts about the benchmark; scores, masks and priorities are model/derived outputs.',
                'patterns': {'node_count': len(d.subgraph['nodes']), 'edge_count': len(d.subgraph['edges']),
                             'interpretation': 'Connected computational neighborhood selected around a scored transaction. No laundering typology inferred from anonymized features.'},
                'kyc': references['kyc'], 'sanctions': references['sanctions']}

@lru_cache(maxsize=2)
def local_llm(path):
    from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
    tokenizer = AutoTokenizer.from_pretrained(path, local_files_only=True)
    model = AutoModelForSeq2SeqLM.from_pretrained(path, local_files_only=True)
    model.eval()
    return tokenizer, model

@lru_cache(maxsize=2)
def local_model_version(path):
    root=Path(path)
    files=sorted(root.glob('*.safetensors')) or sorted(root.glob('pytorch_model*.bin'))
    if not files:
        raise FileNotFoundError('Local model weights unavailable')
    fingerprints={}
    for file in files:
        with file.open('rb') as stream:
            fingerprints[file.name]=hashlib.file_digest(stream,'sha256').hexdigest()
    return fingerprints

class NarrativeAgent:
    def __init__(self, settings):
        self.settings = settings

    def run(self, dossier):
        evidence = {e['id']: Evidence.model_validate(e) for e in dossier['evidence']}
        selected = [r['evidence_id'] for r in dossier['retrieval']]
        # Preserve mandatory limitations/model context alongside ranked retrieval.
        selected += [e.id for e in evidence.values() if e.kind in {'model_output', 'missing_information', 'derived_value'} and e.id not in selected]
        sections = {'Activity and chronology': [], 'Model and triage rationale': [], 'Missing information and review': []}
        for ident in selected:
            e = evidence[ident]
            section = 'Missing information and review' if e.kind == 'missing_information' else 'Model and triage rationale' if e.kind in {'model_output', 'derived_value'} else 'Activity and chronology'
            sections[section].append(Claim(text=e.fact, evidence_ids=[e.id]))
        synthesis, synthesis_status = None, 'not_requested_extractive_mode'
        metadata={'method': 'deterministic cited-fact extraction', 'llm_used': False}
        if self.settings.llm_provider == 'local':
            tokenizer, model = local_llm(self.settings.llm_model)
            facts = [evidence[k].fact for k in selected if evidence[k].kind != 'missing_information'][:6]
            if not facts:
                raise ValueError('No retrieved facts for LLM')
            # Constrained decoding selects a grounded two-fact summary. This is
            # deliberately extractive LLM synthesis, not unrestricted paraphrasing.
            candidates = [a + ' ' + b for a in facts for b in facts if a != b]
            if not candidates:
                candidates = facts
            token_sequences = [tokenizer.encode(c, add_special_tokens=True) for c in candidates]
            def allowed(batch, input_ids):
                prefix = input_ids.tolist()[1:]
                choices = {seq[len(prefix)] for seq in token_sequences if seq[:len(prefix)] == prefix and len(seq) > len(prefix)}
                return sorted(choices) or [tokenizer.eos_token_id]
            prompt = 'Select the most relevant two facts for a suspicious activity review. Use only these facts: ' + ' '.join(facts)
            inputs = tokenizer(prompt, return_tensors='pt', max_length=512, truncation=True)
            with torch.no_grad():
                output = model.generate(**inputs, do_sample=False, max_new_tokens=max(map(len, token_sequences)) + 2, prefix_allowed_tokens_fn=allowed)
            synthesis = tokenizer.decode(output[0], skip_special_tokens=True)
            # Tokenizers may normalize whitespace: compare normalized strings.
            normalized = {' '.join(c.split()) for c in candidates}
            if ' '.join(synthesis.split()) not in normalized:
                raise RuntimeError('Constrained LLM output failed evidence validation')
            synthesis_status = 'validated_constrained_extraction'
            metadata={'method':'greedy decoding constrained to retrieved fact pairs','llm_used':True,
                      'model_path':self.settings.llm_model,'weight_sha256':local_model_version(self.settings.llm_model),
                      'prompt':prompt,'prompt_sha256':hashlib.sha256(prompt.encode()).hexdigest(),
                      'candidate_fact_count':len(facts),'candidate_summary_count':len(candidates)}
        elif self.settings.llm_provider == 'ollama':
            import httpx
            context = '\n'.join(f'[{k}] {evidence[k].fact}' for k in selected)
            response = httpx.post(self.settings.ollama_url.rstrip('/') + '/api/generate',
                json={'model': self.settings.llm_model, 'stream': False, 'prompt': 'Draft a concise AML review summary only from these facts; cite their IDs and state missing facts.\n' + context}, timeout=120)
            response.raise_for_status()
            synthesis = response.json()['response']
            if not synthesis.strip():
                raise RuntimeError('LLM returned empty output')
            synthesis_status = 'unverified_free_text_requires_changes'
            metadata={'method':'Ollama free-text generation','llm_used':True,'model':self.settings.llm_model,
                      'context_sha256':hashlib.sha256(context.encode()).hexdigest(),'model_weights_verified':False}
        return Narrative(provider=self.settings.llm_provider, sections=sections, synthesis=synthesis,
            synthesis_status=synthesis_status, retrieved_evidence_ids=selected,generation_metadata=metadata).model_dump()

class ComplianceAgent:
    def __init__(self, graph=None):
        self.graph = graph
        self.source_index = SourceIndex(graph) if graph is not None else None

    def run(self, detection, dossier, narrative):
        issues = []
        d = Detection.model_validate(detection)
        n = Narrative.model_validate(narrative)
        evidence = {e['id']: Evidence.model_validate(e) for e in dossier['evidence']}
        source_findings = source_issues(detection, dossier, self.graph, self.source_index) if self.graph is not None else []
        issues.extend(source_findings)
        expected_structure = structural_facts(summarize_network(d.subgraph, d.threshold))
        for e in evidence.values():
            if e.source == 'StructureAnalyzer' and (e.kind != 'derived_value' or e.fact != expected_structure.get(e.source_record) or e.version != STRUCTURE_VERSION + ':' + d.dataset_fingerprint):
                issues.append('Derived structural evidence mismatch: ' + e.id)
        claim_validation = []
        if len(evidence) != len(dossier['evidence']):
            issues.append('Duplicate evidence IDs')
        if not n.sections or not all(n.sections.values()):
            issues.append('Missing narrative sections')
        if set(n.sections) != {'Activity and chronology', 'Model and triage rationale', 'Missing information and review'}:
            issues.append('Unexpected or missing section titles; headings must not introduce unsupported claims')
        if not set(n.retrieved_evidence_ids).issubset(evidence):
            issues.append('Retrieved evidence references missing records')
        used = set()
        for section, claims in n.sections.items():
            for claim in claims:
                claim_validation.append({'section': section, **trace_claim(claim.text, claim.evidence_ids, evidence)})
                sources = [evidence.get(k) for k in claim.evidence_ids]
                used.update(claim.evidence_ids)
                if any(e is None for e in sources):
                    issues.append('Missing evidence: ' + claim.text)
                elif claim.text not in [e.fact for e in sources]:
                    issues.append('Unsupported or changed claim: ' + claim.text)
        for e in evidence.values():
            if e.case_id != d.case_id or not e.source_record or not e.version:
                issues.append('Evidence association/version missing: ' + e.id)
        if not used.issubset(n.retrieved_evidence_ids):
            issues.append('Narrative citations missing from retrieval context')
        model_fact = f'Model {d.model_id} assigned transaction {d.seed_transaction} an uncalibrated illicit-class score of {d.score:.6f}.'
        if model_fact not in [e.fact for e in evidence.values()] or not any(e.id in used and e.fact == model_fact for e in evidence.values()):
            issues.append('Narrative/model mismatch or missing model evidence')
        missing = [e.id for e in evidence.values() if e.kind == 'missing_information']
        if not set(SCOPE_FACTS).issubset({e.fact for e in evidence.values() if e.kind == 'missing_information'}):
            issues.append('Missing mandatory dataset-scope evidence')
        if not set(missing).issubset(used):
            issues.append('Missing disclosure of unavailable information or human review')
        if d.explanation.get('status') != 'available' or not d.explanation.get('features'):
            issues.append('Missing model explanation')
        if n.synthesis is not None:
            # Revalidate text itself; never trust its claimed synthesis_status.
            facts = [evidence[k].fact for k in n.retrieved_evidence_ids if k in evidence]
            allowed = {' '.join((a + ' ' + b).split()) for a in facts for b in facts if a != b} | {' '.join(f.split()) for f in facts}
            if ' '.join(n.synthesis.split()) not in allowed:
                issues.append('Unverified LLM free text requires removal or evidence-grounded revision')
        synthesis_ids = synthesis_citations(n.synthesis, [evidence[k] for k in n.retrieved_evidence_ids if k in evidence]) if n.synthesis else []
        checks = {'explanation_available': d.explanation.get('status') == 'available',
                  'evidence_traceable': bool(evidence) and not source_findings and all(e.version and e.source_record for e in evidence.values()),
                  'narrative_consistent': not issues, 'model_versioned': bool(d.model_id),
                  'data_current_for_live_use': False, 'identity_context_complete': False,
                  'human_review_required': True}
        score_checks = {k: v for k, v in checks.items() if k != 'human_review_required'}
        reasons = {'explanation_available': 'Local GNNExplainer output exists; availability is not an explanation confidence estimate.',
                   'evidence_traceable': 'Source IDs and versions required; loaded graph records rechecked.' if self.graph is not None else 'Source IDs and versions checked; source dataset not supplied for revalidation.',
                   'narrative_consistent': f'{len(issues)} unresolved consistency finding(s); exact cited facts required.',
                   'model_versioned': 'Checkpoint identity accompanies the model score.',
                   'data_current_for_live_use': 'Historical anonymous benchmark has no verifiable current calendar dates.',
                   'identity_context_complete': 'Genuine customer identity, KYC and sanctions context are unavailable.',
                   'human_review_required': 'Mandatory policy gate, excluded from score; no score authorizes autonomous filing.'}
        categories = {'Evidence and source records': ['Source ', 'source ', 'Missing evidence', 'Evidence association', 'Duplicate evidence', 'Derived structural'],
                      'Model agreement': ['model mismatch'], 'Explanation': ['Missing model explanation'],
                      'Required data disclosures': ['Missing mandatory', 'Missing disclosure'],
                      'Narrative grounding and structure': ['Unsupported', 'Unverified', 'Missing narrative', 'section titles', 'retrieval context', 'Retrieved evidence']}
        checklist = [{'category': category, 'passed': not any(any(p in issue for p in patterns) for issue in issues),
                      'findings': [issue for issue in issues if any(p in issue for p in patterns)]} for category,patterns in categories.items()]
        return {'status': 'issues_found' if issues else 'review_ready', 'issues': issues,
                'checklist': checklist, 'blocking_issue_count': len(issues),
                'claim_validation': claim_validation, 'synthesis_evidence_ids': synthesis_ids,
                'source_validation': {'performed': self.graph is not None, 'issues': source_findings},
                'approval_eligible': not issues,
                'unsupported_claims': [i for i in issues if 'Unsupported' in i or 'Unverified' in i],
                'missing_information': [evidence[k].fact for k in missing], 'review_required': True,
                'readiness': {'score': round(100 * sum(score_checks.values()) / len(score_checks)), 'checks': checks,
                              'label': 'Internal Prototype Readiness Score',
                              'factors': [{'name': k, 'satisfied': v, 'weight': 0 if k == 'human_review_required' else 1,
                                           'reason': reasons[k]} for k, v in checks.items()],
                              'autonomy': 'human_only', 'basis': 'Unweighted prototype checks; not a regulatory standard'},
                'scope': 'Evidence consistency checks, not legal compliance certification; SHAP explains baseline only'}
