from __future__ import annotations

from collections.abc import Iterable

from validatorlib.core import ValidationItem


def normalize_key(raw: str) -> str:
    return raw.strip().lower().replace(" ", "_")


def parse_record(line: str) -> ValidationItem:
    key, separator, value = line.partition(":")
    if separator == "":
        raise ValueError(f"record missing ':' separator: {line!r}")
    return ValidationItem(key=normalize_key(key), value=value.strip())


def parse_lines(lines: Iterable[str]) -> list[ValidationItem]:
    records: list[ValidationItem] = []
    for line_number, line in enumerate(lines, start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        record = parse_record(stripped)
        records.append(ValidationItem(record.key, record.value, source=f"line:{line_number}"))
    return records
