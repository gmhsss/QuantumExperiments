from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

shots = 4096

def correlation_rate(counts: dict) -> float:
    """
    Computes P(bit0 == bit1).
    Note: Qiskit returns bitstrings as c1c0.
    Here we measured q0->c0 and q1->c1.
    """
    same = counts.get("00", 0) + counts.get("11", 0)
    return same / shots

# Bell |Phi+>
qc = QuantumCircuit(2, 2)
qc.h(0)
qc.cx(0, 1)
qc.measure(0, 0)
qc.measure(1, 1)

print("\n=== Quantum Circuit (Bell |Phi+>) ===")
print(qc.draw())

sim = AerSimulator()
counts = sim.run(qc, shots=shots).result().get_counts()

print("\n=== Measurement counts ===")
print(counts)

rate = correlation_rate(counts)
print("\n=== Correlation metric ===")
print("P(bit0 == bit1) =", round(rate, 6))

print("\nExpected: correlation rate ≈ 1.0")
