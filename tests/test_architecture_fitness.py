from __future__ import annotations

import json
import subprocess
from pathlib import Path

from jsonschema import Draft202012Validator

from arena.architecture_fitness import (
    architecture_contract_target,
    build_import_cycle_contract,
    canonical_contract_text,
    contract_digest,
    selected_import_cycle,
    validate_architecture_contract,
)
from arena.graph_slice import fresh_graph_slice
from arena.proposal_planner import build_proposal_plan


def _cyclic_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    (repo / "src" / "pkg").mkdir(parents=True)
    (repo / "src" / "pkg" / "__init__.py").write_text("", encoding="utf-8")
    (repo / "src" / "pkg" / "a.py").write_text("from pkg import b\n", encoding="utf-8")
    (repo / "src" / "pkg" / "b.py").write_text("from pkg import a\n", encoding="utf-8")
    return repo


def _write_scorecard(tmp_path: Path, repo: Path) -> Path:
    scorecard = tmp_path / "scorecard.json"
    scorecard.write_text(
        json.dumps(
            {
                "schemaVersion": "project-intake-scorecard/v0",
                "id": "scorecard-architecture",
                "snapshotId": "snapshot-architecture",
                "projectRoot": str(repo),
                "profile": "new-project",
                "weights": {"architecture_specs_contracts": 14},
                "findings": [
                    {
                        "id": "architecture.open-questions-or-gaps",
                        "dimension": "architecture_specs_contracts",
                        "title": "Architecture questions need a binding check",
                        "severity": "medium",
                        "confidence": "high",
                        "estimatedEffort": "small",
                        "evidence": [{"kind": "project_model", "path": "iterationReadiness.openQuestions", "checked": True}],
                        "recommendedAction": "Add a fitness function only for graph-evident violations.",
                        "verification": [],
                        "autonomyBoundary": "advisory_only",
                        "impactOnFutureIteration": 3,
                        "riskReduction": 3,
                        "verificationGain": 4,
                        "docKnowledgeGain": 1,
                        "priorityScore": 154.0,
                        "rank": 1,
                    }
                ],
            },
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    return scorecard


def _write_contract(repo: Path, contract: dict[str, object]) -> Path:
    digest = contract_digest(contract)
    path = repo / architecture_contract_target(digest)
    path.parent.mkdir(parents=True, exist_ok=True)
    finalized = dict(contract)
    finalized["id"] = f"architecture-fitness-{digest}"
    path.write_text(canonical_contract_text(finalized), encoding="utf-8")
    return path


def test_architecture_fitness_domain_emits_grounded_contract_candidate(tmp_path: Path) -> None:
    repo = _cyclic_repo(tmp_path)
    scorecard = _write_scorecard(tmp_path, repo)

    plan = build_proposal_plan(repo, scorecard, max_candidates=10)

    candidate = plan.candidates[0]
    assert candidate.finding_id == "architecture.open-questions-or-gaps"
    assert candidate.target_path.startswith("tests/architecture/architecture-fitness-")
    assert candidate.target_path.endswith(".json")
    assert candidate.verification_commands == (f"python3 -m arena.architecture_fitness_gate --repo . --contract {candidate.target_path}",)
    assert "pkg.a" in candidate.intent
    assert "pkg.b" in candidate.intent
    assert "pkg.missing" not in candidate.intent
    assert plan.finding_dispositions[0]["disposition"] == "fitness_function_candidate"
    schema = json.loads((Path(__file__).resolve().parents[1] / "docs" / "schemas" / "proposal-plan-v0.schema.json").read_text(encoding="utf-8"))
    errors = sorted(Draft202012Validator(schema).iter_errors(plan.to_jsonable()), key=lambda error: list(error.path))
    assert errors == []


def test_architecture_gate_accepts_binding_failing_cycle_and_cli_fails_closed(tmp_path: Path) -> None:
    repo = _cyclic_repo(tmp_path)
    graph = fresh_graph_slice(repo)
    contract = build_import_cycle_contract(
        finding_id="architecture.open-questions-or-gaps",
        cycle=selected_import_cycle(graph),
    )
    path = _write_contract(repo, contract)

    result = validate_architecture_contract(repo, path)

    assert result.accepted is True
    assert result.current_status == "failing"
    assert result.reason == "accepted"
    assert result.derived_findings
    proc = subprocess.run(
        ["python3", "-m", "arena.architecture_fitness_gate", "--repo", str(repo), "--contract", str(path)],
        cwd=Path(__file__).resolve().parents[1],
        text=True,
        capture_output=True,
        check=False,
    )
    payload = json.loads(proc.stdout)
    assert proc.returncode == 1
    assert payload["accepted"] is True
    assert payload["currentStatus"] == "failing"


def test_architecture_gate_rejects_fabricated_vacuous_duplicate_and_digest_mismatch(tmp_path: Path) -> None:
    repo = _cyclic_repo(tmp_path)
    graph = fresh_graph_slice(repo)
    valid = build_import_cycle_contract(
        finding_id="architecture.open-questions-or-gaps",
        cycle=selected_import_cycle(graph),
    )
    first_path = _write_contract(repo, valid)

    fabricated = dict(valid)
    fabricated["modules"] = ["pkg.a", "pkg.missing"]
    fabricated["forbiddenEdges"] = [{"from": "pkg.a", "to": "pkg.missing"}, {"from": "pkg.missing", "to": "pkg.a"}]
    fabricated_path = _write_contract(repo, fabricated)
    assert validate_architecture_contract(repo, fabricated_path).reason == "unknown_module"

    vacuous = dict(valid)
    vacuous["modules"] = ["pkg.a", "pkg.b"]
    vacuous["forbiddenEdges"] = [{"from": "pkg.a", "to": "pkg.b"}]
    vacuous_path = _write_contract(repo, vacuous)
    assert validate_architecture_contract(repo, vacuous_path).reason == "non_binding_contract"

    duplicate = dict(valid)
    duplicate["findingId"] = "architecture.other"
    duplicate["description"] = "Different words, same semantic cycle."
    duplicate_path = repo / "tests" / "architecture" / "nested" / f"architecture-fitness-{contract_digest(duplicate)}.json"
    duplicate_path.parent.mkdir(parents=True, exist_ok=True)
    duplicate_finalized = dict(duplicate)
    duplicate_finalized["id"] = f"architecture-fitness-{contract_digest(duplicate)}"
    duplicate_path.write_text(canonical_contract_text(duplicate_finalized), encoding="utf-8")
    assert validate_architecture_contract(repo, duplicate_path).reason == "duplicate_contract"

    mismatched = json.loads(first_path.read_text(encoding="utf-8"))
    mismatched["forbiddenEdges"] = [{"from": "pkg.a", "to": "pkg.b"}]
    first_path.write_text(json.dumps(mismatched, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    assert validate_architecture_contract(repo, first_path).reason == "digest_mismatch"


def test_cycle_selection_and_contract_target_are_deterministic(tmp_path: Path) -> None:
    repo = _cyclic_repo(tmp_path)
    (repo / "src" / "pkg" / "c.py").write_text("from pkg import d\n", encoding="utf-8")
    (repo / "src" / "pkg" / "d.py").write_text("from pkg import c\n", encoding="utf-8")

    graph_1 = fresh_graph_slice(repo)
    graph_2 = fresh_graph_slice(repo)
    contract_1 = build_import_cycle_contract("architecture.open-questions-or-gaps", selected_import_cycle(graph_1))
    contract_2 = build_import_cycle_contract("architecture.open-questions-or-gaps", selected_import_cycle(graph_2))

    assert canonical_contract_text(contract_1) == canonical_contract_text(contract_2)
    assert architecture_contract_target(contract_digest(contract_1)) == architecture_contract_target(contract_digest(contract_2))
    assert contract_1["modules"] == ["pkg.a", "pkg.b"]
