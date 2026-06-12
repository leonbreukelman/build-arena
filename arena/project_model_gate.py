from __future__ import annotations

import copy
import json
import shlex
from pathlib import Path
from typing import Any

from arena.project_graph import ProjectGraph, graph_to_dict
from arena.project_snapshot import (
    Contract,
    GateReport,
    GateViolation,
    ProjectModelSnapshot,
    gate_report_to_dict,
    snapshot_from_dict,
    snapshot_to_dict,
    stable_hash_json,
)

VAGUE_TERMS = {"misc", "miscellaneous", "general", "other", "stuff", "everything", "all", "bucket"}
UNIVERSAL_CONCERNS = {"anti_fabrication", "determinism", "provenance", "no_live_paid_api_acceptance"}
HIGH_IMPACT_EDGE_KINDS = {"calls", "references", "depends_on", "contract_support"}
FILE_BUCKET_KINDS = {"file", "test_file", "config", "protected_surface", "generated_surface", "verification_artifact"}
PROBE_PROOF_SCHEMA_VERSION = "arena.project_probe_proof/v0.1"


def run_project_model_gate(
    snapshot: ProjectModelSnapshot | dict[str, Any],
    graph: ProjectGraph | dict[str, Any],
    *,
    proof_artifact_base: str | Path | None = None,
    _validate_probe_proofs: bool = True,
) -> GateReport:
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
        _check_observable_execution_metadata(check, gap_ids, add, loc)
        if check.acceptance_command_id and check.acceptance_command_id not in allowlist:
            add("no_live_paid_api_acceptance", f"Check {check.id} is not in acceptance allowlist.", loc)
        if check.acceptance_command_id and (check.requires_network or check.requires_paid_api):
            add("no_live_paid_api_acceptance", f"Check {check.id} requires network or paid API for acceptance.", loc)
        if check.acceptance_command_id and (not check.safe_to_run_by_default or check.safety_status != "safe_by_default"):
            add("no_live_paid_api_acceptance", f"Check {check.id} is not safe-by-default for acceptance.", loc)
        if check.acceptance_command_id and check.execution_status != "execution_proven" and not check.proof_artifact:
            add("observable_check_execution", f"Check {check.id} must be execution-proven or carry a proof artifact before acceptance.", loc)
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

    if not snapshot_obj.held_out_probes and not _has_explicit_unproven_probe_gap(snapshot_obj.verification_gaps):
        add("held_out_probe_presence", "Snapshot must include at least one held-out probe or an explicit semantic/probe validation gap.", "held_out_probes")
    for probe in snapshot_obj.held_out_probes:
        loc = f"held_out_probes[{probe.id}]"
        _check_held_out_probe_metadata(
            probe,
            gap_ids,
            snapshot_obj.primary_model_id,
            add,
            loc,
            snapshot_obj=snapshot_obj,
            graph_data=graph_data,
            proof_artifact_base=proof_artifact_base,
            validate_probe_proofs=_validate_probe_proofs,
        )
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
    return run_project_model_gate(snapshot, graph, proof_artifact_base=base)


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


# Public alias: single source of truth for "which modules the inventory gate scores".
# The decomposer prompt imports this so the prompt's coverage list cannot drift from
# what the gate actually checks.
def primary_inventory_nodes(nodes: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    return _primary_inventory_nodes(nodes)


def close_import_contracts_for_gate(
    snapshot: ProjectModelSnapshot,
    graph: ProjectGraph | dict[str, Any],
) -> ProjectModelSnapshot:
    """Deterministically close mechanical import contracts for gate evaluation.

    The LLM remains responsible for component ownership and semantic
    responsibilities. Given that ownership, import-edge direction and
    cross-component contract coverage are mechanical facts already computed by
    this gate module. This helper preserves valid model contracts, removes
    invalid supporting-edge claims, and adds stable ``contract.auto.<edge>``
    contracts only for import edges whose endpoints map to existing components
    and whose contract can carry provenance. It never invents components,
    reassigns ownership, relaxes the gate, or mutates raw model output.
    """

    graph_data = graph_to_dict(graph) if isinstance(graph, ProjectGraph) else graph
    nodes = {node["id"]: node for node in graph_data.get("nodes", [])}
    edges = {edge["id"]: edge for edge in graph_data.get("edges", [])}
    components = {component.id: component for component in snapshot.components}

    kept_contracts: list[Contract] = []
    removed_contract_ids: set[str] = set()
    used_contract_ids: set[str] = set()
    for contract in snapshot.contracts:
        from_component = components.get(contract.from_component_id)
        to_component = components.get(contract.to_component_id)
        valid_edge_ids: list[str] = []
        if from_component is not None and to_component is not None and from_component.id != to_component.id:
            for edge_id in sorted(dict.fromkeys(contract.supporting_edge_ids)):
                edge = edges.get(edge_id)
                if edge is not None and _edge_supports_contract(edge, nodes, from_component, to_component):
                    valid_edge_ids.append(edge_id)
        if valid_edge_ids:
            contract.supporting_edge_ids = valid_edge_ids
            contract.near_neighbor_alternative_ids = sorted(dict.fromkeys(contract.near_neighbor_alternative_ids))
            contract.provenance_refs = sorted(dict.fromkeys(contract.provenance_refs))
            kept_contracts.append(contract)
            used_contract_ids.add(contract.id)
        else:
            removed_contract_ids.add(contract.id)

    snapshot.contracts = kept_contracts
    _remove_contract_references(snapshot, removed_contract_ids)

    for edge in sorted(edges.values(), key=lambda item: str(item.get("id") or "")):
        if edge.get("kind") != "imports":
            continue
        edge_id = str(edge.get("id") or "")
        if not edge_id:
            continue
        for from_id, to_id in sorted(set(_component_pairs_for_import_edge(edge, nodes, components))):
            if from_id == to_id:
                continue
            if any(
                edge_id in contract.supporting_edge_ids
                and contract.from_component_id == from_id
                and contract.to_component_id == to_id
                for contract in snapshot.contracts
            ):
                continue
            provenance_refs = _auto_contract_provenance(edge, components.get(from_id), components.get(to_id))
            if not provenance_refs:
                continue
            contract_id = _unique_auto_contract_id(edge_id, used_contract_ids)
            contract = Contract(
                id=contract_id,
                name=f"Auto import contract {from_id} to {to_id}",
                from_component_id=from_id,
                to_component_id=to_id,
                supporting_edge_ids=[edge_id],
                near_neighbor_alternative_ids=[],
                provenance_refs=provenance_refs,
            )
            snapshot.contracts.append(contract)
            used_contract_ids.add(contract_id)
            for component_id in (from_id, to_id):
                component = components.get(component_id)
                if component is not None and contract_id not in component.contract_ids:
                    component.contract_ids.append(contract_id)

    snapshot.contracts = sorted(snapshot.contracts, key=lambda contract: contract.id)
    _retain_existing_contract_references(snapshot)
    for component in snapshot.components:
        component.contract_ids = sorted(dict.fromkeys(component.contract_ids))
    return snapshot


def _auto_contract_provenance(edge: dict[str, Any], from_component: Any, to_component: Any) -> list[str]:
    refs = [str(ref.get("id")) for ref in edge.get("provenance_refs", []) if isinstance(ref, dict) and ref.get("id")]
    if refs:
        return sorted(dict.fromkeys(refs))
    for component in (from_component, to_component):
        refs = [str(ref) for ref in getattr(component, "provenance_refs", []) if str(ref)]
        if refs:
            return sorted(dict.fromkeys(refs))
    return []


def _remove_contract_references(snapshot: ProjectModelSnapshot, removed_contract_ids: set[str]) -> None:
    if not removed_contract_ids:
        return
    for item in [
        *snapshot.components,
        *snapshot.cross_cutting_concerns,
        *snapshot.observable_checks,
        *snapshot.verification_gaps,
    ]:
        contract_ids = getattr(item, "contract_ids", None)
        if contract_ids is not None:
            item.contract_ids = sorted(
                contract_id for contract_id in dict.fromkeys(contract_ids) if contract_id not in removed_contract_ids
            )
    for contract in snapshot.contracts:
        contract.near_neighbor_alternative_ids = sorted(
            alternative_id
            for alternative_id in dict.fromkeys(contract.near_neighbor_alternative_ids)
            if alternative_id not in removed_contract_ids
        )


def _retain_existing_contract_references(snapshot: ProjectModelSnapshot) -> None:
    existing_contract_ids = {contract.id for contract in snapshot.contracts}
    for item in [
        *snapshot.components,
        *snapshot.cross_cutting_concerns,
        *snapshot.observable_checks,
        *snapshot.verification_gaps,
    ]:
        contract_ids = getattr(item, "contract_ids", None)
        if contract_ids is not None:
            item.contract_ids = sorted(
                contract_id for contract_id in dict.fromkeys(contract_ids) if contract_id in existing_contract_ids
            )
    for contract in snapshot.contracts:
        contract.near_neighbor_alternative_ids = sorted(
            alternative_id
            for alternative_id in dict.fromkeys(contract.near_neighbor_alternative_ids)
            if alternative_id in existing_contract_ids
        )


def _unique_auto_contract_id(edge_id: str, used_ids: set[str]) -> str:
    base = "contract.auto." + edge_id.removeprefix("edge:")
    candidate = base
    suffix = 2
    while candidate in used_ids:
        candidate = f"{base}.{suffix}"
        suffix += 1
    return candidate


def _module_has_owned_descendant(node: dict[str, Any], owned_symbols: set[str]) -> bool:
    symbol = str(node.get("symbol") or "").strip().removesuffix(".__init__")
    if not symbol:
        return False
    return any(owned == symbol or owned.startswith(symbol + ".") for owned in owned_symbols)


def _check_observable_execution_metadata(check: Any, gap_ids: set[str], add: Any, loc: str) -> None:
    allowed_safety = {"safe_by_default", "unsafe", "requires_network", "requires_paid_api", "destructive", "unknown"}
    allowed_execution = {"declared_only", "statically_validated", "execution_proven", "gapped"}
    execution_dir = str(getattr(check, "execution_dir", "") or "").strip()
    if not execution_dir:
        add("observable_check_execution", f"Check {check.id} must declare a non-empty execution directory.", loc)
    else:
        path = Path(execution_dir)
        if path.is_absolute() or any(part == ".." for part in path.parts):
            add("observable_check_execution", f"Check {check.id} execution directory must be workspace-relative.", loc)
    if check.safety_status not in allowed_safety:
        add("observable_check_execution", f"Check {check.id} has unsupported safety status {check.safety_status!r}.", loc)
    if check.execution_status not in allowed_execution:
        add("observable_check_execution", f"Check {check.id} has unsupported execution status {check.execution_status!r}.", loc)
    for gap_id in check.verification_gap_ids:
        if gap_id not in gap_ids:
            add("verification_gaps", f"Check {check.id} references missing verification gap {gap_id}.", loc)
    if check.execution_status == "gapped" and not check.verification_gap_ids:
        add("observable_check_execution", f"Check {check.id} is gapped but references no verification gap.", loc)


def _has_explicit_unproven_probe_gap(gaps: list[Any]) -> bool:
    for gap in gaps:
        text = " ".join(
            [
                str(getattr(gap, "id", "")),
                str(getattr(gap, "description", "")),
                str(getattr(gap, "proposed_closure_check", "")),
            ]
        ).lower()
        if "probe" in text and any(marker in text for marker in ("semantic", "independent", "held-out", "planted-negative")):
            return True
    return False


def _check_held_out_probe_metadata(
    probe: Any,
    gap_ids: set[str],
    primary_model_id: str,
    add: Any,
    loc: str,
    *,
    snapshot_obj: ProjectModelSnapshot,
    graph_data: dict[str, Any],
    proof_artifact_base: str | Path | None,
    validate_probe_proofs: bool,
) -> None:
    if not probe.builder_independent_from_decomposer or probe.builder_model_id == primary_model_id or not probe.hidden_from_primary_decomposer:
        add("held_out_probe_isolation", f"Probe {probe.id} is not isolated from the primary decomposer.", loc)
    if not probe.planted_negative_id:
        add("held_out_probe_discrimination", f"Probe {probe.id} declares no planted negative.", loc)

    proof_artifact = str(getattr(probe, "proof_artifact", "") or "").strip()
    proof_path_valid = True
    if proof_artifact:
        proof_path = Path(proof_artifact)
        if proof_path.is_absolute() or any(part == ".." for part in proof_path.parts):
            proof_path_valid = False
            add("held_out_probe_proof", f"Probe {probe.id} proof artifact must be workspace-relative.", loc)
    if (probe.discrimination_passed or probe.golden_control_passed) and not proof_artifact:
        add("held_out_probe_proof", f"Probe {probe.id} claims passed probe results without a proof artifact.", loc)
    if probe.discrimination_passed and probe.golden_control_passed and proof_artifact and proof_path_valid and validate_probe_proofs:
        base = Path(proof_artifact_base) if proof_artifact_base is not None else Path(snapshot_obj.project_root)
        _check_probe_proof_artifact(probe, snapshot_obj, graph_data, base / proof_artifact, add, loc)

    verification_gap_ids = list(getattr(probe, "verification_gap_ids", []))
    for gap_id in verification_gap_ids:
        if gap_id not in gap_ids:
            add("verification_gaps", f"Probe {probe.id} references missing verification gap {gap_id}.", loc)
    if (not probe.discrimination_passed or not probe.golden_control_passed) and not verification_gap_ids:
        add("held_out_probe_discrimination", f"Probe {probe.id} is unproven or failed but references no verification gap.", loc)


def _check_probe_proof_artifact(probe: Any, snapshot_obj: ProjectModelSnapshot, graph_data: dict[str, Any], proof_path: Path, add: Any, loc: str) -> None:
    try:
        proof_text = proof_path.read_text(encoding="utf-8")
    except OSError as exc:
        add("held_out_probe_proof", f"Probe {probe.id} proof artifact cannot be read: {exc}.", loc)
        return
    try:
        proof = json.loads(proof_text)
    except json.JSONDecodeError as exc:
        add("held_out_probe_proof", f"Probe {probe.id} proof artifact is not valid JSON: {exc}.", loc)
        return
    if not isinstance(proof, dict):
        add("held_out_probe_proof", f"Probe {probe.id} proof artifact must be a JSON object.", loc)
        return

    _check_probe_proof_identity(probe, snapshot_obj, proof, add, loc)
    _check_probe_proof_hash(probe, proof, add, loc)
    control_report = _check_probe_control_replay(probe, snapshot_obj, graph_data, proof, add, loc)
    negative_report = _check_probe_negative_replay(probe, graph_data, proof, add, loc)
    if control_report is None or negative_report is None:
        return
    _check_probe_delta(probe, proof, control_report, negative_report, add, loc)


def _check_probe_proof_identity(probe: Any, snapshot_obj: ProjectModelSnapshot, proof: dict[str, Any], add: Any, loc: str) -> None:
    expected = {
        "schema_version": PROBE_PROOF_SCHEMA_VERSION,
        "probe_id": probe.id,
        "planted_negative_id": probe.planted_negative_id,
        "graph_hash": snapshot_obj.graph_hash,
    }
    for key, expected_value in expected.items():
        if proof.get(key) != expected_value:
            add("held_out_probe_proof", f"Probe {probe.id} proof artifact {key} does not match the snapshot/probe.", loc)
    if proof.get("golden_control_passed") is not True or proof.get("discrimination_passed") is not True:
        add("held_out_probe_proof", f"Probe {probe.id} proof artifact does not record passed golden/discrimination outcomes.", loc)


def _check_probe_proof_hash(probe: Any, proof: dict[str, Any], add: Any, loc: str) -> None:
    claimed = proof.get("deterministic_result_hash")
    if not isinstance(claimed, str) or not claimed:
        add("held_out_probe_proof", f"Probe {probe.id} proof artifact is missing deterministic_result_hash.", loc)
        return
    payload = copy.deepcopy(proof)
    payload.pop("deterministic_result_hash", None)
    actual = stable_hash_json(payload)
    if claimed != actual:
        add("held_out_probe_proof", f"Probe {probe.id} proof artifact deterministic_result_hash does not recompute.", loc)


def _check_probe_control_replay(probe: Any, snapshot_obj: ProjectModelSnapshot, graph_data: dict[str, Any], proof: dict[str, Any], add: Any, loc: str) -> GateReport | None:
    golden = proof.get("golden_control_input")
    if not isinstance(golden, dict):
        add("held_out_probe_proof", f"Probe {probe.id} proof artifact is missing golden_control_input.", loc)
        return None
    control_data = snapshot_to_dict(snapshot_obj)
    control_data["held_out_probes"] = []
    control_hash = stable_hash_json(control_data)
    if golden.get("snapshot_hash") != control_hash:
        add("held_out_probe_proof", f"Probe {probe.id} proof artifact control snapshot hash does not match the snapshot under gate.", loc)
        return None
    control_report = run_project_model_gate(control_data, graph_data, _validate_probe_proofs=False)
    if not control_report.passed or golden.get("gate_passed") is not True:
        add("held_out_probe_proof", f"Probe {probe.id} proof artifact golden control does not replay as a passing gate report.", loc)
    return control_report


def _check_probe_negative_replay(probe: Any, graph_data: dict[str, Any], proof: dict[str, Any], add: Any, loc: str) -> GateReport | None:
    negative = proof.get("planted_negative_input")
    if not isinstance(negative, dict):
        add("held_out_probe_proof", f"Probe {probe.id} proof artifact is missing planted_negative_input.", loc)
        return None
    if negative.get("planted_negative_id") != probe.planted_negative_id:
        add("held_out_probe_proof", f"Probe {probe.id} proof artifact planted negative id does not match.", loc)
    negative_snapshot = negative.get("snapshot")
    if not isinstance(negative_snapshot, dict):
        add("held_out_probe_proof", f"Probe {probe.id} proof artifact is missing embedded planted-negative snapshot.", loc)
        return None
    negative_hash = stable_hash_json(negative_snapshot)
    if negative.get("snapshot_hash") != negative_hash:
        add("held_out_probe_proof", f"Probe {probe.id} proof artifact planted-negative snapshot hash does not recompute.", loc)
        return None
    try:
        snapshot_from_dict(negative_snapshot)
    except Exception as exc:  # noqa: BLE001 - proof validation must fail closed with concise diagnostics.
        add("held_out_probe_proof", f"Probe {probe.id} embedded planted-negative snapshot is invalid: {exc}.", loc)
        return None
    negative_report = run_project_model_gate(negative_snapshot, graph_data, _validate_probe_proofs=False)
    if negative_report.passed or negative.get("gate_passed") is not False:
        add("held_out_probe_proof", f"Probe {probe.id} proof artifact planted negative does not replay as a failing gate report.", loc)
    return negative_report


def _check_probe_delta(probe: Any, proof: dict[str, Any], control_report: GateReport, negative_report: GateReport, add: Any, loc: str) -> None:
    mutation = proof.get("negative_mutation")
    if not isinstance(mutation, dict):
        add("held_out_probe_proof", f"Probe {probe.id} proof artifact is missing negative_mutation metadata.", loc)
        return
    expected_gate = str(mutation.get("expected_violation_gate") or "")
    expected_location = str(mutation.get("expected_violation_location") or "")
    expected_text = str(mutation.get("expected_violation_text") or "").lower()
    if not (expected_gate and expected_location and expected_text):
        add("held_out_probe_proof", f"Probe {probe.id} proof artifact mutation metadata is incomplete.", loc)
        return
    negative_has_delta = _report_has_violation(negative_report, expected_gate, expected_location, expected_text)
    control_has_delta = _report_has_violation(control_report, expected_gate, expected_location, expected_text)
    if not negative_has_delta or control_has_delta:
        add("held_out_probe_proof", f"Probe {probe.id} proof artifact does not replay the expected planted-negative discrimination delta.", loc)
    checks = proof.get("checks")
    if not isinstance(checks, list) or not _proof_checks_match_replay(checks, negative_has_delta=negative_has_delta, control_has_delta=control_has_delta, control_report=control_report, negative_report=negative_report):
        add("held_out_probe_proof", f"Probe {probe.id} proof artifact checks do not match replayed gate outcomes.", loc)


def _report_has_violation(report: GateReport, expected_gate: str, expected_location: str, expected_text: str) -> bool:
    return any(
        violation.gate == expected_gate and violation.location == expected_location and expected_text in violation.message.lower()
        for violation in report.violations
    )


def _proof_checks_match_replay(checks: list[Any], *, negative_has_delta: bool, control_has_delta: bool, control_report: GateReport, negative_report: GateReport) -> bool:
    by_id = {check.get("id"): check for check in checks if isinstance(check, dict)}
    golden = by_id.get("golden-control-gate")
    negative = by_id.get("planted-negative-gate")
    delta = by_id.get("expected-discrimination-delta")
    if not isinstance(golden, dict) or not isinstance(negative, dict) or not isinstance(delta, dict):
        return False
    if golden.get("actual_passed") is not control_report.passed or negative.get("actual_passed") is not negative_report.passed:
        return False
    if delta.get("present_in_planted_negative") is not negative_has_delta:
        return False
    if delta.get("absent_from_golden_control") is not (not control_has_delta):
        return False
    return delta.get("matched") is (negative_has_delta and not control_has_delta)


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
    edge_from_node_id = str(edge.get("from_node_id") or "")
    edge_from = nodes.get(edge_from_node_id, {})
    edge_from_symbol = str(edge_from.get("symbol") or edge_from.get("path") or "")
    imported = _edge_import_target(edge)
    if not edge_from_symbol or not imported:
        return []
    direct_from_ids = [
        component_id
        for component_id, component in components.items()
        if edge_from_node_id in {str(node_id) for node_id in component.owned_node_ids}
    ]
    from_ids = direct_from_ids or [
        component_id
        for component_id, component in components.items()
        if any(_source_module_matches(edge_from_symbol, symbol) for symbol in _component_symbols(component, nodes))
    ]
    target_scores: dict[str, int] = {}
    for component_id, component in components.items():
        scores = [_edge_coverage_target_score(imported, symbol) for symbol in _component_symbols(component, nodes)]
        scores = [score for score in scores if score > 0]
        if scores:
            target_scores[component_id] = max(scores)
    best_target_score = max(target_scores.values(), default=0)
    to_ids = [component_id for component_id, score in target_scores.items() if score == best_target_score]
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
    return (
        imported == component_symbol
        or component_symbol.startswith(imported + ".")
        or imported.startswith(component_symbol + ".")
        or ("." in imported and component_symbol.endswith("." + imported))
    )


def _edge_coverage_target_score(imported: str, component_symbol: str) -> int:
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


def _edge_coverage_target_matches(imported: str, component_symbol: str) -> bool:
    return _edge_coverage_target_score(imported, component_symbol) > 0


def _shares_significant_word(text: str, anchor: str) -> bool:
    text_words = {word for word in _words(text) if len(word) >= 5}
    anchor_words = {word for word in _words(anchor) if len(word) >= 5}
    return bool(text_words & anchor_words)


def _words(text: str) -> list[str]:
    import re

    return re.findall(r"[a-z0-9]+", text.lower())
