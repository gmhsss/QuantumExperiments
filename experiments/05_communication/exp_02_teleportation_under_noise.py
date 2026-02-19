"""
Experiment 02 — Teleportation under noise

We measure how teleportation fidelity degrades under:
- phase damping (coherence loss)
- depolarizing noise (randomization)

We sweep p and compute fidelity of target qubit (q2) vs the original |psi>.
"""

import numpy as np
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, phase_damping_error, depolarizing_error
from qiskit.quantum_info import Statevector, DensityMatrix, partial_trace, state_fidelity

theta = 0.83
phi = 1.17

noise_levels = [0.0, 0.05, 0.10, 0.20, 0.30, 0.50]

# optional timestep to model "time passing" after entangling
USE_TIMESTEP = True
TIMESTEPS = 3

def prepare_psi(qc: QuantumCircuit, q: int):
    qc.ry(theta, q)
    qc.rz(phi, q)

def teleportation_circuit():
    qc = QuantumCircuit(3)

    # |psi> on q0
    prepare_psi(qc, 0)

    # Bell pair between q1-q2
    qc.h(1)
    qc.cx(1, 2)

    if USE_TIMESTEP:
        for _ in range(TIMESTEPS):
            qc.id(1)
            qc.id(2)

    # Bell measurement part (coherent)
    qc.cx(0, 1)
    qc.h(0)

    if USE_TIMESTEP:
        for _ in range(TIMESTEPS):
            qc.id(0)
            qc.id(1)

    # Coherent corrections
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
        # no 1q error on "cx" allowed; timesteps handle decoherence after CX

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
    sim = AerSimulator(noise_model=build_noise_model(kind, p), method="density_matrix")

    qc.save_density_matrix()

    res = sim.run(qc).result()
    rho = res.data(0)["density_matrix"]  # full 3-qubit density matrix

    # keep only target qubit 2
    red = partial_trace(DensityMatrix(rho), [0, 1])

    red_ref = partial_trace(reference_state(), [0, 1])

    return float(np.real(state_fidelity(red, red_ref)))

print("\n=== Experiment 02 — Teleportation under noise ===")
print("theta =", theta, "phi =", phi)
print(f"USE_TIMESTEP={USE_TIMESTEP}, TIMESTEPS={TIMESTEPS}")
print("noise_levels =", noise_levels)

for p in noise_levels:
    f_phase = fidelity_for("phase", p)
    f_dep = fidelity_for("depolarizing", p)

    print(f"\n--- p={p} ---")
    print("phase damping fidelity: ", round(f_phase, 4))
    print("depolarizing fidelity: ", round(f_dep, 4))

print("\nExpected:")
print("- p=0 => fidelity ~ 1.0")
print("- phase damping should degrade more noticeably when coherence matters")
print("- depolarizing should degrade broadly and often faster")
