from __future__ import annotations

import asyncio
from pathlib import Path

from arena.generated.models import Hypothesis, RejectReason, RunnerName
from arena.router import RunnerRouter
from arena.runners.base import ApplyResult, CreditExhausted
from arena.runners.claude_code import ClaudeCodeRunner
from arena.runners.ollama import OllamaRunner


def _hypothesis() -> Hypothesis:
    return Hypothesis(
        id="hyp-1",
        cycle_id="cycle-1",
        intent="improve runtime",
        technique_tag="runtime",
        target_cluster="core",
        target_files=["src/pkg/core.py"],
        fingerprint_id="f" * 32,
        proposed_ts=1.0,
    )


def test_claude_weekly_limit_stream_triggers_ollama_fallback(tmp_path: Path) -> None:
    hypothesis = _hypothesis()
    claude = ClaudeCodeRunner(
        events=[{"type": "result", "is_error": True, "result": "You've hit your weekly limit · resets soon"}]
    )
    ollama = OllamaRunner(patch_path=tmp_path / "fallback.patch")
    router = RunnerRouter(primary=claude, fallback=ollama)

    result = asyncio.run(router.apply(hypothesis, tmp_path))

    assert result.success is True
    assert result.runner_used == RunnerName.ollama
    assert result.patch_path == tmp_path / "fallback.patch"
    assert claude.applied_hypotheses == [hypothesis]
    assert ollama.applied_hypotheses == [hypothesis]
    assert result.attempts == (RunnerName.claude_code, RunnerName.ollama)
    assert [event.type for event in result.events] == ["RUNNER_FALLBACK"]
    assert result.events[0].payload["hypothesis_id"] == hypothesis.id


class ExhaustingRunner:
    def __init__(self, name: RunnerName) -> None:
        self.name = name
        self.applied_hypotheses: list[Hypothesis] = []

    async def apply(self, hypothesis: Hypothesis, worktree: Path) -> Path:
        self.applied_hypotheses.append(hypothesis)
        raise CreditExhausted(str(self.name), "forced exhaustion")


def test_router_reports_runner_error_when_primary_and_fallback_exhaust(tmp_path: Path) -> None:
    hypothesis = _hypothesis()
    primary = ExhaustingRunner(RunnerName.claude_code)
    fallback = ExhaustingRunner(RunnerName.ollama)
    router = RunnerRouter(primary=primary, fallback=fallback)

    result = asyncio.run(router.apply(hypothesis, tmp_path))

    assert isinstance(result, ApplyResult)
    assert result.success is False
    assert result.error_reason == RejectReason.RUNNER_ERROR
    assert result.patch_path is None
    assert result.attempts == (RunnerName.claude_code, RunnerName.ollama)
    assert primary.applied_hypotheses == [hypothesis]
    assert fallback.applied_hypotheses == [hypothesis]
