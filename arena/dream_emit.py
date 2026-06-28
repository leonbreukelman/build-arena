"""Render gated ``dream/v1`` advisory hypotheses to ``experiment.md``.

Emit is deterministic and faithful. It does not call a model, does not re-rank via
soft judgment, and refuses any input containing unresolved/partial dreams. The
dream lane is also hard-separated from the deterministic proposal lane: this
module refuses to write ``proposal.md``.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

SCHEMA_VERSION = "dream/v1"
_SCHEMA_PATH = Path(__file__).resolve().parents[1] / "docs" / "schemas" / "dream-v1.schema.json"


class DreamEmitError(Exception):
    """Raised when gated dreams cannot be faithfully rendered."""


def load_gated_dreams(path: str | Path) -> dict[str, Any]:
    dream_path = Path(path)
    try:
        payload = json.loads(dream_path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise DreamEmitError(f"cannot read dream artifact: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise DreamEmitError(f"dream artifact is not valid JSON: {exc}") from exc
    if not isinstance(payload, dict):
        raise DreamEmitError("dream artifact must be a JSON object")
    if payload.get("schemaVersion") != SCHEMA_VERSION:
        raise DreamEmitError(f"dream artifact must have schemaVersion {SCHEMA_VERSION}")
    validate_schema(payload)
    require_gate_marker(payload)
    return payload


def validate_schema(document: dict[str, Any]) -> None:
    schema = json.loads(_SCHEMA_PATH.read_text(encoding="utf-8"))
    errors = sorted(Draft202012Validator(schema).iter_errors(document), key=lambda error: list(error.path))
    if errors:
        first = errors[0]
        location = "/".join(str(part) for part in first.path) or "<root>"
        raise DreamEmitError(f"dream artifact failed schema validation at {location}: {first.message}")


def require_gate_marker(document: dict[str, Any]) -> None:
    provenance_raw = document.get("provenance")
    provenance: dict[str, Any] = provenance_raw if isinstance(provenance_raw, dict) else {}
    prompt_hashes_raw = provenance.get("promptHashes")
    prompt_hashes: dict[str, Any] = prompt_hashes_raw if isinstance(prompt_hashes_raw, dict) else {}
    if provenance.get("gatedBy") != "arena.dream_gate" or "gate" not in prompt_hashes:
        raise DreamEmitError("dream artifact lacks arena.dream_gate provenance; refusing to trust premiseConfidence")


def select_renderable_dreams(document: dict[str, Any]) -> list[dict[str, Any]]:
    dreams = document.get("dreams")
    if not isinstance(dreams, list):
        raise DreamEmitError("dream artifact has no dreams array")
    unresolved = [
        str(dream.get("id", "<missing>"))
        for dream in dreams
        if isinstance(dream, dict) and dream.get("premiseConfidence") != "all_resolved"
    ]
    if unresolved:
        raise DreamEmitError(f"refusing to render non-all_resolved dream(s): {', '.join(unresolved)}")
    renderable = [dream for dream in dreams if isinstance(dream, dict)]
    if not renderable:
        raise DreamEmitError("dream artifact has no all_resolved dreams to render")
    return sorted(renderable, key=_rank_key)


def render_dream_markdown(document: dict[str, Any]) -> str:
    require_gate_marker(document)
    dreams = select_renderable_dreams(document)
    cap_map = document.get("capabilityMap")
    reviewed = bool(cap_map.get("reviewed")) if isinstance(cap_map, dict) else False
    provenance_line = (
        "Premised on an operator-reviewed capability map."
        if reviewed
        else (
            "Premised on an auto-generated, operator-unreviewed capability map. "
            "Judge these at output or in downstream evaluation; the in-lane gate proves "
            "only that cited premises resolve, not that the capability reading is correct."
        )
    )
    lines: list[str] = [
        "# Experiment Proposals",
        "",
        "Advisory tier-3 experiment proposals. These are not deterministic changes and do not authorize mutation.",
        "",
        provenance_line,
        "",
    ]
    for index, dream in enumerate(dreams, start=1):
        lines.extend(_render_one(index, dream))
        lines.append("")
    lines.extend(_footer(document))
    return "\n".join(lines) + "\n"


def emit_dream(dream_path: str | Path, output_path: str | Path = "experiment.md") -> Path:
    output = Path(output_path)
    if output.name.lower() == "proposal.md":
        raise DreamEmitError("dream_emit refuses to write proposal.md; use experiment.md for the advisory lane")
    document = load_gated_dreams(dream_path)
    markdown = render_dream_markdown(document)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(markdown, encoding="utf-8")
    return output


def _rank_key(dream: dict[str, Any]) -> tuple[int, int, int, str]:
    mode = str(dream.get("mode", ""))
    neighbor = dream.get("neighborAlternativeId")
    if mode == "carrier_swap" and isinstance(neighbor, str) and neighbor:
        mode_rank = 0
    elif mode == "carrier_swap":
        mode_rank = 1
    else:
        mode_rank = 2
    evidence_count = len(dream.get("citedEvidence", [])) if isinstance(dream.get("citedEvidence"), list) else 0
    target_count = len(dream.get("targetCapabilityIds", [])) if isinstance(dream.get("targetCapabilityIds"), list) else 0
    return (mode_rank, -evidence_count, -target_count, str(dream.get("id", "")))


def _render_one(index: int, dream: dict[str, Any]) -> list[str]:
    confidence_raw = dream.get("conclusionConfidence")
    confidence: dict[str, Any] = confidence_raw if isinstance(confidence_raw, dict) else {}
    recipe_raw = dream.get("validationRecipe")
    recipe: dict[str, Any] = recipe_raw if isinstance(recipe_raw, dict) else {}
    current_raw = dream.get("currentStructure")
    current: dict[str, Any] = current_raw if isinstance(current_raw, dict) else {}
    proposed_raw = dream.get("proposedStructure")
    proposed: dict[str, Any] = proposed_raw if isinstance(proposed_raw, dict) else {}
    lines = [
        f"## {index}. {str(dream.get('idea', '')).strip()}",
        "",
        f"- Dream id: `{str(dream.get('id', '')).strip()}`",
        f"- Mode: `{str(dream.get('mode', '')).strip()}`",
        "- Target capabilities: " + ", ".join(f"`{item}`" for item in dream.get("targetCapabilityIds", [])),
        "",
        "### Cited current-state evidence",
    ]
    for evidence in dream.get("citedEvidence", []):
        if not isinstance(evidence, dict):
            continue
        kind = str(evidence.get("anchorKind", "")).strip()
        anchor_id = str(evidence.get("anchorId", "")).strip()
        claim = str(evidence.get("claim", "")).strip() or "current-state premise resolved"
        lines.append(f"- {kind} `{anchor_id}` — {claim}")
    lines.extend(
        [
            "",
            "### Structural delta",
            "- Current: " + _structure_summary(current),
            "- Proposed: " + _structure_summary(proposed),
            "",
            "### Rationale",
            str(dream.get("rationale", "")).strip(),
            "",
            "### Confidence",
            f"- Premise confidence (mechanical): `{str(dream.get('premiseConfidence', '')).strip()}`",
            "- Conclusion confidence (speculative/capped): "
            f"`{str(confidence.get('band', '')).strip()}` ({confidence.get('value')})",
            "",
            "### Validation recipe",
            "To validate, try `"
            + str(recipe.get("action", "")).strip()
            + "`; check `"
            + str(recipe.get("observable", "")).strip()
            + "` moves `"
            + str(recipe.get("expectedDirection", "")).strip()
            + "`.",
        ]
    )
    return lines


def _structure_summary(structure: dict[str, Any]) -> str:
    preferred_keys = ("fromCarrier", "toCarrier", "fromBinding", "toBinding", "description")
    parts = [
        f"`{key}`={str(structure[key]).strip()}"
        for key in preferred_keys
        if isinstance(structure.get(key), str) and str(structure[key]).strip()
    ]
    return ", ".join(parts) if parts else "_not recorded_"


def _footer(document: dict[str, Any]) -> list[str]:
    source_raw = document.get("sourceModel")
    source: dict[str, Any] = source_raw if isinstance(source_raw, dict) else {}
    provenance_raw = document.get("provenance")
    provenance: dict[str, Any] = provenance_raw if isinstance(provenance_raw, dict) else {}
    prompt_hashes_raw = provenance.get("promptHashes")
    prompt_hashes: dict[str, Any] = prompt_hashes_raw if isinstance(prompt_hashes_raw, dict) else {}
    prompt_bits = ", ".join(f"{key}={prompt_hashes[key]}" for key in sorted(prompt_hashes))
    return [
        "---",
        "Provenance:",
        f"- Model id: `{str(provenance.get('modelId', '')).strip()}`",
        f"- Source graphHash: `{str(source.get('graphHash', '')).strip()}`",
        f"- Prompt hashes: {prompt_bits or '_none recorded_'}",
    ]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m arena.dream_emit")
    parser.add_argument("--dreams", required=True)
    parser.add_argument("--output", default="experiment.md")
    args = parser.parse_args(argv)
    try:
        output = emit_dream(args.dreams, args.output)
    except DreamEmitError as exc:
        print(f"dream emit failed: {exc}", file=sys.stderr)
        return 1
    print(str(output))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
