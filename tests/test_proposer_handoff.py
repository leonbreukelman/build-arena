from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from arena.boundary import DEFAULT_READ_ONLY_DIRS, DEFAULT_READ_ONLY_FILES
from arena.proposer_handoff import build_proposer_handoff, handoff_to_dict

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "docs" / "schemas" / "proposer-handoff-v0.schema.json"


def _scorecard(path: Path, *, verification: list[str] | None = None) -> Path:
    payload: dict[str, Any] = {
        "schemaVersion": "project-intake-scorecard/v0",
        "id": "scorecard-1",
        "snapshotId": "snapshot-1",
        "projectRoot": str(path.parent),
        "profile": "new-project",
        "advisoryOnly": True,
        "findings": [
            {
                "id": "doc.readme.missing",
                "dimension": "documentation_project_knowledge",
                "title": "README is missing",
                "severity": "high",
                "confidence": "high",
                "evidence": [{"kind": "absence", "path": "README.md", "checked": True}],
                "whyItMatters": "No entrypoint.",
                "recommendedAction": "Create README.",
                "verification": verification if verification is not None else ["test -f README.md"],
                "autonomyBoundary": "safe_to_patch_docs_only",
                "estimatedEffort": "small",
                "priorityScore": 1512.0,
            }
        ],
        "firstRecommendedImprovement": {"findingId": "doc.readme.missing", "title": "README is missing"},
    }
    path.write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")
    return path


def _freshness(path: Path, status: str = "fresh") -> Path:
    payload = {
        "schemaVersion": "project-model-freshness/v0",
        "snapshotId": "snapshot-1",
        "status": status,
        "safeForMutation": status == "fresh",
        "safeForReadOnlyReview": True,
        "exitCode": 0 if status == "fresh" else 2,
        "warnings": [],
    }
    path.write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")
    return path


def _validate(payload: dict[str, Any]) -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    errors = sorted(Draft202012Validator(schema).iter_errors(payload), key=lambda error: list(error.path))
    assert errors == []


def test_handoff_from_fresh_scorecard_is_schema_valid_and_non_authorizing(tmp_path: Path) -> None:
    handoff = build_proposer_handoff(_scorecard(tmp_path / "scorecard.json"), _freshness(tmp_path / "freshness.json"))
    payload = handoff_to_dict(handoff)

    assert payload["schemaVersion"] == "proposer-handoff/v0"
    assert payload["freshnessStatus"] == "fresh"
    assert payload["selectedFindingId"] == "doc.readme.missing"
    assert payload["targetFiles"] == ["README.md"]
    assert payload["verificationCommands"] == ["test -f README.md"]
    assert payload["notAuthorizedForMutation"] is True
    _validate(payload)


def test_non_fresh_status_blocks_mutation_in_handoff(tmp_path: Path) -> None:
    payload = handoff_to_dict(build_proposer_handoff(_scorecard(tmp_path / "scorecard.json"), _freshness(tmp_path / "freshness.json", "dirty-worktree")))

    assert payload["freshnessStatus"] == "dirty-worktree"
    assert payload["notAuthorizedForMutation"] is True
    assert any("freshness" in note.lower() for note in payload["advisoryNotes"])


def test_missing_verification_requires_owner_approval(tmp_path: Path) -> None:
    payload = handoff_to_dict(build_proposer_handoff(_scorecard(tmp_path / "scorecard.json", verification=[]), _freshness(tmp_path / "freshness.json")))

    assert payload["requiresOwnerApproval"] is True
    assert any("verification" in note.lower() for note in payload["advisoryNotes"])


def test_prohibited_paths_include_full_boundary_defaults(tmp_path: Path) -> None:
    payload = handoff_to_dict(build_proposer_handoff(_scorecard(tmp_path / "scorecard.json"), _freshness(tmp_path / "freshness.json")))

    for path in [*DEFAULT_READ_ONLY_DIRS, *DEFAULT_READ_ONLY_FILES]:
        assert path in payload["prohibitedPaths"]
    for literal in ["scorer/", "verifier/", "schema/", "arena/generated/", "dashboard/src/lib/generated/", ".arena/scorer.lock.toml"]:
        assert literal in payload["prohibitedPaths"]


def test_handoff_output_is_stable_for_identical_inputs(tmp_path: Path) -> None:
    scorecard = _scorecard(tmp_path / "scorecard.json")
    freshness = _freshness(tmp_path / "freshness.json")

    first = handoff_to_dict(build_proposer_handoff(scorecard, freshness))
    second = handoff_to_dict(build_proposer_handoff(scorecard, freshness))

    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)


def test_handoff_cli_writes_packet(tmp_path: Path) -> None:
    from arena.proposer_handoff import main

    output = tmp_path / "handoff.json"
    rc = main(["--scorecard", str(_scorecard(tmp_path / "scorecard.json")), "--freshness", str(_freshness(tmp_path / "freshness.json")), "--output", str(output)])

    assert rc == 0
    assert json.loads(output.read_text(encoding="utf-8"))["schemaVersion"] == "proposer-handoff/v0"


def test_handoff_source_has_no_live_provider_or_runner_imports() -> None:
    source = (ROOT / "arena" / "proposer_handoff.py").read_text(encoding="utf-8")

    forbidden = ["project_model_llm", "diff_proposer", "arena.loop", "OpenAICompatible", "LiveProjectModelLLM", "XAI_API_KEY", "ANTHROPIC_API_KEY"]
    assert not any(token in source for token in forbidden)
