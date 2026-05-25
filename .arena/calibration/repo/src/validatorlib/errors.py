from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field


@dataclass
class ValidationProblem(Exception):
    key: str
    message: str
    cause: Exception | None = None

    def __str__(self) -> str:
        return _format_message(self)


def _format_message(problem: ValidationProblem) -> str:
    return f"{problem.key}: {problem.message}"


@dataclass
class ErrorAccumulator:
    problems: list[ValidationProblem] = field(default_factory=list)

    def add(self, problem: ValidationProblem) -> None:
        self.problems.append(problem)

    def formatted(self) -> str:
        return format_chain(self.problems)

    def count(self) -> int:
        return len(self.problems)


def format_chain(errors: Iterable[ValidationProblem], *, include_causes: bool = False) -> str:
    problems = list(errors)
    if not problems:
        return "no errors"
    lines: list[str] = []
    for problem in problems:
        lines.append(_format_message(problem))
        if include_causes and problem.cause is not None:
            lines.append(f"caused by: {problem.cause}")
    return "\n".join(lines)
