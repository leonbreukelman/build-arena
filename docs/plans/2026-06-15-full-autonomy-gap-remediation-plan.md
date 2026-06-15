# Full Autonomy Gap Remediation Implementation Plan

> Opus-authored plan generated from the 2026-06-15 `fmc-mcp` safe-failed production pass.
>
> Primary diagnosis: `docs/specs/2026-06-15-full-autonomy-gap-analysis.md`
> Agent wiki seed: `docs/agent-wiki/index.md`
> Run report: `reports/2026-06-15-fmc-mcp-production-pass-and-proposal-pipeline-report.md`
> Opus plan JSON: `reports/2026-06-15-full-autonomy-implementation-plan-opus.json`

## Review status

- Reviewer: Opus via Claude Code `--model opus`
- Mode: read-only planning pass over repo files and run artifacts
- Verdict: plan accepted as seven TDD-first, independently verifiable phases
- Implementation status: not started in this pass

## Execution budget instruction

Use generous but bounded investigation budgets. Do not starve future implementation agents with tiny max-turn/tool caps. Separate read/investigation budget from mutation/live-call budget: reads/searches/reasoning should have high per-phase ceilings; live calls, promotions, and target mutation must remain tightly capped and logged.

# Implementation Plan — Build Arena toward repo-scale autonomy (post fmc-mcp pass)

Generated for a fresh Hermes execution agent. Source diagnosis: `docs/specs/2026-06-15-full-autonomy-gap-analysis.md`. Run report: `reports/2026-06-15-fmc-mcp-production-pass-and-proposal-pipeline-report.md`. Wiki seed: `docs/agent-wiki/index.md`.

## Framing (do not soften)

The production pass promoted nothing and mutated nothing. That was a *safe failure*, not success. No downstream summary, report, or status doc produced while executing this plan may describe a zero-promotion run as a successful autonomous improvement. The single most autonomy-limiting fact is that **only docs/Markdown candidates are runnable today**; Phase 2 (load-bearing gate for code/component findings) is the keystone that unlocks everything else.

## Boundaries and ground rules

- **Never modify** `scorer/`, `verifier/`, `schema/`, or `arena/generated/`. All code changes land in `arena/` (excluding `arena/generated/`), `tests/`, and `docs/`.
- **TDD is mandatory.** Every phase names the test(s) to add *before* the implementation. Red → green → refactor. Do not write implementation before the failing test exists.
- **Session-sized phases.** Each phase is independently verifiable and committable on its own branch/worktree. Do not start a later phase before the prior phase's verification passes.
- **No silent truncation.** Any cap hit, skip, or budget halt the code takes must emit an explicit event. Surfacing invisibility is itself a deliverable.
- **Live spend stays bounded and authorized.** Only Phase 7 performs live model calls; everything else is exercised with the existing test seams (`_decompose_llm`, `_diff_transport`, `_force_noop_apply` in `arena/repo_goal_loop.py`) or deterministic fixtures.

## Project verification commands (build-arena itself)

- Targeted: `uv run python -m pytest tests/test_<name>.py -q`
- Full suite: `uv run pytest tests -q`
- Lint: `uv run ruff check .`
- Types: `uv run pyright`

Run the full suite + lint + types at the end of every phase before declaring it done.

---

## Phase 1 — Make the silent skip observable + stand up the agent wiki as a first-class artifact

**Goal:** Two foundational, low-risk deliverables that unblock the rest. (a) `_select_promotable` must emit a `CANDIDATE_SKIPPED` event with a reason whenever it filters a positive-score ranked entry (empty verification, no plan candidate, already tried), so a rank-1 540-priority finding can never again vanish without a trace. (b) Convert the agent wiki from prose into a machine-readable, append-only artifact that later phases (registry, gate catalog, failure memory) write into and that prompts read from.

**Root cause being fixed:** `arena/repo_goal_loop.py:394` does `if not tuple(plan_candidate.get('verification_commands', [])): continue` with no event — the invisible override the diagnosis flags. The wiki (`docs/agent-wiki/index.md`) is currently prose only and consumed by nothing.

**Tests to add first:**
- `tests/test_repo_goal_loop.py::test_select_promotable_emits_candidate_skipped_for_empty_verification` — build a ranked bundle where the top positive-score entry has an empty-verification plan candidate and a lower entry is runnable; assert a `CANDIDATE_SKIPPED` event with `payload.reason == 'empty_verification'` and `payload.finding_id` of the top entry is emitted before `CANDIDATE_SELECTED` of the lower one.
- `tests/test_repo_goal_loop.py::test_select_promotable_skips_emit_for_already_tried` — assert a `CANDIDATE_SKIPPED` with `reason == 'already_tried'` is emitted when a higher entry was tried.
- `tests/test_agent_wiki.py::test_wiki_record_append_and_read_roundtrip` (new file) — a new `arena/agent_wiki.py` API can append a typed record (e.g. failure-mode, gate-recipe, registry-view) to a machine-readable store under `docs/agent-wiki/` and read records back filtered by type, deterministically (sorted, stable hash ids), with no secrets.
- `tests/test_agent_wiki.py::test_wiki_rejects_secret_like_payloads` — appending a record containing an obvious secret pattern is refused (honors the wiki anti-pattern rules).

**Implementation:**
- `arena/repo_goal_loop.py`: `_select_promotable` currently returns only the chosen candidate. Refactor it to take the `log`/`cycle` (or return a structured skip list the caller logs) and emit `CANDIDATE_SKIPPED` for each rejected positive-score entry with `reason` in `{empty_verification, no_plan_candidate, already_tried, non_positive_score}`. Keep the selection result identical; only add observability. Update the call site at `arena/repo_goal_loop.py:146`.
- New `arena/agent_wiki.py`: a small, dependency-light module defining a `WikiRecord` dataclass (type, id, created_run_id placeholder, payload dict, content hash) and `append_record` / `read_records(type=...)` over a JSONL store at `docs/agent-wiki/records.jsonl` plus a regenerated human-readable `docs/agent-wiki/index.md` summary. No live timestamps in hashes (determinism); the run id is injected by callers.
- `docs/agent-wiki/index.md`: keep the existing prose sections; add a generated "Records" section pointer. Add `docs/agent-wiki/records.jsonl` (seeded empty or with the production-pass lesson record).

**Verification:**
- `uv run python -m pytest tests/test_repo_goal_loop.py tests/test_agent_wiki.py -q`
- `uv run ruff check . && uv run pyright`
- Manual: grep the new test artifacts to confirm a `CANDIDATE_SKIPPED` line with `empty_verification` appears in a synthetic loop run.

---

## Phase 2 — Load-bearing verification for code/component findings (KEYSTONE)

**Goal:** A `code.component.untested.*` / `needs_code_change` finding must become a selectable candidate carrying a **non-empty load-bearing gate** (the project's own quality gates: ruff + mypy + pytest), instead of inheriting `verification: []` and being silently filtered. After this phase, `code.component.untested.comp-server` is selectable and, when applied in a worktree, is gated by a real test+type+lint gate before it can be considered promotable.

**Root cause being fixed:** `arena/project_intake_scorecard.py:325` emits `[]` for component findings; `arena/proposal_domains.py:221` (`GenericFileDomain`) reuses that empty list; the loop then drops it. The project's quality-gate commands already exist in the snapshot (`iterationReadiness.qualityGates`) and are surfaced by the `verification.quality-gates.present` finding and `arena/proposal_planner.py:_intake_context_block`.

**Tests to add first:**
- `tests/test_proposal_domains.py::test_component_finding_gets_load_bearing_gate` — given a scorecard with a `code.component.untested.*` finding targeting a `.py` file and a `verification.quality-gates.present` finding exposing `ruff/mypy/pytest` commands, the planner produces a candidate whose `verification_commands` is the non-empty project quality-gate set (not `[]`).
- `tests/test_proposal_planner.py::test_quality_gate_commands_threaded_into_domain_context` — assert the planner extracts quality-gate commands from the scorecard and exposes them via `DomainContext.extras['quality_gate_commands']`.
- `tests/test_repo_goal_loop.py::test_code_component_candidate_is_selectable_and_gated` — using the deterministic apply seam, a `needs_code_change` candidate is now selected (no `CANDIDATE_SKIPPED empty_verification` for it) and a `CANDIDATE_VERIFIED` event records a non-empty gate; with no `test_command` configured it logs `PROMOTION_REFUSED reason=behaviour_gate_required` (fail-closed preserved).
- `tests/test_code_quality_domain.py` (extend): regression — a `code.quality.lint.*` finding still routes to `CodeQualityDomain` and keeps its existing load-bearing gate (no precedence regression).

**Implementation:**
- `arena/proposal_planner.py`: in `build_proposal_plan_with_registry`, extract quality-gate commands from the scorecard's `verification.quality-gates.present` finding and pass them into `DomainContext.extras` (e.g. `extras={'quality_gate_commands': (...)}`). Keep determinism (sorted, deduped).
- `arena/proposal_domains.py`: add a `ComponentVerificationDomain` (or extend `GenericFileDomain`) that claims `code.component.untested.*` (and `needs_code_change` single-`.py`-target findings). When the finding's own `verification` is empty, synthesize `verification_commands` from `context.extras['quality_gate_commands']`; if none are available, fall back to a conservative default gate (`uv run ruff check <path>`, the project mypy command, `uv run pytest -q`) — and record that fallback so it is never silent. Register it ahead of `GenericFileDomain` in `default_domain_registry` (`arena/proposal_domains.py:114`). The intent stays "add an observable check (focused test) covering the component"; full test-authoring across multiple files is Phase 6.
- Keep the loop's behaviour-gate guardrail intact: `arena/repo_goal_loop.py:470-483` still requires a configured+passing `test_command` for code promotion. This phase makes the candidate *selectable and verifiable*, not auto-promotable.

**Verification:**
- `uv run python -m pytest tests/test_proposal_domains.py tests/test_proposal_planner.py tests/test_code_quality_domain.py tests/test_repo_goal_loop.py -q`
- `uv run ruff check . && uv run pyright`
- Acceptance check: a synthetic ranked bundle with `code.component.untested.comp-server` at rank 1 now yields a `CANDIDATE_SELECTED` for it (not the rank-2 docs candidate) when no docs finding outranks it.

---

## Phase 3 — Persistent proposal registry + lineage stamping

**Goal:** Introduce a persistent, lineage-stamped proposal store so repeated runs against the same base produce one active proposal plus duplicate/reused records (not N indistinguishable artifacts), and every proposal input/output carries enough git/snapshot lineage to be branch-safe. This combines diagnosis findings `no-proposal-registry` and `no-base-lineage-tags` (one coherent workstream).

**Root cause being fixed:** `arena/proposal_planner.py` is a pure function of (model, scorecard) with no persisted state; `ProposalPlan.to_jsonable` (`arena/proposal_planner.py:62-75`) records only `sourceScorecardId/snapshotId/repoFactsHash` — no base branch, head OID, dirty fingerprint, or content/diff hash. Four pre-existing `ba/fmc-mcp-grounded-proposal-*` branches are invisible to the proposer.

**Tests to add first:**
- `tests/test_proposal_registry.py::test_registry_dedup_marks_repeat_as_duplicate` (new) — running the planner twice against the same base records the second run's identical candidate keys as `duplicate`/`reused`, leaving exactly one `pending` per key.
- `tests/test_proposal_registry.py::test_lineage_stamp_captures_base_git_state` — a planner run stamps each proposal with project id, base branch, base head OID, dirty fingerprint, snapshot id/hash, scorecard id/hash, run id, target path(s), and intent/content hash.
- `tests/test_proposal_registry.py::test_promoted_finding_is_not_reproposed` — marking a proposal `promoted` causes the next planner run to suppress (not re-emit as pending) that finding's key.
- `tests/test_proposal_registry.py::test_lineage_mismatch_blocks_apply` — a proposal generated against base head A is refused with a `LINEAGE_MISMATCH` reason when applied against a target at head B.
- `tests/test_proposal_planner.py::test_plan_carries_base_lineage_fields` — `ProposalPlan.to_jsonable` includes the new lineage fields.

**Implementation:**
- New `arena/proposal_registry.py`: a `ProposalRegistry` over a JSONL store (default under the run/artifacts root, NOT inside the target repo) with records keyed by `(project_id, base_head_oid_or_branch_overlay, target_paths, finding_id/domain, normalized_intent_hash, diff/content_hash)` and lifecycle states `pending | applied_in_worktree | failed_gate | promoted | rejected | duplicate`. Provide `record_pending`, `mark`, `lookup`, and `pending_for_prompt`. Determinism: stable hashing, sorted keys, no live timestamps in keys.
- `arena/proposal_planner.py`: add a lineage capture helper that reads git base state (`git rev-parse HEAD`, current branch, dirty fingerprint via `git status --porcelain` hash) and stamps both the `ProposalPlan` and each `ProposalCandidate`. Add an optional `registry` parameter to `build_proposal_plan_with_registry`; when present, consult it to mark duplicates and suppress promoted keys. Keep the existing pure path working when no registry is passed (backward compatible — preserves current `tests/test_proposal_domains.py` golden output, which asserts `repo_facts_block` byte-for-byte).
- `arena/repo_goal_loop.py`: wire the registry into `_decompose_and_rank`/`_apply_and_verify`/`_promote` so cycle proposals are recorded `pending` → `applied_in_worktree` → `failed_gate`/`promoted`, and add a lineage/freshness check before apply (reuse `arena/project_model_freshness.py` semantics) that emits `LINEAGE_MISMATCH` and skips rather than mutating against a moved base.

**Verification:**
- `uv run python -m pytest tests/test_proposal_registry.py tests/test_proposal_planner.py tests/test_proposal_domains.py -q`
- `uv run ruff check . && uv run pyright`
- Acceptance: a scripted 10-run loop against one fixture base yields 1 pending + 9 duplicate/reused records for each key (mirrors the diagnosis acceptance signal), asserted in a test.

---

## Phase 4 — Feed registry + wiki context into the live proposer prompt; deterministic prefix-doubling normalization

**Goal:** The live-proposer prompt must show the model (a) existing pending/unmerged proposals from the registry so it does not regenerate invisible branch work, and (b) known failure modes / repo conventions from the wiki so it does not repeat a recorded error. Add a deterministic normalization that collapses repeated repo-root prefixes (`src/src/` → `src/`) before the link gate fails — the exact class of error that ended the production pass.

**Root cause being fixed:** `arena/runners/diff_proposer.py:194-223` (`_diff_prompt`) is seeded only from current file contents + repo facts — no prior-proposal context, no failure memory. `_unique_suffix_match` (`arena/runners/diff_proposer.py:415-420`) only repairs unique-suffix dupes, so `src/src/fmc_mcp/config.py` (a doubled *prefix*) is unrepairable and hard-fails at `arena/runners/diff_proposer.py:376-378`.

**Tests to add first:**
- `tests/test_diff_proposer.py::test_repair_collapses_doubled_repo_root_prefix` — a Markdown patch linking `src/src/fmc_mcp/config.py` is deterministically repaired to `src/fmc_mcp/config.py` when `src/fmc_mcp/config.py` exists, and the gate then passes.
- `tests/test_diff_proposer.py::test_prefix_collapse_does_not_touch_legitimate_paths` — a path that genuinely contains a repeated segment but resolves as-is is left unchanged (no false rewrite).
- `tests/test_diff_proposer.py::test_prompt_includes_pending_proposals_and_failure_notes` — given injected registry pending records and wiki failure notes, `_diff_prompt` (or its request) includes a "Known pending proposals" block and a "Known failure modes" block.
- `tests/test_proposal_planner.py::test_repo_facts_block_lists_canonical_paths` — assert the facts block names canonical repo-relative paths so prefix-doubling is pre-empted (guards the wiki "repo conventions" requirement).

**Implementation:**
- `arena/runners/diff_proposer.py`: extend `_repair_markdown_references`/add a helper that, before declaring a missing link, attempts deterministic collapses of duplicated leading path segments (`a/a/...` → `a/...`) and re-resolves against `_existing_repo_paths`. Keep it conservative: only rewrite when the collapsed form uniquely matches an existing repo path.
- `arena/runners/diff_proposer.py`: thread optional `pending_proposals` and `failure_notes` (and repo-convention facts) into `DiffProposalRequest` and render them as explicit prompt blocks in `_diff_prompt`. Source them from `arena/proposal_registry.py` (Phase 3) and `arena/agent_wiki.py` (Phase 1).
- `arena/repo_goal_loop.py` `_live_diff_apply` (`arena/repo_goal_loop.py:524-552`): pass the registry's pending records and the wiki's failure notes into the runner so live cycles are seeded with them.

**Verification:**
- `uv run python -m pytest tests/test_diff_proposer.py tests/test_proposal_planner.py -q`
- `uv run ruff check . && uv run pyright`
- Acceptance: a unit test reproduces the production-pass `src/src/...` input and shows a gate-passing repaired diff instead of a `RunnerError`.

---

## Phase 5 — Bounded repair/retry loop for live gate failures + separated read/write budgets

**Goal:** A single recoverable model error must no longer end a cycle. On a gate rejection, feed the specific gate error back to the model for a bounded correction attempt within a per-cycle repair budget, recorded as a `CANDIDATE_REPAIR_ATTEMPT` event. Separately, encode the execution-budget guidance into config: distinct read/investigation vs write/mutation budgets, a nonzero per-cycle repair budget, and validation that `max_cycles` can exceed the viable-candidate count.

**Root cause being fixed:** `DiffProposerRunner.apply` (`arena/runners/diff_proposer.py:144-191`) is single-shot; on link-gate rejection it reverses the diff and raises with no retry. The production run also conflated budgets with `--live-max-calls 2 --max-cycles 1`, so one bad patch ended the whole run.

**Tests to add first:**
- `tests/test_diff_proposer.py::test_apply_retries_with_gate_error_feedback` — a transport that returns a bad diff first and a good diff second produces a gate-passing patch within a repair budget of 1, and records the gate error fed back in between.
- `tests/test_diff_proposer.py::test_apply_repair_budget_exhausted_fails_cleanly` — when the repair budget is exhausted, it fails with a structured `RunnerError` (no infinite loop) and the worktree is reverted.
- `tests/test_repo_goal_loop.py::test_cycle_continues_to_next_candidate_after_repairable_failure` — with `max_cycles` > viable candidates and the first candidate failing its gate, the loop proceeds to the next viable candidate instead of halting after one cycle.
- `tests/test_repo_goal_loop.py::test_config_separates_read_and_mutation_budgets` — new config fields (e.g. `live_repair_budget_per_cycle`, distinct mutation cap) validate correctly and reject inert/over-budget combinations, consistent with `_validate_live_config` (`arena/repo_goal_loop.py:210-256`).

**Implementation:**
- `arena/runners/diff_proposer.py`: add a bounded repair loop in `apply` — on patch-gate or Markdown-gate rejection, construct a follow-up request that includes the precise gate error and the offending paths, call the transport again up to `repair_budget` times, and only raise after the budget is spent. Emit/record repair attempts via a provenance field and a structured result the loop can log.
- `arena/repo_goal_loop.py`: add `live_repair_budget_per_cycle: int = 1` (and any explicit mutation-budget field) to `RepoGoalLoopConfig`; thread it into `_live_diff_apply`. Emit `CANDIDATE_REPAIR_ATTEMPT` and `CANDIDATE_REPAIRED` events. Update `_planned_live_calls` / `_validate_live_config` so the repair budget is counted against `live_max_calls` and never silently exceeded. Add a `CYCLE_BUDGET` event documenting the read-vs-write split.
- CLI (`arena/repo_goal_loop.py:728-775`): expose the new flags (`--live-repair-budget`, etc.).

**Verification:**
- `uv run python -m pytest tests/test_diff_proposer.py tests/test_repo_goal_loop.py -q`
- `uv run ruff check . && uv run pyright`
- Acceptance: a seam-driven loop where candidate 1 fails and candidate 2 succeeds promotes (in promotion mode) or records the second candidate, with repair events present and no premature `BUDGET_HALT`.

---

## Phase 6 — Multi-file / model-level proposal contract

**Goal:** Stop silently dropping multi-file component findings (`comp-entrypoints`: `__init__.py` + `__main__.py`) and model-level findings (`architecture.open-questions-or-gaps`, `verification.quality-gates.present`). Extend the proposal contract to carry multiple target paths and a model-level (non-file) intent shape, each with an appropriate gate.

**Root cause being fixed:** `_single_target_path` (`arena/proposal_domains.py:234-247`) returns `None` unless exactly one non-`iterationReadiness` path remains; `ProposalCandidateDraft` is single-`target_path`; `first_candidate` drops anything else, surfacing as `no_single_file_target` skips.

**Tests to add first:**
- `tests/test_proposal_domains.py::test_multi_file_component_produces_candidate` — `code.component.untested.comp-entrypoints` (two `.py` files) yields a valid multi-file candidate with a load-bearing gate instead of a skip.
- `tests/test_proposal_domains.py::test_model_level_finding_becomes_backlog_task_candidate` — `architecture.open-questions-or-gaps` produces a model-level candidate (e.g. a backlog/verification-task intent) with a gate appropriate to its shape, not a `no_single_file_target` skip.
- `tests/test_proposal_planner.py::test_plan_supports_multi_target_candidates` — `ProposalCandidate`/`ProposalPlan` serialize multiple target paths without breaking single-target consumers.
- `tests/test_repo_goal_loop.py::test_multi_file_candidate_boundary_and_promote_staging` — boundary check (`arena/repo_goal_loop.py:160`) and promotion staging (`arena/repo_goal_loop.py:693-709`) handle a multi-path target set (stage exactly the approved set; refuse anything outside it).

**Implementation:**
- `arena/proposal_domains.py`: add `target_paths: tuple[str, ...]` to `ProposalCandidateDraft` (keep `target_path` as a derived single-value for back-compat where exactly one). Add multi-target support to the component domain and a model-level intent path for `iterationReadiness.*`-evidence findings.
- `arena/proposal_planner.py`: extend `ProposalCandidate`/`ProposalPlan` to carry multiple targets; keep `target_path` populated for single-file candidates so `candidate_to_hypothesis` and existing runners keep working. Note: `Hypothesis` lives in `arena/generated/models.py` (protected) — do not edit it; instead keep single-file hypotheses for the diff runner and gate multi-file work through the loop's own apply path.
- `arena/repo_goal_loop.py`: generalize boundary check and promotion staging to operate over the candidate's full approved target set, preserving the "stage only approved, re-check boundary before ff-only" guarantee.

**Verification:**
- `uv run python -m pytest tests/test_proposal_domains.py tests/test_proposal_planner.py tests/test_repo_goal_loop.py -q`
- `uv run ruff check . && uv run pyright`
- Acceptance: `comp-entrypoints` no longer appears in `skippedFindings`; it appears as a multi-file candidate with a non-empty gate.

---

## Phase 7 — First real closed-loop proof (promote → re-decompose → re-intake) + budget encoding

**Goal:** Produce the first recorded live run where one candidate is promoted, the loop then re-decomposes and re-intakes (new snapshot id + fresh intake) before selecting the next candidate. This is the goal's core claim; until a recorded run exists it is code, not capability.

**Root cause being fixed:** `--max-cycles 1` plus the only candidate failing meant `BUDGET_HALT` after one cycle; the promotion → `tried_finding_ids.discard` → re-decompose path (`arena/repo_goal_loop.py:188-194`) was never reached.

**Tests to add first (deterministic, seam-driven — no live spend in CI):**
- `tests/test_repo_goal_loop.py::test_closed_loop_promotes_then_redecomposes` — using `_diff_transport`/deterministic apply seams and a configured passing `test_command`, a run with `max_cycles` > viable candidates promotes one candidate, then a second `DECOMPOSITION_COMPLETED` with a *new* snapshot id and a fresh intake precede the next `CANDIDATE_SELECTED`. Assert the event ordering exactly.
- `tests/test_repo_goal_loop.py::test_promoted_candidate_recorded_in_registry_as_promoted` — the promoted finding is marked `promoted` in the registry (Phase 3) and is not re-selected in the next cycle.
- `tests/test_repo_goal_loop.py::test_max_cycles_must_exceed_viable_candidate_count_guidance` — config/validation surfaces (warns/records) when `max_cycles` ≤ viable-candidate count so a single gate failure cannot silently end the run.

**Implementation:**
- `arena/repo_goal_loop.py`: ensure the promote path emits the full evidence sequence (`PROMOTED` → `BASELINE_ADVANCED` → next-cycle `DECOMPOSITION_COMPLETED` with new snapshot id → fresh `scorecard` → `CANDIDATE_SELECTED`). Add a `RUN_COMPLETED` summary that records `promotions`, `cyclesRun`, and the re-decompose snapshot ids. Record the closed-loop evidence into the agent wiki (Phase 1) as a `closed_loop_proof` record.
- After deterministic tests are green, the executing agent (with explicit operator authorization and the bounded live budgets below) runs ONE live closed-loop pass against a safe target (the same `fmc-mcp` fixture lineage), capturing `loop-events.jsonl` under `reports/` and a status doc. The status doc must state plainly whether a promotion occurred; do not claim success without a recorded `PROMOTED` + re-decompose.

**Verification:**
- `uv run python -m pytest tests/test_repo_goal_loop.py -q`
- `uv run pytest tests -q && uv run ruff check . && uv run pyright` (full gate)
- Acceptance: a recorded `loop-events.jsonl` (deterministic test and, when authorized, one live run) shows `PROMOTED` followed by a second `DECOMPOSITION_COMPLETED` (new snapshot id) and a fresh intake before the next `CANDIDATE_SELECTED`.

---

## Cross-cutting: execution budget encoding (applies to every phase and to the executing agent itself)

- Separate **read/investigation budget** (generous — never cap reading, searching, or reasoning so low an agent cannot finish investigating) from **write/mutation/live-call budget** (strict — bounded calls, one promote per cycle).
- Use **high per-phase ceilings**, not tiny global max-turn/max-tool caps. Bound by **outcome/divergence** (consecutive-failure streak via `max_consecutive_failures`, divergence halt) and **total cost/mutation/divergence caps**, not by artificially small turn counts.
- Set the loop's `max_cycles` strictly **greater than** the number of viable candidates so one gate failure does not end the run.
- Give the live proposer a **small but nonzero** per-cycle repair budget (Phase 5).
- Make **every** truncation/cap-hit an explicit logged event so silent under-investigation is visible.

## Sequencing rationale

Phase 1 is foundational (observability + wiki substrate that 3/4 write into). Phase 2 is the keystone (unlocks non-docs candidates). Phases 3–4 are the registry/lineage/context workstream. Phase 5 adds recovery + budget separation. Phase 6 broadens coverage. Phase 7 proves the loop. Each phase is independently committable and verifiable; do not begin a phase until the prior phase's full gate passes.
