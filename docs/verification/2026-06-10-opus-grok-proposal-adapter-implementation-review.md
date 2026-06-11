Write is disabled in this read-only context, so I'll deliver the review directly (as requested — no repo files were edited).

---

# Adversarial Implementation Review — Grok Proposal Adapter (BA-LLM-01)

Read-only review of branch `ba/model-agnostic-llm-adapters`. No files edited.

## 1. Verdict: **ACCEPT_WITH_CHANGES**

Structurally faithful to the plan: shared OpenAI-compatible client + provider registry, decomposer routed through it with operator switches that are **actually forwarded and tested**, a live diff transport that strips one fence and hands plain text to the deterministic patch gate, docs reworded to "ready to attempt," and a doc-overclaim guard test. The no-network/mock boundary is genuinely respected — no live spend, `--allow-live` preserved and proven, no protected surfaces touched. Safe to land as a mock-only slice.

But it must **not** be called "ready to attempt a bounded authorized real run" until **B1** is fixed: the first thing a real provider is likely to do (401, truncate, malformed envelope) crashes the cycle instead of failing closed — and the passing tests actively hide it.

## 2. Blocking issue

### B1 — Live transport provider errors raise `ValueError`, which the runner router does not catch → cycle crash, not clean failure

- `OpenAICompatibleChatClient.complete` raises **`ValueError`** for *every* provider-side failure: HTTP/401 (`llm_adapter.py:160`), request failure (`:162`), malformed envelope (`:167`), no choices (`:170`), `finish_reason=='length'` truncation (`:174`), empty content (`:178`).
- `OpenAICompatibleDiffTransport.propose` calls `complete(...)` with **no try/except** (`diff_proposer.py:70`); the `ValueError` propagates straight through `DiffProposerRunner.apply`.
- `RunnerRouter.apply` catches only `RunnerError` and `CreditExhausted` (`router.py:41`, `:54`). A `ValueError` is **uncaught** — it escapes the router and crashes the cycle instead of producing `_error_result` / triggering fallback.
- **Net effect on a real run:** auth failure / truncation / malformed response from the real provider crashes the attempt rather than recording a clean runner failure. The decomposer path survives only because its CLI catches `Exception` broadly (`project_model_cli.py:80`); the proposer path has no such net.
- **Why mocks hid it:** `FakeChatClient` never raises — it returns crafted results — so the transport's own `RunnerError` branches fire in tests. With the real client those branches are **dead code** (the client raises first), and the real path (`ValueError`) is exactly what's uncaught. `test_..._rejects_truncated_empty_and_non_diff` therefore proves production-unreachable behavior.
- **Fix:** wrap `complete()` in `propose()`, convert `ValueError` → `RunnerError` (fail-closed, no mutation); add a test driving the **real** `OpenAICompatibleChatClient` with a fake `urlopen` returning 401/length/malformed and assert a `RunnerError` surfaces.

## 3. Required fixes before "ready to attempt a bounded authorized real run"

1. **(B1)** Wrap chat-client `ValueError` → `RunnerError` in the diff transport + real-client error-path test. **Non-negotiable blocker.**
2. **Enforce explicit `--live-model` for live mode (plan R4 / Non-Goal #2 — documented but NOT enforced).** `--live-model` defaults to `None` (`project_model_cli.py:35`); with no value, `resolve_provider_config` falls through to preset default `grok-4.20-0309-non-reasoning` (`llm_adapter.py:49`) — a placeholder-shaped id that will likely 404 live. The plan made "no real run relies on a hardcoded fallback model" a Non-Goal; the code permits exactly that. README:91 only says it "should be used" (advisory). Add a fail-closed CLI guard (live ⇒ `--live-model` required, exit 2) or a mandatory runbook step. Same `model=None` exposure on the diff transport.
3. **Reconcile the dead/triple truncation guard.** Truncation is enforced in three places but only the client `ValueError` fires for the live path; the transport's length branch (`diff_proposer.py:81`) and the runner's `truncated` check (`:198`) are dead because the client raises first and the transport hardcodes `truncated=False` (`:97`). The plan's stated "load-bearing" behavior (return truncation as status, R7) is not what ships — pick one source of truth after B1.

## 4. Missing tests / doc overclaims

- **Missing real-client error-path test** for the transport (ties to B1) — all transport-rejection tests use `FakeChatClient`, so the production `ValueError` path is entirely unexercised.
- **Missing live-mode-without-`--live-model` test** (ties to fix #2).
- **Fence-strip fragility (untested):** `_strip_single_markdown_fence` uses `rfind("```")` (`diff_proposer.py:167`); a legit diff touching a file that itself contains triple backticks (markdown/docstrings) gets its body truncated at the inner fence. Fail-closed (gate rejects), so not unsafe, but silently rejects valid diffs. Add a test + known-limitation note.
- **`redact_error` is pattern-bound** (`llm_adapter.py:225-226`): redacts `Bearer <tok>` and `key=val` shapes but not a bare key echoed without those affixes. Low severity; worth a caveat since it's the secret-leak guard.
- **Deliverable gap (not an overclaim):** Task 6's readiness artifact `docs/verification/2026-06-10-grok-proposal-adapter-readiness.md` was not created; `...-implementation-review.md` exists but is **empty** (untracked, 0 lines) — a stray placeholder.
- **Doc wording itself is clean:** README:44 / brief:40 / AGENTS:34 all carry "ready to attempt a bounded, operator-authorized real run" + "provider acceptance remains unverified until live smoke," guarded by `test_docs_describe_bounded_real_run_attempt_not_unqualified_readiness`; README:110 / AGENTS:36 restate "not ready for broad autonomous live loops." No broad-live-loop overclaim. Caveat: the "ready to attempt" claim is itself premature until B1 lands.

## 5. No-network / mock-verification boundary: **Satisfied**

All tests mocked/offline; `--allow-live` absence proven to exit 2; CLI forwards all four provider switches and a monkeypatched-builder test asserts arrival (closing the latent inert-flag bug the prior plan review flagged); `test_diff_proposer_applies_live_transport_valid_diff_after_patch_gate` + mocked-runner smoke prove the transport→gate→apply wiring offline; `~/.hermes/.env` fallback preserved and tested (R3); provider switchability proven by config alone for xai/openai/openrouter, correctly scoped as request-construction not acceptance (R5). The plan's boundary — prove the wiring under mocks, don't prove a real call succeeds — is met. Honest correction: the mocks **over-prove** the proposal transport's failure handling (B1), so "wiring verified" must exclude "live provider-error path verified," which it is not.

## Bottom line

Land it as a verified mock-only slice. But fix **B1** (ValueError → RunnerError in the live diff transport) and **#2** (require explicit `--live-model`) before anyone says "ready to attempt a bounded authorized real run" — those two are the difference between a clean first authorized call and a cycle that crashes on the provider's first 401 or truncation.

---

This is a review deliverable, not an implementation plan — there's nothing for me to build unless you want me to. If you'd like, I can turn fixes **B1** and **#2** into a small TDD change set (transport `try/except` wrap + a real-client error-path test + a `--live-model` live-mode guard). Say the word and I'll proceed.
