from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Protocol

from arena.events import event_payload
from arena.generated.models import Event, HaltReason


@dataclass
class Diverged(RuntimeError):
    reason: HaltReason
    detail: str

    def __str__(self) -> str:
        return self.detail


class EventReader(Protocol):
    def read_events(self) -> Sequence[Event]: ...


@dataclass
class DivergenceDetector:
    event_log: EventReader
    fingerprint_cluster_failure_rate_max: float = 0.5
    fingerprint_cluster_min_distinct: int = 3
    fingerprint_window: int = 20
    scorer_verifier_disagree_max_consecutive: int = 5
    boundary_violation_attempts_max: int = 3

    def check(self, run_id: str) -> HaltReason | None:
        events = [event for event in self.event_log.read_events() if event.run_id == run_id]
        if self._boundary_attempts(events) >= self.boundary_violation_attempts_max:
            return HaltReason.BOUNDARY_VIOLATION_ATTEMPT
        if self._fingerprint_cluster_failed(events):
            return HaltReason.FINGERPRINT_CLUSTER_FAILURE
        if self._disagreement_streak(events) >= self.scorer_verifier_disagree_max_consecutive:
            return HaltReason.SCORER_VERIFIER_DISAGREEMENT
        return None

    def check_and_raise(self, run_id: str) -> None:
        reason = self.check(run_id)
        if reason is not None:
            raise Diverged(reason, f"divergence detector tripped: {reason.value}")

    @staticmethod
    def _boundary_attempts(events) -> int:
        return sum(1 for event in events if event.type == "BOUNDARY_VIOLATION")

    def _fingerprint_cluster_failed(self, events) -> bool:
        verdicts = [event for event in events if event.type == "VERDICT_DECIDED"][-self.fingerprint_window :]
        seen: set[str] = set()
        failed: set[str] = set()
        for event in verdicts:
            payload = event_payload(event)
            fingerprint_id = payload.get("fingerprint_id")
            if not isinstance(fingerprint_id, str) or not fingerprint_id:
                continue
            seen.add(fingerprint_id)
            outcome = str(payload.get("outcome", ""))
            reject_reason = payload.get("reject_reason")
            if outcome in {"DISCARDED", "ERROR"} or reject_reason:
                failed.add(fingerprint_id)
        if len(failed) < self.fingerprint_cluster_min_distinct:
            return False
        denominator = max(len(seen), 1)
        return (len(failed) / denominator) > self.fingerprint_cluster_failure_rate_max

    @staticmethod
    def _disagreement_streak(events) -> int:
        disagreement_cycles = {_event_cycle_id(event) for event in events if event.type == "SCORER_VERIFIER_DISAGREEMENT"}
        disagreement_cycles.discard(None)
        terminal_cycles = [_event_cycle_id(event) for event in events if event.type == "CYCLE_ENDED"]
        terminal_cycles = [cycle_id for cycle_id in terminal_cycles if cycle_id is not None]
        if terminal_cycles:
            streak = 0
            for cycle_id in reversed(terminal_cycles):
                if cycle_id in disagreement_cycles:
                    streak += 1
                    continue
                break
            return streak

        streak = 0
        for event in reversed(events):
            if event.type == "SCORER_VERIFIER_DISAGREEMENT":
                streak += 1
                continue
            if event.type in {"VERDICT_DECIDED", "PROMOTED"}:
                break
        return streak


def _event_cycle_id(event) -> str | None:
    if event.cycle_id is not None:
        return event.cycle_id
    payload = event_payload(event)
    cycle_id = payload.get("cycle_id")
    if isinstance(cycle_id, str):
        return cycle_id
    return None
