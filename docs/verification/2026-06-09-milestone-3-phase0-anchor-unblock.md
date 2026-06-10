# Build Arena Milestone 3 Phase 0 Evidence

Date: 2026-06-10T04:11:14Z
Kanban card: `t_6ff0635f` — BA-M3-00 Phase 0: Anchor roadmap and unblock worktree-only cycles

## Owner authorization

Leon explicitly authorized unblocking the Build Arena Kanban work and starting execution. The root tracker remains blocked so it does not dispatch as a worker task. Phase 0 is the only running card; downstream implementation cards remain blocked until Phase 0 is complete and reviewed.

## Phase 0 scope

Phase 0 is documentation and governance alignment only. No scorer, verifier, schema, generated model, runner, or loop behavior was changed in this phase.

## Source artifacts landed or staged

- `docs/verification/2026-06-09-fable-build-arena-strategy-review.md`
- `docs/verification/2026-06-09-fable-milestone-3-plan-comparison.md`
- `docs/verification/2026-06-09-fable-roadmap-kanban-review.md`
- `docs/plans/2026-06-09-milestone-3-worktree-cycles-roadmap.md`

These files are repo-local and replace earlier temporary-source references for future workers.

## Governance decision

The pre-live readiness register still reports `not_ready_blockers_remain` for broad autonomy. Phase 0 narrows the Milestone 3 path:

- Broad autonomous live loops remain not ready.
- Decomposition-informed Project Model v1 hypothesis generation and promotion remain blocked.
- Naive Milestone 3 worktree-only cycles are not blocked by Project Model v1 cross-repo adoption, graph/indexer depth, or live decomposer semantic quality gaps.
- Naive Milestone 3 worktree-only cycles remain blocked by internal Build Arena prerequisites:
  - generic scorer accepts per-repo `goal.toml` and is no longer calibration-repo hardcoded;
  - fail-closed diff proposer and patch gate pass fake-transport tests;
  - per-repo boundary/read-only/out-of-scope config exists for the selected pilot repo.

## Selected pilot repo

Selected pilot: `/home/leonb/projects/fmc-mcp`

Evidence:

```text
$ git -C /home/leonb/projects/fmc-mcp rev-parse --show-toplevel
/home/leonb/projects/fmc-mcp

$ git -C /home/leonb/projects/fmc-mcp status --short --branch
## main...origin/main

$ git -C /home/leonb/projects/fmc-mcp remote -v
origin	git@github.com:leonbreukelman/fmc-mcp.git (fetch)
origin	git@github.com:leonbreukelman/fmc-mcp.git (push)
```

Normal documented check command in the pilot README is `uv run pytest -v`, but the current environment does not expose the `pytest` console script through `uv run pytest` without explicit temporary test dependencies:

```text
$ uv run pytest -q
error: Failed to spawn: `pytest`
  Caused by: No such file or directory (os error 2)
```

The tests themselves pass when run via Python module invocation with explicit test dependencies, without dirtying the pilot repo:

```text
$ uv run --with pytest --with pytest-asyncio --with pytest-httpx python -m pytest -q
...................                                                      [100%]
19 passed in 0.04s

$ git status --short --branch
## main...origin/main
```

Phase 1 should encode this as the pilot check command unless a pilot `uv.lock`/dev environment is added later.

## Configured worktree root

Configured worktree root for Milestone 3 cycle worktrees: `/home/leonb/projects/build-arena/.arena/worktrees`

Rationale:

- It matches the active AGENTS rule that runner writes are restricted to `.arena/worktrees/<cycle_id>/`.
- It is outside the pilot repo, keeping `/home/leonb/projects/fmc-mcp` before/after `git status` audits clean.
- It is ignored by Build Arena git:

```text
$ git check-ignore -v .arena/worktrees .arena/worktrees/example
.gitignore:15:.arena/worktrees/	.arena/worktrees
.gitignore:15:.arena/worktrees/	.arena/worktrees/example
```

## Files updated in Phase 0

- `docs/verification/2026-06-05-pre-live-readiness-register.json`
  - Added `phase0Milestone3Update` with selected pilot, worktree root, and internal prerequisites.
  - Moved PMV1-002 and PMV1-003 to non-blocking ecosystem tracking.
  - PMV1-002 and PMV1-003 now set `blocksDryRunHypothesisGeneration=false`, `blocksWorktreeOnlyPatchCycle=false`, and `blocksPromotionMerge=false`; promotion remains blocked through Build Arena/internal readiness items rather than cross-repo adoption.
  - Scoped LIVE-002, GRAPH-001, and GAP-001 away from the naive worktree-only path.
  - Added M3-001 as the internal blocker for naive worktree-only cycles.
- `AGENTS.md`
  - Clarifies Phase 1-4 foundation is verified against the synthetic calibration repo and has not yet improved a real target repo.
  - Clarifies the Milestone 3 naive worktree-only path and ablation-advisory decision.
- `README.md`
  - Aligns owner-facing status with the Phase 0 readiness-register change.
- `docs/build-arena-project-brief.md`
  - Aligns fresh-agent orientation status and backlog wording.
- `docs/plans/2026-06-09-milestone-3-worktree-cycles-roadmap.md`
  - Records that Phase 0 execution has started while downstream cards remain blocked.

## Fable review

Fable reviewed the Phase 0 diff as Leon's representative and returned `ACCEPT_WITH_CHANGES` with no critical blockers. Required changes were applied before completion:

- Register step 4 no longer says it waits on gap-policy enforcement after GAP-001 was scoped away from naive cycles.
- This artifact explicitly records that PMV1-002/003 promotion blockers were flipped to `false` and why promotion remains blocked elsewhere.
- M3-001 now has a mechanical `proofCommand` plus a separate closure criterion.

Review artifact: `docs/verification/2026-06-09-fable-phase0-anchor-unblock-review.md`

## Verification completed

- `python3 -m json.tool docs/verification/2026-06-05-pre-live-readiness-register.json >/dev/null` — passed.
- Readiness-register blocker scan — passed: PMV1-002 and PMV1-003 no longer block dry-run/worktree/promotion; M3-001 remains the internal worktree blocker.
- Roadmap/card scan for dangling temporary source-file references — passed: `dangling_tmp_refs=0`.
- `git -C /home/leonb/projects/fmc-mcp rev-parse --show-toplevel` — passed: `/home/leonb/projects/fmc-mcp`.
- Pilot repo status before/after test command — clean: `## main...origin/main`.
- Pilot repo tests: `uv run --directory /home/leonb/projects/fmc-mcp --with pytest --with pytest-asyncio --with pytest-httpx python -m pytest -q` — passed: `19 passed in 0.04s`.
- Build Arena status-doc tests: `uv run pytest tests/test_project_status_docs.py -q` — passed: `6 passed`.
- Build Arena full tests: `uv run pytest tests -q` — passed.
- `git diff --check` — passed.
