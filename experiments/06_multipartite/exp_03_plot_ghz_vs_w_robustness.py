"""
Experiment 03 — Plot robustness: GHZ_3 vs W_3 under depolarizing noise

Metrics:
- GHZ metric = P(000) + P(111)
- W metric   = P(001) + P(010) + P(100)

We generate a PNG plot:
experiments/06_multipartite/results/exp_03_ghz_vs_w_robustness.png
"""

import math
import matplotlib.pyplot as plt

from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, depolarizing_error

shots = 4096
noise_levels = [0.0, 0.05, 0.10, 0.20, 0.30, 0.50]

out_path = "experiments/06_multipartite/results/exp_03_ghz_vs_w_robustness.png"

def ghz_3():
    qc = QuantumCircuit(3, 3)
    qc.h(0)
    qc.cx(0, 1)
    qc.cx(1, 2)
    qc.measure([0, 1, 2], [0, 1, 2])
    return qc

def w_3_initialize():
    """
    |W3> = (|001> + |010> + |100>) / sqrt(3)
    Qiskit basis order for 3 qubits corresponds to |q2 q1 q0> in the printed bitstring.
    The statevector indices map as:
      |000> index 0
      |001> index 1
      |010> index 2
      |011> index 3
      |100> index 4
      |101> index 5
      |110> index 6
      |111> index 7
    So amplitudes go into indices 1,2,4.
    """
    amp = 1 / math.sqrt(3)
    vec = [0j] * 8
    vec[1] = amp
    vec[2] = amp
    vec[4] = amp

    qc = QuantumCircuit(3, 3)
    qc.initialize(vec, [0, 1, 2])
    qc.measure([0, 1, 2], [0, 1, 2])
    return qc

def metric_ghz(counts):
    return (counts.get("000", 0) + counts.get("111", 0)) / shots

def metric_w(counts):
    return (counts.get("001", 0) + counts.get("010", 0) + counts.get("100", 0)) / shots

def build_noise_model(p):
    nm = NoiseModel()
    if p <= 0:
        return nm
    # Apply 1q depolarizing to all 1q gates and 2q depolarizing to CX
    nm.add_all_qubit_quantum_error(depolarizing_error(p, 1), ["h", "initialize"])
    nm.add_all_qubit_quantum_error(depolarizing_error(p, 2), "cx")
    return nm

print("\n=== Experiment 03 — Plot GHZ vs W robustness (n=3) ===")
print("shots =", shots)
print("noise_levels =", noise_levels)

ghz_vals = []
w_vals = []

for p in noise_levels:
    sim = AerSimulator(noise_model=build_noise_model(p))

    c_ghz = sim.run(ghz_3(), shots=shots).result().get_counts()
    c_w   = sim.run(w_3_initialize(), shots=shots).result().get_counts()

    m_ghz = metric_ghz(c_ghz)
    m_w   = metric_w(c_w)

    ghz_vals.append(m_ghz)
    w_vals.append(m_w)

    print(f"p={p:0.2f} | GHZ_metric={m_ghz:0.4f} | W_metric={m_w:0.4f}")

plt.figure()
plt.plot(noise_levels, ghz_vals, marker="o", label="GHZ_3 metric: P(000)+P(111)")
plt.plot(noise_levels, w_vals, marker="o", label="W_3 metric: P(001)+P(010)+P(100)")

plt.title("Robustness under depolarizing noise (GHZ_3 vs W_3)")
plt.xlabel("Noise strength p")
plt.ylabel("Structure metric (probability mass on ideal subspace)")
plt.ylim(0.0, 1.05)
plt.grid(True)
plt.legend()

plt.tight_layout()
plt.savefig(out_path, dpi=200)

print("\nSaved plot to:", out_path)
