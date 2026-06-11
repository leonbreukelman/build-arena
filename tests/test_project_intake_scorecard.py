from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from arena.project_intake_scorecard import (
    PROFILE_WEIGHTS,
    build_project_intake_scorecard,
    finding_priority_score,
    scorecard_to_markdown,
)

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "docs" / "schemas" / "project-intake-scorecard-v0.schema.json"


def _snapshot(path: Path, repo: Path) -> Path:
    payload: dict[str, Any] = {
        "schemaVersion": "project-model/v1",
        "id": "snapshot-scorecard",
        "project": {"projectRoot": str(repo), "projectId": "scorecard", "goal": "test", "nonGoals": ["none"]},
        "provenance": {"git": {"headOid": "abc123", "dirty": False, "dirtyPaths": []}},
        "projectGraph": {"graphHash": "graph-hash"},
        "hashes": {"artifactHashes": {"project-model-v1.json": "hash"}},
        "snapshot": {"verification_gaps": [{"id": "gap.test", "severity": "medium", "description": "No integration smoke exists."}]},
        "iterationReadiness": {
            "qualityGates": [
                {"id": "quality.pytest", "command": "uv run pytest tests -q", "mode": "test", "safeToRunByDefault": True, "includedInAcceptance": True},
                {"id": "quality.ruff", "command": "uv run ruff check .", "mode": "lint", "safeToRunByDefault": True, "includedInAcceptance": True},
            ],
            "openQuestions": [{"id": "question.live", "question": "Is live smoke manual only?"}],
            "priorityBacklog": [{"id": "pm.backlog", "rank": 1, "title": "Verify smoke", "suggestedVerification": ["uv run pytest tests -q"]}],
        },
    }
    path.write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")
    return path


def _validate(payload: dict[str, Any]) -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    errors = sorted(Draft202012Validator(schema).iter_errors(payload), key=lambda error: list(error.path))
    assert errors == []


def test_profile_weights_match_reviewed_spec() -> None:
    assert PROFILE_WEIGHTS["new-project"]["documentation_project_knowledge"] == 28
    assert PROFILE_WEIGHTS["new-project"]["reproducible_verification"] == 20
    assert PROFILE_WEIGHTS["active-development"]["reproducible_verification"] == 24
    assert PROFILE_WEIGHTS["production"]["security_supply_chain_hygiene"] == 20
    assert PROFILE_WEIGHTS["documentation-first"]["documentation_project_knowledge"] == 33
    assert set(PROFILE_WEIGHTS) == {"new-project", "active-development", "production", "documentation-first"}
    assert all(len(weights) == 8 for weights in PROFILE_WEIGHTS.values())


def test_priority_formula_is_deterministic_and_weighted() -> None:
    docs_score = finding_priority_score(
        dimension_weight=28,
        severity="high",
        confidence="high",
        effort="small",
        impact_on_future_iteration=5,
        risk_reduction=5,
        verification_gain=3,
        doc_knowledge_gain=5,
    )
    code_cleanup_score = finding_priority_score(
        dimension_weight=14,
        severity="low",
        confidence="medium",
        effort="medium",
        impact_on_future_iteration=1,
        risk_reduction=1,
        verification_gain=1,
        doc_knowledge_gain=1,
    )

    assert docs_score == 1512.0
    assert docs_score > code_cleanup_score


def test_scorecard_records_absence_findings_quality_gates_and_first_recommendation(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "pyproject.toml").write_text("[project]\nname='scorecard'\nversion='0.0.0'\n", encoding="utf-8")
    snapshot = _snapshot(tmp_path / "project-model-v1.json", repo)

    scorecard = build_project_intake_scorecard(repo, snapshot, profile="new-project")

    ids = {finding["id"] for finding in scorecard["findings"]}
    assert "doc.readme.missing" in ids
    assert "agent.agents-md.missing" in ids
    assert "verification.quality-gates.present" in ids
    assert scorecard["firstRecommendedImprovement"]["findingId"] == scorecard["findings"][0]["id"]
    assert scorecard["advisoryOnly"] is True
    _validate(scorecard)


def test_scorecard_output_is_stable_and_markdown_is_concise(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    snapshot = _snapshot(tmp_path / "project-model-v1.json", repo)

    first = build_project_intake_scorecard(repo, snapshot, profile="documentation-first")
    second = build_project_intake_scorecard(repo, snapshot, profile="documentation-first")
    markdown = scorecard_to_markdown(first)

    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)
    assert "# Project Intake Scorecard" in markdown
    assert "Advisory only" in markdown
    assert first["profile"] == "documentation-first"


def test_scorecard_cli_writes_json_and_markdown(tmp_path: Path) -> None:
    from arena.project_intake_scorecard import main

    repo = tmp_path / "repo"
    repo.mkdir()
    snapshot = _snapshot(tmp_path / "project-model-v1.json", repo)
    output = tmp_path / "scorecard.json"
    markdown = tmp_path / "scorecard.md"

    rc = main(["--project", str(repo), "--snapshot", str(snapshot), "--profile", "new-project", "--output", str(output), "--markdown-output", str(markdown)])

    assert rc == 0
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["schemaVersion"] == "project-intake-scorecard/v0"
    assert markdown.exists()


def test_scorecard_does_not_write_to_target_repo(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    snapshot = _snapshot(tmp_path / "project-model-v1.json", repo)
    before = sorted(path.relative_to(repo).as_posix() for path in repo.rglob("*") if path.is_file())

    build_project_intake_scorecard(repo, snapshot, profile="new-project")

    after = sorted(path.relative_to(repo).as_posix() for path in repo.rglob("*") if path.is_file())
    assert after == before


def test_scorecard_source_has_no_live_provider_imports() -> None:
    source = (ROOT / "arena" / "project_intake_scorecard.py").read_text(encoding="utf-8")

    forbidden = ["project_model_llm", "diff_proposer", "OpenAICompatible", "LiveProjectModelLLM", "XAI_API_KEY", "ANTHROPIC_API_KEY"]
    assert not any(token in source for token in forbidden)
