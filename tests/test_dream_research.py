from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from arena.capability_lift import build_capability_map
from arena.dream_research import DreamResearchError, research_dreams, write_researched_dreams

GRAPH_HASH = "2" * 64


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
                    "responsibility": "Run stages",
                    "owned_node_ids": ["node.runner"],
                    "provenance_refs": ["prov:runner"],
                    "contract_ids": [],
                    "check_ids": [],
                    "verification_gap_ids": [],
                }
            ],
            "contracts": [],
            "verification_gaps": [],
            "near_neighbor_alternatives": [],
        },
        "projectGraph": {"graphHash": GRAPH_HASH, "nodes": [{"id": "node.runner", "path": "arena/runner.py"}], "edges": []},
        "iterationReadiness": {
            "componentProfiles": [
                {
                    "componentId": "comp.runner",
                    "ownedNodeIds": ["node.runner"],
                    "responsibilitySummary": "stage orchestration",
                    "behavioralTags": ["stage"],
                    "provenanceRefs": ["prov:profile"],
                }
            ]
        },
    }


def _write_inputs(tmp_path: Path, *, reviewed: bool = True) -> tuple[Path, Path, Path, str]:
    model_path = tmp_path / "project-model-v1.json"
    model_path.write_text(json.dumps(_model()), encoding="utf-8")
    cap_map = build_capability_map(model_path)
    cap_map["review"]["reviewed"] = reviewed
    cap_path = tmp_path / "capability-map.json"
    cap_path.write_text(json.dumps(cap_map), encoding="utf-8")
    capability_id = cap_map["capabilities"][0]["id"]
    raw = {
        "dreams": [
            {
                "id": "dream.raw",
                "mode": "function_remap",
                "idea": "Split orchestration roles.",
                "targetCapabilityIds": [capability_id],
                "citedEvidence": [{"anchorKind": "capability", "anchorId": capability_id, "contentHash": "a" * 64, "claim": "Capability exists."}],
                "rationale": "Raw rationale.",
                "conclusionConfidence": {"band": "low", "value": 0.2},
                "validationRecipe": {"action": "try split", "observable": "coupling", "expectedDirection": "decrease"},
            }
        ],
        "provenance": {
            "generatedBy": "arena.dream_generate",
            "researchedBy": "unresearched",
            "promptHashes": {"generate": "3" * 64},
            "modelId": "raw-model",
            "inputHashes": {"scorecard": "4" * 64},
        },
    }
    raw_path = tmp_path / "raw-dreams.json"
    raw_path.write_text(json.dumps(raw), encoding="utf-8")
    return model_path, cap_path, raw_path, capability_id


def _fake_research(capability_id: str) -> Any:
    def _call(prompt: str) -> dict[str, Any]:
        assert "Research these raw tier-3 dream proposals" in prompt
        return {
            "dreams": [
                {
                    "id": "dream.researched",
                    "mode": "function_remap",
                    "idea": "Consider separating selection orchestration from stage execution orchestration.",
                    "targetCapabilityIds": [capability_id],
                    "citedEvidence": [
                        {"anchorKind": "component", "anchorId": "comp.runner", "contentHash": "5" * 64, "claim": "Runner is the current carrier."},
                        {"anchorKind": "capability", "anchorId": capability_id, "contentHash": "6" * 64, "claim": "The capability exists in the reviewed map."},
                    ],
                    "rationale": "The researched claim names the specific carrier and capability boundary being redrawn.",
                    "conclusionConfidence": {"band": "medium", "value": 0.5},
                    "validationRecipe": {"action": "try the split", "observable": "runner coupling", "expectedDirection": "decrease"},
                }
            ]
        }

    return _call


def test_research_rewrites_raw_dream_into_premise_dense_shape(tmp_path: Path) -> None:
    model_path, cap_path, raw_path, capability_id = _write_inputs(tmp_path)
    document = research_dreams(
        project_model_path=model_path,
        capability_map_path=cap_path,
        dreams_path=raw_path,
        model=_fake_research(capability_id),
    )

    dream = document["dreams"][0]
    assert dream["id"] == "dream.researched"
    assert len(dream["citedEvidence"]) == 2
    assert dream["validationRecipe"]["observable"] == "runner coupling"
    assert document["provenance"]["generatedBy"] == "arena.dream_generate"
    assert document["provenance"]["researchedBy"] == "arena.dream_research"


def test_research_writes_output_file(tmp_path: Path) -> None:
    model_path, cap_path, raw_path, capability_id = _write_inputs(tmp_path)
    output = write_researched_dreams(
        project_model_path=model_path,
        capability_map_path=cap_path,
        dreams_path=raw_path,
        output_path=tmp_path / "researched.json",
        model=_fake_research(capability_id),
    )
    assert json.loads(output.read_text(encoding="utf-8"))["dreams"][0]["id"] == "dream.researched"


def test_research_runs_on_unreviewed_map(tmp_path: Path) -> None:
    model_path, cap_path, raw_path, capability_id = _write_inputs(tmp_path, reviewed=False)
    document = research_dreams(
        project_model_path=model_path,
        capability_map_path=cap_path,
        dreams_path=raw_path,
        model=_fake_research(capability_id),
    )

    assert document["capabilityMap"]["reviewed"] is False
    assert document["dreams"][0]["id"] == "dream.researched"


def test_research_fails_if_model_returns_no_researchable_dreams(tmp_path: Path) -> None:
    model_path, cap_path, raw_path, _capability_id = _write_inputs(tmp_path)

    def fake(_prompt: str) -> dict[str, Any]:
        return {"dreams": [{"id": "bad", "mode": "function_remap"}]}

    with pytest.raises(DreamResearchError, match="no dreams"):
        research_dreams(project_model_path=model_path, capability_map_path=cap_path, dreams_path=raw_path, model=fake)
