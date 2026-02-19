"""
Experiment 04 — Plot teleportation fidelity vs noise

We reproduce Experiment 02 and save a PNG plot:
- phase damping fidelity vs p
- depolarizing fidelity vs p

Output:
experiments/05_communication/results/exp_04_teleport_fidelity_vs_noise.png
"""

import numpy as np
import matplotlib.pyplot as plt

from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, phase_damping_error, depolarizing_error
from qiskit.quantum_info import Statevector, DensityMatrix, partial_trace, state_fidelity

theta = 0.83
phi = 1.17

noise_levels = [0.0, 0.05, 0.10, 0.20, 0.30, 0.50]

USE_TIMESTEP = True
TIMESTEPS = 3

out_path = "experiments/05_communication/results/exp_04_teleport_fidelity_vs_noise.png"

def prepare_psi(qc: QuantumCircuit, q: int):
    qc.ry(theta, q)
    qc.rz(phi, q)

def teleportation_circuit():
    qc = QuantumCircuit(3)

    prepare_psi(qc, 0)

    qc.h(1)
    qc.cx(1, 2)

    if USE_TIMESTEP:
        for _ in range(TIMESTEPS):
            qc.id(1)
            qc.id(2)

    qc.cx(0, 1)
    qc.h(0)

    if USE_TIMESTEP:
        for _ in range(TIMESTEPS):
            qc.id(0)
            qc.id(1)

    qc.cx(1, 2)
    qc.cz(0, 2)

    if USE_TIMESTEP:
        for _ in range(TIMESTEPS):
            qc.id(2)

    return qc

def reference_state():
    qc = QuantumCircuit(3)
    prepare_psi(qc, 2)
    return DensityMatrix(Statevector.from_instruction(qc))

def build_noise_model(kind: str, p: float) -> NoiseModel:
    nm = NoiseModel()
    if p <= 0:
        return nm

    if kind == "phase":
        e1 = phase_damping_error(p)
        for g in ["h", "id", "ry", "rz", "z"]:
            nm.add_all_qubit_quantum_error(e1, g)

    elif kind == "depolarizing":
        e1 = depolarizing_error(p, 1)
        e2 = depolarizing_error(p, 2)
        for g in ["h", "id", "ry", "rz", "z"]:
            nm.add_all_qubit_quantum_error(e1, g)
        nm.add_all_qubit_quantum_error(e2, "cx")

    else:
        raise ValueError("Unknown noise kind")

    return nm

def fidelity_for(kind: str, p: float) -> float:
    qc = teleportation_circuit()
    qc.save_density_matrix()

    sim = AerSimulator(
        noise_model=build_noise_model(kind, p),
        method="density_matrix"
    )

    res = sim.run(qc).result()
    rho = res.data(0)["density_matrix"]

    red = partial_trace(DensityMatrix(rho), [0, 1])
    red_ref = partial_trace(reference_state(), [0, 1])

    return float(np.real(state_fidelity(red, red_ref)))

print("\n=== Experiment 04 — Plot teleportation fidelity vs noise ===")
print("theta =", theta, "phi =", phi)
print(f"USE_TIMESTEP={USE_TIMESTEP}, TIMESTEPS={TIMESTEPS}")
print("noise_levels =", noise_levels)

phase_f = []
dep_f = []

for p in noise_levels:
    fp = fidelity_for("phase", p)
    fd = fidelity_for("depolarizing", p)
    phase_f.append(fp)
    dep_f.append(fd)
    print(f"p={p:0.2f} | phase={fp:0.4f} | depolarizing={fd:0.4f}")

plt.figure()
plt.plot(noise_levels, phase_f, marker="o", label="phase damping fidelity")
plt.plot(noise_levels, dep_f, marker="o", label="depolarizing fidelity")

plt.title("Teleportation fidelity vs noise strength")
plt.xlabel("Noise strength p")
plt.ylabel("Fidelity (target qubit vs |psi>)")
plt.ylim(0.0, 1.05)
plt.grid(True)
plt.legend()

plt.tight_layout()
plt.savefig(out_path, dpi=200)

print("\nSaved plot to:", out_path)
