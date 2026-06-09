from __future__ import annotations

import copy
import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from arena.project_graph import GraphNode, ProjectGraph
from arena.project_model_gate import run_project_model_gate
from arena.project_snapshot import (
    HeldOutProbe,
    ProjectModelSnapshot,
    VerificationGap,
    snapshot_to_dict,
    stable_hash_json,
    write_json,
)

PROBE_PROOF_SCHEMA_VERSION = "arena.project_probe_proof/v0.1"
PROBE_RUNNER_VERSION = "arena.project_probe_runner/v0.1"
PATH_BUCKET_PROBE_ID = "probe.path-bucket-contract-discrimination"
PATH_BUCKET_NEGATIVE_ID = "negative.path-bucket-contract-decoy"
SEMANTIC_PROBE_GAP_ID = "gap.semantic-understanding-not-independently-validated"
PROOF_ARTIFACT_PATH = f"proofs/{PATH_BUCKET_PROBE_ID}.json"
_PROBE_PROMPT = "deterministic path-bucket planted-negative gate discrimination probe v0.1"


@dataclass(slots=True)
class PlantedNegative:
    snapshot: ProjectModelSnapshot
    metadata: dict[str, Any]
    mutation: dict[str, Any]


@dataclass(slots=True)
class PathBucketProbeRun:
    snapshot: ProjectModelSnapshot
    probe: HeldOutProbe | None
    proof_artifacts: dict[str, dict[str, Any]]
    planted_negatives: list[dict[str, Any]]


def canonical_probe_control_snapshot(snapshot: ProjectModelSnapshot) -> ProjectModelSnapshot:
    control = copy.deepcopy(snapshot)
    control.held_out_probes = []
    return control


def build_path_bucket_planted_negative(snapshot: ProjectModelSnapshot, graph: ProjectGraph) -> PlantedNegative:
    control = canonical_probe_control_snapshot(snapshot)
    components = {component.id: component for component in control.components}
    node_by_id = {node.id: node for node in graph.nodes}
    nodes_by_path: dict[str, list[GraphNode]] = {}
    for node in graph.nodes:
        if node.path:
            nodes_by_path.setdefault(node.path, []).append(node)

    for contract in sorted(control.contracts, key=lambda item: item.id):
        from_component = components.get(contract.from_component_id)
        to_component = components.get(contract.to_component_id)
        if from_component is None or to_component is None:
            continue
        file_node_ids = _component_file_node_ids([from_component, to_component], node_by_id, nodes_by_path)
        if len(file_node_ids) < 2:
            continue
        negative = copy.deepcopy(control)
        negative.held_out_probes = []
        negative_components = {component.id: component for component in negative.components}
        mutated = negative_components[from_component.id]
        source_paths = _paths_for_node_ids(file_node_ids, node_by_id)
        mutated.owned_node_ids = file_node_ids
        mutated.responsibility = "Contains " + ", ".join(source_paths) + " as a path/file-bucket decomposition instead of an import-backed responsibility."
        mutated.verification_gap_ids = []
        mutation = {
            "type": "path_bucket_component_rewrite",
            "mutated_component_id": mutated.id,
            "source_file_node_ids": file_node_ids,
            "expected_violation_gate": "component_measurability",
            "expected_violation_location": f"components[{mutated.id}]",
            "expected_violation_text": "file-bucket",
        }
        metadata = {
            "id": PATH_BUCKET_NEGATIVE_ID,
            "kind": "path_bucket_contract_decoy",
            "target_probe_id": PATH_BUCKET_PROBE_ID,
            "target_contract_ids": [contract.id],
            "target_component_ids": [from_component.id, to_component.id],
            "mutation": mutation,
            "independent_from_probe_builder": True,
        }
        metadata["snapshot_hash"] = stable_hash_json(snapshot_to_dict(negative))
        return PlantedNegative(snapshot=negative, metadata=metadata, mutation=mutation)

    raise ValueError("no import-backed contract with at least two source files is available for path-bucket probe")


def run_path_bucket_adversarial_probe(snapshot: ProjectModelSnapshot, graph: ProjectGraph) -> PathBucketProbeRun:
    control = canonical_probe_control_snapshot(snapshot)
    output_snapshot = copy.deepcopy(control)
    target_component_ids: list[str] = []
    target_contract_ids: list[str] = []
    provenance_refs = _first_snapshot_provenance(output_snapshot)
    proof_artifacts: dict[str, dict[str, Any]] = {}
    planted_negatives: list[dict[str, Any]] = []

    control_report = run_project_model_gate(control, graph)
    negative: PlantedNegative | None = None
    negative_report = None
    discrimination_passed = False
    golden_control_passed = control_report.passed
    mutation: dict[str, Any] = {}
    try:
        negative = build_path_bucket_planted_negative(control, graph)
        planted_negatives = [negative.metadata]
        mutation = negative.mutation
        target_component_ids = list(negative.metadata["target_component_ids"])
        target_contract_ids = list(negative.metadata["target_contract_ids"])
        negative_report = run_project_model_gate(negative.snapshot, graph)
        discrimination_present = _has_expected_violation(negative_report.violations, mutation)
        absent_from_control = not _has_expected_violation(control_report.violations, mutation)
        discrimination_passed = (not negative_report.passed) and discrimination_present and absent_from_control
    except ValueError:
        planted_negatives = []

    passed = golden_control_passed and discrimination_passed and negative is not None and negative_report is not None
    if passed:
        assert negative is not None
        assert negative_report is not None
        probe = _probe(
            target_component_ids=target_component_ids,
            target_contract_ids=target_contract_ids,
            provenance_refs=provenance_refs,
            golden_control_passed=True,
            discrimination_passed=True,
            proof_artifact=PROOF_ARTIFACT_PATH,
            verification_gap_ids=[],
            primary_model_id=output_snapshot.primary_model_id,
        )
        output_snapshot.held_out_probes = [probe]
        proof = _proof_payload(
            snapshot=output_snapshot,
            control=control,
            control_report=control_report,
            negative=negative,
            negative_report=negative_report,
            mutation=mutation,
            target_component_ids=target_component_ids,
            target_contract_ids=target_contract_ids,
            provenance_refs=provenance_refs,
        )
        proof_artifacts[PROOF_ARTIFACT_PATH] = proof
    else:
        _ensure_semantic_gap(output_snapshot, target_component_ids=target_component_ids, target_contract_ids=target_contract_ids, provenance_refs=provenance_refs)
        probe = _probe(
            target_component_ids=target_component_ids,
            target_contract_ids=target_contract_ids,
            provenance_refs=provenance_refs,
            golden_control_passed=False,
            discrimination_passed=False,
            proof_artifact=None,
            verification_gap_ids=[SEMANTIC_PROBE_GAP_ID],
            primary_model_id=output_snapshot.primary_model_id,
        )
        output_snapshot.held_out_probes = [probe]

    return PathBucketProbeRun(snapshot=output_snapshot, probe=probe, proof_artifacts=proof_artifacts, planted_negatives=planted_negatives)


def write_probe_proof_artifacts(artifact_base: str | Path, result: PathBucketProbeRun) -> list[str]:
    written: list[str] = []
    for rel_path, payload in sorted(result.proof_artifacts.items()):
        write_json(Path(artifact_base) / rel_path, payload)
        written.append(rel_path)
    return written


def _proof_payload(
    *,
    snapshot: ProjectModelSnapshot,
    control: ProjectModelSnapshot,
    control_report: Any,
    negative: PlantedNegative,
    negative_report: Any,
    mutation: dict[str, Any],
    target_component_ids: list[str],
    target_contract_ids: list[str],
    provenance_refs: list[str],
) -> dict[str, Any]:
    negative_violation_gates = sorted({violation.gate for violation in negative_report.violations})
    control_violation_gates = sorted({violation.gate for violation in control_report.violations})
    present_in_negative = _has_expected_violation(negative_report.violations, mutation)
    absent_from_control = not _has_expected_violation(control_report.violations, mutation)
    payload: dict[str, Any] = {
        "schema_version": PROBE_PROOF_SCHEMA_VERSION,
        "probe_id": PATH_BUCKET_PROBE_ID,
        "probe_kind": "path_bucket_planted_negative_gate_discrimination",
        "graph_hash": snapshot.graph_hash,
        "golden_control_input": {
            "kind": "project_model_snapshot_without_held_out_probes",
            "snapshot_hash": stable_hash_json(snapshot_to_dict(control)),
            "gate_passed": control_report.passed,
        },
        "planted_negative_input": {
            "kind": "embedded_project_model_snapshot",
            "planted_negative_id": PATH_BUCKET_NEGATIVE_ID,
            "snapshot_hash": stable_hash_json(snapshot_to_dict(negative.snapshot)),
            "gate_passed": negative_report.passed,
            "snapshot": snapshot_to_dict(negative.snapshot),
        },
        "negative_mutation": mutation,
        "target_component_ids": sorted(target_component_ids),
        "target_contract_ids": sorted(target_contract_ids),
        "planted_negative_id": PATH_BUCKET_NEGATIVE_ID,
        "checks": [
            {
                "id": "golden-control-gate",
                "kind": "project_model_gate",
                "expected_passed": True,
                "actual_passed": control_report.passed,
                "violation_gates": control_violation_gates,
            },
            {
                "id": "planted-negative-gate",
                "kind": "project_model_gate",
                "expected_passed": False,
                "actual_passed": negative_report.passed,
                "violation_gates": negative_violation_gates,
            },
            {
                "id": "expected-discrimination-delta",
                "kind": "gate_violation_delta",
                "expected_gate": mutation["expected_violation_gate"],
                "expected_location": mutation["expected_violation_location"],
                "expected_text": mutation["expected_violation_text"],
                "present_in_planted_negative": present_in_negative,
                "absent_from_golden_control": absent_from_control,
                "matched": present_in_negative and absent_from_control,
            },
        ],
        "golden_control_passed": control_report.passed,
        "discrimination_passed": (not negative_report.passed) and present_in_negative and absent_from_control,
        "provenance_refs": sorted(provenance_refs),
        "tool_versions": {
            "probe_runner": PROBE_RUNNER_VERSION,
            "gate": "arena.project_model_gate",
        },
    }
    payload["deterministic_result_hash"] = stable_hash_json(payload)
    return payload


def _probe(
    *,
    target_component_ids: list[str],
    target_contract_ids: list[str],
    provenance_refs: list[str],
    golden_control_passed: bool,
    discrimination_passed: bool,
    proof_artifact: str | None,
    verification_gap_ids: list[str],
    primary_model_id: str,
) -> HeldOutProbe:
    return HeldOutProbe(
        id=PATH_BUCKET_PROBE_ID,
        target_component_ids=sorted(target_component_ids),
        target_contract_ids=sorted(target_contract_ids),
        builder_model_id="deterministic-project-probe-runner/v0.1",
        builder_prompt_hash=hashlib.sha256(_PROBE_PROMPT.encode()).hexdigest(),
        builder_independent_from_decomposer=True,
        planted_negative_id=PATH_BUCKET_NEGATIVE_ID,
        discrimination_passed=discrimination_passed,
        golden_control_passed=golden_control_passed,
        hidden_from_primary_decomposer=True,
        provenance_refs=sorted(provenance_refs),
        proof_artifact=proof_artifact,
        verification_gap_ids=verification_gap_ids,
    )


def _component_file_node_ids(components: list[Any], node_by_id: dict[str, GraphNode], nodes_by_path: dict[str, list[GraphNode]]) -> list[str]:
    paths: set[str] = set()
    for component in components:
        for node_id in component.owned_node_ids:
            node = node_by_id.get(str(node_id))
            if node and node.path:
                paths.add(node.path)
    file_node_ids: list[str] = []
    for path in sorted(paths):
        file_nodes = [node for node in nodes_by_path.get(path, []) if node.kind == "file"]
        file_node_ids.extend(node.id for node in sorted(file_nodes, key=lambda item: item.id))
    return sorted(set(file_node_ids))


def _paths_for_node_ids(node_ids: list[str], node_by_id: dict[str, GraphNode]) -> list[str]:
    paths = [node_by_id[node_id].path or node_id for node_id in node_ids if node_id in node_by_id]
    return sorted(paths)


def _has_expected_violation(violations: list[Any], mutation: dict[str, Any]) -> bool:
    expected_text = str(mutation.get("expected_violation_text") or "").lower()
    expected_location = str(mutation.get("expected_violation_location") or "")
    expected_gate = str(mutation.get("expected_violation_gate") or "")
    for violation in violations:
        if violation.gate != expected_gate:
            continue
        if violation.location != expected_location:
            continue
        if expected_text and expected_text not in violation.message.lower():
            continue
        return True
    return False


def _first_snapshot_provenance(snapshot: ProjectModelSnapshot) -> list[str]:
    refs: list[str] = []
    for component in snapshot.components:
        for ref in component.provenance_refs:
            if ref and ref not in refs:
                refs.append(ref)
    return refs[:5]


def _ensure_semantic_gap(snapshot: ProjectModelSnapshot, *, target_component_ids: list[str], target_contract_ids: list[str], provenance_refs: list[str]) -> None:
    if any(gap.id == SEMANTIC_PROBE_GAP_ID for gap in snapshot.verification_gaps):
        return
    snapshot.verification_gaps.append(
        VerificationGap(
            id=SEMANTIC_PROBE_GAP_ID,
            description="Semantic component quality has not been independently probe-validated; deterministic graph grounding constrains project claims, but no planted-negative/golden-control probe artifacts passed.",
            severity="medium",
            component_ids=sorted(target_component_ids or [component.id for component in snapshot.components]),
            contract_ids=sorted(target_contract_ids or [contract.id for contract in snapshot.contracts]),
            provenance_refs=sorted(provenance_refs),
            proposed_closure_check="Run independent planted-negative and golden-control probe artifacts, capture the proof outputs, and rerun the deterministic gate.",
        )
    )
