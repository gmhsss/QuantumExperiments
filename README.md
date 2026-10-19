# QuantumExperiments

A little lab notebook of quantum experiments, written in [Qiskit](https://www.ibm.com/quantum/qiskit) — from "what even is superposition?" all the way to noisy circuits and small agentic policies. Built to learn by *running things*, breaking them with noise, and plotting what happens. 

## What's inside

| Module | Topic | What you'll see |
|---|---|---|
| `01_single_qubit_gates` | Superposition, phase, interference | Why phase is invisible in Z but shows up after H-Z-H |
| `02_two_qubits` | Entanglement | Bell states and their correlations |
| `03_oracles` | Oracles & Deutsch–Jozsa | One query to tell constant from balanced (n = 2, 3), plus noise robustness |
| `04_noise` / `04_noise_and_fidelity` | Noise & fidelity | Phase damping vs. depolarizing, and what it does to interference and entanglement |
| `05_communication` | Teleportation | Teleporting a qubit, then watching fidelity fall as noise grows |
| `06_multipartite` | GHZ vs. W | Which entangled state survives noise better? |
| `07_agentic` | Small decision policies | Choosing shots, measurement basis (Z vs. X) and noise thresholds |
| `08_grover` | Grover search | Ideal vs. noisy, and a stopping rule |

Each module has its own `README.md` with the experiments and takeaways, and most keep their plots in a `results/` folder. 📈

## Running an experiment

```bash
pip install qiskit qiskit-aer matplotlib numpy
python experiments/01_single_qubit_gates/exp_01_hadamard_superposition.py
```

Experiments are numbered inside each module, so reading them in order tells a story.

## Also here: `qfi-mis/`

A research side project (PIBIC, PUCPR): measuring **Quantum Functional Information** on Maximum Independent Set, and comparing QAOA with classical EDAs and genetic algorithms on the same landscape. Work in progress — see [`qfi-mis/README.md`](qfi-mis/README.md).

## License

The code in [`experiments/`](experiments/) is released under the [MIT License](experiments/LICENSE). Please keep the attribution: *Rafaella Somoza*.
`qfi-mis/` is a separate research project and is not covered by that license yet.

---

Made with curiosity (and a lot of `AerSimulator`) 💜
