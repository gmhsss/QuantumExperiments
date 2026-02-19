"""
Experiment 03 — Agentic threshold policy: maximum tolerable noise

Task:
- Prepare Bell |Phi+>
- Measure correlation Corr = P(00)+P(11)
- Under depolarizing noise, find the largest p such that Corr >= target_corr

Agent:
- coarse scan over p
- refine around best interval
"""

from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, depolarizing_error

shots = 2048
target_corr = 0.90

coarse_grid = [0.00, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40]
refine_step = 0.01

def bell_measure_z():
    qc = QuantumCircuit(2, 2)
    qc.h(0)
    qc.cx(0, 1)
    qc.measure([0, 1], [0, 1])
    return qc

def corr_metric(counts, shots):
    return (counts.get("00", 0) + counts.get("11", 0)) / shots

def build_dep_noise(p: float) -> NoiseModel:
    nm = NoiseModel()
    if p > 0:
        e1 = depolarizing_error(p, 1)
        e2 = depolarizing_error(p, 2)
        nm.add_all_qubit_quantum_error(e1, ["h"])
        nm.add_all_qubit_quantum_error(e2, ["cx"])
    return nm

def eval_corr(p: float) -> float:
    sim = AerSimulator(noise_model=build_dep_noise(p))
    counts = sim.run(bell_measure_z(), shots=shots).result().get_counts()
    return corr_metric(counts, shots)

print("\n=== Experiment 03 — Agentic noise threshold policy (depolarizing) ===")
print("shots =", shots, "| target_corr =", target_corr)

# 1) coarse scan
best_p = None
best_corr = None

print("\n--- Coarse scan ---")
for p in coarse_grid:
    c = eval_corr(p)
    ok = c >= target_corr
    print(f"p={p:.2f} -> Corr={c:.4f} | {'OK' if ok else 'FAIL'}")
    if ok:
        best_p = p
        best_corr = c

if best_p is None:
    print("\nNo p in coarse grid meets target_corr. Try lowering target or increasing shots.")
    raise SystemExit(0)

# 2) refine around [best_p - step, best_p + step]
low = max(0.0, best_p - 0.05)
high = min(0.5, best_p + 0.05)

print(f"\nRefining around best coarse p={best_p:.2f} in [{low:.2f}, {high:.2f}] ...")

refined_best_p = best_p
refined_best_corr = best_corr

p = low
while p <= high + 1e-9:
    c = eval_corr(p)
    if c >= target_corr and p >= refined_best_p:
        refined_best_p = p
        refined_best_corr = c
    print(f"p={p:.2f} -> Corr={c:.4f}")
    p = round(p + refine_step, 2)

print("\n=== Threshold estimate ===")
print("Estimated max p with Corr >= target:", refined_best_p)
print("Corr at estimate:", round(refined_best_corr, 4))

print("\nInterpretation:")
print("- This is a simple 'policy' for operating range under noise.")
print("- If you change target_corr, shots, or metric, the threshold changes.")
