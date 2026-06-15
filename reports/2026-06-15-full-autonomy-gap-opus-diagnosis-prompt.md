You are Opus performing a read-only research/diagnosis pass for Leon's Build Arena project.

Repo root: /home/leonb/projects/build-arena
Target repo from production pass: /home/leonb/projects/fmc-mcp
Run root: /home/leonb/projects/build-arena/.arena/runs/fmc-mcp-production-20260615T001605Z
Prior report: /home/leonb/projects/build-arena/reports/2026-06-15-fmc-mcp-production-pass-and-proposal-pipeline-report.md

Goal to evaluate against:
Build Arena's final goal is full repo-scale autonomy: given a repo-level `/goal`, it should decompose the target project, build a fresh project model, keep intake synced to the latest accepted model, produce grounded cross-domain proposals against a specific branch/snapshot/base, avoid duplicate/invisible proposal churn, apply a candidate in an isolated worktree, mechanically verify it through a load-bearing domain gate, promote safely, then re-decompose/re-intake before the next cycle under bounded budget/divergence controls.

User asks:
1. Research this result.
2. Identify deviations from the final goal of full autonomy.
3. For each finding, provide a problem statement and root cause.
4. Include that the project needs an agent wiki to work effectively.
5. Include that future implementation agents should use generous but bounded turn/tool budgets: do not make tiny max-turn caps/tool caps that prevent real investigation; set upper high-level limits per phase instead.

Read-only instructions:
- You may read repo files and run read-only shell commands for inspection only.
- Do not edit files, call live APIs, create branches, commit, push, or mutate target repos.
- Do not read .env or credentials.
- Use the event stream and artifact files as source of truth. Do not infer success that is not recorded.
- Be blunt. Do not soften safe failure into success.

Evidence to inspect at minimum:
- reports/2026-06-15-fmc-mcp-production-pass-and-proposal-pipeline-report.md
- .arena/runs/fmc-mcp-production-20260615T001605Z/loop-events.jsonl
- .arena/runs/fmc-mcp-production-20260615T001605Z/post-run-pipeline/freshness.json
- .arena/runs/fmc-mcp-production-20260615T001605Z/post-run-pipeline/intake-scorecard.json
- .arena/runs/fmc-mcp-production-20260615T001605Z/post-run-pipeline/proposal-duplicate-summary.json
- .arena/runs/fmc-mcp-production-20260615T001605Z/post-run-pipeline/proposal-runs/proposal-plan-01.json
- arena/repo_goal_loop.py
- arena/proposal_planner.py
- arena/proposal_ranker.py
- arena/proposal_domains.py
- arena/runners/diff_proposer.py
- arena/project_intake_scorecard.py
- AGENTS.md / README.md only if needed for goal/status framing.

Return JSON only, no markdown fences, with this shape:
{
  "verdict": "...",
  "oneSentenceGap": "...",
  "deviationFindings": [
    {
      "id": "short-stable-id",
      "title": "...",
      "severity": "critical|high|medium|low",
      "problemStatement": "plain problem statement",
      "rootCause": "specific root cause, ideally naming code/artifact boundary",
      "evidence": ["path:line or artifact/event evidence"],
      "deviationFromFullAutonomy": "how this prevents the final goal",
      "implementationImplication": "what must change",
      "acceptanceSignal": "what proof would show this is fixed"
    }
  ],
  "agentWikiRequirement": {
    "problemStatement": "...",
    "rootCause": "...",
    "minimumContents": ["..."],
    "acceptanceSignal": "..."
  },
  "executionBudgetGuidance": {
    "problemStatement": "...",
    "rootCause": "...",
    "recommendedLimits": ["..."],
    "acceptanceSignal": "..."
  },
  "priorityOrder": ["finding-id-1", "finding-id-2"],
  "notesForImplementationPlanner": ["..."]
}
