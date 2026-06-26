You are Opus reviewing a Build Arena production-run readiness artifact for Leon.

Do not use tools. Do not ask to read files. Judge only the embedded artifact below. Return only JSON.

Review target: a readiness artifact that tells the operator exactly what command to run for a real token-spending Build Arena production pass against fmc-mcp.

Primary questions:
1. Does the artifact clearly choose the correct run path and avoid confusing `proposal_run` with the production apply/verify/promote loop?
2. Is the complete command present and internally consistent?
3. Are the live/spend flags load-bearing in the described code contract, not inert?
4. Does the live-call ceiling match the stated max cycles and repair budget?
5. Does the command use the correct target source, given local fmc-mcp is ahead of origin and has `.arena/goal.toml`?
6. Is the promotion/test gate strong enough before local baseline mutation?
7. Does the report overclaim readiness, hide mutation/spend risk, or blur run verdict vs review verdict?
8. Are there corrections that must be patched before telling Leon we are ready?

Return JSON shape exactly:
{
  "verdict": "ACCEPT" | "ACCEPT_WITH_CORRECTIONS" | "REJECT",
  "blockers": ["..."],
  "must_patch_before_ready": ["..."],
  "non_blocking_notes": ["..."],
  "command_assessment": {
    "complete_command_present": true,
    "target_source_correct": true,
    "live_flags_load_bearing": true,
    "budget_math_correct": true,
    "promotion_gate_before_mutation": true,
    "run_vs_review_verdict_separated": true
  },
  "concise_owner_summary": "..."
}

Embedded artifact:

---BEGIN ARTIFACT---
# fmc-mcp Build Arena production-run readiness — 2026-06-26T17:31:18Z

## Verdict

Ready for one bounded local production pass, using the local target checkout, live xAI tokens, live decomposition, live diff proposal, deterministic gates, and local ff-only promotion.

This is not a remote/reproducible GitHub run yet. `<target-repo>` is one commit ahead of `origin/main`; the local commit contains the required `.arena/goal.toml`. A run against `https://github.com/leonbreukelman/fmc-mcp` would clone `origin/main` and miss that local goal config.

## Use this, not the URL clone

Target identity: `https://github.com/leonbreukelman/fmc-mcp`

Run target: `<target-repo>`

Reason: live diff mode requires `.arena/goal.toml` tracked in target `HEAD`; local `HEAD` is `25f445806d5221f21d7ac675799db5c30499f1b7`, while remote `HEAD`/`origin/main` is `d60155bf05841f97d5ec3ba1752e0b7f588d54ce`.

## Exact command

```bash
cd <build-arena-repo>
set -euo pipefail
set -a
. <build-arena-repo>/.env
set +a

RUN_ROOT="<build-arena-repo>/.arena/runs/fmc-mcp-production-live-$(date -u +%Y%m%dT%H%M%SZ)"
mkdir -p "$RUN_ROOT"

uv run python -m arena.repo_goal_loop \
  --project <target-repo> \
  --goal 'Improve the read-only Cisco Firepower Management Center MCP server with bounded, verified, repository-grounded changes using live LLM decomposition and live LLM diff proposal while preserving local tests, lint, and typing.' \
  --artifacts-root "$RUN_ROOT" \
  --profile production \
  --max-cycles 2 \
  --decompose-mode live \
  --apply-mode live_diff \
  --allow-live \
  --live-provider xai \
  --live-model grok-4.3 \
  --live-api-key-env XAI_API_KEY \
  --live-max-tokens 12000 \
  --live-max-calls 6 \
  --test-command 'bash -lc "uv run ruff check . && uv run python -m pytest -q && uv run python -m mypy src tests"' \
  --allow-promotion \
  --no-dry-run \
  2> >(tee "$RUN_ROOT/stderr.txt" >&2) | tee "$RUN_ROOT/stdout.json"
```

## What this command means

- No mock path: `--decompose-mode live`, `--apply-mode live_diff`, `--allow-live`, and explicit `--live-model grok-4.3`.
- Token spend is bounded by `--live-max-calls 6`.
- Planned live-call math from current code: `max_cycles * (1 live decomposition + 1 live diff + 1 repair retry)` = `2 * 3 = 6`.
- Promotion is enabled: `--allow-promotion --no-dry-run`. If a candidate passes its gates, the command may advance the local `fmc-mcp` `main` branch by ff-only merge from an isolated cycle worktree. It does not push to GitHub.
- The promotion behavior gate for code changes is the full target contract, wrapped as one `bash -lc` command because `repo_goal_loop` splits `--test-command` with `shlex.split`.
- The artifacts root is outside the target repo, as required by `repo_goal_loop`.

## Why not `arena.proposal_run run`

`arena.proposal_run run` is the ticket/proposal emitter pipeline: decompose -> intake -> propose -> pairwise rerank -> emit `proposal.md`. It is useful if the desired output is a ticket-ready proposal. It is not the production apply/verify/promote loop. For this production pass, use `arena.repo_goal_loop`.

## Current preflight evidence

Build Arena repo:

```text
<build-arena-repo>
## main...origin/main
1079b80 Merge pull request #55 from leonbreukelman/feat/decomposer-v1-harden-drop-v0
```

Target repo:

```text
## main...origin/main [ahead 1]
25f4458 chore: add Build Arena goal config
local HEAD: 25f445806d5221f21d7ac675799db5c30499f1b7
remote HEAD/origin main: d60155bf05841f97d5ec3ba1752e0b7f588d54ce
goal config tracked in HEAD: yes
```

Credential state:

```text
shell XAI credential before sourcing: missing
<build-arena-repo>/.env: exists and supplies the XAI credential
sourced XAI credential present: yes
~/.hermes/.env also has the XAI credential
```

Capability preflight:

```text
claude/opus: OK
claude/fable: DEGRADED (unconfirmed — treat as fall back to Opus)
git: OK (git version 2.43.0)
```

Current CLI support:

```text
arena.repo_goal_loop supports:
--decompose-mode {fixture,recorded,off,live}
--apply-mode {deterministic,live_diff}
--allow-live
--live-provider
--live-model
--live-api-key-env
--live-max-tokens
--live-max-calls
--allow-promotion
--no-dry-run
```

Target gate preflight:

```text
uv run ruff check .
# All checks passed!
uv run python -m pytest -q
# 19 passed in 0.04s
uv run python -m mypy src tests
# Success: no issues found in 11 source files
```

Command parse and budget preflight:

```text
test_command_shlex= ['bash', '-lc', 'uv run ruff check . && uv run python -m pytest -q && uv run python -m mypy src tests']
max_cycles=1 planned_live_calls=3
max_cycles=2 planned_live_calls=6
```

Build Arena focused verification:

```text
uv run python -m pytest tests/test_repo_goal_loop.py tests/test_proposal_run.py tests/test_diff_proposer.py tests/test_proposal_registry.py tests/test_proposal_planner.py tests/test_proposal_domains.py -q
# all selected tests passed; pytest printed only progress dots

uv run ruff check .
# All checks passed!

uv run pyright
# 0 errors, 0 warnings, 0 informations
```

## Monitoring during/after the run

Ground truth is `$RUN_ROOT/loop-events.jsonl`.

Useful event names:

```text
RUN_STARTED
CYCLE_STARTED
DECOMPOSITION_COMPLETED
DECOMPOSITION_GATE_FAILED
CANDIDATE_SKIPPED
CANDIDATE_SELECTED
CANDIDATE_APPLIED
CANDIDATE_VERIFIED
PROMOTED
BASELINE_ADVANCED
PROMOTION_REFUSED
CANDIDATE_PACKAGED
BUDGET_HALT
DIVERGENCE_HALT
RUN_ENDED
```

Quick event summary:

```bash
uv run python - <<'PY' "$RUN_ROOT/loop-events.jsonl"
import json, sys
for line in open(sys.argv[1], encoding='utf-8'):
    event = json.loads(line)
    payload = event.get('payload', {})
    print(event.get('seq'), event.get('type'), 'cycle=', event.get('cycle'), 'payload=', payload)
PY
```

Post-run target verification:

```bash
cd <target-repo>
git status --short --branch
bash -lc "uv run ruff check . && uv run python -m pytest -q && uv run python -m mypy src tests"
```

## Evaluation rules

- `PROMOTED` + target gates passing = local production improvement happened.
- `PROMOTED` followed by another `DECOMPOSITION_COMPLETED` = closed-loop re-decompose evidence exists.
- Zero `PROMOTED` events = safe failure/no production improvement, even if the report/reviewer accepts the writeup.
- `DECOMPOSITION_GATE_FAILED` = fail-closed decomposition; intake/proposal/apply did not prove anything for that cycle.
- Target repo will remain unpushed; remote GitHub evaluation needs an explicit later push/PR decision.

## Known boundaries

- The public CLI does not expose an xAI `reasoning_effort` flag. The selected supported production command uses `grok-4.3` through the current OpenAI-compatible adapter without the old decomposition-only high-reasoning wrapper.
- Live external Cisco FMC integration testing is not part of this gate. The target contract here is local tests, lint, and typing from `.arena/goal.toml`.
- Broad unattended autonomy remains unproven: no dashboard/control plane, rollback endpoint, or remote promotion wrapper is included.
---END ARTIFACT---
