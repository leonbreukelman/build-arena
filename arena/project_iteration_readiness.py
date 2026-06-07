from __future__ import annotations

import re
import tomllib
from pathlib import Path
from typing import Any

_PROFILE_TAG_LABELS = {
    "auth": "authentication/session lifecycle",
    "rate_limit": "rate limiting",
    "concurrency": "concurrency back-pressure",
    "pagination": "pagination",
    "read_only": "read-only external operations",
    "external_http": "external HTTP access",
    "mcp_server": "MCP server registration",
    "resource_handlers": "resource handlers",
    "tool_handlers": "tool handlers",
    "configuration": "configuration/secrets",
    "entrypoint": "runtime entrypoint",
    "injection": "client injection",
}


def component_responsibility_summary(module: str, text: str, key_symbols: list[str], behavioral_tags: list[str]) -> str:
    symbols = _stable_nonempty(key_symbols)[:5]
    tags = _stable_nonempty(behavioral_tags)[:6]
    module_label = module or "component"
    if "client" in module_label.split(".")[-1] and {"auth", "rate_limit", "concurrency", "pagination"} & set(tags):
        return _join_sentence(
            "Manage authenticated HTTP client behavior",
            _phrase_if("auth" in tags, "auth/session lifecycle"),
            _phrase_if("rate_limit" in tags, "rate limiting"),
            _phrase_if("concurrency" in tags, "concurrency back-pressure"),
            _phrase_if("pagination" in tags, "pagination"),
            _phrase_if("read_only" in tags, "read-only endpoint wrappers"),
            f"through {', '.join(symbols) if symbols else module_label}",
        )
    if tags:
        readable_tags = [_PROFILE_TAG_LABELS.get(tag, tag.replace("_", " ")) for tag in tags]
        symbol_part = f" via {', '.join(symbols)}" if symbols else ""
        return f"Coordinate {', '.join(readable_tags)}{symbol_part} with source-backed behavior in `{module_label}`."
    if symbols:
        return f"Provide `{module_label}` behavior through source symbols {', '.join(symbols[:4])}."
    return f"Represent the source-backed `{module_label}` runtime responsibility."


def detect_behavioral_tags(module: str, path: str, text: str, key_symbols: list[str]) -> list[str]:
    lower = text.lower()
    symbol_text = " ".join(key_symbols).lower()
    tags: set[str] = set()
    leaf = module.split(".")[-1] if module else Path(path).stem
    if "secretstr" in lower or "password" in lower or "api_key" in lower or "token" in lower and "auth" not in lower:
        tags.add("configuration")
    if leaf in {"config", "settings"}:
        tags.add("configuration")
    if any(marker in lower for marker in ("authenticate", "generatetoken", "access_token", "refresh", "authorization", "basic ")):
        tags.add("auth")
    if any(marker in lower for marker in ("ratelimiter", "rate_limit", "requests_per_minute", "120")):
        tags.add("rate_limit")
    if any(marker in lower for marker in ("semaphore", "concurrency", "max_connections", "10")):
        tags.add("concurrency")
    if any(marker in lower for marker in ("get_all_items", "pagination", "offset", "limit")):
        tags.add("pagination")
    if any(marker in lower for marker in ("httpx", "/api/fmc", "asyncclient")):
        tags.add("external_http")
    get_markers = ('.get(', "'get'", '"get"', "method == 'get'", 'method == "get"')
    if any(marker in lower for marker in get_markers) or "get_all_items" in lower:
        tags.add("read_only")
    if any(marker in lower for marker in ("fastmcp", "@mcp.resource", "@resource", "resource(", "@mcp.tool", "@tool", "tool(")):
        tags.add("mcp_server")
    if "fmc://" in lower or leaf == "resources":
        tags.add("resource_handlers")
    if "search_object" in lower or "deployment" in lower or leaf == "tools" or "tool_handlers" in symbol_text:
        tags.add("tool_handlers")
    if any(marker in lower for marker in ("set_client", "get_client", "_client")):
        tags.add("injection")
    if "def main" in lower or "__main__" in lower or Path(path).name in {"main.py", "__main__.py"}:
        tags.add("entrypoint")
    return sorted(tags)


def build_iteration_readiness(snapshot: Any, graph: Any) -> dict[str, Any]:
    components = list(_get(snapshot, "components", []))
    contracts = list(_get(snapshot, "contracts", []))
    nodes = _graph_nodes(graph)
    edges = _graph_edges(graph)
    root = Path(str(_get(graph, "project_root", ".")))
    node_by_id = {_get(node, "id", ""): node for node in nodes}
    component_profiles = _component_profiles(components, nodes, root, node_by_id)
    runtime_contracts = _runtime_contracts(components, contracts, nodes, edges, root, node_by_id)
    external_surfaces = _external_surfaces(components, nodes, root, node_by_id)
    product_invariants = _product_invariants(component_profiles, external_surfaces, nodes, root)
    quality_gates = _quality_gates(snapshot, nodes, root)
    priority_backlog = _priority_backlog(component_profiles, product_invariants, external_surfaces, runtime_contracts, quality_gates)
    open_questions = _open_questions(component_profiles, product_invariants, runtime_contracts, quality_gates, nodes)
    return {
        "summary": _summary(component_profiles, product_invariants, external_surfaces, quality_gates),
        "componentProfiles": component_profiles,
        "runtimeContracts": runtime_contracts,
        "externalSurfaces": external_surfaces,
        "productInvariants": product_invariants,
        "qualityGates": quality_gates,
        "priorityBacklog": priority_backlog,
        "openQuestions": open_questions,
    }


def snapshot_product_concerns(graph: Any, components: list[dict[str, Any]], contracts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    pseudo_snapshot = type("Snapshot", (), {"components": components, "contracts": contracts, "observable_checks": []})()
    readiness = build_iteration_readiness(pseudo_snapshot, graph)
    all_contract_ids = [str(contract.get("id", "")) for contract in contracts if contract.get("id")]
    concerns: list[dict[str, Any]] = []
    for invariant in readiness["productInvariants"]:
        concerns.append(
            {
                "id": "concern." + _slug(str(invariant["category"])),
                "category": str(invariant["category"]),
                "description": str(invariant["description"]),
                "component_ids": list(invariant.get("componentIds", [])),
                "contract_ids": all_contract_ids,
                "provenance_refs": list(invariant.get("provenanceRefs", [])),
                "triggered_by": [str(invariant.get("category", ""))],
            }
        )
    return concerns


def quality_observable_checks(graph: Any, *, component_ids: list[str], contract_ids: list[str], fallback_provenance: str) -> list[dict[str, Any]]:
    specs = detect_quality_gates(graph)
    checks: list[dict[str, Any]] = []
    for spec in specs:
        if not spec.get("safeToRunByDefault") or not spec.get("includedInAcceptance"):
            continue
        checks.append(
            {
                "id": spec["id"].replace("quality.", "check."),
                "description": spec["description"],
                "command": spec["command"],
                "component_ids": component_ids,
                "contract_ids": contract_ids,
                "provenance_refs": spec.get("provenanceRefs") or [fallback_provenance],
                "acceptance_command_id": spec["id"].replace("quality.", "local-"),
                "safe_to_run_by_default": bool(spec["safeToRunByDefault"]),
                "requires_network": False,
                "requires_paid_api": False,
            }
        )
    return checks


def detect_quality_gates(graph: Any) -> list[dict[str, Any]]:
    nodes = _graph_nodes(graph)
    root = Path(str(_get(graph, "project_root", ".")))
    test_prov = _first_provenance(next((node for node in nodes if _get(node, "kind") == "test_file"), None))
    fallback_prov = _first_provenance(nodes[0]) if nodes else ""
    pyproject_node = next((node for node in nodes if _get(node, "path") == "pyproject.toml"), None)
    pyproject_text = _read_path(root, "pyproject.toml")
    pyproject_prov = _first_provenance(pyproject_node) or fallback_prov
    gates = [
        {
            "id": "quality.pytest",
            "command": "uv run python -m pytest -q",
            "source": "snapshot_observable_check",
            "mode": "test",
            "description": "Run the local deterministic pytest suite.",
            "safeToRunByDefault": True,
            "includedInAcceptance": True,
            "provenanceRefs": [test_prov or fallback_prov],
        }
    ]
    parsed = _parse_pyproject(pyproject_text)
    package_path = _primary_python_package_path(nodes)
    if _has_tool(parsed, pyproject_text, "ruff"):
        gates.append(
            {
                "id": "quality.ruff",
                "command": "uv run ruff check .",
                "source": "detected_pyproject",
                "mode": "lint",
                "description": "Run configured Ruff lint checks.",
                "safeToRunByDefault": True,
                "includedInAcceptance": True,
                "provenanceRefs": [pyproject_prov],
            }
        )
    if _has_tool(parsed, pyproject_text, "mypy"):
        gates.append(
            {
                "id": "quality.mypy",
                "command": f"uv run mypy {package_path}",
                "source": "detected_pyproject_advisory",
                "mode": "typecheck",
                "description": "Mypy is configured, but this environment may not have the optional type-check dependency installed; keep it visible as an advisory quality gate unless the command is proven runnable.",
                "safeToRunByDefault": False,
                "includedInAcceptance": False,
                "provenanceRefs": [pyproject_prov],
            }
        )
    if _has_tool(parsed, pyproject_text, "pyright"):
        gates.append(
            {
                "id": "quality.pyright",
                "command": "uv run pyright",
                "source": "detected_pyproject",
                "mode": "typecheck",
                "description": "Run configured Pyright type checks.",
                "safeToRunByDefault": True,
                "includedInAcceptance": True,
                "provenanceRefs": [pyproject_prov],
            }
        )
    return gates


def source_profile_for_module(graph: Any, node: Any) -> dict[str, Any]:
    root = Path(str(_get(graph, "project_root", ".")))
    nodes = _graph_nodes(graph)
    path = str(_get(node, "path", "") or "")
    module = str(_get(node, "symbol", "") or _get(node, "label", ""))
    text = _read_path(root, path)
    key_symbols = _key_symbols_for_paths(nodes, {path})
    tags = detect_behavioral_tags(module, path, text, key_symbols)
    return {
        "module": module,
        "path": path,
        "text": text,
        "keySymbols": key_symbols,
        "behavioralTags": tags,
        "responsibilitySummary": component_responsibility_summary(module, text, key_symbols, tags),
        "provenanceRefs": [_first_provenance(node)],
    }


def _component_profiles(components: list[Any], nodes: list[Any], root: Path, node_by_id: dict[str, Any]) -> list[dict[str, Any]]:
    profiles: list[dict[str, Any]] = []
    for component in components:
        owned_node_ids = [str(item) for item in _get(component, "owned_node_ids", _get(component, "ownedNodeIds", []))]
        owned_nodes = [node_by_id[node_id] for node_id in owned_node_ids if node_id in node_by_id]
        paths = {str(_get(node, "path", "") or "") for node in owned_nodes if _get(node, "path", None)}
        text = "\n".join(_read_path(root, path) for path in sorted(paths))
        module = _component_module(component, owned_nodes)
        key_symbols = _key_symbols_for_paths(nodes, paths)
        tags = detect_behavioral_tags(module, next(iter(sorted(paths)), ""), text, key_symbols)
        risk_score = _risk_score(text, tags, key_symbols)
        profiles.append(
            {
                "componentId": str(_get(component, "id", "")),
                "ownedNodeIds": owned_node_ids,
                "responsibilitySummary": component_responsibility_summary(module, text, key_symbols, tags),
                "keySymbols": key_symbols,
                "behavioralTags": tags,
                "riskLevel": _risk_level(risk_score),
                "priorityRank": 0,
                "whyPriority": _why_priority(risk_score, tags, text),
                "provenanceRefs": _component_provenance(component, owned_nodes),
                "_riskScore": risk_score,
            }
        )
    profiles.sort(key=lambda item: (-int(item["_riskScore"]), str(item["componentId"])))
    for idx, profile in enumerate(profiles, start=1):
        profile["priorityRank"] = idx
        profile.pop("_riskScore", None)
    return profiles


def _runtime_contracts(components: list[Any], contracts: list[Any], nodes: list[Any], edges: list[Any], root: Path, node_by_id: dict[str, Any]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    component_by_leaf = _component_by_leaf(components, node_by_id)
    for contract in contracts:
        result.append(
            {
                "id": "runtime." + _slug(str(_get(contract, "id", "contract"))),
                "kind": "imports",
                "fromComponentId": str(_get(contract, "from_component_id", "")),
                "toComponentId": str(_get(contract, "to_component_id", "")),
                "description": str(_get(contract, "name", "Static import contract.")),
                "supportingNodeIds": [],
                "supportingEdgeIds": [str(item) for item in _get(contract, "supporting_edge_ids", [])],
                "provenanceRefs": [str(item) for item in _get(contract, "provenance_refs", [])],
            }
        )
    for component in components:
        component_id = str(_get(component, "id", ""))
        owned_nodes = [node_by_id[node_id] for node_id in _get(component, "owned_node_ids", []) if node_id in node_by_id]
        paths = {str(_get(node, "path", "") or "") for node in owned_nodes if _get(node, "path", None)}
        text = "\n".join(_read_path(root, path) for path in sorted(paths))
        lower = text.lower()
        provenance = _component_provenance(component, owned_nodes)
        node_ids = [str(_get(node, "id", "")) for node in owned_nodes]
        client_id = _find_leaf(component_by_leaf, "client")
        resources_id = _find_leaf(component_by_leaf, "resources")
        tools_id = _find_leaf(component_by_leaf, "tools")
        if "fmcclient(" in lower and client_id and client_id != component_id:
            result.append(_runtime_record("constructs", component_id, client_id, "Constructs the client during runtime setup/lifespan.", node_ids, provenance))
        if "set_client(" in lower and resources_id and resources_id != component_id:
            result.append(_runtime_record("injects", component_id, resources_id, "Injects the runtime client into the shared resources module.", node_ids, provenance))
        if "get_client(" in lower and resources_id and resources_id != component_id:
            result.append(_runtime_record("delegates_to", component_id, resources_id, "Obtains the injected client through the resources access point.", node_ids, provenance))
        if re.search(r"\btools\.", text) and tools_id and tools_id != component_id:
            result.append(_runtime_record("delegates_to", component_id, tools_id, "Delegates registered MCP tool handlers to the tools module.", node_ids, provenance))
        if "fmc://" in lower or "@mcp.resource" in lower or "@resource" in lower:
            result.append(_runtime_record("registers_resource", component_id, "", "Registers public MCP resource handlers.", node_ids, provenance))
        if "@mcp.tool" in lower or "@tool" in lower or ".tool(" in lower:
            result.append(_runtime_record("registers_tool", component_id, "", "Registers public MCP tool handlers.", node_ids, provenance))
        if "transport" in lower and ("stdio" in lower or "sse" in lower or "http" in lower):
            result.append(_runtime_record("exposes_runtime_mode", component_id, "", "Exposes stdio and/or HTTP/SSE runtime mode selection.", node_ids, provenance))
    return _dedupe_records(result)


def _external_surfaces(components: list[Any], nodes: list[Any], root: Path, node_by_id: dict[str, Any]) -> list[dict[str, Any]]:
    surfaces: list[dict[str, Any]] = []
    owner_by_path: dict[str, list[str]] = {}
    provenance_by_path: dict[str, list[str]] = {}
    for component in components:
        cid = str(_get(component, "id", ""))
        owned = [node_by_id[node_id] for node_id in _get(component, "owned_node_ids", []) if node_id in node_by_id]
        for node in owned:
            path = str(_get(node, "path", "") or "")
            if not path:
                continue
            owner_by_path.setdefault(path, []).append(cid)
            provenance_by_path.setdefault(path, []).extend(_provenance_refs(node))
    for path, owner_ids in sorted(owner_by_path.items()):
        text = _read_path(root, path)
        prov = sorted(set(provenance_by_path.get(path, [])))
        for uri in sorted(set(re.findall(r"fmc://[A-Za-z0-9_./:-]+", text))):
            surfaces.append(_surface("mcp_resource", uri, owner_ids, f"Public MCP resource URI `{uri}`.", prov))
        for tool_name in _decorated_tool_names(text):
            surfaces.append(_surface("mcp_tool", tool_name, owner_ids, f"Public MCP tool `{tool_name}`.", prov))
        for endpoint in sorted(set(re.findall(r"/api/fmc_[A-Za-z0-9_./{}?=&-]+", text))):
            surfaces.append(_surface("http_endpoint_family", endpoint, owner_ids, f"FMC REST endpoint family `{endpoint}`.", prov))
        if "httpx" in text:
            surfaces.append(_surface("dependency", "httpx", owner_ids, "HTTP client dependency used for FMC REST access.", prov))
        if "FastMCP" in text or "fastmcp" in text.lower():
            surfaces.append(_surface("dependency", "FastMCP", owner_ids, "MCP server framework dependency.", prov))
        if "transport" in text and ("stdio" in text or "sse" in text or "http" in text.lower()):
            surfaces.append(_surface("runtime_mode", "stdio/http-sse", owner_ids, "Runtime transport mode selection.", prov))
        for env_name in _environment_setting_names(text):
            surfaces.append(_surface("environment_variable", env_name, owner_ids, f"Environment/settings boundary `{env_name}`.", prov))
    pyproject = _read_path(root, "pyproject.toml")
    pyproject_node = next((node for node in nodes if _get(node, "path") == "pyproject.toml"), None)
    pyproject_prov = _provenance_refs(pyproject_node)
    for script in _console_scripts(pyproject):
        owner_ids = _owners_for_script(script["target"], components, node_by_id)
        surfaces.append(_surface("console_script", script["name"], owner_ids, f"Console script `{script['name']}` -> `{script['target']}`.", pyproject_prov))
    return _dedupe_records(surfaces)


def _product_invariants(component_profiles: list[dict[str, Any]], external_surfaces: list[dict[str, Any]], nodes: list[Any], root: Path) -> list[dict[str, Any]]:
    invariants: list[dict[str, Any]] = []
    profiles_by_tag: dict[str, list[dict[str, Any]]] = {}
    for profile in component_profiles:
        for tag in profile["behavioralTags"]:
            profiles_by_tag.setdefault(str(tag), []).append(profile)
    if profiles_by_tag.get("read_only") or any(surface["surfaceType"] == "http_endpoint_family" for surface in external_surfaces):
        profiles = profiles_by_tag.get("read_only") or profiles_by_tag.get("external_http", [])
        invariants.append(
            _invariant(
                "read_only_external_operations",
                "FMC domain operations are modeled as read-oriented external calls; auth-token POSTs are separate from domain mutation behavior.",
                profiles,
                external_surfaces,
                "modeled",
                {"http_endpoint_family", "mcp_resource", "mcp_tool"},
            )
        )
    if profiles_by_tag.get("configuration") or _project_contains(root, "SecretStr"):
        invariants.append(
            _invariant(
                "secret_safety",
                "Secret-bearing settings and credentials must remain redacted and must not be logged or exposed in model artifacts.",
                profiles_by_tag.get("configuration", []),
                external_surfaces,
                "modeled",
                {"environment_variable"},
            )
        )
    if profiles_by_tag.get("rate_limit"):
        rate_limit_value = _source_setting_value(root, "fmc_rate_limit")
        description = "Rate limiting behavior is a product invariant for external FMC API access."
        if rate_limit_value:
            description += f" Source settings define {rate_limit_value} requests per minute."
        invariants.append(_invariant("rate_limit", description, profiles_by_tag["rate_limit"], external_surfaces, "modeled", {"http_endpoint_family", "environment_variable"}))
    if profiles_by_tag.get("concurrency"):
        max_connections = _source_setting_value(root, "fmc_max_connections")
        description = "Concurrent external FMC requests are bounded by source-modeled back-pressure."
        if max_connections:
            description += f" Source settings define {max_connections} concurrent connections."
        invariants.append(_invariant("concurrency_limit", description, profiles_by_tag["concurrency"], external_surfaces, "modeled", {"http_endpoint_family", "environment_variable"}))
    if any(str(_get(node, "path", "")).endswith("test_live.py") for node in nodes):
        invariants.append(_invariant("live_test_boundary", "Credentialed live tests are present or implied and must remain outside default local acceptance unless explicitly enabled.", component_profiles, external_surfaces, "gap", set()))
    if any(surface["surfaceType"] in {"mcp_resource", "mcp_tool"} for surface in external_surfaces):
        invariants.append(_invariant("public_mcp_contract", "Public MCP resources and tools are externally meaningful contract surfaces.", component_profiles, external_surfaces, "modeled", {"mcp_resource", "mcp_tool"}))
    return _dedupe_records(invariants)


def _quality_gates(snapshot: Any, nodes: list[Any], root: Path) -> list[dict[str, Any]]:
    gates: list[dict[str, Any]] = []
    for check in _get(snapshot, "observable_checks", []):
        command = str(_get(check, "command", ""))
        mode = "test"
        source = "snapshot_observable_check"
        if "ruff" in command:
            mode = "lint"
            source = "detected_pyproject"
        elif "mypy" in command or "pyright" in command:
            mode = "typecheck"
            source = "detected_pyproject"
        gates.append(
            {
                "id": str(_get(check, "id", "")) or "quality.check",
                "command": command,
                "source": source,
                "mode": mode,
                "safeToRunByDefault": bool(_get(check, "safe_to_run_by_default", True)),
                "includedInAcceptance": bool(_get(check, "acceptance_command_id", None)),
                "provenanceRefs": [str(item) for item in _get(check, "provenance_refs", [])],
            }
        )
    known_commands = {gate["command"] for gate in gates}
    for spec in detect_quality_gates(type("Graph", (), {"nodes": nodes, "project_root": str(root)})()):
        if spec["command"] not in known_commands:
            gates.append(
                {
                    "id": spec["id"],
                    "command": spec["command"],
                    "source": spec["source"],
                    "mode": spec["mode"],
                    "safeToRunByDefault": spec["safeToRunByDefault"],
                    "includedInAcceptance": spec["includedInAcceptance"],
                    "provenanceRefs": spec["provenanceRefs"],
                }
            )
    return _dedupe_records(gates)


def _priority_backlog(profiles: list[dict[str, Any]], invariants: list[dict[str, Any]], surfaces: list[dict[str, Any]], runtime_contracts: list[dict[str, Any]], quality_gates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    backlog: list[dict[str, Any]] = []
    inv_ids = {item["category"]: item["id"] for item in invariants}
    surface_ids_by_type = _surface_ids_by_type(surfaces)
    high_profiles = [profile for profile in profiles if profile["riskLevel"] == "high"]
    high_component_ids = [profile["componentId"] for profile in high_profiles]
    if "read_only_external_operations" in inv_ids:
        related_surfaces = sorted(surface_ids_by_type.get("http_endpoint_family", []) + surface_ids_by_type.get("mcp_tool", []))
        invariant_ids = [inv_ids["read_only_external_operations"]]
        backlog.append(
            _backlog(
                1,
                "Verify read-only external behavior",
                "Add or run checks proving domain FMC operations stay read-only while auth token POST remains allowed.",
                high_component_ids,
                invariant_ids,
                related_surfaces,
                "Static scan or mocked client test for HTTP methods.",
                _related_provenance(profiles, invariants, surfaces, high_component_ids, invariant_ids, related_surfaces),
            )
        )
    if any(contract["kind"] in {"injects", "delegates_to"} for contract in runtime_contracts):
        component_ids = sorted({str(contract.get("fromComponentId", "")) for contract in runtime_contracts if contract.get("fromComponentId")})
        related_surfaces = sorted(surface_ids_by_type.get("mcp_resource", []) + surface_ids_by_type.get("mcp_tool", []) + surface_ids_by_type.get("runtime_mode", []))
        backlog.append(
            _backlog(
                2,
                "Verify server/resources/tools wiring",
                "Exercise runtime construction, client injection, and delegation through resource/tool handlers.",
                component_ids,
                [],
                related_surfaces,
                "Mocked server lifespan/resource/tool wiring test.",
                _related_provenance(profiles, invariants, surfaces, component_ids, [], related_surfaces),
            )
        )
    if any(gate["mode"] in {"lint", "typecheck"} for gate in quality_gates):
        component_ids = [profile["componentId"] for profile in profiles]
        gate_refs = sorted({ref for gate in quality_gates for ref in gate.get("provenanceRefs", [])})
        backlog.append(
            _backlog(
                3,
                "Run configured lint and type checks",
                "Configured quality commands are now visible and should be part of improvement verification.",
                component_ids,
                [],
                [],
                "Run ruff and mypy/pyright commands reported in qualityGates, respecting advisory flags.",
                gate_refs or _related_provenance(profiles, invariants, surfaces, component_ids, [], []),
            )
        )
    if high_profiles:
        client_profiles = [profile for profile in high_profiles if "client" in profile["componentId"]]
        chosen = client_profiles or high_profiles
        component_ids = [profile["componentId"] for profile in chosen]
        backlog.append(
            _backlog(
                4,
                "Document or split high-risk client responsibilities",
                "High-risk stateful client code combines auth, retry, rate limiting, pagination, and endpoint wrappers.",
                component_ids,
                [],
                [],
                "Targeted unit tests for each client sub-responsibility.",
                _related_provenance(profiles, invariants, surfaces, component_ids, [], []),
            )
        )
    if any("test_connection" in profile["keySymbols"] for profile in profiles):
        component_ids = [profile["componentId"] for profile in profiles if "test_connection" in profile["keySymbols"]]
        backlog.append(
            _backlog(
                5,
                "Review production `test_connection` naming",
                "A production method with a `test_` prefix can confuse humans and tools even when pytest collection is currently scoped.",
                component_ids,
                [],
                [],
                "Decide whether to rename or document the method.",
                _related_provenance(profiles, invariants, surfaces, component_ids, [], []),
            )
        )
    return sorted(_dedupe_records(backlog), key=lambda item: (int(item["rank"]), str(item["id"])))


def _open_questions(profiles: list[dict[str, Any]], invariants: list[dict[str, Any]], runtime_contracts: list[dict[str, Any]], quality_gates: list[dict[str, Any]], nodes: list[Any]) -> list[dict[str, Any]]:
    questions: list[dict[str, Any]] = []
    if any(str(_get(node, "path", "")).endswith("test_live.py") for node in nodes):
        questions.append(_question("live-test-boundary", "Is `test_live.py` intentionally manual-only, or should it become a credential-gated live smoke profile?", "live test file exists without a safe default live acceptance gate"))
    if any(profile["riskLevel"] == "high" and "client" in profile["componentId"] for profile in profiles):
        questions.append(_question("client-boundary", "Should the stateful client remain one component, or should auth, retry, rate limiting, pagination, and endpoint wrappers become helpers/subcomponents?", "high-risk client profile has multiple behavioral tags"))
    if any(gate["mode"] in {"lint", "typecheck"} for gate in quality_gates):
        questions.append(_question("quality-default", "Should default acceptance become pytest plus configured lint/type checks, or should lint/typecheck remain advisory?", "configured lint/typecheck commands detected"))
    if any("test_connection" in profile["keySymbols"] for profile in profiles):
        questions.append(_question("test-connection-name", "Should production `test_connection` keep its `test_` prefix, or be renamed/documented to avoid tool and human confusion?", "production source exposes a `test_connection` symbol"))
    if any(contract["kind"] == "delegates_to" and "tools" in str(contract.get("toComponentId", "")) for contract in runtime_contracts):
        questions.append(_question("server-tools-indirection", "Is the server wrapper around tools-module functions intentional registration indirection, or should it be consolidated?", "server-to-tools delegation detected"))
    return sorted(_dedupe_records(questions), key=lambda item: str(item["id"]))


def _summary(profiles: list[dict[str, Any]], invariants: list[dict[str, Any]], surfaces: list[dict[str, Any]], quality_gates: list[dict[str, Any]]) -> str:
    high = [profile["componentId"] for profile in profiles if profile["riskLevel"] == "high"]
    return (
        f"Iteration guidance covers {len(profiles)} components, {len(invariants)} product invariants, "
        f"{len(surfaces)} external surfaces, and {len(quality_gates)} local quality gates. "
        f"Highest-risk components: {', '.join(high[:3]) if high else 'none'}."
    )


def _runtime_record(kind: str, from_id: str, to_id: str, description: str, node_ids: list[str], provenance: list[str]) -> dict[str, Any]:
    target = f"-{to_id}" if to_id else ""
    return {
        "id": "runtime." + _slug(f"{kind}-{from_id}{target}"),
        "kind": kind,
        "fromComponentId": from_id,
        "toComponentId": to_id,
        "description": description,
        "supportingNodeIds": sorted(set(node_ids)),
        "supportingEdgeIds": [],
        "provenanceRefs": sorted(set(provenance)),
    }


def _surface(surface_type: str, name: str, owner_ids: list[str], description: str, provenance: list[str]) -> dict[str, Any]:
    return {
        "id": "surface." + _slug(f"{surface_type}-{name}"),
        "surfaceType": surface_type,
        "name": name,
        "ownerComponentIds": sorted(set(owner_ids)),
        "description": description,
        "provenanceRefs": sorted(set(provenance)),
    }


def _invariant(
    category: str,
    description: str,
    profiles: list[dict[str, Any]],
    surfaces: list[dict[str, Any]],
    enforcement: str,
    surface_types: set[str],
) -> dict[str, Any]:
    component_ids = sorted({profile["componentId"] for profile in profiles})
    surface_ids = sorted({surface["id"] for surface in surfaces if surface["surfaceType"] in surface_types})
    provenance = sorted({ref for profile in profiles for ref in profile.get("provenanceRefs", [])})
    if not provenance:
        provenance = sorted({ref for surface in surfaces for ref in surface.get("provenanceRefs", [])})
    return {
        "id": "invariant." + _slug(category),
        "category": category,
        "description": description,
        "componentIds": component_ids,
        "externalSurfaceIds": surface_ids,
        "enforcement": enforcement,
        "provenanceRefs": provenance,
    }


def _backlog(rank: int, title: str, rationale: str, component_ids: list[str], invariant_ids: list[str], surface_ids: list[str], suggested_verification: str, provenance_refs: list[str]) -> dict[str, Any]:
    return {
        "id": "backlog." + _slug(title),
        "rank": rank,
        "title": title,
        "rationale": rationale,
        "componentIds": sorted(set(component_ids)),
        "relatedInvariantIds": sorted(set(invariant_ids)),
        "relatedSurfaceIds": sorted(set(surface_ids)),
        "suggestedVerification": suggested_verification,
        "provenanceRefs": sorted({ref for ref in provenance_refs if ref}),
    }


def _surface_ids_by_type(surfaces: list[dict[str, Any]]) -> dict[str, list[str]]:
    result: dict[str, list[str]] = {}
    for surface in surfaces:
        result.setdefault(str(surface.get("surfaceType", "")), []).append(str(surface.get("id", "")))
    return {key: sorted({value for value in values if value}) for key, values in result.items()}


def _related_provenance(
    profiles: list[dict[str, Any]],
    invariants: list[dict[str, Any]],
    surfaces: list[dict[str, Any]],
    component_ids: list[str],
    invariant_ids: list[str],
    surface_ids: list[str],
) -> list[str]:
    component_set = set(component_ids)
    invariant_set = set(invariant_ids)
    surface_set = set(surface_ids)
    refs: set[str] = set()
    for profile in profiles:
        if profile.get("componentId") in component_set:
            refs.update(str(ref) for ref in profile.get("provenanceRefs", []) if ref)
    for invariant in invariants:
        if invariant.get("id") in invariant_set:
            refs.update(str(ref) for ref in invariant.get("provenanceRefs", []) if ref)
    for surface in surfaces:
        if surface.get("id") in surface_set:
            refs.update(str(ref) for ref in surface.get("provenanceRefs", []) if ref)
    return sorted(refs)


def _question(question_id: str, question: str, trigger: str) -> dict[str, Any]:
    return {"id": "question." + _slug(question_id), "question": question, "trigger": trigger}


def _component_module(component: Any, owned_nodes: list[Any]) -> str:
    for node in owned_nodes:
        symbol = str(_get(node, "symbol", "") or "")
        if symbol:
            return symbol.removesuffix(".__init__")
    component_id = str(_get(component, "id", ""))
    return component_id.removeprefix("component.").replace("-", ".")


def _component_provenance(component: Any, owned_nodes: list[Any]) -> list[str]:
    refs = [str(item) for item in _get(component, "provenance_refs", [])]
    for node in owned_nodes:
        refs.extend(_provenance_refs(node))
    return sorted({ref for ref in refs if ref})


def _key_symbols_for_paths(nodes: list[Any], paths: set[str]) -> list[str]:
    symbols: list[str] = []
    for node in nodes:
        if str(_get(node, "path", "") or "") not in paths:
            continue
        if str(_get(node, "kind", "")) not in {"python_class", "python_function", "javascript_function"}:
            continue
        symbol = str(_get(node, "symbol", "") or _get(node, "label", ""))
        if symbol:
            symbols.append(symbol.split(".")[-1])
    return sorted(set(symbols))


def _risk_score(text: str, tags: list[str], key_symbols: list[str]) -> int:
    line_count = len(text.splitlines())
    score = line_count // 40 + len(key_symbols) // 4
    for tag in tags:
        score += {
            "auth": 4,
            "rate_limit": 4,
            "concurrency": 4,
            "pagination": 3,
            "external_http": 3,
            "read_only": 3,
            "mcp_server": 2,
            "resource_handlers": 2,
            "tool_handlers": 2,
            "configuration": 2,
            "injection": 2,
            "entrypoint": -1,
        }.get(tag, 1)
    return max(score, 0)


def _risk_level(score: int) -> str:
    if score >= 9:
        return "high"
    if score >= 4:
        return "medium"
    return "low"


def _why_priority(score: int, tags: list[str], text: str) -> str:
    if tags:
        return f"Risk score {score} from source tags: {', '.join(tags)}."
    return f"Risk score {score} from {len(text.splitlines())} source lines and symbol coverage."


def _component_by_leaf(components: list[Any], node_by_id: dict[str, Any]) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for component in components:
        cid = str(_get(component, "id", ""))
        for node_id in _get(component, "owned_node_ids", []):
            node = node_by_id.get(str(node_id))
            symbol = str(_get(node, "symbol", "") or "")
            if symbol:
                mapping[symbol.split(".")[-1]] = cid
        slug_leaf = cid.removeprefix("component.").split("-")[-1]
        mapping.setdefault(slug_leaf, cid)
    return mapping


def _find_leaf(mapping: dict[str, str], leaf: str) -> str:
    return mapping.get(leaf, "")


def _decorated_tool_names(text: str) -> list[str]:
    names: list[str] = []
    lines = text.splitlines()
    for idx, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("@tool") or stripped.startswith("@mcp.tool") or ".tool(" in stripped:
            for later in lines[idx + 1 : idx + 5]:
                match = re.search(r"(?:async\s+def|def)\s+([A-Za-z_][A-Za-z0-9_]*)", later)
                if match:
                    names.append(match.group(1))
                    break
    for fallback in ("search_object_by_ip", "check_deployment_status"):
        if re.search(rf"\b{fallback}\b", text):
            names.append(fallback)
    return sorted(set(names))


def _console_scripts(pyproject_text: str) -> list[dict[str, str]]:
    scripts: list[dict[str, str]] = []
    in_scripts = False
    for line in pyproject_text.splitlines():
        stripped = line.strip()
        if stripped.startswith("["):
            in_scripts = stripped == "[project.scripts]"
            continue
        if not in_scripts or not stripped or stripped.startswith("#"):
            continue
        match = re.match(r"([A-Za-z0-9_.-]+)\s*=\s*['\"]([^'\"]+)['\"]", stripped)
        if match:
            scripts.append({"name": match.group(1), "target": match.group(2)})
    return scripts


def _owners_for_script(target: str, components: list[Any], node_by_id: dict[str, Any]) -> list[str]:
    target_module = target.split(":", 1)[0]
    owners: list[str] = []
    for component in components:
        for node_id in _get(component, "owned_node_ids", []):
            node = node_by_id.get(str(node_id))
            symbol = str(_get(node, "symbol", "") or "")
            if symbol == target_module or target_module.startswith(symbol + ".") or symbol.startswith(target_module + "."):
                owners.append(str(_get(component, "id", "")))
    return sorted(set(owners))


def _primary_python_package_path(nodes: list[Any]) -> str:
    candidates = sorted(
        str(_get(node, "path", "") or "")
        for node in nodes
        if _get(node, "kind") == "python_module" and _get(node, "path") and not str(_get(node, "path", "")).startswith("tests/")
    )
    for path in candidates:
        parts = Path(path).parts
        if len(parts) >= 3 and parts[0] == "src":
            return "/".join(parts[:2])
    for path in candidates:
        parts = Path(path).parts
        if len(parts) >= 2:
            return parts[0]
    return "."


def _environment_setting_names(text: str) -> list[str]:
    names: set[str] = set()
    for match in re.finditer(r"^\s*(fmc_[A-Za-z0-9_]+)\s*:\s*", text, flags=re.MULTILINE):
        names.add(match.group(1).upper())
    for match in re.finditer(r"\b(FMC_[A-Z0-9_]+|[A-Z][A-Z0-9_]*(?:TOKEN|PASSWORD|USERNAME|HOST|API_KEY)[A-Z0-9_]*)\b", text):
        names.add(match.group(1))
    return sorted(names)


def _source_setting_value(root: Path, field_name: str) -> str:
    pattern = re.compile(rf"^\s*{re.escape(field_name)}\s*:\s*[^=\n]+?=\s*([^#\n]+)", flags=re.MULTILINE)
    for path in root.rglob("*.py"):
        if any(part in {".git", ".venv", "__pycache__"} for part in path.parts):
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        match = pattern.search(text)
        if match:
            return match.group(1).strip().strip('"\'')
    return ""


def _parse_pyproject(text: str) -> dict[str, Any]:
    if not text.strip():
        return {}
    try:
        parsed = tomllib.loads(text)
    except tomllib.TOMLDecodeError:
        return {}
    return parsed if isinstance(parsed, dict) else {}


def _has_tool(parsed: dict[str, Any], text: str, tool: str) -> bool:
    tools = parsed.get("tool", {}) if isinstance(parsed.get("tool", {}), dict) else {}
    if tool in tools:
        return True
    lower = text.lower()
    return f"{tool}" in lower and ("dependency" in lower or "dev" in lower or f"tool.{tool}" in lower)


def _project_contains(root: Path, needle: str) -> bool:
    for path in root.rglob("*.py"):
        if any(part in {".git", ".venv", "__pycache__"} for part in path.parts):
            continue
        try:
            if needle in path.read_text(encoding="utf-8", errors="replace"):
                return True
        except OSError:
            continue
    return False


def _graph_nodes(graph: Any) -> list[Any]:
    return list(_get(graph, "nodes", []))


def _graph_edges(graph: Any) -> list[Any]:
    return list(_get(graph, "edges", []))


def _get(obj: Any, name: str, default: Any = None) -> Any:
    if isinstance(obj, dict):
        return obj.get(name, default)
    return getattr(obj, name, default)


def _provenance_refs(obj: Any) -> list[str]:
    if obj is None:
        return []
    refs = _get(obj, "provenance_refs", [])
    result: list[str] = []
    for ref in refs:
        if isinstance(ref, str):
            result.append(ref)
        else:
            result.append(str(_get(ref, "id", "")))
    return [ref for ref in result if ref]


def _first_provenance(obj: Any) -> str:
    refs = _provenance_refs(obj)
    return refs[0] if refs else ""


def _read_path(root: Path, rel_path: str) -> str:
    if not rel_path:
        return ""
    try:
        path = root / rel_path
        if path.exists() and path.is_file():
            return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""
    return ""


def _stable_nonempty(values: list[str]) -> list[str]:
    return sorted({value for value in values if value})


def _phrase_if(condition: bool, text: str) -> str:
    return text if condition else ""


def _join_sentence(*parts: str) -> str:
    clean = [part for part in parts if part]
    if not clean:
        return "Represent source-backed behavior."
    sentence = ", ".join(clean)
    return sentence[0].upper() + sentence[1:] + "."


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")[:80] or "item"


def _dedupe_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    result: list[dict[str, Any]] = []
    for record in records:
        key = str(record.get("id") or (record.get("surfaceType"), record.get("name"), record.get("kind"), record.get("fromComponentId"), record.get("toComponentId")))
        if key in seen:
            continue
        seen.add(key)
        result.append(record)
    return sorted(result, key=lambda item: str(item.get("id", "")))
