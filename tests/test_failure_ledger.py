from __future__ import annotations

import pytest

from arena.ledger import FingerprintCollisionError, FingerprintFailureLedger


def test_failure_ledger_rejects_recorded_failed_fingerprint_after_reopen(tmp_path) -> None:
    ledger_path = tmp_path / "failures.jsonl"
    ledger = FingerprintFailureLedger(ledger_path)
    ledger.record_failure(
        fingerprint_id="a" * 32,
        hypothesis_id="hyp-1",
        cycle_id="cycle-1",
        reject_reason="TEST_FAILURE",
    )

    reopened = FingerprintFailureLedger(ledger_path)

    assert reopened.has_failed("a" * 32) is True
    assert reopened.has_failed("b" * 32) is False


def test_failure_ledger_collision_check_rejects_before_runner_spawn(tmp_path) -> None:
    ledger = FingerprintFailureLedger(tmp_path / "failures.jsonl")
    fingerprint_id = "b" * 32
    ledger.record_failure(
        fingerprint_id=fingerprint_id,
        hypothesis_id="hyp-old",
        cycle_id="cycle-old",
        reject_reason="TEST_FAILURE",
    )
    runner_spawned = False

    def spawn_runner() -> None:
        nonlocal runner_spawned
        runner_spawned = True

    with pytest.raises(FingerprintCollisionError, match=fingerprint_id):
        ledger.ensure_not_failed(fingerprint_id=fingerprint_id, hypothesis_id="hyp-new")
        spawn_runner()

    assert runner_spawned is False


def test_failure_ledger_collision_check_permits_clean_fingerprint_spawn(tmp_path) -> None:
    ledger = FingerprintFailureLedger(tmp_path / "failures.jsonl")
    runner_spawned = False

    def spawn_runner() -> None:
        nonlocal runner_spawned
        runner_spawned = True

    ledger.ensure_not_failed(fingerprint_id="e" * 32, hypothesis_id="hyp-clean")
    spawn_runner()

    assert runner_spawned is True


def test_successful_fingerprint_does_not_block_retry(tmp_path) -> None:
    ledger = FingerprintFailureLedger(tmp_path / "failures.jsonl")
    ledger.record_success(
        fingerprint_id="c" * 32,
        hypothesis_id="hyp-2",
        cycle_id="cycle-2",
    )

    assert ledger.has_failed("c" * 32) is False


def test_failure_ledger_ignores_malformed_jsonl_rows_without_mutating(tmp_path) -> None:
    ledger_path = tmp_path / "failures.jsonl"
    ledger_path.write_text('{bad json}\n{"fingerprint_id":"d", "outcome":"DISCARDED"}\n')

    ledger = FingerprintFailureLedger(ledger_path)

    assert ledger.has_failed("d") is True
    assert ledger_path.read_text() == '{bad json}\n{"fingerprint_id":"d", "outcome":"DISCARDED"}\n'
