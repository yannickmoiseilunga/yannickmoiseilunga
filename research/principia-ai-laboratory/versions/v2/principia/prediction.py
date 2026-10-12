"""Cross-condition forecasts. A fitted phenomenological *candidate*, not a universal law.

Leave-one-condition-out ridge, using ONLY pre-experiment design and known synthetic
information ceilings as predictors. Results never used in fitting that fold.
"""
from __future__ import annotations
import math
from collections import defaultdict


def design_features(row):
    """Features must be known before the measured accuracy is read."""
    exp=row['experiment']; name=row['model'];domain=row['domain']
    return [
      1.0,
      row.get('bayes_accuracy',.5),
      row.get('mutual_information_bits',0),
      math.log1p(row.get('n_train',0))/8,
      math.log1p(row.get('params',0))/8,
      float(name=='mlp'),
      float(name=='interactions'),
      float(name=='prior'),
      float(exp.startswith('parity') or exp=='weak_to_strong'),
      float(exp.startswith('spurious')),
      float(domain=='shift'),
      float('inverted' in exp),
      float('noisy' in exp),
      float('weak' in exp),
      float('small' in exp),
    ]


def solve_linear(A,b):
    n=len(b);matrix=[list(A[i])+[b[i]] for i in range(n)]
    for k in range(n):
        best=max(range(k,n),key=lambda j:abs(matrix[j][k]))
        matrix[k],matrix[best]=matrix[best],matrix[k]
        p=matrix[k][k]
        if abs(p)<1e-14:return None
        for j in range(k,n+1):matrix[k][j]/=p
        for i in range(n):
            if i==k:continue
            ratio=matrix[i][k]
            for j in range(k,n+1):matrix[i][j]-=ratio*matrix[k][j]
    return [matrix[i][-1] for i in range(n)]


def ridge_train(rows,penalty=2.0):
    x=[design_features(r) for r in rows];y=[r['accuracy'] for r in rows];n=len(x[0]);
    A=[[sum(t[i]*t[j] for t in x)+(penalty if i==j and i>0 else 0.0001 if i==j else 0)
        for j in range(n)] for i in range(n)]
    b=[sum(t[i]*yy for t,yy in zip(x,y)) for i in range(n)]
    return solve_linear(A,b)


def cross_condition_predictions(rows):
    included=[r for r in rows if r['experiment'] not in ('memory','active_tool')
              and not r['experiment'].startswith('deliberation') and r['experiment']!='weak_to_strong'
              and 'bayes_accuracy' in r]
    groups=defaultdict(list)
    for r in included:groups[r['experiment']].append(r)
    if len(groups)<3:return {'predictions':[],'summary':{'mae':None,'baseline_mae':None,'n_conditions':0}}
    all_preds=[]
    for heldout,tests in groups.items():
        train=[r for label,rr in groups.items() if label!=heldout for r in rr]
        w=ridge_train(train)
        if w is None:continue
        baseline=sum(r['accuracy'] for r in train)/len(train)
        for r in tests:
            f=design_features(r)
            raw=sum(a*b for a,b in zip(w,f))
            predicted=max(0,min(1,raw))
            # Chance baseline also shown (world-agnostic).
            constrained=min(predicted,r['bayes_accuracy'])
            all_preds.append({'heldout_experiment':heldout,'model':r['model'],'domain':r['domain'],
                  'seed':r['seed'],'predicted':round(predicted,7),
                  'constrained_predicted':round(constrained,7),'constrained_abs_error':abs(constrained-r['accuracy']),
                  'observed':r['accuracy'],
                  'absolute_error':abs(predicted-r['accuracy']),
                  'baseline_predicted':baseline,'baseline_abs_error':abs(baseline-r['accuracy']),
                  'bayes_ceiling':r['bayes_accuracy']})
    if not all_preds:return {'predictions':[],'summary':{'mae':None,'baseline_mae':None,'n_conditions':0}}
    mae=sum(r['absolute_error'] for r in all_preds)/len(all_preds)
    bmae=sum(r['baseline_abs_error'] for r in all_preds)/len(all_preds)
    cmae=sum(r['constrained_abs_error'] for r in all_preds)/len(all_preds)
    ceiling_violations=sum(r['predicted']>r['bayes_ceiling']+.005 for r in all_preds)
    return {'predictions':all_preds,
            'summary':{'mae':mae,'constrained_mae':cmae,'baseline_mae':bmae,'n_conditions':len(groups),
                       'n_predictions':len(all_preds),'above_bayes_ceiling_predictions':ceiling_violations,
                       'interpretation':'Leave-one-experiment-condition-out forecast. A failed forecast is a failed candidate model, not a falsification of information theory.',
                       'limitation':'Scenario metadata and synthetic Bayes ceilings are given to the predictor; heldout real worlds require a new design.'}}
