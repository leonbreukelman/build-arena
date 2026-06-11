from __future__ import annotations

import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from arena.boundary import is_boundary_violation
from scorer.goal_config import GoalConfig, load_goal_config


@dataclass(frozen=True)
class PatchGateResult:
    accepted: bool
    reason: str | None
    touched_paths: tuple[str, ...]
    added_lines: int
    deleted_lines: int
    detail: str = ""

    def to_jsonable(self) -> dict[str, Any]:
        return asdict(self)


def validate_unified_diff(
    repo: Path,
    diff_text: str,
    *,
    goal_config: GoalConfig | None = None,
) -> PatchGateResult:
    target = repo.resolve()
    config = goal_config or load_goal_config(target)
    if not diff_text.strip():
        return _reject("empty_diff")
    if "GIT binary patch" in diff_text or "Binary files " in diff_text:
        stats = _parse_diff_stats(diff_text)
        return PatchGateResult(False, "binary_diff", stats.touched_paths, stats.added_lines, stats.deleted_lines)

    stats = _parse_diff_stats(diff_text)
    if not stats.touched_paths:
        return _reject("malformed_diff")
    if is_boundary_violation(stats.touched_paths, goal_config=config):
        return PatchGateResult(
            False,
            "boundary_violation",
            stats.touched_paths,
            stats.added_lines,
            stats.deleted_lines,
        )
    if len(stats.touched_paths) > config.diff_caps.max_files or stats.added_lines + stats.deleted_lines > config.diff_caps.max_lines:
        return PatchGateResult(
            False,
            "diff_caps_exceeded",
            stats.touched_paths,
            stats.added_lines,
            stats.deleted_lines,
        )

    proc = subprocess.run(
        ["git", "apply", "--check", "-"],
        cwd=target,
        input=diff_text,
        text=True,
        capture_output=True,
        check=False,
    )
    if proc.returncode != 0:
        return PatchGateResult(
            False,
            "git_apply_check_failed",
            stats.touched_paths,
            stats.added_lines,
            stats.deleted_lines,
            proc.stderr.strip(),
        )
    return PatchGateResult(True, None, stats.touched_paths, stats.added_lines, stats.deleted_lines)


@dataclass(frozen=True)
class _DiffStats:
    touched_paths: tuple[str, ...]
    added_lines: int
    deleted_lines: int


def _reject(reason: str) -> PatchGateResult:
    return PatchGateResult(False, reason, (), 0, 0)


def _parse_diff_stats(diff_text: str) -> _DiffStats:
    paths: list[str] = []
    added = 0
    deleted = 0
    old_path: str | None = None
    new_path: str | None = None
    for line in diff_text.splitlines():
        if line.startswith("diff --git "):
            parts = line.split()
            if len(parts) >= 4:
                rel = _strip_diff_prefix(parts[3]) or _strip_diff_prefix(parts[2])
                if rel is not None:
                    paths.append(rel)
        elif line.startswith("--- "):
            old_path = _strip_diff_prefix(line[4:].strip())
        elif line.startswith("+++ "):
            new_path = _strip_diff_prefix(line[4:].strip())
            rel = new_path or old_path
            if rel is not None:
                paths.append(rel)
        # Header lines are handled above; only content +/- lines count toward caps.
        elif line.startswith("+"):
            added += 1
        elif line.startswith("-"):
            deleted += 1
    return _DiffStats(tuple(dict.fromkeys(paths)), added, deleted)


def _strip_diff_prefix(raw: str) -> str | None:
    value = raw.strip().strip('"')
    if value == "/dev/null":
        return None
    for prefix in ("a/", "b/"):
        if value.startswith(prefix):
            value = value[len(prefix) :]
    value = value.replace("\\", "/").lstrip("/")
    if not value or ".." in value.split("/"):
        return None
    return value
