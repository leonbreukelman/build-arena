from __future__ import annotations

from pathlib import Path

from arena.generated.models import Hypothesis, RejectReason, RunnerName
from arena.protocols import AgentRunner
from arena.runners.base import ApplyResult, CreditExhausted, RouterEvent, RunnerError


class RunnerRouter:
    def __init__(self, *, primary: AgentRunner, fallback: AgentRunner) -> None:
        self.primary = primary
        self.fallback = fallback

    async def apply(self, hypothesis: Hypothesis, worktree: Path) -> ApplyResult:
        attempts: list[RunnerName] = []
        events: list[RouterEvent] = []
        try:
            attempts.append(self.primary.name)
            patch_path = await self.primary.apply(hypothesis, worktree)
            return ApplyResult(
                hypothesis=hypothesis,
                runner_used=self.primary.name,
                patch_path=patch_path,
                attempts=tuple(attempts),
                events=tuple(events),
            )
        except CreditExhausted as primary_error:
            events.append(
                RouterEvent(
                    type="RUNNER_FALLBACK",
                    payload={
                        "hypothesis_id": hypothesis.id,
                        "fingerprint_id": hypothesis.fingerprint_id,
                        "from_runner": self.primary.name.value,
                        "to_runner": self.fallback.name.value,
                        "detail": primary_error.detail,
                    },
                )
            )
        except RunnerError as error:
            return _error_result(hypothesis, attempts, events, str(error))

        try:
            attempts.append(self.fallback.name)
            patch_path = await self.fallback.apply(hypothesis, worktree)
            return ApplyResult(
                hypothesis=hypothesis,
                runner_used=self.fallback.name,
                patch_path=patch_path,
                attempts=tuple(attempts),
                events=tuple(events),
            )
        except (CreditExhausted, RunnerError) as error:
            return _error_result(hypothesis, attempts, events, str(error))


def _error_result(
    hypothesis: Hypothesis,
    attempts: list[RunnerName],
    events: list[RouterEvent],
    detail: str,
) -> ApplyResult:
    return ApplyResult(
        hypothesis=hypothesis,
        runner_used=None,
        patch_path=None,
        attempts=tuple(attempts),
        events=tuple(events),
        error_reason=RejectReason.RUNNER_ERROR,
        error_detail=detail,
    )
