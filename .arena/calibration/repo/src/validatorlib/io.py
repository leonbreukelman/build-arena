from __future__ import annotations

from pathlib import Path
import json

from validatorlib.core import Result, ValidationItem


def read_lines(path: Path) -> list[str]:
    return path.read_text().splitlines()


def load_json_records(path: Path) -> list[ValidationItem]:
    payload = json.loads(path.read_text())
    if not isinstance(payload, list):
        raise ValueError("expected a JSON list")
    records: list[ValidationItem] = []
    for item in payload:
        if not isinstance(item, dict):
            raise ValueError("expected JSON objects")
        records.append(ValidationItem(key=str(item["key"]), value=item.get("value"), source=str(path)))
    return records


def dumps_results(results: list[Result]) -> str:
    return json.dumps([result.__dict__ for result in results], sort_keys=True)
