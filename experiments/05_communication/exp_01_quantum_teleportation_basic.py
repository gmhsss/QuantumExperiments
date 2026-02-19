"""
Experiment 01 — Quantum Teleportation (ideal)

We teleport an arbitrary single-qubit state |psi> from qubit 0 to qubit 2
using a Bell pair between qubits 1 and 2.

We verify teleportation by comparing statevectors (fidelity) after applying
the classical corrections coherently (using conditional quantum gates).
"""

import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector, state_fidelity

# We will prepare |psi> = cos(theta/2)|0> + e^{i phi} sin(theta/2)|1>
theta = 0.83
phi = 1.17

def prepare_psi(qc: QuantumCircuit, q: int):
    qc.ry(theta, q)
    qc.rz(phi, q)

def bell_pair(qc: QuantumCircuit, a: int, b: int):
    qc.h(a)
    qc.cx(a, b)

def teleportation_circuit():
    qc = QuantumCircuit(3)

    # 1) Prepare |psi> on qubit 0
    prepare_psi(qc, 0)

    # 2) Prepare Bell pair between qubit 1 and qubit 2
    bell_pair(qc, 1, 2)

    # 3) Bell measurement between qubit 0 and qubit 1 (but keep coherent)
    qc.cx(0, 1)
    qc.h(0)

    # Instead of measuring and doing classical corrections,
    # we apply the same logic coherently:
    # If q1 == 1 -> apply X on q2
    # If q0 == 1 -> apply Z on q2
    qc.cx(1, 2)
    qc.cz(0, 2)

    return qc

# Build circuit
qc = teleportation_circuit()

# Compute statevector
sv = Statevector.from_instruction(qc)

# Extract reduced state of qubit 2 by tracing out qubits 0 and 1
# We'll do it by projecting onto basis of (q0,q1) and summing amplitudes.
# Simpler: build an ideal reference circuit that prepares |psi> directly on qubit 2.
qc_ref = QuantumCircuit(3)
prepare_psi(qc_ref, 2)
sv_ref = Statevector.from_instruction(qc_ref)

# Compute fidelity of full 3-qubit state against "junk on 0,1 + |psi> on 2" is annoying.
# So we compare reduced density matrices on qubit 2 by sampling amplitudes:
# We'll use qiskit.quantum_info partial_trace via DensityMatrix.
from qiskit.quantum_info import DensityMatrix, partial_trace

rho = DensityMatrix(sv)
rho_ref = DensityMatrix(sv_ref)

red = partial_trace(rho, [0, 1])       # keep qubit 2
red_ref = partial_trace(rho_ref, [0, 1])

F = state_fidelity(red, red_ref)

print("\n=== Experiment 01 — Quantum Teleportation (ideal) ===")
print("theta =", theta, "phi =", phi)
print("\nCircuit:")
print(qc.draw())
print("\nFidelity on target qubit (q2):", float(np.real(F)))
print("\nExpected: fidelity ~ 1.0 in ideal simulation.")
