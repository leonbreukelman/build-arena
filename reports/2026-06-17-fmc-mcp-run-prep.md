# fmc-mcp Build Arena run prep — 2026-06-17

## Owner outcome

Prepared for a bounded, supervised Build Arena run against `<projects>/fmc-mcp`.

Run readiness: technically ready for a bounded attempt, with two real gates before I execute the live production command:

1. API spend: live decomposition + live diff proposal will call xAI/Grok.
2. Target mutation: `--allow-promotion --no-dry-run` can advance local `fmc-mcp` `main` by fast-forward merge if a candidate passes gates.

This is not broad unattended autonomy. A zero-promotion safe failure is still a valid outcome.

## Current grounded state

### Build Arena repo

- Path: `<repo>`
- Branch/status: `main...origin/main`, clean
- Head: `e551d1a39486a843483b6bff64e776b9f0d1648d`
- Verification run from Build Arena:
  - `uv run pytest tests -q` — pass
  - `uv run ruff check .` — pass (`All checks passed!`)
  - `uv run pyright` — pass (`0 errors, 0 warnings, 0 informations`)

Relevant code facts checked:

- `arena/repo_goal_loop.py` CLI supports `--decompose-mode live`, `--apply-mode live_diff`, `--allow-live`, `--live-model`, `--live-max-calls`, `--allow-promotion`, and `--no-dry-run`.
- Live-call planning is deterministic: each cycle with live decomposition + live diff + one repair retry plans 3 live calls (`arena/repo_goal_loop.py:278-288`). So `--max-cycles 4` requires `--live-max-calls 12`.
- Live diff requires an explicit model and fails closed without one (`arena/runners/diff_proposer.py:64-82`).
- The behaviour gate command is parsed with `shlex.split`, not a shell (`arena/repo_goal_loop.py:703-712`), so do not pass a bare chained `cmd && cmd && cmd` string to `--test-command`. If the run must gate on multiple commands, wrap them as one executable invocation such as `bash -lc "cmd && cmd"`; `shlex.split` preserves that as `['bash', '-lc', 'cmd && cmd']`.
- Proposal plans now record base lineage and write a per-run registry at `<artifacts-root>/proposal-registry.jsonl`, but live diff application still passes `pending_proposals=tuple()` into `DiffProposerRunner` (`arena/repo_goal_loop.py:581-588`). That means prior stale proposal branches are known context for us, not yet automatically fed to the live proposer.

### Target repo: fmc-mcp

- Path: `<projects>/fmc-mcp`
- Branch/status: `main...origin/main [ahead 1]`, clean
- Head: `25f445806d5221f21d7ac675799db5c30499f1b7`
- Latest local commit: `25f4458 chore: add Build Arena goal config`
- `.arena/goal.toml` is present and tracked in HEAD.
- Existing stale proposal worktrees/branches remain:
  - `ba/fmc-mcp-grounded-proposal-20260613T051733Z` at `d60155b`
  - `ba/fmc-mcp-grounded-proposal-20260613T052136Z` at `d60155b`
  - `ba/fmc-mcp-grounded-proposal-20260613T052457Z` at `d60155b`
  - `ba/fmc-mcp-proposal-20260612T025323Z` at `00a632a`

Target verification run:

```text
uv run ruff check . && uv run python -m pytest -q && uv run python -m mypy src tests
```

Result:

- Ruff: pass (`All checks passed!`)
- Pytest: pass (`19 passed`)
- Mypy: pass (`Success: no issues found in 11 source files`)

### Live-provider readiness

- `XAI_API_KEY` is absent from the current shell.
- `XAI_API_KEY` is listed and non-empty in `~/.hermes/.env`.
- Build Arena's resolver reads `~/.hermes/.env` directly without shell-sourcing (`arena/llm_adapter.py:130-144`), so this is usable by the CLI.
- Do not shell-source `~/.hermes/.env` for this run: direct shell sourcing failed on an unrelated line. That is not a Build Arena blocker because the Build Arena resolver is not using shell evaluation.

## Non-mutating rehearsal already run

Command shape exercised with fixture decomposition and deterministic apply, no live calls and no promotion:

```text
uv run python -m arena.repo_goal_loop \
  --project <projects>/fmc-mcp \
  --goal "Improve the read-only Cisco Firepower Management Center MCP server with bounded, verified, single-file changes that preserve local tests, lint, and typing." \
  --artifacts-root <repo>/.arena/runs/fmc-mcp-prep-20260617T193807Z \
  --profile active-development \
  --max-cycles 3 \
  --decompose-mode fixture \
  --apply-mode deterministic
```

Rehearsal result:

- Events: `<repo>/.arena/runs/fmc-mcp-prep-20260617T193807Z/loop-events.jsonl`
- `cyclesRun`: 3
- `promotions`: 0
- `halted`: `budget`
- `plannedLiveCalls`: 0
- Candidate gates passed in isolated worktrees for:
  - `agent.agents-md.missing` -> `AGENTS.md`
  - `decision.history.missing` -> `docs/decisions/index.md`
  - `ops.runbooks.missing` -> `docs/runbooks/index.md`
- Target repo remained clean after rehearsal.

Interpretation: local non-mutating mechanics work. Fixture mode only produced docs candidates; it does not prove a live code/component promotion.

## Recommended live command when explicitly authorized

Use a fresh artifact root; keep artifacts outside the target repo. This command is a real bounded production-live attempt: it can spend API calls and can mutate local `fmc-mcp` `main` if a candidate passes gates.

```bash
RUN_ID="fmc-mcp-live-$(date -u +%Y%m%dT%H%M%SZ)"
ARTIFACT_ROOT="<repo>/.arena/runs/${RUN_ID}"
GOAL="Improve the read-only Cisco Firepower Management Center MCP server with bounded, verified, single-file changes that preserve local tests, lint, and typing."

uv run python -m arena.repo_goal_loop \
  --project <projects>/fmc-mcp \
  --goal "$GOAL" \
  --artifacts-root "$ARTIFACT_ROOT" \
  --profile active-development \
  --max-cycles 4 \
  --decompose-mode live \
  --apply-mode live_diff \
  --allow-live \
  --live-provider xai \
  --live-model grok-4.20-0309-non-reasoning \
  --live-api-key-env XAI_API_KEY \
  --live-max-tokens 12000 \
  --live-max-calls 12 \
  --test-command 'bash -lc "uv run ruff check . && uv run python -m pytest -q && uv run python -m mypy src tests"' \
  --allow-promotion \
  --no-dry-run
```

Why these limits:

- `--max-cycles 4`: one more than the three docs candidates observed in the non-live rehearsal, so a single failed candidate does not end the run immediately.
- `--live-max-calls 12`: exact planned budget for four cycles with live decomposition, one live diff proposal, and one repair retry per cycle.
- `--test-command 'bash -lc "uv run ruff check . && uv run python -m pytest -q && uv run python -m mypy src tests"'`: one executable invocation accepted by the current behaviour gate parser, while enforcing the full target contract before any promotion. I tested the same `bash -lc` command in `<projects>/fmc-mcp`; ruff, pytest, and mypy all passed, and `shlex.split` preserves it as `['bash', '-lc', 'uv run ruff check . && uv run python -m pytest -q && uv run python -m mypy src tests']`.

## Immediate post-run checks

After any live attempt, run and preserve these results before reporting success/failure. The full ruff+pytest+mypy gate above protects promotion; this post-run command is still required as independent final confirmation on the target repo after the loop exits.

```bash
# Target repo state and verification
cd <projects>/fmc-mcp
git status --short --branch
git log -5 --oneline
uv run ruff check . && uv run python -m pytest -q && uv run python -m mypy src tests

# Build Arena event stream
cd <repo>
cat "$ARTIFACT_ROOT/loop-events.jsonl"
```

Owner-facing verdict rules:

- If `RUN_ENDED.promotions` is `0`, report safe failure / no production improvement.
- Do not call the run a success unless there is a `PROMOTED` event and target verification passes afterward.
- Do not call closed-loop autonomy proven unless a promotion is followed by a fresh `DECOMPOSITION_COMPLETED` / intake cycle before the next selection.

Local rollback note if a promoted local change later proves unwanted before push/PR: capture `git status --short --branch` and `git log -5 --oneline`, then use the target repo reflog to identify the pre-run `main` OID (`25f445806d5221f21d7ac675799db5c30499f1b7` at prep time) and reset local `main` back to it. Do not run that reset casually; it is destructive to local commits after the run and should be treated as a rollback action.

## Caveats to keep visible during the run

1. Local target branch is ahead of remote by one commit. This is acceptable for a local bounded run if intentional, but remote reproducibility still requires push/PR later.
2. Stale `ba/fmc-mcp-*` branches/worktrees exist from older proposal attempts. Do not delete them without explicit cleanup scope. Record them as known prior invisible work.
3. Registry primitives exist, but the live proposer is not yet automatically seeded with pending registry notes in current `repo_goal_loop.py`; avoid claiming duplicate/proposal-memory is solved end-to-end.
4. Broad unattended autonomy remains blocked by control-plane/rollback and real multi-cycle production proof gaps.

## Independent review

Reviewer: Claude Opus, fresh context.

- Initial source-reading review hit `error_max_turns`; artifact: `reports/2026-06-17-fmc-mcp-run-prep-opus-review.json`.
- Compact embedded-artifact retry returned `REVISE`; artifact: `reports/2026-06-17-fmc-mcp-run-prep-opus-review-retry.json`.
- Valid blocker patched: the original live command only gated promotion on pytest while the goal required tests, lint, and typing. The command now gates promotion on ruff + pytest + mypy through one `bash -lc` invocation compatible with `shlex.split`.
- Final compact rereview returned `PASS` with no blockers; artifact: `reports/2026-06-17-fmc-mcp-run-prep-opus-rereview.json`.
