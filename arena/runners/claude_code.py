from __future__ import annotations

import json
import re
from collections.abc import Iterable
from pathlib import Path
from typing import Any

from arena.generated.models import Hypothesis, RunnerName
from arena.runners.base import CreditExhausted, RunnerError, ViewBeforeEditViolation

CLAUDE_CREDIT_RE = re.compile(
    r"hit your (weekly|session|Opus|usage) limit|"
    r'"error"\s*:\s*"rate_limit"',
    re.IGNORECASE,
)


class ClaudeStreamGuard:
    """Enforce ViewBeforeEdit on Claude Code stream-json assistant turns."""

    def process_event(self, event: dict[str, Any]) -> None:
        if event.get("type") != "assistant":
            return
        read_set: set[str] = set()
        blocks = event.get("message", {}).get("content", [])
        for block in blocks:
            if block.get("type") != "tool_use":
                continue
            name = str(block.get("name", ""))
            file_path = _tool_file_path(block)
            if not file_path:
                continue
            normalized = _normalize_path(file_path)
            if name == "Read":
                read_set.add(normalized)
            elif name in {"Edit", "Write"} and normalized not in read_set:
                raise ViewBeforeEditViolation(
                    f"{name} on {normalized} without same-turn Read"
                )


class ClaudeCodeRunner:
    name = RunnerName.claude_code

    def __init__(self, *, events: Iterable[dict[str, Any]] | None = None, patch_path: Path | None = None) -> None:
        self.events = list(events or [])
        self.patch_path = patch_path
        self.applied_hypotheses: list[Hypothesis] = []
        self.guard = ClaudeStreamGuard()

    async def apply(self, hypothesis: Hypothesis, worktree: Path) -> Path:
        self.applied_hypotheses.append(hypothesis)
        for event in self.events:
            self._dispatch(event)
        return self.patch_path or (worktree / "claude.patch")

    def _dispatch(self, event: dict[str, Any]) -> None:
        self.guard.process_event(event)
        raw = json.dumps(event, sort_keys=True)
        if event.get("type") == "result" and event.get("is_error") and CLAUDE_CREDIT_RE.search(raw):
            raise CreditExhausted(self.name.value, str(event.get("result", "")))
        if event.get("type") == "result" and event.get("is_error"):
            raise RunnerError(str(event.get("result", "claude result error")))
        if event.get("type") == "system" and event.get("subtype") == "api_retry" and CLAUDE_CREDIT_RE.search(raw):
            raise CreditExhausted(self.name.value, raw)


def _tool_file_path(block: dict[str, Any]) -> str | None:
    value = block.get("input", {})
    if not isinstance(value, dict):
        return None
    raw = value.get("file_path") or value.get("path")
    if raw is None:
        return None
    return str(raw)


def _normalize_path(path: str) -> str:
    return path.replace("\\", "/").strip().lstrip("/")
