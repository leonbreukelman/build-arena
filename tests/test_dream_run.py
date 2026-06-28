from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from arena import dream_run
from arena.capability_lift import build_capability_map
from arena.dream_emit import emit_dream
from arena.dream_gate import anchor_content_hash, write_gated_dreams
from arena.dream_run import (
    EXIT_NO_DREAM,
    EXIT_OK,
    EXIT_STAGE_FAILURE,
    EXIT_USAGE,
    DreamRunError,
    RunConfig,
    StageResult,
    _subprocess_env,
    main,
    run,
)

GRAPH_HASH = "7" * 64


def _argd(args: list[str]) -> dict[str, str]:
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


def _model() -> dict[str, Any]:
    return {
        "id": "model-1",
        "project": {"projectId": "fixture-project"},
        "snapshot": {
            "project_id": "fixture-project",
            "graph_hash": GRAPH_HASH,
            "components": [
                {
                    "id": "comp.runner",
                    "name": "Runner",
                    "responsibility": "Run dream stages",
                    "owned_node_ids": ["node.runner"],
                    "provenance_refs": ["prov:runner"],
                    "contract_ids": [],
                    "check_ids": [],
                    "verification_gap_ids": ["gap.dream-runner"],
                }
            ],
            "contracts": [],
            "verification_gaps": [
                {
                    "id": "gap.dream-runner",
                    "description": "dream runner stage behavior lacks a direct observable check",
                    "severity": "medium",
                    "component_ids": ["comp.runner"],
                    "contract_ids": [],
                    "provenance_refs": ["prov:runner"],
                    "proposed_closure_check": "add stage-order tests",
                }
            ],
            "near_neighbor_alternatives": [],
        },
        "projectGraph": {"graphHash": GRAPH_HASH, "nodes": [{"id": "node.runner", "path": "arena/dream_run.py"}], "edges": []},
        "iterationReadiness": {
            "componentProfiles": [
                {
                    "componentId": "comp.runner",
                    "ownedNodeIds": ["node.runner"],
                    "responsibilitySummary": "dream stage orchestration",
                    "behavioralTags": ["dream"],
                    "provenanceRefs": ["prov:profile"],
                }
            ],
            "qualityGates": [{"command": "uv run pytest tests -q"}],
        },
    }


class FakeStages:
    SNAPSHOT_ID = "snap-1"

    def __init__(self, *, reviewed: bool = True, gate_mode: str = "ok", fail: set[str] | None = None) -> None:
        self.reviewed = reviewed
        self.gate_mode = gate_mode
        self.fail = fail or set()
        self.calls: list[tuple[str, dict[str, str]]] = []

    def run(self, module: str, args: list[str], _env: dict[str, str]) -> StageResult:
        argd = _argd(args)
        self.calls.append((module, argd))
        if module in self.fail:
            return StageResult(1, stderr=f"{module} forced failure")
        if module == dream_run._DECOMPOSE_MODULE:
            return self._decompose(argd)
        if module == dream_run._INTAKE_MODULE:
            Path(argd["--output"]).write_text(json.dumps({"findings": []}), encoding="utf-8")
            return StageResult(0)
        if module == dream_run._CAPABILITY_MODULE:
            return self._capability(argd)
        if module == dream_run._GENERATE_MODULE:
            return self._dreams(argd, bad=False)
        if module == dream_run._RESEARCH_MODULE:
            return self._dreams(argd, bad=self.gate_mode == "no_survivors")
        if module == dream_run._GATE_MODULE:
            return self._gate(argd)
        if module == dream_run._EMIT_MODULE:
            emit_dream(argd["--dreams"], argd["--output"])
            return StageResult(0)
        raise AssertionError(f"unexpected module {module}")

    def _decompose(self, argd: dict[str, str]) -> StageResult:
        snap_dir = Path(argd["--artifacts-root"]) / self.SNAPSHOT_ID
        snap_dir.mkdir(parents=True, exist_ok=True)
        (snap_dir / "project-model-v1.json").write_text(json.dumps(_model()), encoding="utf-8")
        (snap_dir / "manifest.json").write_text(
            json.dumps({"snapshot_id": self.SNAPSHOT_ID, "project_model_primary_path": "project-model-v1.json"}),
            encoding="utf-8",
        )
        return StageResult(0)

    def _capability(self, argd: dict[str, str]) -> StageResult:
        cap_map = build_capability_map(argd["--project-model"])
        cap_map["review"]["reviewed"] = self.reviewed
        Path(argd["--output"]).write_text(json.dumps(cap_map), encoding="utf-8")
        return StageResult(0)

    def _dreams(self, argd: dict[str, str], *, bad: bool) -> StageResult:
        model = json.loads(Path(argd["--project-model"]).read_text(encoding="utf-8"))
        cap_map = json.loads(Path(argd["--capability-map"]).read_text(encoding="utf-8"))
        gap = model["snapshot"]["verification_gaps"][0]
        capability_id = cap_map["capabilities"][0]["id"]
        anchor_id = "gap.fabricated" if bad else "gap.dream-runner"
        document = {
            "dreams": [
                {
                    "id": "dream.runner",
                    "mode": "carrier_swap",
                    "idea": "Consider an injected dream stage seam.",
                    "targetCapabilityIds": [capability_id],
                    "citedEvidence": [
                        {
                            "anchorKind": "verificationGap",
                            "anchorId": anchor_id,
                            "contentHash": anchor_content_hash(gap),
                            "claim": "Runner dream orchestration has no direct behavior check.",
                        }
                    ],
                    "currentStructure": {"fromCarrier": "subprocess dream stage calls"},
                    "proposedStructure": {"toCarrier": "injected dream stage seam"},
                    "rationale": "The dream targets the current orchestration carrier specifically.",
                    "premiseConfidence": "unresolved",
                    "conclusionConfidence": {"band": "medium", "value": 0.5},
                    "validationRecipe": {"action": "try seam", "observable": "stage tests", "expectedDirection": "increase"},
                }
            ],
            "provenance": {"generatedBy": "arena.dream_generate", "researchedBy": "arena.dream_research", "modelId": "fake", "promptHashes": {"fake": "8" * 64}, "inputHashes": {}},
        }
        Path(argd["--output"]).write_text(json.dumps(document), encoding="utf-8")
        return StageResult(0)

    def _gate(self, argd: dict[str, str]) -> StageResult:
        result = write_gated_dreams(
            project_model_path=argd["--project-model"],
            capability_map_path=argd["--capability-map"],
            dreams_path=argd["--dreams"],
            output_path=argd["--output"],
            trace_path=argd["--trace"],
        )
        return StageResult(EXIT_NO_DREAM if result.accepted_count == 0 else 0)


def _fake_git(_record: list[list[str]]) -> dream_run.GitRunner:
    def _git(args: list[str]) -> None:
        _record.append(args)
        if args and args[0] == "clone":
            Path(args[-1]).mkdir(parents=True, exist_ok=True)

    return _git


def _config(repo: Path, output: Path, **overrides: Any) -> RunConfig:
    values: dict[str, Any] = {"repo": str(repo), "output": output, "live_model": "grok-test"}
    values.update(overrides)
    return RunConfig(**values)


@pytest.fixture
def repo_dir(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    return repo


@pytest.fixture(autouse=True)
def _key_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("XAI_API_KEY", "test-key")


def test_happy_path_writes_dream_and_cleans_temp_workdir(tmp_path: Path, repo_dir: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    temp_workdir = tmp_path / "temp-wd"

    def _mkdtemp(*_a: Any, **_k: Any) -> str:
        temp_workdir.mkdir()
        return str(temp_workdir)

    monkeypatch.setattr(dream_run.tempfile, "mkdtemp", _mkdtemp)
    output = tmp_path / "out" / "experiment.md"
    stages = FakeStages()

    rc = run(_config(repo_dir, output), stage_runner=stages.run, git_runner=_fake_git([]))

    assert rc == EXIT_OK
    assert output.is_file()
    assert "Consider an injected dream stage seam" in output.read_text(encoding="utf-8")
    assert not temp_workdir.exists()


def test_stage_order_and_manifest_driven_v1_resolution(tmp_path: Path, repo_dir: Path) -> None:
    workdir = tmp_path / "wd"
    stages = FakeStages()
    rc = run(_config(repo_dir, tmp_path / "experiment.md", workdir=workdir), stage_runner=stages.run, git_runner=_fake_git([]))

    assert rc == EXIT_OK
    assert [module for module, _args in stages.calls] == [
        dream_run._DECOMPOSE_MODULE,
        dream_run._INTAKE_MODULE,
        dream_run._CAPABILITY_MODULE,
        dream_run._GENERATE_MODULE,
        dream_run._RESEARCH_MODULE,
        dream_run._GATE_MODULE,
        dream_run._EMIT_MODULE,
    ]
    expected_v1 = workdir / "snap" / FakeStages.SNAPSHOT_ID / "project-model-v1.json"
    assert Path(stages.calls[1][1]["--snapshot"]) == expected_v1
    assert Path(stages.calls[2][1]["--project-model"]) == expected_v1
    assert Path(stages.calls[3][1]["--project-model"]) == expected_v1


def test_fail_closed_on_stage_failure_preserves_workdir(tmp_path: Path, repo_dir: Path) -> None:
    workdir = tmp_path / "wd"
    output = tmp_path / "experiment.md"
    stages = FakeStages(fail={dream_run._RESEARCH_MODULE})
    with pytest.raises(DreamRunError) as excinfo:
        run(_config(repo_dir, output, workdir=workdir), stage_runner=stages.run, git_runner=_fake_git([]))

    assert excinfo.value.exit_code == EXIT_STAGE_FAILURE
    assert workdir.exists()
    assert not output.exists()
    assert dream_run._GATE_MODULE not in [module for module, _args in stages.calls]


def test_unreviewed_capability_map_runs_to_output(tmp_path: Path, repo_dir: Path) -> None:
    output = tmp_path / "experiment.md"
    stages = FakeStages(reviewed=False)
    rc = run(_config(repo_dir, output, workdir=tmp_path / "wd"), stage_runner=stages.run, git_runner=_fake_git([]))

    assert rc == EXIT_OK
    assert output.is_file()
    text = output.read_text(encoding="utf-8")
    assert text.strip()
    assert text.startswith("# Experiment Proposals")
    assert "auto-generated, operator-unreviewed capability map" in text
    modules = [module for module, _args in stages.calls]
    assert modules == [
        dream_run._DECOMPOSE_MODULE,
        dream_run._INTAKE_MODULE,
        dream_run._CAPABILITY_MODULE,
        dream_run._GENERATE_MODULE,
        dream_run._RESEARCH_MODULE,
        dream_run._GATE_MODULE,
        dream_run._EMIT_MODULE,
    ]


def test_no_dream_survived_gate_exits_two(tmp_path: Path, repo_dir: Path, capsys: pytest.CaptureFixture[str]) -> None:
    stages = FakeStages(gate_mode="no_survivors")
    output = tmp_path / "experiment.md"
    with pytest.raises(DreamRunError) as excinfo:
        run(_config(repo_dir, output, workdir=tmp_path / "wd"), stage_runner=stages.run, git_runner=_fake_git([]))

    assert excinfo.value.exit_code == EXIT_NO_DREAM
    assert excinfo.value.already_reported is True
    assert "No dream survived" in capsys.readouterr().out
    assert not output.exists()
    assert dream_run._EMIT_MODULE not in [module for module, _args in stages.calls]


def test_preflight_requires_live_model(tmp_path: Path, repo_dir: Path) -> None:
    stages = FakeStages()
    with pytest.raises(DreamRunError) as excinfo:
        run(_config(repo_dir, tmp_path / "experiment.md", live_model=None), stage_runner=stages.run, git_runner=_fake_git([]))

    assert excinfo.value.exit_code == EXIT_USAGE
    assert stages.calls == []


def test_preflight_missing_key_is_usage_error(tmp_path: Path, repo_dir: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    def _raise(_env: str) -> Any:
        raise ValueError("missing key")

    monkeypatch.setattr(dream_run, "resolve_api_key_with_source", _raise)
    stages = FakeStages()
    with pytest.raises(DreamRunError) as excinfo:
        run(_config(repo_dir, tmp_path / "experiment.md"), stage_runner=stages.run, git_runner=_fake_git([]))

    assert excinfo.value.exit_code == EXIT_USAGE
    assert stages.calls == []


def test_subprocess_env_threads_live_model_settings() -> None:
    env = _subprocess_env(
        RunConfig(
            repo="/tmp/repo",
            output=Path("/tmp/experiment.md"),
            live_model="grok-x",
            live_base_url="https://api.example/v1",
            live_api_key_env="MY_KEY",
        )
    )
    assert env["BUILD_ARENA_LLM_MODEL"] == "grok-x"
    assert env["BUILD_ARENA_LLM_BASE_URL"] == "https://api.example/v1"
    assert env["BUILD_ARENA_LLM_API_KEY_ENV"] == "MY_KEY"
    assert str(dream_run._REPO_ROOT) in env["PYTHONPATH"]


def test_main_maps_errors(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    def _fake_run(_config: RunConfig, **_kw: Any) -> int:
        raise DreamRunError("boom", EXIT_STAGE_FAILURE)

    monkeypatch.setattr(dream_run, "run", _fake_run)
    rc = main(["run", "/repo", "--live-model", "m"])
    assert rc == EXIT_STAGE_FAILURE
    assert "boom" in capsys.readouterr().err
