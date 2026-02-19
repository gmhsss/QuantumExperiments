"""
Experiment 01 — Phase damping vs depolarizing noise (single qubit)

We prepare |+> and study how:
- phase damping
- depolarizing noise

affect measurement statistics and coherence.
"""

import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector, DensityMatrix
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, phase_damping_error, depolarizing_error

shots = 4096
noise_levels = [0.0, 0.1, 0.3, 0.5]

def build_circuit():
    qc = QuantumCircuit(1, 1)
    qc.h(0)          # |+>
    qc.measure(0, 0)
    return qc

def simulate(noise_model=None):
    sim = AerSimulator(noise_model=noise_model)
    qc = build_circuit()
    return sim.run(qc, shots=shots).result().get_counts()

print("\n=== Phase damping vs Depolarizing (|+>) ===")

for p in noise_levels:
    print(f"\n--- Noise strength p={p} ---")

    # Phase damping
    nm_phase = NoiseModel()
    if p > 0:
        nm_phase.add_all_qubit_quantum_error(
            phase_damping_error(p), "h"
        )

    counts_phase = simulate(nm_phase)
    freq_phase = {k: v / shots for k, v in counts_phase.items()}

    print("Phase damping counts:", counts_phase)
    print("Phase damping freq:  ", freq_phase)

    # Depolarizing
    nm_dep = NoiseModel()
    if p > 0:
        nm_dep.add_all_qubit_quantum_error(
            depolarizing_error(p, 1), "h"
        )

    counts_dep = simulate(nm_dep)
    freq_dep = {k: v / shots for k, v in counts_dep.items()}

    print("Depolarizing counts:", counts_dep)
    print("Depolarizing freq:  ", freq_dep)

print("\nExpected behavior:")
print("- Phase damping preserves ~50/50 in Z, but destroys phase.")
print("- Depolarizing pushes toward uniform noise.")
