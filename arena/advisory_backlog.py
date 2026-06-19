from __future__ import annotations

import hashlib
import json
from typing import Any

EXPECTED_SCHEMA_VERSION = "advisory-backlog-expected/v0"
EXPECTED_DIR = "docs"
BACKLOG_TARGET = "docs/agent-backlog.md"


def advisory_expected_target(digest: str) -> str:
    return f"{EXPECTED_DIR}/advisory-backlog-expected-{digest}.json"


def build_advisory_expected(finding_id: str, items: tuple[dict[str, str], ...]) -> dict[str, Any]:
    normalized_items = tuple(_normalized_item(item) for item in items if _normalized_item(item))
    base: dict[str, Any] = {
        "schemaVersion": EXPECTED_SCHEMA_VERSION,
        "id": "",
        "findingId": finding_id,
        "items": list(normalized_items),
    }
    digest = expected_digest(base)
    base["id"] = f"advisory-backlog-{digest}"
    return _canonical_expected(base)


def canonical_expected_text(expected: dict[str, Any]) -> str:
    return json.dumps(_canonical_expected(expected), indent=2, sort_keys=True) + "\n"


def expected_digest(expected: dict[str, Any]) -> str:
    payload = {
        "findingId": str(expected.get("findingId", "")),
        "items": _items(expected),
        "schemaVersion": str(expected.get("schemaVersion", "")),
    }
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()[:12]


def backlog_markdown_entry(finding_id: str, items: tuple[dict[str, str], ...]) -> str:
    normalized = [_normalized_item(item) for item in items if _normalized_item(item)]
    lines = [
        "# Agent backlog",
        "",
        f"## Advisory finding: {finding_id}",
        "",
        "The following advisory item is backlogged because no mechanical graph signal exists yet for a binding fitness function.",
        "",
    ]
    for item in normalized:
        lines.extend([
            f"- `{item['id']}` ({item['kind']}): {item['text']}",
        ])
    return "\n".join(lines)


def _canonical_expected(expected: dict[str, Any]) -> dict[str, Any]:
    return {
        "findingId": str(expected.get("findingId", "")),
        "id": str(expected.get("id", "")),
        "items": _items(expected),
        "schemaVersion": str(expected.get("schemaVersion", "")),
    }


def _items(expected: dict[str, Any]) -> list[dict[str, str]]:
    raw_items = expected.get("items")
    if not isinstance(raw_items, list):
        return []
    items = [_normalized_item(item) for item in raw_items if isinstance(item, dict)]
    return sorted((item for item in items if item), key=lambda item: (item["kind"], item["id"], item["text"]))


def _normalized_item(item: dict[str, Any]) -> dict[str, str]:
    kind = str(item.get("kind", "")).strip()
    item_id = str(item.get("id", "")).strip()
    text = str(item.get("text", "") or item.get("question", "") or item.get("description", "")).strip()
    if not kind or not item_id or not text:
        return {}
    return {"kind": kind, "id": item_id, "text": text}
