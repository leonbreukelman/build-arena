# Build Arena — Onboarding Cycle: Implementation Plan

## Objective

Give Build Arena one **reliable, deterministic, minimal** way to decompose a target
repo into a Project Model from which the existing intake scorecard ranks
requirements and improvements. Replace the drifting decomposer sprawl (3
decomposers, 3 schema versions, ~345 KB, never closed a loop on a real repo) with
a single frozen contract + a single producer that makes the acceptance test green.

## Definition of done (the only one)

1. `tests/test_onboarding_acceptance.py` is green against an `arena-calibration` checkout.
2. `arena/repo_goal_loop.py` consumes the new model and completes at least one
   dry-run cycle on `arena-calibration` producing a deterministic ranked finding list.
3. `make generated` (if schema-touching), `ruff`, `pyright`, `pytest` are green.
4. Nothing else is added. No new schema version, no new artifact type, no AI path.

If the agent is doing anything not traceable to one of those four lines, it has drifted.

## Non-negotiable constraints

- **Freeze the ruler first.** `docs/schemas/project-model.frozen-v1.json` and the
  acceptance test are inputs, not work products. Do not edit them to pass. Tightening
  is allowed; loosening requires an operator decision.
- **Deterministic only.** The frozen model is built from filesystem + git truth.
  No timestamps, no RNG, no set-iteration-order leakage, no network, no LLM in the
  producer. Same HEAD in → byte-identical model out.
- **Anti-fabrication.** Read the path before asserting a file/symbol exists. Every
  `owned_node_id`, `componentId`, gap anchor must reference a real node. The
  coverage-closure invariant makes a dropped or invented file a test failure.
- **Boundaries.** Never modify or even import `arena/decomposer.py`,
  `arena/project_decomposer_ai.py`, `arena/project_meta_decomposer.py`. Never touch
  `scorer/`, `verifier/`, `schema/`, or `.arena/scorer.lock.toml`.
- **One new module.** All onboarding logic goes in `arena/onboard.py` exposing
  `decompose_project(project_path: str) -> dict`. No new package, no helper sprawl.

## Architecture decision (recommended; operator may override)

- The frozen model is the **deterministic spine the scorecard already consumes**:
  `projectGraph.nodes/edges`, `snapshot.{components, observable_checks,
  verification_gaps, unclassified_node_ids}`, `iterationReadiness.{componentProfiles,
  qualityGates, openQuestions}`. Nothing the scorecard does not read is in it.
- **AI/semantic enrichment is deferred and lives outside this object.** Semantic
  components like "provider boundary" or "runner discrimination matrix" require
  interpretation and were the entry point for the original drift. They are NOT in
  the frozen contract and NOT in the acceptance test. If wanted later, they go in a
  separate sidecar that references model node/component ids — never inside the
  frozen model (`additionalProperties:false` enforces this).
- **riskLevel is a transparent rule, not a model output:**
  - `high` — component owns ≥1 `.py` node and has zero `check_ids`.
  - `low` — component is covered by ≥1 check, OR is non-executable (docs/config/fixtures).
  - `medium` — everything else.
- **Schema format:** JSON Schema (matches `docs/schemas/`, portable across tools).
  Alternative if the operator prefers the LinkML pipeline: author the same shape in
  `schema/` and compile via `make generated`. Decide before Phase 0; do not do both.

## Phases

Each phase ends green (`pytest -q`, `ruff`, `pyright`) and is a separate commit.

**Phase 0 — Freeze the ruler.**
Place the schema at `docs/schemas/project-model.frozen-v1.json` and the test at
`tests/test_onboarding_acceptance.py`. Run it; confirm it is RED for the right
reason (no `arena/onboard.py`). **Opus checkpoint A** (mandatory): Opus verifies the
ruler discriminates — it must FAIL an empty/degenerate/fabricated model and PASS a
hand-built correct one. A ruler that passes garbage is worse than none.

**Phase 1 — Graph + coverage closure.**
Walk git-tracked files (`git ls-files`) — not the working tree, so ignored/untracked
junk never enters the model. Emit file and directory nodes (sorted, id = `node:`+path).
Group files into structural components by top-level surface (`fixtures/`, `arena/`,
`tests/`, `docs/`, `scripts/`, config files, harness scripts), assign `kind`. Put any
ungrouped file in `unclassified_node_ids`. Compute the content-addressed `id` and
`provenance.git.headOid`. Target: `test_*_accounted_for`, `_relative_posix`,
`_required_surfaces_owned`, `_known_fixtures_present`, `_provenance_*`, `_deterministic`,
`_validates_against_schema` green.

**Phase 2 — Checks, quality gates, risk.**
Discover `observable_checks` from `tests/` files and map them to components by
path/import heuristics. Discover `qualityGates` from `pyproject.toml`
(`[tool.ruff]`, `[tool.pytest.ini_options]`, pyright config) and `Makefile`/scripts —
emit runnable commands (`pytest`, `ruff check`, `pyright`). Populate
`componentProfiles` with the riskLevel rule above. Target: `_quality_gates_discovered`
green; component findings now have real risk.

**Phase 3 — Verification gaps (incl. the known gap).**
Derive `verification_gaps` mechanically. The required one: read the F3 fixture's
manifest under `fixtures/F3_bad_passes_tests/` and emit kind
`patch_generalization_axis_missing` anchored to `F3_bad_passes_tests`. **Confirm the
manifest field name/format against the real fixture before coding the parser** — if it
differs from the assumption, that is an Opus-trigger (fixture reality vs plan), not a
guess. Also emit `component_untested` / `no_quality_gates` gaps where applicable.
Target: `_known_patch_generalization_gap_is_recovered` green.

**Phase 4 — Edges (optional in first cut).**
Resolve in-repo Python imports to node ids → `imports` edges. If extraction can't be
made deterministic cheaply, ship `edges: []` (the schema allows it) and defer. Do not
block the loop on this.

**Phase 5 — Close the loop.**
Repoint `arena/repo_goal_loop.py::_decompose_and_rank`: replace the
`build_project_model_snapshot(...)` (AI decomposer) call with
`arena.onboard.decompose_project(...)`, write `project-model.frozen-v1.json`, and feed
that path to `build_project_intake_scorecard`. Confirm the scorecard reads the same
field paths (it does: `snapshot.components/observable_checks/verification_gaps`,
`projectGraph.nodes`, `iterationReadiness.*`). Run a bounded dry-run loop on
arena-calibration. Target: `_model_drives_deterministic_ranking` green + loop dry-run
completes. **Opus checkpoint B** (mandatory): Opus verifies the full implementation
against the acceptance test, hunts determinism traps and fabrication, confirms no
boundary/quarantine violation.

**Phase 6 — Quarantine + lock.**
Move the three old decomposers and their exclusive dependents (encyclopedia, graph,
meta, freshness, iteration_readiness, v0/v1 model modules, project_model_cli) to a
`deferred/` directory or a `deferred-decomposers` branch — do not delete; they may hold
ideas. Remove their wiring. Add the AGENTS.md boundary rule (below).

## AGENTS.md boundary rule to add (the missing lock)

> **Onboarding-scope rule.** The Project Model is defined solely by
> `docs/schemas/project-model.frozen-v1.json`. Introducing a new project-model schema
> version, a new decomposer module/variant, or a new model artifact type requires an
> explicit operator action (same class as bumping `scorer.lock.toml`). Autonomous or
> agent edits must not expand the model surface. The producer is `arena/onboard.py`
> and must remain deterministic (filesystem + git truth, no LLM, no network).

You protect `scorer/`/`verifier/`/`schema/` from mutation but have no rule against
onboarding-scope expansion — the exact axis that ran away. This closes it.

## Anticipated issues and mitigations

- **Determinism traps:** dict/set ordering, `os.walk` order, absolute paths, mtimes,
  hash-seed-dependent ids. → Sort every collection by a stable key; use `git ls-files`;
  store relative POSIX paths; never put time in the model; the `_deterministic` and
  `_id_is_content_addressed` tests catch regressions.
- **Reusing the old decomposers:** highest-probability drift. → Boundary rule forbids
  import; Opus checkpoint B greps for `decomposer` imports in `arena/onboard.py`.
- **Docs-only regression / path fabrication:** the scorecard silently reroutes
  extension-less component surfaces to `<path>/index.md`. → Only emit components whose
  owned files have real suffixes for code/test surfaces; coverage-closure test forbids
  inventing node ids.
- **Scorecard field-name mismatch:** the model must satisfy the exact keys the
  scorecard reads (see list in Phase 5). → The `_model_drives_deterministic_ranking`
  test is the contract check; do not rename fields.
- **Unknown F3 manifest format:** stated as manifest-derived but the field is
  unconfirmed. → Phase 3 reads the real manifest first; mismatch escalates to Opus.
- **riskLevel ambiguity for mixed components:** → fixed rule above; tune only by
  operator decision.

## Testing strategy

- Unit tests per phase in `tests/` for each extractor (graph, ownership, checks,
  gates, gaps, risk) using small temp-dir repos — fast, no fixture dependency.
- The acceptance test is the integration gate, run against `ARENA_CALIBRATION_PATH`.
- A dedicated determinism unit test on a temp repo (decompose twice, assert identical)
  so determinism is caught without the full fixture.
- CI: `ruff`, `pyright`, `pytest` green every phase; never commit a red phase.
