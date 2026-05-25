from __future__ import annotations

import json
from pathlib import Path
from typing import Any

FAILURE_OUTCOMES = {"DISCARDED", "ERROR"}
SUCCESS_OUTCOMES = {"PROMOTED"}


class FingerprintCollisionError(RuntimeError):
    pass


class FingerprintFailureLedger:
    """Append-only JSONL failure ledger for pre-runner collision checks."""

    def __init__(self, path: Path) -> None:
        self.path = path

    def record_failure(
        self,
        *,
        fingerprint_id: str,
        hypothesis_id: str,
        cycle_id: str,
        reject_reason: str,
    ) -> None:
        self._append(
            {
                "fingerprint_id": fingerprint_id,
                "hypothesis_id": hypothesis_id,
                "cycle_id": cycle_id,
                "outcome": "DISCARDED",
                "reject_reason": reject_reason,
            }
        )

    def record_success(self, *, fingerprint_id: str, hypothesis_id: str, cycle_id: str) -> None:
        self._append(
            {
                "fingerprint_id": fingerprint_id,
                "hypothesis_id": hypothesis_id,
                "cycle_id": cycle_id,
                "outcome": "PROMOTED",
            }
        )

    def has_failed(self, fingerprint_id: str) -> bool:
        return any(
            row.get("fingerprint_id") == fingerprint_id and row.get("outcome") in FAILURE_OUTCOMES
            for row in self.iter_records()
        )

    def ensure_not_failed(self, *, fingerprint_id: str, hypothesis_id: str) -> None:
        if self.has_failed(fingerprint_id):
            raise FingerprintCollisionError(
                f"fingerprint collision for hypothesis {hypothesis_id}: {fingerprint_id}"
            )

    def iter_records(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        rows: list[dict[str, Any]] = []
        for line in self.path.read_text().splitlines():
            if not line.strip():
                continue
            try:
                value = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(value, dict):
                rows.append(value)
        return rows

    def _append(self, row: dict[str, Any]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n")
            handle.flush()
