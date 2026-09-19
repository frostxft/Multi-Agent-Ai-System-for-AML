"""Download the real Elliptic CSVs from the official PyG dataset mirror."""
from pathlib import Path
import hashlib
import json
import urllib.request
import zipfile

BASE = 'https://data.pyg.org/datasets/elliptic'
FILES = ['elliptic_txs_features.csv', 'elliptic_txs_edgelist.csv', 'elliptic_txs_classes.csv']

def main():
    root = Path('data/elliptic/raw')
    root.mkdir(parents=True, exist_ok=True)
    manifest = {'kind': 'benchmark', 'publisher': 'Elliptic', 'mirror': BASE, 'files': {}}
    for name in FILES:
        path = root / name
        if not path.exists():
            archive = root / (name + '.zip')
            print('Downloading', name, flush=True)
            urllib.request.urlretrieve(f'{BASE}/{name}.zip', archive)
            with zipfile.ZipFile(archive) as z:
                matches = [n for n in z.namelist() if Path(n).name == name]
                if len(matches) != 1:
                    raise ValueError('Unexpected archive contents')
                with z.open(matches[0]) as src, path.open('wb') as dst:
                    while chunk := src.read(1024 * 1024):
                        dst.write(chunk)
        with path.open('rb') as stream:
            checksum = hashlib.file_digest(stream, 'sha256').hexdigest()
        manifest['files'][name] = {'sha256': checksum, 'bytes': path.stat().st_size}
    (root / 'manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    print(json.dumps(manifest, indent=2))

if __name__ == '__main__':
    main()
