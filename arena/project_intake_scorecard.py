from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
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
    findings.extend(_quality_gate_findings(snapshot, weights))
    findings.extend(_question_and_gap_findings(snapshot, weights))
    return findings


def _absence_findings(project: Path, weights: dict[str, int]) -> list[dict[str, Any]]:
    specs = [
        ("doc.readme.missing", "documentation_project_knowledge", "README is missing", "README.md", "Create a README with purpose, setup, commands, status, and links.", 5, 4, 1, 5),
        ("doc.index.missing", "documentation_project_knowledge", "Docs index is missing", "docs/index.md", "Create docs/index.md as canonical docs navigation.", 4, 3, 1, 5),
        ("agent.agents-md.missing", "ai_agent_usability", "AGENTS.md is missing", "AGENTS.md", "Create AGENTS.md with commands, boundaries, and definition of done.", 5, 5, 2, 4),
        ("decision.history.missing", "decision_history", "Decision records are missing", "docs/decisions", "Create decision records for architecture-significant constraints.", 3, 3, 1, 4),
        ("ops.runbooks.missing", "operations_release_rollback", "Runbooks are missing", "docs/runbooks", "Document start/stop/deploy/rollback/troubleshooting procedures.", 3, 4, 2, 2),
    ]
    findings: list[dict[str, Any]] = []
    for fid, dimension, title, rel_path, action, impact, risk, verification, docs in specs:
        if (project / rel_path).exists():
            continue
        findings.append(
            _finding(
                fid,
                dimension,
                title,
                "high" if fid in {"doc.readme.missing", "agent.agents-md.missing"} else "medium",
                "high",
                [{"kind": "absence", "path": rel_path, "checked": True}],
                f"{rel_path} is absent, reducing future agent or operator understanding.",
                action,
                [f"test -e {rel_path}"],
                "safe_to_patch_docs_only",
                "small",
                weights,
                impact,
                risk,
                verification,
                docs,
            )
        )
    return findings


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
