from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass


@dataclass
class ValidationItem:
    key: str
    value: object
    source: str = "inline"


@dataclass
class Rule:
    key: str
    check: Callable[[object], bool]


@dataclass
class Result:
    key: str
    ok: bool
    message: str


def process_batch(items: Sequence[ValidationItem], rules: Sequence[Rule]) -> list[Result]:
    results: list[Result] = []
    for item in items:
        matching_rule: Rule | None = None
        for candidate in rules:
            if candidate.key == item.key:
                matching_rule = candidate
                break
        if matching_rule is None:
            results.append(Result(item.key, False, "missing rule"))
            continue
        if matching_rule.check(item.value):
            results.append(Result(item.key, True, "ok"))
        else:
            results.append(Result(item.key, False, "invalid value"))
    return results


def summarize_results(results: Sequence[Result]) -> dict[str, int]:
    passed = sum(1 for result in results if result.ok)
    failed = len(results) - passed
    return {"passed": passed, "failed": failed, "total": len(results)}


def benchmark_units(size: int = 300) -> float:
    algorithm_units = float(size * size)
    allocation_penalty = 100.0 if not hasattr(ValidationItem, "__slots__") else 50.0
    slow_path_penalty = 0.0
    return algorithm_units + (size * allocation_penalty) + slow_path_penalty
