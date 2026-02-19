import numpy as np
from qiskit.quantum_info import Statevector, DensityMatrix

def fidelity_pure(psi: Statevector, phi: Statevector) -> float:
    overlap = np.vdot(psi.data, phi.data)
    return float(abs(overlap) ** 2)

def fidelity_pure_vs_mixed(psi: Statevector, rho: DensityMatrix) -> float:
    vec = psi.data.reshape(-1, 1)
    value = np.conjugate(vec).T @ rho.data @ vec
    return float(np.real(value[0, 0]))

print("\n=== Experiment 04 — Fidelity (Basics) ===")

# Case 1: |0> vs |+>
psi0 = Statevector.from_label("0")
plus = Statevector([1 / np.sqrt(2), 1 / np.sqrt(2)])

print("\nCase 1: F(|0>, |+>)")
print("Expected: 0.5")
print("Obtained:", round(fidelity_pure(psi0, plus), 6))

# Case 2: |0> vs mixed state
rho = 0.9 * DensityMatrix.from_label("0") + 0.1 * DensityMatrix.from_label("1")

print("\nCase 2: F(|0>, 0.9|0><0| + 0.1|1><1|)")
print("Expected: 0.9")
print("Obtained:", round(fidelity_pure_vs_mixed(psi0, rho), 6))

print("\nInterpretation:")
print("Fidelity quantifies how close a real quantum state is to a target state.")
