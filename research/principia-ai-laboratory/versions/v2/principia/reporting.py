"""Auditable report outputs: no unsupported 'proof' labels from small samples."""
from __future__ import annotations
import csv
import datetime as dt
import json
import os
from pathlib import Path
from .metrics import mean_ci
from .prediction import cross_condition_predictions


def compile_findings(result):
    by={}
    for row in result['rows']:
        key=(row['experiment'],row['model'],row['domain'])
        by.setdefault(key,[]).append(row)
    findings=[]
    for hypo in result['hypotheses']:
        a=by.get(tuple(hypo['a']),[])
        if not a: continue
        bs=by.get(tuple(hypo['b']),[]) if 'b' in hypo else []
        if hypo.get('metric')=='risk_gain':
            vals=[(1-r['accuracy'])-r['selective_risk_80'] for r in a]
            desc='Reduction in error among most-confident 80% versus all predictions'
        elif 'b' in hypo:
            pairs={r['seed']:r for r in bs}
            if hypo.get('metric')=='brier_advantage':
                vals=[pairs[r['seed']]['brier']-r['brier'] for r in a if r['seed'] in pairs]
                desc='Brier loss(B corrupted) minus Brier loss(A clean); positive means clean correction better'
            else:
                vals=[r['accuracy']-pairs[r['seed']]['accuracy'] for r in a if r['seed'] in pairs]
                desc='Accuracy(A) minus Accuracy(B), paired by random seed'
        else:
            vals=[r['accuracy']-hypo['reference'] for r in a]
            desc='Accuracy minus information-free chance baseline'
        mean,low,high=mean_ci(vals)
        if hypo['direction']=='abs_lt':
            supported=(low is not None and low>-hypo['threshold'] and high<hypo['threshold'])
            contradicted=(low is not None and (low>hypo['threshold'] or high<-hypo['threshold']))
        else:
            supported=low is not None and low>hypo['threshold']
            contradicted=high is not None and high<0
        # Multiple small seeded simulations are not independent confirmations of universal theory.
        status=('consistent (exploratory)' if supported else 'contradicted here' if contradicted else 'inconclusive')
        findings.append({'id':hypo['id'],'name':hypo['name'],'status':status,
                         'effect':mean,'bootstrap_95':[low,high],'threshold':hypo['threshold'],
                         'analysis':desc,'n_seed_pairs':len(vals),'kind':hypo.get('kind','falsifiable'),
                         'caveat':'Seed bootstrap; intervals do not cover sampling/design/benchmark uncertainty.'})
    return findings


def write_csv(filename,rows,preferred=()):
    if not rows: return
    keys=list(preferred)+sorted(set().union(*(set(r) for r in rows))-set(preferred))
    with open(filename,'w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=keys,extrasaction='ignore');w.writeheader();w.writerows(rows)


def save_run(result, root):
    root=Path(root);root.mkdir(parents=True,exist_ok=True)
    findings=compile_findings(result)
    law=cross_condition_predictions(result['rows'])
    # Include a short unique run suffix to prevent overwriting a previous experiment.
    timestamp=dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    base=timestamp+'_'+result['settings']['preset']+'_s'+str(result['settings']['seed'])
    out=root/base; ix=2
    while out.exists(): out=root/(base+'_'+str(ix));ix+=1
    out.mkdir()
    write_csv(out/'observations.csv',result['rows'],('experiment','model','seed','domain','accuracy'))
    write_csv(out/'predictions.csv',result.get('predictions',[]),('experiment','model','seed','domain','index','y','p'))
    write_csv(out/'law_forecasts.csv',law['predictions'],('heldout_experiment','model','seed','predicted','observed','absolute_error'))
    (out/'law_validation.json').write_text(json.dumps(law['summary'],indent=2),encoding='utf-8')
    with open(out/'findings.json','w',encoding='utf-8') as f:json.dump(findings,f,indent=2,allow_nan=False)
    with open(out/'dashboard.json','w',encoding='utf-8') as f:json.dump({'rows':result['rows'],'findings':findings,'settings':result['settings'],'corollary_map':result['corollary_map'],'law_validation':law['summary'],'law_forecasts':law['predictions']},f,allow_nan=False)
    manifest={'created_utc':dt.datetime.now(dt.timezone.utc).isoformat(),
              'settings':result['settings'],'n_observation_rows':len(result['rows']),
              'n_predictions':len(result.get('predictions',[])),
              'prediction_sample':'At most 200 deterministic examples per trial/seed/domain. Evaluation metrics use all test examples.',
              'preregistration':result['hypotheses'],
              'corollary_map':result['corollary_map'],
              'result_limits':['Synthetic controlled worlds; cannot establish universal laws of all AI.',
                               'No frontier LLM reproduction; architectural analogy only.',
                               'Small seed bootstrap not a formal test of theory.',
                               'The known simulation generator supplies ground truth and Bayes ceilings.',
                               'No P values or causal claims beyond randomised synthetic interventions.']}
    with open(out/'manifest.json','w',encoding='utf-8') as f: json.dump(manifest,f,indent=2)
    summary=['# Principia AI Laboratory — Experimental Report','',
             'Generated: '+manifest['created_utc'],'',
             '## Method','',
             'Prespecified synthetic tasks; separate training and test observations; identical master seed for controlled comparisons; '
             'analytic Bayes ceilings where available; multiple seeds; bootstrap over seed-level paired effects.','',
             '## Preregistered hypotheses','',
             '| Hypothesis | Estimated effect | 95% bootstrap interval | Outcome |', '|---|---:|---:|---|']
    for a in findings:
        e=a['effect']; l,h=a['bootstrap_95']
        CI='not estimable' if l is None else f'[{l:+.3f}, {h:+.3f}]'
        summary.append(f"| {a['id']} {a['name']} | {e:+.3f} | {CI} | {a['status']} |")
    if law['summary']['mae'] is not None:
        summary+=['','## Hold-out predictive test', '',
                  f"Condition-out forecast MAE: {law['summary']['mae']:.4f}; Bayes-constrained forecast MAE: {law['summary']['constrained_mae']:.4f}; training-mean baseline MAE: {law['summary']['baseline_mae']:.4f}.",
                  f"Predictions above known Bayes ceiling: {law['summary']['above_bayes_ceiling_predictions']}.",
                  'The forecast is learned from other synthetic conditions using architecture, data count, scenario flags and analytic information ceiling. It is *not* an established law; failed predictions are kept.',
                  'See `law_forecasts.csv` for each observation and `law_validation.json` for summary.']
    summary+=['','**Interpretation:** A result marked “consistent” is compatible with a particular hypothesis in this synthetic study, not proof of a universal law.','',
              '## Core measurable quantities','','1. **Distinguishability**: exact Bayes optimal accuracy and mutual information for discrete generators.',
              '2. **Transformation**: accuracy differences among prior, linear, interaction and small neural engines on parity and sensors.',
              '3. **Correction**: true-world agreement under clean, corrupted and inverted training signals; OOD loss and calibration.',
              '','## Limits and further experiments','',
              '- Repeat with independent real datasets and domain-separated train/test sets.',
              '- Increase to at least 20 seeds and select sample size by a prospective power analysis.',
              '- Report negative findings and predefine acceptable effect sizes.',
              '- Test pre-trained local models via the optional local adapter; do not mix them with this synthetic study.',
              '- Replicate in other architectures, environments, modalities and feedback schemes.',
              '- Do not infer internal consciousness, general intelligence, or architecture-independent emergence from toy tasks.',
              '','## Artefacts','',
              '`observations.csv`: one row per architecture/condition/seed; `predictions.csv`: up to 200 sampled held-out predictions per cell (metrics use all examples);',
              '`manifest.json`: pre-registered comparisons; `findings.json`: effect sizes and seed bootstrap intervals.']
    (out/'REPORT.md').write_text('\n'.join(summary)+'\n',encoding='utf-8')
    return {'directory':str(out),'findings':findings,'rows':result['rows'],
            'settings':result['settings'],'n_predictions':len(result.get('predictions',[]))}
