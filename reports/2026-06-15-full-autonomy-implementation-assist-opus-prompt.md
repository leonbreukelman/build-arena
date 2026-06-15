You are Opus assisting a Hermes implementation pass in /home/leonb/projects/build-arena.

Read-only task: inspect the current repo and the implementation plan at docs/plans/2026-06-15-full-autonomy-gap-remediation-plan.md, then give efficient implementation guidance for completing the plan with minimal churn.

Focus:
1. Identify the smallest coherent implementation sequence that satisfies the plan without overengineering.
2. Flag current tests/helpers that should be reused.
3. Identify likely compatibility traps in proposal_planner/proposal_domains/repo_goal_loop/diff_proposer.
4. Suggest concrete code shapes for proposal registry/lineage, agent wiki record API, candidate skip events, repair retry, and multi-target candidates.
5. Be strict about protected paths: do not touch scorer/, verifier/, schema/, arena/generated/.
6. Do not edit files. Return a concise but implementation-useful report.

Current relevant artifacts:
- docs/plans/2026-06-15-full-autonomy-gap-remediation-plan.md
- docs/specs/2026-06-15-full-autonomy-gap-analysis.md
- docs/agent-wiki/index.md
- arena/repo_goal_loop.py
- arena/proposal_planner.py
- arena/proposal_domains.py
- arena/runners/diff_proposer.py
- tests/test_repo_goal_loop.py
- tests/test_proposal_planner.py
- tests/test_proposal_domains.py
- tests/test_diff_proposer.py

Return JSON only:
{
  "recommendedSequence": ["..."],
  "reusePoints": ["..."],
  "compatibilityTraps": ["..."],
  "minimalCodeShapes": ["..."],
  "testsToPrioritize": ["..."],
  "risks": ["..."],
  "verdict": "..."
}
