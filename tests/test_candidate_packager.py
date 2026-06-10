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


def test_candidate_packager_excludes_evidence_patch_artifacts(
    calibration_repo: Path,
    tmp_path: Path,
) -> None:
    base_oid = _git(calibration_repo, "rev-parse", "HEAD")
    manager = WorktreeManager(repo=calibration_repo, worktree_root=tmp_path / "worktrees")
    worktree = manager.create("cycle-artifacts", base_oid)
    worktree_path = Path(worktree.path)
    marker = worktree_path / "CANDIDATE_MARKER.txt"
    marker.write_text("candidate only\n", encoding="utf-8")
    patch_artifact = worktree_path / ".arena" / "patches" / "hyp.patch"
    provenance_artifact = patch_artifact.with_suffix(".patch.provenance.json")
    patch_artifact.parent.mkdir(parents=True, exist_ok=True)
    patch_artifact.write_text("diff --git a/CANDIDATE_MARKER.txt b/CANDIDATE_MARKER.txt\n", encoding="utf-8")
    provenance_artifact.write_text('{"transport":"fixture"}\n', encoding="utf-8")
    runtime_artifact = worktree_path / ".arena" / "runtime.json"
    runtime_artifact.write_text('{"runtime":"fixture"}\n', encoding="utf-8")
    verdict = Verdict(
        id="verdict-artifacts",
        hypothesis_id="hyp-artifacts",
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

    changed_paths = subprocess.check_output(
        ["git", "diff", "--name-only", base_oid, candidate.git_oid],
        cwd=calibration_repo,
        text=True,
    ).splitlines()
    assert "CANDIDATE_MARKER.txt" in changed_paths
    assert not any(path.startswith(".arena/") for path in changed_paths)
    assert patch_artifact.exists()
    assert provenance_artifact.exists()
    assert runtime_artifact.exists()

    manager.teardown(worktree)
