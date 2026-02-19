"""
Experiment 01 — Grover ideal (1 marked state, 2 qubits)
"""

from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

shots = 2048

def grover_iteration():
    qc = QuantumCircuit(2, 2)

    # Initialize |s>
    qc.h([0, 1])

    # Oracle: mark |11>
    qc.cz(0, 1)

    # Diffusion operator
    qc.h([0, 1])
    qc.x([0, 1])
    qc.h(1)
    qc.cx(0, 1)
    qc.h(1)
    qc.x([0, 1])
    qc.h([0, 1])

    qc.measure([0, 1], [0, 1])
    return qc

sim = AerSimulator()
qc = grover_iteration()
counts = sim.run(qc, shots=shots).result().get_counts()

print("\n=== Experiment 01 — Grover ideal ===")
print("Counts:", counts)
print("Success probability |11>:", counts.get("11", 0) / shots)
print("Expected: high probability on |11>")
