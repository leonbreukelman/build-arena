from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from arena.patch_gate import validate_unified_diff
from scorer.goal_config import load_goal_config


def _run(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=cwd, check=True, capture_output=True, text=True)


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _repo(tmp_path: Path, *, max_files: int = 2, max_lines: int = 6) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    _write(repo / "src" / "app.py", "def value() -> int:\n    return 1\n")
    _write(repo / "private" / "secret.py", "SECRET = 'x'\n")
    _write(
        repo / ".arena" / "goal.toml",
        f"""
schema_version = "goal-config/v1"
project_id = "patch-gate-fixture"

[commands]
test = ["python3", "-c", "pass"]
lint = ["python3", "-c", "pass"]
typecheck = ["python3", "-c", "pass"]

[coverage]
source = "coverage.json"
floor = 0.0

[paths]
source_roots = ["src", "private"]
out_of_scope = ["generated"]
read_only = ["private"]

[diff_caps]
max_files = {max_files}
max_lines = {max_lines}
""".strip()
        + "\n",
    )
    _run(["git", "init", "-b", "main"], repo)
    _run(["git", "config", "user.email", "arena@example.invalid"], repo)
    _run(["git", "config", "user.name", "Arena Tests"], repo)
    _run(["git", "add", "."], repo)
    _run(["git", "commit", "-m", "baseline"], repo)
    return repo


def _valid_diff(path: str = "src/app.py", *, new_value: int = 2) -> str:
    return f"""diff --git a/{path} b/{path}
--- a/{path}
+++ b/{path}
@@ -1,2 +1,2 @@
 def value() -> int:
-    return 1
+    return {new_value}
"""


def test_patch_gate_accepts_valid_diff_without_mutating_worktree(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    config = load_goal_config(repo)

    result = validate_unified_diff(repo, _valid_diff(), goal_config=config)

    assert result.accepted is True
    assert result.reason is None
    assert result.touched_paths == ("src/app.py",)
    assert result.added_lines == 1
    assert result.deleted_lines == 1
    assert result.to_jsonable()["accepted"] is True
    assert (repo / "src" / "app.py").read_text(encoding="utf-8") == "def value() -> int:\n    return 1\n"
    assert subprocess.check_output(["git", "status", "--short"], cwd=repo, text=True) == ""


@pytest.mark.parametrize(
    ("diff_text", "reason"),
    [
        ("", "empty_diff"),
        ("Please change src/app.py to return 2.", "malformed_diff"),
        ("diff --git a/src/app.py b/src/app.py\nGIT binary patch\nliteral 0\n", "binary_diff"),
        (_valid_diff("private/secret.py"), "boundary_violation"),
    ],
)
def test_patch_gate_rejects_invalid_outputs_without_mutation(tmp_path: Path, diff_text: str, reason: str) -> None:
    repo = _repo(tmp_path)
    before = (repo / "src" / "app.py").read_text(encoding="utf-8")

    result = validate_unified_diff(repo, diff_text, goal_config=load_goal_config(repo))

    assert result.accepted is False
    assert result.reason == reason
    assert (repo / "src" / "app.py").read_text(encoding="utf-8") == before
    assert subprocess.check_output(["git", "status", "--short"], cwd=repo, text=True) == ""


def test_patch_gate_rejects_diff_caps_without_mutation(tmp_path: Path) -> None:
    repo = _repo(tmp_path, max_files=1, max_lines=1)

    result = validate_unified_diff(repo, _valid_diff(), goal_config=load_goal_config(repo))

    assert result.accepted is False
    assert result.reason == "diff_caps_exceeded"
    assert result.added_lines == 1
    assert result.deleted_lines == 1
    assert subprocess.check_output(["git", "status", "--short"], cwd=repo, text=True) == ""
