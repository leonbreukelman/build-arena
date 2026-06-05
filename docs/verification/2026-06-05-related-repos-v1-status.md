# Related Repositories Project Model v1 Follow-up Status

Date: 2026-06-05
Scope: read-only inspection of `/home/leonb/projects/elenchus-core` and `/home/leonb/projects/arena-calibration`
Build Arena v1 spec: `docs/specs/2026-06-05-project-model-v1-shared-contract-spec.md`
Inspection transcript: `docs/verification/2026-06-05-related-repos-inspection.json`

## Summary verdict

Build Arena now emits `project-model/v1`, but the related repositories are still Project Model v0 consumers/fixtures only.

- Elenchus Core: v1 adoption is required before dry-run hypothesis generation or worktree mutation can rely on Elenchus review of v1 snapshots. Current code explicitly accepts only `schemaVersion: project-model/v0`; v1 would be reported as `unsupported_version`.
- Arena Calibration: v1 fixture/evaluator adoption is required before the decomposer can be calibrated against v1-specific failure modes such as fabricated provenance, weak held-out probes, missing graph contracts, and misclassified verification gaps. Current fixture suite is explicitly v0-only.

This does not block bounded read-only Build Arena live smoke. It blocks broader cross-repo readiness claims, worktree patch cycles driven from v1, and promotion/merge decisions based on v1 artifacts.

## Elenchus Core status

Repository:

- Path: `/home/leonb/projects/elenchus-core`
- Branch observed: `feat/project-model-v0-signals`
- Dirty state observed: four untracked docs files unrelated to this inspection:
  - `docs/plans/2026-06-02-tech-wide-lens-expansion.md`
  - `docs/specs/2026-06-02-tech-wide-lens-expansion.md`
  - `docs/verification/2026-06-02-tech-wide-lens-plan-opus-review.md`
  - `docs/verification/2026-06-02-tech-wide-lens-spec-opus-review.md`

Evidence read:

- `/home/leonb/projects/elenchus-core/src/elenchus_core/project_model.py`
- `/home/leonb/projects/elenchus-core/docs/api-project-model-v0.md`
- `/home/leonb/projects/elenchus-core/tests/test_project_model_v0.py` was exercised by the targeted test command.

Observed contract behavior:

- `src/elenchus_core/project_model.py` defines `PROJECT_MODEL_V0_SCHEMA_VERSION = "project-model/v0"`.
- `ProjectModelV0.schemaVersion` is typed as `Literal["project-model/v0"]`.
- `assess_project_model_alignment()` reads `request.projectModel`, runs `evaluate_quality_gate()`, and classifies any schema version other than v0 as `unsupported_version`.
- `evaluate_quality_gate()` emits `unsupported_schema_version` with message `Project Model quality gate only accepts project-model/v0.` when `schemaVersion` is not `project-model/v0`.
- `docs/api-project-model-v0.md` documents the v0 API and states absent, invalid, or unsupported Project Models are reported as model/input quality issues.

Verification run:

```text
cd /home/leonb/projects/elenchus-core
uv run pytest tests/test_project_model_v0.py -q
.....                                                                    [100%]
```

Precise v1 follow-up for Elenchus Core:

1. Add a `ProjectModelV1` parser/adapter alongside the existing v0 path. Do not remove v0 support.
2. Accept `schemaVersion: project-model/v1` in `assess_project_model_alignment()` and route it to v1-specific alignment checks rather than `unsupported_version`.
3. Preserve the advisory-only semantics. A v1 check must not become an autonomous allow/deny gate.
4. Evaluate at least these v1 fields:
   - `projectGraph.nodes[*].provenance_refs`
   - `projectGraph.edges[*].provenance_refs`
   - `snapshot.components[*].provenance_refs`
   - `snapshot.contracts[*].supporting_edge_ids`
   - `snapshot.observable_checks[*]`
   - `snapshot.held_out_probes[*]`
   - `snapshot.verification_gaps[*]`
   - `gateReport.passed` and `gateReport.violations`
   - `provenance.git.dirtyStateFingerprint`
5. Add tests showing:
   - v0 remains accepted and current v0 tests still pass.
   - a valid Build Arena v1 fixture is accepted as v1, not unsupported.
   - missing/fabricated provenance is reported as a grounding gap.
   - gate-failing v1 output caps recommendation and adds `invalid_project_model` or a v1-specific readiness reason.
   - weak or absent held-out probes create advisory gaps.
   - unresolved high/blocker verification gaps are surfaced as review blockers, not ignored.

Suggested Elenchus implementation prompt:

```text
Implement Project Model v1 advisory input support in Elenchus Core without removing v0 support. Use Build Arena's `docs/schemas/project-model-v1.schema.json` and emitted `project-model-v1.json` fixture as the contract. Add a v1 model/adapter that evaluates provenance refs, graph contract support, gate report status, held-out probes, verification gaps, and dirty-state fingerprint. Preserve advisory-only semantics and ensure unsupported/invalid v1 snapshots cap recommendations. Add tests for valid v1, fabricated provenance, gate-failing v1, weak probes, and unresolved blocker/high gaps. Run `uv run pytest -q`, `uv run ruff check .`, and `uv run mypy .` or the repo's existing typecheck command.
```

## Arena Calibration status

Repository:

- Path: `/home/leonb/projects/arena-calibration`
- Branch observed: `test/100-percent-coverage`
- Dirty state observed: clean.

Evidence read:

- `/home/leonb/projects/arena-calibration/README.md` inspection summary captured in `2026-06-05-related-repos-inspection.json`.
- `/home/leonb/projects/arena-calibration/arena/project_model_fixtures.py`
- `/home/leonb/projects/arena-calibration/tests/test_project_model_fixtures.py`

Observed contract behavior:

- `arena/project_model_fixtures.py` is explicitly a Project Model v0 fixture loader/checker.
- `PROJECT_MODEL_SCHEMA_VERSION = "project-model/v0"`.
- The loader rejects any fixture whose `project_model.schemaVersion` is not v0.
- Required fields reflect the old v0 parent contract, including `dependencies`, `invariants`, `evidenceRequirements`, `assumptions`, `risks`, and `advisorySignalHandoff`.
- Tests load only `fixtures/project_model_v0` and assert five current v0 fixtures:
  - `F1_project_model_aligned`
  - `F2_project_model_decorative`
  - `F3_project_model_code_too_narrow`
  - `F3_project_model_process_wrong_sequence`
  - `F4_project_model_trivial`

Verification run:

```text
cd /home/leonb/projects/arena-calibration
uv run pytest tests/test_project_model_fixtures.py -q
...............................                                          [100%]
31 passed in 0.07s
uv run python exercise_project_model_fixtures.py --json
# Parsed JSON successfully; summary keys present under metadata, summary, fixtures; fixture_count=5.
```

Precise v1 follow-up for Arena Calibration:

1. Add a separate `fixtures/project_model_v1/` fixture suite. Do not mutate or reinterpret the existing v0 fixture directory.
2. Add a v1 fixture loader/checker that validates against Build Arena's `project-model/v1` schema and v1 policy semantics.
3. Include v1 fixtures for at least:
   - F1 valid rich snapshot with graph, gate pass, probes, checks, and provenance.
   - F2 decorative/generic project rationale despite syntactically valid v1.
   - F3 code too narrow / wrong component level using v1 graph and contracts.
   - F3 process wrong sequence using v1 contracts/edges.
   - F4 trivial or absent project-model utility.
   - fabricated provenance ref.
   - missing graph edge for a claimed contract.
   - reversed contract direction.
   - self-referential contract.
   - weak or non-independent held-out probe.
   - verification gap mislabeled as success.
   - protected/generated/scorer/verifier/schema ownership leak.
4. Extend the runner so v0 and v1 results remain separately reportable; avoid one collapsed score.
5. Add tests for v1 fixture shape, expected F-label coverage, per-field mismatches, and deterministic pass/fail summaries.

Suggested Arena Calibration implementation prompt:

```text
Add Project Model v1 calibration coverage to Arena Calibration while preserving the existing `fixtures/project_model_v0/` suite. Create `fixtures/project_model_v1/`, a v1 fixture loader/checker that validates Build Arena `project-model/v1` artifacts, and tests for valid rich v1 snapshots plus fabricated provenance, missing/reversed/self contracts, weak probes, gap mislabeled as success, protected/generated ownership leaks, and F1/F2/F3/F4 coverage. Keep v0 and v1 reports separate and advisory. Run `uv run pytest -q` and `uv run python exercise_project_model_fixtures.py --json`.
```

## Readiness implication

The related-repo inspections turn the open readiness items into concrete follow-ups:

- `PMV1-002` remains open: Elenchus Core must learn v1 before it can review Build Arena v1 snapshots directly.
- `PMV1-003` remains open: Arena Calibration must add v1 fixtures before v1 decomposer claims can be calibrated beyond local Build Arena gate tests.

Until those are done, Build Arena v1 work is locally implemented and testable but not cross-repo ready for dry-run hypothesis generation, worktree patch cycles, promotion, or broader live-loop claims.
