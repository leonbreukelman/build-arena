from __future__ import annotations

import subprocess
from dataclasses import replace
from pathlib import Path

import pytest

from scorer.engine import Scorer, assert_vectors_close
from scorer.exceptions import ScorerNonDeterministicError


def test_rescoring_same_git_oid_is_deterministic(project_root: Path, calibration_repo: Path) -> None:
    scorer = Scorer(project_root)
    first = scorer.score_repo(calibration_repo)
    second = scorer.score_repo(calibration_repo)
    assert first.git_oid == second.git_oid
    assert first.scorer_lock_sha == second.scorer_lock_sha
    assert_vectors_close(first.vector, second.vector)
    scorer.drift_check(first, calibration_repo)


def test_drift_check_rejects_changed_baseline_git_oid(project_root: Path, calibration_repo: Path) -> None:
    scorer = Scorer(project_root)
    baseline = scorer.score_repo(calibration_repo)
    (calibration_repo / "README.md").write_text("changed baseline tree\n")
    subprocess.run(["git", "add", "README.md"], cwd=calibration_repo, check=True)
    subprocess.run(["git", "commit", "-m", "change baseline"], cwd=calibration_repo, check=True, capture_output=True, text=True)

    with pytest.raises(ScorerNonDeterministicError, match="git oid changed"):
        scorer.drift_check(baseline, calibration_repo)


def test_drift_check_rejects_axis_drift_without_oid_change(project_root: Path, calibration_repo: Path) -> None:
    scorer = Scorer(project_root)
    baseline = scorer.score_repo(calibration_repo)
    impossible = replace(
        baseline,
        vector=replace(baseline.vector, composite=baseline.vector.composite + 1.0),
    )

    with pytest.raises(ScorerNonDeterministicError, match="axis composite drifted"):
        scorer.drift_check(impossible, calibration_repo)
