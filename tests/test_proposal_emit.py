from __future__ import annotations

import copy
import json
import subprocess
from pathlib import Path

import pytest

from arena.proposal_emit import emit_proposal, main, render_ticket_markdown, top_candidate


def _candidate(**overrides):  # type: ignore[no-untyped-def]
    candidate = {
        "rank": 1,
        "finding_id": "doc.index.missing",
        "title": "Docs index is missing",
        "target_path": "docs/index.md",
        "intent": "Create a grounded docs/index.md.",
        "success_criterion": "docs/index.md exists and is grounded.",
        "repo_facts_hash": "INTERNAL_REPO_FACTS_HASH_SHOULD_NOT_APPEAR",
        "repo_facts_block": "INTERNAL_REPO_FACTS_BLOCK_SHOULD_NOT_APPEAR",
        "grounding_constraints": [
            "Do not invent Markdown links.",
            "Cite existing repository files.",
        ],
        "verification_commands": [
            "test -s docs/index.md",
            "python3 -m arena.markdown_links --repo . --path docs/index.md --require-source-references",
        ],
        "priority_score": 728.0,
        "evidence_refs": [
            {"kind": "absence", "path": "docs/index.md", "checked": True},
            {"path": "README.md", "kind": "source", "checked": True},
        ],
        "source_recommended_action": "Create docs/index.md as canonical docs navigation.",
        "target_paths": ["docs/index.md"],
        "base_lineage": {"sentinel": "INTERNAL_LINEAGE_SHOULD_NOT_APPEAR"},
        "intent_hash": "INTERNAL_INTENT_HASH_SHOULD_NOT_APPEAR",
        "proposal_key": "INTERNAL_PROPOSAL_KEY_SHOULD_NOT_APPEAR",
        "registry_status": "INTERNAL_REGISTRY_STATUS_SHOULD_NOT_APPEAR",
        "fabricated_field": "FABRICATED_FIELD_SHOULD_NOT_APPEAR",
    }
    candidate.update(overrides)
    return candidate


def _plan(*candidates):  # type: ignore[no-untyped-def]
    return {
        "schemaVersion": "proposal-plan/v0",
        "id": "proposal-plan-test",
        "sourceScorecardId": "scorecard-test",
        "snapshotId": "snapshot-test",
        "projectRoot": "/tmp/repo",
        "repoFactsHash": "plan-facts-hash",
        "baseLineage": {},
        "candidateCount": len(candidates),
        "omittedCount": 0,
        "skippedCount": 0,
        "skippedFindings": [],
        "findingDispositions": [],
        "candidates": list(candidates),
    }


def test_render_ticket_markdown_maps_every_populated_ticket_field() -> None:
    candidate = _candidate()

    rendered = render_ticket_markdown(candidate)

    assert rendered.startswith("# Docs index is missing\n")
    for expected in [
        "## What & where",
        "Create a grounded docs/index.md.",
        "`docs/index.md`",
        "## Why",
        "\"kind\": \"absence\"",
        "\"path\": \"docs/index.md\"",
        "Create docs/index.md as canonical docs navigation.",
        "## Definition of done",
        "docs/index.md exists and is grounded.",
        "## Constraints / guardrails",
        "Do not invent Markdown links.",
        "Cite existing repository files.",
        "## How to verify",
        "`test -s docs/index.md`",
        "`python3 -m arena.markdown_links --repo . --path docs/index.md --require-source-references`",
        "## Priority & source",
        "Priority score: 728.0",
        "Finding ID: `doc.index.missing`",
    ]:
        assert expected in rendered


def test_render_ticket_markdown_uses_rank_one_only_and_omits_unmapped_fields() -> None:
    rank_one = _candidate()
    rank_two = _candidate(
        rank=2,
        finding_id="agent.agents-md.missing",
        title="RANK_TWO_TITLE_SHOULD_NOT_APPEAR",
        intent="RANK_TWO_INTENT_SHOULD_NOT_APPEAR",
        target_paths=["AGENTS.md"],
    )

    rendered = render_ticket_markdown(top_candidate(_plan(rank_two, rank_one)))

    assert "Docs index is missing" in rendered
    absent = [
        "RANK_TWO_TITLE_SHOULD_NOT_APPEAR",
        "RANK_TWO_INTENT_SHOULD_NOT_APPEAR",
        "INTERNAL_REPO_FACTS_HASH_SHOULD_NOT_APPEAR",
        "INTERNAL_REPO_FACTS_BLOCK_SHOULD_NOT_APPEAR",
        "INTERNAL_LINEAGE_SHOULD_NOT_APPEAR",
        "INTERNAL_INTENT_HASH_SHOULD_NOT_APPEAR",
        "INTERNAL_PROPOSAL_KEY_SHOULD_NOT_APPEAR",
        "INTERNAL_REGISTRY_STATUS_SHOULD_NOT_APPEAR",
        "FABRICATED_FIELD_SHOULD_NOT_APPEAR",
    ]
    for value in absent:
        assert value not in rendered


def test_render_ticket_markdown_is_deterministic_with_stable_evidence_key_order() -> None:
    candidate = _candidate()
    reordered = copy.deepcopy(candidate)
    reordered["evidence_refs"] = [
        {"checked": True, "path": "docs/index.md", "kind": "absence"},
        {"checked": True, "kind": "source", "path": "README.md"},
    ]

    assert render_ticket_markdown(candidate) == render_ticket_markdown(candidate)
    assert render_ticket_markdown(candidate) == render_ticket_markdown(reordered)


def test_render_ticket_markdown_fallback_title_and_empty_section_omission() -> None:
    candidate = _candidate(
        title="  ",
        finding_id="fallback.finding",
        grounding_constraints=[],
        verification_commands=[],
        evidence_refs=[],
        source_recommended_action="",
    )

    rendered = render_ticket_markdown(candidate)

    assert rendered.startswith("# fallback.finding\n")
    assert "## Why" not in rendered
    assert "## Constraints / guardrails" not in rendered
    assert "## How to verify" not in rendered


def test_emit_proposal_cli_writes_same_bytes_as_renderer(tmp_path: Path) -> None:
    plan = _plan(_candidate())
    plan_path = tmp_path / "proposal-plan.json"
    output = tmp_path / "proposal.md"
    direct_output = tmp_path / "proposal-direct.md"
    plan_path.write_text(json.dumps(plan, sort_keys=True), encoding="utf-8")

    rc = main(["--plan", str(plan_path), "--output", str(output)])
    emit_proposal(plan_path, direct_output)

    assert rc == 0
    assert output.read_text(encoding="utf-8") == render_ticket_markdown(top_candidate(plan))
    assert direct_output.read_text(encoding="utf-8") == output.read_text(encoding="utf-8")


def test_cli_module_invocation_writes_output(tmp_path: Path) -> None:
    plan_path = tmp_path / "proposal-plan.json"
    output = tmp_path / "proposal.md"
    plan_path.write_text(json.dumps(_plan(_candidate()), sort_keys=True), encoding="utf-8")

    result = subprocess.run(
        ["python3", "-m", "arena.proposal_emit", "--plan", str(plan_path), "--output", str(output)],
        cwd=Path(__file__).resolve().parents[1],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert output.is_file()
    assert "Docs index is missing" in output.read_text(encoding="utf-8")


@pytest.mark.parametrize(
    "plan,error",
    [
        (_plan(), "no candidate with rank 1"),
        (_plan(_candidate(rank=2)), "no candidate with rank 1"),
        (_plan(_candidate(), _candidate(finding_id="duplicate.rank.one")), "multiple candidates with rank 1"),
    ],
)
def test_empty_or_invalid_rank_one_plan_fails_closed(tmp_path: Path, plan: dict, error: str) -> None:
    plan_path = tmp_path / "proposal-plan.json"
    output = tmp_path / "proposal.md"
    plan_path.write_text(json.dumps(plan, sort_keys=True), encoding="utf-8")

    rc = main(["--plan", str(plan_path), "--output", str(output)])

    assert rc == 1
    assert not output.exists()

    with pytest.raises(ValueError, match=error):
        top_candidate(plan)
