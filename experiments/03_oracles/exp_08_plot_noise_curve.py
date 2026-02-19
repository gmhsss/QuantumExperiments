"""
Experiment 08 — Plot accuracy vs gate noise (Deutsch–Jozsa n=2)

Generates a robustness curve:
p_gate -> accuracy
and saves a PNG plot in experiments/03_oracles/results/.

Notes:
- Uses majority-vote classification on the most frequent outcome.
- Includes depolarizing gate noise and optional readout noise.
"""

import random
import matplotlib.pyplot as plt

from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, depolarizing_error, ReadoutError

# ---- Config ----
seed = 2026
random.seed(seed)

shots = 128
trials = 80
p_readout = 0.05

p_gate_list = [0.00, 0.05, 0.10, 0.12, 0.14, 0.16, 0.18, 0.20, 0.22, 0.24, 0.26, 0.28, 0.30]

out_path = "experiments/03_oracles/results/exp_08_accuracy_vs_pgate.png"

# ---- Helpers ----
X = [(0, 0), (0, 1), (1, 0), (1, 1)]

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

        if pred == kind:
            correct += 1

    return correct / trials

# ---- Run sweep ----
print("\n=== Experiment 08 — Accuracy vs p_gate (DJ n=2) ===")
print(f"seed={seed}, shots={shots}, trials={trials}, p_readout={p_readout}")
print("p_gate_list =", p_gate_list)

accuracies = []
for p in p_gate_list:
    acc = evaluate_accuracy(p)
    accuracies.append(acc)
    print(f"p_gate={p:0.2f} -> accuracy={acc:0.3f}")

# ---- Plot ----
plt.figure()
plt.plot(p_gate_list, accuracies, marker="o")
plt.title("Deutsch–Jozsa (n=2): Accuracy vs Gate Noise")
plt.xlabel("Depolarizing gate noise (p_gate)")
plt.ylabel("Accuracy")
plt.ylim(0.0, 1.05)
plt.grid(True)

plt.tight_layout()
plt.savefig(out_path, dpi=200)

print("\nSaved plot to:", out_path)
