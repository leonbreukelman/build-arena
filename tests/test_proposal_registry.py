from __future__ import annotations

import json
import subprocess
from pathlib import Path

from arena.proposal_planner import build_proposal_plan
from arena.proposal_registry import ProposalRegistry, capture_git_lineage


def _init_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "README.md").write_text("# Readme\n", encoding="utf-8")
    subprocess.run(["git", "init", "-b", "main"], cwd=repo, check=True, capture_output=True, text=True)
    subprocess.run(["git", "config", "user.email", "test@example.invalid"], cwd=repo, check=True, capture_output=True, text=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=repo, check=True, capture_output=True, text=True)
    subprocess.run(["git", "add", "README.md"], cwd=repo, check=True, capture_output=True, text=True)
    subprocess.run(["git", "commit", "-m", "baseline"], cwd=repo, check=True, capture_output=True, text=True)
    return repo


def _scorecard(tmp_path: Path, repo: Path) -> Path:
    payload = {
        "schemaVersion": "project-intake-scorecard/v0",
        "id": "scorecard-registry",
        "snapshotId": "snapshot-registry",
        "snapshotHash": "snapshot-hash",
        "projectRoot": str(repo),
        "findings": [
            {
                "id": "doc.index.missing",
                "title": "Docs missing",
                "evidence": [{"kind": "absence", "path": "docs/index.md", "checked": True}],
                "recommendedAction": "Create docs index",
                "verification": ["test -e docs/index.md"],
                "autonomyBoundary": "safe_to_patch_docs_only",
                "priorityScore": 100.0,
                "rank": 1,
            }
        ],
    }
    path = tmp_path / "scorecard.json"
    path.write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")
    return path


def test_registry_dedup_marks_repeat_as_duplicate(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    scorecard = _scorecard(tmp_path, repo)
    registry = ProposalRegistry(tmp_path / "proposal-registry.jsonl")

    first = build_proposal_plan(repo, scorecard, max_candidates=10, proposal_registry=registry, run_id="run-1")
    second = build_proposal_plan(repo, scorecard, max_candidates=10, proposal_registry=registry, run_id="run-2")

    records = registry.records()
    assert first.candidates[0].registry_status == "pending"
    assert second.candidates[0].registry_status == "duplicate"
    assert len([record for record in records if record.status == "pending"]) == 1
    assert len([record for record in records if record.status == "duplicate"]) == 1


def test_lineage_stamp_captures_base_git_state(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    lineage = capture_git_lineage(
        repo,
        project_id="test-project",
        snapshot_id="snapshot-registry",
        snapshot_hash="snapshot-hash",
        scorecard_id="scorecard-registry",
        scorecard_hash="scorecard-hash",
        run_id="run-1",
    )

    assert lineage.project_id == "test-project"
    assert lineage.base_branch == "main"
    assert lineage.base_head_oid
    assert lineage.dirty is False
    assert lineage.dirty_fingerprint
    assert lineage.snapshot_id == "snapshot-registry"
    assert lineage.scorecard_id == "scorecard-registry"


def test_promoted_finding_is_not_reproposed(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    scorecard = _scorecard(tmp_path, repo)
    registry = ProposalRegistry(tmp_path / "proposal-registry.jsonl")

    first = build_proposal_plan(repo, scorecard, max_candidates=10, proposal_registry=registry, run_id="run-1")
    registry.mark(first.candidates[0].proposal_key, "promoted", run_id="run-1")
    second = build_proposal_plan(repo, scorecard, max_candidates=10, proposal_registry=registry, run_id="run-2")

    assert second.candidate_count == 0
    assert second.skipped_findings[0]["reason"] == "promoted_in_registry"


def test_lineage_mismatch_blocks_apply(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    lineage = capture_git_lineage(
        repo,
        project_id="test-project",
        snapshot_id="snapshot-registry",
        snapshot_hash="snapshot-hash",
        scorecard_id="scorecard-registry",
        scorecard_hash="scorecard-hash",
        run_id="run-1",
    )
    (repo / "README.md").write_text("# Changed\n", encoding="utf-8")
    subprocess.run(["git", "add", "README.md"], cwd=repo, check=True, capture_output=True, text=True)
    subprocess.run(["git", "commit", "-m", "change base"], cwd=repo, check=True, capture_output=True, text=True)

    registry = ProposalRegistry(tmp_path / "proposal-registry.jsonl")
    result = registry.check_lineage(repo, lineage)

    assert result.ok is False
    assert result.reason == "base_head_mismatch"
