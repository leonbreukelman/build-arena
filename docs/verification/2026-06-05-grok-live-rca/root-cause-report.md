# Grok/xAI Live Decomposer Root-Cause Report

Date: 2026-06-05

## Direct conclusion

Before this repair slice, the Build Arena AI-first decomposer did not have a direct Grok/xAI live API path. The implemented modes were fixture, recorded, off, and an explicit live branch that raised `RuntimeError` before any provider call. The prior Grok pilot wrappers were therefore outside the Build Arena live decomposer path; accepted snapshots were replayed through recorded JSON, not produced by `--llm-mode live`.

Direct xAI/Grok API access is healthy in this environment, and the Hermes xAI provider path is also healthy for a tiny JSON request. The RCA-time failing boundary was Build Arena's missing live model adapter plus weak/fail-open handling for wrapper-style empty or cancelled outputs if such outputs are replayed as recorded JSON.

## Evidence map

- Repo state transcript: `repo-state.md`
- Mandated file read manifest: `mandated-file-read-manifest.json`
- Required search results: `required-search-results.json`
- Search/history transcripts: `search-command-transcripts.json`
- Grok artifact summaries: `grok-artifact-summaries.json`
- Wrapper origin search: `wrapper-origin-search.json`
- Shell history search, redacted: `shell-history-grok-search.redacted.json`
- Direct xAI API smoke artifacts: `live-smoke/xai-env-preflight.json`, `live-smoke/xai-models-smoke.json`, `live-smoke/xai-direct-json-chat-smoke.json`
- Hermes provider smoke artifact: `live-smoke/hermes-xai-json-smoke.json`
- Compact decomposer smoke artifacts: `live-smoke/compact-decomposer/`

## Pre-repair source findings

1. At RCA time, `arena/project_model_llm.py` contained only recorded/fixture/noop output helpers. It did not define a direct xAI/OpenAI-compatible API client, a Hermes provider adapter, or a Grok CLI adapter.
2. At RCA time, `arena/project_decomposer_ai.py` dispatched modes as follows: fixture built deterministic fixture output, recorded loaded JSON from disk, off built a no-op blocker model, and live raised `RuntimeError("live mode requires explicit CLI --allow-live and is not implemented for CI")`.
3. `arena/project_model_cli.py` enforced `--allow-live` for live mode, but after that guard it called `build_project_model_snapshot(... llm_mode="live" ...)`, which reached the then-unimplemented live branch.
4. The prior review artifact states accepted snapshots use `--llm-mode recorded --model-output ...repaired.json`; that is consistent with current source.

## Prior Grok wrapper findings

The held-out Grok wrapper artifacts both have top-level keys `text`, `stopReason`, `sessionId`, `requestId`, and `thought`. In both cases `text` is empty and `stopReason` is `Cancelled`, while `thought` shows Grok began reasoning. There is no final JSON response to parse or gate.

The exact argv that produced those wrapper files is not recorded in the repository artifacts. Searching wrapper session/request IDs and filenames found references in review input/report files, but no reproducible command transcript. Redacted shell history only contained `grok` and `grok login`. The safest evidence-backed statement is: the wrappers came from an out-of-band Grok Build/CLI-style interaction, but the exact command is missing from the artifacts and must be treated as an RCA evidence gap.

## Live smoke results

### Direct xAI API

- Credential presence: `XAI_API_KEY` present in `/home/leonb/.hermes/.env`; value not printed.
- `GET https://api.x.ai/v1/models`: HTTP 200.
- Selected model: `grok-4.20-0309-non-reasoning`.
- Tiny JSON chat completion: HTTP 200, finish reason `stop`, parsed JSON `{"ok": true, "path": "direct-xai-api"}`.

### Hermes xAI provider

- `hermes auth status xai`: logged in.
- Redacted model config currently defaults to `['model:', '  default: gpt-5.5', '  provider: openai-codex', '  base_url: https://chatgpt.com/backend-api/codex', '  api_mode: codex_responses']`.
- `hermes --provider xai -m grok-4.20-0309-non-reasoning -z ...`: exit 0, parsed JSON `{"ok": true, "path": "hermes-xai-provider"}`.

### Compact decomposer direct xAI smoke

- Direct xAI generated valid JSON for a tiny repository packet: HTTP 200, finish reason `stop`.
- Recorded ingestion through `arena.project_model_cli snapshot --llm-mode recorded` ran and produced a gate report.
- Gate result: `passed=false`, violation count 9.
- This proves the API can return model JSON and the Build Arena ingestion/gate path can process it. It does not prove semantic adequacy of the live output; the gate correctly failed the first compact output.

## Hypothesis verdicts

See `hypotheses.json` for the structured table. Summary:

- Supported: H1, H2, H3, H5.
- Partially supported: H4.
- Not supported: H6.
- Inconclusive/non-root: H7.

## Root cause

Primary root cause before repair: Build Arena had never implemented a live-model adapter for the AI-first decomposer. `--allow-live` only bypassed the CLI spend guard; it did not create a live provider path.

Contributing causes:

1. Pilot evidence mixed two concepts: out-of-band model generation through Grok/Opus tooling and Build Arena's own decomposer invocation path.
2. Wrapper outputs with empty text and `stopReason: Cancelled` were stored as evidence, but no reusable command transcript or fail-closed wrapper parser existed.
3. The recorded replay path trusts arbitrary JSON shape until Pydantic/gate checks run; wrapper-shaped outputs are not rejected at the model-output boundary with a clear provider failure message.
4. The compact live output can be syntactically valid yet gate-failing, so live success must be defined as: provider returns non-empty parseable JSON, Build Arena records provider metadata/hashes, and the gate result is explicit. Gate failure must not be converted into acceptance.

## Smallest reliable path now

Use direct xAI's OpenAI-compatible API as the live Build Arena decomposer adapter, with Hermes provider support as a secondary smoke/proof path. Do not rely on Grok Build CLI/agent wrappers for acceptance.

Minimum implementation repair:

1. Add a small injectable direct xAI/OpenAI-compatible adapter in `arena/project_model_llm.py`.
2. Wire `llm_mode="live"` in `arena/project_decomposer_ai.py` to call that adapter only after the existing `--allow-live` CLI guard.
3. Fail closed on cancelled/empty wrapper-like outputs, internal-thought-only wrappers, invalid JSON, empty content, and truncation/length finish reasons.
4. Record provider/model/prompt/output hashes and live status in artifacts.
5. Keep fixture/recorded/off modes deterministic and CI-safe.

## Pre-live blockers beyond the API path

- Live decomposer adapter missing: closed for bounded read-only smoke by this repair; semantic live-output quality remains separately blocked by gate failures.
- Compact live model output gate failure: blocks claiming semantic decomposer adequacy from the first smoke; it does not block implementing a fail-closed live path.
- Project Model v1 shared contract ambiguity: blocks broader live loop promotion until the primary v1/v0 compatibility contract is explicit.
- Verification gap policy for live mutation: blocks worktree patch cycles and promotion until gap severity is tied to allowed actions.
- Related consumer/calibration repos have not yet been updated for v1: blocks cross-project readiness claims, not local Build Arena smoke repair.
- Exact Grok wrapper command missing: blocks full reconstruction of the prior failure command, but not the direct API repair because direct API health has been proven.

## Repair status after this RCA

The bounded repair slice has now been implemented test-first:

1. `tests/test_project_model_llm_live.py` covers cancelled/empty wrapper rejection, invalid JSON/empty content/truncation failures, provider metadata/hashing, and live CLI path wiring through an injectable OpenAI-compatible client.
2. `arena/project_model_llm.py` now defines `LiveProjectModelLLM` with xAI/OpenAI-compatible defaults for a direct xAI path.
3. `arena/project_decomposer_ai.py` now routes `llm_mode="live"` to `LiveProjectModelLLM` after the CLI's existing `--allow-live` guard.
4. Targeted verification passed with `uv run pytest tests/test_project_model_llm_live.py -q` and the broader decomposer/CLI/v0/v1 targeted suite.
5. A tiny live CLI smoke under `live-smoke/live-cli-after-fix/` reached the provider and emitted a Build Arena snapshot/gate report. The command exited non-zero because the model output gate failed, which is the intended fail-closed behavior for semantically inadequate live output.

This closes the missing-adapter root cause for bounded read-only smoke. It does not close the semantic-quality, v1 consumer adoption, calibration, graph-indexing, or verification-gap mutation-policy blockers listed in the readiness register.
