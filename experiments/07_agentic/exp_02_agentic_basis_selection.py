"""
Experiment 02 — Agentic basis selection (Z vs X)

We prepare Bell |Phi+> and evaluate correlation metric in:
- Z basis: measure directly
- X basis: apply H to both qubits then measure

Noise:
- phase damping: should preserve Corr(Z) better than Corr(X)
- depolarizing: degrades both

Agent chooses the basis that yields higher correlation.
"""

from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, phase_damping_error, depolarizing_error

shots = 2048
noise_levels = [0.0, 0.05, 0.10, 0.20, 0.30]
noise_kinds = ["phase", "depolarizing"]

def bell_state_phi_plus():
    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)
    return qc

def measure_in_z():
    qc = QuantumCircuit(2, 2)
    qc.compose(bell_state_phi_plus(), inplace=True)
    qc.measure([0, 1], [0, 1])
    return qc

def measure_in_x():
    qc = QuantumCircuit(2, 2)
    qc.compose(bell_state_phi_plus(), inplace=True)
    qc.h(0)
    qc.h(1)
    qc.measure([0, 1], [0, 1])
    return qc

def corr_metric(counts, shots):
    return (counts.get("00", 0) + counts.get("11", 0)) / shots

def build_noise_model(kind: str, p: float) -> NoiseModel:
    nm = NoiseModel()
    if p <= 0:
        return nm

    if kind == "phase":
        e1 = phase_damping_error(p)
        nm.add_all_qubit_quantum_error(e1, ["h"])
        # no 1q error on cx; phase damping won't flip bits in Z anyway
        # keep cx ideal to isolate "basis sensitivity" effect

    elif kind == "depolarizing":
        e1 = depolarizing_error(p, 1)
        e2 = depolarizing_error(p, 2)
        nm.add_all_qubit_quantum_error(e1, ["h"])
        nm.add_all_qubit_quantum_error(e2, ["cx"])

    else:
        raise ValueError("Unknown noise kind")

    return nm

print("\n=== Experiment 02 — Agentic basis selection (Z vs X) ===")
print("shots =", shots)

for kind in noise_kinds:
    print(f"\n### Noise kind: {kind} ###")
    for p in noise_levels:
        sim = AerSimulator(noise_model=build_noise_model(kind, p))

        cz = sim.run(measure_in_z(), shots=shots).result().get_counts()
        cx = sim.run(measure_in_x(), shots=shots).result().get_counts()

        corr_z = corr_metric(cz, shots)
        corr_x = corr_metric(cx, shots)

        chosen = "Z" if corr_z >= corr_x else "X"

        print(f"\n--- p={p} ---")
        print(f"Corr(Z)={corr_z:.4f} | Corr(X)={corr_x:.4f} -> Agent chooses: {chosen}")
