# Opus review prompt: pairwise proposer re-ranker design

You are the independent reviewer for a Build Arena design artifact.

Artifact to review:
- `<repo>/docs/specs/2026-06-19-pairwise-proposal-reranker-design.md`

Relevant repo files to inspect if needed:
- `<repo>/arena/proposal_planner.py`
- `<repo>/arena/proposal_ranker.py`
- `<repo>/arena/proposal_domains.py`
- `<repo>/arena/llm_adapter.py`
- `<repo>/arena/repo_goal_loop.py`
- `<repo>/docs/schemas/proposal-plan-v0.schema.json`
- `<repo>/docs/agent-wiki/index.md`

User goal/scope:
- Add a relative pairwise re-ranker that selects the single best proposal from an existing proposal-plan.json candidate set using ONE default LLM.
- It replaces reliance on absolute priority_score for final pick.
- Mechanical pre-filter drops ungrounded/unrunnable/non-binding/vague/circular candidates.
- Pairwise king-of-the-hill over survivors, both orderings for every matchup; inconsistent swapped result keeps incumbent.
- Set winner rank 1 in the plan so existing emit is unchanged.
- Output comparison trace.

Hard out-of-scope:
- No panel, multiple models, OpenRouter, golden set, self-improvement loop, profile/overlay.
- No changes to decompose, intake, emit, or any gate.
- No new finding types, absolute quality scores, or ticket/GitHub anything.

Review questions:
1. Does the design stay inside the scope and avoid the forbidden work?
2. Is the pre-filter mechanically implementable from current proposal-plan and ProjectGraph structures?
3. Is the no-op/binding verification proposal correct and safe enough, or does it need narrowing?
4. Does the pairwise tournament handle position bias deterministically as requested?
5. Does the output plan strategy remain compatible with proposal-plan-v0 and existing rank-1 emit?
6. Does the prompt text force evidence citation and fixed JSON without leaking priority_score/rank?
7. What must be patched before this plan is implementation-ready?

Return JSON only:
{
  "verdict": "ACCEPT" | "ACCEPT_WITH_CHANGES" | "REJECT",
  "blockers": ["..."],
  "required_patches": ["..."],
  "non_blocking_notes": ["..."],
  "scope_drift_found": ["..."],
  "implementation_risks": ["..."],
  "summary_for_leon": "one blunt sentence"
}
