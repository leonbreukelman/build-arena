from __future__ import annotations

import json
import subprocess
from pathlib import Path

from arena.project_decomposer_ai import build_project_model_snapshot


def _run(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=cwd, text=True, capture_output=True, check=True)


def _init_repo(root: Path) -> None:
    _run(["git", "init", "-b", "main"], root)
    _run(["git", "config", "user.email", "arena@example.invalid"], root)
    _run(["git", "config", "user.name", "Arena Tests"], root)
    _run(["git", "add", "."], root)
    _run(["git", "commit", "-m", "baseline"], root)


def _write_repo(root: Path) -> None:
    (root / "pkg").mkdir()
    (root / "tests").mkdir()
    (root / "schema").mkdir()
    (root / "arena" / "generated").mkdir(parents=True)
    (root / "pkg" / "__init__.py").write_text("", encoding="utf-8")
    (root / "pkg" / "core.py").write_text("from pkg.worker import work\n\ndef run() -> int:\n    return work()\n", encoding="utf-8")
    (root / "pkg" / "worker.py").write_text("def work() -> int:\n    return 1\n", encoding="utf-8")
    (root / "tests" / "test_core.py").write_text("from pkg.core import run\n\ndef test_run():\n    assert run() == 1\n", encoding="utf-8")
    (root / "schema" / "model.yaml").write_text("name: protected\n", encoding="utf-8")
    (root / "arena" / "generated" / "models.py").write_text("# generated\n", encoding="utf-8")
    (root / "pyproject.toml").write_text("[project]\nname='api-project'\nversion='0.0.0'\n", encoding="utf-8")
    _init_repo(root)


def test_build_project_model_snapshot_writes_sidecars_and_v0_projection(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _write_repo(repo)
    artifacts = tmp_path / "artifacts"

    result = build_project_model_snapshot(
        repo,
        artifacts,
        project_id="api-project",
        goal="decompose this repository into responsibility-bearing components",
        non_goals=["do not treat file buckets as final components"],
        llm_mode="fixture",
        overwrite=True,
    )

    assert result.gate_report.passed is True
    assert result.manifest_path.exists()
    manifest = json.loads(result.manifest_path.read_text(encoding="utf-8"))
    assert manifest["schema_version"] == "project-model-snapshot/v0.1"
    assert manifest["goal"]
    assert manifest["non_goals"]
    for rel in [
        "graph.json",
        "encyclopedia/manifest.json",
        "snapshot.json",
        "gate-report.json",
        "project-model-v0.json",
        "prompts/decomposer-prompt.txt",
        "model-outputs/decomposer.raw.json",
        "model-outputs/skeptic-review.raw.json",
        "held-out-probes.json",
        "planted-negatives.json",
        "near-neighbor-alternatives.json",
        "acceptance-command-allowlist.json",
    ]:
        assert (result.snapshot_dir / rel).exists(), rel
    v0 = json.loads((result.snapshot_dir / "project-model-v0.json").read_text(encoding="utf-8"))
    assert v0["schemaVersion"] == "project-model/v0"
    assert v0["id"] == "api-project"
    assert result.snapshot.contracts
    graph_node_by_id = {node.id: node for node in result.graph.nodes}
    assert all(
        not any(tag in graph_node_by_id[node_id].tags for tag in {"protected", "generated"})
        for component in result.snapshot.components
        for node_id in component.owned_node_ids
    )


def test_build_project_model_snapshot_requires_overwrite_for_existing_snapshot_dir(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _write_repo(repo)
    artifacts = tmp_path / "artifacts"
    build_project_model_snapshot(repo, artifacts, project_id="api-project", llm_mode="fixture", overwrite=True)

    try:
        build_project_model_snapshot(repo, artifacts, project_id="api-project", llm_mode="fixture", overwrite=False)
    except FileExistsError as exc:
        assert "pass overwrite" in str(exc)
    else:
        raise AssertionError("expected existing deterministic snapshot directory to require overwrite=True")


def test_decomposer_rebuilds_from_filesystem_truth_each_run(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _write_repo(repo)
    artifacts = tmp_path / "artifacts"
    first = build_project_model_snapshot(repo, artifacts, project_id="api-project", llm_mode="fixture", overwrite=True)
    (repo / "pkg" / "worker.py").write_text("def work() -> int:\n    return 2\n", encoding="utf-8")

    second = build_project_model_snapshot(repo, artifacts, project_id="api-project", llm_mode="fixture", overwrite=True)

    assert first.manifest["graph_hash"] != second.manifest["graph_hash"]
    assert second.manifest["dirty_state"]["dirty"] is True
    assert "pkg/worker.py" in second.manifest["dirty_state"]["dirty_paths"]


def test_recorded_model_output_uses_same_ingestion_path_and_bad_bucket_is_rejected(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _write_repo(repo)
    artifacts = tmp_path / "artifacts"
    fixture = build_project_model_snapshot(repo, artifacts, project_id="api-project", llm_mode="fixture", overwrite=True)
    raw = json.loads((fixture.snapshot_dir / "model-outputs" / "decomposer.raw.json").read_text(encoding="utf-8"))
    recorded_path = tmp_path / "recorded-good.json"
    recorded_path.write_text(json.dumps(raw, indent=2), encoding="utf-8")

    recorded = build_project_model_snapshot(repo, artifacts, project_id="api-project", llm_mode="recorded", model_output_path=recorded_path, overwrite=True)
    assert recorded.gate_report.passed is True
    assert recorded.snapshot.primary_model_id == raw["model_id"]

    bad = raw.copy()
    bad["model_id"] = "recorded-fluent-bucket-model"
    file_nodes = [node for node in fixture.graph.nodes if node.path in {"pkg/core.py", "pkg/worker.py"} and node.kind == "file"]
    bad["components"][0]["name"] = "Runtime Coordination Surface"
    bad["components"][0]["owned_node_ids"] = [node.id for node in file_nodes]
    bad_path = tmp_path / "recorded-bad.json"
    bad_path.write_text(json.dumps(bad, indent=2), encoding="utf-8")

    rejected = build_project_model_snapshot(repo, artifacts, project_id="api-project", llm_mode="recorded", model_output_path=bad_path, overwrite=True)
    assert rejected.gate_report.passed is False
    assert any(v.gate == "component_measurability" for v in rejected.gate_report.violations)


def test_fixture_decomposer_handles_javascript_import_contracts(tmp_path: Path) -> None:
    repo = tmp_path / "js-repo"
    repo.mkdir()
    (repo / "worker" / "mcp").mkdir(parents=True)
    (repo / "worker" / "index.js").write_text(
        "import { handleMcpRequest } from './mcp/server.js';\n\nexport default { async fetch(request) { return handleMcpRequest(request); } };\n",
        encoding="utf-8",
    )
    (repo / "worker" / "mcp" / "server.js").write_text(
        "export async function handleMcpRequest(request) { return request; }\n",
        encoding="utf-8",
    )
    (repo / "dist").mkdir()
    (repo / "dist" / "worker.js").write_text("function bundled() { return 1; }\n", encoding="utf-8")
    (repo / "package.json").write_text('{"name":"js-repo","type":"module"}\n', encoding="utf-8")
    _init_repo(repo)

    result = build_project_model_snapshot(
        repo,
        tmp_path / "artifacts",
        project_id="js-repo",
        goal="decompose a JavaScript worker project",
        non_goals=["do not accept bundled output as source ownership"],
        llm_mode="fixture",
        overwrite=True,
    )
    node_by_id = {node.id: node for node in result.graph.nodes}
    owned_symbols = [node_by_id[node_id].symbol for component in result.snapshot.components for node_id in component.owned_node_ids]

    assert result.gate_report.passed is True
    assert "worker" in owned_symbols
    assert "worker.mcp.server" in owned_symbols
    assert result.snapshot.contracts
    assert not any(symbol == "dist.worker" for symbol in owned_symbols)
