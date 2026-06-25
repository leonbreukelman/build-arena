"""Build an advisory capability overlay for a Project Model v1 snapshot.

The capability map is intentionally separate from Project Model v1: it is an
operator-reviewed interpretation of what roles the current structural components
serve. This module keeps the v0 lift deterministic and auditable: every emitted
capability cites concrete component/node/provenance ids from the source model and
``review.reviewed`` defaults to ``False`` so downstream dream runs fail closed
until the operator edits/reviews the map.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

SCHEMA_VERSION = "capability-map/v0"
GENERATED_BY = "arena.capability_lift"
DEFAULT_MODEL_ID = "deterministic-capability-lift-v0"
PROMPT = (
    "Infer a carrier-agnostic capability map from Project Model v1 components. "
    "Every capability must cite real component ids, supporting node ids, and provenance refs. "
    "The artifact is advisory and must be operator-reviewed before use."
)

_SCHEMA_PATH = Path(__file__).resolve().parents[1] / "docs" / "schemas" / "capability-map-v0.schema.json"


class CapabilityLiftError(Exception):
    """Raised when a capability map cannot be built or validated."""


def load_json_object(path: str | Path) -> dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise CapabilityLiftError(f"{path} must contain a JSON object")
    return payload


def build_capability_map(project_model_path: str | Path, *, model_id: str = DEFAULT_MODEL_ID) -> dict[str, Any]:
    """Build and self-validate a ``capability-map/v0`` document."""

    model_path = Path(project_model_path).resolve()
    model = load_json_object(model_path)
    components = [item for item in _get(model, "snapshot", "components", default=[]) if isinstance(item, dict)]
    if not components:
        raise CapabilityLiftError("Project Model v1 snapshot has no components to lift")

    profiles = {
        str(item.get("componentId")): item
        for item in _get(model, "iterationReadiness", "componentProfiles", default=[])
        if isinstance(item, dict) and item.get("componentId")
    }

    capabilities: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for component in components:
        component_id = str(component.get("id", "")).strip()
        if not component_id:
            continue
        profile = profiles.get(component_id, {})
        cap_id = _unique_id(f"capability.{_slug(component_id)}", seen_ids)
        responsibility = _first_nonempty(
            profile.get("responsibilitySummary"),
            component.get("responsibility"),
            component.get("name"),
            component_id,
        )
        carrier = _first_nonempty(component.get("name"), component.get("responsibility"), component_id)
        supporting_nodes = _dedupe_strings(
            [*component.get("owned_node_ids", []), *profile.get("ownedNodeIds", [])]
        )
        provenance_refs = _dedupe_strings(
            [*component.get("provenance_refs", []), *profile.get("provenanceRefs", [])]
        ) or [f"component:{component_id}"]
        capabilities.append(
            {
                "id": cap_id,
                "capability": responsibility,
                "realizedByComponentIds": [component_id],
                "currentCarrier": carrier,
                "supportingNodeIds": supporting_nodes,
                "behavioralTags": _dedupe_strings(profile.get("behavioralTags", [])),
                "provenanceRefs": provenance_refs,
            }
        )

    if not capabilities:
        raise CapabilityLiftError("Project Model v1 snapshot has no liftable component ids")

    graph_hash = _graph_hash(model)
    project_id = _project_id(model)
    document = {
        "schemaVersion": SCHEMA_VERSION,
        "projectId": project_id,
        "sourceModel": {
            "projectModelV1Path": str(model_path),
            "graphHash": graph_hash,
        },
        "capabilities": capabilities,
        "review": {
            "reviewed": False,
            "reviewedBy": None,
            "reviewedAtUtc": None,
            "editedFromGenerated": False,
        },
        "provenance": {
            "generatedBy": GENERATED_BY,
            "promptHash": _sha_text(PROMPT),
            "modelId": model_id,
            "inputHashes": {"projectModelV1": _file_sha(model_path)},
        },
    }
    validate_capability_map(document, model)
    validate_schema(document)
    return document


def validate_schema(document: dict[str, Any]) -> None:
    schema = load_json_object(_SCHEMA_PATH)
    errors = sorted(Draft202012Validator(schema).iter_errors(document), key=lambda error: list(error.path))
    if errors:
        first = errors[0]
        location = "/".join(str(part) for part in first.path) or "<root>"
        raise CapabilityLiftError(f"capability map failed schema validation at {location}: {first.message}")


def validate_capability_map(document: dict[str, Any], model: dict[str, Any]) -> None:
    """Validate that every capability reference resolves in the source model."""

    component_ids = {
        str(item.get("id"))
        for item in _get(model, "snapshot", "components", default=[])
        if isinstance(item, dict) and item.get("id")
    }
    node_ids = {
        str(item.get("id"))
        for item in _get(model, "projectGraph", "nodes", default=[])
        if isinstance(item, dict) and item.get("id")
    }
    capability_ids: set[str] = set()
    for index, capability in enumerate(document.get("capabilities", [])):
        if not isinstance(capability, dict):
            raise CapabilityLiftError(f"capabilities[{index}] must be an object")
        capability_id = str(capability.get("id", ""))
        if capability_id in capability_ids:
            raise CapabilityLiftError(f"duplicate capability id: {capability_id}")
        capability_ids.add(capability_id)
        for component_id in capability.get("realizedByComponentIds", []):
            if str(component_id) not in component_ids:
                raise CapabilityLiftError(
                    f"capability {capability_id} references unknown component {component_id}"
                )
        for node_id in capability.get("supportingNodeIds", []):
            if str(node_id) not in node_ids:
                raise CapabilityLiftError(f"capability {capability_id} references unknown graph node {node_id}")


def write_capability_map(project_model_path: str | Path, output_path: str | Path, *, model_id: str = DEFAULT_MODEL_ID) -> Path:
    document = build_capability_map(project_model_path, model_id=model_id)
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return output


def _get(payload: dict[str, Any], *keys: str, default: Any = None) -> Any:
    current: Any = payload
    for key in keys:
        if not isinstance(current, dict):
            return default
        current = current.get(key)
    return default if current is None else current


def _project_id(model: dict[str, Any]) -> str:
    return _first_nonempty(
        _get(model, "project", "projectId"),
        _get(model, "snapshot", "project_id"),
        model.get("id"),
        "project",
    )


def _graph_hash(model: dict[str, Any]) -> str:
    graph_hash = _first_nonempty(
        _get(model, "projectGraph", "graphHash"),
        _get(model, "snapshot", "graph_hash"),
    )
    if not re.fullmatch(r"[a-f0-9]{64}", graph_hash):
        raise CapabilityLiftError("Project Model v1 does not expose a valid 64-hex graph hash")
    return graph_hash


def _first_nonempty(*values: Any) -> str:
    for value in values:
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def _dedupe_strings(values: Any) -> list[str]:
    if not isinstance(values, list):
        return []
    return list(dict.fromkeys(str(value).strip() for value in values if str(value).strip()))


def _slug(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", ".", value.lower()).strip(".")
    return slug or "capability"


def _unique_id(base: str, seen: set[str]) -> str:
    candidate = base
    suffix = 2
    while candidate in seen:
        candidate = f"{base}.{suffix}"
        suffix += 1
    seen.add(candidate)
    return candidate


def _sha_text(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def _file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m arena.capability_lift")
    parser.add_argument("--project-model", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--model-id", default=DEFAULT_MODEL_ID)
    args = parser.parse_args(argv)
    try:
        output = write_capability_map(args.project_model, args.output, model_id=args.model_id)
    except (CapabilityLiftError, OSError, json.JSONDecodeError) as exc:
        print(f"capability lift failed: {exc}", file=sys.stderr)
        return 1
    print(str(output))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
