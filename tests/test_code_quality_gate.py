from __future__ import annotations

import subprocess
from pathlib import Path

from arena.code_quality_gate import evaluate_code_quality_gate, main


def _git(repo: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True, text=True)


def _init_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    (repo / "src").mkdir(parents=True)
    _git_init(repo)
    return repo


def _git_init(repo: Path) -> None:
    _git(repo, "init", "-q")
    _git(repo, "config", "user.email", "t@example.com")
    _git(repo, "config", "user.name", "Test")
    # Provide a ruff config so before/after are measured against a stable ruleset.
    (repo / "pyproject.toml").write_text("[tool.ruff]\n", encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "init")


def _commit_file(repo: Path, rel: str, content: str) -> None:
    path = repo / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", f"add {rel}")


def test_gate_accepts_real_fix_that_removes_violation(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    _commit_file(repo, "src/mod.py", "import os\n\n\ndef f():\n    return 1\n")  # F401 unused import

    # Real fix: remove the unused import (working tree, uncommitted).
    (repo / "src" / "mod.py").write_text("def f():\n    return 1\n", encoding="utf-8")

    result = evaluate_code_quality_gate(repo, "src/mod.py")

    assert result.ok is True
    assert result.violations_after < result.violations_before
    assert result.reason == "improved"


def test_gate_rejects_noop_change(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    _commit_file(repo, "src/mod.py", "import os\n\n\ndef f():\n    return 1\n")

    # No-op: only a harmless trailing comment, the F401 remains and no real
    # suppression marker is added.
    (repo / "src" / "mod.py").write_text("import os\n\n\ndef f():\n    return 1  # trailing note\n", encoding="utf-8")

    result = evaluate_code_quality_gate(repo, "src/mod.py")

    assert result.ok is False
    assert result.reason == "no_improvement"


def test_gate_rejects_suppression_gaming(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    _commit_file(repo, "src/mod.py", "import os\n\n\ndef f():\n    return 1\n")

    # Gaming: silence the violation with a suppression instead of fixing it.
    (repo / "src" / "mod.py").write_text("import os  # noqa: F401\n\n\ndef f():\n    return 1\n", encoding="utf-8")

    result = evaluate_code_quality_gate(repo, "src/mod.py")

    assert result.ok is False
    assert result.reason == "suppression_gaming"
    assert result.suppressions_after > result.suppressions_before


def test_gate_rejects_type_ignore_gaming(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    _commit_file(repo, "src/mod.py", "import os\n\n\ndef f():\n    return 1\n")

    (repo / "src" / "mod.py").write_text("import os  # type: ignore\n\n\ndef f():\n    return 1\n", encoding="utf-8")

    result = evaluate_code_quality_gate(repo, "src/mod.py")

    # noqa absent but type:ignore added; F401 still present so it also fails no_improvement,
    # but suppression gaming must take precedence as the more informative reason.
    assert result.ok is False
    assert result.suppressions_after > result.suppressions_before


def test_gate_rejects_file_level_ruff_noqa(tmp_path: Path) -> None:
    """The strongest suppression: a file-level `# ruff: noqa` silences ALL rules.
    It must be detected as gaming, not read as a real improvement."""
    repo = _init_repo(tmp_path)
    _commit_file(repo, "src/mod.py", "import os\n\n\ndef f():\n    return 1\n")

    (repo / "src" / "mod.py").write_text("# ruff: noqa\nimport os\n\n\ndef f():\n    return 1\n", encoding="utf-8")

    result = evaluate_code_quality_gate(repo, "src/mod.py")

    assert result.ok is False
    assert result.reason == "suppression_gaming"
    assert result.suppressions_after > result.suppressions_before


def test_gate_rejects_file_level_ruff_noqa_with_codes(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    _commit_file(repo, "src/mod.py", "import os\n\n\ndef f():\n    return 1\n")

    (repo / "src" / "mod.py").write_text("# ruff: noqa: F401\nimport os\n\n\ndef f():\n    return 1\n", encoding="utf-8")

    result = evaluate_code_quality_gate(repo, "src/mod.py")

    assert result.ok is False
    assert result.reason == "suppression_gaming"


def test_gate_rejects_flake8_file_level_noqa(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    _commit_file(repo, "src/mod.py", "import os\n\n\ndef f():\n    return 1\n")

    (repo / "src" / "mod.py").write_text("# flake8: noqa\nimport os\n\n\ndef f():\n    return 1\n", encoding="utf-8")

    result = evaluate_code_quality_gate(repo, "src/mod.py")

    assert result.ok is False
    assert result.reason == "suppression_gaming"


def test_gate_does_not_count_noqa_inside_string_literal(tmp_path: Path) -> None:
    """A legitimate fix that adds a STRING containing '# noqa' (e.g. an error
    message about linting) must not be falsely flagged as suppression gaming."""
    repo = _init_repo(tmp_path)
    _commit_file(repo, "src/mod.py", "import os\n\n\ndef f():\n    return 1\n")

    # Real fix (remove unused import) plus a string that merely mentions noqa.
    (repo / "src" / "mod.py").write_text('MSG = "do not use # noqa here"\n\n\ndef f():\n    return 1\n', encoding="utf-8")

    result = evaluate_code_quality_gate(repo, "src/mod.py")

    assert result.ok is True
    assert result.reason == "improved"


def test_gate_rejects_change_that_breaks_python_syntax(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    _commit_file(repo, "src/mod.py", "import os\n\n\ndef f():\n    return 1\n")

    # Reduces violations to zero by destroying the file, but it no longer parses.
    (repo / "src" / "mod.py").write_text("def f(:\n", encoding="utf-8")

    result = evaluate_code_quality_gate(repo, "src/mod.py")

    assert result.ok is False
    assert result.reason == "invalid_python"


def test_gate_rejects_deletion_of_public_symbol(tmp_path: Path) -> None:
    """Dropping the violation count by deleting real code (a function/class that
    happened to carry a warning) must be rejected: the public symbol set must not
    shrink. This stops "delete code to pass" gaming the lint-delta."""
    repo = _init_repo(tmp_path)
    _commit_file(repo, "src/mod.py", "import os\n\n\ndef compute(x):\n    return os.getpid() + x\n")

    # 'Fix' the unused-import-style warning by deleting the function that uses os.
    (repo / "src" / "mod.py").write_text("x = 1\n", encoding="utf-8")

    result = evaluate_code_quality_gate(repo, "src/mod.py")

    assert result.ok is False
    assert result.reason == "public_symbols_removed"


def test_gate_allows_keeping_all_public_symbols(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    _commit_file(repo, "src/mod.py", "import os\n\n\ndef compute(x):\n    return x + 1\n")  # F401 unused os

    # Real fix: remove only the unused import, keep compute().
    (repo / "src" / "mod.py").write_text("def compute(x):\n    return x + 1\n", encoding="utf-8")

    result = evaluate_code_quality_gate(repo, "src/mod.py")

    assert result.ok is True
    assert result.reason == "improved"


def test_gate_fails_closed_when_no_baseline_in_git(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    # New, never-committed file: no HEAD baseline to measure improvement against.
    (repo / "src" / "new.py").write_text("def g():\n    return 2\n", encoding="utf-8")

    result = evaluate_code_quality_gate(repo, "src/new.py")

    assert result.ok is False
    assert result.reason == "no_baseline"


def test_gate_fails_closed_when_working_file_missing(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    _commit_file(repo, "src/mod.py", "import os\n\n\ndef f():\n    return 1\n")
    (repo / "src" / "mod.py").unlink()

    result = evaluate_code_quality_gate(repo, "src/mod.py")

    assert result.ok is False
    assert result.reason == "missing_file"


def test_gate_is_deterministic(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    _commit_file(repo, "src/mod.py", "import os\n\n\ndef f():\n    return 1\n")
    (repo / "src" / "mod.py").write_text("def f():\n    return 1\n", encoding="utf-8")

    first = evaluate_code_quality_gate(repo, "src/mod.py")
    second = evaluate_code_quality_gate(repo, "src/mod.py")

    assert first == second


def test_gate_cli_returns_zero_on_real_fix_and_one_on_noop(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    _commit_file(repo, "src/mod.py", "import os\n\n\ndef f():\n    return 1\n")

    (repo / "src" / "mod.py").write_text("def f():\n    return 1\n", encoding="utf-8")
    assert main(["--repo", str(repo), "--path", "src/mod.py"]) == 0

    (repo / "src" / "mod.py").write_text("import os\n\n\ndef f():\n    return 1\n", encoding="utf-8")
    assert main(["--repo", str(repo), "--path", "src/mod.py"]) == 1
