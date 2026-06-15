from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

_SECRET_PATTERNS = (
    re.compile(r"\bsk-[A-Za-z0-9_.-]{6,}"),
    re.compile(r"(?i)api[_-]?key[\"']?\s*[:=]"),
    re.compile(r"(?i)secret[\"']?\s*[:=]"),
    re.compile(r"(?i)token[\"']?\s*[:=]\s*[\"']?[A-Za-z0-9_.-]{8,}"),
)


@dataclass(frozen=True)
class WikiRecord:
    id: str
    record_type: str
    created_run_id: str
    payload: dict[str, Any]
    content_hash: str

    def to_jsonable(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "recordType": self.record_type,
            "createdRunId": self.created_run_id,
            "payload": self.payload,
            "contentHash": self.content_hash,
        }

    @classmethod
    def from_jsonable(cls, raw: dict[str, Any]) -> WikiRecord:
        payload = raw.get("payload", {})
        return cls(
            id=str(raw.get("id", "")),
            record_type=str(raw.get("recordType", "")),
            created_run_id=str(raw.get("createdRunId", "")),
            payload=payload if isinstance(payload, dict) else {},
            content_hash=str(raw.get("contentHash", "")),
        )


def append_record(
    store_path: str | Path,
    *,
    record_type: str,
    created_run_id: str,
    payload: dict[str, Any],
) -> WikiRecord:
    store = Path(store_path)
    if not record_type.strip():
        raise ValueError("record_type must be non-empty")
    if not created_run_id.strip():
        raise ValueError("created_run_id must be non-empty")
    _reject_secret_like_payload(payload)
    canonical_payload = _canonical_json(payload)
    content_hash = hashlib.sha256(
        _canonical_json(
            {
                "recordType": record_type,
                "createdRunId": created_run_id,
                "payload": payload,
            }
        ).encode()
    ).hexdigest()
    record = WikiRecord(
        id=content_hash[:16],
        record_type=record_type,
        created_run_id=created_run_id,
        payload=json.loads(canonical_payload),
        content_hash=content_hash,
    )
    store.parent.mkdir(parents=True, exist_ok=True)
    with store.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record.to_jsonable(), sort_keys=True, separators=(",", ":")) + "\n")
    return record


def read_records(store_path: str | Path, *, record_type: str | None = None) -> list[WikiRecord]:
    store = Path(store_path)
    if not store.exists():
        return []
    records: list[WikiRecord] = []
    for line in store.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        raw = json.loads(line)
        if not isinstance(raw, dict):
            continue
        record = WikiRecord.from_jsonable(raw)
        if record_type is None or record.record_type == record_type:
            records.append(record)
    return sorted(records, key=lambda item: (item.record_type, item.id, item.created_run_id))


def _reject_secret_like_payload(payload: dict[str, Any]) -> None:
    rendered = _canonical_json(payload)
    for pattern in _SECRET_PATTERNS:
        if pattern.search(rendered):
            raise ValueError("wiki record payload appears to contain a secret-like value")


def _canonical_json(payload: Any) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
