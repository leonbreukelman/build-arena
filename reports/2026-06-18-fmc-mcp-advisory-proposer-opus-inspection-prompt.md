# Opus inspection request: Build Arena proposer actionability for advisory architecture/verification findings

You are reviewing Build Arena's current proposer/planner code. Use only the repo code under the supplied `arena/` directory and the run evidence embedded below. Return JSON only.

User question to answer:

- The current intake scorecard produces useful diagnostic/advisory findings such as `architecture.open-questions-or-gaps` and `verification.quality-gates.present`.
- The current proposer can run docs candidates, but advisory architecture/verification findings get skipped as `no_single_file_target`.
- Inspect the current proposer code and identify what is required for it to solve advisory architecture and verification findings instead of merely skipping them.
- Distinguish minimal patch, proper architecture, and risks.

Code paths to inspect:

- `arena/proposal_planner.py`
- `arena/proposal_domains.py`
- `arena/proposal_ranker.py`
- `arena/proposal_candidate_runner.py`
- `arena/runners/diff_proposer.py`
- `arena/project_intake_scorecard.py`
- related helpers if necessary.

Run evidence from current bounded proposer run:

- Target repo: `<projects>/fmc-mcp`
- Base head: `25f445806d5221f21d7ac675799db5c30499f1b7`
- Isolated worktree: `<repo>/.arena/worktrees/fmc-mcp-proposer-docs-rank1-20260618T013019Z`
- Run dir: `<repo>/.arena/runs/fmc-mcp-proposer-docs-rank1-20260618T013019Z`
- Candidate rank 1: `ops.runbooks.missing`, target `docs/runbooks/index.md`
- Result: safe failure; worktree clean after reversal; no patch recorded.
- Runner stdout:

```json
{"error": "RunnerError: missing Markdown link target: docs/index.md->docs/runbooks/docs/index.md, README.md->docs/runbooks/README.md", "ok": false}
```

Current scorecard findings from fmc-mcp production intake:

1. `ops.runbooks.missing` — 418.0 — `safe_to_patch_docs_only` — verification `test -e docs/runbooks`
2. `verification.quality-gates.present` — 216.0 — `advisory_only` — verification commands `uv run --extra dev mypy src/fmc_mcp`, `uv run --extra dev python -m pytest -q`, `uv run --extra dev ruff check .`
3. `agent.agents-md.missing` — 192.0 — `safe_to_patch_docs_only`
4. `architecture.open-questions-or-gaps` — 126.0 — `advisory_only` — verification `[]`
5. `decision.history.missing` — 110.0 — `safe_to_patch_docs_only`

Docs-addressed simulation evidence:

- After simulating `AGENTS.md`, `docs/runbooks`, and `docs/decisions` existing, intake emits:
  1. `verification.quality-gates.present` — 216.0 — `advisory_only`
  2. `architecture.open-questions-or-gaps` — 126.0 — `advisory_only`
- `proposal_planner` then emits 0 candidates and skips both as `no_single_file_target`.
- `proposal_ranker` emits `candidateCount: 0`; both skipped with `no_single_file_target`.

Return JSON only with this schema:

{
  "summary": "one paragraph",
  "current_code_findings": [
    {
      "id": "short-id",
      "severity": "critical|high|medium|low",
      "evidence": ["file:line or function evidence"],
      "finding": "what the code currently does",
      "required_change": "what must change"
    }
  ],
  "minimal_viable_patch": ["concrete code/design steps"],
  "proper_architecture": ["domain/model/runner changes for a durable solution"],
  "advisory_architecture_finding_design": {
    "candidate_generation": "how architecture.open-questions-or-gaps should become candidate(s)",
    "target_selection": "how to choose files/targets without fabricating",
    "verification_gate": "what mechanical gate rejects shallow/no-op fixes"
  },
  "advisory_verification_finding_design": {
    "candidate_generation": "how verification quality/advisory findings should become candidate(s) or context",
    "target_selection": "what it may target",
    "verification_gate": "mechanical gate"
  },
  "doc_proposer_failure_note": "explain the docs link failure and whether it affects advisory design",
  "risks": ["risk and mitigation"],
  "recommended_next_implementation_slice": ["ordered steps"]
}
