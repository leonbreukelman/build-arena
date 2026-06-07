# Hermes independent review — FMC-MCP Project Model v1 usability

Reviewer: Hermes Agent
Date: 2026-06-07
Subject artifact: `snapshot-e75be06540a3883d/project-model-v1.json`

## 1. Overall verdict

`usable_with_gaps` — 6.5/10.

The model is a good durable navigation skeleton: it identifies the six production modules, all currently recognized gate-covered import contracts, the safe local test command, clean provenance, and a usable verification entry point. It is enough for a strong model to orient quickly and avoid inventing the repo shape.

It is not yet enough to let a strong model confidently decide what to improve next without reading the source. The snapshot layer loses the semantic content that matters most in FMC-MCP: read-only safety, auth/token lifecycle, rate limiting, connection back-pressure, pagination, secret handling, MCP public surface, and live-vs-mocked boundary.

## 2. What works well for future iteration

- The model is provenance-backed and pinned to the clean FMC-MCP git state.
- Component ownership is complete for production package modules: `server`, `config`, `resources`, `client`, `tools`, and `__main__`.
- Tests are correctly treated as observable checks rather than production components.
- The local check is the command that actually runs in the repo: `uv run python -m pytest -q`.
- The model now has enough contracts to pass the Build Arena edge-coverage gate.
- The raw graph has rich function-level data that a reviewing model can mine if it is told not to stop at the snapshot layer.

## 3. What the model missed or underrepresented about FMC-MCP

- Component responsibilities are generic templates. For example, `component.fmc-mcp-client` says it owns the responsibility represented by `fmc_mcp.client`, but the source shows this module actually owns `RateLimiter`, auth, refresh/re-auth, request limiting, 429 retry handling, pagination, and read-only endpoint wrappers.
- Project-level invariants are absent from the snapshot concerns. The concerns describe Build Arena process integrity, not FMC-MCP safety requirements. Missing first-class invariants include read-only FMC behavior, secret-safe logging, default no-live acceptance, rate/concurrency limits, and pagination scale.
- Runtime contracts are weaker than static import contracts. `server.py` creates `FMCClient`, injects it through `resources.set_client`, registers four MCP resources, and wraps two MCP tools. The snapshot mostly records imports, not lifecycle/handler/data-flow semantics.
- The `server -> tools` relationship is not promoted as a contract, even though `server.py` imports `tools` and calls `tools.search_object_by_ip` / `tools.check_deployment_status` in registered handlers. The accepted model includes `server -> resources` from the combined package import line but misses the parallel tools half.
- External/public surfaces are not first-class: MCP resource URIs, tool names, package console script, `httpx`/FMC REST boundaries, FastMCP runtime, and env var contract are visible in source but not modeled as surfaces.
- Verification is too narrow for iteration planning. It captures the pytest command but not the repo’s configured `ruff` and `mypy` quality bars in `pyproject.toml`, nor any explicit coverage of live-test exclusion.
- Risk/priority is absent. A six-line entrypoint and 371-line stateful client are treated at the same component abstraction level.

## 4. Questions I would still ask before using this to improve the project

1. Is the next improvement goal hardening the current read-only MVP, expanding MCP coverage, improving packaging/CI, or preparing live FMC validation?
2. Should read-only safety be enforced as a hard invariant with automated scans/tests against mutating FMC endpoints, except auth token endpoints?
3. Should `RateLimiter`, auth/session lifecycle, and pagination remain inside `FMCClient`, or should they become explicit subcomponents/helpers?
4. Which checks should define default acceptance: pytest only, or pytest plus ruff plus mypy?
5. Is `test_live.py` intentionally manual forever, or should there be a credential-gated live smoke profile later?
6. Should the decomposer’s snapshot include external-facing surface inventories: MCP resources/tools, console script, env vars, and REST endpoints?

## 5. Highest-value project improvements identifiable from this model plus source check

- Add a read-only safety test or static check that only auth token POSTs are allowed and all domain object/device operations remain GET-only.
- Add a focused mocked integration test for the FastMCP lifecycle path: server creates client, calls `resources.set_client`, and registered resources/tools delegate through the injected client.
- Add lint/type observable checks to Build Arena’s model output for Python repos that configure `ruff`/`mypy`.
- Consider splitting `client.py` responsibilities or at least documenting them in-source: rate limiter, session/auth lifecycle, request/retry policy, pagination, endpoint wrappers.
- Rename or deliberately mark `FMCClient.test_connection`; the `test_` prefix inside `src/` is easy for tools/humans to confuse with test code even if pytest is configured to search only `tests`.

## 6. Highest-value improvements to the Project Model/decomposer itself

- Replace templated component responsibilities with synthesized summaries from class/function nodes and README/spec evidence.
- Add a separate `project_invariants` or typed concern vocabulary for domain invariants: read-only, secret-bearing, rate limit, concurrency, live-test boundary, external API boundary.
- Promote runtime/data-flow edges in addition to imports: constructs, injects, registers, delegates-to, exposes-resource, exposes-tool.
- Detect combined imports precisely enough to emit both `server -> resources` and `server -> tools` relationships.
- Add priority/risk metadata: file size, public-surface ownership, stateful/concurrency/auth tags, configured quality gates, and test coverage edges.
- Separate Build Arena process concerns from target-project concerns so consumers know which warnings protect the model and which protect the product.

## 7. Risks or warnings if an autonomous agent used this model as-is

- It could trust `verification_gaps: 0` as “the project has no meaningful improvement gaps,” which is false; it only means the current gate scope passed.
- It could miss the real fragile center of the project: token auth, request limiting, pagination, and injected global client state.
- It could break MCP tools because the model does not clearly show `server -> tools` registration/delegation.
- It could make changes that violate the read-only promise because that invariant is not attached to FMC endpoint wrappers.
- It could under-test changes by running only pytest while ignoring configured lint/type checks.

## 8. Bottom-line recommendation

Use this artifact as a trustworthy first map and verification hook, not as a complete improvement planner. Before asking an autonomous agent to improve FMC-MCP from this model, either enrich the Project Model with project-level invariants/runtime surfaces or hand the agent the manual golden checklist alongside the model and explicitly instruct it to inspect `client.py`, `server.py`, `resources.py`, and `tools.py` before proposing changes.
