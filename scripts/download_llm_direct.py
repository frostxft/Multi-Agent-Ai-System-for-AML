"""Download pinned FLAN-T5 safe weights without Hub HEAD/cache inference."""
from pathlib import Path
import hashlib
import json
import os
import urllib.request

revision = '0fc9ddf78a1e988dac52e2dac162b0ede4fd74ab'
base = os.getenv('HF_ENDPOINT', 'https://huggingface.co').rstrip('/')
root = Path('artifacts/flan-t5-small')
root.mkdir(parents=True, exist_ok=True)
manifest = {'publisher': 'google/flan-t5-small', 'revision': revision, 'download_base': base, 'files': {}}
for name in ['config.json', 'tokenizer_config.json', 'tokenizer.json', 'special_tokens_map.json', 'spiece.model', 'generation_config.json', 'model.safetensors']:
    path = root / name
    if not path.exists():
        url = f'{base}/google/flan-t5-small/resolve/{revision}/{name}'
        print('Downloading', name, flush=True)
        with urllib.request.urlopen(url, timeout=30) as response, open(str(path) + '.partial', 'wb') as output:
            while chunk := response.read(1024 * 1024):
                output.write(chunk)
        Path(str(path) + '.partial').replace(path)
    if name.endswith('.json'):
        json.loads(path.read_text(encoding='utf-8'))
    manifest['files'][name] = {'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'bytes': path.stat().st_size}
(root / 'download_manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
print('Download complete')
