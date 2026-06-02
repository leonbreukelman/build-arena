from __future__ import annotations

from collections import defaultdict
from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator

PROJECT_MODEL_V0_SCHEMA_VERSION = "project-model/v0"

FindingSeverity = Literal["error", "warning"]
Identifier = Annotated[str, Field(min_length=1, pattern=r"^[a-z][a-z0-9_\-]*$")]
NonEmptyString = Annotated[str, Field(min_length=1)]
RiskLevel = Literal["low", "medium", "high"]
ComponentKind = Literal[
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
]
DependencyKind = Literal["requires", "precedes", "blocks", "feeds", "informs"]
ObservableCheckMode = Literal[
    "test",
    "static-analysis",
    "simulation",
    "inspection",
    "artifact-audit",
    "stakeholder-decision",
    "non-code-rubric",
    "external-observation",
]
ProbeType = Literal[
    "held-out-example",
    "counterexample",
    "perturbation",
    "tabletop",
    "negative-control",
]
AssumptionStatus = Literal["assumed", "confirmed", "disputed"]

_DIRECTIONAL_DEPENDENCY_KINDS = {"precedes", "requires", "blocks"}
_VAGUE_IDS = {
    "all",
    "everything",
    "general",
    "misc",
    "miscellaneous",
    "other",
    "project",
    "stuff",
    "tbd",
}
_VAGUE_PHRASES = (
    "and so on",
    "do things",
    "do the work",
    "etc",
    "handle stuff",
    "make better",
    "misc",
    "stuff",
    "things",
    "various",
)
_VAGUE_SURFACES = {"all", "everything", "project", "repo", "repository", "stuff"}


class _StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="before")
    @classmethod
    def _reject_explicit_nulls(cls, data: Any) -> Any:
        if isinstance(data, dict):
            for key, value in data.items():
                if value is None:
                    raise ValueError(f"{key} must be omitted rather than set to null")
        return data


class Source(_StrictModel):
    task: NonEmptyString
    primaryBacklogItem: NonEmptyString
    repo: NonEmptyString | None = None
    issue: NonEmptyString | None = None


class Component(_StrictModel):
    id: Identifier
    name: NonEmptyString
    kind: ComponentKind
    riskLevel: RiskLevel
    responsibilities: list[NonEmptyString] = Field(min_length=1)
    ownedSurfaces: list[NonEmptyString] = Field(min_length=1)
    observableCheckIds: list[Identifier]


class Dependency(_StrictModel):
    id: Identifier
    fromComponent: Identifier
    toComponent: Identifier
    kind: DependencyKind
    description: NonEmptyString
    observableCheckIds: list[Identifier] = Field(default_factory=list)


class Invariant(_StrictModel):
    id: Identifier
    description: NonEmptyString
    componentIds: list[Identifier]
    observableCheckIds: list[Identifier]


class ObservableCheck(_StrictModel):
    id: Identifier
    componentId: Identifier
    mode: ObservableCheckMode
    description: NonEmptyString
    observableSignal: NonEmptyString
    evidenceRequired: list[NonEmptyString]
    noLiveApi: bool | None = None


class EvidenceRequirement(_StrictModel):
    id: Identifier
    description: NonEmptyString
    acceptedArtifactTypes: list[NonEmptyString] = Field(min_length=1)
    requiredFor: list[Identifier]


class Assumption(_StrictModel):
    id: Identifier
    description: NonEmptyString
    status: AssumptionStatus | None = None


class Risk(_StrictModel):
    id: Identifier
    level: RiskLevel
    description: NonEmptyString
    componentId: Identifier | None = None
    mitigation: NonEmptyString | None = None


class NearNeighborAlternative(_StrictModel):
    id: Identifier
    description: NonEmptyString
    whyNotPrimary: NonEmptyString
    distinguishingEvidence: list[NonEmptyString]


class HeldOutProbe(_StrictModel):
    id: Identifier
    componentId: Identifier
    probeType: ProbeType
    scenario: NonEmptyString
    expectedBehavior: NonEmptyString
    evidenceRequired: list[NonEmptyString]


class VerificationGap(_StrictModel):
    id: Identifier
    severity: RiskLevel
    description: NonEmptyString
    affectedComponentIds: list[Identifier]
    proposedClosureCheck: NonEmptyString


class UnclassifiedProjectSurface(_StrictModel):
    id: Identifier
    description: NonEmptyString
    reasonUnclassified: NonEmptyString
    candidateOwners: list[Identifier]


class AdvisorySignalHandoff(_StrictModel):
    consumer: Literal["elenchus-core"]
    expectedFields: list[NonEmptyString] = Field(min_length=6)
    optionalFLabelHint: bool


class ProjectModelV0(_StrictModel):
    schemaVersion: Literal["project-model/v0"]
    id: Identifier
    source: Source
    goal: NonEmptyString
    nonGoals: list[NonEmptyString]
    components: list[Component] = Field(min_length=1)
    dependencies: list[Dependency]
    invariants: list[Invariant]
    observableChecks: list[ObservableCheck] = Field(min_length=1)
    evidenceRequirements: list[EvidenceRequirement]
    assumptions: list[Assumption]
    risks: list[Risk]
    nearNeighborAlternatives: list[NearNeighborAlternative]
    heldOutProbes: list[HeldOutProbe]
    verificationGaps: list[VerificationGap]
    unclassifiedProjectSurface: list[UnclassifiedProjectSurface]
    advisorySignalHandoff: AdvisorySignalHandoff


class QualityGateFinding(_StrictModel):
    code: str
    severity: FindingSeverity
    location: str
    message: str


class QualityGateReport(_StrictModel):
    passed: bool
    findings: list[QualityGateFinding] = Field(default_factory=list)


def evaluate_quality_gate(model: BaseModel | dict[str, Any]) -> QualityGateReport:
    """Evaluate Project Model v0 meta-F3 quality guards.

    This is intentionally structural and deterministic. It does not score
    proposal correctness and it never calls live LLM/API services. The goal is
    to keep a vague or under-observed project decomposition from becoming the
    downstream F3 ruler.
    """

    if isinstance(model, BaseModel):
        model = model.model_dump(mode="json", exclude_none=isinstance(model, ProjectModelV0))
    try:
        ProjectModelV0.model_validate(model)
    except ValidationError as exc:
        validation_errors: list[Any] = exc.errors()
    else:
        validation_errors = []

    findings: list[QualityGateFinding] = [
        QualityGateFinding(
            code="schema_validation_error",
            severity="error",
            location=".".join(str(part) for part in error.get("loc", ())) or "<root>",
            message=str(error.get("msg", "Project Model v0 schema validation failed.")),
        )
        for error in validation_errors
    ]

    if model.get("schemaVersion") != PROJECT_MODEL_V0_SCHEMA_VERSION:
        findings.append(
            QualityGateFinding(
                code="unsupported_schema_version",
                severity="error",
                location="schemaVersion",
                message="Project Model quality gate only accepts project-model/v0.",
            )
        )

    components = _list_of_dicts(model.get("components"))
    component_ids = [str(component.get("id", "")) for component in components]
    component_id_set = {component_id for component_id in component_ids if component_id}
    if not components:
        findings.append(
            QualityGateFinding(
                code="missing_components",
                severity="error",
                location="components",
                message="Project Model v0 requires at least one component.",
            )
        )

    observable_checks = _list_of_dicts(model.get("observableChecks"))
    if not observable_checks:
        findings.append(
            QualityGateFinding(
                code="missing_observable_checks",
                severity="error",
                location="observableChecks",
                message="Project Model v0 requires at least one observable check.",
            )
        )
    check_component_by_id = {
        str(check.get("id", "")): str(check.get("componentId", ""))
        for check in observable_checks
        if check.get("id")
    }
    valid_check_ids = set(check_component_by_id)

    for check_id, component_id in sorted(check_component_by_id.items()):
        if component_id not in component_id_set:
            findings.append(
                QualityGateFinding(
                    code="missing_observable_check_component",
                    severity="error",
                    location=f"observableChecks[{check_id}].componentId",
                    message=(
                        f"Observable check {check_id} references unknown component "
                        f"{component_id!r}."
                    ),
                )
            )

    for component in components:
        component_id = str(component.get("id", ""))
        declared_check_ids = {
            str(check_id)
            for check_id in _list_of_scalars(component.get("observableCheckIds"))
            if str(check_id)
        }
        missing_check_ids = sorted(declared_check_ids - valid_check_ids)
        for check_id in missing_check_ids:
            findings.append(
                QualityGateFinding(
                    code="missing_observable_check_reference",
                    severity="error",
                    location=f"components[{component_id}].observableCheckIds",
                    message=f"Component {component_id} references missing observable check {check_id}.",
                )
            )
        mismatched_check_ids = sorted(
            check_id
            for check_id in declared_check_ids & valid_check_ids
            if check_component_by_id.get(check_id) != component_id
        )
        for check_id in mismatched_check_ids:
            findings.append(
                QualityGateFinding(
                    code="observable_check_component_mismatch",
                    severity="error",
                    location=f"components[{component_id}].observableCheckIds",
                    message=(
                        f"Component {component_id} links observable check {check_id}, but that check "
                        f"belongs to {check_component_by_id.get(check_id)}."
                    ),
                )
            )
        if not declared_check_ids:
            findings.append(
                QualityGateFinding(
                    code="component_without_observable_check",
                    severity="error",
                    location=f"components[{component_id}].observableCheckIds",
                    message=f"Component {component_id} has no linked observable check id.",
                )
            )
        if _is_vague_component(component):
            findings.append(
                QualityGateFinding(
                    code="vague_decomposition",
                    severity="error",
                    location=f"components[{component_id}]",
                    message=(
                        f"Component {component_id or '<missing>'} is too vague to be a load-bearing "
                        "project decomposition unit."
                    ),
                )
            )

    dependencies = _list_of_dicts(model.get("dependencies"))
    if len(component_id_set) > 1 and not dependencies:
        findings.append(
            QualityGateFinding(
                code="missing_dependencies",
                severity="error",
                location="dependencies",
                message="Model has multiple components but no dependency or sequencing constraints.",
            )
        )

    dependency_edges: list[tuple[str, str, str]] = []
    for dependency in dependencies:
        dependency_id = str(dependency.get("id", ""))
        from_component = str(dependency.get("fromComponent", ""))
        to_component = str(dependency.get("toComponent", ""))
        kind = str(dependency.get("kind", ""))
        if from_component not in component_id_set or to_component not in component_id_set:
            findings.append(
                QualityGateFinding(
                    code="missing_dependency_reference",
                    severity="error",
                    location=f"dependencies[{dependency_id}]",
                    message=(
                        f"Dependency {dependency_id or '<missing>'} references unknown component(s): "
                        f"{from_component!r} -> {to_component!r}."
                    ),
                )
            )
            continue
        if kind in _DIRECTIONAL_DEPENDENCY_KINDS:
            dependency_edges.append((from_component, to_component, dependency_id))

    for finding in _contradictory_dependency_findings(dependency_edges):
        findings.append(finding)

    unclassified_surfaces = _list_of_dicts(model.get("unclassifiedProjectSurface"))
    if unclassified_surfaces:
        findings.append(
            QualityGateFinding(
                code="unclassified_project_surface",
                severity="error",
                location="unclassifiedProjectSurface",
                message=(
                    "Model leaves significant project surface unclassified: "
                    + ", ".join(str(surface.get("id", "<missing>")) for surface in unclassified_surfaces)
                ),
            )
        )

    high_risk_components = _high_risk_component_ids(components, _list_of_dicts(model.get("risks")))
    held_out_component_ids = {
        str(probe.get("componentId", "")) for probe in _list_of_dicts(model.get("heldOutProbes"))
    }
    for component_id in sorted(high_risk_components):
        if component_id not in held_out_component_ids:
            findings.append(
                QualityGateFinding(
                    code="missing_held_out_probe",
                    severity="error",
                    location=f"heldOutProbes[{component_id}]",
                    message=f"High-risk component {component_id} has no held-out probe or counterexample.",
                )
            )

    return QualityGateReport(
        passed=not any(finding.severity == "error" for finding in findings),
        findings=findings,
    )


def _list_of_dicts(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]


def _list_of_scalars(value: Any) -> list[Any]:
    if not isinstance(value, list):
        return []
    return [item for item in value if not isinstance(item, (dict, list))]


def _normalized_token(value: Any) -> str:
    return str(value or "").strip().lower().replace("-", "_").replace(" ", "_")


def _is_vague_component(component: dict[str, Any]) -> bool:
    component_id = _normalized_token(component.get("id"))
    name = _normalized_token(component.get("name"))
    if component_id in _VAGUE_IDS or name in _VAGUE_IDS:
        return True

    responsibilities = " ".join(str(item) for item in _list_of_scalars(component.get("responsibilities"))).lower()
    if any(phrase in responsibilities for phrase in _VAGUE_PHRASES):
        return True

    owned_surfaces = {
        str(surface).strip().lower() for surface in _list_of_scalars(component.get("ownedSurfaces"))
    }
    return bool(owned_surfaces) and owned_surfaces <= _VAGUE_SURFACES


def _contradictory_dependency_findings(
    dependency_edges: list[tuple[str, str, str]],
) -> list[QualityGateFinding]:
    findings: list[QualityGateFinding] = []
    seen: dict[tuple[str, str], str] = {}
    for source, target, dependency_id in dependency_edges:
        reverse = (target, source)
        if reverse in seen:
            findings.append(
                QualityGateFinding(
                    code="contradictory_dependencies",
                    severity="error",
                    location=f"dependencies[{dependency_id}]",
                    message=(
                        f"Dependency {dependency_id or '<missing>'} contradicts {seen[reverse]}: "
                        f"{source} and {target} are each ordered before the other."
                    ),
                )
            )
        seen[(source, target)] = dependency_id

    graph: dict[str, set[str]] = defaultdict(set)
    for source, target, _dependency_id in dependency_edges:
        graph[source].add(target)
    cycle_path = _first_cycle(graph)
    if cycle_path:
        findings.append(
            QualityGateFinding(
                code="contradictory_dependencies",
                severity="error",
                location="dependencies",
                message="Directional dependency cycle detected: " + " -> ".join(cycle_path),
            )
        )
    return findings


def _first_cycle(graph: dict[str, set[str]]) -> list[str]:
    visiting: set[str] = set()
    visited: set[str] = set()
    stack: list[str] = []

    def visit(node: str) -> list[str]:
        if node in visiting:
            try:
                start = stack.index(node)
            except ValueError:
                start = 0
            return [*stack[start:], node]
        if node in visited:
            return []
        visiting.add(node)
        stack.append(node)
        for neighbor in sorted(graph.get(node, set())):
            cycle = visit(neighbor)
            if cycle:
                return cycle
        stack.pop()
        visiting.remove(node)
        visited.add(node)
        return []

    for node in sorted(graph):
        cycle = visit(node)
        if cycle:
            return cycle
    return []


def _high_risk_component_ids(
    components: list[dict[str, Any]],
    risks: list[dict[str, Any]],
) -> set[str]:
    high_risk = {
        str(component.get("id", ""))
        for component in components
        if str(component.get("riskLevel", "")).lower() == "high" and component.get("id")
    }
    high_risk.update(
        str(risk.get("componentId", ""))
        for risk in risks
        if str(risk.get("level", "")).lower() == "high" and risk.get("componentId")
    )
    return high_risk
