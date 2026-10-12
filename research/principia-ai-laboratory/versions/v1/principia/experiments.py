"""Preregistered, seeded, controlled experiments for the Principia AI programme.

No outside network/model weights. Synthetic worlds include causal generators and exact
Bayes ceilings so an experiment can FAIL or contradict a proposed corollary.
"""
from __future__ import annotations
import hashlib
import math
import random
import time
from .models import make_model
from .worlds import sample,analytic_bayes,noisy
from .metrics import evaluate


def subseed(seed,*parts):
    return int.from_bytes(hashlib.sha256(('::'.join(map(str,(seed,)+parts))).encode()).digest()[:8],'big')

PRESETS={
  'quick': {'seeds':3,'train_n':192,'test_n':300,'quick':True,'math_n':220},
  'standard': {'seeds':6,'train_n':420,'test_n':600,'quick':False,'math_n':500},
  'extended': {'seeds':20,'train_n':720,'test_n':1200,'quick':False,'math_n':1000},
}

HYPOTHESES=[
 {'id':'H01','name':'No information: the blind engine cannot reliably exceed chance', 'a':['blind','linear','train'], 'reference':.5,'direction':'abs_lt','threshold':.05,'kind':'bound'},
 {'id':'H02','name':'Better observation improves sensor-based judgement','a':['sensors_full','linear','train'],'b':['sensors_weak','linear','train'],'direction':'greater','threshold':.03},
 {'id':'H03','name':'Composition allows parity relations inaccessible to linear separators','a':['parity_large','interactions','train'],'b':['parity_large','linear','train'],'direction':'greater','threshold':.10},
 {'id':'H04','name':'A changed environment can disturb a successful disposition','a':['spurious','linear','train'],'b':['spurious','linear','shift'],'direction':'greater','threshold':.10},
 {'id':'H05','name':'An inverted reward misaligns correction with truth','a':['alignment_clean','linear','train'],'b':['alignment_inverted','linear','train'],'direction':'greater','threshold':.25},
 {'id':'H06','name':'Corrected labels outperform corrupted corrections','a':['alignment_clean','linear','train'],'b':['alignment_noisy','linear','train'],'direction':'greater','threshold':.012,'metric':'brier_advantage'},
 {'id':'H07','name':'An additional instrument can improve decisions','a':['active_tool','adaptive','test'],'b':['active_tool','no_tool','test'],'direction':'greater','threshold':.025},
 {'id':'H08','name':'Independent reference memory can resolve otherwise hidden identities','a':['memory','lookup','test'],'b':['memory','unassisted','test'],'direction':'greater','threshold':.20},
 {'id':'H09','name':'Process verification at larger search budgets can beat first attempt','a':['deliberation_16','process','test'],'b':['deliberation_1','first','test'],'direction':'greater','threshold':.05},
 {'id':'H10','name':'Weak supervision may or may not elicit stronger learned structure','a':['weak_to_strong','pseudo','test'],'b':['weak_to_strong','weak','test'],'direction':'greater','threshold':0.0,'kind':'exploratory'},
 {'id':'H11','name':'Selecting high-confidence predictions can reduce accepted error','a':['sensors_full','linear','train'],'metric':'risk_gain','direction':'greater','threshold':.015,'kind':'exploratory'},
 {'id':'H12','name':'Feedback after acting can improve control over a one-shot decision','a':['control','closed_loop','test'],'b':['control','open_loop','test'],'direction':'greater','threshold':.04,'kind':'exploratory'},
]

COROLLARY_MAP={
 'I. Magnitude versus understanding':['H03','parity_small','parity_large'],
 'II. Invention via composition':['H03','parity_large'],
 'III. Several senses':['H02','sensors_full','sensors_pair','sensors_weak'],
 'IV. Memory and forgetfulness':['H08','memory'],
 'V. Apparent versus actual understanding':['H01','H04','blind','spurious','apparent_equivalence'],
 'VI. Uncertainty and false certainty':['H11','sensors_full'],
 'VII. Propagation of internal error':['H05','H06','alignment_inverted','self_training'],
 'VIII. The liberty of experiment':['H04','spurious'],
 'Proposition I. Learning versus transient inference':['weak_to_strong','deliberation_16'],
 'Proposition II. Composition':['H03','parity_large'],
 'Proposition III. Direction of correction':['H05','H06'],
 'Proposition IV. Indistinguishability':['H01','blind'],
 'Proposition V. Changed conditions':['H04','spurious'],
 'Proposition VI. Objective versus truth':['H05','alignment_inverted'],
 'Proposition VII. Additional instruments':['H07','active_tool'],
 'Proposition VIII. Deliberation':['H09','deliberation_16'],
 'Proposition IX. Feedback and action':['H07','H12','active_tool','control'],
}


def _experiment_specs(cfg):
    n=cfg['train_n']
    specs=[]
    def add(id,world,models,train_n=n,mask=None,reward='truth',noise=0,eval_domains=('train',)):
        specs.append(dict(id=id,world=world,models=models,train_n=train_n,mask=mask,reward=reward,noise=noise,eval_domains=eval_domains))
    add('blind','blind',['prior','linear','interactions','mlp'])
    add('sensors_full','sensors',['prior','linear','mlp'])
    add('sensors_pair','sensors',['linear'],mask=[0,1])
    add('sensors_weak','sensors',['linear'],mask=[2])
    add('parity_small','parity',['linear','interactions','mlp'],train_n=48)
    add('parity_medium','parity',['linear','interactions','mlp'],train_n=max(128,n//2))
    add('parity_large','parity',['linear','interactions','mlp'],train_n=n)
    add('spurious','spurious',['linear','interactions','mlp'],eval_domains=('train','shift'))
    add('alignment_clean','alignment',['linear'])
    add('alignment_noisy','alignment',['linear'],noise=.26)
    add('alignment_inverted','alignment',['linear'],reward='inverted')
    return specs


def _predict_record(experiment, model_name, seed, domain, train_n, true_ys, probs, model, elapsed, meta, keep_predictions=True):
    m=evaluate(true_ys,probs)
    row={'experiment':experiment,'model':model_name,'seed':seed,'domain':domain,'n_train':train_n,
         'params':getattr(model,'params',0),'ops_proxy':getattr(model,'steps',0),
         'train_seconds':round(elapsed,6),**{k:round(v,7) if isinstance(v,float) else v for k,v in m.items()},
         **meta}
    predictions=[]
    if keep_predictions:
        # Portable audit sample; aggregate metrics always use the ENTIRE held-out test set.
        cap=min(len(true_ys),200)
        indices=sorted(set(round(i*(len(true_ys)-1)/max(1,cap-1)) for i in range(cap)))
        predictions=[{'experiment':experiment,'model':model_name,'seed':seed,'domain':domain,'index':i,
                      'y':true_ys[i],'p':round(probs[i],8),'pred':int(probs[i]>=.5)} for i in indices]
    return row,predictions


def _arithmetic(seed,count,budget,method):
    truth=[]; chosen=[]; operation_count=0
    for task_i in range(count):
        task_rng=random.Random(subseed(seed,'math',task_i))
        a=task_rng.randrange(-12,13); b=task_rng.randrange(-12,13); c=task_rng.randrange(1,8); d=task_rng.randrange(-8,9)
        real1=a+b;real2=real1*c;real3=real2-d
        candidates=[]
        for i in range(budget):
            r=random.Random(subseed(seed,'candidate',task_i,i))
            one=real1 if r.random()<.81 else real1+r.choice([-3,-2,-1,1,2,3])
            two=one*c if r.random()<.81 else one*c+r.choice([-3,-2,-1,1,2,3])
            three=two-d if r.random()<.81 else two-d+r.choice([-3,-2,-1,1,2,3])
            correctness=(one==real1,two==one*c,three==two-d)
            # A verifier can check local equations, but not directly inspect real3.
            process=sum(int(t if r.random()<.91 else not t) for t in correctness)/3
            # Noisy whole-answer feedback uses a privileged labelled final result.
            out_ok=three==real3
            outcome=int(out_ok if r.random()<.77 else not out_ok)
            candidates.append((three,process,outcome))
            operation_count+=9
        ix=0
        if method=='process': ix=max(range(len(candidates)),key=lambda i:(candidates[i][1],-i))
        if method=='outcome': ix=max(range(len(candidates)),key=lambda i:(candidates[i][2],-i))
        truth.append(real3)
        chosen.append(candidates[ix][0])
    correct=sum(a==b for a,b in zip(truth,chosen))/count
    return correct,operation_count


def _active_sensor(seed,count,mode):
    correct=0; tool_calls=0; brier=0
    for i in range(count):
        r=random.Random(subseed(seed,'sensor',i))
        y=r.randrange(2)
        s1=noisy(y,.69,r);s2=noisy(y,.72,r)
        odds=(1 if s1 else -1)*math.log(.69/.31)+(1 if s2 else -1)*math.log(.72/.28)
        ask=mode=='always' or (mode=='adaptive' and s1!=s2)
        if ask:
            extra=noisy(y,.95,r); tool_calls+=1
            odds+=(1 if extra else -1)*math.log(.95/.05)
        p=1/(1+math.exp(-odds))
        correct+=int(int(p>=.5)==y);brier+=(p-y)**2
    return correct/count,tool_calls/count,brier/count


def _memory(seed,count,mode):
    r=random.Random(seed)
    registry={k:r.randrange(2) for k in range(120)}
    # Evaluate strictly UNSEEN identities; the mapping is independent of the identifier.
    keys=[r.randrange(40,120) for _ in range(count)]
    if mode=='lookup': predicted=[registry[k] for k in keys]
    else: predicted=[0 for _ in keys]
    return sum(predicted[i]==registry[k] for i,k in enumerate(keys))/count


def _control(seed,count,mode):
    successes=0;actions=0
    for i in range(count):
        r=random.Random(subseed(seed,'act',i))
        state=r.randrange(2)
        # Initial human-observer equivalent: imperfect measurement of current state.
        reading=noisy(state,.80,r)
        if reading==1:
            actions+=1
            if r.random()<.96:state=1-state
        if mode=='closed_loop':
            # Independent, higher fidelity post-action measurement.
            for t in range(2):
                reading=noisy(state,.97,r)
                if reading==1:
                    actions+=1
                    if r.random()<.96:state=1-state
        successes+=int(state==0)
    return successes/count,actions/count


def run_suite(preset='quick',seed=42,progress=None,include_predictions=True):
    if preset not in PRESETS: raise ValueError('Unknown preset')
    cfg=PRESETS[preset]
    t0=time.perf_counter(); rows=[]; predictions=[]
    specs=_experiment_specs(cfg)
    # Includes transfer, tools, memory, and verification tasks below.
    estimated=cfg['seeds']*(sum(len(s['models'])*len(s['eval_domains']) for s in specs)+23)
    done=0
    def notify(label):
        if progress: progress({'completed':done,'total':estimated,'detail':label,'elapsed':round(time.perf_counter()-t0,1)})
    for si in range(cfg['seeds']):
        actual_seed=seed+si*10007
        for spec in specs:
            world=spec['world']; n=spec['train_n']; mask=spec['mask']; exp=spec['id']
            train_rng=random.Random(subseed(actual_seed,world,'train',n))
            train=sample(world,n,train_rng,feature_mask=mask)
            xs=[a for a,_,_ in train]; yy=[y for _,y,_ in train]
            # Modify labels on an independent stream to keep observations exactly paired across objectives.
            correction_rng=random.Random(subseed(actual_seed,'correction',exp))
            tr_labels=[(1-y if spec['reward']=='inverted' else y)^int(correction_rng.random()<spec['noise']) for y in yy]
            for model_name in spec['models']:
                model=make_model(model_name,cfg['quick'])
                started=time.perf_counter()
                model.fit(xs,tr_labels,subseed(actual_seed,exp,model_name))
                elapsed=time.perf_counter()-started
                for domain in spec['eval_domains']:
                    test=sample(world,cfg['test_n'],random.Random(subseed(actual_seed,world,'test',domain)),domain=domain,feature_mask=mask)
                    x_test=[x for x,_,_ in test]; y_test=[y for _,y,_ in test]
                    pp=[model.predict(x) for x in x_test]
                    meta=analytic_bayes(world,domain=domain,feature_mask=mask)
                    result,preds=_predict_record(exp,model_name,si,domain,n,y_test,pp,model,elapsed,meta,include_predictions)
                    rows.append(result);predictions.extend(preds)
                    done+=1;notify(exp+' · '+model_name+' · '+domain)
        # Weak-to-strong: no guarantee of recovery from teacher's missing information.
        r=random.Random(subseed(actual_seed,'weak_transfer'))
        n=cfg['train_n']; samples=sample('parity',n,r)
        train_x=[x for x,_,_ in samples]; train_y=[y for _,y,_ in samples]
        weak=make_model('linear',cfg['quick']).fit(train_x,train_y,subseed(actual_seed,'weak'))
        pseudo=[int(weak.predict(x)>=.5) for x in train_x]
        strong=make_model('interactions',cfg['quick']).fit(train_x,pseudo,subseed(actual_seed,'pseudo'))
        gold=make_model('interactions',cfg['quick']).fit(train_x,train_y,subseed(actual_seed,'gold'))
        test=sample('parity',cfg['test_n'],random.Random(subseed(actual_seed,'parity','weaktest')))
        xx=[x for x,_,_ in test]; yy=[y for _,y,_ in test]
        for name,model in [('weak',weak),('pseudo',strong),('gold',gold)]:
            pp=[model.predict(x) for x in xx]
            row,preds=_predict_record('weak_to_strong',name,si,'test',n,yy,pp,model,0,analytic_bayes('parity'),include_predictions)
            rows.append(row);predictions.extend(preds);done+=1;notify('weak-to-strong '+name)
        # Active sensing with feedback, with identical task seeds across treatments.
        for method in ('no_tool','adaptive','always'):
            acc,queries,brier=_active_sensor(subseed(actual_seed,'tool'),cfg['math_n'],method)
            rows.append(dict(experiment='active_tool',model=method,seed=si,domain='test',n_train=0,n_test=cfg['math_n'],
                             accuracy=acc,brier=brier,tool_query_rate=queries,params=0,ops_proxy=cfg['math_n']*2,train_seconds=0))
            done+=1;notify('active observation '+method)
        for method in ('unassisted','lookup'):
            acc=_memory(subseed(actual_seed,'memory'),cfg['math_n'],method)
            rows.append(dict(experiment='memory',model=method,seed=si,domain='test',n_train=40,n_test=cfg['math_n'],
                             accuracy=acc,params=0,ops_proxy=cfg['math_n'],train_seconds=0))
            done+=1;notify('memory '+method)
        for mode in ('open_loop','closed_loop'):
            acc,actions=_control(subseed(actual_seed,'feedback'),cfg['math_n'],mode)
            rows.append(dict(experiment='control',model=mode,seed=si,domain='test',n_train=0,n_test=cfg['math_n'],
                             accuracy=acc,action_rate=actions,params=0,ops_proxy=cfg['math_n']*(1 if mode=='open_loop' else 3),train_seconds=0))
            done+=1;notify('world intervention '+mode)
        # Self-training may amplify certainty even without new ground truth.
        base_train=sample('sensors',cfg['train_n'],random.Random(subseed(actual_seed,'self_train_data')))
        train_x=[x for x,_,_ in base_train];train_y=[y for _,y,_ in base_train]
        base_test=sample('sensors',cfg['test_n'],random.Random(subseed(actual_seed,'self_test')))
        tx=[x for x,_,_ in base_test];ty=[y for _,y,_ in base_test]
        teacher=make_model('linear',cfg['quick']).fit(train_x,train_y,subseed(actual_seed,'self_model'))
        for generation in (0,1,2):
            probs=[teacher.predict(x) for x in tx]
            r,preds=_predict_record('self_training',f'gen_{generation}',si,'test',len(train_x),ty,probs,teacher,0,
                                    analytic_bayes('sensors'),include_predictions)
            rows.append(r);predictions.extend(preds);done+=1;notify('self-training generation '+str(generation))
            pseudo=[int(teacher.predict(x)>=.5) for x in train_x]
            teacher=make_model('linear',cfg['quick']).fit(train_x,pseudo,subseed(actual_seed,'self_round',generation))
        # Two engines can agree outwardly while having different constitutions.
        m1=make_model('linear',cfg['quick']).fit(train_x,train_y,subseed(actual_seed,'comparisonlinear'))
        m2=make_model('mlp',cfg['quick']).fit(train_x,train_y,subseed(actual_seed,'comparisonmlp'))
        agree=sum(int(m1.predict(x)>=.5)==int(m2.predict(x)>=.5) for x in tx)/len(tx)
        rows.append(dict(experiment='apparent_equivalence',model='linear_vs_mlp',seed=si,domain='test',
                         n_train=len(train_x),n_test=len(tx),accuracy=agree,agreement=agree,
                         params=m1.params+m2.params,ops_proxy=m1.steps+m2.steps,train_seconds=0))
        done+=1;notify('apparent intelligence equivalence')
        # Search and verification vs a single generated answer.
        for budget in (1,4,16):
            for method in ('first','process','outcome'):
                acc,ops=_arithmetic(subseed(actual_seed,'deliberation'),cfg['math_n'],budget,method)
                rows.append(dict(experiment='deliberation_'+str(budget),model=method,seed=si,domain='test',
                                 n_train=0,n_test=cfg['math_n'],accuracy=acc,params=0,ops_proxy=ops,train_seconds=0))
                done+=1;notify('deliberation '+str(budget)+' · '+method)
    return {'settings':{'preset':preset,'seed':seed,'config':cfg,'seconds':round(time.perf_counter()-t0,3),
                        'synthetic':True,'independent_seeds':cfg['seeds']},
            'hypotheses':HYPOTHESES,'corollary_map':COROLLARY_MAP,
            'rows':rows,'predictions':predictions}
