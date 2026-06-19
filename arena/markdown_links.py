from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path, PurePosixPath
from typing import Any
from urllib.parse import unquote

_SCHEME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")
_INLINE_LINK_RE = re.compile(r"!?\[[^\]]*\]\(\s*(<[^>]*>|[^)\s]+)(?:\s+\"[^\"]*\")?\s*\)")
_REFERENCE_USE_RE = re.compile(r"!?\[([^\]]+)\]\[([^\]]*)\]")
_REFERENCE_DEF_RE = re.compile(r"^\s{0,3}\[([^\]]+)\]:\s*(<[^>]*>|\S+)")
_PLAIN_FILE_MENTION_RE = re.compile(r"(?<![\]/(])\b(?:[A-Za-z0-9_.-]+/)*[A-Za-z0-9_.-]+\.(?:md|toml|yaml|yml|json|py|ts|tsx|js|jsx|txt|lock)\b")


@dataclass(frozen=True)
class MarkdownLink:
    target: str
    line: int


@dataclass(frozen=True)
class MarkdownLinkResult:
    link: str
    source_path: str
    resolved_path: str
    line: int

    def to_jsonable(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class MarkdownLinkReport:
    path: str
    ok: bool
    checked: tuple[MarkdownLinkResult, ...]
    missing: tuple[MarkdownLinkResult, ...]
    escaped: tuple[MarkdownLinkResult, ...]

    def to_jsonable(self) -> dict[str, Any]:
        return {
            "path": self.path,
            "ok": self.ok,
            "checked": [item.to_jsonable() for item in self.checked],
            "missing": [item.to_jsonable() for item in self.missing],
            "escaped": [item.to_jsonable() for item in self.escaped],
        }


def extract_markdown_links(text: str) -> tuple[MarkdownLink, ...]:
    reference_defs = _reference_definitions(text)
    links: list[MarkdownLink] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        occupied_spans: list[tuple[int, int]] = []
        for match in _INLINE_LINK_RE.finditer(line):
            occupied_spans.append(match.span())
            target = _clean_target(match.group(1))
            if _is_ignored_target(target):
                continue
            stripped = target.split("#", 1)[0]
            if not stripped:
                continue
            links.append(MarkdownLink(target=stripped, line=line_number))
        for match in _REFERENCE_USE_RE.finditer(line):
            occupied_spans.append(match.span())
            label = match.group(2).strip() or match.group(1).strip()
            target = reference_defs.get(_normalize_reference_label(label))
            if target is None or _is_ignored_target(target):
                continue
            stripped = target.split("#", 1)[0]
            if not stripped:
                continue
            links.append(MarkdownLink(target=stripped, line=line_number))
        if _REFERENCE_DEF_RE.match(line):
            occupied_spans.append((0, len(line)))
        for match in _PLAIN_FILE_MENTION_RE.finditer(line):
            if _overlaps(match.span(), occupied_spans):
                continue
            target = match.group(0).strip().rstrip(".,;:")
            if _is_ignored_target(target):
                continue
            links.append(MarkdownLink(target=target, line=line_number))
    return tuple(links)


def check_markdown_links(repo: Path, markdown_path: Path) -> MarkdownLinkReport:
    root = repo.resolve()
    path = markdown_path if markdown_path.is_absolute() else root / markdown_path
    path = path.resolve()
    text = path.read_text(encoding="utf-8")
    checked: list[MarkdownLinkResult] = []
    missing: list[MarkdownLinkResult] = []
    escaped: list[MarkdownLinkResult] = []
    for link in extract_markdown_links(text):
        resolved = _resolve_target(root, path, link.target)
        rel = _display_path(root, resolved)
        result = MarkdownLinkResult(
            link=link.target,
            source_path=_display_path(root, path),
            resolved_path=rel,
            line=link.line,
        )
        if not _is_inside(root, resolved):
            escaped.append(result)
        elif not resolved.exists():
            missing.append(result)
        else:
            checked.append(result)
    return MarkdownLinkReport(
        path=_display_path(root, path),
        ok=not missing and not escaped,
        checked=tuple(checked),
        missing=tuple(missing),
        escaped=tuple(escaped),
    )


def has_source_references(repo: Path, markdown_path: Path) -> bool:
    root = repo.resolve()
    path = markdown_path if markdown_path.is_absolute() else root / markdown_path
    path = path.resolve()
    text = path.read_text(encoding="utf-8")
    section = _source_references_section(text)
    if not section.strip():
        return False
    for link in extract_markdown_links(section):
        resolved = _resolve_target(root, path, link.target)
        if _is_inside(root, resolved) and resolved.exists():
            return True
    return False


def _source_references_section(text: str) -> str:
    lines = text.splitlines()
    start: int | None = None
    for index, line in enumerate(lines):
        if re.match(r"^#{1,6}\s+source references\s*$", line.strip(), flags=re.IGNORECASE):
            start = index + 1
            break
    if start is None:
        return ""
    collected: list[str] = []
    for line in lines[start:]:
        if re.match(r"^#{1,6}\s+", line.strip()):
            break
        collected.append(line)
    return "\n".join(collected)


def _is_ignored_target(target: str) -> bool:
    return target.startswith("#") or _SCHEME_RE.match(target) is not None


def _reference_definitions(text: str) -> dict[str, str]:
    definitions: dict[str, str] = {}
    for line in text.splitlines():
        match = _REFERENCE_DEF_RE.match(line)
        if match is None:
            continue
        target = _clean_target(match.group(2))
        if _is_ignored_target(target):
            continue
        definitions[_normalize_reference_label(match.group(1))] = target
    return definitions


def _normalize_reference_label(label: str) -> str:
    return " ".join(label.casefold().split())


def _clean_target(target: str) -> str:
    value = target.strip()
    if value.startswith("<") and value.endswith(">"):
        value = value[1:-1].strip()
    return value


def _overlaps(span: tuple[int, int], occupied_spans: list[tuple[int, int]]) -> bool:
    start, end = span
    return any(start < occupied_end and end > occupied_start for occupied_start, occupied_end in occupied_spans)


def _resolve_target(root: Path, markdown_path: Path, target: str) -> Path:
    cleaned = unquote(target.split("#", 1)[0])
    if cleaned.startswith("/"):
        return (root / cleaned.lstrip("/")).resolve()
    relative = (markdown_path.parent / cleaned).resolve()
    if relative.exists() or not _should_try_repo_root_fallback(root, cleaned):
        return relative
    return (root / cleaned).resolve()


def _should_try_repo_root_fallback(root: Path, cleaned_target: str) -> bool:
    """Return true for repo-root-looking links from nested generated docs.

    Markdown relative semantics stay primary. The fallback is intentionally narrow:
    only targets without ``..`` and whose first component already exists at repo
    root can fall back to repo-root resolution. This fixes generated nested docs
    that cite ``README.md`` or ``docs/index.md`` without turning arbitrary dead
    links into silently accepted root-relative paths or weakening escape checks.
    """
    if not cleaned_target or cleaned_target.startswith("/"):
        return False
    posix = PurePosixPath(cleaned_target)
    if posix.is_absolute() or ".." in posix.parts:
        return False
    first_part = posix.parts[0] if posix.parts else ""
    return bool(first_part) and (root / first_part).exists()


def _is_inside(root: Path, path: Path) -> bool:
    return path == root or root in path.parents


def _display_path(root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m arena.markdown_links")
    parser.add_argument("--repo", default=".")
    parser.add_argument("--path", required=True)
    parser.add_argument("--require-source-references", action="store_true")
    args = parser.parse_args(argv)
    report = check_markdown_links(Path(args.repo), Path(args.path))
    payload = report.to_jsonable()
    if args.require_source_references:
        payload["sourceReferencesOk"] = has_source_references(Path(args.repo), Path(args.path))
    print(json.dumps(payload, indent=2, sort_keys=True))
    if not report.ok:
        return 1
    if args.require_source_references and not payload["sourceReferencesOk"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
