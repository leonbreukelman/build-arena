from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest

from scorer.engine import COVERAGE_FLOOR, Scorer, ScoreVector, pinned_regressions


def _copy_committed_repo(src: Path, tmp_path: Path) -> Path:
    target = tmp_path / src.name
    shutil.copytree(src, target)
    subprocess.run(["git", "init", "-b", "main"], cwd=target, check=True, capture_output=True, text=True)
    subprocess.run(["git", "config", "user.email", "arena@example.invalid"], cwd=target, check=True)
    subprocess.run(["git", "config", "user.name", "Arena Tests"], cwd=target, check=True)
    subprocess.run(["git", "add", "."], cwd=target, check=True)
    subprocess.run(["git", "commit", "-m", "baseline"], cwd=target, check=True, capture_output=True, text=True)
    return target


def _score_patch(project_root: Path, tmp_path: Path, patch_path: Path):
    repo = _copy_committed_repo(project_root / ".arena" / "calibration" / "repo", tmp_path)
    subprocess.run(["git", "apply", str(patch_path)], cwd=repo, check=True, capture_output=True, text=True)
    subprocess.run(["git", "add", "."], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-m", patch_path.stem], cwd=repo, check=True, capture_output=True, text=True)
    return Scorer(project_root).score_repo(repo)


def test_calibration_catalog_has_thirteen_expected_diffs(project_root: Path) -> None:
    catalog = json.loads((project_root / ".arena" / "calibration" / "expected.json").read_text())
    assert len(catalog["positive"]) == 5
    assert len(catalog["negative"]) == 5
    assert len(catalog["neutral"]) == 3
    patches = sorted((project_root / ".arena" / "calibration" / "diffs").glob("*/*.patch"))
    assert len(patches) == 13


def test_calibration_baseline_is_healthy(project_root: Path, calibration_repo: Path) -> None:
    baseline = Scorer(project_root).score_repo(calibration_repo)
    assert baseline.vector.tests_pass is True
    assert baseline.vector.coverage_pct >= COVERAGE_FLOOR
    assert baseline.vector.pyright_errors >= 0
    assert baseline.vector.ruff_violations >= 0


@pytest.mark.parametrize("patch_name", ["P-1", "P-2", "P-3", "P-4", "P-5"])
def test_positive_calibration_diffs_score_above_baseline(project_root: Path, calibration_repo: Path, tmp_path: Path, patch_name: str) -> None:
    baseline = Scorer(project_root).score_repo(calibration_repo)
    after = _score_patch(project_root, tmp_path, project_root / ".arena" / "calibration" / "diffs" / "positive" / f"{patch_name}.patch")
    assert after.vector.composite > baseline.vector.composite, (patch_name, baseline.vector, after.vector)


@pytest.mark.parametrize("patch_name", ["N-1", "N-2", "N-3", "N-4", "N-5"])
def test_negative_calibration_diffs_score_below_or_pin_regress(project_root: Path, calibration_repo: Path, tmp_path: Path, patch_name: str) -> None:
    baseline = Scorer(project_root).score_repo(calibration_repo)
    after = _score_patch(project_root, tmp_path, project_root / ".arena" / "calibration" / "diffs" / "negative" / f"{patch_name}.patch")
    regressions = pinned_regressions(baseline.vector, after.vector)
    assert after.vector.composite < baseline.vector.composite or regressions, (patch_name, baseline.vector, after.vector, regressions)


@pytest.mark.parametrize("patch_name", ["Z-1", "Z-2", "Z-3"])
def test_neutral_calibration_diffs_stay_within_epsilon(project_root: Path, calibration_repo: Path, tmp_path: Path, patch_name: str) -> None:
    baseline = Scorer(project_root).score_repo(calibration_repo)
    after = _score_patch(project_root, tmp_path, project_root / ".arena" / "calibration" / "diffs" / "neutral" / f"{patch_name}.patch")
    for axis, before_value in baseline.vector.numeric_axes().items():
        assert abs(after.vector.numeric_axes()[axis] - before_value) < 1e-3, (patch_name, axis, before_value, after.vector.numeric_axes()[axis])


def test_pinned_regressions_report_each_pinned_axis() -> None:
    before = ScoreVector(
        composite=10.0,
        coverage_pct=90.0,
        pyright_errors=1,
        ruff_violations=0,
        cyclomatic_avg=1.0,
        runtime_p95_ms=10.0,
        tests_pass=True,
    )
    after = ScoreVector(
        composite=9.0,
        coverage_pct=84.0,
        pyright_errors=3,
        ruff_violations=0,
        cyclomatic_avg=1.0,
        runtime_p95_ms=10.0,
        tests_pass=False,
    )

    assert [regression.axis for regression in pinned_regressions(before, after)] == [
        "tests_pass",
        "coverage_pct",
        "pyright_errors",
    ]
