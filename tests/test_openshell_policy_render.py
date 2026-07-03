"""Tests for generated OpenShell policy and runner dry-run artifacts."""

from __future__ import annotations

import yaml

from arena.maintainer.openshell_policy import render_openshell_policy
from arena.maintainer.runner_command import render_runner_command
from arena.maintainer.task_packet import TaskPacket


def _packet() -> TaskPacket:
    return TaskPacket.model_validate(
        {
            "objective": "Prepare a dry-run delegated coding task.",
            "mode": "dry_run",
            "allowed_paths": ["arena/maintainer", "tests/test_openshell_policy_render.py"],
            "forbidden_paths": ["scorer", "verifier", "schema", "arena/generated"],
            "required_reads": ["AGENTS.md", "README.md", "pyproject.toml"],
            "required_commands": ["uv run pytest tests -q", "uv run ruff check .", "uv run pyright"],
            "stop_conditions": ["stop on live execution request"],
        }
    )


def test_openshell_policy_stub_includes_required_intents_and_draft_comments() -> None:
    text = render_openshell_policy(_packet())

    assert "GENERATED DRAFT" in text
    assert "NOT APPLIED" in text
    assert "Hermes policy is semantic authorization" in text
    assert "OpenShell is the future runtime enforcement layer" in text
    assert "read_intent" in text
    assert "write_intent" in text
    assert "forbidden_path_intent" in text
    assert "egress_intent" in text
    assert "routing_intent" in text
    assert "process_restrictions" in text

    data = yaml.safe_load(text)
    assert data["status"] == "generated_draft_not_applied"
    assert data["runtime"] == {"kind": "openshell_planned", "execution": "not_run"}
    assert data["filesystem"]["write_intent"] == [
        "arena/maintainer",
        "tests/test_openshell_policy_render.py",
    ]
    assert data["network"]["egress_intent"] == "none"
    assert data["inference"]["routing_intent"] == (
        "delegated_worker_no_live_provider_call_in_this_slice"
    )
    assert data["process_restrictions"]["dry_run_only"] is True
    assert data["process_restrictions"]["execute_openhands"] is False
    assert data["process_restrictions"]["target_apply_or_promote"] is False
    assert data["verification"] == {"owner": "hermes", "status": "not_verified"}


def test_runner_command_is_dry_run_only() -> None:
    script = render_runner_command(_packet())

    assert script.startswith("# GENERATED -- DO NOT EXECUTE")
    assert "#!/usr/bin/env sh\n" in script
    assert "DRY RUN ONLY" in script
    assert "no OpenHands execution" in script
    assert "no OpenShell sandbox" in script
    assert "no GitHub call" in script
    assert "execution: not_run" in script
    assert "runtime: openshell_planned" in script
    assert "# required verification: uv run pyright" in script
