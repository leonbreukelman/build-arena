from __future__ import annotations

import argparse
import hashlib
import json
import re
import tomllib
from pathlib import Path, PurePosixPath
from typing import Any

SCHEMA_VERSION = "project-intake-scorecard/v0"

DIMENSIONS = (
    "documentation_project_knowledge",
    "reproducible_verification",
    "architecture_specs_contracts",
    "ai_agent_usability",
    "decision_history",
    "backlog_change_governance",
    "security_supply_chain_hygiene",
    "operations_release_rollback",
)

PROFILE_WEIGHTS: dict[str, dict[str, int]] = {
    "new-project": {
        "documentation_project_knowledge": 28,
        "reproducible_verification": 20,
        "architecture_specs_contracts": 14,
        "ai_agent_usability": 14,
        "security_supply_chain_hygiene": 9,
        "decision_history": 7,
        "backlog_change_governance": 4,
        "operations_release_rollback": 4,
    },
    "active-development": {
        "reproducible_verification": 24,
        "documentation_project_knowledge": 19,
        "architecture_specs_contracts": 18,
        "security_supply_chain_hygiene": 10,
        "ai_agent_usability": 9,
        "decision_history": 8,
        "backlog_change_governance": 8,
        "operations_release_rollback": 4,
    },
    "production": {
        "reproducible_verification": 24,
        "security_supply_chain_hygiene": 20,
        "operations_release_rollback": 19,
        "documentation_project_knowledge": 14,
        "architecture_specs_contracts": 9,
        "decision_history": 5,
        "backlog_change_governance": 5,
        "ai_agent_usability": 4,
    },
    "documentation-first": {
        "documentation_project_knowledge": 33,
        "ai_agent_usability": 18,
        "architecture_specs_contracts": 18,
        "reproducible_verification": 14,
        "decision_history": 10,
        "backlog_change_governance": 4,
        "security_supply_chain_hygiene": 2,
        "operations_release_rollback": 1,
    },
}

_SEVERITY = {"low": 1.0, "medium": 2.0, "high": 3.0, "critical": 4.0}
_CONFIDENCE = {"low": 0.5, "medium": 0.75, "high": 1.0}
_EFFORT = {"small": 1.0, "medium": 2.0, "large": 3.0, "unknown": 4.0}

_AbsenceSpec = tuple[str, str, str, str | tuple[str, ...], str, int, int, int, int]

_ABSENCE_SEVERITY = {
    "doc.readme.missing": "high",
    "agent.agents-md.missing": "high",
    "verification.ci.missing": "high",
    "verification.lockfile.missing": "low",
    "verification.precommit.missing": "low",
    "security.policy.missing": "medium",
    "security.dep-update.missing": "low",
    "governance.contributing.missing": "low",
    "governance.codeowners.missing": "low",
    "governance.templates.missing": "low",
    "ops.env-example.missing": "low",
    "architecture.overview.missing": "medium",
}

_ABSENCE_EFFORT = {
    "verification.ci.missing": "unknown",
    "verification.lockfile.missing": "unknown",
    "verification.precommit.missing": "unknown",
    "security.policy.missing": "unknown",
    "security.dep-update.missing": "unknown",
    "governance.contributing.missing": "unknown",
    "governance.codeowners.missing": "unknown",
    "governance.templates.missing": "unknown",
    "ops.env-example.missing": "unknown",
    "architecture.overview.missing": "unknown",
}

_READINESS_SIGNAL_FINDINGS = frozenset(_ABSENCE_EFFORT) | {"verification.test-command.missing"}

_TEST_COMMAND_CHECK_PATHS = (
    "pyproject.toml",
    "Makefile",
    "package.json",
    "tox.ini",
    "pytest.ini",
)


def finding_priority_score(
    *,
    dimension_weight: int,
    severity: str,
    confidence: str,
    effort: str,
    impact_on_future_iteration: int,
    risk_reduction: int,
    verification_gain: int,
    doc_knowledge_gain: int,
) -> float:
    total_gain = impact_on_future_iteration + risk_reduction + verification_gain + doc_knowledge_gain
    return round(dimension_weight * _SEVERITY[severity] * _CONFIDENCE[confidence] * total_gain / _EFFORT[effort], 6)


def build_project_intake_scorecard(project: str | Path, snapshot: str | Path, *, profile: str = "new-project") -> dict[str, Any]:
    if profile not in PROFILE_WEIGHTS:
        raise ValueError(f"unknown profile: {profile}")
    project_path = Path(project).resolve()
    snapshot_path = Path(snapshot).resolve()
    snapshot_data = _load_json(snapshot_path)
    weights = PROFILE_WEIGHTS[profile]
    findings = _findings(project_path, snapshot_data, weights)
    readiness_checks = _readiness_check_results(project_path)
    findings = sorted(
        findings,
        key=lambda finding: (
            -float(finding["priorityScore"]),
            -_SEVERITY[str(finding["severity"])],
            -_CONFIDENCE[str(finding["confidence"])],
            _EFFORT[str(finding["estimatedEffort"])],
            str(finding["id"]),
        ),
    )
    for index, finding in enumerate(findings, start=1):
        finding["rank"] = index
    first = _first_recommendation(findings)
    base = {
        "schemaVersion": SCHEMA_VERSION,
        "projectRoot": str(project_path),
        "snapshotPath": str(snapshot_path),
        "snapshotId": str(snapshot_data.get("id", "")),
        "snapshotHash": _sha(snapshot_data),
        "repoHead": _get(snapshot_data, "provenance", "git", "headOid"),
        "profile": profile,
        "weights": weights,
        "advisoryOnly": True,
        "dimensionScores": _dimension_scores(readiness_checks),
        "loopReadiness": _loop_readiness(readiness_checks),
        "findings": findings,
        "improvementCandidates": _improvement_candidates(findings),
        "firstRecommendedImprovement": first,
    }
    return {**base, "id": _sha(base)[:16]}


def scorecard_to_markdown(scorecard: dict[str, Any]) -> str:
    lines = [
        "# Project Intake Scorecard",
        "",
        f"Profile: `{scorecard['profile']}`",
        "",
        "Advisory only: this scorecard does not authorize mutation.",
        "",
        "## First recommended improvement",
        "",
    ]
    first = scorecard.get("firstRecommendedImprovement") or {}
    lines.extend([f"- Finding: `{first.get('findingId', '')}`", f"- Title: {first.get('title', '')}", "", "## Ranked findings", ""])
    for finding in scorecard.get("findings", []):
        lines.append(f"{finding['rank']}. `{finding['id']}` — {finding['title']} ({finding['priorityScore']})")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m arena.project_intake_scorecard")
    parser.add_argument("--project", required=True)
    parser.add_argument("--snapshot", required=True)
    parser.add_argument("--profile", choices=sorted(PROFILE_WEIGHTS), default="new-project")
    parser.add_argument("--output", required=True)
    parser.add_argument("--markdown-output")
    args = parser.parse_args(argv)
    scorecard = build_project_intake_scorecard(args.project, args.snapshot, profile=args.profile)
    Path(args.output).write_text(json.dumps(scorecard, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.markdown_output:
        Path(args.markdown_output).write_text(scorecard_to_markdown(scorecard), encoding="utf-8")
    return 0


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("snapshot must be a JSON object")
    return payload


def _findings(project: Path, snapshot: dict[str, Any], weights: dict[str, int]) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    findings.extend(_absence_findings(project, weights))
    findings.extend(_verification_capability_findings(project, weights))
    findings.extend(_component_findings(snapshot, weights))
    findings.extend(_lint_findings(project, weights))
    findings.extend(_quality_gate_findings(snapshot, weights))
    findings.extend(_question_and_gap_findings(snapshot, weights))
    return findings


def _lint_findings(project: Path, weights: dict[str, int], *, max_files: int = 25) -> list[dict[str, Any]]:
    """Emit a ``code.quality.lint.<relpath>`` finding for each Python file with
    ruff violations. Deterministic: files are sorted, violation counts come from
    ruff JSON. Bounded by ``max_files`` so a very dirty repo cannot flood intake.
    Targets the code-quality domain, whose load-bearing gate proves a real fix."""
    counts = _ruff_violation_counts(project)
    findings: list[dict[str, Any]] = []
    for rel_path in sorted(counts)[:max_files]:
        violation_count = counts[rel_path]
        if violation_count <= 0:
            continue
        # Only emit findings the code-quality domain can act on (single .py file
        # with the load-bearing gate). .pyi/.ipynb are linted by ruff but the
        # gate/domain target plain .py, so skip them rather than emit a finding
        # that would fall through to an empty-verification fallback.
        if not rel_path.endswith(".py"):
            continue
        severity = "medium" if violation_count >= 5 else "low"
        findings.append(
            _finding(
                f"code.quality.lint.{rel_path}",
                "architecture_specs_contracts",
                f"{rel_path} has {violation_count} ruff lint violation(s)",
                severity,
                "high",
                [{"kind": "lint", "path": rel_path, "checked": True, "violations": violation_count}],
                f"{rel_path} has ruff lint violations a proposer can mechanically reduce.",
                f"Reduce ruff violations in {rel_path} without adding suppressions.",
                [f"python3 -m arena.code_quality_gate --repo . --path {rel_path}"],
                "needs_code_change",
                "small",
                weights,
                2,
                2,
                3,
                1,
            )
        )
    return findings


def _ruff_violation_counts(project: Path) -> dict[str, int]:
    """Return {relative_path: violation_count} from a single ruff JSON run over
    the repo. Returns {} if ruff is unavailable or produced no parseable output
    (fail safe: no lint findings rather than fabricated ones)."""
    import json as _json
    import subprocess

    try:
        proc = subprocess.run(
            ["ruff", "check", "--no-cache", "--output-format", "json", "."],
            cwd=project,
            text=True,
            capture_output=True,
            check=False,
        )
    except (OSError, ValueError):
        return {}
    stdout = proc.stdout.strip()
    if not stdout:
        return {}
    try:
        violations = _json.loads(stdout)
    except _json.JSONDecodeError:
        return {}
    if not isinstance(violations, list):
        return {}
    counts: dict[str, int] = {}
    project_resolved = project.resolve()
    for violation in violations:
        if not isinstance(violation, dict):
            continue
        filename = violation.get("filename")
        if not isinstance(filename, str):
            continue
        try:
            rel = Path(filename).resolve().relative_to(project_resolved).as_posix()
        except ValueError:
            continue
        counts[rel] = counts.get(rel, 0) + 1
    return counts


_RISK_SEVERITY = {"low": "low", "medium": "medium", "high": "high"}


def _risk_level_to_severity(risk_level: str) -> str:
    """Map a component riskLevel to a finding severity. Unknown values fail safe
    to ``medium`` so a malformed/extended riskLevel never silently downgrades a
    finding to the lowest severity."""
    return _RISK_SEVERITY.get(str(risk_level).strip().lower(), "medium")


def _component_findings(snapshot: dict[str, Any], weights: dict[str, int]) -> list[dict[str, Any]]:
    """Turn the decomposer's anchored interpretation into component-scoped,
    non-documentation findings.

    Today this surfaces high-leverage *untested components*: a component that has
    no observable check is one a proposer cannot safely verify, so it is a
    reproducible-verification gap whose target is the component's own owned source
    surface(s). Severity follows the component's riskLevel.
    """
    profiles = list(_get(snapshot, "iterationReadiness", "componentProfiles") or [])
    components = list(_get(snapshot, "snapshot", "components") or [])
    if not profiles or not components:
        return []

    node_paths = _graph_node_paths(snapshot)
    components_by_id = {str(component.get("id")): component for component in components if isinstance(component, dict)}
    checked_component_ids = _components_with_checks(snapshot)

    findings: list[dict[str, Any]] = []
    for profile in profiles:
        if not isinstance(profile, dict):
            continue
        component_id = str(profile.get("componentId", ""))
        component = components_by_id.get(component_id)
        if component is None:
            continue
        if component_id in checked_component_ids:
            continue
        owned_node_ids = [str(item) for item in component.get("owned_node_ids", [])]
        owned_paths = [node_paths[node_id] for node_id in owned_node_ids if node_id in node_paths]
        # Only target concrete files with a real extension. An extension-less
        # surface (Dockerfile, Makefile, a directory/package node) would be
        # rewritten by the planner to "<path>/index.md" and silently routed back
        # into the documentation contract — fabricating a path and regressing to
        # docs-only. Drop those here so the finding can only point at real files.
        owned_paths = list(dict.fromkeys(path for path in owned_paths if PurePosixPath(path).suffix))
        if not owned_paths:
            # No resolvable, concretely-targetable source surface.
            continue
        verification = _component_verification_commands(owned_paths)
        severity = _risk_level_to_severity(str(profile.get("riskLevel", "")))
        provenance_refs = [str(ref) for ref in profile.get("provenanceRefs", [])]
        evidence: list[dict[str, Any]] = [
            {"kind": "component", "componentId": component_id, "checked": True},
            {"kind": "absence", "path": "iterationReadiness.componentProfiles", "checked": True},
        ]
        evidence.extend({"kind": "owned_surface", "path": path, "checked": True} for path in owned_paths)
        for ref in provenance_refs:
            evidence.append({"kind": "provenance", "ref": ref, "checked": True})
        name = str(component.get("name", component_id))
        findings.append(
            _finding(
                f"code.component.untested.{component_id}",
                "reproducible_verification",
                f"Component {name} has no observable check",
                severity,
                "high",
                evidence,
                f"Component {name} owns code with no observable check, so a proposer cannot verify changes to it.",
                f"Add an observable check (e.g. a focused test) covering {name} before mutating it.",
                verification,
                "needs_code_change",
                "medium",
                weights,
                5,
                4,
                5,
                1,
            )
        )
    return findings


def _component_verification_commands(owned_paths: list[str]) -> list[str]:
    """Return safe, source-bound verification for an untested component finding.

    The finding's definition of done remains "add an observable check"; this
    command is the narrow mechanical smoke that keeps the proposal candidate
    runnable and bound to the component's owned source surface without inventing
    a test file that does not exist yet.
    """
    python_paths = [path for path in owned_paths if path.endswith(".py")]
    return [f"python3 -m ast {path}" for path in python_paths]


def _graph_node_paths(snapshot: dict[str, Any]) -> dict[str, str]:
    nodes = _get(snapshot, "projectGraph", "nodes") or []
    paths: dict[str, str] = {}
    for node in nodes:
        if not isinstance(node, dict):
            continue
        node_id = node.get("id")
        path = node.get("path")
        if isinstance(node_id, str) and isinstance(path, str) and path:
            paths[node_id] = path
    return paths


def _components_with_checks(snapshot: dict[str, Any]) -> set[str]:
    checked: set[str] = set()
    components = [component for component in _get(snapshot, "snapshot", "components") or [] if isinstance(component, dict)]
    all_component_ids = {str(component.get("id")) for component in components if component.get("id")}
    observable_checks = [check for check in _get(snapshot, "snapshot", "observable_checks") or [] if isinstance(check, dict)]
    workspace_check_ids = {
        str(check.get("id"))
        for check in observable_checks
        if _is_workspace_scoped_check(check, all_component_ids)
    }
    for component in components:
        check_ids = [str(check_id) for check_id in component.get("check_ids", [])]
        if any(check_id and check_id not in workspace_check_ids and not _is_workspace_check_id(check_id) for check_id in check_ids):
            checked.add(str(component.get("id")))
    for check in observable_checks:
        if _is_workspace_scoped_check(check, all_component_ids):
            continue
        for component_id in check.get("component_ids", []):
            checked.add(str(component_id))
    return checked


def _is_workspace_scoped_check(check: dict[str, Any], all_component_ids: set[str]) -> bool:
    check_id = str(check.get("id", ""))
    if _is_workspace_check_id(check_id):
        return True
    provenance_refs = [str(ref) for ref in check.get("provenance_refs", []) or check.get("provenanceRefs", [])]
    if any("workspace" in ref.lower() for ref in provenance_refs):
        return True
    component_ids = {str(component_id) for component_id in check.get("component_ids", []) if str(component_id)}
    if len(all_component_ids) > 1 and component_ids and component_ids >= all_component_ids:
        return True
    command = str(check.get("command", "")).strip()
    return len(component_ids) > 1 and _looks_repo_wide_command(command)


def _is_workspace_check_id(check_id: str) -> bool:
    return check_id.startswith("check.workspace-") or check_id.startswith("workspace.")


def _looks_repo_wide_command(command: str) -> bool:
    lowered = command.lower()
    return any(marker in lowered for marker in ("ruff check .", "pytest tests", "pytest -q", "pyright", "mypy ."))


def _absence_findings(project: Path, weights: dict[str, int]) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    for fid, dimension, title, rel_paths, action, impact, risk, verification, docs in _absence_specs():
        checked_paths = _check_paths(rel_paths)
        primary_path = checked_paths[0]
        if _any_path_exists(project, checked_paths):
            continue
        evidence_path = (
            f"iterationReadiness.readinessChecks.{fid}"
            if fid in _READINESS_SIGNAL_FINDINGS
            else primary_path
        )
        evidence: dict[str, Any] = {"kind": "absence", "path": evidence_path, "checked": True}
        if len(checked_paths) > 1 or evidence_path != primary_path:
            evidence["checkedPaths"] = list(checked_paths)
        findings.append(
            _finding(
                fid,
                dimension,
                title,
                _ABSENCE_SEVERITY.get(fid, "medium"),
                "high",
                [evidence],
                f"{primary_path} is absent, reducing future agent or operator understanding.",
                action,
                [f"test -e {primary_path}"],
                "readiness_signal_only" if fid in _READINESS_SIGNAL_FINDINGS else "safe_to_patch_docs_only",
                _ABSENCE_EFFORT.get(fid, "small"),
                weights,
                impact,
                risk,
                verification,
                docs,
            )
        )
    return findings


def _absence_specs() -> list[_AbsenceSpec]:
    return [
        (
            "doc.readme.missing",
            "documentation_project_knowledge",
            "README is missing",
            "README.md",
            "Create a README with purpose, setup, commands, status, and links.",
            5,
            4,
            1,
            5,
        ),
        (
            "doc.index.missing",
            "documentation_project_knowledge",
            "Docs index is missing",
            "docs/index.md",
            "Create docs/index.md as canonical docs navigation.",
            4,
            3,
            1,
            5,
        ),
        (
            "agent.agents-md.missing",
            "ai_agent_usability",
            "AGENTS.md is missing",
            "AGENTS.md",
            "Create AGENTS.md with commands, boundaries, and definition of done.",
            5,
            5,
            2,
            4,
        ),
        (
            "decision.history.missing",
            "decision_history",
            "Decision records are missing",
            "docs/decisions",
            "Create decision records for architecture-significant constraints.",
            3,
            3,
            1,
            4,
        ),
        (
            "ops.runbooks.missing",
            "operations_release_rollback",
            "Runbooks are missing",
            "docs/runbooks",
            "Document start/stop/deploy/rollback/troubleshooting procedures.",
            3,
            4,
            2,
            2,
        ),
        (
            "verification.ci.missing",
            "reproducible_verification",
            "CI configuration is missing",
            (
                ".github/workflows/ci.yml",
                ".github/workflows/*.yml",
                ".github/workflows/*.yaml",
                ".gitlab-ci.yml",
                ".circleci/config.yml",
                "azure-pipelines.yml",
            ),
            "Add a CI workflow or equivalent host CI configuration for the repository test command.",
            1,
            1,
            1,
            1,
        ),
        (
            "verification.lockfile.missing",
            "reproducible_verification",
            "Dependency lockfile is missing",
            ("uv.lock", "package-lock.json", "poetry.lock"),
            "Commit a dependency lockfile so local and CI installs resolve reproducibly.",
            2,
            3,
            3,
            1,
        ),
        (
            "verification.precommit.missing",
            "reproducible_verification",
            "Pre-commit hook configuration is missing",
            ".pre-commit-config.yaml",
            "Add pre-commit hook configuration for repeatable local checks.",
            2,
            2,
            3,
            1,
        ),
        (
            "security.policy.missing",
            "security_supply_chain_hygiene",
            "Security policy is missing",
            "SECURITY.md",
            "Create SECURITY.md with vulnerability reporting and support policy.",
            2,
            4,
            1,
            2,
        ),
        (
            "security.dep-update.missing",
            "security_supply_chain_hygiene",
            "Dependency update configuration is missing",
            (".github/dependabot.yml", "renovate.json"),
            "Add Dependabot or Renovate configuration for dependency update hygiene.",
            2,
            3,
            2,
            1,
        ),
        (
            "governance.contributing.missing",
            "backlog_change_governance",
            "Contributing guide is missing",
            "CONTRIBUTING.md",
            "Create CONTRIBUTING.md with contribution, review, and verification expectations.",
            2,
            2,
            1,
            3,
        ),
        (
            "governance.codeowners.missing",
            "backlog_change_governance",
            "CODEOWNERS is missing",
            ("CODEOWNERS", ".github/CODEOWNERS"),
            "Add CODEOWNERS so ownership and review routing are explicit.",
            2,
            3,
            1,
            1,
        ),
        (
            "governance.templates.missing",
            "backlog_change_governance",
            "Issue or PR templates are missing",
            (
                ".github/pull_request_template.md",
                ".github/ISSUE_TEMPLATE",
                "PULL_REQUEST_TEMPLATE.md",
            ),
            "Add an issue or pull request template with acceptance and verification fields.",
            2,
            2,
            1,
            2,
        ),
        (
            "ops.env-example.missing",
            "operations_release_rollback",
            "Environment example is missing",
            ".env.example",
            "Create .env.example documenting required environment variables without secrets.",
            2,
            3,
            2,
            2,
        ),
        (
            "architecture.overview.missing",
            "architecture_specs_contracts",
            "Architecture overview is missing",
            ("ARCHITECTURE.md", "docs/architecture"),
            "Create an architecture overview that names major components and contracts.",
            4,
            4,
            2,
            4,
        ),
    ]


def _verification_capability_findings(project: Path, weights: dict[str, int]) -> list[dict[str, Any]]:
    if _discover_test_command(project) is not None:
        return []
    return [
        _finding(
            "verification.test-command.missing",
            "reproducible_verification",
            "Declared test command is missing",
            "high",
            "high",
            [
                {
                    "kind": "absence",
                    "path": "iterationReadiness.readinessChecks.verification.test-command.missing",
                    "checked": True,
                    "checkedPaths": list(_TEST_COMMAND_CHECK_PATHS),
                }
            ],
            "No local test command is discoverable from common project manifests, so changes cannot be mechanically verified.",
            "Declare a test command in pyproject.toml, Makefile, package.json, tox.ini, or pytest.ini.",
            [],
            "readiness_signal_only",
            "unknown",
            weights,
            1,
            1,
            1,
            1,
        )
    ]


def _readiness_check_results(project: Path) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for fid, dimension, _title, rel_paths, _action, _impact, _risk, _verification, _docs in _absence_specs():
        results.append(
            {
                "id": fid,
                "dimension": dimension,
                "covered": _any_path_exists(project, _check_paths(rel_paths)),
            }
        )
    results.append(
        {
            "id": "verification.test-command.missing",
            "dimension": "reproducible_verification",
            "covered": _discover_test_command(project) is not None,
        }
    )
    return results


def _dimension_scores(checks: list[dict[str, Any]]) -> dict[str, dict[str, int | float]]:
    counters = {dimension: {"covered": 0, "total": 0} for dimension in DIMENSIONS}
    for check in checks:
        dimension = str(check.get("dimension", ""))
        if dimension not in counters:
            continue
        counters[dimension]["total"] += 1
        if bool(check.get("covered")):
            counters[dimension]["covered"] += 1
    scores: dict[str, dict[str, int | float]] = {}
    for dimension in DIMENSIONS:
        covered = counters[dimension]["covered"]
        total = counters[dimension]["total"]
        scores[dimension] = {
            "covered": covered,
            "total": total,
            "fraction": round(covered / total, 6) if total else 1.0,
        }
    return scores


def _loop_readiness(checks: list[dict[str, Any]]) -> dict[str, Any]:
    by_id = {str(check.get("id", "")): bool(check.get("covered")) for check in checks}
    failing = [
        check_id
        for check_id in ("verification.ci.missing", "verification.test-command.missing")
        if not by_id.get(check_id, False)
    ]
    return {
        "reproducibleVerificationGate": "fail" if failing else "pass",
        "failingChecks": failing,
        "advisory": True,
    }


def _check_paths(rel_paths: str | tuple[str, ...]) -> tuple[str, ...]:
    if isinstance(rel_paths, str):
        return (rel_paths,)
    return rel_paths


def _any_path_exists(project: Path, rel_paths: tuple[str, ...]) -> bool:
    return any(_path_exists(project, rel_path) for rel_path in rel_paths)


def _path_exists(project: Path, rel_path: str) -> bool:
    if any(marker in rel_path for marker in "*?["):
        return any(project.glob(rel_path))
    return (project / rel_path).exists()


def _discover_test_command(project: Path) -> dict[str, str] | None:
    pyproject = project / "pyproject.toml"
    if pyproject.exists() and _pyproject_declares_pytest(pyproject):
        return {"kind": "pyproject", "path": "pyproject.toml", "command": "pytest"}

    makefile = project / "Makefile"
    if makefile.exists() and _makefile_declares_test_target(makefile):
        return {"kind": "makefile", "path": "Makefile", "command": "make test"}

    package_json = project / "package.json"
    package_test = _package_json_test_script(package_json) if package_json.exists() else None
    if package_test:
        return {"kind": "package_json", "path": "package.json", "command": package_test}

    tox_ini = project / "tox.ini"
    if tox_ini.exists():
        return {"kind": "tox", "path": "tox.ini", "command": "tox"}

    pytest_ini = project / "pytest.ini"
    if pytest_ini.exists():
        return {"kind": "pytest_ini", "path": "pytest.ini", "command": "pytest"}

    return None


def _pyproject_declares_pytest(path: Path) -> bool:
    try:
        with path.open("rb") as handle:
            data = tomllib.load(handle)
    except (OSError, tomllib.TOMLDecodeError):
        return False
    tool = data.get("tool")
    if not isinstance(tool, dict):
        return False
    pytest_section = tool.get("pytest")
    if not isinstance(pytest_section, dict):
        return False
    return isinstance(pytest_section.get("ini_options"), dict)


def _makefile_declares_test_target(path: Path) -> bool:
    try:
        content = path.read_text(encoding="utf-8")
    except OSError:
        return False
    return re.search(r"(?m)^test\s*:{1,2}(?:\s|$)", content) is not None


def _package_json_test_script(path: Path) -> str | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(data, dict):
        return None
    scripts = data.get("scripts")
    if not isinstance(scripts, dict):
        return None
    test = scripts.get("test")
    if not isinstance(test, str) or not test.strip():
        return None
    return test


def _quality_gate_findings(snapshot: dict[str, Any], weights: dict[str, int]) -> list[dict[str, Any]]:
    gates = list(_get(snapshot, "iterationReadiness", "qualityGates") or [])
    if gates:
        commands = [str(gate.get("command")) for gate in gates if isinstance(gate, dict) and gate.get("command")]
        return [
            _finding(
                "verification.quality-gates.present",
                "reproducible_verification",
                "Project Model exposes local quality gates",
                "low",
                "high",
                [{"kind": "project_model", "path": "iterationReadiness.qualityGates", "checked": True}],
                "Configured safe local checks are visible to intake and proposer handoff.",
                "Keep these commands linked in future handoff packets.",
                commands,
                "advisory_only",
                "small",
                weights,
                2,
                2,
                4,
                1,
            )
        ]
    return [
        _finding(
            "verification.quality-gates.missing",
            "reproducible_verification",
            "No quality gates are visible in Project Model",
            "high",
            "high",
            [{"kind": "absence", "path": "iterationReadiness.qualityGates", "checked": True}],
            "A proposer cannot choose a verifiable improvement without safe local checks.",
            "Expose safe local test/lint/type/build commands in Project Model v1.",
            [],
            "blocks_autonomous_mutation",
            "medium",
            weights,
            5,
            5,
            5,
            2,
        )
    ]


def _question_and_gap_findings(snapshot: dict[str, Any], weights: dict[str, int]) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    questions = list(_get(snapshot, "iterationReadiness", "openQuestions") or [])
    gaps = list(_get(snapshot, "snapshot", "verification_gaps") or [])
    if questions or gaps:
        findings.append(
            _finding(
                "architecture.open-questions-or-gaps",
                "architecture_specs_contracts",
                "Project Model contains open questions or verification gaps",
                "medium",
                "high",
                [{"kind": "project_model", "path": "iterationReadiness.openQuestions/snapshot.verification_gaps", "checked": True}],
                "Open questions and gaps should be surfaced before proposer mutation.",
                "Convert high-impact gaps into explicit backlog or verification tasks.",
                [],
                "advisory_only",
                "medium",
                weights,
                4,
                4,
                3,
                3,
            )
        )
    return findings


def _finding(
    fid: str,
    dimension: str,
    title: str,
    severity: str,
    confidence: str,
    evidence: list[dict[str, Any]],
    why: str,
    action: str,
    verification: list[str],
    boundary: str,
    effort: str,
    weights: dict[str, int],
    impact: int,
    risk: int,
    verification_gain: int,
    docs: int,
) -> dict[str, Any]:
    return {
        "id": fid,
        "dimension": dimension,
        "title": title,
        "severity": severity,
        "confidence": confidence,
        "evidence": evidence,
        "whyItMatters": why,
        "recommendedAction": action,
        "verification": verification,
        "autonomyBoundary": boundary,
        "estimatedEffort": effort,
        "impactOnFutureIteration": impact,
        "riskReduction": risk,
        "verificationGain": verification_gain,
        "docKnowledgeGain": docs,
        "priorityScore": finding_priority_score(
            dimension_weight=weights[dimension],
            severity=severity,
            confidence=confidence,
            effort=effort,
            impact_on_future_iteration=impact,
            risk_reduction=risk,
            verification_gain=verification_gain,
            doc_knowledge_gain=docs,
        ),
    }


def _improvement_candidates(findings: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "rank": finding["rank"],
            "findingId": finding["id"],
            "title": finding["title"],
            "recommendedAction": finding["recommendedAction"],
            "verification": finding["verification"],
            "priorityScore": finding["priorityScore"],
        }
        for finding in findings
    ]


def _first_recommendation(findings: list[dict[str, Any]]) -> dict[str, Any] | None:
    if not findings:
        return None
    first = findings[0]
    return {
        "findingId": first["id"],
        "title": first["title"],
        "recommendedAction": first["recommendedAction"],
        "verification": first["verification"],
        "whyThisOutranksAlternatives": "Highest deterministic priorityScore after profile weighting, severity, confidence, effort, and gain tie-breaks.",
    }


def _get(payload: dict[str, Any], *keys: str) -> Any:
    current: Any = payload
    for key in keys:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def _sha(payload: Any) -> str:
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


if __name__ == "__main__":
    raise SystemExit(main())
