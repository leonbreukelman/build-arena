from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

SNAPSHOT_SCHEMA_VERSION = "project-model-snapshot/v0.1"


@dataclass(slots=True)
class Component:
    id: str
    name: str
    responsibility: str
    owned_node_ids: list[str]
    provenance_refs: list[str]
    contract_ids: list[str]
    check_ids: list[str]
    verification_gap_ids: list[str]


@dataclass(slots=True)
class Contract:
    id: str
    name: str
    from_component_id: str
    to_component_id: str
    supporting_edge_ids: list[str]
    near_neighbor_alternative_ids: list[str]
    provenance_refs: list[str]


@dataclass(slots=True)
class CrossCuttingConcern:
    id: str
    category: str
    description: str
    component_ids: list[str]
    contract_ids: list[str]
    provenance_refs: list[str]
    triggered_by: list[str] = field(default_factory=list)


@dataclass(slots=True)
class ObservableCheck:
    id: str
    description: str
    command: str
    component_ids: list[str]
    contract_ids: list[str]
    provenance_refs: list[str]
    acceptance_command_id: str | None = None
    safe_to_run_by_default: bool = True
    requires_network: bool = False
    requires_paid_api: bool = False
    execution_dir: str = "."
    safety_status: str = "safe_by_default"
    execution_status: str = "execution_proven"
    proof_artifact: str | None = None
    verification_gap_ids: list[str] = field(default_factory=list)


@dataclass(slots=True)
class HeldOutProbe:
    id: str
    target_component_ids: list[str]
    target_contract_ids: list[str]
    builder_model_id: str
    builder_prompt_hash: str
    builder_independent_from_decomposer: bool
    planted_negative_id: str
    discrimination_passed: bool
    golden_control_passed: bool
    hidden_from_primary_decomposer: bool
    provenance_refs: list[str]


@dataclass(slots=True)
class VerificationGap:
    id: str
    description: str
    severity: str
    component_ids: list[str]
    contract_ids: list[str]
    provenance_refs: list[str]
    proposed_closure_check: str = "Add a deterministic local check or independent review artifact."


@dataclass(slots=True)
class NearNeighborAlternative:
    id: str
    target_id: str
    alternative: str
    why_not_primary: str
    provenance_refs: list[str]


@dataclass(slots=True)
class ProjectModelSnapshot:
    project_id: str
    project_root: str
    goal: str = "decompose this repository into responsibility-bearing components"
    non_goals: list[str] = field(default_factory=lambda: ["do not treat file buckets as final components"])
    primary_model_id: str = "fixture-good-model"
    graph_hash: str = ""
    schema_version: str = SNAPSHOT_SCHEMA_VERSION
    snapshot_id: str = ""
    created_at_utc: str = "1970-01-01T00:00:00Z"
    components: list[Component] = field(default_factory=list)
    contracts: list[Contract] = field(default_factory=list)
    cross_cutting_concerns: list[CrossCuttingConcern] = field(default_factory=list)
    observable_checks: list[ObservableCheck] = field(default_factory=list)
    held_out_probes: list[HeldOutProbe] = field(default_factory=list)
    verification_gaps: list[VerificationGap] = field(default_factory=list)
    near_neighbor_alternatives: list[NearNeighborAlternative] = field(default_factory=list)
    acceptance_command_allowlist: list[str] = field(default_factory=list)
    prompt_hashes: dict[str, str] = field(default_factory=dict)
    model_output_hashes: dict[str, str] = field(default_factory=dict)
    input_hashes: dict[str, str] = field(default_factory=dict)


@dataclass(slots=True)
class GateViolation:
    gate: str
    severity: str
    message: str
    location: str


@dataclass(slots=True)
class GateReport:
    passed: bool
    violations: list[GateViolation]


def to_plain(value: Any) -> Any:
    if hasattr(value, "__dataclass_fields__"):
        return asdict(value)
    if isinstance(value, list):
        return [to_plain(item) for item in value]
    if isinstance(value, dict):
        return {key: to_plain(value[key]) for key in sorted(value)}
    return value


def snapshot_to_dict(snapshot: ProjectModelSnapshot) -> dict[str, Any]:
    return to_plain(snapshot)


def snapshot_from_dict(data: dict[str, Any]) -> ProjectModelSnapshot:
    return ProjectModelSnapshot(
        project_id=data["project_id"],
        project_root=data["project_root"],
        goal=data.get("goal", ""),
        non_goals=list(data.get("non_goals", [])),
        primary_model_id=data.get("primary_model_id", ""),
        graph_hash=data.get("graph_hash", ""),
        schema_version=data.get("schema_version", SNAPSHOT_SCHEMA_VERSION),
        snapshot_id=data.get("snapshot_id", ""),
        created_at_utc=data.get("created_at_utc", "1970-01-01T00:00:00Z"),
        components=[Component(**item) for item in data.get("components", [])],
        contracts=[Contract(**item) for item in data.get("contracts", [])],
        cross_cutting_concerns=[CrossCuttingConcern(**item) for item in data.get("cross_cutting_concerns", [])],
        observable_checks=[ObservableCheck(**_normalize_observable_check(item)) for item in data.get("observable_checks", [])],
        held_out_probes=[HeldOutProbe(**item) for item in data.get("held_out_probes", [])],
        verification_gaps=[VerificationGap(**item) for item in data.get("verification_gaps", [])],
        near_neighbor_alternatives=[NearNeighborAlternative(**item) for item in data.get("near_neighbor_alternatives", [])],
        acceptance_command_allowlist=list(data.get("acceptance_command_allowlist", [])),
        prompt_hashes=dict(data.get("prompt_hashes", {})),
        model_output_hashes=dict(data.get("model_output_hashes", {})),
        input_hashes=dict(data.get("input_hashes", {})),
    )


def canonical_snapshot_json(snapshot: ProjectModelSnapshot) -> str:
    return json.dumps(snapshot_to_dict(snapshot), sort_keys=True, separators=(",", ":"))


def _normalize_observable_check(item: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(item)
    normalized.setdefault("execution_dir", ".")
    normalized.setdefault("safety_status", "safe_by_default")
    if "execution_status" not in normalized:
        normalized["execution_status"] = "execution_proven" if normalized.get("acceptance_command_id") else "statically_validated"
    normalized.setdefault("proof_artifact", None)
    normalized.setdefault("verification_gap_ids", [])
    return normalized


def stable_hash_json(data: Any) -> str:
    return hashlib.sha256(json.dumps(to_plain(data), sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def finalize_snapshot_identity(snapshot: ProjectModelSnapshot) -> ProjectModelSnapshot:
    original = snapshot.snapshot_id
    snapshot.snapshot_id = ""
    digest = hashlib.sha256(canonical_snapshot_json(snapshot).encode()).hexdigest()[:16]
    snapshot.snapshot_id = original or f"snapshot-{digest}"
    return snapshot


def write_json(path: str | Path, data: Any) -> str:
    text = json.dumps(to_plain(data), sort_keys=True, indent=2) + "\n"
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(text, encoding="utf-8")
    return hashlib.sha256(text.encode()).hexdigest()


def gate_report_to_dict(report: GateReport) -> dict[str, Any]:
    return to_plain(report)
