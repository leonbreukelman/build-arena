from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
from pydantic import BaseModel, ValidationError

from arena.project_model_v0 import ProjectModelV0, evaluate_quality_gate

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "docs" / "schemas" / "project-model-v0.schema.json"
EXAMPLE_PATHS = [
    ROOT / "docs" / "examples" / "project-model-v0-code-adjacent.json",
    ROOT / "docs" / "examples" / "project-model-v0-process-strategy.json",
]


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _finding_codes(model: Any) -> set[str]:
    return {finding.code for finding in evaluate_quality_gate(model).findings}


def _base_model() -> dict[str, Any]:
    return {
        "schemaVersion": "project-model/v0",
        "id": "quality-gate-fixture",
        "source": {
            "task": "Define a reusable quality-gate fixture.",
            "primaryBacklogItem": "https://example.invalid/issues/1",
        },
        "goal": "Create a focused project model with observable component checks.",
        "nonGoals": ["Do not implement downstream scoring."],
        "components": [
            {
                "id": "contract_spec",
                "name": "Contract spec",
                "kind": "spec",
                "riskLevel": "high",
                "responsibilities": ["Define the shared field semantics and compatibility target."],
                "ownedSurfaces": ["docs/project-model-v0.md"],
                "observableCheckIds": ["schema_examples_validate"],
            },
            {
                "id": "consumer_alignment",
                "name": "Consumer alignment",
                "kind": "process",
                "riskLevel": "medium",
                "responsibilities": ["Keep downstream agents aligned to the same field names."],
                "ownedSurfaces": ["child issue acceptance criteria"],
                "observableCheckIds": ["issue_links_reference_contract"],
            },
        ],
        "dependencies": [
            {
                "id": "spec_before_consumers",
                "fromComponent": "contract_spec",
                "toComponent": "consumer_alignment",
                "kind": "precedes",
                "description": "Consumers must target the versioned contract before local implementation details.",
            }
        ],
        "invariants": [
            {
                "id": "no_live_api_required",
                "description": "Acceptance must not require live LLM or paid API calls.",
                "componentIds": ["contract_spec", "consumer_alignment"],
                "observableCheckIds": ["schema_examples_validate"],
            }
        ],
        "observableChecks": [
            {
                "id": "schema_examples_validate",
                "componentId": "contract_spec",
                "mode": "static-analysis",
                "description": "JSON examples validate against the Project Model v0 schema.",
                "observableSignal": "validator exits successfully for both worked examples",
                "evidenceRequired": ["pytest output"],
            },
            {
                "id": "issue_links_reference_contract",
                "componentId": "consumer_alignment",
                "mode": "inspection",
                "description": "Child tickets point at the same compatibility target.",
                "observableSignal": "issue bodies mention project-model/v0 and the schema path",
                "evidenceRequired": ["issue URLs"],
            },
        ],
        "evidenceRequirements": [
            {
                "id": "pytest_output",
                "description": "Local targeted tests pass without network calls.",
                "acceptedArtifactTypes": ["terminal-output"],
                "requiredFor": ["contract_spec"],
            }
        ],
        "assumptions": [
            {"id": "json_schema_available", "description": "Consumers can read JSON Schema."}
        ],
        "risks": [
            {
                "id": "meta_f3",
                "componentId": "contract_spec",
                "level": "high",
                "description": "A vague model can become a bad ruler for F3.",
                "mitigation": "Run quality-gate checks before consumers treat the model as authoritative.",
            }
        ],
        "nearNeighborAlternatives": [
            {
                "id": "doc_only_contract",
                "description": "Document the contract without a schema.",
                "whyNotPrimary": "Downstream repos would drift on names and required fields.",
                "distinguishingEvidence": ["schema validation catches missing fields"],
            }
        ],
        "heldOutProbes": [
            {
                "id": "wrong_target_probe",
                "componentId": "contract_spec",
                "probeType": "counterexample",
                "scenario": "A proposal satisfies a checklist but ignores the high-risk component.",
                "expectedBehavior": "The quality gate flags missing held-out coverage for the high-risk component.",
                "evidenceRequired": ["quality-gate finding"],
            }
        ],
        "verificationGaps": [],
        "unclassifiedProjectSurface": [],
        "advisorySignalHandoff": {
            "consumer": "elenchus-core",
            "expectedFields": [
                "componentAlignment",
                "invariantViolations",
                "dependencyViolations",
                "unsupportedAssumptions",
                "evidenceGroundingGaps",
                "nearNeighborResistance",
                "fLabelHint",
            ],
            "optionalFLabelHint": True,
        },
    }


def test_project_model_v0_examples_validate_against_schema_and_quality_gate() -> None:
    schema = _load_json(SCHEMA_PATH)
    validator = Draft202012Validator(schema)

    for example_path in EXAMPLE_PATHS:
        model = _load_json(example_path)
        schema_errors = sorted(validator.iter_errors(model), key=lambda error: list(error.path))
        assert schema_errors == []

        parsed_model = ProjectModelV0.model_validate(model)
        report = evaluate_quality_gate(parsed_model)
        assert report.passed, [f"{finding.code}: {finding.message}" for finding in report.findings]


def test_project_model_v0_python_model_forbids_extra_fields_and_schema_invalid_shapes() -> None:
    model = _base_model()
    parsed_model = ProjectModelV0.model_validate(model)
    assert parsed_model.schemaVersion == "project-model/v0"

    model["unexpected"] = "not part of the contract"
    try:
        ProjectModelV0.model_validate(model)
    except ValidationError as exc:
        assert "unexpected" in str(exc)
    else:  # pragma: no cover - defensive assertion
        raise AssertionError("ProjectModelV0 accepted an extra top-level field")

    empty_components = deepcopy(_base_model())
    empty_components["components"] = []
    try:
        ProjectModelV0.model_validate(empty_components)
    except ValidationError as exc:
        assert "components" in str(exc)
    else:  # pragma: no cover - defensive assertion
        raise AssertionError("ProjectModelV0 accepted an empty components list")

    empty_observable_checks = deepcopy(_base_model())
    empty_observable_checks["observableChecks"] = []
    try:
        ProjectModelV0.model_validate(empty_observable_checks)
    except ValidationError as exc:
        assert "observableChecks" in str(exc)
    else:  # pragma: no cover - defensive assertion
        raise AssertionError("ProjectModelV0 accepted an empty observableChecks list")

    explicit_null = deepcopy(_base_model())
    explicit_null["source"]["repo"] = None
    try:
        ProjectModelV0.model_validate(explicit_null)
    except ValidationError as exc:
        assert "must be omitted rather than set to null" in str(exc)
    else:  # pragma: no cover - defensive assertion
        raise AssertionError("ProjectModelV0 accepted an explicit null optional field")


def test_quality_gate_flags_meta_f3_failure_modes() -> None:
    no_check = deepcopy(_base_model())
    no_check["components"][0]["observableCheckIds"] = []
    assert "component_without_observable_check" in _finding_codes(no_check)

    missing_components = deepcopy(_base_model())
    missing_components["components"] = []
    assert "missing_components" in _finding_codes(missing_components)

    missing_checks = deepcopy(_base_model())
    missing_checks["observableChecks"] = []
    assert "missing_observable_checks" in _finding_codes(missing_checks)

    mismatched_check = deepcopy(_base_model())
    mismatched_check["components"][0]["observableCheckIds"] = ["issue_links_reference_contract"]
    assert "observable_check_component_mismatch" in _finding_codes(mismatched_check)

    schema_invalid_but_non_empty = {
        "schemaVersion": "project-model/v0",
        "components": [
            {
                "id": "contract_spec",
                "observableCheckIds": ["schema_examples_validate"],
            }
        ],
        "observableChecks": [
            {
                "id": "schema_examples_validate",
                "componentId": "contract_spec",
            }
        ],
        "dependencies": [],
        "risks": [],
        "heldOutProbes": [],
        "unclassifiedProjectSurface": [],
    }
    assert "schema_validation_error" in _finding_codes(schema_invalid_but_non_empty)

    explicit_null_optional = deepcopy(_base_model())
    explicit_null_optional["source"]["repo"] = None
    assert "schema_validation_error" in _finding_codes(explicit_null_optional)

    class ArbitraryModel(BaseModel):
        schemaVersion: str
        components: list[dict[str, Any]]
        observableChecks: list[dict[str, Any]]
        dependencies: list[dict[str, Any]]
        risks: list[dict[str, Any]]
        heldOutProbes: list[dict[str, Any]]
        unclassifiedProjectSurface: list[dict[str, Any]]

    arbitrary_model = ArbitraryModel(
        schemaVersion="project-model/v0",
        components=[{"id": "contract_spec", "observableCheckIds": ["schema_examples_validate"]}],
        observableChecks=[{"id": "schema_examples_validate", "componentId": "contract_spec"}],
        dependencies=[],
        risks=[],
        heldOutProbes=[],
        unclassifiedProjectSurface=[],
    )
    assert "schema_validation_error" in _finding_codes(arbitrary_model)

    class ArbitraryModelWithNull(BaseModel):
        schemaVersion: str
        id: str
        source: dict[str, Any]
        goal: str
        nonGoals: list[str]
        components: list[dict[str, Any]]
        dependencies: list[dict[str, Any]]
        invariants: list[dict[str, Any]]
        observableChecks: list[dict[str, Any]]
        evidenceRequirements: list[dict[str, Any]]
        assumptions: list[dict[str, Any]]
        risks: list[dict[str, Any]]
        nearNeighborAlternatives: list[dict[str, Any]]
        heldOutProbes: list[dict[str, Any]]
        verificationGaps: list[dict[str, Any]]
        unclassifiedProjectSurface: list[dict[str, Any]]
        advisorySignalHandoff: dict[str, Any]

    arbitrary_with_null = ArbitraryModelWithNull(**_base_model())
    arbitrary_with_null.source["repo"] = None
    assert "schema_validation_error" in _finding_codes(arbitrary_with_null)

    mutated_project_model = ProjectModelV0.model_validate(_base_model())
    mutated_project_model.components = []
    assert "schema_validation_error" in _finding_codes(mutated_project_model)

    vague = deepcopy(_base_model())
    vague["components"][0].update(
        {
            "id": "misc",
            "name": "Misc",
            "responsibilities": ["Handle various stuff etc."],
            "ownedSurfaces": ["everything"],
        }
    )
    vague["observableChecks"][0]["componentId"] = "misc"
    vague["dependencies"][0]["fromComponent"] = "misc"
    vague["invariants"][0]["componentIds"][0] = "misc"
    vague["risks"][0]["componentId"] = "misc"
    vague["heldOutProbes"][0]["componentId"] = "misc"
    assert "vague_decomposition" in _finding_codes(vague)

    missing_deps = deepcopy(_base_model())
    missing_deps["dependencies"] = []
    assert "missing_dependencies" in _finding_codes(missing_deps)

    contradictory_deps = deepcopy(_base_model())
    contradictory_deps["dependencies"].append(
        {
            "id": "consumer_before_spec",
            "fromComponent": "consumer_alignment",
            "toComponent": "contract_spec",
            "kind": "precedes",
            "description": "Contradicts the required sequence.",
        }
    )
    assert "contradictory_dependencies" in _finding_codes(contradictory_deps)

    unclassified = deepcopy(_base_model())
    unclassified["unclassifiedProjectSurface"] = [
        {
            "id": "unknown_surface",
            "description": "A significant work surface has no component owner.",
            "reasonUnclassified": "No owner selected yet.",
            "candidateOwners": ["contract_spec"],
        }
    ]
    assert "unclassified_project_surface" in _finding_codes(unclassified)

    missing_probe = deepcopy(_base_model())
    missing_probe["heldOutProbes"] = []
    assert "missing_held_out_probe" in _finding_codes(missing_probe)
