# Build Arena issue batch plan — #8-#17

Date: 2026-06-11
Branch: `ba/model-agnostic-llm-adapters`
Repo: `leonbreukelman/build-arena`

## Scope

Implement the newly opened issue batch #8-#17 one issue at a time, using TDD for behavior/code changes, doc guard tests for documentation/status issues, and independent Opus/Fable review gates.

Open issues read from GitHub:

- #8 `docs: current-state.md is stale per its own contract and describes the arena-calibration repo; status-docs test does not cover it`
- #9 `docs: README contains a branch-state snapshot claim now false on main`
- #10 `live adapter: undocumented credential fallback to ~/.hermes/.env`
- #11 `live adapter: served-model mismatch is recorded but not enforced; silent 4-deep model default chain`
- #12 `loop: unexpected exceptions escape run_loop with no HaltRecord, no terminal event, and leaked locked worktrees`
- #13 `loop: PROMOTE rescores the worktree instead of reusing the verdict's score_after; incomplete assert uses hypothesis without guarding it`
- #14 `verifier: README FP/FN numbers need a stand-in caveat; the real AblationRunner replacement target is undocumented`
- #15 `scorer/boundary: target-repo measurement instruments are patch-writable; scorer is calibration-target-specific but presented generically`
- #16 `repo hygiene: verification snapshot corpus dominates the tree (~900 of 1018 files)`
- #17 `decision: record which instrument replaces the deterministic AblationRunner stand-in`

## Constraints

- Do not modify `scorer/`, `verifier/`, `schema/`, `.arena/scorer.lock.toml`, or `arena/generated/` unless a user-approved non-hypothesis maintenance change makes it unavoidable. This plan avoids those surfaces except documentation references.
- Keep broad live loops disabled. No additional live provider runs are required for this batch.
- Use TDD: add failing tests before production/doc changes where behavior is guarded.
- Avoid deleting large verification snapshots for #16 unless the evidence-retention decision explicitly approves it. The safer first implementation is a documented retention policy and guardrail, not destructive pruning.

## Opus plan-review adjustments

Opus-latest review artifact: `docs/verification/2026-06-11-opus-issue-batch-8-17-plan-review.md`.

Accepted adjustments before coding:

- #13: do **not** edit `verifier/`. Instead, reuse verifier `score_after` by wrapping the scorer passed into `verify_worktree` with a loop-local capture adapter. The verifier already calls `score_repo`; the wrapper can expose that exact `ScoreRecord` to PROMOTE without a protected-surface edit or second scorer call.
- #13: the `hypothesis is not None` PROMOTE assert is already fixed in current `loop.py`; document/verify this rather than making a vacuous code change.
- #11: avoid provider-hostile global strictness. The shared client will record mismatches by default and enforce served-model equality only when a strict flag is enabled. Build Arena live surfaces will enable strict enforcement; structural/provider-registry tests can remain mismatch-tolerant when explicitly configured.
- #12: do not call `reap_orphans(live_cycle_ids=set())` globally. Add a safer current-run cleanup shape: only reap candidate stale cycle IDs known from this run's event log, and keep the generic exception handler ordered after budget/divergence handlers.
- #16: treat the batch implementation as a documented evidence-retention decision and guardrail, not destructive corpus pruning. If GitHub issue closure is considered later, call out that no files were pruned.

## Issue-by-issue implementation plan

### #8 current-state stale

Root cause: `docs/build-arena-current-state.md` self-identifies as live state but is a stale arena-calibration handoff. Active status-doc tests omit it.

Plan:
1. Add status-doc test coverage for `docs/build-arena-current-state.md`:
   - rejects stale arena-calibration identifiers (`arena/llm.py`, `arena/runner.py`, `exercise_verifier.py`, `patch_eq.py`, `results/run_`);
   - requires a historical/superseded marker if the file remains dated instead of live.
2. Rewrite `docs/build-arena-current-state.md` as a short historical/superseded pointer to `AGENTS.md`, `README.md`, and `docs/build-arena-project-brief.md`, rather than another duplicated live-status source.
3. Verify `tests/test_project_status_docs.py`.

Acceptance:
- A fresh agent cannot mistake current-state.md for current live truth.
- The guard test fails if calibration-repo paths return.

### #9 README branch-state claim

Root cause: README contains ephemeral branch state: `The current branch has local commits ahead of origin until pushed.`

Plan:
1. Add the stale branch-state sentence to `test_project_status_docs.py` stale strings.
2. Remove the sentence from README and keep durable status only.

Acceptance:
- README has no branch-local snapshot claim.
- Test prevents reintroduction.

### #10 credential fallback documentation/provenance

Root cause: `resolve_api_key` can read `~/.hermes/.env`; docs and metadata do not disclose the credential source.

Plan:
1. Add tests for a key-source-aware resolver and provider metadata recording `api_key_source` as `environment` or `hermes_env_file` without exposing the key.
2. Implement `resolve_api_key_with_source(env_name) -> ApiKeyResolution` and keep `resolve_api_key` as compatibility wrapper.
3. Add `api_key_source` to `OpenAICompatibleChatClient` metadata.
4. Document fallback in README/AGENTS/brief with explicit statement: live mode still requires `--allow-live`; credentials may be sourced from env or `~/.hermes/.env`; provenance records only the source, never the key.

Acceptance:
- Tests prove source metadata and secret non-disclosure.
- Docs make fallback non-surprising.

### #11 served-model mismatch and silent model defaults

Root cause: client records served model but does not enforce it; provider config can fall back to a hardcoded model.

Plan:
1. Add tests that:
   - a served-model mismatch raises `ValueError` when strict served-model enforcement is enabled;
   - default client behavior records mismatch metadata without success overclaim, preserving provider compatibility for structural tests;
   - live/decomposer construction requiring explicit model fails when neither arg nor env provides a model;
   - explicit env model remains allowed.
2. Add `require_explicit_model` support to provider resolution and use it in live surfaces (`LiveProjectModelLLM`, `OpenAICompatibleDiffTransport` when not injected with a test client).
3. Add strict served-model enforcement to `OpenAICompatibleChatClient`, disabled by default but enabled by Build Arena live surfaces.
4. Keep provider registry defaults only for non-strict structural preset inspection, but ensure live code paths do not use them silently.
5. Update docs to say real live attempts require explicit model via CLI or env and enforce served-model matching.

Acceptance:
- Mismatched model response fails closed.
- Live surfaces cannot silently use the hardcoded default chain.

### #12 unexpected loop exceptions

Root cause: `run_loop` only catches budget/divergence exceptions; unexpected failures leave no terminal canonical event and can leak locked worktrees.

Plan:
1. Add loop tests with a fake worktree manager/scanner that raises after worktree creation:
   - result has `halt_record`;
   - event log ends with `HALTED` including exception type/message summary;
   - best-effort teardown is called for the active worktree.
2. Add a test that run start calls a current-run orphan reap only for stale cycle IDs already present in this run's event log, if available, and emits an event with count.
3. Implement generic exception handling in `run_loop` using an existing halt reason (`RUNNER_UNAVAILABLE`) with detail prefix `unexpected_exception:<Type>: <message>` to avoid schema/generated edits.
4. Ensure cleanup failures do not mask the halt event; record cleanup failure detail as an event if needed. Add a guard that budget/divergence still use their specific halt reasons.

Acceptance:
- Canonical event stream terminates with a HaltRecord for unexpected exceptions.
- Active worktree teardown is attempted.
- Prior orphan worktrees are reaped at run start when manager supports it.

### #13 PROMOTE score reuse + assert

Root cause: PROMOTE recomputes score after verifier already computed `score_after`; the issue's `hypothesis` assert sub-item is already fixed in current `loop.py`.

Plan:
1. Add a loop promotion test with spy scorer that counts `score_repo` calls and proves there is no extra PROMOTE rescore after verifier scoring.
2. Wrap the scorer passed to `verify_worktree` in a loop-local score-capture adapter. Reuse the captured `score_after` for `ctx.active_score` and evidence writer after promotion.
3. Keep/assert `hypothesis is not None` in PROMOTE; current code already has this guard, so record the issue sub-item as already satisfied by current branch state.

Acceptance:
- Promotion no longer performs an extra scorer call.
- Active baseline score matches verifier's score_after record.

### #14 README FP/FN caveat

Root cause: README FP/FN acceptance-gate wording does not say the figures are measured against the deterministic stand-in ablation runner.

Plan:
1. Add status-doc test marker requiring `deterministic stand-in` caveat near FP/FN wording.
2. Patch README and brief/AGENTS if needed to state the caveat.

Acceptance:
- The metrics cannot be read as live ablation performance.

### #17 AblationRunner replacement decision

Root cause: docs do not state which real instrument the deterministic stand-in is holding a seat for.

Plan:
1. Add a short decision section to AGENTS/brief/README or a dedicated ADR under `docs/decisions/`:
   - deterministic stand-in currently holds the verifier seat;
   - intended replacement path is arena-calibration's regeneration/Lanham verifier once certified by its discrimination matrix and patch-generalization axis;
   - Elenchus is advisory metadata/operator review only, not promote/discard gate;
   - live Ollama adapter is subordinate to certification rather than an independent uncalibrated gate.
2. Add status-doc tests requiring the decision markers.

Acceptance:
- A fresh agent can reconstruct why the stand-in remains and what blocks replacement.

### #15 scorer/boundary measurement instrument protection + genericity caveat

Root cause: target worktree measurement instruments such as `benchmarks/runtime_proxy.py` are patch-writable, and docs can overstate scorer genericity.

Plan:
1. Add a boundary/goal-config regression test showing a target repo can mark `benchmarks/runtime_proxy.py` read-only and `is_boundary_violation(..., goal_config=...)` rejects it.
2. Update the synthetic calibration fixture `.arena/goal.toml` to mark `benchmarks/runtime_proxy.py` read-only.
3. Add/adjust test for calibration fixture goal config read_only to include `benchmarks/runtime_proxy.py`.
4. Patch README/brief to state the current scorer is still calibrated around configured target commands and the synthetic calibration fixture; genericity depends on per-repo goal config, especially read-only measurement surfaces.

Acceptance:
- The known runtime-proxy measurement surface is protected in the calibration fixture.
- Docs stop presenting the scorer as universally generic without config caveat.

### #16 verification snapshot corpus repo hygiene

Root cause: `docs/verification/` dominates tracked file count (currently measured at 1043/1218 tracked files, about 85.6%).

Plan:
1. Avoid destructive snapshot deletion in this batch.
2. Add a versioned evidence-retention policy doc that records the measured corpus size and chosen current stance: keep existing in-tree evidence immutable for audit, but future bulky snapshot trees should prefer summary reports + manifests/hash pointers unless evidence immutability requires full tree retention.
3. Add status-doc test that the policy exists and mentions `docs/verification`, summary reports/manifests, and non-destructive migration policy.
4. Optionally add a small script/test helper later; out of scope for this batch unless Opus recommends it.

Acceptance:
- The repo has an explicit decision rather than accidental bloat.
- No evidence is pruned without a separate explicit migration.

## Planned verification

Targeted as each issue lands:

- `uv run pytest tests/test_project_status_docs.py -q`
- `uv run pytest tests/test_llm_adapter.py tests/test_project_model_llm_live.py tests/test_diff_proposer.py -q`
- `uv run pytest tests/test_loop_phase4.py tests/test_worktree_cycle_evidence.py -q`
- `uv run pytest tests/test_boundary.py tests/test_goal_config.py -q`

Final:

- `uv run pytest tests -q`
- `uv run ruff check .`
- `uv run pyright`
- `git diff --check`
- secret-shape scan on diffs and new docs
- Opus implementation review and Fable final sign-off
