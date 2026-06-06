from __future__ import annotations

import hashlib
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from arena.project_graph import GraphNode, ProjectGraph

_SECRET_PATTERNS = [
    re.compile(r"(?i)(api[_-]?key|token|secret|password)\s*[:=]\s*['\"]?[^'\"\s]+"),
    re.compile(r"sk-[A-Za-z0-9._-]{6,}"),
]


@dataclass(slots=True)
class EncyclopediaPage:
    id: str
    title: str
    path: str
    source_node_ids: list[str]
    output_hash: str


@dataclass(slots=True)
class EncyclopediaManifest:
    schema_version: str
    pages: list[EncyclopediaPage]
    graph_schema_version: str
    graph_project_root: str


def _redact(text: str) -> str:
    redacted = text
    for pattern in _SECRET_PATTERNS:
        redacted = pattern.sub("[REDACTED]", redacted)
    return redacted


def _source_link(node: GraphNode) -> str:
    if not node.path:
        return "source://project"
    if node.provenance_refs:
        ref = node.provenance_refs[0]
        if ref.line_start:
            return f"source://{node.path}#L{ref.line_start}"
    return f"source://{node.path}"


def _node_summary(node: GraphNode) -> str:
    parts = [f"- `{node.kind}` `{node.label}`"]
    if node.symbol:
        parts.append(f"symbol `{node.symbol}`")
    if node.tags:
        parts.append(f"tags `{', '.join(node.tags)}`")
    parts.append(f"[{_source_link(node)}]")
    if node.provenance_refs:
        ref = node.provenance_refs[0]
        parts.append(
            f"Provenance `{ref.id}` via `{ref.derived_by}` confidence `{ref.confidence}` hash `{ref.content_hash[:12]}`"
        )
    return " — ".join(parts)


def _interesting_snippet(project_root: Path, node: GraphNode) -> str | None:
    if not node.path:
        return None
    path = project_root / node.path
    if not path.is_file() or path.stat().st_size > 32_000:
        return None
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return None
    redacted = _redact(text)
    if "[REDACTED]" not in redacted:
        return None
    return redacted[:300]


def _write_page(path: Path, content: str) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return hashlib.sha256(content.encode()).hexdigest()


def write_encyclopedia(graph: ProjectGraph, output_dir: str | Path) -> EncyclopediaManifest:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    project_root = Path(graph.project_root)

    grouped: dict[str, list[GraphNode]] = {}
    for node in graph.nodes:
        grouped.setdefault(node.kind, []).append(node)

    overview_lines = [
        "# Project Encyclopedia",
        "",
        "This generated encyclopedia is a provenance-backed navigation cache, not authoritative truth.",
        "Accepted claims must trace through the ProjectGraph back to disk/git provenance.",
        "",
        "## Source inventory",
        "",
    ]
    source_nodes: list[str] = []
    for kind in sorted(grouped):
        overview_lines.append(f"### {kind}")
        overview_lines.append("")
        for node in sorted(grouped[kind], key=lambda item: (item.path or "", item.label))[:80]:
            overview_lines.append(_node_summary(node))
            snippet = _interesting_snippet(project_root, node)
            if snippet:
                overview_lines.append("")
                overview_lines.append("Redacted source signal:")
                overview_lines.append("")
                overview_lines.append("```text")
                overview_lines.append(snippet.strip())
                overview_lines.append("```")
            source_nodes.append(node.id)
        overview_lines.append("")
    overview_content = "\n".join(overview_lines).rstrip() + "\n"
    overview_hash = _write_page(output / "overview.md", overview_content)

    manifest = EncyclopediaManifest(
        schema_version="project-encyclopedia/v0.1",
        graph_schema_version=graph.schema_version,
        graph_project_root=graph.project_root,
        pages=[
            EncyclopediaPage(
                id="page:overview",
                title="Project Encyclopedia",
                path="overview.md",
                source_node_ids=sorted(set(source_nodes)),
                output_hash=overview_hash,
            )
        ],
    )
    manifest_data = _to_plain(manifest)
    (output / "manifest.json").write_text(json.dumps(manifest_data, sort_keys=True, indent=2), encoding="utf-8")
    return manifest


def _to_plain(value: Any) -> Any:
    if hasattr(value, "__dataclass_fields__"):
        return asdict(value)
    if isinstance(value, list):
        return [_to_plain(item) for item in value]
    if isinstance(value, dict):
        return {key: _to_plain(value[key]) for key in sorted(value)}
    return value
