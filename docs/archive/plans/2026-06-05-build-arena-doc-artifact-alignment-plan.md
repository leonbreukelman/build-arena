# Build Arena Documentation and Artifact Alignment Implementation Plan

> **For Hermes:** Use subagent-driven-development skill if executing this plan task-by-task. This document is a plan only; implementation is still required.

**Goal:** Align Build Arena’s durable project docs and verification artifacts with the actual code state at local HEAD `08a3e29`: Phase 4 foundation plus AI-first decomposer, Project Model v1 primary artifact, bounded direct xAI live adapter, and explicit broader-live-loop blockers.

**Architecture:** This is a documentation/artifact alignment slice with one lightweight regression test to prevent future drift. The implementation updates `README.md`, `AGENTS.md`, and the stale post-commit wording in the June 5 final report, while preserving historical reports that were accurate for their time. No scorer/verifier/schema/generated code changes are in scope.

**Tech Stack:** Markdown docs, pytest doc consistency tests, existing `uv`/ruff/pyright verification.

---

## Review status

Independent plan review was completed before finalizing this plan.

- Reviewer: Claude Code
- Requested model: Opus
- Review mode: read-only, no tools allowed
- Verdict: `ACCEPT_WITH_CHANGES`
- Raw review artifact: `docs/verification/2026-06-05-build-arena-doc-artifact-alignment-plan-opus-review.json`
- Markdown review artifact: `docs/verification/2026-06-05-build-arena-doc-artifact-alignment-plan-opus-review.md`

Required review changes incorporated:

1. Presence-only tests were strengthened with negative assertions for exact stale README/AGENTS/final-report strings.
2. The final-report edit now requires reading/capturing the actual stale sentence before replacement; no invented string matching.
3. The plan now verifies CLI flags with `--help` before documenting command examples.
4. Secret scanning now allows bare environment variable names and rejects only assignment-like secret leaks.
5. Tests now guard against stale identifiers such as `XAIProvider`, `runner_router.py`, `promoter.py`, and `failure_ledger.py` in active docs.
6. Tests now guard against broad-live-readiness overclaims.
7. Tests now verify that `AGENTS.md` preserves anti-fabrication, blocked-path, and worktree rules.
8. README readiness language is allowed to be human-facing prose; raw `not_ready_blockers_remain` remains required in `AGENTS.md` and/or linked readiness references.
9. Draft-marker scanning is narrowed to true uppercase draft markers to avoid blocking legitimate status prose.
10. Commit-message guidance is conditional on full local verification and, if run, implementation review evidence.

## Source evidence

Primary status report for this plan:

- `docs/verification/2026-06-05-build-arena-expected-vs-actual-status.md`

Current truth to preserve:

1. Phase 1-4 foundation is implemented and verified.
2. No dashboard control plane, rollback endpoint, or live subscription-CLI subprocess execution is implemented.
3. The deterministic Project Model v0 path remains for compatibility.
4. The AI-first decomposer now emits `project-model-v1.json` as the primary enriched artifact and also emits `project-model-v0.json` as compatibility output.
5. `LiveProjectModelLLM` provides a bounded direct xAI/OpenAI-compatible adapter behind the CLI `--allow-live` guard.
6. The pre-live readiness register remains `not_ready_blockers_remain`; broad autonomous live loops, worktree patch cycles, and promotion are not ready.
7. Elenchus Core and Arena Calibration remain v0-only follow-up repos for v1 adoption.
8. The two latest commits are local-only until pushed; do not imply remote availability.

## Non-goals

- Do not implement parser/indexer upgrades such as Tree-sitter, ast-grep, SCIP/LSIF, or CodeQL.
- Do not implement broader live loops, worktree patch cycles, promotion, dashboard control plane, rollback endpoint, or live subscription-CLI subprocess execution.
- Do not modify `scorer/`, `verifier/`, `schema/`, `.arena/scorer.lock.toml`, or `arena/generated/`.
- Do not rewrite historical verification artifacts whose “live Grok blocked” statement was accurate for commit `a26bc37`; only clarify current status where stale post-commit wording exists.
- Do not push, merge, deploy, or run paid/live provider calls during this docs alignment slice.

## Acceptance criteria

The slice is complete when:

1. `README.md` accurately states the current implementation status:
   - Phase 4 foundation complete.
   - AI-first decomposer exists.
   - Project Model v1 is the primary AI decomposer artifact.
   - v0 remains compatibility output.
   - Bounded live xAI adapter exists behind `--allow-live`.
   - Broader live loops remain blocked by the readiness register.
2. `README.md` includes valid CLI examples for both:
   - legacy deterministic/v0 decomposer path; and
   - AI-first snapshot path via `arena.project_model_cli snapshot`.
3. `AGENTS.md` current-status/context section reflects the post-Phase-4 reality without weakening existing anti-fabrication, boundary, or worktree rules.
4. The June 5 final report no longer says the slice is merely “ready to commit”; it records that it was committed locally as `08a3e29` and not pushed/merged/deployed.
5. A pytest doc-consistency test fails before the doc updates and passes after them.
6. Verification passes:
   - `uv run pytest tests/test_project_status_docs.py -q`
   - `uv run pytest tests -q`
   - `uv run ruff check .`
   - `uv run pyright`
   - `git diff --check`
   - marker scan for unresolved draft markers in changed docs
   - secret scan of added lines/changed docs
7. Final git status is understood and reported. If implementing from the fresh-session prompt, make one local commit after verification unless the implementer is explicitly told not to commit. Do not push.

## Task 0: Preflight and source read

**Objective:** Confirm repo, dirty state, actual CLI help, and actual stale strings before editing.

**Files:**

- Read: `README.md`
- Read: `AGENTS.md`
- Read: `docs/verification/2026-06-05-build-arena-expected-vs-actual-status.md`
- Read: `docs/verification/2026-06-05-grok-live-rca-project-model-v1-final-report.md`
- Read: `docs/verification/2026-06-05-pre-live-readiness-register.json`
- Read: `docs/specs/2026-06-05-project-model-v1-shared-contract-spec.md`
- Inspect help: `uv run python -m arena.decomposer --help`
- Inspect help: `uv run python -m arena.project_model_cli --help`
- Inspect help: `uv run python -m arena.project_model_cli snapshot --help`
- Inspect help: `uv run python -m arena.project_model_cli graph --help`
- Inspect help: `uv run python -m arena.project_model_cli gate --help`

**Step 1: Run repo preflight**

Run:

```bash
pwd
git rev-parse --show-toplevel
git status -sb
git branch --show-current
git remote -v
git log --oneline -5
```

Expected:

- Repo root is `/home/leonb/projects/build-arena`.
- Branch is `coverage-100` or another intentional implementation branch.
- If the tree is dirty, classify dirty files before editing and do not overwrite unrelated work.

**Step 2: Capture exact stale strings**

Record the current exact stale strings from the files before editing. As of the planning pass, the expected stale strings were:

```text
Current implementation status: Phase 4 loop glue, budget, divergence, event projection, and worktree promotion foundation is complete.
```

```text
## Current phase
```

```text
This slice is ready to commit as one coherent verified change. It does not push, merge, deploy, start a broader live loop, or enable worktree mutation/promotion.
```

If the actual file text differs, update the test target and replacement to the actual observed text instead of using the planning-pass strings blindly.

**Step 3: Verify CLI flags before documenting commands**

Run the help commands listed above and confirm the README examples use real flags. If a planned flag is missing, update the README example to the actual CLI rather than changing code in this docs slice.

**Step 4: Stop condition**

Stop and report instead of editing if:

- the repo path is not `/home/leonb/projects/build-arena`;
- there are unexpected dirty source changes that overlap target files;
- `HEAD` is no longer at or after `08a3e29` and the status report is no longer current;
- a documented command cannot be made valid from actual CLI help without changing implementation code.

## Task 1: Add documentation consistency tests first

**Objective:** Make stale docs fail before patching them, and ensure the tests catch both missing current-status markers and residual stale/overclaim text.

**Files:**

- Create: `tests/test_project_status_docs.py`

**Step 1: Write failing tests**

Add this test file, adjusting the exact stale strings only if Task 0 observed different exact current text:

```python
from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def test_readme_describes_ai_first_v1_and_bounded_live_status() -> None:
    readme = _read("README.md")

    required_markers = [
        "AI-first decomposer",
        "Project Model v1",
        "project-model-v1.json",
        "project-model-v0.json",
        "arena.project_model_cli",
        "--allow-live",
        "bounded read-only",
        "not ready for broad autonomous live loops",
    ]
    missing = [marker for marker in required_markers if marker not in readme]
    assert missing == []

    stale_strings = [
        "Current implementation status: Phase 4 loop glue, budget, divergence, event projection, and worktree promotion foundation is complete.",
    ]
    assert [text for text in stale_strings if text in readme] == []

    forbidden_overclaims = [
        "production ready",
        "fully autonomous live",
        "live autonomous loop ready",
        "ready for broad autonomous live loops",
    ]
    lowered = readme.lower()
    # Allow the explicit negative readiness statement while rejecting an
    # unqualified readiness claim. A naive substring check would treat
    # "not ready for broad autonomous live loops" as containing the
    # forbidden phrase "ready for broad autonomous live loops".
    lowered_for_overclaim_scan = lowered.replace(
        "not ready for broad autonomous live loops",
        "",
    )
    assert [phrase for phrase in forbidden_overclaims if phrase in lowered_for_overclaim_scan] == []


def test_agents_current_status_reflects_post_phase4_decomposer_and_readiness() -> None:
    agents = _read("AGENTS.md")

    required_markers = [
        "AI-first decomposer",
        "Project Model v1",
        "LiveProjectModelLLM",
        "pre-live readiness register",
        "not_ready_blockers_remain",
        "dashboard control plane",
        "rollback endpoint",
        "live subscription-CLI subprocess execution",
    ]
    missing = [marker for marker in required_markers if marker not in agents]
    assert missing == []

    assert "## Current phase" not in agents
    assert "## Current implementation status" in agents

    stale_identifiers = [
        "XAIProvider",
        "runner_router.py",
        "promoter.py",
        "failure_ledger.py",
    ]
    assert [identifier for identifier in stale_identifiers if identifier in agents] == []

    forbidden_overclaims = [
        "production ready",
        "fully autonomous live",
        "live autonomous loop ready",
        "ready for broad autonomous live loops",
    ]
    lowered = agents.lower()
    lowered_for_overclaim_scan = lowered.replace(
        "not ready for broad autonomous live loops",
        "",
    )
    assert [phrase for phrase in forbidden_overclaims if phrase in lowered_for_overclaim_scan] == []


def test_agents_preserves_safety_boundaries() -> None:
    agents = _read("AGENTS.md")

    required_safety_markers = [
        "NEVER reason from an imagined file",
        "NEVER guess at function/class/symbol existence",
        "NEVER modify anything under `scorer/`, `verifier/`, or `schema/`",
        "NEVER modify `.arena/scorer.lock.toml`",
        "NEVER hand-edit files under `arena/generated/`",
        "Runner writes are restricted to `.arena/worktrees/<cycle_id>/`",
        "Do not run `git checkout`, `git branch -f`, `git reset --hard`, `git rebase`, or `git push` inside a cycle worktree",
        "must use `git merge --ff-only`",
    ]
    missing = [marker for marker in required_safety_markers if marker not in agents]
    assert missing == []


def test_june5_final_report_records_committed_outcome_not_precommit_state() -> None:
    report = _read("docs/verification/2026-06-05-grok-live-rca-project-model-v1-final-report.md")

    stale = "This slice is ready to commit as one coherent verified change. It does not push, merge, deploy, start a broader live loop, or enable worktree mutation/promotion."
    assert stale not in report
    assert "08a3e29" in report
    assert "committed locally" in report


def test_documented_cli_surfaces_exist() -> None:
    checks = [
        (["uv", "run", "python", "-m", "arena.decomposer", "--help"], ["--project", "--output"]),
        (["uv", "run", "python", "-m", "arena.project_model_cli", "snapshot", "--help"], ["--project", "--artifacts-root", "--llm-mode", "--allow-live"]),
        (["uv", "run", "python", "-m", "arena.project_model_cli", "graph", "--help"], ["--project", "--output"]),
        (["uv", "run", "python", "-m", "arena.project_model_cli", "gate", "--help"], ["--snapshot"]),
    ]

    for command, expected_flags in checks:
        result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=True)
        help_text = result.stdout + result.stderr
        missing = [flag for flag in expected_flags if flag not in help_text]
        assert missing == []
```

**Step 2: Run tests and verify expected failure**

Run:

```bash
uv run pytest tests/test_project_status_docs.py -q
```

Expected before documentation updates:

- FAIL, with stale README/AGENTS/final-report findings and/or missing current-status markers.

## Task 2: Update `README.md`

**Objective:** Make README accurately describe the current implementation and provide verified command examples.

**Files:**

- Modify: `README.md`

**Step 1: Replace stale top-level current status**

Replace the Phase 4-only sentence with a concise current status block. Required meaning:

- Phase 4 loop foundation is complete.
- Post-Phase-4 AI-first decomposer is implemented.
- Project Model v1 is the primary AI decomposer artifact.
- v0 remains compatibility output.
- Bounded live xAI adapter exists behind `--allow-live`.
- Build Arena is not ready for broad autonomous live loops; broader live work remains blocked by the pre-live readiness register.

Do not require raw enum text in README if prose is clearer, but include a link/path to:

- `docs/verification/2026-06-05-pre-live-readiness-register.json`

**Step 2: Preserve implemented acceptance gates**

Keep the existing Phase 1-4 acceptance gate list, but add a “Post-Phase-4 decomposer status” subsection after it, including:

- graph/wiki/snapshot/gate sidecars
- `project-model-v1.json` primary artifact
- `project-model-v0.json` compatibility projection
- direct xAI adapter fail-closed boundaries
- related-repo v1 adoption still open

**Step 3: Update “Project decomposition”**

Keep the legacy deterministic decomposer example if actual `arena.decomposer --help` still supports it.

Keep the explicit v0 example only if actual help supports the flags. If help output cannot prove all v0 flags, either simplify the example to a verified command or quote the existing documented v0 flow with a clear note that it is the legacy compatibility CLI.

Add the AI-first snapshot example using flags confirmed by `snapshot --help`:

```bash
uv run python -m arena.project_model_cli snapshot \
  --project /path/to/project \
  --artifacts-root /tmp/build-arena-snapshot \
  --project-id example-project \
  --goal "Decompose the project from git/filesystem truth" \
  --llm-mode fixture
```

Add the live guarded form without encouraging routine spend:

```bash
uv run python -m arena.project_model_cli snapshot \
  --project /path/to/project \
  --artifacts-root /tmp/build-arena-live-snapshot \
  --project-id example-project \
  --goal "Read-only live decomposition smoke" \
  --llm-mode live \
  --allow-live
```

State that live mode is only for bounded read-only smoke under the readiness ladder and must not be used for broad autonomous loops until blockers are closed.

It is acceptable to mention the bare environment variable name `XAI_API_KEY`; do not include a value, example token, or assignment.

**Step 4: Mention graph/gate subcommands**

Add short examples using flags confirmed by help:

```bash
uv run python -m arena.project_model_cli graph --project /path/to/project --output /tmp/project-graph.json
uv run python -m arena.project_model_cli gate --snapshot /tmp/build-arena-snapshot/<snapshot-id>/manifest.json
```

## Task 3: Update `AGENTS.md`

**Objective:** Align active future-agent context with the actual code state while preserving safety rules.

**Files:**

- Modify: `AGENTS.md`

**Step 1: Keep anti-fabrication and boundary rules unchanged**

Do not weaken or delete:

- read-before-quote/edit rules
- blocked paths: `scorer/`, `verifier/`, `schema/`, `.arena/scorer.lock.toml`, `arena/generated/`
- git worktree rules

**Step 2: Replace “Current phase” with “Current implementation status”**

The updated section should include:

- Phase 4 foundation complete and verified.
- AI-first decomposer implemented after Phase 4.
- `project-model-v1.json` is primary for AI decomposer snapshots.
- `project-model-v0.json` remains compatibility output.
- `LiveProjectModelLLM` provides direct xAI/OpenAI-compatible bounded live path behind `--allow-live`.
- `docs/verification/2026-06-05-pre-live-readiness-register.json` remains `not_ready_blockers_remain`.
- Broad live loops, dry-run hypothesis generation from v1, worktree patch cycles, and promotion remain blocked until the readiness register blockers are closed.
- Dashboard control plane, rollback endpoint, and live subscription-CLI subprocess execution remain unimplemented.

Do not say the project is production ready or ready for broad live autonomous loops.

**Step 3: Add decomposer commands to commands section**

Add concise command bullets:

```text
- `uv run python -m arena.project_model_cli snapshot ...` — build AI-first snapshot artifacts.
- `uv run python -m arena.project_model_cli gate --snapshot <manifest.json>` — rerun deterministic gate.
- `uv run python -m arena.project_model_cli graph --project <repo> --output <graph.json>` — emit graph sidecar.
```

Do not include credentials or live provider setup values in `AGENTS.md`.

## Task 4: Patch June 5 final report stale commit wording

**Objective:** Make the artifact’s status match the current local commit state.

**Files:**

- Modify: `docs/verification/2026-06-05-grok-live-rca-project-model-v1-final-report.md`

**Step 1: Replace the actual observed stale wording**

Find the exact stale post-commit sentence captured in Task 0. As of the planning pass, it was:

```text
This slice is ready to commit as one coherent verified change. It does not push, merge, deploy, start a broader live loop, or enable worktree mutation/promotion.
```

Replace it with:

```text
This slice was committed locally as `08a3e29 [verified] add live xai decomposer and project model v1 readiness`. It was not pushed, merged, deployed, used to start a broader live loop, or used to enable worktree mutation/promotion.
```

If Task 0 finds different exact wording, patch that observed wording while preserving the same meaning.

**Step 2: Do not rewrite historical RCA sections**

Do not remove historical statements that were true during the RCA. The only intended report patch is the stale post-commit readiness wording unless the doc-consistency test proves another exact stale marker remains.

## Task 5: Run targeted tests and patch docs until green

**Objective:** Verify the doc-alignment tests now pass.

Run:

```bash
uv run pytest tests/test_project_status_docs.py -q
```

Expected:

- PASS.

If missing markers fail, patch the relevant docs rather than weakening the tests, unless the marker is genuinely wrong or overly brittle. If a marker is wrong, replace it with a better durable marker and document why in the final response.

## Task 6: Full verification and hygiene scans

**Objective:** Ensure docs/test changes do not break the project and do not leak secrets or stale markers.

Run:

```bash
uv run pytest tests -q
uv run ruff check .
uv run pyright
git diff --check
```

Run a secret scan over changed files / added lines. Suggested command:

```bash
python3 - <<'PY'
import re
import subprocess

assignment_patterns = [
    re.compile(r'(?i)(api[_-]?key|token|secret|password)\s*[:=]\s*([^\s`"\']+)'),
]
allowed_bare_names = {'XAI_API_KEY'}
changed = [
    'README.md',
    'AGENTS.md',
    'docs/verification/2026-06-05-grok-live-rca-project-model-v1-final-report.md',
    'tests/test_project_status_docs.py',
]
diff = subprocess.check_output(['git', 'diff', '--', *changed], text=True)
hits = []
for line in diff.splitlines():
    if not line.startswith('+') or line.startswith('+++'):
        continue
    for pattern in assignment_patterns:
        match = pattern.search(line)
        if not match:
            continue
        value = match.group(2)
        if value in allowed_bare_names:
            continue
        hits.append(line)
if hits:
    print('\n'.join(hits))
    raise SystemExit(1)
print('secret_scan_hits=0')
PY
```

Run a marker scan for unresolved draft markers in changed docs. Suggested command:

```bash
python3 - <<'PY'
from pathlib import Path
paths = [
    Path('README.md'),
    Path('AGENTS.md'),
    Path('docs/verification/2026-06-05-grok-live-rca-project-model-v1-final-report.md'),
]
markers = ['TODO', 'FIXME', 'XXX']
hits = []
for path in paths:
    text = path.read_text(encoding='utf-8')
    for marker in markers:
        if marker in text:
            hits.append(f'{path}: contains {marker}')
if hits:
    print('\n'.join(hits))
    raise SystemExit(1)
print('draft_marker_hits=0')
PY
```

Expected:

- All commands pass.
- No secret hits.
- No unresolved draft markers.

## Task 7: Optional independent implementation review before commit

**Objective:** Catch stale-doc or overclaim regressions before landing.

If `claude` with Opus is available, run a read-only review over the diff:

```bash
git diff -- README.md AGENTS.md docs/verification/2026-06-05-grok-live-rca-project-model-v1-final-report.md tests/test_project_status_docs.py > /tmp/build-arena-doc-alignment.diff
claude -p --model opus --output-format json --allowedTools '' < /tmp/build-arena-doc-alignment-review-prompt.md > /tmp/build-arena-doc-alignment-review.json
```

The review prompt should ask whether:

- README and AGENTS reflect actual current status without overclaiming live readiness.
- Historical RCA artifacts are preserved appropriately.
- The new tests are durable rather than brittle.
- No instructions weaken anti-fabrication/boundary rules.
- Documented CLI examples match actual `--help` output.

If Opus is unavailable, label the review as skipped and rely on local verification; do not invent an Opus verdict. If the commit message uses a `[verified]` prefix, the final response must state exactly which verification and review evidence justified it.

## Task 8: Commit boundary

**Objective:** Leave the implementation in a clean, auditable state.

If the fresh implementation session was launched with commit authorization, stage only the intended files:

```bash
git add README.md AGENTS.md \
  docs/verification/2026-06-05-grok-live-rca-project-model-v1-final-report.md \
  tests/test_project_status_docs.py
```

Then run:

```bash
git diff --cached --check
git status --short
git commit -m "[verified] align build-arena status docs"
```

Use the `[verified]` prefix only if full local verification passed and any requested/available independent implementation review did not identify unresolved blockers. Otherwise use a plain docs commit message or leave uncommitted, and report why.

Do not push unless explicitly authorized in that implementation session.

If commit is not authorized, leave files uncommitted and report that implementation is verified but not committed.

## Final response requirements for the implementation session

Start with one of:

- `Aligned and verified.`
- `Aligned locally but not committed.`
- `Blocked.`

Then include:

- exact files changed
- whether a local commit was made
- whether push/merge/deploy/live-provider calls were not performed
- verification commands and results
- any Opus review verdict or explicitly say Opus was unavailable/skipped
- final git status
