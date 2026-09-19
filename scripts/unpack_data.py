from pathlib import Path
import hashlib
import json
import zipfile

root = Path('data/elliptic/raw')
root.mkdir(parents=True, exist_ok=True)
manifest = {'kind': 'benchmark', 'publisher': 'Elliptic', 'source': 'https://www.kaggle.com/datasets/ellipticco/elliptic-data-set', 'files': {}}
with zipfile.ZipFile('data/elliptic/elliptic.zip') as archive:
    for name in ['elliptic_txs_features.csv', 'elliptic_txs_classes.csv', 'elliptic_txs_edgelist.csv']:
        member, = [n for n in archive.namelist() if Path(n).name == name]
        path = root / name
        with archive.open(member) as src, path.open('wb') as dst:
            while chunk := src.read(1024 * 1024):
                dst.write(chunk)
        with path.open('rb') as stream:
            checksum = hashlib.file_digest(stream, 'sha256').hexdigest()
        manifest['files'][name] = {'sha256': checksum, 'bytes': path.stat().st_size}
(root / 'manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
print(json.dumps(manifest, indent=2))
