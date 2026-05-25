from __future__ import annotations

import hashlib
import json
import os
import sqlite3
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from arena.generated.models import Event


@dataclass(frozen=True)
class ProjectionSummary:
    event_count: int
    max_seq: int


class EventLog:
    """Append-only JSONL event log with rebuildable SQLite projection.

    JSONL is the source of truth. The SQLite database is deliberately a thin
    event projection for Phase 4 so it can be deleted and rebuilt without
    changing loop behavior.
    """

    def __init__(self, run_dir: Path, *, run_id: str) -> None:
        self.run_dir = run_dir
        self.run_id = run_id
        self.events_path = run_dir / "events.jsonl"
        self.projection_path = run_dir / "projection.sqlite"
        self.run_dir.mkdir(parents=True, exist_ok=True)
        self._next_seq_cache: int | None = None

    def emit(
        self,
        type: str,
        *,
        cycle_id: str | None = None,
        payload: dict[str, Any] | None = None,
        level: str = "info",
        ts: float | None = None,
    ) -> Event:
        seq = self._next_seq()
        payload_inline = None
        payload_json_sha = None
        if payload is not None:
            payload_inline = json.dumps(payload, sort_keys=True, separators=(",", ":"))
            payload_json_sha = hashlib.sha256(payload_inline.encode("utf-8")).hexdigest()
        event = Event(
            id=f"evt-{self.run_id}-{seq}",
            run_id=self.run_id,
            cycle_id=cycle_id,
            seq=seq,
            ts=ts if ts is not None else time.time(),
            type=type,
            level=level,
            payload_json_sha=payload_json_sha,
            payload_inline=payload_inline,
        )
        self._append_event(event)
        self._next_seq_cache = seq + 1
        return event

    def read_events(self) -> list[Event]:
        if not self.events_path.exists():
            return []
        events: list[Event] = []
        for raw_line in self.events_path.read_text().splitlines():
            line = raw_line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
                events.append(Event(**data))
            except (json.JSONDecodeError, TypeError, ValueError):
                # Crash-tail tolerance: a partial final line is ignored; earlier
                # complete lines remain canonical.
                continue
        return events

    def rebuild_projection(self) -> ProjectionSummary:
        if self.projection_path.exists():
            self.projection_path.unlink()
        events = self.read_events()
        with sqlite3.connect(self.projection_path) as conn:
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS events (
                    seq INTEGER PRIMARY KEY,
                    id TEXT NOT NULL,
                    run_id TEXT NOT NULL,
                    cycle_id TEXT,
                    ts REAL NOT NULL,
                    type TEXT NOT NULL,
                    level TEXT,
                    payload_json_sha TEXT,
                    payload_inline TEXT
                )
                """
            )
            conn.executemany(
                """
                INSERT INTO events(seq, id, run_id, cycle_id, ts, type, level, payload_json_sha, payload_inline)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        event.seq,
                        event.id,
                        event.run_id,
                        event.cycle_id,
                        event.ts,
                        event.type,
                        event.level,
                        event.payload_json_sha,
                        event.payload_inline,
                    )
                    for event in events
                ],
            )
            conn.commit()
        return ProjectionSummary(event_count=len(events), max_seq=max((event.seq for event in events), default=0))

    def ensure_projection_current(self) -> ProjectionSummary:
        jsonl_events = self.read_events()
        jsonl_max = max((event.seq for event in jsonl_events), default=0)
        if not self.projection_path.exists():
            return self.rebuild_projection()
        with sqlite3.connect(self.projection_path) as conn:
            try:
                row = conn.execute("SELECT COUNT(*), COALESCE(MAX(seq), 0) FROM events").fetchone()
            except sqlite3.DatabaseError:
                return self.rebuild_projection()
        event_count = int(row[0]) if row else 0
        max_seq = int(row[1]) if row else 0
        if max_seq < jsonl_max or event_count != len(jsonl_events):
            return self.rebuild_projection()
        return ProjectionSummary(event_count=event_count, max_seq=max_seq)

    def _next_seq(self) -> int:
        if self._next_seq_cache is not None:
            return self._next_seq_cache
        self._next_seq_cache = max((event.seq for event in self.read_events()), default=0) + 1
        return self._next_seq_cache

    def _append_event(self, event: Event) -> None:
        line = json.dumps(event.model_dump(mode="json"), sort_keys=True, separators=(",", ":")) + "\n"
        with self.events_path.open("a", encoding="utf-8") as handle:
            handle.write(line)
            handle.flush()
            os.fsync(handle.fileno())


def event_payload(event: Event) -> dict[str, Any]:
    if not event.payload_inline:
        return {}
    try:
        value = json.loads(event.payload_inline)
    except json.JSONDecodeError:
        return {}
    if isinstance(value, dict):
        return value
    return {}
