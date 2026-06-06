# Fresh Session Prompt: Implement Build Arena Documentation and Artifact Alignment

Use this prompt in a new Hermes session to implement the reviewed plan that aligns Build Arena’s active documentation and artifacts with the actual code status.

## Direct goal

Implement the documentation/artifact alignment plan for:

- Repository: `/home/leonb/projects/build-arena`
- Plan: `docs/plans/2026-06-05-build-arena-doc-artifact-alignment-plan.md`
- Status report: `docs/verification/2026-06-05-build-arena-expected-vs-actual-status.md`
- Opus plan review: `docs/verification/2026-06-05-build-arena-doc-artifact-alignment-plan-opus-review.md`

The plan has already been reviewed by Opus and patched for the required changes. Your job is implementation, verification, and a local commit if all gates pass.

## Current intended truth to align docs with

Build Arena is at/after local commit:

- `08a3e29 [verified] add live xai decomposer and project model v1 readiness`

The docs must state this accurately:

1. Phase 1-4 foundation is implemented and verified.
2. No dashboard control plane, rollback endpoint, or live subscription-CLI subprocess execution is implemented.
3. The deterministic Project Model v0 path remains for compatibility.
4. The AI-first decomposer emits `project-model-v1.json` as the primary enriched artifact and also emits `project-model-v0.json` as compatibility output.
5. `LiveProjectModelLLM` provides a bounded direct xAI/OpenAI-compatible adapter behind the CLI `--allow-live` guard.
6. The pre-live readiness register remains `not_ready_blockers_remain`; broad autonomous live loops, worktree patch cycles, and promotion are not ready.
7. Elenchus Core and Arena Calibration remain v0-only follow-up repos for v1 adoption.
8. The two latest commits are local-only until pushed; do not imply remote availability.

## Hard boundaries

Do not modify:

- `scorer/`
- `verifier/`
- `schema/`
- `.arena/scorer.lock.toml`
- `arena/generated/`

Do not implement:

- dashboard control plane
- rollback endpoint
- live subscription-CLI subprocess execution
- broader live loop
- worktree patch cycles
- promotion/merge behavior
- parser/indexer upgrades such as Tree-sitter, ast-grep, SCIP/LSIF, or CodeQL

Do not:

- push
- merge
- deploy
- run paid/live provider calls
- rewrite historical reports whose “live Grok blocked” statement was accurate for commit `a26bc37`
- include or expose credentials/API keys/tokens/passwords

Local commit is authorized only after all verification gates pass. Push is not authorized.

## Required skills to load first

Before answering or acting, load and follow relevant skills:

- `disciplined-project-delivery`
- `writing-plans`
- `test-driven-development`
- `agent-context-engineering`
- `autonomous-coding-agents` if using Opus/Claude Code review

## Required preflight

Run:

```bash
pwd
git rev-parse --show-toplevel
git status -sb
git branch --show-current
git remote -v
git log --oneline -5
```

Read these exact files before quoting or editing them:

- `README.md`
- `AGENTS.md`
- `docs/plans/2026-06-05-build-arena-doc-artifact-alignment-plan.md`
- `docs/verification/2026-06-05-build-arena-expected-vs-actual-status.md`
- `docs/verification/2026-06-05-build-arena-doc-artifact-alignment-plan-opus-review.md`
- `docs/verification/2026-06-05-grok-live-rca-project-model-v1-final-report.md`
- `docs/verification/2026-06-05-pre-live-readiness-register.json`
- `docs/specs/2026-06-05-project-model-v1-shared-contract-spec.md`

Inspect real CLI help before documenting command examples:

```bash
uv run python -m arena.decomposer --help
uv run python -m arena.project_model_cli --help
uv run python -m arena.project_model_cli snapshot --help
uv run python -m arena.project_model_cli graph --help
uv run python -m arena.project_model_cli gate --help
```

Stop and report instead of editing if:

- repo root is not `/home/leonb/projects/build-arena`;
- target files have unexpected dirty changes;
- HEAD is before `08a3e29` or the plan/status report is clearly stale;
- a documented command cannot be made valid from actual CLI help without changing implementation code.

## Implementation tasks

Follow the plan exactly. In summary:

### Task 1 — Write failing doc-consistency tests first

Create:

- `tests/test_project_status_docs.py`

Tests must check:

- README contains current AI-first / Project Model v1 / bounded live status markers.
- README no longer contains the exact stale Phase 4-only current-status sentence.
- README does not overclaim production/broad-live readiness.
- AGENTS.md contains current AI-first / Project Model v1 / `LiveProjectModelLLM` / readiness-register markers.
- AGENTS.md no longer has `## Current phase`; it has `## Current implementation status`.
- AGENTS.md does not contain stale identifiers such as `XAIProvider`, `runner_router.py`, `promoter.py`, or `failure_ledger.py`.
- AGENTS.md preserves anti-fabrication, blocked-path, and worktree safety rules.
- June 5 final report records committed local outcome and no longer says merely “ready to commit.”
- Documented CLI surfaces exist by running safe `--help` commands only.

Important test-design note: the required negative readiness phrase “not ready for broad autonomous live loops” contains the substring “ready for broad autonomous live loops”. Do not write a naive forbidden-substring assertion that rejects the required negative phrase. Either use a different required marker such as “blocked for broad autonomous live loops” or make the overclaim check negation-aware.

Run:

```bash
uv run pytest tests/test_project_status_docs.py -q
```

Expected before docs edits: FAIL for stale/missing markers.

### Task 2 — Update README.md

Update README to reflect:

- Phase 4 foundation complete.
- Post-Phase-4 AI-first decomposer implemented.
- Project Model v1 primary artifact.
- Project Model v0 compatibility artifact.
- Bounded direct xAI live adapter behind `--allow-live`.
- Broad autonomous live loops not ready; readiness blockers remain.
- Correct verified CLI examples for deterministic/v0 and AI-first snapshot/gate/graph paths.

Use actual `--help` output to keep examples valid.

Do not claim production readiness or broad autonomous live readiness.

### Task 3 — Update AGENTS.md

Preserve all existing anti-fabrication, boundary, and worktree rules.

Replace `## Current phase` with `## Current implementation status` that states:

- Phase 4 foundation complete and verified.
- AI-first decomposer implemented.
- `project-model-v1.json` primary for AI decomposer snapshots.
- `project-model-v0.json` compatibility output.
- `LiveProjectModelLLM` direct xAI/OpenAI-compatible bounded live path behind `--allow-live`.
- Readiness register remains `not_ready_blockers_remain`.
- Broad live loops/dry-run hypothesis generation from v1/worktree patch cycles/promotion remain blocked.
- Dashboard control plane, rollback endpoint, and live subscription-CLI subprocess execution remain unimplemented.

Add concise decomposer command bullets in the Commands section.

### Task 4 — Patch June 5 final report stale commit wording

Modify only:

- `docs/verification/2026-06-05-grok-live-rca-project-model-v1-final-report.md`

Replace the actual observed “ready to commit” wording with:

```text
This slice was committed locally as `08a3e29 [verified] add live xai decomposer and project model v1 readiness`. It was not pushed, merged, deployed, used to start a broader live loop, or used to enable worktree mutation/promotion.
```

Do not rewrite historical RCA sections.

### Task 5 — Verify targeted test now passes

Run:

```bash
uv run pytest tests/test_project_status_docs.py -q
```

Expected: PASS.

### Task 6 — Full verification and hygiene

Run:

```bash
uv run pytest tests -q
uv run ruff check .
uv run pyright
git diff --check
```

Run a changed-doc secret scan that rejects assignment-like secret leaks but allows bare env var names such as `XAI_API_KEY`.

Run a changed-doc draft-marker scan for true uppercase draft-marker words.

### Task 7 — Independent implementation review before commit

If Claude Code Opus is available, run a read-only diff review with no tools allowed. Ask whether:

- README and AGENTS reflect actual status without overclaiming.
- Historical RCA artifacts are preserved appropriately.
- Tests are durable and not merely presence-only.
- AGENTS safety rules were preserved.
- CLI examples match actual `--help` output.

If Opus is unavailable, label the review skipped. Do not invent a review verdict.

### Task 8 — Local commit only after verification

If all verification passes and no review blocker remains, stage only:

- `README.md`
- `AGENTS.md`
- `docs/verification/2026-06-05-grok-live-rca-project-model-v1-final-report.md`
- `tests/test_project_status_docs.py`

Then run:

```bash
git diff --cached --check
git status --short
git commit -m "[verified] align build-arena status docs"
```

Use the `[verified]` prefix only if full local verification passed and any requested/available independent implementation review did not identify unresolved blockers.

Do not push.

## Verification commands expected in final response

Report results for:

- `uv run pytest tests/test_project_status_docs.py -q`
- `uv run pytest tests -q`
- `uv run ruff check .`
- `uv run pyright`
- `git diff --check`
- `git diff --cached --check` if committing
- secret scan
- draft-marker scan
- Opus implementation review, or state explicitly that it was skipped/unavailable

## Final response requirements

Start with one of:

- `Aligned and verified.`
- `Aligned locally but not committed.`
- `Blocked.`

Then include:

- exact files changed
- local commit hash if committed
- confirmation that push/merge/deploy/live-provider calls were not performed
- verification commands and results
- Opus review verdict or skipped/unavailable reason
- final git status
