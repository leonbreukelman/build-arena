"""Research raw dream proposals into premise-dense advisory hypotheses.

This is the tier-3 to tier-2 handoff: a soft model maps each divergent idea onto
concrete current-state claims. The output is still untrusted; the deterministic
``dream_gate`` must resolve every cited anchor before emit.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

from arena.llm_adapter import OpenAICompatibleChatClient, resolve_provider_config

SCHEMA_VERSION = "dream/v0"
RESEARCHED_BY = "arena.dream_research"
PROMPT_VERSION = "dream-research-v0"
ALLOWED_MODES = {"carrier_swap", "function_remap"}

DreamResearchModel = Callable[[str], dict[str, Any]]


class DreamResearchError(Exception):
    """Raised when dream research fails closed."""


def research_dreams(
    *,
    project_model_path: str | Path,
    capability_map_path: str | Path,
    dreams_path: str | Path,
    model: DreamResearchModel | None = None,
    live_provider: str = "xai",
    live_base_url: str | None = None,
    live_model: str | None = None,
    live_api_key_env: str = "XAI_API_KEY",
) -> dict[str, Any]:
    model_path = Path(project_model_path).resolve()
    cap_path = Path(capability_map_path).resolve()
    raw_path = Path(dreams_path).resolve()
    project_model = _load_json_object(model_path)
    capability_map = _load_json_object(cap_path)
    raw_doc = _load_json_object(raw_path)

    prompt = _research_prompt(project_model, capability_map, raw_doc)
    if model is None:
        if not live_model:
            raise DreamResearchError("--live-model is required for dream research")
        provider_config = resolve_provider_config(
            live_provider,
            base_url=live_base_url,
            api_key_env=live_api_key_env,
            model=live_model,
            require_explicit_model=True,
        )
        client = OpenAICompatibleChatClient(provider_config, temperature=0.2, max_tokens=4096)
        result = client.complete(
            messages=[
                {"role": "system", "content": "Return only JSON with a top-level dreams array."},
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
        )
        researched = _parse_model_json(result.text)
        model_id = result.model
    else:
        researched = model(prompt)
        if not isinstance(researched, dict):
            raise DreamResearchError("injected model must return a JSON object")
        model_id = _clean(raw_doc.get("provenance", {}).get("modelId")) or "injected-model"

    dreams = _researched_dreams(researched.get("dreams", []), capability_map=capability_map)
    if not dreams:
        raise DreamResearchError("research produced no dreams with required premise surface")
    return {
        "schemaVersion": SCHEMA_VERSION,
        "projectId": _project_id(project_model, capability_map, raw_doc),
        "sourceModel": {"projectModelV1Path": str(model_path), "graphHash": _graph_hash(project_model)},
        "capabilityMap": {"path": str(cap_path), "reviewed": capability_map.get("review", {}).get("reviewed") is True},
        "dreams": dreams,
        "provenance": _provenance(raw_doc, prompt, model_id, model_path, cap_path, raw_path),
    }


def write_researched_dreams(
    *,
    project_model_path: str | Path,
    capability_map_path: str | Path,
    dreams_path: str | Path,
    output_path: str | Path,
    model: DreamResearchModel | None = None,
    live_provider: str = "xai",
    live_base_url: str | None = None,
    live_model: str | None = None,
    live_api_key_env: str = "XAI_API_KEY",
) -> Path:
    document = research_dreams(
        project_model_path=project_model_path,
        capability_map_path=capability_map_path,
        dreams_path=dreams_path,
        model=model,
        live_provider=live_provider,
        live_base_url=live_base_url,
        live_model=live_model,
        live_api_key_env=live_api_key_env,
    )
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return output


def _researched_dreams(raw_dreams: Any, *, capability_map: dict[str, Any]) -> list[dict[str, Any]]:
    if not isinstance(raw_dreams, list):
        return []
    capability_ids = {
        str(item.get("id"))
        for item in capability_map.get("capabilities", [])
        if isinstance(item, dict) and item.get("id")
    }
    out: list[dict[str, Any]] = []
    for raw in raw_dreams:
        if not isinstance(raw, dict):
            continue
        mode = _clean(raw.get("mode"))
        targets = _string_list(raw.get("targetCapabilityIds"))
        evidence = [item for item in raw.get("citedEvidence", []) if isinstance(item, dict)] if isinstance(raw.get("citedEvidence"), list) else []
        recipe = raw.get("validationRecipe") if isinstance(raw.get("validationRecipe"), dict) else {}
        if mode not in ALLOWED_MODES or not targets or not evidence or not recipe:
            continue
        if any(target not in capability_ids for target in targets):
            continue
        normalized = {
            "id": _clean(raw.get("id")) or f"dream-{len(out) + 1}",
            "mode": mode,
            "idea": _clean(raw.get("idea")),
            "targetCapabilityIds": targets,
            "citedEvidence": evidence,
            "rationale": _clean(raw.get("rationale")),
            "premiseConfidence": _clean(raw.get("premiseConfidence")) or "unresolved",
            "conclusionConfidence": _conclusion(raw.get("conclusionConfidence")),
            "validationRecipe": {
                "action": _clean(recipe.get("action")),
                "observable": _clean(recipe.get("observable")),
                "expectedDirection": _clean(recipe.get("expectedDirection")),
            },
        }
        if raw.get("neighborAlternativeId") is not None:
            normalized["neighborAlternativeId"] = _clean(raw.get("neighborAlternativeId")) or None
        if normalized["idea"] and normalized["rationale"] and normalized["validationRecipe"]["observable"]:
            out.append(normalized)
    return out


def _provenance(
    raw_doc: dict[str, Any], prompt: str, model_id: str, model_path: Path, cap_path: Path, raw_path: Path
) -> dict[str, Any]:
    previous_raw = raw_doc.get("provenance")
    previous: dict[str, Any] = previous_raw if isinstance(previous_raw, dict) else {}
    prompt_hashes_raw = previous.get("promptHashes")
    prompt_hashes = dict(prompt_hashes_raw) if isinstance(prompt_hashes_raw, dict) else {}
    prompt_hashes["research"] = _sha_text(prompt)
    prompt_hashes["researchPromptVersion"] = _sha_text(PROMPT_VERSION)
    input_hashes_raw = previous.get("inputHashes")
    input_hashes = dict(input_hashes_raw) if isinstance(input_hashes_raw, dict) else {}
    input_hashes.update(
        {
            "projectModelV1": _file_sha(model_path),
            "capabilityMap": _file_sha(cap_path),
            "rawDreams": _file_sha(raw_path),
        }
    )
    return {
        "generatedBy": _clean(previous.get("generatedBy")) or "arena.dream_generate",
        "researchedBy": RESEARCHED_BY,
        "promptHashes": prompt_hashes,
        "modelId": model_id,
        "inputHashes": input_hashes,
    }


def _research_prompt(project_model: dict[str, Any], capability_map: dict[str, Any], raw_doc: dict[str, Any]) -> str:
    capability_ids = [
        _clean(capability.get("id"))
        for capability in capability_map.get("capabilities", [])
        if isinstance(capability, dict) and _clean(capability.get("id"))
    ]
    compact = {
        "allowedCapabilityIds": capability_ids,
        "anchorCatalog": _anchor_catalog(project_model, capability_map),
        "capabilities": capability_map.get("capabilities", []),
        "components": _get(project_model, "snapshot", "components", default=[]),
        "contracts": _get(project_model, "snapshot", "contracts", default=[]),
        "verificationGaps": _get(project_model, "snapshot", "verification_gaps", default=[]),
        "nearNeighborAlternatives": _get(project_model, "snapshot", "near_neighbor_alternatives", default=[]),
        "graphNodes": _get(project_model, "projectGraph", "nodes", default=[]),
        "graphEdges": _get(project_model, "projectGraph", "edges", default=[]),
        "rawDreams": raw_doc.get("dreams", []),
    }
    return (
        "Research these raw tier-3 dream proposals into concrete current-state claims. "
        "Do not claim benefit certainty. Preserve novelty, add/check citedEvidence anchors, and return JSON only: {\"dreams\":[...]}. "
        "For targetCapabilityIds, copy exact ids from allowedCapabilityIds. Do not abbreviate component as comp. "
        "For citedEvidence, copy exact anchorKind/anchorId/contentHash triples from anchorCatalog; do not invent or recompute hashes. "
        "Every conclusionConfidence must be an object capped at medium/0.7. Every validationRecipe must include action, "
        "observable, and expectedDirection one of decrease, increase, unchanged, tests_pass. Current model:\n"
        + json.dumps(compact, sort_keys=True, ensure_ascii=False)
    )


def _anchor_catalog(project_model: dict[str, Any], capability_map: dict[str, Any]) -> list[dict[str, str]]:
    anchors: list[tuple[str, dict[str, Any]]] = []
    for capability in capability_map.get("capabilities", []):
        if isinstance(capability, dict):
            anchors.append(("capability", capability))
    for component in _get(project_model, "snapshot", "components", default=[]):
        if isinstance(component, dict):
            anchors.append(("component", component))
    for contract in _get(project_model, "snapshot", "contracts", default=[]):
        if isinstance(contract, dict):
            anchors.append(("contract", contract))
    for gap in _get(project_model, "snapshot", "verification_gaps", default=[]):
        if isinstance(gap, dict):
            anchors.append(("verificationGap", gap))
    for neighbor in _get(project_model, "snapshot", "near_neighbor_alternatives", default=[]):
        if isinstance(neighbor, dict):
            anchors.append(("nearNeighborAlternative", neighbor))
    return [_anchor_record(kind, anchor) for kind, anchor in anchors if _clean(anchor.get("id"))]


def _anchor_record(kind: str, anchor: dict[str, Any]) -> dict[str, str]:
    encoded = json.dumps(anchor, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return {"anchorKind": kind, "anchorId": _clean(anchor.get("id")), "contentHash": hashlib.sha256(encoded).hexdigest()}


def _conclusion(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        return {"band": "low", "value": 0.1}
    band = _clean(value.get("band"))
    if band not in {"low", "medium"}:
        band = "low"
    raw_number = value.get("value")
    number = float(raw_number) if isinstance(raw_number, int | float) else 0.1
    return {"band": band, "value": min(max(number, 0.0), 0.7)}


def _parse_model_json(text: str) -> dict[str, Any]:
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        raise DreamResearchError("live model did not return valid JSON") from exc
    if not isinstance(payload, dict):
        raise DreamResearchError("live model JSON must be an object")
    return payload


def _load_json_object(path: str | Path) -> dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise DreamResearchError(f"{path} must contain a JSON object")
    return payload


def _project_id(project_model: dict[str, Any], capability_map: dict[str, Any], raw_doc: dict[str, Any]) -> str:
    return (
        _clean(raw_doc.get("projectId"))
        or _clean(capability_map.get("projectId"))
        or _clean(_get(project_model, "project", "projectId"))
        or _clean(_get(project_model, "snapshot", "project_id"))
        or "project"
    )


def _graph_hash(project_model: dict[str, Any]) -> str:
    graph_hash = _clean(_get(project_model, "projectGraph", "graphHash")) or _clean(_get(project_model, "snapshot", "graph_hash"))
    if len(graph_hash) != 64:
        raise DreamResearchError("Project Model v1 does not expose a valid graph hash")
    return graph_hash


def _get(payload: dict[str, Any], *keys: str, default: Any = None) -> Any:
    current: Any = payload
    for key in keys:
        if not isinstance(current, dict):
            return default
        current = current.get(key)
    return default if current is None else current


def _clean(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return list(dict.fromkeys(str(item).strip() for item in value if str(item).strip()))


def _sha_text(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def _file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m arena.dream_research")
    parser.add_argument("--project-model", required=True)
    parser.add_argument("--capability-map", required=True)
    parser.add_argument("--dreams", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--live-model")
    parser.add_argument("--live-provider", default="xai")
    parser.add_argument("--live-base-url")
    parser.add_argument("--live-api-key-env", default="XAI_API_KEY")
    args = parser.parse_args(argv)
    try:
        output = write_researched_dreams(
            project_model_path=args.project_model,
            capability_map_path=args.capability_map,
            dreams_path=args.dreams,
            output_path=args.output,
            live_provider=args.live_provider,
            live_base_url=args.live_base_url,
            live_model=args.live_model,
            live_api_key_env=args.live_api_key_env,
        )
    except (DreamResearchError, OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"dream research failed: {exc}", file=sys.stderr)
        return 3 if "--live-model" in str(exc) else 1
    print(str(output))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
