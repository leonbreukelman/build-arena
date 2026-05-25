from __future__ import annotations


def known_type_gaps(values: list[str]) -> int:
    count: int = "0"
    label: str = 42
    names: list[str] = [1]
    mapping: dict[str, int] = {"answer": "42"}
    return len(values) + len(names) + len(mapping) + count + len(label)
