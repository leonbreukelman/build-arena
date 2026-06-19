# Proposer architecture-fitness extension status — 2026-06-18

Branch/worktree: `ba/proposer-architecture-fitness` in the local Build Arena feature worktree.

Scope: extend the proposal component beyond single-file fixes by adding route accounting, structured evidence/graph plumbing, deterministic architecture-fitness candidates/gate, advisory backlog candidates/gate, and nested Markdown link semantics.

## P0 baseline

Artifacts: `reports/2026-06-18-proposer-architecture-fitness/p0-baseline/`.

Calibration baseline:
- Snapshot/gate/intake/planner/ranker generated offline with fixture mode.
- Proposal plan determinism: `de24e9c66090c53c3b11dce9817c66f9ae7b3412fbae3ecef7ddae84f5dcabd4` for both builds.
- Ranked proposals determinism: `f57225a31b1af83b04fdecc72f02c9ba3857affaf2c3c9de00ddeae7a7227f54` for both builds.
- Current routes include `architecture.open-questions-or-gaps -> no_single_file_target` and `verification.quality-gates.present -> no_single_file_target`.

fmc-mcp baseline:
- Snapshot/gate/intake/planner/ranker generated offline with fixture mode.
- Proposal plan determinism: `c3bae3b67ce346ff406685300fd570b8796c8090bbdb4e0aa2c8a59ce27f8fef` for both builds.
- Ranked proposals determinism: `275a91b23228a54b3701d7223f20c706056f83962d40848bb1f1a23d23f756f2` for both builds.
- Current routes include `architecture.open-questions-or-gaps -> no_single_file_target` and `verification.quality-gates.present -> no_single_file_target`.

P0 harness added:
- `tests/test_proposal_planner.py::test_proposal_plan_and_ranker_are_deterministic_on_parity_fixture`.
- Verified with `uv run pytest tests/test_proposal_planner.py::test_proposal_plan_and_ranker_are_deterministic_on_parity_fixture -q` -> `1 passed`.

## Phase status

- P0: complete; baseline captured, determinism harness added, full pytest/ruff/pyright green.
- Gate A: complete; Opus `ACCEPT_WITH_CHANGES` in `reports/2026-06-18-proposer-architecture-fitness/gate-a-opus-review.json`.
- P1: complete; nested repo-root-looking Markdown links from nested docs now resolve to root targets without weakening missing-link or escape handling.
- P2: complete; planner and ranker now receive the same DomainContext advisory evidence and freshly rebuilt graph slice.
- P3: complete; proposal plans now emit `findingDispositions`, quality-gate findings route to `consumed_as_context`, and the v0 schema pins the disposition vocabulary.
- Gate B: complete; Opus `ACCEPT_WITH_CHANGES` in `reports/2026-06-18-proposer-architecture-fitness/gate-b-opus-review.json`.
- P4: complete; architecture findings with graph-evident import cycles now produce inert JSON fitness-contract candidates, the gate rejects fabricated/vacuous/duplicate/digest-mismatched contracts, accepted failing contracts exit nonzero, and repo_goal_loop skips architecture-fitness guardrails as non-promotable.
- P5: complete; advisory-only findings with no mechanical graph signal now route to grounded backlog candidates, and `arena.backlog_gate` rejects boilerplate/no-op and dead-link backlog entries.
- Final review/report: complete; Opus Gate C returned `ACCEPT` with no blockers/no patch-before-final criticism. Raw review/report artifacts remain local-only under `reports/2026-06-18-proposer-architecture-fitness/` and are intentionally not part of the public PR.

P1 verification:
- RED: `uv run pytest tests/test_markdown_links.py::test_nested_markdown_links_can_resolve_repo_root_targets tests/test_markdown_links.py::test_repo_root_fallback_does_not_mask_dead_nested_links_or_escape_attempts -q` failed on the nested root-link assertion before the fix.
- GREEN: `uv run pytest tests/test_markdown_links.py -q` -> `9 passed`.
- Phase gate: `uv run pytest tests -q && uv run ruff check . && uv run pyright` -> all tests passed, ruff clean, pyright 0 errors.

P2 verification:
- RED: `uv run pytest tests/test_proposal_planner.py::test_domain_context_plumbs_advisory_evidence_and_fresh_graph_edges tests/test_proposal_ranker.py::test_ranker_gets_same_domain_context_evidence_as_planner -q` failed before DomainContext exposed `graph_slice`, `open_questions`, and `verification_gaps`.
- GREEN: the same command -> `2 passed`.
- Phase gate: `uv run pytest tests -q && uv run ruff check . && uv run pyright` -> all tests passed, ruff clean, pyright 0 errors.

P3 verification:
- RED: `uv run pytest tests/test_proposal_planner.py::test_proposal_plan_builds_grounded_top_n_without_copying_recommended_action tests/test_proposal_plan_schema.py -q` failed before `findingDispositions` existed and before `verification.quality-gates.present` routed as `consumed_as_context`.
- GREEN: `uv run pytest tests/test_proposal_domains.py tests/test_proposal_planner.py tests/test_proposal_ranker.py tests/test_proposal_plan_schema.py -q` -> `43 passed`.
- Phase gate: `uv run pytest tests -q && uv run ruff check . && uv run pyright` -> all tests passed, ruff clean, pyright 0 errors.

P4 verification:
- RED: `uv run pytest tests/test_architecture_fitness.py -q` failed before `arena.architecture_fitness` existed.
- GREEN: `uv run pytest tests/test_architecture_fitness.py tests/test_proposal_domains.py::test_proposal_domains_are_registered_in_fixed_order tests/test_repo_goal_loop.py::test_select_promotable_skips_architecture_fitness_guardrails -q` -> `6 passed`.
- Phase gate: `uv run pytest tests -q && uv run ruff check . && uv run pyright` -> all tests passed, ruff clean, pyright 0 errors.

P5 verification:
- RED: `uv run pytest tests/test_advisory_backlog.py -q` failed before `arena.advisory_backlog` and `arena.backlog_gate` existed.
- GREEN: `uv run pytest tests/test_advisory_backlog.py -q` -> `2 passed`.
- Phase gate: `uv run pytest tests -q && uv run ruff check . && uv run pyright` -> all tests passed, ruff clean, pyright 0 errors.

Final verification/review:
- `uv run pytest tests -q -rA` -> 517 passed, 11 skipped (default onboarding acceptance skips without `ARENA_CALIBRATION_PATH`).
- `ARENA_CALIBRATION_PATH=<arena-calibration checkout> uv run pytest tests/test_onboarding_acceptance.py -q` -> `........... [100%]`.
- `uv run ruff check .` -> all checks passed.
- `uv run pyright` -> 0 errors, 0 warnings.
- Opus Gate C review: local-only artifact under `reports/2026-06-18-proposer-architecture-fitness/final-review/gate-c-opus-review.json`, verdict `ACCEPT`.

## Gate A corrections to carry into coding

- Add `findingDispositions` to the v0 schema explicitly; do not rely on permissive extra fields.
- Wire the same DomainContext evidence/graph into planner and ranker so their routes cannot diverge.
- Build graph-binding decisions from freshly rebuilt project graph ground truth, not cached snapshot graph. Snapshot evidence is only advisory text.
- Make dispositions conservation explicit: each finding maps to exactly one disposition; skipped/non-candidate rows derive from dispositions.
- Keep architecture fitness contracts as inert data files plus the Build Arena gate runner, not pytest-collected tests in the target repo.
- Advisory backlog gate must re-derive expected item IDs/text from an authoritative expected-input file or snapshot at gate time; it must reject boilerplate/no-op output.

## Guardrails

- Working in a clean branch worktree to avoid the dirty original main checkout.
- No writes under `scorer/`, `verifier/`, `schema/`, `.arena/scorer.lock.toml`, or `arena/generated/`.
- No live model/network producer path planned; Opus reviews are external review gates only.
