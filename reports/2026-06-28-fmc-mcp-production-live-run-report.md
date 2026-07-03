# fmc-mcp Build Arena live production run — 2026-06-28T00:47:22Z

## Owner verdict

Production loop: **succeeded with one local promotion, then fail-closed on the second cycle**.

Generated ticket artifact: **`proposal.md` generated**.

Generated experiment artifact: **`experiment.md` was not generated**. The dream lane failed closed at `dream_research` on the initial run, two direct research retries, and one full dream-run retry. I did not fabricate an experiment artifact from raw dreams.

Target repo mutation: local `/home/leonb/projects/fmc-mcp` `main` advanced from `25f445806d5221f21d7ac675799db5c30499f1b7` to `cbe8a3843b64de4f9d8c3d910d84aa536216cad8`. Nothing was pushed to GitHub.

## Run root

`/home/leonb/projects/build-arena/.arena/runs/fmc-mcp-production-live-20260628T004722Z`

Key files:

- Production event stream: `/home/leonb/projects/build-arena/.arena/runs/fmc-mcp-production-live-20260628T004722Z/loop-events.jsonl`
- Production stdout: `/home/leonb/projects/build-arena/.arena/runs/fmc-mcp-production-live-20260628T004722Z/production.stdout.txt`
- Production stderr: `/home/leonb/projects/build-arena/.arena/runs/fmc-mcp-production-live-20260628T004722Z/production.stderr.txt`
- Promoted patch: `/home/leonb/projects/build-arena/.arena/runs/fmc-mcp-production-live-20260628T004722Z/cycle-1/candidate-artifacts/hyp-goal-cycle-1-e7fce2fa2e31.patch`
- Promoted patch provenance: `/home/leonb/projects/build-arena/.arena/runs/fmc-mcp-production-live-20260628T004722Z/cycle-1/candidate-artifacts/hyp-goal-cycle-1-e7fce2fa2e31.patch.provenance.json`
- Proposal artifact: `/home/leonb/projects/build-arena/.arena/runs/fmc-mcp-production-live-20260628T004722Z/proposal.md`
- Proposal workdir: `/home/leonb/projects/build-arena/.arena/runs/fmc-mcp-production-live-20260628T004722Z/proposal-workdir`
- Initial dream workdir: `/home/leonb/projects/build-arena/.arena/runs/fmc-mcp-production-live-20260628T004722Z/dream-workdir`
- Full dream retry workdir: `/home/leonb/projects/build-arena/.arena/runs/fmc-mcp-production-live-20260628T004722Z/dream-workdir-full-retry`
- Exit code ledger: `/home/leonb/projects/build-arena/.arena/runs/fmc-mcp-production-live-20260628T004722Z/exit-codes.txt`
- Captured target verification after report review: `/home/leonb/projects/build-arena/.arena/runs/fmc-mcp-production-live-20260628T004722Z/target-postrun-verification.txt`
- Captured Build Arena status after report review: `/home/leonb/projects/build-arena/.arena/runs/fmc-mcp-production-live-20260628T004722Z/build-arena-postrun-status.txt`

## Commands run

### Production apply/promote loop

```bash
uv run python -m arena.repo_goal_loop \
  --project /home/leonb/projects/fmc-mcp \
  --goal "Improve the read-only Cisco Firepower Management Center MCP server with bounded, verified, repository-grounded changes using live LLM decomposition and live LLM diff proposal while preserving local tests, lint, and typing." \
  --artifacts-root /home/leonb/projects/build-arena/.arena/runs/fmc-mcp-production-live-20260628T004722Z \
  --profile production \
  --max-cycles 2 \
  --decompose-mode live \
  --apply-mode live_diff \
  --allow-live \
  --live-provider xai \
  --live-model grok-4.3 \
  --live-api-key-env XAI_API_KEY \
  --live-max-tokens 12000 \
  --live-max-calls 8 \
  --test-command 'bash -lc "uv run ruff check . && uv run python -m pytest -q && uv run python -m mypy src tests"' \
  --allow-promotion \
  --no-dry-run
```

### Ticket proposal lane

```bash
uv run python -m arena.proposal_run run /home/leonb/projects/fmc-mcp \
  --decompose-live \
  --live-provider xai \
  --live-model grok-4.3 \
  --live-api-key-env XAI_API_KEY \
  --profile production \
  --max-candidates 10 \
  --workdir /home/leonb/projects/build-arena/.arena/runs/fmc-mcp-production-live-20260628T004722Z/proposal-workdir \
  --keep-workdir \
  --output /home/leonb/projects/build-arena/.arena/runs/fmc-mcp-production-live-20260628T004722Z/proposal.md
```

### Dream lane and retries

Initial:

```bash
uv run python -m arena.dream_run run /home/leonb/projects/fmc-mcp \
  --decompose-live \
  --live-provider xai \
  --live-model grok-4.3 \
  --live-api-key-env XAI_API_KEY \
  --profile production \
  --workdir /home/leonb/projects/build-arena/.arena/runs/fmc-mcp-production-live-20260628T004722Z/dream-workdir \
  --keep-workdir \
  --output /home/leonb/projects/build-arena/.arena/runs/fmc-mcp-production-live-20260628T004722Z/experiment.md
```

Then I retried `arena.dream_research` twice against the preserved raw dreams, and ran one full `arena.dream_run` retry into `dream-workdir-full-retry`. All three retries failed closed at `dream_research`.

## Production-loop result

`production.stdout.txt`:

```json
{
  "cyclesRun": 2,
  "promotions": 1,
  "halted": "budget",
  "events": "/home/leonb/projects/build-arena/.arena/runs/fmc-mcp-production-live-20260628T004722Z/loop-events.jsonl"
}
```

Canonical events summary from `loop-events.jsonl`:

- Cycle 1 live decomposition passed with snapshot `snapshot-5054fb46a0006341`.
- Cycle 1 selected `code.component.untested.component.client` targeting `src/fmc_mcp/client.py`.
- Cycle 1 live diff applied patch `hyp-goal-cycle-1-e7fce2fa2e31.patch`.
- Cycle 1 gates passed:
  - `uv run --extra dev mypy src/fmc_mcp` -> exit 0.
  - `uv run --extra dev python -m pytest -q` -> exit 0, `19 passed in 0.05s`.
  - `uv run --extra dev ruff check .` -> exit 0, `All checks passed!`.
- Boundary: those are the candidate/domain verification commands recorded in `loop-events.jsonl`; they are not the literal `--test-command` string shown in the production command.
- Cycle 1 promoted and advanced the local baseline.
- Cycle 2 live decomposition passed with snapshot `snapshot-d08c9f8a601bde0d`.
- Cycle 2 selected `code.component.untested.component.client` again.
- Cycle 2 failed closed at apply: `RunnerError: patch gate rejected: git_apply_check_failed`.
- Run ended on `BUDGET_HALT` because `--max-cycles 2` was reached.

Event counts:

```text
RUN_STARTED=1
CYCLE_STARTED=2
DECOMPOSITION_COMPLETED=2
CANDIDATE_SELECTED=2
CANDIDATE_APPLIED=1
CANDIDATE_VERIFIED=1
PROMOTED=1
BASELINE_ADVANCED=1
RUN_COMPLETED=1
CANDIDATE_APPLY_FAILED=1
BUDGET_HALT=1
RUN_ENDED=1
```

Captured production usage from persisted artifacts:

- Live decomposition calls captured: 2.
- Successful live diff call captured: 1.
- Captured prompt tokens: 18,941.
- Captured completion tokens: 3,131.
- Captured reasoning tokens inside completion details: 2,462.
- Captured total tokens: 24,534.
- Captured `cost_in_usd_ticks`: 372,555,500.

Boundary: the rejected cycle-2 live-diff attempt likely consumed a live call, but no rejected patch/provenance file was persisted on that fail path, so I am not claiming complete provider usage for the production loop.

## Promoted target change

Target commit:

```text
cbe8a3843b64de4f9d8c3d910d84aa536216cad8 arena: code.component.untested.component.client
```

Patch summary:

```diff
diff --git a/src/fmc_mcp/client.py b/src/fmc_mcp/client.py
@@
+    @property
+    def is_connected(self) -> bool:
+        """Observable connection state for verification."""
+        return self._client is not None
```

Live file location after promotion: `/home/leonb/projects/fmc-mcp/src/fmc_mcp/client.py:373` (confirmed by a live `read_file` check after promotion; the persisted patch records the same added property but not the live file line number).

## Post-run verification

Target repo after run:

```text
## main...origin/main [ahead 2]
cbe8a38 arena: code.component.untested.component.client
25f4458 chore: add Build Arena goal config
```

Post-run target gates captured in `/home/leonb/projects/build-arena/.arena/runs/fmc-mcp-production-live-20260628T004722Z/target-postrun-verification.txt`:

```text
uv run ruff check .
# All checks passed!
uv run python -m pytest -q
# 19 passed in 0.04s
uv run python -m mypy src tests
# Success: no issues found in 11 source files
```

Build Arena checkout after the production commands was clean. After saving this report and the Opus review artifacts, the current Build Arena status is captured in `/home/leonb/projects/build-arena/.arena/runs/fmc-mcp-production-live-20260628T004722Z/build-arena-postrun-status.txt` and shows only untracked report/review files:

```text
## main...origin/main
?? reports/2026-06-28-fmc-mcp-production-live-run-report-opus-review-prompt.md
?? reports/2026-06-28-fmc-mcp-production-live-run-report-opus-review.err
?? reports/2026-06-28-fmc-mcp-production-live-run-report-opus-review.json
?? reports/2026-06-28-fmc-mcp-production-live-run-report.md
f1bb4ac Merge pull request #60 from leonbreukelman/feat/dream-admissibility-v1
```

## Generated `proposal.md`

Path: `/home/leonb/projects/build-arena/.arena/runs/fmc-mcp-production-live-20260628T004722Z/proposal.md`

Full content:

```markdown
# Component Tool Registry has no observable check

## Proposed change
Add or prepare an observable, repository-grounded check for component finding code.component.untested.component.tools: Component Tool Registry has no observable check. Limit changes to the component target path set: src/fmc_mcp/tools.py.

## Why
Add an observable check (e.g. a focused test) covering Tool Registry before mutating it.

## Target file(s)
- `src/fmc_mcp/tools.py`

## Definition of done
A test or check file exists that exercises the component target path set (src/fmc_mcp/tools.py) and asserts its observable behaviour.

## How to verify
```sh
uv run --extra dev mypy src/fmc_mcp
uv run --extra dev python -m pytest -q
uv run --extra dev ruff check .
```

## Constraints
- Prefer a focused test or minimal code-facing verification improvement over broad refactors.
- Do not silence failures or remove behavior to make the gate pass.
- Use only repository-grounded files and commands from the intake quality gates.

## Source references
- component -- component component.tools
- iterationReadiness.componentProfiles (absence)
- src/fmc_mcp/tools.py (owned_surface)
- provenance -- ref prov:750d7fda533e438c

---
_Provenance -- finding `code.component.untested.component.tools` · plan `a86df432f8d1e199` · snapshot `snapshot-17fd2aaef7add958`_
```

Proposal lane metadata:

- `proposal_exit=0`.
- Workdir preserved at `/home/leonb/projects/build-arena/.arena/runs/fmc-mcp-production-live-20260628T004722Z/proposal-workdir`.
- `proposal-workdir/rerank-trace.json` records `callCount: 18`, `survivorCount: 10`, provider `xai`, requested/served model `grok-4.3`.
- The emitted proposal was based on base `cbe8a3843b64de4f9d8c3d910d84aa536216cad8`, after the production-loop promotion.

## Dream lane result

No emitted `experiment.md` exists.

Exit ledger:

```text
production_exit=0
proposal_exit=0
dream_exit=1
dream_research_retry1_exit=1
dream_research_retry2_exit=1
dream_full_retry_exit=1
target_postrun_verification_exit=0
```

Dream failure message:

```text
dream run failed: stage 'dream_research' failed (exit 1): dream research failed: research produced no dreams with required premise surface.
```

Artifacts that do exist:

- Initial raw dreams: `/home/leonb/projects/build-arena/.arena/runs/fmc-mcp-production-live-20260628T004722Z/dream-workdir/raw-dreams.json`
- Full-retry raw dreams: `/home/leonb/projects/build-arena/.arena/runs/fmc-mcp-production-live-20260628T004722Z/dream-workdir-full-retry/raw-dreams.json`
- Initial capability map: `/home/leonb/projects/build-arena/.arena/runs/fmc-mcp-production-live-20260628T004722Z/dream-workdir/capability-map.json`
- Full-retry capability map: `/home/leonb/projects/build-arena/.arena/runs/fmc-mcp-production-live-20260628T004722Z/dream-workdir-full-retry/capability-map.json`

Initial raw dream IDs:

- `dream.client-carrier-split`
- `dream.server-binding-remap`

Full-retry raw dream IDs:

- `dream.client-carrier-swap`
- `dream.resources-function-remap`

Boundary: these raw dreams are not gated emitted experiments. The standard dream lane rejected them at research, so they must not be treated as `experiment.md`.

## What this proves

- Build Arena no longer only safely fails on this target: it produced and promoted one local, verified code change through live decomposition + live diff + deterministic gates.
- The local target repo is still clean after promotion and post-run verification passes.
- The ticket proposal lane produced a usable next proposal after the promotion.
- The dream lane still fails at `dream_research` with the literal persisted reason `research produced no dreams with required premise surface`; it failed closed rather than emitting an invalid experiment.

## Next concrete action

Fix the dream lane research prompt/output capture so failed research attempts persist the raw model response and can be repaired deterministically. The production loop itself should also record failed live-diff raw output/provenance on patch-gate rejection; cycle 2 lost useful forensic data on `git_apply_check_failed`.
