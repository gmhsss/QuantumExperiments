from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

shots = 2048

def bell_prep(label: str) -> QuantumCircuit:
    """
    Prepares one of the 4 Bell states on 2 qubits:
      - PHI_PLUS, PHI_MINUS, PSI_PLUS, PSI_MINUS
    Convention:
      |PHI+>  = (|00> + |11>)/sqrt(2)
      |PHI->  = (|00> - |11>)/sqrt(2)
      |PSI+>  = (|01> + |10>)/sqrt(2)
      |PSI->  = (|01> - |10>)/sqrt(2)
    """
    qc = QuantumCircuit(2, 2)

    # PSI states can be obtained by flipping q1 before entangling
    if label.startswith("PSI"):
        qc.x(1)

    # Entangle
    qc.h(0)
    qc.cx(0, 1)

    # Add relative phase (minus sign) using Z on qubit 0
    if label.endswith("MINUS"):
        qc.z(0)

    return qc

def bell_measurement(qc: QuantumCircuit) -> None:
    """
    Bell-basis measurement implemented by undoing the entangling block:
      CX(0->1), H(0), then measure.
    """
    qc.cx(0, 1)
    qc.h(0)
    qc.measure(0, 0)  # q0 -> c0
    qc.measure(1, 1)  # q1 -> c1

def flip_bitstring_c1c0_to_c0c1(bitstr: str) -> str:
    # Qiskit returns classical strings as c_{n-1}...c_0 (here: c1c0).
    # We want to display as (c0c1) for human reading aligned with q0->c0, q1->c1.
    if len(bitstr) != 2:
        return bitstr
    return bitstr[::-1]

def expected_c0c1(label: str) -> str:
    """
    Expected deterministic outcome after Bell measurement, expressed as c0c1.
    Standard mapping for this circuit:
      PHI_PLUS  -> 00
      PHI_MINUS -> 10
      PSI_PLUS  -> 01
      PSI_MINUS -> 11
    """
    mapping = {
        "PHI_PLUS": "00",
        "PHI_MINUS": "10",
        "PSI_PLUS": "01",
        "PSI_MINUS": "11",
    }
    return mapping[label]

def run(label: str):
    qc = bell_prep(label)
    bell_measurement(qc)

    sim = AerSimulator()
    counts_raw = sim.run(qc, shots=shots).result().get_counts()

    # Convert keys for human-readable view
    counts_c0c1 = {}
    for k, v in counts_raw.items():
        kk = flip_bitstring_c1c0_to_c0c1(k)
        counts_c0c1[kk] = counts_c0c1.get(kk, 0) + v

    exp = expected_c0c1(label)

    print(f"\n=== Bell state: {label} ===")
    print(qc.draw())
    print("Counts (raw, Qiskit c1c0):", counts_raw)
    print("Counts (c0c1):", counts_c0c1)
    print("Expected dominant outcome (c0c1):", exp)

run("PHI_PLUS")
run("PHI_MINUS")
run("PSI_PLUS")
run("PSI_MINUS")

print("\nNote:")
print("- Qiskit prints bitstrings as c1c0 (highest classical bit first).")
print("- The (c0c1) view matches the measurement wiring: q0->c0 and q1->c1.")
