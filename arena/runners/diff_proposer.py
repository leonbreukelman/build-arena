from __future__ import annotations

import json
import re
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
from arena.markdown_links import check_markdown_links
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
    file_exists: bool = True
    repo_facts: str = ""
    grounding_constraints: tuple[str, ...] = ()


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
        if provider_config is None and chat_client is not None:
            provider_config = getattr(chat_client, "config", None) or OpenAIProviderConfig(
                provider="injected",
                base_url="",
                api_key_env="",
                model="injected-client",
                model_source="injected_client",
            )
        self.provider_config = provider_config or resolve_provider_config(
            provider,
            base_url=base_url,
            api_key_env=api_key_env,
            model=model,
            require_explicit_model=True,
        )
        if self.provider_config.model_source == "provider_default":
            raise ValueError("live diff transport requires an explicit model or provider_config with explicit model source")
        self.max_tokens = max_tokens
        self.chat_client = chat_client or OpenAICompatibleChatClient(
            config=self.provider_config,
            timeout_seconds=timeout_seconds,
            max_tokens=max_tokens,
            require_served_model_match=True,
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
        raw_diff_text = _ensure_trailing_newline(_strip_single_markdown_fence(result.text))
        diff_text = _normalize_single_new_file_hunk_count(raw_diff_text)
        diff_was_normalized = diff_text != raw_diff_text
        if not diff_text.strip():
            raise RunnerError("diff proposal empty")
        if not _looks_like_unified_diff(diff_text):
            raise RunnerError("diff proposal was not a unified diff")
        provenance = dict(result.metadata)
        provenance.setdefault("provider", result.provider)
        provenance.setdefault("model", result.model)
        provenance.setdefault("requested_model", result.requested_model)
        provenance["transport"] = "openai_compatible_diff"
        if diff_was_normalized:
            provenance["diff_normalization"] = {"single_new_file_hunk_count_repaired": True}
        return DiffProposalResponse(
            diff_text=diff_text,
            intent=request.intent,
            provenance=provenance,
            truncated=False,
        )


class DiffProposerRunner:
    name = RunnerName.codex

    def __init__(
        self,
        *,
        transport: DiffTransport,
        success_criterion: str,
        repo_facts: str = "",
        grounding_constraints: tuple[str, ...] = (),
    ) -> None:
        self.transport = transport
        self.success_criterion = success_criterion
        self.repo_facts = repo_facts
        self.grounding_constraints = grounding_constraints
        self.applied_hypotheses: list[Hypothesis] = []

    async def apply(self, hypothesis: Hypothesis, worktree: Path) -> Path:
        self.applied_hypotheses.append(hypothesis)
        target = worktree.resolve()
        config = load_goal_config(target)
        target_path = _single_target_path(hypothesis, config)
        file_contents, file_exists = _target_file_contents_or_empty(target, target_path)
        request = DiffProposalRequest(
            hypothesis_id=hypothesis.id,
            target_path=target_path,
            file_contents=file_contents,
            success_criterion=self.success_criterion,
            goal_config_sha=config.content_hash,
            intent=hypothesis.intent,
            file_exists=file_exists,
            repo_facts=self.repo_facts,
            grounding_constraints=self.grounding_constraints,
        )
        response = self.transport.propose(request)
        _raise_for_response_status(response)
        gate = validate_unified_diff(target, response.diff_text, goal_config=config)
        if not gate.accepted:
            raise RunnerError(f"patch gate rejected: {gate.reason}")
        _apply_diff(target, response.diff_text)
        try:
            repaired_markdown = _validate_changed_markdown(target, gate.touched_paths)
        except RunnerError:
            _reverse_diff(target, response.diff_text)
            raise
        if repaired_markdown:
            diff_to_record = _current_diff(target, gate.touched_paths)
            if not diff_to_record:
                _discard_touched_paths(target, gate.touched_paths)
                raise RunnerError("Markdown repair produced no recordable diff")
        else:
            diff_to_record = response.diff_text
        patch_path = target / ".arena" / "patches" / f"{hypothesis.id}.patch"
        patch_path.parent.mkdir(parents=True, exist_ok=True)
        patch_path.write_text(diff_to_record, encoding="utf-8")
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
    file_state = (
        "The target file already exists; return a normal single-file edit diff."
        if request.file_exists
        else "The target file does not exist; return a single-file new-file unified diff using /dev/null as the old path."
    )
    facts = request.repo_facts.strip() or "No additional repository facts supplied."
    constraints = "\n".join(f"- {item}" for item in request.grounding_constraints) or "- Use only the provided target file and repository facts; do not invent files, links, or commands."
    return (
        "Return only a unified diff for exactly the target file below.\n"
        "Do not include markdown fences, explanations, or changes to any other file.\n"
        f"{file_state}\n\n"
        f"Hypothesis ID: {request.hypothesis_id}\n"
        f"Target path: {request.target_path}\n"
        f"Success criterion: {request.success_criterion}\n"
        f"Goal config SHA: {request.goal_config_sha}\n"
        f"Intent: {request.intent}\n\n"
        "Repository facts:\n"
        f"{facts}\n\n"
        "Markdown link rules:\n"
        "- When editing Markdown, create local Markdown links only to exact repository-relative paths shown in the Repository facts above.\n"
        "- Do not shorten repository-relative paths in Markdown links or plain file mentions: use `docs/index.md` and `src/pkg/file.py`, not `index.md` or `file.py`.\n"
        "- If a source file is relevant, mention the exact path from the Source files list. If no exact path is listed, avoid naming the file.\n\n"
        "Grounding constraints:\n"
        f"{constraints}\n\n"
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


def _normalize_single_new_file_hunk_count(text: str) -> str:
    """Repair a common LLM error in otherwise valid single new-file diffs.

    Grok sometimes emits a correct ``/dev/null`` new-file diff with the hunk
    header line count copied from an estimate rather than the actual number of
    added lines. This deterministic adapter fix only applies to one-file,
    one-hunk, additions-only new-file diffs; all other shapes are left for the
    patch gate to accept or reject unchanged.
    """

    lines = text.splitlines()
    if len([line for line in lines if line.startswith("diff --git ")]) != 1:
        return text
    if "--- /dev/null" not in lines:
        return text
    hunk_indices = [index for index, line in enumerate(lines) if line.startswith("@@ ")]
    if len(hunk_indices) != 1:
        return text
    hunk_index = hunk_indices[0]
    header = lines[hunk_index]
    match = re.fullmatch(r"@@ -0,0 \+1(?:,\d+)? @@(.*)", header)
    if match is None:
        return text
    body = lines[hunk_index + 1 :]
    if any(line.startswith("-") or line.startswith(" ") for line in body):
        return text
    if not all(line.startswith("+") or line == r"\ No newline at end of file" for line in body):
        return text
    added_lines = sum(1 for line in body if line.startswith("+"))
    lines[hunk_index] = f"@@ -0,0 +1,{added_lines} @@{match.group(1)}"
    normalized = "\n".join(lines)
    return normalized + ("\n" if text.endswith("\n") else "")


def _looks_like_unified_diff(text: str) -> bool:
    stripped = text.lstrip()
    return stripped.startswith("diff --git ") or stripped.startswith("--- ")


def _target_file_contents_or_empty(target: Path, target_path: str) -> tuple[str, bool]:
    file_path = target / target_path
    if file_path.exists():
        if not file_path.is_file():
            raise RunnerError(f"target path is not a file: {target_path}")
        return file_path.read_text(encoding="utf-8"), True

    existing_parent = file_path.parent
    while not existing_parent.exists() and existing_parent != target:
        existing_parent = existing_parent.parent
    if not existing_parent.exists():
        raise RunnerError(f"target parent is outside repository: {target_path}")
    if not existing_parent.is_dir():
        raise RunnerError(f"target parent is not a directory: {target_path}")
    resolved_parent = existing_parent.resolve()
    if resolved_parent != target and target not in resolved_parent.parents:
        raise RunnerError(f"target parent escapes repository: {target_path}")
    return "", False


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


def _reverse_diff(worktree: Path, diff_text: str) -> None:
    subprocess.run(
        ["git", "apply", "-R", "-"],
        cwd=worktree,
        input=diff_text,
        text=True,
        capture_output=True,
        check=False,
    )


def _discard_touched_paths(worktree: Path, touched_paths: tuple[str, ...]) -> None:
    for path in touched_paths:
        if _is_git_tracked(worktree, path):
            subprocess.run(["git", "checkout", "--", path], cwd=worktree, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
        else:
            subprocess.run(["git", "clean", "-f", "--", path], cwd=worktree, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)


def _validate_changed_markdown(worktree: Path, touched_paths: tuple[str, ...]) -> bool:
    repaired_any = False
    for raw_path in touched_paths:
        if not raw_path.endswith(".md"):
            continue
        path = worktree / raw_path
        if not path.exists() or not path.is_file():
            continue
        report = check_markdown_links(worktree, path)
        if report.ok:
            continue
        if report.missing or report.escaped:
            before = path.read_text(encoding="utf-8")
            _repair_markdown_references(worktree, path, report)
            repaired_any = repaired_any or path.read_text(encoding="utf-8") != before
            report = check_markdown_links(worktree, path)
        if report.missing:
            missing = ", ".join(f"{item.link}->{item.resolved_path}" for item in report.missing)
            raise RunnerError(f"missing Markdown link target: {missing}")
        if report.escaped:
            escaped = ", ".join(f"{item.link}->{item.resolved_path}" for item in report.escaped)
            raise RunnerError(f"Markdown link escapes repository: {escaped}")
    return repaired_any


def _repair_markdown_references(worktree: Path, path: Path, report: Any) -> None:
    replacements: dict[str, str] = {}
    existing_paths = _existing_repo_paths(worktree)
    for item in (*report.missing, *report.escaped):
        if item.link in replacements:
            continue
        match = _unique_suffix_match(item.link, existing_paths)
        if match is not None:
            replacements[item.link] = match
    if not replacements:
        return
    text = path.read_text(encoding="utf-8")
    for old, new in sorted(replacements.items(), key=lambda item: len(item[0]), reverse=True):
        text = text.replace(old, new)
    path.write_text(text, encoding="utf-8")


def _existing_repo_paths(worktree: Path) -> tuple[str, ...]:
    ignored = {".git", ".venv", ".pytest_cache", ".mypy_cache", ".ruff_cache", "__pycache__", "node_modules"}
    paths: list[str] = []
    for path in worktree.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(worktree)
        if any(part in ignored or part.startswith(".") for part in rel.parts):
            continue
        paths.append(rel.as_posix())
    return tuple(sorted(paths))


def _unique_suffix_match(link: str, existing_paths: tuple[str, ...]) -> str | None:
    normalized = link.lstrip("/").split("#", 1)[0]
    if not normalized or ":" in normalized:
        return None
    matches = [path for path in existing_paths if path == normalized or path.endswith("/" + normalized)]
    return matches[0] if len(matches) == 1 else None


def _current_diff(worktree: Path, touched_paths: tuple[str, ...]) -> str:
    tracked: list[str] = []
    untracked: list[str] = []
    for path in touched_paths:
        if _is_git_tracked(worktree, path):
            tracked.append(path)
        elif (worktree / path).is_file():
            untracked.append(path)
    chunks: list[str] = []
    if tracked:
        proc = subprocess.run(
            ["git", "diff", "--", *tracked],
            cwd=worktree,
            text=True,
            capture_output=True,
            check=False,
        )
        if proc.returncode == 0 and proc.stdout:
            chunks.append(proc.stdout)
    for path in untracked:
        proc = subprocess.run(
            ["git", "diff", "--no-index", "--", "/dev/null", path],
            cwd=worktree,
            text=True,
            capture_output=True,
            check=False,
        )
        if proc.returncode in {0, 1} and proc.stdout:
            chunks.append(proc.stdout)
    return "".join(chunks)


def _is_git_tracked(worktree: Path, path: str) -> bool:
    proc = subprocess.run(
        ["git", "ls-files", "--error-unmatch", "--", path],
        cwd=worktree,
        text=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return proc.returncode == 0


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
