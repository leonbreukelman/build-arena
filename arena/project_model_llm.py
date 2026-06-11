from __future__ import annotations

import json
import urllib.request
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from arena.llm_adapter import OpenAICompatibleChatClient, resolve_provider_config
from arena.project_graph import ProjectGraph
from arena.project_meta_decomposer import build_meta_model_output

REQUIRED_MODEL_OUTPUT_KEYS = {
    "model_id",
    "project_id",
    "goal",
    "non_goals",
    "components",
    "contracts",
    "cross_cutting_concerns",
    "observable_checks",
    "held_out_probes",
    "verification_gaps",
    "near_neighbor_alternatives",
    "acceptance_command_allowlist",
}


def load_recorded_model_output(path: str | Path) -> dict[str, Any]:
    return normalize_model_output(json.loads(Path(path).read_text(encoding="utf-8")))


def normalize_model_output(raw: Any) -> dict[str, Any]:
    if not isinstance(raw, dict):
        raise ValueError("model output must be a JSON object")

    if _looks_like_text_wrapper(raw):
        text = str(raw.get("text") or "")
        stop_reason = str(raw.get("stopReason") or raw.get("stop_reason") or "unknown")
        if not text.strip():
            raise ValueError(f"model output wrapper stopReason={stop_reason!r} has empty final text")
        if stop_reason.lower() == "cancelled":
            raise ValueError("model output wrapper stopReason='Cancelled' is not an accepted final answer")
        try:
            parsed = _parse_json_text(text)
        except ValueError as exc:
            raise ValueError("model output wrapper text must be valid JSON") from exc
        return normalize_model_output(parsed)

    return raw


@dataclass(slots=True)
class LiveProjectModelLLM:
    model: str | None = None
    provider: str = "xai"
    base_url: str | None = None
    api_key_env: str | None = None
    timeout_seconds: int = 120
    max_tokens: int = 4096
    urlopen: Callable[..., Any] = field(default=urllib.request.urlopen)

    def generate(self, prompt: str) -> dict[str, Any]:
        config = resolve_provider_config(
            self.provider,
            base_url=self.base_url,
            api_key_env=self.api_key_env,
            model=self.model,
        )
        client = OpenAICompatibleChatClient(
            config=config,
            timeout_seconds=self.timeout_seconds,
            max_tokens=self.max_tokens,
            urlopen=self.urlopen,
        )
        result = client.complete(
            messages=[
                {"role": "system", "content": "Return only strict JSON. No markdown."},
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
        )
        try:
            output = normalize_model_output(_parse_json_text(result.text))
        except ValueError as exc:
            raise ValueError("live model provider content was not valid Build Arena JSON") from exc
        output["model_id"] = str(result.model or output.get("model_id") or config.model)
        output["_provider_metadata"] = dict(result.metadata)
        return output


def _looks_like_text_wrapper(raw: dict[str, Any]) -> bool:
    return "text" in raw or "stopReason" in raw or "stop_reason" in raw or "thought" in raw


def _parse_json_text(text: str) -> Any:
    stripped = text.strip()
    if stripped.startswith("```"):
        lines = stripped.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        stripped = "\n".join(lines).strip()
    try:
        return json.loads(stripped)
    except json.JSONDecodeError as exc:
        raise ValueError("text is not valid JSON") from exc



def build_fixture_model_output(graph: ProjectGraph, *, project_id: str, goal: str, non_goals: list[str]) -> dict[str, Any]:
    return build_meta_model_output(graph, project_id=project_id, goal=goal, non_goals=non_goals)


def build_noop_model_output(graph: ProjectGraph, *, project_id: str, goal: str, non_goals: list[str]) -> dict[str, Any]:
    project_node = next(node for node in graph.nodes if node.kind == "project")
    prov = _first_prov(project_node)
    return {
        "model_id": "noop-no-live-model",
        "project_id": project_id,
        "goal": goal,
        "non_goals": non_goals,
        "components": [],
        "contracts": [],
        "cross_cutting_concerns": [],
        "observable_checks": [],
        "held_out_probes": [],
        "verification_gaps": [
            {
                "id": "gap.no-model-output",
                "description": "No model output was provided; semantic decomposition remains unverified.",
                "severity": "blocker",
                "component_ids": [],
                "contract_ids": [],
                "provenance_refs": [prov],
            }
        ],
        "near_neighbor_alternatives": [],
        "acceptance_command_allowlist": [],
    }


def _first_prov(node: Any) -> str:
    return node.provenance_refs[0].id if getattr(node, "provenance_refs", None) else ""
