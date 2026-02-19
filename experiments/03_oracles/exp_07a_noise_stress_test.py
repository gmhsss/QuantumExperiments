"""
Experiment 07A — Noise stress test (Deutsch–Jozsa n=2)

Goal: push noise / low-shots regimes until classification accuracy drops.

We sweep:
- p_gate (depolarizing)
- p_readout (bit-flip readout error)
- shots (small sample sizes)
"""

import random
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, depolarizing_error, ReadoutError

seed = 123
random.seed(seed)

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

def deutsch_jozsa_circuit(oracle):
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
    noise_model = NoiseModel()

    if p_gate > 0:
        err_1 = depolarizing_error(p_gate, 1)
        err_2 = depolarizing_error(p_gate, 2)
        for g in ["x", "h", "z"]:
            noise_model.add_all_qubit_quantum_error(err_1, g)
        noise_model.add_all_qubit_quantum_error(err_2, "cx")

    if p_readout > 0:
        ro = ReadoutError([[1 - p_readout, p_readout],
                           [p_readout, 1 - p_readout]])
        noise_model.add_all_qubit_readout_error(ro)

    return noise_model

def run_grid(trials, shots_list, p_gate_list, p_readout_list):
    print("\n=== Experiment 07A — Stress Test (DJ n=2) ===")
    print(f"seed={seed}, trials={trials}")

    for shots in shots_list:
        print(f"\n--- shots={shots} ---")
        for p_readout in p_readout_list:
            print(f"  readout p={p_readout}")
            for p_gate in p_gate_list:
                sim = AerSimulator(noise_model=build_noise_model(p_gate, p_readout))

                correct = 0
                for _ in range(trials):
                    kind = random.choice(["CONSTANT", "BALANCED"])
                    table = random_constant_table() if kind == "CONSTANT" else random_balanced_table()
                    oracle = oracle_from_truth_table(table)
                    qc = deutsch_jozsa_circuit(oracle)
                    counts = sim.run(qc, shots=shots).result().get_counts()
                    pred = classify_majority(counts)
                    correct += 1 if pred == kind else 0

                acc = correct / trials
                print(f"    p_gate={p_gate:0.2f} -> accuracy={acc:0.3f}")

# Stress knobs (these should force degradation)
trials = 40
shots_list = [64, 128, 256]
p_gate_list = [0.00, 0.05, 0.10, 0.20, 0.30]
p_readout_list = [0.00, 0.05, 0.10]

run_grid(trials, shots_list, p_gate_list, p_readout_list)
