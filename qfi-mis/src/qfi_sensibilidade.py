"""Exemplo de sensibilidade da metrica <I_F> (1 grafo, n=14, 1 execucao por algoritmo).

Compara QAOA p=1,2,3, UMDA e sorteio uniforme com 4 reguas: <I_F>, P(otimo),
<H> e o quantil 90 de I_F. Depois mostra o erro de <I_F> estimado por shots.
E uma ilustracao (1 grafo, 1 semente), nao uma conclusao estatistica.

Uso (a partir de qfi-mis/src):  python qfi_sensibilidade.py
Requer qfi_compare.py na mesma pasta.
"""
import numpy as np
from scipy.optimize import minimize
import qfi_compare as q
N,OM,bits=q.N,q.OM,q.bits
e=q.make_graph(11); H,IF=q.landscape(e)
hstar=H.min(); top=(H<=hstar)
def train(p,seed=0):
    r=np.random.default_rng(seed); x0=np.concatenate([r.uniform(0,.5,p),r.uniform(0,.8,p)])
    f=lambda x: float(q.qaoa_p(x,H,p)@H)
    return minimize(f,x0,method="COBYLA",options={"maxiter":300,"rhobeg":.3}).x
dist={}
for p in (1,2,3): dist[f"QAOA p={p}"]=q.qaoa_p(train(p),H,p)
# UMDA final
r=np.random.default_rng(0); pv=np.full(N,.5)
for _ in range(60):
    X=(r.random((64,N))<pv).astype(np.int8); idx=X@(1<<np.arange(N))
    pv=np.clip(X[np.argsort(H[idx])[:32]].mean(0),.02,.98)
dist["UMDA"]=q.prod_dist(pv)
dist["Uniforme"]=np.full(OM,1/OM)
def q90(p):
    o=np.argsort(IF); c=np.cumsum(p[o]); return IF[o][np.searchsorted(c,.9)]
print(f"grafo n={N}, arestas={len(e)}, E_otimo={hstar:.0f}, I_F(h*)={IF[top][0]:.2f} bits, <I_F>_unif={IF.mean():.3f}\n")
print(f"{'':10s} {'<I_F>':>7s} {'P(otimo)':>9s} {'<H>':>7s} {'I_F q90':>8s}")
for k,p in dist.items():
    print(f"{k:10s} {p@IF:7.3f} {p[top].sum():9.4f} {p@H:7.2f} {q90(p):8.2f}")
print("\nErro do <I_F> estimado por shots (QAOA p=3, 200 repetições):")
p=dist["QAOA p=3"]; ex=p@IF; r=np.random.default_rng(1)
print(f"valor exato = {ex:.3f}")
print(f"{'shots':>6s} {'media':>7s} {'desvio':>7s} {'erro rel.':>9s}")
for s in (10,100,1000,10000):
    est=np.array([IF[r.choice(OM,s,p=p)].mean() for _ in range(200)])
    print(f"{s:6d} {est.mean():7.3f} {est.std():7.3f} {abs(est.mean()-ex)/ex*100:8.1f}%")
