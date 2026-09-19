"""Label-independent, deterministic connected-case selection and verification."""
import numpy as np
import torch
from torch_geometric.utils import k_hop_subgraph


SELECTION_RULE = 'Time step >=35; score >= model threshold; descending score then transaction ID; incoming two-hop context 3..1500 nodes at target cutoff; skip previously covered targets. No labels consulted.'


def select_transactions(graph, scores, threshold, count=4):
    if count < 1 or len(scores) != len(graph.ids) or not np.isfinite(scores).all():
        raise ValueError('Positive case count and finite dataset-aligned scores required')
    eligible = np.where((graph.times >= 35) & (scores >= threshold))[0]
    ordered = sorted(eligible, key=lambda i: (-float(scores[i]), graph.ids[i]))
    chosen, seen = [], set()
    for i in ordered:
        if int(i) in seen:
            continue
        available = (graph.times[graph.edges[0]] <= graph.times[i]) & (graph.times[graph.edges[1]] <= graph.times[i])
        edges = torch.tensor(graph.edges[:, available], dtype=torch.long)
        neighborhood, _, _, _ = k_hop_subgraph(int(i), 2, edges, num_nodes=len(graph.ids), flow='source_to_target')
        if not 3 <= len(neighborhood) <= 1500:
            continue
        chosen.append(graph.ids[i])
        seen.update(neighborhood.tolist())
        if len(chosen) == count:
            return chosen
    raise ValueError(f'Only {len(chosen)} eligible connected cases; requested {count}')


def validate_case(case, store):
    o = case['outputs']
    return {'id': case['id'], 'transaction_id': case['transaction_id'], 'status': case['status'],
            'checks': {'awaiting_review': case['status'] == 'awaiting_review',
                       'no_human_decisions': not case['reviews'],
                       'all_stages': set(o) == {'detection', 'triage', 'investigation', 'narrative', 'compliance'},
                       'model_flagged': o.get('detection', {}).get('flagged', False),
                       'connected_context': len(o.get('detection', {}).get('subgraph', {}).get('nodes', [])) >= 3,
                       'consistent': o.get('compliance', {}).get('status') == 'review_ready',
                       'source_rechecked': o.get('compliance', {}).get('source_validation', {}).get('performed', False),
                       'audit_integrity': store.audit(case['id'])['valid']},
            'timings': case['timings'], 'error': case['error']}
