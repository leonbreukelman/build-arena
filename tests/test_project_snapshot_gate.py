from __future__ import annotations

import copy
import subprocess
from pathlib import Path

from arena.project_graph import ProjectGraph, build_project_graph
from arena.project_model_gate import run_project_model_gate
from arena.project_snapshot import (
    Component,
    Contract,
    CrossCuttingConcern,
    HeldOutProbe,
    NearNeighborAlternative,
    ObservableCheck,
    ProjectModelSnapshot,
)


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
    (root / "pyproject.toml").write_text("[project]\nname='gate-project'\nversion='0.0.0'\n", encoding="utf-8")
    _init_repo(root)


def _ids(graph: ProjectGraph) -> tuple[str, str, str, str, str]:
    core_symbol = next(node.id for node in graph.nodes if node.symbol == "pkg.core.run")
    worker_symbol = next(node.id for node in graph.nodes if node.symbol == "pkg.worker.work")
    core_file = next(node.id for node in graph.nodes if node.path == "pkg/core.py" and node.kind == "file")
    worker_file = next(node.id for node in graph.nodes if node.path == "pkg/worker.py" and node.kind == "file")
    test_file = next(node.id for node in graph.nodes if node.path == "tests/test_core.py")
    return core_symbol, worker_symbol, core_file, worker_file, test_file


def _prov(graph: ProjectGraph, node_id: str) -> str:
    node = next(node for node in graph.nodes if node.id == node_id)
    return node.provenance_refs[0].id


def _base_snapshot(graph: ProjectGraph) -> ProjectModelSnapshot:
    core_symbol, worker_symbol, _, _, test_file = _ids(graph)
    p1 = _prov(graph, core_symbol)
    p2 = _prov(graph, worker_symbol)
    test_prov = _prov(graph, test_file)
    import_edge = next(edge for edge in graph.edges if edge.kind == "imports" and "pkg.worker" in edge.to_node_id)
    return ProjectModelSnapshot(
        project_id="gate-project",
        project_root=graph.project_root,
        goal="decompose this repository into responsibility-bearing components",
        non_goals=["do not treat file buckets as final components"],
        primary_model_id="fixture-good-model",
        graph_hash="",
        components=[
            Component(
                id="component.runtime-core",
                name="Runtime orchestration",
                responsibility="Coordinate the public runtime function and delegate work through a real import contract.",
                owned_node_ids=[core_symbol],
                provenance_refs=[p1],
                contract_ids=["contract.runtime-worker"],
                check_ids=["check.runtime-tests"],
                verification_gap_ids=[],
            ),
            Component(
                id="component.worker",
                name="Worker execution",
                responsibility="Provide the concrete worker behavior used by runtime orchestration.",
                owned_node_ids=[worker_symbol],
                provenance_refs=[p2],
                contract_ids=["contract.runtime-worker"],
                check_ids=["check.runtime-tests"],
                verification_gap_ids=[],
            ),
        ],
        contracts=[
            Contract(
                id="contract.runtime-worker",
                name="Runtime imports worker",
                from_component_id="component.runtime-core",
                to_component_id="component.worker",
                supporting_edge_ids=[import_edge.id],
                near_neighbor_alternative_ids=["near.contract-path-bucket"],
                provenance_refs=[p1, p2],
            )
        ],
        cross_cutting_concerns=[
            CrossCuttingConcern(id="concern.anti-fabrication", category="anti_fabrication", description="Claims must trace to graph provenance.", component_ids=["component.runtime-core", "component.worker"], contract_ids=["contract.runtime-worker"], provenance_refs=[p1]),
            CrossCuttingConcern(id="concern.determinism", category="determinism", description="Snapshot hashes and gates are deterministic.", component_ids=["component.runtime-core"], contract_ids=[], provenance_refs=[p1]),
            CrossCuttingConcern(id="concern.provenance", category="provenance", description="Graph-derived evidence backs accepted claims.", component_ids=["component.runtime-core", "component.worker"], contract_ids=["contract.runtime-worker"], provenance_refs=[p1, p2]),
            CrossCuttingConcern(id="concern.no-paid-api", category="no_live_paid_api_acceptance", description="Acceptance checks are local and allowlisted.", component_ids=["component.runtime-core"], contract_ids=[], provenance_refs=[test_prov]),
            CrossCuttingConcern(id="concern.protected", category="protected_surface_integrity", description="Protected schema surfaces are observed but not arena hypothesis targets.", component_ids=[], contract_ids=[], provenance_refs=[p1]),
            CrossCuttingConcern(id="concern.generated", category="generated_artifact_integrity", description="Generated surfaces are observed but not hand edited.", component_ids=[], contract_ids=[], provenance_refs=[p1]),
        ],
        observable_checks=[
            ObservableCheck(id="check.runtime-tests", description="Runtime behavior is checked by tests/test_core.py.", command="uv run pytest tests/test_core.py -q", component_ids=["component.runtime-core", "component.worker"], contract_ids=["contract.runtime-worker"], provenance_refs=[test_prov], acceptance_command_id="local-pytest", safe_to_run_by_default=True, requires_network=False, requires_paid_api=False)
        ],
        held_out_probes=[
            HeldOutProbe(id="probe.runtime-bucket", target_component_ids=["component.runtime-core"], target_contract_ids=["contract.runtime-worker"], builder_model_id="independent-probe-model", builder_prompt_hash="probehash", builder_independent_from_decomposer=True, planted_negative_id="negative.path-bucket", discrimination_passed=True, golden_control_passed=True, hidden_from_primary_decomposer=True, provenance_refs=[p1])
        ],
        verification_gaps=[],
        near_neighbor_alternatives=[
            NearNeighborAlternative(id="near.contract-path-bucket", target_id="contract.runtime-worker", alternative="Treat pkg files as one bucket.", why_not_primary="The goal requires responsibility-bearing contracts, while the non-goal forbids file buckets.", provenance_refs=[p1])
        ],
        acceptance_command_allowlist=["local-pytest"],
    )


def test_gate_passes_minimal_well_grounded_snapshot(tmp_path: Path) -> None:
    _write_repo(tmp_path)
    graph = build_project_graph(tmp_path)
    snapshot = _base_snapshot(graph)

    report = run_project_model_gate(snapshot, graph)

    assert report.passed is True
    assert not report.violations


def test_gate_fails_fluent_non_vague_sibling_file_bucket_decomposition(tmp_path: Path) -> None:
    _write_repo(tmp_path)
    graph = build_project_graph(tmp_path)
    snapshot = _base_snapshot(graph)
    _, _, core_file, worker_file, _ = _ids(graph)
    snapshot.components[0].name = "Runtime Coordination Surface"
    snapshot.components[0].owned_node_ids = [core_file, worker_file]
    snapshot.components[0].responsibility = "Own the sibling runtime files as a polished subsystem."
    snapshot.components[0].verification_gap_ids = []

    report = run_project_model_gate(snapshot, graph)

    assert report.passed is False
    assert any(v.gate == "component_measurability" and "file-bucket" in v.message for v in report.violations)


def test_gate_requires_goal_non_goals_and_near_neighbor_anchors(tmp_path: Path) -> None:
    _write_repo(tmp_path)
    graph = build_project_graph(tmp_path)
    snapshot = _base_snapshot(graph)
    snapshot.non_goals = []
    snapshot.near_neighbor_alternatives[0].why_not_primary = "No anchor."

    report = run_project_model_gate(snapshot, graph)

    assert report.passed is False
    assert {v.gate for v in report.violations} >= {"snapshot_goal", "near_neighbor_alternatives"}


def test_gate_requires_independent_probe_decoy_and_golden_control(tmp_path: Path) -> None:
    _write_repo(tmp_path)
    graph = build_project_graph(tmp_path)
    snapshot = _base_snapshot(graph)
    snapshot.held_out_probes[0].builder_model_id = snapshot.primary_model_id
    snapshot.held_out_probes[0].builder_independent_from_decomposer = False
    snapshot.held_out_probes[0].golden_control_passed = False

    report = run_project_model_gate(snapshot, graph)

    assert report.passed is False
    assert any(v.gate == "held_out_probe_isolation" for v in report.violations)
    assert any(v.gate == "held_out_probe_discrimination" for v in report.violations)


def test_gate_fails_live_paid_api_acceptance_checks_not_allowlisted(tmp_path: Path) -> None:
    _write_repo(tmp_path)
    graph = build_project_graph(tmp_path)
    snapshot = _base_snapshot(graph)
    snapshot.observable_checks[0].acceptance_command_id = "paid-live"
    snapshot.observable_checks[0].requires_network = True
    snapshot.observable_checks[0].requires_paid_api = True

    report = run_project_model_gate(snapshot, graph)

    assert report.passed is False
    assert any(v.gate == "no_live_paid_api_acceptance" for v in report.violations)


def test_gate_fails_unsafe_acceptance_command_even_when_allowlisted(tmp_path: Path) -> None:
    _write_repo(tmp_path)
    graph = build_project_graph(tmp_path)
    snapshot = _base_snapshot(graph)
    snapshot.observable_checks[0].command = "curl https://example.invalid"

    report = run_project_model_gate(snapshot, graph)

    assert report.passed is False
    assert any(v.gate == "no_live_paid_api_acceptance" and "nonlocal" in v.message for v in report.violations)


def test_gate_requires_primary_inventory_owned_or_gap_covered(tmp_path: Path) -> None:
    _write_repo(tmp_path)
    (tmp_path / "pkg" / "orphan.py").write_text("def orphan() -> int:\n    return 3\n", encoding="utf-8")
    graph = build_project_graph(tmp_path)
    snapshot = _base_snapshot(graph)

    report = run_project_model_gate(snapshot, graph)

    assert report.passed is False
    assert any(v.gate == "inventory_coverage" and "pkg.orphan" in v.message for v in report.violations)


def test_gate_fails_llm_only_high_impact_edges_without_gap(tmp_path: Path) -> None:
    _write_repo(tmp_path)
    graph = build_project_graph(tmp_path)
    snapshot = _base_snapshot(graph)
    graph = copy.deepcopy(graph)
    graph.edges[0].id = "edge:llm-only-calls"
    graph.edges[0].kind = "calls"
    graph.edges[0].confidence = "llm"
    graph.edges[0].derived_by = "model_output"
    snapshot.contracts[0].supporting_edge_ids = ["edge:llm-only-calls"]

    report = run_project_model_gate(snapshot, graph)

    assert report.passed is False
    assert any(v.gate == "contract_references" and "LLM-only" in v.message for v in report.violations)


def test_gate_fails_reversed_contract_direction_even_when_structurally_complete(tmp_path: Path) -> None:
    _write_repo(tmp_path)
    graph = build_project_graph(tmp_path)
    snapshot = _base_snapshot(graph)
    snapshot.contracts[0].from_component_id = "component.worker"
    snapshot.contracts[0].to_component_id = "component.runtime-core"

    report = run_project_model_gate(snapshot, graph)

    assert report.passed is False
    assert any(v.gate == "contract_references" and "does not connect" in v.message for v in report.violations)


def test_gate_fails_protected_surface_policy_violations(tmp_path: Path) -> None:
    _write_repo(tmp_path)
    graph = build_project_graph(tmp_path)
    snapshot = _base_snapshot(graph)
    protected_node = next(node.id for node in graph.nodes if node.kind == "protected_surface")
    snapshot.components[0].owned_node_ids.append(protected_node)

    report = run_project_model_gate(snapshot, graph)

    assert report.passed is False
    assert any(v.gate == "protected_surfaces" for v in report.violations)


def test_gate_fails_protected_surface_provenance_claims(tmp_path: Path) -> None:
    _write_repo(tmp_path)
    graph = build_project_graph(tmp_path)
    snapshot = _base_snapshot(graph)
    protected_node = next(node for node in graph.nodes if node.kind == "protected_surface")
    snapshot.components[0].provenance_refs.append(protected_node.provenance_refs[0].id)

    report = run_project_model_gate(snapshot, graph)

    assert report.passed is False
    assert any(v.gate == "protected_surfaces" and "provenance" in v.message for v in report.violations)


def test_gate_fails_responsibility_text_file_bucket_even_with_symbol_nodes(tmp_path: Path) -> None:
    _write_repo(tmp_path)
    graph = build_project_graph(tmp_path)
    snapshot = _base_snapshot(graph)
    snapshot.components[0].responsibility = "Contains pkg/core.py and pkg/worker.py as an arena path-classifier bucket."

    report = run_project_model_gate(snapshot, graph)

    assert report.passed is False
    assert any(v.gate == "component_measurability" and "path/file-bucket" in v.message for v in report.violations)


def test_gate_fails_when_owned_import_edge_loses_contract_attribution(tmp_path: Path) -> None:
    _write_repo(tmp_path)
    graph = build_project_graph(tmp_path)
    snapshot = _base_snapshot(graph)
    snapshot.contracts = []
    snapshot.components[0].contract_ids = []
    snapshot.components[1].contract_ids = []

    report = run_project_model_gate(snapshot, graph)

    assert report.passed is False
    assert any(v.gate == "edge_coverage" and "not covered" in v.message for v in report.violations)


def test_gate_fails_when_universal_anti_fabrication_not_all_component_covered(tmp_path: Path) -> None:
    _write_repo(tmp_path)
    graph = build_project_graph(tmp_path)
    snapshot = _base_snapshot(graph)
    anti = next(concern for concern in snapshot.cross_cutting_concerns if concern.category == "anti_fabrication")
    anti.component_ids = ["component.runtime-core"]

    report = run_project_model_gate(snapshot, graph)

    assert report.passed is False
    assert any(v.gate == "cross_cutting_concerns" and "anti_fabrication" in v.message for v in report.violations)


def test_gate_fails_self_referential_contract_after_merge(tmp_path: Path) -> None:
    _write_repo(tmp_path)
    graph = build_project_graph(tmp_path)
    snapshot = _base_snapshot(graph)
    snapshot.contracts[0].to_component_id = snapshot.contracts[0].from_component_id

    report = run_project_model_gate(snapshot, graph)

    assert report.passed is False
    assert any(v.gate == "contract_references" and "self-referential" in v.message for v in report.violations)


def test_gate_fails_cross_cutting_concern_unknown_component_reference(tmp_path: Path) -> None:
    _write_repo(tmp_path)
    graph = build_project_graph(tmp_path)
    snapshot = _base_snapshot(graph)
    snapshot.components = snapshot.components[:1]

    report = run_project_model_gate(snapshot, graph)

    assert report.passed is False
    assert any(v.gate == "cross_cutting_concerns" and "unknown component" in v.message for v in report.violations)
