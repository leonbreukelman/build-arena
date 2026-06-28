# Propose-only remediation — 2026-06-27

Status: implementation record for apply/promote retirement.

## Context

A local `fmc-mcp` production run at `2026-06-28T00:47:22Z` invoked the Build Arena apply/promote path with live decomposition, live diff application, and promotion enabled. That path could write to and advance a target repository. The run advanced local `fmc-mcp` `main` from `25f445806d5221f21d7ac675799db5c30499f1b7` to `cbe8a3843b64de4f9d8c3d910d84aa536216cad8`.

That behavior violated the current Build Arena policy: Build Arena's live lanes are propose-only. The system may emit `proposal.md` through `arena.proposal_run` and `experiment.md` through `arena.dream_run`; it must not apply or promote code to a target repository.

## Remediation

This change removes the target apply/promote machinery instead of disabling it behind flags. A present module is an available module, so the retired roots are deleted and guarded by regression tests.

Deleted modules:

- `arena.repo_goal_loop`
- `arena.patch_gate`
- `arena.runners.diff_proposer`
- `arena.proposal_candidate_runner`

Deleted exclusive tests:

- `tests/test_repo_goal_loop.py`
- `tests/test_patch_gate.py`
- `tests/test_diff_proposer.py`
- `tests/test_proposal_candidate_runner.py`

Additional test cleanup removed the diff-proposer-only scenario from `tests/test_worktree_cycle_evidence.py` while preserving the worktree/evidence coverage that does not depend on the retired runner.

New guard:

- `tests/test_apply_promote_retired.py` asserts the retired modules are absent, unimportable, not invokable with `python -m`, and not registered as console entrypoints.

## Trace result

Trace base: `f1bb4ac4780d6ddfdd86c059e3cd70e7b0f71ed3`.

Specified roots:

- `arena.repo_goal_loop`
- `arena.patch_gate`
- `arena.runners.diff_proposer`

The trace also expanded the retired root set to include `arena.proposal_candidate_runner`, because it was a target apply entrypoint that drove the retired diff proposer.

Delete set:

- `arena.patch_gate`
- `arena.proposal_candidate_runner`
- `arena.repo_goal_loop`
- `arena.runners.diff_proposer`

Shared/kept set:

- `arena.advisory_backlog`
- `arena.architecture_fitness`
- `arena.boundary`
- `arena.ci_workflow`
- `arena.fingerprints`
- `arena.generated.models`
- `arena.graph_slice`
- `arena.llm_adapter`
- `arena.markdown_links`
- `arena.project_decomposer_ai`
- `arena.project_encyclopedia`
- `arena.project_graph`
- `arena.project_intake_scorecard`
- `arena.project_iteration_readiness`
- `arena.project_meta_decomposer`
- `arena.project_model_gate`
- `arena.project_model_llm`
- `arena.project_model_v1`
- `arena.project_probe_runner`
- `arena.project_snapshot`
- `arena.proposal_domains`
- `arena.proposal_planner`
- `arena.proposal_ranker`
- `arena.proposal_registry`
- `arena.repo_facts`
- `arena.worktrees`
- `scorer.goal_config`

`arena.runners.base` was reachable from the retired roots but was not deleted: it is a support-only module used by the historical/internal runner router tests and does not expose an apply/promote entrypoint by itself.

## Target repository recovery

The local `fmc-mcp` recovery target is the parent commit:

- before out-of-policy commit: `25f445806d5221f21d7ac675799db5c30499f1b7`
- out-of-policy local commit: `cbe8a3843b64de4f9d8c3d910d84aa536216cad8`

The recovery operation is intentionally separate from this Build Arena PR because it is a destructive `git reset --hard` in the target repository. It must run only after operator confirmation and after recovery evidence is captured. The required recovery check is: confirm local `fmc-mcp` HEAD is `cbe8a3843b64de4f9d8c3d910d84aa536216cad8`, confirm its parent is `25f445806d5221f21d7ac675799db5c30499f1b7`, then reset local `main` to the parent without pushing any remote.

## Current policy after remediation

- `arena.proposal_run` may emit `proposal.md`.
- `arena.dream_run` may emit `experiment.md`.
- Build Arena must not apply a patch to a target repository.
- Build Arena must not promote or advance a target repository baseline.
- Historical reports and wiki pages that mention the old apply/promote loop are point-in-time evidence, not runnable guidance.
