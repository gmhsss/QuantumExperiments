"""QAOA vs EDA (PBIL/UMDA) vs GA na MESMA paisagem I_F(x). Eixo x: nº de avaliacoes de H."""
import numpy as np, sys, os
from scipy.optimize import minimize
N=int(os.environ.get('QFI_N',14)); S=1024; BUDGETS=np.unique(np.logspace(np.log10(64),np.log10(150000),14).astype(int))
OM=2**N
bits=((np.arange(OM)[:,None]>>np.arange(N))&1).astype(np.int8)

def make_graph(seed):
    r=np.random.default_rng(seed); pts=r.uniform(0,1,(N,2))
    return [(i,j) for i in range(N) for j in range(i+1,N) if np.linalg.norm(pts[i]-pts[j])<0.33*np.sqrt(14/N)]
def landscape(edges):
    H=-bits.sum(1).astype(float)
    for i,j in edges: H+=2.0*bits[:,i]*bits[:,j]
    s=np.sort(H); IF=-np.log2(np.searchsorted(s,H,side="right")/OM)
    return H,IF
# ---- QAOA exato (numpy). x=(1-Z)/2 -> H diagonal; mixer RX(2b) em cada qubit
def qaoa_p(params,H,p):
    psi=np.full(OM,1/np.sqrt(OM),dtype=complex)
    for k in range(p):
        g,b=params[k],params[p+k]
        psi*=np.exp(-1j*g*H)
        c,s=np.cos(b),-1j*np.sin(b)
        psi=psi.reshape([2]*N)
        for q in range(N):
            a=np.take(psi,0,axis=q); bb=np.take(psi,1,axis=q)
            psi=np.stack([c*a+s*bb,s*a+c*bb],axis=q)
        psi=psi.reshape(OM)
    return np.abs(psi)**2
def run_qaoa(H,IF,p,seed,maxev):
    r=np.random.default_rng(seed); x0=np.concatenate([r.uniform(0,.5,p),r.uniform(0,.8,p)])
    hist=[]; best=[np.inf,x0]
    def f(x):
        pr=qaoa_p(x,H,p); idx=r.choice(OM,S,p=pr/pr.sum()); e=H[idx].mean()
        if e<best[0]: best[0]=e;best[1]=x.copy()
        hist.append(float(pr@IF) if False else None); hist[-1]=(best[1].copy()); return e
    minimize(f,x0,method="COBYLA",options={"maxiter":maxev,"rhobeg":0.3})
    out=[]
    for B in BUDGETS:
        k=min(len(hist),max(1,B//S))
        if B<S: out.append(np.nan); continue
        pr=qaoa_p(hist[k-1],H,p); out.append(float(pr@IF))
    return np.array(out)
def prod_dist(pv):
    P=np.where(bits==1,pv,1-pv); return np.prod(P,axis=1)
def run_eda(H,IF,kind,lam,lr,seed,maxB):
    r=np.random.default_rng(seed); pv=np.full(N,.5); used=0; trace=[]
    while used<maxB:
        X=(r.random((lam,N))<pv).astype(np.int8)
        idx=X@(1<<np.arange(N)); used+=lam
        top=np.argsort(H[idx])[:lam//2]; m=X[top].mean(0)
        pv=m if kind=="umda" else (1-lr)*pv+lr*m
        pv=np.clip(pv,.02,.98); trace.append((used,float(prod_dist(pv)@IF)))
    return interp(trace)
def run_ga(H,IF,pop,seed,maxB):
    r=np.random.default_rng(seed); P=r.integers(0,2,(pop,N)).astype(np.int8); used=pop
    trace=[]
    def val(P): return H[P@(1<<np.arange(N))]
    f=val(P); trace.append((used,float(IF[P@(1<<np.arange(N))].mean())))
    while used<maxB:
        ch=[]
        el=np.argsort(f)[:2]; ch=[P[e] for e in el]
        while len(ch)<pop:
            a=[min(r.integers(0,pop,3),key=lambda i:f[i]) for _ in range(2)]
            m=r.random(N)<.5; c=np.where(m,P[a[0]],P[a[1]]); fl=r.random(N)<1/N; c=np.where(fl,1-c,c)
            ch.append(c.astype(np.int8))
        P=np.array(ch); f=val(P); used+=pop-2
        trace.append((used,float(IF[P@(1<<np.arange(N))].mean())))
    return interp(trace)
def interp(trace):
    u=np.array([t[0] for t in trace]); v=np.array([t[1] for t in trace]); out=[]
    for B in BUDGETS:
        j=np.searchsorted(u,B,side="right")-1; out.append(v[j] if j>=0 else np.nan)
    return np.array(out)
if __name__=="__main__":
    GR=[11,12,13][:int(os.environ.get("QFI_G",3))]; SE=[0,1,2][:int(os.environ.get("QFI_S",3))]
    res={}; unif=[]
    for g in GR:
        e=make_graph(g); H,IF=landscape(e); u=IF.mean(); unif.append(u)
        top=IF.max()
        for s in SE:
            for p in (1,2,3): res.setdefault(f"QAOA p={p}",[]).append((u,top,run_qaoa(H,IF,p,s,int(os.environ.get("QFI_IT",400)))))
            for lam,lr in ((64,.05),(64,.2)): res.setdefault(f"PBIL lam={lam} lr={lr}",[]).append((u,top,run_eda(H,IF,"pbil",lam,lr,s,BUDGETS[-1])))
            for lam in (64,256): res.setdefault(f"UMDA lam={lam}",[]).append((u,top,run_eda(H,IF,"umda",lam,0,s,BUDGETS[-1])))
            for pop in (32,128): res.setdefault(f"GA pop={pop}",[]).append((u,top,run_ga(H,IF,pop,s,BUDGETS[-1])))
        print("graph",g,"edges",len(e),"uniform <I_F>=%.3f max I_F=%.3f"%(u,top),flush=True)
    np.save(f"res_n{N}.npy",{k:[(a,b,list(c)) for a,b,c in v] for k,v in res.items()},allow_pickle=True)
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    def prog(v): return np.nanmean([(c-a)/(b-a) for a,b,c in v],axis=0)
    fig,ax=plt.subplots(figsize=(8,5)); summ={}
    for k,v in res.items():
        y=prog(v); summ[k]=y; ax.plot(BUDGETS,y,label=k,ls="-" if k.startswith("QAOA") else ("--" if "GA" not in k else ":"),lw=2 if k.startswith("QAOA") else 1)
    ax.axhline(0,c="k",lw=.8); ax.set_xscale("log"); ax.set_xlabel("avaliacoes de H (amostras)"); ax.set_ylabel("progresso normalizado de <I_F>  (0=uniforme, 1=max)")
    ax.legend(fontsize=7); plt.tight_layout(); plt.savefig(f"qfi_compare_n{N}.png",dpi=140)
    print("\nbudget:",list(BUDGETS))
    for k,y in summ.items(): print(f"{k:22s}",np.round(y,3))
