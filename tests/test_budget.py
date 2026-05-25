from __future__ import annotations

import pytest

from arena.budget import BudgetBreach, BudgetController
from arena.generated.models import HaltReason


def test_zero_promotion_cycle_cap_reports_zero_promotion_halt_reason() -> None:
    budget = BudgetController(wall_clock_seconds_cap=999, cycle_count_cap=1, start_ts=0.0)

    budget.record_cycle_started()

    with pytest.raises(BudgetBreach) as exc_info:
        budget.check(now=1.0)

    assert exc_info.value.reason == HaltReason.BUDGET_EXHAUSTED_ZERO_PROMOTIONS
    assert "cycle_count" in exc_info.value.detail


def test_cap_after_promotion_reports_wall_clock_breach() -> None:
    budget = BudgetController(wall_clock_seconds_cap=10, cycle_count_cap=99, start_ts=0.0)

    budget.record_promotion()

    with pytest.raises(BudgetBreach) as exc_info:
        budget.check(now=10.0)

    assert exc_info.value.reason == HaltReason.WALL_CLOCK_BREACH
    assert "wall_clock" in exc_info.value.detail


def test_runner_credit_cap_uses_zero_promotion_reason_until_first_promotion() -> None:
    budget = BudgetController(
        wall_clock_seconds_cap=999,
        cycle_count_cap=99,
        claude_code_credits_cap=2,
        start_ts=0.0,
    )

    budget.record_runner_credit("claude_code", 2)

    with pytest.raises(BudgetBreach) as exc_info:
        budget.check(now=1.0)

    assert exc_info.value.reason == HaltReason.BUDGET_EXHAUSTED_ZERO_PROMOTIONS
    assert "claude_code_credits" in exc_info.value.detail
