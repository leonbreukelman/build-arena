# Grok Proposal Adapter Readiness Evidence — 2026-06-10

## Owner outcome

Status: ready to attempt a bounded, operator-authorized real run.

This does not mean Build Arena is ready for broad autonomous live loops, and it does not prove xAI/OpenRouter/provider acceptance. It means the Grok/OpenAI-compatible proposal adapter is wired into the proposal component, covered by no-network tests, and guarded so the first real provider attempt can fail cleanly instead of crashing the cycle.

## Scope completed

- Added shared OpenAI-compatible provider/client layer: `arena/llm_adapter.py`.
- Refactored `LiveProjectModelLLM` to use the shared client while preserving the existing decomposer `generate(prompt) -> dict` API.
- Added decomposer CLI switches:
  - `--live-provider`
  - `--live-base-url`
  - `--live-model`
  - `--live-api-key-env`
- Kept `--allow-live` as a live-spend gate and added an explicit `--live-model` gate for live mode.
- Added `OpenAICompatibleDiffTransport` for proposal diffs in `arena/runners/diff_proposer.py`.
- The proposal transport:
  - uses the shared OpenAI-compatible client;
  - asks for a unified diff only;
  - strips one surrounding markdown diff fence;
  - rejects empty/prose-only output before mutation;
  - converts provider/client `ValueError` failures into `RunnerError` so the router records a clean runner failure instead of crashing;
  - requires an explicit model/provider config when constructing a real client.
- Updated README, AGENTS.md, and project brief to use the precise readiness language.

## Opus review trail

Plan review:
- Artifact: `docs/verification/2026-06-10-opus-grok-proposal-adapter-plan-review.md`
- Verdict: ACCEPT_WITH_CHANGES.
- Required changes applied before coding: readiness wording changed to "ready to attempt"; fence handling decided as strip-then-gate; `~/.hermes/.env` fallback preserved; explicit model required for real attempts; mock provider tests scoped as request-construction proof.

Implementation review:
- Artifact: `docs/verification/2026-06-10-opus-grok-proposal-adapter-implementation-review.md`
- Verdict: ACCEPT_WITH_CHANGES.
- Blocking findings fixed after review:
  1. Real provider/client `ValueError` could escape the proposal transport and crash a cycle. Fixed by converting provider failures to `RunnerError`; covered by a real-client fake-urlopen test.
  2. Live mode could rely on an unverified fallback model. Fixed by requiring `--live-model` for decomposer live mode and by refusing to construct a real proposal transport without an explicit model/provider config.

Narrow re-review:
- Artifact: `docs/verification/2026-06-10-opus-grok-proposal-adapter-re-review.md`
- Verdict: ACCEPT_WITH_CHANGES, with no remaining blocker before the bounded-attempt readiness claim.
- Remaining caveat: proposal transport has no standalone operator CLI in this slice, so proposal-side real runs rely on the caller passing an explicit model/provider config. This is documented and tested at constructor level, but not yet a full run CLI.

## Verification commands run

All commands below were run from `/home/leonb/projects/build-arena` on branch `ba/model-agnostic-llm-adapters`.

```bash
uv run pytest tests/test_llm_adapter.py -q
# PASS: 8 passed

uv run pytest tests/test_project_model_llm_live.py tests/test_project_model_cli_ai.py tests/test_project_status_docs.py::test_documented_cli_surfaces_exist -q
# PASS: 18 passed

uv run pytest tests/test_diff_proposer.py -q
# PASS: 16 passed before Opus fixes; expanded test file included in full suite after fixes

uv run pytest tests -q
# PASS: full suite passed

uv run ruff check .
# PASS: All checks passed

uv run pyright
# PASS: 0 errors, 0 warnings, 0 informations

uv run python <no-network mocked OpenAICompatibleDiffTransport + DiffProposerRunner smoke>
# PASS: produced .arena/patches/hyp-smoke.patch, transport=openai_compatible_diff, model=grok-mock-served

uv run python -m arena.project_model_cli snapshot --project /home/leonb/projects/build-arena --artifacts-root /tmp/build-arena-live-gate-check --project-id build-arena --goal 'gate check' --llm-mode live
# PASS: exits 2 before live construction and mentions --allow-live

uv run python -m arena.project_model_cli snapshot --project /home/leonb/projects/build-arena --artifacts-root /tmp/build-arena-live-gate-check --project-id build-arena --goal 'gate check' --llm-mode live --allow-live
# PASS: exits 2 before live construction and mentions --live-model

git diff --check
# PASS

python3 secret-shape scan over tracked diff + new untracked files
# PASS: secret-shape scan clean
```

## Readiness conclusion

Ready to attempt a bounded, operator-authorized real run: yes.

Meaning of that yes:
- The decomposer live adapter is now operator-switchable and still requires `--allow-live` plus explicit `--live-model`.
- The proposal component now has a Grok/OpenAI-compatible live diff transport wired through the shared client.
- The no-network proposal path has been exercised end to end through transport → patch gate → git apply → provenance write.
- Provider errors and truncation fail closed as runner errors.

What remains unproven until the first authorized live smoke:
- xAI/OpenRouter accepts the exact request shape for the selected model.
- The selected Grok model emits a gate-valid unified diff for a real target file.
- The full autonomous loop with a live proposal model produces a verified improvement on a real target repo.

Broad autonomous live loops remain not ready until the readiness-register blockers close.
