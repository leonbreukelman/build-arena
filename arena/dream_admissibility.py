"""Deterministic admissibility checks for divergent dream hypotheses.

The premise gate proves that cited anchors resolve. This module checks the extra
contract that a resolved dream is actually a divergent architectural hypothesis:
it must start from a tension, name an explicit from -> to structural delta, make a
measurable prediction, and stay in the experiment lane rather than the single-file
proposal lane.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ALLOWED_DIRECTIONS = {"decrease", "increase", "passes"}
TENSION_ANCHOR_KINDS = {"verificationGap", "priorityBacklog", "productInvariant", "graphStructural"}
GRAPH_STRUCTURAL_KIND = "graphStructural"
MULTI_TAG_THRESHOLD = 5
HIGH_FAN_IN_THRESHOLD = 3


@dataclass(frozen=True, slots=True)
class RequirementResult:
    """One admissibility requirement verdict."""

    requirement: str
    passed: bool
    reason: str

    def to_jsonable(self) -> dict[str, Any]:
        return {"requirement": self.requirement, "passed": self.passed, "reason": self.reason}


@dataclass(frozen=True, slots=True)
class AdmissibilityResult:
    """Full admissibility verdict for one dream."""

    dream_id: str
    admissible: bool
    requirements: tuple[RequirementResult, ...]

    @property
    def failed_reasons(self) -> list[str]:
        return [item.reason for item in self.requirements if not item.passed]

    def to_jsonable(self) -> dict[str, Any]:
        return {
            "dreamId": self.dream_id,
            "admissible": self.admissible,
            "requirements": [item.to_jsonable() for item in self.requirements],
        }


def anchor_content_hash(anchor: dict[str, Any]) -> str:
    """Canonical content hash for a resolved evidence anchor."""

    encoded = json.dumps(anchor, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(encoded).hexdigest()


def build_anchor_indexes(model: dict[str, Any], capability_map: dict[str, Any]) -> dict[str, dict[str, dict[str, Any]]]:
    """Build all anchor indexes the dream lane can cite."""

    return {
        "graphNode": _index_by_id(_get(model, "projectGraph", "nodes", default=[])),
        "graphEdge": _index_by_id(_get(model, "projectGraph", "edges", default=[])),
        "component": _index_by_id(_get(model, "snapshot", "components", default=[])),
        "contract": _merged_index(
            _get(model, "snapshot", "contracts", default=[]),
            _get(model, "iterationReadiness", "runtimeContracts", default=[]),
        ),
        "capability": _index_by_id(capability_map.get("capabilities", [])),
        "verificationGap": _index_by_id(_get(model, "snapshot", "verification_gaps", default=[])),
        "nearNeighborAlternative": _index_by_id(
            _get(model, "snapshot", "near_neighbor_alternatives", default=[])
        ),
        "priorityBacklog": _merged_index(
            _get(model, "iterationReadiness", "priorityBacklog", default=[]),
            _get(model, "snapshot", "priorityBacklog", default=[]),
            _get(model, "snapshot", "priority_backlog", default=[]),
        ),
        "productInvariant": _merged_index(
            _get(model, "iterationReadiness", "productInvariants", default=[]),
            _get(model, "snapshot", "productInvariants", default=[]),
            _get(model, "snapshot", "product_invariants", default=[]),
        ),
        GRAPH_STRUCTURAL_KIND: _index_by_id(_graph_structural_anchors(model)),
    }


def anchor_catalog_records(model: dict[str, Any], capability_map: dict[str, Any]) -> list[dict[str, Any]]:
    """Return prompt-ready anchor records with stable hashes and tension labels."""

    indexes = build_anchor_indexes(model, capability_map)
    records: list[dict[str, Any]] = []
    for anchor_kind in sorted(indexes):
        for anchor_id in sorted(indexes[anchor_kind]):
            anchor = indexes[anchor_kind][anchor_id]
            tension = _is_tension_anchor(anchor_kind, anchor, indexes)
            record = {
                "anchorKind": anchor_kind,
                "anchorId": anchor_id,
                "contentHash": anchor_content_hash(anchor),
                "tensionBearing": tension,
            }
            if tension:
                record["tensionKind"] = _tension_kind(anchor_kind, anchor, indexes)
            records.append(record)
    return records


def check_dream_admissibility(
    dream: dict[str, Any], *, project_model: dict[str, Any], capability_map: dict[str, Any]
) -> AdmissibilityResult:
    """Check one dream against the divergent-hypothesis contract."""

    indexes = build_anchor_indexes(project_model, capability_map)
    checks = (
        _check_cited_tension(dream, indexes),
        _check_structural_delta(dream),
        _check_measurable_prediction(dream),
        _check_divergence(dream),
    )
    return AdmissibilityResult(
        dream_id=_clean(dream.get("id")) or "<missing>",
        admissible=all(item.passed for item in checks),
        requirements=checks,
    )


def check_document_admissibility(
    document: dict[str, Any], *, project_model: dict[str, Any], capability_map: dict[str, Any]
) -> dict[str, Any]:
    dreams_raw = document.get("dreams")
    dreams: list[Any] = dreams_raw if isinstance(dreams_raw, list) else []
    results = [
        check_dream_admissibility(dream, project_model=project_model, capability_map=capability_map)
        for dream in dreams
        if isinstance(dream, dict)
    ]
    return {
        "schemaVersion": "dream-admissibility/v0",
        "summary": {
            "admissible": sum(1 for item in results if item.admissible),
            "inadmissible": sum(1 for item in results if not item.admissible),
            "total": len(results),
        },
        "dreams": [item.to_jsonable() for item in results],
    }


def check_document_admissibility_from_paths(
    *,
    project_model_path: str | Path,
    capability_map_path: str | Path,
    dreams_path: str | Path,
) -> dict[str, Any]:
    return check_document_admissibility(
        _load_json_object(dreams_path),
        project_model=_load_json_object(project_model_path),
        capability_map=_load_json_object(capability_map_path),
    )


def admissibility_reasons(result: AdmissibilityResult) -> list[str]:
    """Return gate-friendly rejection reasons for one result."""

    return [f"admissibility.{item.requirement}: {item.reason}" for item in result.requirements if not item.passed]


def _check_cited_tension(dream: dict[str, Any], indexes: dict[str, dict[str, dict[str, Any]]]) -> RequirementResult:
    evidence = dream.get("citedEvidence")
    if not isinstance(evidence, list) or not evidence:
        return RequirementResult("cited_tension", False, "missing citedEvidence; no tension-bearing anchor cited")
    unresolved: list[str] = []
    non_tension: list[str] = []
    for item in evidence:
        if not isinstance(item, dict):
            unresolved.append("<non-object>")
            continue
        anchor_kind = _clean(item.get("anchorKind"))
        anchor_id = _clean(item.get("anchorId"))
        anchor = indexes.get(anchor_kind, {}).get(anchor_id)
        if anchor is None:
            unresolved.append(f"{anchor_kind}:{anchor_id}")
            continue
        if _is_tension_anchor(anchor_kind, anchor, indexes):
            return RequirementResult(
                "cited_tension",
                True,
                f"cites tension-bearing {anchor_kind} {anchor_id}",
            )
        non_tension.append(f"{anchor_kind}:{anchor_id}")
    if unresolved:
        return RequirementResult(
            "cited_tension",
            False,
            "cited tension anchor does not resolve: " + ", ".join(unresolved),
        )
    return RequirementResult(
        "cited_tension",
        False,
        "citedEvidence resolves but is not tension-bearing: " + ", ".join(non_tension),
    )


def _check_structural_delta(dream: dict[str, Any]) -> RequirementResult:
    mode = _clean(dream.get("mode"))
    current_raw = dream.get("currentStructure")
    proposed_raw = dream.get("proposedStructure")
    current: dict[str, Any] = current_raw if isinstance(current_raw, dict) else {}
    proposed: dict[str, Any] = proposed_raw if isinstance(proposed_raw, dict) else {}
    missing_bits: list[str] = []
    if not current:
        missing_bits.append("no current structure was provided")
    if not proposed:
        missing_bits.append("no proposed structure was provided")

    if mode == "carrier_swap":
        from_carrier = _clean(current.get("fromCarrier"))
        to_carrier = _clean(proposed.get("toCarrier"))
        if not from_carrier:
            missing_bits.append("currentStructure.fromCarrier is required")
        if not to_carrier:
            missing_bits.append("proposedStructure.toCarrier is required")
        if missing_bits:
            return RequirementResult(
                "structural_delta",
                False,
                "carrier_swap requires fromCarrier != toCarrier; " + "; ".join(dict.fromkeys(missing_bits)),
            )
        if _same_structure_name(from_carrier, to_carrier):
            return RequirementResult(
                "structural_delta",
                False,
                f"carrier_swap requires fromCarrier != toCarrier; both were {from_carrier!r}",
            )
        return RequirementResult(
            "structural_delta",
            True,
            f"carrier_swap changes carrier from {from_carrier!r} to {to_carrier!r}",
        )

    if mode == "function_remap":
        from_binding = _clean(current.get("fromBinding"))
        to_binding = _clean(proposed.get("toBinding"))
        if not from_binding:
            missing_bits.append("currentStructure.fromBinding is required")
        if not to_binding:
            missing_bits.append("proposedStructure.toBinding is required")
        if missing_bits:
            return RequirementResult(
                "structural_delta",
                False,
                "function_remap requires fromBinding != toBinding; " + "; ".join(dict.fromkeys(missing_bits)),
            )
        if _same_structure_name(from_binding, to_binding):
            return RequirementResult(
                "structural_delta",
                False,
                f"function_remap requires fromBinding != toBinding; both were {from_binding!r}",
            )
        return RequirementResult(
            "structural_delta",
            True,
            f"function_remap changes binding from {from_binding!r} to {to_binding!r}",
        )

    return RequirementResult("structural_delta", False, "mode must be carrier_swap or function_remap")


def _check_measurable_prediction(dream: dict[str, Any]) -> RequirementResult:
    recipe_raw = dream.get("validationRecipe")
    recipe: dict[str, Any] = recipe_raw if isinstance(recipe_raw, dict) else {}
    direction = _clean(recipe.get("expectedDirection"))
    observable = _clean(recipe.get("observable"))
    if direction not in ALLOWED_DIRECTIONS:
        return RequirementResult(
            "measurable_prediction",
            False,
            "validationRecipe.expectedDirection must be one of decrease, increase, passes",
        )
    if not observable:
        return RequirementResult("measurable_prediction", False, "validationRecipe.observable is required")
    if not _observable_is_metric_like(observable):
        return RequirementResult(
            "measurable_prediction",
            False,
            f"observable must name a computable metric/axis or buildable fitness function, got {observable!r}",
        )
    return RequirementResult(
        "measurable_prediction",
        True,
        f"predicts {direction} on observable {observable!r}",
    )


def _check_divergence(dream: dict[str, Any]) -> RequirementResult:
    structural = _check_structural_delta(dream)
    if not structural.passed:
        return RequirementResult(
            "divergence",
            False,
            "not divergent because no valid structural from->to delta was provided",
        )
    prose = " ".join(
        _clean(value)
        for value in (
            dream.get("idea"),
            dream.get("rationale"),
            (dream.get("validationRecipe") or {}).get("action") if isinstance(dream.get("validationRecipe"), dict) else "",
        )
    ).lower()
    single_file_markers = (
        "single-file",
        "single file",
        "one-file",
        "one file",
        "fix lint",
        "ruff --fix",
        "add a focused test only",
    )
    if any(marker in prose for marker in single_file_markers):
        return RequirementResult(
            "divergence",
            False,
            "looks reducible to a single-file finding fix; route that to the proposal lane",
        )
    return RequirementResult(
        "divergence",
        True,
        "structural from->to delta is experiment-lane shaped, not a single-file fix",
    )


def _is_tension_anchor(
    anchor_kind: str, anchor: dict[str, Any], indexes: dict[str, dict[str, dict[str, Any]]]
) -> bool:
    if anchor_kind in {"verificationGap", "priorityBacklog", GRAPH_STRUCTURAL_KIND}:
        return True
    if anchor_kind == "productInvariant":
        enforcement = _clean(anchor.get("enforcement")).lower()
        if enforcement and enforcement != "modeled":
            return True
        invariant_id = _clean(anchor.get("id"))
        return any(
            invariant_id in _string_list(backlog.get("relatedInvariantIds"))
            for backlog in indexes.get("priorityBacklog", {}).values()
        )
    return False


def _tension_kind(
    anchor_kind: str, anchor: dict[str, Any], indexes: dict[str, dict[str, dict[str, Any]]]
) -> str:
    if anchor_kind != "productInvariant":
        return anchor_kind
    enforcement = _clean(anchor.get("enforcement")).lower()
    if enforcement and enforcement != "modeled":
        return "at_risk_productInvariant"
    invariant_id = _clean(anchor.get("id"))
    if any(
        invariant_id in _string_list(backlog.get("relatedInvariantIds"))
        for backlog in indexes.get("priorityBacklog", {}).values()
    ):
        return "backlog_linked_productInvariant"
    return "productInvariant"


def _graph_structural_anchors(model: dict[str, Any]) -> list[dict[str, Any]]:
    anchors: list[dict[str, Any]] = []
    nodes = _get(model, "projectGraph", "nodes", default=[])
    edges = _get(model, "projectGraph", "edges", default=[])
    node_index = _index_by_id(nodes)
    incoming: dict[str, list[dict[str, Any]]] = defaultdict(list)
    adjacency: dict[str, set[str]] = defaultdict(set)
    if isinstance(edges, list):
        for edge in edges:
            if not isinstance(edge, dict):
                continue
            source = _clean(edge.get("from_node_id")) or _clean(edge.get("fromNodeId"))
            target = _clean(edge.get("to_node_id")) or _clean(edge.get("toNodeId"))
            if target:
                incoming[target].append(edge)
            if source and target:
                adjacency[source].add(target)
    for node_id, node_edges in sorted(incoming.items()):
        if len(node_edges) >= HIGH_FAN_IN_THRESHOLD:
            node = node_index.get(node_id, {})
            anchors.append(
                {
                    "id": f"graph.highFanIn.{node_id}",
                    "kind": "high_fan_in",
                    "nodeId": node_id,
                    "path": _clean(node.get("path")),
                    "fanIn": len(node_edges),
                    "provenanceRefs": _dedupe_strings(
                        ref
                        for edge in node_edges
                        for ref in (edge.get("provenance_refs") or edge.get("provenanceRefs") or [])
                    ),
                }
            )
    for profile in _get(model, "iterationReadiness", "componentProfiles", default=[]):
        if not isinstance(profile, dict):
            continue
        tags = _string_list(profile.get("behavioralTags"))
        if len(tags) >= MULTI_TAG_THRESHOLD:
            component_id = _clean(profile.get("componentId"))
            anchors.append(
                {
                    "id": f"graph.multiTagComponent.{component_id}",
                    "kind": "multi_tag_component",
                    "componentId": component_id,
                    "behavioralTagCount": len(tags),
                    "behavioralTags": tags,
                    "provenanceRefs": _string_list(profile.get("provenanceRefs")),
                }
            )
    for source, targets in sorted(adjacency.items()):
        for target in sorted(targets):
            if source < target and source in adjacency.get(target, set()):
                anchors.append(
                    {
                        "id": f"graph.importCycle.{source}.{target}",
                        "kind": "import_cycle_pair",
                        "nodeIds": [source, target],
                        "cycleLength": 2,
                        "provenanceRefs": [],
                    }
                )
    return anchors


def _observable_is_metric_like(value: str) -> bool:
    lowered = value.lower()
    metric_markers = (
        "count",
        "fan-in",
        "fan in",
        "fanout",
        "fan-out",
        "cycle",
        "coupling",
        "coverage",
        "test",
        "seam",
        "fitness",
        "metric",
        "score",
        "ratio",
        "rate",
        "latency",
        "wall-clock",
        "runtime",
        "gate",
        "complexity",
        "dependency",
        "import",
    )
    return any(marker in lowered for marker in metric_markers)


def _same_structure_name(left: str, right: str) -> bool:
    return _structure_key(left) == _structure_key(right)


def _structure_key(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", value.lower())


def _index_by_id(items: Any) -> dict[str, dict[str, Any]]:
    if not isinstance(items, list):
        return {}
    return {
        str(item.get("id")): item
        for item in items
        if isinstance(item, dict) and isinstance(item.get("id"), str) and item.get("id")
    }


def _merged_index(*groups: Any) -> dict[str, dict[str, Any]]:
    merged: dict[str, dict[str, Any]] = {}
    for group in groups:
        merged.update(_index_by_id(group))
    return merged


def _get(payload: dict[str, Any], *keys: str, default: Any = None) -> Any:
    current: Any = payload
    for key in keys:
        if not isinstance(current, dict):
            return default
        current = current.get(key)
    return default if current is None else current


def _load_json_object(path: str | Path) -> dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def _clean(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return list(dict.fromkeys(str(item).strip() for item in value if str(item).strip()))


def _dedupe_strings(values: Any) -> list[str]:
    if not isinstance(values, list):
        values = list(values) if values is not None and not isinstance(values, str) else []
    return list(dict.fromkeys(str(value).strip() for value in values if str(value).strip()))
