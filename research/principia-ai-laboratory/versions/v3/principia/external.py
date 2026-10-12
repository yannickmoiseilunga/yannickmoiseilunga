"""Optional independent evidence: real binary CSV and local Ollama models.

No online APIs. CSV must have a binary numeric target; numeric predictors only.
Ollama is contacted on loopback and never invoked unless explicitly requested.
"""
from __future__ import annotations
import csv
import hashlib
import json
import math
import random
import re
import time
import urllib.error
import urllib.request
from pathlib import Path
from .experiments import subseed, COROLLARY_MAP
from .models import make_model
from .metrics import evaluate


def csv_suite(path,target,domain_column=None,train_domain=None,seed=42,seeds=3):
    path=Path(path)
    with path.open(encoding='utf-8-sig',newline='') as f:
        reader=csv.DictReader(f)
        if not reader.fieldnames or target not in reader.fieldnames: raise ValueError('CSV target column not found')
        columns=[x for x in reader.fieldnames if x not in (target,domain_column)]
        if not columns: raise ValueError('At least one numeric feature column is needed')
        source=list(reader)
    if not 40<=len(source)<=200000: raise ValueError('CSV needs 40 to 200,000 rows')
    data=[]
    for ix,row in enumerate(source):
        try:
            y=int(row[target])
            if str(y)!=row[target].strip() or y not in (0,1): raise ValueError('binary 0/1 target required')
            features=[float(row[col]) for col in columns]
            if not all(math.isfinite(x) for x in features): raise ValueError('non-finite feature')
            dom=row[domain_column] if domain_column else None
        except (ValueError,TypeError) as exc: raise ValueError(f'Bad data in CSV row {ix+2}: {exc}') from exc
        data.append((features,y,dom,ix))
    if len(columns)>40: raise ValueError('Limit features to 40 numeric columns (CPU safety)')
    rows=[]; preds=[]
    for si in range(seeds):
        r=random.Random(subseed(seed,'csv',si))
        if domain_column:
            domains=sorted({d for _,_,d,_ in data})
            if len(domains)<2: raise ValueError('Domain column must have at least two values')
            base=train_domain if train_domain is not None else domains[0]
            if base not in domains: raise ValueError('Train domain not found')
            training=[d for d in data if d[2]==base]; testing=[d for d in data if d[2]!=base]
            label=f'other_domains_v_{base}'
        else:
            shuffled=data[:];r.shuffle(shuffled)
            cut=int(len(data)*.7);training=shuffled[:cut]; testing=shuffled[cut:]
            label='holdout'
        if len(training)>3000:
            r.shuffle(training); training=training[:3000]  # Bounded RAM and CPU on a laptop.
        if len(training)<20 or len(testing)<10: raise ValueError('Insufficient train/test observations for this domain split')
        if len({y for _,y,_,_ in training})!=2: raise ValueError('Both classes must appear in training')
        means=[sum(x[j] for x,_,_,_ in training)/len(training) for j in range(len(columns))]
        scales=[max(1e-10,(sum((x[j]-means[j])**2 for x,_,_,_ in training)/len(training))**.5) for j in range(len(columns))]
        # Means and scales are learned from training only. Prevent leakage.
        standardise=lambda x:[max(-8,min(8,(a-m)/s)) for a,m,s in zip(x,means,scales)]
        xtrain=[standardise(x) for x,_,_,_ in training]; ytrain=[y for _,y,_,_ in training]
        xtest=[standardise(x) for x,_,_,_ in testing];ytest=[y for _,y,_,_ in testing]
        for name in ('prior','linear','interactions','mlp'):
            if name=='mlp' and len(training)>10000: continue
            model=make_model(name,quick=True)
            start=time.perf_counter();model.fit(xtrain,ytrain,subseed(seed,si,'csvmodel',name))
            times=time.perf_counter()-start
            probabilities=[model.predict(x) for x in xtest]
            stats=evaluate(ytest,probabilities)
            rows.append({'experiment':'independent_csv','model':name,'seed':si,'domain':label,
                         'n_train':len(training),'n_features':len(columns),'params':model.params,
                         'ops_proxy':model.steps,'train_seconds':round(times,6),**stats})
            cap=min(len(testing),200)
            for ii in sorted(set(round(i*(len(testing)-1)/max(1,cap-1)) for i in range(cap))):
                _,y,_,original_index=testing[ii]
                preds.append({'experiment':'independent_csv','model':name,'seed':si,'domain':label,
                       'index':original_index,'y':y,'p':round(probabilities[ii],8)})
    digest=hashlib.sha256(path.read_bytes()).hexdigest()
    return {'rows':rows,'predictions':preds,'hypotheses':[],'corollary_map':COROLLARY_MAP,
            'settings':{'preset':'external_csv','seed':seed,'seeds':seeds,'dataset_sha256':digest,
                        'data_filename':path.name,'features':columns,'target':target,
                        'domain_column':domain_column,'train_domain':train_domain,
                        'note':'Local dataset, not synthetic: causal and identifiability assumptions cannot be proved from CSV.'}}


def ollama_models(timeout=3):
    req=urllib.request.Request('http://127.0.0.1:11434/api/tags')
    with urllib.request.urlopen(req,timeout=timeout) as response:
        return [m['name'] for m in json.load(response).get('models',[])]


def ollama_generate(model,prompt,timeout=90):
    req=urllib.request.Request('http://127.0.0.1:11434/api/generate',method='POST',
       data=json.dumps({'model':model,'prompt':prompt,'stream':False,
                        'options':{'temperature':0,'num_predict':120}}).encode(),
       headers={'Content-Type':'application/json'})
    with urllib.request.urlopen(req,timeout=timeout) as response:
        return json.load(response).get('response','').strip()


def ollama_suite(model,count=20,seed=42,progress=None):
    if not 5<=count<=200: raise ValueError('Allowed task count: 5 to 200')
    installed=ollama_models()
    if model not in installed: raise ValueError('The model must be installed in local Ollama. Available: '+', '.join(installed))
    rng=random.Random(seed); items=[]
    for i in range(count):
        a=rng.randint(-15,15);b=rng.randint(-15,15);c=rng.randint(1,8)
        actual=(a+b)*c
        prompt=f'Compute exactly ({a} + {b}) * {c}. Reply with only one integer.'
        t0=time.perf_counter()
        try: text=ollama_generate(model,prompt)
        except Exception as exc:
            items.append({'id':i,'error':str(exc),'question':prompt,'truth':actual});
            if progress:progress({'completed':i+1,'total':count,'detail':'Local model request failed'})
            continue
        m=re.fullmatch(r'\s*[-+]?\d+\s*',text)
        prediction=int(text) if m else None
        items.append({'id':i,'question':prompt,'truth':actual,'raw':text,'answer':prediction,
                      'correct':prediction==actual,'seconds':round(time.perf_counter()-t0,3)})
        if progress:progress({'completed':i+1,'total':count,'detail':'Ollama task '+str(i+1)})
    valid=[x for x in items if 'correct' in x]
    accuracy=sum(x['correct'] for x in valid)/len(valid) if valid else None
    return {'model':model,'count':count,'attempted':len(valid),'accuracy':accuracy,'items':items,
            'limits':'Arithmetic-format benchmark only; not evidence of universal intelligence or identifiability.'}
