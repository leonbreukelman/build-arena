from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal, cast

import yaml
from pydantic import BaseModel, ConfigDict, Field

from arena.project_model_v0 import (
    AdvisorySignalHandoff,
    Assumption,
    ComponentKind,
    Dependency,
    DependencyKind,
    EvidenceRequirement,
    HeldOutProbe,
    Invariant,
    NearNeighborAlternative,
    ObservableCheck,
    ObservableCheckMode,
    ProjectModelV0,
    QualityGateReport,
    Risk,
    Source,
    UnclassifiedProjectSurface,
    evaluate_quality_gate,
)
from arena.project_model_v0 import (
    Component as ProjectModelV0Component,
)
from arena.project_model_v0 import (
    VerificationGap as ProjectModelV0VerificationGap,
)

SCHEMA_VERSION = "project-model/v0.1"

InventoryMode = Literal["git", "filesystem"]
Severity = Literal["low", "medium", "high"]


class _StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class GitState(_StrictModel):
    available: bool
    inventory_mode: InventoryMode
    toplevel: str | None = None
    head_oid: str | None = None
    branch: str | None = None
    dirty: bool = False
    dirty_paths: list[str] = Field(default_factory=list)
    untracked_paths: list[str] = Field(default_factory=list)


class FileRecord(_StrictModel):
    path: str
    sha256: str | None
    kind: str
    excluded: bool = False
    reason: str | None = None
    missing_on_disk: bool = False


class FileInventory(_StrictModel):
    included_files: list[FileRecord] = Field(default_factory=list)
    excluded_files: list[FileRecord] = Field(default_factory=list)


class MechanicalCheck(_StrictModel):
    id: str
    command: str
    description: str = ""
    referenced_paths: list[str] = Field(default_factory=list)
    no_live_api: bool = True


class ScoringDimension(_StrictModel):
    id: str
    description: str
    weight: float = 1.0
    mechanical_signal: str


class FingerprintTemplate(_StrictModel):
    id: str
    intent: str
    target_files: list[str]
    technique_tag: str
    success_criterion: str
    failure_criterion: str


class RollbackBoundary(_StrictModel):
    id: str
    stop_condition: str
    files: list[str] = Field(default_factory=list)


class ScopeBoundary(_StrictModel):
    id: str
    in_scope: list[str] = Field(default_factory=list)
    out_of_scope: list[str] = Field(default_factory=list)


class VerificationGap(_StrictModel):
    id: str
    component_id: str
    severity: Severity
    evidence: list[str]
    proposed_check: str


class Component(_StrictModel):
    id: str
    name: str
    kind: str
    owned_files: list[str]
    responsibilities: list[str]
    checks: list[MechanicalCheck] = Field(default_factory=list)
    scoring_dimensions: list[ScoringDimension] = Field(default_factory=list)
    fingerprint_templates: list[FingerprintTemplate] = Field(default_factory=list)
    rollback_boundaries: list[RollbackBoundary] = Field(default_factory=list)
    scope_boundaries: list[ScopeBoundary] = Field(default_factory=list)
    verification_gaps: list[str] = Field(default_factory=list)


class Contract(_StrictModel):
    id: str
    producer_component_id: str
    consumer_component_id: str
    assumes: list[str]
    guarantees: list[str]
    checks: list[MechanicalCheck] = Field(default_factory=list)
    verification_gaps: list[str] = Field(default_factory=list)


class CrossCuttingConcern(_StrictModel):
    id: str
    description: str
    affected_components: list[str]
    checks: list[MechanicalCheck] = Field(default_factory=list)
    verification_gaps: list[str] = Field(default_factory=list)


class CoverageReport(_StrictModel):
    total_files: int
    included_files: int
    excluded_files: int
    owned_included_files: int
    coverage_numerator: int
    coverage_denominator: int
    unowned_included_files: list[str] = Field(default_factory=list)
    multiply_owned_included_files: dict[str, list[str]] = Field(default_factory=dict)


class ProjectModel(_StrictModel):
    schema_version: str = SCHEMA_VERSION
    project_id: str
    project_root: str
    git: GitState
    file_inventory: FileInventory
    components: list[Component] = Field(default_factory=list)
    contracts: list[Contract] = Field(default_factory=list)
    cross_cutting_concerns: list[CrossCuttingConcern] = Field(default_factory=list)
    verification_gaps: list[VerificationGap] = Field(default_factory=list)
    coverage: CoverageReport


class DecompositionValidationReport(_StrictModel):
    valid: bool
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    gap_count: int = 0


@dataclass(frozen=True)
class _ScanResult:
    root: Path
    git: GitState
    inventory: FileInventory


def decompose_project(project_root: Path | str, project_id: str | None = None) -> ProjectModel:
    """Scan a project and emit a deterministic, mechanically checkable model.

    The decomposer only reads filesystem/git state. It records commands that a
    later verifier may run, but it does not execute project tests, runners, or
    live model/API calls.
    """
    scan = _scan_project(Path(project_root))
    resolved_project_id = project_id or scan.root.name
    included_paths = {record.path for record in scan.inventory.included_files}

    if _looks_like_arena_calibration(included_paths):
        components, contracts, concerns, gaps = _arena_calibration_decomposition(scan.root, included_paths)
    else:
        components, contracts, concerns, gaps = _generic_decomposition(included_paths)

    coverage = _build_coverage(scan.inventory, components)
    model = ProjectModel(
        project_id=resolved_project_id,
        project_root=str(scan.root),
        git=scan.git,
        file_inventory=scan.inventory,
        components=_sort_components(components),
        contracts=sorted(contracts, key=lambda contract: contract.id),
        cross_cutting_concerns=sorted(concerns, key=lambda concern: concern.id),
        verification_gaps=sorted(gaps, key=lambda gap: gap.id),
        coverage=coverage,
    )
    return model


def decompose_project_model_v0(
    project_root: Path | str,
    *,
    source_task: str,
    primary_backlog_item: str,
    project_id: str | None = None,
    repo: str | None = None,
    issue: str | None = None,
) -> ProjectModelV0:
    """Emit the shared Project Model v0 contract from a primary task.

    This is a compatibility adapter over the deterministic filesystem/git
    scanner model. It preserves the existing `project-model/v0.1` decomposer
    shape while giving downstream agents a canonical `project-model/v0` JSON
    document before planning, architecture, or code work begins.
    """
    internal_model = decompose_project(project_root, project_id=project_id)
    return project_model_v0_from_decomposition(
        internal_model,
        source_task=source_task,
        primary_backlog_item=primary_backlog_item,
        repo=repo,
        issue=issue,
    )


def project_model_v0_from_decomposition(
    model: ProjectModel,
    *,
    source_task: str,
    primary_backlog_item: str,
    repo: str | None = None,
    issue: str | None = None,
) -> ProjectModelV0:
    component_id_map = _component_id_map(model.components)
    gaps_by_component: dict[str, list[VerificationGap]] = defaultdict(list)
    for gap in model.verification_gaps:
        gaps_by_component[gap.component_id].append(gap)

    observable_checks: list[ObservableCheck] = []
    component_check_ids: dict[str, list[str]] = defaultdict(list)
    used_check_ids: set[str] = set()
    for component in model.components:
        component_id = component_id_map[component.id]
        for check in component.checks:
            check_id = _unique_identifier(check.id, used_check_ids, f"{component_id}_check")
            component_check_ids[component.id].append(check_id)
            observable_checks.append(
                ObservableCheck(
                    id=check_id,
                    componentId=component_id,
                    mode=_observable_mode_for_check(check),
                    description=check.description or f"Run {check.command} for {component.name}.",
                    observableSignal=check.command,
                    evidenceRequired=_check_evidence_requirements(check),
                    noLiveApi=check.no_live_api,
                )
            )
        if not component.checks and component.verification_gaps:
            check_id = _unique_identifier(
                f"{component_id}_verification_gap_observed",
                used_check_ids,
                f"{component_id}_gap_check",
            )
            gap_ids = sorted(component.verification_gaps)
            component_check_ids[component.id].append(check_id)
            observable_checks.append(
                ObservableCheck(
                    id=check_id,
                    componentId=component_id,
                    mode="inspection",
                    description=f"Inspect surfaced verification gap(s) for {component.name}.",
                    observableSignal="verification gap is present in verificationGaps and has proposed closure evidence",
                    evidenceRequired=gap_ids,
                    noLiveApi=True,
                )
            )

    v0_components = [
        ProjectModelV0Component(
            id=component_id_map[component.id],
            name=component.name,
            kind=_component_kind_for_v0(component),
            riskLevel=_component_risk_level(component, gaps_by_component.get(component.id, [])),
            responsibilities=component.responsibilities,
            ownedSurfaces=component.owned_files or [component.name],
            observableCheckIds=sorted(component_check_ids.get(component.id, [])),
        )
        for component in model.components
    ]

    dependencies = _dependencies_for_v0(model, component_id_map, component_check_ids)
    invariants = _invariants_for_v0(model, component_id_map, component_check_ids)
    evidence_requirements = _evidence_requirements_for_v0(model, component_id_map)
    risks = _risks_for_v0(model, component_id_map)
    held_out_probes = _held_out_probes_for_v0(model, component_id_map, gaps_by_component)
    unclassified_surface = _unclassified_surface_for_v0(model, component_id_map)

    source_payload = {
        "task": source_task,
        "primaryBacklogItem": primary_backlog_item,
    }
    if repo:
        source_payload["repo"] = repo
    if issue:
        source_payload["issue"] = issue

    return ProjectModelV0(
        schemaVersion="project-model/v0",
        id=_identifier(model.project_id, "project_model"),
        source=Source(**source_payload),
        goal=source_task,
        nonGoals=[
            "Do not require live paid LLM/API calls to emit or validate this model.",
            "Do not implement Elenchus scoring or advisory evaluation in the Build Arena decomposer.",
            "Do not treat ownership accounting as quality scoring.",
        ],
        components=v0_components,
        dependencies=dependencies,
        invariants=invariants,
        observableChecks=observable_checks,
        evidenceRequirements=evidence_requirements,
        assumptions=[
            Assumption(
                id="filesystem_and_git_are_authoritative",
                description="The model is derived only from filesystem and git inventory state observed by the decomposer.",
                status="confirmed",
            )
        ],
        risks=risks,
        nearNeighborAlternatives=[
            NearNeighborAlternative(
                id="plan_without_project_model",
                description="Start implementation or architecture work from the backlog item without a shared Project Model.",
                whyNotPrimary="That reopens the F3 risk of coherent work aimed at the wrong component, sequence, or example.",
                distinguishingEvidence=["schemaVersion", "components", "dependencies", "observableChecks"],
            ),
            NearNeighborAlternative(
                id="ownership_only_decomposition",
                description="Use file ownership coverage as the only decomposition signal.",
                whyNotPrimary="Ownership accounting does not express responsibilities, dependencies, non-code checks, risks, or held-out probes.",
                distinguishingEvidence=["responsibilities", "verificationGaps", "heldOutProbes"],
            ),
        ],
        heldOutProbes=held_out_probes,
        verificationGaps=[
            ProjectModelV0VerificationGap(
                id=_identifier(gap.id, "verification_gap"),
                severity=gap.severity,
                description="; ".join(gap.evidence),
                affectedComponentIds=[component_id_map.get(gap.component_id, _identifier(gap.component_id, "component"))],
                proposedClosureCheck=gap.proposed_check,
            )
            for gap in model.verification_gaps
        ],
        unclassifiedProjectSurface=unclassified_surface,
        advisorySignalHandoff=AdvisorySignalHandoff(
            consumer="elenchus-core",
            expectedFields=[
                "componentAlignment",
                "invariantViolations",
                "dependencyViolations",
                "unsupportedAssumptions",
                "evidenceGroundingGaps",
                "nearNeighborResistance",
                "fLabelHint",
            ],
            optionalFLabelHint=True,
        ),
    )


def validate_project_model_v0(model: ProjectModelV0 | BaseModel | dict[str, Any]) -> QualityGateReport:
    return evaluate_quality_gate(model)


def canonical_project_model_v0_json(model: ProjectModelV0) -> str:
    payload = model.model_dump(mode="json", exclude_none=True)
    return json.dumps(payload, sort_keys=True, indent=2, separators=(",", ": ")) + "\n"


def validate_project_model(model: ProjectModel) -> DecompositionValidationReport:
    errors: list[str] = []
    warnings: list[str] = []

    included_paths = {record.path for record in model.file_inventory.included_files}
    excluded_paths = {record.path for record in model.file_inventory.excluded_files}
    all_paths = included_paths | excluded_paths
    component_ids = {component.id for component in model.components}
    gap_ids = {gap.id for gap in model.verification_gaps}

    for record in model.file_inventory.included_files:
        if record.excluded:
            errors.append(f"included file {record.path} is marked excluded")
        if record.missing_on_disk:
            errors.append(f"included file {record.path} is missing on disk")
        if record.sha256 is None:
            errors.append(f"included file {record.path} has no sha256")
    for record in model.file_inventory.excluded_files:
        if not record.excluded:
            errors.append(f"excluded file {record.path} is not marked excluded")
        if not (record.reason or "").strip():
            errors.append(f"excluded file {record.path} has empty reason")

    owners: dict[str, list[str]] = {path: [] for path in included_paths}
    for component in model.components:
        if not component.owned_files:
            errors.append(f"component {component.id} has no owned files")
        for path in component.owned_files:
            if path not in included_paths:
                errors.append(f"component {component.id} owns non-included file {path}")
            else:
                owners[path].append(component.id)
        if not component.checks and not component.verification_gaps:
            errors.append(f"component {component.id} has neither checks nor verification gaps")
        for check in component.checks:
            _validate_check_references(errors, check, included_paths, f"component {component.id}")
        for gap_id in component.verification_gaps:
            if gap_id not in gap_ids:
                errors.append(f"component {component.id} references missing verification gap {gap_id}")
        for template in component.fingerprint_templates:
            for path in template.target_files:
                if path not in included_paths:
                    errors.append(f"fingerprint template {template.id} references missing file {path}")
        for boundary in component.rollback_boundaries:
            if not boundary.stop_condition.strip():
                errors.append(f"rollback boundary {boundary.id} has empty stop_condition")
            for path in boundary.files:
                if path not in all_paths:
                    errors.append(f"rollback boundary {boundary.id} references missing file {path}")

    for path, component_owners in sorted(owners.items()):
        if len(component_owners) == 0:
            errors.append(f"included file {path} is unowned")
        elif len(component_owners) > 1:
            errors.append(
                f"included file {path} has multiple owners: {', '.join(sorted(component_owners))}"
            )

    for contract in model.contracts:
        if contract.producer_component_id not in component_ids:
            errors.append(
                f"contract {contract.id} references missing producer component {contract.producer_component_id}"
            )
        if contract.consumer_component_id not in component_ids:
            errors.append(
                f"contract {contract.id} references missing consumer component {contract.consumer_component_id}"
            )
        if not contract.checks and not contract.verification_gaps:
            errors.append(f"contract {contract.id} has neither checks nor verification gaps")
        for check in contract.checks:
            _validate_check_references(errors, check, included_paths, f"contract {contract.id}")
        for gap_id in contract.verification_gaps:
            if gap_id not in gap_ids:
                errors.append(f"contract {contract.id} references missing verification gap {gap_id}")

    for gap in model.verification_gaps:
        if gap.component_id not in component_ids:
            errors.append(f"verification gap {gap.id} references missing component {gap.component_id}")
        if not gap.evidence:
            errors.append(f"verification gap {gap.id} has no evidence")
        if not gap.proposed_check.strip():
            errors.append(f"verification gap {gap.id} has empty proposed_check")

    for concern in model.cross_cutting_concerns:
        for component_id in concern.affected_components:
            if component_id not in component_ids:
                errors.append(
                    f"cross-cutting concern {concern.id} references missing component {component_id}"
                )
        for check in concern.checks:
            _validate_check_references(errors, check, included_paths, f"cross-cutting concern {concern.id}")
        for gap_id in concern.verification_gaps:
            if gap_id not in gap_ids:
                errors.append(f"cross-cutting concern {concern.id} references missing verification gap {gap_id}")

    recomputed = _build_coverage(model.file_inventory, model.components)
    if recomputed != model.coverage:
        errors.append("coverage report is stale")
    if model.coverage.coverage_numerator != model.coverage.coverage_denominator:
        errors.append("source coverage is incomplete")

    if model.git.dirty:
        warnings.append("git tree was dirty; hashes reflect disk contents, not necessarily HEAD blobs")
    if model.git.inventory_mode == "filesystem":
        warnings.append("filesystem fallback inventory was used")
    if "documentation_and_operator_guidance" in component_ids and not any(
        component.id == "documentation_and_operator_guidance" and component.checks
        for component in model.components
    ):
        warnings.append("documentation component has no mechanical drift check")

    return DecompositionValidationReport(
        valid=not errors,
        errors=errors,
        warnings=warnings,
        gap_count=len(model.verification_gaps),
    )


def canonical_project_model_json(model: ProjectModel) -> str:
    payload = model.model_dump(mode="json")
    return json.dumps(payload, sort_keys=True, indent=2, separators=(",", ": ")) + "\n"


def _identifier(value: str, fallback: str) -> str:
    raw = re.sub(r"[^a-z0-9_-]+", "_", value.strip().lower())
    raw = re.sub(r"_+", "_", raw).strip("_-")
    if not raw:
        raw = fallback
    if not raw[0].isalpha():
        raw = f"{fallback}_{raw}"
    return raw


def _unique_identifier(value: str, used: set[str], fallback: str) -> str:
    base = _identifier(value, fallback)
    candidate = base
    suffix = 2
    while candidate in used:
        candidate = f"{base}_{suffix}"
        suffix += 1
    used.add(candidate)
    return candidate


def _component_id_map(components: list[Component]) -> dict[str, str]:
    used: set[str] = set()
    return {
        component.id: _unique_identifier(component.id, used, "component")
        for component in components
    }


def _component_kind_for_v0(component: Component) -> ComponentKind:
    if component.kind in {
        "source",
        "test",
        "documentation",
        "configuration",
        "spec",
        "process",
        "architecture",
        "strategy",
        "data",
        "integration",
        "operations",
        "fixture",
        "unknown",
    }:
        return cast(ComponentKind, component.kind)
    if component.kind == "verification":
        return "test"
    if component.kind == "artifact":
        return "data"
    return "unknown"


def _component_risk_level(component: Component, gaps: list[VerificationGap]) -> Severity:
    severities = {gap.severity for gap in gaps}
    if "high" in severities:
        return "high"
    if "medium" in severities or component.kind == "unknown":
        return "medium"
    return "low"


def _observable_mode_for_check(check: MechanicalCheck) -> ObservableCheckMode:
    command = check.command.lower()
    if "pytest" in command:
        return "test"
    if any(token in command for token in ("compileall", "ruff", "pyright", "mypy")):
        return "static-analysis"
    if "dry-run" in command or "exercise_verifier" in command:
        return "simulation"
    return "inspection"


def _check_evidence_requirements(check: MechanicalCheck) -> list[str]:
    evidence = [f"terminal output for `{check.command}`"]
    evidence.extend(f"referenced path exists: {path}" for path in check.referenced_paths)
    return evidence


def _dependencies_for_v0(
    model: ProjectModel,
    component_id_map: dict[str, str],
    component_check_ids: dict[str, list[str]],
) -> list[Dependency]:
    dependencies: list[Dependency] = []
    used_ids: set[str] = set()
    for contract in model.contracts:
        if (
            contract.producer_component_id not in component_id_map
            or contract.consumer_component_id not in component_id_map
        ):
            continue
        observable_ids = sorted(
            set(component_check_ids.get(contract.producer_component_id, []))
            | set(component_check_ids.get(contract.consumer_component_id, []))
        )
        dependencies.append(
            Dependency(
                id=_unique_identifier(contract.id, used_ids, "dependency"),
                fromComponent=component_id_map[contract.producer_component_id],
                toComponent=component_id_map[contract.consumer_component_id],
                kind="feeds",
                description=_contract_description(contract),
                observableCheckIds=observable_ids,
            )
        )
    if dependencies or len(model.components) <= 1:
        return dependencies
    return _default_dependencies_for_v0(model.components, component_id_map, component_check_ids, used_ids)


def _default_dependencies_for_v0(
    components: list[Component],
    component_id_map: dict[str, str],
    component_check_ids: dict[str, list[str]],
    used_ids: set[str],
) -> list[Dependency]:
    dependencies: list[Dependency] = []

    def add(raw_id: str, source: str, target: str, kind: DependencyKind, description: str) -> None:
        if source not in component_id_map or target not in component_id_map or source == target:
            return
        dependencies.append(
            Dependency(
                id=_unique_identifier(raw_id, used_ids, "dependency"),
                fromComponent=component_id_map[source],
                toComponent=component_id_map[target],
                kind=kind,
                description=description,
                observableCheckIds=sorted(
                    set(component_check_ids.get(source, [])) | set(component_check_ids.get(target, []))
                ),
            )
        )

    add(
        "python_package_feeds_regression_tests",
        "python_package",
        "regression_tests",
        "feeds",
        "The source package is the behavior surface exercised by regression tests.",
    )
    for component in components:
        if component.id != "project_configuration":
            add(
                f"project_configuration_informs_{component.id}",
                "project_configuration",
                component.id,
                "informs",
                "Project configuration constrains how this component is installed, tested, or linted.",
            )
    if not dependencies:
        ordered = sorted(component.id for component in components)
        add(
            f"{ordered[0]}_informs_{ordered[1]}",
            ordered[0],
            ordered[1],
            "informs",
            "Filesystem-derived decomposition exposes at least one sequencing or information dependency for downstream review.",
        )
    return dependencies


def _contract_description(contract: Contract) -> str:
    assumes = "; ".join(contract.assumes) if contract.assumes else "no explicit assumptions"
    guarantees = "; ".join(contract.guarantees) if contract.guarantees else "no explicit guarantees"
    return f"Assumes: {assumes}. Guarantees: {guarantees}."


def _invariants_for_v0(
    model: ProjectModel,
    component_id_map: dict[str, str],
    component_check_ids: dict[str, list[str]],
) -> list[Invariant]:
    invariants: list[Invariant] = []
    used_ids: set[str] = set()
    for concern in model.cross_cutting_concerns:
        component_ids = [
            component_id_map[component_id]
            for component_id in concern.affected_components
            if component_id in component_id_map
        ]
        if not component_ids:
            continue
        check_ids = sorted(
            {
                check_id
                for component_id in concern.affected_components
                for check_id in component_check_ids.get(component_id, [])
            }
        )
        invariants.append(
            Invariant(
                id=_unique_identifier(concern.id, used_ids, "invariant"),
                description=concern.description,
                componentIds=sorted(component_ids),
                observableCheckIds=check_ids,
            )
        )
    all_component_ids = sorted(component_id_map.values())
    all_check_ids = sorted({check_id for ids in component_check_ids.values() for check_id in ids})
    invariants.append(
        Invariant(
            id=_unique_identifier("no_live_api_required", used_ids, "invariant"),
            description="Project Model emission and validation must not require live paid LLM/API calls.",
            componentIds=all_component_ids,
            observableCheckIds=all_check_ids,
        )
    )
    return invariants


def _evidence_requirements_for_v0(
    model: ProjectModel,
    component_id_map: dict[str, str],
) -> list[EvidenceRequirement]:
    requirements = [
        EvidenceRequirement(
            id="canonical_project_model_json",
            description="Canonical Project Model v0 JSON emitted by arena.decomposer before planning begins.",
            acceptedArtifactTypes=["project-model-v0-json", "terminal-output", "file-path"],
            requiredFor=sorted(component_id_map.values()),
        )
    ]
    if model.verification_gaps:
        requirements.append(
            EvidenceRequirement(
                id="verification_gap_evidence",
                description="Evidence and proposed closure checks for every surfaced verification gap.",
                acceptedArtifactTypes=["project-model-v0-json", "file-path", "terminal-output", "review-note"],
                requiredFor=sorted(_identifier(gap.id, "verification_gap") for gap in model.verification_gaps),
            )
        )
    return requirements


def _risks_for_v0(model: ProjectModel, component_id_map: dict[str, str]) -> list[Risk]:
    risks = [
        Risk(
            id="wrong_target_planning",
            level="medium",
            description="A downstream agent could start coherent work against the wrong component, sequence, or visible example if the Project Model is skipped.",
            mitigation="Emit Project Model v0 before planning and consume its components, dependencies, checks, and gaps.",
        )
    ]
    used_ids = {"wrong_target_planning"}
    for gap in model.verification_gaps:
        payload: dict[str, Any] = {
            "id": _unique_identifier(f"{gap.id}_risk", used_ids, "risk"),
            "level": gap.severity,
            "description": "; ".join(gap.evidence),
            "mitigation": gap.proposed_check,
        }
        if gap.component_id in component_id_map:
            payload["componentId"] = component_id_map[gap.component_id]
        risks.append(Risk(**payload))
    return risks


def _held_out_probes_for_v0(
    model: ProjectModel,
    component_id_map: dict[str, str],
    gaps_by_component: dict[str, list[VerificationGap]],
) -> list[HeldOutProbe]:
    probes: list[HeldOutProbe] = []
    used_ids: set[str] = set()
    for component in model.components:
        if _component_risk_level(component, gaps_by_component.get(component.id, [])) != "high":
            continue
        component_id = component_id_map[component.id]
        gap_ids = [gap.id for gap in gaps_by_component.get(component.id, [])]
        probes.append(
            HeldOutProbe(
                id=_unique_identifier(f"{component_id}_wrong_target_probe", used_ids, "held_out_probe"),
                componentId=component_id,
                probeType="counterexample",
                scenario="A downstream proposal passes visible mechanical checks while treating the surfaced high-risk gap as already solved.",
                expectedBehavior="The Project Model keeps the gap visible and requires the proposed closure check before downstream acceptance.",
                evidenceRequired=gap_ids or [component_id],
            )
        )
    return probes


def _unclassified_surface_for_v0(
    model: ProjectModel,
    component_id_map: dict[str, str],
) -> list[UnclassifiedProjectSurface]:
    unclassified: list[UnclassifiedProjectSurface] = []
    used_ids: set[str] = set()
    candidate_owners = sorted(
        component_id
        for original_id, component_id in component_id_map.items()
        if original_id != "unclassified_project_surface"
    )
    for component in model.components:
        if component.id != "unclassified_project_surface":
            continue
        for path in component.owned_files:
            unclassified.append(
                UnclassifiedProjectSurface(
                    id=_unique_identifier(f"unclassified_{path}", used_ids, "unclassified_surface"),
                    description=f"{path} is included in the project inventory but not assigned to a project-specific responsibility boundary.",
                    reasonUnclassified="The deterministic scanner could not infer a more specific owner from path or file type.",
                    candidateOwners=candidate_owners[:3],
                )
            )
    return unclassified


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Emit a Build Arena project decomposition model.")
    parser.add_argument("--project", required=True, help="Project path to scan")
    parser.add_argument("--output", default="-", help="Output JSON path, or '-' for stdout")
    parser.add_argument("--project-id", default=None, help="Override project_id")
    parser.add_argument(
        "--format",
        choices=["scanner-v0.1", "project-model-v0"],
        default="scanner-v0.1",
        help="Output the internal scanner model or the shared Project Model v0 contract",
    )
    parser.add_argument("--source-task", default=None, help="Primary task text for Project Model v0")
    parser.add_argument(
        "--primary-backlog-item",
        default=None,
        help="Primary backlog item or issue URL for Project Model v0",
    )
    parser.add_argument("--repo", default=None, help="Optional repo identity for Project Model v0 source")
    parser.add_argument("--issue", default=None, help="Optional issue URL/id for Project Model v0 source")
    parser.add_argument("--fail-on-gap", action="store_true", help="Exit non-zero if verification gaps exist")
    args = parser.parse_args(argv)

    if args.format == "project-model-v0" and (
        not (args.source_task or "").strip() or not (args.primary_backlog_item or "").strip()
    ):
        print(
            "decomposer error: --source-task and --primary-backlog-item are required for --format project-model-v0",
            file=sys.stderr,
        )
        return 2

    try:
        if args.format == "project-model-v0":
            v0_model = decompose_project_model_v0(
                Path(args.project),
                source_task=args.source_task,
                primary_backlog_item=args.primary_backlog_item,
                project_id=args.project_id,
                repo=args.repo,
                issue=args.issue,
            )
            output = canonical_project_model_v0_json(v0_model)
            report = validate_project_model_v0(v0_model)
            gap_count = len(v0_model.verificationGaps)
        else:
            scanner_model = decompose_project(Path(args.project), project_id=args.project_id)
            output = canonical_project_model_json(scanner_model)
            scanner_report = validate_project_model(scanner_model)
            report = scanner_report
            gap_count = scanner_report.gap_count
    except Exception as exc:  # pragma: no cover - CLI guard
        print(f"decomposer error: {exc}", file=sys.stderr)
        return 2

    if args.output == "-":
        sys.stdout.write(output)
    else:
        Path(args.output).write_text(output, encoding="utf-8")

    if isinstance(report, QualityGateReport):
        if not report.passed:
            print("project model v0 quality gate failed", file=sys.stderr)
            for finding in report.findings:
                print(f"- {finding.code}: {finding.location}: {finding.message}", file=sys.stderr)
            return 2
    elif not report.valid:
        print("decomposition model is invalid", file=sys.stderr)
        for error in report.errors:
            print(f"- {error}", file=sys.stderr)
        return 2
    if args.fail_on_gap and gap_count > 0:
        noun = "Project Model v0" if args.format == "project-model-v0" else "decomposition model"
        print(f"{noun} has {gap_count} verification gap(s)", file=sys.stderr)
        return 3
    return 0


def _validate_check_references(
    errors: list[str],
    check: MechanicalCheck,
    included_paths: set[str],
    owner_label: str,
) -> None:
    for path in check.referenced_paths:
        if path not in included_paths:
            errors.append(f"{owner_label} check {check.id} references missing path {path}")


def _scan_project(project_path: Path) -> _ScanResult:
    requested = project_path.resolve()
    if not requested.exists():
        raise FileNotFoundError(f"project path does not exist: {requested}")
    if not requested.is_dir():
        raise NotADirectoryError(f"project path is not a directory: {requested}")

    git_root = _git_toplevel(requested)
    if git_root is not None:
        root = git_root
        tracked = _git_output(root, ["ls-files", "-z"])
        tracked_paths = sorted(path for path in tracked.split("\0") if path)
        untracked_raw = _git_output(root, ["ls-files", "--others", "--exclude-standard", "-z"])
        untracked_paths = sorted(path for path in untracked_raw.split("\0") if path)
        dirty_paths = _git_dirty_paths(root)
        git_state = GitState(
            available=True,
            inventory_mode="git",
            toplevel=str(root),
            head_oid=_git_optional_output(root, ["rev-parse", "HEAD"]),
            branch=_git_optional_output(root, ["branch", "--show-current"]) or None,
            dirty=bool(dirty_paths),
            dirty_paths=dirty_paths,
            untracked_paths=untracked_paths,
        )
        inventory = _inventory_from_paths(root, tracked_paths, include_exclusions=True)
        return _ScanResult(root=root, git=git_state, inventory=inventory)

    root = requested
    paths = sorted(_filesystem_paths(root))
    git_state = GitState(available=False, inventory_mode="filesystem")
    inventory = _inventory_from_paths(root, paths, include_exclusions=True)
    return _ScanResult(root=root, git=git_state, inventory=inventory)


def _git_toplevel(path: Path) -> Path | None:
    try:
        proc = subprocess.run(
            ["git", "-C", str(path), "rev-parse", "--show-toplevel"],
            text=True,
            capture_output=True,
            check=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None
    return Path(proc.stdout.strip()).resolve()


def _git_output(root: Path, args: list[str]) -> str:
    proc = subprocess.run(
        ["git", "-C", str(root), *args],
        text=True,
        capture_output=True,
        check=True,
    )
    return proc.stdout


def _git_optional_output(root: Path, args: list[str]) -> str | None:
    try:
        return _git_output(root, args).strip() or None
    except subprocess.CalledProcessError:
        return None


def _git_dirty_paths(root: Path) -> list[str]:
    try:
        status = _git_output(root, ["status", "--porcelain=v1"])
    except subprocess.CalledProcessError:
        return []
    paths: set[str] = set()
    for line in status.splitlines():
        if not line:
            continue
        if line.startswith("??"):
            continue
        raw_path = line[3:]
        if " -> " in raw_path:
            old, new = raw_path.split(" -> ", 1)
            paths.add(old.strip())
            paths.add(new.strip())
        else:
            paths.add(raw_path.strip())
    return sorted(path for path in paths if path)


def _filesystem_paths(root: Path) -> list[str]:
    result: list[str] = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        rel = _to_posix(path.relative_to(root))
        result.append(rel)
    return result


def _inventory_from_paths(root: Path, paths: list[str], *, include_exclusions: bool) -> FileInventory:
    included: list[FileRecord] = []
    excluded: list[FileRecord] = []
    for rel in sorted(paths):
        reason = _exclusion_reason(rel)
        abs_path = root / rel
        if reason is not None:
            if include_exclusions:
                excluded.append(
                    FileRecord(
                        path=rel,
                        sha256=None,
                        kind=_classify_file(rel),
                        excluded=True,
                        reason=reason,
                        missing_on_disk=not abs_path.exists(),
                    )
                )
            continue
        included.append(
            FileRecord(
                path=rel,
                sha256=_sha256_file(abs_path) if abs_path.is_file() else None,
                kind=_classify_file(rel),
                missing_on_disk=not abs_path.exists(),
            )
        )
    return FileInventory(included_files=included, excluded_files=excluded)


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _to_posix(path: Path) -> str:
    return path.as_posix()


def _exclusion_reason(path: str) -> str | None:
    parts = path.split("/")
    suffix = Path(path).suffix.lower()
    if any(part in {".git", ".hg", ".svn"} for part in parts):
        return "vcs_metadata"
    if any(part in {".venv", "venv", "node_modules"} for part in parts):
        return "dependency_environment"
    if any(part in {"__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", ".coverage", "htmlcov"} for part in parts):
        return "tool_cache"
    if any(part.endswith(".egg-info") for part in parts):
        return "build_metadata"
    if parts[0] in {"build", "dist", "results", ".tox", ".nox"}:
        return "generated_or_runtime_artifact"
    if suffix in {".pyc", ".pyo", ".sqlite", ".sqlite3", ".db", ".log", ".tmp", ".swp", ".bak"}:
        return "generated_or_runtime_artifact"
    if suffix in {".tar", ".tgz", ".zip", ".7z"}:
        return "archive_artifact"
    return None


def _classify_file(path: str) -> str:
    suffix = Path(path).suffix.lower()
    name = Path(path).name
    if path.startswith("tests/"):
        return "test"
    if path.startswith("fixtures/"):
        return "fixture"
    if path.startswith("docs/") or suffix in {".md", ".rst"}:
        return "documentation"
    if suffix == ".py":
        return "source"
    if name in {"pyproject.toml", "uv.lock", "poetry.lock", "requirements.txt", ".gitignore"}:
        return "configuration"
    if suffix in {".toml", ".yaml", ".yml", ".json", ".ini", ".cfg"}:
        return "configuration"
    if suffix in {".diff", ".patch", ".txt"}:
        return "artifact"
    return "resource"


def _looks_like_arena_calibration(paths: set[str]) -> bool:
    required = {
        "arena/fixtures.py",
        "arena/scorer.py",
        "arena/verifier.py",
        "arena/runner.py",
    }
    return required <= paths and any(
        path.startswith("fixtures/") and path.endswith("/manifest.yaml") for path in paths
    )


def _arena_calibration_decomposition(
    root: Path,
    included_paths: set[str],
) -> tuple[list[Component], list[Contract], list[CrossCuttingConcern], list[VerificationGap]]:
    assignments: dict[str, list[str]] = defaultdict(list)
    provider_tests = {
        "tests/test_api_llm.py",
        "tests/test_cli_llm.py",
        "tests/test_runner_api_provider.py",
        "tests/test_runner_cli_provider.py",
    }

    for path in sorted(included_paths):
        component_id = _arena_component_for_path(path, provider_tests)
        assignments[component_id].append(path)

    gaps = _derive_arena_gaps(root, included_paths)
    if "documentation_and_operator_guidance" in assignments:
        gaps.append(
            VerificationGap(
                id="doc_spec_drift_check_missing",
                component_id="documentation_and_operator_guidance",
                severity="medium",
                evidence=["docs are covered as operator guidance but no doc/spec drift checker exists yet"],
                proposed_check="add a mechanical documentation/spec drift check once the goal schema stabilizes",
            )
        )
    if "unclassified_project_surface" in assignments:
        gaps.append(
            VerificationGap(
                id="unclassified_project_surface_gap",
                component_id="unclassified_project_surface",
                severity="medium",
                evidence=sorted(assignments["unclassified_project_surface"]),
                proposed_check="classify these files into a named component with an explicit mechanical check",
            )
        )

    gap_ids_by_component: dict[str, list[str]] = defaultdict(list)
    for gap in gaps:
        gap_ids_by_component[gap.component_id].append(gap.id)

    components: list[Component] = []
    for component_id, files in sorted(assignments.items()):
        components.append(_arena_component(component_id, sorted(files), sorted(gap_ids_by_component[component_id])))

    component_ids = {component.id for component in components}
    contracts = _arena_contracts(component_ids, sorted(included_paths))
    concerns = _arena_cross_cutting_concerns(component_ids)
    return components, contracts, concerns, gaps


def _arena_component_for_path(path: str, provider_tests: set[str]) -> str:
    if path == "arena/fixtures.py" or path.startswith("fixtures/"):
        return "fixture_manifest_model"
    if path == "arena/scorer.py":
        return "mechanical_scorer"
    if path in {"arena/verifier.py", "arena/lanham.py", "arena/patch_eq.py"}:
        return "reasoning_ablation_verifier"
    if path in {"arena/llm.py", "arena/api_llm.py", "arena/cli_llm.py"} or path in provider_tests:
        return "provider_boundary"
    if path in {"arena/runner.py", "exercise_verifier.py"}:
        return "runner_discrimination_matrix"
    if path.startswith("tests/"):
        return "regression_tests"
    if path.startswith("docs/") or path == "README.md":
        return "documentation_and_operator_guidance"
    if path in {"pyproject.toml", "uv.lock", ".gitignore"} or path.startswith("arena_calibration.egg-info/"):
        return "project_configuration"
    if path == "arena/__init__.py":
        return "package_marker"
    return "unclassified_project_surface"


def _arena_component(component_id: str, files: list[str], gap_ids: list[str]) -> Component:
    check = _arena_component_check(component_id, files)
    checks = [check] if check is not None else []
    return Component(
        id=component_id,
        name=component_id.replace("_", " ").title(),
        kind=_arena_component_kind(component_id),
        owned_files=files,
        responsibilities=[_arena_component_responsibility(component_id)],
        checks=checks,
        scoring_dimensions=[
            ScoringDimension(
                id=f"{component_id}_mechanical_signal",
                description=f"Mechanical health signal for {component_id}",
                mechanical_signal=check.command if check is not None else "verification gap only",
            )
        ],
        fingerprint_templates=[_fingerprint_for_component(component_id, files)],
        rollback_boundaries=[_rollback_for_component(component_id, files)],
        scope_boundaries=[_scope_for_component(component_id, files)],
        verification_gaps=gap_ids,
    )


def _arena_component_kind(component_id: str) -> str:
    if component_id in {"regression_tests", "runner_discrimination_matrix"}:
        return "verification"
    if component_id in {"fixture_manifest_model"}:
        return "fixture"
    if component_id in {"documentation_and_operator_guidance"}:
        return "documentation"
    if component_id in {"project_configuration", "package_marker"}:
        return "configuration"
    return "source"


def _arena_component_responsibility(component_id: str) -> str:
    descriptions = {
        "fixture_manifest_model": "Load and preserve calibration fixture ground truth from manifests and fixture artifacts.",
        "mechanical_scorer": "Run tier-1 measurements and emit deterministic promote/reject score reports.",
        "reasoning_ablation_verifier": "Run Lanham-style reasoning ablation and AST-normalized patch comparison.",
        "provider_boundary": "Isolate live/API/CLI model providers from verifier and runner logic.",
        "runner_discrimination_matrix": "Drive scorer/verifier execution and emit dry-run/live discrimination matrices.",
        "regression_tests": "Preserve local regression coverage for the calibration harness.",
        "documentation_and_operator_guidance": "Document operator-facing usage, plans, verification reviews, and project rationale.",
        "project_configuration": "Define package, dependency, pytest, and tool configuration surfaces.",
        "package_marker": "Expose the package namespace for imports.",
        "unclassified_project_surface": "Explicitly hold files that the decomposer could not yet classify.",
    }
    return descriptions.get(component_id, f"Maintain {component_id}.")


def _arena_component_check(component_id: str, files: list[str]) -> MechanicalCheck | None:
    refs = set(files)
    if component_id == "fixture_manifest_model":
        refs.update(path for path in files if path.endswith("manifest.yaml"))
        return MechanicalCheck(
            id="fixture_loader_regression_tests",
            command="uv run pytest -q",
            description="Regression tests cover fixture loading and manifest shape.",
            referenced_paths=sorted(refs),
        )
    if component_id == "mechanical_scorer":
        return MechanicalCheck(
            id="scorer_regression_tests",
            command="uv run pytest -q",
            description="Regression tests exercise scorer measurement and verdict semantics.",
            referenced_paths=sorted(refs),
        )
    if component_id == "reasoning_ablation_verifier":
        return MechanicalCheck(
            id="hermetic_verifier_exercise",
            command="uv run python exercise_verifier.py",
            description="Hermetic scripted-worker verifier exercise.",
            referenced_paths=sorted(refs | {"exercise_verifier.py"}),
        )
    if component_id == "provider_boundary":
        test_refs = [path for path in files if path.startswith("tests/")]
        command = "uv run pytest " + " ".join(test_refs) + " -q" if test_refs else "uv run pytest -q"
        return MechanicalCheck(
            id="provider_boundary_unit_tests",
            command=command,
            description="Provider wrappers are checked without live spend by unit tests/dry-run seams.",
            referenced_paths=sorted(refs),
        )
    if component_id == "runner_discrimination_matrix":
        return MechanicalCheck(
            id="runner_dry_run_plan",
            command="uv run python -m arena.runner --dry-run --llm-provider xai",
            description="Dry-run computes model-call plan without live model execution.",
            referenced_paths=sorted(refs),
        )
    if component_id == "regression_tests":
        return MechanicalCheck(
            id="full_regression_tests",
            command="uv run pytest -q",
            description="Project regression suite.",
            referenced_paths=sorted(refs),
        )
    if component_id == "project_configuration":
        return MechanicalCheck(
            id="project_tooling_regression",
            command="uv run pytest -q",
            description="Tooling config is exercised by the test suite.",
            referenced_paths=sorted(refs),
        )
    if component_id == "package_marker":
        return MechanicalCheck(
            id="package_import_regression",
            command="uv run pytest -q",
            description="Import/package marker is exercised by test imports.",
            referenced_paths=sorted(refs),
        )
    return None


def _derive_arena_gaps(root: Path, included_paths: set[str]) -> list[VerificationGap]:
    evidence: list[str] = []
    for path in sorted(included_paths):
        if not (path.startswith("fixtures/") and path.endswith("/manifest.yaml")):
            continue
        raw = yaml.safe_load((root / path).read_text(encoding="utf-8")) or {}
        ground_truth = raw.get("ground_truth", {})
        scorer_should = str(ground_truth.get("scorer_should", "")).lower()
        verifier_should = str(ground_truth.get("verifier_should", "")).lower()
        rationale = str(ground_truth.get("rationale", ""))
        rationale_lower = rationale.lower()
        kind = str(raw.get("kind", "")).lower()
        if scorer_should == "promote" and verifier_should == "reject" and kind == "bad_passes_tests" and any(
            token in rationale_lower for token in ("lanham", "hardcod", "generaliz", "lookup")
        ):
            fixture_id = str(raw.get("id", Path(path).parent.name))
            evidence.append(f"{path}: {fixture_id}: {rationale.strip()}")
    if not evidence:
        return []
    return [
        VerificationGap(
            id="patch_generalization_axis_missing",
            component_id="reasoning_ablation_verifier",
            severity="high",
            evidence=evidence,
            proposed_check="add a patch-generalization verifier axis that rejects hardcoded or non-generalizing patches before promotion",
        )
    ]


def _arena_contracts(component_ids: set[str], included_paths: list[str]) -> list[Contract]:
    contracts: list[Contract] = []

    def has(*paths: str) -> list[str]:
        present = set(included_paths)
        return [path for path in paths if path in present]

    def add(
        id: str,
        producer: str,
        consumer: str,
        assumes: list[str],
        guarantees: list[str],
        command: str,
        referenced_paths: list[str],
    ) -> None:
        if producer not in component_ids or consumer not in component_ids:
            return
        contracts.append(
            Contract(
                id=id,
                producer_component_id=producer,
                consumer_component_id=consumer,
                assumes=assumes,
                guarantees=guarantees,
                checks=[
                    MechanicalCheck(
                        id=f"{id}_check",
                        command=command,
                        description=f"Mechanical check for {id}",
                        referenced_paths=referenced_paths,
                    )
                ],
            )
        )

    add(
        "fixture_manifest_to_scorer",
        "fixture_manifest_model",
        "mechanical_scorer",
        ["fixtures expose measurement commands and expected fail counts"],
        ["scorer emits observed fail counts and promote/reject verdicts"],
        "uv run pytest -q",
        has("arena/fixtures.py", "arena/scorer.py"),
    )
    add(
        "scorer_to_runner",
        "mechanical_scorer",
        "runner_discrimination_matrix",
        ["scorer verdicts are deterministic and fixture integrity is independent"],
        ["runner short-circuits verifier on scorer reject and records rows"],
        "uv run python -m arena.runner --dry-run --llm-provider xai",
        has("arena/scorer.py", "arena/runner.py"),
    )
    add(
        "verifier_to_runner",
        "reasoning_ablation_verifier",
        "runner_discrimination_matrix",
        ["verifier emits per-component load-bearing verdicts"],
        ["runner records verifier verdicts and threshold sweep"],
        "uv run python exercise_verifier.py",
        has("arena/verifier.py", "exercise_verifier.py"),
    )
    add(
        "provider_boundary_to_verifier",
        "provider_boundary",
        "reasoning_ablation_verifier",
        ["worker and judge satisfy stable protocols without provider leakage"],
        ["verifier can consume worker/judge implementations through protocol seams"],
        "uv run pytest -q",
        has("arena/llm.py", "arena/api_llm.py", "arena/cli_llm.py", "arena/verifier.py"),
    )
    return contracts


def _arena_cross_cutting_concerns(component_ids: set[str]) -> list[CrossCuttingConcern]:
    ids = sorted(component_ids)
    concerns = [
        CrossCuttingConcern(
            id="deterministic_execution",
            description="Scanner, scorer, verifier, and runner outputs must be reproducible from filesystem/git state.",
            affected_components=ids,
            checks=[MechanicalCheck(id="regression_suite", command="uv run pytest -q")],
        ),
    ]
    if "provider_boundary" in component_ids:
        concerns.append(
            CrossCuttingConcern(
                id="no_live_spend_by_default",
                description="Provider components must expose dry-run/unit-test paths that avoid live API spend unless explicitly confirmed.",
                affected_components=["provider_boundary", "runner_discrimination_matrix"],
                checks=[
                    MechanicalCheck(
                        id="runner_dry_run_no_live_calls",
                        command="uv run python -m arena.runner --dry-run --llm-provider xai",
                        referenced_paths=["arena/runner.py"],
                    )
                ],
            )
        )
    return concerns


def _generic_decomposition(
    included_paths: set[str],
) -> tuple[list[Component], list[Contract], list[CrossCuttingConcern], list[VerificationGap]]:
    assignments: dict[str, list[str]] = defaultdict(list)
    for path in sorted(included_paths):
        assignments[_generic_component_for_path(path)].append(path)

    gaps: list[VerificationGap] = []
    if "documentation_and_operator_guidance" in assignments:
        gaps.append(
            VerificationGap(
                id="doc_spec_drift_check_missing",
                component_id="documentation_and_operator_guidance",
                severity="medium",
                evidence=["documentation files exist but no mechanical doc/spec drift check is derivable from the filesystem scan"],
                proposed_check="add a project-specific doc/spec drift checker or explicit acceptance fixture",
            )
        )
    if "unclassified_project_surface" in assignments:
        gaps.append(
            VerificationGap(
                id="unclassified_project_surface_gap",
                component_id="unclassified_project_surface",
                severity="medium",
                evidence=sorted(assignments["unclassified_project_surface"]),
                proposed_check="classify these files into project-specific components with mechanical checks",
            )
        )

    gap_ids_by_component: dict[str, list[str]] = defaultdict(list)
    for gap in gaps:
        gap_ids_by_component[gap.component_id].append(gap.id)

    components = [
        _generic_component(component_id, sorted(files), sorted(gap_ids_by_component[component_id]))
        for component_id, files in sorted(assignments.items())
    ]
    concerns = [
        CrossCuttingConcern(
            id="source_coverage",
            description="Every included source/config/test/doc file is owned exactly once or the model is invalid.",
            affected_components=sorted(component.id for component in components),
        )
    ]
    return components, [], concerns, gaps


def _generic_component_for_path(path: str) -> str:
    if path.startswith("tests/"):
        return "regression_tests"
    if path.startswith("docs/") or Path(path).suffix.lower() in {".md", ".rst"}:
        return "documentation_and_operator_guidance"
    if path.endswith(".py"):
        return "python_package"
    if Path(path).name in {"pyproject.toml", "uv.lock", "poetry.lock", "requirements.txt", ".gitignore"}:
        return "project_configuration"
    return "unclassified_project_surface"


def _generic_component(component_id: str, files: list[str], gap_ids: list[str]) -> Component:
    refs = sorted(files)
    check: MechanicalCheck | None = None
    kind = "source"
    if component_id == "python_package":
        check = MechanicalCheck(
            id="python_compile_check",
            command="uv run python -m compileall .",
            description="Python source compiles.",
            referenced_paths=refs,
        )
    elif component_id == "regression_tests":
        kind = "test"
        check = MechanicalCheck(
            id="regression_tests",
            command="uv run pytest -q",
            description="Project regression tests.",
            referenced_paths=refs,
        )
    elif component_id == "project_configuration":
        kind = "configuration"
        check = MechanicalCheck(
            id="project_configuration_check",
            command="uv run pytest -q",
            description="Project configuration is exercised by normal tests/tooling.",
            referenced_paths=refs,
        )
    elif component_id == "documentation_and_operator_guidance":
        kind = "documentation"
    elif component_id == "unclassified_project_surface":
        kind = "unknown"

    checks = [check] if check is not None else []
    return Component(
        id=component_id,
        name=component_id.replace("_", " ").title(),
        kind=kind,
        owned_files=files,
        responsibilities=[f"Maintain {component_id.replace('_', ' ')}."],
        checks=checks,
        scoring_dimensions=[
            ScoringDimension(
                id=f"{component_id}_signal",
                description=f"Mechanical or gap signal for {component_id}",
                mechanical_signal=check.command if check is not None else "verification gap only",
            )
        ],
        fingerprint_templates=[_fingerprint_for_component(component_id, files)],
        rollback_boundaries=[_rollback_for_component(component_id, files)],
        scope_boundaries=[_scope_for_component(component_id, files)],
        verification_gaps=gap_ids,
    )


def _fingerprint_for_component(component_id: str, files: list[str]) -> FingerprintTemplate:
    return FingerprintTemplate(
        id=f"{component_id}_improvement_template",
        intent=f"Improve {component_id} without expanding scope.",
        target_files=sorted(files),
        technique_tag=component_id,
        success_criterion="component mechanical check improves or remains green while target metric improves",
        failure_criterion="component check fails, scope boundary expands, or rollback condition triggers",
    )


def _rollback_for_component(component_id: str, files: list[str]) -> RollbackBoundary:
    return RollbackBoundary(
        id=f"{component_id}_rollback_boundary",
        stop_condition=f"rollback if checks for {component_id} fail or an edit touches files outside the component scope",
        files=sorted(files),
    )


def _scope_for_component(component_id: str, files: list[str]) -> ScopeBoundary:
    return ScopeBoundary(
        id=f"{component_id}_scope_boundary",
        in_scope=sorted(files),
        out_of_scope=["files owned by other components", "generated/runtime artifacts"],
    )


def _build_coverage(inventory: FileInventory, components: list[Component]) -> CoverageReport:
    included_paths = {record.path for record in inventory.included_files}
    owners: dict[str, list[str]] = {path: [] for path in included_paths}
    for component in components:
        for path in component.owned_files:
            if path in owners:
                owners[path].append(component.id)
    unowned = sorted(path for path, component_ids in owners.items() if len(component_ids) == 0)
    multiply_owned = {
        path: sorted(component_ids)
        for path, component_ids in sorted(owners.items())
        if len(component_ids) > 1
    }
    owned_once = sum(1 for component_ids in owners.values() if len(component_ids) == 1)
    denominator = len(included_paths)
    return CoverageReport(
        total_files=len(inventory.included_files) + len(inventory.excluded_files),
        included_files=len(inventory.included_files),
        excluded_files=len(inventory.excluded_files),
        owned_included_files=owned_once,
        coverage_numerator=owned_once,
        coverage_denominator=denominator,
        unowned_included_files=unowned,
        multiply_owned_included_files=multiply_owned,
    )


def _sort_components(components: list[Component]) -> list[Component]:
    sorted_components: list[Component] = []
    for component in sorted(components, key=lambda item: item.id):
        sorted_components.append(
            component.model_copy(
                update={
                    "owned_files": sorted(component.owned_files),
                    "checks": sorted(component.checks, key=lambda check: check.id),
                    "fingerprint_templates": sorted(
                        component.fingerprint_templates, key=lambda template: template.id
                    ),
                    "rollback_boundaries": sorted(
                        component.rollback_boundaries, key=lambda boundary: boundary.id
                    ),
                    "scope_boundaries": sorted(
                        component.scope_boundaries, key=lambda boundary: boundary.id
                    ),
                    "verification_gaps": sorted(component.verification_gaps),
                }
            )
        )
    return sorted_components


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
