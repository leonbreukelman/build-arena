from __future__ import annotations

from typing import Any

from arena.proposal_domains import CodeQualityDomain, DomainContext, default_domain_registry
from arena.repo_facts import RepoFacts


def _ctx() -> DomainContext:
    facts = RepoFacts(
        project_root="/x",
        readme_exists=True,
        docs_dir_exists=False,
        top_level_files=(),
        top_level_dirs=(),
        docs_markdown_files=(),
        markdown_files=(),
        docs_markdown_files_truncated=False,
        markdown_files_truncated=False,
        content_hash="hash",
    )
    return DomainContext(project_name="x", facts=facts, intake_context_block="", require_source_references=False)


def _lint_finding(path: str) -> dict[str, Any]:
    return {
        "id": f"code.quality.lint.{path}",
        "title": f"{path} has lint violations",
        "dimension": "architecture_specs_contracts",
        "evidence": [{"kind": "lint", "path": path, "checked": True}],
        "verification": [],
        "priorityScore": 120.0,
        "rank": 1,
    }


def test_registry_includes_code_quality_before_generic() -> None:
    names = [d.name for d in default_domain_registry()]
    assert "code_quality" in names
    # code_quality must precede generic_file so a lint finding routes to the
    # domain with the load-bearing gate, not the bare generic fallback.
    assert names.index("code_quality") < names.index("generic_file")


def test_code_quality_domain_claims_lint_finding_for_python_file() -> None:
    finding = _lint_finding("src/pkg/mod.py")
    drafts = CodeQualityDomain().candidates_for_finding(finding, _ctx())
    assert len(drafts) == 1
    draft = drafts[0]
    assert draft.target_path == "src/pkg/mod.py"
    assert "lint" in draft.intent.lower() or "ruff" in draft.intent.lower()
    # The domain's gate command must be the load-bearing code-quality gate.
    assert any("arena.code_quality_gate" in cmd for cmd in draft.verification_commands)
    assert any("--path src/pkg/mod.py" in cmd for cmd in draft.verification_commands)


def test_code_quality_domain_ignores_non_python_and_markdown() -> None:
    ctx = _ctx()
    assert CodeQualityDomain().candidates_for_finding(_lint_finding("docs/index.md"), ctx) == []
    assert CodeQualityDomain().candidates_for_finding(_lint_finding("Makefile"), ctx) == []


def test_code_quality_domain_ignores_non_lint_findings() -> None:
    finding = {
        "id": "doc.readme.missing",
        "title": "README is missing",
        "evidence": [{"kind": "absence", "path": "README.md", "checked": True}],
        "verification": [],
        "priorityScore": 100.0,
        "rank": 1,
    }
    assert CodeQualityDomain().candidates_for_finding(finding, _ctx()) == []


def test_code_quality_constraints_forbid_suppression_gaming() -> None:
    drafts = CodeQualityDomain().candidates_for_finding(_lint_finding("src/mod.py"), _ctx())
    joined = "\n".join(drafts[0].grounding_constraints).lower()
    assert "noqa" in joined or "suppress" in joined
