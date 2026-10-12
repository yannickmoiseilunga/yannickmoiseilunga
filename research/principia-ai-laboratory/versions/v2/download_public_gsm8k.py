"""Optional explicit download of OpenAI GSM8K test questions from Hugging Face.

Usage: python -m pip install datasets; python download_public_gsm8k.py
Verify benchmark licence and consent before redistribution; downloaded content is
not included in distributed ZIP. Requires internet. Dataset may be changed upstream.
"""
from pathlib import Path
import json
import re
import hashlib
from datasets import load_dataset

out=Path(__file__).parent/'data'/'gsm8k_test.jsonl'
out.parent.mkdir(parents=True,exist_ok=True)
ds=load_dataset('openai/gsm8k','main',split='test')
count=0
with out.open('w',encoding='utf-8') as f:
    for i,rec in enumerate(ds):
        m=re.search(r'####\s*([-+]?\d[\d,]*(?:\.\d+)?)',rec['answer'])
        if not m:continue
        obj={'id':str(i),'question':rec['question'],'answer':m.group(1).replace(',','')}
        f.write(json.dumps(obj,ensure_ascii=False)+'\n');count+=1
print('Saved',count,'public test questions to',out,'SHA256',hashlib.sha256(out.read_bytes()).hexdigest())
print('WARNING: Never use benchmark test answers for model training or prompt selection.')
