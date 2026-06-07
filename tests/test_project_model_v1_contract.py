from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from arena.project_decomposer_ai import build_project_model_snapshot
from arena.project_model_v1 import project_model_v1_from_snapshot

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "docs" / "schemas" / "project-model-v1.schema.json"


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def test_project_model_v1_schema_validates_ai_decomposer_primary_artifact(tmp_path: Path) -> None:
    project = tmp_path / "repo"
    _write_tiny_repo(project)
    artifacts = tmp_path / "artifacts"

    result = build_project_model_snapshot(
        project,
        artifacts,
        project_id="tiny-v1",
        goal="decompose tiny repo",
        non_goals=["no buckets"],
        llm_mode="fixture",
    )

    v1_path = result.snapshot_dir / "project-model-v1.json"
    v0_path = result.snapshot_dir / "project-model-v0.json"
    assert result.manifest["project_model_primary_path"] == "project-model-v1.json"
    assert result.manifest["project_model_v1_path"] == "project-model-v1.json"
    assert result.manifest["project_model_v0_path"] == "project-model-v0.json"
    assert v1_path.exists()
    assert v0_path.exists()

    schema = _load_json(SCHEMA_PATH)
    v1 = _load_json(v1_path)
    errors = sorted(Draft202012Validator(schema).iter_errors(v1), key=lambda error: list(error.path))
    assert errors == []
    assert v1["schemaVersion"] == "project-model/v1"
    assert v1["id"] == result.snapshot.snapshot_id
    assert v1["projectGraph"]["graphHash"] == result.snapshot.graph_hash
    assert v1["snapshot"]["schema_version"] == "project-model-snapshot/v0.1"
    assert v1["gateReport"]["passed"] is True
    assert v1["compatibility"]["projectModelV0Path"] == "project-model-v0.json"
    assert v1["hashes"]["inputHashes"]["graph"] == result.snapshot.graph_hash
    assert v1["models"]["primary"] == result.snapshot.primary_model_id
    assert {artifact["artifactType"] for artifact in v1["derivedArtifacts"]} >= {"jsonl-events", "sqlite-projection", "markdown-summary"}

    iteration = v1["iterationReadiness"]
    assert {"componentProfiles", "runtimeContracts", "externalSurfaces", "productInvariants", "qualityGates", "priorityBacklog", "openQuestions"} <= set(iteration)
    assert iteration["componentProfiles"]
    assert all("own the responsibility represented by" not in profile["responsibilitySummary"].lower() for profile in iteration["componentProfiles"])

    legacy_without_iteration = dict(v1)
    legacy_without_iteration.pop("iterationReadiness")
    legacy_errors = sorted(Draft202012Validator(schema).iter_errors(legacy_without_iteration), key=lambda error: list(error.path))
    assert legacy_errors == []


def test_project_model_v1_schema_rejects_legacy_v0_shape() -> None:
    schema = _load_json(SCHEMA_PATH)
    legacy_shape = {
        "schemaVersion": "project-model/v0",
        "id": "legacy",
        "components": [],
        "observableChecks": [],
    }

    errors = list(Draft202012Validator(schema).iter_errors(legacy_shape))

    assert errors
    assert any(error.validator == "const" for error in errors)


def test_project_model_v1_from_snapshot_requires_gate_report_and_graph_context(tmp_path: Path) -> None:
    project = tmp_path / "repo"
    _write_tiny_repo(project)
    result = build_project_model_snapshot(
        project,
        tmp_path / "artifacts",
        project_id="tiny-v1-builder",
        goal="decompose tiny repo",
        non_goals=["no buckets"],
        llm_mode="fixture",
    )

    v1 = project_model_v1_from_snapshot(
        result.snapshot,
        result.graph,
        result.gate_report,
        artifact_hashes=result.manifest["artifact_hashes"],
        compatibility_v0_path="project-model-v0.json",
    )

    assert v1["projectGraph"]["nodes"]
    assert v1["projectGraph"]["edges"]
    assert v1["gateReport"]["passed"] is True
    assert v1["provenance"]["git"]["headOid"]
    assert v1["provenance"]["git"]["dirtyStateFingerprint"]


def _write_tiny_repo(project: Path) -> None:
    (project / "pkg").mkdir(parents=True)
    (project / "tests").mkdir()
    (project / "pkg/core.py").write_text("def add_one(value: int) -> int:\n    return value + 1\n", encoding="utf-8")
    (project / "tests/test_core.py").write_text(
        "from pkg.core import add_one\n\ndef test_add_one():\n    assert add_one(1) == 2\n",
        encoding="utf-8",
    )
    (project / "pyproject.toml").write_text("[project]\nname = \"tiny-v1\"\nversion = \"0.1.0\"\n", encoding="utf-8")
    subprocess.run(["git", "init", "-b", "main"], cwd=project, check=True, stdout=subprocess.DEVNULL)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=project, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=project, check=True)
    subprocess.run(["git", "add", "."], cwd=project, check=True)
    subprocess.run(["git", "commit", "-m", "initial"], cwd=project, check=True, stdout=subprocess.DEVNULL)
