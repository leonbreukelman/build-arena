# Build Arena fmc-mcp production pass + fresh-model intake/proposal report

Generated: 2026-06-15T00:22:00Z

## Owner verdict

The bounded live production pass ran, but it promoted nothing.

That is a safe failure, not a successful production improvement. Build Arena did exactly the right thing by not mutating `fmc-mcp` when the live proposal produced invalid Markdown links.

The fresh model and intake were built successfully from the live decomposition. The proposal pipeline was run ten times. It did not produce ten unique proposals; it deterministically reproduced the same four proposal candidates each time. There is no proposal registry yet that catches or suppresses duplicates across runs.

## Run artifacts

- Production pass root: `/home/leonb/projects/build-arena/.arena/runs/fmc-mcp-production-20260615T001605Z`
- Event stream: `/home/leonb/projects/build-arena/.arena/runs/fmc-mcp-production-20260615T001605Z/loop-events.jsonl`
- Live model: `/home/leonb/projects/build-arena/.arena/runs/fmc-mcp-production-20260615T001605Z/cycle-1/snapshot/snapshot-f83afa04ea4a7dc8/project-model-v1.json`
- Freshness: `/home/leonb/projects/build-arena/.arena/runs/fmc-mcp-production-20260615T001605Z/post-run-pipeline/freshness.json`
- Intake scorecard: `/home/leonb/projects/build-arena/.arena/runs/fmc-mcp-production-20260615T001605Z/post-run-pipeline/intake-scorecard.json`
- Intake markdown: `/home/leonb/projects/build-arena/.arena/runs/fmc-mcp-production-20260615T001605Z/post-run-pipeline/intake-scorecard.md`
- Ten-run duplicate summary: `/home/leonb/projects/build-arena/.arena/runs/fmc-mcp-production-20260615T001605Z/post-run-pipeline/proposal-duplicate-summary.json`
- Proposal runs: `/home/leonb/projects/build-arena/.arena/runs/fmc-mcp-production-20260615T001605Z/post-run-pipeline/proposal-runs/`
- Target verification log: `/home/leonb/projects/build-arena/.arena/runs/fmc-mcp-production-20260615T001605Z/fmc-mcp-final-verification.log`

## Production pass outcome

Command used the full live path:

- `--decompose-mode live`
- `--apply-mode live_diff`
- `--allow-live`
- `--live-provider xai`
- `--live-model grok-4.20-0309-non-reasoning`
- `--live-api-key-env XAI_API_KEY`
- `--live-max-tokens 12000`
- `--live-max-calls 2`
- `--allow-promotion`
- `--no-dry-run`
- `--max-cycles 1`

Event summary:

1. `RUN_STARTED`
   - live: true
   - model: `grok-4.20-0309-non-reasoning`
   - liveMaxCalls: 2
   - plannedLiveCalls: 2
2. `DECOMPOSITION_COMPLETED`
   - mode: live
   - snapshot: `snapshot-f83afa04ea4a7dc8`
   - gate_passed: true
   - violation_count: 0
   - usage: 7544 prompt tokens, 3739 completion tokens, 11283 total tokens
3. `CANDIDATE_SELECTED`
   - selected: `agent.agents-md.missing`
   - domain: documentation
   - target: `AGENTS.md`
4. `CANDIDATE_APPLY_FAILED`
   - error: `RunnerError: missing Markdown link target: src/src/fmc_mcp/config.py->src/src/fmc_mcp/config.py, src/src/fmc_mcp/config.py->src/src/fmc_mcp/config.py`
5. `BUDGET_HALT`
   - reason: `max_cycles`
6. `RUN_ENDED`
   - promotions: 0
   - cyclesRun: 1
   - halted: budget

Interpretation: the live model produced a bad docs patch with invented/wrong local Markdown paths. The patch/link gate caught it before promotion. `fmc-mcp` was not mutated.

## Target repo verification after the pass

`fmc-mcp` status:

- Branch: `main...origin/main [ahead 1]`
- Dirty state: clean
- Current local head: `25f4458 chore: add Build Arena goal config`
- `.arena/goal.toml` is tracked in HEAD

Verification command:

```bash
uv run ruff check . && uv run python -m pytest -q && uv run python -m mypy src tests
```

Result:

- Ruff: all checks passed
- Pytest: 19 passed
- Mypy: success, no issues found in 11 source files

Captured proof:

- `/home/leonb/projects/build-arena/.arena/runs/fmc-mcp-production-20260615T001605Z/fmc-mcp-final-verification.log`
- `/home/leonb/projects/build-arena/.arena/runs/fmc-mcp-production-20260615T001605Z/fmc-mcp-final-verification.exitcode` (`0`)

## Fresh model + intake

The live decomposition from the production pass produced a new Project Model v1:

- Snapshot ID: `snapshot-f83afa04ea4a7dc8`
- Snapshot HEAD: `25f445806d5221f21d7ac675799db5c30499f1b7`
- Current HEAD: `25f445806d5221f21d7ac675799db5c30499f1b7`
- Freshness status: `fresh`
- `safeForMutation`: true
- Current dirty state: false

Intake was rerun from that exact model, so intake is in sync with the latest decomposed model.

Intake produced seven findings:

1. `code.component.untested.comp-server` — Component MCP Server Runtime has no observable check — 540.0
2. `agent.agents-md.missing` — AGENTS.md is missing — 432.0
3. `architecture.open-questions-or-gaps` — Project Model contains open questions or verification gaps — 252.0
4. `verification.quality-gates.present` — Project Model exposes local quality gates — 216.0
5. `code.component.untested.comp-entrypoints` — Component Application Entrypoints has no observable check — 180.0
6. `decision.history.missing` — Decision records are missing — 176.0
7. `ops.runbooks.missing` — Runbooks are missing — 88.0

## Proposal pipeline ten-run result

I ran the proposal ranker and proposal planner ten times from the synced intake scorecard.

Result:

- Ranked proposal artifacts produced: 10
- Proposal plan artifacts produced: 10
- Unique ranked artifact hashes: 1
- Unique proposal-plan artifact hashes: 1
- Candidate count per run: 4
- Unique proposal keys across all 10 runs: 4
- Duplicate proposal keys across runs: each of the four proposal keys appeared 10 times

Bluntly: the current system is deterministic, but it is not deduplicating through a proposal registry. It just emits the same plan again because no registry/state layer exists for pending proposals.

## Top proposals actually available

You asked for top 10 proposals. The current implementation produced only four proposal candidates from this fresh model. I am not inventing six extra proposals.

### 1. Component MCP Server Runtime has no observable check

- Finding: `code.component.untested.comp-server`
- Domain: `generic_file`
- Target: `src/fmc_mcp/server.py`
- Priority: 540.0
- Source recommended action: Add an observable check, e.g. a focused test, covering MCP Server Runtime before mutating it.
- Verification commands: none in proposal plan
- Status: high-priority but not runnable/promotable by the current proposal runner because no deterministic verification commands are attached.

### 2. AGENTS.md is missing

- Finding: `agent.agents-md.missing`
- Domain: `documentation`
- Target: `AGENTS.md`
- Priority: 432.0
- Source recommended action: Create AGENTS.md with commands, boundaries, and definition of done.
- Verification commands:
  - `test -s AGENTS.md`
  - `python3 -m arena.markdown_links --repo . --path AGENTS.md --require-source-references`
- Status: runnable in principle, but the live production pass selected this and failed because the model produced bad local Markdown links.

### 3. Decision records are missing

- Finding: `decision.history.missing`
- Domain: `documentation`
- Target: `docs/decisions/index.md`
- Priority: 176.0
- Source recommended action: Create decision records for architecture-significant constraints.
- Verification commands:
  - `test -s docs/decisions/index.md`
  - `python3 -m arena.markdown_links --repo . --path docs/decisions/index.md --require-source-references`
- Status: runnable in principle; not attempted in the production pass because max cycles was 1.

### 4. Runbooks are missing

- Finding: `ops.runbooks.missing`
- Domain: `documentation`
- Target: `docs/runbooks/index.md`
- Priority: 88.0
- Source recommended action: Document start/stop/deploy/rollback/troubleshooting procedures.
- Verification commands:
  - `test -s docs/runbooks/index.md`
  - `python3 -m arena.markdown_links --repo . --path docs/runbooks/index.md --require-source-references`
- Status: runnable in principle; not attempted in the production pass because max cycles was 1.

## Skipped findings that should become better proposals

The current proposal domains skipped three findings:

1. `architecture.open-questions-or-gaps`
   - Reason: `no_single_file_target`
   - Problem: valid architecture/verification-gap findings do not yet map to a concrete proposal artifact.
2. `verification.quality-gates.present`
   - Reason: `no_single_file_target`
   - Problem: the system recognizes quality gates but cannot propose gate hardening or coverage improvements from them.
3. `code.component.untested.comp-entrypoints`
   - Reason: `no_single_file_target`
   - Problem: entrypoint component spans `src/fmc_mcp/__init__.py` and `src/fmc_mcp/__main__.py`; current proposal contract is single-file and drops it.

## Duplicate/registry check

Actual result: no proposal registry exists for cross-run dedupe.

Evidence:

- Code search found domain registry duplicate-name checks, but no proposal registry for pending proposal IDs, base refs, hidden/unmerged proposals, or duplicate suppression.
- Ten deterministic runs emitted identical artifacts.
- Duplicate summary shows each available proposal key appeared 10 times:
  - `code.component.untested.comp-server` / `src/fmc_mcp/server.py` — 10 times
  - `agent.agents-md.missing` / `AGENTS.md` — 10 times
  - `decision.history.missing` / `docs/decisions/index.md` — 10 times
  - `ops.runbooks.missing` / `docs/runbooks/index.md` — 10 times

This validates your concern: proposals need a persistent registry/state layer, not just deterministic re-ranking.

## Backlog item recorded from this run

### Proposal snapshot/branch lineage + registry/dedup layer

Problem:

The current proposer is too tightly downstream of intake/decomposition artifacts and has no persistent view of proposals not yet visible in the repo. It can repeatedly propose the same logical change across runs because pending/unmerged/generated proposals are not part of the proposer context.

Required shape:

1. Proposal inputs must be anchored to a specific base:
   - project id
   - git branch/ref
   - head OID
   - dirty-state fingerprint
   - snapshot id/hash when consuming a Project Model
   - scorecard id/hash when consuming intake
2. Proposal outputs must carry the same lineage tags:
   - base branch/ref
   - base head OID
   - model snapshot id/hash, if used
   - intake scorecard id/hash, if used
   - proposal run id
   - target path(s)
   - proposal content hash / diff hash
3. Proposer should be callable against a git branch/ref or snapshot without internally depending on running decomposition or intake first.
   - Decomposition/intake can feed it, but should not be hidden prerequisites.
4. A proposal registry should persist proposals not yet visible in the repo:
   - pending
   - applied-in-worktree
   - failed-gate
   - promoted
   - rejected/duplicate
5. Duplicate keys should include at least:
   - project id
   - base head OID or branch-overlay id
   - target path(s)
   - finding id/domain where present
   - normalized intent hash
   - diff/content hash when available
6. Proposal prompts for live proposal models should include existing pending/unmerged proposals from the registry so the model does not regenerate invisible work.
7. Freshness policy:
   - if target HEAD changes, dirty state changes, or the selected branch advances, require a fresh model or a branch-overlay model before mutation;
   - intake must be regenerated or explicitly validated fresh against the latest model before proposal generation;
   - if a promotion succeeds, run a new decomposition/intake before selecting the next proposal.

Suggested acceptance tests:

- Running the proposal pipe 10 times against the same base produces one active proposal plus nine duplicate/reused records, not ten indistinguishable artifacts.
- A proposal generated against branch A cannot be applied silently to branch B without a freshness/lineage check.
- A new decomposition is required after a successful promotion before a second proposal can be selected.
- A pending proposal absent from the repo is included in the next live-proposer prompt/context.

## What went wrong in the production pass

The live docs proposal generated Markdown links to `src/src/fmc_mcp/config.py`, which does not exist. The deterministic link gate rejected it:

`missing Markdown link target: src/src/fmc_mcp/config.py->src/src/fmc_mcp/config.py`

This is exactly the class of issue the source-reference/link gate is supposed to catch. The run failed safe.

## What this says about Build Arena readiness

Good:

- Live decomposition worked and passed the Project Model gate.
- Freshness worked and marked the model safe for mutation.
- Intake stayed synced to the fresh model.
- The proposal pipeline is deterministic.
- The patch/link gate prevented a bad live proposal from mutating the target repo.
- `fmc-mcp` stayed clean and green.

Bad / next engineering blockers:

1. Proposal registry does not exist.
2. Proposal artifacts do not yet carry enough branch/snapshot lineage for robust cross-run dedupe and branch safety.
3. Live proposal prompt/context does not include existing pending proposals invisible to the repo.
4. The top code finding has no deterministic verification commands, so the runner skips the highest-priority actual code improvement.
5. The live docs proposer can still invent bad relative paths; the gate catches it, but the proposer prompt/repair path needs improvement.
6. The system cannot produce 10 unique proposals for this repo/model because current intake/domain mapping yielded only four candidate targets.

## Bottom line

The production pass was a safe failed attempt: no promotion, no target damage, live decomposition succeeded, live proposal failed at the gate.

The fresh model/intake/proposal flow worked, but it exposed the next real Build Arena backlog item: proposal lineage + persistent registry/dedup + pending-proposal prompt context. Without that, repeated proposal runs are deterministic duplicates, not a managed proposal queue.
