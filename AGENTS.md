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

## Cross-project intake and prioritization rule

1. For any Build Arena task that consumes, resumes, decomposes, audits, prioritizes, or plans work for a project, apply the `weighted-project-intake-prioritization` Hermes skill before selecting the first improvement. Use the skill's lightweight mode for trivial/narrow edits so this rule does not create unnecessary ceremony.
2. Treat documentation/project knowledge, reproducible verification, architecture/spec contracts, AI-agent usability, decision history, security hygiene, backlog governance, and operations/rollback as scorecard dimensions. Adjust weights by project phase instead of using one universal priority order.
3. Canonical project knowledge should live in versioned repo docs and agent instructions. GitHub Wiki or generated encyclopedia output may be used as a navigation layer, but not as the only source of truth unless explicitly mirrored/versioned.
4. The Build Arena backlog specification for this strategy is `docs/specs/2026-06-07-weighted-project-intake-prioritization.md`. It is not implemented yet; do not claim a scorecard CLI or gate exists until code and tests land.
5. Scorecard output is advisory until implemented and gated. It does not override anti-fabrication rules, protected-path boundaries, live-provider authorization gates, or the current broad-autonomy blockers.

## Current implementation status

Phase 1-4 foundation is implemented and verified against the synthetic calibration repo. The loop uses JSONL events as canonical state, locked git worktrees for cycle isolation, ff-only promotion foundation, live wall-clock budget checks, and hard divergence halts. It has not yet produced a verified improvement on a real target repo.

The post-Phase-4 AI-first decomposer is also implemented. AI decomposer snapshots now write `project-model-v1.json` as the primary Project Model v1 enriched artifact and `project-model-v0.json` as compatibility output for v0 consumers. `LiveProjectModelLLM` provides the direct xAI/OpenAI-compatible bounded live path behind the CLI `--allow-live` guard. The shared OpenAI-compatible LLM path is operator-switchable for decomposition and proposal transport by provider/base URL/model/API-key-env configuration; the proposal transport can request a unified diff from an explicit Grok/OpenAI-compatible model and then hands the output to the deterministic patch gate. With mock/no-network verification green, Build Arena is ready to attempt a bounded, operator-authorized real run, not an unattended broad live loop; provider acceptance remains unverified until live smoke and any real attempt still needs an explicit model ID plus call budget.

The pre-live readiness register at `docs/verification/2026-06-05-pre-live-readiness-register.json` remains `not_ready_blockers_remain`. Build Arena is not ready for broad autonomous live loops: decomposition-informed/v1 hypothesis generation, promotion, dashboard control plane, rollback endpoint, and live subscription-CLI subprocess execution remain blocked or unimplemented. Milestone 3 now separates a narrower naive worktree-only pilot path; that path is blocked only by internal Build Arena prerequisites (generic scorer, fail-closed proposer tests, and per-repo boundary config), not by Project Model v1 cross-repo adoption. The current ablation keyword gate is advisory for real cycles until a real ablation runner exists; it must not be treated as a load-bearing semantic gate for the Milestone 3 pilot.

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
- `uv run python -m arena.project_model_cli snapshot --project <repo> --artifacts-root <dir> --project-id <id> --goal <goal> --llm-mode live --allow-live --live-model <explicit-model>` — run a bounded read-only live smoke only when explicitly authorized; provider/base URL/API-key-env can also be selected with `--live-provider`, `--live-base-url`, and `--live-api-key-env`.
- `uv run python -m arena.project_model_cli gate --snapshot <manifest.json>` — rerun the deterministic gate for a snapshot manifest.
- `uv run python -m arena.project_model_cli graph --project <repo> --output <graph.json>` — emit the project graph sidecar.
