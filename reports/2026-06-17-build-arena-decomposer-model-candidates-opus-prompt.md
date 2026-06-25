You are Opus reviewing a model-selection recommendation for Build Arena's live project decomposer role.

Task: Review the report for correctness, overclaims, missing caveats, and whether the recommended candidate order is reasonable.

Scope:
- This is not an implementation review. It is a model-research/recommendation review.
- Evidence includes a saved report and supporting source artifacts under <repo>/reports.
- Check especially whether the report overstates benchmark relevance, ignores schema/gate issues, or recommends non-reproducible routers too strongly.
- Return JSON only.

Primary report:
<repo>/reports/2026-06-17-build-arena-decomposer-model-candidates.md

Supporting artifacts:
<repo>/reports/2026-06-17-build-arena-decomposer-model-shortlist.json
<repo>/reports/2026-06-17-model-candidate-research-raw.json
<repo>/reports/2026-06-17-fmc-mcp-grok43-high-vs-nonreasoning-report.md

Return JSON:
{
  "verdict": "ACCEPT" | "ACCEPT_WITH_CORRECTIONS" | "REJECT",
  "valid_criticisms": ["..."],
  "overclaims_or_errors": ["..."],
  "missing_caveats": ["..."],
  "recommended_patches": ["..."],
  "summary": "..."
}
