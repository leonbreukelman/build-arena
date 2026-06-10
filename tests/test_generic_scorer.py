from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from arena.boundary import is_boundary_violation
from scorer.engine import Scorer
from scorer.goal_config import GoalConfigError, load_goal_config


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _init_repo(repo: Path) -> None:
    subprocess.run(["git", "init", "-b", "main"], cwd=repo, check=True, capture_output=True, text=True)
    subprocess.run(["git", "config", "user.email", "arena@example.invalid"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.name", "Arena Tests"], cwd=repo, check=True)
    subprocess.run(["git", "add", "."], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-m", "baseline"], cwd=repo, check=True, capture_output=True, text=True)


def _generic_repo(tmp_path: Path, *, coverage_pct: float = 93.5, coverage_floor: float = 90.0) -> Path:
    repo = tmp_path / "generic-repo"
    repo.mkdir()
    _write(
        repo / "lib" / "samplepkg" / "__init__.py",
        "from samplepkg.core import classify\n\n__all__ = ['classify']\n",
    )
    _write(
        repo / "lib" / "samplepkg" / "core.py",
        "def classify(value: int) -> str:\n    if value > 0:\n        return 'positive'\n    return 'other'\n",
    )
    _write(
        repo / "tools" / "test_command.py",
        "from samplepkg import classify\nassert classify(1) == 'positive'\n",
    )
    _write(
        repo / "tools" / "coverage_command.py",
        "import json\nfrom pathlib import Path\nPath('reports').mkdir(exist_ok=True)\nPath('reports/coverage.json').write_text(json.dumps({'totals': {'percent_covered': "
        + repr(coverage_pct)
        + "}}))\n",
    )
    _write(
        repo / "tools" / "lint_command.py",
        "import json\nprint(json.dumps([{'code': 'E501'}, {'code': 'F401'}]))\n",
    )
    _write(
        repo / "tools" / "typecheck_command.py",
        "import json\nprint(json.dumps({'generalDiagnostics': [{'severity': 'error'}, {'severity': 'warning'}]}))\n",
    )
    _write(
        repo / "tools" / "runtime_command.py",
        "import json\nprint(json.dumps({'runtime_p95_ms': 12.5}))\n",
    )
    _write(
        repo / ".arena" / "goal.toml",
        f"""
schema_version = "goal-config/v1"
project_id = "generic-fixture"
goal = "Exercise config-driven scoring."

[commands]
test = [{sys.executable!r}, "tools/test_command.py"]
lint = [{sys.executable!r}, "tools/lint_command.py"]
typecheck = [{sys.executable!r}, "tools/typecheck_command.py"]
coverage = [{sys.executable!r}, "tools/coverage_command.py"]
runtime_proxy = [{sys.executable!r}, "tools/runtime_command.py"]

[coverage]
source = "reports/coverage.json"
floor = {coverage_floor}

[paths]
source_roots = ["lib"]
out_of_scope = ["dist"]
read_only = ["private"]

[diff_caps]
max_files = 3
max_lines = 120

[weights]
coverage_pct = 1.0
pyright_errors = -10.0
ruff_violations = -2.0
cyclomatic_avg = -3.0
runtime_p95_ms = -4.0
test_failure_penalty = -500.0
""".strip()
        + "\n",
    )
    _init_repo(repo)
    return repo


def test_scorer_uses_goal_config_commands_source_roots_weights_and_provenance(
    project_root: Path,
    tmp_path: Path,
) -> None:
    repo = _generic_repo(tmp_path)

    record = Scorer(project_root).score_repo(repo)
    config = load_goal_config(repo)

    assert record.goal_config_sha == config.content_hash
    assert record.goal_config_schema_version == "goal-config/v1"
    assert config.content_hash[:12] in record.id
    assert record.vector.tests_pass is True
    assert record.vector.coverage_pct == 93.5
    assert record.vector.pyright_errors == 1
    assert record.vector.ruff_violations == 2
    assert record.vector.cyclomatic_avg == 2.0
    assert record.vector.runtime_p95_ms == 12.5
    assert record.vector.composite == 23.5


def test_scorer_marks_tests_failed_when_configured_coverage_floor_is_not_met(
    project_root: Path,
    tmp_path: Path,
) -> None:
    repo = _generic_repo(tmp_path, coverage_pct=42.0, coverage_floor=85.0)

    record = Scorer(project_root).score_repo(repo)

    assert record.vector.coverage_pct == 42.0
    assert record.vector.tests_pass is False
    assert record.vector.composite == -528.0


def test_scorer_uses_all_configured_source_roots_for_commands_and_complexity(
    project_root: Path,
    tmp_path: Path,
) -> None:
    repo = _generic_repo(tmp_path)
    _write(
        repo / "plugins" / "pluginpkg" / "__init__.py",
        "from pluginpkg.feature import enabled\n\n__all__ = ['enabled']\n",
    )
    _write(
        repo / "plugins" / "pluginpkg" / "feature.py",
        "def enabled(flag: bool) -> str:\n    if flag:\n        return 'enabled'\n    return 'disabled'\n",
    )
    _write(
        repo / "tools" / "test_command.py",
        "from samplepkg import classify\nfrom pluginpkg import enabled\nassert classify(1) == 'positive'\nassert enabled(True) == 'enabled'\n",
    )
    goal_path = repo / ".arena" / "goal.toml"
    goal_path.write_text(
        goal_path.read_text(encoding="utf-8").replace(
            'source_roots = ["lib"]',
            'source_roots = ["lib", "plugins"]',
        ),
        encoding="utf-8",
    )
    subprocess.run(["git", "add", "."], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-m", "add plugin root"], cwd=repo, check=True, capture_output=True, text=True)

    record = Scorer(project_root).score_repo(repo)

    assert record.vector.tests_pass is True
    assert record.vector.cyclomatic_avg == 2.0


def test_scorer_does_not_leave_runtime_artifacts_in_target_repo(
    project_root: Path,
    tmp_path: Path,
) -> None:
    repo = _generic_repo(tmp_path)

    Scorer(project_root).score_repo(repo)

    status = subprocess.check_output(["git", "status", "--short"], cwd=repo, text=True)
    assert status == ""


def test_scorer_fails_closed_when_goal_config_is_missing(project_root: Path, tmp_path: Path) -> None:
    repo = tmp_path / "missing-config"
    repo.mkdir()
    _write(repo / "src" / "pkg" / "__init__.py", "VALUE = 1\n")
    _init_repo(repo)

    with pytest.raises(GoalConfigError, match=".arena/goal.toml"):
        Scorer(project_root).score_repo(repo)


def test_boundary_accepts_goal_config_read_only_and_out_of_scope_paths(tmp_path: Path) -> None:
    repo = _generic_repo(tmp_path)
    config = load_goal_config(repo)

    assert is_boundary_violation(["private/secret.py"], goal_config=config)
    assert is_boundary_violation(["dist/generated.txt"], goal_config=config)
    assert not is_boundary_violation(["lib/samplepkg/core.py"], goal_config=config)
