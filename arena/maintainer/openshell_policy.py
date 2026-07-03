"""Render a draft OpenShell runtime policy artifact for future enforcement."""

from __future__ import annotations

from arena.maintainer.task_packet import TaskPacket


def render_openshell_policy(packet: TaskPacket) -> str:
    """Render ``openshell-policy.yaml`` as a generated draft, not an applied sandbox policy."""
    lines: list[str] = [
        "# GENERATED DRAFT: Build Arena maintainer dry-run OpenShell policy intent.",
        "# NOT APPLIED: this artifact does not create or enter a live OpenShell sandbox.",
        "# Hermes policy is semantic authorization; OpenShell is the future runtime enforcement layer.",
        "version: openshell-policy-draft/v0",
        "status: generated_draft_not_applied",
        "runtime:",
        "  kind: openshell_planned",
        "  execution: not_run",
        "filesystem:",
        "  read_intent:",
        *_yaml_list(packet.required_reads, indent="    "),
        "  write_intent:",
        *_yaml_list(packet.allowed_paths, indent="    "),
        "  forbidden_path_intent:",
        *_yaml_list(packet.forbidden_paths, indent="    "),
        "network:",
        "  egress_intent: none",
        "  allow_github: false",
        "inference:",
        "  routing_intent: delegated_worker_no_live_provider_call_in_this_slice",
        "  live_model_required: false",
        "process_restrictions:",
        "  dry_run_only: true",
        "  execute_openshell: false",
        "  execute_openhands: false",
        "  git_push: false",
        "  auto_merge: false",
        "  target_apply_or_promote: false",
        "verification:",
        "  owner: hermes",
        "  status: not_verified",
    ]
    return "\n".join(lines) + "\n"


def _yaml_list(values: tuple[str, ...], *, indent: str) -> list[str]:
    if not values:
        return [f"{indent}[]"]
    return [f"{indent}- {_quote_yaml_string(value)}" for value in values]


def _quote_yaml_string(value: str) -> str:
    escaped = value.replace('"', '\\"')
    return f'"{escaped}"'
