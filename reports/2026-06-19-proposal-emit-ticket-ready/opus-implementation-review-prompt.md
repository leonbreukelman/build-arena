You are Claude Code Opus Max acting as the independent reviewer for Build Arena foundation stage 4.

Repo: /home/leonb/projects/build-arena-proposal-emit
Branch: ba/proposal-emit-ticket-ready

Frozen scope:
- ONLY add emit step: decompose -> intake -> propose -> emit one formatted proposal.
- New formatter reads proposal-plan.json, takes rank-1 candidate, and writes deterministic ticket-ready Markdown.
- It must render only existing candidate fields and fabricate nothing.
- Out of scope: ticket gate/checks, GitHub issue creation/delivery, ticket logging, apply/promote/worktree changes, new finding/domain/schema versions, scorer/verifier/schema changes.

Files to inspect:
- arena/proposal_emit.py
- tests/test_proposal_emit.py
- reports/2026-06-19-proposal-emit-ticket-ready/fmc-mcp/proposal-plan.json
- reports/2026-06-19-proposal-emit-ticket-ready/fmc-mcp/proposal.md
- reports/2026-06-19-proposal-emit-ticket-ready/fmc-mcp/field-trace.json
- reports/2026-06-19-proposal-emit-ticket-ready/fmc-mcp/proposal-hashes.txt
- reports/2026-06-19-proposal-emit-ticket-ready/logs/pytest-tests-q.log
- reports/2026-06-19-proposal-emit-ticket-ready/logs/ruff-check.log
- reports/2026-06-19-proposal-emit-ticket-ready/logs/pyright.log
- reports/2026-06-19-proposal-emit-ticket-ready/git-status-before-review.txt
- reports/2026-06-19-proposal-emit-ticket-ready/protected-paths-head-diff.txt
- reports/2026-06-19-proposal-emit-ticket-ready/protected-paths-status.txt

Main-agent verification already run:
- uv run pytest tests/test_proposal_emit.py -q: passed before full run.
- uv run pytest tests -q: passed.
- uv run ruff check .: passed after one unused-import fix.
- uv run pyright: 0 errors, 0 warnings, 0 informations.
- fmc-mcp foundation run used a detached origin/main worktree at d60155bf05841f97d5ec3ba1752e0b7, live xAI grok-4.3 snapshot gate passed, scorecard/proposal-plan emitted, proposal_emit run twice produced identical SHA256 7cb59f0ca88490d07b3ad1d7c77bdf3cc3684448f4eac777bd3114e50aae2e96.

Review questions:
1. Does arena/proposal_emit.py implement only the requested emit formatter and CLI?
2. Does the formatter map exactly these candidate fields and no others?
   - Title <- title fallback finding_id
   - What & where <- intent + target_paths
   - Why <- evidence_refs + source_recommended_action
   - Definition of done <- success_criterion
   - Constraints / guardrails <- grounding_constraints
   - How to verify <- verification_commands
   - Priority & source <- priority_score + finding_id
3. Does the output proposal.md trace to proposal-plan.json with no invented candidate content and no internal field leakage (repo_facts_block, lineage, registry, proposal_key, etc.)?
4. Do tests cover rank-1 selection, no rank-2 leakage, no unmapped/internal field leakage, deterministic evidence key order, fallback title, empty-section omission, CLI output, and fail-closed empty/invalid candidate plans?
5. Did this touch any out-of-scope code path (repo_goal_loop/apply/promote/GitHub delivery/gates/schemas/scorer/verifier)?
6. Any blocker before commit/push?

You may run read-only commands if useful. Do not edit files.
Return JSON only:
{
  "verdict": "ACCEPT" | "ACCEPT_WITH_CHANGES" | "REJECT",
  "blockers": ["..."],
  "checkedClaims": [{"claim":"...", "status":"pass|fail|partial", "evidence":"..."}],
  "requiredChanges": ["..."],
  "nonBlockingNotes": ["..."],
  "leonSummary": "one blunt sentence"
}
