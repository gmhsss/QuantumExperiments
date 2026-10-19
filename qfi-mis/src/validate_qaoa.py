"""Valida o simulador numpy do QAOA (qfi_compare.qaoa_p) contra o Qiskit (RZ/RZZ/RX)."""
import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector
import qfi_compare as q

def qiskit_probs(params, edges, n, p):
    deg=np.zeros(n)
    for i,j in edges: deg[i]+=1; deg[j]+=1
    h=0.5-deg/2          # coef de Z_i em H ; coef de Z_iZ_j = 1/2
    qc=QuantumCircuit(n); qc.h(range(n))
    for k in range(p):
        g,b=params[k],params[p+k]
        for i in range(n): qc.rz(2*g*h[i],i)
        for i,j in edges: qc.rzz(2*g*0.5,i,j)
        for i in range(n): qc.rx(2*b,i)
    return Statevector.from_instruction(qc).probabilities()

if __name__=="__main__":
    worst=0
    for N in (6,8,10):
        q.N=N; q.OM=2**N
        q.bits=((np.arange(q.OM)[:,None]>>np.arange(N))&1).astype(np.int8)
        for seed in range(3):
            r=np.random.default_rng(seed)
            edges=[(i,j) for i in range(N) for j in range(i+1,N) if r.random()<0.35]
            H,_=q.landscape(edges)
            for p in (1,2,3):
                x=r.uniform(0,1.5,2*p)
                d=np.abs(q.qaoa_p(x,H,p)-qiskit_probs(x,edges,N,p)).max()
                worst=max(worst,d)
    print("max |diff| de probabilidades numpy vs Qiskit:",worst)
    assert worst<1e-10; print("OK")
