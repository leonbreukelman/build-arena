from __future__ import annotations

import hashlib
import json
import os
import re
import urllib.error
import urllib.request
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True, slots=True)
class ProviderPreset:
    provider: str
    base_url: str
    api_key_env: str
    default_model_envs: tuple[str, ...]
    default_model: str


@dataclass(frozen=True, slots=True)
class OpenAIProviderConfig:
    provider: str
    base_url: str
    api_key_env: str
    model: str


@dataclass(frozen=True, slots=True)
class OpenAIChatResult:
    text: str
    provider: str
    model: str
    requested_model: str
    finish_reason: str
    usage: Any
    metadata: dict[str, Any]


PROVIDER_PRESETS: dict[str, ProviderPreset] = {
    "xai": ProviderPreset(
        provider="xai",
        base_url="https://api.x.ai/v1",
        api_key_env="XAI_API_KEY",
        default_model_envs=("BUILD_ARENA_XAI_MODEL", "XAI_MODEL"),
        default_model="grok-4.20-0309-non-reasoning",
    ),
    "openai": ProviderPreset(
        provider="openai",
        base_url="https://api.openai.com/v1",
        api_key_env="OPENAI_API_KEY",
        default_model_envs=("BUILD_ARENA_OPENAI_MODEL", "OPENAI_MODEL"),
        default_model="gpt-4.1-mini",
    ),
    "openrouter": ProviderPreset(
        provider="openrouter",
        base_url="https://openrouter.ai/api/v1",
        api_key_env="OPENROUTER_API_KEY",
        default_model_envs=("BUILD_ARENA_OPENROUTER_MODEL", "OPENROUTER_MODEL"),
        default_model="openai/gpt-4.1-mini",
    ),
    "google-openai-compat": ProviderPreset(
        provider="google-openai-compat",
        base_url="https://generativelanguage.googleapis.com/v1beta/openai",
        api_key_env="GEMINI_API_KEY",
        default_model_envs=("BUILD_ARENA_GOOGLE_MODEL", "GEMINI_MODEL"),
        default_model="gemini-2.5-flash",
    ),
}


def resolve_provider_config(
    provider: str = "xai",
    *,
    base_url: str | None = None,
    api_key_env: str | None = None,
    model: str | None = None,
) -> OpenAIProviderConfig:
    provider_key = provider.strip().lower()
    try:
        preset = PROVIDER_PRESETS[provider_key]
    except KeyError as exc:
        known = ", ".join(sorted(PROVIDER_PRESETS))
        raise ValueError(f"unknown OpenAI-compatible provider {provider!r}; known providers: {known}") from exc

    provider_env_prefix = "BUILD_ARENA_" + re.sub(r"[^A-Z0-9]+", "_", provider_key.upper()).strip("_")
    resolved_base_url = base_url or os.environ.get(f"{provider_env_prefix}_BASE_URL") or os.environ.get("BUILD_ARENA_LLM_BASE_URL") or preset.base_url
    resolved_api_key_env = api_key_env or os.environ.get(f"{provider_env_prefix}_API_KEY_ENV") or os.environ.get("BUILD_ARENA_LLM_API_KEY_ENV") or preset.api_key_env
    resolved_model = model or os.environ.get("BUILD_ARENA_LLM_MODEL")
    if not resolved_model:
        for env_name in preset.default_model_envs:
            resolved_model = os.environ.get(env_name)
            if resolved_model:
                break
    resolved_model = resolved_model or preset.default_model
    return OpenAIProviderConfig(
        provider=preset.provider,
        base_url=resolved_base_url.rstrip("/"),
        api_key_env=resolved_api_key_env,
        model=resolved_model,
    )


def resolve_api_key(env_name: str) -> str:
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


@dataclass(slots=True)
class OpenAICompatibleChatClient:
    config: OpenAIProviderConfig
    timeout_seconds: int = 120
    max_tokens: int = 4096
    temperature: float = 0
    urlopen: Callable[..., Any] = field(default=urllib.request.urlopen)

    def complete(
        self,
        *,
        messages: list[dict[str, Any]],
        response_format: dict[str, Any] | None = None,
        max_tokens: int | None = None,
    ) -> OpenAIChatResult:
        api_key = resolve_api_key(self.config.api_key_env)
        payload: dict[str, Any] = {
            "model": self.config.model,
            "messages": messages,
            "temperature": self.temperature,
            "max_tokens": max_tokens if max_tokens is not None else self.max_tokens,
        }
        if response_format is not None:
            payload["response_format"] = response_format
        request = urllib.request.Request(
            self.config.base_url.rstrip("/") + "/chat/completions",
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
            raise ValueError(f"live model provider returned HTTP {exc.code}: {redact_error(body)}") from exc
        except Exception as exc:  # noqa: BLE001 - convert provider details to a concise fail-closed diagnostic.
            raise ValueError(f"live model provider request failed: {redact_error(str(exc))}") from exc

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
        content = _visible_content(message.get("content"))
        if not content.strip():
            raise ValueError(f"live model provider returned empty content with finish_reason={finish_reason!r}")
        served_model = str(packet.get("model") or self.config.model)
        prompt_hash = hashlib.sha256(json.dumps(messages, sort_keys=True).encode()).hexdigest()
        content_hash = hashlib.sha256(content.encode()).hexdigest()
        metadata = {
            "provider": self.config.provider,
            "api_mode": "openai_chat_completions",
            "base_url": self.config.base_url.rstrip("/"),
            "model": served_model,
            "requested_model": self.config.model,
            "status_code": status,
            "finish_reason": finish_reason,
            "prompt_hash": prompt_hash,
            "content_hash": content_hash,
            "usage": packet.get("usage"),
        }
        return OpenAIChatResult(
            text=content,
            provider=self.config.provider,
            model=served_model,
            requested_model=self.config.model,
            finish_reason=finish_reason,
            usage=packet.get("usage"),
            metadata=metadata,
        )


def _visible_content(content: Any) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        visible: list[str] = []
        for part in content:
            if not isinstance(part, dict):
                continue
            text = part.get("text")
            if isinstance(text, str):
                visible.append(text)
                continue
            nested_content = part.get("content")
            if isinstance(nested_content, str):
                visible.append(nested_content)
        return "".join(visible)
    return ""


def redact_error(text: str) -> str:
    text = re.sub(r"Bearer\s+[A-Za-z0-9._\-*]+", "Bearer [REDACTED]", text)
    text = re.sub(r"(?i)(api[_-]?key|token|password|secret|authorization)\s*[:=]\s*[^\s,]+", r"\1=[REDACTED]", text)
    return text[:500]
