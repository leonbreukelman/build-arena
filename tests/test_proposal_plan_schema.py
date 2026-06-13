from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator

from arena.proposal_planner import build_proposal_plan

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "docs" / "schemas" / "proposal-plan-v0.schema.json"


def test_proposal_plan_schema_accepts_planner_output(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "README.md").write_text("# Readme\n", encoding="utf-8")
    scorecard = tmp_path / "scorecard.json"
    scorecard.write_text(
        json.dumps(
            {
                "schemaVersion": "project-intake-scorecard/v0",
                "id": "scorecard-schema",
                "snapshotId": "snapshot-schema",
                "projectRoot": str(repo),
                "findings": [
                    {
                        "id": "doc.index.missing",
                        "title": "Docs index is missing",
                        "evidence": [{"kind": "absence", "path": "docs/index.md", "checked": True}],
                        "recommendedAction": "Create docs/index.md as canonical docs navigation.",
                        "verification": ["test -e docs/index.md"],
                        "priorityScore": 728.0,
                        "rank": 1,
                    }
                ],
            },
            sort_keys=True,
        ),
        encoding="utf-8",
    )

    payload = build_proposal_plan(repo, scorecard, max_candidates=10).to_jsonable()
    assert "skippedFindings" in payload
    assert "skippedCount" in payload
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    errors = sorted(Draft202012Validator(schema).iter_errors(payload), key=lambda error: list(error.path))

    assert errors == []
