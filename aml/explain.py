"""Actual GNNExplainer masks, intervention checks and baseline-only SHAP."""
import numpy as np
import torch
from torch_geometric.explain import Explainer, GNNExplainer
from torch_geometric.utils import k_hop_subgraph

def explain_case(model, x, edges, index, ids, baseline_path, epochs=40):
    torch.manual_seed(17)
    subset, sub_edges, mapping, edge_mask = k_hop_subgraph(index, 2, edges, relabel_nodes=True, num_nodes=x.shape[0], flow='source_to_target')
    if len(subset) > 1500:
        raise RuntimeError('Explanation neighborhood exceeds 1500 nodes; needs bounded scalable explanation')
    sub_x = x[subset]
    target = int(mapping.item())
    explainer = Explainer(model=model, algorithm=GNNExplainer(epochs=epochs), explanation_type='model',
                          node_mask_type='attributes', edge_mask_type='object',
                          model_config=dict(mode='binary_classification', task_level='node', return_type='raw'))
    result = explainer(sub_x, sub_edges, index=target)
    feature_mask = result.node_mask.detach().mean(0).numpy()
    edge_values = result.edge_mask.detach().numpy()
    if not np.isfinite(feature_mask).all() or not np.isfinite(edge_values).all():
        raise RuntimeError('Nonfinite explanation')
    with torch.no_grad():
        score = float(model(sub_x, sub_edges)[target].sigmoid())
        keep = torch.ones(sub_edges.shape[1], dtype=torch.bool)
        top = np.argsort(-edge_values)[:min(5, len(edge_values))]
        keep[top] = False
        deleted = float(model(sub_x, sub_edges[:, keep])[target].sigmoid())
    nodes = [{'id': ids[int(n)], 'attribution': float(result.node_mask[i].detach().mean()), 'target': int(n) == index} for i, n in enumerate(subset)]
    edge_records = [{'source': ids[int(subset[int(s)])], 'target': ids[int(subset[int(t)])], 'attribution': float(edge_values[i])} for i, (s, t) in enumerate(sub_edges.T)]
    # Exact interventional linear SHAP for the separate logistic model, in log-odds.
    import shap
    b = np.load(baseline_path)
    sh = shap.LinearExplainer((b['coef'][0], b['intercept'][0]), b['background'])
    values = np.asarray(sh.shap_values(x[index:index + 1].numpy()))[0]
    baseline_logit = float(b['intercept'][0] + np.dot(b['coef'][0], x[index].numpy()))
    shap_sum = float(sh.expected_value + values.sum())
    if not np.isclose(shap_sum, baseline_logit, atol=1e-4):
        raise RuntimeError('SHAP additivity failed')
    return {'status': 'available', 'method': 'PyG GNNExplainer', 'epochs': epochs,
            'explained_target': 'predicted class', 'provenance': 'model_derived',
            'nodes': nodes, 'edges': edge_records,
            'features': [{'name': f'local_feature_{int(i) + 1}', 'attribution': float(feature_mask[i])} for i in np.argsort(-feature_mask)[:10]],
            'fidelity': {'original_score': score, 'top5_edges_removed_score': deleted, 'score_drop': score - deleted},
            'baseline_shap': {'method': 'SHAP LinearExplainer', 'explains': 'separate logistic baseline log-odds, NOT GAT or narrative truth',
                              'expected_value': float(sh.expected_value), 'sum': shap_sum, 'logit': baseline_logit,
                              'features': [{'name': f'local_feature_{int(i) + 1}', 'value': float(values[i])} for i in np.argsort(-abs(values))[:10]]},
            'limitations': ['Local optimized masks, not causal proof', 'Anonymized feature semantics unavailable', 'Attention/masks do not establish money laundering', 'SubgraphX not implemented; GNNExplainer supplies graph attribution']}
