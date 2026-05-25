from __future__ import annotations

import pytest

from validatorlib.validate import assert_valid_key, build_rules, validate_lines


def test_assert_valid_key_rejects_empty_and_padded_keys() -> None:
    with pytest.raises(AssertionError):
        assert_valid_key("")
    with pytest.raises(AssertionError):
        assert_valid_key(" padded")


def test_build_rules_preserves_allowed_keys() -> None:
    rules = build_rules(["name", "age"])
    assert [rule.key for rule in rules] == ["name", "age"]


def test_validate_lines_uses_parsed_records_and_rules() -> None:
    results = validate_lines(["Name: Ada", "Age:"], ["name", "age"])
    assert [result.ok for result in results] == [True, False]
