"""
Experiment 03 — Entanglement under noise (Bell correlations)

We prepare the Bell state |Phi+> = (|00> + |11>)/sqrt(2)
and measure correlations in the Z basis.

Correlation metric:
  P(bit0 == bit1) = P(00) + P(11)

We compare:
- phase damping noise
- depolarizing noise

Goal: see how entanglement signatures decay under noise.
"""

from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, phase_damping_error, depolarizing_error

shots = 4096
noise_levels = [0.0, 0.05, 0.10, 0.20, 0.30, 0.50]

def bell_phi_plus_circuit():
    qc = QuantumCircuit(2, 2)
    qc.h(0)
    qc.cx(0, 1)
    qc.measure(0, 0)
    qc.measure(1, 1)
    return qc

def build_noise_model(kind: str, p: float) -> NoiseModel:
    nm = NoiseModel()
    if p <= 0:
        return nm

    if kind == "phase":
        e1 = phase_damping_error(p)
        for g in ["h"]:
            nm.add_all_qubit_quantum_error(e1, g)
    elif kind == "depolarizing":
        e1 = depolarizing_error(p, 1)
        e2 = depolarizing_error(p, 2)
        nm.add_all_qubit_quantum_error(e1, "h")
        nm.add_all_qubit_quantum_error(e2, "cx")

    else:
        raise ValueError("Unknown noise kind")

    return nm

def run(qc, nm):
    sim = AerSimulator(noise_model=nm)
    return sim.run(qc, shots=shots).result().get_counts()

def corr_rate(counts):
    p00 = counts.get("00", 0) / shots
    p11 = counts.get("11", 0) / shots
    return p00 + p11

qc = bell_phi_plus_circuit()

print("\n=== Experiment 03 — Bell correlations under noise (|Phi+>) ===")
print(f"shots={shots}")
print("\nCorrelation metric: P(bit0 == bit1) = P(00) + P(11)")

for p in noise_levels:
    print(f"\n--- p={p} ---")

    nm_phase = build_noise_model("phase", p)
    c_phase = run(qc, nm_phase)
    corr_phase = corr_rate(c_phase)

    print("Phase damping counts:", c_phase)
    print("Phase damping correlation:", round(corr_phase, 4))

    nm_dep = build_noise_model("depolarizing", p)
    c_dep = run(qc, nm_dep)
    corr_dep = corr_rate(c_dep)

    print("Depolarizing counts:", c_dep)
    print("Depolarizing correlation:", round(corr_dep, 4))

print("\nExpected:")
print("- At p=0, correlation ~1.0 (only 00 and 11).")
print("- With noise, correlation drops toward ~0.5 (random bits).")
print("- Depolarizing should destroy correlations faster than phase damping.")
