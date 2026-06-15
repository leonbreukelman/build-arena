# Proposal registry, lineage, and repair-loop mechanics — 2026-06-15

## Why this page exists

The 2026-06-15 `fmc-mcp` live production pass failed safely but exposed autonomy gaps that were not visible enough to future runs:

- high-priority candidates could be skipped because their executable verification was empty;
- proposal attempts had no durable registry, so repeated runs could rediscover the same proposal;
- proposal artifacts did not carry enough git/snapshot lineage to prove they still applied to the same base;
- a live Markdown proposal with a bad path had no bounded repair retry;
- model-level and multi-file findings degraded to invisible `no_single_file_target` skips.

## Current implementation rules

1. Candidate selection emits `CANDIDATE_SKIPPED` for positive-score candidates that are skipped because they were already tried, have no plan candidate, or have empty verification.
2. Component findings (`code.component.untested.*`) now route through `component_verification` before the generic-file fallback and receive load-bearing quality-gate commands from the intake `verification.quality-gates.present` finding.
3. Proposal plans carry:
   - `baseLineage` at plan level;
   - candidate `target_paths`;
   - candidate `base_lineage`;
   - `intent_hash`;
   - `proposal_key`;
   - `registry_status`.
4. The JSONL proposal registry can mark proposal keys as pending, duplicate, failed/applied/promoted/rejected, and can fail lineage checks on base-head mismatch.
5. Live diff proposal has one bounded repair retry per cycle. The retry gets the previous patch-gate/Markdown-gate error as `repair_context` and is counted in `plannedLiveCalls`.
6. Markdown reference repair can collapse an accidental doubled path segment such as `src/src/fmc_mcp/config.py` to `src/fmc_mcp/config.py` only when the collapsed path uniquely exists. It preserves legitimate existing paths such as `src/src/real.py`.
7. Multi-file component findings produce a multi-target proposal contract (`target_paths`) instead of silently skipping. The current live diff runner remains single-target; promotion/boundary checks are target-set aware.
8. Model-level backlog candidates are only created for findings explicitly marked `safe_to_patch_docs_only`; advisory-only architecture findings do not outrank runnable code work.

## Still not broad-autonomy proof

This implementation improves bounded production readiness, but broad unattended production still needs separate proof:

- real target-project production promotion, not just fixture/dry-run proof;
- a UI/control-plane and rollback operation path;
- registry status updates for every loop state (`applied_in_worktree`, `failed_gate`, `promoted`) in the production loop;
- multi-file apply support beyond the contract/selector/promotion boundary;
- a live semantic verifier/ablation gate if that becomes load-bearing.

## Verification commands used for this implementation

```text
uv run python -m pytest tests/test_repo_goal_loop.py tests/test_proposal_domains.py tests/test_proposal_planner.py tests/test_proposal_plan_schema.py tests/test_diff_proposer.py -q
uv run python -m pytest tests/test_agent_wiki.py tests/test_proposal_registry.py tests/test_proposal_candidate_runner.py tests/test_proposal_ranker.py tests/test_project_intake_scorecard.py tests/test_worktree_cycle_evidence.py -q
```
