from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from arena.boundary import DEFAULT_READ_ONLY_DIRS, DEFAULT_READ_ONLY_FILES

SCHEMA_VERSION = "proposer-handoff/v0"


@dataclass(frozen=True)
class ProposerHandoff:
    source_scorecard_id: str
    snapshot_id: str
    freshness_status: str
    selected_finding_id: str
    hypothesis_intent: str
    target_files: tuple[str, ...]
    success_criteria: tuple[str, ...]
    failure_criteria: tuple[str, ...]
    verification_commands: tuple[str, ...]
    rollback_condition: str
    prohibited_paths: tuple[str, ...]
    requires_owner_approval: bool
    evidence_refs: tuple[dict[str, Any], ...]
    advisory_notes: tuple[str, ...]
    not_authorized_for_mutation: bool = True


def build_proposer_handoff(scorecard_path: str | Path, freshness_path: str | Path) -> ProposerHandoff:
    scorecard = _load_json(Path(scorecard_path))
    freshness = _load_json(Path(freshness_path))
    finding = _selected_finding(scorecard)
    verification = tuple(str(item) for item in finding.get("verification", []) if str(item).strip())
    freshness_status = str(freshness.get("status", "unknown"))
    notes: list[str] = ["Prepared handoff is advisory and does not authorize runner mutation."]
    if freshness_status != "fresh":
        notes.append(f"Project Model freshness status is {freshness_status}; mutation remains blocked until refreshed or explicitly approved.")
    requires_owner_approval = not bool(verification)
    if requires_owner_approval:
        notes.append("Selected finding has no verification commands; owner approval or a stronger verification plan is required.")
    return ProposerHandoff(
        source_scorecard_id=str(scorecard.get("id", "")),
        snapshot_id=str(scorecard.get("snapshotId", freshness.get("snapshotId", ""))),
        freshness_status=freshness_status,
        selected_finding_id=str(finding.get("id", "")),
        hypothesis_intent=str(finding.get("recommendedAction") or finding.get("title") or "Prepare bounded improvement from intake finding."),
        target_files=tuple(_target_files(finding)),
        success_criteria=tuple(_success_criteria(finding)),
        failure_criteria=("Target touches a prohibited path.", "Verification commands are absent or fail.", "Freshness status is not fresh."),
        verification_commands=verification,
        rollback_condition="Discard handoff or candidate patch if freshness, boundary, or verification requirements fail.",
        prohibited_paths=tuple([*DEFAULT_READ_ONLY_DIRS, *DEFAULT_READ_ONLY_FILES]),
        requires_owner_approval=requires_owner_approval,
        evidence_refs=tuple(finding.get("evidence", [])),
        advisory_notes=tuple(notes),
        not_authorized_for_mutation=True,
    )


def handoff_to_dict(handoff: ProposerHandoff) -> dict[str, Any]:
    base = {
        "schemaVersion": SCHEMA_VERSION,
        "sourceScorecardId": handoff.source_scorecard_id,
        "snapshotId": handoff.snapshot_id,
        "freshnessStatus": handoff.freshness_status,
        "selectedFindingId": handoff.selected_finding_id,
        "hypothesisIntent": handoff.hypothesis_intent,
        "targetFiles": list(handoff.target_files),
        "successCriteria": list(handoff.success_criteria),
        "failureCriteria": list(handoff.failure_criteria),
        "verificationCommands": list(handoff.verification_commands),
        "rollbackCondition": handoff.rollback_condition,
        "prohibitedPaths": list(handoff.prohibited_paths),
        "requiresOwnerApproval": handoff.requires_owner_approval,
        "evidenceRefs": list(handoff.evidence_refs),
        "advisoryNotes": list(handoff.advisory_notes),
        "notAuthorizedForMutation": handoff.not_authorized_for_mutation,
    }
    return {**base, "id": hashlib.sha256(json.dumps(base, sort_keys=True, separators=(",", ":")).encode()).hexdigest()[:16]}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m arena.proposer_handoff")
    parser.add_argument("--scorecard", required=True)
    parser.add_argument("--freshness", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args(argv)
    packet = handoff_to_dict(build_proposer_handoff(args.scorecard, args.freshness))
    Path(args.output).write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def _selected_finding(scorecard: dict[str, Any]) -> dict[str, Any]:
    selected_id = (scorecard.get("firstRecommendedImprovement") or {}).get("findingId")
    findings = [finding for finding in scorecard.get("findings", []) if isinstance(finding, dict)]
    if selected_id:
        for finding in findings:
            if finding.get("id") == selected_id:
                return finding
    if findings:
        return findings[0]
    raise ValueError("scorecard contains no finding to hand off")


def _target_files(finding: dict[str, Any]) -> list[str]:
    files: list[str] = []
    for evidence in finding.get("evidence", []):
        if not isinstance(evidence, dict):
            continue
        path = evidence.get("path")
        if isinstance(path, str) and path and not path.startswith("iterationReadiness"):
            files.append(path)
    return sorted(dict.fromkeys(files))


def _success_criteria(finding: dict[str, Any]) -> list[str]:
    criteria = [str(finding.get("recommendedAction") or finding.get("title") or "Complete selected finding.")]
    criteria.extend(str(command) for command in finding.get("verification", []) if str(command).strip())
    return criteria


if __name__ == "__main__":
    raise SystemExit(main())
