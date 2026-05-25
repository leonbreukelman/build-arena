from __future__ import annotations

from validatorlib.errors import ErrorAccumulator, ValidationProblem, format_chain


def test_validation_problem_string_contains_key_and_message() -> None:
    assert str(ValidationProblem("name", "missing")) == "name: missing"


def test_format_chain_handles_empty_errors() -> None:
    assert format_chain([]) == "no errors"


def test_format_chain_joins_problem_messages() -> None:
    result = format_chain([ValidationProblem("name", "missing"), ValidationProblem("age", "invalid")])
    assert result == "name: missing\nage: invalid"


def test_error_accumulator_formats_and_counts_problems() -> None:
    accumulator = ErrorAccumulator()
    accumulator.add(ValidationProblem("name", "missing"))
    assert accumulator.count() == 1
    assert accumulator.formatted() == "name: missing"
