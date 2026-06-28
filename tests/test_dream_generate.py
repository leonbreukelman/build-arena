from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from arena.capability_lift import build_capability_map
from arena.dream_generate import DreamGenerateError, generate_dreams, write_generated_dreams

GRAPH_HASH = "1" * 64


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
            "near_neighbor_alternatives": [{"id": "near.runner", "target_id": "comp.runner", "alternative": "in-process seam"}],
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
    scorecard = tmp_path / "scorecard.json"
    scorecard.write_text(json.dumps({"findings": [{"id": "verification.gap", "rank": 1}]}), encoding="utf-8")
    return model_path, cap_path, scorecard, cap_map["capabilities"][0]["id"]


def _fake_model(capability_id: str) -> Any:
    def _model_call(prompt: str) -> dict[str, Any]:
        assert "tier-3 divergent architectural hypotheses" in prompt
        return {
            "dreams": [
                {
                    "id": "dream.carrier",
                    "mode": "carrier_swap",
                    "idea": "Consider replacing subprocess glue with an injected stage seam.",
                    "targetCapabilityIds": [capability_id],
                    "citedEvidence": [{"anchorKind": "capability", "anchorId": capability_id, "contentHash": "a" * 64, "claim": "Runner capability exists."}],
                    "currentStructure": {"fromCarrier": "subprocess glue"},
                    "proposedStructure": {"toCarrier": "injected stage seam"},
                    "rationale": "The carrier swap specifically targets the runner capability.",
                    "conclusionConfidence": {"band": "medium", "value": 0.9},
                    "validationRecipe": {"action": "try the seam", "observable": "test coverage", "expectedDirection": "increase"},
                    "neighborAlternativeId": "near.runner",
                },
                {
                    "id": "dream.function",
                    "mode": "function_remap",
                    "idea": "Consider splitting proposal selection from execution orchestration.",
                    "targetCapabilityIds": [capability_id],
                    "citedEvidence": [{"anchorKind": "capability", "anchorId": capability_id, "contentHash": "b" * 64, "claim": "Runner combines stage orchestration today."}],
                    "currentStructure": {"fromBinding": "selection and execution in one runner"},
                    "proposedStructure": {"toBinding": "selection separated from execution orchestration"},
                    "rationale": "The remap changes the capability boundary rather than patching one file.",
                    "conclusionConfidence": {"band": "low", "value": 0.3},
                    "validationRecipe": {"action": "try the split", "observable": "orchestration coupling", "expectedDirection": "decrease"},
                },
            ]
        }

    return _model_call


def test_generate_yields_typed_diversity_and_minimum_grounding(tmp_path: Path) -> None:
    model_path, cap_path, scorecard, capability_id = _write_inputs(tmp_path)
    document = generate_dreams(
        project_model_path=model_path,
        capability_map_path=cap_path,
        scorecard_path=scorecard,
        model=_fake_model(capability_id),
    )

    modes = {dream["mode"] for dream in document["dreams"]}
    assert modes == {"carrier_swap", "function_remap"}
    for dream in document["dreams"]:
        assert dream["targetCapabilityIds"] == [capability_id]
        assert dream["citedEvidence"]
        assert dream["validationRecipe"]["action"]
    assert document["dreams"][0]["conclusionConfidence"]["value"] == 0.7  # capped


def test_generate_writes_output_file(tmp_path: Path) -> None:
    model_path, cap_path, scorecard, capability_id = _write_inputs(tmp_path)
    output = write_generated_dreams(
        project_model_path=model_path,
        capability_map_path=cap_path,
        scorecard_path=scorecard,
        output_path=tmp_path / "raw-dreams.json",
        model=_fake_model(capability_id),
    )
    assert json.loads(output.read_text(encoding="utf-8"))["dreams"][0]["id"] == "dream.carrier"


def test_generate_runs_on_unreviewed_map(tmp_path: Path) -> None:
    model_path, cap_path, scorecard, capability_id = _write_inputs(tmp_path, reviewed=False)
    document = generate_dreams(
        project_model_path=model_path,
        capability_map_path=cap_path,
        scorecard_path=scorecard,
        model=_fake_model(capability_id),
    )

    assert document["capabilityMap"]["reviewed"] is False
    assert {dream["mode"] for dream in document["dreams"]} == {"carrier_swap", "function_remap"}


def test_generate_drops_ungrounded_model_items_and_fails_if_none_remain(tmp_path: Path) -> None:
    model_path, cap_path, scorecard, _capability_id = _write_inputs(tmp_path)

    def fake(_prompt: str) -> dict[str, Any]:
        return {"dreams": [{"id": "bad", "mode": "carrier_swap"}]}

    with pytest.raises(DreamGenerateError, match="no dreams"):
        generate_dreams(project_model_path=model_path, capability_map_path=cap_path, scorecard_path=scorecard, model=fake)
