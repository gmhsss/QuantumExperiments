"""
Experiment 05 — Plot Bell correlations in Z vs X under noise

We reproduce Experiment 04 but save curves as a PNG plot.

Outputs:
- experiments/04_noise/results/exp_05_bell_corr_Z_vs_X.png
"""

import random
import matplotlib.pyplot as plt

from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, phase_damping_error, depolarizing_error

shots = 4096
noise_levels = [0.0, 0.05, 0.10, 0.20, 0.30, 0.50]

USE_TIMESTEP = True
TIMESTEPS_AFTER_CX = 3

out_path = "experiments/04_noise/results/exp_05_bell_corr_Z_vs_X.png"

def bell_phi_plus(measure_basis: str):
    qc = QuantumCircuit(2, 2)
    qc.h(0)
    qc.cx(0, 1)

    if USE_TIMESTEP:
        for _ in range(TIMESTEPS_AFTER_CX):
            qc.id(0)
            qc.id(1)

    if measure_basis.upper() == "X":
        qc.h(0)
        qc.h(1)

    qc.measure(0, 0)
    qc.measure(1, 1)
    return qc

def build_noise_model(kind: str, p: float) -> NoiseModel:
    nm = NoiseModel()
    if p <= 0:
        return nm

    if kind == "phase":
        e1 = phase_damping_error(p)
        for g in ["h", "id"]:
            nm.add_all_qubit_quantum_error(e1, g)

    elif kind == "depolarizing":
        e1 = depolarizing_error(p, 1)
        e2 = depolarizing_error(p, 2)
        nm.add_all_qubit_quantum_error(e1, "h")
        nm.add_all_qubit_quantum_error(e1, "id")
        nm.add_all_qubit_quantum_error(e2, "cx")

    else:
        raise ValueError("Unknown noise kind")

    return nm

def run_counts(qc, nm):
    sim = AerSimulator(noise_model=nm)
    return sim.run(qc, shots=shots).result().get_counts()

def corr_rate(counts):
    return (counts.get("00", 0) + counts.get("11", 0)) / shots

def corr_for(kind: str):
    corrZ = []
    corrX = []
    for p in noise_levels:
        nm = build_noise_model(kind, p)
        cz = corr_rate(run_counts(bell_phi_plus("Z"), nm))
        cx = corr_rate(run_counts(bell_phi_plus("X"), nm))
        corrZ.append(cz)
        corrX.append(cx)
        print(f"{kind:12s} p={p:0.2f} -> Corr(Z)={cz:0.4f}, Corr(X)={cx:0.4f}")
    return corrZ, corrX

print("\n=== Experiment 05 — Plot Bell correlations (Z vs X) ===")
print(f"shots={shots}, USE_TIMESTEP={USE_TIMESTEP}, TIMESTEPS_AFTER_CX={TIMESTEPS_AFTER_CX}")
print("noise_levels =", noise_levels)

phaseZ, phaseX = corr_for("phase")
depZ, depX = corr_for("depolarizing")

plt.figure()
plt.plot(noise_levels, phaseZ, marker="o", label="phase damping: Corr(Z)")
plt.plot(noise_levels, phaseX, marker="o", label="phase damping: Corr(X)")
plt.plot(noise_levels, depZ, marker="o", label="depolarizing: Corr(Z)")
plt.plot(noise_levels, depX, marker="o", label="depolarizing: Corr(X)")

plt.title("Bell-state correlations under noise (Z vs X basis)")
plt.xlabel("Noise strength p")
plt.ylabel("Correlation P(bit0 == bit1)")
plt.ylim(0.0, 1.05)
plt.grid(True)
plt.legend()

plt.tight_layout()
plt.savefig(out_path, dpi=200)

print("\nSaved plot to:", out_path)
