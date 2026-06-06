# Build Arena Expected-vs-Actual Status Report

Date: 2026-06-05
Generated at UTC: 2026-06-05T13:32:41Z
Repository: `/home/leonb/projects/build-arena`
Branch observed: `coverage-100`
HEAD observed: `08a3e29 [verified] add live xai decomposer and project model v1 readiness`
Working tree observed: clean
Remote state observed: local branch ahead of `origin/coverage-100` by 2 commits

## Direct outcome

Build Arena is mostly aligned with the progress described in prior conversations, but several high-value project documents are stale.

The actual code matches the broad conversation timeline through:

- Phase 1 scorer calibration
- Phase 2 verifier calibration
- Phase 3 runner routing
- Phase 4 loop/budget/divergence/events/worktree promotion foundation
- deterministic Project Model v0
- AI-first decomposer
- Project Model v1 primary artifact
- bounded direct xAI/Grok live adapter behind `--allow-live`

The main misalignment is documentation drift:

- `README.md` still presents the project mainly as Phase 4 plus deterministic Project Model v0.
- `AGENTS.md` still names the current phase as Phase 4 and does not mention the AI-first decomposer, Project Model v1 primary artifact, or bounded live xAI adapter.
- The June 5 final report still says the slice is “ready to commit,” although it has since been committed locally as `08a3e29`.

A read-only Opus cross-check was run against the evidence packet. Opus agreed with this verdict: `MOSTLY_ALIGNED_WITH_STALE_DOCS`.

Opus artifact:

- `/tmp/build-arena-timeline-status-opus.json`

Opus run metadata:

- `is_error=False`
- `stop_reason=end_turn`
- `total_cost_usd=0.37929375`

## Current verification evidence

Commands run during the status pass:

```text
uv run pytest tests -q
uv run ruff check .
uv run pyright
uv run pytest tests/test_project_model_llm_live.py tests/test_project_model_v1_contract.py -q
```

Observed results:

- Full test suite passed.
- Ruff passed.
- Pyright passed.
- Focused Project Model v1/live tests passed: `9 passed`.

## Expected timeline from conversations

### 1. May 24 — project not started

Conversation evidence said `/home/leonb/projects/build-arena` and related repos were missing.

Expected status then: no Build Arena implementation yet.

### 2. May 24 — Phase 1 scorer calibration complete

Conversation/final summaries said Build Arena was bootstrapped.

Commit:

- `aa353e6 [verified] bootstrap phase 1 scorer calibration`

Expected status:

- standalone repo
- scorer lock/content hash
- deterministic calibration diffs
- Opus review
- verified commit

### 3. Phase 2 verifier calibration

Commit present in actual log:

- `94229d9 [verified] add phase 2 verifier calibration`

Expected status:

- verifier calibration and gates implemented and tested

### 4. Phase 3 runner routing contracts

Commit present:

- `d62a4d4 [verified] add phase 3 runner routing contracts`

Expected status:

- runner fallback/routing contracts
- fingerprints/ledger/hypothesis plumbing

### 5. Phase 4 loop/budget/divergence/events/worktree promotion foundation

Commit present:

- `979cf3c [verified] add phase 4 loop budget divergence`

Conversation and project docs agree this phase added:

- JSONL events as canonical loop state
- SQLite projection
- budget checks
- divergence detection
- locked git worktrees
- ff-only promotion foundation
- loop glue

Explicitly not expected yet:

- dashboard control plane
- rollback endpoint
- live subscription-CLI subprocess execution

### 6. Rename/calibration cleanup period

Commits present:

- `44a17c3 Rename project to build-calibration`
- `7c7bb60 [verified] ignore local calibration build bundles`
- `7eab736 Rename main loop project to build-arena`

### 7. Initial deterministic project decomposer / Project Model v0

Commits present:

- `3cd7418 feat: add project decomposer`
- `7675b49 [verified] Define Project Model v0 contract (#2)`
- `95e75d3 Emit Project Model v0 from decomposer (#3)`

Conversation evidence said this decomposer was deterministic and shallow:

- git/filesystem scanner
- hardcoded/path-ish classifier
- not a real AI semantic reader
- no Hermes skills, no LLM, no Elenchus, no GitHub API

Expected status:

- useful v0 compatibility projection
- not the desired AI-first decomposer

### 8. Coverage hardening

Commit present:

- `df3d1c7 Reach 100 percent coverage`

### 9. June 3/4 — shift to “proper AI-first decomposer”

Conversation goal changed from v0 classifier to:

```text
git/filesystem truth
→ code/doc/issue/config graph
→ provenance-backed encyclopedia/wiki
→ Grok/leading-model recursive decomposer
→ components/contracts/cross-cutting concerns/checks/held-out probes/verification gaps
→ deterministic gate
→ frozen decomposition snapshot
```

Expected status:

- sidecar-first implementation
- not a breaking v0 schema rewrite

### 10. June 4 — AI-first decomposer implemented and accepted

Commit present:

- `a26bc37 [verified] add AI-first project decomposer`

Conversation/final report claimed:

- graph/wiki/snapshot/gate sidecars implemented
- v0 compatibility preserved
- LLM claims advisory until deterministic gate passes
- pilots passed on Build Arena, FMC-MCP, and `leonbreukelman-engineer`
- Opus final rereview passed

Important expected limitation:

- live Grok decomposition was still blocked in that run
- acceptance relied on recorded leading-model outputs/probe evidence

### 11. June 5 — Grok/xAI RCA, live adapter, Project Model v1 readiness

Commit present:

- `08a3e29 [verified] add live xai decomposer and project model v1 readiness`

Conversation/final report claimed:

- direct xAI/OpenAI-compatible adapter added
- cancelled/empty wrapper output now fails closed
- invalid/truncated/empty live responses rejected
- CLI live mode guarded by `--allow-live`
- Project Model v1 emitted as primary enriched artifact
- v0 still emitted for compatibility
- Elenchus Core and Arena Calibration inspected and found v0-only

Important expected limitation:

- broader live loop still not ready
- readiness register still says blockers remain

## Actual code status

### Repo and branch

- Repository: `/home/leonb/projects/build-arena`
- Branch: `coverage-100`
- Remote: `origin git@github.com:leonbreukelman/build-arena.git`
- Local branch is ahead of `origin/coverage-100` by 2 commits.
- Working tree is clean.
- HEAD is `08a3e29`.

### Phase 1-4 foundation exists

Observed files/directories:

- `.arena/scorer.lock.toml`
- `scorer/`
- `verifier/`
- `schema/arena.yaml`
- `arena/generated/models.py`
- `arena/events.py`
- `arena/budget.py`
- `arena/divergence.py`
- `arena/worktrees.py`
- `arena/loop.py`

Naming note:

- `GitPromoter` is in `arena/worktrees.py`, not `arena/promoter.py`.
- `RunnerRouter` is in `arena/router.py`, not `arena/runner_router.py`.
- `FingerprintFailureLedger` is in `arena/ledger.py`, not `arena/failure_ledger.py`.

### AI-first decomposer / v1 / live files exist

Observed files:

- `arena/project_graph.py`
- `arena/project_encyclopedia.py`
- `arena/project_snapshot.py`
- `arena/project_model_gate.py`
- `arena/project_decomposer_ai.py`
- `arena/project_model_llm.py`
- `arena/project_model_v1.py`
- `arena/project_model_cli.py`

### Actual live/xAI behavior in code

`LiveProjectModelLLM` posts to:

- `https://api.x.ai/v1/chat/completions`

It uses:

- `XAI_API_KEY`
- `response_format: {"type": "json_object"}`
- `temperature: 0`

It rejects:

- no choices
- `finish_reason == length`
- empty content
- invalid JSON
- cancelled wrapper output with empty final text

It records provider metadata:

- provider
- api mode
- finish reason
- prompt hash
- content hash

### Actual Project Model v1 behavior

The AI decomposer writes:

- `project-model-v1.json`
- `project-model-v0.json`

The manifest sets:

- `project_model_primary_path = project-model-v1.json`
- `project_model_v1_path = project-model-v1.json`
- `project_model_v0_path = project-model-v0.json`

The v1 schema version is:

- `project-model/v1`

The v1 artifact bundles:

- project identity and goal
- snapshot
- project graph
- gate report
- provenance
- hashes
- models
- derived artifacts
- compatibility metadata

### Actual CLI behavior

The `snapshot` subcommand supports:

- `--llm-mode fixture`
- `--llm-mode recorded`
- `--llm-mode live`
- `--llm-mode off`

Live mode requires:

- `--allow-live`

Without `--allow-live`, CLI refuses routine live spend and exits 2.

## Where conversations and code are aligned

1. The commit progression exists.
2. Phase 4 foundation matches code.
3. Dashboard, rollback endpoint, and live subscription-CLI subprocess execution are still not implemented.
4. Deterministic v0 path exists and is preserved.
5. AI-first decomposer exists.
6. Project Model v1 exists and is primary for AI decomposer snapshots.
7. Direct xAI live adapter exists.
8. Broader live readiness is still blocked.
9. Related repos still need v1 adoption.

## Where conversations, docs, and code are not aligned

### 1. `README.md` is stale

Severity: high

`README.md` still says the current implementation status is Phase 4 foundation and still describes project decomposition mainly as deterministic Project Model v0 output.

It does not reflect:

- AI-first decomposer
- Project Model v1 as primary
- live xAI adapter
- readiness-register distinction between bounded read-only live and broader live loop blockers

### 2. `AGENTS.md` is stale

Severity: high

`AGENTS.md` current phase stops at Phase 4 and does not mention the post-Phase-4 AI-first decomposer or Project Model v1/live readiness commits.

This matters because `AGENTS.md` is active project context for future agents.

### 3. “Live Grok blocked” is historical, not current headline

Severity: medium

It was true at commit `a26bc37`.

It is superseded by commit `08a3e29`.

Current accurate statement:

- live Grok/xAI is fixed for bounded direct API/read-only smoke through `LiveProjectModelLLM`
- broad autonomous live loops are still blocked by readiness items

### 4. `XAIProvider` is a stale/phantom class name from a compacted summary

Severity: medium

Actual code uses `LiveProjectModelLLM`. No separate `XAIProvider` class was observed.

### 5. Some module names in summaries are shorthand

Severity: low

- `runner_router.py` does not exist; actual file is `arena/router.py`.
- `promoter.py` does not exist; actual `GitPromoter` is in `arena/worktrees.py`.
- `failure_ledger.py` does not exist; actual file is `arena/ledger.py`.

Functionality exists; filenames differ from shorthand.

### 6. Final report has stale commit wording

Severity: low

`docs/verification/2026-06-05-grok-live-rca-project-model-v1-final-report.md` says the slice is ready to commit. It has since been committed locally as `08a3e29`.

### 7. Branch is local-only ahead by 2 commits

Severity: operational note

“Committed locally” is true. “Available remotely” is not true unless pushed.

## Expected status vs actual status

Expected from latest conversations:

- Build Arena should have completed Phase 1-4 foundation.
- It should preserve deterministic Project Model v0 compatibility.
- It should have an AI-first decomposer sidecar pipeline.
- It should emit Project Model v1 as the primary enriched artifact.
- It should have a bounded direct xAI/Grok live adapter.
- It should not yet be ready for full autonomous live worktree mutation/promotion.
- Related repos should still need v1 adoption.

Actual:

- Yes, all of the above is true in code/docs/tests, except `README.md` and `AGENTS.md` do not accurately advertise the newer AI-first/v1/live state.
- The repo is green locally.
- The two latest commits are not pushed to upstream.

## Recommended current status statement

Build Arena is at local commit `08a3e29` with a clean tree and green tests/lint/types. Phases 1-4 are implemented and verified. The deterministic Project Model v0 path is preserved, but the AI-first decomposer now emits Project Model v1 as the primary enriched artifact, with v0 as a compatibility projection. A direct xAI/OpenAI-compatible live adapter exists behind the `--allow-live` guard and fails closed on cancelled/empty/invalid/truncated output. However, Build Arena is not ready for broad live autonomous loops: the readiness register remains `not_ready_blockers_remain`, and broader dry-run hypothesis generation, worktree patch cycles, and promotion are blocked pending v1 adoption in related repos and remaining graph/gap/live-readiness work. `README.md` and `AGENTS.md` are stale and should be updated before future agents rely on them.

## Most important follow-ups

1. Update `AGENTS.md` current phase/status.
   - Mention that the AI-first decomposer exists.
   - Mention that Project Model v1 is primary for AI decomposer snapshots.
   - Mention that v0 is compatibility output.
   - Mention that the live xAI adapter exists only for bounded guarded use.
   - Mention that broader live loops remain blocked by the readiness register.

2. Update `README.md` implementation status and project decomposition sections.
   - Current README under-reports the state as Phase 4/v0.

3. Patch stale wording in the June 5 final report.
   - Replace “ready to commit” with the current local commit outcome.

4. Add a lightweight documentation consistency test.
   - Guard against future drift where docs regress to v0-only/Phase-4-only language.

5. Do not claim production/live autonomous readiness.
   - Correct claim is bounded read-only live adapter ready; broader live loop not ready.

6. Treat old “live Grok blocked” reports as historical.
   - Current state after `08a3e29` is different.

7. Push status remains separate.
   - The branch is ahead of origin by 2. Do not imply remote availability unless pushed.
