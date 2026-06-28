from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from arena.capability_lift import build_capability_map
from arena.dream_gate import DreamGateError, anchor_content_hash, gate_dreams, write_gated_dreams

GRAPH_HASH = "b" * 64


def _model() -> dict[str, Any]:
    return {
        "id": "model-1",
        "project": {"projectId": "fixture-project"},
        "snapshot": {
            "project_id": "fixture-project",
            "graph_hash": GRAPH_HASH,
            "components": [
                {
                    "id": "comp.runner",
                    "name": "Runner",
                    "responsibility": "Run proposal stages",
                    "owned_node_ids": ["node.runner"],
                    "provenance_refs": ["prov:runner"],
                    "contract_ids": ["contract.runner"],
                    "check_ids": [],
                    "verification_gap_ids": ["gap.behaviour"],
                }
            ],
            "contracts": [
                {
                    "id": "contract.runner",
                    "name": "stage contract",
                    "from_component_id": "comp.runner",
                    "to_component_id": "comp.runner",
                    "supporting_edge_ids": ["edge.self"],
                    "near_neighbor_alternative_ids": ["near.subprocess"],
                    "provenance_refs": ["prov:contract"],
                }
            ],
            "verification_gaps": [
                {
                    "id": "gap.behaviour",
                    "description": "behaviour gate missing",
                    "severity": "high",
                    "component_ids": ["comp.runner"],
                    "contract_ids": ["contract.runner"],
                    "provenance_refs": ["prov:gap"],
                    "proposed_closure_check": "run tests",
                }
            ],
            "near_neighbor_alternatives": [
                {
                    "id": "near.subprocess",
                    "target_id": "contract.runner",
                    "alternative": "in-process stage seam",
                    "why_not_primary": "subprocess boundary is simpler",
                    "provenance_refs": ["prov:near"],
                }
            ],
        },
        "projectGraph": {
            "graphHash": GRAPH_HASH,
            "nodes": [{"id": "node.runner", "kind": "module", "label": "runner", "path": "arena/runner.py"}],
            "edges": [
                {
                    "id": "edge.self",
                    "kind": "calls",
                    "from_node_id": "node.runner",
                    "to_node_id": "node.runner",
                    "label": "self",
                    "provenance_refs": [],
                    "confidence": "high",
                    "derived_by": "fixture",
                }
            ],
        },
        "iterationReadiness": {
            "componentProfiles": [
                {
                    "componentId": "comp.runner",
                    "ownedNodeIds": ["node.runner"],
                    "responsibilitySummary": "stage orchestration",
                    "behavioralTags": ["orchestrate"],
                    "provenanceRefs": ["prov:profile"],
                }
            ]
        },
    }


def _write_inputs(tmp_path: Path) -> tuple[Path, Path, dict[str, Any], dict[str, Any]]:
    model = _model()
    model_path = tmp_path / "project-model-v1.json"
    model_path.write_text(json.dumps(model), encoding="utf-8")
    cap_map = build_capability_map(model_path)
    cap_map["review"]["reviewed"] = True
    cap_path = tmp_path / "capability-map.json"
    cap_path.write_text(json.dumps(cap_map), encoding="utf-8")
    return model_path, cap_path, model, cap_map


def _dream(model: dict[str, Any], cap_map: dict[str, Any], **overrides: Any) -> dict[str, Any]:
    gap = model["snapshot"]["verification_gaps"][0]
    dream = {
        "id": "dream.runner-carrier",
        "mode": "carrier_swap",
        "idea": "Consider replacing subprocess-only stage wiring with an injected stage seam.",
        "targetCapabilityIds": [cap_map["capabilities"][0]["id"]],
        "citedEvidence": [
            {
                "anchorKind": "verificationGap",
                "anchorId": "gap.behaviour",
                "contentHash": anchor_content_hash(gap),
                "claim": "The runner has a behavior verification gap.",
            }
        ],
        "currentStructure": {"fromCarrier": "subprocess-only stage wiring"},
        "proposedStructure": {"toCarrier": "injected stage seam"},
        "rationale": "The seam targets the runner capability specifically rather than arbitrary cleanup.",
        "premiseConfidence": "unresolved",
        "conclusionConfidence": {"band": "medium", "value": 0.6},
        "validationRecipe": {
            "action": "try an injected runner seam behind the same CLI",
            "observable": "stage-order test coverage",
            "expectedDirection": "increase",
        },
        "neighborAlternativeId": "near.subprocess",
    }
    dream.update(overrides)
    return dream


def _write_dreams(tmp_path: Path, dreams: list[dict[str, Any]]) -> Path:
    path = tmp_path / "dreams.json"
    path.write_text(json.dumps({"dreams": dreams, "provenance": {"modelId": "fixture"}}), encoding="utf-8")
    return path


def test_grounded_dream_passes_with_all_resolved(tmp_path: Path) -> None:
    model_path, cap_path, model, cap_map = _write_inputs(tmp_path)
    result = gate_dreams(project_model_path=model_path, capability_map_path=cap_path, dreams_path=_write_dreams(tmp_path, [_dream(model, cap_map)]))

    assert result.accepted_count == 1
    assert result.killed_count == 0
    accepted = result.document["dreams"][0]
    assert accepted["premiseConfidence"] == "all_resolved"
    assert accepted["targetCapabilityIds"] == [cap_map["capabilities"][0]["id"]]
    assert result.document["provenance"]["gatedBy"] == "arena.dream_gate"


def test_planted_fabricated_anchor_is_killed(tmp_path: Path) -> None:
    model_path, cap_path, model, cap_map = _write_inputs(tmp_path)
    fabricated = _dream(model, cap_map)
    fabricated["citedEvidence"][0]["anchorId"] = "comp.fabricated"

    result = gate_dreams(project_model_path=model_path, capability_map_path=cap_path, dreams_path=_write_dreams(tmp_path, [fabricated]))

    assert result.accepted_count == 0
    assert result.trace["killedDreams"][0]["premiseConfidence"] == "unresolved"
    assert "unresolved verificationGap comp.fabricated" in result.trace["killedDreams"][0]["reasons"][0]


def test_missing_recipe_is_killed(tmp_path: Path) -> None:
    model_path, cap_path, model, cap_map = _write_inputs(tmp_path)
    bad = _dream(model, cap_map)
    del bad["validationRecipe"]

    result = gate_dreams(project_model_path=model_path, capability_map_path=cap_path, dreams_path=_write_dreams(tmp_path, [bad]))

    assert result.accepted_count == 0
    assert any("validationRecipe" in reason for reason in result.trace["killedDreams"][0]["reasons"])


def test_invalid_mode_is_killed(tmp_path: Path) -> None:
    model_path, cap_path, model, cap_map = _write_inputs(tmp_path)
    bad = _dream(model, cap_map, mode="patch_file")

    result = gate_dreams(project_model_path=model_path, capability_map_path=cap_path, dreams_path=_write_dreams(tmp_path, [bad]))

    assert result.accepted_count == 0
    assert any("mode" in reason for reason in result.trace["killedDreams"][0]["reasons"])


def test_unreviewed_capability_map_is_gated_and_labeled_unreviewed(tmp_path: Path) -> None:
    model_path, cap_path, model, cap_map = _write_inputs(tmp_path)
    cap_map["review"]["reviewed"] = False
    cap_path.write_text(json.dumps(cap_map), encoding="utf-8")

    result = gate_dreams(project_model_path=model_path, capability_map_path=cap_path, dreams_path=_write_dreams(tmp_path, [_dream(model, cap_map)]))

    assert result.accepted_count == 1
    assert result.killed_count == 0
    assert result.document["capabilityMap"]["reviewed"] is False


def test_capability_map_graph_hash_must_match_source_model(tmp_path: Path) -> None:
    model_path, cap_path, model, cap_map = _write_inputs(tmp_path)
    cap_map["sourceModel"]["graphHash"] = "0" * 64
    cap_path.write_text(json.dumps(cap_map), encoding="utf-8")

    with pytest.raises(DreamGateError, match="graphHash does not match"):
        gate_dreams(project_model_path=model_path, capability_map_path=cap_path, dreams_path=_write_dreams(tmp_path, [_dream(model, cap_map)]))


def test_gate_writes_trace_for_killed_dream(tmp_path: Path) -> None:
    model_path, cap_path, model, cap_map = _write_inputs(tmp_path)
    bad = _dream(model, cap_map)
    bad["citedEvidence"][0]["contentHash"] = "0" * 64
    output = tmp_path / "gated.json"
    trace = tmp_path / "trace.json"

    result = write_gated_dreams(
        project_model_path=model_path,
        capability_map_path=cap_path,
        dreams_path=_write_dreams(tmp_path, [bad]),
        output_path=output,
        trace_path=trace,
    )

    assert result.accepted_count == 0
    assert output.exists()
    assert trace.exists()
    assert "contentHash mismatch" in trace.read_text(encoding="utf-8")
