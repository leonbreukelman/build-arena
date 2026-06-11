Write isn't enabled in this review context, so I'll deliver the review directly. The repository fully confirms the plan's grounded-state claims (live transport absent from `diff_proposer.py`, `LiveProjectModelLLM` hardwired to xAI with no shared adapter, CLI `_snapshot` not even forwarding the existing `live_model`/`live_base_url`, doc-guard test enforcing markers/overclaims). Here is the adversarial review.

---

## 1. Verdict
**ACCEPT_WITH_CHANGES.** Structurally sound, TDD-first, respects the no-live-spend boundary, edits nothing under scorer/verifier/schema/generated, and is implementable under mock/no-network verification. But it carries one false-readiness framing risk, one unresolved design decision that decides whether a *real* run succeeds, and several silent-regression / overclaim gaps to close before coding.

## 2. Blocking issues
- **B1 — "Ready for a real run" is unprovable under mock-only verification.** All residual risk lives in the provider boundary (auth, real envelope shapes, `json_object` support per model, how a real model formats a unified diff). Mocks cannot retire that risk. The plan's own readiness section admits the paid call was never executed — so every "ready for a real run" must become **"ready to *attempt* a bounded, operator-authorized real run."** This is precisely the false-readiness trap to guard against.
- **B2 — Unresolved fence-handling decision (Task 5).** The plan literally asks itself *"Strip markdown fences if present?"* and leaves it open. That decides whether a real Grok response (which routinely wraps diffs in ```` ```diff ````) is applied or rejected. Mocks can pass while the first real call fails. Decide now: **strip a single leading/trailing fence** — reuse the existing logic at `arena/project_model_llm.py:134` (`_parse_json_text`) — then hand stripped text to the patch gate; reject only if still non-diff.

## 3. Required plan changes before implementation
- **R1 (B1):** Reword Goal, Acceptance Criteria, Task 6 docs, and Readiness Definition to "attempt a bounded authorized real run"; state plainly that no provider compatibility was empirically verified.
- **R2 (B2):** Resolve fence handling (strip-then-gate); delete the ambivalent "Strip…? Prefer reject…" note. Pin with tests (fenced-diff accepted, prose rejected).
- **R3 — Preserve the `~/.hermes/.env` key fallback.** `_resolve_api_key` (`project_model_llm.py:149-163`) reads keys from `~/.hermes/.env` when the env var is absent. The shared adapter must reuse that exact resolver, or the plan must consciously decide to drop it. Silently losing it regresses only at real-run time. Add a fallback-resolution test.
- **R4 — Don't trust the hardcoded default model for a real run.** Default `"grok-4.20-0309-non-reasoning"` (`project_model_llm.py:68`) looks like a placeholder and may 404 against the live xAI catalog. Require an explicit `--live-model` for any real attempt and label the hardcoded default as a structural/test fallback, not a verified live id. Otherwise the "real run" 404s on its first call.
- **R5 — Re-scope Acceptance Criterion 5.** Mock tests prove *request construction*, not provider acceptance. Reword to "structural tests prove the same code path constructs valid requests for xai/openai/openrouter presets; provider acceptance is unverified." Same caveat on Task 4's `test_same_diff_transport_config_can_target_xai_openai_openrouter`.
- **R6 — Specify a diff-transport `max_tokens` + context-cost caveat.** The prompt embeds full target-file contents; too-small `max_tokens` → `finish_reason='length'` → rejection, and large files inflate cost/context. Set an explicit value; document large-file behavior.
- **R7 — Don't claim "reject non-diff before patch gate" as a new safety property.** The patch gate already rejects empty/malformed/boundary/caps (`patch_gate.py:33-57`) and the runner already rejects empty/truncated/cancelled (`diff_proposer.py:100-107`). The genuinely new, load-bearing behavior is **mapping `finish_reason=='length'` → `DiffProposalResponse(truncated=True)`** so a partial-but-plausible diff is refused. Frame Criterion 4 around that.

## 4. Missing tests / unsafe assumptions
- **Doc-overclaim regression test (missing).** `test_project_status_docs.py` forbids "production ready" / "ready for broad autonomous live loops" but would happily pass docs saying **"ready for a real run."** Extend that test to require the new docs to state the proposal transport is *built but unproven against a real provider*, and to forbid "ready for a real run." Without it, the doc guard gives false comfort.
- **Fence/format tests (missing, ties to R2):** fenced-diff accepted after strip; prose rejected; `length`-truncated rejected.
- **`~/.hermes/.env` fallback test (missing, ties to R3).**
- **CLI forwarding must be asserted end-to-end, not just at argparse.** The current `_snapshot` (`project_model_cli.py:59-71`) doesn't forward even the existing `live_model`/`live_base_url` — a latent inert-flag bug. The new flags must be threaded into `build_project_model_snapshot` *and* the test must assert they arrive (monkeypatched builder), or they're silently dead.
- **Existing exact-request test will break by design.** `test_live_project_model_llm_uses_direct_xai_json_api_and_records_metadata` asserts byte-exact payload equality (system prompt, `temperature` 0, `max_tokens` 4096, `response_format` json_object). Task 3 must preserve that exact shape through the shared client or consciously update the assertion — flag it so the refactor isn't a free behavior change.
- **Unsafe assumption:** that `response_format={"type":"json_object"}` is honored identically across xAI/OpenAI/OpenRouter per model. It isn't uniform. Keep as an explicit unverified caveat; do not gate readiness on it.

## 5. Sufficient to proceed under mock/no-network verification?
**Yes, with R1–R7 applied.** No live spend, `--allow-live` preserved, no protected surfaces touched. Task 4's `...applies_live_transport_valid_diff_after_patch_gate` plus the final mocked-runner smoke give a legitimate no-network proof of the transport→gate→apply wiring. That mock verification is sufficient to prove **the wiring** — and explicitly **not** sufficient to prove **a real provider call will succeed**. That distinction must be the headline of the readiness writeup, not a footnote.

---

**Bottom line:** the plan is safe to implement under mocks and won't incur spend, but as written its readiness language would let us falsely report "ready for a real run." Apply R1, R4, and the doc-overclaim test as the non-negotiable minimum; B2/R2 is the one decision that determines whether the eventual authorized real call actually applies a patch instead of bouncing off the gate.
