from __future__ import annotations

import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from arena.capability_lift import (
    CapabilityLiftError,
    build_capability_map,
    validate_capability_map,
    write_capability_map,
)

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "docs" / "schemas" / "capability-map-v0.schema.json"
GRAPH_HASH = "a" * 64


def _model() -> dict[str, object]:
    return {
        "id": "model-1",
        "project": {"projectId": "fixture-project"},
        "snapshot": {
            "project_id": "fixture-project",
            "graph_hash": GRAPH_HASH,
            "components": [
                {
                    "id": "comp.decomposer",
                    "name": "Project decomposer",
                    "responsibility": "Build Project Model v1 snapshots from repository facts",
                    "owned_node_ids": ["node.decomposer"],
                    "provenance_refs": ["prov:component"],
                    "contract_ids": ["contract.decomposer"],
                    "check_ids": [],
                    "verification_gap_ids": ["gap.semantic"],
                }
            ],
            "contracts": [],
            "verification_gaps": [],
            "near_neighbor_alternatives": [],
        },
        "projectGraph": {
            "graphHash": GRAPH_HASH,
            "nodes": [
                {"id": "node.decomposer", "kind": "module", "label": "arena.decomposer", "path": "arena/decomposer.py"}
            ],
            "edges": [],
        },
        "iterationReadiness": {
            "componentProfiles": [
                {
                    "componentId": "comp.decomposer",
                    "ownedNodeIds": ["node.decomposer"],
                    "responsibilitySummary": "repository decomposition",
                    "behavioralTags": ["decompose", "gate"],
                    "provenanceRefs": ["prov:profile"],
                }
            ]
        },
    }


def _write_model(tmp_path: Path) -> Path:
    path = tmp_path / "project-model-v1.json"
    path.write_text(json.dumps(_model()), encoding="utf-8")
    return path


def test_capability_lift_emits_schema_valid_review_false_map(tmp_path: Path) -> None:
    model_path = _write_model(tmp_path)
    output = write_capability_map(model_path, tmp_path / "capability-map.json")
    payload = json.loads(output.read_text(encoding="utf-8"))

    assert payload["schemaVersion"] == "capability-map/v0"
    assert payload["review"]["reviewed"] is False
    assert payload["capabilities"][0]["realizedByComponentIds"] == ["comp.decomposer"]
    assert payload["capabilities"][0]["supportingNodeIds"] == ["node.decomposer"]

    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    errors = sorted(Draft202012Validator(schema).iter_errors(payload), key=lambda error: list(error.path))
    assert errors == []


def test_capability_lift_fails_closed_for_bad_component_ref(tmp_path: Path) -> None:
    model = _model()
    document = build_capability_map(_write_model(tmp_path))
    document["capabilities"][0]["realizedByComponentIds"] = ["comp.fabricated"]

    with pytest.raises(CapabilityLiftError, match="unknown component"):
        validate_capability_map(document, model)  # type: ignore[arg-type]


def test_capability_lift_fails_closed_for_bad_node_ref(tmp_path: Path) -> None:
    model = _model()
    document = build_capability_map(_write_model(tmp_path))
    document["capabilities"][0]["supportingNodeIds"] = ["node.fabricated"]

    with pytest.raises(CapabilityLiftError, match="unknown graph node"):
        validate_capability_map(document, model)  # type: ignore[arg-type]
