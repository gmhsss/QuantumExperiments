"""
Quantum Functional Information (QFI) for Maximum Independent Set (MIS)
-----------------------------------------------------------------------
Proof-of-concept implementation of the problem-space reformulation of QFI:

    Functional information belongs to the problem landscape (Omega, H(x));
    the quantum circuit only redistributes probability p_d(x) over that
    fixed landscape. Expected functional information <I_F>_d tracks how
    strongly the circuit concentrates probability on rare, high-quality
    (functional) regions as a function of circuit depth d.

Sections:
  1. Problem definition (graph, Hamiltonian, intrinsic functional landscape)
  2. Intrinsic functional information I_F(x), feasibility/optimality split
  3. Synthetic Boltzmann-like distributions p_d(x) as a depth surrogate
  4. Real QAOA circuit (Qiskit, statevector simulation) at increasing depth p
  5. Plots
"""

import numpy as np
import networkx as nx
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

RNG = np.random.default_rng(7)

# ----------------------------------------------------------------------
# 1. Problem definition
# ----------------------------------------------------------------------

N_VERTICES = 8
G = nx.erdos_renyi_graph(N_VERTICES, p=0.35, seed=42)
EDGES = list(G.edges())
N = N_VERTICES
OMEGA_SIZE = 2 ** N

A_PENALTY = 2.0   # penalizes adjacent-selected pairs (must dominate B for exact MIS)
B_REWARD = 1.0    # rewards larger sets

def bitstring_array(x_int, n=N):
    """Integer 0..2^n-1 -> numpy array of bits (x[0] = qubit 0 = vertex 0)."""
    return np.array([(x_int >> i) & 1 for i in range(n)], dtype=np.int8)

def hamiltonian(x):
    """H(x) = A * sum_{(i,j) in E} x_i x_j  -  B * sum_i x_i."""
    penalty = sum(x[i] * x[j] for (i, j) in EDGES)
    reward = x.sum()
    return A_PENALTY * penalty - B_REWARD * reward

def is_independent_set(x):
    return all(not (x[i] and x[j]) for (i, j) in EDGES)

# Enumerate the full problem space Omega = {0,1}^n
all_x = [bitstring_array(k) for k in range(OMEGA_SIZE)]
all_H = np.array([hamiltonian(x) for x in all_x])
all_valid = np.array([is_independent_set(x) for x in all_x])
all_size = np.array([x.sum() for x in all_x])

print(f"Grafo: n={N_VERTICES} vertices, {len(EDGES)} arestas, |Omega|={OMEGA_SIZE}")
print(f"Independent sets validos: {all_valid.sum()} de {OMEGA_SIZE} "
      f"({100*all_valid.sum()/OMEGA_SIZE:.2f}%)")
best_idx = np.argmax(all_size[all_valid])
best_valid_sizes = all_size[all_valid]
mis_size = best_valid_sizes.max()
print(f"Maior independent set (MIS) encontrado por enumeracao: tamanho {mis_size}")

# ----------------------------------------------------------------------
# 2. Intrinsic functional information I_F(x) and feasibility/optimality split
# ----------------------------------------------------------------------

# I_F(x) = -log2( |{y : H(y) <= H(x)}| / |Omega| )
# Rank-based: sort H ascending, count how many y have H(y) <= H(x) via rank.
order = np.argsort(all_H, kind="mergesort")
sorted_H = all_H[order]
# rank_le[i] = number of configurations with H(y) <= H(x_i) (handles ties)
rank_le = np.searchsorted(sorted_H, all_H, side="right")
I_F_all = -np.log2(rank_le / OMEGA_SIZE)

# Feasibility information: I_valid = -log2(|Omega_IS| / |Omega|)
n_valid = all_valid.sum()
I_valid = -np.log2(n_valid / OMEGA_SIZE)
print(f"I_valid (raridade de ser um independent set valido) = {I_valid:.3f} bits")

# Conditional quality given feasibility, for k = mis_size (the optimum found)
k_star = int(mis_size)
valid_sizes = all_size[all_valid]
n_Fk_given_IS = (valid_sizes >= k_star).sum()
I_quality_given_IS = -np.log2(n_Fk_given_IS / n_valid)
print(f"I_quality(k={k_star} | IS) = {I_quality_given_IS:.3f} bits "
      f"(raro entre os validos)")

# Unconditional quality-at-k (over the whole space, not just valid ones)
n_Fk_total = ((all_size >= k_star) & all_valid).sum()
I_quality_total = -np.log2(n_Fk_total / OMEGA_SIZE)
print(f"I_F(k={k_star}) [nao condicional] = {I_quality_total:.3f} bits")
print(f"Identidade I_valid + I_quality(k|IS) = "
      f"{I_valid + I_quality_given_IS:.3f}  (deve == I_F(k) acima)")

# ----------------------------------------------------------------------
# 3. Synthetic Boltzmann-like distributions p_d(x) as a depth surrogate
# ----------------------------------------------------------------------

D_STEPS = 12
betas = np.linspace(0.0, 3.0, D_STEPS)  # beta=0 -> uniform; beta large -> concentrated

def boltzmann_dist(beta):
    logits = -beta * all_H
    logits -= logits.max()
    w = np.exp(logits)
    return w / w.sum()

# Threshold h for "functional" set F_h: use the Hamiltonian value of the
# best-known solution found by enumeration (k_star), i.e. h* = min H among valid x of size >= k_star
h_star = all_H[all_valid & (all_size >= k_star)].min()
F_h_mask = all_H <= h_star
P_problem_h = F_h_mask.sum() / OMEGA_SIZE
I_F_problem_h = -np.log2(P_problem_h)
print(f"\nLimiar h* (energia do melhor MIS) = {h_star:.2f}")
print(f"P_problem(h*) = {P_problem_h:.6e}  ->  I_F,problem(h*) = {I_F_problem_h:.3f} bits")

expected_IF_synth = []
P_h_synth = []
expected_size_synth = []
P_feasible_synth = []
A_F_synth = []
G_F_synth = []

for beta in betas:
    p_d = boltzmann_dist(beta)
    expected_IF_synth.append(np.sum(p_d * I_F_all))
    P_h = np.sum(p_d[F_h_mask])
    P_h_synth.append(P_h)
    expected_size_synth.append(np.sum(p_d * all_size))
    P_feasible_synth.append(np.sum(p_d[all_valid]))
    A_F = P_h / P_problem_h if P_problem_h > 0 else np.inf
    A_F_synth.append(A_F)
    G_F_synth.append(np.log2(A_F) if A_F > 0 else -np.inf)

expected_IF_synth = np.array(expected_IF_synth)
P_h_synth = np.array(P_h_synth)
expected_size_synth = np.array(expected_size_synth)
P_feasible_synth = np.array(P_feasible_synth)
G_F_synth = np.array(G_F_synth)

# ----------------------------------------------------------------------
# 4. Real QAOA circuit (Qiskit), statevector at increasing depth p
# ----------------------------------------------------------------------

from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

def qaoa_circuit(n, edges, gammas, betas_mix):
    """Standard QAOA ansatz for a diagonal cost Hamiltonian encoding MIS."""
    p = len(gammas)
    qc = QuantumCircuit(n)
    qc.h(range(n))  # uniform superposition
    for layer in range(p):
        g = gammas[layer]
        # Cost unitary: exp(-i*g*H_C) with H_C = A*sum ZZ-like penalty - B*sum Z-like reward
        # Encode via standard QUBO->Ising mapping using x_i in {0,1}: cost term A*x_i*x_j - B*x_i
        # Implement penalty on edges via CNOT-RZ-CNOT (ZZ interaction), and single-qubit RZ for reward.
        for (i, j) in edges:
            qc.cx(i, j)
            qc.rz(2 * g * A_PENALTY / 4, j)
            qc.cx(i, j)
        for i in range(n):
            qc.rz(-2 * g * (-B_REWARD) / 2, i)  # sign convention for reward term
        # Mixer unitary: exp(-i*beta*sum X_i)
        b = betas_mix[layer]
        for i in range(n):
            qc.rx(2 * b, i)
    return qc

P_MAX = 6  # QAOA depth levels to test
qaoa_expected_IF = []
qaoa_P_h = []
qaoa_expected_size = []
qaoa_P_feasible = []
qaoa_G_F = []

# Fixed, hand-picked schedule (annealing-like: gamma grows, beta shrinks with depth)
for p in range(1, P_MAX + 1):
    gammas = np.linspace(0.2, 0.8, p)
    betas_mix = np.linspace(0.8, 0.1, p)
    qc = qaoa_circuit(N_VERTICES, EDGES, gammas, betas_mix)
    sv = Statevector.from_instruction(qc)
    probs = sv.probabilities()  # length 2^n, index = integer bitstring (qubit 0 = LSB)
    qaoa_expected_IF.append(np.sum(probs * I_F_all))
    qaoa_P_h.append(np.sum(probs[F_h_mask]))
    qaoa_expected_size.append(np.sum(probs * all_size))
    qaoa_P_feasible.append(np.sum(probs[all_valid]))
    A_F_q = qaoa_P_h[-1] / P_problem_h if P_problem_h > 0 else np.inf
    qaoa_G_F.append(np.log2(A_F_q) if A_F_q > 0 else -np.inf)

qaoa_expected_IF = np.array(qaoa_expected_IF)
qaoa_P_h = np.array(qaoa_P_h)
qaoa_expected_size = np.array(qaoa_expected_size)
qaoa_P_feasible = np.array(qaoa_P_feasible)
qaoa_G_F = np.array(qaoa_G_F)

print("\n--- QAOA (Qiskit, statevector) ---")
for p in range(1, P_MAX + 1):
    print(f"p={p}: <I_F>={qaoa_expected_IF[p-1]:.3f} bits, "
          f"P_feasible={qaoa_P_feasible[p-1]:.3f}, "
          f"E[|x|]={qaoa_expected_size[p-1]:.2f}, "
          f"G_F(h*)={qaoa_G_F[p-1]:.2f} bits")

# ----------------------------------------------------------------------
# 5. Plots
# ----------------------------------------------------------------------

fig, axes = plt.subplots(2, 2, figsize=(11, 8))

ax = axes[0, 0]
ax.plot(betas, expected_IF_synth, "o-", label="Boltzmann sintetico (vs beta)")
ax.set_xlabel(r"$\beta$ (concentracao sintetica)")
ax.set_ylabel(r"$\langle I_F \rangle_d$ (bits)")
ax.set_title("Informacao funcional esperada (distribuicoes sinteticas)")
ax.legend()
ax.grid(alpha=0.3)

ax2 = axes[0, 0].twiny()
ax2.plot(range(1, P_MAX + 1), qaoa_expected_IF, "s--", color="tab:red", label="QAOA (profundidade p)")
ax2.set_xlabel("Profundidade QAOA p")

ax = axes[0, 1]
ax.plot(betas, P_feasible_synth, "o-", label="Sintetico")
ax.plot(np.linspace(betas.min(), betas.max(), P_MAX), qaoa_P_feasible, "s--",
        color="tab:red", label="QAOA (reescalado em p)")
ax.axhline(all_valid.sum() / OMEGA_SIZE, color="gray", ls=":", label="Uniforme (baseline)")
ax.set_xlabel(r"$\beta$ / profundidade (reescalada)")
ax.set_ylabel(r"$P_d(\mathrm{feasible})$")
ax.set_title("Probabilidade de amostrar um independent set valido")
ax.legend()
ax.grid(alpha=0.3)

ax = axes[1, 0]
ax.plot(betas, expected_size_synth, "o-", label="Sintetico")
ax.plot(np.linspace(betas.min(), betas.max(), P_MAX), qaoa_expected_size, "s--",
        color="tab:red", label="QAOA (reescalado em p)")
ax.axhline(all_size.mean(), color="gray", ls=":", label="Uniforme (baseline)")
ax.set_xlabel(r"$\beta$ / profundidade (reescalada)")
ax.set_ylabel(r"$E[|x|]$")
ax.set_title("Tamanho esperado do subconjunto amostrado")
ax.legend()
ax.grid(alpha=0.3)

ax = axes[1, 1]
ax.plot(betas, G_F_synth, "o-", label="Sintetico")
ax.plot(np.linspace(betas.min(), betas.max(), P_MAX), qaoa_G_F, "s--",
        color="tab:red", label="QAOA (reescalado em p)")
ax.axhline(0, color="gray", ls=":", label=r"$G_F=0$ (sem ganho)")
ax.set_xlabel(r"$\beta$ / profundidade (reescalada)")
ax.set_ylabel(r"$G_F(C,h^*)$ (bits)")
ax.set_title("Ganho funcional em relacao ao espaco do problema")
ax.legend()
ax.grid(alpha=0.3)

fig.suptitle(f"QFI-MIS: grafo com n={N_VERTICES}, |E|={len(EDGES)}, "
             f"MIS={mis_size}, I_F,problem(h*)={I_F_problem_h:.2f} bits", fontsize=11)
fig.tight_layout(rect=[0, 0, 1, 0.96])
fig.savefig("qfi_mis_results.png", dpi=150)
print("\nGrafico salvo em qfi_mis_results.png")

# Histogram of I_F(x) values, colored by feasibility
fig2, ax = plt.subplots(figsize=(7, 4.5))
ax.hist(I_F_all[all_valid], bins=25, alpha=0.7, label="Independent sets validos", color="tab:green")
ax.hist(I_F_all[~all_valid], bins=25, alpha=0.5, label="Configuracoes invalidas", color="tab:gray")
ax.axvline(I_F_problem_h, color="black", ls="--", label=r"$I_F$ no limiar $h^*$")
ax.set_xlabel(r"$I_F(x)$ (bits)")
ax.set_ylabel("Numero de configuracoes")
ax.set_title("Distribuicao de informacao funcional intrinseca sobre " + r"$\Omega$")
ax.legend()
fig2.tight_layout()
fig2.savefig("qfi_mis_histogram.png", dpi=150)
print("Histograma salvo em qfi_mis_histogram.png")

print("\nResumo final:")
print(f"  I_valid = {I_valid:.3f} bits")
print(f"  I_quality(k={k_star}|IS) = {I_quality_given_IS:.3f} bits")
print(f"  I_F,problem(h*) = {I_F_problem_h:.3f} bits")
print(f"  QAOA p=1: <I_F>={qaoa_expected_IF[0]:.3f}  ->  p={P_MAX}: <I_F>={qaoa_expected_IF[-1]:.3f}")
print(f"  QAOA G_F(h*) p=1: {qaoa_G_F[0]:.2f} bits  ->  p={P_MAX}: {qaoa_G_F[-1]:.2f} bits")

# ----------------------------------------------------------------------
# 4b. Optimized QAOA (COBYLA minimizing <H>) -- intermediate layers
# ----------------------------------------------------------------------
from scipy.optimize import minimize

P_OPT = 4

def expected_H(params):
    gammas = params[:P_OPT]
    betas_mix = params[P_OPT:]
    qc = qaoa_circuit(N_VERTICES, EDGES, gammas, betas_mix)
    sv = Statevector.from_instruction(qc)
    probs = sv.probabilities()
    return np.sum(probs * all_H)

x0 = np.concatenate([np.full(P_OPT, 0.5), np.full(P_OPT, 0.5)])
res = minimize(expected_H, x0, method="COBYLA",
                options={"maxiter": 300, "rhobeg": 0.5})
gammas_opt, betas_opt = res.x[:P_OPT], res.x[P_OPT:]
print(f"\nCOBYLA otimizado: <H> final = {res.fun:.3f} (vs H* = {h_star:.2f})")

# Intermediate statevectors of the OPTIMIZED circuit, layer by layer
opt_expected_IF, opt_P_feasible, opt_expected_size, opt_G_F = [], [], [], []
for d in range(1, P_OPT + 1):
    qc_d = qaoa_circuit(N_VERTICES, EDGES, gammas_opt[:d], betas_opt[:d])
    sv = Statevector.from_instruction(qc_d)
    probs = sv.probabilities()
    opt_expected_IF.append(np.sum(probs * I_F_all))
    opt_P_feasible.append(np.sum(probs[all_valid]))
    opt_expected_size.append(np.sum(probs * all_size))
    P_h_opt = np.sum(probs[F_h_mask])
    A_F_opt = P_h_opt / P_problem_h if P_problem_h > 0 else np.inf
    opt_G_F.append(np.log2(A_F_opt) if A_F_opt > 0 else -np.inf)

print("\n--- QAOA OTIMIZADO (COBYLA), estados intermediarios ---")
for d in range(1, P_OPT + 1):
    print(f"d={d}: <I_F>={opt_expected_IF[d-1]:.3f} bits, "
          f"P_feasible={opt_P_feasible[d-1]:.3f}, "
          f"E[|x|]={opt_expected_size[d-1]:.2f}, "
          f"G_F(h*)={opt_G_F[d-1]:.2f} bits")

fig3, axes3 = plt.subplots(1, 3, figsize=(13, 4))
d_range = range(1, P_OPT + 1)
axes3[0].plot(d_range, opt_expected_IF, "o-", color="tab:blue")
axes3[0].set_xlabel("Profundidade d (camadas QAOA otimizadas)")
axes3[0].set_ylabel(r"$\langle I_F \rangle_d$ (bits)")
axes3[0].set_title("Informacao funcional esperada")
axes3[0].grid(alpha=0.3)

axes3[1].plot(d_range, opt_P_feasible, "o-", color="tab:green", label="P(feasible)")
axes3[1].plot(d_range, np.array(opt_expected_size) / mis_size, "s--", color="tab:orange",
              label="E[|x|] / MIS (normalizado)")
axes3[1].axhline(all_valid.sum()/OMEGA_SIZE, color="gray", ls=":", label="baseline uniforme")
axes3[1].set_xlabel("Profundidade d")
axes3[1].set_title("Feasibility vs. tamanho esperado")
axes3[1].legend(fontsize=8)
axes3[1].grid(alpha=0.3)

axes3[2].plot(d_range, opt_G_F, "o-", color="tab:red")
axes3[2].axhline(0, color="gray", ls=":")
axes3[2].set_xlabel("Profundidade d")
axes3[2].set_ylabel(r"$G_F(C_d, h^*)$ (bits)")
axes3[2].set_title("Ganho funcional (circuito otimizado)")
axes3[2].grid(alpha=0.3)

fig3.suptitle("QAOA com parametros otimizados (COBYLA minimizando <H>): estados intermediarios", fontsize=11)
fig3.tight_layout(rect=[0, 0, 1, 0.94])
fig3.savefig("qfi_mis_optimized_depth.png", dpi=150)
print("Grafico salvo em qfi_mis_optimized_depth.png")
