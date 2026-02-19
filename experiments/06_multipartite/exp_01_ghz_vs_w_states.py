"""
Experiment 01 — GHZ vs W states (n=3, ideal)

We prepare:
- GHZ_3 = (|000> + |111>) / sqrt(2)
- W_3   = (|001> + |010> + |100>) / sqrt(3)

We inspect measurement statistics to verify correct preparation.
"""

from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

shots = 4096

def ghz_3():
    qc = QuantumCircuit(3, 3)
    qc.h(0)
    qc.cx(0, 1)
    qc.cx(1, 2)
    qc.measure([0,1,2], [0,1,2])
    return qc

def w_3():
    # Simple circuit to generate W_3
    qc = QuantumCircuit(3, 3)

    qc.ry(2 * 0.61548, 0)   # tuned angle for equal amplitudes
    qc.cx(0, 1)
    qc.ry(2 * 0.95532, 1)
    qc.cx(1, 2)
    qc.cx(0, 1)

    qc.measure([0,1,2], [0,1,2])
    return qc

print("\n=== Experiment 01 — GHZ vs W (ideal) ===")

qc_ghz = ghz_3()
qc_w = w_3()

sv_ghz = Statevector.from_instruction(qc_ghz.remove_final_measurements(inplace=False))
sv_w = Statevector.from_instruction(qc_w.remove_final_measurements(inplace=False))

print("\nGHZ_3 statevector:")
print(sv_ghz)

print("\nW_3 statevector:")
print(sv_w)

print("\nExpected:")
print("- GHZ: amplitudes only on |000> and |111>")
print("- W: amplitudes on |001>, |010>, |100>")
