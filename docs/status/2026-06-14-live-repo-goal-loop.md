# Live repo-goal loop production-readiness status — 2026-06-14

## Status

`arena.repo_goal_loop` is now wired for bounded production-live execution:

- live Project Model decomposition is selectable with `--decompose-mode live`;
- live LLM diff proposal is selectable with `--apply-mode live_diff`;
- live execution fails closed unless `--allow-live` and `--live-model` are explicit;
- live diff proposal requires a non-default target repo `.arena/goal.toml`;
- live candidates must have deterministic verification commands before selection;
- patch/provenance artifacts are preserved outside temporary worktrees;
- fmc-mcp has a project goal config committed at `25f445806d5221f21d7ac675799db5c30499f1b7`.

## Verified run

Latest live fmc-mcp dry-run:

```text
/home/leonb/projects/build-arena/.arena/runs/fmc-mcp-live-20260614T174137Z
```

Observed stages:

1. `RUN_STARTED` — live decomposition and `live_diff` apply enabled.
2. `DECOMPOSITION_COMPLETED` — xAI model `grok-4.20-0309-non-reasoning`, gate passed, zero violations.
3. `CANDIDATE_SELECTED` — selected `agent.agents-md.missing` for `AGENTS.md`.
4. `CANDIDATE_APPLIED` — live diff patch applied in isolated worktree and preserved to run artifacts.
5. `CANDIDATE_VERIFIED` — `test -s AGENTS.md` and `arena.markdown_links` both exited 0.
6. `CANDIDATE_PACKAGED` — dry-run package only, no promotion.
7. `RUN_ENDED` — one cycle complete, promotions 0 by dry-run design.

## Gates green

Build Arena:

```text
uv run pytest tests -q
uv run ruff check .
uv run pyright
```

fmc-mcp:

```text
uv run ruff check .
uv run python -m pytest -q
uv run python -m mypy src tests
```

## Operator command for actual production promotion

```bash
cd /home/leonb/projects/build-arena && \
uv run python -m arena.repo_goal_loop \
  --project /home/leonb/projects/fmc-mcp \
  --goal 'Improve fmc-mcp with bounded, verified, repository-grounded changes using live LLM decomposition and live LLM diff proposal.' \
  --artifacts-root /home/leonb/projects/build-arena/.arena/runs/fmc-mcp-production-live-$(date -u +%Y%m%dT%H%M%SZ) \
  --max-cycles 1 \
  --decompose-mode live \
  --apply-mode live_diff \
  --allow-live \
  --live-provider xai \
  --live-model grok-4.20-0309-non-reasoning \
  --live-max-tokens 12000 \
  --test-command 'uv run python -m pytest -q' \
  --allow-promotion \
  --no-dry-run
```

## Boundary

Independent Opus review accepted the implementation for the bounded fmc-mcp production-live command. One minor patch-provenance robustness note was patched after review: repaired Markdown candidates now fail closed if no current diff can be recorded.

This is ready for a bounded fmc-mcp production-live cycle. It is not a claim that broad unattended cross-repo autonomy is solved.
