"""Boundary checks for hypothesis target paths.

The boundary check is deliberately small and deterministic: future runners call it
before spawning any subscription/local coding adapter. A hypothesis that targets
read-only scorer/verifier/schema/generated paths is rejected before the adapter
can edit.
"""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import PurePosixPath

from scorer.goal_config import GoalConfig

DEFAULT_READ_ONLY_DIRS: tuple[str, ...] = (
    "scorer/",
    "verifier/",
    "schema/",
    "arena/generated/",
    "dashboard/src/lib/generated/",
)
DEFAULT_READ_ONLY_FILES: tuple[str, ...] = (".arena/scorer.lock.toml",)


def _normalize_relative_path(path: str) -> str:
    raw = path.replace("\\", "/").strip()
    if raw in {"", "."}:
        return ""
    pure = PurePosixPath(raw)
    if pure.is_absolute() or ".." in pure.parts:
        raise ValueError(f"target path must be repo-relative and non-traversing: {path!r}")
    return pure.as_posix().removeprefix("./")


def is_boundary_violation(
    target_files: Iterable[str],
    read_only_dirs: Iterable[str] = DEFAULT_READ_ONLY_DIRS,
    read_only_files: Iterable[str] = DEFAULT_READ_ONLY_FILES,
    *,
    goal_config: GoalConfig | None = None,
) -> bool:
    """Return True when any target is read-only Phase-1 safety surface."""

    normalized_roots = tuple(_normalize_relative_path(root).rstrip("/") + "/" for root in read_only_dirs)
    normalized_files = frozenset(_normalize_relative_path(path) for path in read_only_files)
    goal_paths = () if goal_config is None else goal_config.paths.read_only + goal_config.paths.out_of_scope
    normalized_goal_paths = frozenset(_normalize_relative_path(path) for path in goal_paths)
    normalized_goal_roots = tuple(path.rstrip("/") + "/" for path in normalized_goal_paths)
    for target in target_files:
        normalized = _normalize_relative_path(target)
        if normalized in normalized_files:
            return True
        if normalized in normalized_goal_paths:
            return True
        for root in normalized_roots:
            root_without_slash = root.rstrip("/")
            if normalized == root_without_slash or normalized.startswith(root):
                return True
        for root in normalized_goal_roots:
            if normalized.startswith(root):
                return True
    return False
