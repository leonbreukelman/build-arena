from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from arena.proposal_planner import build_proposal_plan

FIXTURES = Path(__file__).resolve().parent / "fixtures"


def _write_scorecard(tmp_path: Path, repo: Path, fixture: str) -> Path:
    raw = json.loads((FIXTURES / fixture).read_text(encoding="utf-8"))
    raw["projectRoot"] = str(repo)
    out = tmp_path / "scorecard.json"
    out.write_text(json.dumps(raw, sort_keys=True), encoding="utf-8")
    return out


def _prepare_repo(tmp_path: Path, name: str) -> Path:
    repo = tmp_path / name
    (repo / "src" / "pkg").mkdir(parents=True)
    (repo / "README.md").write_text("# Readme\n", encoding="utf-8")
    (repo / "src" / "pkg" / "auth.py").write_text("def login():\n    return True\n", encoding="utf-8")
    return repo


def _normalize(plan_json: dict[str, Any]) -> dict[str, Any]:
    """Drop only fields that depend on the absolute repo path or the on-disk
    content hash. ``repo_facts_block`` is deterministic for the fixed fixture
    tree and is asserted byte-for-byte (it is the field whose construction moved
    in the refactor), so it is intentionally NOT normalized."""
    plan_json = json.loads(json.dumps(plan_json))  # deep copy
    plan_json["projectRoot"] = "<REPO>"
    plan_json["id"] = "<ID>"
    plan_json["repoFactsHash"] = "<FACTS_HASH>"
    plan_json.pop("baseLineage", None)
    for candidate in plan_json.get("candidates", []):
        candidate["repo_facts_hash"] = "<FACTS_HASH>"
        candidate.pop("target_paths", None)
        candidate.pop("base_lineage", None)
        candidate.pop("intent_hash", None)
        candidate.pop("proposal_key", None)
        candidate.pop("registry_status", None)
    return plan_json


@pytest.mark.parametrize(
    ("fixture", "repo_name", "golden"),
    [
        ("parity_scorecard_normal.json", "repo", "parity_plan_normal.json"),
        ("parity_scorecard_compliance.json", "cmmc-level1-readiness-assistant", "parity_plan_compliance.json"),
    ],
)
def test_proposal_plan_matches_pre_refactor_golden(tmp_path: Path, fixture: str, repo_name: str, golden: str) -> None:
    """Byte-for-byte parity against the plan captured BEFORE the domain-registry
    refactor. Proves the refactor changed structure, not behaviour."""
    repo = _prepare_repo(tmp_path, repo_name)
    scorecard = _write_scorecard(tmp_path, repo, fixture)

    plan = build_proposal_plan(repo, scorecard, max_candidates=10)
    actual = _normalize(plan.to_jsonable())
    expected = json.loads((FIXTURES / golden).read_text(encoding="utf-8"))

    assert actual == expected


def test_proposal_domains_are_registered_in_fixed_order() -> None:
    from arena.proposal_domains import default_domain_registry

    names = [domain.name for domain in default_domain_registry()]
    assert names == ["documentation", "code_quality", "component_verification", "generic_file", "model_level"]
    assert len(set(names)) == len(names), "domain names must be unique"


def test_registry_iteration_is_deterministic() -> None:
    from arena.proposal_domains import default_domain_registry

    first = [d.name for d in default_domain_registry()]
    second = [d.name for d in default_domain_registry()]
    assert first == second


def test_domain_missing_protocol_method_is_rejected_at_construction() -> None:
    from arena.proposal_domains import ProposalDomainRegistry

    class Broken:
        name = "broken"
        # no candidates_for_finding method

    with pytest.raises((TypeError, ValueError)):
        ProposalDomainRegistry([Broken()])  # type: ignore[list-item]


def test_planner_orchestrates_registered_domains_union(tmp_path: Path) -> None:
    """With two stub domains, the planner returns the union of their candidates,
    ranked, with provenance preserved."""
    from arena.proposal_domains import ProposalCandidateDraft, ProposalDomainRegistry
    from arena.proposal_planner import build_proposal_plan_with_registry

    repo = _prepare_repo(tmp_path, "repo")
    scorecard = _write_scorecard(tmp_path, repo, "parity_scorecard_normal.json")

    class OnlyAuth:
        name = "alpha"

        def candidates_for_finding(self, finding, context):  # type: ignore[no-untyped-def]
            if finding.get("id", "").startswith("code.component"):
                return [ProposalCandidateDraft(
                    intent="stub auth intent",
                    target_path="src/pkg/auth.py",
                    success_criterion="auth changed",
                    grounding_constraints=("c1",),
                    verification_commands=("test -s src/pkg/auth.py",),
                )]
            return []

    class NeverMatches:
        name = "beta"

        def candidates_for_finding(self, finding, context):  # type: ignore[no-untyped-def]
            return []

    registry = ProposalDomainRegistry([OnlyAuth(), NeverMatches()])
    plan = build_proposal_plan_with_registry(repo, scorecard, registry, max_candidates=10)

    targets = [c.target_path for c in plan.candidates]
    assert "src/pkg/auth.py" in targets
    auth = next(c for c in plan.candidates if c.target_path == "src/pkg/auth.py")
    assert auth.intent == "stub auth intent"
    assert auth.finding_id == "code.component.untested.comp-auth"


def test_documentation_domain_gate_still_rejects_dead_links(tmp_path: Path) -> None:
    """After the refactor the documentation domain's success contract must still
    carry the markdown-link verification command (the docs gate is intact)."""
    repo = _prepare_repo(tmp_path, "repo")
    scorecard = _write_scorecard(tmp_path, repo, "parity_scorecard_normal.json")

    plan = build_proposal_plan(repo, scorecard, max_candidates=10)

    docs = next(c for c in plan.candidates if c.target_path == "docs/index.md")
    assert any("markdown_links" in cmd for cmd in docs.verification_commands)


def _domain_context() -> Any:
    from arena.proposal_domains import DomainContext
    from arena.repo_facts import RepoFacts

    facts = RepoFacts(
        project_root="/x",
        readme_exists=True,
        docs_dir_exists=False,
        top_level_files=(),
        top_level_dirs=(),
        docs_markdown_files=(),
        markdown_files=(),
        source_files=(),
        docs_markdown_files_truncated=False,
        markdown_files_truncated=False,
        content_hash="hash",
    )
    return DomainContext(project_name="x", facts=facts, intake_context_block="", require_source_references=False)


@pytest.mark.parametrize(
    ("evidence_path", "expected_claimer"),
    [
        ("docs/index.md", "documentation"),
        ("AGENTS.md", "documentation"),
        ("docs/decisions", "documentation"),  # extension-less dir -> docs/decisions/index.md (.md)
        ("src/pkg/auth.py", "generic_file"),
        ("Makefile.py", "generic_file"),
    ],
)
def test_documentation_and_generic_domains_are_mutually_exclusive(evidence_path: str, expected_claimer: str) -> None:
    """Exactly one built-in domain claims any single-file finding. This invariant
    replaces the old if/elif exhaustiveness in the planner."""
    from arena.proposal_domains import DocumentationDomain, GenericFileDomain

    finding = {"id": "f", "title": "t", "evidence": [{"kind": "absence", "path": evidence_path, "checked": True}]}
    ctx = _domain_context()
    doc_claims = bool(DocumentationDomain().candidates_for_finding(finding, ctx))
    gen_claims = bool(GenericFileDomain().candidates_for_finding(finding, ctx))

    assert [doc_claims, gen_claims].count(True) == 1, "exactly one domain must claim a single-file finding"
    assert (expected_claimer == "documentation") == doc_claims


def test_neither_domain_claims_multi_file_finding() -> None:
    """A finding with two distinct evidence paths has no single-file target, so
    neither built-in domain claims it and the planner skips it."""
    from arena.proposal_domains import DocumentationDomain, GenericFileDomain

    finding = {
        "id": "f",
        "title": "t",
        "evidence": [
            {"kind": "owned_surface", "path": "src/a.py", "checked": True},
            {"kind": "owned_surface", "path": "src/b.py", "checked": True},
        ],
    }
    ctx = _domain_context()
    assert DocumentationDomain().candidates_for_finding(finding, ctx) == []
    assert GenericFileDomain().candidates_for_finding(finding, ctx) == []


def test_multi_file_finding_produces_component_candidate(tmp_path: Path) -> None:
    repo = _prepare_repo(tmp_path, "repo")
    scorecard_path = tmp_path / "scorecard.json"
    scorecard_path.write_text(
        json.dumps(
            {
                "schemaVersion": "project-intake-scorecard/v0",
                "id": "sc",
                "snapshotId": "snap",
                "projectRoot": str(repo),
                "findings": [
                    {
                        "id": "code.component.untested.multi",
                        "title": "Multi-file component",
                        "evidence": [
                            {"kind": "owned_surface", "path": "src/a.py", "checked": True},
                            {"kind": "owned_surface", "path": "src/b.py", "checked": True},
                        ],
                        "verification": [],
                        "autonomyBoundary": "needs_code_change",
                        "priorityScore": 100.0,
                        "rank": 1,
                    }
                ],
            },
            sort_keys=True,
        ),
        encoding="utf-8",
    )

    plan = build_proposal_plan(repo, scorecard_path, max_candidates=10)

    assert plan.candidate_count == 1
    assert plan.candidates[0].target_paths == ("src/a.py", "src/b.py")
    assert not plan.skipped_findings


def test_component_finding_gets_load_bearing_gate(tmp_path: Path) -> None:
    repo = _prepare_repo(tmp_path, "repo")
    scorecard_path = tmp_path / "scorecard.json"
    scorecard_path.write_text(
        json.dumps(
            {
                "schemaVersion": "project-intake-scorecard/v0",
                "id": "sc",
                "snapshotId": "snap",
                "projectRoot": str(repo),
                "findings": [
                    {
                        "id": "code.component.untested.comp-auth",
                        "title": "Auth component lacks observable checks",
                        "evidence": [{"kind": "owned_surface", "path": "src/pkg/auth.py", "checked": True}],
                        "verification": [],
                        "autonomyBoundary": "needs_code_change",
                        "priorityScore": 540.0,
                        "rank": 1,
                    },
                    {
                        "id": "verification.quality-gates.present",
                        "title": "Quality gates exist",
                        "evidence": [{"kind": "project_model", "path": "iterationReadiness.qualityGates", "checked": True}],
                        "verification": ["uv run ruff check .", "uv run pyright", "uv run pytest tests -q"],
                        "priorityScore": 1.0,
                        "rank": 2,
                    },
                ],
            },
            sort_keys=True,
        ),
        encoding="utf-8",
    )

    plan = build_proposal_plan(repo, scorecard_path, max_candidates=10)

    candidate = next(c for c in plan.candidates if c.finding_id == "code.component.untested.comp-auth")
    assert candidate.target_path == "src/pkg/auth.py"
    assert candidate.verification_commands == ("uv run ruff check .", "uv run pyright", "uv run pytest tests -q")


def test_multi_file_component_produces_candidate(tmp_path: Path) -> None:
    repo = _prepare_repo(tmp_path, "repo")
    (repo / "src" / "pkg" / "entry.py").write_text("def main():\n    return True\n", encoding="utf-8")
    scorecard_path = tmp_path / "scorecard.json"
    scorecard_path.write_text(
        json.dumps(
            {
                "schemaVersion": "project-intake-scorecard/v0",
                "id": "sc",
                "snapshotId": "snap",
                "projectRoot": str(repo),
                "findings": [
                    {
                        "id": "code.component.untested.comp-entrypoints",
                        "title": "Entrypoints component lacks checks",
                        "evidence": [
                            {"kind": "owned_surface", "path": "src/pkg/auth.py", "checked": True},
                            {"kind": "owned_surface", "path": "src/pkg/entry.py", "checked": True},
                        ],
                        "verification": [],
                        "autonomyBoundary": "needs_code_change",
                        "priorityScore": 540.0,
                        "rank": 1,
                    },
                    {
                        "id": "verification.quality-gates.present",
                        "title": "Quality gates exist",
                        "evidence": [{"kind": "project_model", "path": "iterationReadiness.qualityGates", "checked": True}],
                        "verification": ["uv run pytest tests -q"],
                        "priorityScore": 1.0,
                        "rank": 2,
                    },
                ],
            },
            sort_keys=True,
        ),
        encoding="utf-8",
    )

    plan = build_proposal_plan(repo, scorecard_path, max_candidates=10)

    candidate = next(c for c in plan.candidates if c.finding_id == "code.component.untested.comp-entrypoints")
    assert candidate.target_paths == ("src/pkg/auth.py", "src/pkg/entry.py")
    assert candidate.target_path == "src/pkg/auth.py"
    assert candidate.verification_commands == ("uv run pytest tests -q",)
    assert not any(s["finding_id"] == "code.component.untested.comp-entrypoints" for s in plan.skipped_findings)


def test_model_level_finding_becomes_backlog_task_candidate(tmp_path: Path) -> None:
    repo = _prepare_repo(tmp_path, "repo")
    scorecard_path = tmp_path / "scorecard.json"
    scorecard_path.write_text(
        json.dumps(
            {
                "schemaVersion": "project-intake-scorecard/v0",
                "id": "sc",
                "snapshotId": "snap",
                "projectRoot": str(repo),
                "findings": [
                    {
                        "id": "architecture.open-questions-or-gaps",
                        "title": "Open architecture questions remain",
                        "evidence": [{"kind": "project_model", "path": "iterationReadiness.openQuestions", "checked": True}],
                        "verification": [],
                        "autonomyBoundary": "safe_to_patch_docs_only",
                        "priorityScore": 100.0,
                        "rank": 1,
                    }
                ],
            },
            sort_keys=True,
        ),
        encoding="utf-8",
    )

    plan = build_proposal_plan(repo, scorecard_path, max_candidates=10)

    candidate = plan.candidates[0]
    assert candidate.finding_id == "architecture.open-questions-or-gaps"
    assert candidate.target_path == "docs/agent-backlog.md"
    assert candidate.verification_commands
