from __future__ import annotations

import hashlib
import json
import os
import urllib.error
import urllib.request
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

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
    base_url: str = "https://api.x.ai/v1"
    api_key_env: str = "XAI_API_KEY"
    timeout_seconds: int = 120
    max_tokens: int = 4096
    urlopen: Callable[..., Any] = field(default=urllib.request.urlopen)

    def generate(self, prompt: str) -> dict[str, Any]:
        api_key = _resolve_api_key(self.api_key_env)
        model = self.model or os.environ.get("BUILD_ARENA_XAI_MODEL") or os.environ.get("XAI_MODEL") or "grok-4.20-0309-non-reasoning"
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": "Return only strict JSON. No markdown."},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0,
            "max_tokens": self.max_tokens,
            "response_format": {"type": "json_object"},
        }
        request = urllib.request.Request(
            self.base_url.rstrip("/") + "/chat/completions",
            data=json.dumps(payload).encode(),
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            method="POST",
        )
        try:
            with self.urlopen(request, timeout=self.timeout_seconds) as response:
                response_text = response.read().decode("utf-8", errors="replace")
                status = int(getattr(response, "status", 200))
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            raise ValueError(f"live model provider returned HTTP {exc.code}: {_redact_error(body)}") from exc
        except Exception as exc:  # noqa: BLE001 - convert provider details to a concise fail-closed diagnostic.
            raise ValueError(f"live model provider request failed: {_redact_error(str(exc))}") from exc

        try:
            packet = json.loads(response_text)
        except json.JSONDecodeError as exc:
            raise ValueError("live model provider response envelope was not valid JSON") from exc
        choices = packet.get("choices") or []
        if not choices:
            raise ValueError("live model provider response had no choices")
        choice = choices[0]
        finish_reason = str(choice.get("finish_reason") or "")
        if finish_reason.lower() == "length":
            raise ValueError("live model provider response was truncated with finish_reason='length'")
        message = choice.get("message") or {}
        content = str(message.get("content") or "")
        if not content.strip():
            raise ValueError(f"live model provider returned empty content with finish_reason={finish_reason!r}")

        try:
            output = normalize_model_output(_parse_json_text(content))
        except ValueError as exc:
            raise ValueError("live model provider content was not valid Build Arena JSON") from exc
        output["model_id"] = str(packet.get("model") or output.get("model_id") or model)
        output["_provider_metadata"] = {
            "provider": self.provider,
            "api_mode": "openai_chat_completions",
            "base_url": self.base_url.rstrip("/"),
            "model": output["model_id"],
            "status_code": status,
            "finish_reason": finish_reason,
            "prompt_hash": hashlib.sha256(prompt.encode()).hexdigest(),
            "content_hash": hashlib.sha256(content.encode()).hexdigest(),
            "usage": packet.get("usage"),
        }
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


def _resolve_api_key(env_name: str) -> str:
    value = os.environ.get(env_name)
    if value:
        return value
    env_path = Path.home() / ".hermes" / ".env"
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8", errors="replace").splitlines():
            if not line or line.lstrip().startswith("#") or "=" not in line:
                continue
            key, raw_value = line.split("=", 1)
            if key.strip() == env_name:
                value = raw_value.strip().strip('"\'')
                if value:
                    return value
    raise ValueError(f"live model provider requires {env_name} in the environment or ~/.hermes/.env")


def _redact_error(text: str) -> str:
    import re

    text = re.sub(r"Bearer\s+[A-Za-z0-9._\-]+", "Bearer [REDACTED]", text)
    text = re.sub(r"(?i)(api[_-]?key|token|password|secret|authorization)\s*[:=]\s*[^\s,]+", r"\1=[REDACTED]", text)
    return text[:500]


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
