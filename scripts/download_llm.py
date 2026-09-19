"""Explicit one-time download; runtime inference uses local_files_only."""
from pathlib import Path
import os
os.environ['HF_HUB_DISABLE_XET'] = '1'
os.environ['HF_HOME'] = str(Path('artifacts/hf_cache').resolve())
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

target = Path('artifacts/flan-t5-small')
tokenizer = AutoTokenizer.from_pretrained('google/flan-t5-small')
model = AutoModelForSeq2SeqLM.from_pretrained('google/flan-t5-small')
target.mkdir(parents=True, exist_ok=True)
tokenizer.save_pretrained(target)
model.save_pretrained(target)
(target / 'source.txt').write_text('https://huggingface.co/google/flan-t5-small\nApache-2.0\n', encoding='utf-8')
print('Saved real local language model:', target)
