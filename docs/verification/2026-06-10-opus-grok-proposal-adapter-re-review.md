I've reviewed all five files against the two blockers. Let me trace the critical paths.

**B1 (provider ValueError must become RunnerError):**
- `diff_proposer.py:72-85` — the `chat_client.complete(...)` call is wrapped in `try/except ValueError` that re-raises as `RunnerError(f"diff proposal provider failed: {exc}")`. The real adapter raises `ValueError` on truncation/malformed envelopes, so a real-client `length` finish now surfaces as `RunnerError`, not a crash.
- `diff_proposer.py:86-87` separately handles the injected/fake path where the result is *returned* with `finish_reason == "length"` → `RunnerError("diff proposal truncated")`. Both producer paths converge on `RunnerError`.
- `test_diff_proposer.py:199-241` constructs a *real* `OpenAICompatibleChatClient` (fake `urlopen` returning `finish_reason: length`) wired into the transport and asserts `RunnerError`. This exercises the actual adapter→ValueError→RunnerError conversion, not just the fake. ✓

**B2 (live mode must require explicit model):**
- `project_model_cli.py:62-64` — `if args.llm_mode == "live" and not args.live_model:` prints a refusal and returns `2`, *before* `build_project_model_snapshot(...)` is called at line 66. Ordered after the `--allow-live` check (59-60). ✓
- `test_project_model_cli_ai.py:154-186` monkeypatches the builder to raise, then asserts `called is False`, `rc == 2`, and `--live-model` in stderr — proving refusal precedes builder construction. ✓
- Transport-level: `diff_proposer.py:56-57` raises `ValueError("live diff transport requires an explicit model or provider_config")` when `chat_client`, `provider_config`, and `model` are all absent; `test_diff_proposer.py:281-283` covers it. ✓

Both blockers are resolved in code with matching tests.

---

## Verdict: **ACCEPT_WITH_CHANGES**

(Accept the fixes as resolving B1 and B2; the "changes" are honesty caveats to record, not code blockers.)

### B1 — RESOLVED
ValueError from the chat client is caught and converted to `RunnerError` (`diff_proposer.py:84-85`), with a real-client test exercising the adapter's own `length`→`ValueError` path (`test_diff_proposer.py:199-241`). The fake-transport `length` path is independently covered (`diff_proposer.py:86`, parametrized test line 184).

### B2 — RESOLVED
Live decomposer mode now fail-closes without `--live-model` before any builder/client construction (`project_model_cli.py:62-64`), tested at `test_project_model_cli_ai.py:154-186`. The proposal transport refuses to construct with no model at all (`diff_proposer.py:56-57`), tested at line 281-283.

### Remaining blockers before "ready to attempt a bounded, operator-authorized real run"
**None that block the "ready to *attempt*" claim** — provided the claim keeps the plan's exact framing (ready to *attempt* a bounded, operator-authorized run; provider acceptance unverified until a real smoke). No real provider call has been executed, which the plan explicitly scopes as expected (Non-Goals; Readiness Definition line 213). If anyone upgrades the language to "proven ready" or "ready for an unattended/broad run," that *would* be a blocker — but as scoped, the readiness statement is supportable.

### Non-blocking caveats (report honestly)
1. **Transport guard is weaker than the CLI guard.** `__init__` only rejects when `chat_client`, `provider_config`, *and* `model` are all `None`. A `provider_config` produced by `resolve_provider_config(provider)` *without* an explicit model (falling back to a default/env model) would still construct successfully. The explicit-model discipline for a real run is enforced only on the **decomposer CLI path** (`--live-model`); the proposal transport has no CLI wiring or operator gate of its own in this change, so it relies on the caller passing an explicit model. The B2 fix is sound for the surface that has an operator entrypoint, but the proposal path's "no unverified fallback model" guarantee is caller-discipline, not enforced-at-transport.
2. **Two distinct truncation paths.** Real-client truncation → `ValueError` → caught at line 84; injected-client truncation → returned result → line 86. Both reach `RunnerError`, and the real-client test's regex `match="truncated|length"` tolerates either message — fine, but the message text differs between paths ("diff proposal provider failed: ..." vs "diff proposal truncated"), so log-based assertions downstream should not assume one wording.
3. **Verification not re-executed.** This is a read-only review; I did not re-run pytest/ruff/pyright or the no-network smoke. The verdict rests on reading code + tests. The implementation agent's claim that all suites pass is plausible and consistent with the code, but is not independently confirmed here.
4. **Provider acceptance genuinely unproven.** No paid/live call ran; whether xAI/OpenRouter accept the request and whether a real model emits a gate-valid diff is untested by construction (plan AC#5, line 213). This is by design, not a defect — just must remain stated in any readiness writeup.

Since this is a read-only review with no code to implement, there is no implementation plan to approve — the verdict above is the deliverable.
