You are independently reviewing a Build Arena run-prep report before a bounded live run against fmc-mcp.

Artifact under review:
<repo>/reports/2026-06-17-fmc-mcp-run-prep.md

Scope:
- Review the artifact for owner-facing safety, command correctness, internal consistency, and overclaims.
- Do not ask for broad new implementation work.
- Assume the artifact's cited command outputs are producer-provided evidence; you may read the artifact itself.
- Focus on whether the recommended live command is dangerous/incomplete, whether API-spend and mutation gates are visible, whether broad-autonomy caveats are honest, and whether any wording could mislead Leon into thinking the run is already a success.

Return compact JSON only:
{
  "verdict": "PASS" | "REVISE",
  "blockers": ["..."],
  "recommended_corrections": ["..."],
  "non_blocking_notes": ["..."],
  "summary": "..."
}
