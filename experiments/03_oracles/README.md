## Module 03 — Quantum Oracles & Interference

This module introduces quantum oracles and shows how interference
can be used to extract global properties of a function.

The focus is not on speedups alone, but on understanding *why*
quantum algorithms work.

### Topics
- Boolean functions and oracles
- Phase kickback
- Interference as a computational resource
- Deutsch and Deutsch–Jozsa problems

---

## Results & Findings

### Deutsch (n=1)
Using a single oracle query, the algorithm deterministically classifies:
- measurement `0` → **constant**
- measurement `1` → **balanced**

This illustrates how **interference** can reveal a *global* property of a Boolean function without learning `f(x)` itself.

### Deutsch–Jozsa (n=2)
For ideal simulation, the decision rule is deterministic:
- input register measures `00` → **constant**
- any other outcome → **balanced**

We also implemented a small experimental loop that generates random constant/balanced truth tables, compiles them into an oracle `U_f`, runs Deutsch–Jozsa, and reports classification accuracy. In the ideal simulator the accuracy is `1.0`.

### Robustness under noise (n=2)
We stress-tested robustness by sweeping:
- depolarizing gate noise `p_gate`
- readout bit-flip noise `p_readout`
- number of shots

Key observations:
- With moderate noise and enough shots, the majority-vote classifier remains accurate.
- Under stronger noise and low-shot regimes, accuracy degrades (e.g., noticeable drops around `p_gate ≈ 0.20–0.30` with small shot counts).

### Scaling test (n=3)
For `n=3` input qubits, the algorithm remains deterministic in the ideal simulator:
- constants → always `000`
- balanced functions → never `000`

Different balanced functions can produce distinct deterministic signatures (e.g., `001`, `010`, `100`, `111`), reflecting how the oracle influences the interference pattern.

### Agentic threshold search
We implemented a minimal “agentic” experiment loop that searches for the largest `p_gate` that still satisfies a target accuracy threshold under fixed readout noise.

Example run (shots=128, trials=60, p_readout=0.05, target accuracy ≥ 0.95):
- estimated maximum `p_gate ≈ 0.24` meeting the target.

This is a stepping stone toward automated experimentation workflows (generate → run → evaluate → update).

---

## How to run

From the project root:

```bash
python3.11 experiments/03_oracles/exp_01_classical_boolean_functions.py
python3.11 experiments/03_oracles/exp_02_quantum_oracle.py
python3.11 experiments/03_oracles/exp_03_deutsch_algorithm.py
python3.11 experiments/03_oracles/exp_04_deutsch_jozsa_n2.py
python3.11 experiments/03_oracles/exp_05_random_oracles_classifier.py
python3.11 experiments/03_oracles/exp_06_noise_robustness.py
python3.11 experiments/03_oracles/exp_07a_noise_stress_test.py
python3.11 experiments/03_oracles/exp_07b_deutsch_jozsa_n3.py
python3.11 experiments/03_oracles/exp_07c_agentic_threshold_search.py
