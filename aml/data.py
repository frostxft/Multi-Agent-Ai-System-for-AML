"""Strict Elliptic ingestion. Labels are targets, never input features."""
from dataclasses import dataclass
from pathlib import Path
import hashlib
import json
import numpy as np
import pandas as pd
import torch

FILES = ('elliptic_txs_features.csv', 'elliptic_txs_edgelist.csv', 'elliptic_txs_classes.csv')

@dataclass
class Graph:
    ids: list[str]
    times: np.ndarray
    features: np.ndarray
    labels: np.ndarray
    edges: np.ndarray
    fingerprint: str
    kind: str
    source: str

    def mask(self, split):
        temporal = {'train': self.times <= 29, 'validation': (self.times >= 30) & (self.times <= 34), 'test': self.times >= 35}[split]
        return temporal & (self.labels >= 0)

    def tensors(self, mean, scale, cutoff=49):
        x = torch.tensor((self.features - mean) / scale, dtype=torch.float32)
        e = self.edges[:, (self.times[self.edges[0]] <= cutoff) & (self.times[self.edges[1]] <= cutoff)]
        return x, torch.tensor(e, dtype=torch.long)

def load_graph(root: Path) -> Graph:
    paths = [root / f for f in FILES]
    for p in paths:
        if not p.is_file():
            raise FileNotFoundError(f'Missing dataset file: {p}')
    feat = pd.read_csv(paths[0], header=None, dtype={0: np.int64, **{i: np.float32 for i in range(1, 167)}})
    edges = pd.read_csv(paths[1], dtype=str)
    labels = pd.read_csv(paths[2], dtype=str)
    if feat.shape[1] != 167:
        raise ValueError('Expected txId, time_step and 165 anonymized Elliptic features')
    if list(edges.columns) != ['txId1', 'txId2'] or list(labels.columns) != ['txId', 'class']:
        raise ValueError('Invalid edge or label schema')
    ids = feat[0].astype(str).tolist()
    if len(set(ids)) != len(ids) or labels.txId.duplicated().any():
        raise ValueError('Duplicate transaction IDs')
    if set(labels.txId) != set(ids) or not set(labels['class']).issubset({'1', '2', 'unknown'}):
        raise ValueError('Missing/extra IDs or invalid classes')
    mapping = {v: i for i, v in enumerate(ids)}
    mapped = edges.apply(lambda c: c.map(mapping))
    if mapped.isna().any().any():
        raise ValueError('Edge references unknown transaction')
    times = feat[1].to_numpy(dtype=float)
    if not np.all(np.isfinite(times)) or not np.all(times == times.astype(int)) or np.any((times < 1) | (times > 49)):
        raise ValueError('Invalid time steps')
    features = feat.iloc[:, 2:].to_numpy(dtype=np.float32)
    if not np.isfinite(features).all():
        raise ValueError('Nonfinite features')
    target = labels.set_index('txId').loc[ids, 'class'].map({'1': 1, '2': 0, 'unknown': -1}).to_numpy(dtype=np.int64)
    hashes = {}
    for p in paths:
        with p.open('rb') as stream:
            hashes[p.name] = hashlib.file_digest(stream, 'sha256').hexdigest()
    fingerprint = hashlib.sha256(json.dumps(hashes, sort_keys=True).encode()).hexdigest()
    manifest_path = root / 'manifest.json'
    manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
    kind = manifest.get('kind', 'unverified_input')
    if kind not in {'benchmark', 'synthetic_test', 'unverified_input'}:
        raise ValueError('Unknown dataset provenance kind')
    declared = manifest.get('files', {})
    if kind == 'benchmark' and set(declared) != set(FILES):
        raise ValueError('Benchmark manifest must declare all three source file hashes')
    for name, details in declared.items():
        if name in hashes and details.get('sha256') != hashes[name]:
            raise ValueError(f'Dataset manifest hash mismatch: {name}')
    return Graph(ids, times.astype(int), features, target, mapped.to_numpy(dtype=np.int64).T, fingerprint, kind, str(root.resolve()))

def describe(g):
    return {'kind': g.kind, 'source': g.source, 'fingerprint': g.fingerprint,
            'nodes': len(g.ids), 'edges': g.edges.shape[1], 'features': g.features.shape[1],
            'node_semantics': 'Bitcoin transactions', 'edge_semantics': 'Directed payment flow between transactions',
            'time_steps': [int(g.times.min()), int(g.times.max())],
            'class_counts': {str(k): int((g.labels == k).sum()) for k in [-1, 0, 1]},
            'graph_checks': {'duplicate_directed_edges': int(g.edges.shape[1] - np.unique(g.edges, axis=1).shape[1]),
                             'self_edges': int((g.edges[0] == g.edges[1]).sum()),
                             'cross_time_edges': int((g.times[g.edges[0]] != g.times[g.edges[1]]).sum()),
                             'backward_time_edges': int((g.times[g.edges[0]] > g.times[g.edges[1]]).sum())},
            'splits': {s: {'labeled': int(g.mask(s).sum()), 'illicit': int((g.labels[g.mask(s)] == 1).sum())} for s in ['train', 'validation', 'test']},
            'limitations': ['No customer identity, KYC, sanctions, exact calendar dates or interpretable currency amounts', 'Anonymized features; illicit labels are benchmark categories, not proof of a crime']}

def synthetic_fixture(root: Path, seed=17):
    """Small independent time-step networks, exclusively for software tests."""
    root.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(seed)
    rows, labels, edges = [], [], []
    for t in [1, 10, 20, 29, 30, 34, 35, 40, 49]:
        for j in range(20):
            ident = t * 100 + j
            illicit = j < 5
            x = rng.normal(0, .5, 165)
            x[:5] += 1.5 * illicit
            rows.append([ident, t, *x])
            labels.append([ident, '1' if illicit else ('unknown' if j == 19 else '2')])
            edges.append([ident, t * 100 + (j + 1) % 20])
            if illicit:
                edges.append([ident, t * 100 + (j + 2) % 5])
    pd.DataFrame(rows).to_csv(root / FILES[0], index=False, header=False)
    pd.DataFrame(edges, columns=['txId1', 'txId2']).to_csv(root / FILES[1], index=False)
    pd.DataFrame(labels, columns=['txId', 'class']).to_csv(root / FILES[2], index=False)
    (root / 'manifest.json').write_text(json.dumps({'kind': 'synthetic_test', 'seed': seed}), encoding='utf-8')
