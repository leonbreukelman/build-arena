from __future__ import annotations

from pathlib import Path

import pytest

from scorer.goal_config import GoalConfigError, load_goal_config


def _write_goal_config(repo: Path, content: str) -> Path:
    config_path = repo / ".arena" / "goal.toml"
    config_path.parent.mkdir(parents=True)
    config_path.write_text(content, encoding="utf-8")
    return config_path


def test_load_goal_config_normalizes_commands_paths_and_hash(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    config_path = _write_goal_config(
        repo,
        """
schema_version = "goal-config/v1"
project_id = "example"
goal = "Keep the example project healthy."

[commands]
test = ["uv", "run", "pytest", "tests", "-q"]
lint = ["uv", "run", "ruff", "check", "."]
typecheck = ["uv", "run", "pyright"]
coverage = ["uv", "run", "pytest", "tests", "--cov=example", "--cov-report=json:coverage.json", "-q"]
runtime_proxy = ["uv", "run", "python", "benchmarks/runtime_proxy.py"]

[coverage]
source = "coverage.json"
floor = 90.5

[paths]
source_roots = ["src", "lib"]
out_of_scope = [".venv", "dist"]
read_only = ["scorer", "schema/", ".arena/scorer.lock.toml"]

[diff_caps]
max_files = 7
max_lines = 250

[weights]
coverage_pct = 2.0
pyright_errors = -5.0
ruff_violations = -0.75
cyclomatic_avg = -2.0
runtime_p95_ms = -1.0
test_failure_penalty = -1000.0
""".strip()
        + "\n",
    )

    config = load_goal_config(repo)
    same_config = load_goal_config(repo)

    assert config.config_path == config_path
    assert config.schema_version == "goal-config/v1"
    assert config.project_id == "example"
    assert config.commands.test == ("uv", "run", "pytest", "tests", "-q")
    assert config.commands.lint == ("uv", "run", "ruff", "check", ".")
    assert config.commands.typecheck == ("uv", "run", "pyright")
    assert config.commands.coverage == (
        "uv",
        "run",
        "pytest",
        "tests",
        "--cov=example",
        "--cov-report=json:coverage.json",
        "-q",
    )
    assert config.commands.runtime_proxy == (
        "uv",
        "run",
        "python",
        "benchmarks/runtime_proxy.py",
    )
    assert config.coverage.source == "coverage.json"
    assert config.coverage.floor == 90.5
    assert config.paths.source_roots == ("src", "lib")
    assert config.paths.out_of_scope == (".venv", "dist")
    assert config.paths.read_only == ("scorer", "schema", ".arena/scorer.lock.toml")
    assert config.diff_caps.max_files == 7
    assert config.diff_caps.max_lines == 250
    assert config.weights.coverage_pct == 2.0
    assert len(config.content_hash) == 64
    assert config.content_hash == same_config.content_hash


def test_load_goal_config_rejects_missing_required_commands(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _write_goal_config(
        repo,
        """
schema_version = "goal-config/v1"
project_id = "broken"

[commands]
test = ["uv", "run", "pytest"]

[coverage]
source = "coverage.json"
""".strip()
        + "\n",
    )

    with pytest.raises(GoalConfigError, match="commands.lint"):
        load_goal_config(repo)


def test_goal_config_defaults_are_deterministic_and_documented(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _write_goal_config(
        repo,
        """
schema_version = "goal-config/v1"
project_id = "defaults"

[commands]
test = ["uv", "run", "pytest"]
lint = ["uv", "run", "ruff", "check", "."]
typecheck = ["uv", "run", "pyright"]

[coverage]
source = "coverage.json"
""".strip()
        + "\n",
    )

    config = load_goal_config(repo)

    assert config.commands.coverage is None
    assert config.commands.runtime_proxy is None
    assert config.coverage.floor == 85.0
    assert config.paths.source_roots == ("src",)
    assert config.paths.out_of_scope == ()
    assert config.paths.read_only == ()
    assert config.diff_caps.max_files == 8
    assert config.diff_caps.max_lines == 400
    assert config.weights.coverage_pct == 2.0
    assert config.weights.pyright_errors == -5.0
    assert config.weights.ruff_violations == -0.75
    assert config.weights.cyclomatic_avg == -2.0
    assert config.weights.runtime_p95_ms == -1.0
    assert config.weights.test_failure_penalty == -1000.0


def test_load_goal_config_rejects_empty_commands(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _write_goal_config(
        repo,
        """
schema_version = "goal-config/v1"
project_id = "unsafe"

[commands]
test = []
lint = ["uv", "run", "ruff", "check", "."]
typecheck = ["uv", "run", "pyright"]

[coverage]
source = "coverage.json"
""".strip()
        + "\n",
    )

    with pytest.raises(GoalConfigError, match="commands.test"):
        load_goal_config(repo)


@pytest.mark.parametrize("unsafe_path", ["../outside", "src/..", "."])
def test_load_goal_config_rejects_unsafe_paths(tmp_path: Path, unsafe_path: str) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _write_goal_config(
        repo,
        f"""
schema_version = "goal-config/v1"
project_id = "unsafe-paths"

[commands]
test = ["uv", "run", "pytest"]
lint = ["uv", "run", "ruff", "check", "."]
typecheck = ["uv", "run", "pyright"]

[coverage]
source = "coverage.json"

[paths]
read_only = ["{unsafe_path}"]
""".strip()
        + "\n",
    )

    with pytest.raises(GoalConfigError, match="paths.read_only"):
        load_goal_config(repo)


@pytest.mark.parametrize(
    ("field", "toml"),
    [
        ("coverage.floor", "[coverage]\nsource = \"coverage.json\"\nfloor = true"),
        ("diff_caps.max_files", "[coverage]\nsource = \"coverage.json\"\n\n[diff_caps]\nmax_files = true"),
    ],
)
def test_load_goal_config_rejects_bool_numeric_fields(
    tmp_path: Path,
    field: str,
    toml: str,
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _write_goal_config(
        repo,
        f"""
schema_version = "goal-config/v1"
project_id = "bool-numeric"

[commands]
test = ["uv", "run", "pytest"]
lint = ["uv", "run", "ruff", "check", "."]
typecheck = ["uv", "run", "pyright"]

{toml}
""".strip()
        + "\n",
    )

    with pytest.raises(GoalConfigError, match=field):
        load_goal_config(repo)


def test_load_goal_config_rejects_missing_config_file(tmp_path: Path) -> None:
    with pytest.raises(GoalConfigError, match=".arena/goal.toml"):
        load_goal_config(tmp_path)


def test_build_arena_goal_config_file_loads(project_root: Path) -> None:
    config = load_goal_config(project_root)

    assert config.project_id == "build-arena"
    assert config.paths.read_only[:4] == ("scorer", "verifier", "schema", "arena/generated")
    assert ".arena/scorer.lock.toml" in config.paths.read_only
    assert config.commands.test == ("uv", "run", "pytest", "tests", "-q")


def test_calibration_fixture_goal_config_file_loads(calibration_repo: Path) -> None:
    config = load_goal_config(calibration_repo)

    assert config.project_id == "arena-calibration-fixture"
    assert config.coverage.source == "coverage.json"
    assert config.paths.source_roots == ("src",)
    assert config.commands.runtime_proxy == ("uv", "run", "python", "benchmarks/runtime_proxy.py")
