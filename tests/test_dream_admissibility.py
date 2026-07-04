from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from arena.dream_admissibility import (
    anchor_catalog_records,
    anchor_provenance_class,
    build_anchor_indexes,
    check_document_admissibility,
    check_document_admissibility_from_paths,
)
from arena.dream_gate import gate_dreams
from arena.dream_generate import generate_dreams
from arena.dream_research import research_dreams

FIXTURES = Path(__file__).parent / "fixtures" / "dream_admissibility"
MODEL = FIXTURES / "captured-project-model-v1.json"
CAPABILITY_MAP = FIXTURES / "captured-capability-map.json"
SCORECARD = FIXTURES / "captured-scorecard.json"
RESTATEMENTS = FIXTURES / "captured-restatement-dreams-v0.json"
POSITIVE = FIXTURES / "positive-divergent-dreams-v1.json"


def _load(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(payload, dict)
    return payload


def _cycle_model(edges: list[tuple[str, str]]) -> dict[str, Any]:
    modules = {
        "pkg.a": "node.a",
        "pkg.b": "node.b",
        "pkg.c": "node.c",
    }
    return {
        "snapshot": {"components": [], "contracts": [], "verification_gaps": [], "near_neighbor_alternatives": []},
        "projectGraph": {
            "graphHash": "a" * 64,
            "nodes": [
                {
                    "id": node_id,
                    "kind": "python_module",
                    "symbol": symbol,
                    "label": symbol,
                    "path": f"{symbol.replace('.', '/')}.py",
                }
                for symbol, node_id in modules.items()
            ],
            "edges": [
                {
                    "id": f"edge.{source}.{target}",
                    "kind": "imports",
                    "from_node_id": modules[source],
                    "to_node_id": modules[target],
                    "label": target,
                    "provenance_refs": [],
                }
                for source, target in edges
            ],
        },
        "iterationReadiness": {"componentProfiles": []},
    }


def test_graph_structural_import_cycle_anchor_detects_three_node_cycle() -> None:
    indexes = build_anchor_indexes(_cycle_model([("pkg.a", "pkg.b"), ("pkg.b", "pkg.c"), ("pkg.c", "pkg.a")]), {})

    cycle_anchors = [anchor for anchor in indexes["graphStructural"].values() if anchor["kind"] == "import_cycle"]

    assert cycle_anchors == [
        {
            "id": "graph.importCycle.pkg.a->pkg.b->pkg.c",
            "kind": "import_cycle",
            "moduleSymbols": ["pkg.a", "pkg.b", "pkg.c"],
            "cycleLength": 3,
            "nodeIds": ["node.a", "node.b", "node.c"],
            "provenanceRefs": [],
        }
    ]


def test_graph_structural_import_cycle_anchor_preserves_two_node_parity() -> None:
    indexes = build_anchor_indexes(_cycle_model([("pkg.a", "pkg.b"), ("pkg.b", "pkg.a")]), {})

    cycle_anchors = [anchor for anchor in indexes["graphStructural"].values() if anchor["kind"] == "import_cycle"]

    assert cycle_anchors == [
        {
            "id": "graph.importCycle.pkg.a->pkg.b",
            "kind": "import_cycle",
            "moduleSymbols": ["pkg.a", "pkg.b"],
            "cycleLength": 2,
            "nodeIds": ["node.a", "node.b"],
            "provenanceRefs": [],
        }
    ]


def test_graph_structural_import_cycle_anchor_absent_for_dag() -> None:
    indexes = build_anchor_indexes(_cycle_model([("pkg.a", "pkg.b"), ("pkg.b", "pkg.c")]), {})

    assert [anchor for anchor in indexes["graphStructural"].values() if anchor["kind"] == "import_cycle"] == []


def test_anchor_catalog_records_include_provenance_class() -> None:
    model = _cycle_model([("pkg.a", "pkg.b"), ("pkg.b", "pkg.c"), ("pkg.c", "pkg.a")])
    model["iterationReadiness"]["componentProfiles"] = [
        {
            "componentId": "comp.many-tags",
            "behavioralTags": ["a", "b", "c", "d", "e"],
            "provenanceRefs": ["prov:profile"],
        }
    ]
    model["snapshot"]["components"] = [{"id": "comp.snapshot", "name": "Snapshot-authored component"}]

    records = anchor_catalog_records(model, {})
    by_id = {record["anchorId"]: record for record in records}

    assert by_id["graph.importCycle.pkg.a->pkg.b->pkg.c"]["provenanceClass"] == "deterministic"
    assert by_id["graph.multiTagComponent.comp.many-tags"]["provenanceClass"] == "llm_derived"
    assert by_id["comp.snapshot"]["provenanceClass"] == "llm_derived"


def test_anchor_provenance_class_mapping_is_pinned() -> None:
    assert anchor_provenance_class("graphStructural", {"kind": "import_cycle"}) == "deterministic"
    assert anchor_provenance_class("graphStructural", {"kind": "high_fan_in"}) == "deterministic"
    assert anchor_provenance_class("graphStructural", {"kind": "multi_tag_component"}) == "llm_derived"
    assert anchor_provenance_class("component", {"id": "comp.snapshot"}) == "llm_derived"


def _prompt_json(prompt: str, marker: str) -> dict[str, Any]:
    assert marker in prompt
    payload = json.loads(prompt.split(marker, 1)[1])
    assert isinstance(payload, dict)
    return payload


def test_frozen_captured_restatements_are_inadmissible_with_structural_delta_reason() -> None:
    report = check_document_admissibility_from_paths(
        project_model_path=MODEL,
        capability_map_path=CAPABILITY_MAP,
        dreams_path=RESTATEMENTS,
    )

    assert report["summary"] == {"admissible": 0, "inadmissible": 2, "total": 2}
    by_id = {dream["dreamId"]: dream for dream in report["dreams"]}
    for dream_id in ("dream-1", "dream-2"):
        failed = [item for item in by_id[dream_id]["requirements"] if not item["passed"]]
        structural = [item for item in failed if item["requirement"] == "structural_delta"]
        assert structural, failed
        assert "no proposed structure was provided" in structural[0]["reason"]


def test_gate_kills_frozen_captured_restatements_before_emit(tmp_path: Path) -> None:
    result = gate_dreams(project_model_path=MODEL, capability_map_path=CAPABILITY_MAP, dreams_path=RESTATEMENTS)

    assert result.accepted_count == 0
    assert result.killed_count == 2
    for killed in result.trace["killedDreams"]:
        reasons = "\n".join(killed["reasons"])
        assert "admissibility.structural_delta" in reasons
        assert "no proposed structure was provided" in reasons


def test_positive_divergent_hypothesis_is_admissible_and_gate_accepted() -> None:
    report = check_document_admissibility_from_paths(
        project_model_path=MODEL,
        capability_map_path=CAPABILITY_MAP,
        dreams_path=POSITIVE,
    )
    assert report["summary"] == {"admissible": 1, "inadmissible": 0, "total": 1}

    result = gate_dreams(project_model_path=MODEL, capability_map_path=CAPABILITY_MAP, dreams_path=POSITIVE)
    assert result.accepted_count == 1
    accepted = result.document["dreams"][0]
    assert accepted["premiseConfidence"] == "all_resolved"
    assert accepted["currentStructure"]["fromCarrier"] != accepted["proposedStructure"]["toCarrier"]


def test_captured_input_replay_generate_research_yields_admissible_dream(tmp_path: Path) -> None:
    def generate_model(prompt: str) -> dict[str, Any]:
        payload = _prompt_json(prompt, "Current facts:\n")
        assert payload["goal"] == "build-arena dream run"
        assert payload["nonGoals"] == ["do not treat file buckets as final components"]
        assert payload["priorityBacklog"]
        assert payload["productInvariants"]
        assert payload["verificationGaps"]
        assert payload["graphStructuralSummary"]
        tension = next(anchor for anchor in payload["tensionAnchorCatalog"] if anchor["anchorKind"] == "priorityBacklog")
        capability_id = "capability.component.client"
        return {
            "dreams": [
                {
                    "id": "dream-replay-client-carrier",
                    "mode": "carrier_swap",
                    "idea": "Move high-risk client responsibilities from MCPClient to a ClientPort seam.",
                    "targetCapabilityIds": [capability_id],
                    "citedEvidence": [
                        {
                            "anchorKind": tension["anchorKind"],
                            "anchorId": tension["anchorId"],
                            "contentHash": tension["contentHash"],
                            "claim": "The backlog records high-risk client responsibilities that should be split or documented.",
                        }
                    ],
                    "currentStructure": {"fromCarrier": "MCPClient"},
                    "proposedStructure": {"toCarrier": "ClientPort seam owned by server wiring"},
                    "rationale": "The backlog tension is about carrier responsibilities, so a carrier seam is the structural mutation to test.",
                    "conclusionConfidence": {"band": "medium", "value": 0.6},
                    "validationRecipe": {
                        "action": "build the seam and compare graph metrics",
                        "observable": "fan-in count for node:4042451215c279f0dca7",
                        "expectedDirection": "decrease",
                    },
                }
            ]
        }

    def research_model(prompt: str) -> dict[str, Any]:
        payload = _prompt_json(prompt, "Current model:\n")
        assert "without collapsing their mutation" in prompt
        raw = payload["rawDreams"][0]
        assert raw["currentStructure"]["fromCarrier"] != raw["proposedStructure"]["toCarrier"]
        return {
            "dreams": [
                {
                    **raw,
                    "idea": "Move high-risk client responsibilities from MCPClient to a ClientPort seam while preserving public behavior.",
                    "rationale": "Research preserves the from->to carrier delta and grounds it in the backlog tension plus fan-in metric.",
                }
            ]
        }

    raw_doc = generate_dreams(
        project_model_path=MODEL,
        capability_map_path=CAPABILITY_MAP,
        scorecard_path=SCORECARD,
        model=generate_model,
    )
    raw_path = tmp_path / "raw-dreams.json"
    raw_path.write_text(json.dumps(raw_doc), encoding="utf-8")

    researched_doc = research_dreams(
        project_model_path=MODEL,
        capability_map_path=CAPABILITY_MAP,
        dreams_path=raw_path,
        model=research_model,
    )
    researched_path = tmp_path / "researched-dreams.json"
    researched_path.write_text(json.dumps(researched_doc), encoding="utf-8")

    gated = gate_dreams(project_model_path=MODEL, capability_map_path=CAPABILITY_MAP, dreams_path=researched_path)
    assert gated.accepted_count >= 1
    report = check_document_admissibility(
        gated.document,
        project_model=_load(MODEL),
        capability_map=_load(CAPABILITY_MAP),
    )
    assert report["summary"]["admissible"] == gated.accepted_count
    assert report["summary"]["inadmissible"] == 0
