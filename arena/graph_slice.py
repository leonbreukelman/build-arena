from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from arena.project_graph import build_project_graph, graph_to_dict


@dataclass(frozen=True)
class GraphNodeRef:
    node_id: str
    kind: str
    symbol: str
    path: str


@dataclass(frozen=True)
class GraphEdgeRef:
    edge_id: str
    kind: str
    from_node_id: str
    to_node_id: str
    from_symbol: str
    to_symbol: str
    from_path: str
    to_path: str


@dataclass(frozen=True)
class GraphSlice:
    modules: tuple[GraphNodeRef, ...] = ()
    import_edges: tuple[GraphEdgeRef, ...] = ()
    call_edges: tuple[GraphEdgeRef, ...] = ()


def fresh_graph_slice(project_path: Path) -> GraphSlice:
    """Return a reduced graph slice rebuilt from live filesystem/git ground truth."""
    graph_data = graph_to_dict(build_project_graph(project_path))
    return graph_slice_from_graph_data(graph_data)


def graph_slice_from_graph_data(graph_data: dict[str, Any]) -> GraphSlice:
    nodes = [node for node in graph_data.get("nodes", []) if isinstance(node, dict)]
    edges = [edge for edge in graph_data.get("edges", []) if isinstance(edge, dict)]
    nodes_by_id = {str(node.get("id", "")): node for node in nodes if node.get("id")}
    modules = tuple(sorted((_node_ref(node) for node in nodes if _is_module_node(node)), key=_node_ref_key))
    modules_by_id = {module.node_id: module for module in modules}
    modules_by_symbol: dict[str, list[GraphNodeRef]] = {}
    for module in modules:
        modules_by_symbol.setdefault(module.symbol, []).append(module)
    unique_module_by_symbol = {symbol: refs[0] for symbol, refs in modules_by_symbol.items() if len(refs) == 1}

    import_edges: list[GraphEdgeRef] = []
    call_edges: list[GraphEdgeRef] = []
    for edge in edges:
        edge_kind = str(edge.get("kind", ""))
        from_node = nodes_by_id.get(str(edge.get("from_node_id", "")))
        to_node = nodes_by_id.get(str(edge.get("to_node_id", "")))
        if edge_kind == "imports" and from_node is not None and to_node is not None:
            from_module = modules_by_id.get(str(from_node.get("id", "")))
            imported_symbol = _node_symbol(to_node) or str(edge.get("label", ""))
            to_module = unique_module_by_symbol.get(imported_symbol)
            if from_module is not None and to_module is not None:
                import_edges.append(_edge_ref(edge, "imports", from_module, to_module))
        elif edge_kind == "calls" and from_node is not None and to_node is not None:
            from_ref = _node_ref(from_node)
            to_ref = _node_ref(to_node)
            if from_ref.path and to_ref.path:
                call_edges.append(_edge_ref(edge, "calls", from_ref, to_ref))
    return GraphSlice(
        modules=modules,
        import_edges=tuple(sorted(dict.fromkeys(import_edges), key=_edge_ref_key)),
        call_edges=tuple(sorted(dict.fromkeys(call_edges), key=_edge_ref_key)),
    )


def _is_module_node(node: dict[str, Any]) -> bool:
    return str(node.get("kind", "")) in {"python_module", "javascript_module"} and bool(_node_symbol(node))


def _node_ref(node: dict[str, Any]) -> GraphNodeRef:
    return GraphNodeRef(
        node_id=str(node.get("id", "")),
        kind=str(node.get("kind", "")),
        symbol=_node_symbol(node),
        path=str(node.get("path", "")),
    )


def _node_symbol(node: dict[str, Any]) -> str:
    return str(node.get("symbol") or node.get("label") or "")


def _edge_ref(edge: dict[str, Any], kind: str, from_node: GraphNodeRef, to_node: GraphNodeRef) -> GraphEdgeRef:
    return GraphEdgeRef(
        edge_id=str(edge.get("id", "")),
        kind=kind,
        from_node_id=from_node.node_id,
        to_node_id=to_node.node_id,
        from_symbol=from_node.symbol,
        to_symbol=to_node.symbol,
        from_path=from_node.path,
        to_path=to_node.path,
    )


def _node_ref_key(node: GraphNodeRef) -> tuple[str, str, str, str]:
    return (node.symbol, node.path, node.kind, node.node_id)


def _edge_ref_key(edge: GraphEdgeRef) -> tuple[str, str, str, str, str]:
    return (edge.kind, edge.from_symbol, edge.to_symbol, edge.from_path, edge.to_path)
