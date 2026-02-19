from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

shots = 2048

def oracle_constant_zero():
    qc = QuantumCircuit(2)
    return qc

def oracle_constant_one():
    qc = QuantumCircuit(2)
    qc.x(1)
    return qc

def oracle_identity():
    qc = QuantumCircuit(2)
    qc.cx(0, 1)
    return qc

def oracle_not():
    qc = QuantumCircuit(2)
    qc.cx(0, 1)
    qc.x(1)
    return qc

oracles = {
    "constant_zero": oracle_constant_zero,
    "constant_one": oracle_constant_one,
    "identity": oracle_identity,
    "not": oracle_not,
}

def deutsch_algorithm(oracle_builder):
    qc = QuantumCircuit(2, 1)
    qc.x(1)
    qc.h(0)
    qc.h(1)
    oracle = oracle_builder()
    qc.compose(oracle, inplace=True)
    qc.h(0)
    qc.measure(0, 0)
    return qc

print("\\n=== Deutsch Algorithm Results ===")
sim = AerSimulator()

for name, oracle_builder in oracles.items():
    qc = deutsch_algorithm(oracle_builder)
    counts = sim.run(qc, shots=shots).result().get_counts()
    print(f"\\nOracle: {name}")
    print(qc.draw())
    print("Counts:", counts)
    if "0" in counts:
        print("→ Classified as: CONSTANT")
    else:
        print("→ Classified as: BALANCED")
