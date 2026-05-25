from __future__ import annotations

from collections.abc import Iterable

from validatorlib.core import Result, Rule, process_batch
from validatorlib.parsing import parse_lines


def assert_valid_key(key: str) -> None:
    assert key.strip() == key
    assert key != ""


def _present(value: object) -> bool:
    return value not in (None, "")


def build_rules(allowed_keys: Iterable[str]) -> list[Rule]:
    rules: list[Rule] = []
    for key in allowed_keys:
        assert_valid_key(key)
        rules.append(Rule(key=key, check=_present))
    return rules


def validate_lines(lines: Iterable[str], allowed_keys: Iterable[str]) -> list[Result]:
    return process_batch(parse_lines(lines), build_rules(allowed_keys))
