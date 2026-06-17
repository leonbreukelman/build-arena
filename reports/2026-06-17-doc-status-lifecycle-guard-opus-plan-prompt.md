You are Opus reviewing a Build Arena implementation task before coding. Return a concrete, implementation-ready plan only; do not edit files.

Task from Leon: implement a guard for the gap where dated docs/status files can say a feature is "implemented locally/not committed" after the branch/PR has already merged. Use existing Build Arena conventions and TDD.

Repo facts already inspected:
- Repo: `<repo>`
- Current branch: main...origin/main
- HEAD: 360e9a2 Merge pull request #40 from leonbreukelman/graph/call-inheritance-treesitter
- Feature commit: af48ead feat: add project graph call and inheritance edges
- Current untracked reports exist under reports/ from analysis/reviews; avoid relying on them as source code.

Existing relevant files:
1. tests/test_project_status_docs.py already guards README/AGENTS/project-brief/readiness docs. It has helper:
   ROOT = Path(__file__).resolve().parents[1]
   def _read(relative: str) -> str:
       return (ROOT / relative).read_text(encoding="utf-8")
   It already imports json, re, subprocess, Path.
   It contains tests like:
   - test_readme_describes_ai_first_v1_and_bounded_live_status
   - test_agents_current_status_reflects_post_phase4_decomposer_and_readiness
   - test_project_brief_current_status_matches_implemented_foundation
   - test_june5_final_report_records_committed_outcome_not_precommit_state
   - test_docs_describe_bounded_real_run_attempt_as_safe_failed_not_unqualified_readiness
   - test_pre_live_register_scopes_bounded_fmc_mcp_production_run_without_broad_overclaim
   - test_orientation_docs_referenced_arena_modules_exist
   - test_documented_intake_proposal_cli_surfaces_exist

2. Stale status doc:
   docs/status/2026-06-16-project-graph-call-inheritance-treesitter.md
   line 3 currently says:
   Status: implemented locally on branch `graph/call-inheritance-treesitter`; not committed.
   But git shows the branch merged to main via PR #40 / merge commit 360e9a2, and the file exists in HEAD from af48ead.

3. docs/status currently contains only dated .md files and no index:
   - 2026-06-16-project-graph-call-inheritance-treesitter.md
   - 2026-06-14-live-repo-goal-loop.md
   - 2026-06-15-full-autonomy-gap-remediation-implementation-status.md
   - 2026-06-15-current-status-timeline-production-readiness.md
   - 2026-06-14-progress-timeline-and-production-readiness-audit.md

4. Prior analysis conclusion:
   - This is not a Hermes memory problem.
   - Hermes skills/session search/cron/hooks can help, but the authoritative guard should be repo-level pytest.
   - The readiness register should remain broad-autonomy readiness only, not per-feature merge tracking.
   - A docs/status index/current map plus tests is likely enough.

Constraints:
- Respect AGENTS.md: do not touch scorer/, verifier/, schema/, arena/generated/, .arena/scorer.lock.toml.
- Use TDD: add failing tests first, verify RED, then patch docs/code to pass.
- Prefer targeted edits: tests/test_project_status_docs.py plus docs/status files.
- Do not add heavy infrastructure unless necessary.
- Avoid a brittle test that forbids historically valid wording in clearly historical/superseded docs. Need a clean active/historical/superseded distinction.
- Keep the solution understandable for future agents.

Please propose:
1. Minimal file changes.
2. Exact test behavior to add.
3. How to model current vs historical/superseded status docs.
4. How to patch the stale 2026-06-16 status doc.
5. Verification commands to run.
6. Risks/boundaries.

Return markdown with a concise plan and acceptance criteria.