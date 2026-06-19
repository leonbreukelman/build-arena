"""Cross-domain proposal ranker for Build Arena (epic #25, Phase 4, issue #30).

Phases 1-3 made intake emit findings across documentation AND code, and Phase 2
gave each finding a domain. This module produces the single **ranked top-N
across all domains** — the operator-facing "what should this repo improve next"
answer — using the same explainable weighted formula the intake scorecard uses
(``finding_priority_score``), recomputed here from each finding's breakdown
inputs + the profile weights so the ranking math is pinned and auditable rather
than trusted from a stored value.

Each ranked entry carries its full score breakdown (dimension weight, severity/
confidence/effort multipliers, gain components, formula, computed score) so the
ranking is explainable, plus enumerated omitted (dropped by max_candidates) and
skipped (no domain could target) accounting.

Determinism: candidates are ranked by (-score, -severity, -confidence, +effort,
id); the artifact hash is stable for a stable input. No live providers, no
network.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from arena.project_intake_scorecard import (
    _CONFIDENCE,
    _EFFORT,
    _SEVERITY,
    PROFILE_WEIGHTS,
    finding_priority_score,
)
from arena.proposal_domains import ProposalDomainRegistry, default_domain_registry
from arena.proposal_planner import _is_consumed_context_finding, build_domain_context
from arena.repo_facts import collect_repo_facts

SCHEMA_VERSION = "ranked-proposals/v0"

_FORMULA = "dimensionWeight * severityMultiplier * confidenceMultiplier * totalGain / effortDivisor"


@dataclass(frozen=True)
class RankedEntry:
    rank: int
    finding_id: str
    domain: str
    target_path: str
    title: str
    priority_score: float
    autonomy_boundary: str
    score_breakdown: dict[str, Any]

    def to_jsonable(self) -> dict[str, Any]:
        return {
            "rank": self.rank,
            "findingId": self.finding_id,
            "domain": self.domain,
            "targetPath": self.target_path,
            "title": self.title,
            "priorityScore": self.priority_score,
            "autonomyBoundary": self.autonomy_boundary,
            "scoreBreakdown": self.score_breakdown,
        }


@dataclass(frozen=True)
class RankedProposals:
    schema_version: str
    source_scorecard_id: str
    project_root: str
    profile: str
    candidate_count: int
    omitted_count: int
    skipped_count: int
    entries: tuple[RankedEntry, ...]
    omitted: tuple[dict[str, Any], ...]
    skipped: tuple[dict[str, Any], ...]
    plan_hash: str

    def to_jsonable(self) -> dict[str, Any]:
        return {
            "schemaVersion": self.schema_version,
            "sourceScorecardId": self.source_scorecard_id,
            "projectRoot": self.project_root,
            "profile": self.profile,
            "candidateCount": self.candidate_count,
            "omittedCount": self.omitted_count,
            "skippedCount": self.skipped_count,
            "entries": [entry.to_jsonable() for entry in self.entries],
            "omitted": list(self.omitted),
            "skipped": list(self.skipped),
            "planHash": self.plan_hash,
        }


def rank_entries_to_jsonable(entries: tuple[RankedEntry, ...] | list[RankedEntry]) -> list[dict[str, Any]]:
    return [entry.to_jsonable() for entry in entries]


def build_ranked_proposals(
    project: str | Path,
    scorecard_path: str | Path,
    *,
    max_candidates: int = 10,
    registry: ProposalDomainRegistry | None = None,
) -> RankedProposals:
    if max_candidates <= 0:
        raise ValueError("max_candidates must be positive")
    project_path = Path(project).resolve()
    scorecard = _load_json(Path(scorecard_path))
    profile = str(scorecard.get("profile", "new-project"))
    if profile not in PROFILE_WEIGHTS:
        raise ValueError(f"unknown profile: {profile}")
    # Honor the weights the scorecard actually recorded, so re-ranking an existing
    # scorecard stays faithful to the intake run that produced it even if the live
    # PROFILE_WEIGHTS table is later edited. Fall back to the table only if the
    # scorecard predates stored weights.
    stored_weights = scorecard.get("weights")
    weights = stored_weights if isinstance(stored_weights, dict) and stored_weights else PROFILE_WEIGHTS[profile]
    domain_registry = registry or default_domain_registry()

    facts = collect_repo_facts(project_path)
    context = build_domain_context(
        project_path,
        scorecard,
        facts,
        require_source_references=True,
    )

    findings = [f for f in scorecard.get("findings", []) if isinstance(f, dict)]

    scored: list[tuple[tuple[float, float, float, float, str], RankedEntry]] = []
    skipped: list[dict[str, Any]] = []
    for finding in findings:
        if _is_consumed_context_finding(finding):
            skipped.append(_skipped(finding, "consumed_as_context"))
            continue
        result = domain_registry.first_candidate(finding, context)
        if result is None:
            skipped.append(_skipped(finding, "no_single_file_target"))
            continue
        domain_name, draft = result
        breakdown = _score_breakdown(finding, weights)
        sort_key = (
            -breakdown["computedScore"],
            -_SEVERITY.get(str(finding.get("severity", "low")), 1.0),
            -_CONFIDENCE.get(str(finding.get("confidence", "low")), 0.5),
            _EFFORT.get(str(finding.get("estimatedEffort", "unknown")), 4.0),
            str(finding.get("id", "")),
        )
        entry = RankedEntry(
            rank=0,  # assigned after sort
            finding_id=str(finding.get("id", "")),
            domain=domain_name,
            target_path=draft.target_path,
            title=str(finding.get("title", "")),
            priority_score=breakdown["computedScore"],
            autonomy_boundary=str(finding.get("autonomyBoundary", "")),
            score_breakdown=breakdown,
        )
        scored.append((sort_key, entry))

    scored.sort(key=lambda item: item[0])
    ranked_entries = [
        RankedEntry(
            rank=index,
            finding_id=entry.finding_id,
            domain=entry.domain,
            target_path=entry.target_path,
            title=entry.title,
            priority_score=entry.priority_score,
            autonomy_boundary=entry.autonomy_boundary,
            score_breakdown=entry.score_breakdown,
        )
        for index, (_key, entry) in enumerate(scored, start=1)
    ]

    candidate_count = len(ranked_entries)
    kept = tuple(ranked_entries[:max_candidates])
    omitted_entries = ranked_entries[max_candidates:]
    omitted = tuple(
        {
            "findingId": entry.finding_id,
            "domain": entry.domain,
            "targetPath": entry.target_path,
            "rank": entry.rank,
            "priorityScore": entry.priority_score,
        }
        for entry in omitted_entries
    )

    base = {
        "schemaVersion": SCHEMA_VERSION,
        "sourceScorecardId": str(scorecard.get("id", "")),
        "projectRoot": str(project_path),
        "profile": profile,
        "candidateCount": candidate_count,
        "omittedCount": len(omitted),
        "skippedCount": len(skipped),
        "entries": [entry.to_jsonable() for entry in kept],
        "omitted": list(omitted),
        "skipped": list(skipped),
    }
    plan_hash = _sha(base)[:16]
    return RankedProposals(
        schema_version=SCHEMA_VERSION,
        source_scorecard_id=base["sourceScorecardId"],
        project_root=base["projectRoot"],
        profile=profile,
        candidate_count=candidate_count,
        omitted_count=len(omitted),
        skipped_count=len(skipped),
        entries=kept,
        omitted=omitted,
        skipped=tuple(skipped),
        plan_hash=plan_hash,
    )


def _score_breakdown(finding: dict[str, Any], weights: dict[str, int]) -> dict[str, Any]:
    dimension = str(finding.get("dimension", ""))
    severity = str(finding.get("severity", "low"))
    confidence = str(finding.get("confidence", "low"))
    effort = str(finding.get("estimatedEffort", "unknown"))
    impact = int(finding.get("impactOnFutureIteration", 0))
    risk = int(finding.get("riskReduction", 0))
    vgain = int(finding.get("verificationGain", 0))
    docs = int(finding.get("docKnowledgeGain", 0))
    dimension_weight = int(weights[dimension]) if dimension in weights else 0
    total_gain = impact + risk + vgain + docs
    computed = finding_priority_score(
        dimension_weight=dimension_weight,
        severity=severity,
        confidence=confidence,
        effort=effort,
        impact_on_future_iteration=impact,
        risk_reduction=risk,
        verification_gain=vgain,
        doc_knowledge_gain=docs,
    )
    return {
        "dimension": dimension,
        "dimensionWeight": dimension_weight,
        "severity": severity,
        "severityMultiplier": _SEVERITY.get(severity, 1.0),
        "confidence": confidence,
        "confidenceMultiplier": _CONFIDENCE.get(confidence, 0.5),
        "effort": effort,
        "effortDivisor": _EFFORT.get(effort, 4.0),
        "gains": {
            "impactOnFutureIteration": impact,
            "riskReduction": risk,
            "verificationGain": vgain,
            "docKnowledgeGain": docs,
        },
        "totalGain": total_gain,
        "formula": _FORMULA,
        "computedScore": computed,
    }


def _skipped(finding: dict[str, Any], reason: str) -> dict[str, Any]:
    return {
        "findingId": str(finding.get("id", "")),
        "title": str(finding.get("title", "")),
        "reason": reason,
        "evidencePaths": [
            str(ev.get("path", ""))
            for ev in finding.get("evidence", [])
            if isinstance(ev, dict) and ev.get("path")
        ],
    }


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def _sha(payload: dict[str, Any]) -> str:
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m arena.proposal_ranker")
    parser.add_argument("--project", required=True)
    parser.add_argument("--scorecard", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--max-candidates", type=int, default=10)
    args = parser.parse_args(argv)
    ranked = build_ranked_proposals(args.project, args.scorecard, max_candidates=args.max_candidates)
    Path(args.output).write_text(json.dumps(ranked.to_jsonable(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
