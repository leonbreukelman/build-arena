# Ticket-ready proposal emit worklog and result

## Branch and commit

- Branch: `ba/proposal-emit-ticket-ready`
- Commit SHA: recorded in the final owner handoff after commit/push. A commit cannot contain its own final hash; verify with `git rev-parse HEAD` on the pushed branch.
- New module: `arena/proposal_emit.py`
- New tests: `tests/test_proposal_emit.py`

## Scope

Built only the emit formatter: `proposal-plan.json` -> rank-1 candidate -> ticket-ready Markdown.

Not built or changed: ticket quality gate/checks, GitHub issue creation/delivery, ticket logging, apply/promote/worktree code, new finding type/domain/schema version, `scorer/`, `verifier/`, or `schema/`.

## Real fmc-mcp run

Run target came from a detached `origin/main` worktree of `github.com/leonbreukelman/fmc-mcp`.

- fmc-mcp source HEAD: `d60155bf05841f97d5ec3ba1752e0b7f588d54ce`
- Snapshot/gate: `reports/2026-06-19-proposal-emit-ticket-ready/fmc-mcp/snapshot-artifacts/snapshot-d9e419b1e0695a46/manifest.json`
- Scorecard: `reports/2026-06-19-proposal-emit-ticket-ready/fmc-mcp/scorecard.json`
- Proposal plan: `reports/2026-06-19-proposal-emit-ticket-ready/fmc-mcp/proposal-plan.json`
- Emitted proposal: `reports/2026-06-19-proposal-emit-ticket-ready/fmc-mcp/proposal.md`
- Field trace: `reports/2026-06-19-proposal-emit-ticket-ready/fmc-mcp/field-trace.md`

Top candidate rendered:

- Finding: `code.component.untested.comp:client`
- Title: Component MCPClient has no observable check
- Target paths: `src/fmc_mcp/client.py`
- Priority score: `540.0`

## Field-by-field trace

- `Title` <- `candidate.title` with `candidate.finding_id` fallback. Fallback was not used.
- `What & where` <- `candidate.intent` + `candidate.target_paths`.
- `Why` <- `candidate.evidence_refs` + `candidate.source_recommended_action`.
- `Definition of done` <- `candidate.success_criterion`.
- `Constraints / guardrails` <- `candidate.grounding_constraints`.
- `How to verify` <- `candidate.verification_commands`.
- `Priority & source` <- `candidate.priority_score` + `candidate.finding_id`.

No derived summary, priority bucket, repo facts block, lineage, registry status, proposal key, or singular `target_path` was rendered. Details are in `field-trace.json` and `field-trace.md`.

## Determinism

Two emitter runs on the same plan produced byte-identical output:

```text
7cb59f0ca88490d07b3ad1d7c77bdf3cc3684448f4eac777bd3114e50aae2e96  reports/2026-06-19-proposal-emit-ticket-ready/fmc-mcp/proposal.md
7cb59f0ca88490d07b3ad1d7c77bdf3cc3684448f4eac777bd3114e50aae2e96  reports/2026-06-19-proposal-emit-ticket-ready/fmc-mcp/proposal-second-run.md
```

## Tests and checks

- `uv run pytest tests/test_proposal_emit.py -q`: 9 passed (also re-run by Opus review).
- `uv run pytest tests -q -rA`: 526 passed, 11 skipped.
- `uv run ruff check .`: All checks passed.
- `uv run pyright`: 0 errors, 0 warnings, 0 informations.
- Protected-path status/diff files are empty:
  - `reports/2026-06-19-proposal-emit-ticket-ready/final-protected-paths-status.txt`
  - `reports/2026-06-19-proposal-emit-ticket-ready/final-protected-paths-head-diff.txt`
  - `reports/2026-06-19-proposal-emit-ticket-ready/final-out-of-scope-source-diff.txt`

## Opus reviews

- Pre-coding Opus review: `ACCEPT_WITH_CHANGES`. Valid changes were incorporated: use planner `candidates`, not ranker `entries`; test no internal-field leakage; no derived priority labels.
- Implementation/output Opus review: `ACCEPT` with blockers `[]`.

## What I built

A deterministic formatter and CLI: `python -m arena.proposal_emit --plan <proposal-plan.json> --output <proposal.md>`.

## What I ran

Decompose -> intake -> propose -> emit on fmc-mcp using the live xAI `grok-4.3` snapshot path; then focused tests, full pytest, ruff, pyright, deterministic double-run check, protected-path checks, and Opus review.

## Anything that did not hold

The first full ruff pass caught one unused test import. I fixed the test to exercise `emit_proposal()` directly. After that, ruff/pytest/pyright passed.
