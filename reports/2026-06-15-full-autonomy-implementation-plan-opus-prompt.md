You are Opus creating an implementation plan for Leon's Build Arena project.

Repo root: /home/leonb/projects/build-arena
Primary diagnosis: /home/leonb/projects/build-arena/docs/specs/2026-06-15-full-autonomy-gap-analysis.md
Agent wiki seed: /home/leonb/projects/build-arena/docs/agent-wiki/index.md
Run report: /home/leonb/projects/build-arena/reports/2026-06-15-fmc-mcp-production-pass-and-proposal-pipeline-report.md
Run root: /home/leonb/projects/build-arena/.arena/runs/fmc-mcp-production-20260615T001605Z

Goal:
Create an implementation plan that moves Build Arena materially closer to full repo-scale autonomy after the failed fmc-mcp production pass.

Required plan priorities:
1. Fix top-ranked code findings being unrunnable: code/component findings must become candidates with load-bearing verification, and silent skips must be visible.
2. Add proposal lineage + registry/dedup: proposal artifacts anchored to base branch/head/snapshot/scorecard; persistent proposal state for pending/applied/failed/promoted/rejected/duplicate proposals.
3. Feed registry/wiki context into live proposal prompts so the model sees pending/invisible proposals and known failure modes.
4. Add bounded repair/retry for live proposer gate failures, especially Markdown local-link path errors.
5. Support the first real closed-loop proof: promote one candidate, then re-decompose/re-intake before selecting the next candidate.
6. Establish the agent wiki as a first-class repo artifact used by future agents and, eventually, by proposer prompts.
7. Explicitly encode generous but bounded turn/tool guidance: do not use tiny max-turn/tool caps for implementation agents; separate read/investigation budget from write/mutation/live-call budget; use high per-phase ceilings and hard cost/mutation/divergence caps.

Constraints:
- Do not modify protected dirs `scorer/`, `verifier/`, `schema/`, or `arena/generated/`.
- Prefer TDD. The plan should name tests to add before code.
- Keep work in session-sized phases. Each phase should be independently verifiable.
- Avoid broad, hand-wavy instructions. Name exact files likely to change and exact verification commands.
- Plan only; do not implement.
- The plan should be suitable for a fresh Hermes agent to execute with generous but bounded budgets.

Read-only tools allowed. You may inspect code/artifacts but do not edit.

Return JSON only, no markdown fences:
{
  "verdict": "...",
  "implementationPlanMarkdown": "complete markdown plan text",
  "phaseSummary": [
    {"phase": 1, "name": "...", "goal": "...", "files": ["..."], "tests": ["..."], "verification": ["..."]}
  ],
  "recommendedExecutionLimits": ["..."],
  "openRisks": ["..."],
  "firstAction": "..."
}
