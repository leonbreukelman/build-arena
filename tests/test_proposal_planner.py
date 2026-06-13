from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from arena.proposal_planner import build_proposal_plan, candidate_to_hypothesis


def _scorecard(path: Path, project: Path) -> Path:
    payload: dict[str, Any] = {
        "schemaVersion": "project-intake-scorecard/v0",
        "id": "scorecard-test",
        "snapshotId": "snapshot-test",
        "projectRoot": str(project),
        "snapshotPath": str(path.parent / "project-model-v1.json"),
        "snapshotHash": "snapshot-hash",
        "repoHead": "abc123",
        "profile": "new-project",
        "weights": {"documentation_project_knowledge": 28},
        "advisoryOnly": True,
        "findings": [
            {
                "id": "doc.index.missing",
                "dimension": "documentation_project_knowledge",
                "title": "Docs index is missing",
                "severity": "medium",
                "confidence": "high",
                "evidence": [{"kind": "absence", "path": "docs/index.md", "checked": True}],
                "whyItMatters": "No docs entrypoint.",
                "recommendedAction": "Create docs/index.md as canonical docs navigation.",
                "verification": ["test -e docs/index.md"],
                "autonomyBoundary": "safe_to_patch_docs_only",
                "estimatedEffort": "small",
                "impactOnFutureIteration": 4,
                "riskReduction": 3,
                "verificationGain": 1,
                "docKnowledgeGain": 5,
                "priorityScore": 728.0,
                "rank": 1,
            },
            {
                "id": "agent.agents-md.missing",
                "dimension": "ai_agent_usability",
                "title": "AGENTS.md is missing",
                "severity": "high",
                "confidence": "high",
                "evidence": [{"kind": "absence", "path": "AGENTS.md", "checked": True}],
                "whyItMatters": "No agent instructions.",
                "recommendedAction": "Create AGENTS.md with commands, boundaries, and definition of done.",
                "verification": ["test -e AGENTS.md"],
                "autonomyBoundary": "safe_to_patch_docs_only",
                "estimatedEffort": "small",
                "impactOnFutureIteration": 5,
                "riskReduction": 5,
                "verificationGain": 2,
                "docKnowledgeGain": 4,
                "priorityScore": 672.0,
                "rank": 2,
            },
            {
                "id": "verification.quality-gates.present",
                "dimension": "reproducible_verification",
                "title": "Project Model exposes local quality gates",
                "severity": "low",
                "confidence": "high",
                "evidence": [{"kind": "project_model", "path": "iterationReadiness.qualityGates", "checked": True}],
                "whyItMatters": "Configured safe local checks are visible to intake and proposer handoff.",
                "recommendedAction": "Keep these commands linked in future handoff packets.",
                "verification": ["uv run ruff check .", "uv run python -m pytest -q", "uv run mypy src/fmc_mcp"],
                "autonomyBoundary": "advisory_only",
                "estimatedEffort": "small",
                "impactOnFutureIteration": 2,
                "riskReduction": 2,
                "verificationGain": 4,
                "docKnowledgeGain": 1,
                "priorityScore": 196.0,
                "rank": 3,
            },
        ],
        "improvementCandidates": [],
        "firstRecommendedImprovement": {"findingId": "doc.index.missing"},
    }
    path.write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")
    return path


def test_proposal_plan_builds_grounded_top_n_without_copying_recommended_action(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "README.md").write_text("# Readme\n", encoding="utf-8")
    scorecard = _scorecard(tmp_path / "scorecard.json", repo)

    plan = build_proposal_plan(repo, scorecard, max_candidates=10)

    assert plan.candidate_count == 2
    assert plan.skipped_count == 1
    assert plan.skipped_findings[0]["finding_id"] == "verification.quality-gates.present"
    assert plan.skipped_findings[0]["reason"] == "no_single_file_target"
    assert plan.candidates[0].finding_id == "doc.index.missing"
    assert plan.candidates[0].target_path == "docs/index.md"
    assert plan.candidates[0].intent != "Create docs/index.md as canonical docs navigation."
    assert "existing repository files" in plan.candidates[0].intent
    assert "plain text" not in plan.candidates[0].intent
    assert "title only" in plan.candidates[0].intent
    assert plan.candidates[0].repo_facts_block
    assert "README.md" in plan.candidates[0].repo_facts_block
    assert any("Do not invent Markdown links" in item for item in plan.candidates[0].grounding_constraints)
    assert any("title only" in item and "no filename" in item for item in plan.candidates[0].grounding_constraints)
    assert plan.candidates[1].finding_id == "agent.agents-md.missing"
    assert plan.candidates[1].target_path == "AGENTS.md"
    assert plan.candidates[1].intent != "Create AGENTS.md with commands, boundaries, and definition of done."
    assert "Quality gate commands:" in plan.candidates[1].repo_facts_block
    assert "uv run ruff check ." in plan.candidates[1].repo_facts_block
    assert "uv run python -m pytest -q" in plan.candidates[1].repo_facts_block
    assert "Autonomy boundaries from intake:" in plan.candidates[1].repo_facts_block
    assert "safe_to_patch_docs_only" in plan.candidates[1].repo_facts_block
    assert "all local Markdown links resolve" in plan.candidates[1].success_criterion
    assert plan.candidates[1].verification_commands == (
        "test -s AGENTS.md",
        "python3 -m arena.markdown_links --repo . --path AGENTS.md",
    )


def test_proposal_plan_maps_missing_docs_directories_to_index_markdown_targets(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "README.md").write_text("# Readme\n", encoding="utf-8")
    scorecard = tmp_path / "scorecard.json"
    scorecard.write_text(
        json.dumps(
            {
                "schemaVersion": "project-intake-scorecard/v0",
                "id": "scorecard-directory",
                "snapshotId": "snapshot-directory",
                "projectRoot": str(repo),
                "findings": [
                    {
                        "id": "decision.history.missing",
                        "title": "Decision records are missing",
                        "evidence": [{"kind": "absence", "path": "docs/decisions", "checked": True}],
                        "recommendedAction": "Create decision records for architecture-significant constraints.",
                        "verification": ["test -e docs/decisions"],
                        "priorityScore": 512.0,
                        "rank": 1,
                    }
                ],
            },
            sort_keys=True,
        ),
        encoding="utf-8",
    )

    plan = build_proposal_plan(repo, scorecard, max_candidates=10)

    assert plan.candidates[0].target_path == "docs/decisions/index.md"
    assert plan.candidates[0].verification_commands == (
        "test -s docs/decisions/index.md",
        "python3 -m arena.markdown_links --repo . --path docs/decisions/index.md",
    )


def test_proposal_plan_requires_source_references_for_compliance_repos(tmp_path: Path) -> None:
    repo = tmp_path / "cmmc-level1-readiness-assistant"
    repo.mkdir()
    (repo / "README.md").write_text("# CMMC Readiness\n", encoding="utf-8")
    scorecard = _scorecard(tmp_path / "scorecard.json", repo)

    plan = build_proposal_plan(repo, scorecard, max_candidates=10)

    docs_candidate = next(candidate for candidate in plan.candidates if candidate.target_path == "docs/index.md")
    assert "Source references" in "\n".join(docs_candidate.grounding_constraints)
    assert docs_candidate.verification_commands == (
        "test -s docs/index.md",
        "python3 -m arena.markdown_links --repo . --path docs/index.md --require-source-references",
    )


def test_proposal_plan_is_stable_and_caps_candidates(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "README.md").write_text("# Readme\n", encoding="utf-8")
    scorecard = _scorecard(tmp_path / "scorecard.json", repo)

    first = build_proposal_plan(repo, scorecard, max_candidates=1).to_jsonable()
    second = build_proposal_plan(repo, scorecard, max_candidates=1).to_jsonable()

    assert first == second
    assert first["candidateCount"] == 2
    assert first["omittedCount"] == 1
    assert len(first["candidates"]) == 1


def test_candidate_to_hypothesis_uses_one_target_and_success_criterion(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "README.md").write_text("# Readme\n", encoding="utf-8")
    plan = build_proposal_plan(repo, _scorecard(tmp_path / "scorecard.json", repo), max_candidates=1)

    hypothesis = candidate_to_hypothesis(plan.candidates[0], cycle_id="cycle-docs-index", plan_id=plan.id)

    assert hypothesis.target_files == ["docs/index.md"]
    assert hypothesis.intent == plan.candidates[0].intent
    assert hypothesis.reasoning_blob_sha == plan.id
