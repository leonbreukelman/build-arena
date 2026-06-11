from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from arena.ledger import FingerprintFailureLedger
from arena.pr_packager import (
    FabricatedClaimError,
    OperatorAuthorizationError,
    RemoteTargetError,
    package_candidate_pr,
    record_owner_outcome,
    render_pr_body,
)


def _git(cwd: Path, *args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=cwd, text=True).strip()


def _init_repo(path: Path, remote_url: str) -> Path:
    path.mkdir(parents=True)
    subprocess.run(["git", "init", "-q"], cwd=path, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=path, check=True)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=path, check=True)
    (path / "README.md").write_text("repo\n", encoding="utf-8")
    subprocess.run(["git", "add", "README.md"], cwd=path, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "init"], cwd=path, check=True)
    subprocess.run(["git", "remote", "add", "origin", remote_url], cwd=path, check=True)
    return path


def _evidence(path: Path) -> Path:
    payload = {
        "schema_version": "cycle-evidence/v1",
        "run_id": "run-1",
        "cycle_id": "cycle-1",
        "worktree_root": "/tmp/worktrees",
        "worktree": {"id": "cycle-1", "path": "/tmp/worktrees/cycle-1", "base_git_oid": "a" * 40},
        "budget": {"cycle_count_cap": 60, "promotions_total": 1},
        "score_before": {
            "id": "score-before",
            "git_oid": "a" * 40,
            "scorer_lock_sha": "c" * 64,
            "computed_ts": 1.0,
            "vector": {
                "composite": 10.0,
                "coverage_pct": 90.0,
                "pyright_errors": 0,
                "ruff_violations": 1,
                "cyclomatic_avg": 2.0,
                "runtime_p95_ms": 30.0,
                "tests_pass": True,
            },
        },
        "score_after": {
            "id": "score-after",
            "git_oid": "b" * 40,
            "scorer_lock_sha": "c" * 64,
            "computed_ts": 2.0,
            "vector": {
                "composite": 12.5,
                "coverage_pct": 91.0,
                "pyright_errors": 0,
                "ruff_violations": 0,
                "cyclomatic_avg": 1.5,
                "runtime_p95_ms": 20.0,
                "tests_pass": True,
            },
        },
        "verdict": {
            "id": "verdict-1",
            "hypothesis_id": "hyp-1",
            "outcome": "PROMOTED",
            "reject_reason": None,
            "score_before_id": "score-before",
            "score_after_id": "score-after",
            "tests_passed": True,
            "score_delta": 2.5,
        },
        "candidate": {
            "id": "candidate-bbbbbbbbbbbb",
            "branch": "arena/candidate/cycle-1",
            "git_oid": "b" * 40,
            "score_record_id": "score-after",
            "promoted_from_verdict_id": "verdict-1",
        },
        "patch": {
            "base_git_oid": "a" * 40,
            "head_git_oid": "b" * 40,
            "added_lines": 3,
            "deleted_lines": 1,
            "sha256": "d" * 64,
            "files": [{"path": "src/core.py", "added_lines": 3, "deleted_lines": 1}],
        },
        "events": [
            {"type": "RUN_STARTED", "payload_json_sha": "1" * 64, "payload": {"run_id": "run-1"}},
            {
                "type": "HYPOTHESIS_PROPOSED",
                "payload_json_sha": "2" * 64,
                "payload": {"hypothesis_id": "hyp-1", "fingerprint_id": "fp-1"},
            },
            {"type": "CANDIDATE_PACKAGED", "payload_json_sha": "3" * 64, "payload": {}},
        ],
    }
    path.write_text(json.dumps(payload, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return path


class RecordingRunner:
    def __init__(self) -> None:
        self.calls: list[tuple[list[str], Path]] = []

    def __call__(self, args: list[str], *, cwd: Path) -> subprocess.CompletedProcess[str]:
        self.calls.append((args, cwd))
        stdout = "https://github.com/example/repo/pull/1\n" if args[:3] == ["gh", "pr", "create"] else ""
        return subprocess.CompletedProcess(args=args, returncode=0, stdout=stdout, stderr="")


def test_dry_run_renders_traceable_pr_body_without_gh(tmp_path: Path) -> None:
    evidence = _evidence(tmp_path / "cycle-1.json")
    target_repo = _init_repo(tmp_path / "target", "git@github.com:example/target.git")
    build_arena_repo = _init_repo(tmp_path / "build-arena", "git@github.com:example/build-arena.git")
    runner = RecordingRunner()

    result = package_candidate_pr(
        evidence_path=evidence,
        target_repo=target_repo,
        build_arena_repo=build_arena_repo,
        dry_run=True,
        command_runner=runner,
    )

    assert result.mode == "dry-run"
    assert result.pr_url is None
    assert runner.calls == []
    assert "arena/candidate/cycle-1" in result.body
    assert "#/candidate/git_oid" in result.body
    assert "#/score_after/vector/composite" in result.body
    assert "No automatic merge" in result.body


def test_fabricated_claim_fixture_fails(tmp_path: Path) -> None:
    evidence = _evidence(tmp_path / "cycle-1.json")

    with pytest.raises(FabricatedClaimError, match="fabricated"):
        render_pr_body(evidence, extra_claims=("This improves user delight by 40%",))


def test_open_pr_requires_explicit_operator_authorization(tmp_path: Path) -> None:
    evidence = _evidence(tmp_path / "cycle-1.json")
    target_repo = _init_repo(tmp_path / "target", "git@github.com:example/target.git")
    build_arena_repo = _init_repo(tmp_path / "build-arena", "git@github.com:example/build-arena.git")
    runner = RecordingRunner()

    with pytest.raises(OperatorAuthorizationError):
        package_candidate_pr(
            evidence_path=evidence,
            target_repo=target_repo,
            build_arena_repo=build_arena_repo,
            dry_run=False,
            allow_gh=False,
            command_runner=runner,
        )

    assert runner.calls == []


def test_open_pr_rejects_build_arena_remote_for_different_target(tmp_path: Path) -> None:
    evidence = _evidence(tmp_path / "cycle-1.json")
    remote = "git@github.com:example/build-arena.git"
    target_repo = _init_repo(tmp_path / "target", remote)
    build_arena_repo = _init_repo(tmp_path / "build-arena", remote)

    with pytest.raises(RemoteTargetError):
        package_candidate_pr(
            evidence_path=evidence,
            target_repo=target_repo,
            build_arena_repo=build_arena_repo,
            dry_run=False,
            allow_gh=True,
            command_runner=RecordingRunner(),
        )


def test_open_pr_uses_git_push_and_gh_create_when_authorized(tmp_path: Path) -> None:
    evidence = _evidence(tmp_path / "cycle-1.json")
    target_repo = _init_repo(tmp_path / "target", "git@github.com:example/target.git")
    build_arena_repo = _init_repo(tmp_path / "build-arena", "git@github.com:example/build-arena.git")
    runner = RecordingRunner()

    result = package_candidate_pr(
        evidence_path=evidence,
        target_repo=target_repo,
        build_arena_repo=build_arena_repo,
        dry_run=False,
        allow_gh=True,
        command_runner=runner,
    )

    assert result.mode == "opened"
    assert result.pr_url == "https://github.com/example/repo/pull/1"
    assert any(call[0][:2] == ["git", "push"] for call in runner.calls)
    assert any(call[0][:3] == ["gh", "pr", "create"] for call in runner.calls)
    assert all("merge" not in call[0] for call in runner.calls)


def test_owner_outcome_records_back_to_ledger(tmp_path: Path) -> None:
    evidence = _evidence(tmp_path / "cycle-1.json")
    ledger = FingerprintFailureLedger(tmp_path / "ledger.jsonl")

    record_owner_outcome(ledger, evidence, outcome="rejected", pr_url="https://github.com/example/repo/pull/1")

    rows = ledger.iter_records()
    assert rows == [
        {
            "cycle_id": "cycle-1",
            "fingerprint_id": "fp-1",
            "hypothesis_id": "hyp-1",
            "outcome": "OWNER_REJECTED",
            "pr_url": "https://github.com/example/repo/pull/1",
        }
    ]


def test_cli_dry_run_prints_body_without_pushing(tmp_path: Path) -> None:
    evidence = _evidence(tmp_path / "cycle-1.json")
    target_repo = _init_repo(tmp_path / "target", "git@github.com:example/target.git")
    build_arena_repo = _init_repo(tmp_path / "build-arena", "git@github.com:example/build-arena.git")

    completed = subprocess.run(
        [
            "uv",
            "run",
            "python",
            "-m",
            "arena.package_pr",
            "--evidence",
            str(evidence),
            "--target-repo",
            str(target_repo),
            "--build-arena-repo",
            str(build_arena_repo),
            "--dry-run",
        ],
        cwd=Path(__file__).resolve().parents[1],
        text=True,
        capture_output=True,
        check=True,
    )

    assert "arena/candidate/cycle-1" in completed.stdout
    assert "Dry-run only" in completed.stdout
