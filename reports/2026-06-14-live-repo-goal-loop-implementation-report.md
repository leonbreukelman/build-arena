# Build Arena live repo-goal loop implementation report — 2026-06-14

## Blunt answer

The repo-goal loop was not production-live. It was wired to look like a loop, but it hard-pinned the Project Model snapshot to fixture mode and the apply phase to deterministic/offline patching. That meant the loop could rank and dry-run candidates, but it could not use a real LLM end-to-end for decomposition plus proposal the way `live` was supposed to mean.

This report covers the implementation that removes that blocker and the verification run against `fmc-mcp`.

## What was broken from code inspection

1. `arena.repo_goal_loop` called `build_project_model_snapshot(... llm_mode="fixture" ...)` unconditionally.
2. Candidate apply was hard-wired to `_deterministic_apply`; there was no repo-goal CLI path to live diff proposal.
3. Live model settings were not threaded through the loop; max-token control was missing for the decomposer and proposer path.
4. `live_diff` had no fail-closed requirement for a project `.arena/goal.toml`; without that, the patch gate would use defaults rather than repo-specific production boundaries.
5. Candidate selection could spend a live diff call on a candidate with no deterministic verification commands.
6. Repo facts included hidden cache Markdown (`.pytest_cache/README.md`), poisoning live documentation prompts with non-source paths.
7. Live Markdown proposals could fail deterministic link validation because the model shortened paths (`index.md`, `fmc_mcp/config.py`) instead of exact repo-relative paths.
8. Live proposal patches were stored only inside the temporary worktree, so a successful dry-run could lose its patch/provenance artifact when the worktree was cleaned.

## What changed

Build Arena:

- Added repo-goal loop modes:
  - `--decompose-mode fixture|recorded|off|live`
  - `--apply-mode deterministic|live_diff`
  - `--allow-live`
  - `--live-provider`
  - `--live-model`
  - `--live-base-url`
  - `--live-api-key-env`
  - `--live-max-tokens`
- Live modes now fail closed unless `--allow-live` and an explicit `--live-model` are supplied.
- `live_diff` now requires a non-default project `.arena/goal.toml` before any live proposal call.
- `repo_goal_loop` now emits live mode/provider/model metadata in `RUN_STARTED` and live decomposition metadata in `DECOMPOSITION_COMPLETED`.
- `repo_goal_loop` now feeds live Project Model output into intake/ranking/proposal, then feeds the selected proposal candidate into the live diff proposer transport.
- Candidate selection skips unverified candidates instead of spending a live call on them.
- Live-applied patches and provenance are preserved under the run artifact directory: `cycle-N/candidate-artifacts/`.
- Repo facts now exclude hidden/cache directories and include source-file paths so live documentation proposals can cite exact repo-relative source paths.
- Diff proposer prompts now explicitly instruct exact Markdown/source path usage.
- Diff proposer now repairs unambiguous shortened Markdown references after apply and before validation, then records the repaired actual patch.
- CLI snapshot path also exposes `--live-max-tokens`.

fmc-mcp:

- Added `.arena/goal.toml` with single-file diff caps, read-only boundaries, and project commands.
- Fixed an existing mypy fixture annotation in `tests/test_resources.py` so the repo quality gate is clean.
- Committed in `fmc-mcp`: `25f445806d5221f21d7ac675799db5c30499f1b7 chore: add Build Arena goal config`.

## Verification evidence

Build Arena gates:

```text
uv run pytest tests -q
... 457 tests passed

uv run ruff check .
All checks passed!

uv run pyright
0 errors, 0 warnings, 0 informations
```

fmc-mcp gates:

```text
uv run ruff check .
All checks passed!

uv run python -m pytest -q
19 passed in 0.04s

uv run python -m mypy src tests
Success: no issues found in 11 source files
```

Secret-shape scan on Build Arena diff:

```text
secret-shape scan clean
```

## Live fmc-mcp dry-run verification

Run root:

```text
/home/leonb/projects/build-arena/.arena/runs/fmc-mcp-live-20260614T174137Z
```

Command used:

```bash
uv run python -m arena.repo_goal_loop \
  --project /home/leonb/projects/fmc-mcp \
  --goal 'Improve fmc-mcp with bounded, verified, repository-grounded changes using live LLM decomposition and live LLM diff proposal.' \
  --artifacts-root /home/leonb/projects/build-arena/.arena/runs/fmc-mcp-live-20260614T174137Z \
  --max-cycles 1 \
  --decompose-mode live \
  --apply-mode live_diff \
  --allow-live \
  --live-provider xai \
  --live-model grok-4.20-0309-non-reasoning \
  --live-max-tokens 12000 \
  --test-command 'uv run python -m pytest -q'
```

Observed stages:

1. `RUN_STARTED`: live decomposition and `live_diff` apply enabled; dry-run true.
2. `DECOMPOSITION_COMPLETED`: provider `xai`, served model `grok-4.20-0309-non-reasoning`, gate passed true, violation count 0.
3. `CANDIDATE_SELECTED`: documentation candidate `agent.agents-md.missing`, target `AGENTS.md`.
4. `CANDIDATE_APPLIED`: live diff proposer produced and applied a patch; patch and provenance preserved.
5. `CANDIDATE_VERIFIED`: deterministic verification passed:
   - `test -s AGENTS.md` exit 0
   - `python3 -m arena.markdown_links --repo . --path AGENTS.md` exit 0
6. `CANDIDATE_PACKAGED`: not promoted because this was a dry-run.
7. `RUN_ENDED`: cyclesRun 1, promotions 0, halted by max-cycle budget.

Preserved artifacts:

```text
/home/leonb/projects/build-arena/.arena/runs/fmc-mcp-live-20260614T174137Z/cycle-1/candidate-artifacts/hyp-goal-cycle-1-48f67a1f3007.patch
/home/leonb/projects/build-arena/.arena/runs/fmc-mcp-live-20260614T174137Z/cycle-1/candidate-artifacts/hyp-goal-cycle-1-48f67a1f3007.patch.provenance.json
/home/leonb/projects/build-arena/.arena/runs/fmc-mcp-live-20260614T174137Z/loop-events.jsonl
```

## Production-live command

This is the command that actually allows promotion into `fmc-mcp` if the selected candidate verifies:

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

## Current readiness statement

Independent Opus review result: `ACCEPT`. Opus found no blockers for the bounded fmc-mcp production-live command. It raised minor robustness notes around Markdown repair; the recorded-patch fallback was hardened so a repaired Markdown candidate now fails closed if no current diff can be recorded.

Ready to run a bounded production-live fmc-mcp cycle with explicit live spend and explicit promotion gates. The verified dry-run proved the actual live decomposer and actual live diff proposer path, not fixture output.

Not claimed: broad unattended autonomous loops across arbitrary repos. This is bounded repo-goal execution with one-cycle budget, project goal config, deterministic patch gate, verification commands, and promotion guard.
