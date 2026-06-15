# Full-autonomy gap remediation implementation status — 2026-06-15

## Plain status

Implemented the first concrete remediation slice from the 2026-06-15 full-autonomy gap plan. The repo now has code and tests for candidate-skip observability, proposal registry/lineage metadata, component verification routing, bounded live-diff repair, Markdown doubled-prefix repair, and multi-target proposal contracts.

This is not yet a claim of broad unattended production autonomy. It is a verified implementation step that removes several blockers that caused the bounded `fmc-mcp` production pass to fail safely.

## Implemented

1. Candidate skip observability
   - `_select_promotable` can emit `CANDIDATE_SKIPPED` with reasons such as `already_tried`, `missing_plan_candidate`, and `empty_verification`.
   - Positive-score candidates no longer disappear silently from the loop.

2. Agent wiki record API
   - Added `arena.agent_wiki` with deterministic JSONL records and secret-like payload rejection.
   - Seeded `docs/agent-wiki/records.jsonl` and added a wiki page for registry/lineage/repair mechanics.

3. Component verification domain
   - Added `component_verification` before `generic_file`.
   - Component findings can inherit load-bearing quality-gate commands from the scorecard's `verification.quality-gates.present` finding.

4. Proposal lineage and registry
   - Added `arena.proposal_registry` with JSONL records, proposal keys, git base lineage, duplicate detection, promoted-skip behavior, and base-head mismatch checks.
   - Proposal plans now include `baseLineage`; candidates include `target_paths`, `base_lineage`, `intent_hash`, `proposal_key`, and `registry_status`.

5. Live proposer context and repair
   - `DiffProposalRequest` now accepts pending proposal notes, failure notes, and repair feedback.
   - `DiffProposerRunner` supports one bounded repair retry and exposes repair events.
   - Repo-goal live-call planning counts the repair attempt.

6. Markdown path repair
   - Markdown reference repair can collapse accidental doubled path segments only when the collapsed path uniquely exists.
   - Legitimate existing repeated paths are preserved.

7. Multi-target proposal contract
   - Proposal drafts/candidates can carry `target_paths`.
   - Boundary and promotion staging checks use the approved target set.
   - The current live diff runner remains single-target; multi-file apply beyond contract/staging remains future work.

8. Closed-loop proof test
   - Added fixture-level proof that promotion advances baseline before a later decomposition event.

## Verified

```text
uv run pytest tests -q
# PASS — 2026-06-15 final run

uv run ruff check .
# PASS — All checks passed!

uv run pyright
# PASS — 0 errors, 0 warnings, 0 informations
```

Independent Opus review file: `reports/2026-06-15-full-autonomy-implementation-final-opus-review.json`.

Opus verdict: `pass`; blockers: none.

Opus non-blocking notes kept as future work: loop registry status transitions are still thin, multi-file candidates fail closed rather than being fully applied, README-less docs candidates may fail the source-reference gate, and broad unattended autonomy still needs control-plane/rollback/real production proof.

## Remaining blockers before a real target-project production run

1. Registry state is created at planning time, but the production loop still needs richer status transitions for `applied_in_worktree`, `failed_gate`, and `promoted` events.
2. Multi-file candidates are represented and protected by boundary/promotion staging, but deterministic/live apply support for actually editing multiple files remains incomplete.
3. Broad unattended autonomy still lacks dashboard/control-plane, rollback endpoint/operator path, and a proven multi-cycle live production promotion on a real target repo.
4. The semantic ablation verifier remains advisory unless a real live ablation runner is added and validated.
