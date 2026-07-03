"""Example-packet tests for maintainer CLI dogfood artifacts."""

from __future__ import annotations

import json
from pathlib import Path

from arena.maintainer.policy import evaluate_task_packet
from arena.maintainer.task_packet import TaskPacket


def test_openshell_preflight_example_packet_is_valid_and_policy_allowed() -> None:
    packet_path = Path("docs/examples/maintainer-openshell-preflight-packet.json")

    packet = TaskPacket.model_validate(json.loads(packet_path.read_text(encoding="utf-8")))
    result = evaluate_task_packet(packet)

    assert packet.mode == "dry_run"
    assert result.allowed is True
    assert result.execution == "not_run"
    assert result.runtime == "openshell_planned"
    assert "openshell doctor check" in packet.required_commands
    assert "docs/examples/maintainer-openshell-preflight-packet.json" in packet.allowed_paths
    assert ".arena/scorer.lock.toml" in packet.forbidden_paths
