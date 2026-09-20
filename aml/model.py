"""Temporal GAT training and independent logistic-regression baseline."""
from pathlib import Path
import copy
import hashlib
import json
import time
import random
import numpy as np
import torch
from torch import nn
from torch_geometric.nn import GATConv
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, precision_score, recall_score, confusion_matrix, fbeta_score
from .data import describe

class GAT(nn.Module):
    def __init__(self, features=93, hidden=16, heads=2):
        super().__init__()
        self.first = GATConv(features, hidden, heads=heads, dropout=.1)
        self.second = GATConv(hidden * heads, 1, heads=1, concat=False, dropout=.1)

    def forward(self, x, edge_index):
        return self.second(torch.nn.functional.elu(self.first(x, edge_index)), edge_index).squeeze(-1)

def seed_everything(seed):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.set_num_threads(4)
    torch.use_deterministic_algorithms(True)

def metrics(y, p, threshold):
    pred = p >= threshold
    return {'threshold': float(threshold), 'precision': float(precision_score(y, pred, zero_division=0)),
            'recall': float(recall_score(y, pred, zero_division=0)),
            'average_precision': float(average_precision_score(y, p)),
            # Compatibility alias for original reports/UI; this is AP, not trapezoidal PR-AUC.
            'pr_auc_average_precision': float(average_precision_score(y, p)),
            'confusion_matrix_tn_fp_fn_tp': confusion_matrix(y, pred, labels=[0, 1]).ravel().tolist(),
            'n': len(y), 'positives': int(y.sum())}

def select_threshold(y, p):
    grid = np.linspace(.05, .95, 91)
    # Validation-only F2 emphasizes recall; no test-label tuning.
    return float(max(grid, key=lambda t: fbeta_score(y, p >= t, beta=2, zero_division=0)))

def train(g, out: Path, epochs=25, seed=17):
    if epochs < 1:
        raise ValueError('epochs must be positive')
    seed_everything(seed)
    out.mkdir(parents=True, exist_ok=True)
    start = time.perf_counter()
    masks = {s: g.mask(s) for s in ['train', 'validation', 'test']}
    for s, mask in masks.items():
        if set(g.labels[mask]) != {0, 1}:
            raise ValueError(f'{s} needs both labeled classes')
    # First 93 columns after time are local features. Exclude 72 pre-aggregated
    # neighbor features so the baseline is tabular and GAT supplies topology.
    features = g.features[:, :93]
    train_nodes = g.times <= 29
    mean = features[train_nodes].mean(0)
    scale = features[train_nodes].std(0)
    scale[scale < 1e-6] = 1
    x = torch.tensor((features - mean) / scale, dtype=torch.float32)
    y = torch.tensor(g.labels, dtype=torch.float32)
    edge_sets = {s: torch.tensor(g.edges[:, (g.times[g.edges[0]] <= cutoff) & (g.times[g.edges[1]] <= cutoff)], dtype=torch.long) for s, cutoff in [('train', 29), ('validation', 34), ('test', 49)]}
    tm = torch.tensor(masks['train'])
    model = GAT()
    optimizer = torch.optim.Adam(model.parameters(), lr=.005, weight_decay=5e-4)
    loss_fn = nn.BCEWithLogitsLoss(pos_weight=torch.tensor(float((g.labels[tm] == 0).sum() / (g.labels[tm] == 1).sum())))
    best, best_state, best_epoch, history = -1., None, None, []
    for epoch in range(1, epochs + 1):
        model.train()
        optimizer.zero_grad()
        logits = model(x, edge_sets['train'])
        loss = loss_fn(logits[tm], y[tm])
        if not torch.isfinite(loss):
            raise RuntimeError('Nonfinite training loss')
        loss.backward()
        optimizer.step()
        model.eval()
        with torch.no_grad():
            p = model(x, edge_sets['validation']).sigmoid().numpy()
        ap = float(average_precision_score(g.labels[masks['validation']], p[masks['validation']]))
        history.append({'epoch': epoch, 'loss': float(loss.detach()), 'validation_ap': ap})
        if ap > best:
            best, best_state, best_epoch = ap, copy.deepcopy(model.state_dict()), epoch
        print(json.dumps(history[-1]), flush=True)
    model.load_state_dict(best_state)
    model.eval()
    with torch.no_grad():
        val_p = model(x, edge_sets['validation']).sigmoid().numpy()
        test_p = model(x, edge_sets['test']).sigmoid().numpy()
    threshold = select_threshold(g.labels[masks['validation']], val_p[masks['validation']])
    baseline = LogisticRegression(class_weight='balanced', max_iter=1500, random_state=seed)
    baseline.fit(x.numpy()[masks['train']], g.labels[masks['train']])
    baseline_p = baseline.predict_proba(x.numpy())[:, 1]
    baseline_threshold = select_threshold(g.labels[masks['validation']], baseline_p[masks['validation']])
    checkpoint = {'state_dict': best_state, 'mean': torch.tensor(mean), 'scale': torch.tensor(scale),
                  'fingerprint': g.fingerprint, 'kind': g.kind, 'seed': seed, 'threshold': threshold,
                  'features': 93, 'best_epoch': best_epoch}
    torch.save(checkpoint, out / 'gat.pt')
    model_id = 'gat-' + hashlib.sha256((out / 'gat.pt').read_bytes()).hexdigest()[:16]
    np.savez(out / 'baseline.npz', coef=baseline.coef_, intercept=baseline.intercept_, background=x.numpy()[masks['train']][:1000], threshold=baseline_threshold)
    np.save(out / 'scores.npy', test_p)
    report = {'data': describe(g), 'model_id': model_id, 'seed': seed, 'epochs': epochs, 'best_epoch': best_epoch,
              'configuration': {'hidden': 16, 'heads': 2, 'layers': 2, 'dropout': .1,
                                'learning_rate': .005, 'weight_decay': 5e-4,
                                'positive_loss_weight': float(loss_fn.pos_weight),
                                'baseline': 'LogisticRegression balanced, C=1, max_iter=1500',
                                'threshold_policy': 'maximum validation F2 over 0.05..0.95 step 0.01; lowest threshold on tie'},
              'metric_definition': 'Average Precision (AP), sklearn step-weighted precision-recall summary; not trapezoidal PR-AUC',
              'feature_policy': '93 local anonymized features; exclude time and 72 preaggregated features',
              'methodology': 'Train <=29; validation 30-34; test 35-49. Unknown labels excluded from loss/metrics. Train-only normalization. Edges masked at split cutoff. Best epoch by validation AP; threshold by validation F2. Single seeded CPU run.',
              'history': history,
              'gat': {s: metrics(g.labels[masks[s]], (val_p if s == 'validation' else test_p)[masks[s]], threshold) for s in ['validation', 'test']},
              'baseline': {s: metrics(g.labels[masks[s]], baseline_p[masks[s]], baseline_threshold) for s in ['validation', 'test']},
              'threshold_behavior': {str(t): metrics(g.labels[masks['test']], test_p[masks['test']], t) for t in [.3, .5, .7, .9]},
              'training_total_seconds': time.perf_counter() - start}
    fp_g = report['gat']['test']['confusion_matrix_tn_fp_fn_tp'][1]
    fp_b = report['baseline']['test']['confusion_matrix_tn_fp_fn_tp'][1]
    report['false_positive_change'] = {'gat_count': fp_g, 'baseline_count': fp_b,
        'relative_reduction': (fp_b - fp_g) / fp_b if fp_b else None,
        'caveat': 'Each threshold chosen by validation F2; operating points and recalls differ. Not a matched-recall business savings estimate.'}
    (out / 'evaluation.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    return report

def load_model(g, folder):
    checkpoint = torch.load(folder / 'gat.pt', map_location='cpu', weights_only=True)
    if checkpoint['fingerprint'] != g.fingerprint:
        raise ValueError('Model/dataset fingerprint mismatch; retrain or restore matching data')
    model = GAT()
    model.load_state_dict(checkpoint['state_dict'])
    model.eval()
    model_id = 'gat-' + hashlib.sha256((folder / 'gat.pt').read_bytes()).hexdigest()[:16]
    x = (torch.tensor(g.features[:, :93]) - checkpoint['mean']) / checkpoint['scale']
    return model, x, checkpoint, model_id
