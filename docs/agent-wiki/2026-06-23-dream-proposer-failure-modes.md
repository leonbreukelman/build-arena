# Dream Proposer Failure Modes — 2026-06-23

## Why this page exists

The dream proposer is allowed to invent advisory architecture hypotheses, so its failure mode is not merely bad code. The dangerous failure is laundering speculation as grounded deterministic work. Future agents must preserve the lane boundary and the kill gate.

## New lane rules

1. `dream.md` is advisory only. It never authorizes mutation, promotion, or a patch.
2. `dream_emit` must not write `proposal.md`. A dream is not a proposal candidate.
3. `capability-map/v0` is operator-reviewed intent. `review.reviewed: true` is required before generation/research/gate can produce an emitted dream.
4. `dream_gate` is the trust boundary. It kills dreams whose cited anchors, target capabilities, content hashes, mode, or validation recipe do not resolve.
5. `dream_gate` stamps gate provenance, and `dream_emit` refuses artifacts lacking that marker. Do not let emit trust a model-authored `premiseConfidence: all_resolved` field by itself.
6. `conclusionConfidence` is soft and capped. It is not a pre-emission proof of benefit.

## Failure modes to remember

### F-MAEI: means displacing ends

Problem: the team optimizes dream-generation volume or prettiness instead of proving emitted dreams lead to downstream successful attempts.

Guard: the external license for this lane is emitted -> attempted by repo agent -> tests/build/metric verdict. Until a structured ledger exists, record live dream ids and downstream attempt outcomes in this wiki or a versioned report. If acceptance-rate is zero or untracked, the dreamer is noise.

### F-neuter: safe but non-novel output

Problem: anti-fabrication pressure collapses tier 3 into another grounded proposer that only says what already exists.

Guard: keep the novelty-floor test. The generator path must be able to produce at least one `function_remap` dream that describes a boundary/capability change rather than a single-file patch.

### F-drift: wrong capability map becomes truth

Problem: the capability lift guesses intent incorrectly, and every dream optimizes that wrong map.

Guard: the capability map is never truth until operator review. The gate checks coherence given the reviewed map; it does not retire the review gate and does not prove the map is semantically right.

### F-false: confident nonsense from fabricated premises

Problem: a dream cites an anchor that does not exist or whose content changed.

Guard: maintain the planted-fabrication test. A fabricated `citedEvidence.anchorId` must be killed by `dream_gate`, with no `dream.md` written by the orchestrator for that survivor set.

Defense-in-depth: `dream_gate` must reject capability maps whose `sourceModel.graphHash` does not match the Project Model v1 graph hash, and `dream_emit` must require `provenance.gatedBy: arena.dream_gate` plus the gate prompt hash marker.

### F-invalid: real premises, bad conclusion

Problem: every anchor resolves, but the conclusion is still wrong or not worth doing.

Guard: do not promote conclusion confidence above `medium` / `0.7`; require a validation recipe and let the downstream repo agent/test reality judge benefit. Also remember that `citedEvidence.claim` text is rendered for human readability but is not semantically proven by the gate; the gate proves the anchor exists and has the cited content hash.

## Gate recipe

Focused local verification for this lane:

```bash
uv run pytest tests/test_capability_lift.py tests/test_dream_generate.py tests/test_dream_research.py tests/test_dream_gate.py tests/test_dream_emit.py tests/test_dream_run.py -q
uv run ruff check arena/capability_lift.py arena/dream_generate.py arena/dream_research.py arena/dream_gate.py arena/dream_emit.py arena/dream_run.py tests/test_capability_lift.py tests/test_dream_generate.py tests/test_dream_research.py tests/test_dream_gate.py tests/test_dream_emit.py tests/test_dream_run.py
uv run pyright arena/capability_lift.py arena/dream_generate.py arena/dream_research.py arena/dream_gate.py arena/dream_emit.py arena/dream_run.py tests/test_capability_lift.py tests/test_dream_generate.py tests/test_dream_research.py tests/test_dream_gate.py tests/test_dream_emit.py tests/test_dream_run.py
```

Whole-repo gates remain `uv run pytest tests -q`, `uv run ruff check .`, `uv run pyright`, and `make generated`, but this checkout may contain unrelated dirty files from other work. Do not attribute unrelated failures to the dream lane without isolating them.
