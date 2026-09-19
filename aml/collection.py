"""Read-only presentation collection; never selects by benchmark class labels."""
import json


def demo_collection(pipeline):
    p = pipeline
    path = p.settings.artifact_dir / 'demo_manifest.json'
    empty = {'status': 'unavailable', 'case_ids': [], 'canonical_case_id': None,
             'reason': 'No verified demo collection; use Technical Mode to inspect stored cases.'}
    if not path.exists():
        return empty
    try:
        manifest = json.loads(path.read_text(encoding='utf-8'))
        ids = [c['id'] for c in manifest['cases']]
        if not ids or len(ids) != len(set(ids)) or manifest['canonical_case_id'] != ids[0]:
            return empty
        if manifest['model_id'] != p.detector.model_id or manifest['dataset_fingerprint'] != p.graph.fingerprint:
            return empty
        transactions = []
        for ident in ids:
            c = p.store.get(ident); d = c['outputs'].get('detection', {})
            if c['data_kind'] != p.graph.kind or d.get('model_id') != manifest['model_id'] or d.get('dataset_fingerprint') != manifest['dataset_fingerprint']:
                return empty
            transactions.append(c['transaction_id'])
        if transactions != manifest['transactions'] or len(set(transactions)) != len(transactions) or transactions[0] != manifest['canonical_transaction']:
            return empty
        return {'status': 'available', 'case_ids': ids, 'canonical_case_id': ids[0],
                'selection_rule': manifest['selection_rule'], 'data_kind': p.graph.kind,
                'reason': 'Recorded label-independent demo runs. Historical cases remain in Technical Mode.'}
    except (KeyError, ValueError, TypeError):
        return empty
