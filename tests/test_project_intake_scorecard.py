from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
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


def _write_repo_file(repo: Path, rel_path: str, content: str = "present\n") -> None:
    target = repo / rel_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")


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
    assert scorecard["loopReadiness"]["advisory"] is True
    _validate(scorecard)


@pytest.mark.parametrize(
    ("finding_id", "present_path"),
    [
        ("verification.ci.missing", ".github/workflows/ci.yml"),
        ("verification.lockfile.missing", "uv.lock"),
        ("verification.precommit.missing", ".pre-commit-config.yaml"),
        ("security.policy.missing", "SECURITY.md"),
        ("security.dep-update.missing", ".github/dependabot.yml"),
        ("governance.contributing.missing", "CONTRIBUTING.md"),
        ("governance.codeowners.missing", "CODEOWNERS"),
        ("governance.templates.missing", ".github/pull_request_template.md"),
        ("ops.env-example.missing", ".env.example"),
        ("architecture.overview.missing", "ARCHITECTURE.md"),
    ],
)
def test_readiness_absence_checks_emit_once_and_clear_when_present(
    tmp_path: Path,
    finding_id: str,
    present_path: str,
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    snapshot = _snapshot(tmp_path / "project-model-v1.json", repo)

    missing = build_project_intake_scorecard(repo, snapshot, profile="new-project")
    assert finding_id in {finding["id"] for finding in missing["findings"]}

    _write_repo_file(repo, present_path)
    present = build_project_intake_scorecard(repo, snapshot, profile="new-project")
    assert finding_id not in {finding["id"] for finding in present["findings"]}
    _validate(present)


@pytest.mark.parametrize(
    ("rel_path", "content"),
    [
        ("pyproject.toml", "[tool.pytest.ini_options]\naddopts = '-q'\n"),
        ("Makefile", "test:\n\tpytest\n"),
        ("package.json", '{"scripts": {"test": "pytest"}}\n'),
        ("tox.ini", "[tox]\nenvlist = py\n"),
        ("pytest.ini", "[pytest]\naddopts = -q\n"),
    ],
)
def test_verification_test_command_sources_are_discovered(
    tmp_path: Path,
    rel_path: str,
    content: str,
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _write_repo_file(repo, rel_path, content)
    snapshot = _snapshot(tmp_path / "project-model-v1.json", repo)

    scorecard = build_project_intake_scorecard(repo, snapshot, profile="new-project")

    assert "verification.test-command.missing" not in {finding["id"] for finding in scorecard["findings"]}
    _validate(scorecard)


def test_dimension_scores_roll_up_readiness_checks(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    snapshot = _snapshot(tmp_path / "project-model-v1.json", repo)

    empty = build_project_intake_scorecard(repo, snapshot, profile="new-project")
    assert empty["dimensionScores"]["documentation_project_knowledge"] == {
        "covered": 0,
        "total": 2,
        "fraction": 0.0,
    }
    assert empty["dimensionScores"]["reproducible_verification"] == {
        "covered": 0,
        "total": 4,
        "fraction": 0.0,
    }

    _write_repo_file(repo, ".github/workflows/ci.yml")
    _write_repo_file(repo, "pyproject.toml", "[tool.pytest.ini_options]\naddopts = '-q'\n")
    partly_ready = build_project_intake_scorecard(repo, snapshot, profile="new-project")
    assert partly_ready["dimensionScores"]["reproducible_verification"] == {
        "covered": 2,
        "total": 4,
        "fraction": 0.5,
    }
    _validate(partly_ready)


def test_loop_readiness_fails_without_ci_or_test_command(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    snapshot = _snapshot(tmp_path / "project-model-v1.json", repo)

    scorecard = build_project_intake_scorecard(repo, snapshot, profile="new-project")

    ids = {finding["id"] for finding in scorecard["findings"]}
    assert "verification.ci.missing" in ids
    assert "verification.test-command.missing" in ids
    assert scorecard["loopReadiness"] == {
        "reproducibleVerificationGate": "fail",
        "failingChecks": ["verification.ci.missing", "verification.test-command.missing"],
        "advisory": True,
    }
    assert scorecard["advisoryOnly"] is True
    _validate(scorecard)


def test_loop_readiness_passes_with_ci_workflow_and_pytest_config(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _write_repo_file(repo, ".github/workflows/ci.yml")
    _write_repo_file(repo, "pyproject.toml", "[tool.pytest.ini_options]\naddopts = '-q'\n")
    snapshot = _snapshot(tmp_path / "project-model-v1.json", repo)

    scorecard = build_project_intake_scorecard(repo, snapshot, profile="new-project")

    ids = {finding["id"] for finding in scorecard["findings"]}
    assert "verification.ci.missing" not in ids
    assert "verification.test-command.missing" not in ids
    assert scorecard["loopReadiness"] == {
        "reproducibleVerificationGate": "pass",
        "failingChecks": [],
        "advisory": True,
    }
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


# --- Phase 1 (#27): intake must consume the decomposer's anchored interpretation ---


def _snapshot_with_components(path: Path, repo: Path) -> Path:
    """A v1 snapshot carrying graph nodes, components, observable checks, and
    componentProfiles so the scorecard can emit component-scoped findings.

    comp-auth: riskLevel=high, owns one source file, has NO observable check  -> untested
    comp-util: riskLevel=low,  owns one source file, HAS an observable check  -> tested
    """
    payload: dict[str, Any] = {
        "schemaVersion": "project-model/v1",
        "id": "snapshot-components",
        "project": {"projectRoot": str(repo), "projectId": "scorecard", "goal": "test", "nonGoals": ["none"]},
        "provenance": {"git": {"headOid": "abc123", "dirty": False, "dirtyPaths": []}},
        "projectGraph": {
            "graphHash": "graph-hash",
            "nodes": [
                {"id": "node.auth", "kind": "python_module", "path": "src/pkg/auth.py"},
                {"id": "node.util", "kind": "python_module", "path": "src/pkg/util.py"},
            ],
        },
        "hashes": {"artifactHashes": {"project-model-v1.json": "hash"}},
        "snapshot": {
            "verification_gaps": [{"id": "gap.test", "severity": "medium", "description": "No integration smoke exists."}],
            "components": [
                {"id": "comp-auth", "name": "Auth", "responsibility": "Authenticates and authorizes requests.", "owned_node_ids": ["node.auth"], "provenance_refs": ["prov.auth"], "contract_ids": [], "check_ids": [], "verification_gap_ids": []},
                {"id": "comp-util", "name": "Util", "responsibility": "Shared string and path helpers used widely.", "owned_node_ids": ["node.util"], "provenance_refs": ["prov.util"], "contract_ids": [], "check_ids": ["check-util"], "verification_gap_ids": []},
            ],
            "observable_checks": [
                {"id": "check-util", "description": "Util unit tests", "command": "uv run pytest tests/test_util.py -q", "component_ids": ["comp-util"], "contract_ids": [], "provenance_refs": ["prov.util"]},
            ],
        },
        "iterationReadiness": {
            "qualityGates": [
                {"id": "quality.pytest", "command": "uv run pytest tests -q", "mode": "test", "safeToRunByDefault": True, "includedInAcceptance": True},
            ],
            "openQuestions": [],
            "priorityBacklog": [],
            "componentProfiles": [
                {"componentId": "comp-auth", "ownedNodeIds": ["node.auth"], "responsibilitySummary": "Authn/authz", "keySymbols": [], "behavioralTags": ["auth"], "riskLevel": "high", "priorityRank": 1, "whyPriority": "security-sensitive", "provenanceRefs": ["prov.auth"]},
                {"componentId": "comp-util", "ownedNodeIds": ["node.util"], "responsibilitySummary": "Helpers", "keySymbols": [], "behavioralTags": [], "riskLevel": "low", "priorityRank": 2, "whyPriority": "low blast radius", "provenanceRefs": ["prov.util"]},
            ],
        },
    }
    path.write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")
    return path


def test_high_risk_untested_component_yields_nondoc_finding(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    snapshot = _snapshot_with_components(tmp_path / "project-model-v1.json", repo)

    scorecard = build_project_intake_scorecard(repo, snapshot, profile="active-development")

    untested = [f for f in scorecard["findings"] if f["id"] == "code.component.untested.comp-auth"]
    assert len(untested) == 1, "expected a non-doc finding for the high-risk untested component"
    finding = untested[0]
    # It must NOT be a documentation-only change.
    assert finding["autonomyBoundary"] != "safe_to_patch_docs_only"
    assert finding["dimension"] == "reproducible_verification"
    # Its target must be the real component source file, resolved via graph nodes.
    target_paths = [ev["path"] for ev in finding["evidence"] if ev.get("kind") == "owned_surface"]
    assert target_paths == ["src/pkg/auth.py"]
    # The tested low-risk component must NOT produce an untested finding.
    assert not any(f["id"] == "code.component.untested.comp-util" for f in scorecard["findings"])
    _validate(scorecard)


def test_high_risk_untested_component_becomes_nondoc_proposal_candidate(tmp_path: Path) -> None:
    from arena.proposal_planner import build_proposal_plan

    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "src" / "pkg").mkdir(parents=True)
    (repo / "src" / "pkg" / "auth.py").write_text("def login():\n    return True\n", encoding="utf-8")
    snapshot = _snapshot_with_components(tmp_path / "project-model-v1.json", repo)
    scorecard_path = tmp_path / "scorecard.json"
    scorecard = build_project_intake_scorecard(repo, snapshot, profile="active-development")
    scorecard_path.write_text(json.dumps(scorecard, sort_keys=True), encoding="utf-8")

    plan = build_proposal_plan(repo, scorecard_path, max_candidates=10)

    nondoc = [c for c in plan.candidates if c.target_path == "src/pkg/auth.py"]
    assert len(nondoc) == 1, "planner must produce a non-doc candidate for the untested component"
    assert not nondoc[0].target_path.endswith(".md")


def test_docs_absence_findings_still_emitted_with_components(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    snapshot = _snapshot_with_components(tmp_path / "project-model-v1.json", repo)

    scorecard = build_project_intake_scorecard(repo, snapshot, profile="new-project")

    ids = {f["id"] for f in scorecard["findings"]}
    assert "doc.readme.missing" in ids
    assert "agent.agents-md.missing" in ids


def test_high_risk_untested_component_outranks_docs_under_active_development(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    snapshot = _snapshot_with_components(tmp_path / "project-model-v1.json", repo)

    scorecard = build_project_intake_scorecard(repo, snapshot, profile="active-development")

    by_id = {f["id"]: f for f in scorecard["findings"]}
    assert "code.component.untested.comp-auth" in by_id
    assert "doc.index.missing" in by_id
    assert by_id["code.component.untested.comp-auth"]["priorityScore"] > by_id["doc.index.missing"]["priorityScore"]
    assert by_id["code.component.untested.comp-auth"]["rank"] < by_id["doc.index.missing"]["rank"]


def test_component_findings_are_deterministic(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    snapshot = _snapshot_with_components(tmp_path / "project-model-v1.json", repo)

    first = build_project_intake_scorecard(repo, snapshot, profile="active-development")
    second = build_project_intake_scorecard(repo, snapshot, profile="active-development")

    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)


def test_component_finding_evidence_is_grounded_in_snapshot(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    snapshot = _snapshot_with_components(tmp_path / "project-model-v1.json", repo)

    scorecard = build_project_intake_scorecard(repo, snapshot, profile="active-development")
    finding = next(f for f in scorecard["findings"] if f["id"] == "code.component.untested.comp-auth")

    # Every owned_surface path must be a real graph node path; component + provenance must come from the snapshot.
    known_paths = {"src/pkg/auth.py", "src/pkg/util.py"}
    for ev in finding["evidence"]:
        if ev.get("kind") == "owned_surface":
            assert ev["path"] in known_paths
        if ev.get("kind") == "component":
            assert ev["componentId"] == "comp-auth"


def test_component_risk_level_maps_to_severity(tmp_path: Path) -> None:
    from arena.project_intake_scorecard import _risk_level_to_severity

    assert _risk_level_to_severity("high") == "high"
    assert _risk_level_to_severity("medium") == "medium"
    assert _risk_level_to_severity("low") == "low"
    # Unknown values fail safe to medium, never silently to low.
    assert _risk_level_to_severity("bogus") == "medium"


def test_component_findings_absent_when_snapshot_lacks_components(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    # The legacy minimal fixture has no projectGraph.nodes / components / componentProfiles.
    snapshot = _snapshot(tmp_path / "project-model-v1.json", repo)

    scorecard = build_project_intake_scorecard(repo, snapshot, profile="active-development")

    assert not any(f["id"].startswith("code.component.untested") for f in scorecard["findings"])


# --- Phase 3 (#29): lint findings drive the code-quality domain ---


def test_scorecard_emits_lint_finding_for_file_with_violations(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "src" / "pkg").mkdir(parents=True)
    (repo / "pyproject.toml").write_text("[tool.ruff]\n", encoding="utf-8")
    # A real violation ruff will flag: unused import (F401) + unsorted (I001).
    (repo / "src" / "pkg" / "dirty.py").write_text("import os\nimport sys\n\n\ndef f():\n    return 1\n", encoding="utf-8")
    (repo / "src" / "pkg" / "clean.py").write_text("def g():\n    return 2\n", encoding="utf-8")
    snapshot = _snapshot(tmp_path / "project-model-v1.json", repo)

    scorecard = build_project_intake_scorecard(repo, snapshot, profile="active-development")

    lint_ids = {f["id"] for f in scorecard["findings"] if f["id"].startswith("code.quality.lint.")}
    assert "code.quality.lint.src/pkg/dirty.py" in lint_ids
    # The clean file must not produce a lint finding.
    assert "code.quality.lint.src/pkg/clean.py" not in lint_ids
    finding = next(f for f in scorecard["findings"] if f["id"] == "code.quality.lint.src/pkg/dirty.py")
    assert finding["autonomyBoundary"] != "safe_to_patch_docs_only"
    assert any(ev.get("path") == "src/pkg/dirty.py" for ev in finding["evidence"])


def test_scorecard_lint_findings_are_deterministic(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "src").mkdir(parents=True)
    (repo / "pyproject.toml").write_text("[tool.ruff]\n", encoding="utf-8")
    (repo / "src" / "a.py").write_text("import os\n\n\ndef f():\n    return 1\n", encoding="utf-8")
    (repo / "src" / "b.py").write_text("import sys\n\n\ndef g():\n    return 2\n", encoding="utf-8")
    snapshot = _snapshot(tmp_path / "project-model-v1.json", repo)

    first = build_project_intake_scorecard(repo, snapshot, profile="active-development")
    second = build_project_intake_scorecard(repo, snapshot, profile="active-development")

    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)


def test_scorecard_lint_findings_absent_when_no_violations(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "src").mkdir(parents=True)
    (repo / "pyproject.toml").write_text("[tool.ruff]\n", encoding="utf-8")
    (repo / "src" / "clean.py").write_text("def g():\n    return 2\n", encoding="utf-8")
    snapshot = _snapshot(tmp_path / "project-model-v1.json", repo)

    scorecard = build_project_intake_scorecard(repo, snapshot, profile="active-development")

    assert not any(f["id"].startswith("code.quality.lint.") for f in scorecard["findings"])


def _component_snapshot(path: Path, repo: Path, *, nodes: list[dict[str, Any]], components: list[dict[str, Any]], observable_checks: list[dict[str, Any]], profiles: list[dict[str, Any]]) -> Path:
    payload: dict[str, Any] = {
        "schemaVersion": "project-model/v1",
        "id": "snapshot-custom",
        "project": {"projectRoot": str(repo), "projectId": "scorecard", "goal": "test", "nonGoals": ["none"]},
        "provenance": {"git": {"headOid": "abc123", "dirty": False, "dirtyPaths": []}},
        "projectGraph": {"graphHash": "graph-hash", "nodes": nodes},
        "hashes": {"artifactHashes": {"project-model-v1.json": "hash"}},
        "snapshot": {"verification_gaps": [], "components": components, "observable_checks": observable_checks},
        "iterationReadiness": {"qualityGates": [], "openQuestions": [], "priorityBacklog": [], "componentProfiles": profiles},
    }
    path.write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")
    return path


def test_component_covered_only_by_observable_check_is_not_flagged(tmp_path: Path) -> None:
    """A component with empty check_ids but referenced by an observable_check's
    component_ids is covered and must NOT be flagged untested."""
    repo = tmp_path / "repo"
    repo.mkdir()
    snapshot = _component_snapshot(
        tmp_path / "pm.json",
        repo,
        nodes=[{"id": "node.svc", "kind": "python_module", "path": "src/pkg/svc.py"}],
        components=[{"id": "comp-svc", "name": "Svc", "responsibility": "Service layer handling requests end to end.", "owned_node_ids": ["node.svc"], "provenance_refs": ["prov.svc"], "contract_ids": [], "check_ids": [], "verification_gap_ids": []}],
        observable_checks=[{"id": "check-svc", "description": "svc tests", "command": "uv run pytest -q", "component_ids": ["comp-svc"], "contract_ids": [], "provenance_refs": ["prov.svc"]}],
        profiles=[{"componentId": "comp-svc", "ownedNodeIds": ["node.svc"], "responsibilitySummary": "svc", "keySymbols": [], "behavioralTags": [], "riskLevel": "high", "priorityRank": 1, "whyPriority": "x", "provenanceRefs": ["prov.svc"]}],
    )

    scorecard = build_project_intake_scorecard(repo, snapshot, profile="active-development")

    assert not any(f["id"] == "code.component.untested.comp-svc" for f in scorecard["findings"])


def test_workspace_scoped_check_does_not_suppress_component_candidate(tmp_path: Path) -> None:
    from arena.proposal_pairwise_reranker import GraphIndex, prefilter_candidates
    from arena.proposal_planner import build_proposal_plan

    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "src" / "pkg").mkdir(parents=True)
    (repo / "src" / "pkg" / "svc.py").write_text("def handle():\n    return True\n", encoding="utf-8")
    snapshot = _component_snapshot(
        tmp_path / "pm.json",
        repo,
        nodes=[{"id": "node.svc", "kind": "python_module", "path": "src/pkg/svc.py"}],
        components=[
            {
                "id": "comp-svc",
                "name": "Svc",
                "responsibility": "Service layer handling requests end to end.",
                "owned_node_ids": ["node.svc"],
                "provenance_refs": ["prov.svc"],
                "contract_ids": [],
                "check_ids": ["check.workspace-python-tests"],
                "verification_gap_ids": [],
            }
        ],
        observable_checks=[
            {
                "id": "check.workspace-python-tests",
                "description": "workspace pytest",
                "command": "uv run pytest tests -q",
                "component_ids": ["comp-svc"],
                "contract_ids": [],
                "provenance_refs": ["prov.workspace"],
            }
        ],
        profiles=[
            {
                "componentId": "comp-svc",
                "ownedNodeIds": ["node.svc"],
                "responsibilitySummary": "svc",
                "keySymbols": [],
                "behavioralTags": [],
                "riskLevel": "high",
                "priorityRank": 1,
                "whyPriority": "x",
                "provenanceRefs": ["prov.svc"],
            }
        ],
    )

    scorecard = build_project_intake_scorecard(repo, snapshot, profile="active-development")
    findings = [f for f in scorecard["findings"] if f["id"] == "code.component.untested.comp-svc"]
    assert len(findings) == 1
    assert findings[0]["verification"] == ["python3 -m ast src/pkg/svc.py"]
    scorecard_path = tmp_path / "scorecard.json"
    scorecard_path.write_text(json.dumps(scorecard, sort_keys=True), encoding="utf-8")

    plan = build_proposal_plan(repo, scorecard_path, max_candidates=20).to_jsonable()
    component_candidates = [
        candidate for candidate in plan["candidates"] if candidate["finding_id"] == "code.component.untested.comp-svc"
    ]
    assert len(component_candidates) == 1
    assert component_candidates[0]["target_paths"] == ["src/pkg/svc.py"]
    assert component_candidates[0]["verification_commands"] == ["python3 -m ast src/pkg/svc.py"]
    graph = GraphIndex.from_graph({"nodes": [{"id": "node.svc", "path": "src/pkg/svc.py"}], "edges": []})

    survivors, dropped = prefilter_candidates({**plan, "candidates": component_candidates}, graph)

    assert [candidate["finding_id"] for candidate in survivors] == ["code.component.untested.comp-svc"]
    assert dropped == []


def test_workspace_scoped_check_covering_all_components_does_not_count_as_per_component(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "src").mkdir()
    (repo / "src" / "a.py").write_text("a = 1\n", encoding="utf-8")
    (repo / "src" / "b.py").write_text("b = 2\n", encoding="utf-8")
    snapshot = _component_snapshot(
        tmp_path / "pm.json",
        repo,
        nodes=[{"id": "node.a", "kind": "python_module", "path": "src/a.py"}, {"id": "node.b", "kind": "python_module", "path": "src/b.py"}],
        components=[
            {"id": "comp-a", "name": "A", "responsibility": "A service.", "owned_node_ids": ["node.a"], "provenance_refs": ["prov.a"], "contract_ids": [], "check_ids": [], "verification_gap_ids": []},
            {"id": "comp-b", "name": "B", "responsibility": "B service.", "owned_node_ids": ["node.b"], "provenance_refs": ["prov.b"], "contract_ids": [], "check_ids": [], "verification_gap_ids": []},
        ],
        observable_checks=[{"id": "check.all", "description": "all tests", "command": "uv run pytest tests -q", "component_ids": ["comp-a", "comp-b"], "contract_ids": [], "provenance_refs": ["prov.tests"]}],
        profiles=[
            {"componentId": "comp-a", "ownedNodeIds": ["node.a"], "responsibilitySummary": "a", "keySymbols": [], "behavioralTags": [], "riskLevel": "high", "priorityRank": 1, "whyPriority": "x", "provenanceRefs": ["prov.a"]},
            {"componentId": "comp-b", "ownedNodeIds": ["node.b"], "responsibilitySummary": "b", "keySymbols": [], "behavioralTags": [], "riskLevel": "high", "priorityRank": 2, "whyPriority": "x", "provenanceRefs": ["prov.b"]},
        ],
    )

    scorecard = build_project_intake_scorecard(repo, snapshot, profile="active-development")

    ids = {finding["id"] for finding in scorecard["findings"]}
    assert "code.component.untested.comp-a" in ids
    assert "code.component.untested.comp-b" in ids


def test_extensionless_single_owned_surface_does_not_become_doc_candidate(tmp_path: Path) -> None:
    """A component whose only owned surface is extension-less (e.g. Dockerfile)
    must not be turned into a fabricated <path>/index.md documentation candidate."""
    from arena.proposal_planner import build_proposal_plan

    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "Dockerfile").write_text("FROM python:3.12\n", encoding="utf-8")
    snapshot = _component_snapshot(
        tmp_path / "pm.json",
        repo,
        nodes=[{"id": "node.docker", "kind": "dockerfile", "path": "Dockerfile"}],
        components=[{"id": "comp-img", "name": "Image", "responsibility": "Container image build definition for deploys.", "owned_node_ids": ["node.docker"], "provenance_refs": ["prov.docker"], "contract_ids": [], "check_ids": [], "verification_gap_ids": []}],
        observable_checks=[],
        profiles=[{"componentId": "comp-img", "ownedNodeIds": ["node.docker"], "responsibilitySummary": "image", "keySymbols": [], "behavioralTags": [], "riskLevel": "high", "priorityRank": 1, "whyPriority": "x", "provenanceRefs": ["prov.docker"]}],
    )
    scorecard = build_project_intake_scorecard(repo, snapshot, profile="active-development")
    scorecard_path = tmp_path / "sc.json"
    scorecard_path.write_text(json.dumps(scorecard, sort_keys=True), encoding="utf-8")

    plan = build_proposal_plan(repo, scorecard_path, max_candidates=10)

    # No candidate may target a fabricated Dockerfile/index.md path.
    assert not any(c.target_path == "Dockerfile/index.md" for c in plan.candidates)
    assert not any(c.target_path.endswith("/index.md") and "Dockerfile" in c.target_path for c in plan.candidates)
    # The extension-less surface produces no untested-component finding (no real-suffix file to target).
    assert not any(f["id"] == "code.component.untested.comp-img" for f in scorecard["findings"])


def test_multi_file_component_becomes_multi_target_candidate(tmp_path: Path) -> None:
    """A component owning 2+ resolvable source files becomes one multi-target
    proposal candidate instead of being mis-targeted to only one file."""
    from arena.proposal_planner import build_proposal_plan

    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "src").mkdir()
    (repo / "src" / "a.py").write_text("x = 1\n", encoding="utf-8")
    (repo / "src" / "b.py").write_text("y = 2\n", encoding="utf-8")
    snapshot = _component_snapshot(
        tmp_path / "pm.json",
        repo,
        nodes=[{"id": "node.a", "kind": "python_module", "path": "src/a.py"}, {"id": "node.b", "kind": "python_module", "path": "src/b.py"}],
        components=[{"id": "comp-ab", "name": "AB", "responsibility": "Two-module subsystem handling A and B.", "owned_node_ids": ["node.a", "node.b"], "provenance_refs": ["prov.a"], "contract_ids": [], "check_ids": [], "verification_gap_ids": []}],
        observable_checks=[],
        profiles=[{"componentId": "comp-ab", "ownedNodeIds": ["node.a", "node.b"], "responsibilitySummary": "ab", "keySymbols": [], "behavioralTags": [], "riskLevel": "high", "priorityRank": 1, "whyPriority": "x", "provenanceRefs": ["prov.a"]}],
    )
    scorecard = build_project_intake_scorecard(repo, snapshot, profile="active-development")
    # The finding is still emitted (it has 2 owned surfaces)...
    assert any(f["id"] == "code.component.untested.comp-ab" for f in scorecard["findings"])
    scorecard_path = tmp_path / "sc.json"
    scorecard_path.write_text(json.dumps(scorecard, sort_keys=True), encoding="utf-8")

    plan = build_proposal_plan(repo, scorecard_path, max_candidates=10)

    candidate = next(c for c in plan.candidates if c.finding_id == "code.component.untested.comp-ab")
    assert candidate.target_path == "src/a.py"
    assert candidate.target_paths == ("src/a.py", "src/b.py")
    assert not any(s["finding_id"] == "code.component.untested.comp-ab" for s in plan.skipped_findings)


def test_component_with_unresolvable_nodes_yields_no_finding(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    snapshot = _component_snapshot(
        tmp_path / "pm.json",
        repo,
        nodes=[],  # no graph nodes -> owned_node_ids resolve to nothing
        components=[{"id": "comp-x", "name": "X", "responsibility": "Some responsibility text here please.", "owned_node_ids": ["node.missing"], "provenance_refs": ["prov.x"], "contract_ids": [], "check_ids": [], "verification_gap_ids": []}],
        observable_checks=[],
        profiles=[{"componentId": "comp-x", "ownedNodeIds": ["node.missing"], "responsibilitySummary": "x", "keySymbols": [], "behavioralTags": [], "riskLevel": "high", "priorityRank": 1, "whyPriority": "x", "provenanceRefs": ["prov.x"]}],
    )

    scorecard = build_project_intake_scorecard(repo, snapshot, profile="active-development")

    assert not any(f["id"] == "code.component.untested.comp-x" for f in scorecard["findings"])


def test_unknown_risk_level_component_finding_is_medium_severity(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    snapshot = _component_snapshot(
        tmp_path / "pm.json",
        repo,
        nodes=[{"id": "node.q", "kind": "python_module", "path": "src/q.py"}],
        components=[{"id": "comp-q", "name": "Q", "responsibility": "Queue worker draining the job queue.", "owned_node_ids": ["node.q"], "provenance_refs": ["prov.q"], "contract_ids": [], "check_ids": [], "verification_gap_ids": []}],
        observable_checks=[],
        profiles=[{"componentId": "comp-q", "ownedNodeIds": ["node.q"], "responsibilitySummary": "q", "keySymbols": [], "behavioralTags": [], "riskLevel": "bogus", "priorityRank": 1, "whyPriority": "x", "provenanceRefs": ["prov.q"]}],
    )

    scorecard = build_project_intake_scorecard(repo, snapshot, profile="active-development")

    finding = next(f for f in scorecard["findings"] if f["id"] == "code.component.untested.comp-q")
    assert finding["severity"] == "medium"
