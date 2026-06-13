from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path, PurePosixPath
from typing import Any

from arena.fingerprints import compute_fingerprint
from arena.generated.models import Hypothesis
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
    if max_candidates <= 0:
        raise ValueError("max_candidates must be positive")
    project_path = Path(project).resolve()
    scorecard = _load_json(Path(scorecard_path))
    facts = collect_repo_facts(project_path)
    findings = _ranked_findings(scorecard)
    intake_context_block = _intake_context_block(findings)
    require_source_references = _requires_source_references(project_path, facts)
    planned: list[ProposalCandidate] = []
    skipped: list[dict[str, Any]] = []
    for finding in findings:
        target_path = _single_target_path(finding)
        if target_path is None:
            skipped.append(_skipped_finding(finding, "no_single_file_target"))
            continue
        planned.append(
            _candidate_from_finding(
                finding,
                target_path,
                facts,
                intake_context_block,
                len(planned) + 1,
                require_source_references=require_source_references,
            )
        )
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


def _single_target_path(finding: dict[str, Any]) -> str | None:
    paths: list[str] = []
    for evidence in finding.get("evidence", []):
        if not isinstance(evidence, dict):
            continue
        raw = evidence.get("path")
        if not isinstance(raw, str) or not raw.strip() or raw.startswith("iterationReadiness"):
            continue
        path = PurePosixPath(raw.replace("\\", "/"))
        if path.is_absolute() or ".." in path.parts:
            continue
        paths.append(_proposal_target_for_evidence_path(path))
    unique = tuple(dict.fromkeys(paths))
    return unique[0] if len(unique) == 1 else None


def _proposal_target_for_evidence_path(path: PurePosixPath) -> str:
    if path.suffix:
        return path.as_posix()
    return (path / "index.md").as_posix()


def _skipped_finding(finding: dict[str, Any], reason: str) -> dict[str, Any]:
    return {
        "finding_id": str(finding.get("id", "")),
        "rank": int(finding.get("rank", 0) or 0),
        "title": str(finding.get("title", "")),
        "reason": reason,
        "evidence_paths": [str(evidence.get("path", "")) for evidence in finding.get("evidence", []) if isinstance(evidence, dict) and evidence.get("path")],
    }


def _candidate_from_finding(
    finding: dict[str, Any],
    target_path: str,
    facts: RepoFacts,
    intake_context_block: str,
    rank: int,
    *,
    require_source_references: bool,
) -> ProposalCandidate:
    finding_id = str(finding.get("id", ""))
    source_action = str(finding.get("recommendedAction", ""))
    facts_block = "\n".join(part for part in (facts.to_prompt_block(), intake_context_block) if part)
    if finding_id == "doc.index.missing" or target_path == "docs/index.md":
        intent = "Create a grounded docs/index.md that links only to existing repository files and names missing future documentation topics by title only, with no filename or extension."
        success, constraints, verification = _markdown_success_contract(target_path, require_source_references=require_source_references)
    elif target_path == "AGENTS.md":
        intent = "Create a grounded AGENTS.md for future agents using existing repository facts, commands, and boundaries."
        success, constraints, verification = _markdown_success_contract(target_path, require_source_references=require_source_references)
    elif target_path.endswith(".md"):
        title = str(finding.get("title") or finding_id or target_path)
        intent = f"Create a grounded Markdown file at {target_path} that addresses finding {finding_id}: {title}."
        success, constraints, verification = _markdown_success_contract(target_path, require_source_references=require_source_references)
    else:
        title = str(finding.get("title") or finding_id or target_path)
        intent = f"Prepare a grounded one-file improvement for {target_path} based on finding {finding_id}: {title}."
        success = f"{target_path} is changed in a bounded, repository-grounded way and project verification remains green."
        constraints = ("Use only repository facts and current file contents; do not invent project structure, files, or commands.",)
        verification = tuple(str(command) for command in finding.get("verification", []) if str(command).strip())
    return ProposalCandidate(
        rank=rank,
        finding_id=finding_id,
        title=str(finding.get("title", "")),
        target_path=target_path,
        intent=intent,
        success_criterion=success,
        repo_facts_hash=facts.content_hash,
        repo_facts_block=facts_block,
        grounding_constraints=constraints,
        verification_commands=verification,
        priority_score=float(finding.get("priorityScore", 0.0)),
        evidence_refs=tuple(evidence for evidence in finding.get("evidence", []) if isinstance(evidence, dict)),
        source_recommended_action=source_action,
    )


def _markdown_success_contract(target_path: str, *, require_source_references: bool = False) -> tuple[str, tuple[str, ...], tuple[str, ...]]:
    success = f"{target_path} exists, is non-empty, and all local Markdown links resolve to existing repository files."
    constraints = [
        "Do not invent Markdown links to files absent from the repository facts.",
        "If a future documentation topic has no existing file, describe it by title only, with no filename or extension.",
        "Local Markdown links must resolve after the patch is applied.",
    ]
    verification = [f"test -s {target_path}", f"python3 -m arena.markdown_links --repo . --path {target_path}"]
    if require_source_references:
        success += " It includes a Source references section citing at least one existing repository file."
        constraints.append("Include a `## Source references` section that cites existing repository files for factual or compliance claims.")
        verification[-1] = f"python3 -m arena.markdown_links --repo . --path {target_path} --require-source-references"
    return (success, tuple(constraints), tuple(verification))


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
