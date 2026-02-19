"""
Experiment 04 — Bell correlations in Z vs X under noise

We prepare |Phi+> = (|00> + |11>)/sqrt(2)

We measure correlation rate:
  Corr = P(bit0 == bit1) = P(00) + P(11)

We compare:
- Z basis measurement (direct)
- X basis measurement (apply H on both qubits before measuring)

Key idea:
- Phase damping mainly destroys coherence (off-diagonal terms),
  so it is much more visible in X-basis correlations than in Z-basis.
"""

from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, phase_damping_error, depolarizing_error, ReadoutError

shots = 4096
noise_levels = [0.0, 0.05, 0.10, 0.20, 0.30, 0.50]

# Optional: simulate "time passing" by inserting identity gates and applying phase damping to them.
USE_TIMESTEP = True
TIMESTEPS_AFTER_CX = 3

def bell_phi_plus(measure_basis: str):
    qc = QuantumCircuit(2, 2)
    qc.h(0)
    qc.cx(0, 1)

    if USE_TIMESTEP:
        for _ in range(TIMESTEPS_AFTER_CX):
            qc.id(0)
            qc.id(1)

    if measure_basis.upper() == "X":
        qc.h(0)
        qc.h(1)

    qc.measure(0, 0)
    qc.measure(1, 1)
    return qc

def build_noise_model(kind: str, p: float) -> NoiseModel:
    nm = NoiseModel()
    if p <= 0:
        return nm

    if kind == "phase":
        e1 = phase_damping_error(p)
        # Phase damping on 1-qubit gates + optional timestep ids
        for g in ["h", "id"]:
            nm.add_all_qubit_quantum_error(e1, g)

        # We do NOT attach 1q errors to "cx" (Aer forbids).
        # The timestep ids after CX model decoherence affecting the entangled state.

    elif kind == "depolarizing":
        e1 = depolarizing_error(p, 1)
        e2 = depolarizing_error(p, 2)
        nm.add_all_qubit_quantum_error(e1, "h")
        nm.add_all_qubit_quantum_error(e1, "id")
        nm.add_all_qubit_quantum_error(e2, "cx")

    else:
        raise ValueError("Unknown noise kind")

    return nm

def run(qc, nm):
    sim = AerSimulator(noise_model=nm)
    return sim.run(qc, shots=shots).result().get_counts()

def corr_rate(counts):
    p00 = counts.get("00", 0) / shots
    p11 = counts.get("11", 0) / shots
    return p00 + p11

print("\n=== Experiment 04 — Bell correlations in Z vs X under noise ===")
print(f"shots={shots}, USE_TIMESTEP={USE_TIMESTEP}, TIMESTEPS_AFTER_CX={TIMESTEPS_AFTER_CX}")
print("Correlation metric: P(bit0 == bit1) = P(00) + P(11)")

for p in noise_levels:
    print(f"\n--- p={p} ---")

    for kind in ["phase", "depolarizing"]:
        nm = build_noise_model(kind, p)

        cz = corr_rate(run(bell_phi_plus("Z"), nm))
        cx = corr_rate(run(bell_phi_plus("X"), nm))

        print(f"{kind:12s} | Corr(Z)={cz:0.4f} | Corr(X)={cx:0.4f}")

print("\nExpected:")
print("- Corr(Z) for phase damping can remain high (phase errors don't flip bits).")
print("- Corr(X) should drop significantly under phase damping (coherence loss).")
print("- Depolarizing tends to reduce both Corr(Z) and Corr(X).")
