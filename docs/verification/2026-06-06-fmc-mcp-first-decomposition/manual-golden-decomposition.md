# FMC-MCP first real decomposition: manual golden checklist

Date: 2026-06-06
Target repo: `/home/leonb/projects/fmc-mcp`
Target git HEAD: `00a632ac950a8c411f8d8ac90197e28191f58619`
Build Arena HEAD at start: `e06cff0927220acdd782e6b988a0c3787cf4c99c`
Mode: durable, non-live, first real project decomposition review. No live FMC/API calls and no paid/live LLM calls are part of acceptance.

## Source-truth summary

FMC-MCP is a read-only Model Context Protocol server for Cisco Firepower Management Center 7.4.x. The README states the purpose as read-only MCP access to FMC configuration, object search, and deployment status (README.md:1-12). The design spec defines the MVP scope as read-only, with success criteria around authentication longevity, 120 req/min plus 10 concurrent connection limits, >1,000 object pagination, and resources for devices/objects (fmc-mcp-spec.md:7-15).

The implementation is a compact Python package under `src/fmc_mcp` with seven primary modules:

- `fmc_mcp.config` (`src/fmc_mcp/config.py`): pydantic settings from env/.env, secret-bearing password field, SSL/default timeout/rate limit/concurrency config, and redacted configuration logging (config.py:12-57).
- `fmc_mcp.client` (`src/fmc_mcp/client.py`): async FMC transport/session manager. It owns token-bucket rate limiting, 10-connection semaphore/limits, Basic Auth token generation, 401 refresh/re-auth, 429 retry-after behavior, JSON helpers, transparent pagination, and read-only FMC endpoint wrappers (client.py:16-371).
- `fmc_mcp.resources` (`src/fmc_mcp/resources.py`): MCP resource handlers that use the configured FMC client to return JSON strings for system info, devices, network objects, and deployment status summaries (resources.py:16-120).
- `fmc_mcp.tools` (`src/fmc_mcp/tools.py`): MCP tool handlers. `search_object_by_ip` validates IP input and searches network/host objects; `check_deployment_status` filters deployment state and summarizes sync/pending state (tools.py:12-134).
- `fmc_mcp.server` (`src/fmc_mcp/server.py`): FastMCP runtime/lifecycle. It creates the FMC client at startup, injects it into resources, registers the four resources and two tools, and selects stdio vs HTTP/SSE transport from environment (server.py:26-140).
- `fmc_mcp.__init__` (`src/fmc_mcp/__init__.py`): public package export for `mcp`, `main`, and version (init.py:1-7).
- `fmc_mcp.__main__` (`src/fmc_mcp/__main__.py`): module entry point that calls `server.main()` (__main__.py:1-6).

Tests provide local, mocked acceptance coverage for the rate limiter, client auth/domain/request behavior, resources, tools, and fixtures. `uv run python -m pytest -q` returned `19 passed in 0.04s` during preflight.

## Golden responsibility decomposition

The decomposition should prefer semantic/runtime responsibilities over directories or file buckets. A passing Project Model v1 for this repo should identify at least these responsibility-bearing components or an equivalent semantic grouping:

1. Configuration and secret-safe settings boundary
   - Owns: `fmc_mcp.config`.
   - Responsibility: validate environment/.env settings, carry FMC credentials via `SecretStr`, expose runtime defaults for SSL, timeout, rate limit, and concurrency, and log configuration without secrets.
   - Evidence: config.py:12-57; README.md:55-83; README.md:203-208.

2. FMC API transport/session/read-only data boundary
   - Owns: `fmc_mcp.client`.
   - Responsibility: keep a safe read-only FMC API session alive while enforcing rate and connection limits, handling token refresh/re-auth, retrying rate limits, paginating large reads, and exposing GET-only helper methods for system, domain, devices, objects, hosts, and deployable devices.
   - Evidence: client.py:16-371; fmc-mcp-spec.md:19-74; fmc-mcp-spec.md:92-104; README.md:187-201.

3. MCP resource projection boundary
   - Owns: `fmc_mcp.resources`.
   - Responsibility: convert FMC client calls into JSON resource payloads for `fmc://system/info`, `fmc://devices/list`, `fmc://objects/network`, and `fmc://deployment/status`.
   - Evidence: resources.py:16-120; server.py:65-87; README.md:14-22.

4. MCP tool/query boundary
   - Owns: `fmc_mcp.tools`.
   - Responsibility: provide read-only query actions, including IP-object lookup and deployment status filtering, using the resource/client access boundary.
   - Evidence: tools.py:12-134; server.py:90-115; README.md:23-29.

5. MCP runtime and entrypoint boundary
   - Owns: `fmc_mcp.server`, `fmc_mcp.__init__`, `fmc_mcp.__main__`.
   - Responsibility: create and manage FastMCP runtime lifecycle, instantiate/connect/close `FMCClient`, inject it into resources, register resource/tool handlers, and choose stdio or HTTP/SSE transport.
   - Evidence: server.py:26-140; init.py:1-7; __main__.py:1-6; README.md:87-126.

6. Local verification harness / observable checks
   - Owns primarily tests, not production runtime components.
   - Responsibility: verify client/session behavior, mocked FMC responses, resource JSON projection, and tool behavior without live FMC access.
   - Evidence: tests/test_client.py:10-162; tests/test_resources.py:13-153; tests/conftest.py:12-158.

## Expected component contracts

A good model should cover deterministic import/runtime contracts among owned production components:

- Runtime -> Configuration: `fmc_mcp.server` imports/uses `get_settings`; `fmc_mcp.client` imports/uses `FMCSettings` and `get_settings`.
- Runtime -> Client: `fmc_mcp.server` constructs, connects, stores, and closes `FMCClient` during FastMCP lifespan.
- Runtime -> Resources: `fmc_mcp.server` calls `resources.set_client` and registers resource functions.
- Runtime -> Tools: `fmc_mcp.server` registers tool handlers that delegate to `fmc_mcp.tools`.
- Resources -> Client: `fmc_mcp.resources` stores and retrieves the singleton-like `FMCClient` and calls its read-only methods.
- Tools -> Resources/Client access: `fmc_mcp.tools` imports `get_client` from resources and uses the returned client to fetch host/network/deployment data.
- Entrypoints -> Runtime: `fmc_mcp.__init__` exports `server.main`/`server.mcp`; `fmc_mcp.__main__` calls `server.main`.

## Expected observable checks

- Required local acceptance check: `uv run pytest -q` or `uv run python -m pytest -q` in `/home/leonb/projects/fmc-mcp`.
- The check must not require FMC credentials, network access, live API calls, or paid LLM/API calls.
- Live integration in `tests/test_live.py` is informative only and must not be part of default acceptance for this decomposition.

## Expected cross-cutting concerns

- Anti-fabrication/provenance: every component, contract, and check must trace to graph/source evidence.
- Determinism: snapshot artifacts must be reproducible from git/filesystem truth.
- Read-only safety: FMC-MCP claims read-only behavior; accepted contracts/checks should not require POST/PUT/DELETE against FMC except authentication token endpoints already embedded in client lifecycle.
- Secret handling: credentials are env/.env settings and `SecretStr`; reports must not record real credential values.
- No live/paid acceptance: default checks must be mocked/local.
- Rate/concurrency resilience: the client must preserve the 120 req/min and 10-connection constraints.

## Review criteria for generated Project Model v1

Accept only if:

1. Primary production modules are component-owned or explicitly covered by a justified verification gap.
2. Owned inter-component import edges are covered by contracts or by explicit, reviewed gaps.
3. Contracts are semantically meaningful and backed by deterministic graph edges/provenance.
4. Checks are local, safe, and allowlisted.
5. Generated output does not treat adjacent files/directories as polished final components.
6. Gate failures, if any, are classified as decomposer defects, gate defects, or accepted review-only gaps with evidence.
