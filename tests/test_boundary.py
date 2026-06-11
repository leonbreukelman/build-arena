from __future__ import annotations

from pathlib import Path

import pytest

from arena.boundary import is_boundary_violation
from scorer.goal_config import load_goal_config


def _write_goal_config(repo: Path, read_only: list[str]) -> None:
    config_path = repo / ".arena" / "goal.toml"
    config_path.parent.mkdir(parents=True)
    config_path.write_text(
        f"""
schema_version = "goal-config/v1"
project_id = "boundary-fixture"

[commands]
test = ["python3", "-c", "pass"]
lint = ["python3", "-c", "pass"]
typecheck = ["python3", "-c", "pass"]

[coverage]
source = "coverage.json"

[paths]
read_only = {read_only!r}
""".strip()
        + "\n",
        encoding="utf-8",
    )


def test_boundary_violation_rejects_scorer_target_before_runner_spawn() -> None:
    assert is_boundary_violation(["scorer/engine.py"])


def test_boundary_violation_rejects_schema_and_verifier_targets() -> None:
    assert is_boundary_violation(["schema/arena.yaml"])
    assert is_boundary_violation(["verifier/ablation.py"])


def test_boundary_rejects_scorer_lock_and_generated_artifacts() -> None:
    assert is_boundary_violation([".arena/scorer.lock.toml"])
    assert is_boundary_violation(["arena/generated/models.py"])
    assert is_boundary_violation(["dashboard/src/lib/generated/arena.d.ts"])


def test_boundary_allows_ordinary_arena_files() -> None:
    assert not is_boundary_violation(["arena/loop.py", "dashboard/src/App.svelte"])


def test_boundary_allows_similar_but_unprotected_names() -> None:
    assert not is_boundary_violation(["scorers/util.py", "schema_helper.py", "arena/generated_notes.md"])


def test_boundary_rejects_absolute_or_traversing_targets() -> None:
    with pytest.raises(ValueError):
        is_boundary_violation(["/tmp/scorer/engine.py"])
    with pytest.raises(ValueError):
        is_boundary_violation(["../scorer/engine.py"])


def test_boundary_uses_target_repo_goal_config_read_only_measurement_paths(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _write_goal_config(repo, ["benchmarks/runtime_proxy.py"])
    config = load_goal_config(repo)

    assert is_boundary_violation(["benchmarks/runtime_proxy.py"], goal_config=config)
    assert not is_boundary_violation(["benchmarks/notes.md"], goal_config=config)
