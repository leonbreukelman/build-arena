from __future__ import annotations

from collections.abc import AsyncIterator, Mapping, Sequence
from pathlib import Path
from typing import Any, Protocol

from arena.generated.models import (
    Baseline,
    Cycle,
    Event,
    HaltReason,
    Hypothesis,
    RunnerName,
    ScoreRecord,
    Verdict,
    Worktree,
)


class Scanner(Protocol):
    async def scan(self, worktree: Worktree) -> Any: ...


class Scorer(Protocol):
    lock_sha: str

    async def score(self, worktree: Worktree, north_star_id: str) -> ScoreRecord: ...
    async def drift_check(self, baseline: Baseline, worktree: Worktree) -> None: ...


class Hypothesizer(Protocol):
    async def propose(self, cycle: Cycle, scan: Any, history: Any) -> Hypothesis: ...


class AgentRunner(Protocol):
    name: RunnerName

    async def apply(self, hypothesis: Hypothesis, worktree: Worktree) -> Path: ...
    def stream_events(self) -> AsyncIterator[Event]: ...
    async def remaining_credit(self) -> Any: ...


class RunnerRouter(Protocol):
    async def pick(self, call_site: str) -> AgentRunner: ...
    async def report_credit(self, runner: RunnerName, snap: Any) -> None: ...


class Verifier(Protocol):
    async def verify(self, hypothesis: Hypothesis, patch: Path, worktree: Worktree, baseline: Baseline) -> Verdict: ...


class DivergenceDetector(Protocol):
    async def check(self, run_id: str) -> HaltReason | None: ...


class Promoter(Protocol):
    async def promote(self, verdict: Verdict, worktree: Worktree) -> Baseline: ...


class Rollbacker(Protocol):
    async def rollback(self, target: Baseline) -> Baseline: ...


class EventEmitter(Protocol):
    async def emit(self, event: Event) -> None: ...


class DashboardPublisher(Protocol):
    def subscribe(self) -> AsyncIterator[Event]: ...


class HistoryView(Protocol):
    async def recent_verdicts(self, run_id: str, n: int = 50) -> Sequence[Verdict]: ...
    async def fingerprint_cluster_failure_rate(self, run_id: str, window: int = 20) -> float: ...
    async def bandit_state(self, run_id: str) -> Mapping[str, Any]: ...
