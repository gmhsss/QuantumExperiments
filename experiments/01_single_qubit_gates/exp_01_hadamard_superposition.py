from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector
from qiskit_aer import AerSimulator

shots = 1024

def clean_probs(d: dict) -> dict:
    return {str(k): round(float(v), 6) for k, v in d.items()}

# Circuit with measurement
qc = QuantumCircuit(1, 1)
qc.h(0)
qc.measure(0, 0)

print("\n=== Quantum Circuit ===")
print(qc.draw())

# Ideal statevector (no measurement)
qc_sv = QuantumCircuit(1)
qc_sv.h(0)
state = Statevector.from_instruction(qc_sv)

print("\n=== Statevector (ideal) ===")
print(state)

probs = clean_probs(state.probabilities_dict())
print("\n=== Theoretical probabilities ===")
print(probs)

# Measurement simulation
sim = AerSimulator()
result = sim.run(qc, shots=shots).result()
counts = result.get_counts()
freqs = {k: round(v / shots, 6) for k, v in counts.items()}

print("\n=== Measurement counts ===")
print(counts)

print("\n=== Normalized frequencies ===")
print(freqs)
