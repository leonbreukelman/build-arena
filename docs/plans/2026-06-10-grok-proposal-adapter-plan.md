# Grok Proposal Adapter Implementation Plan

> **For Hermes:** Use test-driven-development for every behavior change. Do not run live paid/provider calls while implementing this plan; prove the adapter with mock transports first.

**Goal:** Wire the proposal component so it can use an explicit Grok model through the same OpenAI-compatible adapter layer as the decomposer, while keeping all broad live runs behind existing explicit live gates. This implementation makes Build Arena ready to *attempt* a bounded, operator-authorized real run; it does not prove provider compatibility until that real provider smoke is authorized and executed.

**Architecture:** Add one shared OpenAI-compatible chat client and provider registry under `arena/llm_adapter.py`. Refactor `LiveProjectModelLLM` to use that shared client for JSON decomposition output. Add a live `OpenAICompatibleDiffTransport` for `arena/runners/diff_proposer.py` that prompts for a strict unified diff, strips one surrounding markdown fence when present, and returns `DiffProposalResponse` only after visible content is non-empty, non-truncated, and diff-shaped. The existing `DiffProposerRunner` remains the deterministic patch-gate/applier.

**Tech Stack:** Python stdlib `urllib.request`, existing `pytest`, `ruff`, `pyright`, existing `validate_unified_diff`, existing `--allow-live` gate for decomposer snapshots.

---

## Grounded Current State

- Prior conversation/card `t_5869e944` says BA-LLM-01 requires model-agnostic/operator-switchable LLM support for all LLM surfaces.
- Code verified in this session:
  - `arena/project_model_llm.py` has `LiveProjectModelLLM`, currently direct xAI/OpenAI-compatible but not using a shared adapter.
  - `arena/project_decomposer_ai.py` forwards only `live_model` and `live_base_url`; not `provider` or `api_key_env`.
  - `arena/project_model_cli.py` exposes `--llm-mode live --allow-live` but not provider/base-url/model/key-env switches.
  - `arena/runners/diff_proposer.py` has only `DiffTransport` protocol and fake/test transports; no live Grok transport exists.
- Guardrail: this plan builds and verifies the switch; it does not declare Build Arena ready for broad autonomous live loops.
- Opus review artifact: `docs/verification/2026-06-10-opus-grok-proposal-adapter-plan-review.md`. Verdict was `ACCEPT_WITH_CHANGES`; required changes applied here before coding: reword readiness to "ready to attempt", decide strip-then-gate fence handling, preserve `~/.hermes/.env` fallback, require explicit live model for real attempts, re-scope provider-preset tests as request-construction proof, set proposal max-token/context caveats, and add doc-overclaim/fence/fallback tests.

## Acceptance Criteria

1. A shared `OpenAICompatibleChatClient`/provider registry exists and redacts secrets in diagnostics.
2. The decomposer live path routes through the shared client and is operator-switchable by CLI flags and env/configurable constructor fields: provider, base URL, model, API key env.
3. The proposal path has a live `OpenAICompatibleDiffTransport` that can call an explicit Grok model or another OpenAI-compatible provider by config and produce a `DiffProposalResponse`.
4. The live proposal transport converts provider failures/truncation into `RunnerError`, strips one surrounding markdown fence when present, and rejects empty/prose-only output before patch application.
5. Mock tests prove at least xAI, OpenAI, and OpenRouter presets construct requests through the same code path by config alone. These tests do not prove those providers will accept the request or that a real model will emit a valid diff.
6. CLI help/docs expose provider switches for decomposer live snapshots, while explicitly preserving `--allow-live` and not-ready-for-broad-loop boundaries.
7. Verification: targeted RED/GREEN tests, full `uv run pytest tests -q`, `uv run ruff check .`, `uv run pyright`, `git diff --check`, and a no-network direct smoke of the proposal runner using a mocked response.

## Non-Goals

- No paid/live provider call without a separate explicit live-smoke authorization.
- No real run should rely on a hardcoded fallback model. A bounded real attempt must pass an explicit `--live-model`/constructor model such as the operator-selected Grok model for that run.
- No broad autonomous loop execution.
- No edits under `scorer/`, `verifier/`, `schema/`, `.arena/scorer.lock.toml`, or generated files.
- No Anthropic-native adapter; Anthropic can be reached later via OpenRouter or a separate native adapter.

## Task 1: Add shared OpenAI-compatible chat adapter tests

**Objective:** Pin the adapter contract before production code.

**Files:**
- Create: `tests/test_llm_adapter.py`
- Later create: `arena/llm_adapter.py`

**Test cases:**
1. `test_provider_registry_presets_are_openai_compatible`:
   - xai => `https://api.x.ai/v1`, `XAI_API_KEY`, model fallback from Grok env/default.
   - openai => `https://api.openai.com/v1`, `OPENAI_API_KEY`.
   - openrouter => `https://openrouter.ai/api/v1`, `OPENROUTER_API_KEY`.
2. `test_chat_client_posts_visible_messages_and_records_metadata`:
   - monkeypatch env key.
   - fake `urlopen` captures URL/body/headers/timeout.
   - assert `/chat/completions`, `Bearer` header, requested model, messages, max tokens, temperature, `response_format` when supplied.
   - assert returned `OpenAIChatResult` contains visible text, served model, finish reason, usage, prompt/content hashes, provider metadata.
3. `test_chat_client_extracts_structured_visible_content_parts`:
   - response has `message.content` as a list of text parts.
   - visible text is concatenated/returned.
4. `test_chat_client_rejects_no_choices_empty_content_and_length`.
5. `test_chat_client_redacts_provider_errors`:
   - HTTP/error text includes bearer/api key; raised message must redact it.
6. `test_chat_client_reads_api_key_from_hermes_env_file`:
   - monkeypatch HOME to a temp directory containing `.hermes/.env` and prove the shared resolver preserves the existing fallback behavior from `LiveProjectModelLLM`.

**RED command:**
`uv run pytest tests/test_llm_adapter.py -q`

Expected before implementation: import failure for `arena.llm_adapter`.

## Task 2: Implement shared adapter minimally

**Objective:** Make Task 1 green without changing behavior elsewhere.

**Files:**
- Create: `arena/llm_adapter.py`

**Implementation notes:**
- `ProviderPreset(provider, base_url, api_key_env, default_model_envs, default_model)`.
- `resolve_provider_config(provider='xai', base_url=None, api_key_env=None, model=None)` with env fallback:
  - model override env names: `BUILD_ARENA_LLM_MODEL`, provider-specific envs such as `BUILD_ARENA_XAI_MODEL`, existing `XAI_MODEL`.
  - base URL env: `BUILD_ARENA_LLM_BASE_URL` or provider-specific when useful.
  - api key env override: `BUILD_ARENA_LLM_API_KEY_ENV`.
  - Keep the existing `~/.hermes/.env` key fallback when resolving the actual API key.
- `OpenAICompatibleChatClient.complete(messages, response_format=None, system=None)`.
- Visible content extraction must accept string content and list content parts with `text` or `content` fields; ignore reasoning-only fields.
- Raise `ValueError` for missing key, HTTP failure, malformed envelope, no choices, empty content, or `finish_reason == 'length'`.
- Default model IDs are structural/test fallbacks only; any real run readiness writeup must require an explicit operator-selected model.

**GREEN command:**
`uv run pytest tests/test_llm_adapter.py -q`

## Task 3: Refactor decomposer live path to shared adapter + operator switches

**Objective:** Keep existing live decomposer behavior while adding provider/model/base URL/key-env switchability.

**Files:**
- Modify: `arena/project_model_llm.py`
- Modify: `arena/project_decomposer_ai.py`
- Modify: `arena/project_model_cli.py`
- Modify tests: `tests/test_project_model_llm_live.py`, `tests/test_project_model_cli_ai.py`, `tests/test_project_status_docs.py`

**TDD tests:**
1. Update/add `test_live_project_model_llm_uses_shared_openai_client_and_records_metadata` to assert the same request shape through the shared client.
2. Add a CLI test that `snapshot --llm-mode live --allow-live --live-provider openrouter --live-base-url https://openrouter.ai/api/v1 --live-model test-model --live-api-key-env OPENROUTER_API_KEY` forwards all four values into the builder or a monkeypatched builder.
3. Add a fail-closed CLI test for `--llm-mode live` without `--allow-live` remaining unchanged.
4. Update CLI help marker test so documented flags exist.
5. Add/update doc status tests to forbid unqualified "ready for a real run" language and require "ready to attempt a bounded, operator-authorized real run" plus "provider acceptance unverified until live smoke" wording.

**RED command:**
`uv run pytest tests/test_project_model_llm_live.py tests/test_project_model_cli_ai.py tests/test_project_status_docs.py -q`

**Implementation notes:**
- Preserve `LiveProjectModelLLM.generate(prompt) -> dict` public API for compatibility.
- Its constructor should accept provider/base_url/api_key_env/model and instantiate/use `OpenAICompatibleChatClient` internally.
- Project model CLI flags:
  - `--live-provider`
  - `--live-base-url`
  - `--live-model`
  - `--live-api-key-env`
- `build_project_model_snapshot` should accept/pass `live_provider`, `live_api_key_env`, `live_model`, `live_base_url`.
- Do not create a live client before the `--allow-live` check.

**GREEN command:**
`uv run pytest tests/test_project_model_llm_live.py tests/test_project_model_cli_ai.py tests/test_project_status_docs.py -q`

## Task 4: Add live Grok/OpenAI-compatible diff transport tests

**Objective:** Pin the proposal-side live adapter before implementation.

**Files:**
- Modify: `tests/test_diff_proposer.py`
- Later modify: `arena/runners/diff_proposer.py`

**TDD tests:**
1. `test_openai_compatible_diff_transport_requests_unified_diff_and_records_provenance`:
   - fake chat client returns a valid diff.
   - assert request includes target path, file content, success criterion, goal config sha, and strict unified diff/no markdown instruction.
   - assert response contains diff text, intent, provider/model/provenance, not truncated.
2. `test_openai_compatible_diff_transport_rejects_truncated_empty_and_non_diff`:
   - fake chat client returns length finish reason, empty text, and prose; adapter returns/raises fail-closed before runner mutation.
3. `test_openai_compatible_diff_transport_strips_single_markdown_diff_fence`:
   - fake chat client returns a markdown-fenced diff; adapter strips one surrounding fence and still lets the deterministic patch gate decide validity.
4. `test_diff_proposer_applies_live_transport_valid_diff_after_patch_gate`:
   - use fake chat client with valid diff through `DiffProposerRunner` and ensure the patch is applied and provenance is written.
5. `test_same_diff_transport_config_can_target_xai_openai_openrouter`:
   - instantiate config via provider registry; no network.

**RED command:**
`uv run pytest tests/test_diff_proposer.py -q`

Expected before implementation: import failure or missing class failure.

## Task 5: Implement live diff transport minimally

**Objective:** Make Task 4 green.

**Files:**
- Modify: `arena/runners/diff_proposer.py`

**Implementation notes:**
- Add `OpenAICompatibleDiffTransport` taking either a shared `OpenAICompatibleChatClient` or provider configuration.
- Build a compact prompt with:
  - target path
  - success criterion
  - hypothesis intent/id
  - current file contents
  - instruction: return only a unified diff for exactly this target file; no markdown/fences/explanations.
- Call shared chat client with `response_format=None` because a diff is plain text.
- Use a proposal `max_tokens` large enough for a small unified diff (default 4096 unless tests force a narrower value), and document that large target files increase context/cost and can still fail with truncation.
- Strip exactly one surrounding markdown fence if present; then hand stripped text to the patch gate. Reject output that is still not diff-shaped.
- Return `DiffProposalResponse(diff_text=visible_text, intent=request.intent, provenance={...}, truncated=False)` for accepted visible diffs. Convert provider-side `ValueError` failures, including real-client truncation, into `RunnerError` so the router records a clean runner failure instead of crashing the cycle. Existing non-provider transports may still use `DiffProposalResponse.truncated=True`, which the runner rejects before mutation.
- Do not apply patches here; runner remains the deterministic applier/gate.

**GREEN command:**
`uv run pytest tests/test_diff_proposer.py tests/test_llm_adapter.py -q`

## Task 6: Update docs/status and run full verification

**Objective:** Document the new operator switches honestly and prove no broad readiness overclaim.

**Files:**
- Modify: `README.md`
- Modify: `AGENTS.md`
- Modify: `docs/build-arena-project-brief.md`
- Add/update verification artifact: `docs/verification/2026-06-10-grok-proposal-adapter-readiness.md`

**Docs must say:**
- LLM provider path is OpenAI-compatible and operator-switchable for decomposer and proposal transport by config/code.
- Proposal now has a live Grok/OpenAI-compatible transport, but broad autonomous live loops are still not ready until readiness-register blockers close.
- Build Arena is ready to attempt a bounded, operator-authorized real run after verification, not proven ready for an unattended real run. A bounded real run still needs explicit operator authorization, a call budget, and an explicit model ID; provider acceptance remains unverified until that smoke runs.

**Final commands:**
- `uv run pytest tests/test_llm_adapter.py tests/test_project_model_llm_live.py tests/test_project_model_cli_ai.py tests/test_diff_proposer.py tests/test_project_status_docs.py -q`
- `uv run pytest tests -q`
- `uv run ruff check .`
- `uv run pyright`
- `git diff --check`
- `python`/`uv run python` no-network direct smoke using mocked chat response through `OpenAICompatibleDiffTransport` + `DiffProposerRunner`.

## Bounded Real-Run Attempt Readiness Definition

After implementation, report "ready to attempt a bounded, operator-authorized real run" only if:

- All code/docs/tests above are green.
- A no-network mocked proposal runner smoke proves the live transport and patch gate path end to end.
- Secret-shape scan of diffs/artifacts is clean.
- A dry live-gate check proves `--allow-live` is still required for decomposer live mode.
- The writeup requires an explicit Grok model ID and call budget for any real attempt.
- Remaining limitation is explicit: actual paid Grok proposal call/full loop was not executed in this implementation pass unless separately authorized, so provider acceptance and real model diff behavior remain unproven until the first live smoke.
