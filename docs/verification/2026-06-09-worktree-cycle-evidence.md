# Build Arena BA-M3-05 Worktree Cycle Evidence

Date: 2026-06-10T06:06:01Z
Kanban card: `t_d1682f0d` — BA-M3-05 Phase 3: Wire worktree-only cycle and mechanical evidence
Branch: `ba/m3-worktree-cycle-evidence`

## Scope completed

- Added advisory ablation behavior in `verifier/config.py` and `verifier/engine.py`.
- Added `CandidatePackager` in `arena/worktrees.py` for owner-gated `arena/candidate/<cycle_id>` branches.
- Updated `arena/loop.py` for candidate-only packaging, goal-config-aware boundary checks, evidence emission, halt evidence for budget/divergence, and ledger adapter compatibility.
- Added `arena/evidence.py` for mechanical `cycle-evidence/v1` and `halt-evidence/v1` JSON reports.
- Added tests:
  - `tests/test_verifier_advisory.py`
  - `tests/test_candidate_packager.py`
  - `tests/test_worktree_cycle_evidence.py`

## Behavior implemented

### Advisory ablation

- `VerifierConfig.ablation_advisory` defaults to `False`.
- Strict/default verifier behavior still requires Ollama and rejects non-load-bearing ablation.
- Advisory config permits non-Ollama ablation runners and still emits `AblationResult`.
- Advisory mode skips only `ABLATION_REASONING_NOT_LOAD_BEARING`; test failure, pinned metric regression, and nonpositive score still reject.

### Candidate-only packaging

- `CandidatePackager` implements the existing promoter-shaped seam but sets `candidate_only = True`.
- It commits the cycle worktree when needed and creates/updates `refs/heads/arena/candidate/<cycle_id>` using `git update-ref`.
- It never merges into or advances the main checkout.
- Loop emits `CANDIDATE_PACKAGED` instead of `PROMOTED`/`BASELINE_ADVANCED` for candidate-only packaging.
- `GitPromoter` remains available and unchanged for calibration promotion tests.

### Mechanical evidence

`CycleEvidenceWriter` writes:

- `cycle-evidence/v1` with worktree root, worktree record, budget caps/usage, score before/after, verdict, candidate branch/OID, patch numstat, patch hash, and canonical events with payload hashes.
- `halt-evidence/v1` for budget and divergence halts with halt record, budget config/usage, and event sequence.

Evidence is written before worktree teardown so patch numstat and patch hashes are mechanically read from the live worktree/artifacts.

### Boundary and goal config handling

- The loop uses `.arena/goal.toml` boundary/read-only rules when the file exists.
- If `.arena/goal.toml` is absent, the loop emits `GOAL_CONFIG_FALLBACK` and uses default protected-path rules for legacy/fake worktrees.
- If `.arena/goal.toml` exists but is malformed, `GoalConfigError` propagates fail-closed; it does not fall back.

### Ledger interface fix

- The loop now prefers `record_failure(...)` and `record_success(...)`.
- It falls back to the legacy `record(...)` shape for old fake ledgers in existing coverage tests.

## TDD evidence

Initial RED run failed as expected with missing pieces:

- `CandidatePackager` missing from `arena.worktrees`.
- `arena.evidence` missing.
- `VerifierConfig(ablation_advisory=...)` missing.
- `LoopContext(evidence_writer=...)` missing.

Implementation followed the RED run. Later Fable-required safety tests were added for missing vs malformed goal config handling.

## Verification completed

- `uv run pytest tests/test_verifier_advisory.py tests/test_candidate_packager.py tests/test_worktree_cycle_evidence.py tests/test_worktrees.py tests/test_loop_phase4.py tests/test_ablation.py tests/test_verifier_gates.py tests/test_failure_ledger.py tests/test_diff_proposer.py tests/test_target_picker.py tests/test_coverage_closure.py::test_loop_discards_boundary_failed_ledger_apply_and_structural_cases tests/test_coverage_closure.py::test_loop_promotes_then_continues_until_budget_and_helper_edges -q` — passed.
- `uv run pytest tests -q` — passed.
- `uv run ruff check .` — passed.
- `uv run pyright` — passed: `0 errors, 0 warnings`.
- `git diff --check` — passed.
- New-file whitespace checks for `arena/evidence.py`, `tests/test_verifier_advisory.py`, `tests/test_candidate_packager.py`, and `tests/test_worktree_cycle_evidence.py` — passed.

## Fable review

Initial verdict: `ACCEPT_WITH_CHANGES`.

Required changes:

1. Distinguish missing vs malformed goal config. Fall back only when missing; fail closed on malformed; emit fallback event.
2. Confirm/pin that candidate refs survive `WorktreeManager.teardown`.

Both were completed and re-verified.

### Initial review transcript

VERDICT: ACCEPT_WITH_CHANGES

**critical_blockers**

None that prevent merge — but one fail-open path needs to be fixed before this card is called done, because it sits on the safety-critical boundary-enforcement line:

1. **`_boundary_violation_for_worktree` fails open on malformed goal config.** It catches `GoalConfigError` and silently falls back to default boundary rules. That conflates two very different cases: "no `.arena/goal.toml` present" (legitimate legacy/fake-worktree fallback) and "goal.toml exists but is invalid" (misconfiguration that should halt, not degrade). In a real-cycle repo, a typo in goal.toml would silently swap in whatever the default rules allow, and nothing in the event log would say so. This project's whole posture (fail-closed diff proposer, strict gates) argues for: fall back only when the config file is absent; raise or HALT on a parse/validation error, and at minimum emit an event when the fallback path is taken.

**required_changes_before_completion**

- Fix the fail-open above: distinguish missing vs. malformed goal config, fail closed (or halt) on malformed, and emit an event (e.g. `GOAL_CONFIG_FALLBACK`) whenever default rules are used so evidence stays traceable. Add a test for the malformed-config case — current tests apparently cover only present-and-valid and absent.
- Confirm (and pin with a test if not already) that the candidate ref survives `WorktreeManager.teardown` — i.e., `refs/heads/arena/candidate/<cycle_id>` keeps the commit reachable after the `arena/cycle/<id>` branch and worktree are deleted. If `test_candidate_packager.py` already proves this, no change needed; if it only checks the ref exists pre-teardown, extend it.

**guidance_as_leon_representative**

The core of the card is sound. Candidate-only semantics are right: `active_baseline`/`active_score` untouched, no `PROMOTED`/`BASELINE_ADVANCED` emission, `CANDIDATE_PACKAGED` carries the verdict and candidate record, `GitPromoter` calibration path untouched. The advisory-ablation change is correctly scoped — `AblationResult` still emitted, only the non-load-bearing rejection is skipped, and the ollama-only constraint relaxes only when advisory is explicitly set, so strict calibration defaults are intact. Ledger adapters preferring `record_failure`/`record_success` with a legacy `record(...)` fallback is the right compatibility shape, and recording success on promote closes a gap that existed before.

Three non-blocking observations to carry forward (file as notes, don't expand this card):

- In candidate-only mode, candidates still increment `promotions_total`, `budget.record_promotion()`, and count toward `stop_after_promotions`. That's defensible as a budget bound on real cycles, but it means "promotions" now means two different things depending on promoter. Rename or document before it confuses evidence consumers.
- Evidence writing happens before `_cleanup`; if the evidence writer throws, the worktree leaks. A try/finally around cleanup would be cheap insurance.
- The `LoopState.HALT` return path and any unexpected exception write no halt evidence — only `BudgetBreach`/`Diverged` do. Acceptable for this card, but note it for the evidence-completeness pass.

**next_cards_to_claim_or_continue**

Finish this card first: make the two required changes, re-run the full suite + ruff + pyright, attach the evidence artifact, commit on `ba/m3-worktree-cycle-evidence`. After that, the critical path is the first end-to-end real-cycle exercise of what this card just wired: the M3 card that runs a real-repo cycle with the real transport under tight budget caps and produces an owner-reviewable candidate branch plus its evidence file (BA-M3-06 or whichever card covers the real-cycle smoke run / owner gate). Everything downstream depends on proving the worktree → verify → package → evidence chain works outside fakes, so claim that before any breadth work like additional probes or scorer extensions.

## Fable re-review

Focused re-review verdict: `ACCEPT`.

### Re-review transcript

VERDICT: ACCEPT

critical_blockers: None.

required_changes_before_completion: None. Both required changes from the prior review are satisfied:

1. Missing vs malformed distinction — `_boundary_violation_for_worktree` checks `worktree / DEFAULT_GOAL_CONFIG` existence: absent config emits `GOAL_CONFIG_FALLBACK` with `reason: "missing_goal_config"` and the resolved path, then applies default boundary rules; present config goes straight to `load_goal_config(worktree)` with no exception handling, so a malformed file raises `GoalConfigError` and fails closed. Both branches have dedicated tests, including the negative assertion that no fallback event is emitted on the malformed path.
2. Candidate ref survival — `tests/test_candidate_packager.py` asserts `arena/candidate/cycle-1` still resolves to the candidate OID after `manager.teardown(worktree)` while the ephemeral `arena/cycle/cycle-1` branch is removed, which is exactly the durability guarantee requested.

Reported verification (targeted tests, full suite, ruff, pyright clean, whitespace checks) is consistent with completion. BA-M3-05 can be committed and closed.

brief guidance (non-blocking, fine as follow-ups):

- A `GoalConfigError` raised mid-cycle propagates out of `run_loop` uncaught — the `try` only handles `BudgetBreach` and `Diverged`, so no `HALTED` event or halt evidence is written for this failure mode. Fail-closed is correct, but consider mapping it to a halt record in a future milestone so the event log stays a complete account of run termination.
- `_boundary_violation_for_worktree` defaults `event_log=None`, which would make the fallback silently un-evented if the helper is ever reused outside `run_loop`. Since the requirement is "emit an event whenever fallback is used," consider making `event_log` a required parameter.
- The `exists()` check followed by `load_goal_config()` has a small check-then-act window; harmless in this single-process loop, just don't let callers assume the existence check guarantees a successful load.

## Non-blocking follow-ups noted by Fable

- Future evidence-completeness pass: map malformed goal config failures to halt records/evidence rather than uncaught exceptions.
- Consider making the boundary fallback helper require an event log if reused outside `run_loop`.
- Rename or document `promotions_total` semantics because candidate packaging currently uses the legacy promotion counter/budget path.
