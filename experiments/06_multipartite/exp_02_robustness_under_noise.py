"""
Experiment 02 — Robustness under noise (GHZ vs W, n=3)

We compare how multipartite entanglement degrades under depolarizing noise.

Metrics:
- GHZ: P(000) + P(111)
- W:   P(001) + P(010) + P(100)
"""

from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, depolarizing_error

shots = 4096
noise_levels = [0.0, 0.05, 0.10, 0.20, 0.30, 0.50]

def ghz_3():
    qc = QuantumCircuit(3, 3)
    qc.h(0)
    qc.cx(0, 1)
    qc.cx(1, 2)
    qc.measure([0,1,2], [0,1,2])
    return qc

def w_3():
    qc = QuantumCircuit(3, 3)
    qc.ry(2 * 0.61548, 0)
    qc.cx(0, 1)
    qc.ry(2 * 0.95532, 1)
    qc.cx(1, 2)
    qc.cx(0, 1)
    qc.measure([0,1,2], [0,1,2])
    return qc

def metric_ghz(counts):
    return (counts.get("000",0) + counts.get("111",0)) / shots

def metric_w(counts):
    return (counts.get("001",0) + counts.get("010",0) + counts.get("100",0)) / shots

print("\n=== Experiment 02 — Robustness under noise (GHZ vs W) ===")
print("shots =", shots)

for p in noise_levels:
    nm = NoiseModel()
    if p > 0:
        nm.add_all_qubit_quantum_error(depolarizing_error(p,1), ["h","ry"])
        nm.add_all_qubit_quantum_error(depolarizing_error(p,2), "cx")

    sim = AerSimulator(noise_model=nm)

    c_ghz = sim.run(ghz_3(), shots=shots).result().get_counts()
    c_w   = sim.run(w_3(), shots=shots).result().get_counts()

    m_ghz = metric_ghz(c_ghz)
    m_w   = metric_w(c_w)

    print(f"\n--- p={p} ---")
    print("GHZ metric:", round(m_ghz,4))
    print("W   metric:", round(m_w,4))

print("\nExpected:")
print("- GHZ metric drops sharply with noise")
print("- W metric degrades more smoothly (more robust entanglement)")
