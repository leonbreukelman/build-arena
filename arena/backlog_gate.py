from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from arena.advisory_backlog import EXPECTED_SCHEMA_VERSION, _items, expected_digest
from arena.markdown_links import check_markdown_links

_BOILERPLATE_MARKERS = (
    "todo",
    "tbd",
    "placeholder",
    "fill this in",
    "boilerplate",
    "lorem ipsum",
    "no-op",
)


@dataclass(frozen=True)
class BacklogGateResult:
    accepted: bool
    reason: str
    path: str
    expected_ids: tuple[str, ...] = ()

    def to_jsonable(self) -> dict[str, Any]:
        return {
            "accepted": self.accepted,
            "reason": self.reason,
            "path": self.path,
            "expectedIds": list(self.expected_ids),
        }


def validate_backlog_entry(repo: str | Path, path: str | Path, expected: str | Path) -> BacklogGateResult:
    repo_path = Path(repo).resolve()
    backlog_path = (repo_path / path).resolve() if not Path(path).is_absolute() else Path(path).resolve()
    expected_path = (repo_path / expected).resolve() if not Path(expected).is_absolute() else Path(expected).resolve()
    rel_path = _relative_or_str(repo_path, backlog_path)
    try:
        expected_payload = json.loads(expected_path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return _reject("missing_expected", rel_path)
    except json.JSONDecodeError:
        return _reject("invalid_expected_json", rel_path)
    if not isinstance(expected_payload, dict) or expected_payload.get("schemaVersion") != EXPECTED_SCHEMA_VERSION:
        return _reject("invalid_expected", rel_path)
    digest = expected_digest(expected_payload)
    if expected_payload.get("id") != f"advisory-backlog-{digest}" or expected_path.name != f"advisory-backlog-expected-{digest}.json":
        return _reject("expected_digest_mismatch", rel_path)
    items = _items(expected_payload)
    if not items:
        return _reject("missing_expected_items", rel_path)
    expected_ids = tuple(item["id"] for item in items)

    try:
        text = backlog_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return _reject("missing_backlog", rel_path, expected_ids=expected_ids)
    stripped = text.strip()
    if len(stripped) < 80 or any(marker in stripped.lower() for marker in _BOILERPLATE_MARKERS):
        return _reject("boilerplate_entry", rel_path, expected_ids=expected_ids)
    for item in items:
        if item["id"] not in text or item["text"] not in text:
            return _reject("missing_expected_item", rel_path, expected_ids=expected_ids)
    link_report = check_markdown_links(repo_path, backlog_path)
    if not link_report.ok:
        return _reject("dead_local_link", rel_path, expected_ids=expected_ids)
    return BacklogGateResult(True, "accepted", rel_path, expected_ids)


def _reject(reason: str, path: str, *, expected_ids: tuple[str, ...] = ()) -> BacklogGateResult:
    return BacklogGateResult(False, reason, path, expected_ids)


def _relative_or_str(root: Path, path: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return str(path)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m arena.backlog_gate")
    parser.add_argument("--repo", required=True)
    parser.add_argument("--path", required=True)
    parser.add_argument("--expected", required=True)
    args = parser.parse_args(argv)
    result = validate_backlog_entry(args.repo, args.path, args.expected)
    print(json.dumps(result.to_jsonable(), sort_keys=True))
    return 0 if result.accepted else 1


if __name__ == "__main__":
    raise SystemExit(main())
