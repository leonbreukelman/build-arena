"""Render the rank-1 candidate of a reranked ``proposal-plan/v0`` into a GitHub-issue-ready ``proposal.md``.

Deterministic and faithful: identical input renders byte-identical output. No timestamps, host
paths, or randomness. No LLM, no network. This stage does not re-rank, analyse, apply, log, or
deliver anything -- it only renders the rank-1 candidate the re-ranker already chose.

Internal scoring/registry/prompt fields (``priority_score``, ``repo_facts_block``,
``repo_facts_hash``, ``intent_hash``, ``proposal_key``, ``registry_status``, ``base_lineage``) are
read but never rendered: showing the discarded ``priority_score`` in particular would mislead.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

PLAN_SCHEMA_VERSION = "proposal-plan/v0"
_SCHEMA_PATH = (
    Path(__file__).resolve().parents[1] / "docs" / "schemas" / "proposal-plan-v0.schema.json"
)

#: Internal fields that must never appear in the rendered proposal.
LEAK_FIELDS = (
    "priority_score",
    "repo_facts_block",
    "repo_facts_hash",
    "intent_hash",
    "proposal_key",
    "registry_status",
    "base_lineage",
)


class EmitError(Exception):
    """Raised when a reranked plan cannot be faithfully rendered (fail closed)."""


def load_reranked_plan(path: str | Path) -> dict[str, Any]:
    """Read and schema-validate a reranked ``proposal-plan/v0`` document, or raise ``EmitError``."""
    plan_path = Path(path)
    try:
        raw = plan_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise EmitError(f"cannot read reranked plan: {exc}") from exc
    try:
        plan = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise EmitError(f"reranked plan is not valid JSON: {exc}") from exc
    if not isinstance(plan, dict):
        raise EmitError("reranked plan must be a JSON object")
    if plan.get("schemaVersion") != PLAN_SCHEMA_VERSION:
        raise EmitError(f"reranked plan must have schemaVersion {PLAN_SCHEMA_VERSION}")
    _validate_schema(plan)
    return plan


def _validate_schema(plan: dict[str, Any]) -> None:
    schema = json.loads(_SCHEMA_PATH.read_text(encoding="utf-8"))
    errors = sorted(Draft202012Validator(schema).iter_errors(plan), key=lambda e: list(e.path))
    if errors:
        first = errors[0]
        location = "/".join(str(part) for part in first.path) or "<root>"
        raise EmitError(f"reranked plan failed schema validation at {location}: {first.message}")


def select_rank_one(plan: dict[str, Any]) -> dict[str, Any]:
    """Return the single ``rank == 1`` candidate, or raise ``EmitError``."""
    candidates = plan.get("candidates")
    if not isinstance(candidates, list):
        raise EmitError("reranked plan has no candidates array")
    rank_one = [c for c in candidates if isinstance(c, dict) and c.get("rank") == 1]
    if not rank_one:
        raise EmitError("reranked plan has no rank-1 candidate")
    if len(rank_one) > 1:
        raise EmitError("reranked plan has multiple rank-1 candidates")
    return rank_one[0]


def _clean(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


def _target_files(candidate: dict[str, Any]) -> list[str]:
    files: list[str] = []
    for path in candidate.get("target_paths") or []:
        if isinstance(path, str) and path and path not in files:
            files.append(path)
    single = candidate.get("target_path")
    if isinstance(single, str) and single and single not in files:
        files.append(single)
    return files


def _evidence_line(ref: dict[str, Any]) -> str:
    path = _clean(ref.get("path"))
    kind = _clean(ref.get("kind"))
    if path:
        head = f"{path} ({kind})" if kind else path
    elif kind:
        head = kind
    else:
        # A readable key=value summary -- never a raw JSON dump.
        head = ", ".join(f"{key}={ref[key]}" for key in sorted(ref)) or "(unspecified reference)"
    extras: list[str] = []
    provenance_ref = _clean(ref.get("ref"))
    if provenance_ref:
        extras.append(f"ref {provenance_ref}")
    component = _clean(ref.get("componentId"))
    if component:
        extras.append(f"component {component}")
    return f"{head} -- {', '.join(extras)}" if extras else head


def render_proposal_markdown(plan: dict[str, Any], candidate: dict[str, Any]) -> str:
    """Render the rank-1 candidate to GitHub-issue-ready markdown. Pure, deterministic, leak-free."""
    lines: list[str] = []

    lines.append(f"# {_clean(candidate.get('title')) or 'Untitled proposal'}")
    lines.append("")

    lines.append("## Proposed change")
    lines.append(_clean(candidate.get("intent")) or "_No intent provided._")
    lines.append("")

    lines.append("## Why")
    lines.append(_clean(candidate.get("source_recommended_action")) or "_No motivation provided._")
    lines.append("")

    lines.append("## Target file(s)")
    targets = _target_files(candidate)
    if targets:
        lines.extend(f"- `{path}`" for path in targets)
    else:
        lines.append("_No target file specified._")
    lines.append("")

    lines.append("## Definition of done")
    lines.append(_clean(candidate.get("success_criterion")) or "_No success criterion provided._")
    lines.append("")

    lines.append("## How to verify")
    commands = [c for c in candidate.get("verification_commands") or [] if isinstance(c, str) and c]
    if commands:
        lines.append("```sh")
        lines.extend(commands)
        lines.append("```")
    else:
        lines.append("_No verification commands provided._")
    lines.append("")

    lines.append("## Constraints")
    constraints = [
        c for c in candidate.get("grounding_constraints") or [] if isinstance(c, str) and c
    ]
    if constraints:
        lines.extend(f"- {item}" for item in constraints)
    else:
        lines.append("_No constraints provided._")
    lines.append("")

    lines.append("## Source references")
    refs = [r for r in candidate.get("evidence_refs") or [] if isinstance(r, dict)]
    if refs:
        lines.extend(f"- {_evidence_line(ref)}" for ref in refs)
    else:
        lines.append("_No source references provided._")
    lines.append("")

    lines.append("---")
    finding_id = _clean(candidate.get("finding_id")) or "unknown"
    plan_id = _clean(plan.get("id")) or "unknown"
    snapshot_id = _clean(plan.get("snapshotId")) or "unknown"
    lines.append(
        f"_Provenance -- finding `{finding_id}` \u00b7 plan `{plan_id}` \u00b7 snapshot `{snapshot_id}`_"
    )

    return "\n".join(lines) + "\n"


def emit_proposal(reranked_plan_path: str | Path, output_path: str | Path) -> Path:
    """Load -> select rank 1 -> render -> write. Returns the output path."""
    plan = load_reranked_plan(reranked_plan_path)
    candidate = select_rank_one(plan)
    markdown = render_proposal_markdown(plan, candidate)
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(markdown, encoding="utf-8")
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m arena.proposal_emit")
    parser.add_argument("--reranked-plan", required=True)
    parser.add_argument("--output", default="proposal.md")
    args = parser.parse_args(argv)
    try:
        out = emit_proposal(args.reranked_plan, args.output)
    except EmitError as exc:
        print(f"proposal emit failed: {exc}", file=sys.stderr)
        return 1
    print(str(out))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
