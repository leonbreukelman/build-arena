# fmc-mcp schema-fix status — 2026-06-17

Status: completed.

Scope: Build Arena decomposer schema/prompt fix for Grok 4.3 high-reasoning universal `cross_cutting_concerns` category/id drift, followed by a production-profile intake scorecard. No proposal/promotion.

Implementation:
- `arena/project_decomposer_ai.py`: prompt hardening plus narrow in-memory universal concern category canonicalization from exact known-universal concern id.
- `tests/test_project_decomposer_ai.py`: regression tests for observed drift, unknown-category fail-closed guard, and prompt hardening.

Verification:
- Focused new tests: pass.
- `uv run pytest tests/test_project_decomposer_ai.py -q`: pass.
- `uv run pytest tests/test_project_meta_decomposer.py -q`: pass.
- `uv run pyright`: pass.
- `uv run pytest tests -q`: pass.
- `uv run ruff check .`: pass.
- Secret-shaped scan of new report/review/run artifacts: clean.

Review:
- Opus plan: `reports/2026-06-17-fmc-mcp-schema-fix-opus-plan-retry.json`
- Opus implementation review: `reports/2026-06-17-fmc-mcp-schema-fix-opus-review-retry.json`
- Opus verdict: `ACCEPT`, no blocking issues.

Live rerun:
- Run root: `.arena/runs/fmc-mcp-decomposition-grok43-high-reasoning-schema-fix-20260617T221237Z`
- Snapshot: `snapshot-3e9b19da00478bf8`
- Gate: `passed=true`, `violations=[]`
- Deterministic gate rerun command returned `{"passed": true, "violations": []}`.
- Comparison: `reports/2026-06-17-fmc-mcp-schema-fix-rerun-comparison.json`
- Final report: `reports/2026-06-17-fmc-mcp-schema-fix-rerun-report.md`

Intake:
- Profile: `production`
- Freshness: `fresh`, snapshot/current head `25f445806d5221f21d7ac675799db5c30499f1b7`, target repo clean, local `main` one commit ahead of `origin/main`.
- Scorecard: `.arena/runs/fmc-mcp-decomposition-grok43-high-reasoning-schema-fix-20260617T221237Z/intake/scorecard-production.json`
- Markdown scorecard: `.arena/runs/fmc-mcp-decomposition-grok43-high-reasoning-schema-fix-20260617T221237Z/intake/scorecard-production.md`
- Handoff: `.arena/runs/fmc-mcp-decomposition-grok43-high-reasoning-schema-fix-20260617T221237Z/intake/proposer-handoff.json`, `notAuthorizedForMutation=true`.
- Intake report: `reports/2026-06-17-fmc-mcp-production-intake-result.md`
- First recommendation: `ops.runbooks.missing` targeting `docs/runbooks`; score `418.0`.

Conclusion: schema issue resolved and production-profile intake completed. The new high-reasoning decomposition is gate-clean while retaining production-client-first ranking. Intake recommends runbook documentation first. This does not prove proposal/promotion readiness.
