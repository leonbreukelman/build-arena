# AGENTS.md — Autonomous Build Arena

## Anti-fabrication rules (highest priority)

1. NEVER reason from an imagined file. Before quoting or editing any file content, read that exact path in the current turn.
2. NEVER guess at function/class/symbol existence. Inspect files or search first.
3. The scanner/scorer model must be rebuilt from filesystem and git ground truth. Cached projections are never authoritative.

## Boundary-violation rules

1. NEVER modify anything under `scorer/`, `verifier/`, or `schema/` as part of an arena-generated hypothesis. These paths are read-only to autonomous runners.
2. NEVER modify `.arena/scorer.lock.toml` from inside an arena cycle. Bumping the scorer requires a new run/operator action.
3. NEVER hand-edit files under `arena/generated/`. They are produced from `schema/arena.yaml` by `make generated`.
4. NEVER bypass `git worktree` for future APPLY/PROMOTE phases. Phase 1 tests may use temporary fixture repos only.

## Worktree rules for future runners

1. Runner writes are restricted to `.arena/worktrees/<cycle_id>/`.
2. Do not run `git checkout`, `git branch -f`, `git reset --hard`, `git rebase`, or `git push` inside a cycle worktree.
3. The promoter is the only component allowed to advance the internal baseline, and it must use `git merge --ff-only`.

## Current phase

Phase 3 hypothesizer + fingerprinting + runner-router contracts are implemented and verified. Intent embeddings are currently deterministic no-API stand-ins seeded by the pinned model name; live embedding execution is deferred. Do not implement dashboard, autonomous loop glue, promotion/rollback machinery, or live subscription-CLI subprocess execution until Phase 3 remains green and the next phase is explicitly started.

## Commands

- `make generated` — regenerate LinkML artifacts.
- `uv run pytest tests -q` — run tests.
- `uv run ruff check .` — lint source.
- `uv run pyright` — type-check source.
- `uv run python scripts/rebuild_calibration.py` — rebuild synthetic calibration repo and patch catalog.
- `uv run python scripts/update_scorer_lock.py` — update `.arena/scorer.lock.toml` after intentional scorer source changes.
