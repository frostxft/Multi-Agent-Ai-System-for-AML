"""Inspect the preserved model on validation data only. No fitting of GAT/test tuning."""
import argparse
import json
import time
from pathlib import Path
import numpy as np
import torch
from aml.data import load_graph
from aml.model import load_model, seed_everything
from aml.diagnostics import threshold_table, operating_points, reliability, calibration_experiment


def analyze(graph, folder):
    model, x, checkpoint, model_id = load_model(graph, folder)
    mask = graph.mask('validation')
    available = (graph.times[graph.edges[0]] <= 34) & (graph.times[graph.edges[1]] <= 34)
    edges = torch.tensor(graph.edges[:, available], dtype=torch.long)
    start = time.perf_counter()
    with torch.no_grad():
        scores = model(x, edges).sigmoid().numpy()[mask]
        reduced = model(x, torch.empty((2, 0), dtype=torch.long)).sigmoid().numpy()[mask]
    baseline = np.load(folder / 'baseline.npz', allow_pickle=False)
    logits = x.numpy()[mask] @ baseline['coef'][0] + baseline['intercept'][0]
    baseline_scores = torch.tensor(logits).sigmoid().numpy()
    y = graph.labels[mask]
    result = {'model_id': model_id, 'dataset_fingerprint': graph.fingerprint, 'data_kind': graph.kind,
              'split': 'validation only, steps 30..34; no test labels/scores used',
              'default_threshold': float(checkpoint['threshold']), 'models': {},
              'topology_intervention': {'label': 'Inference intervention, fixed weights, all explicit edges removed; GAT self-loops retained. Not a retrained no-graph model.',
                                        'original': reliability(y, scores), 'no_explicit_edges': reliability(y, reduced)},
              'inference_and_baseline_seconds': time.perf_counter() - start}
    for name, values in [('gat', scores), ('baseline', baseline_scores)]:
        table = threshold_table(y, values)
        result['models'][name] = {'thresholds': table, 'operating_points': operating_points(table),
                                  'raw_reliability': reliability(y, values),
                                  'calibration': calibration_experiment(y, values, graph.times[mask])}
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data', type=Path, default=Path('data/elliptic/raw'))
    parser.add_argument('--artifacts', type=Path, default=Path('artifacts/benchmark'))
    parser.add_argument('--out', type=Path, default=Path('artifacts/validation-diagnostics-20260915'))
    args = parser.parse_args(); args.out.mkdir(parents=True, exist_ok=False)
    protocol = {'split': 'validation 30..34 only', 'threshold_grid': '.05..95 step .01; lowest threshold wins objective ties',
                'calibration': 'Fit 30..32; assess 33..34. Raw, L2 sigmoid, isotonic; diagnostic only, not deployed.',
                'ablation': 'Fixed original GAT weights, remove explicit edges only; not a training comparison.',
                'deployment': 'Original seed-17 model and threshold unchanged.'}
    (args.out/'protocol.json').write_text(json.dumps(protocol, indent=2), encoding='utf-8')
    seed_everything(17)
    report = analyze(load_graph(args.data), args.artifacts)
    report['protocol'] = protocol
    (args.out/'analysis.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps({name: data['operating_points'] for name,data in report['models'].items()}, indent=2))


if __name__ == '__main__': main()
