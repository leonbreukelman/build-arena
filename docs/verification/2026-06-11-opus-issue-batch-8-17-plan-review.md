I have decisive evidence. The verifier already computes `score_after` (`verifier/engine.py:63`) but only returns `verdict` + `ablation_result` — and `verifier/` is a protected surface. That makes #13's "reuse score_after" plan internally contradictory. Here is my review.

---

# Adversarial Plan Review — issue batch #8–#17

**Plan:** `docs/plans/2026-06-11-issue-batch-8-17-plan.md`
**Branch:** `ba/model-agnostic-llm-adapters`
**Posture:** Read-only. No files edited. (The sibling `docs/verification/...review.md` is currently empty; I'm returning the review inline as instructed.)

## 1. Verdict: **ACCEPT_WITH_CHANGES**

The plan is well-structured, correctly keeps broad live loops disabled, reuses the existing status-doc guard harness, and is mostly accurate. But three issues (#13, #11, #16) have blocking flaws — most seriously, **#13's recommended fix silently requires editing a protected surface the plan itself forbids**, and **#11's default behavior will break real providers and existing passing tests.** Fix the items in §2–§3 before implementation.

## 2. Blocking flaws / unsafe assumptions

### B1 — #13 score_after reuse forces a protected `verifier/` edit (or a non-existent score store). Plan does not acknowledge this.
- `VerificationResult` exposes only `verdict` + `ablation_result` (`verifier/engine.py:24-26`). The verifier *does* compute the candidate score at `verifier/engine.py:63` (`score_after = scorer.score_repo(worktree)`) and feeds it into the request (`:69`), but **never returns it**.
- `Verdict.score_after_id` (`arena/generated/models.py:425`) is an **ID string**, not a `ScoreRecord`. I found **no score store / lookup** that resolves that id back to a `ScoreRecord` (grep for `ScoreStore`/`get_score`/`lookup` is empty). So the loop cannot reconstruct the record from the id.
- Therefore the only ways to "reuse the verifier's score_after" are: **(a)** add a field to `VerificationResult` in `verifier/engine.py` — but `verifier/` is in `DEFAULT_READ_ONLY_DIRS` (`arena/boundary.py:16-23`) and the plan's own constraint (line 26) forbids editing it without explicit user approval; or **(b)** build a new score store. The plan's fallback — "capture it through a local variable in the loop by reading from the `verification` object" — **is impossible as written**: the verification object carries no score_after to read.
- **This is the central contradiction in the plan.** Either escalate the `verifier/` change as an explicitly user-approved unavoidable maintenance edit (it qualifies, and it's low-risk: add `score_after: ScoreRecord` to the returned `VerificationResult` and pass it through), or descope #13's reuse. Decide before coding, don't discover it mid-implementation.

### B2 — #13 "incomplete assert" root cause appears already fixed; test risks being vacuous.
The PROMOTE assert at `arena/loop.py:157` **already** guards `hypothesis is not None` (as do VERIFY `:144` and DISCARD `:214`). The plan/issue claim it "omitted hypothesis before use" is not true of current code (likely fixed by a recent hardening commit). Before writing a guard test that passes trivially — or "fixing" something already correct — re-read the issue's exact cited location. If stale, close #13's assert sub-item with that explanation rather than a no-op change.

### B3 — #11 strict served-model equality by default will break real providers and existing green tests.
OpenAI-compatible providers routinely return a served-model string ≠ the requested alias (OpenRouter canonicalizes; xAI returns versioned ids). The current code records both without enforcing (`arena/llm_adapter.py:179,186-187`), and **existing passing tests deliberately use served≠requested** (`test_llm_adapter.py`, `test_diff_proposer.py` use `grok-served` vs `grok-requested`). Defaulting to a hard `ValueError` on inequality (plan #11 step 3, "enforce by default") would break those tests and legitimate live providers. **Change the default:** warn + record mismatch by default; hard-fail only when an explicit `expected_served_model` is configured or under the `require_explicit_model`/strict flag. Any retirement of the mismatch-tolerant tests must be deliberate and called out, not collateral.

### B4 — #16 documentation-only does not resolve the issue as stated.
Issue #16 is "corpus *dominates the tree* (~85%)." A retention-policy doc + guard test records a decision but does not reduce bloat. The non-destructive stance is the right *first* step and is safe — but the plan must not let #16 be **closed** as resolved on that basis. Either keep #16 open as a tracked decision, or get explicit user confirmation that "decision + guardrail recorded" is the agreed acceptance bar. Otherwise this overclaims.

### B5 — #12 run-start orphan reaping with `live_cycle_ids=set()` is concurrency-unsafe.
`reap_orphans(live_cycle_ids=...)` exists (`arena/worktrees.py:48`) and tears down every worktree dir not in the exclusion set. Calling it at run start with an **empty** set would destroy worktrees belonging to a concurrently running loop. Pass the current run's live cycle id(s), or guard against concurrent runs explicitly.

### B6 — #12 generic handler ordering and event-name validity.
- The new catch-all must be placed **after** `except BudgetBreach`/`except Diverged` (`arena/loop.py:240-247`) so those keep their specific halt reasons. Add a test asserting a `BudgetBreach` still halts as budget, not `RUNNER_UNAVAILABLE`.
- On exception, the active `worktree` local may be `None` or stale; teardown must null-check.
- The plan introduces a **new** orphan-reap event "with count." Confirm the `Event` type field accepts arbitrary strings before relying on it. Reusing existing `HALTED` is safe (already emitted), but a brand-new event name could hit schema/generated validation — which the plan is trying to avoid. Verify `arena/events.py:37` / generated `Event` model is free-text, else pick an existing event type.

## 3. Concrete changes required

1. **#13:** Explicitly choose and document one path: (a) user-approved minimal `verifier/engine.py` edit to return `score_after` on `VerificationResult` (recommended — low risk, semantically clean), or (b) drop the reuse and keep the rescore but add a comment/issue note. Do not rely on "read it from the verification object" — that surface doesn't exist. Also confirm `promoter.promote` (`arena/loop.py:161`) does not mutate scored worktree content between verify and promote, so reuse is semantically equivalent; the test should assert score-record identity/equality.
2. **#13 assert:** Re-verify the issue's cited assert location against current `loop.py`; if already guarded, record that and skip a vacuous test.
3. **#11:** Make served-model enforcement opt-in/strict-flag-gated, not default-on. Enumerate **every** live construction site that must set `require_explicit_model=True` — `LiveProjectModelLLM` (`arena/llm_adapter.py` generate path), `OpenAICompatibleDiffTransport.__init__`, **and any CLI entrypoint that builds a live client** — a missed site re-opens the silent-default hole (`resolve_provider_config` default chain, `arena/llm_adapter.py:92-98`). `require_explicit_model` must default `False`.
4. **#10:** `resolve_api_key` has a single caller (`arena/llm_adapter.py:139`), so the wrapper refactor is safe. Good.
5. **#15:** Before editing the calibration fixture `.arena/calibration/repo/.arena/goal.toml` (`read_only = []`), check whether any committed ScoreRecord/scorer.lock pins the fixture's `goal_config_sha` (`ScoreRecord.goal_config_sha`, `scorer/engine.py:51-64`). Adding `benchmarks/runtime_proxy.py` changes the goal-config content → changes its sha → may invalidate pinned calibration records or break `test_goal_config.py:249-260`. If so, this is more than a one-line edit. Confirm the fixture goal.toml is not itself a protected/locked surface.
6. **#16:** Reframe acceptance to "decision + guardrail recorded," and keep the issue open/tracked rather than closed-as-fixed.
7. **#12:** Pass real live cycle ids to `reap_orphans`; order generic except last; null-check teardown; confirm event-name validity.

## 4. Issue-vs-implementation gaps
- **#13:** Proposed "reuse" not achievable as written without a protected edit (B1); assert fix likely already done (B2).
- **#11:** Default strict equality does not match how compatible providers behave; over-enforces (B3).
- **#16:** Doc-only does not satisfy "corpus dominates the tree" (B4).
- **#14/#17:** Accurate to code — `DeterministicOllamaAblationRunner` genuinely does **not** call an LLM (`verifier/ablation.py:32-52`), so the caveat and "subordinate to certification" language do not overclaim. **But:** README already states "3 Lanham probes and a 2-of-3 quorum" (`README.md:21`). The caveat must also cover that line so a reader doesn't infer a live Lanham ablation gate exists; otherwise #14 fixes the FP/FN sentence while leaving an adjacent overclaim.

## 5. TDD / tests I would require
- **#12:** non-budget/non-divergence exception (scanner raises after worktree create) → `LoopResult.halt_record` set, terminal `HALTED` event with `unexpected_exception:<Type>` detail, teardown attempted on active worktree; cleanup-failure does not mask the halt event; `BudgetBreach` still halts as budget (ordering); run-start `reap_orphans` emits count event **and does not remove the active run's worktree**.
- **#13:** spy scorer asserting `score_repo` is **not** called in PROMOTE; `ctx.active_score` equals the verifier-produced `score_after` record (by id/identity), not a fresh score.
- **#11:** mismatch under strict flag raises `ValueError` **before** returning success and before recording success metadata; mismatch under default records metadata + warning and succeeds (protect existing providers); construction without explicit model under `require_explicit_model` raises; explicit env model allowed; **CLI live entry requires explicit model**.
- **#10:** `api_key_source` metadata is `environment`/`hermes_env_file`; **secret-non-disclosure test must scan the serialized metadata/event/evidence output for the actual key substring**, not merely check for absence of a `key` field.
- **#15:** `is_boundary_violation(..., goal_config=fixture)` rejects `benchmarks/runtime_proxy.py`; fixture `read_only` includes it; calibration still scores/locks consistently after the sha change.

## 6. Protected surfaces / broad-live-loop boundaries
- **Live loops:** Plan correctly keeps broad live loops off and requires no new live runs. Good.
- **Protected-surface risk — must resolve before coding:** #13's recommended fix touches `verifier/` (B1); #15 may perturb a pinned `goal_config_sha`/`scorer.lock` (item 5). The plan claims to avoid these surfaces "except documentation references," but #13 as drafted cannot. Either escalate for explicit user approval (it qualifies as an unavoidable maintenance edit) or descope.
- **#12 no-schema-edit compromise:** confirmed viable — `RUNNER_UNAVAILABLE` exists (`schema/arena.yaml:44`) and `HaltRecord.detail` is free-text `Optional[str]`. Reusing it for mid-run crashes is semantically loose ("missing at boot" vs "unexpected crash"); acceptable if the `unexpected_exception:<Type>` detail prefix is mandated/tested and the overloaded meaning is noted in AGENTS/README. Flag the cleaner alternative (one user-approved schema reason) as an option, not a requirement.

---

**Bottom line:** ACCEPT_WITH_CHANGES. The plan is sound on #8/#9/#10/#14/#17 and structurally good elsewhere, but do not start coding until B1 (#13 protected-edit contradiction) and B3 (#11 default-strict regression) are resolved, and #16's acceptance bar is realigned with the user.
