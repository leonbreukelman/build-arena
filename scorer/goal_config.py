"""Per-repository goal configuration for Build Arena scoring.

The goal config is the operator-owned contract that tells Build Arena how to
measure a target repository without assuming the synthetic calibration repo's
layout or commands.
"""

from __future__ import annotations

import hashlib
import tomllib
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any

DEFAULT_GOAL_CONFIG = Path(".arena") / "goal.toml"
DEFAULT_COVERAGE_FLOOR = 85.0


class GoalConfigError(ValueError):
    """Raised when a goal config is missing or invalid."""


@dataclass(frozen=True)
class GoalCommands:
    test: tuple[str, ...]
    lint: tuple[str, ...]
    typecheck: tuple[str, ...]
    coverage: tuple[str, ...] | None = None
    runtime_proxy: tuple[str, ...] | None = None


@dataclass(frozen=True)
class CoverageConfig:
    source: str
    floor: float = DEFAULT_COVERAGE_FLOOR


@dataclass(frozen=True)
class PathConfig:
    source_roots: tuple[str, ...] = ("src",)
    out_of_scope: tuple[str, ...] = ()
    read_only: tuple[str, ...] = ()


@dataclass(frozen=True)
class DiffCaps:
    max_files: int = 8
    max_lines: int = 400


@dataclass(frozen=True)
class CompositeWeights:
    coverage_pct: float = 2.0
    pyright_errors: float = -5.0
    ruff_violations: float = -0.75
    cyclomatic_avg: float = -2.0
    runtime_p95_ms: float = -1.0
    test_failure_penalty: float = -1000.0


@dataclass(frozen=True)
class GoalConfig:
    config_path: Path
    content_hash: str
    schema_version: str
    project_id: str
    goal: str
    commands: GoalCommands
    coverage: CoverageConfig
    paths: PathConfig
    diff_caps: DiffCaps
    weights: CompositeWeights


def load_goal_config(repo: Path, config_path: Path | None = None) -> GoalConfig:
    """Load and validate `<repo>/.arena/goal.toml`.

    The returned dataclass contains only normalized immutable values so callers
    can safely use it in scoring provenance, event logs, and deterministic tests.
    """

    path = (config_path or repo / DEFAULT_GOAL_CONFIG).resolve()
    if not path.exists():
        raise GoalConfigError(f"goal config not found: {DEFAULT_GOAL_CONFIG}")

    raw_bytes = path.read_bytes()
    try:
        payload = tomllib.loads(raw_bytes.decode("utf-8"))
    except tomllib.TOMLDecodeError as exc:
        raise GoalConfigError(f"invalid TOML in {path}: {exc}") from exc

    content_hash = hashlib.sha256(raw_bytes).hexdigest()
    return _parse_goal_config(path, content_hash, payload)


def _parse_goal_config(path: Path, content_hash: str, payload: dict[str, Any]) -> GoalConfig:
    schema_version = _required_str(payload, "schema_version")
    if schema_version != "goal-config/v1":
        raise GoalConfigError("schema_version must be goal-config/v1")

    project_id = _required_str(payload, "project_id")
    goal = _optional_str(payload, "goal", default="")

    commands_payload = _required_table(payload, "commands")
    coverage_payload = _required_table(payload, "coverage")
    paths_payload = _optional_table(payload, "paths")
    caps_payload = _optional_table(payload, "diff_caps")
    weights_payload = _optional_table(payload, "weights")

    commands = GoalCommands(
        test=_required_command(commands_payload, "commands.test"),
        lint=_required_command(commands_payload, "commands.lint"),
        typecheck=_required_command(commands_payload, "commands.typecheck"),
        coverage=_optional_command(commands_payload, "coverage", "commands.coverage"),
        runtime_proxy=_optional_command(commands_payload, "runtime_proxy", "commands.runtime_proxy"),
    )
    coverage = CoverageConfig(
        source=_normalize_relative_path(_required_str(coverage_payload, "source"), "coverage.source"),
        floor=_optional_float(coverage_payload, "floor", default=DEFAULT_COVERAGE_FLOOR, label="coverage.floor"),
    )
    paths = PathConfig(
        source_roots=_optional_paths(paths_payload, "source_roots", default=("src",)),
        out_of_scope=_optional_paths(paths_payload, "out_of_scope", default=()),
        read_only=_optional_paths(paths_payload, "read_only", default=()),
    )
    diff_caps = DiffCaps(
        max_files=_positive_int(caps_payload, "max_files", default=8, label="diff_caps.max_files"),
        max_lines=_positive_int(caps_payload, "max_lines", default=400, label="diff_caps.max_lines"),
    )
    weights = CompositeWeights(
        coverage_pct=_optional_float(weights_payload, "coverage_pct", default=2.0, label="weights.coverage_pct"),
        pyright_errors=_optional_float(weights_payload, "pyright_errors", default=-5.0, label="weights.pyright_errors"),
        ruff_violations=_optional_float(weights_payload, "ruff_violations", default=-0.75, label="weights.ruff_violations"),
        cyclomatic_avg=_optional_float(weights_payload, "cyclomatic_avg", default=-2.0, label="weights.cyclomatic_avg"),
        runtime_p95_ms=_optional_float(weights_payload, "runtime_p95_ms", default=-1.0, label="weights.runtime_p95_ms"),
        test_failure_penalty=_optional_float(
            weights_payload,
            "test_failure_penalty",
            default=-1000.0,
            label="weights.test_failure_penalty",
        ),
    )

    return GoalConfig(
        config_path=path,
        content_hash=content_hash,
        schema_version=schema_version,
        project_id=project_id,
        goal=goal,
        commands=commands,
        coverage=coverage,
        paths=paths,
        diff_caps=diff_caps,
        weights=weights,
    )


def _required_table(payload: dict[str, Any], key: str) -> dict[str, Any]:
    value = payload.get(key)
    if not isinstance(value, dict):
        raise GoalConfigError(f"{key} must be a table")
    return value


def _optional_table(payload: dict[str, Any], key: str) -> dict[str, Any]:
    value = payload.get(key, {})
    if not isinstance(value, dict):
        raise GoalConfigError(f"{key} must be a table")
    return value


def _required_str(payload: dict[str, Any], key: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value.strip():
        raise GoalConfigError(f"{key} must be a non-empty string")
    return value.strip()


def _optional_str(payload: dict[str, Any], key: str, *, default: str) -> str:
    value = payload.get(key, default)
    if not isinstance(value, str):
        raise GoalConfigError(f"{key} must be a string")
    return value.strip()


def _required_command(payload: dict[str, Any], key: str) -> tuple[str, ...]:
    short_key = key.split(".")[-1]
    return _command(payload.get(short_key), key)


def _optional_command(payload: dict[str, Any], key: str, label: str) -> tuple[str, ...] | None:
    if key not in payload:
        return None
    return _command(payload[key], label)


def _command(value: Any, label: str) -> tuple[str, ...]:
    if not isinstance(value, list) or not value:
        raise GoalConfigError(f"{label} must be a non-empty list of strings")
    if not all(isinstance(part, str) and part for part in value):
        raise GoalConfigError(f"{label} must be a non-empty list of strings")
    return tuple(value)


def _optional_float(payload: dict[str, Any], key: str, *, default: float, label: str) -> float:
    value = payload.get(key, default)
    if isinstance(value, bool) or not isinstance(value, int | float):
        raise GoalConfigError(f"{label} must be a number")
    return float(value)


def _positive_int(payload: dict[str, Any], key: str, *, default: int, label: str) -> int:
    value = payload.get(key, default)
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise GoalConfigError(f"{label} must be a positive integer")
    return value


def _optional_paths(payload: dict[str, Any], key: str, *, default: tuple[str, ...]) -> tuple[str, ...]:
    if key not in payload:
        return default
    value = payload[key]
    if not isinstance(value, list):
        raise GoalConfigError(f"paths.{key} must be a list of relative paths")
    return tuple(_normalize_relative_path(item, f"paths.{key}") for item in value)


def _normalize_relative_path(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise GoalConfigError(f"{label} must contain non-empty relative paths")
    normalized = value.strip().replace("\\", "/").rstrip("/")
    path = PurePosixPath(normalized)
    parts = normalized.split("/")
    if path.is_absolute() or normalized == "" or any(part in {"", ".", ".."} for part in parts):
        raise GoalConfigError(f"{label} must contain repository-relative paths")
    return normalized
