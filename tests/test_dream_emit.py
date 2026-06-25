from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from arena.dream_emit import DreamEmitError, emit_dream, load_gated_dreams, render_dream_markdown

GRAPH_HASH = "c" * 64
PROMPT_HASH = "d" * 64
CONTENT_HASH = "e" * 64
INPUT_HASH = "f" * 64


def _dream(**overrides: Any) -> dict[str, Any]:
    dream = {
        "id": "dream.test",
        "mode": "carrier_swap",
        "idea": "Consider moving stage execution behind an injected seam.",
        "targetCapabilityIds": ["capability.runner"],
        "citedEvidence": [
            {
                "anchorKind": "component",
                "anchorId": "comp.runner",
                "contentHash": CONTENT_HASH,
                "claim": "The runner component owns stage orchestration.",
            }
        ],
        "rationale": "The idea specifically targets the current runner carrier, not arbitrary cleanup.",
        "premiseConfidence": "all_resolved",
        "conclusionConfidence": {"band": "medium", "value": 0.6},
        "validationRecipe": {
            "action": "try an injected runner seam",
            "observable": "stage-order coverage",
            "expectedDirection": "increase",
        },
        "neighborAlternativeId": "near.runner",
    }
    dream.update(overrides)
    return dream


def _doc(dreams: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "schemaVersion": "dream/v0",
        "projectId": "fixture-project",
        "sourceModel": {"projectModelV1Path": "/tmp/project-model-v1.json", "graphHash": GRAPH_HASH},
        "capabilityMap": {"path": "/tmp/capability-map.json", "reviewed": True},
        "dreams": dreams,
        "provenance": {
            "generatedBy": "arena.dream_generate",
            "researchedBy": "arena.dream_research",
            "gatedBy": "arena.dream_gate",
            "promptHashes": {"generate": PROMPT_HASH, "research": "a" * 64, "gate": "b" * 64},
            "modelId": "fixture-model",
            "inputHashes": {"rawDreams": INPUT_HASH},
        },
    }


def _write(tmp_path: Path, document: dict[str, Any], name: str = "gated-dreams.json") -> Path:
    path = tmp_path / name
    path.write_text(json.dumps(document), encoding="utf-8")
    return path


def test_all_resolved_dream_renders_readable_sections(tmp_path: Path) -> None:
    output = emit_dream(_write(tmp_path, _doc([_dream()])), tmp_path / "dream.md")
    text = output.read_text(encoding="utf-8")

    assert text.startswith("# Dream Proposals")
    assert "Advisory tier-3 hypotheses" in text
    assert "component `comp.runner` — The runner component owns stage orchestration." in text
    assert "Premise confidence (mechanical): `all_resolved`" in text
    assert "Conclusion confidence (speculative/capped): `medium` (0.6)" in text
    assert "To validate, try `try an injected runner seam`; check `stage-order coverage` moves `increase`." in text


def test_byte_identical_repeat(tmp_path: Path) -> None:
    path = _write(tmp_path, _doc([_dream()]))
    first = emit_dream(path, tmp_path / "a.md").read_bytes()
    second = emit_dream(path, tmp_path / "b.md").read_bytes()
    assert first == second


def test_internal_hashes_do_not_leak_into_body(tmp_path: Path) -> None:
    text = emit_dream(_write(tmp_path, _doc([_dream()])), tmp_path / "dream.md").read_text("utf-8")
    body = text.split("---", 1)[0]

    assert CONTENT_HASH not in text
    assert INPUT_HASH not in text
    assert "contentHash" not in text
    assert "inputHashes" not in text
    assert PROMPT_HASH not in body  # prompt hashes are footer-only provenance


def test_partial_dream_never_reaches_dream_md(tmp_path: Path) -> None:
    path = _write(tmp_path, _doc([_dream(premiseConfidence="partial")]))
    output = tmp_path / "dream.md"

    with pytest.raises(DreamEmitError, match="non-all_resolved"):
        emit_dream(path, output)
    assert not output.exists()


def test_no_dreams_fails_closed(tmp_path: Path) -> None:
    path = _write(tmp_path, _doc([]))
    with pytest.raises(DreamEmitError, match="no all_resolved"):
        emit_dream(path, tmp_path / "dream.md")


def test_fail_closed_bad_schema_version(tmp_path: Path) -> None:
    doc = _doc([_dream()])
    doc["schemaVersion"] = "dream/v1"
    with pytest.raises(DreamEmitError, match="schemaVersion"):
        load_gated_dreams(_write(tmp_path, doc))


def test_never_writes_proposal_md(tmp_path: Path) -> None:
    path = _write(tmp_path, _doc([_dream()]))
    proposal = tmp_path / "proposal.md"
    with pytest.raises(DreamEmitError, match="refuses to write proposal.md"):
        emit_dream(path, proposal)
    assert not proposal.exists()

    proposal_upper = tmp_path / "proposal.MD"
    with pytest.raises(DreamEmitError, match="refuses to write proposal.md"):
        emit_dream(path, proposal_upper)
    assert not proposal_upper.exists()


def test_emit_requires_gate_marker(tmp_path: Path) -> None:
    doc = _doc([_dream()])
    del doc["provenance"]["gatedBy"]
    path = _write(tmp_path, doc)

    with pytest.raises(DreamEmitError, match="lacks arena.dream_gate provenance"):
        emit_dream(path, tmp_path / "dream.md")


def test_render_orders_neighbor_backed_carrier_swap_first() -> None:
    doc = _doc(
        [
            _dream(id="z-function", mode="function_remap", idea="Function remap", neighborAlternativeId=None),
            _dream(id="a-carrier", idea="Carrier swap with neighbor"),
        ]
    )
    text = render_dream_markdown(doc)
    assert text.index("Carrier swap with neighbor") < text.index("Function remap")
