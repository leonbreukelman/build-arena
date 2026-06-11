I have enough to render the verdict. All four flagged risk areas check out against the code, and I've confirmed the verifier's single-`score_repo` call, the fail-closed exception path, the served-model strictness scoping, and the doc hedging.

---

# Implementation Review — Issue Batch #8–#17

## 1. Verdict: **SIGN_OFF_WITH_NITS**

The diff is correct, fail-closed, and well-tested. No blockers. The flagged high-risk areas (loop cleanup, score_after capture, served-model strictness, doc overclaim) all hold up under adversarial reading. Nits below are follow-ups, not gates.

## 2. Blockers
**None.**

## 3. Hidden regressions / coverage gaps

**No true regressions.** The one behavior change — uncaught exceptions now convert to a `HaltRecord` instead of propagating out of `run_loop` — is intentional (#12) and the affected existing test (`test_malformed_present_goal_config_fails_closed`) was correctly updated to assert the halt path, with `GOAL_CONFIG_FALLBACK` still absent (fail-closed preserved).

Verified non-issues I specifically went looking for:
- **score_after is NOT contaminated by ablation.** `Verifier.verify_worktree` calls `scorer.score_repo` **exactly once** (engine.py:63); `DeterministicOllamaAblationRunner.run_probe` never touches the scorer. So `_ScoreCapture.last_score` reliably holds the real full-worktree score, not an ablated variant. My primary worry — "last call wins, last call is an ablation score" — does not materialize.
- **#13 is actually a consistency *improvement*.** Old code rescored at PROMOTE, which could diverge from `verdict.score_after_id` computed at VERIFY. Reusing the captured score removes that latent inconsistency. verifier/ genuinely untouched (confirmed).
- **CancelledError safe.** Broad `except Exception` does not catch `asyncio.CancelledError` (BaseException in 3.8+) — cooperative cancellation intact.
- **Cleanup can't mask the halt.** `_cleanup_after_unexpected_exception` swallows its own teardown failure into `WORKTREE_CLEANUP_FAILED` and still returns the primary halt.

**Coverage gap:** the `if verified_score_after is None: raise RuntimeError(...)` guard at `loop.py:172-173` is **unexercised** — every verifier fake now calls `score_repo` (including the newly-patched `StaticVerifier` in test_coverage_closure). The anti-fabrication contract it enforces has no negative test.

## 4. Protected surfaces / live-loop boundaries
**Respected.**
- `verifier/`, `scorer/`, `schema/`, `arena/generated/` untouched. The choice to reuse `HaltReason.RUNNER_UNAVAILABLE` (rather than add an enum value) is itself evidence the generated/schema boundary was honored.
- `read_only = ["benchmarks/runtime_proxy.py"]` protects a real existing file; boundary test drives target-repo goal-config `read_only` resolution.
- Default chat client stays provider-compatible (`require_served_model_match=False`, records the match flag without raising); only LiveProjectModelLLM + diff transport opt into strict matching + explicit-model. Correct scoping.
- API key value never enters metadata (only `api_key_source`); test asserts the secret string is absent from serialized metadata.
- Docs uniformly retain "not ready for broad autonomous live loops," and the status-doc guards actively enforce no-overclaim + no-stale-path drift. No overclaim found; stand-in-vs-live-ablation and FP/FN-are-not-live-claims are explicitly caveated.

## 5. Nits & tests to add

**Nits (non-blocking):**
- **N1 — `RUNNER_UNAVAILABLE` semantic overload.** That enum is documented "Required runner missing at boot," but it now also buckets scanner crashes, `GoalConfigError`, `KeyError`, `AssertionError`, etc. Any reason-level aggregation/alerting will mis-bucket internal defects as runner-availability problems. The `unexpected_exception:` detail prefix mitigates forensics but not metrics. Proper fix is a schema-level `INTERNAL_ERROR`/`UNEXPECTED_EXCEPTION` reason + regeneration (out of scope for this batch) — track as follow-up, and add a code comment noting the intentional reuse.
- **N2 — guard placement.** The `RuntimeError` at loop.py:172 fires *after* `promoter.promote(...)` (line 165) and `VERDICT_DECIDED` emission. If it ever triggers, you get a half-completed promotion (side effects done, `promotions_total` not incremented, no evidence) turned into a halt. Moving it directly under `case LoopState.PROMOTE:` makes it a clean precondition with zero partial side effects.
- **N3 — undocumented contract tightening.** The guard silently requires *every* verifier (real or fake) to call the injected `scorer.score_repo` or PROMOTE halts. Intentional anti-fabrication, but worth a one-line doc on `verify_worktree`/`ScorerLike` so future verifier authors don't trip it (test_coverage_closure already had to add the call).

**Tests I'd add:**
1. **Negative score-capture test:** a verifier fake that returns `PROMOTED` *without* calling `scorer.score_repo` → assert loop halts with `RUNNER_UNAVAILABLE` and detail containing "did not return a score_after record." Locks the currently-uncovered guard and documents N3.
2. **Cleanup-failure-during-halt test:** `worktrees.teardown` raises inside the broad-except path → assert `WORKTREE_CLEANUP_FAILED` is emitted *and* the halt record is still returned (cleanup failure must not mask the primary halt). Currently only the happy teardown path is covered.
3. **(Optional) CancelledError pass-through test** as a regression guard against anyone later widening the catch to `BaseException`.

Cleared for Fable review.
