from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector
from qiskit_aer import AerSimulator

shots = 2048

def clean_probs(d: dict) -> dict:
    return {str(k): round(float(v), 6) for k, v in d.items()}

# Prepare |Phi+> = (|00> + |11>) / sqrt(2)
qc = QuantumCircuit(2, 2)
qc.h(0)
qc.cx(0, 1)
qc.measure(0, 0)
qc.measure(1, 1)

print("\n=== Quantum Circuit (Bell |Phi+>) ===")
print(qc.draw())

# Ideal statevector (no measurement)
qc_sv = QuantumCircuit(2)
qc_sv.h(0)
qc_sv.cx(0, 1)

state = Statevector.from_instruction(qc_sv)
print("\n=== Statevector (ideal) ===")
print(state)

probs = clean_probs(state.probabilities_dict())
print("\n=== Theoretical probabilities ===")
print(probs)

sim = AerSimulator()
counts = sim.run(qc, shots=shots).result().get_counts()
freqs = {k: round(v / shots, 6) for k, v in counts.items()}

print("\n=== Measurement counts ===")
print(counts)

print("\n=== Normalized frequencies ===")
print(freqs)

print("\nExpected: only '00' and '11' outcomes, ~50/50 each.")
