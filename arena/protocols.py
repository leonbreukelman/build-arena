from __future__ import annotations

from collections.abc import AsyncIterator, Mapping, Sequence
from pathlib import Path
from typing import Any, Protocol

from arena.generated.models import (
    Baseline,
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
    """Phase 3 symbolic hypothesizer contract.

    The loop glue will adapt Cycle/ProjectModel/HistoryView into the explicit
    cycle_id and AST-diff pattern inputs used by the deterministic Phase 3
    implementation. The hypothesizer remains symbolic: it produces an intent,
    target files, and fingerprint metadata, not a filesystem patch.
    """

    def propose(self, *, cycle_id: str, ast_diff_pattern: str) -> Any: ...


class AgentRunner(Protocol):
    """Phase 3 runner contract: parse/apply within a supplied worktree path.

    Live stream_events and credit snapshots are deferred to the later live CLI
    adapter phase; the current contract is the identity-preserving apply path
    used by RunnerRouter tests.
    """

    name: RunnerName

    async def apply(self, hypothesis: Hypothesis, worktree: Path) -> Path: ...


class RunnerRouter(Protocol):
    """Phase 3 router contract: primary apply with fallback on CreditExhausted."""

    async def apply(self, hypothesis: Hypothesis, worktree: Path) -> Any: ...


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
