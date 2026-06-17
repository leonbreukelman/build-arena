You are Opus doing a final implementation review for Build Arena.

Scope: review the doc-status lifecycle guard implementation and its tests. The implementation report is at `reports/2026-06-17-doc-status-lifecycle-guard-implementation-report.md`.

Your primary job is to break the guard or find a material testing gap. This is a load-bearing status-drift guard, so do not only check whether the report sounds plausible. Check whether the test would actually prevent the stale-status failure class without overfitting or causing obvious false positives.

Review questions:
1. Does the implementation match the prior Opus plan closely enough?
2. Are the tests sufficient for the intended failure mode: active dated status docs tracked in HEAD should not claim `not committed` / `implemented locally` after landing?
3. Does `docs/status/INDEX.md` create a maintainable active/superseded/historical map without overloading the broad readiness register?
4. Are the TDD and verification claims backed by the evidence in the report?
5. Run or inspect the relevant tests if needed. Exact commands already run by Hermes were:
   - `uv run python -m pytest tests/test_project_status_docs.py -k "status_index or active_status or superseded_status or project_graph_status" -v`
   - `uv run python -m pytest tests/test_project_status_docs.py -v`
   - `uv run ruff check tests/test_project_status_docs.py`
   - `uv run pyright tests/test_project_status_docs.py`
   - `make test`
   - `make lint`
   - `make typecheck`

Do not edit files. If you run commands, run read-only verification only.

Return concise JSON only:
{
  "verdict": "ACCEPT" | "ACCEPT_WITH_CHANGES" | "REJECT",
  "mustFixBeforeFinal": ["..."],
  "testAdequacy": "...",
  "notes": ["..."]
}
