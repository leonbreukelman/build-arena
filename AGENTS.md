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

## Current implementation status

Phase 1-4 foundation is implemented and verified. The loop uses JSONL events as canonical state, locked git worktrees for cycle isolation, ff-only promotion foundation, live wall-clock budget checks, and hard divergence halts.

The post-Phase-4 AI-first decomposer is also implemented. AI decomposer snapshots now write `project-model-v1.json` as the primary Project Model v1 enriched artifact and `project-model-v0.json` as compatibility output for v0 consumers. `LiveProjectModelLLM` provides the direct xAI/OpenAI-compatible bounded live path behind the CLI `--allow-live` guard.

The pre-live readiness register at `docs/verification/2026-06-05-pre-live-readiness-register.json` remains `not_ready_blockers_remain`. Build Arena is not ready for broad autonomous live loops: dry-run hypothesis generation from v1, worktree patch cycles, and promotion remain blocked until readiness blockers close. The dashboard control plane, rollback endpoint, and live subscription-CLI subprocess execution remain unimplemented.

## Commands

- `make generated` — regenerate LinkML artifacts.
- `uv run pytest tests -q` — run tests.
- `uv run ruff check .` — lint source.
- `uv run pyright` — type-check source.
- `uv run python scripts/rebuild_calibration.py` — rebuild synthetic calibration repo and patch catalog.
- `uv run python scripts/update_scorer_lock.py` — update `.arena/scorer.lock.toml` after intentional scorer source changes.
- `uv run python -m arena.decomposer --project <repo> --output <model.json>` — emit the deterministic scanner model.
- `uv run python -m arena.decomposer --project <repo> --format project-model-v0 --source-task <task> --output <model-v0.json>` — emit Project Model v0 compatibility output.
- `uv run python -m arena.project_model_cli snapshot --project <repo> --artifacts-root <dir> --project-id <id> --goal <goal> --llm-mode fixture` — build AI-first snapshot artifacts without live provider calls.
- `uv run python -m arena.project_model_cli snapshot --project <repo> --artifacts-root <dir> --project-id <id> --goal <goal> --llm-mode live --allow-live` — run a bounded read-only live smoke only when explicitly authorized.
- `uv run python -m arena.project_model_cli gate --snapshot <manifest.json>` — rerun the deterministic gate for a snapshot manifest.
- `uv run python -m arena.project_model_cli graph --project <repo> --output <graph.json>` — emit the project graph sidecar.
