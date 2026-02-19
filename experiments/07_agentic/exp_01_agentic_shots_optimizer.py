"""
Experiment 01 — Agentic optimization of shots
Goal: keep success probability >= target_accuracy
"""

from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit_aer.noise import depolarizing_error, NoiseModel

target_accuracy = 0.95
shots_candidates = [64, 128, 256, 512, 1024]
noise_levels = [0.0, 0.05, 0.1, 0.2]

def bell_circuit():
    qc = QuantumCircuit(2, 2)
    qc.h(0)
    qc.cx(0, 1)
    qc.measure([0, 1], [0, 1])
    return qc

def metric(counts, shots):
    return (counts.get("00", 0) + counts.get("11", 0)) / shots

def build_noise(p):
    nm = NoiseModel()
    if p > 0:
        nm.add_all_qubit_quantum_error(depolarizing_error(p, 1), ["h"])
        nm.add_all_qubit_quantum_error(depolarizing_error(p, 2), ["cx"])
    return nm

print("\n=== Agentic shots optimization ===")
print("Target accuracy =", target_accuracy)

for p in noise_levels:
    print(f"\n--- Noise p={p} ---")
    sim = AerSimulator(noise_model=build_noise(p))
    qc = bell_circuit()

    chosen = None
    for shots in shots_candidates:
        counts = sim.run(qc, shots=shots).result().get_counts()
        acc = metric(counts, shots)
        print(f"shots={shots:4d} -> accuracy={acc:.3f}")

        if acc >= target_accuracy:
            chosen = shots
            break

    if chosen:
        print("→ Agent choice:", chosen, "shots")
    else:
        print("→ Agent failed to meet target accuracy")
