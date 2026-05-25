from __future__ import annotations

import pytest

from arena.boundary import is_boundary_violation


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
