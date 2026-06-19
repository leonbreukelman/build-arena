from __future__ import annotations

import json
from pathlib import Path

from arena.advisory_backlog import (
    advisory_expected_target,
    backlog_markdown_entry,
    build_advisory_expected,
    canonical_expected_text,
    expected_digest,
)
from arena.backlog_gate import validate_backlog_entry
from arena.proposal_planner import build_proposal_plan


def _repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "README.md").write_text("# Readme\n", encoding="utf-8")
    return repo


def _scorecard_with_snapshot(tmp_path: Path, repo: Path) -> Path:
    snapshot = tmp_path / "project-model-v1.json"
    snapshot.write_text(
        json.dumps(
            {
                "schemaVersion": "project-model/v1",
                "id": "snapshot-advisory",
                "snapshot": {
                    "verification_gaps": [
                        {"id": "gap.arch.guard", "description": "Architecture dependency direction is not yet guarded."}
                    ]
                },
                "iterationReadiness": {
                    "openQuestions": [
                        {"id": "question.arch.owner", "question": "Which package owns dependency direction decisions?"}
                    ],
                    "qualityGates": [],
                },
            },
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    scorecard = tmp_path / "scorecard.json"
    scorecard.write_text(
        json.dumps(
            {
                "schemaVersion": "project-intake-scorecard/v0",
                "id": "scorecard-advisory",
                "snapshotId": "snapshot-advisory",
                "snapshotPath": str(snapshot),
                "projectRoot": str(repo),
                "profile": "new-project",
                "weights": {"architecture_specs_contracts": 14},
                "findings": [
                    {
                        "id": "architecture.open-questions-or-gaps",
                        "dimension": "architecture_specs_contracts",
                        "title": "Architecture questions need routing",
                        "severity": "medium",
                        "confidence": "high",
                        "estimatedEffort": "small",
                        "evidence": [{"kind": "project_model", "path": "iterationReadiness.openQuestions", "checked": True}],
                        "recommendedAction": "Backlog advisory-only architecture questions when no graph signal exists.",
                        "verification": [],
                        "autonomyBoundary": "advisory_only",
                        "impactOnFutureIteration": 3,
                        "riskReduction": 2,
                        "verificationGain": 2,
                        "docKnowledgeGain": 2,
                        "priorityScore": 100.0,
                        "rank": 1,
                    }
                ],
            },
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    return scorecard


def _write_expected(repo: Path) -> Path:
    expected = build_advisory_expected(
        finding_id="architecture.open-questions-or-gaps",
        items=(
            {"kind": "open_question", "id": "question.arch.owner", "text": "Which package owns dependency direction decisions?"},
        ),
    )
    digest = expected_digest(expected)
    path = repo / advisory_expected_target(digest)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(canonical_expected_text(expected), encoding="utf-8")
    return path


def test_advisory_backlog_domain_routes_open_advisory_finding(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    scorecard = _scorecard_with_snapshot(tmp_path, repo)

    plan = build_proposal_plan(repo, scorecard, max_candidates=10)

    candidate = plan.candidates[0]
    assert candidate.finding_id == "architecture.open-questions-or-gaps"
    assert candidate.target_path == "docs/agent-backlog.md"
    assert candidate.target_paths[0] == "docs/agent-backlog.md"
    assert candidate.target_paths[1].startswith("docs/advisory-backlog-expected-")
    assert "question.arch.owner" in candidate.intent
    assert "Which package owns dependency direction decisions?" in candidate.intent
    assert plan.finding_dispositions[0]["disposition"] == "advisory_backlogged"
    assert candidate.verification_commands == (
        f"python3 -m arena.backlog_gate --repo . --path docs/agent-backlog.md --expected {candidate.target_paths[1]}",
    )


def test_backlog_gate_accepts_grounded_entry_and_rejects_noop_or_dead_links(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    expected_path = _write_expected(repo)
    backlog = repo / "docs" / "agent-backlog.md"
    backlog.parent.mkdir(parents=True, exist_ok=True)

    backlog.write_text("# Agent backlog\n\nTODO: fill this in later.\n", encoding="utf-8")
    assert validate_backlog_entry(repo, backlog, expected_path).reason == "boilerplate_entry"

    good = backlog_markdown_entry(
        finding_id="architecture.open-questions-or-gaps",
        items=(
            {"kind": "open_question", "id": "question.arch.owner", "text": "Which package owns dependency direction decisions?"},
        ),
    )
    backlog.write_text(good + "\n\n## Source references\n\n- README.md\n", encoding="utf-8")
    accepted = validate_backlog_entry(repo, backlog, expected_path)
    assert accepted.accepted is True
    assert accepted.reason == "accepted"

    backlog.write_text(good + "\n\n[Missing](missing.md)\n", encoding="utf-8")
    assert validate_backlog_entry(repo, backlog, expected_path).reason == "dead_local_link"
