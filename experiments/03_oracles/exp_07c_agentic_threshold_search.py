"""
Experiment 07C — Agentic threshold search (DJ n=2)

Agent behavior:
- Goal: find the largest p_gate such that accuracy >= target_accuracy.
- Strategy: iterative search (coarse-to-fine).

This is a minimal example of agentic experimentation:
hypothesis -> experiment -> evaluation -> update -> stop.
"""

import random
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, depolarizing_error, ReadoutError

seed = 99
random.seed(seed)

shots = 128
trials = 60
target_accuracy = 0.95

p_readout = 0.05  # fixed readout noise for the search

X = [(0,0), (0,1), (1,0), (1,1)]

def random_constant_table():
    v = random.choice([0, 1])
    return [v, v, v, v]

def random_balanced_table():
    ones_idx = set(random.sample(range(4), 2))
    return [1 if i in ones_idx else 0 for i in range(4)]

def oracle_from_truth_table(table):
    qc = QuantumCircuit(3)
    for (x0, x1), fx in zip(X, table):
        if fx == 0:
            continue

        if x0 == 0:
            qc.x(0)
        if x1 == 0:
            qc.x(1)

        qc.ccx(0, 1, 2)

        if x1 == 0:
            qc.x(1)
        if x0 == 0:
            qc.x(0)
    return qc

def deutsch_jozsa(oracle):
    qc = QuantumCircuit(3, 2)
    qc.x(2)
    qc.h(0); qc.h(1); qc.h(2)
    qc.compose(oracle, inplace=True)
    qc.h(0); qc.h(1)
    qc.measure(0, 0)
    qc.measure(1, 1)
    return qc

def classify_majority(counts):
    most_common = max(counts.items(), key=lambda kv: kv[1])[0]
    return "CONSTANT" if most_common == "00" else "BALANCED"

def build_noise_model(p_gate: float, p_readout: float) -> NoiseModel:
    nm = NoiseModel()

    if p_gate > 0:
        err_1 = depolarizing_error(p_gate, 1)
        err_2 = depolarizing_error(p_gate, 2)
        for g in ["x", "h", "z"]:
            nm.add_all_qubit_quantum_error(err_1, g)
        nm.add_all_qubit_quantum_error(err_2, "cx")

    if p_readout > 0:
        ro = ReadoutError([[1 - p_readout, p_readout],
                           [p_readout, 1 - p_readout]])
        nm.add_all_qubit_readout_error(ro)

    return nm

def evaluate_accuracy(p_gate: float) -> float:
    sim = AerSimulator(noise_model=build_noise_model(p_gate, p_readout))
    correct = 0

    for _ in range(trials):
        kind = random.choice(["CONSTANT", "BALANCED"])
        table = random_constant_table() if kind == "CONSTANT" else random_balanced_table()
        qc = deutsch_jozsa(oracle_from_truth_table(table))
        counts = sim.run(qc, shots=shots).result().get_counts()
        pred = classify_majority(counts)
        correct += 1 if pred == kind else 0

    return correct / trials

print("\n=== Experiment 07C — Agentic Threshold Search (DJ n=2) ===")
print(f"seed={seed}, shots={shots}, trials={trials}, target_accuracy={target_accuracy}, p_readout={p_readout}")

# Coarse-to-fine search over p_gate
grid = [0.00, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40]
results = []

for p in grid:
    acc = evaluate_accuracy(p)
    results.append((p, acc))
    print(f"coarse p_gate={p:0.2f} -> accuracy={acc:0.3f}")

# Find best p that still meets the target
candidates = [p for p, acc in results if acc >= target_accuracy]
if not candidates:
    print("\nNo p_gate in coarse grid met the target. Try lowering target or noise.")
    raise SystemExit(0)

best = max(candidates)
print(f"\nCoarse best p_gate meeting target: {best:0.2f}")

# Refine around best
low = max(0.0, best - 0.05)
high = min(0.50, best + 0.05)

print(f"\nRefining in [{low:0.3f}, {high:0.3f}] ...")

# Simple refinement: step search with smaller step
step = 0.01
p = low
best_refined = low
best_acc = 0.0

while p <= high + 1e-9:
    acc = evaluate_accuracy(round(p, 3))
    print(f"refine p_gate={p:0.3f} -> accuracy={acc:0.3f}")
    if acc >= target_accuracy and p >= best_refined:
        best_refined = p
        best_acc = acc
    p += step

print("\n=== Threshold estimate ===")
print("Estimated max p_gate with accuracy >= target:", round(best_refined, 3))
print("Accuracy at estimate:", round(best_acc, 3))
