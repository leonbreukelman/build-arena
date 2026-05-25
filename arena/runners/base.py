from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from arena.generated.models import Hypothesis, RejectReason, RunnerName


class CreditExhausted(RuntimeError):
    def __init__(self, runner: str, detail: str) -> None:
        super().__init__(detail)
        self.runner = runner
        self.detail = detail


class RunnerError(RuntimeError):
    pass


class ViewBeforeEditViolation(RunnerError):
    pass


@dataclass(frozen=True)
class RouterEvent:
    type: str
    payload: dict[str, str]


@dataclass(frozen=True)
class ApplyResult:
    hypothesis: Hypothesis
    runner_used: RunnerName | None
    patch_path: Path | None
    attempts: tuple[RunnerName, ...]
    events: tuple[RouterEvent, ...]
    error_reason: RejectReason | None = None
    error_detail: str | None = None

    @property
    def success(self) -> bool:
        return self.patch_path is not None and self.error_reason is None
