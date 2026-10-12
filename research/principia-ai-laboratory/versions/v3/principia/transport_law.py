"""V3: conditional Information--Transport Law (ITL); see V3_PROTOCOL_FROZEN.md.

Meta-model is fitted to ONLY the four V2 development sources. External source
outcomes MUST NOT influence any hyperparameter or model weights. The old V2
records are used without recalculating their predictions. The V3 confirmation
sources from independent bundled statistical datasets are not used for fitting.

A probabilistic *candidate*, not a theorem: logistic odds of error transported
from a training-only capability probe, with covariate displacement, label/sensor
fidelity and empirical learnability. We explicitly test concept-shift impossibility.
"""
from __future__ import annotations
import csv
import datetime
import hashlib
import json
import math
import os
from pathlib import Path
import statistics
import zipfile

import numpy as np
from scipy.special import expit,logit
from scipy.stats import t as student_t
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from . import real_study as v2

ROOT=Path(__file__).resolve().parent.parent
V2_RESEARCH_CSV=ROOT/'frozen_development_v2.csv'
RESEARCH_SOURCES=['breast_cancer','wine','iris','digits']
EXTERNAL_SOURCES=['anes96','randhie','fair']
ALL_MODELS=['prior','linear','tree','rbf','gnb','knn']
EXTERNAL_MODELS=['gnb','knn']
REGIMES=['clean','label_noise','sensor_dropout']
PROTOCOL={
 'version':'3.0.0','candidate':'Information-Transport Log-Odds Law (ITL)',
 'origin':'four already-inspected v2 development datasets; no v3 data used in fitting',
 'evaluation_sources': EXTERNAL_SOURCES,
 'evaluation_architectures':EXTERNAL_MODELS,
 'primary':'MAE gain over train-only probe, macro by independent dataset',
 'secondary':'MAE gain over V2 residual Ridge; shift-conditional coverage',
 'success_threshold_mae_gain':.01,'min_seeds':20,'alpha':.05,
 'bootstrap_interval_percentiles':[.025,.975],
 'model_features':['constant','shift','shift_square','shift_x_probe_confidence','info_gap','probe_brier','label_loss','sensor_loss','log_sample_efficiency'],
 'ridge_alpha':50.,'coefficient_shrinkage':.35,
 'v2_reference':'train-only probe + nested shrinkage Ridge correction',
 'test_regimes':['unseen_dataset','unseen_architecture','unseen_both'],
 'external_domain_note':'ANES96 population median and Fair marriage duration median are feature-derived; RANDHIE idp group is a real observed regime, but is not independently collected site/time. Not WILDS or DomainBed.',
 'interpretation':'Exploratory external sample: datasets selected by author before inspecting results, but no public timestamped preregistration and the architecture/model may be revised afterwards. Independent replications remain needed.',
 'unknown_concept_shift':'Impossible to bound without assumptions/label access. Empirical uncertainty bands are descriptive and NOT distribution-free validity guarantees.'
}


def source_data(name):
    """Public real-life survey datasets distributed with statsmodels. No network."""
    import statsmodels.api as sm
    if name=='anes96':
        d=sm.datasets.anes96.load_pandas().data.copy()
        y=d.pop('vote').to_numpy().astype(int)
        group_col=d.pop('popul').to_numpy(dtype=float)
        X=d.select_dtypes(include='number').to_numpy(dtype=float)
        # Population grouping appears as a real recorded quantity, not independent site.
        domain=(group_col>np.median(group_col)).astype(int)
    elif name=='randhie':
        d=sm.datasets.randhie.load_pandas().data.copy()
        y=(d.pop('mdvis').to_numpy(dtype=float)>0).astype(int)
        domain=d.pop('idp').to_numpy().astype(int)
        X=d.select_dtypes(include='number').to_numpy(dtype=float)
    elif name=='fair':
        d=sm.datasets.fair.load_pandas().data.copy()
        y=(d.pop('affairs').to_numpy(dtype=float)>0).astype(int)
        period=d.pop('yrs_married').to_numpy(dtype=float)
        domain=(period>np.median(period)).astype(int)
        X=d.select_dtypes(include='number').to_numpy(dtype=float)
    elif name in RESEARCH_SOURCES:
        return v2.dataset_load(name)[:3]
    else:raise KeyError(name)
    X=np.nan_to_num(X,nan=0.,posinf=0.,neginf=0.)
    assert len(np.unique(y))==2 and len(np.unique(domain))==2
    return X,y,domain


def v3_model(name,seed):
    if name in v2.PROTOCOL['main_models']:
        return v2.build_model(name,seed)
    from sklearn.naive_bayes import GaussianNB
    from sklearn.neighbors import KNeighborsClassifier
    from sklearn.preprocessing import StandardScaler
    from sklearn.pipeline import make_pipeline
    if name=='gnb':return make_pipeline(StandardScaler(),GaussianNB(var_smoothing=1e-8))
    if name=='knn':return make_pipeline(StandardScaler(),KNeighborsClassifier(n_neighbors=9,weights='distance'))
    raise ValueError(name)


def exact_features(row):
    """Predeclared mechanism proxies. No knowledge of held-out ground truth."""
    p=float(row['train_probe_accuracy']); q=float(row['train_cv_knn'])
    dx=float(row['shift_proxy']); b=float(row['train_probe_brier'])
    fidelity=float(row['label_fidelity']); sensing=float(row['sensor_fidelity'])
    return np.asarray([
      1., dx,dx*dx,dx*abs(p-.5),q-p,b,1.-fidelity,1.-sensing,
      math.log1p(float(row['n_train']))/(1.+math.log1p(float(row['n_features']))),
    ],dtype=float)


def fits_and_predicts(source_rows,target_rows):
    """Fit once on V2 known rows. Predict rows without consulting their outcomes."""
    src_features=np.stack([exact_features(r) for r in source_rows]); trg_features=np.stack([exact_features(r) for r in target_rows]);
    # Logit of error is additive under assumed multiplicative change in error odds.
    source_p=np.clip([float(r['train_probe_accuracy']) for r in source_rows],.005,.995)
    source_y=np.clip([float(r['accuracy']) for r in source_rows],.005,.995)
    delta=logit(1.-source_y)-logit(1.-source_p)
    pipe=make_pipeline(StandardScaler(),Ridge(alpha=PROTOCOL['ridge_alpha']))
    pipe.fit(src_features,delta)
    new_probe=np.clip([float(r['train_probe_accuracy']) for r in target_rows],.005,.995)
    logit_error=logit(1.-new_probe) + PROTOCOL['coefficient_shrinkage']*pipe.predict(trg_features)
    out=1.-expit(logit_error)
    return np.clip(out,0,1)


def v2_features_with_unseen(rows):
    # Retains V2 feature ordering. New models receive architecture descriptors
    # fixed at a neutral setting rather than being assigned a seen family's ID.
    features=[]
    for r in rows:
        desc=v2.ARCH_DESC.get(r['model'],(.50,.50,.75))
        features.append([
          math.log1p(float(r['n_train'])),math.log1p(float(r['n_features'])),
          float(r['train_cv_knn']),float(r['train_probe_accuracy']),float(r['train_probe_brier']),
          float(r['label_entropy']),float(r['train_pos_rate']),
          float(r['sensor_fidelity']),float(r['label_fidelity']),float(r['shift_proxy']),
          *desc,float(r['domain']=='ood'),float(r['intervention']=='label_noise')
        ])
    return np.asarray(features,dtype=float)


def previous_law(source_rows,target_rows):
    """Independent V2 reference, shrinkage frozen on V2 development meta-validation."""
    all_rows=source_rows+target_rows
    X=v2_features_with_unseen(all_rows)
    y=np.array([float(r['accuracy']) for r in source_rows])
    residual=y-np.array([float(r['train_probe_accuracy']) for r in source_rows])
    m=make_pipeline(StandardScaler(),Ridge(alpha=100.))
    m.fit(X[:len(source_rows)],residual)
    # V2 nested chosen correction strength, computed only using V2 source data.
    # For prospective transfer the fixed regime is 'unseen_both'.
    numeric_rows=[dict(r, train_probe_accuracy=float(r['train_probe_accuracy'])) for r in source_rows]
    w,selection=v2._choose_correction_weight(X[:len(source_rows)],y,numeric_rows,
                       np.ones(len(source_rows),dtype=bool),'unseen_both')
    p=np.array([float(r['train_probe_accuracy']) for r in target_rows])
    return np.clip(p+w*m.predict(X[len(source_rows):]),0,1),w,selection


def make_rows(name,seed,cap=500,test_cap=700,which_models=None):
    """New rows are produced from source-domain fits; no target labels in predictors."""
    from sklearn.model_selection import train_test_split
    X,y,dom=source_data(name)
    rng=np.random.default_rng(seed)
    low=np.flatnonzero(dom==0); high=np.flatnonzero(dom==1)
    if len(low)<45 or len(high)<25:raise ValueError('Insufficient domain-specific samples')
    train,iid=train_test_split(low,test_size=.25,random_state=seed,
      stratify=y[low] if min(np.bincount(y[low],minlength=2))>=5 else None)
    if len(train)>cap:train=rng.choice(train,cap,replace=False)
    if len(iid)>test_cap:iid=rng.choice(iid,test_cap,replace=False)
    if len(high)>test_cap:high=rng.choice(high,test_cap,replace=False)
    if len(np.unique(y[train]))<2:raise ValueError('One class on source domain')
    info=v2.train_info_proxy(X,y,train,seed)
    result=[]
    for mode in REGIMES:
        yfit=y[train].copy()
        flips=np.random.default_rng(seed*31+829).random(len(yfit))<.2 if mode=='label_noise' else np.zeros(len(yfit),bool)
        if mode=='label_noise':yfit[flips]=1-yfit[flips]
        for model_name in (which_models or ALL_MODELS):
            Xtrain,_=v2.preprocessor(X[train],X[iid],mode,seed)
            # Two-fold out-of-fit calibration, on training-only labelled data
            # Reimplement v2 probe with v3 architecture construction.
            from sklearn.model_selection import StratifiedKFold
            cv=StratifiedKFold(2,shuffle=True,random_state=seed+7)
            true_y=y[train]; scores=[]; brier=[]
            for j,(a,b) in enumerate(cv.split(Xtrain,true_y)):
                model=v3_model(model_name,seed+j+1)
                if len(np.unique(yfit[a]))<2: pr=np.repeat(float(yfit[a].mean()),len(b))
                else:
                    model.fit(Xtrain[a],yfit[a]);pr=model.predict_proba(Xtrain[b])[:,1]
                scores.extend(((pr>=.5).astype(int)==true_y[b]).astype(float))
                brier.extend((pr-true_y[b])**2)
            probe={'train_probe_accuracy':float(np.mean(scores)),'train_probe_brier':float(np.mean(brier))}
            model=v3_model(model_name,seed);model.fit(Xtrain,yfit)
            for eval_label,ids in [('iid',iid),('ood',high)]:
                _,Xe=v2.preprocessor(X[train],X[ids],mode,seed+(0 if eval_label=='iid' else 10007))
                observed=v2.evaluate_binary(model,Xe,y[ids]);shift=v2.shift_stat(X,train,ids)
                result.append({'dataset':name,'seed':seed,'model':model_name,
                   'intervention':mode,'domain':eval_label,'n_train':len(train),'n_test':len(ids),
                   'label_fidelity':round(1.-flips.mean(),5),'sensor_fidelity':.6 if mode=='sensor_dropout' else 1.,
                   'shift_proxy':round(shift,6),**info,**probe,**observed})
    return result


def source_rows_from_v2():
    if not V2_RESEARCH_CSV.is_file():raise FileNotFoundError('Missing frozen V2 development measurements: '+str(V2_RESEARCH_CSV))
    with V2_RESEARCH_CSV.open(newline='') as f:return list(csv.DictReader(f))


def summarize(rows):
    result=[]
    for group in ['new_datasets_known_arch','new_arch_known_datasets','double_unseen']:
        rs=[r for r in rows if r['regime']==group]
        clusters=sorted(set(r['dataset'] for r in rs))
        differences=[]; macros=[]
        for cluster in clusters:
            part=[r for r in rs if r['dataset']==cluster]
            p_mae=float(np.mean([abs(r['probe_prediction']-r['observed']) for r in part]))
            t_mae=float(np.mean([abs(r['transport_prediction']-r['observed']) for r in part]))
            v_mae=float(np.mean([abs(r['v2_prediction']-r['observed']) for r in part]))
            differences.append(p_mae-t_mae)
            macros.append({'dataset':cluster,'n':len(part),'probe_mae':p_mae,'v2_mae':v_mae,'itl_mae':t_mae,
                           'itl_gain_over_probe':p_mae-t_mae,'itl_gain_over_v2':v_mae-t_mae})
        ci=[None,None]
        if len(differences)>=2:
            se=np.std(differences,ddof=1)/np.sqrt(len(differences));bound=student_t.ppf(.975,len(differences)-1)*se
            ci=[float(np.mean(differences)-bound),float(np.mean(differences)+bound)]
        result.append({'regime':group,'independent_dataset_clusters':len(clusters),'measurements':len(rs),
          'probe_macro_mae':float(np.mean([x['probe_mae'] for x in macros])) if macros else None,
          'v2_macro_mae':float(np.mean([x['v2_mae'] for x in macros])) if macros else None,
          'itl_macro_mae':float(np.mean([x['itl_mae'] for x in macros])) if macros else None,
          'itl_gain_over_probe':float(np.mean(differences)) if differences else None,
          'itl_gain_vs_probe_ci95':ci,
          'decision':'not confirmed' if not differences or ci[0] is None or ci[0]<=0 or np.mean(differences)<.01 else 'exploratory signal; needs independent confirmation',
          'by_dataset':macros})
    return result


def no_free_lunch_witness():
    """A constructive falsification of unconditional unseen-world prediction.
    Two worlds have exactly equal source evidence and unlabeled test points.
    Changing ONLY test labels changes the desired accuracy, unseen by predictor.
    """
    from sklearn.linear_model import LogisticRegression
    rg=np.random.default_rng(20261012)
    X=rg.normal(size=(800,4)); y=(X[:,0]+.2*X[:,1]>0).astype(int)
    tr=np.arange(400); te=np.arange(400,800)
    model=LogisticRegression().fit(X[tr],y[tr]);h=model.predict(X[te])
    a=float((h==y[te]).mean());b=float((h==(1-y[te])).mean())
    return {'equal_visible_train_and_unlabeled_test':True,'world_one_accuracy':a,'world_two_accuracy':b,
      'mean_of_accuracies':(a+b)/2,'minimax_absolute_error_lower_bound':abs(a-b)/2,
      'logical_conclusion':'An identical forecast must be wrong by at least this amount in at least one world; changing P(Y|X) is not identifiable from unlabeled X.'}


def run(seeds=20,cap=500,progress=None):
    if seeds<20:raise ValueError('Prospective v3 protocol requires >=20 seeds')
    source=source_rows_from_v2()
    # Restrict source to frozen 4 and seed independent models.
    assert set(r['dataset'] for r in source)==set(RESEARCH_SOURCES)
    seeds_list=[42+i*1009 for i in range(seeds)]
    saved=[]; tasks=[]
    for name in RESEARCH_SOURCES:
        for s in seeds_list:tasks.append((name,s,EXTERNAL_MODELS))
    for name in EXTERNAL_SOURCES:
        for s in seeds_list:tasks.append((name,s,['prior','linear']+EXTERNAL_MODELS))
    for j,(name,seed,models) in enumerate(tasks):
        obs=make_rows(name,seed,cap,which_models=models)
        saved.extend(obs)
        if progress and ((j+1)%8==0 or j+1==len(tasks)):progress({'completed':j+1,'total':len(tasks),'detail':f'{name}: {j+1}/{len(tasks)} runs'})
    p_itl=fits_and_predicts(source,saved)
    p_v2,w,v2_tuning=previous_law(source,saved)
    scored=[]
    for row,itl,ref in zip(saved,p_itl,p_v2):
        r={k:row[k] for k in ('dataset','model','domain','intervention','seed','n_test','accuracy','train_probe_accuracy','shift_proxy','train_probe_brier')}
        r['observed']=float(r.pop('accuracy'))
        r['probe_prediction']=float(r.pop('train_probe_accuracy'))
        r['transport_prediction']=float(itl)
        r['v2_prediction']=float(ref)
        r['abs_error_itl']=abs(itl-r['observed'])
        r['abs_error_probe']=abs(r['probe_prediction']-r['observed'])
        r['abs_error_v2']=abs(ref-r['observed'])
        if row['dataset'] in RESEARCH_SOURCES:r['regime']='new_arch_known_datasets'
        elif row['model'] in EXTERNAL_MODELS:r['regime']='double_unseen'
        else:r['regime']='new_datasets_known_arch'
        scored.append(r)
    # Empirical error quantiles on v2 SOURCE held-out folds, never new target outcomes.
    source_pred=fits_and_predicts(source,source) # in-sample only: explicitly optimistic
    in_sample_err=np.abs(source_pred-np.array([float(r['accuracy']) for r in source]))
    rad=float(np.quantile(in_sample_err,.90))
    for p in scored:
        p['exploratory_source_fit_90pct_radius']=rad
        p['inside_source_fit_interval']=(p['observed']>=max(0,p['transport_prediction']-rad) and p['observed']<=min(1,p['transport_prediction']+rad))
    coverage=[{'regime':name,'empirical_coverage':float(np.mean([p['inside_source_fit_interval'] for p in scored if p['regime']==name]))} for name in ('new_datasets_known_arch','new_arch_known_datasets','double_unseen')]
    return {'protocol':PROTOCOL,'seeds':seeds_list,'v2_weight':w,'v2_tuning':v2_tuning,'summary':summarize(scored),
      'interval_radius_from_source_in_sample_optimistic':rad,'interval_coverage':coverage,
      'impossibility':no_free_lunch_witness(),
      'rows':scored,
      'source_csv_sha256':hashlib.sha256(V2_RESEARCH_CSV.read_bytes()).hexdigest()}


def save(result,outdir=None):
    root=Path(outdir or ROOT/'reports');root.mkdir(exist_ok=True,parents=True)
    name='transport_v3_'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    folder=root/name;folder.mkdir()
    (folder/'protocol.json').write_text(json.dumps(result['protocol'],indent=2))
    (folder/'summary.json').write_text(json.dumps({k:v for k,v in result.items() if k!='rows'},indent=2))
    with (folder/'all_predictions.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(result['rows'][0]));writer.writeheader();writer.writerows(result['rows'])
    lines=['# Principia V3 — conditional Information-Transport Law','',
      '**Status: exploratory; not proof of a universal law.**','',
      'V3 candidate is frozen and fitted exclusively on Version 2 development source measurements.','',
      '| Evaluation | Train-only probe MAE | V2 MAE | V3 ITL MAE | V3 gain vs probe | 95% CI (source clusters) |',
      '|---|---:|---:|---:|---:|---|']
    for r in result['summary']:
        interval=r['itl_gain_vs_probe_ci95']
        fmt='N/A' if interval[0] is None else f'[{interval[0]:+.4f}, {interval[1]:+.4f}]'
        lines.append(f"| {r['regime']} ({r['independent_dataset_clusters']} sources) | {r['probe_macro_mae']:.4f} | {r['v2_macro_mae']:.4f} | {r['itl_macro_mae']:.4f} | {r['itl_gain_over_probe']:+.4f} | {fmt} |")
    lines+=['','## Prespecified outcome','',
       f"Success threshold: >= {PROTOCOL['success_threshold_mae_gain']:.2f} absolute macro MAE improvement over probe AND cluster-level 95% lower bound > 0.",'']
    for r in result['summary']:
        lines.append(f"- **{r['regime']}**: {r['decision']}.")
        for d in r['by_dataset']:lines.append(f"  - {d['dataset']}: probe={d['probe_mae']:.4f}, ITL={d['itl_mae']:.4f}, V2={d['v2_mae']:.4f}")
    w=result['impossibility']
    lines+=['','## Impossibility witness','',f"Indistinguishable worlds yield accuracies {w['world_one_accuracy']:.4f} and {w['world_two_accuracy']:.4f}, enforcing worst-case point-forecast absolute error >= {w['minimax_absolute_error_lower_bound']:.4f}.",'',
      '## Uncertainty audit','',
      f"In-sample source residual 90th percentile: {result['interval_radius_from_source_in_sample_optimistic']:.4f}; THIS IS NOT a valid 90% predictive interval for arbitrary unseen conditions."]
    for c in result['interval_coverage']:lines.append(f"- {c['regime']}: observed coverage={c['empirical_coverage']:.2%}")
    lines+=['','## Limitations','',
      '- The previously inspected V2 datasets supply all fitted coefficients. No data from these new sources enters candidate fitting.',
      '- Included independently collected surveys do not supply naturally held-out institutions; observational or feature-defined domains are not proof of causal domain robustness.',
      '- 20 random seeds are repeated fits on the same sources, not 20 independent real-world data-generating environments.',
      '- The inference uses a measured two-fold training-only probe of each architecture, not design-only zero-shot inference.',
      '- This conditional candidate cannot identify arbitrary unseen changes in P(Y|X) from X alone.',
      '- Source-fit residual intervals are optimistic and empirical only.',
      '- No conclusions about consciousness or universal artificial intelligence.','']
    (folder/'REPORT.md').write_text('\n'.join(lines))
    (folder/'dashboard.json').write_text(json.dumps({'type':'real_v3','summary':result['summary'],
      'interval_coverage':result['interval_coverage'],'impossibility':result['impossibility'],
      'v2_weight':result['v2_weight'],'seeds':len(result['seeds']),
      'source_csv_sha256':result['source_csv_sha256'],
      'limitations':'EXPLORATORY. Candidate failed the predeclared cross-source confirmation criterion; no universal law is established.'},indent=2))
    archive=root/(name+'.zip')
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=7) as z:
        for f in folder.iterdir():z.write(f,arcname=name+'/'+f.name)
    return {'directory':str(folder),'report':str(folder/'REPORT.md'),'archive':str(archive)}
