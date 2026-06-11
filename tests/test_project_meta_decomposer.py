from __future__ import annotations

import json
import subprocess
from pathlib import Path

from arena.project_graph import build_project_graph
from arena.project_meta_decomposer import _best_target_component
from arena.project_model_gate import run_project_model_gate
from arena.project_model_llm import build_fixture_model_output
from arena.project_snapshot import ObservableCheck, snapshot_from_dict, to_plain
from tests.test_project_snapshot_gate import _base_snapshot, _write_repo


def _run(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=cwd, text=True, capture_output=True, check=True)


def _init_repo(root: Path) -> None:
    _run(["git", "init", "-b", "main"], root)
    _run(["git", "config", "user.email", "arena@example.invalid"], root)
    _run(["git", "config", "user.name", "Arena Tests"], root)
    _run(["git", "add", "."], root)
    _run(["git", "commit", "-m", "baseline"], root)


def _write_two_root_repo(root: Path) -> None:
    backend = root / "app" / "backend"
    frontend = root / "app" / "frontend"
    (backend / "src" / "service").mkdir(parents=True)
    (backend / "tests").mkdir(parents=True)
    (frontend / "src" / "widgets").mkdir(parents=True)
    (frontend / "src" / "lib").mkdir(parents=True)
    (frontend / "tests").mkdir(parents=True)
    (backend / "src" / "service" / "__init__.py").write_text("", encoding="utf-8")
    (backend / "src" / "service" / "api.py").write_text("from service.worker import work\n\ndef run() -> int:\n    return work()\n", encoding="utf-8")
    (backend / "src" / "service" / "worker.py").write_text("def work() -> int:\n    return 1\n", encoding="utf-8")
    (backend / "tests" / "test_api.py").write_text("from service.api import run\n\ndef test_run():\n    assert run() == 1\n", encoding="utf-8")
    (backend / "pyproject.toml").write_text("[project]\nname='synthetic-python-root'\nversion='0.0.0'\n", encoding="utf-8")
    (frontend / "src" / "lib" / "math.ts").write_text("export function one(): number { return 1; }\n", encoding="utf-8")
    (frontend / "src" / "widgets" / "Panel.tsx").write_text("import { one } from '../lib/math'\nexport function Panel() { return one() }\n", encoding="utf-8")
    (frontend / "tests" / "panel.test.ts").write_text("import { Panel } from '../src/widgets/Panel'\ntest('panel', () => expect(Panel()).toBe(1))\n", encoding="utf-8")
    (frontend / "package.json").write_text(
        json.dumps(
            {
                "scripts": {
                    "test": "vitest --run",
                    "build": "vite build",
                    "deploy": "gh release upload artifact",
                },
                "dependencies": {},
                "devDependencies": {},
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    _init_repo(root)


def _write_three_root_repo(root: Path) -> None:
    for rel, manifest, source_name in [
        ("services/api", "pyproject.toml", "svc"),
        ("packages/ui", "package.json", "ui"),
        ("tools/worker", "pyproject.toml", "worker"),
    ]:
        base = root / rel
        if manifest == "pyproject.toml":
            (base / "src" / source_name).mkdir(parents=True)
            (base / "tests").mkdir(parents=True)
            (base / "src" / source_name / "__init__.py").write_text("", encoding="utf-8")
            (base / "src" / source_name / "main.py").write_text("def run() -> int:\n    return 1\n", encoding="utf-8")
            (base / "tests" / "test_main.py").write_text(f"from {source_name}.main import run\n\ndef test_run():\n    assert run() == 1\n", encoding="utf-8")
            (base / manifest).write_text(f"[project]\nname='{source_name}'\nversion='0.0.0'\n", encoding="utf-8")
        else:
            (base / "src").mkdir(parents=True)
            (base / "src" / "index.ts").write_text("export function render() { return 1 }\n", encoding="utf-8")
            (base / manifest).write_text(json.dumps({"scripts": {"test": "vitest --run"}}, indent=2), encoding="utf-8")
    _init_repo(root)


def test_observable_check_serializes_execution_metadata_and_legacy_defaults() -> None:
    check = ObservableCheck(
        id="check.unit",
        description="Unit tests run in a root-scoped execution directory.",
        command="uv run pytest -q",
        component_ids=["component.one"],
        contract_ids=[],
        provenance_refs=["prov:test"],
        execution_dir="app/backend",
        safety_status="safe_by_default",
        execution_status="execution_proven",
        proof_artifact="proofs/backend-pytest.txt",
        verification_gap_ids=[],
    )

    plain = to_plain(check)

    assert plain["execution_dir"] == "app/backend"
    assert plain["safety_status"] == "safe_by_default"
    assert plain["execution_status"] == "execution_proven"
    assert plain["proof_artifact"] == "proofs/backend-pytest.txt"

    legacy = {
        "project_id": "legacy",
        "project_root": "/repo",
        "goal": "decompose this repository into responsibility-bearing components",
        "non_goals": ["do not treat file buckets as final components"],
        "observable_checks": [
            {
                "id": "check.legacy",
                "description": "Legacy local check.",
                "command": "uv run pytest -q",
                "component_ids": [],
                "contract_ids": [],
                "provenance_refs": [],
                "acceptance_command_id": "local-pytest",
            }
        ],
        "acceptance_command_allowlist": ["local-pytest"],
    }
    loaded = snapshot_from_dict(legacy)

    assert loaded.observable_checks[0].execution_dir == "."
    assert loaded.observable_checks[0].safety_status == "safe_by_default"
    assert loaded.observable_checks[0].execution_status == "execution_proven"


def test_gate_requires_execution_dir_and_acceptance_proof(tmp_path: Path) -> None:
    _write_repo(tmp_path)
    graph = build_project_graph(tmp_path)
    snapshot = _base_snapshot(graph)

    snapshot.observable_checks[0].execution_dir = ""
    report = run_project_model_gate(snapshot, graph)
    assert report.passed is False
    assert any(v.gate == "observable_check_execution" and "execution directory" in v.message for v in report.violations)

    snapshot = _base_snapshot(graph)
    snapshot.observable_checks[0].execution_status = "statically_validated"
    snapshot.observable_checks[0].proof_artifact = None
    report = run_project_model_gate(snapshot, graph)
    assert report.passed is False
    assert any(v.gate == "observable_check_execution" and "execution-proven" in v.message for v in report.violations)


def test_fixture_decomposer_discovers_root_scoped_checks_for_two_manifest_roots(tmp_path: Path) -> None:
    _write_two_root_repo(tmp_path)
    graph = build_project_graph(tmp_path)

    output = build_fixture_model_output(
        graph,
        project_id="synthetic-two-root",
        goal="decompose this repository into responsibility-bearing components",
        non_goals=["do not treat file buckets as final components"],
    )

    checks = {check["id"]: check for check in output["observable_checks"]}
    execution_dirs = {check["execution_dir"] for check in checks.values()}
    commands = {check["command"] for check in checks.values()}

    assert "app/backend" in execution_dirs
    assert "app/frontend" in execution_dirs
    assert all(command != "uv run pytest -q" or check["execution_dir"] == "app/backend" for check in checks.values() for command in [check["command"]])
    assert not any(check["execution_dir"] == "." and check["command"] == "uv run pytest -q" for check in checks.values())
    assert "npm test -- --run" in commands
    assert "npm run build" in commands
    assert not any("deploy" in check["command"] for check in checks.values())
    assert output["acceptance_command_allowlist"] == []
    assert all(check["execution_status"] == "statically_validated" for check in checks.values())


def test_fixture_decomposer_handles_non_app_three_root_shape_without_identity_branch(tmp_path: Path) -> None:
    _write_three_root_repo(tmp_path)
    graph = build_project_graph(tmp_path)

    output = build_fixture_model_output(
        graph,
        project_id="synthetic-three-root",
        goal="decompose this repository into responsibility-bearing components",
        non_goals=["do not treat file buckets as final components"],
    )

    execution_dirs = {check["execution_dir"] for check in output["observable_checks"]}
    assert {"services/api", "packages/ui", "tools/worker"} <= execution_dirs
    assert len(output["components"]) >= 3
    assert len(output["components"]) > 8 or len(graph.nodes) <= 80


def test_fixture_decomposer_output_is_deterministic(tmp_path: Path) -> None:
    _write_two_root_repo(tmp_path)
    graph = build_project_graph(tmp_path)
    kwargs = {
        "project_id": "synthetic-two-root",
        "goal": "decompose this repository into responsibility-bearing components",
        "non_goals": ["do not treat file buckets as final components"],
    }

    first = build_fixture_model_output(graph, **kwargs)
    second = build_fixture_model_output(graph, **kwargs)

    assert first == second


def test_fixture_decomposer_marks_unrun_semantic_probe_quality_as_gap_not_passed(tmp_path: Path) -> None:
    _write_two_root_repo(tmp_path)
    graph = build_project_graph(tmp_path)

    output = build_fixture_model_output(
        graph,
        project_id="synthetic-two-root",
        goal="decompose this repository into responsibility-bearing components",
        non_goals=["do not treat file buckets as final components"],
    )

    assert output["held_out_probes"] == []
    semantic_gap = next(
        gap for gap in output["verification_gaps"] if gap["id"] == "gap.semantic-understanding-not-independently-validated"
    )
    assert semantic_gap["component_ids"]
    assert "independently" in semantic_gap["description"]
    assert "planted-negative" in semantic_gap["proposed_closure_check"]


def test_decomposition_logic_has_no_target_identity_branches() -> None:
    source_files = [
        Path("arena/project_model_llm.py"),
        Path("arena/project_meta_decomposer.py"),
    ]
    forbidden = ["cmmc", "fmc", "calibration", "level1", "readiness_assistant"]
    combined = "\n".join(path.read_text(encoding="utf-8", errors="replace").lower() for path in source_files if path.exists())

    assert not any(token in combined for token in forbidden)


def test_contract_ids_remain_unique_when_component_names_share_long_prefix(tmp_path: Path) -> None:
    root = tmp_path / "app" / "frontend"
    (root / "src" / "components").mkdir(parents=True)
    (root / "src" / "api").mkdir(parents=True)
    (root / "src" / "types").mkdir(parents=True)
    (root / "package.json").write_text('{"scripts":{"test":"vitest --run"}}\n', encoding="utf-8")
    (root / "src" / "components" / "Panel.tsx").write_text(
        "import { client } from '../api/client';\nimport type { Thing } from '../types';\nexport function Panel(x: Thing) { return client(x); }\n",
        encoding="utf-8",
    )
    (root / "src" / "api" / "client.ts").write_text("export function client(x: unknown) { return x; }\n", encoding="utf-8")
    (root / "src" / "types" / "index.ts").write_text("export interface Thing { id: string }\n", encoding="utf-8")

    graph = build_project_graph(tmp_path)
    output = build_fixture_model_output(
        graph,
        project_id="long-prefix-contracts",
        goal="decompose this repository into responsibility-bearing components",
        non_goals=["do not treat file buckets as final components"],
    )

    contracts = output["contracts"]
    assert len({contract["id"] for contract in contracts}) == len(contracts)
    component_contracts = [
        contract
        for contract in contracts
        if contract["from_component_id"] == "component.app-frontend-source-components"
    ]
    assert {contract["to_component_id"] for contract in component_contracts} >= {
        "component.app-frontend-source-api",
        "component.app-frontend-source-types",
    }


def test_import_target_selection_prefers_exact_module_over_longer_test_descendant() -> None:
    symbols_by_component = {
        "component.production-pages": ["app.frontend.src.pages.App", "app.frontend.src.pages.App.App"],
        "component.verification": ["app.frontend.src.pages.App.test", "app.frontend.src.pages.App.test.setup"],
    }

    selected = _best_target_component(
        "app.frontend.src.pages.App",
        symbols_by_component,
        exclude="component.entrypoint",
    )

    assert selected == "component.production-pages"


def test_import_target_selection_does_not_suffix_match_single_segment_stdlib_names() -> None:
    symbols_by_component = {
        "component.frontend-html": ["app.frontend.index.html"],
    }

    selected = _best_target_component(
        "html",
        symbols_by_component,
        exclude="component.backend-reports",
    )

    assert selected is None


def test_fixture_decomposer_resolves_python_src_root_relative_import_contracts(tmp_path: Path) -> None:
    root = tmp_path / "service" / "backend"
    (root / "src" / "api").mkdir(parents=True)
    (root / "src" / "assessment").mkdir(parents=True)
    (root / "tests").mkdir(parents=True)
    (root / "pyproject.toml").write_text("[project]\nname='python-root-imports'\nversion='0.0.0'\n", encoding="utf-8")
    (root / "src" / "api" / "main.py").write_text(
        "from assessment.text_analysis import score\n\ndef run() -> int:\n    return score()\n",
        encoding="utf-8",
    )
    (root / "src" / "assessment" / "text_analysis.py").write_text("def score() -> int:\n    return 1\n", encoding="utf-8")
    (root / "tests" / "test_main.py").write_text("from api.main import run\n\ndef test_run():\n    assert run() == 1\n", encoding="utf-8")
    _init_repo(tmp_path)

    graph = build_project_graph(tmp_path)
    output = build_fixture_model_output(
        graph,
        project_id="python-root-relative-imports",
        goal="decompose this repository into responsibility-bearing components",
        non_goals=["do not treat file buckets as final components"],
    )

    assert any(
        contract["from_component_id"] == "component.service-backend-source-api"
        and contract["to_component_id"] == "component.service-backend-source-assessment"
        for contract in output["contracts"]
    )


def test_gate_edge_coverage_sees_python_src_root_relative_imports(tmp_path: Path) -> None:
    root = tmp_path / "service" / "backend"
    (root / "src" / "api").mkdir(parents=True)
    (root / "src" / "assessment").mkdir(parents=True)
    (root / "tests").mkdir(parents=True)
    (root / "pyproject.toml").write_text("[project]\nname='python-root-imports'\nversion='0.0.0'\n", encoding="utf-8")
    (root / "src" / "__init__.py").write_text("", encoding="utf-8")
    (root / "src" / "api" / "main.py").write_text(
        "from assessment.text_analysis import score\n\ndef run() -> int:\n    return score()\n",
        encoding="utf-8",
    )
    (root / "src" / "assessment" / "text_analysis.py").write_text("def score() -> int:\n    return 1\n", encoding="utf-8")
    (root / "tests" / "test_main.py").write_text("from api.main import run\n\ndef test_run():\n    assert run() == 1\n", encoding="utf-8")
    _init_repo(tmp_path)

    graph = build_project_graph(tmp_path)
    output = build_fixture_model_output(
        graph,
        project_id="python-root-relative-imports",
        goal="decompose this repository into responsibility-bearing components",
        non_goals=["do not treat file buckets as final components"],
    )
    snapshot = snapshot_from_dict({**output, "project_root": str(tmp_path), "primary_model_id": output["model_id"]})
    removed_contract = next(
        contract
        for contract in snapshot.contracts
        if contract.from_component_id == "component.service-backend-source-api"
        and contract.to_component_id == "component.service-backend-source-assessment"
    )
    snapshot.contracts = [contract for contract in snapshot.contracts if contract.id != removed_contract.id]

    report = run_project_model_gate(snapshot, graph)

    assert any(v.gate == "edge_coverage" and "component.service-backend-source-assessment" in v.message for v in report.violations)
    assert not any(v.gate == "edge_coverage" and "component.service-backend-source-init" in v.message for v in report.violations)


def test_fixture_decomposer_keeps_test_symbols_out_of_source_components(tmp_path: Path) -> None:
    root = tmp_path / "service" / "backend"
    (root / "src" / "api").mkdir(parents=True)
    (root / "tests").mkdir(parents=True)
    (root / "pyproject.toml").write_text("[project]\nname='python-test-routing'\nversion='0.0.0'\n", encoding="utf-8")
    (root / "src" / "api" / "main.py").write_text("def run() -> int:\n    return 1\n", encoding="utf-8")
    (root / "tests" / "test_main.py").write_text(
        "from api.main import run\n\ndef test_run():\n    assert run() == 1\n",
        encoding="utf-8",
    )
    _init_repo(tmp_path)

    graph = build_project_graph(tmp_path)
    output = build_fixture_model_output(
        graph,
        project_id="python-test-routing",
        goal="decompose this repository into responsibility-bearing components",
        non_goals=["do not treat file buckets as final components"],
    )
    nodes_by_id = {node.id: node for node in graph.nodes}

    for component in output["components"]:
        if "-source-" not in component["id"]:
            continue
        owned_paths = [nodes_by_id[node_id].path or "" for node_id in component["owned_node_ids"] if node_id in nodes_by_id]
        assert not any("/tests/" in f"/{path}" for path in owned_paths), component["id"]


def test_fixture_decomposer_surfaces_gap_when_multi_component_root_has_no_contracts(tmp_path: Path) -> None:
    root = tmp_path / "service" / "backend"
    (root / "src" / "api").mkdir(parents=True)
    (root / "src" / "assessment").mkdir(parents=True)
    (root / "tests").mkdir(parents=True)
    (root / "pyproject.toml").write_text("[project]\nname='python-no-contracts'\nversion='0.0.0'\n", encoding="utf-8")
    (root / "src" / "api" / "main.py").write_text("def run() -> int:\n    return 1\n", encoding="utf-8")
    (root / "src" / "assessment" / "text_analysis.py").write_text("def score() -> int:\n    return 1\n", encoding="utf-8")
    (root / "tests" / "test_main.py").write_text("from api.main import run\n\ndef test_run():\n    assert run() == 1\n", encoding="utf-8")
    _init_repo(tmp_path)

    graph = build_project_graph(tmp_path)
    output = build_fixture_model_output(
        graph,
        project_id="python-no-contracts",
        goal="decompose this repository into responsibility-bearing components",
        non_goals=["do not treat file buckets as final components"],
    )

    assert any(gap["id"] == "gap.service-backend-unresolved-source-contracts" for gap in output["verification_gaps"])
