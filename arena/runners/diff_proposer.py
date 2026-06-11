from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Protocol

from arena.generated.models import Hypothesis, RunnerName
from arena.llm_adapter import (
    OpenAICompatibleChatClient,
    OpenAIProviderConfig,
    resolve_provider_config,
)
from arena.patch_gate import validate_unified_diff
from arena.runners.base import RunnerError
from scorer.goal_config import GoalConfig, load_goal_config


@dataclass(frozen=True)
class DiffProposalRequest:
    hypothesis_id: str
    target_path: str
    file_contents: str
    success_criterion: str
    goal_config_sha: str
    intent: str


@dataclass(frozen=True)
class DiffProposalResponse:
    diff_text: str
    intent: str
    provenance: dict[str, Any] | None = None
    truncated: bool = False
    cancelled: bool = False


class DiffTransport(Protocol):
    def propose(self, request: DiffProposalRequest) -> DiffProposalResponse: ...


class OpenAICompatibleDiffTransport:
    def __init__(
        self,
        *,
        chat_client: Any | None = None,
        provider_config: OpenAIProviderConfig | None = None,
        provider: str = "xai",
        base_url: str | None = None,
        api_key_env: str | None = None,
        model: str | None = None,
        timeout_seconds: int = 120,
        max_tokens: int = 4096,
    ) -> None:
        if chat_client is None and provider_config is None and model is None:
            raise ValueError("live diff transport requires an explicit model or provider_config")
        self.provider_config = provider_config or resolve_provider_config(
            provider,
            base_url=base_url,
            api_key_env=api_key_env,
            model=model,
        )
        self.max_tokens = max_tokens
        self.chat_client = chat_client or OpenAICompatibleChatClient(
            config=self.provider_config,
            timeout_seconds=timeout_seconds,
            max_tokens=max_tokens,
        )

    def propose(self, request: DiffProposalRequest) -> DiffProposalResponse:
        try:
            result = self.chat_client.complete(
                messages=[
                    {
                        "role": "system",
                        "content": "Return only a unified diff. No markdown, no prose, no explanations.",
                    },
                    {"role": "user", "content": _diff_prompt(request)},
                ],
                response_format=None,
                max_tokens=self.max_tokens,
            )
        except ValueError as exc:
            raise RunnerError(f"diff proposal provider failed: {exc}") from exc
        if str(result.finish_reason).lower() == "length":
            raise RunnerError("diff proposal truncated")
        diff_text = _ensure_trailing_newline(_strip_single_markdown_fence(result.text))
        if not diff_text.strip():
            raise RunnerError("diff proposal empty")
        if not _looks_like_unified_diff(diff_text):
            raise RunnerError("diff proposal was not a unified diff")
        provenance = dict(result.metadata)
        provenance.setdefault("provider", result.provider)
        provenance.setdefault("model", result.model)
        provenance.setdefault("requested_model", result.requested_model)
        provenance["transport"] = "openai_compatible_diff"
        return DiffProposalResponse(
            diff_text=diff_text,
            intent=request.intent,
            provenance=provenance,
            truncated=False,
        )


class DiffProposerRunner:
    name = RunnerName.codex

    def __init__(self, *, transport: DiffTransport, success_criterion: str) -> None:
        self.transport = transport
        self.success_criterion = success_criterion
        self.applied_hypotheses: list[Hypothesis] = []

    async def apply(self, hypothesis: Hypothesis, worktree: Path) -> Path:
        self.applied_hypotheses.append(hypothesis)
        target = worktree.resolve()
        config = load_goal_config(target)
        target_path = _single_target_path(hypothesis, config)
        file_path = target / target_path
        if not file_path.exists() or not file_path.is_file():
            raise RunnerError(f"target file does not exist: {target_path}")
        request = DiffProposalRequest(
            hypothesis_id=hypothesis.id,
            target_path=target_path,
            file_contents=file_path.read_text(encoding="utf-8"),
            success_criterion=self.success_criterion,
            goal_config_sha=config.content_hash,
            intent=hypothesis.intent,
        )
        response = self.transport.propose(request)
        _raise_for_response_status(response)
        gate = validate_unified_diff(target, response.diff_text, goal_config=config)
        if not gate.accepted:
            raise RunnerError(f"patch gate rejected: {gate.reason}")
        _apply_diff(target, response.diff_text)
        patch_path = target / ".arena" / "patches" / f"{hypothesis.id}.patch"
        patch_path.parent.mkdir(parents=True, exist_ok=True)
        patch_path.write_text(response.diff_text, encoding="utf-8")
        patch_path.with_suffix(".patch.provenance.json").write_text(
            json.dumps(
                _provenance(hypothesis, target_path, response, gate.to_jsonable()),
                sort_keys=True,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        return patch_path


def _diff_prompt(request: DiffProposalRequest) -> str:
    return (
        "Return only a unified diff for exactly the target file below.\n"
        "Do not include markdown fences, explanations, or changes to any other file.\n\n"
        f"Hypothesis ID: {request.hypothesis_id}\n"
        f"Target path: {request.target_path}\n"
        f"Success criterion: {request.success_criterion}\n"
        f"Goal config SHA: {request.goal_config_sha}\n"
        f"Intent: {request.intent}\n\n"
        "Current file contents:\n"
        "```text\n"
        f"{request.file_contents}"
        "```\n"
    )


def _strip_single_markdown_fence(text: str) -> str:
    stripped = text.strip()
    if not stripped.startswith("```"):
        return text
    first_newline = stripped.find("\n")
    last_fence = stripped.rfind("```")
    if first_newline == -1 or last_fence <= first_newline:
        return text
    return stripped[first_newline + 1 : last_fence]


def _ensure_trailing_newline(text: str) -> str:
    if text and not text.endswith("\n"):
        return text + "\n"
    return text


def _looks_like_unified_diff(text: str) -> bool:
    stripped = text.lstrip()
    return stripped.startswith("diff --git ") or stripped.startswith("--- ")


def _single_target_path(hypothesis: Hypothesis, goal_config: GoalConfig) -> str:
    if len(hypothesis.target_files) != 1:
        raise RunnerError("diff proposer requires exactly one target file")
    raw = hypothesis.target_files[0]
    path = PurePosixPath(raw.replace("\\", "/"))
    if path.is_absolute() or ".." in path.parts:
        raise RunnerError(f"target file must be repository-relative: {raw}")
    normalized = path.as_posix().removeprefix("./")
    if not normalized:
        raise RunnerError("target file must be non-empty")
    from arena.boundary import is_boundary_violation

    if is_boundary_violation([normalized], goal_config=goal_config):
        raise RunnerError(f"target file violates boundary: {normalized}")
    return normalized


def _raise_for_response_status(response: DiffProposalResponse) -> None:
    if response.cancelled:
        raise RunnerError("diff proposal cancelled")
    if response.truncated:
        raise RunnerError("diff proposal truncated")
    if not response.diff_text.strip():
        raise RunnerError("diff proposal empty")


def _apply_diff(worktree: Path, diff_text: str) -> None:
    proc = subprocess.run(
        ["git", "apply", "-"],
        cwd=worktree,
        input=diff_text,
        text=True,
        capture_output=True,
        check=False,
    )
    if proc.returncode != 0:
        raise RunnerError(f"git apply failed after patch gate: {proc.stderr.strip()}")


def _provenance(
    hypothesis: Hypothesis,
    target_path: str,
    response: DiffProposalResponse,
    patch_gate: dict[str, Any],
) -> dict[str, Any]:
    payload = dict(response.provenance or {})
    payload.update(
        {
            "hypothesis_id": hypothesis.id,
            "fingerprint_id": hypothesis.fingerprint_id,
            "target_path": target_path,
            "intent": response.intent,
            "patch_gate": patch_gate,
        }
    )
    return payload
