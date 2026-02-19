from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector
from qiskit_aer import AerSimulator

shots = 1024

def clean_probs(d: dict) -> dict:
    return {str(k): round(float(v), 6) for k, v in d.items()}

def run_case(title: str, qc_sv: QuantumCircuit, qc_meas: QuantumCircuit):
    print(f"\n=== {title} ===")
    print(qc_meas.draw())

    state = Statevector.from_instruction(qc_sv)
    print("Statevector:", state)
    print("Theoretical probabilities:", clean_probs(state.probabilities_dict()))

    sim = AerSimulator()
    counts = sim.run(qc_meas, shots=shots).result().get_counts()
    freqs = {k: round(v / shots, 6) for k, v in counts.items()}
    print("Counts:", counts)
    print("Frequencies:", freqs)

# Case A: |0> → H
qc_sv_a = QuantumCircuit(1)
qc_sv_a.h(0)

qc_a = QuantumCircuit(1, 1)
qc_a.h(0)
qc_a.measure(0, 0)

# Case B: |0> → H → Z
qc_sv_b = QuantumCircuit(1)
qc_sv_b.h(0)
qc_sv_b.z(0)

qc_b = QuantumCircuit(1, 1)
qc_b.h(0)
qc_b.z(0)
qc_b.measure(0, 0)

run_case("Case A: H", qc_sv_a, qc_a)
run_case("Case B: H → Z (phase flip)", qc_sv_b, qc_b)

print("\nExpected observation:")
print("Phase changes do not affect measurement probabilities in the Z basis.")
