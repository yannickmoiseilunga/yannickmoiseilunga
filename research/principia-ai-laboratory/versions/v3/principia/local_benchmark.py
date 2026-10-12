"""PRETRAINED MODEL track, always separate from tabular/synthetic findings.

Requires installed local Ollama, public question/ground-truth JSONL. No grade leakage.
Results remain purely observational and benchmark-specific.
"""
from __future__ import annotations
import csv
import hashlib
import json
import math
from pathlib import Path
import re
import time
from .external import ollama_models,ollama_generate

NUMBER=re.compile(r'[-+]?\d[\d,]*(?:\.\d+)?')


def canonical(text):
    text=str(text).strip().replace(',','')
    nums=NUMBER.findall(text)
    # Extract a single answer where possible; free-form extra numbers are ambiguous.
    if re.fullmatch(r'[-+]?\d+(?:\.\d+)?',text):
        try:return str(float(text))
        except ValueError:pass
    return re.sub(r'\s+',' ',text.casefold())


def clean_record(record,i):
    q=record.get('question') or record.get('prompt')
    a=record.get('answer') or record.get('gold') or record.get('truth')
    if q is None or a is None:raise ValueError(f'JSONL line {i}: question and answer required')
    if len(str(q))>6000 or len(str(a))>1200:raise ValueError('Single record too long')
    return {'id':str(record.get('id',i)),'question':str(q),'answer':str(a)}


def run_local_benchmark(model,path,limit=50,progress=None):
    if not 1<=limit<=200:raise ValueError('Limit must be 1..200')
    path=Path(path)
    if path.stat().st_size>15_000_000:raise ValueError('Benchmark JSONL exceeds 15 MB')
    records=[]
    with path.open(encoding='utf-8') as f:
        for i,line in enumerate(f,1):
            if not line.strip():continue
            records.append(clean_record(json.loads(line),i))
            if len(records)>=limit:break
    if not records:raise ValueError('No benchmark questions found')
    models=ollama_models()
    if model not in models:raise ValueError('Install requested model in Ollama first; detected: '+', '.join(models))
    arms={
      'direct':'Solve the following problem and give ONLY the final numeric answer (no explanation).\n\n',
      'verify':'Solve the problem. Check your arithmetic carefully before responding. Give ONLY the final numeric answer (no explanation).\n\n',
    }
    rows=[];t0=time.perf_counter();total=len(records)*len(arms)
    for i,rec in enumerate(records):
        expected=canonical(rec['answer'])
        for arm,pre in arms.items():
            began=time.perf_counter();returned=None;error=None
            try:returned=ollama_generate(model,pre+rec['question'],timeout=120)
            except Exception as exc:error=str(exc)
            output=canonical(returned) if returned is not None else ''
            correct=(output==expected) and not error
            rows.append({'id':rec['id'],'arm':arm,'question':rec['question'],
              'expected':rec['answer'],'model_answer':returned,'correct':bool(correct),
              'format_ok':bool(returned and re.fullmatch(r'[-+]?\d[\d,]*(?:\.\d+)?',returned.strip())),
              'error':error,'seconds':round(time.perf_counter()-began,3)})
            if progress:progress({'completed':len(rows),'total':total,'detail':f'Local {model} · question {i+1}/{len(records)} · {arm}'})
    from collections import defaultdict
    by_arm=defaultdict(list)
    for row in rows:by_arm[row['arm']].append(row)
    summary={arm:{'accuracy':sum(r['correct'] for r in val)/len(val),
                'format_success':sum(r['format_ok'] for r in val)/len(val),
                'requests':len(val),'errors':sum(bool(r['error']) for r in val)} for arm,val in by_arm.items()}
    return {'type':'local_pretrained_model','model':model,'dataset_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
      'dataset_filename':path.name,'count':len(records),'elapsed_seconds':round(time.perf_counter()-t0,2),
      'summary':summary,'rows':rows,'notes':[
       'Local pretrained model results are NOT pooled with synthetic or tabular experiments.',
       'No model finetuning is conducted here. Differences between prompts are not proofs of process-supervision mechanisms.',
       'Exact answer scoring may mark semantically correct differently formatted answers wrong.',
       'No claims of consciousness, agency or universal intelligence.']}


def save_local(result,root):
    import datetime as dt
    import zipfile
    folder=Path(root)/('pretrained_v2_'+dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ'))
    folder.mkdir(parents=True,exist_ok=True)
    (folder/'model_results.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    (folder/'dashboard.json').write_text(json.dumps({'type':'local_pretrained_model',
      'settings':{'model':result['model'],'dataset_sha256':result['dataset_sha256']},
      'summary':result['summary'],'limitations':result['notes']},indent=2),encoding='utf-8')
    with (folder/'answers.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(result['rows'][0]));w.writeheader();w.writerows(result['rows'])
    archive=folder.with_suffix('.zip')
    with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED) as z:
        for f in folder.iterdir():z.write(f,arcname=folder.name+'/'+f.name)
    return {'directory':str(folder),'archive':str(archive)}
