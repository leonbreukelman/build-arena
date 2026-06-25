You are Opus reviewing the REAL live Build Arena decomposition result for fmc-mcp.

Task: compare the real decomposition artifacts against the expected-good criteria and return a concise, blunt owner-facing review.

Scope boundaries:
- This was decomposition only. Do NOT penalize for no intake, no scorecard, no proposal, no promotion, no closed-loop proof.
- Do assess Project Model v1 quality, deterministic gate result, provider metadata, component richness, runtime contracts, external surfaces, invariants, quality gates, backlog/open questions, and provenance-groundedness at the artifact level.
- Do not ask for new Build Arena implementation unless the decomposition itself exposes a blocker.
- Secrets must not be printed; provider metadata should only include api_key_source, not key values.

Expected-good criteria artifact:
<repo>/reports/2026-06-17-fmc-mcp-decomposition-expected-opus-retry.json

Real result summary:
<repo>/reports/2026-06-17-fmc-mcp-decomposition-real-summary.json

Real artifact directory:
<repo>/.arena/runs/fmc-mcp-decomposition-20260617T195758Z/snapshot-ddb951deca8d5c7b

Key files if you need to inspect:
- project-model-v1.json
- manifest.json
- gate-report.json
- model-outputs/decomposer.raw.json
- prompts/decomposer-prompt.txt

Return JSON only:
{
  "verdict": "GOOD" | "MIXED" | "BAD",
  "blockers": ["..."],
  "met_expectations": ["..."],
  "missed_or_weak_expectations": ["..."],
  "important_caveats": ["..."],
  "recommended_next_step": "...",
  "summary": "..."
}
