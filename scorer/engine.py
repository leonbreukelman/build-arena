"""Deterministic Phase 1 scorer.

The scorer intentionally avoids wall-clock benchmarks. The calibration target
repository exposes a deterministic benchmark proxy, which preserves the
`runtime_p95_ms` axis semantics without introducing non-deterministic timing
noise that would violate the drift invariant.
"""

from __future__ import annotations

import ast
import json
import os
import subprocess
import time
from collections.abc import Iterable, Sequence
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from scorer.exceptions import ScorerNonDeterministicError
from scorer.goal_config import CompositeWeights, GoalConfig, load_goal_config
from scorer.lock import DEFAULT_LOCK_PATH, load_scorer_lock

DETERMINISM_TOLERANCE = 1.0e-6
COVERAGE_FLOOR = 85.0


@dataclass(frozen=True)
class ScoreVector:
    composite: float
    coverage_pct: float
    pyright_errors: int
    ruff_violations: int
    cyclomatic_avg: float
    runtime_p95_ms: float
    tests_pass: bool

    def numeric_axes(self) -> dict[str, float]:
        return {
            "composite": self.composite,
            "coverage_pct": self.coverage_pct,
            "pyright_errors": float(self.pyright_errors),
            "ruff_violations": float(self.ruff_violations),
            "cyclomatic_avg": self.cyclomatic_avg,
            "runtime_p95_ms": self.runtime_p95_ms,
            "tests_pass": 1.0 if self.tests_pass else 0.0,
        }


@dataclass(frozen=True)
class ScoreRecord:
    id: str
    git_oid: str
    scorer_lock_sha: str
    vector: ScoreVector
    computed_ts: float
    goal_config_sha: str = ""
    goal_config_schema_version: str = ""

    def to_jsonable(self) -> dict[str, Any]:
        data = asdict(self)
        data["vector"] = asdict(self.vector)
        return data


@dataclass(frozen=True)
class PinnedRegression:
    axis: str
    before: float | bool
    after: float | bool


def pinned_regressions(before: ScoreVector, after: ScoreVector) -> list[PinnedRegression]:
    """Return hard pinned-axis regressions for verifier rejection.

    Coverage is pinned by floor rather than strict monotonic movement: a patch
    may trade a small amount of coverage above the floor for a large runtime or
    quality gain, but it may not drop coverage below the configured floor.
    """
    regressions: list[PinnedRegression] = []
    if before.tests_pass and not after.tests_pass:
        regressions.append(PinnedRegression("tests_pass", True, False))
    if after.coverage_pct < COVERAGE_FLOOR:
        regressions.append(PinnedRegression("coverage_pct", before.coverage_pct, after.coverage_pct))
    if after.pyright_errors > before.pyright_errors:
        regressions.append(PinnedRegression("pyright_errors", before.pyright_errors, after.pyright_errors))
    return regressions


class Scorer:
    def __init__(
        self,
        project_root: Path,
        lock_path: Path | None = None,
        *,
        tolerance: float = DETERMINISM_TOLERANCE,
    ) -> None:
        self.project_root = project_root.resolve()
        self.lock_path = lock_path or DEFAULT_LOCK_PATH
        self.tolerance = tolerance
        self.lock = load_scorer_lock(self.project_root, self.lock_path, validate=True)
        self.lock_sha = self.lock.scorer_sha

    def score_repo(self, repo: Path) -> ScoreRecord:
        target = repo.resolve()
        goal_config = load_goal_config(target)
        # Re-validate at every score call so source changes fail closed.
        self.lock = load_scorer_lock(self.project_root, self.lock_path, validate=True)
        vector = self._score_vector(target, goal_config)
        git_oid = _git_oid(target)
        record_id = f"score-{git_oid[:12]}-{self.lock.scorer_sha[:12]}-{goal_config.content_hash[:12]}"
        return ScoreRecord(
            id=record_id,
            git_oid=git_oid,
            scorer_lock_sha=self.lock.scorer_sha,
            vector=vector,
            computed_ts=time.time(),
            goal_config_sha=goal_config.content_hash,
            goal_config_schema_version=goal_config.schema_version,
        )

    def drift_check(self, baseline_record: ScoreRecord, repo: Path) -> None:
        current = self.score_repo(repo)
        if current.git_oid != baseline_record.git_oid:
            raise ScorerNonDeterministicError(
                f"baseline git oid changed: expected {baseline_record.git_oid}, actual {current.git_oid}"
            )
        if current.goal_config_sha != baseline_record.goal_config_sha:
            raise ScorerNonDeterministicError(
                "goal config hash changed: "
                f"expected {baseline_record.goal_config_sha}, actual {current.goal_config_sha}"
            )
        for axis, expected in baseline_record.vector.numeric_axes().items():
            actual = current.vector.numeric_axes()[axis]
            if abs(actual - expected) > self.tolerance:
                raise ScorerNonDeterministicError(
                    f"axis {axis} drifted by {abs(actual - expected)}: expected {expected}, actual {actual}"
                )

    def _score_vector(self, repo: Path, goal_config: GoalConfig) -> ScoreVector:
        tests_pass, coverage_pct = _test_and_coverage(repo, goal_config)
        pyright_errors = _pyright_errors(repo, goal_config)
        ruff_violations = _ruff_violations(repo, goal_config)
        cyclomatic_avg = _cyclomatic_average(repo / root for root in goal_config.paths.source_roots)
        runtime_p95_ms = _runtime_proxy(repo, goal_config)
        composite = _composite(
            tests_pass=tests_pass,
            coverage_pct=coverage_pct,
            pyright_errors=pyright_errors,
            ruff_violations=ruff_violations,
            cyclomatic_avg=cyclomatic_avg,
            runtime_p95_ms=runtime_p95_ms,
            weights=goal_config.weights,
        )
        return ScoreVector(
            composite=round(composite, 6),
            coverage_pct=round(coverage_pct, 6),
            pyright_errors=pyright_errors,
            ruff_violations=ruff_violations,
            cyclomatic_avg=round(cyclomatic_avg, 6),
            runtime_p95_ms=round(runtime_p95_ms, 6),
            tests_pass=tests_pass,
        )


def _composite(
    *,
    tests_pass: bool,
    coverage_pct: float,
    pyright_errors: int,
    ruff_violations: int,
    cyclomatic_avg: float,
    runtime_p95_ms: float,
    weights: CompositeWeights,
) -> float:
    score = (
        (weights.coverage_pct * coverage_pct)
        + (weights.pyright_errors * pyright_errors)
        + (weights.ruff_violations * ruff_violations)
        + (weights.cyclomatic_avg * cyclomatic_avg)
        + (weights.runtime_p95_ms * runtime_p95_ms)
    )
    if not tests_pass:
        score += weights.test_failure_penalty
    return score


def _run(
    args: Sequence[str],
    repo: Path,
    *,
    timeout: int = 120,
    source_roots: Iterable[str] = ("src",),
) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PYTHONHASHSEED"] = "0"
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["TZ"] = "UTC"
    pythonpath = [str(repo / root) for root in source_roots]
    if existing := env.get("PYTHONPATH"):
        pythonpath.append(existing)
    env["PYTHONPATH"] = os.pathsep.join(pythonpath)
    return subprocess.run(list(args), cwd=repo, env=env, text=True, capture_output=True, timeout=timeout, check=False)


def _git_oid(repo: Path) -> str:
    proc = _run(["git", "rev-parse", "HEAD"], repo)
    if proc.returncode != 0:
        raise RuntimeError(f"git rev-parse failed: {proc.stderr}")
    return proc.stdout.strip()


def _test_and_coverage(repo: Path, goal_config: GoalConfig) -> tuple[bool, float]:
    coverage_file = repo / goal_config.coverage.source
    if coverage_file.exists():
        coverage_file.unlink()
    test_proc = _run(
        goal_config.commands.test,
        repo,
        timeout=180,
        source_roots=goal_config.paths.source_roots,
    )
    coverage_proc = None
    if goal_config.commands.coverage is not None:
        coverage_proc = _run(
            goal_config.commands.coverage,
            repo,
            timeout=180,
            source_roots=goal_config.paths.source_roots,
        )
    coverage_pct = 0.0
    if coverage_file.exists():
        try:
            coverage_pct = float(json.loads(coverage_file.read_text())["totals"]["percent_covered"])
        except (KeyError, json.JSONDecodeError, TypeError, ValueError):
            coverage_pct = 0.0
        coverage_file.unlink()
    (repo / ".coverage").unlink(missing_ok=True)
    coverage_command_ok = coverage_proc is None or coverage_proc.returncode == 0
    tests_pass = test_proc.returncode == 0 and coverage_command_ok and coverage_pct >= goal_config.coverage.floor
    return tests_pass, coverage_pct


def _ruff_violations(repo: Path, goal_config: GoalConfig) -> int:
    proc = _run(goal_config.commands.lint, repo, source_roots=goal_config.paths.source_roots)
    try:
        payload = json.loads(proc.stdout or "[]")
    except json.JSONDecodeError:
        return 999
    if isinstance(payload, list):
        return len(payload)
    return 999


def _pyright_errors(repo: Path, goal_config: GoalConfig) -> int:
    proc = _run(goal_config.commands.typecheck, repo, timeout=180, source_roots=goal_config.paths.source_roots)
    try:
        payload = json.loads(proc.stdout)
    except json.JSONDecodeError:
        return 999
    diagnostics = payload.get("generalDiagnostics", [])
    return sum(1 for diag in diagnostics if diag.get("severity") == "error")


def _runtime_proxy(repo: Path, goal_config: GoalConfig) -> float:
    if goal_config.commands.runtime_proxy is None:
        return 0.0
    proc = _run(goal_config.commands.runtime_proxy, repo, source_roots=goal_config.paths.source_roots)
    if proc.returncode != 0:
        return 9999.0
    try:
        return float(json.loads(proc.stdout)["runtime_p95_ms"])
    except (KeyError, json.JSONDecodeError, TypeError, ValueError):
        return 9999.0


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


def _function_complexity(function: ast.FunctionDef | ast.AsyncFunctionDef) -> int:
    visitor = _ComplexityVisitor()
    for child in function.body:
        visitor.visit(child)
    return visitor.current


def _cyclomatic_average(src_roots: Iterable[Path]) -> float:
    complexities: list[int] = []
    for src_root in src_roots:
        for path in sorted(src_root.rglob("*.py")):
            tree = ast.parse(path.read_text())
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                    complexities.append(_function_complexity(node))
    if not complexities:
        return 0.0
    return sum(complexities) / len(complexities)


def assert_vectors_close(a: ScoreVector, b: ScoreVector, *, tolerance: float = DETERMINISM_TOLERANCE) -> None:
    for axis, left in a.numeric_axes().items():
        right = b.numeric_axes()[axis]
        if abs(left - right) > tolerance:
            raise AssertionError(f"axis {axis} differs: {left} != {right}")


def score_axes_delta(before: ScoreVector, after: ScoreVector) -> dict[str, float]:
    return {axis: after.numeric_axes()[axis] - before.numeric_axes()[axis] for axis in before.numeric_axes()}
