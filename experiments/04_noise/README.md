## Module 04 — Noise & Decoherence (NISQ Reality)

This module studies how different noise mechanisms affect
quantum information, interference, and entanglement.

Focus:
- phase damping vs depolarizing noise
- loss of coherence
- when quantum advantage disappears

---

## Results & Findings

### Phase damping vs depolarizing (single qubit)
Measuring |+> in the Z basis stays ~50/50 even under phase damping, because Z measurements do not reveal phase information. This motivates interference-based tests to detect coherence loss.

### Interference under noise (HZH)
The deterministic interference patterns (H→H gives 0, H→Z→H gives 1) degrade under noise. Depolarizing noise increases error rates faster than phase damping at low-to-moderate noise levels.

### Entanglement and basis-dependent signatures
For the Bell state |Φ+>, phase damping preserves Z-basis correlation (bits still match) while significantly reducing X-basis correlation, revealing coherence loss. Depolarizing noise reduces correlations in both bases, approaching ~0.5 at high noise (near-random outcomes).
