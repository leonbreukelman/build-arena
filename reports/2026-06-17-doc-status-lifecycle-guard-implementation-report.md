# Doc-status lifecycle guard implementation report — 2026-06-17
## Summary
- Added a repo-level status lifecycle guard to `tests/test_project_status_docs.py`.
- Added `docs/status/INDEX.md` as the explicit Active/Superseded/Historical classification map for dated status docs.
- Patched the project-graph status doc from stale `not committed` wording to merged PR/commit truth.
- Used TDD: focused lifecycle tests failed before the index/status patch, then passed after.
- Opus final review found one material regex bypass (`not yet merged`); added a RED regression test, patched the regex, and reran focused/full gates.

## Files changed
- `tests/test_project_status_docs.py`
- `docs/status/INDEX.md`
- `docs/status/2026-06-16-project-graph-call-inheritance-treesitter.md`

## TDD evidence
Initial RED command before doc/index patch:

```text
uv run python -m pytest tests/test_project_status_docs.py -k "status_index or active_status or superseded_status or project_graph_status" -v
Result: 4 failed as expected: missing docs/status/INDEX.md plus stale project-graph Status line.
```

Opus-review RED regression for regex bypass:

```text
uv run python -m pytest tests/test_project_status_docs.py::test_active_status_stale_claim_regex_rejects_negated_merge_phrasing -v
Result before regex patch: 1 failed; `Status: implemented locally; not yet merged; not committed.` was not caught.
```

Final verification commands:

```text
uv run python -m pytest tests/test_project_status_docs.py -k "status_index or active_status or superseded_status or project_graph_status" -v
# 5 passed, 19 deselected

uv run python -m pytest tests/test_project_status_docs.py -v
# 24 passed

uv run ruff check tests/test_project_status_docs.py && uv run pyright tests/test_project_status_docs.py
# ruff passed; pyright 0 errors, 0 warnings, 0 informations

make test
# exit 0; full test suite passed with 11 skipped tests

make lint
# exit 0; All checks passed!

make typecheck
# exit 0; 0 errors, 0 warnings, 0 informations
```

## Current git status

```text
$ git status --short --branch
exit=0
STDOUT:
## main...origin/main
 M docs/status/2026-06-16-project-graph-call-inheritance-treesitter.md
 M tests/test_project_status_docs.py
?? docs/status/INDEX.md
?? reports/2026-06-16-project-graph-gate-a-opus-review.json
?? reports/2026-06-16-project-graph-gate-b-design.md
?? reports/2026-06-16-project-graph-gate-b-opus-review.json
?? reports/2026-06-16-project-graph-gate-c-followup-opus-review.json
?? reports/2026-06-16-project-graph-gate-c-opus-review.json
?? reports/2026-06-17-doc-status-lifecycle-guard-implementation-report.md
?? reports/2026-06-17-doc-status-lifecycle-guard-opus-plan-prompt.md
?? reports/2026-06-17-doc-status-lifecycle-guard-opus-plan-retry.err
?? reports/2026-06-17-doc-status-lifecycle-guard-opus-plan-retry.json
?? reports/2026-06-17-doc-status-lifecycle-guard-opus-plan.err
?? reports/2026-06-17-doc-status-lifecycle-guard-opus-plan.json
?? reports/2026-06-17-doc-status-lifecycle-guard-opus-plan.md
?? reports/2026-06-17-doc-status-lifecycle-guard-opus-review-prompt.md
?? reports/2026-06-17-doc-status-lifecycle-guard-opus-review.err
?? reports/2026-06-17-doc-status-lifecycle-guard-opus-review.json
?? reports/2026-06-17-work-memory-gap-analysis-opus-retry-prompt.md
?? reports/2026-06-17-work-memory-gap-analysis-opus-retry-review.err
?? reports/2026-06-17-work-memory-gap-analysis-opus-retry-review.json
?? reports/2026-06-17-work-memory-gap-analysis-opus-review.err
?? reports/2026-06-17-work-memory-gap-analysis-opus-review.json
?? reports/2026-06-17-work-memory-gap-analysis-review-prompt.md
?? reports/2026-06-17-work-memory-gap-analysis.md

STDERR:

```

## Tracked-file diff

```diff
diff --git a/docs/status/2026-06-16-project-graph-call-inheritance-treesitter.md b/docs/status/2026-06-16-project-graph-call-inheritance-treesitter.md
index 458062a..5b4a146 100644
--- a/docs/status/2026-06-16-project-graph-call-inheritance-treesitter.md
+++ b/docs/status/2026-06-16-project-graph-call-inheritance-treesitter.md
@@ -1,6 +1,6 @@
 # Project graph call/inheritance + tree-sitter status — 2026-06-16

-Status: implemented locally on branch `graph/call-inheritance-treesitter`; not committed.
+Status: merged to `main` via PR #40 (merge commit 360e9a2); feature commit af48ead.

 Changed:
 - Added Python `inherits` and `calls` edges using the existing `ast` path.
diff --git a/tests/test_project_status_docs.py b/tests/test_project_status_docs.py
index 269db94..6907eab 100644
--- a/tests/test_project_status_docs.py
+++ b/tests/test_project_status_docs.py
@@ -3,9 +3,21 @@ from __future__ import annotations
 import json
 import re
 import subprocess
+from collections import Counter
 from pathlib import Path

 ROOT = Path(__file__).resolve().parents[1]
+STATUS_DIR = ROOT / "docs" / "status"
+STATUS_INDEX = STATUS_DIR / "INDEX.md"
+STATUS_SECTIONS = ("Active", "Superseded", "Historical")
+STATUS_ENTRY_RE = re.compile(
+    r"^-\s+`?(?P<doc>[^`\s]+\.md)`?(?:\s+→\s+`?(?P<successor>[^`\s]+\.md)`?)?",
+    re.MULTILINE,
+)
+STALE_ACTIVE_STATUS_RE = re.compile(
+    r"^Status:\s*(?=.*\b(?:not committed|implemented locally)\b).*$",
+    re.IGNORECASE | re.MULTILINE,
+)

 # Core modules that make up the implemented intake -> proposal pipeline. These
 # exist on disk today and MUST be discoverable from the orientation docs so a
@@ -28,6 +40,100 @@ def _read(relative: str) -> str:
     return (ROOT / relative).read_text(encoding="utf-8")


+def _status_docs() -> list[Path]:
+    return sorted(p for p in STATUS_DIR.glob("*.md") if p.name != STATUS_INDEX.name)
+
+
+def _status_index_sections() -> dict[str, list[tuple[str, str | None]]]:
+    assert STATUS_INDEX.exists(), "docs/status/INDEX.md must classify dated status docs"
+    sections: dict[str, list[tuple[str, str | None]]] = {section: [] for section in STATUS_SECTIONS}
+    current_section: str | None = None
+    for line in STATUS_INDEX.read_text(encoding="utf-8").splitlines():
+        if line.startswith("## "):
+            title = line.removeprefix("## ").strip()
+            current_section = title if title in sections else None
+            continue
+        if current_section is None or not line.startswith("- "):
+            continue
+        match = STATUS_ENTRY_RE.match(line)
+        assert match is not None, f"Malformed docs/status/INDEX.md entry: {line!r}"
+        sections[current_section].append((match.group("doc"), match.group("successor")))
+    return sections
+
+
+def _file_tracked_in_head(relative: str) -> bool:
+    result = subprocess.run(
+        ["git", "ls-tree", "-r", "--name-only", "HEAD", relative],
+        cwd=ROOT,
+        text=True,
+        capture_output=True,
+        check=True,
+    )
+    return bool(result.stdout.strip())
+
+
+def test_status_index_exists_and_classifies_every_status_doc() -> None:
+    sections = _status_index_sections()
+
+    indexed = [doc for entries in sections.values() for doc, _successor in entries]
+    counts = Counter(indexed)
+    duplicates = sorted(doc for doc, count in counts.items() if count > 1)
+    expected = sorted(path.name for path in _status_docs())
+
+    assert duplicates == []
+    assert sorted(indexed) == expected
+    assert sections["Active"], "At least one status doc should be marked active"
+
+    missing = [doc for doc in indexed if not (STATUS_DIR / doc).exists()]
+    assert missing == []
+
+
+def test_active_status_docs_do_not_claim_uncommitted_when_tracked_in_head() -> None:
+    sections = _status_index_sections()
+
+    stale_claims: list[str] = []
+    for doc, _successor in sections["Active"]:
+        relative = f"docs/status/{doc}"
+        if not _file_tracked_in_head(relative):
+            continue
+        match = STALE_ACTIVE_STATUS_RE.search(_read(relative))
+        if match is not None:
+            stale_claims.append(f"{relative}: {match.group(0)}")
+
+    assert stale_claims == []
+
+
+def test_active_status_stale_claim_regex_rejects_negated_merge_phrasing() -> None:
+    status_line = "Status: implemented locally; not yet merged; not committed."
+
+    assert STALE_ACTIVE_STATUS_RE.search(status_line) is not None
+
+
+def test_superseded_status_docs_point_to_existing_successor() -> None:
+    sections = _status_index_sections()
+
+    missing_successors: list[str] = []
+    for doc, successor in sections["Superseded"]:
+        if not successor:
+            missing_successors.append(f"{doc}: missing successor")
+            continue
+        if not (STATUS_DIR / successor).exists():
+            missing_successors.append(f"{doc}: successor {successor} does not exist")
+
+    assert missing_successors == []
+
+
+def test_project_graph_status_doc_reflects_merged_pr() -> None:
+    status = _read("docs/status/2026-06-16-project-graph-call-inheritance-treesitter.md")
+
+    status_line = next(line for line in status.splitlines() if line.startswith("Status:"))
+    assert "merged to `main`" in status_line
+    assert "PR #40" in status_line
+    assert "360e9a2" in status_line
+    assert "af48ead" in status_line
+    assert "not committed" not in status_line.lower()
+
+
 def test_readme_describes_ai_first_v1_and_bounded_live_status() -> None:
     readme = _read("README.md")

```

## New docs/status/INDEX.md

```markdown
# Status Doc Index

Status docs are dated, point-in-time records. This index is the source of truth for which docs describe current reality and which are retained as historical evidence.

Maintenance rule: when a status doc's feature or run state changes, either update the doc in place and keep it under Active, or move it to Superseded/Historical with a successor or reason. Active docs tracked in git must not claim `not committed` or `implemented locally` after they have landed in `main`. Do not move a doc to Historical just to hide a still-active stale claim; Historical is for point-in-time evidence, not current-state truth.

## Active

- `2026-06-16-project-graph-call-inheritance-treesitter.md` — project graph call/inheritance and JS/TS tree-sitter extraction; merged via PR #40 / 360e9a2.
- `2026-06-15-full-autonomy-gap-remediation-implementation-status.md` — current implementation status for the first full-autonomy gap-remediation slice.

## Superseded

- `2026-06-14-live-repo-goal-loop.md` → `2026-06-15-current-status-timeline-production-readiness.md` — pre-production-run readiness snapshot superseded by the June 15 production-readiness audit.
- `2026-06-14-progress-timeline-and-production-readiness-audit.md` → `2026-06-15-current-status-timeline-production-readiness.md` — pre-production-run audit superseded after the bounded fmc-mcp production-live attempt.

## Historical

- `2026-06-15-current-status-timeline-production-readiness.md` — point-in-time audit with captured dirty-state and run evidence; use current git/docs before treating its repository-state details as live.

```

## Guard behavior
- `docs/status/INDEX.md` must classify every dated `docs/status/*.md` exactly once.
- `Superseded` entries must point to an existing successor doc.
- Active status docs that are tracked in `HEAD` may not have a `Status:` line claiming `not committed` or `implemented locally`.
- A regression test proves negated/future merge phrasing such as `not yet merged` does not bypass the stale-claim regex.
- The known project-graph stale status is pinned directly: its Status line must mention `merged to main`, PR #40, merge commit `360e9a2`, and feature commit `af48ead`.
- Readiness register scope is unchanged; this is doc lifecycle hygiene, not broad-autonomy readiness tracking.
