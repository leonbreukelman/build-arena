"""Tests for Hermes semantic maintainer policy."""

from __future__ import annotations

from arena.maintainer.policy import evaluate_task_packet
from arena.maintainer.task_packet import TaskPacket


def _packet(**overrides: object) -> TaskPacket:
    data: dict[str, object] = {
        "objective": "Prepare a dry-run delegated coding task.",
        "mode": "dry_run",
        "allowed_paths": ["arena/maintainer", "tests/test_maintainer_policy.py"],
        "forbidden_paths": ["scorer", "verifier", "schema", "arena/generated"],
        "required_reads": ["AGENTS.md", "README.md"],
        "required_commands": ["uv run pytest tests -q", "uv run ruff check .", "uv run pyright"],
        "stop_conditions": ["stop on live execution request"],
    }
    data.update(overrides)
    return TaskPacket.model_validate(data)


def test_policy_allows_safe_dry_run_packet_and_reports_not_run_status() -> None:
    result = evaluate_task_packet(_packet())

    assert result.allowed is True
    assert result.reasons == ()
    assert result.execution == "not_run"
    assert result.runtime == "openshell_planned"
    assert result.verification_owner == "hermes"
    assert result.verification_status == "not_verified"


def test_policy_rejects_forbidden_path_write_overlap() -> None:
    result = evaluate_task_packet(_packet(allowed_paths=["arena/maintainer", "scorer/engine.py"]))

    assert result.allowed is False
    assert any("allowed write path overlaps forbidden path" in reason for reason in result.reasons)


def test_policy_rejects_target_apply_promote_phrase() -> None:
    result = evaluate_task_packet(_packet(objective="Use the worker to target apply/promote a patch."))

    assert result.allowed is False
    assert "target apply/promote is outside Build Arena propose-only scope" in result.reasons


def test_policy_rejects_git_push_phrase() -> None:
    result = evaluate_task_packet(_packet(required_commands=["git push origin main"]))

    assert result.allowed is False
    assert "git push is not allowed" in result.reasons


def test_policy_rejects_broad_autonomy_phrase() -> None:
    result = evaluate_task_packet(_packet(objective="Start broad live autonomy over this repo."))

    assert result.allowed is False
    assert "broad live autonomy is not allowed" in result.reasons


def test_policy_rejects_auto_merge_phrase() -> None:
    result = evaluate_task_packet(_packet(stop_conditions=["continue through auto-merge if tests pass"]))

    assert result.allowed is False
    assert "auto-merge is not allowed" in result.reasons
