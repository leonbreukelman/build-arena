from __future__ import annotations

import subprocess
from pathlib import Path

from arena.project_encyclopedia import write_encyclopedia
from arena.project_graph import build_project_graph


def _run(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=cwd, text=True, capture_output=True, check=True)


def _init_git_repo(root: Path) -> None:
    _run(["git", "init", "-b", "main"], root)
    _run(["git", "config", "user.email", "arena@example.invalid"], root)
    _run(["git", "config", "user.name", "Arena Tests"], root)
    _run(["git", "add", "."], root)
    _run(["git", "commit", "-m", "baseline"], root)


def test_encyclopedia_writes_manifest_and_source_linked_pages(tmp_path: Path) -> None:
    (tmp_path / "pkg").mkdir()
    (tmp_path / "docs").mkdir()
    (tmp_path / "pkg" / "core.py").write_text("def add(a: int, b: int) -> int:\n    return a + b\n", encoding="utf-8")
    (tmp_path / "docs" / "README.md").write_text("# Operator Guide\n", encoding="utf-8")
    (tmp_path / "pyproject.toml").write_text("[project]\nname='encyclopedia-project'\nversion='0.0.0'\n", encoding="utf-8")
    _init_git_repo(tmp_path)

    graph = build_project_graph(tmp_path)
    manifest = write_encyclopedia(graph, tmp_path / "encyclopedia")

    assert manifest.schema_version == "project-encyclopedia/v0.1"
    assert (tmp_path / "encyclopedia" / "manifest.json").exists()
    overview = (tmp_path / "encyclopedia" / "overview.md").read_text(encoding="utf-8")
    assert "# Project Encyclopedia" in overview
    assert "pkg/core.py" in overview
    assert "Provenance" in overview
    assert "source://" in overview


def test_encyclopedia_redacts_secret_shaped_content(tmp_path: Path) -> None:
    (tmp_path / "pkg").mkdir()
    fake_key = "API" + "_" + "KEY"
    fake_value = "sk-" + "liv" + "..." + "alue"
    (tmp_path / "pkg" / "core.py").write_text(f"{fake_key}='{fake_value}'\n", encoding="utf-8")
    (tmp_path / "README.md").write_text("# Secret Project\n", encoding="utf-8")
    _init_git_repo(tmp_path)

    graph = build_project_graph(tmp_path)
    write_encyclopedia(graph, tmp_path / "encyclopedia")
    overview = (tmp_path / "encyclopedia" / "overview.md").read_text(encoding="utf-8")

    assert fake_value not in overview
    assert "[REDACTED]" in overview
