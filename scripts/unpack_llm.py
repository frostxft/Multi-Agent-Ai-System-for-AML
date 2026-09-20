"""Extract model assets only, never execute repository-supplied Python."""
from pathlib import Path
import hashlib
import json
import zipfile

root=Path('artifacts/flan-t5-small')
root.mkdir(parents=True,exist_ok=True)
allowed={'config.json','tokenizer_config.json','tokenizer.json','special_tokens_map.json','spiece.model','generation_config.json','model.safetensors','pytorch_model.bin'}
manifest={'publisher_model':'google/flan-t5-small','distribution':'https://www.kaggle.com/datasets/d0rj3228/googleflan-t5-small','mirror_notice':'Third-party distribution; PyTorch weight SHA256 checked against publisher file metadata','publisher_weight_source':'https://huggingface.co/google/flan-t5-small/blob/main/pytorch_model.bin','files':{}}
with zipfile.ZipFile('artifacts/flan-t5-small-kaggle.zip') as z:
    print('Archive model assets:',[n for n in z.namelist() if Path(n).name in allowed])
    for member in z.namelist():
        name=Path(member).name
        if name not in allowed:continue
        path=root/name
        with z.open(member) as src, path.open('wb') as dst:
            while chunk:=src.read(1024*1024):dst.write(chunk)
        with path.open('rb') as stream:
            checksum=hashlib.file_digest(stream,'sha256').hexdigest()
        manifest['files'][name]={'sha256':checksum,'bytes':path.stat().st_size}
for required in ['config.json','spiece.model']:
    if required not in manifest['files']:raise RuntimeError('Required asset missing: '+required)
if not {'model.safetensors','pytorch_model.bin'} & manifest['files'].keys():raise RuntimeError('No model weights')
if manifest['files'].get('pytorch_model.bin',{}).get('sha256')!='4a8c0174fa3ee6fe2ffd0f6e21992d4ca4ad1e9b12bd14155b57479e27f56292':
    raise RuntimeError('Publisher weight checksum mismatch')
(root/'download_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print('Model assets extracted with manifest')
