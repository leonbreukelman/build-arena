# Plan: Guard Against Stale "Not Committed" Status Docs After Merge

## Problem statement

Dated status docs under `docs/status/` can assert a feature is "implemented locally / not committed" even after its branch merged to `main`. Concretely, `docs/status/2026-06-16-project-graph-call-inheritance-treesitter.md:3` says `not committed`, but the file exists in HEAD (from `af48ead`) and the branch merged via PR #40 (`360e9a2`). We need a repo-level pytest guard plus a lightweight convention that future agents can follow, without making the test brittle against legitimately historical wording.

## Core design idea: explicit lifecycle classification

The key to avoiding brittleness is **not** scanning all docs for forbidden phrases. Instead, classify each status doc into one of three lifecycle states via an explicit, machine-readable marker, and only enforce the invariant on `active` docs:

- **active** — describes present reality; "not committed" / "implemented locally" claims must be *true right now*.
- **superseded** — replaced by a later doc; the pointer to the successor must exist.
- **historical** — a point-in-time record (e.g. a June-5 report); past-tense pre-commit wording is allowed and never linted for current accuracy.

A single index file (`docs/status/INDEX.md`) is the source of truth for classification, so the test reads structured data rather than guessing from prose. This keeps the active/historical/superseded distinction explicit and self-documenting for future agents.

---

## 1. Minimal file changes

| File | Change |
|---|---|
| `tests/test_project_status_docs.py` | Add 3 new tests (RED first) + small helpers. No change to existing tests. |
| `docs/status/INDEX.md` | **New.** Current-status map classifying each dated doc as active/superseded/historical, with a short "how to maintain" preamble. |
| `docs/status/2026-06-16-project-graph-call-inheritance-treesitter.md` | Patch line 3 to reflect merged-to-`main` reality. |

No changes to `scorer/`, `verifier/`, `schema/`, `arena/generated/`, or `.arena/scorer.lock.toml` (AGENTS.md compliance). No new infrastructure, no new dependencies — reuses the existing `subprocess`/`json`/`re`/`Path` imports already in the test module.

---

## 2. Exact test behavior to add

Add to `tests/test_project_status_docs.py`. Reuse `ROOT` and `_read`. Add two small helpers:

```python
STATUS_DIR = ROOT / "docs" / "status"

def _status_docs() -> list[Path]:
    return sorted(p for p in STATUS_DIR.glob("*.md") if p.name != "INDEX.md")

def _file_tracked_in_head(relative: str) -> bool:
    result = subprocess.run(
        ["git", "ls-tree", "-r", "--name-only", "HEAD", relative],
        cwd=ROOT, capture_output=True, text=True,
    )
    return bool(result.stdout.strip())
```

### Test A — `test_status_index_exists_and_classifies_every_status_doc`
Asserts:
- `docs/status/INDEX.md` exists.
- Every file from `_status_docs()` is referenced in the index exactly once.
- Each is classified under exactly one of the three sections: `## Active`, `## Superseded`, `## Historical`.
- No index entry points to a nonexistent file (round-trip integrity).

This is the anti-rot guard: a future agent who adds a status doc but forgets to classify it gets a failing test.

### Test B — `test_active_status_docs_do_not_claim_uncommitted_when_tracked_in_head`
The central guard. For each doc listed under `## Active` in the index:
- If `_file_tracked_in_head(relative_path)` is `True`, the doc body must **not** contain an unqualified "not committed" / "implemented locally; not committed" claim.
- Use a narrow regex targeting the specific failure mode, e.g. case-insensitive match on `not committed` or `implemented locally` **on a `Status:` line** (anchor to the status line, not arbitrary prose, to avoid false positives in narrative text).

```python
STALE_CLAIM = re.compile(
    r"^status:.*(not committed|implemented locally(?!.*merged))",
    re.IGNORECASE | re.MULTILINE,
)
```

Because this only runs on `active` docs that are *actually tracked in HEAD*, it cannot misfire on a genuinely uncommitted work-in-progress doc, nor on historical/superseded records.

### Test C — `test_superseded_status_docs_point_to_successor`
For each doc under `## Superseded`, the index entry must name a successor doc that exists. Keeps the chain navigable and prevents "superseded" being used as a dumping ground to silence Test B.

> Optional 4th test (cheap, recommended): `test_project_graph_status_doc_reflects_merge` — specifically asserts the 2026-06-16 doc's Status line mentions `main` / merged and does *not* say `not committed`. This pins the known regression so it can't silently reappear.

---

## 3. Modeling current vs historical/superseded

`docs/status/INDEX.md` structure:

```markdown
# Status Doc Index

Status docs are dated, point-in-time records. This index is the source of
truth for which describe **current** reality versus which are kept for history.

When a status doc's feature merges, move its entry to "Superseded" (pointing to
the doc/PR that replaced it) or update it in place and keep it under "Active".
Tests in tests/test_project_status_docs.py enforce that **Active** docs tracked
in HEAD never claim "not committed".

## Active
- 2026-06-16-project-graph-call-inheritance-treesitter.md — project graph call/inheritance edges (merged via PR #40, 360e9a2)
- ...

## Superseded
- 2026-06-14-progress-timeline-and-production-readiness-audit.md → superseded by 2026-06-15-current-status-timeline-production-readiness.md

## Historical
- 2026-06-14-live-repo-goal-loop.md — point-in-time record; not linted for current accuracy
```

Classification is human-assigned but test-enforced for *completeness and integrity*, never auto-inferred from prose. This is the clean distinction the constraints asked for.

---

## 4. Patching the stale 2026-06-16 doc

Change line 3 from:

```
Status: implemented locally on branch `graph/call-inheritance-treesitter`; not committed.
```

to:

```
Status: merged to `main` via PR #40 (merge commit 360e9a2); feature commit af48ead.
```

Do **not** rewrite the rest of the doc's body. Then list it under `## Active` in the index.

---

## 5. Verification commands (TDD order)

```bash
# 1. RED — add tests first, before INDEX.md / doc patch. Confirm they fail.
python -m pytest tests/test_project_status_docs.py -k "status_index or active_status or superseded_status" -v

# 2. Create docs/status/INDEX.md and patch the 2026-06-16 doc.

# 3. GREEN — confirm new tests pass.
python -m pytest tests/test_project_status_docs.py -k "status_index or active_status or superseded_status" -v

# 4. No regressions in the existing doc-guard suite.
python -m pytest tests/test_project_status_docs.py -v

# 5. Spot-check the HEAD-tracking helper matches reality.
git ls-tree -r --name-only HEAD docs/status/2026-06-16-project-graph-call-inheritance-treesitter.md
```

Expect step 1 to fail (no INDEX.md / stale line present), step 3+4 to pass.

---

## 6. Risks / boundaries

- **Brittleness risk** — mitigated by (a) anchoring the regex to `Status:` lines, (b) gating Test B on `git ls-tree HEAD` so only tracked active docs are checked, (c) never linting historical/superseded docs. Past-tense narrative like the June-5 report stays valid.
- **HEAD vs branch nuance** — `git ls-tree HEAD` answers "is this file committed on the current branch's tip," which is the exact invariant. It correctly does *not* fail on a genuinely new uncommitted status doc (it won't be in HEAD, so it's skipped) — the guard targets the *contradiction* (in HEAD **and** claiming uncommitted), not mere presence of the phrase.
- **Index maintenance burden** — Test A forces every status doc to be classified, so the index can't silently rot. The preamble tells future agents the one-line rule.
- **`reports/` untracked noise** — out of scope; tests only glob `docs/status/*.md`, never `reports/`.
- **AGENTS.md protected paths** — untouched.
- **Readiness register scope** — unchanged; this guard is per-doc lifecycle hygiene, deliberately *not* per-feature merge tracking, consistent with the prior analysis conclusion.

---

## Acceptance criteria

1. New tests fail before the doc/index changes (RED verified) and pass after (GREEN).
2. `docs/status/INDEX.md` exists, classifies **every** `docs/status/*.md` exactly once across Active/Superseded/Historical, and has no dangling references.
3. No active doc that is tracked in HEAD claims "not committed" / "implemented locally."
4. The 2026-06-16 project-graph status doc's Status line reflects the merge to `main` (PR #40 / `360e9a2`) and is listed Active.
5. Every Superseded entry points to an existing successor doc.
6. The full existing `tests/test_project_status_docs.py` suite still passes; no protected paths touched.
7. The convention is documented in `INDEX.md` so a future agent can maintain it without re-deriving the design.