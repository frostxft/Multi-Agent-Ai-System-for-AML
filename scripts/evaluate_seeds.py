"""Fixed protocol replication; preserves original benchmark and rejects output reuse."""
import argparse
import hashlib
import json
import platform
from pathlib import Path
import numpy as np
import torch
from aml.data import load_graph
from aml.model import train


def summarize(reports):
    if len(reports) < 2 or len({r['seed'] for r in reports}) != len(reports):
        raise ValueError('At least two distinct seeds are required')
    return {model: {metric: {
        'mean': float(np.mean([r[model]['test'][metric] for r in reports])),
        'sample_standard_deviation': float(np.std([r[model]['test'][metric] for r in reports], ddof=1)),
        'per_seed': {str(r['seed']): r[model]['test'][metric] for r in reports}}
        for metric in ('precision', 'recall', 'average_precision')}
        for model in ('gat', 'baseline')}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data', type=Path, default=Path('data/elliptic/raw'))
    parser.add_argument('--out', type=Path, default=Path('artifacts/multiseed-20260914'))
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    protocol = {
        'seeds': [17, 29, 43], 'epochs': 25,
        'model_selection': 'No architecture search; fixed original configuration. Best epoch by validation AP; threshold by validation F2.',
        'split': 'train <=29; validation 30..34; evaluation 35..49',
        'test_status': 'Previously observed held-out benchmark, reused only for fixed replication. No fresh external untouched set exists in this dataset.',
        'interpretation': 'Across-seed sample SD (ddof=1), not a confidence interval or uncertainty over temporal populations. No seed is selected as winner.',
        'python': platform.python_version(), 'torch': torch.__version__,
        'model_source_sha256': hashlib.sha256(Path('aml/model.py').read_bytes()).hexdigest()}
    # Freeze protocol before loading data or training; never overwrite the original run.
    (args.out / 'protocol.json').write_text(json.dumps(protocol, indent=2), encoding='utf-8')
    graph = load_graph(args.data)
    reports = [train(graph, args.out / f'seed-{seed}', epochs=protocol['epochs'], seed=seed)
               for seed in protocol['seeds']]
    result = {'protocol': protocol, 'dataset_fingerprint': graph.fingerprint, 'data_kind': graph.kind,
              'summary': summarize(reports), 'runs': reports}
    (args.out / 'evaluation.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps(result['summary'], indent=2))


if __name__ == '__main__':
    main()
