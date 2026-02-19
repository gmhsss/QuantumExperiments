"""
Experiment 04 — Deutsch–Jozsa Algorithm (n=2)

We decide whether a Boolean function f: {0,1}^2 -> {0,1}
is constant or balanced with a single oracle query.

Decision rule (ideal):
- Measure 00 on the input register => CONSTANT
- Anything else => BALANCED
"""

from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

shots = 2048

# Register layout:
# q0, q1 = input qubits (2-bit x)
# q2      = ancilla qubit (y)

def oracle_constant_zero():
    qc = QuantumCircuit(3)
    # f(x)=0 => do nothing
    return qc

def oracle_constant_one():
    qc = QuantumCircuit(3)
    # f(x)=1 => y ^= 1
    qc.x(2)
    return qc

def oracle_balanced_x0():
    qc = QuantumCircuit(3)
    # f(x)=x0 => y ^= x0
    qc.cx(0, 2)
    return qc

def oracle_balanced_x1():
    qc = QuantumCircuit(3)
    # f(x)=x1 => y ^= x1
    qc.cx(1, 2)
    return qc

def oracle_balanced_x0_xor_x1():
    qc = QuantumCircuit(3)
    # f(x)=x0 XOR x1 => y ^= x0, y ^= x1
    qc.cx(0, 2)
    qc.cx(1, 2)
    return qc

oracles = {
    "constant_zero": oracle_constant_zero,
    "constant_one": oracle_constant_one,
    "balanced_x0": oracle_balanced_x0,
    "balanced_x1": oracle_balanced_x1,
    "balanced_x0_xor_x1": oracle_balanced_x0_xor_x1,
}

def deutsch_jozsa(oracle_builder):
    qc = QuantumCircuit(3, 2)

    # ancilla |1>
    qc.x(2)

    # create superposition on inputs and |-> on ancilla
    qc.h(0)
    qc.h(1)
    qc.h(2)

    # apply oracle Uf
    oracle = oracle_builder()
    qc.compose(oracle, inplace=True)

    # interference on input register
    qc.h(0)
    qc.h(1)

    # measure only the input register
    qc.measure(0, 0)
    qc.measure(1, 1)

    return qc

def classify(counts: dict) -> str:
    # Qiskit returns bitstrings as c1c0 for 2 classical bits.
    # We measured q0->c0 and q1->c1, so "00" means both measured 0.
    return "CONSTANT" if counts.get("00", 0) == shots else "BALANCED"

sim = AerSimulator()

print("\n=== Deutsch–Jozsa (n=2) Results ===")

for name, builder in oracles.items():
    qc = deutsch_jozsa(builder)
    counts = sim.run(qc, shots=shots).result().get_counts()

    print(f"\nOracle: {name}")
    print(qc.draw())
    print("Counts:", counts)
    print("→ Classified as:", classify(counts))

print("\nExpected (ideal):")
print("- constant_* => always '00'")
print("- balanced_* => never '00'")
