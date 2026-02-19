"""
Experiment 03 — Agentic stopping rule for Grover
"""

from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, depolarizing_error

shots = 2048
noise_p = 0.1
max_iters = 6

def grover_step(qc):
    qc.cz(0, 1)
    qc.h([0, 1])
    qc.x([0, 1])
    qc.h(1)
    qc.cx(0, 1)
    qc.h(1)
    qc.x([0, 1])
    qc.h([0, 1])

def build_circuit(k):
    qc = QuantumCircuit(2, 2)
    qc.h([0, 1])
    for _ in range(k):
        grover_step(qc)
    qc.measure([0, 1], [0, 1])
    return qc

def noise_model(p):
    nm = NoiseModel()
    nm.add_all_qubit_quantum_error(depolarizing_error(p, 1), ["h", "x"])
    nm.add_all_qubit_quantum_error(depolarizing_error(p, 2), ["cx", "cz"])
    return nm

sim = AerSimulator(noise_model=noise_model(noise_p))

print("\n=== Experiment 03 — Agentic stopping rule ===")
print("noise p =", noise_p)

best_k = None
best_p = 0.0

for k in range(1, max_iters + 1):
    counts = sim.run(build_circuit(k), shots=shots).result().get_counts()
    p_succ = counts.get("11", 0) / shots
    print(f"iterations={k} -> P(|11>)={p_succ:.3f}")

    if p_succ >= best_p:
        best_p = p_succ
        best_k = k
    else:
        print("→ Agent stops: performance decreased")
        break

print("\nAgent decision:")
print("Optimal iterations =", best_k)
print("Success probability =", round(best_p, 3))
