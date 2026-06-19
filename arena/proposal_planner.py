from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from arena.fingerprints import compute_fingerprint
from arena.generated.models import Hypothesis
from arena.graph_slice import fresh_graph_slice
from arena.proposal_domains import (
    DomainContext,
    ProposalCandidateDraft,
    ProposalDomainRegistry,
    default_domain_registry,
)
from arena.proposal_registry import (
    ProposalLineage,
    ProposalRegistry,
    capture_git_lineage,
    proposal_key_for,
)
from arena.repo_facts import RepoFacts, collect_repo_facts

SCHEMA_VERSION = "proposal-plan/v0"
TECHNIQUE_TAG = "diff_proposal"
CANDIDATE_DISPOSITIONS = {"docs_candidate", "code_candidate", "fitness_function_candidate", "advisory_backlogged"}


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
    target_paths: tuple[str, ...]
    base_lineage: dict[str, Any]
    intent_hash: str
    proposal_key: str
    registry_status: str

    def to_jsonable(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["grounding_constraints"] = list(self.grounding_constraints)
        payload["verification_commands"] = list(self.verification_commands)
        payload["evidence_refs"] = list(self.evidence_refs)
        payload["target_paths"] = list(self.target_paths)
        payload["base_lineage"] = dict(self.base_lineage)
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
    finding_dispositions: tuple[dict[str, Any], ...]
    candidates: tuple[ProposalCandidate, ...]
    base_lineage: dict[str, Any]

    def to_jsonable(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "schemaVersion": self.schema_version,
            "sourceScorecardId": self.source_scorecard_id,
            "snapshotId": self.snapshot_id,
            "projectRoot": self.project_root,
            "repoFactsHash": self.repo_facts_hash,
            "baseLineage": dict(self.base_lineage),
            "candidateCount": self.candidate_count,
            "omittedCount": self.omitted_count,
            "skippedCount": self.skipped_count,
            "skippedFindings": list(self.skipped_findings),
            "findingDispositions": list(self.finding_dispositions),
            "candidates": [candidate.to_jsonable() for candidate in self.candidates],
        }


def build_proposal_plan(
    project: str | Path,
    scorecard_path: str | Path,
    *,
    max_candidates: int = 10,
    proposal_registry: ProposalRegistry | None = None,
    run_id: str = "",
) -> ProposalPlan:
    """Build the proposal plan using the default multi-domain registry.

    Thin wrapper preserving the original public signature/behaviour; the actual
    orchestration lives in ``build_proposal_plan_with_registry``."""
    return build_proposal_plan_with_registry(
        project,
        scorecard_path,
        default_domain_registry(),
        max_candidates=max_candidates,
        proposal_registry=proposal_registry,
        run_id=run_id,
    )


def build_proposal_plan_with_registry(
    project: str | Path,
    scorecard_path: str | Path,
    registry: ProposalDomainRegistry,
    *,
    max_candidates: int = 10,
    proposal_registry: ProposalRegistry | None = None,
    run_id: str = "",
) -> ProposalPlan:
    if max_candidates <= 0:
        raise ValueError("max_candidates must be positive")
    project_path = Path(project).resolve()
    scorecard_file = Path(scorecard_path)
    scorecard = _load_json(scorecard_file)
    facts = collect_repo_facts(project_path)
    findings = _ranked_findings(scorecard)
    scorecard_hash = _file_sha(scorecard_file)
    lineage = capture_git_lineage(
        project_path,
        project_id=project_path.name,
        snapshot_id=str(scorecard.get("snapshotId", "")),
        snapshot_hash=str(scorecard.get("snapshotHash", "")),
        scorecard_id=str(scorecard.get("id", "")),
        scorecard_hash=scorecard_hash,
        run_id=run_id,
    )
    context = build_domain_context(
        project_path,
        scorecard,
        facts,
        require_source_references=_requires_source_references(project_path, facts),
    )
    facts_block = "\n".join(part for part in (facts.to_prompt_block(), context.intake_context_block) if part)
    planned: list[ProposalCandidate] = []
    skipped: list[dict[str, Any]] = []
    dispositions: list[dict[str, Any]] = []
    for finding in findings:
        if _is_consumed_context_finding(finding):
            disposition = _finding_disposition(finding, "consumed_as_context")
            dispositions.append(disposition)
            skipped.append(_skipped_from_disposition(disposition))
            continue
        result = registry.first_candidate(finding, context)
        if result is None:
            disposition = _finding_disposition(finding, "no_single_file_target")
            dispositions.append(disposition)
            skipped.append(_skipped_from_disposition(disposition))
            continue
        domain_name, draft = result
        candidate = _candidate_from_draft(
            finding,
            draft,
            facts,
            facts_block,
            len(planned) + 1,
            domain_name=domain_name,
            lineage=lineage,
            proposal_registry=proposal_registry,
            run_id=run_id,
        )
        dispositions.append(
            _finding_disposition(
                finding,
                _candidate_disposition_for_domain(domain_name),
                domain=domain_name,
                target_path=candidate.target_path,
            )
        )
        if candidate.registry_status == "promoted":
            skipped.append(_skipped_finding(finding, "promoted_in_registry"))
            continue
        planned.append(candidate)
    limited = tuple(planned[:max_candidates])
    base = {
        "schemaVersion": SCHEMA_VERSION,
        "sourceScorecardId": str(scorecard.get("id", "")),
        "snapshotId": str(scorecard.get("snapshotId", "")),
        "projectRoot": str(project_path),
        "repoFactsHash": facts.content_hash,
        "baseLineage": lineage.to_jsonable(),
        "candidateCount": len(planned),
        "omittedCount": max(0, len(planned) - len(limited)),
        "skippedCount": len(skipped),
        "skippedFindings": skipped,
        "findingDispositions": dispositions,
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
        finding_dispositions=tuple(dispositions),
        candidates=limited,
        base_lineage=lineage.to_jsonable(),
    )


def candidate_to_hypothesis(candidate: ProposalCandidate, *, cycle_id: str, plan_id: str | None = None) -> Hypothesis:
    fingerprint = compute_fingerprint(
        intent=candidate.intent,
        target_files=tuple(candidate.target_paths),
        technique_tag=TECHNIQUE_TAG,
        ast_diff_pattern="grounded_proposal_plan_v0",
        first_seen_cycle_id=cycle_id,
    )
    digest = hashlib.sha256(f"{cycle_id}\0{candidate.finding_id}\0{','.join(candidate.target_paths)}".encode()).hexdigest()[:12]
    return Hypothesis(
        id=f"hyp-{cycle_id}-{digest}",
        cycle_id=cycle_id,
        intent=candidate.intent,
        technique_tag=TECHNIQUE_TAG,
        target_cluster=candidate.target_path,
        target_files=list(candidate.target_paths),
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


def build_domain_context(
    project_path: Path,
    scorecard: dict[str, Any],
    facts: RepoFacts,
    *,
    require_source_references: bool,
) -> DomainContext:
    """Build the shared context consumed by planner and ranker domains.

    Advisory text comes from the scorecard's v1 snapshot when available. The
    graph slice is rebuilt from current filesystem/git state, matching the
    anti-fabrication rule that cached projections are not authoritative for
    scanner/scorer decisions.
    """
    findings = _ranked_findings(scorecard)
    snapshot = _snapshot_from_scorecard(scorecard)
    quality_gate_commands = _quality_gate_commands(findings)
    return DomainContext(
        project_name=project_path.name,
        facts=facts,
        intake_context_block=_intake_context_block(findings),
        require_source_references=require_source_references,
        open_questions=_snapshot_items(snapshot, "iterationReadiness", "openQuestions"),
        verification_gaps=_snapshot_items(snapshot, "snapshot", "verification_gaps"),
        graph_slice=fresh_graph_slice(project_path),
        extras={"quality_gate_commands": quality_gate_commands},
    )


def _snapshot_from_scorecard(scorecard: dict[str, Any]) -> dict[str, Any]:
    snapshot_path = scorecard.get("snapshotPath")
    if not isinstance(snapshot_path, str) or not snapshot_path.strip():
        return {}
    path = Path(snapshot_path)
    if not path.is_file():
        return {}
    try:
        return _load_json(path)
    except (OSError, ValueError, json.JSONDecodeError):
        return {}


def _snapshot_items(snapshot: dict[str, Any], *keys: str) -> tuple[dict[str, Any], ...]:
    current: Any = snapshot
    for key in keys:
        if not isinstance(current, dict):
            return ()
        current = current.get(key)
    if not isinstance(current, list):
        return ()
    items = [json.loads(json.dumps(item, sort_keys=True)) for item in current if isinstance(item, dict)]
    return tuple(sorted(items, key=_stable_json))


def _stable_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def _is_consumed_context_finding(finding: dict[str, Any]) -> bool:
    return str(finding.get("id", "")) == "verification.quality-gates.present"


def _candidate_disposition_for_domain(domain_name: str) -> str:
    if domain_name in {"documentation", "model_level"}:
        return "docs_candidate"
    if domain_name == "architecture_fitness":
        return "fitness_function_candidate"
    if domain_name == "advisory_backlog":
        return "advisory_backlogged"
    return "code_candidate"


def _finding_disposition(
    finding: dict[str, Any],
    disposition: str,
    *,
    domain: str = "",
    target_path: str = "",
) -> dict[str, Any]:
    return {
        "finding_id": str(finding.get("id", "")),
        "rank": int(finding.get("rank", 0) or 0),
        "title": str(finding.get("title", "")),
        "disposition": disposition,
        "domain": domain,
        "target_path": target_path,
        "evidence_paths": _evidence_paths(finding),
    }


def _skipped_from_disposition(disposition: dict[str, Any]) -> dict[str, Any]:
    return {
        "finding_id": str(disposition.get("finding_id", "")),
        "rank": int(disposition.get("rank", 0) or 0),
        "title": str(disposition.get("title", "")),
        "reason": str(disposition.get("disposition", "")),
        "evidence_paths": [str(path) for path in disposition.get("evidence_paths", []) if str(path)],
    }


def _evidence_paths(finding: dict[str, Any]) -> list[str]:
    return [str(evidence.get("path", "")) for evidence in finding.get("evidence", []) if isinstance(evidence, dict) and evidence.get("path")]


def _skipped_finding(finding: dict[str, Any], reason: str) -> dict[str, Any]:
    return {
        "finding_id": str(finding.get("id", "")),
        "rank": int(finding.get("rank", 0) or 0),
        "title": str(finding.get("title", "")),
        "reason": reason,
        "evidence_paths": _evidence_paths(finding),
    }


def _candidate_from_draft(
    finding: dict[str, Any],
    draft: ProposalCandidateDraft,
    facts: RepoFacts,
    facts_block: str,
    rank: int,
    *,
    domain_name: str = "",
    lineage: ProposalLineage | None = None,
    proposal_registry: ProposalRegistry | None = None,
    run_id: str = "",
) -> ProposalCandidate:
    """Attach finding-level metadata (rank, score, evidence, provenance) to a
    domain-produced draft to form the final ranked candidate."""
    target_paths = draft.target_paths or (draft.target_path,)
    intent_hash = _sha(
        {
            "intent": draft.intent,
            "successCriterion": draft.success_criterion,
            "targetPaths": list(target_paths),
            "verificationCommands": list(draft.verification_commands),
        }
    )
    lineage_payload = lineage.to_jsonable() if lineage is not None else {}
    proposal_key = proposal_key_for(
        project_id=str(lineage.project_id if lineage else ""),
        base_head_oid=str(lineage.base_head_oid if lineage else ""),
        target_paths=target_paths,
        finding_id=str(finding.get("id", "")),
        domain=domain_name,
        intent_hash=intent_hash,
        content_hash=facts.content_hash,
    )
    registry_status = "untracked"
    if proposal_registry is not None and lineage is not None:
        record = proposal_registry.record_pending(
            proposal_key=proposal_key,
            finding_id=str(finding.get("id", "")),
            target_paths=target_paths,
            lineage=lineage,
            payload={"domain": domain_name, "intentHash": intent_hash, "targetPath": draft.target_path},
            run_id=run_id,
        )
        registry_status = record.status
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
        target_paths=target_paths,
        base_lineage=lineage_payload,
        intent_hash=intent_hash,
        proposal_key=proposal_key,
        registry_status=registry_status,
    )


def _requires_source_references(project_path: Path, facts: RepoFacts) -> bool:
    """Documentation candidates always need source references.

    This started as a compliance-sensitive-only policy, but production live runs
    need a stronger default docs gate: generated Markdown must cite existing
    repository files for factual grounding rather than merely being non-empty
    with resolvable links.
    """
    _ = (project_path, facts)
    return True


def _intake_context_block(findings: list[dict[str, Any]]) -> str:
    quality_gate_commands = list(_quality_gate_commands(findings))
    boundaries: list[str] = []
    for finding in findings:
        boundary = finding.get("autonomyBoundary")
        if isinstance(boundary, str) and boundary.strip():
            boundaries.append(boundary.strip())
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


def _file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _quality_gate_commands(findings: list[dict[str, Any]]) -> tuple[str, ...]:
    commands: list[str] = []
    for finding in findings:
        if str(finding.get("id", "")) != "verification.quality-gates.present":
            continue
        for command in finding.get("verification", []):
            if isinstance(command, str) and command.strip():
                commands.append(command.strip())
    return tuple(dict.fromkeys(commands))


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
