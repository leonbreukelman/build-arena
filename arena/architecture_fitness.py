from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from arena.graph_slice import GraphSlice, fresh_graph_slice

CONTRACT_SCHEMA_VERSION = "architecture-fitness-contract/v0"
CONTRACT_KIND_IMPORT_CYCLE = "forbid_import_cycle"
CONTRACT_DIR = "tests/architecture"


@dataclass(frozen=True)
class ArchitectureFitnessGateResult:
    accepted: bool
    reason: str
    current_status: str
    contract_path: str
    grounded_modules: tuple[str, ...] = ()
    bound_edges: tuple[dict[str, str], ...] = ()
    derived_findings: tuple[dict[str, Any], ...] = ()

    def to_jsonable(self) -> dict[str, Any]:
        return {
            "accepted": self.accepted,
            "reason": self.reason,
            "currentStatus": self.current_status,
            "contractPath": self.contract_path,
            "groundedModules": list(self.grounded_modules),
            "boundEdges": list(self.bound_edges),
            "derivedFindings": list(self.derived_findings),
        }


def architecture_contract_target(digest: str) -> str:
    return f"{CONTRACT_DIR}/architecture-fitness-{digest}.json"


def canonical_contract_text(contract: dict[str, Any]) -> str:
    return json.dumps(_canonical_contract(contract), indent=2, sort_keys=True) + "\n"


def contract_digest(contract: dict[str, Any]) -> str:
    payload = _semantic_constraint_payload(contract)
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()[:12]


def selected_import_cycle(graph_slice: GraphSlice) -> tuple[str, ...]:
    cycles = import_cycles(graph_slice)
    return cycles[0] if cycles else ()


def import_cycles(graph_slice: GraphSlice) -> tuple[tuple[str, ...], ...]:
    adjacency: dict[str, set[str]] = {}
    modules = {module.symbol for module in graph_slice.modules}
    for edge in graph_slice.import_edges:
        if edge.from_symbol == edge.to_symbol:
            continue
        if edge.from_symbol in modules and edge.to_symbol in modules:
            adjacency.setdefault(edge.from_symbol, set()).add(edge.to_symbol)
    found: set[tuple[str, ...]] = set()
    for start in sorted(adjacency):
        _walk_cycles(start, start, adjacency, (start,), found)
    return tuple(sorted(found))


def build_import_cycle_contract(finding_id: str, cycle: tuple[str, ...]) -> dict[str, Any]:
    if len(cycle) < 2:
        raise ValueError("cycle must contain at least two modules")
    modules = sorted(cycle)
    edges = _cycle_edges(cycle)
    base: dict[str, Any] = {
        "schemaVersion": CONTRACT_SCHEMA_VERSION,
        "kind": CONTRACT_KIND_IMPORT_CYCLE,
        "id": "",
        "findingId": finding_id,
        "modules": modules,
        "forbiddenEdges": edges,
        "description": f"Prevent the graph-evidenced import cycle {' -> '.join(cycle)} -> {cycle[0]}.",
    }
    digest = contract_digest(base)
    base["id"] = f"architecture-fitness-{digest}"
    return _canonical_contract(base)


def validate_architecture_contract(repo: str | Path, contract_path: str | Path) -> ArchitectureFitnessGateResult:
    repo_path = Path(repo).resolve()
    path = (repo_path / contract_path).resolve() if not Path(contract_path).is_absolute() else Path(contract_path).resolve()
    rel_path = _relative_or_str(repo_path, path)
    try:
        contract = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return _reject("missing_contract", rel_path)
    except json.JSONDecodeError:
        return _reject("invalid_json", rel_path)
    if not isinstance(contract, dict):
        return _reject("invalid_contract", rel_path)
    if contract.get("schemaVersion") != CONTRACT_SCHEMA_VERSION:
        return _reject("unknown_schema", rel_path)
    if contract.get("kind") != CONTRACT_KIND_IMPORT_CYCLE:
        return _reject("unknown_kind", rel_path)

    digest = contract_digest(contract)
    expected_id = f"architecture-fitness-{digest}"
    expected_name = f"architecture-fitness-{digest}.json"
    if contract.get("id") != expected_id or path.name != expected_name:
        return _reject("digest_mismatch", rel_path)

    duplicate = _duplicate_contract_path(repo_path, path, digest)
    if duplicate is not None:
        return _reject("duplicate_contract", rel_path)

    modules = _string_list(contract.get("modules"))
    edges = _edge_list(contract.get("forbiddenEdges"))
    graph = fresh_graph_slice(repo_path)
    real_modules = {module.symbol for module in graph.modules}
    referenced = set(modules)
    for edge in edges:
        referenced.add(edge["from"])
        referenced.add(edge["to"])
    unknown = sorted(referenced - real_modules)
    if unknown:
        return _reject("unknown_module", rel_path, grounded_modules=tuple(sorted(referenced & real_modules)))

    if not _is_exact_simple_cycle(modules, edges):
        return _reject("non_binding_contract", rel_path, grounded_modules=tuple(sorted(modules)))
    live_edges = {(edge.from_symbol, edge.to_symbol) for edge in graph.import_edges}
    edge_pairs = tuple((edge["from"], edge["to"]) for edge in edges)
    if not all(pair in live_edges for pair in edge_pairs):
        return _reject("non_binding_contract", rel_path, grounded_modules=tuple(sorted(modules)))

    bound_edges = tuple({"from": left, "to": right} for left, right in sorted(edge_pairs))
    derived_id = f"code.change.break-import-cycle.{digest}"
    return ArchitectureFitnessGateResult(
        accepted=True,
        reason="accepted",
        current_status="failing",
        contract_path=rel_path,
        grounded_modules=tuple(sorted(modules)),
        bound_edges=bound_edges,
        derived_findings=(
            {
                "id": derived_id,
                "title": f"Break graph-evidenced import cycle among {', '.join(sorted(modules))}",
                "sourceContract": rel_path,
                "autonomyBoundary": "needs_code_change",
            },
        ),
    )


def _walk_cycles(
    start: str,
    current: str,
    adjacency: dict[str, set[str]],
    path: tuple[str, ...],
    found: set[tuple[str, ...]],
) -> None:
    for nxt in sorted(adjacency.get(current, set())):
        if nxt == start and len(path) >= 2:
            found.add(_canonical_cycle(path))
            continue
        if nxt in path or len(path) >= 8:
            continue
        _walk_cycles(start, nxt, adjacency, (*path, nxt), found)


def _canonical_cycle(cycle: tuple[str, ...]) -> tuple[str, ...]:
    rotations = [cycle[index:] + cycle[:index] for index in range(len(cycle))]
    return min(rotations)


def _cycle_edges(cycle: tuple[str, ...]) -> list[dict[str, str]]:
    return [
        {"from": cycle[index], "to": cycle[(index + 1) % len(cycle)]}
        for index in range(len(cycle))
    ]


def _canonical_contract(contract: dict[str, Any]) -> dict[str, Any]:
    modules = sorted(_string_list(contract.get("modules")))
    edges = sorted(_edge_list(contract.get("forbiddenEdges")), key=lambda item: (item["from"], item["to"]))
    return {
        "description": str(contract.get("description", "")),
        "findingId": str(contract.get("findingId", "")),
        "forbiddenEdges": edges,
        "id": str(contract.get("id", "")),
        "kind": str(contract.get("kind", "")),
        "modules": modules,
        "schemaVersion": str(contract.get("schemaVersion", "")),
    }


def _semantic_constraint_payload(contract: dict[str, Any]) -> dict[str, Any]:
    return {
        "forbiddenEdges": sorted(_edge_list(contract.get("forbiddenEdges")), key=lambda item: (item["from"], item["to"])),
        "kind": str(contract.get("kind", "")),
        "modules": sorted(_string_list(contract.get("modules"))),
    }


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value if isinstance(item, str) and item.strip()]


def _edge_list(value: Any) -> list[dict[str, str]]:
    if not isinstance(value, list):
        return []
    edges: list[dict[str, str]] = []
    for item in value:
        if not isinstance(item, dict):
            continue
        left = item.get("from")
        right = item.get("to")
        if isinstance(left, str) and left.strip() and isinstance(right, str) and right.strip():
            edges.append({"from": left, "to": right})
    return edges


def _is_exact_simple_cycle(modules: list[str], edges: list[dict[str, str]]) -> bool:
    if len(modules) < 2 or len(set(modules)) != len(modules) or len(edges) != len(modules):
        return False
    edge_modules = {edge["from"] for edge in edges} | {edge["to"] for edge in edges}
    if edge_modules != set(modules):
        return False
    if any(edge["from"] == edge["to"] for edge in edges):
        return False
    outgoing: dict[str, str] = {}
    incoming: dict[str, str] = {}
    for edge in edges:
        if edge["from"] in outgoing or edge["to"] in incoming:
            return False
        outgoing[edge["from"]] = edge["to"]
        incoming[edge["to"]] = edge["from"]
    start = min(modules)
    seen: list[str] = []
    current = start
    for _ in modules:
        if current in seen or current not in outgoing:
            return False
        seen.append(current)
        current = outgoing[current]
    return current == start and set(seen) == set(modules)


def _duplicate_contract_path(repo: Path, current: Path, digest: str) -> Path | None:
    root = repo / CONTRACT_DIR
    if not root.exists():
        return None
    for candidate in sorted(root.glob("**/*.json")):
        if candidate.resolve() == current:
            continue
        try:
            payload = json.loads(candidate.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if isinstance(payload, dict) and contract_digest(payload) == digest:
            return candidate
    return None


def _reject(
    reason: str,
    contract_path: str,
    *,
    grounded_modules: tuple[str, ...] = (),
) -> ArchitectureFitnessGateResult:
    return ArchitectureFitnessGateResult(
        accepted=False,
        reason=reason,
        current_status="invalid",
        contract_path=contract_path,
        grounded_modules=grounded_modules,
    )


def _relative_or_str(root: Path, path: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return str(path)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m arena.architecture_fitness_gate")
    parser.add_argument("--repo", required=True)
    parser.add_argument("--contract", required=True)
    args = parser.parse_args(argv)
    result = validate_architecture_contract(args.repo, args.contract)
    print(json.dumps(result.to_jsonable(), sort_keys=True))
    return 0 if result.accepted and result.current_status == "passing" else 1


if __name__ == "__main__":
    raise SystemExit(main())
