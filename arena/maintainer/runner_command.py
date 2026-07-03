"""Render the dry-run runner command artifact for future delegated workers."""

from __future__ import annotations

from arena.maintainer.task_packet import TaskPacket


def render_runner_command(packet: TaskPacket) -> str:
    """Render ``runner-command.sh`` as a non-executing dry-run script."""
    commands = "\n".join(f"# required verification: {command}" for command in packet.required_commands)
    return (
        "# GENERATED -- DO NOT EXECUTE. Dry-run command preview only.\n"
        "# No OpenHands, OpenShell sandbox, GitHub call, push, merge, apply, or promote.\n"
        "#!/usr/bin/env sh\n"
        "set -eu\n"
        "echo 'DRY RUN ONLY: no OpenHands execution, no OpenShell sandbox, no GitHub call.'\n"
        "echo 'Hermes verification owner: hermes; execution: not_run; runtime: openshell_planned.'\n"
        f"echo 'Task objective: {_single_quote_shell_text(packet.objective)}'\n"
        f"{commands}\n"
    )


def _single_quote_shell_text(value: str) -> str:
    return value.replace("'", "'\"'\"'")
