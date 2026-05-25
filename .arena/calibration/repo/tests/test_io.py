from __future__ import annotations

from pathlib import Path
import json

import pytest

from validatorlib.core import Result
from validatorlib.io import dumps_results, load_json_records, read_lines


def test_read_lines_returns_file_lines(tmp_path: Path) -> None:
    path = tmp_path / "records.txt"
    path.write_text("a\nb\n")
    assert read_lines(path) == ["a", "b"]


def test_load_json_records_accepts_list_of_objects(tmp_path: Path) -> None:
    path = tmp_path / "records.json"
    path.write_text(json.dumps([{"key": "name", "value": "Ada"}]))
    records = load_json_records(path)
    assert records[0].key == "name"
    assert records[0].value == "Ada"


def test_load_json_records_rejects_non_list(tmp_path: Path) -> None:
    path = tmp_path / "records.json"
    path.write_text(json.dumps({"key": "name"}))
    with pytest.raises(ValueError):
        load_json_records(path)


def test_dumps_results_sorts_output_keys() -> None:
    payload = dumps_results([Result("name", True, "ok")])
    assert payload == '[{"key": "name", "message": "ok", "ok": true}]'
