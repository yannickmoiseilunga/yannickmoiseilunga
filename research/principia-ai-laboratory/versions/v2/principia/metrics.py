"""Evaluation on isolated test sets, simple risk/coverage and seed bootstrap."""
import math
import random
import statistics

def evaluate(ys, ps):
    if len(ys)!=len(ps) or not ys: raise ValueError('Nonempty matching y,p required')
    n=len(ys); pred=[int(p>=.5) for p in ps]
    accuracy=sum(p==y for p,y in zip(pred,ys))/n
    brier=sum((p-y)**2 for p,y in zip(ps,ys))/n
    logloss=-sum(y*math.log(max(1e-12,min(1-1e-12,p)))+(1-y)*math.log(max(1e-12,min(1-1e-12,1-p))) for y,p in zip(ys,ps))/n
    ece=0
    for i in range(10):
        vals=[(max(p,1-p),int(pred[k]==ys[k])) for k,p in enumerate(ps) if min(9,int(max(p,1-p)*10))==i]
        if vals:
            ece+=len(vals)/n*abs(sum(v[0] for v in vals)/len(vals)-sum(v[1] for v in vals)/len(vals))
    ranked=sorted(range(n),key=lambda k:(max(ps[k],1-ps[k]),-k),reverse=True)
    top=ranked[:max(1,int(math.ceil(n*.8)))]
    risk80=1-sum(pred[i]==ys[i] for i in top)/len(top)
    return {'accuracy':accuracy,'brier':brier,'log_loss':logloss,'ece':ece,'selective_risk_80':risk80,
            'coverage_80':len(top)/n, 'n_test':n}

def mean_ci(values, seed=3487, iterations=800):
    vals=list(values)
    if not vals: return [None,None,None]
    mean=statistics.mean(vals)
    if len(vals)<2: return [mean,None,None]
    rng=random.Random(seed); draws=[]
    for _ in range(iterations): draws.append(sum(vals[rng.randrange(len(vals))] for _ in vals)/len(vals))
    draws.sort()
    return [mean,draws[int(.025*(iterations-1))],draws[int(.975*(iterations-1))]]
