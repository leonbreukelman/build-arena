from __future__ import annotations

import io
import json
import urllib.error
from email.message import Message
from pathlib import Path
from typing import Any, cast

import pytest

from arena.llm_adapter import (
    ApiKeyResolution,
    OpenAICompatibleChatClient,
    OpenAIProviderConfig,
    resolve_api_key,
    resolve_api_key_with_source,
    resolve_provider_config,
)


class _FakeHTTPResponse:
    def __init__(self, payload: dict[str, Any], *, status: int = 200) -> None:
        self.status = status
        self._payload = payload

    def __enter__(self) -> _FakeHTTPResponse:
        return self

    def __exit__(self, *exc: object) -> None:
        return None

    def read(self) -> bytes:
        return json.dumps(self._payload).encode()



def test_provider_registry_presets_are_openai_compatible(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("BUILD_ARENA_LLM_BASE_URL", raising=False)
    monkeypatch.delenv("BUILD_ARENA_LLM_API_KEY_ENV", raising=False)
    monkeypatch.setenv("BUILD_ARENA_XAI_MODEL", "grok-test")

    xai = resolve_provider_config("xai")
    openai = resolve_provider_config("openai", model="gpt-test")
    openrouter = resolve_provider_config("openrouter", model="openrouter-test")

    assert xai == OpenAIProviderConfig(
        provider="xai",
        base_url="https://api.x.ai/v1",
        api_key_env="XAI_API_KEY",
        model="grok-test",
        model_source="env:BUILD_ARENA_XAI_MODEL",
    )
    assert openai.base_url == "https://api.openai.com/v1"
    assert openai.api_key_env == "OPENAI_API_KEY"
    assert openai.model == "gpt-test"
    assert openrouter.base_url == "https://openrouter.ai/api/v1"
    assert openrouter.api_key_env == "OPENROUTER_API_KEY"
    assert openrouter.model == "openrouter-test"


def test_chat_client_posts_visible_messages_and_records_metadata(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("XAI_API_KEY", "test-key")
    calls: list[dict[str, Any]] = []

    def fake_urlopen(request: Any, timeout: int) -> _FakeHTTPResponse:
        calls.append(
            {
                "url": request.full_url,
                "timeout": timeout,
                "headers": dict(request.header_items()),
                "body": json.loads(request.data.decode()),
            }
        )
        return _FakeHTTPResponse(
            {
                "model": "grok-served",
                "choices": [
                    {
                        "finish_reason": "stop",
                        "message": {"content": "visible text"},
                    }
                ],
                "usage": {"prompt_tokens": 3, "completion_tokens": 5},
            }
        )

    config = OpenAIProviderConfig(
        provider="xai",
        base_url="https://api.x.ai/v1",
        api_key_env="XAI_API_KEY",
        model="grok-requested",
    )
    client = OpenAICompatibleChatClient(
        config=config,
        timeout_seconds=17,
        max_tokens=123,
        urlopen=fake_urlopen,
    )

    result = client.complete(
        messages=[{"role": "system", "content": "system"}, {"role": "user", "content": "hello"}],
        response_format={"type": "json_object"},
    )

    assert calls == [
        {
            "url": "https://api.x.ai/v1/chat/completions",
            "timeout": 17,
            "headers": {"Authorization": "Bearer test-key", "Content-type": "application/json"},
            "body": {
                "model": "grok-requested",
                "messages": [{"role": "system", "content": "system"}, {"role": "user", "content": "hello"}],
                "temperature": 0,
                "max_tokens": 123,
                "response_format": {"type": "json_object"},
            },
        }
    ]
    assert result.text == "visible text"
    assert result.model == "grok-served"
    assert result.requested_model == "grok-requested"
    assert result.provider == "xai"
    assert result.finish_reason == "stop"
    assert result.usage == {"prompt_tokens": 3, "completion_tokens": 5}
    assert result.metadata["api_mode"] == "openai_chat_completions"
    assert result.metadata["api_key_source"] == "environment"
    assert result.metadata["served_model_matches_requested"] is False
    assert result.metadata["prompt_hash"]
    assert result.metadata["content_hash"]


def test_chat_client_extracts_structured_visible_content_parts(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")

    def fake_urlopen(request: Any, timeout: int) -> _FakeHTTPResponse:
        return _FakeHTTPResponse(
            {
                "model": "provider/model",
                "choices": [
                    {
                        "finish_reason": "stop",
                        "message": {
                            "content": [
                                {"type": "reasoning", "reasoning": "hidden"},
                                {"type": "text", "text": "visible"},
                                {"content": " content"},
                            ]
                        },
                    }
                ],
            }
        )

    client = OpenAICompatibleChatClient(
        config=resolve_provider_config("openrouter", model="provider/model"),
        urlopen=fake_urlopen,
    )

    assert client.complete(messages=[{"role": "user", "content": "hello"}]).text == "visible content"


@pytest.mark.parametrize(
    "payload, match",
    [
        ({"model": "m", "choices": []}, "no choices"),
        ({"model": "m", "choices": [{"finish_reason": "stop", "message": {"content": "   "}}]}, "empty content"),
        ({"model": "m", "choices": [{"finish_reason": "length", "message": {"content": "partial"}}]}, "truncated|length"),
    ],
)
def test_chat_client_rejects_no_choices_empty_content_and_length(
    monkeypatch: pytest.MonkeyPatch,
    payload: dict[str, Any],
    match: str,
) -> None:
    monkeypatch.setenv("XAI_API_KEY", "test-key")

    def fake_urlopen(request: Any, timeout: int) -> _FakeHTTPResponse:
        return _FakeHTTPResponse(payload)

    client = OpenAICompatibleChatClient(config=resolve_provider_config("xai", model="grok-test"), urlopen=fake_urlopen)

    with pytest.raises(ValueError, match=match):
        client.complete(messages=[{"role": "user", "content": "hello"}])


def test_chat_client_redacts_provider_errors(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("XAI_API_KEY", "xai-secret-token")

    def fake_urlopen(request: Any, timeout: int) -> _FakeHTTPResponse:
        body = "Authorization: Bearer xai-secret-token api_key=xai-secret-token"
        raise urllib.error.HTTPError(
            request.full_url,
            401,
            "Unauthorized",
            Message(),
            cast(Any, io.BytesIO(body.encode())),
        )

    client = OpenAICompatibleChatClient(config=resolve_provider_config("xai", model="grok-test"), urlopen=fake_urlopen)

    with pytest.raises(ValueError) as excinfo:
        client.complete(messages=[{"role": "user", "content": "hello"}])

    message = str(excinfo.value)
    assert "xai-secret-token" not in message
    assert "[REDACTED]" in message


def test_chat_client_reads_api_key_from_hermes_env_file(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    hermes = tmp_path / ".hermes"
    hermes.mkdir()
    (hermes / ".env").write_text("OPENROUTER_API_KEY=from-file\n", encoding="utf-8")
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)

    assert resolve_api_key("OPENROUTER_API_KEY") == "from-file"
    assert resolve_api_key_with_source("OPENROUTER_API_KEY") == ApiKeyResolution(
        value="from-file",
        source="hermes_env_file",
    )


def test_chat_client_records_hermes_env_api_key_source_without_leaking_key(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    hermes = tmp_path / ".hermes"
    hermes.mkdir()
    hermes_secret = "from-hermes-file-secret"
    (hermes / ".env").write_text(f"XAI_API_KEY={hermes_secret}\n", encoding="utf-8")
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.delenv("XAI_API_KEY", raising=False)

    def fake_urlopen(request: Any, timeout: int) -> _FakeHTTPResponse:
        return _FakeHTTPResponse(
            {
                "model": "grok-test",
                "choices": [{"finish_reason": "stop", "message": {"content": "visible text"}}],
            }
        )

    client = OpenAICompatibleChatClient(
        config=resolve_provider_config("xai", model="grok-test"),
        urlopen=fake_urlopen,
    )

    result = client.complete(messages=[{"role": "user", "content": "hello"}])

    serialized_metadata = json.dumps(result.metadata, sort_keys=True)
    assert result.metadata["api_key_source"] == "hermes_env_file"
    assert hermes_secret not in serialized_metadata


def test_resolve_provider_config_can_require_explicit_model(monkeypatch: pytest.MonkeyPatch) -> None:
    for env_name in ["BUILD_ARENA_LLM_MODEL", "BUILD_ARENA_XAI_MODEL", "XAI_MODEL"]:
        monkeypatch.delenv(env_name, raising=False)

    with pytest.raises(ValueError, match="explicit model"):
        resolve_provider_config("xai", require_explicit_model=True)

    monkeypatch.setenv("BUILD_ARENA_XAI_MODEL", "grok-env")
    config = resolve_provider_config("xai", require_explicit_model=True)

    assert config.model == "grok-env"
    assert config.model_source == "env:BUILD_ARENA_XAI_MODEL"


def test_chat_client_strict_served_model_match_fails_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("XAI_API_KEY", "test-key")

    def fake_urlopen(request: Any, timeout: int) -> _FakeHTTPResponse:
        return _FakeHTTPResponse(
            {
                "model": "unexpected-served-model",
                "choices": [{"finish_reason": "stop", "message": {"content": "visible text"}}],
            }
        )

    client = OpenAICompatibleChatClient(
        config=resolve_provider_config("xai", model="grok-requested"),
        urlopen=fake_urlopen,
        require_served_model_match=True,
    )

    with pytest.raises(ValueError, match="served unexpected model"):
        client.complete(messages=[{"role": "user", "content": "hello"}])


def test_chat_client_strict_served_model_match_rejects_missing_model_field(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("XAI_API_KEY", "test-key")

    def fake_urlopen(request: Any, timeout: int) -> _FakeHTTPResponse:
        _ = request, timeout
        return _FakeHTTPResponse(
            {
                "choices": [{"finish_reason": "stop", "message": {"content": "visible text"}}],
            }
        )

    strict_client = OpenAICompatibleChatClient(
        config=resolve_provider_config("xai", model="grok-requested"),
        urlopen=fake_urlopen,
        require_served_model_match=True,
    )
    with pytest.raises(ValueError, match="served unexpected model"):
        strict_client.complete(messages=[{"role": "user", "content": "hello"}])

    non_strict_client = OpenAICompatibleChatClient(
        config=resolve_provider_config("xai", model="grok-requested"),
        urlopen=fake_urlopen,
    )
    result = non_strict_client.complete(messages=[{"role": "user", "content": "hello"}])

    assert result.model == "grok-requested"
    assert result.metadata["served_model_matches_requested"] is True
