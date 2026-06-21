"""Tests for ``arena.proposal_run`` -- the orchestrator, exercised entirely offline.

The five stage CLIs are replaced by an injected ``FakeStages`` runner and ``git clone`` by a fake
git runner, so no subprocess, network, or live model call happens. The fake re-ranker writes a real
schema-valid reranked plan and the fake emit calls the *real* ``emit_proposal``, so the happy path
verifies an actual ``proposal.md`` end to end.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from arena import proposal_run
from arena.proposal_emit import emit_proposal
from arena.proposal_run import (
    EXIT_NO_PROPOSAL,
    EXIT_OK,
    EXIT_STAGE_FAILURE,
    EXIT_USAGE,
    ProposalRunError,
    RunConfig,
    StageResult,
    _decompose_args,
    _subprocess_env,
    main,
    resolve_target,
    run,
)


def _candidate(finding_id: str = "finding-1", *, rank: int = 1, title: str | None = None) -> dict[str, Any]:
    target = "src/pkg/a.py"
    return {
        "rank": rank,
        "finding_id": finding_id,
        "title": title or f"Title for {finding_id}",
        "target_path": target,
        "intent": f"Improve {target}.",
        "success_criterion": f"{target} exists.",
        "repo_facts_hash": "facts-hash",
        "repo_facts_block": "Repository facts:\n- README.md exists: yes",
        "grounding_constraints": ["Use only repository-grounded files."],
        "verification_commands": [f"test -s {target}"],
        "priority_score": 1000.0 - rank,
        "evidence_refs": [{"kind": "owned_surface", "path": target}],
        "source_recommended_action": "Do the improvement.",
        "target_paths": [target],
        "base_lineage": {"baseHeadOid": "abc123"},
        "intent_hash": f"intent-{finding_id}",
        "proposal_key": f"proposal-{finding_id}",
        "registry_status": "untracked",
    }


def _plan(candidates: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "schemaVersion": "proposal-plan/v0",
        "id": "reranked-plan",
        "sourceScorecardId": "scorecard-1",
        "snapshotId": "snapshot-1",
        "projectRoot": "/tmp/example-repo",
        "repoFactsHash": "facts-hash",
        "baseLineage": {"baseHeadOid": "abc123"},
        "candidateCount": len(candidates),
        "omittedCount": 0,
        "skippedCount": 0,
        "skippedFindings": [],
        "findingDispositions": [],
        "candidates": candidates,
    }


def _argd(args: list[str]) -> dict[str, str]:
    """Parse ``--flag value`` / store-true args into a dict (positionals ignored)."""
    out: dict[str, str] = {}
    i = 0
    while i < len(args):
        token = args[i]
        if token.startswith("--"):
            if i + 1 < len(args) and not args[i + 1].startswith("--"):
                out[token] = args[i + 1]
                i += 2
            else:
                out[token] = "true"
                i += 1
        else:
            i += 1
    return out


class FakeStages:
    """A stage runner that writes the expected artifacts and records each call.

    ``rerank_mode`` selects the re-ranker outcome:
      - "ok"            : trace with survivors + a real reranked plan, exit 0
      - "no_survivors"  : trace with survivorCount 0, no reranked plan, exit 1
      - "crash"         : trace with survivors, no reranked plan, exit 1
      - "crash_no_trace": no trace, no reranked plan, exit 1
    Any other stage can be made to fail by adding its module to ``fail``.
    """

    SNAPSHOT_ID = "snap-1"

    def __init__(self, *, rerank_mode: str = "ok", fail: set[str] | None = None) -> None:
        self.rerank_mode = rerank_mode
        self.fail = fail or set()
        self.calls: list[tuple[str, dict[str, str]]] = []

    def run(self, module: str, args: list[str], env: dict[str, str]) -> StageResult:
        argd = _argd(args)
        self.calls.append((module, argd))
        if module in self.fail:
            return StageResult(1, stderr=f"{module} forced failure")
        if module == proposal_run._DECOMPOSE_MODULE:
            return self._decompose(argd)
        if module == proposal_run._INTAKE_MODULE:
            Path(argd["--output"]).write_text("{}", encoding="utf-8")
            return StageResult(0)
        if module == proposal_run._PROPOSE_MODULE:
            Path(argd["--output"]).write_text(json.dumps(_plan([_candidate()])), encoding="utf-8")
            return StageResult(0)
        if module == proposal_run._RERANK_MODULE:
            return self._rerank(argd)
        if module == proposal_run._EMIT_MODULE:
            emit_proposal(argd["--reranked-plan"], argd["--output"])  # real emit
            return StageResult(0)
        raise AssertionError(f"unexpected module {module}")

    def _decompose(self, argd: dict[str, str]) -> StageResult:
        snap_dir = Path(argd["--artifacts-root"]) / self.SNAPSHOT_ID
        snap_dir.mkdir(parents=True, exist_ok=True)
        (snap_dir / "project-model-v1.json").write_text(
            json.dumps({"schemaVersion": "project-model/v1", "projectGraph": {"nodes": []}}),
            encoding="utf-8",
        )
        (snap_dir / "manifest.json").write_text(
            json.dumps(
                {
                    "snapshot_id": self.SNAPSHOT_ID,
                    "project_model_primary_path": "project-model-v1.json",
                    "project_model_v1_path": "project-model-v1.json",
                    "project_model_v0_path": "project-model-v0.json",
                }
            ),
            encoding="utf-8",
        )
        return StageResult(0, stdout=json.dumps({"snapshot_id": self.SNAPSHOT_ID}))

    def _rerank(self, argd: dict[str, str]) -> StageResult:
        trace_path = Path(argd["--trace"])
        if self.rerank_mode == "ok":
            trace_path.write_text(json.dumps({"preFilter": {"survivorCount": 2}}), encoding="utf-8")
            Path(argd["--output-plan"]).write_text(
                json.dumps(_plan([_candidate(rank=1)])), encoding="utf-8"
            )
            return StageResult(0)
        if self.rerank_mode == "no_survivors":
            trace_path.write_text(
                json.dumps({"preFilter": {"survivorCount": 0, "inputCandidateCount": 3}}),
                encoding="utf-8",
            )
            return StageResult(1, stderr="no candidates survived pre-filter")
        if self.rerank_mode == "crash":
            trace_path.write_text(
                json.dumps({"preFilter": {"survivorCount": 2}}), encoding="utf-8"
            )
            return StageResult(1, stderr="judge exploded")
        if self.rerank_mode == "crash_no_trace":
            return StageResult(1, stderr="died before trace")
        raise AssertionError(f"unknown rerank_mode {self.rerank_mode}")


def _fake_git(record: list[list[str]]) -> proposal_run.GitRunner:
    def _git(args: list[str]) -> None:
        record.append(args)
        # Simulate a successful clone by creating the destination directory.
        if args and args[0] == "clone":
            Path(args[-1]).mkdir(parents=True, exist_ok=True)
    return _git


def _config(repo: Path, output: Path, **overrides: Any) -> RunConfig:
    base: dict[str, Any] = {
        "repo": str(repo),
        "output": output,
        "live_model": "grok-test",
        "workdir": None,
    }
    base.update(overrides)
    return RunConfig(**base)


@pytest.fixture
def repo_dir(tmp_path: Path) -> Path:
    path = tmp_path / "repo"
    path.mkdir()
    return path


@pytest.fixture(autouse=True)
def _key_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("XAI_API_KEY", "sk-test-value")


def test_happy_path_writes_proposal_and_cleans_temp_workdir(
    tmp_path: Path, repo_dir: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    temp_workdir = tmp_path / "temp-wd"

    def _mkdtemp(*_a: Any, **_k: Any) -> str:
        temp_workdir.mkdir()
        return str(temp_workdir)

    monkeypatch.setattr(proposal_run.tempfile, "mkdtemp", _mkdtemp)
    output = tmp_path / "out" / "proposal.md"
    stages = FakeStages()
    rc = run(_config(repo_dir, output), stage_runner=stages.run, git_runner=_fake_git([]))
    assert rc == EXIT_OK
    assert output.is_file()
    text = output.read_text(encoding="utf-8")
    assert text.startswith("# Title for finding-1")
    assert not temp_workdir.exists()  # temp workdir cleaned on success


def test_stage_order_and_v1_resolved_from_manifest(
    tmp_path: Path, repo_dir: Path
) -> None:
    workdir = tmp_path / "wd"
    stages = FakeStages()
    rc = run(
        _config(repo_dir, tmp_path / "proposal.md", workdir=workdir),
        stage_runner=stages.run,
        git_runner=_fake_git([]),
    )
    assert rc == EXIT_OK
    modules = [module for module, _ in stages.calls]
    assert modules == [
        proposal_run._DECOMPOSE_MODULE,
        proposal_run._INTAKE_MODULE,
        proposal_run._PROPOSE_MODULE,
        proposal_run._RERANK_MODULE,
        proposal_run._EMIT_MODULE,
    ]
    expected_v1 = workdir / "snap" / FakeStages.SNAPSHOT_ID / "project-model-v1.json"
    intake_args = dict(stages.calls[1][1])
    rerank_args = dict(stages.calls[3][1])
    assert Path(intake_args["--snapshot"]) == expected_v1
    assert Path(rerank_args["--graph"]) == expected_v1
    assert rerank_args["--allow-live"] == "true"


def test_fail_closed_on_stage_failure(tmp_path: Path, repo_dir: Path) -> None:
    workdir = tmp_path / "wd"
    output = tmp_path / "proposal.md"
    stages = FakeStages(fail={proposal_run._INTAKE_MODULE})
    with pytest.raises(ProposalRunError) as excinfo:
        run(_config(repo_dir, output, workdir=workdir), stage_runner=stages.run, git_runner=_fake_git([]))
    assert excinfo.value.exit_code == EXIT_STAGE_FAILURE
    assert not output.exists()
    assert workdir.exists()  # workdir preserved on failure
    modules = [module for module, _ in stages.calls]
    assert proposal_run._PROPOSE_MODULE not in modules  # stopped before later stages
    assert proposal_run._EMIT_MODULE not in modules


def test_no_proposal_met_bar(
    tmp_path: Path, repo_dir: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    workdir = tmp_path / "wd"
    output = tmp_path / "proposal.md"
    stages = FakeStages(rerank_mode="no_survivors")
    with pytest.raises(ProposalRunError) as excinfo:
        run(_config(repo_dir, output, workdir=workdir), stage_runner=stages.run, git_runner=_fake_git([]))
    assert excinfo.value.exit_code == EXIT_NO_PROPOSAL
    assert excinfo.value.already_reported is True
    out = capsys.readouterr().out
    assert "No proposal met the bar" in out
    assert "3 candidate" in out
    assert str(workdir / "rerank-trace.json") in out
    assert not output.exists()
    assert proposal_run._EMIT_MODULE not in [module for module, _ in stages.calls]


def test_rerank_crash_with_survivors_is_stage_failure(tmp_path: Path, repo_dir: Path) -> None:
    stages = FakeStages(rerank_mode="crash")
    with pytest.raises(ProposalRunError) as excinfo:
        run(
            _config(repo_dir, tmp_path / "proposal.md", workdir=tmp_path / "wd"),
            stage_runner=stages.run,
            git_runner=_fake_git([]),
        )
    assert excinfo.value.exit_code == EXIT_STAGE_FAILURE
    assert proposal_run._EMIT_MODULE not in [module for module, _ in stages.calls]


def test_rerank_crash_without_trace_is_stage_failure(tmp_path: Path, repo_dir: Path) -> None:
    stages = FakeStages(rerank_mode="crash_no_trace")
    with pytest.raises(ProposalRunError) as excinfo:
        run(
            _config(repo_dir, tmp_path / "proposal.md", workdir=tmp_path / "wd"),
            stage_runner=stages.run,
            git_runner=_fake_git([]),
        )
    assert excinfo.value.exit_code == EXIT_STAGE_FAILURE


def test_resolve_target_local_dir_used_in_place(tmp_path: Path, repo_dir: Path) -> None:
    record: list[list[str]] = []
    resolved = resolve_target(str(repo_dir), tmp_path / "wd", _fake_git(record))
    assert resolved == repo_dir.resolve()
    assert record == []  # no clone for a local path


def test_resolve_target_git_url_clones(tmp_path: Path) -> None:
    record: list[list[str]] = []
    workdir = tmp_path / "wd"
    workdir.mkdir()
    url = "https://github.com/example/repo.git"
    resolved = resolve_target(url, workdir, _fake_git(record))
    assert resolved == (workdir / "target").resolve()
    assert record[0][:3] == ["clone", "--depth", "1"]
    assert record[0][3] == url


def test_resolve_target_rejects_non_repo(tmp_path: Path) -> None:
    with pytest.raises(ProposalRunError) as excinfo:
        resolve_target("not-a-real-thing", tmp_path / "wd", _fake_git([]))
    assert excinfo.value.exit_code == EXIT_USAGE


def test_preflight_requires_live_model(tmp_path: Path, repo_dir: Path) -> None:
    stages = FakeStages()
    with pytest.raises(ProposalRunError) as excinfo:
        run(
            _config(repo_dir, tmp_path / "proposal.md", live_model=None),
            stage_runner=stages.run,
            git_runner=_fake_git([]),
        )
    assert excinfo.value.exit_code == EXIT_USAGE
    assert stages.calls == []  # failed before any stage ran


def test_preflight_missing_key_is_usage_error(
    tmp_path: Path, repo_dir: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def _raise(_env: str) -> Any:
        raise ValueError("missing key")

    monkeypatch.setattr(proposal_run, "resolve_api_key_with_source", _raise)
    stages = FakeStages()
    with pytest.raises(ProposalRunError) as excinfo:
        run(_config(repo_dir, tmp_path / "proposal.md"), stage_runner=stages.run, git_runner=_fake_git([]))
    assert excinfo.value.exit_code == EXIT_USAGE
    assert stages.calls == []


def test_keep_workdir_retains_temp_on_success(
    tmp_path: Path, repo_dir: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    temp_workdir = tmp_path / "temp-wd"

    def _mkdtemp(*_a: Any, **_k: Any) -> str:
        temp_workdir.mkdir()
        return str(temp_workdir)

    monkeypatch.setattr(proposal_run.tempfile, "mkdtemp", _mkdtemp)
    stages = FakeStages()
    rc = run(
        _config(repo_dir, tmp_path / "proposal.md", keep_workdir=True),
        stage_runner=stages.run,
        git_runner=_fake_git([]),
    )
    assert rc == EXIT_OK
    assert temp_workdir.exists()  # retained because keep_workdir


def test_subprocess_env_threads_judge_vars() -> None:
    config = _config(
        Path("/tmp/repo"),
        Path("/tmp/proposal.md"),
        live_model="grok-x",
        live_base_url="https://api.example/v1",
        live_api_key_env="MY_KEY",
    )
    env = _subprocess_env(config)
    assert env["BUILD_ARENA_LLM_MODEL"] == "grok-x"
    assert env["BUILD_ARENA_LLM_BASE_URL"] == "https://api.example/v1"
    assert env["BUILD_ARENA_LLM_API_KEY_ENV"] == "MY_KEY"
    assert str(proposal_run._REPO_ROOT) in env["PYTHONPATH"]


def test_decompose_fixture_mode_omits_live_flags(repo_dir: Path) -> None:
    config = _config(repo_dir, Path("/tmp/proposal.md"))
    args = _decompose_args(config, repo_dir, repo_dir / "snap")
    assert "--llm-mode" in args and args[args.index("--llm-mode") + 1] == "fixture"
    assert "--allow-live" not in args


def test_decompose_live_mode_includes_flags(repo_dir: Path) -> None:
    config = _config(repo_dir, Path("/tmp/proposal.md"), decompose_live=True)
    args = _decompose_args(config, repo_dir, repo_dir / "snap")
    assert args[args.index("--llm-mode") + 1] == "live"
    assert "--allow-live" in args
    assert args[args.index("--live-model") + 1] == "grok-test"


def test_main_run_builds_config_and_returns_code(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, RunConfig] = {}

    def _fake_run(config: RunConfig, **_kw: Any) -> int:
        captured["config"] = config
        return EXIT_OK

    monkeypatch.setattr(proposal_run, "run", _fake_run)
    rc = main(["run", "/some/repo", "--live-model", "grok-9"])
    assert rc == EXIT_OK
    config = captured["config"]
    assert config.repo == "/some/repo"
    assert config.live_model == "grok-9"
    assert config.profile == "new-project"
    assert config.max_candidates == 10
    assert config.output.is_absolute()


def test_main_maps_no_proposal_exit(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    def _fake_run(_config: RunConfig, **_kw: Any) -> int:
        raise ProposalRunError("", EXIT_NO_PROPOSAL, already_reported=True)

    monkeypatch.setattr(proposal_run, "run", _fake_run)
    rc = main(["run", "/some/repo", "--live-model", "m"])
    assert rc == EXIT_NO_PROPOSAL
    assert capsys.readouterr().err == ""  # already reported; main stays quiet


def test_main_maps_stage_failure_exit(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    def _fake_run(_config: RunConfig, **_kw: Any) -> int:
        raise ProposalRunError("boom happened", EXIT_STAGE_FAILURE)

    monkeypatch.setattr(proposal_run, "run", _fake_run)
    rc = main(["run", "/some/repo", "--live-model", "m"])
    assert rc == EXIT_STAGE_FAILURE
    assert "boom happened" in capsys.readouterr().err


def test_missing_subcommand_exits_via_argparse() -> None:
    # The subparser is required, so argparse rejects a bare invocation before main() dispatches.
    with pytest.raises(SystemExit) as excinfo:
        main([])
    assert excinfo.value.code == 2


def test_unknown_subcommand_exits_via_argparse() -> None:
    with pytest.raises(SystemExit) as excinfo:
        main(["does-not-exist"])
    assert excinfo.value.code == 2
