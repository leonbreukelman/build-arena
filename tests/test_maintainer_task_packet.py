"""Tests for dry-run maintainer task packets."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from arena.maintainer.task_packet import TaskPacket, render_task_markdown


def packet_kwargs() -> dict[str, object]:
    return {
        "objective": "Prepare a dry-run maintainer delegation task.",
        "mode": "dry_run",
        "allowed_paths": ["arena/maintainer", "tests/test_maintainer_task_packet.py"],
        "forbidden_paths": ["scorer", "verifier", "schema", "arena/generated"],
        "required_reads": ["AGENTS.md", "README.md"],
        "required_commands": ["uv run pytest tests -q", "uv run ruff check .", "uv run pyright"],
        "stop_conditions": ["any request to push, merge, apply, or promote"],
    }


def test_task_packet_accepts_allowed_dry_run_task() -> None:
    packet = TaskPacket.model_validate(packet_kwargs())

    assert packet.mode == "dry_run"
    assert packet.objective.startswith("Prepare")
    assert packet.allowed_paths == ("arena/maintainer", "tests/test_maintainer_task_packet.py")


def test_task_packet_rejects_blank_objective() -> None:
    data = packet_kwargs()
    data["objective"] = "  "

    with pytest.raises(ValidationError):
        TaskPacket.model_validate(data)


def test_task_packet_rejects_non_dry_run_mode() -> None:
    data = packet_kwargs()
    data["mode"] = "live"

    with pytest.raises(ValidationError):
        TaskPacket.model_validate(data)


def test_task_packet_rejects_absolute_or_parent_paths() -> None:
    absolute = packet_kwargs()
    absolute["allowed_paths"] = ["/tmp/outside"]
    with pytest.raises(ValidationError):
        TaskPacket.model_validate(absolute)

    parent = packet_kwargs()
    parent["required_reads"] = ["../AGENTS.md"]
    with pytest.raises(ValidationError):
        TaskPacket.model_validate(parent)


def test_render_task_markdown_contains_worker_boundaries() -> None:
    text = render_task_markdown(TaskPacket.model_validate(packet_kwargs()))

    assert text.startswith("# Build Arena maintainer delegation task\n")
    assert "## Objective" in text
    assert "## Allowed write path intent" in text
    assert "## Required verification commands" in text
    assert "uv run pyright" in text
    assert "Do not execute OpenHands" in text
    assert "Hermes owns semantic authorization" in text
