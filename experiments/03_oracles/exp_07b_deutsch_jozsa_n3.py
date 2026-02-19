"""
Experiment 07B — Deutsch–Jozsa scaling (n=3)

We classify f: {0,1}^3 -> {0,1} as CONSTANT or BALANCED with 1 oracle query.
Decision rule (ideal):
- measure 000 on input register => CONSTANT
- otherwise => BALANCED
"""

from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

shots = 2048

# Qubits:
# q0,q1,q2 = inputs
# q3 = ancilla (y)

def oracle_constant_zero():
    return QuantumCircuit(4)

def oracle_constant_one():
    qc = QuantumCircuit(4)
    qc.x(3)
    return qc

def oracle_balanced_x0():
    qc = QuantumCircuit(4)
    qc.cx(0, 3)
    return qc

def oracle_balanced_x1():
    qc = QuantumCircuit(4)
    qc.cx(1, 3)
    return qc

def oracle_balanced_x2():
    qc = QuantumCircuit(4)
    qc.cx(2, 3)
    return qc

def oracle_balanced_parity():
    # f(x)=x0 XOR x1 XOR x2
    qc = QuantumCircuit(4)
    qc.cx(0, 3)
    qc.cx(1, 3)
    qc.cx(2, 3)
    return qc

oracles = {
    "constant_zero": oracle_constant_zero,
    "constant_one": oracle_constant_one,
    "balanced_x0": oracle_balanced_x0,
    "balanced_x1": oracle_balanced_x1,
    "balanced_x2": oracle_balanced_x2,
    "balanced_parity": oracle_balanced_parity,
}

def deutsch_jozsa_n3(oracle_builder):
    qc = QuantumCircuit(4, 3)

    # ancilla |1>
    qc.x(3)

    # superposition on inputs + |-> on ancilla
    qc.h(0); qc.h(1); qc.h(2); qc.h(3)

    # oracle
    qc.compose(oracle_builder(), inplace=True)

    # interference on input register
    qc.h(0); qc.h(1); qc.h(2)

    # measure inputs only
    qc.measure(0, 0)  # c0
    qc.measure(1, 1)  # c1
    qc.measure(2, 2)  # c2

    return qc

def classify(counts):
    # Qiskit bitstring for 3 classical bits is c2c1c0.
    # With q0->c0, q1->c1, q2->c2, "000" means all zeros.
    return "CONSTANT" if counts.get("000", 0) == shots else "BALANCED"

sim = AerSimulator()

print("\n=== Experiment 07B — Deutsch–Jozsa (n=3) ===")

for name, builder in oracles.items():
    qc = deutsch_jozsa_n3(builder)
    counts = sim.run(qc, shots=shots).result().get_counts()

    print(f"\nOracle: {name}")
    print(qc.draw())
    print("Counts:", counts)
    print("→ Classified as:", classify(counts))

print("\nExpected (ideal):")
print("- constant_* => always '000'")
print("- balanced_* => never '000'")
