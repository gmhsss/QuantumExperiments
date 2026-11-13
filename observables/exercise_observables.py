"""
Exercicio de observaveis (Prof. Rodrigo Pasti): valores esperados de strings de Pauli
em circuitos de 3 qubits, estimados por contagens (shots) e comparados com o valor exato.

Baseado no conceito do observables_template.py do professor; implementacao propria.

Convencao: pauli_string[i] atua no qubit i. Qiskit usa little-endian nas contagens
(bit mais a direita = qubit 0), entao o bit do qubit i esta em bitstring[n-1-i].
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit.quantum_info import Statevector, Pauli

N = 3
SHOTS = 10000
BASES = ["ZZZ", "XXX", "YYY", "XYZ"]


def prepare(kind):
    qc = QuantumCircuit(N)
    for i in range(N):
        qc.h(i)
    if kind == "H+S":
        for i in range(N):
            qc.s(i)
    elif kind == "H+T":
        for i in range(N):
            qc.t(i)
    return qc


CIRCUITS = ["H", "H+S", "H+T"]


def measure_in_basis(qc, pauli_string):
    """Copia o circuito e gira cada qubit para a base do Pauli pedido, depois mede."""
    m = qc.copy()
    m.add_register(__import__("qiskit").ClassicalRegister(N))
    for i, p in enumerate(pauli_string):
        if p == "X":
            m.h(i)
        elif p == "Y":
            m.sdg(i)
            m.h(i)
    for i in range(N):
        m.measure(i, i)
    return m


def expectation_from_counts(counts, pauli_string):
    """<P> = soma_x p(x) * produto dos autovalores (bit 0 -> +1, bit 1 -> -1)."""
    total = sum(counts.values())
    n = len(pauli_string)
    exp = 0.0
    for bits, c in counts.items():
        val = 1
        for i, p in enumerate(pauli_string):
            if p == "I":
                continue
            val *= 1 if bits[n - 1 - i] == "0" else -1
        exp += (c / total) * val
    return exp


def exact_expectation(qc, pauli_string):
    # Qiskit Pauli: string escrita com o qubit 0 mais a direita
    return float(np.real(Statevector.from_instruction(qc).expectation_value(Pauli(pauli_string[::-1]))))


if __name__ == "__main__":
    backend = AerSimulator()
    rows = []
    for c in CIRCUITS:
        qc = prepare(c)
        for b in BASES:
            m = transpile(measure_in_basis(qc, b), backend)
            counts = backend.run(m, shots=SHOTS, seed_simulator=7).result().get_counts()
            est = expectation_from_counts(counts, b)
            ex = exact_expectation(qc, b)
            rows.append((c, b, est, ex))
    print(f"{'circuito':8s} {'bases':5s} {'medido':>8s} {'exato':>8s} {'dif':>7s}")
    for c, b, est, ex in rows:
        print(f"{c:8s} {b:5s} {est:8.3f} {ex:8.3f} {est-ex:7.3f}")
    # grafico
    fig, ax = plt.subplots(figsize=(8, 4.2))
    w = 0.35
    x = np.arange(len(rows))
    ax.bar(x - w/2, [r[3] for r in rows], w, label="exato")
    ax.bar(x + w/2, [r[2] for r in rows], w, label=f"medido ({SHOTS} shots)")
    ax.set_xticks(x)
    ax.set_xticklabels([f"{r[0]}\n{r[1]}" for r in rows], fontsize=7)
    ax.set_ylabel("valor esperado da string de Pauli")
    ax.axhline(0, c="k", lw=.6)
    ax.legend()
    plt.tight_layout()
    plt.savefig("observables_resultados.png", dpi=140)
    with open("observables_resultados.csv", "w") as f:
        f.write("circuito,bases,medido,exato\n")
        for r in rows:
            f.write(f"{r[0]},{r[1]},{r[2]:.4f},{r[3]:.4f}\n")
