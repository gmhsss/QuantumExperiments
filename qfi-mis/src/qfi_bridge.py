"""
Ponte entre o repo do David (enbpar-quantum-qaoa) e a metrica QFI do projeto.

Uso (a partir de qualquer pasta):
    PYTHONPATH=<repo>/src python qfi_bridge.py

O que faz:
  1. Monta um grafo geometrico pequeno (substitui o CSV real, que nao veio no dump).
  2. Usa build_mis_qubo / qubo_to_ising / run_qaoa DO DAVID, sem modifica-los.
  3. Verifica que o custo do David e a nossa H(x) coincidem (A=beta=2, B=alpha=1).
  4. Enumera Omega (2^n), calcula I_F(x) pela nossa definicao.
  5. Pega os parametros otimos devolvidos pelo run_qaoa e reconstroi o estado
     EXATO apos cada camada d=1..p (Statevector), dando p_d(x) sem ruido de shots.
  6. Calcula <I_F>_d, P_d(h*), G_F e P_d(viavel); compara com a "distribution"
     que o proprio run_qaoa devolve (amostrada, so a profundidade final).
"""
import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

from core.qubo_formalization import build_mis_qubo, qubo_to_ising, classical_cost
from core.qaoa_solver import run_qaoa
from core.classical_baseline import solve_exact_ilp
from core.solution_decoder import integer_to_bits

# ------------------------------------------------------------------ grafo
import os
N = int(os.environ.get("QN", "12"))
rng = np.random.default_rng(3)
pts = rng.uniform(0, 1, size=(N, 2))
RADIUS = 0.33
edges = [(i, j) for i in range(N) for j in range(i + 1, N)
         if np.linalg.norm(pts[i] - pts[j]) < RADIUS]
print(f"grafo: n={N}, |E|={len(edges)}")

# ------------------------------------------------------------------ modelo (David)
linear, quadratic, off = build_mis_qubo(N, edges)          # alpha=1, beta=2
model = qubo_to_ising(N, linear, quadratic, off)

# ------------------------------------------------------------------ Omega e I_F(x)
OMEGA = 2 ** N
bits_all = np.array([integer_to_bits(k, N) for k in range(OMEGA)], dtype=np.int8)
H_all = np.array([classical_cost(b, edges) for b in bits_all])      # custo do David
valid = np.array([all(not (b[i] and b[j]) for i, j in edges) for b in bits_all])
size = bits_all.sum(axis=1)

# nossa H(x) = A*sum x_i x_j - B*sum x_i com A=2, B=1  -> deve ser identica
H_ours = 2.0 * np.array([sum(b[i] * b[j] for i, j in edges) for b in bits_all]) - 1.0 * size
assert np.allclose(H_all, H_ours), "custo do David != nossa H(x)"
print("OK: custo do David == nossa H(x) (A=2, B=1) em todas as", OMEGA, "configuracoes")

order = np.sort(H_all)
rank_le = np.searchsorted(order, H_all, side="right")        # |{y: H(y) <= H(x)}|
I_F = -np.log2(rank_le / OMEGA)

_, exact_cost = solve_exact_ilp(N, edges)                    # otimo via ILP do David
h_star = exact_cost
F_h = H_all <= h_star + 1e-9
print(f"otimo (ILP) = {exact_cost:.1f} | |F_h*| = {F_h.sum()} | "
      f"I_F(h*) = {-np.log2(F_h.sum() / OMEGA):.3f} bits | validos: {valid.sum()}/{OMEGA}")

# ------------------------------------------------------------------ treino (David)
P = 3
res = run_qaoa(model, reps=P, shots=4096, seed=int(os.environ.get("QSEED", "1")), maxiter=150, optimizer_name="COBYLA")
params = res.optimal_parameters
print("parametros otimos:", {k: round(v, 3) for k, v in params.items()})

def get(prefix, k):
    # QAOAAnsatz do Qiskit nomeia os parametros com letras gregas; aceita as duas grafias
    for key, v in params.items():
        if key in (f"{prefix}[{k}]",):
            return v
    greek = {"gamma": "γ", "beta": "β"}[prefix]
    return params[f"{greek}[{k}]"]

gammas = [get("gamma", k) for k in range(P)]
betas = [get("beta", k) for k in range(P)]

def qaoa_state(d):
    """Estado exato apos d camadas, usando os MESMOS parametros otimos (camadas 0..d-1)."""
    qc = QuantumCircuit(N)
    qc.h(range(N))
    for layer in range(d):
        for i, c in model.h.items():
            if c: qc.rz(2 * gammas[layer] * c, i)
        for (i, j), c in model.j.items():
            if c: qc.rzz(2 * gammas[layer] * c, i, j)
        for i in range(N):
            qc.rx(2 * betas[layer], i)
    return Statevector.from_instruction(qc).probabilities()

# sanidade: o estado exato com p camadas tem a energia que o run_qaoa reportou?
p_final = qaoa_state(P)
E_exact = float(np.sum(p_final * H_all))
print(f"energia exata das {P} camadas = {E_exact:.4f} | reportada pelo run_qaoa (amostrada) = "
      f"{res.expectation_qubo:.4f}")

# ------------------------------------------------------------------ QFI por camada
P_unif = F_h.mean()
print("\n d | <I_F>_d | P_d(viavel) | E[|x|] | P_d(h*) |  G_F (bits)")
rows = []
for d in range(0, P + 1):
    p_d = np.full(OMEGA, 1 / OMEGA) if d == 0 else qaoa_state(d)
    EIF = float(np.sum(p_d * I_F))
    Pf = float(np.sum(p_d[valid]))
    Es = float(np.sum(p_d * size))
    Ph = float(np.sum(p_d[F_h]))
    G = float(np.log2(Ph / P_unif)) if Ph > 0 else float("-inf")
    rows.append((d, EIF, Pf, Es, Ph, G))
    print(f" {d} | {EIF:7.3f} | {Pf:11.3f} | {Es:6.2f} | {Ph:7.4f} | {G:8.2f}")

# ------------------------------------------------------------------ distribuicao amostrada vs exata
dist = res.distribution
tv = 0.5 * sum(abs(dist.get(k, 0.0) - p_final[k]) for k in range(OMEGA))
print(f"\ndistancia de variacao total entre a distribuicao amostrada (4096 shots) e a exata: {tv:.3f}")
mass_h_samp = sum(v for k, v in dist.items() if F_h[k])
print(f"massa em F_h*: amostrada = {mass_h_samp:.4f} | exata = {p_final[F_h].sum():.4f}")
