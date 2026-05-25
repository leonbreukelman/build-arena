from __future__ import annotations

from pathlib import Path

GENERATED_TEXT_PATHS = (
    Path("arena/generated/ddl.sql"),
    Path("arena/generated/schema.json"),
    Path("dashboard/src/lib/generated/arena.d.ts"),
)


def _canonicalize_create_index_groups(text: str) -> str:
    lines = text.splitlines(keepends=True)
    output: list[str] = []
    index_group: list[str] = []

    def flush_indexes() -> None:
        if index_group:
            output.extend(sorted(index_group))
            index_group.clear()

    for line in lines:
        if line.startswith("CREATE INDEX "):
            index_group.append(line)
        else:
            flush_indexes()
            output.append(line)
    flush_indexes()
    return "".join(output)


def _normalize_text(text: str) -> str:
    lines = [line.rstrip() for line in text.splitlines()]
    while lines and lines[-1] == "":
        lines.pop()
    return "\n".join(lines) + "\n"


def main() -> None:
    for path in GENERATED_TEXT_PATHS:
        text = path.read_text()
        if path.name == "ddl.sql":
            text = _canonicalize_create_index_groups(text)
        path.write_text(_normalize_text(text))


if __name__ == "__main__":
    main()
