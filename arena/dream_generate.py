"""Live-gated typed generation for advisory dream proposals.

The generator is intentionally not trusted. It only produces raw dream candidates
with minimum structure; ``arena.dream_gate`` later decides which premises resolve.
Tests inject a model callable, so the offline suite never spends or calls a live
provider.
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
GENERATED_BY = "arena.dream_generate"
PROMPT_VERSION = "dream-generate-v0"
ALLOWED_MODES = {"carrier_swap", "function_remap"}

DreamModel = Callable[[str], dict[str, Any]]


class DreamGenerateError(Exception):
    """Raised when raw dream generation fails closed."""


def generate_dreams(
    *,
    project_model_path: str | Path,
    capability_map_path: str | Path,
    scorecard_path: str | Path,
    model: DreamModel | None = None,
    live_provider: str = "xai",
    live_base_url: str | None = None,
    live_model: str | None = None,
    live_api_key_env: str = "XAI_API_KEY",
) -> dict[str, Any]:
    model_path = Path(project_model_path).resolve()
    cap_path = Path(capability_map_path).resolve()
    scorecard = Path(scorecard_path).resolve()
    project_model = _load_json_object(model_path)
    capability_map = _load_json_object(cap_path)
    scorecard_doc = _load_json_object(scorecard)

    prompt = _generation_prompt(project_model, capability_map, scorecard_doc)
    if model is None:
        if not live_model:
            raise DreamGenerateError("--live-model is required for dream generation")
        provider_config = resolve_provider_config(
            live_provider,
            base_url=live_base_url,
            api_key_env=live_api_key_env,
            model=live_model,
            require_explicit_model=True,
        )
        client = OpenAICompatibleChatClient(provider_config, temperature=0.7, max_tokens=4096)
        result = client.complete(
            messages=[
                {"role": "system", "content": "Return only JSON with a top-level dreams array."},
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
        )
        raw = _parse_model_json(result.text)
        model_id = result.model
    else:
        raw = model(prompt)
        if not isinstance(raw, dict):
            raise DreamGenerateError("injected model must return a JSON object")
        model_id = "injected-model"

    dreams = _minimum_grounded_dreams(raw.get("dreams", []), capability_map=capability_map)
    if not dreams:
        raise DreamGenerateError("generation produced no dreams with the required minimum grounding")
    return {
        "schemaVersion": SCHEMA_VERSION,
        "projectId": _project_id(project_model, capability_map),
        "sourceModel": {"projectModelV1Path": str(model_path), "graphHash": _graph_hash(project_model)},
        "capabilityMap": {"path": str(cap_path), "reviewed": capability_map.get("review", {}).get("reviewed") is True},
        "dreams": dreams,
        "provenance": {
            "generatedBy": GENERATED_BY,
            "researchedBy": "unresearched",
            "promptHashes": {"generate": _sha_text(prompt), "generatePromptVersion": _sha_text(PROMPT_VERSION)},
            "modelId": model_id,
            "inputHashes": {
                "projectModelV1": _file_sha(model_path),
                "capabilityMap": _file_sha(cap_path),
                "scorecard": _file_sha(scorecard),
            },
        },
    }


def write_generated_dreams(
    *,
    project_model_path: str | Path,
    capability_map_path: str | Path,
    scorecard_path: str | Path,
    output_path: str | Path,
    model: DreamModel | None = None,
    live_provider: str = "xai",
    live_base_url: str | None = None,
    live_model: str | None = None,
    live_api_key_env: str = "XAI_API_KEY",
) -> Path:
    document = generate_dreams(
        project_model_path=project_model_path,
        capability_map_path=capability_map_path,
        scorecard_path=scorecard_path,
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


def _minimum_grounded_dreams(raw_dreams: Any, *, capability_map: dict[str, Any]) -> list[dict[str, Any]]:
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
        if normalized["idea"] and normalized["rationale"] and normalized["validationRecipe"]["action"]:
            out.append(normalized)
    return out


def _conclusion(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        return {"band": "low", "value": 0.1}
    band = _clean(value.get("band"))
    if band not in {"low", "medium"}:
        band = "low"
    raw_number = value.get("value")
    number = float(raw_number) if isinstance(raw_number, int | float) else 0.1
    return {"band": band, "value": min(max(number, 0.0), 0.7)}


def _generation_prompt(project_model: dict[str, Any], capability_map: dict[str, Any], scorecard: dict[str, Any]) -> str:
    compact = {
        "projectId": _project_id(project_model, capability_map),
        "capabilities": capability_map.get("capabilities", []),
        "componentProfiles": _get(project_model, "iterationReadiness", "componentProfiles", default=[]),
        "nearNeighborAlternatives": _get(project_model, "snapshot", "near_neighbor_alternatives", default=[]),
        "topFindings": scorecard.get("findings", [])[:8] if isinstance(scorecard.get("findings"), list) else [],
    }
    return (
        "Generate advisory tier-3 dream proposals for Build Arena. Return JSON only: "
        "{\"dreams\":[...]}. Include at least one carrier_swap and one function_remap when possible. "
        "Every dream must include mode, idea, targetCapabilityIds, citedEvidence with anchorKind/anchorId/contentHash/claim, "
        "rationale, conclusionConfidence capped at medium/0.7, and validationRecipe. Current facts:\n"
        + json.dumps(compact, sort_keys=True, ensure_ascii=False)
    )


def _parse_model_json(text: str) -> dict[str, Any]:
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        raise DreamGenerateError("live model did not return valid JSON") from exc
    if not isinstance(payload, dict):
        raise DreamGenerateError("live model JSON must be an object")
    return payload


def _load_json_object(path: str | Path) -> dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise DreamGenerateError(f"{path} must contain a JSON object")
    return payload


def _project_id(project_model: dict[str, Any], capability_map: dict[str, Any]) -> str:
    return (
        _clean(capability_map.get("projectId"))
        or _clean(_get(project_model, "project", "projectId"))
        or _clean(_get(project_model, "snapshot", "project_id"))
        or "project"
    )


def _graph_hash(project_model: dict[str, Any]) -> str:
    graph_hash = _clean(_get(project_model, "projectGraph", "graphHash")) or _clean(_get(project_model, "snapshot", "graph_hash"))
    if len(graph_hash) != 64:
        raise DreamGenerateError("Project Model v1 does not expose a valid graph hash")
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
    parser = argparse.ArgumentParser(prog="python -m arena.dream_generate")
    parser.add_argument("--project-model", required=True)
    parser.add_argument("--capability-map", required=True)
    parser.add_argument("--scorecard", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--live-model")
    parser.add_argument("--live-provider", default="xai")
    parser.add_argument("--live-base-url")
    parser.add_argument("--live-api-key-env", default="XAI_API_KEY")
    args = parser.parse_args(argv)
    try:
        output = write_generated_dreams(
            project_model_path=args.project_model,
            capability_map_path=args.capability_map,
            scorecard_path=args.scorecard,
            output_path=args.output,
            live_provider=args.live_provider,
            live_base_url=args.live_base_url,
            live_model=args.live_model,
            live_api_key_env=args.live_api_key_env,
        )
    except (DreamGenerateError, OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"dream generate failed: {exc}", file=sys.stderr)
        return 3 if "--live-model" in str(exc) else 1
    print(str(output))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
