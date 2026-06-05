from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

import pytest

from arena.project_decomposer_ai import build_project_model_snapshot
from arena.project_graph import build_project_graph
from arena.project_model_llm import (
    LiveProjectModelLLM,
    build_fixture_model_output,
    load_recorded_model_output,
)


def test_load_recorded_model_output_rejects_cancelled_empty_wrapper(tmp_path: Path) -> None:
    output = tmp_path / "wrapper.json"
    output.write_text(
        json.dumps(
            {
                "text": "",
                "stopReason": "Cancelled",
                "thought": "I started working but never emitted final JSON.",
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Cancelled.*empty final text|empty final text.*Cancelled"):
        load_recorded_model_output(output)


def test_load_recorded_model_output_rejects_internal_thought_without_final_text(tmp_path: Path) -> None:
    output = tmp_path / "wrapper.json"
    output.write_text(
        json.dumps(
            {
                "text": "   ",
                "stopReason": "Stop",
                "thought": "The hidden/internal reasoning is not an accepted model answer.",
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="empty final text"):
        load_recorded_model_output(output)


def test_load_recorded_model_output_rejects_invalid_json_wrapper_text(tmp_path: Path) -> None:
    output = tmp_path / "wrapper.json"
    output.write_text(json.dumps({"text": "not json", "stopReason": "Stop"}), encoding="utf-8")

    with pytest.raises(ValueError, match="valid JSON"):
        load_recorded_model_output(output)


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


def test_live_project_model_llm_uses_direct_xai_json_api_and_records_metadata(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("XAI_API_KEY", "test-key")
    calls: list[dict[str, Any]] = []
    model_output = {
        "model_id": "model-overridden-by-provider",
        "project_id": "tiny",
        "goal": "decompose",
        "non_goals": ["no buckets"],
        "components": [],
        "contracts": [],
        "cross_cutting_concerns": [],
        "observable_checks": [],
        "held_out_probes": [],
        "verification_gaps": [],
        "near_neighbor_alternatives": [],
        "acceptance_command_allowlist": [],
    }

    def fake_urlopen(request: Any, timeout: int) -> _FakeHTTPResponse:
        calls.append({"url": request.full_url, "timeout": timeout, "body": json.loads(request.data.decode())})
        return _FakeHTTPResponse(
            {
                "model": "grok-live-test",
                "choices": [
                    {
                        "finish_reason": "stop",
                        "message": {"content": json.dumps(model_output)},
                    }
                ],
                "usage": {"prompt_tokens": 3, "completion_tokens": 5},
            }
        )

    llm = LiveProjectModelLLM(model="grok-live-test", urlopen=fake_urlopen, timeout_seconds=17)

    result = llm.generate("return JSON")

    assert calls == [
        {
            "url": "https://api.x.ai/v1/chat/completions",
            "timeout": 17,
            "body": {
                "model": "grok-live-test",
                "messages": [
                    {"role": "system", "content": "Return only strict JSON. No markdown."},
                    {"role": "user", "content": "return JSON"},
                ],
                "temperature": 0,
                "max_tokens": 4096,
                "response_format": {"type": "json_object"},
            },
        }
    ]
    assert result["model_id"] == "grok-live-test"
    assert result["_provider_metadata"]["provider"] == "xai"
    assert result["_provider_metadata"]["api_mode"] == "openai_chat_completions"
    assert result["_provider_metadata"]["finish_reason"] == "stop"
    assert result["_provider_metadata"]["prompt_hash"]
    assert result["_provider_metadata"]["content_hash"]


def test_live_project_model_llm_rejects_truncated_or_empty_content(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("XAI_API_KEY", "test-key")

    def fake_urlopen(request: Any, timeout: int) -> _FakeHTTPResponse:
        return _FakeHTTPResponse({"model": "grok-live-test", "choices": [{"finish_reason": "length", "message": {"content": "{}"}}]})

    llm = LiveProjectModelLLM(model="grok-live-test", urlopen=fake_urlopen)

    with pytest.raises(ValueError, match="truncated|length"):
        llm.generate("return JSON")


def test_build_project_model_snapshot_live_uses_injected_llm_and_records_hashes(tmp_path: Path) -> None:
    project = tmp_path / "repo"
    _write_tiny_repo(project)
    artifacts = tmp_path / "artifacts"

    class FakeLiveLLM:
        def generate(self, prompt: str) -> dict[str, Any]:
            graph = build_project_graph(project)
            output = build_fixture_model_output(
                graph,
                project_id="tiny-live",
                goal="decompose tiny repo",
                non_goals=["no buckets"],
            )
            output["model_id"] = "grok-live-test"
            output["_provider_metadata"] = {"provider": "xai", "model": "grok-live-test", "prompt_seen": bool(prompt)}
            return output

    result = build_project_model_snapshot(
        project,
        artifacts,
        project_id="tiny-live",
        goal="decompose tiny repo",
        non_goals=["no buckets"],
        llm_mode="live",
        live_llm=FakeLiveLLM(),
    )

    assert result.snapshot.primary_model_id == "grok-live-test"
    assert result.snapshot.prompt_hashes["decomposer"]
    assert result.snapshot.model_output_hashes["decomposer"]
    assert result.manifest["model_ids"]["decomposer"] == "grok-live-test"
    assert result.manifest["live_provider_metadata"] == {"provider": "xai", "model": "grok-live-test", "prompt_seen": True}
    assert result.gate_report.passed is True


def _write_tiny_repo(project: Path) -> None:
    (project / "pkg").mkdir(parents=True)
    (project / "tests").mkdir()
    (project / "pkg/core.py").write_text("def add_one(value: int) -> int:\n    return value + 1\n", encoding="utf-8")
    (project / "tests/test_core.py").write_text(
        "from pkg.core import add_one\n\ndef test_add_one():\n    assert add_one(1) == 2\n",
        encoding="utf-8",
    )
    (project / "pyproject.toml").write_text("[project]\nname = \"tiny-live\"\nversion = \"0.1.0\"\n", encoding="utf-8")
    subprocess.run(["git", "init", "-b", "main"], cwd=project, check=True, stdout=subprocess.DEVNULL)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=project, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=project, check=True)
    subprocess.run(["git", "add", "."], cwd=project, check=True)
    subprocess.run(["git", "commit", "-m", "initial"], cwd=project, check=True, stdout=subprocess.DEVNULL)
