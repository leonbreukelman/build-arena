"""Deterministic premise-resolution gate for tier-3 dream proposals.

The gate is the trust boundary for the dream lane. It does not judge whether a
dream is useful. It only proves that every cited current-state premise resolves
against the real Project Model v1 / capability map and that the dream carries a
validation recipe. Dreams that fail this check are killed before emit.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from arena.capability_lift import CapabilityLiftError, validate_capability_map
from arena.dream_admissibility import (
    admissibility_reasons,
    anchor_provenance_class,
    build_anchor_indexes,
    check_dream_admissibility,
)
from arena.dream_admissibility import (
    anchor_content_hash as _admissibility_anchor_content_hash,
)

SCHEMA_VERSION = "dream/v1"
TRACE_SCHEMA_VERSION = "dream-gate-trace/v0"
GATED_BY = "arena.dream_gate"
ALLOWED_MODES = {"carrier_swap", "function_remap"}
ANCHOR_KINDS = {
    "graphNode",
    "graphEdge",
    "component",
    "contract",
    "capability",
    "verificationGap",
    "nearNeighborAlternative",
    "priorityBacklog",
    "productInvariant",
    "graphStructural",
}

_SCHEMA_PATH = Path(__file__).resolve().parents[1] / "docs" / "schemas" / "dream-v1.schema.json"


class DreamGateError(Exception):
    """Raised when the gate cannot evaluate its inputs fail-closed."""


@dataclass(frozen=True, slots=True)
class GateResult:
    document: dict[str, Any]
    trace: dict[str, Any]
    accepted_count: int
    killed_count: int


def anchor_content_hash(anchor: dict[str, Any]) -> str:
    """Canonical content hash for a resolved evidence anchor."""

    return _admissibility_anchor_content_hash(anchor)


def gate_dreams(
    *,
    project_model_path: str | Path,
    capability_map_path: str | Path,
    dreams_path: str | Path,
) -> GateResult:
    model_path = Path(project_model_path).resolve()
    cap_path = Path(capability_map_path).resolve()
    source_path = Path(dreams_path).resolve()
    model = _load_json_object(model_path)
    capability_map = _load_json_object(cap_path)
    dreams_doc = _load_json_object(source_path)

    cap_source = capability_map.get("sourceModel") if isinstance(capability_map.get("sourceModel"), dict) else {}
    cap_graph_hash = _clean(cap_source.get("graphHash")) if isinstance(cap_source, dict) else ""
    model_graph_hash = _graph_hash(model)
    if cap_graph_hash and cap_graph_hash != model_graph_hash:
        raise DreamGateError("capability map graphHash does not match the Project Model v1 graphHash")
    try:
        validate_capability_map(capability_map, model)
    except CapabilityLiftError as exc:
        raise DreamGateError(str(exc)) from exc

    indexes = _anchor_indexes(model, capability_map)
    capability_ids = set(indexes["capability"])
    near_neighbor_ids = set(indexes["nearNeighborAlternative"])
    accepted: list[dict[str, Any]] = []
    killed: list[dict[str, Any]] = []

    for raw in dreams_doc.get("dreams", []):
        if not isinstance(raw, dict):
            killed.append({"id": "<non-object>", "premiseConfidence": "unresolved", "reasons": ["dream is not an object"]})
            continue
        normalized, reasons, premise_confidence = _evaluate_dream(
            raw,
            indexes=indexes,
            capability_ids=capability_ids,
            near_neighbor_ids=near_neighbor_ids,
        )
        admissibility = check_dream_admissibility(normalized, project_model=model, capability_map=capability_map)
        all_reasons = [*reasons, *admissibility_reasons(admissibility)]
        if not all_reasons and premise_confidence == "all_resolved":
            accepted.append(normalized)
        else:
            killed.append(
                {
                    "id": str(raw.get("id", "<missing>")),
                    "premiseConfidence": premise_confidence,
                    "admissibility": admissibility.to_jsonable(),
                    "reasons": all_reasons or ["premise confidence was not all_resolved"],
                }
            )

    document = {
        "schemaVersion": SCHEMA_VERSION,
        "projectId": _project_id(model, capability_map, dreams_doc),
        "sourceModel": {
            "projectModelV1Path": str(model_path),
            "graphHash": model_graph_hash,
        },
        "capabilityMap": {
            "path": str(cap_path),
            "reviewed": capability_map.get("review", {}).get("reviewed") is True,
        },
        "dreams": accepted,
        "provenance": _provenance(dreams_doc, model_path, cap_path, source_path),
    }
    validate_dream_schema(document)
    trace = {
        "schemaVersion": TRACE_SCHEMA_VERSION,
        "acceptedDreamIds": [dream["id"] for dream in accepted],
        "killedDreams": killed,
        "summary": {"accepted": len(accepted), "killed": len(killed)},
    }
    return GateResult(document=document, trace=trace, accepted_count=len(accepted), killed_count=len(killed))


def write_gated_dreams(
    *,
    project_model_path: str | Path,
    capability_map_path: str | Path,
    dreams_path: str | Path,
    output_path: str | Path,
    trace_path: str | Path | None = None,
) -> GateResult:
    result = gate_dreams(
        project_model_path=project_model_path,
        capability_map_path=capability_map_path,
        dreams_path=dreams_path,
    )
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result.document, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if trace_path is not None:
        trace = Path(trace_path)
        trace.parent.mkdir(parents=True, exist_ok=True)
        trace.write_text(json.dumps(result.trace, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def validate_dream_schema(document: dict[str, Any]) -> None:
    schema = _load_json_object(_SCHEMA_PATH)
    errors = sorted(Draft202012Validator(schema).iter_errors(document), key=lambda error: list(error.path))
    if errors:
        first = errors[0]
        location = "/".join(str(part) for part in first.path) or "<root>"
        raise DreamGateError(f"dream/v1 failed schema validation at {location}: {first.message}")


def _evaluate_dream(
    dream: dict[str, Any], *, indexes: dict[str, dict[str, dict[str, Any]]], capability_ids: set[str], near_neighbor_ids: set[str]
) -> tuple[dict[str, Any], list[str], str]:
    reasons: list[str] = []
    resolved_count = 0
    evidence_items: list[dict[str, Any]] = []

    dream_id = _clean(dream.get("id"))
    if not dream_id:
        reasons.append("missing id")
    mode = _clean(dream.get("mode"))
    if mode not in ALLOWED_MODES:
        reasons.append("mode must be carrier_swap or function_remap")
    idea = _clean(dream.get("idea"))
    if not idea:
        reasons.append("missing idea")
    rationale = _clean(dream.get("rationale"))
    if not rationale:
        reasons.append("missing rationale")

    target_capabilities = _string_list(dream.get("targetCapabilityIds"))
    if not target_capabilities:
        reasons.append("missing targetCapabilityIds")
    for capability_id in target_capabilities:
        if capability_id not in capability_ids:
            reasons.append(f"unknown target capability {capability_id}")

    current_structure = _structure(dream.get("currentStructure"))
    proposed_structure = _structure(dream.get("proposedStructure"))
    if not current_structure:
        reasons.append("missing currentStructure")
    if not proposed_structure:
        reasons.append("missing proposedStructure")

    raw_evidence = dream.get("citedEvidence")
    if not isinstance(raw_evidence, list) or not raw_evidence:
        reasons.append("missing citedEvidence")
        raw_evidence = []
    for index, evidence in enumerate(raw_evidence):
        if not isinstance(evidence, dict):
            reasons.append(f"citedEvidence[{index}] is not an object")
            continue
        normalized_evidence = {
            "anchorKind": _clean(evidence.get("anchorKind")),
            "anchorId": _clean(evidence.get("anchorId")),
            "contentHash": _clean(evidence.get("contentHash")),
        }
        claim = _clean(evidence.get("claim"))
        if claim:
            normalized_evidence["claim"] = claim
        anchor_kind = normalized_evidence["anchorKind"]
        anchor_id = normalized_evidence["anchorId"]
        content_hash = normalized_evidence["contentHash"]
        anchor = indexes.get(anchor_kind, {}).get(anchor_id)
        if anchor_kind not in ANCHOR_KINDS:
            reasons.append(f"citedEvidence[{index}] has invalid anchorKind {anchor_kind!r}")
        elif anchor is None:
            reasons.append(f"citedEvidence[{index}] unresolved {anchor_kind} {anchor_id}")
        elif content_hash != anchor_content_hash(anchor):
            reasons.append(f"citedEvidence[{index}] contentHash mismatch for {anchor_kind} {anchor_id}")
        else:
            normalized_evidence["provenanceClass"] = anchor_provenance_class(anchor_kind, anchor)
            resolved_count += 1
        evidence_items.append(normalized_evidence)

    recipe = dream.get("validationRecipe")
    if not isinstance(recipe, dict):
        reasons.append("missing validationRecipe")
        recipe = {}
    validation_recipe = {
        "action": _clean(recipe.get("action")),
        "observable": _clean(recipe.get("observable")),
        "expectedDirection": _clean(recipe.get("expectedDirection")),
    }
    if not validation_recipe["action"] or not validation_recipe["observable"]:
        reasons.append("validationRecipe action and observable are required")
    if validation_recipe["expectedDirection"] not in {"decrease", "increase", "passes"}:
        reasons.append("validationRecipe expectedDirection is invalid")

    conclusion = dream.get("conclusionConfidence")
    if not isinstance(conclusion, dict):
        reasons.append("missing conclusionConfidence")
        conclusion = {}
    band = _clean(conclusion.get("band"))
    value = conclusion.get("value")
    if band not in {"low", "medium"}:
        reasons.append("conclusionConfidence.band must be low or medium")
    if not isinstance(value, int | float) or value < 0 or value > 0.7:
        reasons.append("conclusionConfidence.value must be between 0 and 0.7")
        numeric_value = 0.0
    else:
        numeric_value = float(value)

    neighbor = dream.get("neighborAlternativeId")
    neighbor_id = _clean(neighbor) if neighbor is not None else None
    if neighbor_id and neighbor_id not in near_neighbor_ids:
        reasons.append(f"unknown neighborAlternativeId {neighbor_id}")

    if not evidence_items:
        premise_confidence = "unresolved"
    elif resolved_count == len(evidence_items) and not any(reason.startswith("citedEvidence") for reason in reasons):
        premise_confidence = "all_resolved"
    elif resolved_count > 0:
        premise_confidence = "partial"
    else:
        premise_confidence = "unresolved"

    normalized = {
        "id": dream_id,
        "mode": mode,
        "idea": idea,
        "targetCapabilityIds": target_capabilities,
        "citedEvidence": evidence_items,
        "currentStructure": current_structure,
        "proposedStructure": proposed_structure,
        "rationale": rationale,
        "premiseConfidence": premise_confidence,
        "conclusionConfidence": {"band": band, "value": numeric_value},
        "validationRecipe": validation_recipe,
    }
    if neighbor is not None:
        normalized["neighborAlternativeId"] = neighbor_id
    return normalized, reasons, premise_confidence


def _anchor_indexes(model: dict[str, Any], capability_map: dict[str, Any]) -> dict[str, dict[str, dict[str, Any]]]:
    return build_anchor_indexes(model, capability_map)


def _structure(value: Any) -> dict[str, str]:
    if not isinstance(value, dict):
        return {}
    out: dict[str, str] = {}
    for key in ("fromCarrier", "toCarrier", "fromBinding", "toBinding", "description"):
        cleaned = _clean(value.get(key))
        if cleaned:
            out[key] = cleaned
    return out


def _index_by_id(items: Any) -> dict[str, dict[str, Any]]:
    if not isinstance(items, list):
        return {}
    return {
        str(item.get("id")): item
        for item in items
        if isinstance(item, dict) and isinstance(item.get("id"), str) and item.get("id")
    }


def _provenance(dreams_doc: dict[str, Any], model_path: Path, cap_path: Path, dreams_path: Path) -> dict[str, Any]:
    original_raw = dreams_doc.get("provenance")
    original: dict[str, Any] = original_raw if isinstance(original_raw, dict) else {}
    prompt_hashes_raw = original.get("promptHashes")
    prompt_hashes = prompt_hashes_raw if isinstance(prompt_hashes_raw, dict) else {}
    prompt_hashes = {
        str(key): str(value)
        for key, value in prompt_hashes.items()
        if isinstance(value, str) and re.fullmatch(r"[a-f0-9]{64}", value)
    }
    prompt_hashes.setdefault("gate", hashlib.sha256(GATED_BY.encode()).hexdigest())
    input_hashes_raw = original.get("inputHashes")
    input_hashes = input_hashes_raw if isinstance(input_hashes_raw, dict) else {}
    normalized_input_hashes = {
        str(key): str(value)
        for key, value in input_hashes.items()
        if isinstance(value, str) and re.fullmatch(r"[a-f0-9]{64}", value)
    }
    normalized_input_hashes.update(
        {
            "projectModelV1": _file_sha(model_path),
            "capabilityMap": _file_sha(cap_path),
            "researchedDreams": _file_sha(dreams_path),
        }
    )
    return {
        "generatedBy": _clean(original.get("generatedBy")) or "arena.dream_generate",
        "researchedBy": _clean(original.get("researchedBy")) or "arena.dream_research",
        "gatedBy": GATED_BY,
        "promptHashes": prompt_hashes,
        "modelId": _clean(original.get("modelId")) or "unknown",
        "inputHashes": normalized_input_hashes,
    }


def _project_id(model: dict[str, Any], capability_map: dict[str, Any], dreams_doc: dict[str, Any]) -> str:
    return (
        _clean(dreams_doc.get("projectId"))
        or _clean(capability_map.get("projectId"))
        or _clean(_get(model, "project", "projectId"))
        or _clean(_get(model, "snapshot", "project_id"))
        or "project"
    )


def _graph_hash(model: dict[str, Any]) -> str:
    graph_hash = _clean(_get(model, "projectGraph", "graphHash")) or _clean(_get(model, "snapshot", "graph_hash"))
    if not re.fullmatch(r"[a-f0-9]{64}", graph_hash):
        raise DreamGateError("Project Model v1 does not expose a valid 64-hex graph hash")
    return graph_hash


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
        raise DreamGateError(f"{path} must contain a JSON object")
    return payload


def _clean(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return list(dict.fromkeys(str(item).strip() for item in value if str(item).strip()))


def _file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m arena.dream_gate")
    parser.add_argument("--project-model", required=True)
    parser.add_argument("--capability-map", required=True)
    parser.add_argument("--dreams", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--trace")
    args = parser.parse_args(argv)
    try:
        result = write_gated_dreams(
            project_model_path=args.project_model,
            capability_map_path=args.capability_map,
            dreams_path=args.dreams,
            output_path=args.output,
            trace_path=args.trace,
        )
    except (DreamGateError, OSError, json.JSONDecodeError) as exc:
        print(f"dream gate failed: {exc}", file=sys.stderr)
        return 1
    print(str(args.output))
    if result.accepted_count == 0:
        return 2
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
