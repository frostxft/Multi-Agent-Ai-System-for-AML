"""Explicitly synthetic browser-test environment, separate from benchmark cases."""
from pathlib import Path
from aml.data import synthetic_fixture, load_graph
from aml.model import train
from aml.config import Settings
from aml.pipeline import Pipeline

def main():
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--db', type=Path, help='Separate synthetic test database')
    parser.add_argument('--reference-fixture', default='', help='Explicit synthetic reference JSON snapshot')
    args = parser.parse_args()
    root = Path('artifacts/ui-test')
    raw = root / 'raw'
    if not (raw / 'manifest.json').exists():
        synthetic_fixture(raw)
    g = load_graph(raw)
    if not (root / 'model/gat.pt').exists():
        train(g, root / 'model', epochs=5)
    s = Settings(data_dir=raw, artifact_dir=root / 'model', db_path=args.db or root / 'cases.db', llm_provider='extractive', reference_fixture=args.reference_fixture)
    p = Pipeline(g, s)
    c = p.create('3500', 'synthetic-ui-test-setup')
    print({'case_id': c['id'], 'status': c['status'], 'data_kind': c['data_kind']})

if __name__ == '__main__':
    main()
