from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from arena.project_graph import GraphEdge, GraphNode, ProjectGraph

EXCLUDED_TAGS = {"excluded_from_primary_context", "protected", "generated", "symlink"}
SOURCE_KINDS = {"python_module", "python_function", "python_class", "javascript_module", "javascript_function"}
MODULE_KINDS = {"python_module", "javascript_module"}
TEST_KINDS = {"test_file"}
CONFIG_KINDS = {"config"}
DOC_KINDS = {"markdown_section"}
FILE_BUCKET_KINDS = {"file", "test_file", "config", "protected_surface", "generated_surface", "verification_artifact"}
PYTHON_MANIFESTS = {"pyproject.toml", "setup.cfg", "setup.py", "requirements.txt"}
NODE_MANIFESTS = {"package.json"}
ROOT_MANIFESTS = PYTHON_MANIFESTS | NODE_MANIFESTS | {"Cargo.toml", "go.mod", "Makefile"}
SAFE_NODE_SCRIPT_NAMES = ("test", "build", "typecheck", "lint")
UNSAFE_SCRIPT_MARKERS = (
    "curl",
    "wget",
    "ssh",
    "scp",
    "rsync",
    "gh ",
    "gcloud",
    "aws ",
    "az ",
    "kubectl",
    "deploy",
    "publish",
    "release",
    "rm -rf",
    "token",
    "secret",
    "password",
    "api_key",
    "$",
    "&&",
    "||",
    ";",
    "|",
    "`",
    "$(",
    ">",
    "<",
)


@dataclass(slots=True)
class ProjectRoot:
    path: str
    toolchains: set[str] = field(default_factory=set)
    manifest_paths: list[str] = field(default_factory=list)
    synthetic: bool = False

    @property
    def id(self) -> str:
        return _id("root", self.path or "workspace")

    @property
    def execution_dir(self) -> str:
        return self.path or "."


@dataclass(slots=True)
class ComponentDraft:
    id: str
    name: str
    responsibility: str
    root_path: str
    seed: str
    owned_node_ids: list[str] = field(default_factory=list)
    provenance_refs: list[str] = field(default_factory=list)
    contract_ids: list[str] = field(default_factory=list)
    check_ids: list[str] = field(default_factory=list)
    verification_gap_ids: list[str] = field(default_factory=list)


def build_meta_model_output(graph: ProjectGraph, *, project_id: str, goal: str, non_goals: list[str]) -> dict[str, Any]:
    nodes = list(graph.nodes)
    edges = list(graph.edges)
    node_by_id = {node.id: node for node in nodes}
    roots = discover_project_roots(graph)
    root_by_path = {root.path: root for root in roots}
    root_for_node = {node.id: _nearest_root_path(node.path, root_by_path) for node in nodes if node.path}
    checks = _discover_checks(graph, roots)
    components, node_to_component = _build_components(nodes, roots, root_for_node, checks)
    contracts = _build_contracts(edges, node_by_id, components, node_to_component)
    _attach_contracts(components, contracts)
    gaps = _build_gaps(components, contracts, checks, node_by_id)
    component_dicts = [_component_to_dict(component) for component in sorted(components.values(), key=lambda item: item.id)]
    contract_dicts = sorted(contracts.values(), key=lambda item: item["id"])
    check_dicts = sorted(checks, key=lambda item: item["id"])
    gap_dicts = sorted(gaps, key=lambda item: item["id"])
    first_prov = _first_graph_provenance(nodes)
    target_id = contract_dicts[0]["id"] if contract_dicts else (component_dicts[0]["id"] if component_dicts else "component.workspace")
    return {
        "model_id": "fixture-meta-decomposer",
        "project_id": project_id,
        "goal": goal,
        "non_goals": non_goals,
        "components": component_dicts,
        "contracts": contract_dicts,
        "cross_cutting_concerns": _cross_cutting_concerns(component_dicts, contract_dicts, nodes, first_prov),
        "observable_checks": check_dicts,
        "held_out_probes": [],
        "verification_gaps": gap_dicts,
        "near_neighbor_alternatives": [
            {
                "id": "near.file-bucket-boundary",
                "target_id": target_id,
                "alternative": "Treat adjacent files as a polished bucket without responsibility evidence.",
                "why_not_primary": f"Rejected for this project goal: {goal}. It also violates the stated non-goal: {non_goals[0] if non_goals else 'avoid fluent file buckets'}. A file bucket is not responsibility-bearing evidence.",
                "provenance_refs": [first_prov],
            }
        ],
        "acceptance_command_allowlist": _acceptance_command_allowlist(check_dicts),
    }


def _acceptance_command_allowlist(checks: list[dict[str, Any]]) -> list[str]:
    commands = {
        str(check.get("command") or "")
        for check in checks
        if check.get("execution_dir") == "." and check.get("command") == "uv run python -m pytest -q"
    }
    if not commands:
        return []
    return ["local-pytest", *sorted(commands)]


def discover_project_roots(graph: ProjectGraph) -> list[ProjectRoot]:
    nodes = list(graph.nodes)
    root_by_path: dict[str, ProjectRoot] = {}
    for node in nodes:
        path = node.path or ""
        name = Path(path).name
        if name not in ROOT_MANIFESTS:
            continue
        root_path = Path(path).parent.as_posix()
        if root_path == ".":
            root_path = ""
        root = root_by_path.setdefault(root_path, ProjectRoot(path=root_path))
        root.manifest_paths.append(path)
        if name in PYTHON_MANIFESTS:
            root.toolchains.add("python")
        elif name in NODE_MANIFESTS:
            root.toolchains.add("node")
        elif name == "Cargo.toml":
            root.toolchains.add("rust")
        elif name == "go.mod":
            root.toolchains.add("go")
        elif name == "Makefile":
            root.toolchains.add("make")
    if not root_by_path:
        root_by_path[""] = ProjectRoot(path="", toolchains={"synthetic"}, synthetic=True)
    for node in nodes:
        if not node.path or _is_excluded(node):
            continue
        if _nearest_root_path(node.path, root_by_path) is None:
            root_by_path.setdefault("", ProjectRoot(path="", toolchains={"synthetic"}, synthetic=True))
            break
    return sorted(root_by_path.values(), key=lambda item: (item.path.count("/"), item.path))


def _discover_checks(graph: ProjectGraph, roots: list[ProjectRoot]) -> list[dict[str, Any]]:
    project_root = Path(graph.project_root)
    checks: list[dict[str, Any]] = []
    for root in sorted(roots, key=lambda item: item.path):
        root_path = project_root / root.path if root.path else project_root
        root_nodes = [node for node in graph.nodes if node.path and _path_in_root(node.path, root.path)]
        components_placeholder: list[str] = []
        if "python" in root.toolchains and _has_python_tests(root_nodes):
            prov = _first_prov_for_paths(graph.nodes, root.manifest_paths) or _first_prov(root_nodes) or _first_graph_provenance(graph.nodes)
            checks.append(
                _check(
                    root=root,
                    kind="python-tests",
                    command="uv run python -m pytest -q" if not root.path else "uv run pytest -q",
                    description="Run root-local Python tests discovered from generic project metadata.",
                    provenance_refs=[prov],
                    component_ids=components_placeholder,
                )
            )
        if "python" in root.toolchains and _has_ruff_config(root_path, root):
            prov = _first_prov_for_paths(graph.nodes, root.manifest_paths) or _first_prov(root_nodes) or _first_graph_provenance(graph.nodes)
            checks.append(
                _check(
                    root=root,
                    kind="python-ruff",
                    command="uv run ruff check .",
                    description="Run root-local Ruff checks discovered from generic project metadata.",
                    provenance_refs=[prov],
                    component_ids=components_placeholder,
                )
            )
        if "node" in root.toolchains:
            package_json = root_path / "package.json"
            scripts = _read_package_scripts(package_json)
            for script_name in SAFE_NODE_SCRIPT_NAMES:
                script_body = scripts.get(script_name)
                if not script_body or not _script_is_modelable(script_body):
                    continue
                command = _node_command(script_name, script_body)
                if not command:
                    continue
                prov = _first_prov_for_paths(graph.nodes, [f"{root.path}/package.json".strip("/")]) or _first_graph_provenance(graph.nodes)
                checks.append(
                    _check(
                        root=root,
                        kind=f"node-{script_name}",
                        command=command,
                        description=f"Run root-local Node {script_name} task discovered from package metadata.",
                        provenance_refs=[prov],
                        component_ids=components_placeholder,
                        safety_status="unknown",
                        safe_to_run_by_default=False,
                    )
                )
    if not checks:
        prov = _first_graph_provenance(graph.nodes)
        checks.append(
            {
                "id": "check.workspace-review-gap",
                "description": "No root-local safe check was discovered; review the verification gap before applying changes.",
                "command": "manual deterministic review required",
                "execution_dir": ".",
                "component_ids": [],
                "contract_ids": [],
                "provenance_refs": [prov],
                "acceptance_command_id": None,
                "safe_to_run_by_default": False,
                "requires_network": False,
                "requires_paid_api": False,
                "safety_status": "unknown",
                "execution_status": "gapped",
                "proof_artifact": None,
                "verification_gap_ids": ["gap.workspace-no-local-check"],
            }
        )
    return checks


def _build_components(
    nodes: list[GraphNode],
    roots: list[ProjectRoot],
    root_for_node: dict[str, str | None],
    checks: list[dict[str, Any]],
) -> tuple[dict[str, ComponentDraft], dict[str, str]]:
    components: dict[str, ComponentDraft] = {}
    node_to_component: dict[str, str] = {}
    checks_by_root: dict[str, list[str]] = {}
    for check in checks:
        root_path = "." if check["execution_dir"] == "." else check["execution_dir"]
        checks_by_root.setdefault("" if root_path == "." else root_path, []).append(check["id"])

    for root in roots:
        root_nodes = [node for node in nodes if root_for_node.get(node.id) == root.path and not _is_excluded(node)]
        source_nodes = [node for node in root_nodes if node.kind in SOURCE_KINDS and not _is_test_path(node.path or "")]
        if not source_nodes and not root_nodes:
            continue
        split_module_level = _should_split_single_package_modules(source_nodes, root.path)
        for node in sorted(source_nodes, key=lambda item: (item.path or "", item.symbol or item.label, item.kind)):
            seed = _source_seed(node.path or "", root.path, split_module_level=split_module_level)
            component_id = _source_component_id(root, seed)
            component = components.setdefault(
                component_id,
                ComponentDraft(
                    id=component_id,
                    name=_component_name(root, seed, "source"),
                    responsibility=_component_responsibility(root, seed, "source"),
                    root_path=root.path,
                    seed=seed,
                ),
            )
            _add_node(component, node)
            node_to_component[node.id] = component.id
        for node in sorted(root_nodes, key=lambda item: (item.path or "", item.kind, item.id)):
            if node.id in node_to_component:
                continue
            if _is_import_placeholder(node):
                continue
            seed = _non_source_seed(node, root.path)
            source_component = (
                _component_for_root_seed(components, root.path, _source_seed(node.path or "", root.path, split_module_level=split_module_level))
                if node.kind == "file" and not _is_test_path(node.path or "")
                else None
            )
            if source_component is not None:
                component = source_component
            else:
                component = components.setdefault(
                    _id("component", f"{root.path or 'workspace'} {seed}"),
                    ComponentDraft(
                        id=_id("component", f"{root.path or 'workspace'} {seed}"),
                        name=_component_name(root, seed, "support"),
                        responsibility=_component_responsibility(root, seed, "support"),
                        root_path=root.path,
                        seed=seed,
                    ),
                )
            _add_node(component, node)
            node_to_component[node.id] = component.id
        for component in [item for item in components.values() if item.root_path == root.path]:
            for check_id in checks_by_root.get(root.path, []):
                if check_id not in component.check_ids:
                    component.check_ids.append(check_id)
    if not components:
        project_node = next((node for node in nodes if node.kind == "project"), nodes[0])
        component = ComponentDraft(
            id="component.workspace-overview",
            name="Workspace overview",
            responsibility="Represent the repository-level context when no parseable source roots are available.",
            root_path="",
            seed="overview",
        )
        _add_node(component, project_node)
        components[component.id] = component
        node_to_component[project_node.id] = component.id
    for check in checks:
        root_path = "" if check["execution_dir"] == "." else check["execution_dir"]
        check["component_ids"] = sorted(component.id for component in components.values() if component.root_path == root_path)
    return components, node_to_component


def _build_contracts(
    edges: list[GraphEdge],
    node_by_id: dict[str, GraphNode],
    components: dict[str, ComponentDraft],
    node_to_component: dict[str, str],
) -> dict[str, dict[str, Any]]:
    contracts: dict[str, dict[str, Any]] = {}
    symbols_by_component = {component.id: _component_symbols(component, node_by_id) for component in components.values()}
    for edge in sorted(edges, key=lambda item: item.id):
        if edge.kind != "imports":
            continue
        from_component_id = node_to_component.get(edge.from_node_id)
        if not from_component_id:
            continue
        imported = _edge_import_target(edge)
        if not imported:
            continue
        to_component_id = _best_target_component(imported, symbols_by_component, exclude=from_component_id)
        if not to_component_id or to_component_id == from_component_id:
            continue
        contract_id = _id("contract", f"{from_component_id} imports {to_component_id}")
        provs = _unique([
            *components[from_component_id].provenance_refs[:1],
            *components[to_component_id].provenance_refs[:1],
            *_edge_provs(edge),
        ])
        if contract_id not in contracts:
            contracts[contract_id] = {
                "id": contract_id,
                "name": f"{components[from_component_id].name} imports {components[to_component_id].name}",
                "from_component_id": from_component_id,
                "to_component_id": to_component_id,
                "supporting_edge_ids": [],
                "near_neighbor_alternative_ids": ["near.file-bucket-boundary"],
                "provenance_refs": provs,
            }
        contracts[contract_id]["supporting_edge_ids"].append(edge.id)
        contracts[contract_id]["supporting_edge_ids"] = sorted(set(contracts[contract_id]["supporting_edge_ids"]))
    return contracts


def _attach_contracts(components: dict[str, ComponentDraft], contracts: dict[str, dict[str, Any]]) -> None:
    for contract in contracts.values():
        for component_id in (contract["from_component_id"], contract["to_component_id"]):
            component = components.get(component_id)
            if component and contract["id"] not in component.contract_ids:
                component.contract_ids.append(contract["id"])


def _is_source_component(component: ComponentDraft) -> bool:
    return "-source-" in component.id


def _add_unresolved_source_contract_gaps(gaps: list[dict[str, Any]], components: dict[str, ComponentDraft], contracts: dict[str, dict[str, Any]]) -> None:
    source_by_root: dict[str, list[ComponentDraft]] = {}
    for component in components.values():
        if _is_source_component(component):
            source_by_root.setdefault(component.root_path, []).append(component)
    for root_path, source_components in sorted(source_by_root.items()):
        if len(source_components) < 2:
            continue
        source_ids = {component.id for component in source_components}
        has_source_contract = any(
            contract.get("from_component_id") in source_ids and contract.get("to_component_id") in source_ids
            for contract in contracts.values()
        )
        if has_source_contract:
            continue
        gap_id = _id("gap", f"{root_path or 'workspace'} unresolved source contracts")
        for component in source_components:
            if gap_id not in component.verification_gap_ids:
                component.verification_gap_ids.append(gap_id)
        gaps.append(
            {
                "id": gap_id,
                "description": "This root has multiple source components but no resolved source-to-source contracts; import resolution may be incomplete or coupling may be absent.",
                "severity": "medium",
                "component_ids": sorted(source_ids),
                "contract_ids": [],
                "provenance_refs": _component_provs(source_components),
                "proposed_closure_check": "Inspect root-local imports or add language-specific resolution evidence proving whether cross-component coupling exists.",
            }
        )


def _build_gaps(components: dict[str, ComponentDraft], contracts: dict[str, dict[str, Any]], checks: list[dict[str, Any]], node_by_id: dict[str, GraphNode]) -> list[dict[str, Any]]:
    gaps: list[dict[str, Any]] = []
    _add_unresolved_source_contract_gaps(gaps, components, contracts)
    if components:
        gaps.append(
            {
                "id": "gap.semantic-understanding-not-independently-validated",
                "description": "Semantic component quality has not been independently probe-validated; deterministic graph grounding constrains project claims, but no planted-negative/golden-control probe artifacts were run.",
                "severity": "medium",
                "component_ids": sorted(components),
                "contract_ids": sorted(contracts),
                "provenance_refs": _component_provs(components.values()),
                "proposed_closure_check": "Run independent planted-negative and golden-control probe artifacts, capture the proof outputs, and rerun the deterministic gate.",
            }
        )
    if any(check["execution_status"] == "gapped" for check in checks):
        gaps.append(
            {
                "id": "gap.workspace-no-local-check",
                "description": "No root-local safe verification command was discovered from generic manifest evidence.",
                "severity": "high",
                "component_ids": sorted(components),
                "contract_ids": [],
                "provenance_refs": _component_provs(components.values()),
                "proposed_closure_check": "Add a local test/build task to a recognized project manifest and rerun decomposition.",
            }
        )
    for component in sorted(components.values(), key=lambda item: item.id):
        owned_nodes = [node_by_id[node_id] for node_id in component.owned_node_ids if node_id in node_by_id]
        owned_kinds = {node.kind for node in owned_nodes}
        needs_gap = False
        if not (component.contract_ids or component.check_ids or component.verification_gap_ids):
            needs_gap = True
        if len(owned_nodes) >= 2 and owned_kinds <= FILE_BUCKET_KINDS:
            needs_gap = True
        if needs_gap:
            gap_id = _id("gap", f"{component.id} verification")
            if gap_id not in component.verification_gap_ids:
                component.verification_gap_ids.append(gap_id)
            gaps.append(
                {
                    "id": gap_id,
                    "description": f"Component {component.name} needs more specific behavioral verification than generic manifest discovery could prove.",
                    "severity": "medium",
                    "component_ids": [component.id],
                    "contract_ids": component.contract_ids,
                    "provenance_refs": component.provenance_refs[:3] or _component_provs([component]),
                    "proposed_closure_check": "Add or identify a root-local deterministic test/build command covering this component.",
                }
            )
    gap_ids = {gap["id"] for gap in gaps}
    for check in checks:
        check["verification_gap_ids"] = [gap_id for gap_id in check["verification_gap_ids"] if gap_id in gap_ids]
    return gaps


def _component_to_dict(component: ComponentDraft) -> dict[str, Any]:
    return {
        "id": component.id,
        "name": component.name,
        "responsibility": component.responsibility,
        "owned_node_ids": sorted(set(component.owned_node_ids)),
        "provenance_refs": component.provenance_refs[:5],
        "contract_ids": sorted(set(component.contract_ids)),
        "check_ids": sorted(set(component.check_ids)),
        "verification_gap_ids": sorted(set(component.verification_gap_ids)),
    }


def _cross_cutting_concerns(component_dicts: list[dict[str, Any]], contract_dicts: list[dict[str, Any]], nodes: list[GraphNode], first_prov: str) -> list[dict[str, Any]]:
    component_ids = [component["id"] for component in component_dicts]
    contract_ids = [contract["id"] for contract in contract_dicts]
    concerns = [
        {
            "id": "concern.anti-fabrication",
            "category": "anti_fabrication",
            "description": "Accepted decomposition claims must trace to deterministic graph provenance.",
            "component_ids": component_ids,
            "contract_ids": contract_ids,
            "provenance_refs": [first_prov],
            "triggered_by": [],
        },
        {
            "id": "concern.determinism",
            "category": "determinism",
            "description": "Root discovery, component grouping, contracts, and checks are sorted and reproducible.",
            "component_ids": component_ids,
            "contract_ids": [],
            "provenance_refs": [first_prov],
            "triggered_by": [],
        },
        {
            "id": "concern.provenance",
            "category": "provenance",
            "description": "Every component, contract, check, and gap is backed by graph/file provenance.",
            "component_ids": component_ids,
            "contract_ids": contract_ids,
            "provenance_refs": [first_prov],
            "triggered_by": [],
        },
        {
            "id": "concern.no-live-paid-api",
            "category": "no_live_paid_api_acceptance",
            "description": "Generated checks are local candidates and are not acceptance-allowlisted without proof.",
            "component_ids": component_ids,
            "contract_ids": [],
            "provenance_refs": [first_prov],
            "triggered_by": [],
        },
    ]
    if any(node.kind == "protected_surface" or "protected" in node.tags for node in nodes):
        concerns.append(
            {
                "id": "concern.protected-surface-integrity",
                "category": "protected_surface_integrity",
                "description": "Protected surfaces are detected and excluded from normal component ownership.",
                "component_ids": [],
                "contract_ids": [],
                "provenance_refs": [first_prov],
                "triggered_by": ["protected_surface"],
            }
        )
    if any(node.kind == "generated_surface" or "generated" in node.tags for node in nodes):
        concerns.append(
            {
                "id": "concern.generated-artifact-integrity",
                "category": "generated_artifact_integrity",
                "description": "Generated artifacts are detected and excluded from hand-edit ownership.",
                "component_ids": [],
                "contract_ids": [],
                "provenance_refs": [first_prov],
                "triggered_by": ["generated_surface"],
            }
        )
    return concerns


def _check(*, root: ProjectRoot, kind: str, command: str, description: str, provenance_refs: list[str], component_ids: list[str], safety_status: str = "safe_by_default", safe_to_run_by_default: bool = True) -> dict[str, Any]:
    return {
        "id": _id("check", f"{root.path or 'workspace'} {kind}"),
        "description": description,
        "command": command,
        "execution_dir": root.execution_dir,
        "component_ids": component_ids,
        "contract_ids": [],
        "provenance_refs": provenance_refs,
        "acceptance_command_id": None,
        "safe_to_run_by_default": safe_to_run_by_default,
        "requires_network": False,
        "requires_paid_api": False,
        "safety_status": safety_status,
        "execution_status": "statically_validated",
        "proof_artifact": None,
        "verification_gap_ids": [],
    }


def _read_package_scripts(path: Path) -> dict[str, str]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    scripts = data.get("scripts")
    if not isinstance(scripts, dict):
        return {}
    return {str(key): str(value) for key, value in scripts.items()}


def _script_is_modelable(script_body: str) -> bool:
    lower = script_body.lower()
    return not any(marker in lower for marker in UNSAFE_SCRIPT_MARKERS)


def _node_command(script_name: str, script_body: str) -> str | None:
    if script_name == "test":
        return "npm test -- --run" if "--run" in script_body or "vitest" in script_body else "npm test"
    if script_name in {"build", "typecheck", "lint"}:
        return f"npm run {script_name}"
    return None


def _has_python_tests(nodes: list[GraphNode]) -> bool:
    return any(node.path and node.path.endswith(".py") and _is_test_path(node.path) for node in nodes)


def _has_ruff_config(root_path: Path, root: ProjectRoot) -> bool:
    for manifest in root.manifest_paths:
        if Path(manifest).name != "pyproject.toml":
            continue
        candidate = root_path / "pyproject.toml" if Path(manifest).parent.as_posix() in {".", root.path or "."} else root_path / Path(manifest).name
        try:
            text = candidate.read_text(encoding="utf-8")
        except OSError:
            continue
        if "[tool.ruff" in text:
            return True
    return (root_path / "ruff.toml").exists() or (root_path / ".ruff.toml").exists()


def _should_split_single_package_modules(source_nodes: list[GraphNode], root_path: str) -> bool:
    top_level_parts = set()
    module_files = 0
    for node in source_nodes:
        parts = _source_parts(node.path or "", root_path)
        if not parts:
            continue
        top_level_parts.add(parts[0])
        if len(parts) >= 2 and Path(parts[-1]).suffix in {".py", ".js", ".ts", ".tsx"} and Path(parts[-1]).stem != "__init__":
            module_files += 1
    return len(top_level_parts) == 1 and module_files >= 2


def _source_parts(path: str, root_path: str) -> list[str]:
    rel = _relative_to_root(path, root_path)
    parts = [part for part in Path(rel).parts if part]
    if parts and parts[0] in {"src", "lib"}:
        parts = parts[1:]
    if parts and parts[0] in {"python", "javascript", "typescript"}:
        parts = parts[1:]
    return parts


def _source_seed(path: str, root_path: str, *, split_module_level: bool = False) -> str:
    parts = _source_parts(path, root_path)
    if split_module_level and len(parts) >= 2:
        module_stem = Path(parts[-1]).stem
        if module_stem != "__init__" and Path(parts[-1]).suffix in {".py", ".js", ".ts", ".tsx"}:
            return _slug("-".join([parts[0], module_stem]))
    if len(parts) >= 3:
        return _slug("-".join(parts[:2]))
    if len(parts) >= 2:
        return _slug(parts[0])
    if parts:
        return _slug(Path(parts[0]).stem)
    return "source"


def _non_source_seed(node: GraphNode, root_path: str) -> str:
    if node.kind in CONFIG_KINDS:
        return "tooling"
    if node.kind in DOC_KINDS or (node.path or "").lower().endswith(('.md', '.rst')):
        return "guidance"
    if node.kind in TEST_KINDS or _is_test_path(node.path or ""):
        return "verification"
    rel = _relative_to_root(node.path or node.label, root_path)
    first = Path(rel).parts[0] if Path(rel).parts else "support"
    return _slug(first or "support")


def _source_component_id(root: ProjectRoot, seed: str) -> str:
    if not root.path:
        return _id("component", seed)
    return _id("component", f"{root.path} source {seed}")


def _component_name(root: ProjectRoot, seed: str, role: str) -> str:
    root_label = _title(Path(root.path).name if root.path else "workspace")
    seed_label = _title(seed)
    if role == "source":
        return f"{root_label} {seed_label} behavior"
    return f"{root_label} {seed_label} support"


def _component_responsibility(root: ProjectRoot, seed: str, role: str) -> str:
    toolchain = "/".join(sorted(root.toolchains)) or "source"
    if role == "source":
        return f"Provide the {seed} responsibility within the {toolchain} project root using graph-resolved source evidence."
    return f"Support the {seed} responsibility for the {toolchain} project root with manifest, test, or documentation evidence."


def _add_node(component: ComponentDraft, node: GraphNode) -> None:
    if node.id not in component.owned_node_ids:
        component.owned_node_ids.append(node.id)
    for prov in _node_provs(node):
        if prov and prov not in component.provenance_refs:
            component.provenance_refs.append(prov)


def _first_component_for_root(components: dict[str, ComponentDraft], root_path: str) -> ComponentDraft | None:
    matches = [component for component in components.values() if component.root_path == root_path and component.seed not in {"tooling", "guidance", "verification"}]
    return sorted(matches, key=lambda item: item.id)[0] if matches else None


def _component_for_root_seed(components: dict[str, ComponentDraft], root_path: str, seed: str) -> ComponentDraft | None:
    matches = [component for component in components.values() if component.root_path == root_path and component.seed == seed]
    return sorted(matches, key=lambda item: item.id)[0] if matches else None


def _component_symbols(component: ComponentDraft, node_by_id: dict[str, GraphNode]) -> list[str]:
    symbols: list[str] = []
    for node_id in component.owned_node_ids:
        node = node_by_id.get(node_id)
        if node is None:
            continue
        symbol = node.symbol or node.path or ""
        if not symbol:
            continue
        normalized = symbol.removesuffix(".py").replace("/", ".")
        symbols.append(normalized)
        if node.kind in {"python_function", "python_class", "javascript_function"} and "." in normalized:
            symbols.append(normalized.rsplit(".", 1)[0])
    return sorted(set(symbols))


def _best_target_component(imported: str, symbols_by_component: dict[str, list[str]], *, exclude: str) -> str | None:
    candidates: list[tuple[int, int, str]] = []
    for component_id, symbols in symbols_by_component.items():
        if component_id == exclude:
            continue
        scores = [_target_match_score(imported, symbol) for symbol in symbols]
        scores = [score for score in scores if score > 0]
        if scores:
            candidates.append((max(scores), max(len(symbol) for symbol in symbols if _target_match_score(imported, symbol) > 0), component_id))
    if not candidates:
        return None
    return sorted(candidates, key=lambda item: (-item[0], -item[1], item[2]))[0][2]


def _target_match_score(imported: str, component_symbol: str) -> int:
    imported = imported.strip().removesuffix(".__init__")
    component_symbol = component_symbol.strip().removesuffix(".__init__")
    if not imported or not component_symbol:
        return 0
    if imported == component_symbol:
        return 3_000 + len(component_symbol)
    if imported.startswith(component_symbol + "."):
        return 2_000 + len(component_symbol)
    if "." in imported and component_symbol.endswith("." + imported):
        return 1_500 + len(imported)
    if component_symbol.startswith(imported + "."):
        return 1_000 + len(imported)
    return 0


def _target_module_matches(imported: str, component_symbol: str) -> bool:
    imported = imported.strip().removesuffix(".__init__")
    component_symbol = component_symbol.strip().removesuffix(".__init__")
    if not imported or not component_symbol:
        return False
    return (
        imported == component_symbol
        or component_symbol.startswith(imported + ".")
        or imported.startswith(component_symbol + ".")
        or ("." in imported and component_symbol.endswith("." + imported))
    )


def _edge_import_target(edge: GraphEdge) -> str:
    for prefix in ("node:python_import:", "node:javascript_import:"):
        if edge.to_node_id.startswith(prefix):
            return edge.to_node_id.removeprefix(prefix)
    return edge.label if edge.kind == "imports" else ""


def _nearest_root_path(path: str | None, root_by_path: dict[str, ProjectRoot]) -> str | None:
    if not path:
        return None
    matches = [root_path for root_path in root_by_path if _path_in_root(path, root_path)]
    if not matches:
        return None
    return sorted(matches, key=lambda item: (item.count("/"), len(item), item), reverse=True)[0]


def _path_in_root(path: str, root_path: str) -> bool:
    return not root_path or path == root_path or path.startswith(root_path.rstrip("/") + "/")


def _relative_to_root(path: str, root_path: str) -> str:
    if root_path and _path_in_root(path, root_path):
        return path.removeprefix(root_path.rstrip("/") + "/")
    return path


def _is_test_path(path: str) -> bool:
    name = Path(path).name
    return "/tests/" in f"/{path}" or name.startswith("test_") or ".test." in name or ".spec." in name


def _is_import_placeholder(node: GraphNode) -> bool:
    return node.id.startswith("node:python_import:") or node.id.startswith("node:javascript_import:")


def _is_excluded(node: GraphNode) -> bool:
    return node.kind in {"protected_surface", "generated_surface"} or bool(set(node.tags) & EXCLUDED_TAGS)


def _first_prov_for_paths(nodes: list[GraphNode], paths: list[str]) -> str | None:
    wanted = set(paths)
    for node in sorted(nodes, key=lambda item: item.id):
        if node.path in wanted:
            return _node_provs(node)[0] if _node_provs(node) else None
    return None


def _first_prov(nodes: list[GraphNode]) -> str | None:
    for node in sorted(nodes, key=lambda item: item.id):
        refs = _node_provs(node)
        if refs:
            return refs[0]
    return None


def _first_graph_provenance(nodes: list[GraphNode]) -> str:
    return _first_prov(nodes) or ""


def _node_provs(node: GraphNode) -> list[str]:
    return [ref.id for ref in node.provenance_refs if ref.id]


def _edge_provs(edge: GraphEdge) -> list[str]:
    return [ref.id for ref in edge.provenance_refs if ref.id]


def _component_provs(components: Any) -> list[str]:
    refs: list[str] = []
    for component in components:
        for ref in component.provenance_refs:
            if ref not in refs:
                refs.append(ref)
    return refs[:5]


def _unique(values: list[str]) -> list[str]:
    result: list[str] = []
    for value in values:
        if value and value not in result:
            result.append(value)
    return result


def _id(prefix: str, raw: str) -> str:
    slug = _slug(raw)
    if len(slug) > 72:
        slug = f"{slug[:63].rstrip('-')}-{hashlib.sha256(raw.encode()).hexdigest()[:8]}"
    return f"{prefix}.{slug}"


def _slug(raw: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", raw.lower()).strip("-") or "workspace"


def _title(raw: str) -> str:
    return " ".join(part.capitalize() for part in re.split(r"[^a-z0-9]+", raw.lower()) if part) or "Workspace"
