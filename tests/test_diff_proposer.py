from __future__ import annotations

import asyncio
import json
import subprocess
from pathlib import Path
from typing import Any

import pytest

from arena.generated.models import Hypothesis, RunnerName
from arena.llm_adapter import (
    OpenAIChatResult,
    OpenAICompatibleChatClient,
    OpenAIProviderConfig,
    resolve_provider_config,
)
from arena.router import RunnerRouter
from arena.runners.base import RunnerError
from arena.runners.diff_proposer import (
    DiffProposalRequest,
    DiffProposalResponse,
    DiffProposerRunner,
    OpenAICompatibleDiffTransport,
)


def _run(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=cwd, check=True, capture_output=True, text=True)


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _repo(tmp_path: Path, *, max_lines: int = 6) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    _write(repo / "src" / "app.py", "def value() -> int:\n    return 1\n")
    _write(repo / "private" / "secret.py", "SECRET='***'\n")
    _write(
        repo / ".arena" / "goal.toml",
        f"""
schema_version = "goal-config/v1"
project_id = "diff-proposer-fixture"

[commands]
test = ["python3", "-c", "pass"]
lint = ["python3", "-c", "pass"]
typecheck = ["python3", "-c", "pass"]

[coverage]
source = "coverage.json"
floor = 0.0

[paths]
source_roots = ["src", "private"]
out_of_scope = []
read_only = ["private"]

[diff_caps]
max_files = 1
max_lines = {max_lines}
""".strip()
        + "\n",
    )
    _run(["git", "init", "-b", "main"], repo)
    _run(["git", "config", "user.email", "arena@example.invalid"], repo)
    _run(["git", "config", "user.name", "Arena Tests"], repo)
    _run(["git", "add", "."], repo)
    _run(["git", "commit", "-m", "baseline"], repo)
    return repo


def _hypothesis(*, target_files: list[str] | None = None) -> Hypothesis:
    return Hypothesis(
        id="hyp-diff-1",
        cycle_id="cycle-1",
        intent="Return the safer value",
        technique_tag="diff_proposal",
        target_cluster="src/app.py",
        target_files=target_files or ["src/app.py"],
        fingerprint_id="f" * 32,
        proposed_ts=1.0,
    )


def _valid_diff(path: str = "src/app.py", *, new_value: int = 2) -> str:
    return f"""diff --git a/{path} b/{path}
--- a/{path}
+++ b/{path}
@@ -1,2 +1,2 @@
 def value() -> int:
-    return 1
+    return {new_value}
"""


class FakeTransport:
    def __init__(self, response: DiffProposalResponse) -> None:
        self.response = response
        self.requests: list[Any] = []

    def propose(self, request: Any) -> DiffProposalResponse:
        self.requests.append(request)
        return self.response


class SequenceTransport:
    def __init__(self, responses: list[DiffProposalResponse]) -> None:
        self.responses = responses
        self.requests: list[Any] = []

    def propose(self, request: Any) -> DiffProposalResponse:
        self.requests.append(request)
        return self.responses[len(self.requests) - 1]


class FakeChatClient:
    def __init__(self, result: OpenAIChatResult) -> None:
        self.result = result
        self.calls: list[dict[str, Any]] = []

    def complete(
        self,
        *,
        messages: list[dict[str, Any]],
        response_format: dict[str, Any] | None = None,
        max_tokens: int | None = None,
    ) -> OpenAIChatResult:
        self.calls.append({"messages": messages, "response_format": response_format, "max_tokens": max_tokens})
        return self.result


def _chat_result(text: str, *, finish_reason: str = "stop") -> OpenAIChatResult:
    return OpenAIChatResult(
        text=text,
        provider="xai",
        model="grok-served",
        requested_model="grok-requested",
        finish_reason=finish_reason,
        usage={"prompt_tokens": 10, "completion_tokens": 20},
        metadata={
            "provider": "xai",
            "api_mode": "openai_chat_completions",
            "base_url": "https://api.x.ai/v1",
            "model": "grok-served",
            "requested_model": "grok-requested",
            "finish_reason": finish_reason,
            "prompt_hash": "p" * 64,
            "content_hash": "c" * 64,
            "usage": {"prompt_tokens": 10, "completion_tokens": 20},
        },
    )


def _diff_request() -> DiffProposalRequest:
    return DiffProposalRequest(
        hypothesis_id="hyp-diff-1",
        target_path="src/app.py",
        file_contents="def value() -> int:\n    return 1\n",
        success_criterion="value returns 2",
        goal_config_sha="g" * 64,
        intent="Return the safer value",
    )


def test_openai_compatible_diff_transport_prompt_includes_grounding_facts_and_constraints() -> None:
    chat = FakeChatClient(_chat_result(_valid_diff()))
    transport = OpenAICompatibleDiffTransport(chat_client=chat)
    request = DiffProposalRequest(
        hypothesis_id="hyp-docs-index",
        target_path="docs/index.md",
        file_contents="",
        success_criterion="docs index exists and all local Markdown links resolve",
        goal_config_sha="g" * 64,
        intent="Create grounded docs index",
        file_exists=False,
        repo_facts="README.md exists; docs has no Markdown pages",
        grounding_constraints=("Do not invent Markdown links to files absent from repo facts.",),
    )

    transport.propose(request)

    prompt = chat.calls[0]["messages"][-1]["content"]
    assert "Repository facts:" in prompt
    assert "README.md exists; docs has no Markdown pages" in prompt
    assert "Grounding constraints:" in prompt
    assert "Do not invent Markdown links" in prompt
    assert "Do not shorten repository-relative paths in Markdown links or plain file mentions" in prompt
    assert "If a source file is relevant, mention the exact path from the Source files list" in prompt


def test_prompt_includes_pending_proposals_and_failure_notes() -> None:
    request = DiffProposalRequest(
        hypothesis_id="hyp-docs-index",
        target_path="docs/index.md",
        file_contents="",
        success_criterion="docs index links resolve",
        goal_config_sha="g" * 64,
        intent="Create grounded docs index",
        pending_proposals=("pending proposal doc.index.missing on docs/index.md",),
        failure_notes=("Prior AGENTS.md proposal doubled src/src paths",),
    )

    chat = FakeChatClient(_chat_result(_valid_diff()))
    OpenAICompatibleDiffTransport(chat_client=chat).propose(request)
    prompt = chat.calls[0]["messages"][-1]["content"]

    assert "Known pending proposals:" in prompt
    assert "pending proposal doc.index.missing" in prompt
    assert "Known failure modes:" in prompt
    assert "doubled src/src paths" in prompt


def test_openai_compatible_diff_transport_requests_unified_diff_and_records_provenance() -> None:
    chat = FakeChatClient(_chat_result(_valid_diff()))
    transport = OpenAICompatibleDiffTransport(chat_client=chat)

    response = transport.propose(_diff_request())

    prompt = chat.calls[0]["messages"][-1]["content"]
    assert chat.calls[0]["response_format"] is None
    assert chat.calls[0]["max_tokens"] == 4096
    assert "Return only a unified diff" in prompt
    assert "src/app.py" in prompt
    assert "def value() -> int:" in prompt
    assert "value returns 2" in prompt
    assert response.diff_text == _valid_diff()
    assert response.intent == "Return the safer value"
    assert response.truncated is False
    assert response.provenance is not None
    assert response.provenance["provider"] == "xai"
    assert response.provenance["model"] == "grok-served"
    assert response.provenance["requested_model"] == "grok-requested"


@pytest.mark.parametrize(
    "result, match",
    [
        (_chat_result(_valid_diff(), finish_reason="length"), "truncated"),
        (_chat_result("   "), "empty"),
        (_chat_result("Please edit the file."), "unified diff"),
    ],
)
def test_openai_compatible_diff_transport_rejects_truncated_empty_and_non_diff(
    result: OpenAIChatResult,
    match: str,
) -> None:
    transport = OpenAICompatibleDiffTransport(chat_client=FakeChatClient(result))

    with pytest.raises(RunnerError, match=match):
        transport.propose(_diff_request())


def test_openai_compatible_diff_transport_converts_real_client_errors_to_runner_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("XAI_API_KEY", "test-key")

    class LengthResponse:
        status = 200

        def __enter__(self) -> LengthResponse:
            return self

        def __exit__(self, *exc: object) -> None:
            return None

        def read(self) -> bytes:
            return json.dumps(
                {
                    "model": "grok-served",
                    "choices": [
                        {
                            "finish_reason": "length",
                            "message": {"content": _valid_diff()},
                        }
                    ],
                }
            ).encode()

    def fake_urlopen(request: Any, timeout: int) -> LengthResponse:
        return LengthResponse()

    client = OpenAICompatibleChatClient(
        config=OpenAIProviderConfig(
            provider="xai",
            base_url="https://api.x.ai/v1",
            api_key_env="XAI_API_KEY",
            model="grok-test",
        ),
        urlopen=fake_urlopen,
    )
    transport = OpenAICompatibleDiffTransport(chat_client=client)

    with pytest.raises(RunnerError, match="truncated|length"):
        transport.propose(_diff_request())


def test_openai_compatible_diff_transport_strips_single_markdown_diff_fence() -> None:
    fenced = "```diff\n" + _valid_diff() + "```\n"
    transport = OpenAICompatibleDiffTransport(chat_client=FakeChatClient(_chat_result(fenced)))

    response = transport.propose(_diff_request())

    assert response.diff_text == _valid_diff()


def test_openai_compatible_diff_transport_adds_missing_final_newline() -> None:
    transport = OpenAICompatibleDiffTransport(chat_client=FakeChatClient(_chat_result(_valid_diff().rstrip("\n"))))

    response = transport.propose(_diff_request())

    assert response.diff_text == _valid_diff()


def test_openai_compatible_diff_transport_repairs_single_new_file_hunk_count() -> None:
    malformed = """diff --git a/docs/index.md b/docs/index.md
new file mode 100644
--- /dev/null
+++ b/docs/index.md
@@ -0,0 +1,12 @@
+# FMC-MCP Documentation
+
+Canonical navigation index for fmc-mcp.
+
+- [README](../README.md)
+- [Setup](setup.md)
+- [Verification](verification.md)
+- [Architecture](architecture.md)
+
+Future documentation locations will be added here as they are created.
"""
    transport = OpenAICompatibleDiffTransport(chat_client=FakeChatClient(_chat_result(malformed)))

    response = transport.propose(_diff_request())

    assert "@@ -0,0 +1,10 @@" in response.diff_text
    assert "@@ -0,0 +1,12 @@" not in response.diff_text
    assert response.provenance is not None
    assert response.provenance["diff_normalization"] == {"single_new_file_hunk_count_repaired": True}


def test_diff_proposer_applies_live_transport_valid_diff_after_patch_gate(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    transport = OpenAICompatibleDiffTransport(chat_client=FakeChatClient(_chat_result(_valid_diff())))
    runner = DiffProposerRunner(transport=transport, success_criterion="value returns 2")

    patch_path = asyncio.run(runner.apply(_hypothesis(), repo))

    assert patch_path.read_text(encoding="utf-8") == _valid_diff()
    assert (repo / "src" / "app.py").read_text(encoding="utf-8") == "def value() -> int:\n    return 2\n"
    provenance = json.loads(patch_path.with_suffix(".patch.provenance.json").read_text(encoding="utf-8"))
    assert provenance["provider"] == "xai"
    assert provenance["model"] == "grok-served"
    assert provenance["hypothesis_id"] == "hyp-diff-1"


def test_same_diff_transport_config_can_target_xai_openai_openrouter() -> None:
    configs = [
        resolve_provider_config("xai", model="grok-test"),
        resolve_provider_config("openai", model="gpt-test"),
        resolve_provider_config("openrouter", model="openrouter-test"),
    ]

    transports = [OpenAICompatibleDiffTransport(provider_config=config) for config in configs]

    assert [transport.provider_config.provider for transport in transports] == ["xai", "openai", "openrouter"]
    assert [transport.provider_config.model for transport in transports] == ["grok-test", "gpt-test", "openrouter-test"]


def test_openai_compatible_diff_transport_requires_explicit_model_without_injected_client() -> None:
    with pytest.raises(ValueError, match="explicit model"):
        OpenAICompatibleDiffTransport()


def test_openai_compatible_diff_transport_strictly_rejects_served_model_mismatch(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("XAI_API_KEY", "test-key")

    class MismatchResponse:
        status = 200

        def __enter__(self) -> MismatchResponse:
            return self

        def __exit__(self, *exc: object) -> None:
            return None

        def read(self) -> bytes:
            return json.dumps(
                {
                    "model": "unexpected-served-model",
                    "choices": [{"finish_reason": "stop", "message": {"content": _valid_diff()}}],
                }
            ).encode()

    def fake_urlopen(request: Any, timeout: int) -> MismatchResponse:
        return MismatchResponse()

    client = OpenAICompatibleChatClient(
        config=resolve_provider_config("xai", model="grok-requested"),
        urlopen=fake_urlopen,
        require_served_model_match=True,
    )
    transport = OpenAICompatibleDiffTransport(chat_client=client)

    with pytest.raises(RunnerError, match="served unexpected model"):
        transport.propose(_diff_request())


def test_diff_proposer_applies_valid_fake_diff_after_patch_gate(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    transport = FakeTransport(
        DiffProposalResponse(
            diff_text=_valid_diff(),
            intent="Change value to two",
            provenance={"transport": "fake"},
        )
    )
    runner = DiffProposerRunner(transport=transport, success_criterion="value returns 2")

    patch_path = asyncio.run(runner.apply(_hypothesis(), repo))

    assert runner.name == RunnerName.codex
    assert patch_path.exists()
    assert patch_path.read_text(encoding="utf-8") == _valid_diff()
    assert (repo / "src" / "app.py").read_text(encoding="utf-8") == "def value() -> int:\n    return 2\n"
    provenance = json.loads(patch_path.with_suffix(".patch.provenance.json").read_text(encoding="utf-8"))
    assert provenance["hypothesis_id"] == "hyp-diff-1"
    assert provenance["target_path"] == "src/app.py"
    assert provenance["intent"] == "Change value to two"
    assert provenance["transport"] == "fake"
    assert transport.requests[0].target_path == "src/app.py"
    assert transport.requests[0].file_contents == "def value() -> int:\n    return 1\n"
    assert transport.requests[0].success_criterion == "value returns 2"


@pytest.mark.parametrize(
    "response",
    [
        DiffProposalResponse(diff_text="", intent="empty"),
        DiffProposalResponse(diff_text="Please change the file.", intent="prose"),
        DiffProposalResponse(diff_text=_valid_diff("private/secret.py"), intent="boundary"),
        DiffProposalResponse(diff_text=_valid_diff(), intent="oversized"),
        DiffProposalResponse(diff_text=_valid_diff(), intent="truncated", truncated=True),
        DiffProposalResponse(diff_text=_valid_diff(), intent="cancelled", cancelled=True),
    ],
)
def test_diff_proposer_rejects_invalid_fake_outputs_without_mutation(
    tmp_path: Path,
    response: DiffProposalResponse,
) -> None:
    repo = _repo(tmp_path, max_lines=1)
    before = (repo / "src" / "app.py").read_text(encoding="utf-8")
    runner = DiffProposerRunner(transport=FakeTransport(response), success_criterion="value returns 2")

    with pytest.raises(RunnerError):
        asyncio.run(runner.apply(_hypothesis(target_files=["src/app.py"]), repo))

    assert (repo / "src" / "app.py").read_text(encoding="utf-8") == before
    assert not (repo / ".arena" / "patches").exists()
    assert subprocess.check_output(["git", "status", "--short"], cwd=repo, text=True) == ""


def test_diff_proposer_runner_router_integration(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    runner = DiffProposerRunner(
        transport=FakeTransport(DiffProposalResponse(diff_text=_valid_diff(), intent="Change value")),
        success_criterion="value returns 2",
    )
    router = RunnerRouter(primary=runner, fallback=runner)

    result = asyncio.run(router.apply(_hypothesis(), repo))

    assert result.success is True
    assert result.error_reason is None
    assert result.runner_used == RunnerName.codex
    assert result.patch_path is not None
    assert result.patch_path.exists()


def test_diff_proposer_rejects_multi_target_hypotheses(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    runner = DiffProposerRunner(
        transport=FakeTransport(DiffProposalResponse(diff_text=_valid_diff(), intent="Change value")),
        success_criterion="value returns 2",
    )

    with pytest.raises(RunnerError, match="exactly one target"):
        asyncio.run(runner.apply(_hypothesis(target_files=["src/app.py", "src/other.py"]), repo))

    assert subprocess.check_output(["git", "status", "--short"], cwd=repo, text=True) == ""


def _new_file_diff(path: str, content: str = "# Docs\n\n") -> str:
    lines = content.splitlines()
    added = "\n".join(f"+{line}" for line in lines) + "\n"
    return f"""diff --git a/{path} b/{path}
new file mode 100644
index 0000000..3b18e51
--- /dev/null
+++ b/{path}
@@ -0,0 +1,{len(lines)} @@
{added}"""


def test_diff_proposer_applies_single_new_file_diff_after_patch_gate(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    transport = FakeTransport(
        DiffProposalResponse(
            diff_text=_new_file_diff("docs/index.md"),
            intent="Create docs index",
            provenance={"transport": "fake"},
        )
    )
    runner = DiffProposerRunner(transport=transport, success_criterion="docs index exists")

    patch_path = asyncio.run(runner.apply(_hypothesis(target_files=["docs/index.md"]), repo))

    assert (repo / "docs" / "index.md").read_text(encoding="utf-8") == "# Docs\n\n"
    assert patch_path.exists()
    assert transport.requests[0].target_path == "docs/index.md"
    assert transport.requests[0].file_contents == ""
    provenance = json.loads(patch_path.with_suffix(".patch.provenance.json").read_text(encoding="utf-8"))
    assert provenance["target_path"] == "docs/index.md"


def test_diff_proposer_rejects_markdown_with_missing_relative_links(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    transport = FakeTransport(
        DiffProposalResponse(
            diff_text=_new_file_diff("docs/index.md", "# Docs\n\n- [Overview](overview.md)\n"),
            intent="Create docs index",
            provenance={"transport": "fake"},
        )
    )
    runner = DiffProposerRunner(transport=transport, success_criterion="docs index links resolve")

    with pytest.raises(RunnerError, match="missing Markdown link target"):
        asyncio.run(runner.apply(_hypothesis(target_files=["docs/index.md"]), repo))

    assert not (repo / ".arena" / "patches").exists()


def test_diff_proposer_repairs_markdown_file_mentions_to_exact_repo_paths(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    _write(repo / "src" / "fmc_mcp" / "config.py", "class Settings:\n    pass\n")
    _write(repo / "docs" / "index.md", "# Docs\n")
    _run(["git", "add", "src/fmc_mcp/config.py", "docs/index.md"], repo)
    _run(["git", "commit", "-m", "add docs and config"], repo)
    transport = FakeTransport(
        DiffProposalResponse(
            diff_text=_new_file_diff("AGENTS.md", "# Agents\n\nSee fmc_mcp/config.py and [Docs](index.md).\n"),
            intent="Create AGENTS",
            provenance={"transport": "fake"},
        )
    )
    runner = DiffProposerRunner(transport=transport, success_criterion="agent docs links resolve")

    patch_path = asyncio.run(runner.apply(_hypothesis(target_files=["AGENTS.md"]), repo))

    text = (repo / "AGENTS.md").read_text(encoding="utf-8")
    assert "src/fmc_mcp/config.py" in text
    assert "See fmc_mcp/config.py" not in text
    assert "[Docs](index.md)" not in text
    assert patch_path.is_file()
    assert "src/fmc_mcp/config.py" in patch_path.read_text(encoding="utf-8")


def test_repair_collapses_doubled_repo_root_prefix(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    _write(repo / "src" / "fmc_mcp" / "config.py", "class Settings:\n    pass\n")
    _run(["git", "add", "src/fmc_mcp/config.py"], repo)
    _run(["git", "commit", "-m", "add config"], repo)
    transport = FakeTransport(
        DiffProposalResponse(
            diff_text=_new_file_diff("AGENTS.md", "# Agents\n\nSee [Config](src/src/fmc_mcp/config.py).\n"),
            intent="Create AGENTS",
            provenance={"transport": "fake"},
        )
    )
    runner = DiffProposerRunner(transport=transport, success_criterion="agent docs links resolve")

    patch_path = asyncio.run(runner.apply(_hypothesis(target_files=["AGENTS.md"]), repo))

    text = (repo / "AGENTS.md").read_text(encoding="utf-8")
    assert "src/src/fmc_mcp/config.py" not in text
    assert "src/fmc_mcp/config.py" in text
    assert "src/fmc_mcp/config.py" in patch_path.read_text(encoding="utf-8")


def test_prefix_collapse_does_not_touch_legitimate_paths(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    _write(repo / "src" / "src" / "real.py", "VALUE = 1\n")
    _run(["git", "add", "src/src/real.py"], repo)
    _run(["git", "commit", "-m", "add real repeated path"], repo)
    transport = FakeTransport(
        DiffProposalResponse(
            diff_text=_new_file_diff("AGENTS.md", "# Agents\n\nSee [Real](src/src/real.py).\n"),
            intent="Create AGENTS",
            provenance={"transport": "fake"},
        )
    )
    runner = DiffProposerRunner(transport=transport, success_criterion="agent docs links resolve")

    asyncio.run(runner.apply(_hypothesis(target_files=["AGENTS.md"]), repo))

    assert "src/src/real.py" in (repo / "AGENTS.md").read_text(encoding="utf-8")


def test_apply_retries_with_gate_error_feedback(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    transport = SequenceTransport(
        [
            DiffProposalResponse(diff_text=_valid_diff("private/secret.py"), intent="Bad boundary", provenance={"transport": "fake"}),
            DiffProposalResponse(diff_text=_valid_diff(), intent="Good diff", provenance={"transport": "fake"}),
        ]
    )
    runner = DiffProposerRunner(transport=transport, success_criterion="value returns 2", repair_budget=1)

    patch_path = asyncio.run(runner.apply(_hypothesis(), repo))

    assert patch_path.exists()
    assert len(transport.requests) == 2
    assert "Previous diff failed" in transport.requests[1].repair_context
    assert runner.repair_events[0]["attempt"] == 1


def test_apply_repair_budget_exhausted_fails_cleanly(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    before = (repo / "src" / "app.py").read_text(encoding="utf-8")
    transport = SequenceTransport(
        [
            DiffProposalResponse(diff_text=_valid_diff("private/secret.py"), intent="Bad boundary", provenance={"transport": "fake"}),
            DiffProposalResponse(diff_text=_valid_diff("private/secret.py"), intent="Bad boundary again", provenance={"transport": "fake"}),
        ]
    )
    runner = DiffProposerRunner(transport=transport, success_criterion="value returns 2", repair_budget=1)

    with pytest.raises(RunnerError, match="patch gate rejected"):
        asyncio.run(runner.apply(_hypothesis(), repo))

    assert len(transport.requests) == 2
    assert (repo / "src" / "app.py").read_text(encoding="utf-8") == before
    assert subprocess.check_output(["git", "status", "--short"], cwd=repo, text=True) == ""


def test_diff_proposer_applies_nested_new_file_diff_when_parent_is_missing(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    transport = FakeTransport(
        DiffProposalResponse(
            diff_text=_new_file_diff("docs/sub/index.md", "# Nested\n\n"),
            intent="Create nested docs index",
            provenance={"transport": "fake"},
        )
    )
    runner = DiffProposerRunner(transport=transport, success_criterion="nested docs index exists")

    patch_path = asyncio.run(runner.apply(_hypothesis(target_files=["docs/sub/index.md"]), repo))

    assert (repo / "docs" / "sub" / "index.md").read_text(encoding="utf-8") == "# Nested\n\n"
    assert patch_path.exists()
    assert transport.requests[0].file_contents == ""


def test_diff_proposer_rejects_protected_missing_target_without_transport_call(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    transport = FakeTransport(
        DiffProposalResponse(
            diff_text=_new_file_diff("private/new.py", "SECRET = 'no'\n"),
            intent="Create protected file",
            provenance={"transport": "fake"},
        )
    )
    runner = DiffProposerRunner(transport=transport, success_criterion="protected file exists")

    with pytest.raises(RunnerError, match="boundary"):
        asyncio.run(runner.apply(_hypothesis(target_files=["private/new.py"]), repo))

    assert transport.requests == []
    assert not (repo / "private" / "new.py").exists()
