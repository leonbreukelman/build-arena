from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


def load_plan(path: str | Path) -> dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("proposal plan must be a JSON object")
    return payload


def top_candidate(plan: dict[str, Any]) -> dict[str, Any]:
    candidates = plan.get("candidates")
    if not isinstance(candidates, list):
        raise ValueError("proposal plan must contain a candidates array")
    rank_one = [candidate for candidate in candidates if isinstance(candidate, dict) and candidate.get("rank") == 1]
    if not rank_one:
        raise ValueError("no candidate with rank 1")
    if len(rank_one) > 1:
        raise ValueError("multiple candidates with rank 1")
    return rank_one[0]


def render_ticket_markdown(candidate: dict[str, Any]) -> str:
    title = _clean_text(candidate.get("title")) or _clean_text(candidate.get("finding_id"))
    if not title:
        raise ValueError("rank 1 candidate is missing title and finding_id")

    lines: list[str] = [f"# {title}", ""]

    what_lines: list[str] = []
    intent = _clean_text(candidate.get("intent"))
    if intent:
        what_lines.extend(["Intent:", "", intent, ""])
    target_paths = _string_list(candidate.get("target_paths"))
    if target_paths:
        what_lines.append("Target paths:")
        what_lines.extend(f"- `{path}`" for path in target_paths)
        what_lines.append("")
    _append_section(lines, "What & where", what_lines)

    why_lines: list[str] = []
    evidence_refs = candidate.get("evidence_refs")
    if isinstance(evidence_refs, list) and evidence_refs:
        why_lines.extend([
            "Evidence refs:",
            "",
            "```json",
            json.dumps(evidence_refs, indent=2, sort_keys=True),
            "```",
            "",
        ])
    source_action = _clean_text(candidate.get("source_recommended_action"))
    if source_action:
        why_lines.extend(["Source recommended action:", "", source_action, ""])
    _append_section(lines, "Why", why_lines)

    success = _clean_text(candidate.get("success_criterion"))
    _append_section(lines, "Definition of done", [success, ""] if success else [])

    constraints = _string_list(candidate.get("grounding_constraints"))
    _append_section(lines, "Constraints / guardrails", [f"- {constraint}" for constraint in constraints] + ([""] if constraints else []))

    commands = _string_list(candidate.get("verification_commands"))
    _append_section(lines, "How to verify", [f"- `{command}`" for command in commands] + ([""] if commands else []))

    priority_lines: list[str] = []
    priority = candidate.get("priority_score")
    if priority is not None and _clean_text(priority):
        priority_lines.append(f"Priority score: {priority}")
    finding_id = _clean_text(candidate.get("finding_id"))
    if finding_id:
        priority_lines.append(f"Finding ID: `{finding_id}`")
    _append_section(lines, "Priority & source", priority_lines + ([""] if priority_lines else []))

    while lines and lines[-1] == "":
        lines.pop()
    return "\n".join(lines) + "\n"


def emit_proposal(plan_path: str | Path, output_path: str | Path) -> None:
    plan = load_plan(plan_path)
    rendered = render_ticket_markdown(top_candidate(plan))
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(rendered, encoding="utf-8")


def _append_section(lines: list[str], heading: str, body_lines: list[str]) -> None:
    if not any(line for line in body_lines):
        return
    lines.extend([f"## {heading}", ""])
    lines.extend(body_lines)


def _clean_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [text for item in value if (text := _clean_text(item))]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m arena.proposal_emit")
    parser.add_argument("--plan", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args(argv)
    try:
        emit_proposal(args.plan, args.output)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"proposal_emit: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
