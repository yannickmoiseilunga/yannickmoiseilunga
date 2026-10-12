"""Small CPU learners written with Python standard library. No pretrained weights."""
from __future__ import annotations
import math
import random
import time


def sigmoid(z):
    if z < -40: return 1e-12
    if z > 40: return 1 - 1e-12
    return 1/(1+math.exp(-z))


def augment(x, interaction=False):
    x = list(x)
    if interaction:
        x += [x[i]*x[j] for i in range(len(x)) for j in range(i+1,len(x))]
    return x


class Prior:
    def fit(self, xs, ys, seed=0):
        self.p=(sum(ys)+1)/(len(ys)+2)
        self.params=1
        self.steps=0
        return self
    def predict(self,x): return self.p


class Logistic:
    def __init__(self, interaction=False, epochs=65, lr=.26, l2=.001):
        self.interaction=interaction; self.epochs=epochs; self.lr=lr; self.l2=l2
    def fit(self,xs,ys,seed=0):
        r=random.Random(seed)
        data=[augment(x,self.interaction) for x in xs]
        dim=len(data[0]); self.w=[r.uniform(-.12,.12) for _ in range(dim+1)]
        self.params=len(self.w); self.steps=0
        ids=list(range(len(data)))
        for ep in range(self.epochs):
            r.shuffle(ids)
            rate=self.lr/(1+.012*ep)
            for ix in ids:
                x=data[ix]; y=ys[ix]
                p=sigmoid(self.w[-1]+sum(a*b for a,b in zip(x,self.w)))
                err=p-y
                for j in range(dim):
                    self.w[j]-=rate*(err*x[j]+self.l2*self.w[j])
                self.w[-1]-=rate*err
                self.steps+=dim*4+10
        return self
    def predict(self,x):
        z=augment(x,self.interaction)
        return sigmoid(sum(a*b for a,b in zip(z,self.w))+self.w[-1])


class TinyMLP:
    """One-hidden-layer tanh neural classifier, manually differentiated."""
    def __init__(self, hidden=8, epochs=90, lr=.07, l2=.0002):
        self.hidden=hidden; self.epochs=epochs; self.lr=lr; self.l2=l2
    def fit(self,xs,ys,seed=0):
        r=random.Random(seed)
        dim=len(xs[0]); h=self.hidden
        self.v=[[r.uniform(-.65,.65) for _ in range(dim+1)] for _ in range(h)]
        self.w=[r.uniform(-.45,.45) for _ in range(h+1)]
        self.params=h*(dim+1)+(h+1); self.steps=0
        ids=list(range(len(xs)))
        for ep in range(self.epochs):
            r.shuffle(ids)
            rate=self.lr/(1+.008*ep)
            for ix in ids:
                x=xs[ix]; y=ys[ix]
                activ=[math.tanh(sum(row[j]*x[j] for j in range(dim))+row[-1]) for row in self.v]
                p=sigmoid(self.w[-1]+sum(self.w[j]*activ[j] for j in range(h)))
                delta=p-y
                old=self.w[:]
                for j in range(h): self.w[j]-=rate*(delta*activ[j]+self.l2*self.w[j])
                self.w[-1]-=rate*delta
                for j in range(h):
                    delta_hidden=delta*old[j]*(1-activ[j]*activ[j])
                    for k in range(dim): self.v[j][k]-=rate*(delta_hidden*x[k]+self.l2*self.v[j][k])
                    self.v[j][-1]-=rate*delta_hidden
                self.steps+=h*(dim*9+25)
        return self
    def predict(self,x):
        activ=[math.tanh(sum(row[j]*x[j] for j in range(len(x)))+row[-1]) for row in self.v]
        return sigmoid(self.w[-1]+sum(self.w[j]*activ[j] for j in range(self.hidden)))


def make_model(name, quick=False):
    if name=='prior': return Prior()
    if name=='linear': return Logistic(epochs=40 if quick else 70)
    if name=='interactions': return Logistic(True,epochs=48 if quick else 80)
    if name=='mlp': return TinyMLP(epochs=50 if quick else 100)
    raise ValueError('Unknown architecture: '+name)
