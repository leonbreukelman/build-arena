from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from jsonschema import Draft202012Validator

from arena import proposal_pairwise_reranker
from arena.llm_adapter import OpenAICompatibleChatClient
from arena.proposal_pairwise_reranker import (
    DefaultLLMProposalJudge,
    GraphIndex,
    JudgeResult,
    RerankError,
    build_candidate_payload,
    build_derived_plan,
    load_graph,
    prefilter_candidates,
    rerank_plan_payload,
    rerank_proposal_plan,
    run_pairwise_tournament,
    stable_plan_hash,
    validate_judge_payload,
)

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "docs" / "schemas" / "proposal-plan-v0.schema.json"


class SequenceJudge:
    def __init__(self, winners: list[str]) -> None:
        self.winners = winners
        self.calls: list[tuple[dict[str, Any], dict[str, Any], dict[str, Any]]] = []

    def compare(self, slot_a: dict[str, Any], slot_b: dict[str, Any], repo_context: dict[str, Any]) -> JudgeResult:
        self.calls.append((slot_a, slot_b, repo_context))
        winner = self.winners[len(self.calls) - 1]
        if winner == slot_a["finding_id"]:
            slot = "A"
            evidence_a = [slot_a["citable_evidence"][0]]
            evidence_b = [slot_b["citable_evidence"][0]]
        elif winner == slot_b["finding_id"]:
            slot = "B"
            evidence_a = [slot_a["citable_evidence"][0]]
            evidence_b = [slot_b["citable_evidence"][0]]
        else:
            slot = "A"
            evidence_a = [slot_a["citable_evidence"][0]]
            evidence_b = [slot_b["citable_evidence"][0]]
        return JudgeResult(
            winner_slot=slot,
            winner_finding_id=winner,
            candidate_a_evidence_cited=tuple(evidence_a),
            candidate_b_evidence_cited=tuple(evidence_b),
            reason=f"{winner} is better grounded, more specific, and more verifiable.",
            prompt_hash="prompt-hash",
            response_hash=f"response-{len(self.calls)}",
        )


def _candidate(
    finding_id: str,
    *,
    rank: int = 1,
    target: str = "src/pkg/a.py",
    title: str | None = None,
    intent: str | None = None,
    success: str | None = None,
    verification: list[str] | None = None,
    evidence_refs: list[dict[str, Any]] | None = None,
    constraints: list[str] | None = None,
) -> dict[str, Any]:
    title = title or f"Title for {finding_id}"
    intent = intent or f"Improve {target} with a grounded, target-specific check."
    success = success or f"{target} exists and is non-empty."
    verification = [f"test -s {target}"] if verification is None else verification
    evidence_refs = evidence_refs if evidence_refs is not None else [{"kind": "owned_surface", "path": target, "checked": True}]
    return {
        "rank": rank,
        "finding_id": finding_id,
        "title": title,
        "target_path": target,
        "intent": intent,
        "success_criterion": success,
        "repo_facts_hash": "facts-hash",
        "repo_facts_block": "Repository facts:\n- README.md exists: yes",
        "grounding_constraints": constraints or ["Use only repository-grounded files."],
        "verification_commands": verification,
        "priority_score": 1000.0 - rank,
        "evidence_refs": evidence_refs,
        "source_recommended_action": "Do the target-specific improvement.",
        "target_paths": [target],
        "base_lineage": {"baseHeadOid": "abc123"},
        "intent_hash": f"intent-{finding_id}",
        "proposal_key": f"proposal-{finding_id}",
        "registry_status": "untracked",
    }


def _plan(candidates: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "schemaVersion": "proposal-plan/v0",
        "id": "source-plan",
        "sourceScorecardId": "scorecard-1",
        "snapshotId": "snapshot-1",
        "projectRoot": "/tmp/example-repo",
        "repoFactsHash": "facts-hash",
        "baseLineage": {"baseHeadOid": "abc123"},
        "candidateCount": len(candidates),
        "omittedCount": 0,
        "skippedCount": 0,
        "skippedFindings": [],
        "findingDispositions": [],
        "candidates": candidates,
    }


def _graph(paths: tuple[str, ...] = ("src/pkg/a.py", "src/pkg/b.py", "README.md"), symbols: tuple[str, ...] = ("pkg.a", "pkg.b")) -> dict[str, Any]:
    nodes: list[dict[str, Any]] = []
    for index, path in enumerate(paths):
        nodes.append(
            {
                "id": f"node:file:{index}",
                "kind": "file",
                "label": path,
                "path": path,
                "symbol": None,
                "provenance_refs": [{"id": f"prov:file:{index}"}],
            }
        )
    for index, symbol in enumerate(symbols):
        nodes.append(
            {
                "id": f"node:module:{index}",
                "kind": "python_module",
                "label": symbol,
                "path": paths[min(index, len(paths) - 1)],
                "symbol": symbol,
                "provenance_refs": [{"id": f"prov:module:{index}"}],
            }
        )
    return {"schemaVersion": "project-graph/v0", "nodes": nodes, "edges": []}


def _schema_errors(plan: dict[str, Any]) -> list[Any]:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    return sorted(Draft202012Validator(schema).iter_errors(plan), key=lambda error: list(error.path))


def test_prefilter_rejects_unresolved_file_reference() -> None:
    graph = GraphIndex.from_graph(_graph(paths=("README.md",)))
    candidate = _candidate(
        "finding.unresolved",
        target="docs/new.md",
        intent="Create docs/new.md based on docs/missing.md evidence.",
        evidence_refs=[{"kind": "absence", "path": "docs/new.md", "checked": True}],
    )

    survivors, dropped = prefilter_candidates(_plan([candidate]), graph)

    assert survivors == []
    assert dropped[0].finding_id == "finding.unresolved"
    assert "unresolved_file_reference:docs/missing.md" in dropped[0].reasons


def test_prefilter_rejects_empty_or_unknown_verification_command() -> None:
    graph = GraphIndex.from_graph(_graph())
    empty = _candidate("finding.empty", verification=[])
    unknown = _candidate("finding.unknown", rank=2, verification=["definitely-not-real --flag src/pkg/a.py"])

    survivors, dropped = prefilter_candidates(_plan([empty, unknown]), graph)

    assert survivors == []
    reasons = {drop.finding_id: drop.reasons for drop in dropped}
    assert reasons["finding.empty"] == ["empty_verification"]
    assert any(reason.startswith("verification_unknown_executable:") for reason in reasons["finding.unknown"])


def test_prefilter_keeps_grounded_non_binding_verification_candidate() -> None:
    graph = GraphIndex.from_graph(_graph())
    candidate = _candidate(
        "finding.nonbinding",
        verification=["uv run pytest -q"],
        success="A test file exists for src/pkg/a.py with assertions covering the proposal.",
    )

    survivors, dropped = prefilter_candidates(_plan([candidate]), graph)

    assert [item["finding_id"] for item in survivors] == ["finding.nonbinding"]
    assert dropped == []


def test_prefilter_rejects_shell_control_verification_command() -> None:
    graph = GraphIndex.from_graph(_graph())
    candidate = _candidate("finding.shell", verification=["pytest && rm -rf build"])

    survivors, dropped = prefilter_candidates(_plan([candidate]), graph)

    assert survivors == []
    assert any(reason.startswith("verification_disallowed_shell:") for reason in dropped[0].reasons)


def test_prefilter_removed_binding_gate_reasons_are_not_emitted_for_safe_commands() -> None:
    graph = GraphIndex.from_graph(_graph())
    candidates = [
        _candidate("finding.nonbinding", verification=["uv run pytest -q"]),
        _candidate("finding.other-target", rank=2, verification=["test -s src/pkg/b.py"]),
        _candidate("finding.unknown-family", rank=3, verification=["python3 --version"]),
    ]

    survivors, dropped = prefilter_candidates(_plan(candidates), graph)

    assert [item["finding_id"] for item in survivors] == [
        "finding.nonbinding",
        "finding.other-target",
        "finding.unknown-family",
    ]
    assert dropped == []


def test_prefilter_keeps_missing_file_creation_target_without_requiring_graph_node() -> None:
    graph = GraphIndex.from_graph(_graph(paths=("README.md",)))
    candidate = _candidate(
        "doc.new",
        target="docs/new.md",
        success="docs/new.md exists and is non-empty.",
        verification=["test -s docs/new.md"],
        evidence_refs=[{"kind": "absence", "path": "docs/new.md", "checked": True}],
    )

    survivors, dropped = prefilter_candidates(_plan([candidate]), graph)

    assert [item["finding_id"] for item in survivors] == ["doc.new"]
    assert dropped == []


def test_prefilter_rejects_no_specific_target_location() -> None:
    graph = GraphIndex.from_graph(_graph())
    candidate = _candidate(
        "finding.vague",
        target="docs/",
        verification=["test -s docs/"],
        success="The docs target exists and is non-empty.",
        evidence_refs=[],
    )

    survivors, dropped = prefilter_candidates(_plan([candidate]), graph)

    assert survivors == []
    assert "directory_only_target:docs" in dropped[0].reasons


def test_prefilter_rejects_circular_definition_of_done() -> None:
    graph = GraphIndex.from_graph(_graph())
    candidate = _candidate(
        "finding.circular",
        success="The quality gate commands pass for this proposal.",
        verification=["test -s src/pkg/a.py"],
    )

    survivors, dropped = prefilter_candidates(_plan([candidate]), graph)

    assert survivors == []
    assert "circular_definition_of_done" in dropped[0].reasons


def test_tournament_runs_both_orderings_per_matchup() -> None:
    survivors = [
        _candidate("a", rank=1),
        _candidate("b", rank=2, target="src/pkg/b.py"),
        _candidate("c", rank=3, target="README.md"),
    ]
    judge = SequenceJudge(["a", "a", "a", "a"])

    result = run_pairwise_tournament(survivors, judge, {"projectRoot": "/tmp/repo"})

    assert result.winner["finding_id"] == "a"
    assert result.call_count == 4
    assert len(judge.calls) == 4
    assert [record["decision"] for record in result.tournament] == ["incumbent_kept", "incumbent_kept"]


def test_inconsistent_swapped_order_keeps_incumbent() -> None:
    survivors = [_candidate("a", rank=1), _candidate("b", rank=2, target="src/pkg/b.py")]
    judge = SequenceJudge(["a", "b"])

    result = run_pairwise_tournament(survivors, judge, {"projectRoot": "/tmp/repo"})

    assert result.winner["finding_id"] == "a"
    assert result.tournament[0]["consistent"] is False
    assert result.tournament[0]["decision"] == "position_inconsistent_keep_incumbent"


def test_consistent_challenger_replaces_incumbent() -> None:
    survivors = [_candidate("a", rank=1), _candidate("b", rank=2, target="src/pkg/b.py")]
    judge = SequenceJudge(["b", "b"])

    result = run_pairwise_tournament(survivors, judge, {"projectRoot": "/tmp/repo"})

    assert result.winner["finding_id"] == "b"
    assert result.tournament[0]["consistent"] is True
    assert result.tournament[0]["decision"] == "challenger_replaces_incumbent"


def test_output_plan_sets_winner_rank_one_and_preserves_candidate_fields_except_rank() -> None:
    source = _plan([_candidate("a", rank=1), _candidate("b", rank=2, target="src/pkg/b.py")])
    original_b = dict(source["candidates"][1])

    derived = build_derived_plan(source, source["candidates"][1], source["candidates"], [])

    assert derived["candidates"][0]["finding_id"] == "b"
    assert derived["candidates"][0]["rank"] == 1
    preserved = dict(derived["candidates"][0])
    preserved["rank"] = original_b["rank"]
    assert preserved == original_b
    assert derived["snapshotId"] == source["snapshotId"]
    assert derived["projectRoot"] == source["projectRoot"]
    assert _schema_errors(derived) == []


def test_trace_records_prefilter_drops_both_orderings_reasons_and_hashes() -> None:
    graph = _graph()
    keep_a = _candidate("a", rank=1)
    keep_b = _candidate("b", rank=2, target="src/pkg/b.py")
    drop = _candidate("drop", rank=3, verification=[])
    judge = SequenceJudge(["b", "b"])

    result = rerank_plan_payload(_plan([keep_a, keep_b, drop]), graph, judge, source_plan_path="plan.json", graph_path="graph.json")

    assert result.trace["preFilter"]["inputCandidateCount"] == 3
    assert result.trace["preFilter"]["survivorCount"] == 2
    assert result.trace["preFilter"]["dropped"][0]["reasons"] == ["empty_verification"]
    matchup = result.trace["tournament"][0]
    assert matchup["call_ab"]["prompt_hash"]
    assert matchup["call_ab"]["response_hash"]
    assert matchup["call_ba"]["prompt_hash"]
    assert matchup["call_ba"]["response_hash"]
    assert result.trace["callCount"] == 2


def test_no_survivors_fails_closed_without_output_plan(tmp_path: Path) -> None:
    plan_path = tmp_path / "plan.json"
    graph_path = tmp_path / "graph.json"
    output_path = tmp_path / "reranked.json"
    trace_path = tmp_path / "trace.json"
    plan_path.write_text(json.dumps(_plan([_candidate("drop", verification=[])])), encoding="utf-8")
    graph_path.write_text(json.dumps(_graph()), encoding="utf-8")

    with pytest.raises(RerankError, match="no candidates survived"):
        rerank_proposal_plan(tmp_path, plan_path, graph_path, output_path, trace_path, judge=SequenceJudge([]))

    assert not output_path.exists()
    trace = json.loads(trace_path.read_text(encoding="utf-8"))
    assert trace["preFilter"]["survivorCount"] == 0
    assert trace["callCount"] == 0


def test_single_survivor_uses_zero_llm_calls() -> None:
    candidate = _candidate("only")
    judge = SequenceJudge([])

    result = rerank_plan_payload(_plan([candidate]), _graph(), judge)

    assert result.plan["candidates"][0]["finding_id"] == "only"
    assert result.trace["callCount"] == 0
    assert judge.calls == []


def test_priority_score_and_original_rank_are_not_sent_to_judge() -> None:
    survivors = [_candidate("a", rank=1), _candidate("b", rank=2, target="src/pkg/b.py")]
    judge = SequenceJudge(["a", "a"])

    run_pairwise_tournament(survivors, judge, {"projectRoot": "/tmp/repo"})

    for slot_a, slot_b, _context in judge.calls:
        assert "priority_score" not in slot_a
        assert "priority_score" not in slot_b
        assert "rank" not in slot_a
        assert "rank" not in slot_b
    payload = build_candidate_payload(survivors[0])
    assert payload["citable_evidence"][0] == "target_path:src/pkg/a.py"


def test_schema_invalid_judge_response_fails_closed() -> None:
    candidate_a = build_candidate_payload(_candidate("a", rank=1))
    candidate_b = build_candidate_payload(_candidate("b", rank=2, target="src/pkg/b.py"))

    with pytest.raises(RerankError, match="winner_finding_id"):
        validate_judge_payload(
            {
                "winner_slot": "A",
                "winner_finding_id": "b",
                "candidate_a_evidence_cited": [candidate_a["citable_evidence"][0]],
                "candidate_b_evidence_cited": [candidate_b["citable_evidence"][0]],
                "reason": "wrong mapped winner",
            },
            candidate_a,
            candidate_b,
            prompt_hash="prompt",
            response_hash="response",
        )

    assert stable_plan_hash(_plan([_candidate("a")]))
    assert load_graph({"projectGraph": _graph()}) == _graph()


def test_default_llm_judge_requires_explicit_model(monkeypatch: pytest.MonkeyPatch) -> None:
    for env_name in ["BUILD_ARENA_LLM_MODEL", "BUILD_ARENA_XAI_MODEL", "XAI_MODEL"]:
        monkeypatch.delenv(env_name, raising=False)

    with pytest.raises(ValueError, match="explicit model"):
        DefaultLLMProposalJudge.create()

    monkeypatch.setenv("BUILD_ARENA_XAI_MODEL", "grok-explicit")
    judge = DefaultLLMProposalJudge.create()

    assert judge.client.config.model == "grok-explicit"
    assert judge.client.require_served_model_match is True


def test_default_llm_judge_rejects_served_model_mismatch(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("XAI_API_KEY", "test-key")
    monkeypatch.setenv("BUILD_ARENA_XAI_MODEL", "grok-requested")

    def fake_urlopen(request: Any, timeout: int) -> _FakeResponse:
        _ = request, timeout
        return _FakeResponse(
            {
                "model": "unexpected-served-model",
                "choices": [
                    {
                        "finish_reason": "stop",
                        "message": {
                            "content": json.dumps(
                                {
                                    "winner_slot": "A",
                                    "winner_finding_id": "a",
                                    "candidate_a_evidence_cited": ["target_path:src/pkg/a.py"],
                                    "candidate_b_evidence_cited": ["target_path:src/pkg/b.py"],
                                    "reason": "A is better grounded, more specific, and more verifiable.",
                                }
                            )
                        },
                    }
                ],
            }
        )

    def client_factory(*, config: Any, **kwargs: Any) -> OpenAICompatibleChatClient:
        return OpenAICompatibleChatClient(config=config, urlopen=fake_urlopen, **kwargs)

    monkeypatch.setattr(proposal_pairwise_reranker, "OpenAICompatibleChatClient", client_factory)
    judge = DefaultLLMProposalJudge.create()
    candidate_a = build_candidate_payload(_candidate("a", target="src/pkg/a.py"))
    candidate_b = build_candidate_payload(_candidate("b", target="src/pkg/b.py"))

    with pytest.raises(ValueError, match="served unexpected model"):
        judge.compare(candidate_a, candidate_b, {"projectRoot": "/tmp/repo"})


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
