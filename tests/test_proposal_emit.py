"""Tests for ``arena.proposal_emit`` -- rank-1 rendering, leak-freedom, determinism, fail-closed."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from arena.proposal_emit import (
    LEAK_FIELDS,
    EmitError,
    emit_proposal,
    load_reranked_plan,
    main,
    render_proposal_markdown,
    select_rank_one,
)

# Distinctive sentinel values for every internal field that must never be rendered. Each is a
# string/number unlikely to collide with any legitimately rendered content, so a substring search
# of the output is a sound leak check.
LEAK_SENTINELS: dict[str, Any] = {
    "priority_score": 314159.0,
    "repo_facts_hash": "ZZLEAK-repo-facts-hash-ZZ",
    "repo_facts_block": "ZZLEAK-repo-facts-block-ZZ",
    "intent_hash": "ZZLEAK-intent-hash-ZZ",
    "proposal_key": "ZZLEAK-proposal-key-ZZ",
    "registry_status": "ZZLEAK-registry-status-ZZ",
    "base_lineage": {"baseHeadOid": "ZZLEAK-base-lineage-ZZ"},
}


def _candidate(
    finding_id: str = "finding-1",
    *,
    rank: int = 1,
    target: str = "src/pkg/a.py",
    title: str | None = None,
    intent: str | None = None,
    success: str | None = None,
    verification: list[str] | None = None,
    evidence_refs: list[dict[str, Any]] | None = None,
    constraints: list[str] | None = None,
    target_paths: list[str] | None = None,
    leak: bool = False,
) -> dict[str, Any]:
    """Build a schema-valid candidate. With ``leak=True``, fill internal fields with sentinels."""
    title = title if title is not None else f"Title for {finding_id}"
    intent = intent if intent is not None else f"Improve {target} with a grounded check."
    success = success if success is not None else f"{target} exists and is non-empty."
    verification = [f"test -s {target}"] if verification is None else verification
    if evidence_refs is None:
        evidence_refs = [{"kind": "owned_surface", "path": target, "checked": True}]
    candidate: dict[str, Any] = {
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
        "target_paths": target_paths if target_paths is not None else [target],
        "base_lineage": {"baseHeadOid": "abc123"},
        "intent_hash": f"intent-{finding_id}",
        "proposal_key": f"proposal-{finding_id}",
        "registry_status": "untracked",
    }
    if leak:
        candidate.update(LEAK_SENTINELS)
    return candidate


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


def _write(tmp_path: Path, plan: dict[str, Any], name: str = "reranked-plan.json") -> Path:
    path = tmp_path / name
    path.write_text(json.dumps(plan), encoding="utf-8")
    return path


def test_selects_rank_one_regardless_of_order(tmp_path: Path) -> None:
    plan = _plan(
        [
            _candidate("loser", rank=2, title="LOSER TITLE"),
            _candidate("winner", rank=1, title="WINNER TITLE"),
        ]
    )
    out = emit_proposal(_write(tmp_path, plan), tmp_path / "proposal.md")
    text = out.read_text(encoding="utf-8")
    assert text.splitlines()[0] == "# WINNER TITLE"
    assert "LOSER TITLE" not in text


def test_all_sections_present(tmp_path: Path) -> None:
    out = emit_proposal(_write(tmp_path, _plan([_candidate()])), tmp_path / "proposal.md")
    text = out.read_text(encoding="utf-8")
    for header in (
        "## Proposed change",
        "## Why",
        "## Target file(s)",
        "## Definition of done",
        "## How to verify",
        "## Constraints",
        "## Source references",
    ):
        assert header in text
    assert text.startswith("# ")
    assert "_Provenance" in text


def test_no_internal_fields_leak(tmp_path: Path) -> None:
    plan = _plan([_candidate(rank=1, leak=True), _candidate("other", rank=2, leak=True)])
    out = emit_proposal(_write(tmp_path, plan), tmp_path / "proposal.md")
    text = out.read_text(encoding="utf-8")
    assert "314159" not in text
    for value in ("repo-facts-hash", "repo-facts-block", "intent-hash", "proposal-key",
                  "registry-status", "base-lineage"):
        assert value not in text
    # And the field names themselves never appear as labels.
    for field in LEAK_FIELDS:
        assert field not in text


def test_byte_identical_on_repeat(tmp_path: Path) -> None:
    plan_path = _write(tmp_path, _plan([_candidate()]))
    first = emit_proposal(plan_path, tmp_path / "a.md").read_bytes()
    second = emit_proposal(plan_path, tmp_path / "b.md").read_bytes()
    assert first == second


def test_verification_commands_rendered_verbatim_in_fence(tmp_path: Path) -> None:
    commands = ["uv run pytest tests -q", "uv run ruff check ."]
    plan = _plan([_candidate(verification=commands)])
    text = emit_proposal(_write(tmp_path, plan), tmp_path / "proposal.md").read_text("utf-8")
    body = text.split("## How to verify", 1)[1]
    assert "```sh" in body
    for command in commands:
        assert command in body


def test_evidence_refs_render_readable_not_raw_json(tmp_path: Path) -> None:
    refs = [{"kind": "import_cycle", "path": "src/pkg/a.py", "ref": "prov-7", "componentId": "C12"}]
    plan = _plan([_candidate(evidence_refs=refs)])
    text = emit_proposal(_write(tmp_path, plan), tmp_path / "proposal.md").read_text("utf-8")
    section = text.split("## Source references", 1)[1]
    assert "src/pkg/a.py (import_cycle)" in section
    assert "ref prov-7" in section
    assert "component C12" in section
    assert '{"kind"' not in section  # no raw JSON dump


def test_target_paths_and_single_deduplicated(tmp_path: Path) -> None:
    plan = _plan([_candidate(target="src/pkg/a.py", target_paths=["src/pkg/a.py", "src/pkg/b.py"])])
    text = emit_proposal(_write(tmp_path, plan), tmp_path / "proposal.md").read_text("utf-8")
    section = text.split("## Target file(s)", 1)[1].split("## Definition of done", 1)[0]
    assert section.count("src/pkg/a.py") == 1
    assert "src/pkg/b.py" in section


def test_render_is_pure_function() -> None:
    plan = _plan([_candidate()])
    candidate = select_rank_one(plan)
    assert render_proposal_markdown(plan, candidate) == render_proposal_markdown(plan, candidate)


def test_fail_closed_no_rank_one(tmp_path: Path) -> None:
    plan = _plan([_candidate("a", rank=2), _candidate("b", rank=3)])
    with pytest.raises(EmitError, match="rank-1"):
        emit_proposal(_write(tmp_path, plan), tmp_path / "proposal.md")
    assert not (tmp_path / "proposal.md").exists()


def test_fail_closed_multiple_rank_one(tmp_path: Path) -> None:
    plan = _plan([_candidate("a", rank=1), _candidate("b", rank=1)])
    with pytest.raises(EmitError, match="multiple rank-1"):
        select_rank_one(plan)


def test_fail_closed_bad_schema_version(tmp_path: Path) -> None:
    plan = _plan([_candidate()])
    plan["schemaVersion"] = "proposal-plan/v1"
    with pytest.raises(EmitError, match="schemaVersion"):
        load_reranked_plan(_write(tmp_path, plan))


def test_fail_closed_invalid_schema(tmp_path: Path) -> None:
    plan = _plan([_candidate()])
    del plan["projectRoot"]  # required top-level field
    with pytest.raises(EmitError, match="schema validation"):
        load_reranked_plan(_write(tmp_path, plan))


def test_fail_closed_unreadable_path(tmp_path: Path) -> None:
    with pytest.raises(EmitError, match="cannot read"):
        load_reranked_plan(tmp_path / "does-not-exist.json")


def test_fail_closed_not_json(tmp_path: Path) -> None:
    path = tmp_path / "bad.json"
    path.write_text("this is not json", encoding="utf-8")
    with pytest.raises(EmitError, match="not valid JSON"):
        load_reranked_plan(path)


def test_main_success_writes_and_prints(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    plan_path = _write(tmp_path, _plan([_candidate()]))
    out_path = tmp_path / "proposal.md"
    rc = main(["--reranked-plan", str(plan_path), "--output", str(out_path)])
    assert rc == 0
    assert out_path.exists()
    assert str(out_path) in capsys.readouterr().out


def test_main_failure_returns_one(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    plan = _plan([_candidate("a", rank=2)])
    plan_path = _write(tmp_path, plan)
    rc = main(["--reranked-plan", str(plan_path), "--output", str(tmp_path / "proposal.md")])
    assert rc == 1
    assert "failed" in capsys.readouterr().err
