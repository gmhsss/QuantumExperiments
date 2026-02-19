"""
Experiment 03 — Quantum Teleportation with measurement + conditional corrections (Qiskit if_test)

Teleport |psi> from qubit 0 to qubit 2 using:
- Bell pair between qubits 1 and 2
- Bell measurement on qubits 0 and 1
- Classical feed-forward corrections on qubit 2

We verify by computing fidelity on target qubit (q2) against a reference |psi>.
"""

import numpy as np
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit.quantum_info import Statevector, DensityMatrix, partial_trace, state_fidelity

theta = 0.83
phi = 1.17

def prepare_psi(qc: QuantumCircuit, q: int):
    qc.ry(theta, q)
    qc.rz(phi, q)

def reference_density():
    qc = QuantumCircuit(3)
    prepare_psi(qc, 2)
    return DensityMatrix(Statevector.from_instruction(qc))

def teleportation_meas_if():
    # 3 qubits, 2 classical bits
    qc = QuantumCircuit(3, 2)

    # |psi> on q0
    prepare_psi(qc, 0)

    # Bell pair q1-q2
    qc.h(1)
    qc.cx(1, 2)

    # Bell measurement on q0,q1
    qc.cx(0, 1)
    qc.h(0)

    # Store outcomes:
    # c[0] = m0 (from q0), c[1] = m1 (from q1)
    qc.measure(0, 0)
    qc.measure(1, 1)

    # Feed-forward corrections on q2:
    # if m1 == 1 -> apply X on q2
    with qc.if_test((qc.clbits[1], 1)):
        qc.x(2)

    # if m0 == 1 -> apply Z on q2
    with qc.if_test((qc.clbits[0], 1)):
        qc.z(2)

    return qc

qc = teleportation_meas_if()

# Density matrix method handles measurement branches properly
sim = AerSimulator(method="density_matrix")

qc.save_density_matrix()
res = sim.run(qc, shots=1).result()
rho = res.data(0)["density_matrix"]

# Keep only qubit 2
red = partial_trace(DensityMatrix(rho), [0, 1])
red_ref = partial_trace(reference_density(), [0, 1])

F = float(np.real(state_fidelity(red, red_ref)))

print("\n=== Experiment 03 — Teleportation with measurement + if_test ===")
print("theta =", theta, "phi =", phi)
print("\nCircuit:")
print(qc.draw())
print("\nFidelity on target qubit (q2):", F)
print("\nExpected: fidelity ~ 1.0 in ideal simulation.")
