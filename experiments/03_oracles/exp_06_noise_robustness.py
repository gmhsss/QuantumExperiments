"""
Experiment 06 — Noise robustness (Deutsch–Jozsa n=2)

We evaluate how Deutsch–Jozsa classification accuracy degrades under noise.

We use Aer noise models:
- depolarizing errors on 1-qubit and 2-qubit gates
- optional measurement bit-flip (simple readout noise)

This is an empirical NISQ-style robustness curve:
noise_strength -> accuracy
"""

import random
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, depolarizing_error, ReadoutError

shots = 1024
trials_per_level = 30
seed = 7

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
    qc.h(0)
    qc.h(1)
    qc.h(2)
    qc.compose(oracle, inplace=True)
    qc.h(0)
    qc.h(1)
    qc.measure(0, 0)
    qc.measure(1, 1)
    return qc

def classify_from_counts(counts):
    # Ideal rule: CONSTANT iff 00 occurs for all shots
    # Under noise, we use majority vote:
    # if most frequent outcome is "00" => CONSTANT else BALANCED
    most_common = max(counts.items(), key=lambda kv: kv[1])[0]
    return "CONSTANT" if most_common == "00" else "BALANCED"

def build_noise_model(p_gate: float, p_readout: float) -> NoiseModel:
    """
    p_gate: depolarizing strength per gate
    p_readout: probability of flipping a measured classical bit
    """
    noise_model = NoiseModel()

    if p_gate > 0:
        err_1 = depolarizing_error(p_gate, 1)
        err_2 = depolarizing_error(p_gate, 2)

        # Apply to common basis gates used by our circuits
        for g in ["x", "h", "z"]:
            noise_model.add_all_qubit_quantum_error(err_1, g)

        # CX / CCX appear; Aer handles CCX decomposition into basis gates depending on backend,
        # but we still attach 2-qubit error to cx to capture dominant effect.
        noise_model.add_all_qubit_quantum_error(err_2, "cx")

    if p_readout > 0:
        ro = ReadoutError([[1 - p_readout, p_readout],
                           [p_readout, 1 - p_readout]])
        noise_model.add_all_qubit_readout_error(ro)

    return noise_model

noise_levels = [0.0, 0.001, 0.005, 0.01, 0.02, 0.05]
readout_levels = [0.0, 0.01]  # run two sweeps: no readout noise and mild readout noise

print("\n=== Experiment 06 — Noise Robustness (DJ n=2) ===")
print(f"shots={shots}, trials_per_level={trials_per_level}, seed={seed}")

for p_readout in readout_levels:
    print(f"\n--- Readout noise p_readout={p_readout} ---")

    for p_gate in noise_levels:
        noise_model = build_noise_model(p_gate=p_gate, p_readout=p_readout)
        sim = AerSimulator(noise_model=noise_model)

        correct = 0

        for _ in range(trials_per_level):
            kind = random.choice(["CONSTANT", "BALANCED"])
            table = random_constant_table() if kind == "CONSTANT" else random_balanced_table()

            oracle = oracle_from_truth_table(table)
            qc = deutsch_jozsa_circuit(oracle)

            counts = sim.run(qc, shots=shots).result().get_counts()
            pred = classify_from_counts(counts)

            if pred == kind:
                correct += 1

        accuracy = correct / trials_per_level
        print(f"p_gate={p_gate:0.3f} -> accuracy={accuracy:0.3f}")
