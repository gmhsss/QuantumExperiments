"""
Experiment 02 — Grover under depolarizing noise
"""

from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, depolarizing_error

shots = 2048
noise_levels = [0.0, 0.05, 0.1, 0.2]
iterations = [1, 2, 3, 4]

def grover_circuit(k):
    qc = QuantumCircuit(2, 2)
    qc.h([0, 1])

    for _ in range(k):
        qc.cz(0, 1)
        qc.h([0, 1])
        qc.x([0, 1])
        qc.h(1)
        qc.cx(0, 1)
        qc.h(1)
        qc.x([0, 1])
        qc.h([0, 1])

    qc.measure([0, 1], [0, 1])
    return qc

def noise_model(p):
    nm = NoiseModel()
    if p > 0:
        nm.add_all_qubit_quantum_error(depolarizing_error(p, 1), ["h", "x"])
        nm.add_all_qubit_quantum_error(depolarizing_error(p, 2), ["cx", "cz"])
    return nm

print("\n=== Experiment 02 — Grover under noise ===")

for p in noise_levels:
    print(f"\n--- noise p={p} ---")
    sim = AerSimulator(noise_model=noise_model(p))

    for k in iterations:
        counts = sim.run(grover_circuit(k), shots=shots).result().get_counts()
        success = counts.get("11", 0) / shots
        print(f"iterations={k} -> P(|11>)={success:.3f}")
