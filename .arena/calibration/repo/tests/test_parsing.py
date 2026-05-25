from __future__ import annotations

import pytest

from validatorlib.parsing import normalize_key, parse_lines, parse_record


def test_normalize_key_trims_and_replaces_spaces() -> None:
    assert normalize_key(" Company Name ") == "company_name"


def test_parse_record_splits_key_and_value() -> None:
    record = parse_record("Name: Ada")
    assert record.key == "name"
    assert record.value == "Ada"


def test_parse_record_rejects_missing_separator() -> None:
    with pytest.raises(ValueError):
        parse_record("not-a-record")


def test_parse_lines_skips_comments_and_blanks() -> None:
    records = parse_lines(["", "# comment", "Name: Ada"])
    assert len(records) == 1
    assert records[0].source == "line:3"
