"""Conservative bounded-neighborhood measures. No labels or monetary inference."""
from collections import deque, Counter

VERSION = 'local-directed-structure-v1'


def summarize_network(subgraph, threshold):
    nodes = {n['id']: n for n in subgraph['nodes']}
    edges = {(e['source'], e['target']) for e in subgraph['edges']}
    incoming = {i: set() for i in nodes}; outgoing = {i: set() for i in nodes}
    for source, target in edges:
        if source not in nodes or target not in nodes:
            raise ValueError('Structural edge endpoint missing from case')
        incoming[target].add(source); outgoing[source].add(target)
    target = next((i for i, n in nodes.items() if n.get('target')), None)
    distances = {target: 0} if target else {}
    queue = deque(distances)
    while queue:
        i = queue.popleft()
        for source in sorted(incoming[i]):
            if source not in distances:
                distances[source] = distances[i] + 1; queue.append(source)
    components, visited = 0, set()
    for i in sorted(nodes):
        if i in visited: continue
        components += 1; queue = deque([i]); visited.add(i)
        while queue:
            current = queue.popleft()
            for other in incoming[current] | outgoing[current]:
                if other not in visited: visited.add(other); queue.append(other)
    indegree = {i: len(incoming[i]) for i in nodes}
    queue = deque(i for i, degree in indegree.items() if degree == 0); removed = 0
    while queue:
        i = queue.popleft(); removed += 1
        for other in outgoing[i]:
            indegree[other] -= 1
            if indegree[other] == 0: queue.append(other)
    scored = [n for n in nodes.values() if n.get('model_score') is not None]
    flagged = sum(n['model_score'] >= threshold for n in scored)
    nonself = sum(a != b for a,b in edges)
    timeline = Counter(n['time_step'] for n in nodes.values())
    return {'version': VERSION, 'scope': 'Stored case neighborhood only; counts describe topology, not currency concentration or laundering typology.',
            'node_count': len(nodes), 'edge_count': len(edges),
            'directed_density': nonself / (len(nodes)*(len(nodes)-1)) if len(nodes)>1 else 0.,
            'weak_components': components, 'has_directed_cycle': removed < len(nodes),
            'max_in_degree': max(map(len,incoming.values()), default=0),
            'max_out_degree': max(map(len,outgoing.values()), default=0),
            'scored_nodes': len(scored), 'above_threshold_nodes': flagged,
            'above_threshold_fraction': flagged/len(scored) if scored else None,
            'threshold': threshold, 'timeline': [{'time_step': t, 'transactions': count} for t,count in sorted(timeline.items())],
            'temporal_limit': 'Dataset time steps only. Transactions sharing a time step have no observed within-step chronology.',
            'node_metrics': [{'id': i, 'in_degree': len(incoming[i]), 'out_degree': len(outgoing[i]),
                              'distance_to_target': distances.get(i), 'model_score': nodes[i].get('model_score')}
                             for i in sorted(nodes)]}


def structural_facts(summary):
    return {
        'topology': f'The stored case neighborhood contains {summary["node_count"]} transaction nodes and {summary["edge_count"]} distinct directed edges, with directed density {summary["directed_density"]:.6f}.',
        'fan_structure': f'Within the stored case neighborhood, maximum in-degree is {summary["max_in_degree"]} and maximum out-degree is {summary["max_out_degree"]}.',
        'connectivity': f'The stored case neighborhood has {summary["weak_components"]} weakly connected component(s); directed cycle present: {str(summary["has_directed_cycle"]).lower()}.',
        'score_concentration': f'At the case snapshot, {summary["above_threshold_nodes"]} of {summary["scored_nodes"]} scored neighborhood nodes meet model threshold {summary["threshold"]:.6f}; these are uncalibrated model outputs.'}
