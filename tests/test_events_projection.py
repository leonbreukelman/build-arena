from __future__ import annotations

from arena.events import EventLog


def test_event_log_assigns_monotonic_seq_and_replays_jsonl_projection(tmp_path) -> None:
    log = EventLog(tmp_path / "run-1", run_id="run-1")

    first = log.emit("RUN_STARTED", payload={"run_id": "run-1"})
    second = log.emit("SCAN_COMPLETE", cycle_id="cycle-1", payload={"files": 3})

    assert first.seq == 1
    assert second.seq == 2
    assert [event.type for event in log.read_events()] == ["RUN_STARTED", "SCAN_COMPLETE"]

    initial = log.rebuild_projection()
    assert initial.event_count == 2
    assert initial.max_seq == 2

    log.projection_path.unlink()
    rebuilt = log.ensure_projection_current()

    assert rebuilt.event_count == 2
    assert rebuilt.max_seq == 2


def test_event_log_ignores_incomplete_crash_tail_line(tmp_path) -> None:
    log = EventLog(tmp_path / "run-1", run_id="run-1")
    log.emit("RUN_STARTED")
    with log.events_path.open("ab") as handle:
        handle.write(b'{"seq": 2, "type": "TORN')

    events = log.read_events()

    assert len(events) == 1
    assert events[0].seq == 1
