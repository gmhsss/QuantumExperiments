"""
Experiment 02 — Interference under noise (HZH)

We compare two circuits:
A) H -> H          (should yield |0> deterministically)
B) H -> Z -> H     (should yield |1> deterministically)

Then we add noise and measure how interference degrades.
We compare:
- phase damping (kills coherence)
- depolarizing (randomizes state)

We report "error rate":
- for A: P(measure 1)
- for B: P(measure 0)
"""

from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, phase_damping_error, depolarizing_error

shots = 4096
noise_levels = [0.0, 0.05, 0.10, 0.20, 0.30, 0.50]

def circuit_A():
    qc = QuantumCircuit(1, 1)
    qc.h(0)
    qc.h(0)
    qc.measure(0, 0)
    return qc

def circuit_B():
    qc = QuantumCircuit(1, 1)
    qc.h(0)
    qc.z(0)
    qc.h(0)
    qc.measure(0, 0)
    return qc

def build_noise_model(kind: str, p: float) -> NoiseModel:
    nm = NoiseModel()
    if p <= 0:
        return nm

    if kind == "phase":
        e1 = phase_damping_error(p)
        # attach to gates where coherence matters
        for g in ["h", "z"]:
            nm.add_all_qubit_quantum_error(e1, g)

    elif kind == "depolarizing":
        e1 = depolarizing_error(p, 1)
        for g in ["h", "z"]:
            nm.add_all_qubit_quantum_error(e1, g)

    else:
        raise ValueError("Unknown noise kind")

    return nm

def run(qc, nm):
    sim = AerSimulator(noise_model=nm)
    return sim.run(qc, shots=shots).result().get_counts()

def prob(counts, bit):
    return counts.get(bit, 0) / shots

print("\n=== Experiment 02 — Interference under noise (HZH) ===")
print(f"shots={shots}")

for p in noise_levels:
    print(f"\n--- p={p} ---")

    # Phase damping
    nm_phase = build_noise_model("phase", p)
    ca_p = run(circuit_A(), nm_phase)
    cb_p = run(circuit_B(), nm_phase)

    err_A_phase = prob(ca_p, "1")  # should be 0
    err_B_phase = prob(cb_p, "0")  # should be 0

    print("Phase damping:")
    print("  A counts:", ca_p, "| error P(1):", round(err_A_phase, 4))
    print("  B counts:", cb_p, "| error P(0):", round(err_B_phase, 4))

    # Depolarizing
    nm_dep = build_noise_model("depolarizing", p)
    ca_d = run(circuit_A(), nm_dep)
    cb_d = run(circuit_B(), nm_dep)

    err_A_dep = prob(ca_d, "1")
    err_B_dep = prob(cb_d, "0")

    print("Depolarizing:")
    print("  A counts:", ca_d, "| error P(1):", round(err_A_dep, 4))
    print("  B counts:", cb_d, "| error P(0):", round(err_B_dep, 4))

print("\nExpected:")
print("- As p increases, both circuits lose determinism.")
print("- Phase damping specifically destroys phase coherence, which is what interference relies on.")
