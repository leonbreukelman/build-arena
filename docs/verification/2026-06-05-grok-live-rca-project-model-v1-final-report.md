# Grok Live RCA, Project Model v1, and Pre-Live Readiness Final Report

Date: 2026-06-05
Repository: `/home/leonb/projects/build-arena`

## Outcome

The requested bounded repair and readiness slice is complete and verified.

Implemented:

1. Fixed the AI decomposer live path with a small test-first direct xAI/OpenAI-compatible adapter.
2. Added fail-closed handling for empty/cancelled wrapper outputs, invalid JSON, empty live content, and truncated live responses.
3. Wired `llm_mode="live"` to the live adapter after the existing CLI `--allow-live` spend guard.
4. Added Project Model v1 as the primary enriched AI decomposer artifact while preserving Project Model v0 compatibility output.
5. Added the Project Model v1 JSON schema, spec, plan, and pre-live readiness register.
6. Inspected Elenchus Core and Arena Calibration and saved precise v1 adoption follow-up status.
7. Ran independent review, fixed review blockers, reran focused re-review, and completed full verification.

## Files changed

Implementation:

- `arena/project_model_llm.py`
- `arena/project_decomposer_ai.py`
- `arena/project_model_v1.py`

Tests:

- `tests/test_project_model_llm_live.py`
- `tests/test_project_model_v1_contract.py`

Specs/plans/schema:

- `docs/specs/2026-06-05-project-model-v1-shared-contract-spec.md`
- `docs/plans/2026-06-05-project-model-v1-and-pre-live-readiness-plan.md`
- `docs/schemas/project-model-v1.schema.json`
- `docs/prompts/2026-06-05-grok-live-rca-project-model-v1-pre-live-readiness.md`

Verification artifacts:

- `docs/verification/2026-06-05-grok-live-rca/`
- `docs/verification/2026-06-05-pre-live-readiness-register.json`
- `docs/verification/2026-06-05-related-repos-inspection.json`
- `docs/verification/2026-06-05-related-repos-v1-status.md`
- `docs/verification/2026-06-05-grok-live-rca-project-model-v1-final-report.md`

## Live decomposer path and failure handling

The new live adapter lives in `arena/project_model_llm.py` as `LiveProjectModelLLM`. It uses xAI's OpenAI-compatible `/chat/completions` endpoint by default and remains injectable for tests.

Fail-closed behavior now covers:

- wrapper-shaped output with empty `text`;
- wrapper-shaped output with `stopReason=Cancelled`;
- wrapper text that is not valid JSON;
- live provider envelope that is not JSON;
- live provider response with no choices;
- live response with `finish_reason=length`;
- live provider content that is empty;
- live provider content that is not Build Arena JSON.

The CLI spend guard remains in `arena/project_model_cli.py`; tests exercise the live path through injected adapters, so CI does not require paid API calls.

## Project Model v1

Build Arena now writes `project-model-v1.json` for every AI decomposer snapshot and marks it as the primary project-model artifact in `manifest.json`:

- `project_model_primary_path: project-model-v1.json`
- `project_model_v1_path: project-model-v1.json`
- `project_model_v0_path: project-model-v0.json`

The v1 artifact includes:

- project identity and goal;
- the full internal `ProjectModelSnapshot`;
- `ProjectGraph` nodes and edges with provenance refs;
- deterministic `GateReport`;
- git/dirty-state provenance;
- input/prompt/output/artifact hashes;
- model ids;
- derived-artifact strategy for JSONL events, SQLite projections, and Markdown summaries;
- v0 compatibility metadata.

The v1 schema validates emitted artifacts and rejects legacy v0-shaped JSON.

## RCA and readiness status

RCA summary:

- Direct xAI API worked.
- Hermes xAI provider worked for a tiny JSON request.
- The original Build Arena failure was a missing in-process live adapter plus weak wrapper-output boundary handling.
- The missing-adapter root cause is closed for bounded read-only smoke.
- Semantic live-output quality remains guarded by the gate; one tiny live CLI smoke reached the provider and then failed closed at the gate, which is expected for inadequate model output.

Pre-live readiness remains intentionally not-ready for broader live loops:

- `LIVE-002`: compact live output can be syntactically valid while gate-failing.
- `PMV1-002`: Elenchus Core v1 consumer adoption is still open.
- `PMV1-003`: Arena Calibration v1 fixture/evaluator adoption is still open.
- `GRAPH-001`: stronger parser/indexer integration is deferred and blocks mutation/promotion when graph adequacy is unproven.
- `GAP-001`: verification-gap live-action policy is specified but not yet enforced in mutation code.

## Related repository inspection

Elenchus Core:

- Path: `/home/leonb/projects/elenchus-core`
- Branch observed: `feat/project-model-v0-signals`
- Current status: v0-only Project Model consumer.
- Targeted verification: `uv run pytest tests/test_project_model_v0.py -q` passed.
- Follow-up: add a v1 parser/adapter and advisory checks for graph provenance, contracts, gate reports, held-out probes, verification gaps, and dirty-state fingerprint.

Arena Calibration:

- Path: `/home/leonb/projects/arena-calibration`
- Branch observed: `test/100-percent-coverage`
- Current status: clean working tree; v0-only Project Model fixture suite.
- Targeted verification: `uv run pytest tests/test_project_model_fixtures.py -q` passed; `uv run python exercise_project_model_fixtures.py --json` produced parseable JSON with 5 fixtures.
- Follow-up: add separate `fixtures/project_model_v1/` with v1 valid and adversarial cases.

Detailed status is saved in `docs/verification/2026-06-05-related-repos-v1-status.md`.

## Independent review

Initial independent review failed the staged change because the RCA document still described pre-repair live-path findings in present tense and claimed an `XAIProvider` class existed.

Fixes applied:

- Reframed RCA source findings as pre-repair/RCA-time evidence.
- Removed the `XAIProvider` class claim and described the actual `LiveProjectModelLLM` implementation.
- Updated `hypotheses.json` to add post-repair status and remove stale present-tense no-adapter/RuntimeError claims.

Focused independent re-review result:

```json
{
  "passed": true,
  "security_concerns": [],
  "logic_errors": [],
  "scope_concerns": [],
  "summary": "The staged RCA artifacts now frame the removed RuntimeError/no-client findings as RCA-time or pre-repair and reflect the new LiveProjectModelLLM live path, with no XAIProvider contradiction found."
}
```

## Final verification

Final verification commands completed successfully:

```text
uv run pytest tests -q
........................................................................ [ 43%]
........................................................................ [ 87%]
.....................                                                    [100%]

uv run ruff check .
All checks passed!

uv run pyright
0 errors, 0 warnings, 0 informations

python JSON validation
validated_json_files=50

staged secret/path scan
staged_paths=74
blocked_path_hits=[]
secret_hit_count=0
```

`git diff --cached --check` also passed.

## Commit readiness

This slice was committed locally as `08a3e29 [verified] add live xai decomposer and project model v1 readiness`. It was not pushed, merged, deployed, used to start a broader live loop, or used to enable worktree mutation/promotion.
