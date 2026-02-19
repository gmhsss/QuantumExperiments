"""
Experiment 05 — Random Oracles + Automatic Classification (Deutsch–Jozsa n=2)

We generate random Boolean functions f: {0,1}^2 -> {0,1} that are
either CONSTANT or BALANCED, compile them into an oracle Uf, and
use Deutsch–Jozsa to classify them using a single oracle query.

This is a stepping stone toward agentic experiment loops:
- generate hypothesis (oracle),
- run experiment (DJ circuit),
- analyze output (classification),
- report metrics (accuracy).
"""

import random
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

shots = 1024
trials = 20
seed = 42

random.seed(seed)

# Inputs x in {00, 01, 10, 11}
X = [(0,0), (0,1), (1,0), (1,1)]

def is_constant(table):
    return all(v == table[0] for v in table)

def is_balanced(table):
    return sum(table) == 2  # for 4 inputs, balanced means two 1s and two 0s

def random_constant_table():
    v = random.choice([0, 1])
    return [v, v, v, v]

def random_balanced_table():
    # choose exactly two inputs to map to 1
    ones_idx = set(random.sample(range(4), 2))
    return [1 if i in ones_idx else 0 for i in range(4)]

def oracle_from_truth_table(table):
    """
    Build Uf for f(x0,x1) using a reversible embedding:
      Uf |x, y> = |x, y XOR f(x)>

    Implementation trick:
    For each input x where f(x)=1, apply an X on controls to match that x,
    then a multi-controlled X onto y, then undo the X gates.
    """
    qc = QuantumCircuit(3)  # q0,q1 inputs, q2 ancilla y

    for (x0, x1), fx in zip(X, table):
        if fx == 0:
            continue

        # Map |x0 x1> to |11> using X on 0-controls
        if x0 == 0:
            qc.x(0)
        if x1 == 0:
            qc.x(1)

        # Apply controlled-controlled-NOT (Toffoli) onto y (q2)
        qc.ccx(0, 1, 2)

        # Undo mapping
        if x1 == 0:
            qc.x(1)
        if x0 == 0:
            qc.x(0)

    return qc

def deutsch_jozsa_circuit(oracle):
    qc = QuantumCircuit(3, 2)

    # ancilla |1>
    qc.x(2)

    # superposition on input + |-> on ancilla
    qc.h(0)
    qc.h(1)
    qc.h(2)

    # oracle query
    qc.compose(oracle, inplace=True)

    # interference
    qc.h(0)
    qc.h(1)

    # measure inputs only (q0->c0, q1->c1)
    qc.measure(0, 0)
    qc.measure(1, 1)

    return qc

def classify_from_counts(counts):
    """
    Ideal DJ decision rule:
      - If input measures 00 => CONSTANT
      - Else => BALANCED

    With Aer ideal simulation, it should be deterministic.
    """
    return "CONSTANT" if counts.get("00", 0) == shots else "BALANCED"

sim = AerSimulator()

print("\n=== Experiment 05 — Random Oracles Classifier (DJ n=2) ===")
print(f"trials={trials}, shots={shots}, seed={seed}")

correct = 0

for i in range(1, trials + 1):
    kind = random.choice(["CONSTANT", "BALANCED"])
    table = random_constant_table() if kind == "CONSTANT" else random_balanced_table()

    # Sanity check
    assert is_constant(table) if kind == "CONSTANT" else is_balanced(table)

    oracle = oracle_from_truth_table(table)
    qc = deutsch_jozsa_circuit(oracle)

    counts = sim.run(qc, shots=shots).result().get_counts()
    pred = classify_from_counts(counts)

    ok = (pred == kind)
    correct += 1 if ok else 0

    # Human-readable truth table string
    tt = " ".join(f"{x0}{x1}->{fx}" for (x0, x1), fx in zip(X, table))

    print(f"\nTrial {i:02d}")
    print("Truth table:", tt)
    print("True label:", kind)
    print("Counts:", counts)
    print("Predicted:", pred, "|", "OK" if ok else "WRONG")

accuracy = correct / trials
print("\n=== Summary ===")
print("Correct:", correct, "/", trials)
print("Accuracy:", round(accuracy, 6))
print("\nExpected: accuracy = 1.0 in ideal simulation.")
