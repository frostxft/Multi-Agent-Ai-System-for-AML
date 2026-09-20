import argparse
import json
from dataclasses import replace
from pathlib import Path
from .config import Settings
from .data import load_graph, describe, synthetic_fixture
from .model import train, seed_everything

def main():
    p = argparse.ArgumentParser(description='Team Zen AML prototype')
    p.add_argument('command', choices=['inspect', 'train', 'evaluate', 'demo', 'synthetic'])
    p.add_argument('--data', type=Path)
    p.add_argument('--artifacts', type=Path)
    p.add_argument('--epochs', type=int, default=25)
    p.add_argument('--cases', type=int, default=4)
    args = p.parse_args()
    s = Settings()
    if args.data:
        s = replace(s, data_dir=args.data)
    if args.artifacts:
        s = replace(s, artifact_dir=args.artifacts)
    if args.command == 'synthetic':
        if not args.data:
            p.error('synthetic requires explicit --data to avoid writing benchmark directory')
        if any(args.data.iterdir()) if args.data.exists() else False:
            p.error('synthetic output directory must be empty')
        synthetic_fixture(args.data)
        print('Created SYNTHETIC TEST fixture at', args.data)
        return
    if args.command == 'evaluate':
        print((s.artifact_dir / 'evaluation.json').read_text())
        return
    seed_everything(17)
    graph = load_graph(s.data_dir)
    if args.command == 'inspect':
        report = describe(graph)
        s.artifact_dir.mkdir(parents=True, exist_ok=True)
        (s.artifact_dir / 'data_profile.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
        print(json.dumps(report, indent=2))
    elif args.command == 'train':
        report = train(graph, s.artifact_dir, epochs=args.epochs)
        print(json.dumps({k: report[k] for k in ['model_id', 'gat', 'baseline', 'false_positive_change']}, indent=2))
    else:
        import numpy as np
        from .demo import select_transactions, validate_case, SELECTION_RULE
        from .pipeline import Pipeline
        pipeline = Pipeline(graph, s)
        # Select by model score and temporal holdout only, never by ground-truth labels.
        scores = np.load(s.artifact_dir / 'scores.npy')
        targets = select_transactions(graph, scores, pipeline.detector.threshold, args.cases)
        chosen = []
        for target in targets:
            case = pipeline.create(target, 'demo-cli')
            chosen.append(validate_case(case, pipeline.store))
            print(json.dumps(chosen[-1]), flush=True)
        (s.artifact_dir / 'demo_run.json').write_text(json.dumps(chosen, indent=2), encoding='utf-8')
        manifest = {'selection_rule': SELECTION_RULE, 'canonical_transaction': targets[0],
                    'canonical_case_id': chosen[0]['id'], 'transactions': targets,
                    'model_id': pipeline.detector.model_id, 'dataset_fingerprint': graph.fingerprint,
                    'cases': chosen, 'timing_scope': 'Per-stage wall clock; pipeline excludes dataset/checkpoint startup and human review. First narrative includes model loading; later cases use cache.'}
        (s.artifact_dir / 'demo_manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
        if any(not all(c['checks'].values()) for c in chosen):
            raise SystemExit(1)

if __name__ == '__main__':
    main()
