from __future__ import annotations

import ast
import hashlib
import importlib.metadata as importlib_metadata
import json
import re
import subprocess
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import tree_sitter_javascript
import tree_sitter_typescript
from tree_sitter import Language, Node, Parser

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
    metadata: dict[str, Any] = field(default_factory=dict)


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


def _edge(
    kind: str,
    from_node_id: str,
    to_node_id: str,
    provs: list[ProvenanceRef],
    label: str = "",
    *,
    confidence: str = "deterministic",
    derived_by: str = "project_graph",
) -> GraphEdge:
    raw = f"{kind}|{from_node_id}|{to_node_id}|{label}"
    if kind in {"calls", "inherits"} or confidence != "deterministic" or derived_by != "project_graph":
        raw = f"{raw}|{confidence}|{derived_by}"
    return GraphEdge(
        id="edge:" + _sha256_bytes(raw.encode())[:20],
        kind=kind,
        from_node_id=from_node_id,
        to_node_id=to_node_id,
        label=label or kind,
        provenance_refs=provs,
        confidence=confidence,
        derived_by=derived_by,
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


def _resolve_python_import(current_module: str, rel_path: str, node: ast.ImportFrom, module_symbols: set[str]) -> list[str]:
    def _module_alias_targets(module_name: str) -> list[str]:
        targets: list[str] = []
        needs_module_target = False
        for alias in node.names:
            if alias.name == "*":
                needs_module_target = True
                continue
            submodule = f"{module_name}.{alias.name}" if module_name else alias.name
            if submodule in module_symbols:
                targets.append(submodule)
            else:
                needs_module_target = True
        if needs_module_target and module_name:
            targets.insert(0, module_name)
        return list(dict.fromkeys(targets))

    if node.level == 0:
        if node.module:
            return _module_alias_targets(node.module)
        return [alias.name for alias in node.names if alias.name != "*"]
    if not current_module:
        if node.module:
            return _module_alias_targets(node.module)
        return [alias.name for alias in node.names if alias.name != "*"]
    current_parts = current_module.split(".")
    if Path(rel_path).name != "__init__.py":
        current_parts = current_parts[:-1]
    keep = max(0, len(current_parts) - (node.level - 1))
    base = current_parts[:keep]
    if node.module:
        suffix = node.module.split(".")
        return _module_alias_targets(".".join([*base, *suffix]))
    targets: list[str] = []
    base_module = ".".join(base)
    for alias in node.names:
        if alias.name == "*":
            continue
        submodule = ".".join([*base, alias.name])
        if submodule in module_symbols:
            targets.append(submodule)
        elif base_module:
            targets.append(base_module)
        else:
            targets.append(alias.name)
    return list(dict.fromkeys(targets))


def _type_checking_guard_polarity(node: ast.AST) -> bool | None:
    if isinstance(node, ast.Name):
        return True if node.id == "TYPE_CHECKING" else None
    if isinstance(node, ast.Attribute):
        return True if node.attr == "TYPE_CHECKING" else None
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
        polarity = _type_checking_guard_polarity(node.operand)
        return None if polarity is None else not polarity
    return None


class _RuntimeImportCollector(ast.NodeVisitor):
    def __init__(self) -> None:
        self.imports: list[ast.Import | ast.ImportFrom] = []

    def visit_Import(self, node: ast.Import) -> None:
        self.imports.append(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        self.imports.append(node)

    def visit_If(self, node: ast.If) -> None:
        polarity = _type_checking_guard_polarity(node.test)
        if polarity is True:
            for child in node.orelse:
                self.visit(child)
            return
        if polarity is False:
            for child in node.body:
                self.visit(child)
            return
        self.generic_visit(node)


def _runtime_imports(tree: ast.AST) -> list[ast.Import | ast.ImportFrom]:
    collector = _RuntimeImportCollector()
    collector.visit(tree)
    return collector.imports


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


def _ast_reference_name(node: ast.AST) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    return None


def _ast_line_start(node: ast.AST, fallback: int) -> int:
    return int(getattr(node, "lineno", fallback) or fallback)


def _ast_line_end(node: ast.AST, fallback: int) -> int:
    return int(getattr(node, "end_lineno", getattr(node, "lineno", fallback)) or fallback)


def _single_named_node(nodes_by_name: dict[str, list[GraphNode]], name: str | None) -> GraphNode | None:
    if not name:
        return None
    candidates = nodes_by_name.get(name, [])
    if len(candidates) != 1:
        return None
    return candidates[0]


def _edge_symbol_label(prefix: str, from_node: GraphNode, to_node: GraphNode) -> str:
    from_symbol = from_node.symbol or from_node.label
    to_symbol = to_node.symbol or to_node.label
    return f"{from_symbol} {prefix} {to_symbol}"


def _add_python_inheritance_edges(
    *,
    rel_path: str,
    data_hash: str,
    git: GitState,
    class_defs: list[ast.ClassDef],
    class_nodes_by_name: dict[str, list[GraphNode]],
    edges: dict[str, GraphEdge],
) -> None:
    for class_def in sorted(class_defs, key=lambda item: (item.lineno, item.col_offset, item.name)):
        from_node = _single_named_node(class_nodes_by_name, class_def.name)
        if from_node is None:
            continue
        for base in class_def.bases:
            to_node = _single_named_node(class_nodes_by_name, _ast_reference_name(base))
            if to_node is None:
                continue
            line_start = _ast_line_start(base, class_def.lineno)
            prov = _prov(
                rel_path=rel_path,
                data_hash=data_hash,
                git=git,
                derived_by="python_ast",
                line_start=line_start,
                line_end=_ast_line_end(base, line_start),
            )
            edge = _edge(
                "inherits",
                from_node.id,
                to_node.id,
                [prov],
                label=_edge_symbol_label("inherits", from_node, to_node),
                confidence="deterministic",
                derived_by="python_ast",
            )
            edges[edge.id] = edge


class _PythonCallEdgeCollector(ast.NodeVisitor):
    def __init__(
        self,
        *,
        rel_path: str,
        data_hash: str,
        git: GitState,
        function_nodes_by_name: dict[str, list[GraphNode]],
        edges: dict[str, GraphEdge],
    ) -> None:
        self.rel_path = rel_path
        self.data_hash = data_hash
        self.git = git
        self.function_nodes_by_name = function_nodes_by_name
        self.edges = edges
        self.function_stack: list[ast.FunctionDef | ast.AsyncFunctionDef] = []

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self.function_stack.append(node)
        self.generic_visit(node)
        self.function_stack.pop()

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self.function_stack.append(node)
        self.generic_visit(node)
        self.function_stack.pop()

    def visit_Call(self, node: ast.Call) -> None:
        if self.function_stack:
            caller_node = _single_named_node(self.function_nodes_by_name, self.function_stack[-1].name)
            callee_node = _single_named_node(self.function_nodes_by_name, _ast_reference_name(node.func))
            if caller_node is not None and callee_node is not None:
                line_start = _ast_line_start(node, self.function_stack[-1].lineno)
                prov = _prov(
                    rel_path=self.rel_path,
                    data_hash=self.data_hash,
                    git=self.git,
                    derived_by="python_ast",
                    line_start=line_start,
                    line_end=_ast_line_end(node, line_start),
                )
                edge = _edge(
                    "calls",
                    caller_node.id,
                    callee_node.id,
                    [prov],
                    label=_edge_symbol_label("calls", caller_node, callee_node),
                    confidence="deterministic",
                    derived_by="python_ast",
                )
                self.edges[edge.id] = edge
        self.generic_visit(node)


def _ast_dotted_name(node: ast.AST) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        prefix = _ast_dotted_name(node.value)
        if not prefix:
            return None
        return f"{prefix}.{node.attr}"
    return None


def _single_symbol_node(nodes_by_symbol: dict[str, list[GraphNode]], symbol: str | None) -> GraphNode | None:
    if not symbol:
        return None
    candidates = nodes_by_symbol.get(symbol, [])
    if len(candidates) != 1:
        return None
    return candidates[0]


def _python_import_base(current_module: str, rel_path: str, node: ast.ImportFrom) -> str:
    if node.level == 0:
        return node.module or ""
    current_parts = current_module.split(".") if current_module else []
    if Path(rel_path).name != "__init__.py":
        current_parts = current_parts[:-1]
    keep = max(0, len(current_parts) - (node.level - 1))
    base = current_parts[:keep]
    if node.module:
        base = [*base, *node.module.split(".")]
    return ".".join(part for part in base if part)


def _add_alias(aliases: dict[str, set[str]], local: str, target: str) -> None:
    if local and target:
        aliases.setdefault(local, set()).add(target)


def _python_import_bindings(
    *,
    module: str,
    rel_path: str,
    tree: ast.AST,
    function_symbols: set[str],
    module_symbols: set[str],
) -> tuple[dict[str, set[str]], set[str]]:
    aliases: dict[str, set[str]] = {}
    imported_modules: set[str] = set()
    for child in sorted(_runtime_imports(tree), key=lambda item: (getattr(item, "lineno", 0), getattr(item, "col_offset", 0), type(item).__name__)):
        if isinstance(child, ast.Import):
            for alias in child.names:
                imported_modules.add(alias.name)
                if alias.asname:
                    _add_alias(aliases, alias.asname, alias.name)
                elif alias.name in module_symbols:
                    _add_alias(aliases, alias.name.split(".", 1)[0], alias.name)
        elif isinstance(child, ast.ImportFrom):
            base = _python_import_base(module, rel_path, child)
            for alias in child.names:
                if alias.name == "*":
                    continue
                local = alias.asname or alias.name
                target = f"{base}.{alias.name}" if base else alias.name
                if target in function_symbols or target in module_symbols:
                    _add_alias(aliases, local, target)
    return aliases, imported_modules


def _python_function_bound_names(node: ast.FunctionDef | ast.AsyncFunctionDef) -> set[str]:
    names: set[str] = set()
    args = node.args
    for arg in [*args.posonlyargs, *args.args, *args.kwonlyargs]:
        names.add(arg.arg)
    if args.vararg:
        names.add(args.vararg.arg)
    if args.kwarg:
        names.add(args.kwarg.arg)
    for child in ast.walk(node):
        if isinstance(child, ast.Name) and isinstance(child.ctx, ast.Store):
            names.add(child.id)
    return names


class _PythonCrossFileCallCollector(ast.NodeVisitor):
    def __init__(
        self,
        *,
        module: str,
        rel_path: str,
        data_hash: str,
        git: GitState,
        function_nodes_by_symbol: dict[str, list[GraphNode]],
        same_file_function_names: set[str],
        aliases: dict[str, set[str]],
        imported_modules: set[str],
        edges: dict[str, GraphEdge],
    ) -> None:
        self.module = module
        self.rel_path = rel_path
        self.data_hash = data_hash
        self.git = git
        self.function_nodes_by_symbol = function_nodes_by_symbol
        self.same_file_function_names = same_file_function_names
        self.aliases = aliases
        self.imported_modules = imported_modules
        self.edges = edges
        self.function_stack: list[ast.FunctionDef | ast.AsyncFunctionDef] = []
        self.bound_name_stack: list[set[str]] = []

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self.function_stack.append(node)
        self.bound_name_stack.append(_python_function_bound_names(node))
        self.generic_visit(node)
        self.bound_name_stack.pop()
        self.function_stack.pop()

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self.function_stack.append(node)
        self.bound_name_stack.append(_python_function_bound_names(node))
        self.generic_visit(node)
        self.bound_name_stack.pop()
        self.function_stack.pop()

    def visit_Call(self, node: ast.Call) -> None:
        if self.function_stack:
            self._maybe_add_call_edge(node)
        self.generic_visit(node)

    def _maybe_add_call_edge(self, node: ast.Call) -> None:
        caller = self._caller_node()
        target = self._target_node(node.func)
        if caller is None or target is None or caller.path == target.path:
            return
        line_start = _ast_line_start(node, self.function_stack[-1].lineno)
        prov = _prov(
            rel_path=self.rel_path,
            data_hash=self.data_hash,
            git=self.git,
            derived_by="python_ast",
            line_start=line_start,
            line_end=_ast_line_end(node, line_start),
            confidence="heuristic",
        )
        edge = _edge(
            "calls",
            caller.id,
            target.id,
            [prov],
            label=_edge_symbol_label("calls", caller, target),
            confidence="heuristic",
            derived_by="python_ast",
        )
        self.edges[edge.id] = edge

    def _caller_node(self) -> GraphNode | None:
        function_name = self.function_stack[-1].name
        symbol = f"{self.module}.{function_name}" if self.module else function_name
        return _single_symbol_node(self.function_nodes_by_symbol, symbol)

    def _target_node(self, func: ast.AST) -> GraphNode | None:
        if isinstance(func, ast.Name):
            if func.id in self.same_file_function_names or func.id in self.bound_name_stack[-1]:
                return None
            targets = self.aliases.get(func.id, set())
            if len(targets) != 1:
                return None
            return _single_symbol_node(self.function_nodes_by_symbol, next(iter(targets)))
        dotted = _ast_dotted_name(func)
        if not dotted:
            return None
        parts = dotted.split(".")
        if parts[0] in self.bound_name_stack[-1] or parts[-1] in self.same_file_function_names:
            return None
        target_symbol = self._target_symbol_for_attribute(parts)
        return _single_symbol_node(self.function_nodes_by_symbol, target_symbol)

    def _target_symbol_for_attribute(self, parts: list[str]) -> str | None:
        if len(parts) < 2:
            return None
        receiver = ".".join(parts[:-1])
        attr = parts[-1]
        direct_targets = self.aliases.get(receiver, set())
        if len(direct_targets) == 1:
            return f"{next(iter(direct_targets))}.{attr}"
        if receiver in self.imported_modules:
            return ".".join(parts)
        first_targets = self.aliases.get(parts[0], set())
        if len(first_targets) == 1:
            return ".".join([next(iter(first_targets)), *parts[1:]])
        return None


def _add_python_cross_file_call_edges(
    *,
    root: Path,
    git: GitState,
    file_nodes: dict[str, GraphNode],
    nodes: dict[str, GraphNode],
    edges: dict[str, GraphEdge],
) -> None:
    function_nodes_by_symbol: dict[str, list[GraphNode]] = {}
    module_symbols: set[str] = set()
    for node in nodes.values():
        if node.kind == "python_function" and node.symbol:
            function_nodes_by_symbol.setdefault(node.symbol, []).append(node)
        elif node.kind == "python_module" and node.symbol:
            module_symbols.add(node.symbol)
    function_symbols = set(function_nodes_by_symbol)
    for rel_path, file_node in sorted(file_nodes.items()):
        if not rel_path.endswith(".py") or any(tag in file_node.tags for tag in {"excluded_from_primary_context", "protected", "generated"}):
            continue
        path = root / rel_path
        if not _is_parseable_regular_file(path):
            continue
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except (SyntaxError, UnicodeDecodeError, OSError):
            continue
        module = _module_name(rel_path)
        same_file_function_names = {
            node.label
            for node in nodes.values()
            if node.kind == "python_function" and node.path == rel_path
        }
        aliases, imported_modules = _python_import_bindings(
            module=module,
            rel_path=rel_path,
            tree=tree,
            function_symbols=function_symbols,
            module_symbols=module_symbols,
        )
        data_hash = file_node.provenance_refs[0].content_hash if file_node.provenance_refs else _sha256_bytes(_file_identity_bytes(path))
        _PythonCrossFileCallCollector(
            module=module,
            rel_path=rel_path,
            data_hash=data_hash,
            git=git,
            function_nodes_by_symbol=function_nodes_by_symbol,
            same_file_function_names=same_file_function_names,
            aliases=aliases,
            imported_modules=imported_modules,
            edges=edges,
        ).visit(tree)


_JS_IMPORT_RE = re.compile(
    r"(?:import\s+(?:[^'\"]+?\s+from\s+)?|export\s+[^'\"]+?\s+from\s+|require\s*\()"
    r"['\"]([^'\"]+)['\"]"
)
_JS_FUNCTION_RE = re.compile(r"(?:export\s+)?(?:async\s+)?function\s+([A-Za-z_$][\w$]*)\s*\(")


def _package_version(package: str) -> str:
    try:
        return importlib_metadata.version(package)
    except importlib_metadata.PackageNotFoundError:
        return "unknown"


def _tree_sitter_metadata() -> dict[str, Any]:
    return {
        "tree_sitter": _package_version("tree-sitter"),
        "tree_sitter_javascript": _package_version("tree-sitter-javascript"),
        "tree_sitter_typescript": _package_version("tree-sitter-typescript"),
    }


def _tree_sitter_language(rel_path: str) -> Language | None:
    if rel_path.endswith((".js", ".mjs", ".cjs")):
        return Language(tree_sitter_javascript.language())
    if rel_path.endswith(".tsx"):
        return Language(tree_sitter_typescript.language_tsx())
    if rel_path.endswith(".ts"):
        return Language(tree_sitter_typescript.language_typescript())
    return None


def _parse_javascript_treesitter(rel_path: str, path: Path) -> tuple[bytes, Node] | None:
    language = _tree_sitter_language(rel_path)
    if language is None:
        return None
    data = _safe_read_bytes(path)
    parser = Parser()
    parser.language = language
    return data, parser.parse(data).root_node


def _ts_text(node: Node, data: bytes) -> str:
    return data[node.start_byte : node.end_byte].decode("utf-8", "replace")


def _ts_string_value(node: Node, data: bytes) -> str:
    return _ts_text(node, data).strip("'\"")


def _ts_descendants(node: Node) -> list[Node]:
    found = [node]
    for child in node.named_children:
        found.extend(_ts_descendants(child))
    return found


def _ts_sorted_descendants(node: Node, node_type: str) -> list[Node]:
    return sorted(
        [candidate for candidate in _ts_descendants(node) if candidate.type == node_type],
        key=lambda candidate: (candidate.start_byte, candidate.end_byte, candidate.type),
    )


def _ts_name(node: Node, data: bytes) -> str | None:
    name = node.child_by_field_name("name")
    if name is None:
        return None
    return _ts_text(name, data)


def _ts_prov(*, rel_path: str, data_hash: str, git: GitState, node: Node, confidence: str = "deterministic") -> ProvenanceRef:
    return _prov(
        rel_path=rel_path,
        data_hash=data_hash,
        git=git,
        derived_by="javascript_treesitter",
        line_start=node.start_point.row + 1,
        line_end=node.end_point.row + 1,
        confidence=confidence,
    )


def _add_node_with_defined_edge(
    *,
    nodes: dict[str, GraphNode],
    edges: dict[str, GraphEdge],
    node: GraphNode,
    file_node: GraphNode,
    prov: ProvenanceRef,
) -> GraphNode:
    existing = nodes.get(node.id)
    if existing is not None:
        return existing
    nodes[node.id] = node
    edge = _edge("defined_in", node.id, file_node.id, [prov])
    edges[edge.id] = edge
    return node


def _add_javascript_treesitter_imports(
    *,
    rel_path: str,
    data: bytes,
    data_hash: str,
    git: GitState,
    root_node: Node,
    module_node: GraphNode,
    nodes: dict[str, GraphNode],
    edges: dict[str, GraphEdge],
) -> None:
    for import_node in _ts_sorted_descendants(root_node, "import_statement"):
        source = import_node.child_by_field_name("source")
        if source is None:
            continue
        imported = _resolve_javascript_import(rel_path, _ts_string_value(source, data))
        prov = _ts_prov(rel_path=rel_path, data_hash=data_hash, git=git, node=source)
        graph_node = _node(kind="javascript_import", label=imported, rel_path=rel_path, symbol=imported, provenance_refs=[prov])
        nodes.setdefault(graph_node.id, graph_node)
        edge = _edge("imports", module_node.id, graph_node.id, [prov], label=imported)
        edges.setdefault(edge.id, edge)


def _add_javascript_treesitter_nodes_for_file(
    *,
    rel_path: str,
    file_node: GraphNode,
    data: bytes,
    data_hash: str,
    git: GitState,
    root_node: Node,
    nodes: dict[str, GraphNode],
    edges: dict[str, GraphEdge],
) -> None:
    module = _javascript_module_name(rel_path)
    module_prov = _ts_prov(rel_path=rel_path, data_hash=data_hash, git=git, node=root_node)
    module_node = _node(kind="javascript_module", label=module, rel_path=rel_path, symbol=module, tags=file_node.tags, provenance_refs=[module_prov])
    module_node = _add_node_with_defined_edge(nodes=nodes, edges=edges, node=module_node, file_node=file_node, prov=module_prov)
    _add_javascript_treesitter_imports(rel_path=rel_path, data=data, data_hash=data_hash, git=git, root_node=root_node, module_node=module_node, nodes=nodes, edges=edges)
    for class_node in _ts_sorted_descendants(root_node, "class_declaration"):
        class_name = _ts_name(class_node, data)
        if not class_name:
            continue
        prov = _ts_prov(rel_path=rel_path, data_hash=data_hash, git=git, node=class_node)
        class_graph_node = _node(kind="javascript_class", label=class_name, rel_path=rel_path, symbol=f"{module}.{class_name}" if module else class_name, tags=file_node.tags, provenance_refs=[prov])
        _add_node_with_defined_edge(nodes=nodes, edges=edges, node=class_graph_node, file_node=file_node, prov=prov)
        body = class_node.child_by_field_name("body")
        if body is None:
            continue
        for method in [child for child in body.named_children if child.type == "method_definition"]:
            method_name = _ts_name(method, data)
            if not method_name:
                continue
            method_prov = _ts_prov(rel_path=rel_path, data_hash=data_hash, git=git, node=method)
            symbol = f"{module}.{class_name}.{method_name}" if module else f"{class_name}.{method_name}"
            method_node = _node(kind="javascript_function", label=method_name, rel_path=rel_path, symbol=symbol, tags=file_node.tags, provenance_refs=[method_prov])
            _add_node_with_defined_edge(nodes=nodes, edges=edges, node=method_node, file_node=file_node, prov=method_prov)
    for function_node in _ts_sorted_descendants(root_node, "function_declaration"):
        function_name = _ts_name(function_node, data)
        if not function_name:
            continue
        prov = _ts_prov(rel_path=rel_path, data_hash=data_hash, git=git, node=function_node)
        symbol = f"{module}.{function_name}" if module else function_name
        graph_node = _node(kind="javascript_function", label=function_name, rel_path=rel_path, symbol=symbol, tags=file_node.tags, provenance_refs=[prov])
        _add_node_with_defined_edge(nodes=nodes, edges=edges, node=graph_node, file_node=file_node, prov=prov)
    for declarator in _ts_sorted_descendants(root_node, "variable_declarator"):
        value = declarator.child_by_field_name("value")
        if value is None or value.type not in {"arrow_function", "function"}:
            continue
        variable_name = _ts_name(declarator, data)
        if not variable_name:
            continue
        prov = _ts_prov(rel_path=rel_path, data_hash=data_hash, git=git, node=declarator)
        symbol = f"{module}.{variable_name}" if module else variable_name
        graph_node = _node(kind="javascript_function", label=variable_name, rel_path=rel_path, symbol=symbol, tags=file_node.tags, provenance_refs=[prov])
        _add_node_with_defined_edge(nodes=nodes, edges=edges, node=graph_node, file_node=file_node, prov=prov)


def _javascript_import_bindings(
    *,
    rel_path: str,
    data: bytes,
    root_node: Node,
    function_symbols: set[str],
    class_symbols: set[str],
) -> dict[str, set[str]]:
    aliases: dict[str, set[str]] = {}
    target_symbols = function_symbols | class_symbols
    for import_node in _ts_sorted_descendants(root_node, "import_statement"):
        source = import_node.child_by_field_name("source")
        if source is None:
            continue
        imported_module = _resolve_javascript_import(rel_path, _ts_string_value(source, data))
        for specifier in _ts_sorted_descendants(import_node, "import_specifier"):
            name_node = specifier.child_by_field_name("name")
            if name_node is None:
                continue
            alias_node = specifier.child_by_field_name("alias")
            imported_name = _ts_text(name_node, data)
            local_name = _ts_text(alias_node, data) if alias_node is not None else imported_name
            target = f"{imported_module}.{imported_name}"
            if target in target_symbols:
                _add_alias(aliases, local_name, target)
    return aliases


def _javascript_same_file_symbols(nodes: dict[str, GraphNode], *, rel_path: str, kind: str) -> dict[str, list[GraphNode]]:
    symbols: dict[str, list[GraphNode]] = {}
    for node in nodes.values():
        if node.kind == kind and node.path == rel_path:
            symbols.setdefault(node.label, []).append(node)
    return symbols


def _javascript_resolve_symbol(
    *,
    name: str,
    same_file: dict[str, list[GraphNode]],
    aliases: dict[str, set[str]],
    target_nodes_by_symbol: dict[str, list[GraphNode]],
) -> tuple[GraphNode | None, str]:
    same_file_target = _single_named_node(same_file, name)
    if same_file_target is not None:
        return same_file_target, "deterministic"
    alias_targets = aliases.get(name, set())
    if len(alias_targets) != 1:
        return None, "ambiguous"
    return _single_symbol_node(target_nodes_by_symbol, next(iter(alias_targets))), "heuristic"


def _javascript_first_identifier(node: Node, data: bytes) -> str | None:
    for child in _ts_descendants(node):
        if child.type in {"identifier", "type_identifier"}:
            return _ts_text(child, data)
    return None


def _add_javascript_inheritance_edges(
    *,
    rel_path: str,
    data: bytes,
    data_hash: str,
    git: GitState,
    root_node: Node,
    nodes: dict[str, GraphNode],
    edges: dict[str, GraphEdge],
    class_nodes_by_symbol: dict[str, list[GraphNode]],
    class_symbols: set[str],
) -> None:
    aliases = _javascript_import_bindings(rel_path=rel_path, data=data, root_node=root_node, function_symbols=set(), class_symbols=class_symbols)
    same_file_classes = _javascript_same_file_symbols(nodes, rel_path=rel_path, kind="javascript_class")
    for class_node in _ts_sorted_descendants(root_node, "class_declaration"):
        class_name = _ts_name(class_node, data)
        if not class_name:
            continue
        from_node = _single_named_node(same_file_classes, class_name)
        heritage = next((child for child in class_node.named_children if child.type == "class_heritage"), None)
        if from_node is None or heritage is None:
            continue
        base_name = _javascript_first_identifier(heritage, data)
        if not base_name:
            continue
        to_node, confidence = _javascript_resolve_symbol(name=base_name, same_file=same_file_classes, aliases=aliases, target_nodes_by_symbol=class_nodes_by_symbol)
        if to_node is None:
            continue
        prov = _ts_prov(rel_path=rel_path, data_hash=data_hash, git=git, node=heritage, confidence=confidence)
        edge = _edge("inherits", from_node.id, to_node.id, [prov], label=_edge_symbol_label("inherits", from_node, to_node), confidence=confidence, derived_by="javascript_treesitter")
        edges[edge.id] = edge


def _javascript_function_scopes(*, module: str, rel_path: str, data: bytes, root_node: Node, function_nodes_by_symbol: dict[str, list[GraphNode]]) -> list[tuple[GraphNode, Node]]:
    scopes: list[tuple[GraphNode, Node]] = []
    for class_node in _ts_sorted_descendants(root_node, "class_declaration"):
        class_name = _ts_name(class_node, data)
        body = class_node.child_by_field_name("body")
        if not class_name or body is None:
            continue
        for method in [child for child in body.named_children if child.type == "method_definition"]:
            method_name = _ts_name(method, data)
            if not method_name:
                continue
            symbol = f"{module}.{class_name}.{method_name}" if module else f"{class_name}.{method_name}"
            graph_node = _single_symbol_node(function_nodes_by_symbol, symbol)
            body_node = method.child_by_field_name("body") or method
            if graph_node is not None:
                scopes.append((graph_node, body_node))
    for function_node in _ts_sorted_descendants(root_node, "function_declaration"):
        function_name = _ts_name(function_node, data)
        if not function_name:
            continue
        symbol = f"{module}.{function_name}" if module else function_name
        graph_node = _single_symbol_node(function_nodes_by_symbol, symbol)
        body_node = function_node.child_by_field_name("body") or function_node
        if graph_node is not None:
            scopes.append((graph_node, body_node))
    for declarator in _ts_sorted_descendants(root_node, "variable_declarator"):
        value = declarator.child_by_field_name("value")
        if value is None or value.type not in {"arrow_function", "function"}:
            continue
        variable_name = _ts_name(declarator, data)
        if not variable_name:
            continue
        symbol = f"{module}.{variable_name}" if module else variable_name
        graph_node = _single_symbol_node(function_nodes_by_symbol, symbol)
        if graph_node is not None:
            scopes.append((graph_node, value))
    return sorted(scopes, key=lambda item: (item[1].start_byte, item[0].id))


def _add_javascript_call_edges(
    *,
    rel_path: str,
    data: bytes,
    data_hash: str,
    git: GitState,
    root_node: Node,
    nodes: dict[str, GraphNode],
    edges: dict[str, GraphEdge],
    function_nodes_by_symbol: dict[str, list[GraphNode]],
    function_symbols: set[str],
) -> None:
    module = _javascript_module_name(rel_path)
    aliases = _javascript_import_bindings(rel_path=rel_path, data=data, root_node=root_node, function_symbols=function_symbols, class_symbols=set())
    same_file_functions = _javascript_same_file_symbols(nodes, rel_path=rel_path, kind="javascript_function")
    for from_node, body in _javascript_function_scopes(module=module, rel_path=rel_path, data=data, root_node=root_node, function_nodes_by_symbol=function_nodes_by_symbol):
        for call in _ts_sorted_descendants(body, "call_expression"):
            callee = call.child_by_field_name("function")
            if callee is None or callee.type not in {"identifier", "property_identifier"}:
                continue
            target, confidence = _javascript_resolve_symbol(name=_ts_text(callee, data), same_file=same_file_functions, aliases=aliases, target_nodes_by_symbol=function_nodes_by_symbol)
            if target is None:
                continue
            prov = _ts_prov(rel_path=rel_path, data_hash=data_hash, git=git, node=call, confidence=confidence)
            edge = _edge("calls", from_node.id, target.id, [prov], label=_edge_symbol_label("calls", from_node, target), confidence=confidence, derived_by="javascript_treesitter")
            edges[edge.id] = edge


def _add_javascript_treesitter_nodes_and_edges(
    *,
    root: Path,
    git: GitState,
    file_nodes: dict[str, GraphNode],
    nodes: dict[str, GraphNode],
    edges: dict[str, GraphEdge],
) -> None:
    parsed: dict[str, tuple[bytes, Node, str]] = {}
    for rel_path, file_node in sorted(file_nodes.items()):
        if not rel_path.endswith((".js", ".mjs", ".cjs", ".ts", ".tsx")) or any(tag in file_node.tags for tag in {"excluded_from_primary_context", "protected", "generated"}):
            continue
        parsed_file = _parse_javascript_treesitter(rel_path, root / rel_path)
        if parsed_file is None:
            continue
        data, root_node = parsed_file
        data_hash = file_node.provenance_refs[0].content_hash if file_node.provenance_refs else _sha256_bytes(data)
        parsed[rel_path] = (data, root_node, data_hash)
        _add_javascript_treesitter_nodes_for_file(rel_path=rel_path, file_node=file_node, data=data, data_hash=data_hash, git=git, root_node=root_node, nodes=nodes, edges=edges)
    function_nodes_by_symbol: dict[str, list[GraphNode]] = {}
    class_nodes_by_symbol: dict[str, list[GraphNode]] = {}
    for node in nodes.values():
        if node.kind == "javascript_function" and node.symbol:
            function_nodes_by_symbol.setdefault(node.symbol, []).append(node)
        elif node.kind == "javascript_class" and node.symbol:
            class_nodes_by_symbol.setdefault(node.symbol, []).append(node)
    function_symbols = set(function_nodes_by_symbol)
    class_symbols = set(class_nodes_by_symbol)
    for rel_path, (data, root_node, data_hash) in sorted(parsed.items()):
        _add_javascript_inheritance_edges(rel_path=rel_path, data=data, data_hash=data_hash, git=git, root_node=root_node, nodes=nodes, edges=edges, class_nodes_by_symbol=class_nodes_by_symbol, class_symbols=class_symbols)
        _add_javascript_call_edges(rel_path=rel_path, data=data, data_hash=data_hash, git=git, root_node=root_node, nodes=nodes, edges=edges, function_nodes_by_symbol=function_nodes_by_symbol, function_symbols=function_symbols)


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
    module_symbols: set[str],
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
    class_defs: list[ast.ClassDef] = []
    class_nodes_by_name: dict[str, list[GraphNode]] = {}
    function_nodes_by_name: dict[str, list[GraphNode]] = {}
    for child in ast.walk(tree):
        if isinstance(child, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            is_class = isinstance(child, ast.ClassDef)
            kind = "python_class" if is_class else "python_function"
            symbol = f"{module}.{child.name}" if module else child.name
            end_lineno = getattr(child, "end_lineno", child.lineno)
            prov = _prov(rel_path=rel_path, data_hash=data_hash, git=git, derived_by="python_ast", line_start=child.lineno, line_end=end_lineno)
            sym_node = _node(kind=kind, label=child.name, rel_path=rel_path, symbol=symbol, tags=file_node.tags, provenance_refs=[prov])
            nodes[sym_node.id] = sym_node
            edges[_edge("defined_in", sym_node.id, file_node.id, [prov]).id] = _edge("defined_in", sym_node.id, file_node.id, [prov])
            if is_class:
                class_defs.append(child)
                class_nodes_by_name.setdefault(child.name, []).append(sym_node)
            else:
                function_nodes_by_name.setdefault(child.name, []).append(sym_node)
    for child in _runtime_imports(tree):
        names: list[str] = []
        if isinstance(child, ast.Import):
            names = [alias.name for alias in child.names]
        elif isinstance(child, ast.ImportFrom):
            names = _resolve_python_import(module, rel_path, child, module_symbols)
        for imported in names:
            prov = _prov(rel_path=rel_path, data_hash=data_hash, git=git, derived_by="python_ast", line_start=child.lineno, line_end=getattr(child, "end_lineno", child.lineno))
            import_node = _node(kind="python_import", label=imported, rel_path=rel_path, symbol=imported, provenance_refs=[prov])
            nodes[import_node.id] = import_node
            edges[_edge("imports", module_node.id, import_node.id, [prov], label=imported).id] = _edge("imports", module_node.id, import_node.id, [prov], label=imported)
    _add_python_inheritance_edges(
        rel_path=rel_path,
        data_hash=data_hash,
        git=git,
        class_defs=class_defs,
        class_nodes_by_name=class_nodes_by_name,
        edges=edges,
    )
    _PythonCallEdgeCollector(
        rel_path=rel_path,
        data_hash=data_hash,
        git=git,
        function_nodes_by_name=function_nodes_by_name,
        edges=edges,
    ).visit(tree)
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
    python_module_symbols = {
        _module_name(rel_path)
        for rel_path, file_node in file_nodes.items()
        if rel_path.endswith(".py")
        and not any(tag in file_node.tags for tag in {"excluded_from_primary_context", "protected", "generated"})
        and _is_parseable_regular_file(root / rel_path)
    }
    # Parse after file nodes exist so inferred test edges can find target modules independent of order.
    for rel_path, file_node in sorted(file_nodes.items()):
        path = root / rel_path
        if not _is_parseable_regular_file(path):
            continue
        data_hash = file_node.provenance_refs[0].content_hash if file_node.provenance_refs else _sha256_bytes(_file_identity_bytes(path))
        if rel_path.endswith(".py") and not any(tag in file_node.tags for tag in {"excluded_from_primary_context", "protected", "generated"}):
            _add_python_nodes(root=root, rel_path=rel_path, path=path, data_hash=data_hash, git=git, file_node=file_node, module_symbols=python_module_symbols, nodes=nodes, edges=edges)
        if rel_path.endswith((".js", ".mjs", ".cjs", ".ts", ".tsx")) and not any(tag in file_node.tags for tag in {"excluded_from_primary_context", "protected", "generated"}):
            _add_javascript_nodes(rel_path=rel_path, path=path, data_hash=data_hash, git=git, file_node=file_node, nodes=nodes, edges=edges)
        if rel_path.endswith(".md") and not any(tag in file_node.tags for tag in {"excluded_from_primary_context", "protected", "generated"}):
            _add_markdown_nodes(rel_path=rel_path, path=path, data_hash=data_hash, git=git, file_node=file_node, nodes=nodes, edges=edges)
    _add_python_cross_file_call_edges(root=root, git=git, file_nodes=file_nodes, nodes=nodes, edges=edges)
    _add_javascript_treesitter_nodes_and_edges(root=root, git=git, file_nodes=file_nodes, nodes=nodes, edges=edges)
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
        metadata={"tree_sitter": _tree_sitter_metadata()},
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
