from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from arena import project_model_cli
from arena.project_model_freshness import assess_project_model_freshness, freshness_to_dict

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "docs" / "schemas" / "project-model-freshness-v0.schema.json"


def _run(cmd: list[str], cwd: Path, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=cwd, text=True, capture_output=True, check=check)


def _init_repo(repo: Path) -> str:
    repo.mkdir(parents=True)
    (repo / "README.md").write_text("# Repo\n", encoding="utf-8")
    _run(["git", "init", "-b", "main"], repo)
    _run(["git", "config", "user.email", "test@example.invalid"], repo)
    _run(["git", "config", "user.name", "Test User"], repo)
    _run(["git", "add", "."], repo)
    _run(["git", "commit", "-m", "initial"], repo)
    return _run(["git", "rev-parse", "HEAD"], repo).stdout.strip()


def _snapshot(path: Path, repo: Path, head: str, *, dirty: bool = False, graph_hash: str = "graph-a", project_graph_hash: str = "graph-a") -> Path:
    payload: dict[str, Any] = {
        "schemaVersion": "project-model/v1",
        "id": "snapshot-1",
        "project": {"projectRoot": str(repo), "projectId": "repo", "goal": "test", "nonGoals": ["none"]},
        "snapshot": {"graph_hash": graph_hash},
        "projectGraph": {"graphHash": project_graph_hash},
        "provenance": {"git": {"headOid": head, "dirty": dirty, "dirtyPaths": [], "dirtyStateFingerprint": "fingerprint"}},
        "gateReport": {"passed": True, "violations": []},
        "hashes": {"artifactHashes": {}},
        "iterationReadiness": {"qualityGates": [], "openQuestions": [], "priorityBacklog": []},
    }
    path.write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")
    return path


def _validate(payload: dict[str, Any]) -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    errors = sorted(Draft202012Validator(schema).iter_errors(payload), key=lambda error: list(error.path))
    assert errors == []


def test_fresh_snapshot_is_safe_and_schema_valid(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    head = _init_repo(repo)
    snapshot = _snapshot(tmp_path / "project-model-v1.json", repo, head)

    report = assess_project_model_freshness(repo, snapshot)
    payload = freshness_to_dict(report)

    assert payload["status"] == "fresh"
    assert payload["safeForReadOnlyReview"] is True
    assert payload["safeForMutation"] is True
    assert payload["exitCode"] == 0
    _validate(payload)


def test_dirty_worktree_precedes_base_advanced_and_exits_two(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    head = _init_repo(repo)
    snapshot = _snapshot(tmp_path / "project-model-v1.json", repo, head)
    (repo / "README.md").write_text("# Changed\n", encoding="utf-8")
    _run(["git", "commit", "--allow-empty", "-m", "advance"], repo)

    payload = freshness_to_dict(assess_project_model_freshness(repo, snapshot))

    assert payload["status"] == "dirty-worktree"
    assert payload["safeForMutation"] is False
    assert payload["exitCode"] == 2
    assert "README.md" in payload["currentDirtyPaths"]
    _validate(payload)


def test_base_advanced_when_current_head_descends_from_snapshot(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    head = _init_repo(repo)
    snapshot = _snapshot(tmp_path / "project-model-v1.json", repo, head)
    (repo / "next.txt").write_text("next\n", encoding="utf-8")
    _run(["git", "add", "next.txt"], repo)
    _run(["git", "commit", "-m", "advance"], repo)

    payload = freshness_to_dict(assess_project_model_freshness(repo, snapshot))

    assert payload["status"] == "base-advanced"
    assert payload["exitCode"] == 2


def test_branch_diverged_when_current_head_is_not_descendant(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    head = _init_repo(repo)
    snapshot = _snapshot(tmp_path / "project-model-v1.json", repo, head)
    _run(["git", "checkout", "-b", "other"], repo)
    (repo / "other.txt").write_text("other\n", encoding="utf-8")
    _run(["git", "add", "other.txt"], repo)
    _run(["git", "commit", "-m", "other"], repo)
    _run(["git", "checkout", "main"], repo)
    (repo / "main.txt").write_text("main\n", encoding="utf-8")
    _run(["git", "add", "main.txt"], repo)
    _run(["git", "commit", "-m", "main"], repo)
    other_head = _run(["git", "rev-parse", "other"], repo).stdout.strip()
    _snapshot(snapshot, repo, other_head)

    payload = freshness_to_dict(assess_project_model_freshness(repo, snapshot))

    assert payload["status"] == "branch-diverged"
    assert payload["exitCode"] == 2


def test_snapshot_hash_mismatch_takes_precedence(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    head = _init_repo(repo)
    snapshot = _snapshot(tmp_path / "project-model-v1.json", repo, head, graph_hash="a", project_graph_hash="b")
    (repo / "README.md").write_text("# Dirty\n", encoding="utf-8")

    payload = freshness_to_dict(assess_project_model_freshness(repo, snapshot))

    assert payload["status"] == "snapshot-mismatch"
    assert payload["exitCode"] == 2


def test_cli_emits_json_for_non_fresh_status(tmp_path: Path, capsys: Any) -> None:
    repo = tmp_path / "repo"
    head = _init_repo(repo)
    snapshot = _snapshot(tmp_path / "project-model-v1.json", repo, head)
    (repo / "README.md").write_text("# Dirty\n", encoding="utf-8")

    rc = project_model_cli.main(["freshness", "--project", str(repo), "--snapshot", str(snapshot)])
    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert rc == 2
    assert payload["status"] == "dirty-worktree"


def test_freshness_output_is_stable_for_identical_inputs(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    head = _init_repo(repo)
    snapshot = _snapshot(tmp_path / "project-model-v1.json", repo, head)

    first = freshness_to_dict(assess_project_model_freshness(repo, snapshot))
    second = freshness_to_dict(assess_project_model_freshness(repo, snapshot))

    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)
    assert first["aheadBehind"]["available"] is False


def test_missing_git_fails_closed_to_unknown(monkeypatch: Any, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    snapshot = _snapshot(tmp_path / "project-model-v1.json", repo, "abc123")

    import arena.project_model_freshness as freshness

    def fake_run(*args: object, **kwargs: object) -> object:
        raise FileNotFoundError("git")

    monkeypatch.setattr(freshness.subprocess, "run", fake_run)

    payload = freshness_to_dict(assess_project_model_freshness(repo, snapshot))

    assert payload["status"] == "unknown"
    assert payload["exitCode"] == 2
    assert any("git executable not found" in warning for warning in payload["warnings"])


def test_freshness_does_not_write_to_target_repo(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    head = _init_repo(repo)
    snapshot = _snapshot(tmp_path / "project-model-v1.json", repo, head)
    before = sorted(path.relative_to(repo).as_posix() for path in repo.rglob("*") if path.is_file())

    assess_project_model_freshness(repo, snapshot)

    after = sorted(path.relative_to(repo).as_posix() for path in repo.rglob("*") if path.is_file())
    assert after == before
