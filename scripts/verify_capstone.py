"""Recreate four benchmark cases in a fresh database; never simulate their reviews."""
import argparse
import json
from dataclasses import replace
from pathlib import Path
import numpy as np
from aml.config import Settings
from aml.data import load_graph
from aml.demo import select_transactions, validate_case
from aml.model import seed_everything
from aml.pipeline import Pipeline


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, default=Path('artifacts/capstone-reproduction'))
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    seed_everything(17)
    settings = replace(Settings(), db_path=args.out / 'cases.db', llm_provider='local')
    graph = load_graph(settings.data_dir)
    pipeline = Pipeline(graph, settings)
    manifest = json.loads((settings.artifact_dir / 'demo_manifest.json').read_text())
    targets = select_transactions(graph, np.load(settings.artifact_dir / 'scores.npy'), pipeline.detector.threshold, 4)
    if targets != manifest['transactions']:
        raise RuntimeError('Selection differs from recorded four-case manifest')
    cases = [pipeline.create(target, 'benchmark-reproduction-no-human-decision') for target in targets]
    validations = [validate_case(c, pipeline.store) for c in cases]
    # Reopen persistence through a new pipeline, proving no in-memory case dependency.
    restored = Pipeline(graph, settings)
    for c in cases:
        if restored.store.get(c['id']) != c:
            raise RuntimeError('Persisted case changed across pipeline restart')
    report = {'dataset_fingerprint': graph.fingerprint, 'model_id': pipeline.detector.model_id,
              'transactions_match_canonical_manifest': True, 'persistence_restart_verified': True,
              'database': str(settings.db_path), 'cases': validations}
    (args.out / 'validation.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps(report, indent=2))
    if not all(all(c['checks'].values()) for c in validations):
        raise SystemExit(1)


if __name__ == '__main__':
    main()
