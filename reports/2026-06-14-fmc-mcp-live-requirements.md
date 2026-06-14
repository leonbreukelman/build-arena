# Requirements to run Build Arena live for fmc-mcp — 2026-06-14

## Direct answer

There are three different meanings of "live" here. They have different requirements.

1. **Live LLM decomposition only, read-only**: currently supported by `arena.project_model_cli snapshot --llm-mode live --allow-live --live-model <model>`. This makes provider/API calls but does not mutate `fmc-mcp`.
2. **Live LLM proposal/diff generation**: partially supported by `arena.proposal_candidate_runner --model <model>`, but not wired into `arena.repo_goal_loop`. Running it as a loop requires code changes or manual orchestration.
3. **Live promotion into fmc-mcp**: currently supported by `arena.repo_goal_loop --no-dry-run --allow-promotion`, but only for the existing deterministic offline apply path. That is not live LLM generation. It would currently promote the docs-only candidates unless the proposal domains are improved first.

A fourth meaning is **live Cisco FMC integration testing**. That is separate from Build Arena live LLM/promotion. It requires FMC credentials and a reachable read-only FMC instance; `/home/leonb/projects/fmc-mcp/.env` is currently missing.

## Current state checked

Build Arena:

- `arena.project_model_cli` exposes `--llm-mode live`, `--allow-live`, `--live-provider`, `--live-base-url`, `--live-model`, and `--live-api-key-env`.
- `arena.project_model_cli` refuses live mode unless `--allow-live` and `--live-model` are both provided.
- `arena.repo_goal_loop._decompose_and_rank()` hardcodes `llm_mode="fixture"` and does not expose live provider/model args.
- `arena.repo_goal_loop._deterministic_apply()` only does deterministic `ruff --fix` for `.py` and a minimal docs generator for `.md`; it does not call the live diff proposer.
- `arena.proposal_candidate_runner` can use an OpenAI-compatible live diff transport, but requires `--model` unless a fake diff file is supplied.
- `arena.runners.diff_proposer.OpenAICompatibleDiffTransport` requires an explicit model/provider config and uses the patch gate before applying a proposed diff.
- `scorer.goal_config.load_goal_config()` requires `<repo>/.arena/goal.toml` for diff proposer/scoring configuration.

fmc-mcp:

- `/home/leonb/projects/fmc-mcp/.env` is missing.
- No `.arena/goal.toml` exists in fmc-mcp.
- Local clean verification works when commands use `python -m`:
  - `uv run ruff check .` passed.
  - `uv run --extra dev python -m pytest -q` passed, 19 tests.
  - `uv run --extra dev python -m mypy src/fmc_mcp` passed.
- Local console-script commands are currently unsafe because `.venv/bin/pytest` and `.venv/bin/mypy` have stale shebangs pointing at `/home/leonb/maei/projects/fmc-mcp/.venv/bin/python`.
- CI uses clean setup and commands in `.github/workflows/ci.yml`, including `uv sync --extra dev --frozen`, pytest, ruff, and mypy.
- Source inspection shows FMC runtime operations are GET-only after authentication/token refresh, except auth and refresh token POSTs to FMC platform auth endpoints.

Credentials/provider status checked without exposing secrets:

- `XAI_API_KEY` is present in `~/.hermes/.env`.
- `OPENROUTER_API_KEY` is present in `~/.hermes/.env`.
- `GEMINI_API_KEY` is present in `~/.hermes/.env`.
- `OPENAI_API_KEY` is missing.

## Minimum safe live ladder

### Step 1 — Read-only live Project Model smoke

Requirements:

- Explicit owner authorization for API spend.
- Explicit model ID; do not rely on provider defaults.
- Provider key available in environment or `~/.hermes/.env`.
- Artifact root outside the target repo.
- No mutation/promotion.

Command shape:

```bash
RUN_ID="fmc-mcp-live-snapshot-$(date -u +%Y%m%dT%H%M%SZ)"
ARTIFACTS="/home/leonb/projects/build-arena/.arena/runs/$RUN_ID"
uv run python -m arena.project_model_cli snapshot \
  --project /home/leonb/projects/fmc-mcp \
  --artifacts-root "$ARTIFACTS/snapshot" \
  --project-id repo-goal-fmc-mcp \
  --goal "Improve fmc-mcp with bounded evidence-backed changes" \
  --llm-mode live \
  --allow-live \
  --live-provider xai \
  --live-api-key-env XAI_API_KEY \
  --live-model '<explicit-current-xai-model>' \
  --overwrite
```

Follow-up gates:

```bash
uv run python -m arena.project_model_cli gate --snapshot <manifest.json>
uv run python -m arena.project_model_cli freshness \
  --project /home/leonb/projects/fmc-mcp \
  --snapshot <project-model-v1.json>
```

If the gate fails, stop. A syntactically valid live model response is not enough.

### Step 2 — Live snapshot to advisory scorecard/proposal artifacts

Requirements:

- Step 1 gate passed.
- Freshness says `safeForMutation=true` before any mutation path consumes the snapshot.

Command shape:

```bash
uv run python -m arena.project_intake_scorecard \
  --project /home/leonb/projects/fmc-mcp \
  --snapshot <project-model-v1.json> \
  --profile active-development \
  --output <scorecard.json>

uv run python -m arena.proposal_ranker \
  --project /home/leonb/projects/fmc-mcp \
  --scorecard <scorecard.json> \
  --output <ranked-proposals.json> \
  --max-candidates 10

uv run python -m arena.proposal_planner \
  --project /home/leonb/projects/fmc-mcp \
  --scorecard <scorecard.json> \
  --output <proposal-plan.json> \
  --max-candidates 10
```

Current limitation: with fmc-mcp today, the existing proposal path will likely still select docs-only candidates and skip architecture/verification findings with `no_single_file_target` unless the proposal domains are improved.

### Step 3 — Live diff proposal in a worktree

Requirements:

- A real proposal-plan candidate.
- An isolated git worktree.
- `fmc-mcp/.arena/goal.toml`, because the diff proposer loads per-repo goal config.
- Explicit model and provider/API key.
- Patch gate enabled; no direct model-written file edits.
- Verification commands that work locally.

Required fmc-mcp `.arena/goal.toml` shape:

```toml
schema_version = "goal-config/v1"
project_id = "fmc-mcp"
goal = "Improve the read-only Cisco FMC MCP server without expanding write-side FMC behavior."

[commands]
test = ["uv", "run", "--extra", "dev", "python", "-m", "pytest", "-q"]
lint = ["uv", "run", "--extra", "dev", "ruff", "check", "src/", "tests/"]
typecheck = ["uv", "run", "--extra", "dev", "python", "-m", "mypy", "src/fmc_mcp"]

[coverage]
source = "src/fmc_mcp"
floor = 0

[paths]
source_roots = ["src/fmc_mcp", "tests", "docs"]
out_of_scope = [".env", ".venv", ".mypy_cache", ".pytest_cache", ".ruff_cache"]
read_only = ["uv.lock", ".github/workflows/ci.yml"]

[diff_caps]
max_files = 1
max_lines = 120
```

The exact read-only/out-of-scope list should be tuned before promotion. The important point is that `.env`, caches, venvs, and generated/local runtime files must never be proposal targets.

Command shape:

```bash
git -C /home/leonb/projects/fmc-mcp worktree add \
  /home/leonb/projects/build-arena/.arena/worktrees/fmc-mcp-live-candidate \
  HEAD

uv run python -m arena.proposal_candidate_runner \
  --worktree /home/leonb/projects/build-arena/.arena/worktrees/fmc-mcp-live-candidate \
  --proposal-plan <proposal-plan.json> \
  --candidate-rank 1 \
  --provider xai \
  --model '<explicit-current-xai-model>' \
  --output <candidate-result.json>
```

This is not yet the repo-scale loop. It is a single live candidate attempt.

### Step 4 — Repo-scale live loop

Current status: not available as a single safe CLI for live LLM generation.

Required Build Arena code changes:

1. Add live config fields to `RepoGoalLoopConfig` and CLI:
   - `llm_mode`
   - `allow_live`
   - `live_provider`
   - `live_base_url`
   - `live_model`
   - `live_api_key_env`
2. Replace the hardcoded `llm_mode="fixture"` in `_decompose_and_rank()` with fail-closed live/fixture selection.
3. Add a proposal apply mode to `repo_goal_loop`:
   - deterministic apply, current behavior; or
   - live diff proposer, routed through `DiffProposerRunner`/`OpenAICompatibleDiffTransport` and patch gate.
4. Add per-run budget controls:
   - max live calls
   - max cycles
   - max candidates
   - max estimated spend or explicit owner-set call budget
   - hard stop on provider/model mismatch, truncation, empty diff, or patch gate rejection
5. Persist provenance per cycle:
   - requested model
   - served model
   - provider
   - API-key source only, not value
   - patch gate result
   - verification outputs
6. Require fmc-mcp `.arena/goal.toml` before any live diff generation.
7. Use behaviour gates that avoid stale local console scripts:
   - `uv run --extra dev python -m pytest -q`
   - `uv run --extra dev python -m mypy src/fmc_mcp`
   - `uv run --extra dev ruff check src/ tests/`
8. Add/keep tests for all new live-loop plumbing without making real API calls:
   - live mode refuses without `--allow-live`.
   - live mode refuses without explicit model.
   - provider errors fail closed.
   - no-op/truncated/non-diff model output fails closed.
   - patch gate rejects cross-file or out-of-scope diffs.
   - code promotion refuses without a passing behaviour gate.
9. Run Build Arena gates:
   - `uv run pytest tests -q`
   - `uv run ruff check .`
   - `uv run pyright`
10. Run independent review on the live-loop plumbing before any promotion-capable live run.

### Step 5 — Promotion into fmc-mcp

Current deterministic promotion command shape:

First promotion-capable run should happen from a deliberately named branch with the target repo clean and no unrelated worktrees/branches being advanced accidentally. The command below mutates the target repo baseline by design; do not use it for the first live LLM smoke.

```bash
uv run python -m arena.repo_goal_loop \
  --project /home/leonb/projects/fmc-mcp \
  --goal "Improve fmc-mcp with bounded evidence-backed changes" \
  --artifacts-root /home/leonb/projects/build-arena/.arena/runs/<run-id> \
  --profile active-development \
  --max-cycles 3 \
  --no-dry-run \
  --allow-promotion \
  --test-command "uv run --extra dev python -m pytest -q"
```

This is promotion-capable, but not live LLM-capable. With today's intake/proposal behavior on fmc-mcp, it would likely promote the same docs-only candidates from the dry-run unless the proposal domains are improved first.

For code changes, promotion requires a configured and passing behaviour gate. Without `--test-command`, `.py` candidates are verified but refused for promotion.

## Live Cisco FMC integration testing requirements

This is separate from Build Arena's live LLM/proposal path.

Requirements:

- `/home/leonb/projects/fmc-mcp/.env` with:
  - `FMC_HOST`
  - `FMC_USERNAME`
  - `FMC_PASSWORD`
  - optional `FMC_VERIFY_SSL`
  - optional `FMC_DOMAIN_UUID`
- Reachable FMC 7.4.x instance.
- Dedicated read-only FMC API user.
- Permission awareness: deployment-status endpoint can return 403 on restricted accounts.
- Treat live FMC tests as side-effect-bearing network tests even though app operations are read-only after auth.

Command shape after credentials are installed:

```bash
cd /home/leonb/projects/fmc-mcp
uv run --extra dev python tests/test_live.py
```

I would not wire this into the default Build Arena behaviour gate yet. Keep it as an explicit, credential-gated smoke until the repo has a documented live-test policy.

## Practical shortest path

If the goal is a safe live proof on fmc-mcp, do this order:

1. Run a read-only live Project Model smoke with explicit xAI model and a small call budget.
2. Gate and freshness-check that snapshot.
3. Produce scorecard/ranked/proposal artifacts from the live snapshot.
4. Add fmc-mcp `.arena/goal.toml` and fix/avoid stale console-script commands.
5. Run a single live candidate in a manually created worktree through `proposal_candidate_runner`.
6. Verify with local gates.
7. Only after that, wire live diff generation into `repo_goal_loop` and run the full Build Arena test suite plus independent review.
8. Promotion comes last, with `--no-dry-run --allow-promotion`, not in the first live LLM smoke.

## Independent review

Claude Opus reviewed this note and returned `VERDICT: ACCEPT`, blockers: none. Review artifacts:

- Preflight: `/home/leonb/projects/build-arena/reports/2026-06-14-fmc-mcp-live-requirements-opus-preflight.json`
- Review result: `/home/leonb/projects/build-arena/reports/2026-06-14-fmc-mcp-live-requirements-opus-review.json`

Two non-blocking review notes were patched back into this file: Step 1 now makes `--live-api-key-env XAI_API_KEY` explicit, and Step 5 warns that promotion mutates the target baseline and should not be the first live LLM smoke.

## Bottom line

The minimum live thing is ready-ish: a read-only live decomposition smoke, assuming explicit owner spend authorization and a valid model ID.

The full live fmc-mcp improvement loop is not ready as one command. The blocking gaps are:

- `repo_goal_loop` is hardcoded to fixture decomposition.
- `repo_goal_loop` does not use the live diff proposer.
- fmc-mcp has no `.arena/goal.toml`.
- fmc-mcp local venv console scripts have stale shebangs; use `python -m` or rebuild the venv.
- The current proposal pipeline still tends to docs-only and skips architecture/verification findings with `no_single_file_target`.
- Live FMC integration credentials are absent if the intended acceptance gate touches a real Cisco FMC.
