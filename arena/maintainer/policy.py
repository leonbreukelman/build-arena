"""Semantic policy checks for dry-run maintainer delegation packets."""

from __future__ import annotations

from pathlib import PurePosixPath

from pydantic import BaseModel, ConfigDict, Field

from arena.maintainer.task_packet import TaskPacket

FORBIDDEN_PHRASES: tuple[tuple[str, str], ...] = (
    ("target apply/promote", "target apply/promote is outside Build Arena propose-only scope"),
    ("apply/promote", "target apply/promote is outside Build Arena propose-only scope"),
    ("apply or promote", "target apply/promote is outside Build Arena propose-only scope"),
    ("apply and promote", "target apply/promote is outside Build Arena propose-only scope"),
    ("auto-merge", "auto-merge is not allowed"),
    ("automerge", "auto-merge is not allowed"),
    ("git push", "git push is not allowed"),
    ("broad live autonomy", "broad live autonomy is not allowed"),
    ("broad autonomous live", "broad live autonomy is not allowed"),
    ("unattended production autonomy", "broad live autonomy is not allowed"),
)

DEFAULT_FORBIDDEN_WRITE_PATHS: tuple[str, ...] = (
    "scorer",
    "verifier",
    "schema",
    "arena/generated",
    ".arena/scorer.lock.toml",
)


class PolicyResult(BaseModel):
    """Outcome of Hermes semantic authorization for a maintainer task packet."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    allowed: bool
    reasons: tuple[str, ...] = Field(default_factory=tuple)
    execution: str = "not_run"
    runtime: str = "openshell_planned"
    verification_owner: str = "hermes"
    verification_status: str = "not_verified"


def evaluate_task_packet(packet: TaskPacket) -> PolicyResult:
    """Evaluate a packet without running any delegated worker or sandbox."""
    reasons: list[str] = []
    reasons.extend(_phrase_rejections(packet))
    reasons.extend(_path_rejections(packet))
    return PolicyResult(allowed=not reasons, reasons=tuple(dict.fromkeys(reasons)))


def _phrase_rejections(packet: TaskPacket) -> list[str]:
    haystack = "\n".join(
        [
            packet.objective,
            *packet.required_commands,
            *packet.stop_conditions,
        ]
    ).lower()
    return [reason for phrase, reason in FORBIDDEN_PHRASES if phrase in haystack]


def _path_rejections(packet: TaskPacket) -> list[str]:
    reasons: list[str] = []
    forbidden_paths = tuple(dict.fromkeys((*DEFAULT_FORBIDDEN_WRITE_PATHS, *packet.forbidden_paths)))
    for allowed_path in packet.allowed_paths:
        for forbidden_path in forbidden_paths:
            if _paths_overlap(allowed_path, forbidden_path):
                reasons.append(f"allowed write path overlaps forbidden path: {allowed_path} -> {forbidden_path}")
    return reasons


def _paths_overlap(left: str, right: str) -> bool:
    left_norm = _normalize_path(left)
    right_norm = _normalize_path(right)
    return _is_same_or_child(left_norm, right_norm) or _is_same_or_child(right_norm, left_norm)


def _normalize_path(path: str) -> PurePosixPath:
    normalized = path.rstrip("/") or "."
    return PurePosixPath(normalized)


def _is_same_or_child(path: PurePosixPath, parent: PurePosixPath) -> bool:
    if parent == PurePosixPath("."):
        return True
    return path == parent or parent in path.parents
