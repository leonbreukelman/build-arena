from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

from arena.proposal_candidate_runner import main


def _run(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=cwd, check=True, capture_output=True, text=True)


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    _write(repo / "README.md", "# Readme\n")
    _write(repo / "src" / "app.py", "def value() -> int:\n    return 1\n")
    _write(
        repo / ".arena" / "goal.toml",
        """
schema_version = "goal-config/v1"
project_id = "proposal-candidate-runner-fixture"

[commands]
test = ["python3", "-c", "pass"]
lint = ["python3", "-c", "pass"]
typecheck = ["python3", "-c", "pass"]

[coverage]
source = "coverage.json"
floor = 0.0

[paths]
source_roots = ["src"]
out_of_scope = []
read_only = []

[diff_caps]
max_files = 1
max_lines = 20
""".strip()
        + "\n",
    )
    _run(["git", "init", "-b", "main"], repo)
    _run(["git", "config", "user.email", "arena@example.invalid"], repo)
    _run(["git", "config", "user.name", "Arena Tests"], repo)
    _run(["git", "add", "."], repo)
    _run(["git", "commit", "-m", "baseline"], repo)
    return repo


def _proposal_plan(path: Path, repo: Path) -> Path:
    payload: dict[str, Any] = {
        "schemaVersion": "proposal-plan/v0",
        "id": "plan-test",
        "sourceScorecardId": "scorecard-test",
        "snapshotId": "snapshot-test",
        "projectRoot": str(repo),
        "repoFactsHash": "facts-hash",
        "candidateCount": 1,
        "omittedCount": 0,
        "candidates": [
            {
                "rank": 1,
                "finding_id": "doc.index.missing",
                "title": "Docs index is missing",
                "target_path": "docs/index.md",
                "intent": "Create a grounded docs index.",
                "success_criterion": "docs/index.md exists and all local Markdown links resolve.",
                "repo_facts_hash": "facts-hash",
                "repo_facts_block": "Repository facts:\n- README.md exists: yes\n- Existing docs markdown files: none",
                "grounding_constraints": ["Do not invent Markdown links."],
                "verification_commands": ["test -s docs/index.md", "python3 -m arena.markdown_links --repo . --path docs/index.md"],
                "priority_score": 728.0,
                "evidence_refs": [{"kind": "absence", "path": "docs/index.md", "checked": True}],
                "source_recommended_action": "Create docs/index.md as canonical docs navigation.",
            }
        ],
    }
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return path


def test_proposal_candidate_runner_applies_fake_diff_from_grounded_plan(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    plan = _proposal_plan(tmp_path / "proposal-plan.json", repo)
    output = tmp_path / "result.json"
    fake_diff = tmp_path / "fake.patch"
    fake_diff.write_text(
        """diff --git a/docs/index.md b/docs/index.md
new file mode 100644
--- /dev/null
+++ b/docs/index.md
@@ -0,0 +1,5 @@
+# Documentation Index
+
+See [README](../README.md).
+
+Future docs will be added as plain text.
""",
        encoding="utf-8",
    )

    rc = main([
        "--worktree",
        str(repo),
        "--proposal-plan",
        str(plan),
        "--candidate-rank",
        "1",
        "--fake-diff-file",
        str(fake_diff),
        "--output",
        str(output),
    ])

    assert rc == 0
    assert (repo / "docs" / "index.md").exists()
    result = json.loads(output.read_text(encoding="utf-8"))
    assert result["candidateRank"] == 1
    assert result["patchPath"].endswith(".patch")
    assert result["verification"]["commands"][0]["exitCode"] == 0
    assert result["verification"]["commands"][1]["exitCode"] == 0


def test_proposal_candidate_runner_rejects_dead_markdown_links_without_patch_artifact(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    plan = _proposal_plan(tmp_path / "proposal-plan.json", repo)
    fake_diff = tmp_path / "dead-link.patch"
    fake_diff.write_text(
        """diff --git a/docs/index.md b/docs/index.md
new file mode 100644
--- /dev/null
+++ b/docs/index.md
@@ -0,0 +1,3 @@
+# Documentation Index
+
+See [Overview](overview.md).
""",
        encoding="utf-8",
    )

    rc = main([
        "--worktree",
        str(repo),
        "--proposal-plan",
        str(plan),
        "--candidate-rank",
        "1",
        "--fake-diff-file",
        str(fake_diff),
    ])

    assert rc == 1
    assert not (repo / ".arena" / "patches").exists()


def test_proposal_candidate_runner_fails_closed_when_no_verification_commands_run(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    plan = _proposal_plan(tmp_path / "proposal-plan.json", repo)
    payload = json.loads(plan.read_text(encoding="utf-8"))
    payload["candidates"][0]["verification_commands"] = []
    plan.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    output = tmp_path / "result.json"
    fake_diff = tmp_path / "fake.patch"
    fake_diff.write_text(
        """diff --git a/docs/index.md b/docs/index.md
new file mode 100644
--- /dev/null
+++ b/docs/index.md
@@ -0,0 +1,3 @@
+# Documentation Index
+
+See [README](../README.md).
""",
        encoding="utf-8",
    )

    rc = main([
        "--worktree",
        str(repo),
        "--proposal-plan",
        str(plan),
        "--candidate-rank",
        "1",
        "--fake-diff-file",
        str(fake_diff),
        "--output",
        str(output),
    ])

    assert rc == 1
    result = json.loads(output.read_text(encoding="utf-8"))
    assert result["ok"] is False
    assert result["verification"]["ran"] is False


def test_proposal_candidate_runner_rejects_unverified_candidate_rank(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    plan = _proposal_plan(tmp_path / "proposal-plan.json", repo)

    rc = main([
        "--worktree",
        str(repo),
        "--proposal-plan",
        str(plan),
        "--candidate-rank",
        "2",
        "--fake-diff-file",
        str(tmp_path / "missing.patch"),
    ])

    assert rc == 2


# --- Phase 3 (#29): non-doc (code-quality) candidate end-to-end via the load-bearing gate ---


def _code_quality_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    _write(repo / "pyproject.toml", "[tool.ruff]\n")
    # A committed file with a real ruff violation (F401 unused import).
    _write(repo / "src" / "dirty.py", "import os\n\n\ndef f():\n    return 1\n")
    _write(
        repo / ".arena" / "goal.toml",
        """
schema_version = "goal-config/v1"
project_id = "code-quality-fixture"

[commands]
test = ["python3", "-c", "pass"]
lint = ["python3", "-c", "pass"]
typecheck = ["python3", "-c", "pass"]

[coverage]
source = "coverage.json"
floor = 0.0

[paths]
source_roots = ["src"]
out_of_scope = []
read_only = []

[diff_caps]
max_files = 1
max_lines = 20
""".strip()
        + "\n",
    )
    _run(["git", "init", "-b", "main"], repo)
    _run(["git", "config", "user.email", "arena@example.invalid"], repo)
    _run(["git", "config", "user.name", "Arena Tests"], repo)
    _run(["git", "add", "."], repo)
    _run(["git", "commit", "-m", "baseline"], repo)
    return repo


def _code_quality_plan(path: Path, repo: Path) -> Path:
    payload: dict[str, Any] = {
        "schemaVersion": "proposal-plan/v0",
        "id": "plan-cq",
        "sourceScorecardId": "scorecard-cq",
        "snapshotId": "snapshot-cq",
        "projectRoot": str(repo),
        "repoFactsHash": "facts-hash",
        "candidateCount": 1,
        "omittedCount": 0,
        "candidates": [
            {
                "rank": 1,
                "finding_id": "code.quality.lint.src/dirty.py",
                "title": "src/dirty.py has ruff lint violations",
                "target_path": "src/dirty.py",
                "intent": "Fix the ruff lint violations in src/dirty.py without suppressions.",
                "success_criterion": "src/dirty.py parses, has fewer ruff violations, adds no suppressions.",
                "repo_facts_hash": "facts-hash",
                "repo_facts_block": "Repository facts:\n- README.md exists: no",
                "grounding_constraints": ["Reduce real ruff violations; do not add `# noqa`."],
                "verification_commands": ["python3 -m arena.code_quality_gate --repo . --path src/dirty.py"],
                "priority_score": 120.0,
                "evidence_refs": [{"kind": "lint", "path": "src/dirty.py", "checked": True}],
                "source_recommended_action": "Reduce ruff violations in src/dirty.py.",
            }
        ],
    }
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return path


def test_code_quality_candidate_passes_gate_on_real_fix(tmp_path: Path) -> None:
    repo = _code_quality_repo(tmp_path)
    plan = _code_quality_plan(tmp_path / "plan.json", repo)
    output = tmp_path / "result.json"
    # Real fix: remove the unused import.
    fix = tmp_path / "fix.patch"
    fix.write_text(
        """diff --git a/src/dirty.py b/src/dirty.py
--- a/src/dirty.py
+++ b/src/dirty.py
@@ -1,5 +1,2 @@
-import os
-
-
 def f():
     return 1
""",
        encoding="utf-8",
    )

    rc = main(["--worktree", str(repo), "--proposal-plan", str(plan), "--candidate-rank", "1", "--fake-diff-file", str(fix), "--output", str(output)])

    assert rc == 0, output.read_text(encoding="utf-8")
    result = json.loads(output.read_text(encoding="utf-8"))
    assert result["ok"] is True
    assert result["targetPath"] == "src/dirty.py"
    assert not result["targetPath"].endswith(".md")  # this is the "not just docs" proof
    assert result["verification"]["commands"][0]["exitCode"] == 0


def test_code_quality_candidate_fails_gate_on_noop_change(tmp_path: Path) -> None:
    repo = _code_quality_repo(tmp_path)
    plan = _code_quality_plan(tmp_path / "plan.json", repo)
    output = tmp_path / "result.json"
    # No-op: add a comment, the F401 remains -> gate must reject.
    noop = tmp_path / "noop.patch"
    noop.write_text(
        """diff --git a/src/dirty.py b/src/dirty.py
--- a/src/dirty.py
+++ b/src/dirty.py
@@ -1,5 +1,5 @@
 import os
 
 
 def f():
-    return 1
+    return 1  # touched
""",
        encoding="utf-8",
    )

    rc = main(["--worktree", str(repo), "--proposal-plan", str(plan), "--candidate-rank", "1", "--fake-diff-file", str(noop), "--output", str(output)])

    assert rc == 1
    result = json.loads(output.read_text(encoding="utf-8"))
    assert result["ok"] is False
    assert result["verification"]["commands"][0]["exitCode"] != 0


def test_code_quality_candidate_fails_gate_on_suppression(tmp_path: Path) -> None:
    repo = _code_quality_repo(tmp_path)
    plan = _code_quality_plan(tmp_path / "plan.json", repo)
    output = tmp_path / "result.json"
    # Gaming: silence the warning with noqa instead of fixing it.
    gamed = tmp_path / "gamed.patch"
    gamed.write_text(
        """diff --git a/src/dirty.py b/src/dirty.py
--- a/src/dirty.py
+++ b/src/dirty.py
@@ -1,5 +1,5 @@
-import os
+import os  # noqa: F401
 
 
 def f():
     return 1
""",
        encoding="utf-8",
    )

    rc = main(["--worktree", str(repo), "--proposal-plan", str(plan), "--candidate-rank", "1", "--fake-diff-file", str(gamed), "--output", str(output)])

    assert rc == 1
    result = json.loads(output.read_text(encoding="utf-8"))
    assert result["ok"] is False
