from __future__ import annotations

import ast
import hashlib
import json
import re
import subprocess
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

PRIMARY_CONTEXT_EXCLUDED_PREFIXES = (
    "docs/verification/",
    ".arena/calibration/repo/",
    ".arena/project-model/",
    ".arena/project-model-snapshots/",
    ".arena/worktrees/",
)

PROTECTED_PREFIXES = ("scorer/", "verifier/", "schema/")
GENERATED_PREFIXES = ("arena/generated/", "dist/", "build/", "coverage/", "node_modules/")
GENERATED_DIRECTORY_SENTINELS = ("arena/generated/", "dist/", "build/", "coverage/")
CONFIG_NAMES = {
    "pyproject.toml",
    "uv.lock",
    "package.json",
    "package-lock.json",
    "pnpm-lock.yaml",
    "yarn.lock",
    "Cargo.toml",
    "Cargo.lock",
    "Makefile",
    "Dockerfile",
}
CONFIG_SUFFIXES = (".toml", ".yaml", ".yml", ".json", ".ini", ".cfg")


@dataclass(slots=True)
class ProvenanceRef:
    id: str
    source_type: str
    derived_by: str
    confidence: str
    content_hash: str
    path: str | None = None
    line_start: int | None = None
    line_end: int | None = None
    git_oid: str | None = None
    dirty: bool = False


@dataclass(slots=True)
class GraphNode:
    id: str
    kind: str
    label: str
    path: str | None = None
    symbol: str | None = None
    tags: list[str] = field(default_factory=list)
    provenance_refs: list[ProvenanceRef] = field(default_factory=list)


@dataclass(slots=True)
class GraphEdge:
    id: str
    kind: str
    from_node_id: str
    to_node_id: str
    label: str
    provenance_refs: list[ProvenanceRef] = field(default_factory=list)
    confidence: str = "deterministic"
    derived_by: str = "project_graph"


@dataclass(slots=True)
class GitState:
    available: bool
    root: str | None
    head_oid: str | None
    dirty: bool
    dirty_paths: list[str]


@dataclass(slots=True)
class ProjectGraph:
    schema_version: str
    project_root: str
    git: GitState
    nodes: list[GraphNode]
    edges: list[GraphEdge]


def _run_git(args: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], cwd=cwd, text=True, capture_output=True, check=False)


def _resolve_project_root(path: Path) -> tuple[Path, GitState]:
    path = path.resolve()
    probe = path if path.is_dir() else path.parent
    top = _run_git(["rev-parse", "--show-toplevel"], probe)
    if top.returncode != 0:
        return path, GitState(False, None, None, False, [])
    root = Path(top.stdout.strip()).resolve()
    head = _run_git(["rev-parse", "HEAD"], root)
    status = _run_git(["status", "--porcelain=v1"], root)
    dirty_paths: list[str] = []
    if status.returncode == 0:
        for line in status.stdout.splitlines():
            if not line:
                continue
            candidate = line[3:] if len(line) > 3 else line
            if " -> " in candidate:
                candidate = candidate.split(" -> ", 1)[1]
            dirty_paths.append(candidate)
    return root, GitState(
        available=True,
        root=str(root),
        head_oid=head.stdout.strip() if head.returncode == 0 else None,
        dirty=bool(dirty_paths),
        dirty_paths=sorted(set(dirty_paths)),
    )


def _tracked_and_untracked_files(root: Path, git_available: bool) -> list[str]:
    if git_available:
        listed: list[str] = []
        tracked = _run_git(["ls-files", "-z"], root)
        if tracked.returncode == 0:
            listed.extend(part for part in tracked.stdout.split("\0") if part)
        untracked = _run_git(["ls-files", "--others", "--exclude-standard", "-z"], root)
        if untracked.returncode == 0:
            listed.extend(part for part in untracked.stdout.split("\0") if part)
        return sorted({rel for rel in listed if rel})
    return sorted(p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file() and ".git" not in p.parts)


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _safe_read_bytes(path: Path) -> bytes:
    try:
        return path.read_bytes()
    except OSError:
        return b""


def _file_identity_bytes(path: Path) -> bytes:
    if path.is_symlink():
        try:
            return ("symlink->" + str(path.readlink())).encode()
        except OSError:
            return b"symlink-><unreadable>"
    return _safe_read_bytes(path)


def _is_parseable_regular_file(path: Path) -> bool:
    return path.exists() and path.is_file() and not path.is_symlink()


def _line_count(data: bytes) -> int:
    if not data:
        return 1
    return max(1, data.count(b"\n") + (0 if data.endswith(b"\n") else 1))


def _rel(root: Path, path: Path) -> str:
    return path.resolve().relative_to(root).as_posix()


def _is_dirty(rel_path: str, git: GitState) -> bool:
    return rel_path in git.dirty_paths


def _prov(
    *,
    rel_path: str,
    data_hash: str,
    git: GitState,
    derived_by: str,
    source_type: str = "file",
    line_start: int | None = None,
    line_end: int | None = None,
    confidence: str = "deterministic",
) -> ProvenanceRef:
    bits = [rel_path, derived_by, str(line_start), str(line_end), data_hash]
    return ProvenanceRef(
        id="prov:" + _sha256_bytes("|".join(bits).encode())[:16],
        source_type=source_type,
        derived_by=derived_by,
        confidence=confidence,
        content_hash=data_hash,
        path=rel_path,
        line_start=line_start,
        line_end=line_end,
        git_oid=git.head_oid,
        dirty=_is_dirty(rel_path, git),
    )


def _node(
    *,
    kind: str,
    label: str,
    rel_path: str | None = None,
    symbol: str | None = None,
    tags: list[str] | None = None,
    provenance_refs: list[ProvenanceRef] | None = None,
) -> GraphNode:
    raw = f"{kind}|{rel_path or ''}|{symbol or label}"
    if kind.endswith("_import") and symbol:
        node_id = f"node:{kind}:" + symbol.replace("/", ".")
    else:
        node_id = "node:" + _sha256_bytes(raw.encode())[:20]
    return GraphNode(
        id=node_id,
        kind=kind,
        label=label,
        path=rel_path,
        symbol=symbol,
        tags=sorted(set(tags or [])),
        provenance_refs=provenance_refs or [],
    )


def _edge(kind: str, from_node_id: str, to_node_id: str, provs: list[ProvenanceRef], label: str = "") -> GraphEdge:
    raw = f"{kind}|{from_node_id}|{to_node_id}|{label}"
    return GraphEdge(
        id="edge:" + _sha256_bytes(raw.encode())[:20],
        kind=kind,
        from_node_id=from_node_id,
        to_node_id=to_node_id,
        label=label or kind,
        provenance_refs=provs,
    )


def _classify_file(rel_path: str) -> tuple[str, list[str]]:
    tags: list[str] = []
    kind = "file"
    if rel_path.startswith(PRIMARY_CONTEXT_EXCLUDED_PREFIXES):
        kind = "verification_artifact"
        tags.append("excluded_from_primary_context")
    if rel_path.startswith(PROTECTED_PREFIXES):
        kind = "protected_surface"
        tags.append("protected")
    if rel_path.startswith(GENERATED_PREFIXES):
        kind = "generated_surface"
        tags.append("generated")
    name = Path(rel_path).name
    if kind == "file" and (name in CONFIG_NAMES or rel_path.endswith(CONFIG_SUFFIXES)):
        kind = "config"
    if kind == "file" and (rel_path.startswith("tests/") or name.startswith("test_")) and rel_path.endswith(".py"):
        kind = "test_file"
    return kind, tags


def _module_name(rel_path: str) -> str:
    without_suffix = rel_path[:-3] if rel_path.endswith(".py") else rel_path
    parts = without_suffix.split("/")
    if parts and parts[0] == "src":
        parts = parts[1:]
    if parts and parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join(part for part in parts if part)


def _javascript_module_name(rel_path: str) -> str:
    module_path = rel_path
    for suffix in (".js", ".mjs", ".cjs", ".ts", ".tsx"):
        if module_path.endswith(suffix):
            module_path = module_path[: -len(suffix)]
            break
    parts = module_path.split("/")
    if parts and parts[0] == "src":
        parts = parts[1:]
    if parts and parts[-1] == "index":
        parts = parts[:-1] or ["index"]
    return ".".join(part for part in parts if part)


def _resolve_python_import(current_module: str, rel_path: str, node: ast.ImportFrom) -> list[str]:
    if node.level == 0:
        if node.module:
            return [node.module]
        return [alias.name for alias in node.names if alias.name != "*"]
    if not current_module:
        return [node.module] if node.module else [alias.name for alias in node.names if alias.name != "*"]
    current_parts = current_module.split(".")
    if Path(rel_path).name != "__init__.py":
        current_parts = current_parts[:-1]
    keep = max(0, len(current_parts) - (node.level - 1))
    base = current_parts[:keep]
    if node.module:
        suffix = node.module.split(".")
        return [".".join([*base, *suffix])]
    return [".".join([*base, alias.name]) for alias in node.names if alias.name != "*"]


def _resolve_javascript_import(rel_path: str, imported: str) -> str:
    if not imported.startswith("."):
        return imported
    base = Path(rel_path).parent
    target = (base / imported).as_posix()
    for suffix in (".js", ".mjs", ".cjs", ".ts", ".tsx"):
        if target.endswith(suffix):
            target = target[: -len(suffix)]
            break
    if target.endswith("/index"):
        target = target[: -len("/index")]
    parts = [part for part in target.split("/") if part not in {"", "."}]
    normalized: list[str] = []
    for part in parts:
        if part == "..":
            if normalized:
                normalized.pop()
        else:
            normalized.append(part)
    if normalized and normalized[0] == "src":
        normalized = normalized[1:]
    return ".".join(normalized)


_JS_IMPORT_RE = re.compile(
    r"(?:import\s+(?:[^'\"]+?\s+from\s+)?|export\s+[^'\"]+?\s+from\s+|require\s*\()"
    r"['\"]([^'\"]+)['\"]"
)
_JS_FUNCTION_RE = re.compile(r"(?:export\s+)?(?:async\s+)?function\s+([A-Za-z_$][\w$]*)\s*\(")


def _add_javascript_nodes(
    *,
    rel_path: str,
    path: Path,
    data_hash: str,
    git: GitState,
    file_node: GraphNode,
    nodes: dict[str, GraphNode],
    edges: dict[str, GraphEdge],
) -> None:
    try:
        text = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return
    module = _javascript_module_name(rel_path)
    module_prov = _prov(rel_path=rel_path, data_hash=data_hash, git=git, derived_by="javascript_regex", line_start=1, line_end=_line_count(_safe_read_bytes(path)))
    module_node = _node(kind="javascript_module", label=module, rel_path=rel_path, symbol=module, tags=file_node.tags, provenance_refs=[module_prov])
    nodes[module_node.id] = module_node
    edge = _edge("defined_in", module_node.id, file_node.id, [module_prov])
    edges[edge.id] = edge
    line_starts = [0]
    for match in re.finditer(r"\n", text):
        line_starts.append(match.end())
    for match in _JS_FUNCTION_RE.finditer(text):
        line_no = 1 + sum(1 for start in line_starts if start <= match.start())
        name = match.group(1)
        prov = _prov(rel_path=rel_path, data_hash=data_hash, git=git, derived_by="javascript_regex", line_start=line_no, line_end=line_no)
        symbol = f"{module}.{name}" if module else name
        fn_node = _node(kind="javascript_function", label=name, rel_path=rel_path, symbol=symbol, tags=file_node.tags, provenance_refs=[prov])
        nodes[fn_node.id] = fn_node
        edges[_edge("defined_in", fn_node.id, file_node.id, [prov]).id] = _edge("defined_in", fn_node.id, file_node.id, [prov])
    for match in _JS_IMPORT_RE.finditer(text):
        imported = _resolve_javascript_import(rel_path, match.group(1))
        line_no = 1 + sum(1 for start in line_starts if start <= match.start())
        prov = _prov(rel_path=rel_path, data_hash=data_hash, git=git, derived_by="javascript_regex", line_start=line_no, line_end=line_no)
        import_node = _node(kind="javascript_import", label=imported, rel_path=rel_path, symbol=imported, provenance_refs=[prov])
        nodes[import_node.id] = import_node
        edges[_edge("imports", module_node.id, import_node.id, [prov], label=imported).id] = _edge("imports", module_node.id, import_node.id, [prov], label=imported)


def _add_python_nodes(
    *,
    root: Path,
    rel_path: str,
    path: Path,
    data_hash: str,
    git: GitState,
    file_node: GraphNode,
    nodes: dict[str, GraphNode],
    edges: dict[str, GraphEdge],
) -> None:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except (SyntaxError, UnicodeDecodeError, OSError):
        return
    module = _module_name(rel_path)
    module_prov = _prov(rel_path=rel_path, data_hash=data_hash, git=git, derived_by="python_ast", line_start=1, line_end=_line_count(_safe_read_bytes(path)))
    module_node = _node(kind="python_module", label=module, rel_path=rel_path, symbol=module, tags=file_node.tags, provenance_refs=[module_prov])
    nodes[module_node.id] = module_node
    edge = _edge("defined_in", module_node.id, file_node.id, [module_prov])
    edges[edge.id] = edge
    for child in ast.walk(tree):
        if isinstance(child, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            kind = "python_class" if isinstance(child, ast.ClassDef) else "python_function"
            symbol = f"{module}.{child.name}" if module else child.name
            end_lineno = getattr(child, "end_lineno", child.lineno)
            prov = _prov(rel_path=rel_path, data_hash=data_hash, git=git, derived_by="python_ast", line_start=child.lineno, line_end=end_lineno)
            sym_node = _node(kind=kind, label=child.name, rel_path=rel_path, symbol=symbol, tags=file_node.tags, provenance_refs=[prov])
            nodes[sym_node.id] = sym_node
            edges[_edge("defined_in", sym_node.id, file_node.id, [prov]).id] = _edge("defined_in", sym_node.id, file_node.id, [prov])
        elif isinstance(child, (ast.Import, ast.ImportFrom)):
            names: list[str] = []
            if isinstance(child, ast.Import):
                names = [alias.name for alias in child.names]
            elif isinstance(child, ast.ImportFrom):
                names = _resolve_python_import(module, rel_path, child)
            for imported in names:
                prov = _prov(rel_path=rel_path, data_hash=data_hash, git=git, derived_by="python_ast", line_start=child.lineno, line_end=getattr(child, "end_lineno", child.lineno))
                import_node = _node(kind="python_import", label=imported, rel_path=rel_path, symbol=imported, provenance_refs=[prov])
                nodes[import_node.id] = import_node
                edges[_edge("imports", module_node.id, import_node.id, [prov], label=imported).id] = _edge("imports", module_node.id, import_node.id, [prov], label=imported)
    if rel_path.startswith("tests/") or Path(rel_path).name.startswith("test_"):
        guessed = Path(rel_path).stem
        if guessed.startswith("test_"):
            target_name = guessed.removeprefix("test_")
            for candidate in nodes.values():
                if candidate.kind == "python_module" and candidate.symbol and candidate.symbol.endswith(target_name):
                    edges[_edge("tests", file_node.id, candidate.id, file_node.provenance_refs, label="tests inferred module").id] = _edge("tests", file_node.id, candidate.id, file_node.provenance_refs, label="tests inferred module")


def _add_markdown_nodes(
    *,
    rel_path: str,
    path: Path,
    data_hash: str,
    git: GitState,
    file_node: GraphNode,
    nodes: dict[str, GraphNode],
    edges: dict[str, GraphEdge],
) -> None:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except UnicodeDecodeError:
        return
    for idx, line in enumerate(lines, start=1):
        if line.startswith("#"):
            title = line.lstrip("#").strip() or Path(rel_path).name
            prov = _prov(rel_path=rel_path, data_hash=data_hash, git=git, derived_by="markdown_parser", source_type="doc_section", line_start=idx, line_end=idx)
            section = _node(kind="markdown_section", label=title, rel_path=rel_path, symbol=f"{rel_path}#{title}", provenance_refs=[prov])
            nodes[section.id] = section
            edges[_edge("documents", section.id, file_node.id, [prov]).id] = _edge("documents", section.id, file_node.id, [prov])


def _add_generated_directory_sentinels(root: Path, git: GitState, nodes: dict[str, GraphNode], edges: dict[str, GraphEdge], project_id: str) -> None:
    for prefix in GENERATED_DIRECTORY_SENTINELS:
        directory = root / prefix.rstrip("/")
        if not directory.is_dir():
            continue
        rel_path = prefix
        if any(node.path == rel_path and node.kind == "generated_surface" for node in nodes.values()):
            continue
        child_names = sorted(child.name for child in directory.iterdir())[:200]
        data_hash = _sha256_bytes((rel_path + "\n" + "\n".join(child_names)).encode())
        prov = _prov(rel_path=rel_path, data_hash=data_hash, git=git, derived_by="filesystem_generated_directory", source_type="directory")
        node = _node(kind="generated_surface", label=rel_path, rel_path=rel_path, tags=["generated"], provenance_refs=[prov])
        nodes[node.id] = node
        edges[_edge("contains", project_id, node.id, [prov]).id] = _edge("contains", project_id, node.id, [prov])
        edges[_edge("generated_from", node.id, project_id, [prov]).id] = _edge("generated_from", node.id, project_id, [prov])


def build_project_graph(project_root: str | Path) -> ProjectGraph:
    requested = Path(project_root)
    root, git = _resolve_project_root(requested)
    project_hash = _sha256_bytes(f"{root}|{git.head_oid}|{','.join(git.dirty_paths)}".encode())
    project_prov = ProvenanceRef(
        id="prov:project:" + project_hash[:16],
        source_type="git" if git.available else "filesystem",
        derived_by="git" if git.available else "filesystem",
        confidence="deterministic",
        content_hash=project_hash,
        path=None,
        line_start=None,
        line_end=None,
        git_oid=git.head_oid,
        dirty=git.dirty,
    )
    project = _node(kind="project", label=root.name, rel_path=None, provenance_refs=[project_prov])
    nodes: dict[str, GraphNode] = {project.id: project}
    edges: dict[str, GraphEdge] = {}
    files = _tracked_and_untracked_files(root, git.available)
    file_nodes: dict[str, GraphNode] = {}
    for rel_path in files:
        path = root / rel_path
        if rel_path.startswith(".git/"):
            continue
        if not path.exists() and not path.is_symlink():
            continue
        data = _file_identity_bytes(path)
        data_hash = _sha256_bytes(data)
        kind, tags = _classify_file(rel_path)
        if path.is_symlink():
            tags = [*tags, "symlink"]
        prov = _prov(rel_path=rel_path, data_hash=data_hash, git=git, derived_by="filesystem", line_start=1, line_end=_line_count(data))
        file_node = _node(kind=kind, label=rel_path, rel_path=rel_path, tags=tags, provenance_refs=[prov])
        nodes[file_node.id] = file_node
        file_nodes[rel_path] = file_node
        edges[_edge("contains", project.id, file_node.id, [prov]).id] = _edge("contains", project.id, file_node.id, [prov])
        if kind == "config":
            edges[_edge("configures", file_node.id, project.id, [prov]).id] = _edge("configures", file_node.id, project.id, [prov])
        if kind == "protected_surface":
            edges[_edge("protects", file_node.id, project.id, [prov]).id] = _edge("protects", file_node.id, project.id, [prov])
        if kind == "generated_surface":
            edges[_edge("generated_from", file_node.id, project.id, [prov]).id] = _edge("generated_from", file_node.id, project.id, [prov])
    _add_generated_directory_sentinels(root, git, nodes, edges, project.id)
    # Parse after file nodes exist so inferred test edges can find target modules independent of order.
    for rel_path, file_node in sorted(file_nodes.items()):
        path = root / rel_path
        if not _is_parseable_regular_file(path):
            continue
        data_hash = file_node.provenance_refs[0].content_hash if file_node.provenance_refs else _sha256_bytes(_file_identity_bytes(path))
        if rel_path.endswith(".py") and not any(tag in file_node.tags for tag in {"excluded_from_primary_context", "protected", "generated"}):
            _add_python_nodes(root=root, rel_path=rel_path, path=path, data_hash=data_hash, git=git, file_node=file_node, nodes=nodes, edges=edges)
        if rel_path.endswith((".js", ".mjs", ".cjs", ".ts", ".tsx")) and not any(tag in file_node.tags for tag in {"excluded_from_primary_context", "protected", "generated"}):
            _add_javascript_nodes(rel_path=rel_path, path=path, data_hash=data_hash, git=git, file_node=file_node, nodes=nodes, edges=edges)
        if rel_path.endswith(".md") and not any(tag in file_node.tags for tag in {"excluded_from_primary_context", "protected", "generated"}):
            _add_markdown_nodes(rel_path=rel_path, path=path, data_hash=data_hash, git=git, file_node=file_node, nodes=nodes, edges=edges)
    # Second pass for tests after all module nodes exist.
    for rel_path, file_node in sorted(file_nodes.items()):
        if (rel_path.startswith("tests/") or Path(rel_path).name.startswith("test_")) and rel_path.endswith(".py"):
            stem = Path(rel_path).stem.removeprefix("test_")
            for candidate in nodes.values():
                if candidate.kind == "python_module" and candidate.symbol and candidate.symbol.split(".")[-1] == stem:
                    edge = _edge("tests", file_node.id, candidate.id, file_node.provenance_refs, label="tests inferred module")
                    edges[edge.id] = edge
    return ProjectGraph(
        schema_version="project-graph/v0.1",
        project_root=str(root),
        git=git,
        nodes=sorted(nodes.values(), key=lambda n: n.id),
        edges=sorted(edges.values(), key=lambda e: e.id),
    )


def _to_plain(value: Any) -> Any:
    if hasattr(value, "__dataclass_fields__"):
        return asdict(value)
    if isinstance(value, list):
        return [_to_plain(item) for item in value]
    if isinstance(value, dict):
        return {key: _to_plain(value[key]) for key in sorted(value)}
    return value


def graph_to_dict(graph: ProjectGraph) -> dict[str, Any]:
    return _to_plain(graph)


def canonical_graph_json(graph: ProjectGraph) -> str:
    return json.dumps(graph_to_dict(graph), sort_keys=True, separators=(",", ":"))


def write_graph_json(graph: ProjectGraph, path: str | Path) -> None:
    Path(path).write_text(json.dumps(graph_to_dict(graph), sort_keys=True, indent=2), encoding="utf-8")
