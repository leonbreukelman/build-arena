from __future__ import annotations

from arena.divergence import DivergenceDetector
from arena.events import EventLog
from arena.generated.models import HaltReason


def test_boundary_violation_attempts_trip_after_threshold(tmp_path) -> None:
    log = EventLog(tmp_path / "run-1", run_id="run-1")
    detector = DivergenceDetector(log, boundary_violation_attempts_max=3)

    for idx in range(3):
        log.emit("BOUNDARY_VIOLATION", payload={"hypothesis_id": f"hyp-{idx}"})

    assert detector.check("run-1") == HaltReason.BOUNDARY_VIOLATION_ATTEMPT


def test_fingerprint_cluster_failure_requires_minimum_distinct_fingerprints(tmp_path) -> None:
    log = EventLog(tmp_path / "run-1", run_id="run-1")
    detector = DivergenceDetector(
        log,
        fingerprint_cluster_failure_rate_max=0.5,
        fingerprint_cluster_min_distinct=3,
        fingerprint_window=20,
    )

    for idx in range(2):
        log.emit(
            "VERDICT_DECIDED",
            payload={
                "fingerprint_id": f"{idx:032x}",
                "outcome": "DISCARDED",
                "reject_reason": "TEST_FAILURE",
            },
        )
    assert detector.check("run-1") is None

    log.emit(
        "VERDICT_DECIDED",
        payload={
            "fingerprint_id": f"{2:032x}",
            "outcome": "DISCARDED",
            "reject_reason": "RUNNER_ERROR",
        },
    )

    assert detector.check("run-1") == HaltReason.FINGERPRINT_CLUSTER_FAILURE


def test_scorer_verifier_disagreement_streak_trips(tmp_path) -> None:
    log = EventLog(tmp_path / "run-1", run_id="run-1")
    detector = DivergenceDetector(log, scorer_verifier_disagree_max_consecutive=5)

    for idx in range(5):
        log.emit("SCORER_VERIFIER_DISAGREEMENT", payload={"cycle_id": f"cycle-{idx}"})

    assert detector.check("run-1") == HaltReason.SCORER_VERIFIER_DISAGREEMENT
