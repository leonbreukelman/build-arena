from __future__ import annotations

import ast
import hashlib
import json
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path, PurePosixPath
from typing import Any

from arena.boundary import is_boundary_violation
from scorer.goal_config import GoalConfig, load_goal_config

SELECTION_VERSION = "target-selection/v1"


@dataclass(frozen=True)
class TargetSignals:
    coverage_gap: float
    lint_violations: int
    lint_density: float
    complexity: float
    git_churn: int
    todo_count: int
    loc: int

    def to_jsonable(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class TargetCandidate:
    rank: int
    path: str
    score: float
    signals: TargetSignals

    def to_jsonable(self) -> dict[str, Any]:
        return {
            "rank": self.rank,
            "path": self.path,
            "score": self.score,
            "signals": self.signals.to_jsonable(),
        }


@dataclass(frozen=True)
class TargetSelection:
    id: str
    version: str
    git_oid: str
    goal_config_sha: str
    goal_config_schema_version: str
    candidate_count: int
    omitted_count: int
    candidates: tuple[TargetCandidate, ...]

    def to_jsonable(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "version": self.version,
            "git_oid": self.git_oid,
            "goal_config_sha": self.goal_config_sha,
            "goal_config_schema_version": self.goal_config_schema_version,
            "candidate_count": self.candidate_count,
            "omitted_count": self.omitted_count,
            "candidates": [candidate.to_jsonable() for candidate in self.candidates],
        }


def select_targets(
    repo: Path,
    *,
    max_candidates: int = 5,
    lint_path: Path | None = None,
    coverage_path: Path | None = None,
    goal_config: GoalConfig | None = None,
) -> TargetSelection:
    if max_candidates <= 0:
        raise ValueError("max_candidates must be positive")

    target = repo.resolve()
    config = goal_config or load_goal_config(target)
    git_oid = _git_oid(target)
    coverage_gaps = _coverage_gaps(target, coverage_path or Path(config.coverage.source))
    lint_counts = _lint_counts(target, lint_path)

    ranked = sorted(
        (_candidate_for(target, rel_path, coverage_gaps, lint_counts) for rel_path in _candidate_paths(target, config)),
        key=lambda candidate: (-candidate.score, candidate.path),
    )
    limited = tuple(
        TargetCandidate(
            rank=index,
            path=candidate.path,
            score=candidate.score,
            signals=candidate.signals,
        )
        for index, candidate in enumerate(ranked[:max_candidates], start=1)
    )
    selection_id = _selection_id(
        git_oid=git_oid,
        goal_config_sha=config.content_hash,
        candidates=limited,
        candidate_count=len(ranked),
        omitted_count=max(0, len(ranked) - len(limited)),
    )
    return TargetSelection(
        id=selection_id,
        version=SELECTION_VERSION,
        git_oid=git_oid,
        goal_config_sha=config.content_hash,
        goal_config_schema_version=config.schema_version,
        candidate_count=len(ranked),
        omitted_count=max(0, len(ranked) - len(limited)),
        candidates=limited,
    )


def _candidate_paths(repo: Path, goal_config: GoalConfig) -> tuple[str, ...]:
    paths: list[str] = []
    for root in goal_config.paths.source_roots:
        root_path = repo / root
        if not root_path.exists():
            continue
        for path in sorted(root_path.rglob("*.py")):
            rel = _relative_path(repo, path)
            if is_boundary_violation([rel], goal_config=goal_config):
                continue
            paths.append(rel)
    return tuple(sorted(dict.fromkeys(paths)))


def _candidate_for(
    repo: Path,
    rel_path: str,
    coverage_gaps: dict[str, float],
    lint_counts: dict[str, int],
) -> TargetCandidate:
    path = repo / rel_path
    text = path.read_text(encoding="utf-8")
    loc = len(text.splitlines())
    lint_violations = lint_counts.get(rel_path, 0)
    signals = TargetSignals(
        coverage_gap=round(coverage_gaps.get(rel_path, 0.0), 6),
        lint_violations=lint_violations,
        lint_density=round(lint_violations / max(loc, 1), 6),
        complexity=round(_complexity(text), 6),
        git_churn=_git_churn(repo, rel_path),
        todo_count=_todo_count(text),
        loc=loc,
    )
    score = _score(signals)
    return TargetCandidate(rank=0, path=rel_path, score=score, signals=signals)


def _score(signals: TargetSignals) -> float:
    return round(
        (4.0 * signals.coverage_gap)
        + (100.0 * signals.lint_density)
        + (2.0 * signals.complexity)
        + (3.0 * signals.git_churn)
        + (5.0 * signals.todo_count),
        6,
    )


def _coverage_gaps(repo: Path, coverage_path: Path) -> dict[str, float]:
    path = repo / coverage_path
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    files = payload.get("files", {}) if isinstance(payload, dict) else {}
    if not isinstance(files, dict):
        return {}
    gaps: dict[str, float] = {}
    for raw_path, details in files.items():
        rel = _normalize_repo_path(repo, raw_path)
        if rel is None or not isinstance(details, dict):
            continue
        summary = details.get("summary", {})
        if not isinstance(summary, dict):
            continue
        percent = summary.get("percent_covered")
        if not isinstance(percent, int | float):
            continue
        gaps[rel] = round(max(0.0, 100.0 - float(percent)), 6)
    return gaps


def _lint_counts(repo: Path, lint_path: Path | None) -> dict[str, int]:
    if lint_path is None:
        return {}
    path = repo / lint_path
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    if not isinstance(payload, list):
        return {}
    counts: dict[str, int] = {}
    for item in payload:
        if not isinstance(item, dict):
            continue
        filename = item.get("filename")
        rel = _normalize_repo_path(repo, filename)
        if rel is None:
            continue
        counts[rel] = counts.get(rel, 0) + 1
    return counts


def _normalize_repo_path(repo: Path, value: Any) -> str | None:
    if not isinstance(value, str) or not value.strip():
        return None
    raw = value.strip().replace("\\", "/")
    candidate = Path(raw)
    if candidate.is_absolute():
        try:
            return _relative_path(repo, candidate)
        except ValueError:
            return None
    pure = PurePosixPath(raw)
    if pure.is_absolute() or ".." in pure.parts:
        return None
    normalized = pure.as_posix().removeprefix("./")
    return normalized or None


def _relative_path(repo: Path, path: Path) -> str:
    return path.resolve().relative_to(repo).as_posix()


def _git_oid(repo: Path) -> str:
    proc = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repo,
        text=True,
        capture_output=True,
        check=False,
    )
    if proc.returncode != 0:
        return ""
    return proc.stdout.strip()


def _git_churn(repo: Path, rel_path: str) -> int:
    proc = subprocess.run(
        ["git", "log", "--follow", "--format=%H", "--", rel_path],
        cwd=repo,
        text=True,
        capture_output=True,
        check=False,
    )
    if proc.returncode != 0:
        return 0
    return len([line for line in proc.stdout.splitlines() if line.strip()])


class _ComplexityVisitor(ast.NodeVisitor):
    def __init__(self) -> None:
        self.current = 1

    def visit_If(self, node: ast.If) -> Any:
        self.current += 1
        self.generic_visit(node)

    def visit_For(self, node: ast.For) -> Any:
        self.current += 1
        self.generic_visit(node)

    def visit_While(self, node: ast.While) -> Any:
        self.current += 1
        self.generic_visit(node)

    def visit_Try(self, node: ast.Try) -> Any:
        self.current += max(1, len(node.handlers))
        self.generic_visit(node)

    def visit_BoolOp(self, node: ast.BoolOp) -> Any:
        self.current += max(0, len(node.values) - 1)
        self.generic_visit(node)


def _complexity(text: str) -> float:
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return 0.0
    complexities: list[int] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
            visitor = _ComplexityVisitor()
            for child in node.body:
                visitor.visit(child)
            complexities.append(visitor.current)
    if not complexities:
        return 0.0
    return float(sum(complexities))


def _todo_count(text: str) -> int:
    lowered = text.lower()
    return lowered.count("todo") + lowered.count("fixme")


def _selection_id(
    *,
    git_oid: str,
    goal_config_sha: str,
    candidates: tuple[TargetCandidate, ...],
    candidate_count: int,
    omitted_count: int,
) -> str:
    payload = {
        "version": SELECTION_VERSION,
        "git_oid": git_oid,
        "goal_config_sha": goal_config_sha,
        "candidate_count": candidate_count,
        "omitted_count": omitted_count,
        "candidates": [candidate.to_jsonable() for candidate in candidates],
    }
    digest = hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()[:16]
    return f"target-selection-{digest}"
