"""V2: falsifiable out-of-dataset, out-of-architecture, double-held-out forecasts.

Independent publicly distributed empirical observations (not synthetic worlds).
All intervention regimes and scientific assumptions are fixed in PROTOCOL before fitting.
Requires numpy, scipy, scikit-learn. No internet at runtime for bundled datasets.
"""
from __future__ import annotations
import csv
import datetime as dt
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import sys
import time
from statistics import NormalDist

PROTOCOL = {
  'version':'2.0.0',
  'protocol_version_fixed_at_release': '2026-10-12',
  'status':'exploratory_development; current code and thresholds are frozen for subsequent prospective replication only',
  'development_datasets_already_inspected':['breast_cancer','wine','iris','digits'],
  'primary_hypotheses': [
   {'id':'R01','name':'Nonlinear architecture exceeds linear classifier','a':['rbf','clean','iid'],'b':['linear','clean','iid'],'mde':.04},
   {'id':'R02','name':'Clean labels exceed 20% corrupted labels','a':['linear','clean','iid'],'b':['linear','label_noise','iid'],'mde':.04},
   {'id':'R03','name':'Full sensing exceeds 40% feature dropout','a':['linear','clean','iid'],'b':['linear','sensor_dropout','iid'],'mde':.04},
   {'id':'R04','name':'Matched-environment evaluation exceeds domain-shift evaluation','a':['linear','clean','iid'],'b':['linear','clean','ood'],'mde':.04},
  ],
  'alpha_family':.05,'power':.80,'sd_of_paired_seed_effect_assumed':.05,
  'min_seeds':20,'split_test_fraction':.25,
  'main_models':['prior','linear','tree','rbf'],
  'interventions':['clean','label_noise','sensor_dropout'],
  'intervention_settings':{'label_flip_probability':.20,'independent_feature_dropout_probability':.40},
  'forecasts':['unseen_dataset','unseen_architecture','unseen_both'],
  'primary_metric':'accuracy','forecast_metric':'mean absolute accuracy error',
  'default_train_cap':900,
  'decision_rule':'supported iff mean effect > MDE, Holm-adjusted one-sided p < 0.05 and dataset-cluster lower 95% CI > 0; otherwise not confirmed; opposite sign explicitly reported',
  'limitations':'Seed repeats are NOT independent datasets. Dataset/feature-defined domains may be confounded. No exact Bayes ceiling for observational real data. A passing small-study result does not prove a universal AI law.'
}

CATALOG = {
 'breast_cancer': {'modality':'tabular','source':'scikit-learn Wisconsin Diagnostic Breast Cancer','domain_feature':1,'domain_definition':'median of mean texture (original feature 1)','source_url':'https://scikit-learn.org/stable/modules/generated/sklearn.datasets.load_breast_cancer.html'},
 'wine': {'modality':'tabular','source':'UCI Wine chemical analysis via scikit-learn','domain_feature':2,'domain_definition':'median ash content (original feature 2)','source_url':'https://scikit-learn.org/stable/modules/generated/sklearn.datasets.load_wine.html'},
 'iris': {'modality':'tabular','source':'Fisher iris measurements via scikit-learn','domain_feature':1,'domain_definition':'median sepal width (original feature 1)','source_url':'https://scikit-learn.org/stable/modules/generated/sklearn.datasets.load_iris.html'},
 'digits': {'modality':'image_as_pixels','source':'UCI optical handwritten digits via scikit-learn','domain_feature':'ink','domain_definition':'median total ink intensity of 8x8 image','source_url':'https://scikit-learn.org/stable/modules/generated/sklearn.datasets.load_digits.html'},
}

# Optional public sources. These are downloaded by the user on their own machine only
# when explicitly selected; no proprietary model or special API key is required.
OPENML_CATALOG={
 'openml_diabetes': {'openml_id':37,'modality':'tabular','source':'OpenML Pima diabetes','domain_feature_name':'plas',
    'source_url':'https://www.openml.org/d/37','domain_definition':'numeric glucose median; feature-defined covariate shift'},
 'openml_credit_g':{'openml_id':31,'modality':'tabular','source':'OpenML German credit','domain_feature_name':'duration',
    'source_url':'https://www.openml.org/d/31','domain_definition':'numeric loan-duration median; feature-defined covariate shift'},
 'openml_adult':{'openml_id':1590,'modality':'tabular','source':'OpenML Adult income','domain_feature_name':'age',
    'source_url':'https://www.openml.org/d/1590','domain_definition':'numeric age median; feature-defined covariate shift'},
}


CUSTOM_SOURCES={}


def register_custom_csv(path,target,domain_column,train_domain=None):
    """Register user-owned, real site/time-grouped observations in this process.

    CSV columns must be numeric other than target and domain. The target is 0/1,
    the user chooses what counts as the training environment. Only the fingerprint,
    not the raw CSV itself, is exported into the evidence archive.
    """
    import numpy as np
    path=Path(path)
    if not path.is_file():raise ValueError('CSV not found')
    if path.stat().st_size>30_000_000:raise ValueError('CSV >30 MB; sample locally or import via research script')
    from collections import Counter
    with path.open('r',encoding='utf-8-sig',newline='') as f:
        reader=csv.DictReader(f)
        if not reader.fieldnames or target not in reader.fieldnames or domain_column not in reader.fieldnames:
            raise ValueError('Select present target and domain column names')
        features=[c for c in reader.fieldnames if c not in (target,domain_column)]
        if not 1<=len(features)<=250:raise ValueError('1 to 250 numeric feature columns required')
        xs=[];ys=[];ds=[]
        for i,row in enumerate(reader,2):
            try:
                y=int(row[target]);values=[float(row[f]) for f in features]
                if y not in (0,1) or not all(math.isfinite(x) for x in values):raise ValueError('nonbinary target or nonfinite feature')
            except (ValueError,TypeError) as exc:raise ValueError(f'CSV row {i}: {exc}') from exc
            xs.append(values);ys.append(y);ds.append(row[domain_column])
            if len(xs)>200000:raise ValueError('Dataset exceeds 200k rows')
    if len(xs)<100:raise ValueError('At least 100 rows are required for this strict study')
    domains=sorted(set(ds))
    if len(domains)<2:raise ValueError('Domain column needs two or more domain values')
    base=train_domain if train_domain is not None else domains[0]
    if base not in domains:raise ValueError('Selected training domain not present')
    X=np.asarray(xs,dtype=float);y=np.asarray(ys,dtype=int);domain=np.asarray([int(v!=base) for v in ds],dtype=int)
    if (domain==0).sum()<45 or (domain==1).sum()<12:raise ValueError('Train/test domain too small')
    if len(set(y[domain==0]))!=2:raise ValueError('Training domain needs both target classes')
    digest=hashlib.sha256(path.read_bytes()).hexdigest();name='csv_'+digest[:10]
    metadata={'source':path.name,'source_type':'user_csv_real_domain',
      'source_sha256':digest,'samples':len(xs),'features':len(features),
      'feature_columns':features,'domain_column':domain_column,'training_domain':base,
      'heldout_domains':[v for v in domains if v!=base],'modality':'tabular',
      'domain_definition':'user-supplied domain label; no test labels used in building domain',
      'class_balance':float(y.mean())}
    CUSTOM_SOURCES[name]=(X,y,domain,metadata)
    return name


def power_plan(sd=.05,mde=.04,alpha=.05,power=.80,n_tests=4,min_seeds=20):
    """Prospective normal approximation for 1-sided paired mean, Bonferroni conservatism.
    Not a claim that the specified SD assumption holds across real task families.
    """
    if min(sd,mde,alpha,power)<=0 or alpha>=1 or power>=1 or n_tests<1:
        raise ValueError('Invalid prospective power assumptions')
    n=int(math.ceil(((NormalDist().inv_cdf(1-alpha/n_tests)+NormalDist().inv_cdf(power))*sd/mde)**2))
    return {'assumed_sd':sd,'minimum_detectable_effect':mde,'alpha_family':alpha,
       'alpha_per_comparison':alpha/n_tests,'target_power':power,'comparison_count':n_tests,
       'normal_approx_seeds':n,'chosen_seeds':max(min_seeds,n),
       'interpretation':'Planning calculation for FUTURE independent studies. Development runs inspected the four bundled datasets, so their results must not be relabelled as preregistered confirmation. Estimated SD is an assumption.'}


def require_sklearn():
    try:
        import numpy, scipy, sklearn
        return numpy,scipy,sklearn
    except ImportError as exc:
        raise RuntimeError('V2 empirical experiments need numpy, scipy and scikit-learn. Run install_research.bat (Windows), or python -m pip install -r requirements-research.txt') from exc


def dataset_load(name):
    np,sp,sk = require_sklearn()
    from sklearn import datasets
    if name in CUSTOM_SOURCES:return CUSTOM_SOURCES[name]
    loaders={'breast_cancer':datasets.load_breast_cancer,
             'wine':datasets.load_wine,'iris':datasets.load_iris,'digits':datasets.load_digits}
    if name in OPENML_CATALOG:
        try:import pandas as pd
        except ImportError as exc:raise RuntimeError('For OpenML datasets, install pandas using requirements-research.txt') from exc
        from sklearn.datasets import fetch_openml
        info=OPENML_CATALOG[name]
        try: bunch=fetch_openml(data_id=info['openml_id'],as_frame=True,parser='auto')
        except Exception as exc:raise RuntimeError(f"OpenML download failed for {name} (id={info['openml_id']}): {exc}") from exc
        frame=bunch.data.copy()
        raw=pd.Series(bunch.target).astype(str).str.strip()
        if name=='openml_diabetes': positive={'tested_positive','1','positive'}
        elif name=='openml_credit_g': positive={'bad','2','1'}
        else: positive={'>50k','>50k.','1'}
        y=np.array([int(v.lower() in positive) for v in raw],dtype=np.int64)
        if min(np.bincount(y,minlength=2))<10:
            values=raw.value_counts().index.tolist()
            raise ValueError(f'OpenML target encoding unrecognised: {values!r}; explicit mapping required')
        # A deterministic row cap for mid-sized data prevents CPU exhaustion.
        if len(frame)>10000:
            rng=np.random.default_rng(20261012)
            ids=np.sort(rng.choice(len(frame),10000,replace=False))
            frame=frame.iloc[ids].reset_index(drop=True);y=y[ids]
        col=info['domain_feature_name']
        if col not in frame.columns:
            col=next((c for c in frame if pd.api.types.is_numeric_dtype(frame[c])),None)
        if col is None:raise ValueError('No observed numeric field for domain separation')
        z=pd.to_numeric(frame[col],errors='coerce').fillna(pd.to_numeric(frame[col],errors='coerce').median()).to_numpy()
        # Encoding here observes unlabeled feature categories from the full public dataset.
        # This is a TRANSDUCTIVE encoding (disclosed in reports), never target-label information.
        frame=pd.get_dummies(frame,columns=list(frame.select_dtypes(exclude=['number','bool']).columns),dtype=float)
        frame=frame.apply(pd.to_numeric,errors='coerce')
        frame=frame.fillna(frame.median()).fillna(0)
        X=frame.to_numpy(dtype=float)
        if X.shape[1]>250:raise ValueError('OpenML transformed input exceeds laptop limit of 250 features')
        domain=(z>float(np.median(z))).astype(int)
        fingerprint=hashlib.sha256(X.tobytes()+y.tobytes()).hexdigest()
        return X,y,domain,{'sha256_values':fingerprint,'samples':len(y),'features':X.shape[1],
          'class_balance':float(y.mean()),'observed_domain_column':col,
          'transductive_feature_vocabulary':True,**info}
    if name not in loaders: raise ValueError('Dataset is not in fixed catalog: '+name)
    bunch=loaders[name]()
    X=np.asarray(bunch.data,dtype=float)
    raw=np.asarray(bunch.target,dtype=int)
    if name=='wine': y=(raw==0).astype(int)
    elif name=='iris':y=(raw==0).astype(int)
    elif name=='digits':y=(raw%2==0).astype(int)
    else:y=raw
    f=CATALOG[name]['domain_feature']
    z=X.sum(axis=1) if f=='ink' else X[:,f]
    # This is an explicit COVARIATE-defined domain, not independently collected sites.
    domain=(z>float(np.median(z))).astype(int)
    # File fingerprint is computed from the full public observations and fixed labels.
    fingerprint=hashlib.sha256(X.tobytes()+y.tobytes()).hexdigest()
    return X,y,domain,{'sha256_values':fingerprint,'samples':len(y),'features':X.shape[1],
         'class_balance':float(y.mean()),**CATALOG[name]}


def build_model(name,seed):
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
    from sklearn.linear_model import LogisticRegression
    from sklearn.dummy import DummyClassifier
    from sklearn.tree import DecisionTreeClassifier
    from sklearn.kernel_approximation import RBFSampler
    if name=='prior':return DummyClassifier(strategy='prior')
    if name=='linear':return make_pipeline(StandardScaler(),LogisticRegression(max_iter=180,solver='liblinear',random_state=seed))
    if name=='tree':return DecisionTreeClassifier(max_depth=6,min_samples_leaf=4,random_state=seed)
    if name=='rbf':return make_pipeline(StandardScaler(),RBFSampler(gamma=.05,n_components=120,random_state=seed),LogisticRegression(max_iter=160,solver='liblinear',random_state=seed))
    raise ValueError('Unknown fixed architecture '+name)


ARCH_DESC={'prior':(.0,.0,.0),'linear':(.33,.0,1.0),'tree':(.55,1.,.5),'rbf':(.75,1.,1.),
          'weak_to_strong':(.75,1.,1.)}


def make_splits(X,y,domain,seed,cap):
    import numpy as np
    from sklearn.model_selection import train_test_split
    rng=np.random.default_rng(seed)
    low=np.flatnonzero(domain==0); high=np.flatnonzero(domain==1)
    if len(low)<45 or len(high)<12:raise ValueError('Domain groups are too small')
    a,b=train_test_split(low,test_size=.25,random_state=seed,stratify=y[low] if min(np.bincount(y[low],minlength=2))>=4 else None)
    if len(a)>cap:a=rng.choice(a,cap,replace=False)
    # High-domain evaluation is never part of fitting. Independent sample from original dataset.
    if len(np.unique(y[a]))<2:raise ValueError('Training domain contains only one label; not evaluable')
    return np.asarray(a),np.asarray(b),high


def train_info_proxy(X,y,idx,seed):
    """Quantities available before training the target learner or inspecting any target labels.
    Stratified 2-fold nearest-neighbour evaluation WITHIN the training-domain sample.
    An empirical learnability proxy, NOT the true Bayes information ceiling.
    """
    import numpy as np
    from sklearn.model_selection import StratifiedKFold,cross_val_score
    from sklearn.neighbors import KNeighborsClassifier
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
    xv=X[idx];yv=y[idx]
    from sklearn.metrics import mutual_info_score
    # Sample class information only, not mutual information between inputs and target.
    p=float(yv.mean());entropy=0 if p in (0.,1.) else -p*math.log2(p)-(1-p)*math.log2(1-p)
    cv=StratifiedKFold(2,shuffle=True,random_state=seed)
    kn=make_pipeline(StandardScaler(),KNeighborsClassifier(n_neighbors=5))
    score=cross_val_score(kn,xv,yv,cv=cv,n_jobs=1,scoring='accuracy')
    return {'train_cv_knn':float(score.mean()),'label_entropy':entropy,'train_pos_rate':p,
            'n_train':len(idx),'n_features':X.shape[1]}


def shift_stat(X,train,test):
    """Unsupervised covariate shift proxy; test labels are NOT accessed."""
    import numpy as np
    m=X[train].mean(axis=0);s=X[train].std(axis=0)+1e-3
    delta=np.clip((X[test].mean(axis=0)-m)/s,-3,3)
    return float(min(5.,np.sqrt(np.mean(delta*delta))))


def preprocessor(X_train,X_eval,mode,seed):
    """Intervention on observed features; mask is generated from independent RNGs.
    The zero mask represents an unavailable reading, not a retrained imputer.
    """
    import numpy as np
    if mode!='sensor_dropout':return X_train,X_eval
    a=np.random.default_rng(seed+641).random(X_train.shape)>=.40
    b=np.random.default_rng(seed+1597).random(X_eval.shape)>=.40
    return X_train*a,X_eval*b


def evaluate_binary(model,X,y):
    import numpy as np
    p=np.asarray(model.predict_proba(X))[:,1]
    p=np.clip(p,1e-5,1-1e-5)
    pred=(p>=.5).astype(int)
    return {'accuracy':float((pred==y).mean()),'brier':float(np.mean((p-y)**2)),
            'n_test':int(len(y)),'mean_confidence':float(np.mean(np.maximum(p,1-p))),
            'mean_predicted_positive':float(p.mean())}


def architecture_probe(model_id,Xtrain,true_labels,fit_labels,seed):
    """Two-fold out-of-fit predictions using labeled training-domain observations ONLY.

    External held-out domain labels never enter this probe. For correction experiments,
    the held-out probe labels are clean, whereas fold-fit labels are corrupted.
    This estimates demonstrated competence; it is NOT a full-data test result.
    """
    import numpy as np
    from sklearn.model_selection import StratifiedKFold
    cv=StratifiedKFold(n_splits=2,shuffle=True,random_state=seed+7)
    correct=[];bs=[]
    for a,b in cv.split(Xtrain,true_labels):
        m=build_model(model_id,seed+len(correct)+1)
        if len(np.unique(fit_labels[a]))<2:
            pred=np.full(len(b),float(np.mean(fit_labels[a])))
        else:
            m.fit(Xtrain[a],fit_labels[a]);pred=m.predict_proba(Xtrain[b])[:,1]
        correct.extend(list(((pred>=.5).astype(int)==true_labels[b]).astype(int)))
        bs.extend(list((pred-true_labels[b])**2))
    return {'train_probe_accuracy':float(np.mean(correct)),
            'train_probe_brier':float(np.mean(bs))}


def _single_rows(name,X,y,dom,seed,cap,progress=None):
    import numpy as np
    train,iid,ood=make_splits(X,y,dom,seed,cap)
    info=train_info_proxy(X,y,train,seed)
    rows=[]
    for mode in PROTOCOL['interventions']:
        yfit=y[train].copy()
        if mode=='label_noise':
            flips=np.random.default_rng(seed*31+829).random(len(yfit))<.20
            yfit[flips]=1-yfit[flips]
        else:flips=np.zeros(len(yfit),bool)
        for model_id in PROTOCOL['main_models']:
            model=build_model(model_id,seed)
            Xtr,_=preprocessor(X[train],X[iid],mode,seed)
            probes=architecture_probe(model_id,Xtr,y[train],yfit,seed)
            t0=time.perf_counter();model.fit(Xtr,yfit);fit_s=time.perf_counter()-t0
            for domain,ids in [('iid',iid),('ood',ood)]:
                _,Xte=preprocessor(X[train],X[ids],mode,seed+ (0 if domain=='iid' else 10007))
                stats=evaluate_binary(model,Xte,y[ids])
                row={'dataset':name,'seed':int(seed),'model':model_id,'intervention':mode,
                  'domain':domain,'fit_seconds':round(fit_s,6),'n_train':len(train),
                  'n_test':len(ids),'label_fidelity':round(1-float(flips.mean()),5),
                  'sensor_fidelity':.60 if mode=='sensor_dropout' else 1.,
                  'shift_proxy':round(shift_stat(X,train,ids),6),
                  **info,**probes,**stats}
                rows.append(row)
    return rows


def law_features(rows):
    import numpy as np
    result=[]
    for r in rows:
        arch,nonlinear,regularized=ARCH_DESC[r['model']]
        result.append([math.log1p(r['n_train']),math.log1p(r['n_features']),
            r['train_cv_knn'],r['train_probe_accuracy'],r['train_probe_brier'],
            r['label_entropy'],r['train_pos_rate'],
            r['sensor_fidelity'],r['label_fidelity'],r['shift_proxy'],
            arch,nonlinear,regularized,float(r['domain']=='ood'),
            float(r['intervention']=='label_noise')])
    return np.asarray(result,dtype=float)


def _choose_correction_weight(X,y,rows,train_mask,regime):
    """Nested meta-validation *only* on the outer training group. Pure probe is allowed.
    The shrinkage parameter is chosen before target-dataset/architecture test labels
    are ever consulted. Weights are intentionally restricted to [0,1].
    """
    import numpy as np
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
    from sklearn.linear_model import Ridge
    train_ids=np.flatnonzero(train_mask)
    datasets=sorted({rows[int(i)]['dataset'] for i in train_ids})
    archs=sorted({rows[int(i)]['model'] for i in train_ids})
    if len(datasets)<2 or len(archs)<2:return 0.,{'reason':'insufficient_meta_groups'}
    probe=np.array([r['train_probe_accuracy'] for r in rows])
    residual=y-probe
    holdouts=[]
    if regime=='unseen_dataset':
        holdouts=[np.array([rows[int(i)]['dataset']==d for i in train_ids]) for d in datasets]
    elif regime=='unseen_architecture':
        holdouts=[np.array([rows[int(i)]['model']==a for i in train_ids]) for a in archs]
    else:
        holdouts=[np.array([rows[int(i)]['dataset']==d and rows[int(i)]['model']==a for i in train_ids]) for d in datasets for a in archs]
    fold_preds=[]
    for hm in holdouts:
        inner_test=train_ids[hm]
        if regime=='unseen_both':
            d=rows[int(inner_test[0])]['dataset']; a=rows[int(inner_test[0])]['model']
            inner_fit=np.array([i for i in train_ids if rows[int(i)]['dataset']!=d and rows[int(i)]['model']!=a])
        else:inner_fit=train_ids[~hm]
        if len(inner_fit)<30 or len(inner_test)==0:continue
        m=make_pipeline(StandardScaler(),Ridge(alpha=100.))
        m.fit(X[inner_fit],residual[inner_fit])
        fold_preds.append((probe[inner_test],m.predict(X[inner_test]),y[inner_test]))
    if len(fold_preds)<2:return 0.,{'reason':'no_internal_folds'}
    candidates=(0.,.1,.25,.5,1.)
    errors={}
    for weight in candidates:
        # Hierarchical validation: each withheld dataset/arch condition equal weight.
        losses=[float(np.mean(np.abs(np.clip(pr+weight*correction,0,1)-truth))) for pr,correction,truth in fold_preds]
        errors[weight]=float(np.mean(losses))
    chosen=min(candidates,key=lambda w:(errors[w],w))
    return chosen,{'inner_group_count':len(fold_preds),'inner_loss_by_weight':{str(k):v for k,v in errors.items()}}


def law_forecast(rows,progress=None):
    """Strict exclusion of the entire held-out dataset and/or architecture FROM fitting.
    Reused target labels across settings are evaluated only after all model fits.
    Output is observational forecast accuracy, not a physics law or a Bayes proof.
    """
    import numpy as np
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
    from sklearn.linear_model import Ridge
    from scipy.stats import t
    X=law_features(rows); y=np.array([r['accuracy'] for r in rows])
    ds=sorted({r['dataset'] for r in rows});arch=sorted({r['model'] for r in rows});predictions=[];groups=[]
    for regime in PROTOCOL['forecasts']:
        combos=([(d,None) for d in ds] if regime=='unseen_dataset' else
           [(None,a) for a in arch] if regime=='unseen_architecture' else
           [(d,a) for d in ds for a in arch])
        for d,a in combos:
            if regime=='unseen_dataset':
                test=np.array([r['dataset']==d for r in rows]);train=~test
            elif regime=='unseen_architecture':
                test=np.array([r['model']==a for r in rows]);train=~test
            else:
                test=np.array([r['dataset']==d and r['model']==a for r in rows]);
                train=np.array([r['dataset']!=d and r['model']!=a for r in rows])
            if train.sum()<30 or test.sum()==0:continue
            # Predefined mechanistic correction law: training-only empirical probe +
            # learned correction for environment, reward and sensing conditions.
            residual=y-np.array([r['train_probe_accuracy'] for r in rows])
            weight,meta_selection=_choose_correction_weight(X,y,rows,train,regime)
            m=make_pipeline(StandardScaler(),Ridge(alpha=100.))
            m.fit(X[train],residual[train])
            probe=np.array([rows[int(k)]['train_probe_accuracy'] for k in np.flatnonzero(test)])
            yp=np.clip(probe+weight*m.predict(X[test]),0.,1.)
            base=float(np.mean(y[train]))
            indices=np.flatnonzero(test)
            for idx,estimated in zip(indices,yp):
                row=rows[int(idx)]
                predictions.append({'test_type':regime,'held_dataset':d or '-',
                  'held_architecture':a or '-','dataset':row['dataset'],'model':row['model'],
                  'seed':row['seed'],'intervention':row['intervention'],'domain':row['domain'],
                  'observed':row['accuracy'],'predicted':float(estimated),
                  'baseline_predicted':base,'probe_only_prediction':row['train_probe_accuracy'],
                  'absolute_error':abs(float(estimated)-row['accuracy']),
                  'baseline_absolute_error':abs(base-row['accuracy']),
                  'probe_only_absolute_error':abs(row['train_probe_accuracy']-row['accuracy'])})
            chunk=[p for p in predictions[-len(indices):]]
            groups.append({'test_type':regime,'held_dataset':d,'held_architecture':a,
                'n_evaluations':len(chunk),'correction_weight':weight,'inner_selection':meta_selection,
                'law_mae':float(np.mean([p['absolute_error'] for p in chunk])),
                'baseline_mae':float(np.mean([p['baseline_absolute_error'] for p in chunk])),
                'probe_only_mae':float(np.mean([p['probe_only_absolute_error'] for p in chunk]))})
    summary=[]
    for regime in PROTOCOL['forecasts']:
        subset=[g for g in groups if g['test_type']==regime]
        # Equal weight per independent heldout unit, not a pooled seed-weighted estimate.
        gains=[g['probe_only_mae']-g['law_mae'] for g in subset]
        if regime=='unseen_both':
            # Dataset is the primary independent source cluster; held architectures
            # within a dataset are correlated rather than 16 independent domains.
            means=[float(np.mean([g['probe_only_mae']-g['law_mae'] for g in subset if g['held_dataset']==d])) for d in ds]
        else:means=gains
        if len(means)>1:
            se=float(np.std(means,ddof=1)/math.sqrt(len(means)))
            ci=[float(np.mean(means)-t.ppf(.975,len(means)-1)*se),
                float(np.mean(means)+t.ppf(.975,len(means)-1)*se)]
        else:ci=[None,None]
        summary.append({'test_type':regime,'held_out_groups':len(subset),
            'independent_source_clusters_for_ci':len(means),
            'gain_over_probe_cluster_ci95':ci,
            'gain_over_probe_directionally_confirmed':ci[0] is not None and ci[0]>0,
            'law_macro_mae':float(np.mean([g['law_mae'] for g in subset])) if subset else None,
            'baseline_macro_mae':float(np.mean([g['baseline_mae'] for g in subset])) if subset else None,
            'probe_only_macro_mae':float(np.mean([g['probe_only_mae'] for g in subset])) if subset else None,
            'improvement_macro_mae':float(np.mean([g['baseline_mae']-g['law_mae'] for g in subset])) if subset else None,
            'improvement_over_probe_mae':float(np.mean([g['probe_only_mae']-g['law_mae'] for g in subset])) if subset else None})
    return {'summary':summary,'groups':groups,'predictions':predictions,
      'rule':'LODO excludes ALL final-test observations of one dataset; LOAO excludes ALL final-test observations of one architecture; double excludes both from fitting. Training-only 2-fold probes of new architectures ARE permitted. Nested group holdouts inside outer training select a correction strength, including zero; no target test labels are used.'}


def primary_tests(rows,plan):
    import numpy as np
    from scipy.stats import ttest_1samp,t
    from collections import defaultdict
    look={(r['dataset'],r['seed'],r['model'],r['intervention'],r['domain']):r for r in rows}
    results=[]
    for h in PROTOCOL['primary_hypotheses']:
        grouped=defaultdict(list)
        for dataset,seed,model,intervention,domain in look:
            if (model,intervention,domain)!=tuple(h['a']):continue
            a=look[(dataset,seed,*h['a'])]
            b=look.get((dataset,seed,*h['b']))
            if b is not None:grouped[dataset].append(float(a['accuracy']-b['accuracy']))
        all_effects=[v for effects in grouped.values() for v in effects]
        mean=float(np.mean(all_effects)) if all_effects else None
        dataset_effects=np.array([np.mean(v) for v in grouped.values()])
        if len(dataset_effects)>1:
            sem=float(dataset_effects.std(ddof=1)/np.sqrt(len(dataset_effects)))
            lower=float(dataset_effects.mean()-t.ppf(.975,len(dataset_effects)-1)*sem)
            upper=float(dataset_effects.mean()+t.ppf(.975,len(dataset_effects)-1)*sem)
        else:lower=upper=None
        # p-value computed using dataset as primary independent unit; seeds are replications.
        p=float(ttest_1samp(dataset_effects,0,alternative='greater').pvalue) if len(dataset_effects)>1 else 1.
        results.append({'id':h['id'],'name':h['name'],'effect':mean,'minimum_effect':h['mde'],
            'dataset_count':len(dataset_effects),'paired_seeds_per_dataset':{k:len(v) for k,v in grouped.items()},
            'cluster_ci95':[lower,upper],'dataset_cluster_p_one_sided':p,
            'dataset_effects':{k:float(np.mean(v)) for k,v in grouped.items()},
            'power_plan_seeds':plan['chosen_seeds'],'status':'not_confirmed'})
    # Holm step-down on dataset-cluster p-values, NOT seed-wise pseudoindependence.
    order=sorted(range(len(results)),key=lambda i:results[i]['dataset_cluster_p_one_sided'])
    running=0.
    for rank,j in enumerate(order):
        running=max(running,min(1.,results[j]['dataset_cluster_p_one_sided']*(len(order)-rank)))
        results[j]['holm_adjusted_p']=float(running)
    for z in results:
        if z['effect'] is None:z['status']='insufficient_data'
        elif z['effect']<0:z['status']='opposite_direction'
        elif z['effect']>=z['minimum_effect'] and z['cluster_ci95'][0] is not None and z['cluster_ci95'][0]>0 and z['holm_adjusted_p']<.05:
            z['status']='supported_within_tested_datasets'
        elif z['effect']<z['minimum_effect']:
            z['status']='effect_below_predeclared_threshold'
        else:z['status']='not_confirmed'
    return results


def weak_to_strong(rows=None):
    # Implemented in a separate empirical text/model evaluation rather than mixing synthetic supervisor and real evidence.
    return {'status':'excluded_from_primary_tests','reason':'No supervised language model is silently substituted for the weak human evaluator. An optional genuine weak-supervision study must specify distinct weak and strong models.'}


def run_real_study(seeds=None,master_seed=42,datasets=None,cap=900,progress=None):
    np,sp,sk=require_sklearn()
    plan=power_plan()
    if seeds is None:seeds=plan['chosen_seeds']
    if not 2<=seeds<=100:raise ValueError('Seed count must be 2 to 100; research-confirmatory requires at least '+str(plan['chosen_seeds']))
    if not 100<=cap<=3000:raise ValueError('Training sample cap must be 100 to 3000')
    names=datasets or list(CATALOG)
    if len(names)<2:raise ValueError('Use at least two datasets for held-out-domain forecasting')
    if any(name not in CATALOG and name not in OPENML_CATALOG and name not in CUSTOM_SOURCES for name in names):raise ValueError('Unregistered dataset selection')
    started=time.perf_counter();rows=[];metadata={}; failures=[];count=0;total=len(names)*seeds
    for name in names:
        X,y,domain,details=dataset_load(name)
        metadata[name]=details
        for i in range(seeds):
            seed=master_seed+1009*i
            try:rows.extend(_single_rows(name,X,y,domain,seed,cap))
            except (ValueError,RuntimeError) as exc:failures.append({'dataset':name,'seed':seed,'error':str(exc)})
            count+=1
            if progress:progress({'completed':count,'total':total+2,'detail':f'{name}: seed {i+1}/{seeds}'})
    if not rows:raise RuntimeError('No valid empirical experiments; examine dataset/domain label overlap')
    if progress:progress({'completed':total+1,'total':total+2,'detail':'Fitting out-of-domain predictive law'})
    forecasts=law_forecast(rows)
    findings=primary_tests(rows,plan)
    if progress:progress({'completed':total+2,'total':total+2,'detail':'Writing reproducible findings'})
    development_used=any(name in PROTOCOL['development_datasets_already_inspected'] for name in names)
    phase='exploratory_development' if development_used else 'prospective_candidate_requires_external_registration'
    return {'protocol':PROTOCOL,'power_plan':plan,'settings':{'phase':phase,'seeds':seeds,'master_seed':master_seed,'train_cap':cap,'datasets':names,
      'package_versions':{'python':sys.version,'numpy':np.__version__,'scipy':sp.__version__,'sklearn':sk.__version__},
      'elapsed_seconds':round(time.perf_counter()-started,2),
      'confirmatory_seed_count_met':seeds>=plan['chosen_seeds']},
      'data_provenance':metadata,'rows':rows,'forecast':forecasts,'hypotheses':findings,
      'failures':failures,'separate_local_model_track':weak_to_strong(),
      'interpretation':'Empirical stress-test of a proposed forecast law. Does not establish universal guarantees. No observational Bayes limit is assumed.'}


def save_real_study(result,outdir):
    root=Path(outdir);root.mkdir(parents=True,exist_ok=True)
    stamp=dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    dirname='real_v2_'+stamp+'_s'+str(result['settings']['master_seed'])
    target=root/dirname
    if target.exists():target=root/(dirname+'_'+os.urandom(3).hex())
    target.mkdir()
    def dump(name,obj): (target/name).write_text(json.dumps(obj,indent=2,ensure_ascii=False,allow_nan=False),encoding='utf-8')
    def csv_dump(name,records):
        if not records:return
        with (target/name).open('w',newline='',encoding='utf-8') as f:
            writer=csv.DictWriter(f,list(records[0]));writer.writeheader();writer.writerows(records)
    dump('PROTOCOL_FROZEN.json',result['protocol']);dump('power_analysis.json',result['power_plan'])
    dump('provenance.json',result['data_provenance']);dump('manifest.json',result['settings'])
    dump('primary_findings.json',result['hypotheses']);dump('forecast_summary.json',result['forecast']['summary'])
    dump('forecast_groups.json',result['forecast']['groups']);dump('excluded_runs.json',result['failures'])
    csv_dump('observations.csv',result['rows']);csv_dump('law_predictions.csv',result['forecast']['predictions'])
    report=[]
    report+=['# Principia AI Lab V2: Independent Empirical Replication','',
       '**Not a proof of a universal law.** Forecaster predictions on held-out datasets and architectures.','',
       f"**Research phase: {result['settings']['phase']}.** The bundled datasets were observed during model development. Treat them as exploratory, NOT confirmatory preregistered evidence.",'',
       f"Seeds per dataset: {result['settings']['seeds']} · dataset count: {len(result['settings']['datasets'])} · observations: {len(result['rows'])} · excluded failed runs: {len(result['failures'])}",'',
       f"Prospective planning for *future* studies: MDE {result['power_plan']['minimum_detectable_effect']:.1%} · assumed paired SD {result['power_plan']['assumed_sd']:.1%} · Holm family alpha 0.05 · minimum planned seeds {result['power_plan']['chosen_seeds']}",'',
       f"Planned seed requirement met: **{result['settings']['confirmatory_seed_count_met']}**",'',
       '## Held-out predictive tests','',
       '| Generalisation test | Candidate MAE | Constant baseline | Probe-only baseline | vs probe (positive preferred) |','|---|---:|---:|---:|---:|']
    for z in result['forecast']['summary']:
        report.append(f"| {z['test_type']} | {z['law_macro_mae']:.4f} | {z['baseline_macro_mae']:.4f} | {z['probe_only_macro_mae']:.4f} | {z['improvement_over_probe_mae']:+.4f} |")
    report+=['','### Uncertainty around improvement over probe-only baseline','',
      '| Holdout | Gain (positive preferred) | Approximate 95% cluster CI | Cluster count |','|---|---:|---:|---:|']
    for z in result['forecast']['summary']:
        lo,hi=z['gain_over_probe_cluster_ci95']
        ci=f'[{lo:+.3f}, {hi:+.3f}]' if lo is not None else 'not estimable'
        report.append(f"| {z['test_type']} | {z['improvement_over_probe_mae']:+.4f} | {ci} | {z['independent_source_clusters_for_ci']} |")
    report+=['','## Release-protocol primary hypotheses (development data; not prospectively confirmed)','',
      '| ID | Effect (accuracy points) | 95% CI across datasets | Holm p | Verdict |','|---|---:|---:|---:|---|']
    for z in result['hypotheses']:
        lo,hi=z['cluster_ci95']; ci=f'[{lo:+.3f}, {hi:+.3f}]' if lo is not None else 'not estimable'
        report.append(f"| {z['id']} | {z['effect']:+.4f} | {ci} | {z['holm_adjusted_p']:.3f} | {z['status']} |")
    report+=['','## Provenance and statistical caveats','',
      '- Observations come from independent publicly distributed measured datasets, with binary target remappings stated in source.',
      '- OOD here means **feature-median-defined covariate groups**, not independent hospitals, locations, or collection periods.',
      '- Model fitting and preprocessing never use the labels of either test subset.',
      '- No empirical dataset is assumed to have a known Bayes ceiling.',
      '- Dataset-level cluster intervals (only four datasets by default) are the primary inferential summary; repeated random seeds are not independent real-world domains.',
      '- Four bundled data sources were inspected while designing and tuning the predictor. A genuine prospective confirmation MUST use newly registered, uninspected sources; development results are not confirmatory.',
      '- The normal-approximation power design uses an assumed seed-level SD and does NOT ensure adequate power across the four independent source datasets.',
      '- The mechanism descriptors use known intervention settings and a cross-validated learnability estimate from labeled TRAIN samples; they are not available for completely unlabeled new tasks.',
      '- The candidate law has been allowed to probe each unseen architecture on training-only labels; this is NOT zero-shot architecture prediction. Probe-only accuracy is separately reported as a demanding baseline.',
      '- All per-condition and negative results, including unsuccessful forecasts, remain available in CSV.',
      '- No claim about consciousness, universal general intelligence, architecture-independent emergence or causality is made.',
      '- Dataset choice, hyperparameters, transform mapping and minimum effect sizes are documented in PROTOCOL_FROZEN.json as RELEASE SETTINGS for future replications, not falsely claimed to have been preregistered before model development.',
      '- Selected OpenML datasets (if any) use feature-vocabulary one-hot encoding learned from unlabeled covariates, a transductive choice disclosed in provenance; never interpret this as a fully prospective live deployment.',
      '', '## Next falsification gate','',
      'A credible stronger claim requires more independent families, genuinely observed site/time domains, blinded held-out task registration, and a forecast law that beats baseline with uncertainty intervals across such families.',
      '']
    (target/'REPORT.md').write_text('\n'.join(report),encoding='utf-8')
    dump('dashboard.json',{'type':'real_v2','settings':result['settings'], 'power':result['power_plan'],
       'hypotheses':result['hypotheses'],'summary':result['forecast']['summary'],
       'groups':result['forecast']['groups'],'sample_rows':result['rows'][:80],
       'limitations':result['interpretation'],'failures':result['failures']})
    import zipfile
    archive=root/(target.name+'.zip')
    with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=5) as z:
        for f in target.iterdir():z.write(f,arcname=target.name+'/'+f.name)
    return {'directory':str(target),'archive':str(archive),'rows':len(result['rows']),'summary':result['forecast']['summary']}
