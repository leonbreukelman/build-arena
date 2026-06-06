# Project Model v1 and Pre-Live Readiness Plan

Date: 2026-06-05
Status: Build Arena v1 emission implemented; related-repo adoption remains open
Spec: `docs/specs/2026-06-05-project-model-v1-shared-contract-spec.md`
Readiness register: `docs/verification/2026-06-05-pre-live-readiness-register.json`

## Goal

Make `project-model/v1` the primary enriched AI decomposer contract in Build Arena, keep Project Model v0 as a compatibility projection, and classify the remaining pre-live blockers before any full autonomous live loop begins.

## Architecture

Build Arena keeps its internal `ProjectModelSnapshot` and deterministic gate as the source of runtime truth. A new v1 builder composes the snapshot, ProjectGraph, GateReport, provenance, hashes, model ids, and derived-artifact strategy into `project-model-v1.json`. The decomposer manifest points to v1 as primary and v0 as compatibility output.

## Completed Build Arena slice

### Task 1: Add v1 contract tests first

Files:

- `tests/test_project_model_v1_contract.py`

Verification:

- Initial run failed because `arena.project_model_v1` did not exist.
- Current targeted result: `uv run pytest tests/test_project_model_v1_contract.py -q` passes.

### Task 2: Add v1 builder

Files:

- `arena/project_model_v1.py`

Behavior:

- Builds `project-model/v1` from the existing snapshot, graph, and gate report.
- Computes a dirty-state fingerprint from git head OID, dirty flag, and dirty paths.
- Names JSONL, SQLite, and Markdown derived-artifact strategies without treating them as authoritative runtime state.

### Task 3: Emit v1 as the primary AI decomposer artifact

Files:

- `arena/project_decomposer_ai.py`

Behavior:

- Writes `project-model-v1.json` in each snapshot directory.
- Keeps writing `project-model-v0.json`.
- Adds primary and compatibility paths/hashes to `manifest.json`.

### Task 4: Add v1 schema

Files:

- `docs/schemas/project-model-v1.schema.json`

Behavior:

- Validates the emitted v1 artifact.
- Includes ProjectGraph, GraphNode, GraphEdge, ProvenanceRef, Component, Contract, CrossCuttingConcern, ObservableCheck, HeldOutProbe, VerificationGap, ProjectModelSnapshot, GateReport, git OID, dirty-state fingerprint, input hashes, prompt hashes, model ids, output hashes, and derived-artifact strategy.
- Rejects a legacy v0-shaped object.

### Task 5: Preserve v0 compatibility

Verification:

- Existing v0 tests still pass in the targeted suite.
- The v1 contract test asserts that `project-model-v0.json` still exists and is named in the manifest.

## Remaining pre-live work by mode

### Read-only live smoke

Status: allowed with guardrails for small bounded repositories.

Required proof before claiming success:

- Provider returns non-empty parseable JSON.
- Build Arena records prompt/output hashes and provider metadata.
- Gate result is explicit and saved, even when failed.
- No live API call is required in CI.

### Dry-run hypothesis generation

Status: blocked until v1 consumer readiness is proven for Elenchus Core or a local dry-run adapter that consumes v1 without mutation is implemented.

### Worktree-only patch cycle

Status: blocked.

Required before enabling:

- Verification-gap policy enforced in code for mutation boundaries.
- Target repo graph/indexing adequacy proven for the surfaces being mutated.
- Independent review confirms v1 snapshot cannot silently pass with critical gaps.

### Promotion or merge

Status: blocked.

Required before enabling:

- No critical or blocker verification gaps on mutated surfaces.
- Worktree cycle evidence is independently reviewed.
- The promoter remains the only component that advances the internal baseline by ff-only merge.

## Graph and indexing plan

Do not add Tree-sitter, ast-grep, SCIP/LSIF, or CodeQL in this slice. The current deterministic graph is enough for bounded read-only live smoke and v1 contract proof. Add stronger indexing only when a target repo needs JS/TS/Markdown route/config edges or when the readiness register marks graph limitations as blocking a worktree patch cycle.

## Verification-gap policy plan

The policy is specified in the v1 spec and classified in the readiness register. Code-level enforcement should be added in the first session that attempts dry-run hypothesis generation or worktree mutation. Tests for that future slice should cover:

1. Critical gap blocks mutation.
2. Blocker gap blocks mutation.
3. High gap blocks promotion.
4. Medium gap permits read-only analysis but creates a backlog item.
5. Protected/generated/scorer/verifier/schema surfaces are non-mutable independent of gap severity.

## Related-repo adoption plan

Elenchus Core:

- Inspect current project-model consumption path.
- Add or plan a v1 parser/adapter that can inspect provenance, contracts, probes, verification gaps, and gate reports.
- Keep v0 compatibility.
- Add tests for wrong-target, fabricated-provenance, and weak-probe cases.

Arena Calibration:

- Inspect current fixtures and evaluator usage.
- Add v1 fixtures for valid rich snapshot, fluent file-bucket fake, fabricated provenance, missing import contract, reversed contract direction, self-referential contract, protected/generated ownership leak, weak held-out probe, and verification gap mislabeled as success.
- Add schema and deterministic gate expected pass/fail tests.

## Verification commands for this Build Arena slice

Run before commit:

```bash
uv run pytest tests -q
uv run ruff check .
uv run pyright
git diff --check
```

Also validate JSON artifacts and schemas:

```bash
python3 -m json.tool docs/schemas/project-model-v1.schema.json >/dev/null
python3 -m json.tool docs/verification/2026-06-05-pre-live-readiness-register.json >/dev/null
```

## Commit boundary

Commit the coherent Build Arena slice after verification passes. Do not push, deploy, merge, or run a full autonomous live loop in this session.
