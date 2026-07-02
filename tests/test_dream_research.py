from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from arena import dream_research
from arena.capability_lift import build_capability_map
from arena.dream_research import DreamResearchError, research_dreams, write_researched_dreams
from arena.llm_adapter import OpenAICompatibleChatClient

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
                "currentStructure": {"fromBinding": "combined runner orchestration"},
                "proposedStructure": {"toBinding": "split selection and execution orchestration"},
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
        assert "Research these raw tier-3 divergent hypotheses" in prompt
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
                    "currentStructure": {"fromBinding": "combined runner orchestration"},
                    "proposedStructure": {"toBinding": "split selection and execution orchestration"},
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


def test_main_refuses_live_model_without_allow_live_before_client_construction(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    model_path, cap_path, raw_path, _capability_id = _write_inputs(tmp_path)

    def forbidden_resolve(*_args: Any, **_kwargs: Any) -> None:
        raise AssertionError("provider config must not be resolved without --allow-live")

    def forbidden_client(*_args: Any, **_kwargs: Any) -> None:
        raise AssertionError("client must not be constructed without --allow-live")

    monkeypatch.setattr(dream_research, "resolve_provider_config", forbidden_resolve)
    monkeypatch.setattr(dream_research, "OpenAICompatibleChatClient", forbidden_client)

    rc = dream_research.main(
        [
            "--project-model",
            str(model_path),
            "--capability-map",
            str(cap_path),
            "--dreams",
            str(raw_path),
            "--output",
            str(tmp_path / "researched.json"),
            "--live-model",
            "grok-requested",
        ]
    )

    assert rc == 3
    assert "--allow-live" in capsys.readouterr().err


def test_research_live_client_rejects_served_model_mismatch(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("XAI_API_KEY", "test-key")
    model_path, cap_path, raw_path, _capability_id = _write_inputs(tmp_path)

    def fake_urlopen(request: Any, timeout: int) -> _FakeResponse:
        _ = request, timeout
        return _FakeResponse(
            {
                "model": "unexpected-served-model",
                "choices": [{"finish_reason": "stop", "message": {"content": "{\"dreams\": []}"}}],
            }
        )

    def client_factory(config: Any, **kwargs: Any) -> OpenAICompatibleChatClient:
        return OpenAICompatibleChatClient(config=config, urlopen=fake_urlopen, **kwargs)

    monkeypatch.setattr(dream_research, "OpenAICompatibleChatClient", client_factory)

    with pytest.raises(ValueError, match="served unexpected model"):
        research_dreams(
            project_model_path=model_path,
            capability_map_path=cap_path,
            dreams_path=raw_path,
            live_model="grok-requested",
            allow_live=True,
        )


class _FakeResponse:
    def __init__(self, payload: dict[str, Any]) -> None:
        self.status = 200
        self._payload = payload

    def __enter__(self) -> _FakeResponse:
        return self

    def __exit__(self, *exc: object) -> None:
        return None

    def read(self) -> bytes:
        return json.dumps(self._payload).encode()
