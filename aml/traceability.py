"""Recheck benchmark facts against loaded source records, not generated prose."""
from pathlib import Path


class SourceIndex:
    """Built once for a loaded graph. No labels and no per-case full-edge scan."""
    def __init__(self, graph):
        self.lookup = {ident: i for i, ident in enumerate(graph.ids)}
        self.edges = set(map(tuple, graph.edges.T.tolist()))


def source_issues(detection, dossier, graph, index=None):
    issues = []
    if detection['dataset_fingerprint'] != graph.fingerprint or detection['data_kind'] != graph.kind:
        issues.append('Source dataset identity mismatch')
    nodes = {n['id'] for n in detection['subgraph']['nodes']}
    index = index or SourceIndex(graph)
    lookup = index.lookup
    source_records = {e['source_record'] for e in dossier['evidence'] if e['kind'] == graph.kind}
    if not nodes.issubset(source_records):
        issues.append('Missing source transaction evidence')
    expected_edges = {e['source'] + '->' + e['target'] for e in detection['subgraph']['edges']}
    if not expected_edges.issubset(source_records):
        issues.append('Missing source edge evidence')
    for e in dossier['evidence']:
        if e['kind'] not in {'benchmark', 'synthetic_test', 'unverified_input'}:
            continue
        valid = e['kind'] == graph.kind and e['version'] == graph.fingerprint
        record = e['source_record']
        source = Path(e['source'])
        if source == Path(graph.source) / 'elliptic_txs_features.csv':
            valid &= record in nodes and record in lookup
            if record in lookup:
                valid &= e['fact'] == f'Transaction {record} occurs in dataset time step {graph.times[lookup[record]]}.'
        elif source == Path(graph.source) / 'elliptic_txs_edgelist.csv':
            pair = tuple(record.split('->'))
            valid &= len(pair) == 2 and all(i in nodes and i in lookup for i in pair) and tuple(lookup.get(i, -1) for i in pair) in index.edges
            if len(pair) == 2:
                valid &= e['fact'] == f'A directed payment-flow edge links transaction {pair[0]} to transaction {pair[1]}.'
        else:
            valid = False
        if not valid:
            issues.append('Source record mismatch: ' + e['id'])
    return issues


def trace_claim(text, evidence_ids, evidence):
    sources = [evidence[k] for k in evidence_ids if k in evidence]
    return {'text': text, 'evidence_ids': evidence_ids,
            'status': 'grounded' if len(sources) == len(evidence_ids) and any(e.fact == text for e in sources) else 'unsupported',
            'sources': [{'evidence_id': e.id, 'source': e.source, 'record': e.source_record,
                         'version': e.version, 'kind': e.kind} for e in sources]}


def synthesis_citations(text, evidence):
    """Find exact normalized one/two-fact support; never trust provider metadata."""
    normalized = ' '.join(text.split())
    for a in evidence:
        if normalized == ' '.join(a.fact.split()):
            return [a.id]
        for b in evidence:
            if a.id != b.id and normalized == ' '.join((a.fact + ' ' + b.fact).split()):
                return [a.id, b.id]
    return []
