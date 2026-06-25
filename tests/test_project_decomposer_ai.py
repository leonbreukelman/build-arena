from __future__ import annotations

import json
import subprocess
from pathlib import Path

from arena.project_decomposer_ai import _decomposer_prompt, build_project_model_snapshot
from arena.project_graph import build_project_graph, graph_to_dict
from arena.project_model_gate import close_import_contracts_for_gate, run_project_model_gate
from arena.project_snapshot import Component, ProjectModelSnapshot, snapshot_to_dict


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
    assert result.snapshot.observable_checks[0].command == "uv run python -m pytest -q"
    assert "local-pytest" in result.snapshot.acceptance_command_allowlist
    assert "uv run python -m pytest -q" in result.snapshot.acceptance_command_allowlist
    graph_node_by_id = {node.id: node for node in result.graph.nodes}
    assert all(
        not any(tag in graph_node_by_id[node_id].tags for tag in {"protected", "generated"})
        for component in result.snapshot.components
        for node_id in component.owned_node_ids
    )


def test_build_project_model_snapshot_can_run_real_adversarial_probe(tmp_path: Path) -> None:
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
        run_adversarial_probes=True,
    )

    assert result.gate_report.passed is True
    assert len(result.snapshot.held_out_probes) == 1
    probe = result.snapshot.held_out_probes[0]
    assert probe.golden_control_passed is True
    assert probe.discrimination_passed is True
    assert probe.proof_artifact == "proofs/probe.path-bucket-contract-discrimination.json"
    assert probe.verification_gap_ids == []
    assert (result.snapshot_dir / probe.proof_artifact).exists()
    planted_negatives = json.loads((result.snapshot_dir / "planted-negatives.json").read_text(encoding="utf-8"))
    assert planted_negatives[0]["id"] == probe.planted_negative_id
    assert planted_negatives[0]["snapshot_hash"]
    assert any(gap.id == "gap.semantic-understanding-not-independently-validated" for gap in result.snapshot.verification_gaps)


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


def test_recorded_model_output_repairs_universal_concern_category_from_exact_id(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _write_repo(repo)
    artifacts = tmp_path / "artifacts"
    fixture = build_project_model_snapshot(
        repo,
        artifacts,
        project_id="api-project",
        llm_mode="fixture",
        overwrite=True,
    )
    raw = json.loads(
        (fixture.snapshot_dir / "model-outputs" / "decomposer.raw.json").read_text(
            encoding="utf-8"
        )
    )
    thematic_categories = {
        "anti_fabrication": "integrity",
        "determinism": "reliability",
        "provenance": "traceability",
        "no_live_paid_api_acceptance": "compliance",
    }
    for concern in raw["cross_cutting_concerns"]:
        canonical = concern["category"]
        if canonical in thematic_categories:
            concern["id"] = canonical
            concern["category"] = thematic_categories[canonical]
    raw["model_id"] = "recorded-universal-concern-id-category-drift"
    recorded_path = tmp_path / "recorded-concern-drift.json"
    recorded_path.write_text(json.dumps(raw, indent=2), encoding="utf-8")

    result = build_project_model_snapshot(
        repo,
        artifacts,
        project_id="api-project",
        llm_mode="recorded",
        model_output_path=recorded_path,
        overwrite=True,
    )

    assert result.gate_report.passed is True
    categories = {concern.category for concern in result.snapshot.cross_cutting_concerns}
    assert set(thematic_categories) <= categories
    assert categories.isdisjoint(thematic_categories.values())
    persisted_raw = json.loads(
        (result.snapshot_dir / "model-outputs" / "decomposer.raw.json").read_text(
            encoding="utf-8"
        )
    )
    persisted_themes = {
        concern["category"]
        for concern in persisted_raw["cross_cutting_concerns"]
        if concern["id"] in thematic_categories
    }
    assert persisted_themes == set(thematic_categories.values())


def test_recorded_model_output_does_not_repair_unknown_concern_category(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _write_repo(repo)
    artifacts = tmp_path / "artifacts"
    fixture = build_project_model_snapshot(
        repo,
        artifacts,
        project_id="api-project",
        llm_mode="fixture",
        overwrite=True,
    )
    raw = json.loads(
        (fixture.snapshot_dir / "model-outputs" / "decomposer.raw.json").read_text(
            encoding="utf-8"
        )
    )
    for concern in raw["cross_cutting_concerns"]:
        if concern["category"] == "anti_fabrication":
            concern["id"] = "integrity-envelope"
            concern["category"] = "integrity"
            break
    raw["model_id"] = "recorded-unknown-concern-category"
    recorded_path = tmp_path / "recorded-unknown-concern.json"
    recorded_path.write_text(json.dumps(raw, indent=2), encoding="utf-8")

    result = build_project_model_snapshot(
        repo,
        artifacts,
        project_id="api-project",
        llm_mode="recorded",
        model_output_path=recorded_path,
        overwrite=True,
    )

    assert result.gate_report.passed is False
    assert any(
        violation.gate == "cross_cutting_concerns"
        and "Missing universal concerns" in violation.message
        and "anti_fabrication" in violation.message
        for violation in result.gate_report.violations
    )


def test_live_decomposer_prompt_makes_universal_concern_categories_non_negotiable(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _write_repo(repo)
    graph = build_project_graph(repo)

    prompt = _decomposer_prompt(
        project_id="api-project",
        goal="decompose this repository into responsibility-bearing components",
        non_goals=["do not treat file buckets as final components"],
        graph=graph,
    )

    assert "category MUST be exactly one of" in prompt
    assert '"category": "anti_fabrication"' in prompt
    assert "Do not use thematic labels such as integrity" in prompt


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


def test_fixture_decomposer_covers_every_owned_cross_component_import_edge(tmp_path: Path) -> None:
    repo = tmp_path / "multi-contract-repo"
    repo.mkdir()
    (repo / "pkg").mkdir()
    (repo / "tests").mkdir()
    (repo / "pkg" / "__init__.py").write_text("", encoding="utf-8")
    (repo / "pkg" / "config.py").write_text("VALUE = 1\n", encoding="utf-8")
    (repo / "pkg" / "client.py").write_text(
        "from pkg.config import VALUE\n\ndef fetch() -> int:\n    return VALUE\n",
        encoding="utf-8",
    )
    (repo / "pkg" / "server.py").write_text(
        "from pkg.client import fetch\nfrom pkg.config import VALUE\n\ndef run() -> int:\n    return fetch() + VALUE\n",
        encoding="utf-8",
    )
    (repo / "tests" / "test_server.py").write_text(
        "from pkg.server import run\n\ndef test_run():\n    assert run() == 2\n",
        encoding="utf-8",
    )
    (repo / "pyproject.toml").write_text("[project]\nname='multi-contract-repo'\nversion='0.0.0'\n", encoding="utf-8")
    _init_repo(repo)

    result = build_project_model_snapshot(
        repo,
        tmp_path / "artifacts",
        project_id="multi-contract-repo",
        goal="decompose all runtime contracts",
        non_goals=["do not collapse files into a path bucket"],
        llm_mode="fixture",
        overwrite=True,
    )

    assert result.gate_report.passed is True
    assert {
        (contract.from_component_id, contract.to_component_id)
        for contract in result.snapshot.contracts
    } >= {
        ("component.pkg-server", "component.pkg-client"),
        ("component.pkg-server", "component.pkg-config"),
        ("component.pkg-client", "component.pkg-config"),
    }


def test_fixture_decomposer_emits_iteration_ready_model_for_fmc_like_project(tmp_path: Path) -> None:
    repo = tmp_path / "fmc-like"
    repo.mkdir()
    (repo / "src" / "pkg").mkdir(parents=True)
    (repo / "tests").mkdir()
    (repo / "src" / "pkg" / "__init__.py").write_text("", encoding="utf-8")
    (repo / "src" / "pkg" / "config.py").write_text(
        "from pydantic import SecretStr\n\nclass Settings:\n    fmc_host: str\n    fmc_password: SecretStr\n    fmc_rate_limit: int = 120\n    fmc_max_connections: int = 10\n",
        encoding="utf-8",
    )
    (repo / "src" / "pkg" / "client.py").write_text(
        "import asyncio\nimport httpx\n\n"
        "class RateLimiter:\n    def __init__(self, rate_limit: int = 120):\n        self.rate_limit = rate_limit\n\n"
        "class FMCClient:\n    def __init__(self):\n        self.semaphore = asyncio.Semaphore(10)\n        self.rate_limiter = RateLimiter(120)\n\n"
        "    async def authenticate(self):\n        return await httpx.AsyncClient().post('/api/fmc_platform/v1/auth/generatetoken')\n\n"
        "    async def _request(self, method: str, path: str):\n        if method == 'GET':\n            return await httpx.AsyncClient().get(path)\n        if method == 'POST':\n            return await self.authenticate()\n        raise ValueError(method)\n\n"
        "    async def get_all_items(self, path: str):\n        return await self._request('GET', path + '?offset=0&limit=1000')\n\n"
        "    async def test_connection(self):\n        return await self._request('GET', '/api/fmc_platform/v1/info/server')\n",
        encoding="utf-8",
    )
    (repo / "src" / "pkg" / "resources.py").write_text(
        "_client = None\n\ndef set_client(client):\n    global _client\n    _client = client\n\ndef get_client():\n    return _client\n",
        encoding="utf-8",
    )
    (repo / "src" / "pkg" / "tools.py").write_text(
        "from pkg import resources\n\nasync def search_object_by_ip(ip: str):\n    client = resources.get_client()\n    return await client.get_all_items('/api/fmc_config/v1/domain/default/object/networkaddresses')\n",
        encoding="utf-8",
    )
    (repo / "src" / "pkg" / "server.py").write_text(
        "from pkg import resources, tools\nfrom pkg.client import FMCClient\n\n"
        "def lifespan():\n    client = FMCClient()\n    resources.set_client(client)\n    return client\n\n"
        "def resource(uri):\n    return lambda fn: fn\n\ndef tool(fn):\n    return fn\n\n"
        "@resource('fmc://system/info')\nasync def system_info():\n    return await resources.get_client().test_connection()\n\n"
        "@tool\nasync def search_object_by_ip(ip: str):\n    return await tools.search_object_by_ip(ip)\n\n"
        "def main(transport='stdio'):\n    if transport == 'sse':\n        return 'http'\n    return 'stdio'\n",
        encoding="utf-8",
    )
    (repo / "src" / "pkg" / "main.py").write_text("from pkg.server import main\n\nif __name__ == '__main__':\n    main()\n", encoding="utf-8")
    (repo / "tests" / "test_server.py").write_text("from pkg.server import lifespan\n\ndef test_lifespan():\n    assert lifespan() is not None\n", encoding="utf-8")
    (repo / "tests" / "test_live.py").write_text("def test_live_placeholder():\n    pass\n", encoding="utf-8")
    (repo / "pyproject.toml").write_text(
        "[project]\nname='fmc-like'\nversion='0.0.0'\n[project.scripts]\nmcp-server-fmc='pkg.server:main'\n[tool.ruff]\nline-length=100\n[tool.mypy]\npython_version='3.12'\n",
        encoding="utf-8",
    )
    _init_repo(repo)

    result = build_project_model_snapshot(
        repo,
        tmp_path / "artifacts",
        project_id="fmc-like",
        goal="decompose FMC-like MCP server into iteration-ready responsibility-bearing components",
        non_goals=["do not collapse files into buckets"],
        llm_mode="fixture",
        overwrite=True,
    )

    assert result.gate_report.passed is True
    assert {
        (contract.from_component_id, contract.to_component_id)
        for contract in result.snapshot.contracts
    } >= {
        ("component.pkg-server", "component.pkg-resources"),
        ("component.pkg-server", "component.pkg-tools"),
    }
    commands = {check.command for check in result.snapshot.observable_checks}
    assert "uv run python -m pytest -q" in commands
    assert "uv run ruff check ." in commands
    assert "uv run mypy src/pkg" not in commands
    assert all("own the responsibility represented by" not in component.responsibility.lower() for component in result.snapshot.components)

    v1 = json.loads((result.snapshot_dir / "project-model-v1.json").read_text(encoding="utf-8"))
    iteration = v1["iterationReadiness"]
    profiles = {profile["componentId"]: profile for profile in iteration["componentProfiles"]}
    client_profile = profiles["component.pkg-client"]
    assert {"auth", "rate_limit", "concurrency", "pagination", "read_only"} <= set(client_profile["behavioralTags"])
    assert client_profile["riskLevel"] == "high"
    assert client_profile["priorityRank"] < profiles["component.pkg-main"]["priorityRank"]
    assert "RateLimiter" in client_profile["keySymbols"]
    assert any(contract["kind"] == "injects" for contract in iteration["runtimeContracts"])
    assert any(contract["kind"] == "delegates_to" for contract in iteration["runtimeContracts"])
    assert any(surface["surfaceType"] == "mcp_resource" and surface["name"] == "fmc://system/info" for surface in iteration["externalSurfaces"])
    assert any(surface["surfaceType"] == "console_script" and surface["name"] == "mcp-server-fmc" for surface in iteration["externalSurfaces"])
    env_names = {surface["name"] for surface in iteration["externalSurfaces"] if surface["surfaceType"] == "environment_variable"}
    assert {"FMC_HOST", "FMC_PASSWORD", "FMC_RATE_LIMIT", "FMC_MAX_CONNECTIONS"} <= env_names
    assert "API" not in env_names
    assert {"read_only_external_operations", "secret_safety", "rate_limit", "concurrency_limit", "live_test_boundary"} <= {
        invariant["category"] for invariant in iteration["productInvariants"]
    }
    invariants = {invariant["category"]: invariant for invariant in iteration["productInvariants"]}
    assert "120 requests per minute" in invariants["rate_limit"]["description"]
    assert "10 concurrent connections" in invariants["concurrency_limit"]["description"]
    surface_by_id = {surface["id"]: surface for surface in iteration["externalSurfaces"]}
    assert {surface_by_id[surface_id]["surfaceType"] for surface_id in invariants["secret_safety"]["externalSurfaceIds"]} == {"environment_variable"}
    assert {
        surface_by_id[surface_id]["surfaceType"] for surface_id in invariants["public_mcp_contract"]["externalSurfaceIds"]
    } <= {"mcp_resource", "mcp_tool"}
    assert any(item["rank"] == 1 and "read-only" in item["title"].lower() for item in iteration["priorityBacklog"])
    assert all(item["provenanceRefs"] for item in iteration["priorityBacklog"])
    quality = {gate["id"]: gate for gate in iteration["qualityGates"]}
    assert quality["quality.mypy"]["includedInAcceptance"] is False
    assert quality["quality.mypy"]["safeToRunByDefault"] is False
    assert any("test_connection" in question["question"] for question in iteration["openQuestions"])


def test_quality_gates_use_dev_extra_when_tooling_is_optional_dependency(tmp_path: Path) -> None:
    repo = tmp_path / "optional-dev-tools"
    repo.mkdir()
    (repo / "src" / "pkg").mkdir(parents=True)
    (repo / "tests").mkdir()
    (repo / "src" / "pkg" / "__init__.py").write_text("", encoding="utf-8")
    (repo / "src" / "pkg" / "core.py").write_text("def value() -> int:\n    return 1\n", encoding="utf-8")
    (repo / "tests" / "test_core.py").write_text("from pkg.core import value\n\ndef test_value():\n    assert value() == 1\n", encoding="utf-8")
    (repo / "pyproject.toml").write_text(
        """[project]
name = "optional-dev-tools"
version = "0.0.0"

[project.optional-dependencies]
dev = ["pytest>=8", "ruff>=0.8", "mypy>=1.13"]

[tool.ruff]
line-length = 100

[tool.mypy]
python_version = "3.12"
""",
        encoding="utf-8",
    )
    _init_repo(repo)

    result = build_project_model_snapshot(
        repo,
        tmp_path / "artifacts",
        project_id="optional-dev-tools",
        llm_mode="fixture",
        overwrite=True,
    )

    assert result.gate_report.passed is True
    v1 = json.loads((result.snapshot_dir / "project-model-v1.json").read_text(encoding="utf-8"))
    commands = {gate["command"] for gate in v1["iterationReadiness"]["qualityGates"]}
    assert "uv run --extra dev python -m pytest -q" in commands
    assert "uv run --extra dev ruff check ." in commands
    assert "uv run --extra dev mypy src/pkg" in commands
    assert "uv run python -m pytest -q" not in commands
    assert "uv run ruff check ." not in commands


def test_recorded_live_shaped_output_gets_deterministic_import_contract_closure(tmp_path: Path) -> None:
    repo = tmp_path / "closure-repo"
    repo.mkdir()
    _write_contract_closure_repo(repo)
    artifacts = tmp_path / "artifacts"
    fixture = build_project_model_snapshot(
        repo,
        artifacts,
        project_id="closure-repo",
        goal="decompose all runtime import contracts",
        non_goals=["do not force the model to enumerate mechanical imports"],
        llm_mode="fixture",
        overwrite=True,
    )
    raw = json.loads((fixture.snapshot_dir / "model-outputs" / "decomposer.raw.json").read_text(encoding="utf-8"))
    raw["model_id"] = "recorded-live-shaped-missing-contracts"
    raw["contracts"] = [
        {
            "id": "contract:model-reversed-server-client",
            "name": "Wrong-way server client import",
            "from_component_id": "component.pkg-client",
            "to_component_id": "component.pkg-server",
            "supporting_edge_ids": [
                next(
                    edge.id
                    for edge in fixture.graph.edges
                    if edge.kind == "imports" and edge.to_node_id == "node:python_import:pkg.client"
                )
            ],
            "near_neighbor_alternative_ids": [],
            "provenance_refs": [fixture.graph.nodes[0].provenance_refs[0].id],
        }
    ]
    for component in raw["components"]:
        component["contract_ids"] = ["contract:model-reversed-server-client"] if component["id"] in {"component.pkg-client", "component.pkg-server"} else []
    recorded_path = tmp_path / "recorded-live-shaped.json"
    recorded_path.write_text(json.dumps(raw, indent=2), encoding="utf-8")

    result = build_project_model_snapshot(
        repo,
        artifacts,
        project_id="closure-repo",
        goal="decompose all runtime import contracts",
        non_goals=["do not force the model to enumerate mechanical imports"],
        llm_mode="recorded",
        model_output_path=recorded_path,
        overwrite=True,
    )

    assert result.gate_report.passed is True
    auto_contracts = [contract for contract in result.snapshot.contracts if contract.id.startswith("contract.auto.")]
    closure_report = json.loads((result.snapshot_dir / "import-contract-closure.json").read_text(encoding="utf-8"))
    assert closure_report["autoContractCount"] == len(auto_contracts)
    assert closure_report["autoContractIds"] == [contract.id for contract in auto_contracts]
    assert auto_contracts
    assert {
        (contract.from_component_id, contract.to_component_id)
        for contract in auto_contracts
    } >= {
        ("component.pkg-server", "component.pkg-client"),
        ("component.pkg-server", "component.pkg-config"),
        ("component.pkg-client", "component.pkg-config"),
    }
    assert all(contract.provenance_refs for contract in auto_contracts)
    assert all(contract.near_neighbor_alternative_ids == [] for contract in auto_contracts)
    assert not any(contract.id == "contract:model-reversed-server-client" for contract in result.snapshot.contracts)
    for component in result.snapshot.components:
        assert "contract:model-reversed-server-client" not in component.contract_ids
    persisted_raw = json.loads((result.snapshot_dir / "model-outputs" / "decomposer.raw.json").read_text(encoding="utf-8"))
    assert persisted_raw["contracts"] == raw["contracts"]
    assert persisted_raw["components"] == raw["components"]


def test_contract_closure_is_idempotent_and_stable(tmp_path: Path) -> None:
    repo = tmp_path / "stable-closure"
    repo.mkdir()
    _write_contract_closure_repo(repo)
    artifacts = tmp_path / "artifacts"
    fixture = build_project_model_snapshot(repo, artifacts, project_id="stable-closure", llm_mode="fixture", overwrite=True)
    raw = json.loads((fixture.snapshot_dir / "model-outputs" / "decomposer.raw.json").read_text(encoding="utf-8"))
    raw["contracts"] = []
    for component in raw["components"]:
        component["contract_ids"] = []
    recorded_path = tmp_path / "recorded-no-contracts.json"
    recorded_path.write_text(json.dumps(raw, indent=2), encoding="utf-8")

    first = build_project_model_snapshot(repo, artifacts, project_id="stable-closure", llm_mode="recorded", model_output_path=recorded_path, overwrite=True)
    second = build_project_model_snapshot(repo, artifacts, project_id="stable-closure", llm_mode="recorded", model_output_path=recorded_path, overwrite=True)
    before = snapshot_to_dict(first.snapshot)
    closed_again = close_import_contracts_for_gate(first.snapshot, first.graph)

    assert snapshot_to_dict(closed_again) == before
    assert first.manifest["snapshot_hash"] == second.manifest["snapshot_hash"]
    auto_ids = [contract.id for contract in first.snapshot.contracts if contract.id.startswith("contract.auto.")]
    assert len(auto_ids) == len(set(auto_ids))
    assert not set(auto_ids) & {contract["id"] for contract in raw["contracts"]}


def test_contract_closure_does_not_mask_unmeasurable_no_edge_component(tmp_path: Path) -> None:
    repo = tmp_path / "lonely-repo"
    repo.mkdir()
    (repo / "pkg").mkdir()
    (repo / "pkg" / "__init__.py").write_text("", encoding="utf-8")
    (repo / "pkg" / "lonely.py").write_text("VALUE = 1\n", encoding="utf-8")
    (repo / "pyproject.toml").write_text("[project]\nname='lonely-repo'\nversion='0.0.0'\n", encoding="utf-8")
    _init_repo(repo)
    graph = build_project_graph(repo)
    graph_data = graph_to_dict(graph)
    module = next(node for node in graph_data["nodes"] if node.get("path") == "pkg/lonely.py" and node.get("kind") == "python_module")
    prov = module["provenance_refs"][0]["id"]
    snapshot = ProjectModelSnapshot(
        project_id="lonely-repo",
        project_root=str(repo),
        components=[
            Component(
                id="component.pkg-lonely",
                name="Lonely Runtime Value",
                responsibility="Provide a standalone runtime value for local imports",
                owned_node_ids=[module["id"]],
                provenance_refs=[prov],
                contract_ids=[],
                check_ids=[],
                verification_gap_ids=[],
            )
        ],
        observable_checks=[],
        verification_gaps=[],
    )

    closed = close_import_contracts_for_gate(snapshot, graph_data)
    report = run_project_model_gate(closed, graph_data)

    assert closed.contracts == []
    assert report.passed is False
    assert any("no contracts, checks, or gaps" in violation.message for violation in report.violations)


def test_contract_closure_requires_provenance_for_auto_contracts(tmp_path: Path) -> None:
    repo = tmp_path / "no-provenance"
    repo.mkdir()
    _write_contract_closure_repo(repo)
    fixture = build_project_model_snapshot(repo, tmp_path / "artifacts", project_id="no-provenance", llm_mode="fixture", overwrite=True)
    snapshot = fixture.snapshot
    graph_data = graph_to_dict(fixture.graph)
    snapshot.contracts = []
    for component in snapshot.components:
        component.contract_ids = []
        component.provenance_refs = []
    for edge in graph_data["edges"]:
        edge["provenance_refs"] = []

    closed = close_import_contracts_for_gate(snapshot, graph_data)
    report = run_project_model_gate(closed, graph_data)

    assert not any(contract.id.startswith("contract.auto.") for contract in closed.contracts)
    assert report.passed is False


def _write_contract_closure_repo(repo: Path) -> None:
    (repo / "pkg").mkdir()
    (repo / "tests").mkdir()
    (repo / "pkg" / "__init__.py").write_text("", encoding="utf-8")
    (repo / "pkg" / "config.py").write_text("VALUE = 1\n", encoding="utf-8")
    (repo / "pkg" / "client.py").write_text(
        "from pkg.config import VALUE\n\ndef fetch() -> int:\n    return VALUE\n",
        encoding="utf-8",
    )
    (repo / "pkg" / "server.py").write_text(
        "from pkg.client import fetch\nfrom pkg.config import VALUE\n\ndef run() -> int:\n    return fetch() + VALUE\n",
        encoding="utf-8",
    )
    (repo / "tests" / "test_server.py").write_text(
        "from pkg.server import run\n\ndef test_run():\n    assert run() == 2\n",
        encoding="utf-8",
    )
    (repo / "pyproject.toml").write_text("[project]\nname='closure-repo'\nversion='0.0.0'\n", encoding="utf-8")
    _init_repo(repo)
