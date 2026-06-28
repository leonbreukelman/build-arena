# Opus review request — propose-only remediation

You are the independent certifier for Build Arena Track F.

Repository: `/home/leonb/projects/build-arena-retire-apply-promote`
Branch: `retire/apply-promote-machinery`
Base: `f1bb4ac4780d6ddfdd86c059e3cd70e7b0f71ed3`

Task: review the current uncommitted diff against HEAD. Do not modify files.

User intent:
- Build Arena must be propose-only.
- Target apply/promote machinery must be deleted, not hidden behind flags.
- Retired modules must be unimportable and not invokable.
- `arena.proposal_run` and `arena.dream_run` must still work.
- Keep shared/non-exclusive modules used by propose-only lanes.
- Add a neutral incident/remediation record for the 2026-06-28 local `fmc-mcp` mutation.

Retired roots/delete set recorded by trace:
- `arena.repo_goal_loop`
- `arena.patch_gate`
- `arena.runners.diff_proposer`
- `arena.proposal_candidate_runner`

Shared set recorded by trace is in `.arena/runs/retire-apply-promote-20260627/evidence/phase-a-import-trace.json`.

Review focus:
1. Does the diff actually delete the target apply/promote roots and their exclusive tests?
2. Does `tests/test_apply_promote_retired.py` fail if a retired module returns or if an apply/promote console entrypoint is registered?
3. Are current README/AGENTS/project-brief/readiness docs updated to propose-only without presenting the retired loop as current runnable guidance?
4. Are `proposal_run` and `dream_run` preserved?
5. Are there remaining Python imports/entrypoints that would let Build Arena apply/promote a target repo through the retired machinery?
6. Is the incident spec neutral and accurate enough for survivorship-bias protection?

Local gate results already observed before this review:
- `uv run pytest tests/test_apply_promote_retired.py -q` => passed
- `uv run pytest tests/test_project_status_docs.py -q` => passed
- `uv run pytest tests/test_worktree_cycle_evidence.py -q` => passed
- `uv run pytest tests -q` => passed
- `uv run pytest tests/test_proposal_run.py -q` => passed
- `uv run pytest tests/test_dream_run.py -q` => passed
- `uv run ruff check .` => passed
- `uv run pyright` => passed with only the new-version warning

Return JSON only:
{
  "verdict": "PASS" | "REVISE",
  "blockers": ["..."],
  "must_patch_before_merge": ["..."],
  "non_blocking_notes": ["..."],
  "evidence_checked": ["..."]
}
