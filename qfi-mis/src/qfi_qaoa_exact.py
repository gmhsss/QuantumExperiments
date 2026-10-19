import numpy as np
from scipy.optimize import minimize
import qfi_compare as q
out={p:[] for p in (1,2,3)}
for g in (11,12,13):
    H,IF=q.landscape(q.make_graph(g)); u=IF.mean(); top=IF.max()
    for s in (0,1,2):
        for p in (1,2,3):
            r=np.random.default_rng(s); x0=np.concatenate([r.uniform(0,.5,p),r.uniform(0,.8,p)]); hist=[]
            def f(x): hist.append(x.copy()); return float(q.qaoa_p(x,H,p)@H)
            minimize(f,x0,method="COBYLA",options={"maxiter":400,"rhobeg":0.3})
            e=[]
            for B in q.BUDGETS:
                k=B//q.S
                e.append(np.nan if k<1 else (float(q.qaoa_p(min(hist[:k],key=lambda x:float(q.qaoa_p(x,H,p)@H)),H,p)@IF)-u)/(top-u))
            out[p].append(e)
for p in out: print("QAOA exact-energy p=%d"%p,np.round(np.nanmean(out[p],axis=0),3))
