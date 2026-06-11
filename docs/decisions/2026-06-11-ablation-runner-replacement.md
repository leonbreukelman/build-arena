# Decision: deterministic AblationRunner replacement target

Date: 2026-06-11

## Decision

`DeterministicOllamaAblationRunner` remains a deterministic no-API stand-in for
Build Arena's ablation verifier seat. It is not a live Lanham ablation gate and
must not be treated as load-bearing semantic proof for real autonomous cycles.

The intended replacement is the Arena Calibration regeneration/Lanham verifier
once it is certified by its own discrimination matrix and patch-generalization
axis. In practical terms, the replacement must show that it can separate known
positive, neutral, and negative patches and catch the F3-style generalization
failure before its output can influence promote/discard decisions.

Elenchus may supply advisory planning, decomposition, or operator-review
metadata, but Elenchus is advisory only. It is not the verifier replacement and
must not become an uncalibrated promote/discard gate.

A future live Ollama adapter is subordinate to that certification path. Merely
calling a live model through Ollama is insufficient; the live instrument must be
bound to the certified discrimination matrix and patch-generalization axis first.

## Consequences

- README/AGENTS/brief FP/FN figures are stand-in calibration figures, not live
  ablation-performance claims.
- Broad live loops remain blocked while this verifier seat is a deterministic
  stand-in.
- Any implementation that replaces the stand-in must update this decision,
  active status docs, and tests in the same change.
