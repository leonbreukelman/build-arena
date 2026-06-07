from __future__ import annotations

import json
import shlex
from pathlib import Path
from typing import Any

from arena.project_graph import ProjectGraph, graph_to_dict
from arena.project_snapshot import (
    GateReport,
    GateViolation,
    ProjectModelSnapshot,
    gate_report_to_dict,
    snapshot_from_dict,
    snapshot_to_dict,
)

VAGUE_TERMS = {"misc", "miscellaneous", "general", "other", "stuff", "everything", "all", "bucket"}
UNIVERSAL_CONCERNS = {"anti_fabrication", "determinism", "provenance", "no_live_paid_api_acceptance"}
HIGH_IMPACT_EDGE_KINDS = {"calls", "references", "depends_on", "contract_support"}
FILE_BUCKET_KINDS = {"file", "test_file", "config", "protected_surface", "generated_surface", "verification_artifact"}


def run_project_model_gate(snapshot: ProjectModelSnapshot | dict[str, Any], graph: ProjectGraph | dict[str, Any]) -> GateReport:
    snapshot_obj = snapshot_from_dict(snapshot) if isinstance(snapshot, dict) else snapshot
    graph_data = graph_to_dict(graph) if isinstance(graph, ProjectGraph) else graph
    violations: list[GateViolation] = []
    snapshot_data = snapshot_to_dict(snapshot_obj)

    nodes = {node["id"]: node for node in graph_data.get("nodes", [])}
    edges = {edge["id"]: edge for edge in graph_data.get("edges", [])}
    provenance_ids = _provenance_ids(graph_data)
    provenance_sources = _provenance_sources(graph_data)
    components_by_id = {component.id: component for component in snapshot_obj.components}
    component_ids = set(components_by_id)
    contract_ids = {contract.id for contract in snapshot_obj.contracts}
    check_ids = {check.id for check in snapshot_obj.observable_checks}
    gap_ids = {gap.id for gap in snapshot_obj.verification_gaps}
    near_ids = {near.id for near in snapshot_obj.near_neighbor_alternatives}

    def add(gate: str, message: str, location: str, severity: str = "error") -> None:
        violations.append(GateViolation(gate=gate, severity=severity, message=message, location=location))

    if snapshot_obj.schema_version != "project-model-snapshot/v0.1":
        add("schema", "Unsupported snapshot schema version.", "schema_version")
    if not snapshot_obj.goal.strip() or not snapshot_obj.non_goals:
        add("snapshot_goal", "Snapshot must include a goal and at least one non-goal.", "goal/non_goals")
    if not snapshot_obj.components:
        add("inventory_coverage", "Snapshot must contain at least one component.", "components")
    if not snapshot_obj.observable_checks:
        add("component_measurability", "Snapshot must contain at least one observable check.", "observable_checks")

    if snapshot_obj.graph_hash:
        actual_hash = _sha(canonical_graph_json_from_dict(graph_data))
        if snapshot_obj.graph_hash != actual_hash:
            add("snapshot_freshness", "Snapshot graph_hash does not match graph artifact hash.", "graph_hash")

    for component in snapshot_obj.components:
        loc = f"components[{component.id}]"
        lower_name = component.name.lower().replace("-", " ").replace("_", " ")
        if any(term in lower_name.split() for term in VAGUE_TERMS) or component.id.split(".")[-1] in VAGUE_TERMS:
            add("component_measurability", f"Component {component.id} has a vague name.", loc)
        if len(component.responsibility.split()) < 6:
            add("component_measurability", f"Component {component.id} has an underspecified responsibility.", loc)
        if _looks_like_responsibility_file_bucket(component.responsibility):
            add("component_measurability", f"Component {component.id} responsibility reads like a path/file-bucket decomposition rather than a semantic responsibility.", loc)
        if not component.owned_node_ids:
            add("inventory_coverage", f"Component {component.id} owns no graph nodes.", loc)
        for node_id in component.owned_node_ids:
            if node_id not in nodes:
                add("inventory_coverage", f"Component {component.id} references unknown graph node {node_id}.", loc)
        if not component.provenance_refs:
            add("provenance_completeness", f"Component {component.id} has no provenance.", loc)
        for prov in component.provenance_refs:
            if prov not in provenance_ids:
                add("transitive_source_provenance", f"Component {component.id} provenance {prov} does not resolve to graph provenance.", loc)
            elif _provenance_is_protected_or_generated(provenance_sources.get(prov, {})):
                add("protected_surfaces", f"Component {component.id} claims protected/generated provenance {prov}.", loc)
        if not (component.contract_ids or component.check_ids or component.verification_gap_ids):
            add("component_measurability", f"Component {component.id} has no contracts, checks, or gaps.", loc)
        for contract_id in component.contract_ids:
            if contract_id not in contract_ids:
                add("contract_references", f"Component {component.id} references missing contract {contract_id}.", loc)
        for check_id in component.check_ids:
            if check_id not in check_ids:
                add("component_measurability", f"Component {component.id} references missing check {check_id}.", loc)
        for gap_id in component.verification_gap_ids:
            if gap_id not in gap_ids:
                add("verification_gaps", f"Component {component.id} references missing verification gap {gap_id}.", loc)
        owned_nodes = [nodes[node_id] for node_id in component.owned_node_ids if node_id in nodes]
        owned_kinds = {node.get("kind", "") for node in owned_nodes}
        if len(owned_nodes) >= 2 and owned_kinds <= FILE_BUCKET_KINDS and not component.verification_gap_ids:
            add(
                "component_measurability",
                f"Component {component.id} is a fluent file-bucket: sibling files without symbol/contract/check-resolved ownership.",
                loc,
            )
        for node in owned_nodes:
            if node.get("kind") in {"protected_surface", "generated_surface"} or "protected" in node.get("tags", []) or "generated" in node.get("tags", []):
                add("protected_surfaces", f"Component {component.id} owns protected/generated surface {node.get('path') or node.get('id')}.", loc)

    for contract in snapshot_obj.contracts:
        loc = f"contracts[{contract.id}]"
        if contract.from_component_id not in component_ids or contract.to_component_id not in component_ids:
            add("contract_references", f"Contract {contract.id} references unknown component endpoint.", loc)
        elif contract.from_component_id == contract.to_component_id:
            add("contract_references", f"Contract {contract.id} is self-referential after component merge.", loc)
        if not contract.supporting_edge_ids:
            add("contract_references", f"Contract {contract.id} has no supporting graph edges.", loc)
        for edge_id in contract.supporting_edge_ids:
            edge = edges.get(edge_id)
            if edge is None:
                add("contract_references", f"Contract {contract.id} references missing edge {edge_id}.", loc)
                continue
            if edge.get("kind") in HIGH_IMPACT_EDGE_KINDS and (edge.get("confidence") != "deterministic" or edge.get("derived_by") == "model_output"):
                add("contract_references", f"Contract {contract.id} uses LLM-only high-impact edge {edge_id} without a verification gap.", loc)
            from_component = components_by_id.get(contract.from_component_id)
            to_component = components_by_id.get(contract.to_component_id)
            if from_component is not None and to_component is not None and not _edge_supports_contract(edge, nodes, from_component, to_component):
                add(
                    "contract_references",
                    f"Contract {contract.id} supporting edge {edge_id} does not connect the declared from/to components.",
                    loc,
                )
        for near_id in contract.near_neighbor_alternative_ids:
            if near_id not in near_ids:
                add("near_neighbor_alternatives", f"Contract {contract.id} references missing near-neighbor {near_id}.", loc)
        _check_provenance(contract.provenance_refs, provenance_ids, "provenance_completeness", loc, add)

    _check_owned_import_edge_coverage(snapshot_obj, nodes, edges, add)

    concern_categories = {concern.category for concern in snapshot_obj.cross_cutting_concerns}
    missing_universal = UNIVERSAL_CONCERNS - concern_categories
    if missing_universal:
        add("cross_cutting_concerns", f"Missing universal concerns: {', '.join(sorted(missing_universal))}.", "cross_cutting_concerns")
    if any(node.get("kind") == "protected_surface" or "protected" in node.get("tags", []) for node in nodes.values()) and "protected_surface_integrity" not in concern_categories:
        add("cross_cutting_concerns", "Protected surfaces exist but protected_surface_integrity concern is missing.", "cross_cutting_concerns")
    if any(node.get("kind") == "generated_surface" or "generated" in node.get("tags", []) for node in nodes.values()) and "generated_artifact_integrity" not in concern_categories:
        add("cross_cutting_concerns", "Generated surfaces exist but generated_artifact_integrity concern is missing.", "cross_cutting_concerns")
    for universal_category in ("anti_fabrication", "provenance"):
        covered_components = {
            component_id
            for concern in snapshot_obj.cross_cutting_concerns
            if concern.category == universal_category
            for component_id in concern.component_ids
        }
        missing_components = component_ids - covered_components
        if missing_components:
            add(
                "cross_cutting_concerns",
                f"Universal concern {universal_category} does not cover components: {', '.join(sorted(missing_components))}.",
                "cross_cutting_concerns",
            )
    for concern in snapshot_obj.cross_cutting_concerns:
        loc = f"cross_cutting_concerns[{concern.id}]"
        for component_id in concern.component_ids:
            if component_id not in component_ids:
                add("cross_cutting_concerns", f"Concern {concern.id} references unknown component {component_id}.", loc)
        for contract_id in concern.contract_ids:
            if contract_id not in contract_ids:
                add("cross_cutting_concerns", f"Concern {concern.id} references unknown contract {contract_id}.", loc)
        _check_provenance(concern.provenance_refs, provenance_ids, "provenance_completeness", loc, add)

    allowlist = set(snapshot_obj.acceptance_command_allowlist)
    owned_node_ids = {node_id for component in snapshot_obj.components for node_id in component.owned_node_ids}
    owned_symbols = {
        str(nodes[node_id].get("symbol") or nodes[node_id].get("path") or "")
        for node_id in owned_node_ids
        if node_id in nodes
    }
    gap_provenance_refs = {ref for gap in snapshot_obj.verification_gaps for ref in gap.provenance_refs}
    for node in _primary_inventory_nodes(nodes):
        if node["id"] in owned_node_ids or _module_has_owned_descendant(node, owned_symbols):
            continue
        node_provenance = {str(ref.get("id")) for ref in node.get("provenance_refs", [])}
        if node_provenance & gap_provenance_refs:
            continue
        add(
            "inventory_coverage",
            f"Primary source node {node.get('symbol') or node.get('path') or node.get('id')} is neither component-owned nor covered by a verification gap.",
            f"graph.nodes[{node.get('id')}]",
        )
    for check in snapshot_obj.observable_checks:
        loc = f"observable_checks[{check.id}]"
        if check.acceptance_command_id and check.acceptance_command_id not in allowlist:
            add("no_live_paid_api_acceptance", f"Check {check.id} is not in acceptance allowlist.", loc)
        if check.acceptance_command_id and (check.requires_network or check.requires_paid_api):
            add("no_live_paid_api_acceptance", f"Check {check.id} requires network or paid API for acceptance.", loc)
        if check.acceptance_command_id:
            unsafe_reason = _unsafe_acceptance_command_reason(check.command)
            if unsafe_reason:
                add("no_live_paid_api_acceptance", f"Check {check.id} command is not safe for local acceptance: {unsafe_reason}.", loc)
        for component_id in check.component_ids:
            if component_id not in component_ids:
                add("component_measurability", f"Check {check.id} references unknown component {component_id}.", loc)
        for contract_id in check.contract_ids:
            if contract_id not in contract_ids:
                add("contract_references", f"Check {check.id} references unknown contract {contract_id}.", loc)
        _check_provenance(check.provenance_refs, provenance_ids, "provenance_completeness", loc, add)

    anchors = [snapshot_obj.goal, *snapshot_obj.non_goals]
    for near in snapshot_obj.near_neighbor_alternatives:
        loc = f"near_neighbor_alternatives[{near.id}]"
        if not any(_shares_significant_word(near.why_not_primary, anchor) for anchor in anchors):
            add("near_neighbor_alternatives", f"Near-neighbor {near.id} does not cite snapshot goal/non-goals.", loc)
        _check_provenance(near.provenance_refs, provenance_ids, "provenance_completeness", loc, add)

    if not snapshot_obj.held_out_probes:
        add("held_out_probe_presence", "Snapshot must include at least one held-out probe or explicit blocker gap.", "held_out_probes")
    for probe in snapshot_obj.held_out_probes:
        loc = f"held_out_probes[{probe.id}]"
        if not probe.builder_independent_from_decomposer or probe.builder_model_id == snapshot_obj.primary_model_id or not probe.hidden_from_primary_decomposer:
            add("held_out_probe_isolation", f"Probe {probe.id} is not isolated from the primary decomposer.", loc)
        if not probe.planted_negative_id or not probe.discrimination_passed:
            add("held_out_probe_discrimination", f"Probe {probe.id} did not discriminate against an independent planted negative.", loc)
        if not probe.golden_control_passed:
            add("held_out_probe_discrimination", f"Probe {probe.id} failed the known-good false-positive control.", loc)
        _check_provenance(probe.provenance_refs, provenance_ids, "provenance_completeness", loc, add)

    for gap in snapshot_obj.verification_gaps:
        if gap.severity not in {"low", "medium", "high", "blocker"}:
            add("verification_gaps", f"Gap {gap.id} has unsupported severity.", f"verification_gaps[{gap.id}]")
        _check_provenance(gap.provenance_refs, provenance_ids, "provenance_completeness", f"verification_gaps[{gap.id}]", add)

    # The snapshot dict is intentionally touched to make schema drift visible during debugging.
    if not isinstance(snapshot_data, dict):
        add("schema", "Snapshot could not be serialized.", "snapshot")
    return GateReport(passed=not violations, violations=violations)


def run_project_model_gate_from_manifest(manifest_path: str | Path) -> GateReport:
    manifest_path = Path(manifest_path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    base = manifest_path.parent
    snapshot = json.loads((base / manifest["snapshot_path"]).read_text(encoding="utf-8"))
    graph = json.loads((base / manifest["graph_path"]).read_text(encoding="utf-8"))
    return run_project_model_gate(snapshot, graph)


def write_gate_report(path: str | Path, report: GateReport) -> None:
    Path(path).write_text(json.dumps(gate_report_to_dict(report), sort_keys=True, indent=2) + "\n", encoding="utf-8")


def canonical_graph_json_from_dict(graph: dict[str, Any]) -> str:
    return json.dumps(graph, sort_keys=True, separators=(",", ":"))


def _sha(text: str) -> str:
    import hashlib

    return hashlib.sha256(text.encode()).hexdigest()


def _provenance_ids(graph_data: dict[str, Any]) -> set[str]:
    ids: set[str] = set()
    for node in graph_data.get("nodes", []):
        for ref in node.get("provenance_refs", []):
            ids.add(str(ref.get("id")))
    for edge in graph_data.get("edges", []):
        for ref in edge.get("provenance_refs", []):
            ids.add(str(ref.get("id")))
    return ids


def _provenance_sources(graph_data: dict[str, Any]) -> dict[str, dict[str, Any]]:
    sources: dict[str, dict[str, Any]] = {}
    for node in graph_data.get("nodes", []):
        for ref in node.get("provenance_refs", []):
            sources[str(ref.get("id"))] = {"kind": node.get("kind"), "tags": node.get("tags", []), "path": node.get("path"), "node_id": node.get("id")}
    for edge in graph_data.get("edges", []):
        for ref in edge.get("provenance_refs", []):
            sources.setdefault(str(ref.get("id")), {"kind": "edge", "tags": [], "edge_id": edge.get("id")})
    return sources


def _provenance_is_protected_or_generated(source: dict[str, Any]) -> bool:
    tags = set(source.get("tags", []))
    return source.get("kind") in {"protected_surface", "generated_surface"} or bool(tags & {"protected", "generated"})


def _check_provenance(refs: list[str], provenance_ids: set[str], gate: str, loc: str, add: Any) -> None:
    if not refs:
        add(gate, "Object has no provenance refs.", loc)
        return
    for ref in refs:
        if ref not in provenance_ids:
            add("transitive_source_provenance", f"Provenance {ref} does not resolve to graph/file evidence.", loc)


def _primary_inventory_nodes(nodes: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    primary_kinds = {"python_module", "javascript_module"}
    excluded_tags = {"excluded_from_primary_context", "protected", "generated", "symlink"}
    result: list[dict[str, Any]] = []
    for node in nodes.values():
        if node.get("kind") not in primary_kinds:
            continue
        tags = set(node.get("tags", []))
        if tags & excluded_tags:
            continue
        path = str(node.get("path") or "")
        if path.startswith("tests/") or "/tests/" in path or Path(path).name.startswith("test_"):
            continue
        if path.startswith("dashboard/src/lib/generated/") or path.endswith(".d.ts"):
            continue
        result.append(node)
    return result


def _module_has_owned_descendant(node: dict[str, Any], owned_symbols: set[str]) -> bool:
    symbol = str(node.get("symbol") or "").strip().removesuffix(".__init__")
    if not symbol:
        return False
    return any(owned == symbol or owned.startswith(symbol + ".") for owned in owned_symbols)


def _unsafe_acceptance_command_reason(command: str) -> str | None:
    text = command.strip()
    if not text:
        return "empty command"
    if "\n" in text or any(token in text for token in (";", "|", "`", "$(", ">", "<")):
        return "contains shell control syntax outside the allowed && chain"
    if "&" in text.replace("&&", ""):
        return "contains standalone background operator"
    upper = text.upper()
    if any(marker in upper for marker in ("API_KEY", "TOKEN", "SECRET", "PASSWORD", "PASSWD")) and "$" in text:
        return "references credential-shaped environment variables"
    parts = [part.strip() for part in text.split("&&")]
    if not parts or any(not part for part in parts):
        return "contains an empty && segment"
    for part in parts:
        try:
            argv = shlex.split(part)
        except ValueError as exc:
            return f"cannot parse command segment: {exc}"
        if not argv:
            return "empty command segment"
        denied = {"curl", "wget", "ssh", "scp", "rsync", "gh", "gcloud", "aws", "az", "kubectl", "claude", "grok"}
        if argv[0] in denied:
            return f"uses nonlocal/live-capable tool {argv[0]!r}"
        if not _is_allowed_local_command(argv):
            return f"segment {part!r} is not on the deterministic local command allowlist"
    return None


def _is_allowed_local_command(argv: list[str]) -> bool:
    joined = " ".join(argv)
    prefixes = (
        "uv run pytest",
        "uv run python -m pytest",
        "uv run python -m arena.project_model_cli",
        "uv run python scripts/",
        "uv run ruff check",
        "uv run mypy",
        "uv run pyright",
        "python3 scripts/",
        "npm run build",
        "npm run check:links",
        "npm test",
        "make generated",
        "make test",
    )
    return any(joined == prefix or joined.startswith(prefix + " ") for prefix in prefixes)


def _looks_like_responsibility_file_bucket(text: str) -> bool:
    lower = text.lower()
    path_markers = (".py", ".js", ".ts", ".json", "arena/", "src/", "tests/", "docs/", "worker/", "scripts/")
    bucket_markers = ("contains", "own the files", "owns the files", "file bucket", "file-bucket", "path bucket", "path-bucket", "path classifier", "path-classifier", "directory bucket")
    has_path_marker = any(marker in lower for marker in path_markers)
    return (any(marker in lower for marker in bucket_markers) and has_path_marker) or (lower.startswith("contains ") and has_path_marker)


def _check_owned_import_edge_coverage(snapshot_obj: ProjectModelSnapshot, nodes: dict[str, dict[str, Any]], edges: dict[str, dict[str, Any]], add: Any) -> None:
    components = {component.id: component for component in snapshot_obj.components}
    contracts = list(snapshot_obj.contracts)
    for edge in edges.values():
        if edge.get("kind") != "imports":
            continue
        candidates = _component_pairs_for_import_edge(edge, nodes, components)
        for from_id, to_id in candidates:
            if from_id == to_id:
                continue
            if any(contract.from_component_id == from_id and contract.to_component_id == to_id for contract in contracts):
                continue
            add(
                "edge_coverage",
                f"Owned import edge {edge.get('id')} from {from_id} to {to_id} is not covered by any contract between those components.",
                f"edges[{edge.get('id')}]",
            )


def _component_pairs_for_import_edge(edge: dict[str, Any], nodes: dict[str, dict[str, Any]], components: dict[str, Any]) -> list[tuple[str, str]]:
    edge_from = nodes.get(str(edge.get("from_node_id")), {})
    edge_from_symbol = str(edge_from.get("symbol") or edge_from.get("path") or "")
    imported = _edge_import_target(edge)
    if not edge_from_symbol or not imported:
        return []
    from_ids = [component_id for component_id, component in components.items() if any(_source_module_matches(edge_from_symbol, symbol) for symbol in _component_symbols(component, nodes))]
    to_ids = [component_id for component_id, component in components.items() if any(_edge_coverage_target_matches(imported, symbol) for symbol in _component_symbols(component, nodes))]
    return [(from_id, to_id) for from_id in from_ids for to_id in to_ids]


def _edge_supports_contract(edge: dict[str, Any], nodes: dict[str, dict[str, Any]], from_component: Any, to_component: Any) -> bool:
    from_symbols = _component_symbols(from_component, nodes)
    to_symbols = _component_symbols(to_component, nodes)
    edge_from = nodes.get(str(edge.get("from_node_id")), {})
    edge_from_symbol = str(edge_from.get("symbol") or edge_from.get("path") or "")
    from_ok = str(edge.get("from_node_id")) in set(from_component.owned_node_ids) or any(_source_module_matches(edge_from_symbol, symbol) for symbol in from_symbols)
    imported = _edge_import_target(edge)
    if imported:
        to_ok = any(_target_module_matches(imported, symbol) for symbol in to_symbols)
    else:
        to_ok = str(edge.get("to_node_id")) in set(to_component.owned_node_ids)
    return from_ok and to_ok


def _component_symbols(component: Any, nodes: dict[str, dict[str, Any]]) -> list[str]:
    symbols: list[str] = []
    for node_id in component.owned_node_ids:
        node = nodes.get(str(node_id), {})
        symbol = str(node.get("symbol") or node.get("path") or "")
        if symbol:
            normalized = symbol.removesuffix(".py").replace("/", ".")
            symbols.append(normalized)
            if node.get("kind") in {"python_function", "python_class", "javascript_function"} and "." in normalized:
                symbols.append(normalized.rsplit(".", 1)[0])
    return symbols


def _edge_import_target(edge: dict[str, Any]) -> str:
    to_node_id = str(edge.get("to_node_id") or "")
    for prefix in ("node:python_import:", "node:javascript_import:"):
        if to_node_id.startswith(prefix):
            return to_node_id.removeprefix(prefix)
    return str(edge.get("label") or "") if edge.get("kind") == "imports" else ""


def _source_module_matches(edge_source: str, component_symbol: str) -> bool:
    edge_source = edge_source.strip().removesuffix(".__init__")
    component_symbol = component_symbol.strip().removesuffix(".__init__")
    if not edge_source or not component_symbol:
        return False
    return edge_source == component_symbol or edge_source.startswith(component_symbol + ".")


def _target_module_matches(imported: str, component_symbol: str) -> bool:
    imported = imported.strip().removesuffix(".__init__")
    component_symbol = component_symbol.strip().removesuffix(".__init__")
    if not imported or not component_symbol:
        return False
    return imported == component_symbol or component_symbol.startswith(imported + ".") or imported.startswith(component_symbol + ".")


def _edge_coverage_target_matches(imported: str, component_symbol: str) -> bool:
    imported = imported.strip().removesuffix(".__init__")
    component_symbol = component_symbol.strip().removesuffix(".__init__")
    if not imported or not component_symbol:
        return False
    return imported == component_symbol or imported.startswith(component_symbol + ".")


def _shares_significant_word(text: str, anchor: str) -> bool:
    text_words = {word for word in _words(text) if len(word) >= 5}
    anchor_words = {word for word in _words(anchor) if len(word) >= 5}
    return bool(text_words & anchor_words)


def _words(text: str) -> list[str]:
    import re

    return re.findall(r"[a-z0-9]+", text.lower())
