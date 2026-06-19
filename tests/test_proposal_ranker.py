from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from arena.proposal_ranker import build_ranked_proposals, rank_entries_to_jsonable


def _scorecard_path(tmp_path: Path, repo: Path, findings: list[dict[str, Any]], profile: str = "new-project") -> Path:
    # Minimal scorecard the ranker consumes: it needs findings with breakdown
    # inputs + the profile weights. We import the real weights so the formula is
    # exercised exactly as production.
    from arena.project_intake_scorecard import PROFILE_WEIGHTS

    payload = {
        "schemaVersion": "project-intake-scorecard/v0",
        "id": "scorecard-rank",
        "snapshotId": "snap-rank",
        "projectRoot": str(repo),
        "profile": profile,
        "weights": PROFILE_WEIGHTS[profile],
        "findings": findings,
    }
    out = tmp_path / "scorecard.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")
    return out


def _finding(fid: str, dimension: str, severity: str, *, confidence: str = "high", effort: str = "small",
             evidence_path: str, impact: int = 3, risk: int = 3, vgain: int = 3, docs: int = 3,
             rank: int = 1, score: float = 0.0) -> dict[str, Any]:
    return {
        "id": fid,
        "dimension": dimension,
        "title": f"{fid} title",
        "severity": severity,
        "confidence": confidence,
        "estimatedEffort": effort,
        "evidence": [{"kind": "absence", "path": evidence_path, "checked": True}],
        "recommendedAction": "do the thing",
        "verification": [],
        "autonomyBoundary": "safe_to_patch_docs_only" if evidence_path.endswith(".md") else "needs_code_change",
        "impactOnFutureIteration": impact,
        "riskReduction": risk,
        "verificationGain": vgain,
        "docKnowledgeGain": docs,
        "priorityScore": score,
        "rank": rank,
    }


def _prepare_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    (repo / "src" / "pkg").mkdir(parents=True)
    (repo / "README.md").write_text("# Readme\n", encoding="utf-8")
    (repo / "src" / "pkg" / "mod.py").write_text("def f():\n    return 1\n", encoding="utf-8")
    return repo


def _multi_domain_findings() -> list[dict[str, Any]]:
    return [
        _finding("doc.index.missing", "documentation_project_knowledge", "medium", evidence_path="docs/index.md"),
        _finding("code.quality.lint.src/pkg/mod.py", "architecture_specs_contracts", "high", evidence_path="src/pkg/mod.py"),
        _finding("code.component.untested.comp-a", "reproducible_verification", "high", evidence_path="src/pkg/mod.py"),
    ]


def test_cross_domain_ranking_is_deterministic(tmp_path: Path) -> None:
    repo = _prepare_repo(tmp_path)
    scorecard = _scorecard_path(tmp_path, repo, _multi_domain_findings())

    first = build_ranked_proposals(repo, scorecard, max_candidates=10)
    second = build_ranked_proposals(repo, scorecard, max_candidates=10)

    assert first.to_jsonable() == second.to_jsonable()
    assert first.plan_hash == second.plan_hash


def test_priority_formula_pinned(tmp_path: Path) -> None:
    """A fixed candidate set produces exactly the expected priorityScore so the
    formula + multipliers cannot drift silently."""
    repo = _prepare_repo(tmp_path)
    # new-project weight for documentation_project_knowledge = 28; severity medium=2.0;
    # confidence high=1.0; gains 3+3+3+3=12; effort small=1.0 -> 28*2*1*12/1 = 672.0
    findings = [_finding("doc.index.missing", "documentation_project_knowledge", "medium", evidence_path="docs/index.md")]
    scorecard = _scorecard_path(tmp_path, repo, findings)

    ranked = build_ranked_proposals(repo, scorecard, max_candidates=10)

    assert ranked.entries[0].priority_score == 672.0


def test_profile_changes_ranking(tmp_path: Path) -> None:
    """new-project -> production must re-rank security/verification above docs."""
    repo = _prepare_repo(tmp_path)
    findings = [
        _finding("doc.index.missing", "documentation_project_knowledge", "high", evidence_path="docs/index.md"),
        _finding("code.component.untested.comp-a", "reproducible_verification", "high", evidence_path="src/pkg/mod.py"),
    ]

    new_proj = build_ranked_proposals(repo, _scorecard_path(tmp_path / "a", repo, findings, "new-project"), max_candidates=10)
    production = build_ranked_proposals(repo, _scorecard_path(tmp_path / "b", repo, findings, "production"), max_candidates=10)

    # Under new-project, docs (weight 28) outranks verification (weight 20).
    assert new_proj.entries[0].finding_id == "doc.index.missing"
    # Under production, verification (weight 24) outranks docs (weight 14).
    assert production.entries[0].finding_id == "code.component.untested.comp-a"


def test_score_breakdown_present(tmp_path: Path) -> None:
    repo = _prepare_repo(tmp_path)
    scorecard = _scorecard_path(tmp_path, repo, _multi_domain_findings())

    ranked = build_ranked_proposals(repo, scorecard, max_candidates=10)

    for entry in ranked.entries:
        bd = entry.score_breakdown
        assert bd["dimension"]
        assert isinstance(bd["dimensionWeight"], int)
        assert bd["severity"] and isinstance(bd["severityMultiplier"], float)
        assert bd["confidence"] and isinstance(bd["confidenceMultiplier"], float)
        assert bd["effort"] and isinstance(bd["effortDivisor"], float)
        assert isinstance(bd["totalGain"], int)
        assert "formula" in bd
        # The breakdown must reproduce the score.
        assert bd["computedScore"] == entry.priority_score


def test_skipped_and_omitted_accounting(tmp_path: Path) -> None:
    repo = _prepare_repo(tmp_path)
    # 3 candidate-producing findings + 1 that no domain can target (multi-file).
    findings = _multi_domain_findings()
    findings.append({
        "id": "verification.quality-gates.present",
        "dimension": "reproducible_verification",
        "title": "no single target",
        "severity": "low",
        "confidence": "high",
        "estimatedEffort": "small",
        "evidence": [{"kind": "project_model", "path": "iterationReadiness.qualityGates", "checked": True}],
        "recommendedAction": "x",
        "verification": [],
        "autonomyBoundary": "advisory_only",
        "impactOnFutureIteration": 1, "riskReduction": 1, "verificationGain": 1, "docKnowledgeGain": 1,
        "priorityScore": 1.0, "rank": 99,
    })
    scorecard = _scorecard_path(tmp_path, repo, findings)

    ranked = build_ranked_proposals(repo, scorecard, max_candidates=2)

    # max_candidates=2 -> 1 omitted (enumerated, not just counted).
    assert ranked.candidate_count == 3
    assert len(ranked.entries) == 2
    assert ranked.omitted_count == 1
    assert len(ranked.omitted) == 1
    assert ranked.omitted[0]["findingId"]
    # the quality-gate finding is consumed into domain context rather than emitted as a candidate.
    assert any(s["reason"] == "consumed_as_context" for s in ranked.skipped)


def test_top10_spans_multiple_domains(tmp_path: Path) -> None:
    repo = _prepare_repo(tmp_path)
    scorecard = _scorecard_path(tmp_path, repo, _multi_domain_findings())

    ranked = build_ranked_proposals(repo, scorecard, max_candidates=10)

    domains = {entry.domain for entry in ranked.entries}
    assert len(domains) >= 2
    assert "documentation" in domains
    assert "code_quality" in domains
    # ordered by priorityScore descending
    scores = [e.priority_score for e in ranked.entries]
    assert scores == sorted(scores, reverse=True)


def test_high_severity_nondoc_outranks_docs(tmp_path: Path) -> None:
    repo = _prepare_repo(tmp_path)
    findings = [
        _finding("doc.index.missing", "documentation_project_knowledge", "medium", evidence_path="docs/index.md"),
        _finding("code.quality.lint.src/pkg/mod.py", "security_supply_chain_hygiene", "critical", evidence_path="src/pkg/mod.py"),
    ]
    scorecard = _scorecard_path(tmp_path, repo, findings, "production")

    ranked = build_ranked_proposals(repo, scorecard, max_candidates=10)

    assert ranked.entries[0].finding_id == "code.quality.lint.src/pkg/mod.py"
    assert ranked.entries[0].priority_score > ranked.entries[1].priority_score


def test_ranked_artifact_round_trips(tmp_path: Path) -> None:
    repo = _prepare_repo(tmp_path)
    scorecard = _scorecard_path(tmp_path, repo, _multi_domain_findings())

    ranked = build_ranked_proposals(repo, scorecard, max_candidates=10)
    payload = ranked.to_jsonable()
    serialized = json.dumps(payload, sort_keys=True)
    reloaded = json.loads(serialized)

    assert reloaded["schemaVersion"] == "ranked-proposals/v0"
    assert [e["findingId"] for e in reloaded["entries"]] == [e.finding_id for e in ranked.entries]
    assert rank_entries_to_jsonable(ranked.entries) == payload["entries"]


def test_ranked_artifact_validates_against_schema(tmp_path: Path) -> None:
    from jsonschema import Draft202012Validator

    repo = _prepare_repo(tmp_path)
    scorecard = _scorecard_path(tmp_path, repo, _multi_domain_findings())
    ranked = build_ranked_proposals(repo, scorecard, max_candidates=10)

    schema_path = Path(__file__).resolve().parents[1] / "docs" / "schemas" / "ranked-proposals-v0.schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    errors = sorted(Draft202012Validator(schema).iter_errors(ranked.to_jsonable()), key=lambda e: list(e.path))
    assert errors == [], [e.message for e in errors]


def test_ranker_recompute_matches_intake_stored_score(tmp_path: Path) -> None:
    """The ranker recomputes scores instead of reading the finding's stored
    priorityScore; this pins that the two never diverge for the same finding.
    Builds a real scorecard via intake, then ranks it, and asserts every ranked
    entry's score equals what intake stored AND equals its own breakdown."""
    from arena.project_intake_scorecard import build_project_intake_scorecard

    repo = tmp_path / "repo"
    (repo / "docs").mkdir(parents=True)
    (repo / "README.md").write_text("# R\n", encoding="utf-8")
    snapshot = tmp_path / "pm.json"
    snapshot.write_text(
        json.dumps(
            {
                "schemaVersion": "project-model/v1",
                "id": "s",
                "project": {"projectRoot": str(repo), "projectId": "x", "goal": "g", "nonGoals": ["n"]},
                "provenance": {"git": {"headOid": "abc", "dirty": False, "dirtyPaths": []}},
                "projectGraph": {"graphHash": "h", "nodes": []},
                "hashes": {"artifactHashes": {"project-model-v1.json": "h"}},
                "snapshot": {"verification_gaps": [], "components": [], "observable_checks": []},
                "iterationReadiness": {"qualityGates": [], "openQuestions": [], "priorityBacklog": [], "componentProfiles": []},
            },
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    scorecard = build_project_intake_scorecard(repo, snapshot, profile="new-project")
    scorecard_path = tmp_path / "scorecard.json"
    scorecard_path.write_text(json.dumps(scorecard, sort_keys=True), encoding="utf-8")
    stored = {f["id"]: f["priorityScore"] for f in scorecard["findings"]}

    ranked = build_ranked_proposals(repo, scorecard_path, max_candidates=50)

    assert ranked.entries  # the intake produced doc findings that map to candidates
    for entry in ranked.entries:
        assert entry.finding_id in stored
        assert entry.priority_score == stored[entry.finding_id]
        assert entry.score_breakdown["computedScore"] == entry.priority_score


def test_ranker_uses_scorecard_profile_consistently(tmp_path: Path) -> None:
    """The ranker must rank under the profile recorded in the scorecard (the same
    one intake scored under), not a hardcoded default."""
    repo = _prepare_repo(tmp_path)
    findings = [_finding("doc.index.missing", "documentation_project_knowledge", "high", evidence_path="docs/index.md")]
    scorecard = _scorecard_path(tmp_path, repo, findings, "production")

    ranked = build_ranked_proposals(repo, scorecard, max_candidates=10)

    assert ranked.profile == "production"
    # production weight for documentation_project_knowledge is 14 (not new-project's 28).
    assert ranked.entries[0].score_breakdown["dimensionWeight"] == 14


def test_ranker_rejects_unknown_profile(tmp_path: Path) -> None:
    import pytest

    repo = _prepare_repo(tmp_path)
    findings = [_finding("doc.index.missing", "documentation_project_knowledge", "high", evidence_path="docs/index.md")]
    out = tmp_path / "scorecard.json"
    out.write_text(json.dumps({"id": "x", "profile": "bogus-profile", "findings": findings}, sort_keys=True), encoding="utf-8")

    with pytest.raises(ValueError, match="unknown profile"):
        build_ranked_proposals(repo, out, max_candidates=10)


def test_ranker_honors_scorecard_stored_weights_over_live_table(tmp_path: Path, monkeypatch) -> None:
    """B2: the ranker must score with the weights the scorecard recorded, so a
    later edit to the live PROFILE_WEIGHTS table cannot silently desync an
    existing scorecard's ranks from its stored priorityScore."""
    import arena.proposal_ranker as ranker_mod

    repo = _prepare_repo(tmp_path)
    findings = [_finding("doc.index.missing", "documentation_project_knowledge", "medium", evidence_path="docs/index.md")]
    # Scorecard records its own weights (doc weight 28) — the intake run's truth.
    scorecard = _scorecard_path(tmp_path, repo, findings, "new-project")

    # Now the live table is mutated (someone "tunes" the weight to 999).
    mutated = dict(ranker_mod.PROFILE_WEIGHTS)
    mutated["new-project"] = {**mutated["new-project"], "documentation_project_knowledge": 999}
    monkeypatch.setattr(ranker_mod, "PROFILE_WEIGHTS", mutated)

    ranked = build_ranked_proposals(repo, scorecard, max_candidates=10)

    # Must use the scorecard's stored weight (28), giving 28*2*1*12/1 = 672.0,
    # NOT the mutated 999.
    assert ranked.entries[0].score_breakdown["dimensionWeight"] == 28
    assert ranked.entries[0].priority_score == 672.0


def test_ranker_order_matches_planner_for_same_scorecard(tmp_path: Path) -> None:
    """The operator-facing ranked order must match the order the planner produces
    its candidates in, so the top-N reflects what will actually be planned. Uses a
    REAL intake scorecard (stored rank/priorityScore consistent with the formula)
    rather than hand-built fixtures with placeholder scores."""
    from arena.project_intake_scorecard import build_project_intake_scorecard
    from arena.proposal_planner import build_proposal_plan

    repo = tmp_path / "repo"
    (repo / "docs").mkdir(parents=True)
    (repo / "README.md").write_text("# R\n", encoding="utf-8")
    snapshot = tmp_path / "pm.json"
    snapshot.write_text(
        json.dumps(
            {
                "schemaVersion": "project-model/v1",
                "id": "s",
                "project": {"projectRoot": str(repo), "projectId": "x", "goal": "g", "nonGoals": ["n"]},
                "provenance": {"git": {"headOid": "abc", "dirty": False, "dirtyPaths": []}},
                "projectGraph": {"graphHash": "h", "nodes": []},
                "hashes": {"artifactHashes": {"project-model-v1.json": "h"}},
                "snapshot": {"verification_gaps": [], "components": [], "observable_checks": []},
                "iterationReadiness": {"qualityGates": [], "openQuestions": [], "priorityBacklog": [], "componentProfiles": []},
            },
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    scorecard = build_project_intake_scorecard(repo, snapshot, profile="new-project")
    scorecard_path = tmp_path / "scorecard.json"
    scorecard_path.write_text(json.dumps(scorecard, sort_keys=True), encoding="utf-8")

    ranked = build_ranked_proposals(repo, scorecard_path, max_candidates=10)
    plan = build_proposal_plan(repo, scorecard_path, max_candidates=10)

    ranked_order = [e.finding_id for e in ranked.entries]
    plan_order = [c.finding_id for c in plan.candidates]
    assert ranked_order == plan_order


def test_ranker_gets_same_domain_context_evidence_as_planner(tmp_path: Path) -> None:
    from arena.proposal_domains import ProposalCandidateDraft, ProposalDomainRegistry

    repo = tmp_path / "repo"
    (repo / "src" / "pkg").mkdir(parents=True)
    (repo / "src" / "pkg" / "__init__.py").write_text("", encoding="utf-8")
    (repo / "src" / "pkg" / "a.py").write_text("from pkg import b\n", encoding="utf-8")
    (repo / "src" / "pkg" / "b.py").write_text("VALUE = 1\n", encoding="utf-8")
    snapshot = tmp_path / "project-model-v1.json"
    snapshot.write_text(
        json.dumps(
            {
                "schemaVersion": "project-model/v1",
                "id": "snapshot-ranker-evidence",
                "projectGraph": {"nodes": [], "edges": []},
                "snapshot": {"verification_gaps": [{"id": "gap.arch", "description": "No import guard."}]},
                "iterationReadiness": {
                    "openQuestions": [{"id": "question.arch", "question": "Should pkg.a import pkg.b?"}],
                    "qualityGates": [],
                },
            },
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    finding = _finding(
        "probe.context",
        "architecture_specs_contracts",
        "medium",
        evidence_path="iterationReadiness.openQuestions",
    )
    finding["autonomyBoundary"] = "advisory_only"
    scorecard = tmp_path / "scorecard.json"
    payload = {
        "schemaVersion": "project-intake-scorecard/v0",
        "id": "scorecard-ranker-evidence",
        "snapshotId": "snapshot-ranker-evidence",
        "snapshotPath": str(snapshot),
        "profile": "new-project",
        "weights": {"architecture_specs_contracts": 14},
        "findings": [finding],
    }
    scorecard.write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")

    class ContextProbeDomain:
        name = "context_probe"

        def candidates_for_finding(self, finding, context):  # type: ignore[no-untyped-def]
            import_pairs = {(edge.from_symbol, edge.to_symbol) for edge in context.graph_slice.import_edges}
            if context.open_questions and context.verification_gaps and ("pkg.a", "pkg.b") in import_pairs:
                return [ProposalCandidateDraft("context intent", "src/pkg/a.py", "context success")]
            return []

    ranked = build_ranked_proposals(
        repo,
        scorecard,
        max_candidates=10,
        registry=ProposalDomainRegistry([ContextProbeDomain()]),
    )

    assert [entry.finding_id for entry in ranked.entries] == ["probe.context"]
    assert ranked.skipped == ()
