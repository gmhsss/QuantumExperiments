# Chapter 7 — Agentic Quantum Control

This chapter introduces agent-based control loops applied to quantum experiments.

Instead of running circuits with fixed parameters, a classical agent:
- observes experimental outcomes,
- evaluates performance metrics,
- and adaptively selects actions to satisfy constraints.

This bridges quantum computing, decision theory, and agentic AI.

---

## Results & Findings

### Agentic shot optimization
A classical agent dynamically selected the minimum number of shots required to maintain a target accuracy. Results show that increasing shots only mitigates statistical noise and cannot compensate for strong physical noise in the circuit.

### Agentic basis selection
For Bell states under noise, the agent compared Z- and X-basis measurements and consistently selected the basis maximizing correlation. Under phase damping, Z-basis correlations remained robust while X-basis correlations degraded due to coherence loss. Under depolarizing noise, both bases degraded, but Z-basis remained slightly more stable for equality-based metrics.

### Agentic noise threshold policy
The agent learned the maximum depolarizing noise strength for which Bell-state correlations remained above a target threshold. A coarse-to-fine search strategy was used to estimate the operational noise boundary, demonstrating a simple but effective policy-learning mechanism for quantum systems.

### Key insight
These experiments demonstrate that quantum experiments can be augmented with classical agentic control loops, enabling adaptive decision-making under noise. This hybrid paradigm is essential for near-term quantum systems where noise-aware strategies outperform static configurations.
