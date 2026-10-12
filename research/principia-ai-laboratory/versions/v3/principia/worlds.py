"""Explicit causal generators. Truth is held separately from the learner's observations."""
from __future__ import annotations
import random
import math
import itertools


def noisy(bit, reliability, rng): return bit if rng.random()<reliability else 1-bit


def sample(world, n, rng, domain='train', reward='truth', feature_mask=None, label_noise=0.0):
    rows=[]
    for _ in range(n):
        y=rng.randrange(2)
        if world=='blind':
            x=[rng.randrange(2),rng.randrange(2),rng.randrange(2)]
        elif world=='sensors':
            x=[noisy(y,.78,rng),noisy(y,.72,rng),noisy(y,.67,rng)]
        elif world=='spurious':
            x=[noisy(y,.82,rng),noisy(y,.97 if domain=='train' else .12,rng),rng.randrange(2)]
        elif world=='parity':
            a=rng.randrange(2); b=rng.randrange(2)
            y=a^b
            x=[a,b,rng.randrange(2)]
        elif world=='alignment':
            x=[noisy(y,.93,rng),rng.randrange(2),rng.randrange(2)]
        else:
            raise ValueError('Unknown world: '+world)
        if feature_mask is not None:
            x=[x[i] for i in feature_mask]
        train_y=1-y if reward=='inverted' else y
        if label_noise and rng.random()<label_noise: train_y=1-train_y
        rows.append((x,y,train_y))
    return rows


def analytic_bayes(world, domain='test', feature_mask=None):
    """Enumerate P(X,Y) EXACTLY for simple discrete worlds; return Bayes accuracy and MI bits.
    For parity, account for y := XOR of two uniform observed causes, not a sampled label.
    """
    joint={}
    def add(x,y,p):
        if feature_mask is not None: x=tuple(x[i] for i in feature_mask)
        else: x=tuple(x)
        joint[(x,y)]=joint.get((x,y),0.0)+p
    if world=='parity':
        for a,b,z in itertools.product((0,1),repeat=3): add([a,b,z],a^b,1/8)
    else:
        reliabilities={'blind': [None,None,None], 'sensors':[.78,.72,.67],
                       'spurious':[.82,.97 if domain=='train' else .12,None],
                       'alignment':[.93,None,None]}[world]
        for y in (0,1):
            for x in itertools.product((0,1),repeat=3):
                p=.5
                for bit,q in zip(x,reliabilities):
                    p*=.5 if q is None else q if bit==y else 1-q
                add(x,y,p)
    xs={k[0] for k in joint}
    bayes=sum(max(joint.get((x,0),0),joint.get((x,1),0)) for x in xs)
    hy=1.0
    hcond=0
    for x in xs:
        p0=joint.get((x,0),0);p1=joint.get((x,1),0);mass=p0+p1
        if mass<=0: continue
        for py in (p0,p1):
            if py>0: hcond-=py*math.log2(py/mass)
    return {'bayes_accuracy':bayes, 'mutual_information_bits':max(0,hy-hcond)}
