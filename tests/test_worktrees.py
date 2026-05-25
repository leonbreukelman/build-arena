from __future__ import annotations

import subprocess
from pathlib import Path

from arena.generated.models import Verdict, VerdictOutcome
from arena.worktrees import GitPromoter, WorktreeManager


def _git(cwd: Path, *args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=cwd, text=True).strip()


def test_worktree_manager_creates_promotes_and_tears_down_git_worktree(calibration_repo: Path, tmp_path: Path) -> None:
    base_oid = _git(calibration_repo, "rev-parse", "HEAD")
    manager = WorktreeManager(repo=calibration_repo, worktree_root=tmp_path / "worktrees")

    worktree = manager.create("cycle-1", base_oid)
    worktree_path = Path(worktree.path)

    assert worktree_path.exists()
    assert _git(worktree_path, "rev-parse", "HEAD") == base_oid

    marker = worktree_path / "PHASE4_MARKER.txt"
    marker.write_text("promoted\n")
    verdict = Verdict(
        id="verdict-1",
        hypothesis_id="hyp-1",
        outcome=VerdictOutcome.PROMOTED,
        score_before_id="score-before",
        score_after_id="score-after",
        tests_passed=True,
        decided_ts=1.0,
    )
    baseline = GitPromoter(main_repo=calibration_repo).promote(
        verdict,
        worktree,
        run_id="run-1",
        score_record_id="score-after",
    )

    assert baseline.git_oid == _git(calibration_repo, "rev-parse", "HEAD")
    assert (calibration_repo / "PHASE4_MARKER.txt").read_text() == "promoted\n"

    manager.teardown(worktree)

    assert not worktree_path.exists()
