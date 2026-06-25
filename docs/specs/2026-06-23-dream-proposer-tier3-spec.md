# Dream Proposer (Tier 3) — Design Record

> **Superseded in part (2026-06-25):** the operator review gate described below
> (`operator review gate`, `review.reviewed true required`, exit `4`) is removed.
> The lane now emits autonomously; the capability map is auto-generated and used
> as-is, with an honest provenance label on the output. See
> `docs/specs/2026-06-25-experiment-lane-autonomous-emit.md`. Body retained as the
> historical record.

Date: 2026-06-23
Status: implemented locally in this checkout; offline acceptance added.

## Goal

Add a tier-3 divergent proposer lane that emits advisory architectural hypotheses as `dream.md`. The lane is for improvements that do not fit the single-file deterministic proposal contract: carrier swaps, capability remaps, redrawn boundaries, and added capabilities. It never applies a patch, never promotes a branch, and never writes `proposal.md`.

The working artifact is a `dream.md` produced from a gated `dream/v0` document. Each rendered dream must carry:

- cited current-state evidence;
- mechanically separated premise confidence;
- capped speculative conclusion confidence;
- a concrete validation recipe for a downstream repo agent.

## Architecture decision

The dream proposer is a parallel track, not a `ProposalDomainRegistry` member.

Reasons:

1. `arena/proposal_domains.py` is explicitly offline and file-patch-centric.
2. `ProposalCandidateDraft` requires a target path and verification commands for a concrete patch candidate; a dream has no single-file target.
3. The existing proposal path ranks actionable patch candidates. A divergent architectural hypothesis would pollute that ranking and launder speculation as deterministic work.

The dream lane shares inputs with the proposal pipeline — Project Model v1 and intake scorecard — and adds a reviewed capability map. It then runs:

```text
Project Model v1 + intake scorecard
  -> arena.capability_lift        -> capability-map/v0 (review.reviewed false)
  -> operator review gate          -> review.reviewed true required
  -> arena.dream_generate          -> raw dreams (live / injected in tests)
  -> arena.dream_research          -> premise-dense dreams (live / injected in tests)
  -> arena.dream_gate              -> gated dream/v0 (deterministic kill gate)
  -> arena.dream_emit              -> dream.md (deterministic advisory renderer)
```

`arena.dream_run` is the thin orchestrator for the lane.

## Contracts

### `capability-map/v0`

File: `docs/schemas/capability-map-v0.schema.json`

An advisory, operator-reviewed function/capability overlay over Project Model v1. It is a separate artifact, not a Project Model v1 field, because capability inference is interpretive and may be edited by the operator. Every capability cites real Project Model component ids and optional graph node ids.

Load-bearing invariant:

- every `capabilities[].realizedByComponentIds[]` resolves to `snapshot.components[].id`;
- every `capabilities[].supportingNodeIds[]` resolves to `projectGraph.nodes[].id`;
- `review.reviewed` defaults to `false`.

### `dream/v0`

File: `docs/schemas/dream-v0.schema.json`

A gated advisory hypothesis artifact. Schema-level constraints keep the lane honest:

- `mode` is one of `carrier_swap` or `function_remap`;
- every dream has target capabilities, cited evidence, rationale, separated confidences, and a validation recipe;
- `conclusionConfidence.band` is only `low` or `medium`;
- `conclusionConfidence.value` is capped at `0.7`;
- rendered artifacts require `premiseConfidence == all_resolved`.

## Stage summaries

### `arena.capability_lift`

Deterministic v0 lift from `snapshot.components[]` and `iterationReadiness.componentProfiles[]`. It emits schema-valid `capability-map/v0`, self-validates references, and marks the map unreviewed.

CLI:

```bash
uv run python -m arena.capability_lift --project-model project-model-v1.json --output capability-map.json
```

### `arena.dream_generate`

Typed single-shot generation. The production path requires `--live-model`; tests use an injected model callable. It drops candidates missing the minimum grounding surface: mode, target capability id, cited evidence, and validation recipe.

### `arena.dream_research`

LLM-driven change-impact/research pass. It rewrites raw dreams into premise-dense hypotheses by adding concrete cited anchors. It does not certify benefit; that remains speculative and capped.

### `arena.dream_gate`

Deterministic kill gate. It resolves each `citedEvidence` anchor against the real Project Model v1 / capability map and verifies `contentHash` consistency using canonical JSON SHA-256 of the resolved anchor object. It also verifies target capability ids, mode, conclusion-confidence bounds, and recipe presence.

Accepted dreams are emitted with `premiseConfidence: all_resolved`. Unresolved, partial, malformed, or fabricated-premise dreams are killed and recorded in the gate trace.

The gate also stamps `provenance.gatedBy: arena.dream_gate`, records a `promptHashes.gate` marker, and refuses a capability map whose recorded `sourceModel.graphHash` diverges from the Project Model v1 graph hash. This is defense-in-depth so `dream_emit` does not trust a model- or hand-authored `premiseConfidence: all_resolved` field by itself.

### `arena.dream_emit`

Deterministic markdown renderer. It validates `dream/v0`, refuses any non-`all_resolved` dream, renders readable evidence lines, shows premise and conclusion confidence separately, includes the validation recipe, and writes `dream.md` only. It refuses to write `proposal.md`.

`dream_emit` requires the gate provenance marker before rendering. It still does not prove that the free-text `citedEvidence.claim` is semantically true; the deterministic guarantee is anchor existence/content consistency plus advisory labeling, not claim truth.

### `arena.dream_run`

Thin fail-closed orchestrator. It runs stages through injectable subprocess seams and preserves the workdir on failure. Exit codes:

- `0`: success, `dream.md` written;
- `1`: stage failure;
- `2`: no dream survived the premise gate;
- `3`: usage/preflight error;
- `4`: capability map not reviewed.

A first real run normally stops at exit `4` after writing `capability-map.json`; the operator reviews/edits that file and reruns with `--capability-map <reviewed-map>`.

## Acceptance tests

Implemented offline tests:

- `tests/test_capability_lift.py`
- `tests/test_dream_generate.py`
- `tests/test_dream_research.py`
- `tests/test_dream_gate.py`
- `tests/test_dream_emit.py`
- `tests/test_dream_run.py`

Required safety assertions covered:

1. capability references resolve and bad refs fail closed;
2. generation keeps typed diversity and minimum grounding;
3. research preserves a checkable premise surface;
4. grounded dreams pass and planted fabricated anchors are killed;
5. missing recipe / invalid mode are killed;
6. emit is byte-identical for fixed input;
7. partial/unresolved dreams never reach `dream.md`;
8. `dream_emit` never writes `proposal.md`;
9. `dream_run` enforces stage order, manifest-driven Project Model v1 resolution, preflight, unreviewed-map exit `4`, no-dream exit `2`, and workdir preservation.

## Known boundaries

- Live generation/research are not byte-reproducible. The deterministic boundary is the gated `dream/v0` artifact.
- The gate verifies premise resolution, not usefulness or buildability.
- Elenchus alignment, loop-back re-research, population/QD generation, reference-architecture retrieval, dashboards, promotion, and repo-agent execution are out of scope for v0.
- The current implementation remains advisory. A real live `dream_run` with operator-reviewed capability map is still operator-gated because it spends model calls.
