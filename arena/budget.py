from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from arena.generated.models import HaltReason

RunnerCreditName = Literal["claude_code", "codex", "copilot_premium"]


@dataclass
class BudgetBreach(RuntimeError):
    reason: HaltReason
    detail: str

    def __str__(self) -> str:
        return self.detail


@dataclass
class BudgetController:
    wall_clock_seconds_cap: int
    cycle_count_cap: int
    claude_code_credits_cap: int | None = None
    codex_credits_cap: int | None = None
    copilot_premium_cap: int | None = None
    start_ts: float | None = None
    wall_clock_seconds_used: int = 0
    cycle_count_used: int = 0
    claude_code_credits_used: int = 0
    codex_credits_used: int = 0
    copilot_premium_used: int = 0
    promotions_total: int = 0
    _breach_checks: list[str] = field(default_factory=list, init=False, repr=False)

    def check(self, *, now: float | None = None) -> None:
        elapsed = self.wall_clock_seconds_used
        if now is not None:
            if self.start_ts is None:
                self.start_ts = now
            elapsed = max(self.wall_clock_seconds_used, int(now - self.start_ts))
        checks = [
            ("wall_clock", elapsed, self.wall_clock_seconds_cap),
            ("cycle_count", self.cycle_count_used, self.cycle_count_cap),
            ("claude_code_credits", self.claude_code_credits_used, self.claude_code_credits_cap),
            ("codex_credits", self.codex_credits_used, self.codex_credits_cap),
            ("copilot_premium", self.copilot_premium_used, self.copilot_premium_cap),
        ]
        for name, used, cap in checks:
            if cap is None:
                continue
            if used >= cap:
                detail = f"{name} budget exhausted: used={used} cap={cap} promotions={self.promotions_total}"
                raise BudgetBreach(self._halt_reason(), detail)

    def record_cycle_started(self) -> None:
        self.cycle_count_used += 1

    def record_promotion(self) -> None:
        self.promotions_total += 1

    def record_runner_credit(self, runner: RunnerCreditName | str, amount: int = 1) -> None:
        if runner == "claude_code":
            self.claude_code_credits_used += amount
        elif runner == "codex":
            self.codex_credits_used += amount
        elif runner == "copilot_premium":
            self.copilot_premium_used += amount
        else:
            raise ValueError(f"unknown credit runner: {runner}")

    def _halt_reason(self) -> HaltReason:
        if self.promotions_total == 0:
            return HaltReason.BUDGET_EXHAUSTED_ZERO_PROMOTIONS
        return HaltReason.WALL_CLOCK_BREACH
