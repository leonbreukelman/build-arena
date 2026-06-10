from __future__ import annotations

import subprocess
from pathlib import Path

from arena.generated.models import Verdict, VerdictOutcome
from arena.worktrees import CandidatePackager, WorktreeManager


def _git(cwd: Path, *args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=cwd, text=True).strip()


def test_candidate_packager_creates_candidate_branch_without_advancing_main(
    calibration_repo: Path,
    tmp_path: Path,
) -> None:
    base_oid = _git(calibration_repo, "rev-parse", "HEAD")
    manager = WorktreeManager(repo=calibration_repo, worktree_root=tmp_path / "worktrees")
    worktree = manager.create("cycle-1", base_oid)
    worktree_path = Path(worktree.path)
    (worktree_path / "CANDIDATE_MARKER.txt").write_text("candidate only\n", encoding="utf-8")
    verdict = Verdict(
        id="verdict-1",
        hypothesis_id="hyp-1",
        outcome=VerdictOutcome.PROMOTED,
        score_before_id="score-before",
        score_after_id="score-after",
        tests_passed=True,
        decided_ts=1.0,
    )

    candidate = CandidatePackager(main_repo=calibration_repo).promote(
        verdict,
        worktree,
        run_id="run-1",
        score_record_id="score-after",
    )

    assert _git(calibration_repo, "rev-parse", "HEAD") == base_oid
    assert not (calibration_repo / "CANDIDATE_MARKER.txt").exists()
    assert candidate.id.startswith("candidate-")
    assert candidate.git_oid == _git(calibration_repo, "rev-parse", "arena/candidate/cycle-1")
    assert candidate.promoted_from_verdict_id == verdict.id

    manager.teardown(worktree)

    assert _git(calibration_repo, "rev-parse", "HEAD") == base_oid
    assert _git(calibration_repo, "rev-parse", "arena/candidate/cycle-1") == candidate.git_oid
    assert "arena/cycle/cycle-1" not in subprocess.check_output(
        ["git", "branch", "--format=%(refname:short)"],
        cwd=calibration_repo,
        text=True,
    )
