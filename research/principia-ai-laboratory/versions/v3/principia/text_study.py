"""Optional REAL text modality from 20 Newsgroups, never pooled with numeric v2 law.
Downloads via sklearn only if explicitly requested, and uses upstream train/test split.
"""
from __future__ import annotations
import csv
import datetime as dt
import hashlib
import json
from pathlib import Path
import re
import time


def run_text_study(seeds=20,master_seed=42,progress=None):
    if not 2<=seeds<=100:raise ValueError('Allowed text replication seeds 2..100')
    try:
        import numpy as np
        from sklearn.datasets import fetch_20newsgroups
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.pipeline import make_pipeline
        from sklearn.linear_model import LogisticRegression
        from sklearn.naive_bayes import MultinomialNB
        from sklearn.svm import LinearSVC
        from sklearn.model_selection import train_test_split
    except ImportError as exc:raise RuntimeError('Research dependencies missing. Run install_research first.') from exc
    cats=['rec.sport.baseball','sci.space']
    tr=fetch_20newsgroups(subset='train',categories=cats,remove=('headers','footers','quotes'),download_if_missing=True)
    te=fetch_20newsgroups(subset='test',categories=cats,remove=('headers','footers','quotes'),download_if_missing=True)
    text_train=list(tr.data);truth=np.asarray(tr.target,dtype=int)
    text_test=list(te.data);test_y=np.asarray(te.target,dtype=int)
    if tr.target_names!=te.target_names:raise RuntimeError('Upstream train/test categories inconsistent')
    models={'logistic':lambda s:LogisticRegression(max_iter=240,solver='liblinear',random_state=s),
        'naive_bayes':lambda s:MultinomialNB(alpha=.5),
        'linear_svm':lambda s:LinearSVC(C=.7,random_state=s,max_iter=2500)}
    # Restrict test set to the official published test partition, not heldout examples
    # from the same train partition. Header/quotations removed to reduce shortcuts.
    rows=[];start=time.perf_counter();total=seeds*3*3;done=0
    rng=np.random.default_rng(master_seed)
    def weaken_text(text,seed):
        local=np.random.default_rng(seed)
        toks=text.split()
        return ' '.join(t for t in toks if local.random()>=.40)
    for i in range(seeds):
        seed=master_seed+i*1009
        idx=np.arange(len(text_train))
        a,b=train_test_split(idx,test_size=.20,random_state=seed,stratify=truth)
        # Only 80% of upstream train may fit. The remaining 20% are not used.
        docs=[text_train[j] for j in a];labels=truth[a].copy()
        for condition in ('clean','label_noise','token_dropout'):
            labs=labels.copy();items=docs;outs=text_test
            if condition=='label_noise':
                rr=np.random.default_rng(seed+23);mask=rr.random(len(labs))<.20;labs[mask]=1-labs[mask]
            if condition=='token_dropout':
                items=[weaken_text(t,seed+11+j) for j,t in enumerate(items)]
                outs=[weaken_text(t,seed+100023+j) for j,t in enumerate(outs)]
            for name,creator in models.items():
                t0=time.perf_counter()
                m=make_pipeline(TfidfVectorizer(min_df=2,max_features=7000,ngram_range=(1,2),sublinear_tf=True),creator(seed))
                m.fit(items,labs);prediction=m.predict(outs)
                rows.append({'modality':'text','source':'20newsgroups_official_test','seed':seed,'model':name,
                 'intervention':condition,'domain':'official_test','accuracy':float(np.mean(prediction==test_y)),
                 'n_train':len(items),'n_test':len(test_y),'fit_seconds':round(time.perf_counter()-t0,4)})
                done+=1
                if progress:progress({'completed':done,'total':total,'detail':f'Text · seed {i+1}/{seeds} · {name} · {condition}'})
    return {'type':'real_text_v2','settings':{'seeds':seeds,'seed':master_seed,'categories':cats,
        'elapsed_seconds':round(time.perf_counter()-start,2),'official_train_count':len(tr.data),'official_test_count':len(te.data)},
       'rows':rows,'limitations':['A genuine text modality, but not an independent site/time OOD split.',
          'Model tuning was frozen in advance; train/test source split kept separate.',
          'The text baseline has not been incorporated into the numeric three-quantity predictive law.',
          'Repeated seeds are not independent data collection sources.'],
       'source':'https://scikit-learn.org/stable/modules/generated/sklearn.datasets.fetch_20newsgroups.html'}


def save_text(result,outdir):
    import zipfile
    folder=Path(outdir)/('text_v2_'+dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ'))
    folder.mkdir(parents=True,exist_ok=True)
    (folder/'dashboard.json').write_text(json.dumps({'type':'real_text_v2',**result},indent=2),encoding='utf-8')
    (folder/'study.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    with (folder/'observations.csv').open('w',encoding='utf-8',newline='') as f:
        writer=csv.DictWriter(f,list(result['rows'][0]));writer.writeheader();writer.writerows(result['rows'])
    ar=folder.with_suffix('.zip')
    with zipfile.ZipFile(ar,'w',compression=zipfile.ZIP_DEFLATED) as z:
        for f in folder.iterdir():z.write(f,arcname=folder.name+'/'+f.name)
    return {'directory':str(folder),'archive':str(ar)}
