# FMC MCP live Grok 4.3 blocker root-cause note

Date: 2026-06-12
Target repo: `/home/leonb/projects/fmc-mcp`
Target head: `00a632ac950a8c411f8d8ac90197e28191f58619`
Provider/model: xAI OpenAI-compatible, requested `grok-4.3`, served `grok-4.3`

## Issue description

A real live Grok 4.3 Build Arena run against `fmc-mcp` successfully reached the provider and produced Project Model artifacts, but the deterministic Project Model gate rejected both live decomposition attempts. Because the Project Model did not pass the gate, the process correctly stopped before live patch proposal or mutation.

Evidence:

- Smoke call passed with exact served model match: requested `grok-4.3`, served `grok-4.3`, finish reason `stop`.
- Attempt 1 artifact root: `.arena/artifacts/fmc-mcp-live-grok-4.3-20260612T011018Z/snapshot-f2d130ac98d4a482/`
  - Gate result: failed, 24 violations.
  - Violation classes: 6 `component_measurability`, 5 `contract_references`, 13 `edge_coverage`.
- Attempt 2 artifact root: `.arena/artifacts/fmc-mcp-live-grok-4.3-gate-aware-20260612T011226Z/snapshot-f3bc39509a473e51/`
  - Gate result: failed, 16 violations.
  - Violation classes: 2 `component_measurability`, 1 `contract_references`, 13 `edge_coverage`.
- Freshness for attempt 2 passed: snapshot head and target repo head both `00a632ac950a8c411f8d8ac90197e28191f58619`, no dirty paths.
- Read-only intake and handoff completed, but the handoff is explicitly non-authorizing and selected missing file `docs/index.md`.
- The current `DiffProposerRunner.apply()` requires the target path to already exist before requesting a diff, so it cannot currently produce a new-file proposal for `docs/index.md`.

## Problem statement

Build Arena cannot currently complete a live `fmc-mcp` flow from decomposition through proposal-in-hand because two seams still rely on assumptions that are false for the first real live target:

1. The live decomposer is asked to manually emit a gate-perfect contract graph. Grok 4.3 can produce plausible components, but it fails to enumerate every directed cross-component import edge as a contract and can reverse contract direction. The deterministic gate is therefore correct to block the model.
2. The intake layer can select a missing-file documentation improvement, but the live diff proposer runner only supports modifying an existing single target file. That leaves the top scorecard item un-runnable by the current proposal path even if the handoff is fresh.

The desired behavior is a simple, deterministic bridge:

- Let the LLM provide semantic grouping/responsibility hints.
- Let deterministic Build Arena code derive all mechanically knowable cross-component import contracts from the graph and component ownership.
- Let the proposal path handle a missing single target file by sending empty file contents and accepting a valid new-file unified diff, still behind boundary and patch-gate checks.

## Root cause

Primary root cause: Build Arena puts too much deterministic bookkeeping burden on the live LLM.

The gate already knows how to compute the cross-component import pairs it requires (`_component_pairs_for_import_edge`, `_edge_supports_contract`, `_check_owned_import_edge_coverage` in `arena/project_model_gate.py`). The prompt only tells the model to cite supporting edge IDs whose endpoints map to two components; it does not give a machine-readable table of `(edge_id, required_from_component, required_to_component)`, and the ingestion path does not repair/derive these contracts deterministically. A model can therefore produce semantically plausible components while failing exact edge-coverage bookkeeping.

Secondary root cause: intake and proposer capabilities are mismatched.

`arena.project_intake_scorecard` can select absence findings such as `docs/index.md` because missing docs are high-leverage for a new project. `arena.proposer_handoff` can encode that target. But `arena.runners.diff_proposer.DiffProposerRunner.apply()` checks `if not file_path.exists() or not file_path.is_file(): raise RunnerError(...)` before transport invocation. The proposal path therefore cannot produce a new-file documentation diff for the top intake result.

## Non-root causes

- xAI authentication/model availability: not root cause. Model list and smoke call confirmed `grok-4.3`.
- Target repo staleness: not root cause. Freshness passed and `fmc-mcp` stayed clean.
- Local fmc-mcp tests/lint/typecheck: not root cause. `pytest`, `ruff`, import smoke, and `python -m mypy` all passed with appropriate invocation.
- Secret leakage: not root cause. Final artifact scan was clean; an initial broad `sk-` regex hit was a false positive inside `high-risk-client`.

## Proposed simplest fix direction

1. Add deterministic Project Model contract closure after model-output ingestion and before gate/final identity:
   - For every owned cross-component import edge required by the gate, add or normalize a deterministic `Contract` in the correct direction.
   - Attach the deterministic contract ID back to the from/to components so component measurability sees contracts.
   - Keep raw model output unchanged on disk for audit; mark generated contract IDs distinctly, e.g. `contract.auto.<edge-id>`.
   - Do not relax the gate.

2. Add new-file support to the diff proposer runner for a single target path:
   - If the target file is missing but parent path is in-scope and boundary-safe, send empty `file_contents` to the transport.
   - Require the model to return a unified diff that creates exactly that file.
   - Let `validate_unified_diff` and `git apply --check` remain the proof.
   - Keep multi-file and protected-path rejection unchanged.

3. Add tests first:
   - Recorded/live-shaped model output with missing/reversed contracts becomes gate-passing because deterministic contract closure fills the mechanically knowable contracts.
   - Existing fixture behavior remains passing.
   - Diff proposer can apply a valid single new-file diff.
   - Diff proposer rejects new-file attempts under protected/read-only paths or multi-target hypotheses.

## Confidence

High confidence in the root cause from the saved artifacts and code path:

- The gate failures match exactly the deterministic edge-coverage/contract-reference checks in `project_model_gate.py`.
- The second prompt nudged the model toward better responsibilities, reducing measurability failures, but all 13 edge-coverage failures remained, confirming that exact contract closure is deterministic bookkeeping rather than semantic interpretation.
- The selected handoff target is absent and the runner has an explicit pre-transport existence check, so the proposal blocker is direct and mechanically reproduced by code inspection.
