from __future__ import annotations

import copy
from pathlib import Path
from typing import Any

from arena.project_graph import build_project_graph
from arena.project_model_gate import run_project_model_gate
from arena.project_probe_runner import (
    PATH_BUCKET_PROBE_ID,
    SEMANTIC_PROBE_GAP_ID,
    build_path_bucket_planted_negative,
    canonical_probe_control_snapshot,
    run_path_bucket_adversarial_probe,
    write_probe_proof_artifacts,
)
from arena.project_snapshot import VerificationGap, snapshot_to_dict, stable_hash_json
from tests.test_project_snapshot_gate import _base_snapshot, _write_repo


def _control_snapshot(graph: Any) -> Any:
    snapshot = _base_snapshot(graph)
    snapshot.held_out_probes = []
    snapshot.verification_gaps = [
        VerificationGap(
            id=SEMANTIC_PROBE_GAP_ID,
            description="Semantic component quality has not been independently probe-validated; deterministic graph grounding still constrains project claims.",
            severity="medium",
            component_ids=[component.id for component in snapshot.components],
            contract_ids=[contract.id for contract in snapshot.contracts],
            provenance_refs=snapshot.components[0].provenance_refs[:1],
            proposed_closure_check="Generate independent planted-negative and golden-control probe artifacts, then rerun the deterministic gate.",
        )
    ]
    return snapshot


def _repo_graph(tmp_path: Path) -> Any:
    _write_repo(tmp_path)
    return build_project_graph(tmp_path)


def _rehash(payload: dict[str, Any]) -> dict[str, Any]:
    payload = copy.deepcopy(payload)
    payload.pop("deterministic_result_hash", None)
    payload["deterministic_result_hash"] = stable_hash_json(payload)
    return payload


def _proof_path(artifact_base: Path, result: Any) -> Path:
    assert result.probe is not None
    assert result.probe.proof_artifact is not None
    return artifact_base / result.probe.proof_artifact


def test_path_bucket_probe_passes_golden_and_rejects_planted_negative(tmp_path: Path) -> None:
    graph = _repo_graph(tmp_path)
    snapshot = _control_snapshot(graph)

    result = run_path_bucket_adversarial_probe(snapshot, graph)

    assert result.probe is not None
    assert result.probe.id == PATH_BUCKET_PROBE_ID
    assert result.probe.golden_control_passed is True
    assert result.probe.discrimination_passed is True
    assert result.probe.proof_artifact == "proofs/probe.path-bucket-contract-discrimination.json"
    assert result.probe.verification_gap_ids == []
    assert result.proof_artifacts
    proof = next(iter(result.proof_artifacts.values()))
    assert proof["golden_control_passed"] is True
    assert proof["discrimination_passed"] is True
    assert proof["planted_negative_input"]["snapshot"]
    assert proof["negative_mutation"]["type"] == "path_bucket_component_rewrite"
    assert any(gap.id == SEMANTIC_PROBE_GAP_ID for gap in result.snapshot.verification_gaps)


def test_planted_negative_is_path_bucket_and_gate_rejects_it(tmp_path: Path) -> None:
    graph = _repo_graph(tmp_path)
    snapshot = _control_snapshot(graph)

    negative = build_path_bucket_planted_negative(snapshot, graph)
    report = run_project_model_gate(negative.snapshot, graph)

    assert report.passed is False
    assert negative.mutation["expected_violation_gate"] == "component_measurability"
    assert any(
        violation.gate == "component_measurability"
        and violation.location == negative.mutation["expected_violation_location"]
        and "file-bucket" in violation.message
        for violation in report.violations
    )


def test_probe_result_is_deterministic_for_same_inputs(tmp_path: Path) -> None:
    graph = _repo_graph(tmp_path)
    snapshot = _control_snapshot(graph)

    first = run_path_bucket_adversarial_probe(copy.deepcopy(snapshot), graph)
    second = run_path_bucket_adversarial_probe(copy.deepcopy(snapshot), graph)

    assert first.proof_artifacts == second.proof_artifacts
    first_proof = next(iter(first.proof_artifacts.values()))
    second_proof = next(iter(second.proof_artifacts.values()))
    assert first_proof["deterministic_result_hash"] == second_proof["deterministic_result_hash"]


def test_probe_does_not_write_or_attach_proof_when_control_fails(tmp_path: Path) -> None:
    graph = _repo_graph(tmp_path)
    snapshot = _control_snapshot(graph)
    snapshot.components[0].responsibility = "Too short."

    result = run_path_bucket_adversarial_probe(snapshot, graph)
    written = write_probe_proof_artifacts(tmp_path / "snapshot", result)

    assert result.proof_artifacts == {}
    assert written == []
    assert result.probe is not None
    assert result.probe.proof_artifact is None
    assert result.probe.golden_control_passed is False
    assert SEMANTIC_PROBE_GAP_ID in result.probe.verification_gap_ids


def test_canonical_probe_control_hash_ignores_attached_probes_only(tmp_path: Path) -> None:
    graph = _repo_graph(tmp_path)
    snapshot = _control_snapshot(graph)
    result = run_path_bucket_adversarial_probe(copy.deepcopy(snapshot), graph)

    assert stable_hash_json(snapshot_to_dict(canonical_probe_control_snapshot(result.snapshot))) == stable_hash_json(
        snapshot_to_dict(snapshot)
    )


def test_write_probe_proof_artifacts_writes_only_passed_payloads(tmp_path: Path) -> None:
    graph = _repo_graph(tmp_path)
    snapshot = _control_snapshot(graph)
    result = run_path_bucket_adversarial_probe(snapshot, graph)

    written = write_probe_proof_artifacts(tmp_path / "snapshot", result)

    assert written == ["proofs/probe.path-bucket-contract-discrimination.json"]
    assert (tmp_path / "snapshot" / written[0]).exists()

    failing = _control_snapshot(graph)
    failing.components[0].responsibility = "Too short."
    failed_result = run_path_bucket_adversarial_probe(failing, graph)

    assert write_probe_proof_artifacts(tmp_path / "failed", failed_result) == []
    assert not (tmp_path / "failed").exists()


def test_gate_accepts_passed_probe_with_valid_replayable_proof_json(tmp_path: Path) -> None:
    graph = _repo_graph(tmp_path)
    snapshot = _control_snapshot(graph)
    result = run_path_bucket_adversarial_probe(snapshot, graph)
    artifact_base = tmp_path / "snapshot"
    write_probe_proof_artifacts(artifact_base, result)

    report = run_project_model_gate(result.snapshot, graph, proof_artifact_base=artifact_base)

    assert report.passed is True
    assert report.violations == []


def test_gate_rejects_passed_probe_when_proof_json_is_missing_or_invalid(tmp_path: Path) -> None:
    graph = _repo_graph(tmp_path)
    snapshot = _control_snapshot(graph)
    result = run_path_bucket_adversarial_probe(snapshot, graph)

    missing = run_project_model_gate(result.snapshot, graph, proof_artifact_base=tmp_path / "missing")
    assert missing.passed is False
    assert any(violation.gate == "held_out_probe_proof" for violation in missing.violations)

    artifact_base = tmp_path / "snapshot"
    write_probe_proof_artifacts(artifact_base, result)
    proof_path = _proof_path(artifact_base, result)
    proof_path.write_text('{"schema_version":"wrong"}\n', encoding="utf-8")

    invalid = run_project_model_gate(result.snapshot, graph, proof_artifact_base=artifact_base)
    assert invalid.passed is False
    assert any(violation.gate == "held_out_probe_proof" for violation in invalid.violations)


def test_gate_rejects_forged_internally_consistent_probe_proof(tmp_path: Path) -> None:
    graph = _repo_graph(tmp_path)
    snapshot = _control_snapshot(graph)
    result = run_path_bucket_adversarial_probe(snapshot, graph)
    artifact_base = tmp_path / "snapshot"
    write_probe_proof_artifacts(artifact_base, result)
    proof_path = _proof_path(artifact_base, result)
    proof = copy.deepcopy(next(iter(result.proof_artifacts.values())))
    control = canonical_probe_control_snapshot(result.snapshot)
    proof["planted_negative_input"]["snapshot"] = snapshot_to_dict(control)
    proof["planted_negative_input"]["snapshot_hash"] = stable_hash_json(snapshot_to_dict(control))
    proof["planted_negative_input"]["gate_passed"] = False
    proof_path.write_text(__import__("json").dumps(_rehash(proof), sort_keys=True, indent=2) + "\n", encoding="utf-8")

    report = run_project_model_gate(result.snapshot, graph, proof_artifact_base=artifact_base)

    assert report.passed is False
    assert any(violation.gate == "held_out_probe_proof" for violation in report.violations)


def test_gate_rejects_replayed_probe_proof_for_different_control_snapshot(tmp_path: Path) -> None:
    graph = _repo_graph(tmp_path)
    snapshot = _control_snapshot(graph)
    result = run_path_bucket_adversarial_probe(snapshot, graph)
    artifact_base = tmp_path / "snapshot"
    write_probe_proof_artifacts(artifact_base, result)
    replayed = copy.deepcopy(result.snapshot)
    replayed.components[0].responsibility = replayed.components[0].responsibility + " Extra replay drift."

    report = run_project_model_gate(replayed, graph, proof_artifact_base=artifact_base)

    assert report.passed is False
    assert any(violation.gate == "held_out_probe_proof" and "control" in violation.message for violation in report.violations)


def test_gate_rejects_absolute_or_parent_relative_probe_proof_paths(tmp_path: Path) -> None:
    graph = _repo_graph(tmp_path)
    snapshot = _control_snapshot(graph)
    result = run_path_bucket_adversarial_probe(snapshot, graph)

    absolute = copy.deepcopy(result.snapshot)
    absolute.held_out_probes[0].proof_artifact = "/tmp/proof.json"
    absolute_report = run_project_model_gate(absolute, graph, proof_artifact_base=tmp_path)

    parent = copy.deepcopy(result.snapshot)
    parent.held_out_probes[0].proof_artifact = "../proof.json"
    parent_report = run_project_model_gate(parent, graph, proof_artifact_base=tmp_path)

    assert any(violation.gate == "held_out_probe_proof" for violation in absolute_report.violations)
    assert any(violation.gate == "held_out_probe_proof" for violation in parent_report.violations)


def test_gate_rejects_negative_that_fails_for_unrelated_reason_only(tmp_path: Path) -> None:
    graph = _repo_graph(tmp_path)
    snapshot = _control_snapshot(graph)
    result = run_path_bucket_adversarial_probe(snapshot, graph)
    artifact_base = tmp_path / "snapshot"
    write_probe_proof_artifacts(artifact_base, result)
    proof_path = _proof_path(artifact_base, result)
    proof = copy.deepcopy(next(iter(result.proof_artifacts.values())))
    unrelated = canonical_probe_control_snapshot(result.snapshot)
    unrelated.goal = ""
    proof["planted_negative_input"]["snapshot"] = snapshot_to_dict(unrelated)
    proof["planted_negative_input"]["snapshot_hash"] = stable_hash_json(snapshot_to_dict(unrelated))
    proof["planted_negative_input"]["gate_passed"] = False
    proof_path.write_text(__import__("json").dumps(_rehash(proof), sort_keys=True, indent=2) + "\n", encoding="utf-8")

    report = run_project_model_gate(result.snapshot, graph, proof_artifact_base=artifact_base)

    assert report.passed is False
    assert any(violation.gate == "held_out_probe_proof" for violation in report.violations)
