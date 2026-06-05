from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from arena.project_graph import ProjectGraph


def load_recorded_model_output(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def build_fixture_model_output(graph: ProjectGraph, *, project_id: str, goal: str, non_goals: list[str]) -> dict[str, Any]:
    nodes = list(graph.nodes)
    edges = list(graph.edges)
    module_nodes = [
        node
        for node in nodes
        if node.kind in {"python_module", "javascript_module"}
        and node.path
        and not node.path.startswith("tests/")
        and not node.path.endswith("/__init__.py")
        and not any(tag in node.tags for tag in {"excluded_from_primary_context", "protected", "generated"})
    ]
    python_symbols = sorted(module_nodes, key=lambda node: node.symbol or node.label)
    if not python_symbols:
        python_symbols = [
            node
            for node in nodes
            if node.kind in {"python_function", "python_class", "javascript_function"}
            and node.path
            and not node.path.startswith("tests/")
            and not any(tag in node.tags for tag in {"excluded_from_primary_context", "protected", "generated"})
        ]
    if not python_symbols:
        python_symbols = [node for node in nodes if node.kind == "project"]

    module_map = {str(node.symbol or node.label): node for node in python_symbols}
    contract_priority: list[Any] = []
    for edge in edges:
        if edge.kind != "imports":
            continue
        imported = _import_symbol_from_edge(edge)
        if imported is None:
            continue
        from_node = next((node for node in nodes if node.id == edge.from_node_id), None)
        if from_node is None:
            continue
        from_module = _component_module(from_node)
        target_module = _best_import_target(imported, module_map.keys(), from_module)
        if from_module in module_map and target_module and from_module != target_module:
            for module in (from_module, target_module):
                node = module_map[module]
                if node not in contract_priority:
                    contract_priority.append(node)
    selected = (contract_priority + [node for node in python_symbols if node not in contract_priority])[:8]
    first_prov = _first_prov(selected[0])
    test_nodes = [node for node in nodes if node.kind == "test_file"]
    check_prov = _first_prov(test_nodes[0]) if test_nodes else first_prov
    check_command = "uv run pytest -q" if test_nodes else "uv run python -m pytest -q"

    components: list[dict[str, Any]] = []
    module_to_component: dict[str, str] = {}
    for node in selected:
        module = _component_module(node)
        component_id = _id("component", module or node.label)
        component = {
            "id": component_id,
            "name": _title(module or node.label, suffix=" responsibility"),
            "responsibility": f"Own the responsibility represented by `{node.symbol or node.label}` and expose it through graph-resolvable code evidence.",
            "owned_node_ids": [node.id],
            "provenance_refs": [_first_prov(node)],
            "contract_ids": [],
            "check_ids": ["check.local-tests"],
            "verification_gap_ids": [],
        }
        components.append(component)
        if module:
            module_to_component[module] = component_id

    contracts: list[dict[str, Any]] = []
    for edge in edges:
        if edge.kind != "imports":
            continue
        imported = _import_symbol_from_edge(edge)
        if imported is None:
            continue
        from_node = next((node for node in nodes if node.id == edge.from_node_id), None)
        if from_node is None:
            continue
        from_module = _component_module(from_node)
        from_component = module_to_component.get(from_module)
        to_component = None
        target_module = _best_import_target(imported, module_to_component.keys(), from_module)
        if target_module:
            to_component = module_to_component[target_module]
        if not from_component or not to_component or from_component == to_component:
            continue
        contract_id = _id("contract", f"{from_component}-{to_component}")
        contracts.append(
            {
                "id": contract_id,
                "name": f"{from_component} imports {to_component}",
                "from_component_id": from_component,
                "to_component_id": to_component,
                "supporting_edge_ids": [edge.id],
                "near_neighbor_alternative_ids": ["near.primary-path-bucket"],
                "provenance_refs": [
                    _first_prov(from_node),
                    _first_prov(next(node for node in selected if module_to_component.get(_component_module(node)) == to_component)),
                ],
            }
        )
        for component in components:
            if component["id"] in {from_component, to_component} and contract_id not in component["contract_ids"]:
                component["contract_ids"].append(contract_id)
        break

    concerns = [
        {
            "id": "concern.anti-fabrication",
            "category": "anti_fabrication",
            "description": "Accepted decomposition claims must trace to graph provenance.",
            "component_ids": [component["id"] for component in components],
            "contract_ids": [contract["id"] for contract in contracts],
            "provenance_refs": [first_prov],
            "triggered_by": [],
        },
        {
            "id": "concern.determinism",
            "category": "determinism",
            "description": "Snapshot artifacts are canonical and gateable without live APIs.",
            "component_ids": [component["id"] for component in components],
            "contract_ids": [],
            "provenance_refs": [first_prov],
            "triggered_by": [],
        },
        {
            "id": "concern.provenance",
            "category": "provenance",
            "description": "Graph-derived evidence backs each accepted component and contract.",
            "component_ids": [component["id"] for component in components],
            "contract_ids": [contract["id"] for contract in contracts],
            "provenance_refs": [first_prov],
            "triggered_by": [],
        },
        {
            "id": "concern.no-live-paid-api",
            "category": "no_live_paid_api_acceptance",
            "description": "Acceptance checks are local and allowlisted.",
            "component_ids": [component["id"] for component in components],
            "contract_ids": [],
            "provenance_refs": [check_prov],
            "triggered_by": [],
        },
    ]
    if any(node.kind == "protected_surface" or "protected" in node.tags for node in nodes):
        concerns.append(
            {
                "id": "concern.protected-surface-integrity",
                "category": "protected_surface_integrity",
                "description": "Protected surfaces are detected and excluded from arena hypothesis ownership.",
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

    near_target = contracts[0]["id"] if contracts else components[0]["id"]
    probe_contract_ids = [contracts[0]["id"]] if contracts else []
    return {
        "model_id": "fixture-good-model",
        "project_id": project_id,
        "goal": goal,
        "non_goals": non_goals,
        "components": components,
        "contracts": contracts,
        "cross_cutting_concerns": concerns,
        "observable_checks": [
            {
                "id": "check.local-tests",
                "description": "Run the local deterministic test suite or nearest safe local check.",
                "command": check_command,
                "component_ids": [component["id"] for component in components],
                "contract_ids": [contract["id"] for contract in contracts],
                "provenance_refs": [check_prov],
                "acceptance_command_id": "local-pytest",
                "safe_to_run_by_default": True,
                "requires_network": False,
                "requires_paid_api": False,
            }
        ],
        "held_out_probes": [
            {
                "id": "probe.primary-file-bucket-negative",
                "target_component_ids": [components[0]["id"]],
                "target_contract_ids": probe_contract_ids,
                "builder_model_id": "fixture-independent-probe-builder",
                "builder_prompt_hash": "fixture-probe-hash",
                "builder_independent_from_decomposer": True,
                "planted_negative_id": "negative.fluent-file-bucket",
                "discrimination_passed": True,
                "golden_control_passed": True,
                "hidden_from_primary_decomposer": True,
                "provenance_refs": [first_prov],
            }
        ],
        "verification_gaps": [],
        "near_neighbor_alternatives": [
            {
                "id": "near.primary-path-bucket",
                "target_id": near_target,
                "alternative": "Treat adjacent files as one polished bucket.",
                "why_not_primary": f"The goal requires responsibility-bearing components, and the non-goal forbids file buckets: {non_goals[0] if non_goals else 'no file buckets'}.",
                "provenance_refs": [first_prov],
            }
        ],
        "acceptance_command_allowlist": ["local-pytest"],
    }


def build_noop_model_output(graph: ProjectGraph, *, project_id: str, goal: str, non_goals: list[str]) -> dict[str, Any]:
    project_node = next(node for node in graph.nodes if node.kind == "project")
    prov = _first_prov(project_node)
    return {
        "model_id": "noop-no-live-model",
        "project_id": project_id,
        "goal": goal,
        "non_goals": non_goals,
        "components": [],
        "contracts": [],
        "cross_cutting_concerns": [],
        "observable_checks": [],
        "held_out_probes": [],
        "verification_gaps": [
            {
                "id": "gap.no-model-output",
                "description": "No model output was provided; semantic decomposition remains unverified.",
                "severity": "blocker",
                "component_ids": [],
                "contract_ids": [],
                "provenance_refs": [prov],
            }
        ],
        "near_neighbor_alternatives": [],
        "acceptance_command_allowlist": [],
    }


def _first_prov(node: Any) -> str:
    return node.provenance_refs[0].id if getattr(node, "provenance_refs", None) else ""


def _component_module(node: Any) -> str:
    symbol = str(getattr(node, "symbol", None) or getattr(node, "label", ""))
    kind = str(getattr(node, "kind", ""))
    if kind in {"python_module", "javascript_module"}:
        return symbol
    return _module_from_symbol(symbol)


def _import_symbol_from_edge(edge: Any) -> str | None:
    to_node_id = str(getattr(edge, "to_node_id", ""))
    for prefix in ("node:python_import:", "node:javascript_import:"):
        if to_node_id.startswith(prefix):
            return to_node_id.removeprefix(prefix)
    return None


def _best_import_target(imported: str, modules: Any, from_module: str) -> str | None:
    candidates = [
        str(module)
        for module in modules
        if str(module) != from_module
        and (str(module) == imported or str(module).startswith(imported + ".") or imported.startswith(str(module) + "."))
    ]
    if not candidates:
        return None
    exact = [module for module in candidates if module == imported]
    if exact:
        return exact[0]
    return max(candidates, key=len)


def _module_from_symbol(symbol: str) -> str:
    parts = symbol.split(".")
    if len(parts) <= 1:
        return symbol
    return ".".join(parts[:-1])


def _id(prefix: str, raw: str) -> str:
    import re

    slug = re.sub(r"[^a-z0-9]+", "-", raw.lower()).strip("-") or "project"
    return f"{prefix}.{slug[:48]}"


def _title(raw: str, *, suffix: str = "") -> str:
    clean = raw.replace("_", " ").replace("-", " ").replace(".", " ").strip()
    titled = " ".join(part.capitalize() for part in clean.split()) or "Project"
    return (titled + suffix).strip()
