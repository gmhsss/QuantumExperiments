from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

shots = 4096

def run(label: str, add_phase: bool):
    qc = QuantumCircuit(2, 2)

    # Prepare |Phi+> or |Phi->
    qc.h(0)
    qc.cx(0, 1)

    if add_phase:
        qc.z(0)  # turns Phi+ into Phi-

    qc.measure(0, 0)
    qc.measure(1, 1)

    sim = AerSimulator()
    counts = sim.run(qc, shots=shots).result().get_counts()

    print(f"\n=== State: {label} ===")
    print(qc.draw())
    print("Counts:", counts)

print("Measuring Bell states directly in the Z basis")

run("PHI_PLUS", add_phase=False)
run("PHI_MINUS", add_phase=True)

print("\nExpected:")
print("- Both states give ~50% '00' and ~50% '11'")
print("- The relative phase (- sign) is invisible in the Z basis")
