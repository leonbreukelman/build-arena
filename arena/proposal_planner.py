from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from arena.fingerprints import compute_fingerprint
from arena.generated.models import Hypothesis
from arena.proposal_domains import (
    DomainContext,
    ProposalCandidateDraft,
    ProposalDomainRegistry,
    default_domain_registry,
)
from arena.repo_facts import RepoFacts, collect_repo_facts

SCHEMA_VERSION = "proposal-plan/v0"
TECHNIQUE_TAG = "diff_proposal"


@dataclass(frozen=True)
class ProposalCandidate:
    rank: int
    finding_id: str
    title: str
    target_path: str
    intent: str
    success_criterion: str
    repo_facts_hash: str
    repo_facts_block: str
    grounding_constraints: tuple[str, ...]
    verification_commands: tuple[str, ...]
    priority_score: float
    evidence_refs: tuple[dict[str, Any], ...]
    source_recommended_action: str

    def to_jsonable(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["grounding_constraints"] = list(self.grounding_constraints)
        payload["verification_commands"] = list(self.verification_commands)
        payload["evidence_refs"] = list(self.evidence_refs)
        return payload


@dataclass(frozen=True)
class ProposalPlan:
    id: str
    schema_version: str
    source_scorecard_id: str
    snapshot_id: str
    project_root: str
    repo_facts_hash: str
    candidate_count: int
    omitted_count: int
    skipped_count: int
    skipped_findings: tuple[dict[str, Any], ...]
    candidates: tuple[ProposalCandidate, ...]

    def to_jsonable(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "schemaVersion": self.schema_version,
            "sourceScorecardId": self.source_scorecard_id,
            "snapshotId": self.snapshot_id,
            "projectRoot": self.project_root,
            "repoFactsHash": self.repo_facts_hash,
            "candidateCount": self.candidate_count,
            "omittedCount": self.omitted_count,
            "skippedCount": self.skipped_count,
            "skippedFindings": list(self.skipped_findings),
            "candidates": [candidate.to_jsonable() for candidate in self.candidates],
        }


def build_proposal_plan(project: str | Path, scorecard_path: str | Path, *, max_candidates: int = 10) -> ProposalPlan:
    """Build the proposal plan using the default multi-domain registry.

    Thin wrapper preserving the original public signature/behaviour; the actual
    orchestration lives in ``build_proposal_plan_with_registry``."""
    return build_proposal_plan_with_registry(
        project, scorecard_path, default_domain_registry(), max_candidates=max_candidates
    )


def build_proposal_plan_with_registry(
    project: str | Path,
    scorecard_path: str | Path,
    registry: ProposalDomainRegistry,
    *,
    max_candidates: int = 10,
) -> ProposalPlan:
    if max_candidates <= 0:
        raise ValueError("max_candidates must be positive")
    project_path = Path(project).resolve()
    scorecard = _load_json(Path(scorecard_path))
    facts = collect_repo_facts(project_path)
    findings = _ranked_findings(scorecard)
    intake_context_block = _intake_context_block(findings)
    context = DomainContext(
        project_name=project_path.name,
        facts=facts,
        intake_context_block=intake_context_block,
        require_source_references=_requires_source_references(project_path, facts),
    )
    facts_block = "\n".join(part for part in (facts.to_prompt_block(), intake_context_block) if part)
    planned: list[ProposalCandidate] = []
    skipped: list[dict[str, Any]] = []
    for finding in findings:
        result = registry.first_candidate(finding, context)
        if result is None:
            skipped.append(_skipped_finding(finding, "no_single_file_target"))
            continue
        _domain_name, draft = result
        planned.append(_candidate_from_draft(finding, draft, facts, facts_block, len(planned) + 1))
    limited = tuple(planned[:max_candidates])
    base = {
        "schemaVersion": SCHEMA_VERSION,
        "sourceScorecardId": str(scorecard.get("id", "")),
        "snapshotId": str(scorecard.get("snapshotId", "")),
        "projectRoot": str(project_path),
        "repoFactsHash": facts.content_hash,
        "candidateCount": len(planned),
        "omittedCount": max(0, len(planned) - len(limited)),
        "skippedCount": len(skipped),
        "skippedFindings": skipped,
        "candidates": [candidate.to_jsonable() for candidate in limited],
    }
    return ProposalPlan(
        id=_sha(base)[:16],
        schema_version=SCHEMA_VERSION,
        source_scorecard_id=base["sourceScorecardId"],
        snapshot_id=base["snapshotId"],
        project_root=base["projectRoot"],
        repo_facts_hash=facts.content_hash,
        candidate_count=len(planned),
        omitted_count=max(0, len(planned) - len(limited)),
        skipped_count=len(skipped),
        skipped_findings=tuple(skipped),
        candidates=limited,
    )


def candidate_to_hypothesis(candidate: ProposalCandidate, *, cycle_id: str, plan_id: str | None = None) -> Hypothesis:
    fingerprint = compute_fingerprint(
        intent=candidate.intent,
        target_files=(candidate.target_path,),
        technique_tag=TECHNIQUE_TAG,
        ast_diff_pattern="grounded_proposal_plan_v0",
        first_seen_cycle_id=cycle_id,
    )
    digest = hashlib.sha256(f"{cycle_id}\0{candidate.finding_id}\0{candidate.target_path}".encode()).hexdigest()[:12]
    return Hypothesis(
        id=f"hyp-{cycle_id}-{digest}",
        cycle_id=cycle_id,
        intent=candidate.intent,
        technique_tag=TECHNIQUE_TAG,
        target_cluster=candidate.target_path,
        target_files=[candidate.target_path],
        fingerprint_id=fingerprint.id,
        reasoning_blob_sha=plan_id or "",
        proposed_ts=0.0,
    )


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def _ranked_findings(scorecard: dict[str, Any]) -> list[dict[str, Any]]:
    findings = [finding for finding in scorecard.get("findings", []) if isinstance(finding, dict)]
    return sorted(
        findings,
        key=lambda finding: (
            int(finding.get("rank", 999999)),
            -float(finding.get("priorityScore", 0.0)),
            str(finding.get("id", "")),
        ),
    )


def _skipped_finding(finding: dict[str, Any], reason: str) -> dict[str, Any]:
    return {
        "finding_id": str(finding.get("id", "")),
        "rank": int(finding.get("rank", 0) or 0),
        "title": str(finding.get("title", "")),
        "reason": reason,
        "evidence_paths": [str(evidence.get("path", "")) for evidence in finding.get("evidence", []) if isinstance(evidence, dict) and evidence.get("path")],
    }


def _candidate_from_draft(
    finding: dict[str, Any],
    draft: ProposalCandidateDraft,
    facts: RepoFacts,
    facts_block: str,
    rank: int,
) -> ProposalCandidate:
    """Attach finding-level metadata (rank, score, evidence, provenance) to a
    domain-produced draft to form the final ranked candidate."""
    return ProposalCandidate(
        rank=rank,
        finding_id=str(finding.get("id", "")),
        title=str(finding.get("title", "")),
        target_path=draft.target_path,
        intent=draft.intent,
        success_criterion=draft.success_criterion,
        repo_facts_hash=facts.content_hash,
        repo_facts_block=facts_block,
        grounding_constraints=tuple(draft.grounding_constraints),
        verification_commands=tuple(draft.verification_commands),
        priority_score=float(finding.get("priorityScore", 0.0)),
        evidence_refs=tuple(evidence for evidence in finding.get("evidence", []) if isinstance(evidence, dict)),
        source_recommended_action=str(finding.get("recommendedAction", "")),
    )


def _requires_source_references(project_path: Path, facts: RepoFacts) -> bool:
    signals = [project_path.name, *facts.top_level_files, *facts.top_level_dirs, *facts.markdown_files]
    joined = "\n".join(signals).lower()
    return any(term in joined for term in ("cmmc", "compliance", "control", "readiness", "readyness"))


def _intake_context_block(findings: list[dict[str, Any]]) -> str:
    quality_gate_commands: list[str] = []
    boundaries: list[str] = []
    for finding in findings:
        boundary = finding.get("autonomyBoundary")
        if isinstance(boundary, str) and boundary.strip():
            boundaries.append(boundary.strip())
        if str(finding.get("id", "")) == "verification.quality-gates.present":
            for command in finding.get("verification", []):
                if isinstance(command, str) and command.strip():
                    quality_gate_commands.append(command.strip())
    lines: list[str] = []
    if quality_gate_commands:
        lines.append("Quality gate commands:")
        lines.extend(f"- {command}" for command in dict.fromkeys(quality_gate_commands))
    if boundaries:
        lines.append("Autonomy boundaries from intake:")
        lines.extend(f"- {boundary}" for boundary in dict.fromkeys(boundaries))
    return "\n".join(lines)


def _sha(payload: dict[str, Any]) -> str:
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m arena.proposal_planner")
    parser.add_argument("--project", required=True)
    parser.add_argument("--scorecard", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--max-candidates", type=int, default=10)
    args = parser.parse_args(argv)
    plan = build_proposal_plan(args.project, args.scorecard, max_candidates=args.max_candidates)
    Path(args.output).write_text(json.dumps(plan.to_jsonable(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
