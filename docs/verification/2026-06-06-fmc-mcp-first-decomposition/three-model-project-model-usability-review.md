# Three-model review of FMC-MCP Project Model v1 iteration usability

Date: 2026-06-07
Subject artifact: `snapshot-e75be06540a3883d/project-model-v1.json`
Target repo: `/home/leonb/projects/fmc-mcp`
Review packet: `ai-review-input-packet.json`

## Reviewers

1. Grok review: `grok-review.md`
   - Verdict: `strong`
   - Score: 8/10
   - Note: Grok CLI produced a complete review while also logging auth/MCP authorization warnings. `XAI_API_KEY` was not available for API fallback.
2. Claude Opus review: `opus-review.md`
   - Verdict: `usable_with_gaps`
   - Score: 5/10
   - Ran through Claude Code with `--model opus`, tools disabled, and a budget cap.
3. Hermes review: `hermes-review.md`
   - Verdict: `usable_with_gaps`
   - Score: 6.5/10
   - Grounded by reading the Project Model, model graph/contracts, and FMC-MCP source files.

## Consensus answer

The generated Project Model is good enough as a first durable map, but not yet good enough as a complete improvement planner.

All three reviewers agreed that the artifact is useful for orientation:

- it identifies the production module/component boundaries;
- it is pinned to clean git/filesystem provenance;
- it has a real local acceptance command;
- it passes the Build Arena gate;
- it correctly treats tests as verification rather than production components;
- it gives an agent a safe starting point for source inspection.

All three also found the same main usability problem: the accepted snapshot is mostly a static ownership/import map. It does not yet surface the actual project semantics that a strong model would need to confidently improve FMC-MCP without re-reading source.

## Highest-confidence missed or underrepresented project facts

1. `client.py` is the real complexity center.

The model owns `fmc_mcp.client`, but its component responsibility is generic. It does not explicitly model:

- `RateLimiter` token-bucket behavior;
- 120 requests/minute rate constraint;
- 10-connection semaphore/back-pressure;
- Basic Auth token generation;
- access-token refresh and full re-auth behavior;
- 401 retry flow;
- 429 `Retry-After` handling;
- pagination through `get_all_items`;
- the distinction between GET-only read API wrappers and auth-token POST endpoints.

2. FMC-MCP’s own safety invariants are not first-class.

The snapshot’s cross-cutting concerns mostly protect Build Arena process integrity:

- anti-fabrication;
- determinism;
- provenance;
- no live/paid API acceptance.

They do not sufficiently represent FMC-MCP product invariants:

- read-only FMC behavior;
- secret-safe `SecretStr` handling and redacted config logging;
- rate/concurrency limits;
- no-live default acceptance vs optional credentialed live tests;
- public MCP resources/tools as the user-facing contract.

3. Runtime/data-flow contracts are missing or weak.

The model covers static imports, but not enough of the actual runtime architecture:

- `server.lifespan` constructs `FMCClient`;
- `server.lifespan` calls `resources.set_client(_client)`;
- `resources.get_client()` is the injected client access point;
- `tools` obtains the client through `resources.get_client()`;
- `server.py` registers four MCP resources and two MCP tools;
- stdio vs HTTP/SSE transport is an external runtime mode decision.

A specific gap: the accepted model has no clear `server -> tools` contract even though `server.py` imports `tools` and delegates registered tool handlers to it.

4. Public/external surfaces are not modeled as surfaces.

The model does not first-class the externally meaningful contract:

- MCP resource URIs: `fmc://system/info`, `fmc://devices/list`, `fmc://objects/network`, `fmc://deployment/status`;
- MCP tools: `search_object_by_ip`, deployment-status check;
- console script: `mcp-server-fmc = fmc_mcp:main`;
- env vars/settings boundary;
- FMC REST endpoints;
- `httpx` and `FastMCP` as important external dependencies.

5. There is no risk or priority signal.

A future agent sees six components but no ranking. The 371-line stateful client and the tiny entrypoint are structurally equivalent in the snapshot. That makes it harder for Grok/Opus/Hermes to know where improvement effort should start.

6. Verification is too narrow for improvement work.

The model includes the real pytest command, which is good. But the repo also configures `ruff` and `mypy` in `pyproject.toml`; the Project Model does not expose those as observable checks or quality surfaces. Opus and Hermes both flagged this.

## Questions reviewers would ask before iterating on FMC-MCP

The recurring questions were:

1. What is the next improvement goal: hardening current read-only MVP, expanding MCP resources/tools, improving packaging/CI, or preparing live FMC validation?
2. Are read-only behavior, secret safety, rate limit, and 10-connection limit hard invariants that future agents must preserve?
3. Should `client.py` remain one component, or should rate limiting, auth/session lifecycle, request/retry, pagination, and endpoint wrappers become subcomponents/helpers?
4. Should default acceptance be pytest only, or pytest plus ruff and mypy?
5. Is `test_live.py` intentionally manual-only, or should it become a credential-gated live smoke profile later?
6. Should the Project Model include public MCP resources/tools and env vars as explicit external surfaces?
7. Is the `server.py` wrapper around `tools.py` functions intentional, or should the indirection be consolidated?

## Highest-value project improvements identified from the model plus review

These are improvements to FMC-MCP itself, not Build Arena:

1. Add/readiness-enforce a read-only safety test or static scan.
   - Allow auth token POST endpoints.
   - Ensure domain object/device/deployment operations remain GET-only.

2. Add a mocked end-to-end server wiring test.
   - Exercise lifespan client creation.
   - Verify `resources.set_client` injection.
   - Verify registered resource/tool handlers delegate through the injected client.

3. Add default quality checks beyond pytest.
   - At minimum expose or run `ruff` and `mypy` because they are already configured in `pyproject.toml`.

4. Improve `client.py` structure or documentation.
   - Make rate limiting, auth/session lifecycle, request/retry policy, pagination, and endpoint wrappers explicit sub-responsibilities.

5. Review `FMCClient.test_connection` naming.
   - The `test_` prefix inside production source is a smell and can confuse humans/tools, even if pytest currently searches only `tests`.

6. Consider consolidating or documenting the server/tool indirection.
   - `server.py` exposes MCP tool functions that call `tools.py` functions with related names. This is probably intentional registration wrapping, but future agents need that made explicit.

## Highest-value Build Arena / Project Model improvements

1. Generate real component responsibilities.
   - Synthesize from class/function nodes, docstrings, README/spec evidence, and public symbols.
   - Avoid tautologies like “own the responsibility represented by module X.”

2. Add target-project invariant modeling.
   - Read-only safety.
   - Secret-bearing settings.
   - Rate/concurrency constraints.
   - Live-test vs local-test boundaries.
   - External API/protocol surfaces.

3. Model runtime/data-flow edges, not only imports.
   - Constructs.
   - Injects.
   - Registers resource/tool.
   - Delegates to.
   - Exposes endpoint/resource/tool.

4. Fix combined-import resolution and semantic contract promotion.
   - The current model captures `server -> resources` from `from fmc_mcp import resources, tools`, but not the parallel `server -> tools` relationship.

5. Add risk/priority metadata.
   - LOC/complexity.
   - Stateful/auth/concurrency tags.
   - Public-surface ownership.
   - Test/quality-check coverage.
   - Churn if git history is available.

6. Separate process concerns from product concerns.
   - Build Arena concerns explain why the model is trustworthy.
   - Product concerns explain what future changes must preserve.

7. Include configured quality commands in observable checks.
   - For Python repos, detect `ruff`, `mypy`/`pyright`, coverage, and test extras where configured.

## Practical interpretation for Leon

Yes, this model is usable — but it is mostly a map, not yet a mentor.

A strong model can use it to find the right files and run the right local test. It cannot yet look at the model alone and know the important product constraints or the best next improvement. For that, it still needs either the manual golden checklist or a richer decomposition pass.

Best next Build Arena improvement:

> Enrich Project Model v1 so each component has real behavioral responsibilities, project-specific invariants, runtime/data-flow contracts, external surfaces, and risk/priority metadata.

Best next FMC-MCP improvement:

> Add explicit tests/checks around read-only behavior, server/resource/tool injection, and configured lint/type gates, then consider splitting or documenting the overloaded client responsibilities.

## Artifact index

- Review packet: `ai-review-input-packet.json`
- Grok review: `grok-review.md`
- Opus review: `opus-review.md`
- Hermes review: `hermes-review.md`
- This synthesis: `three-model-project-model-usability-review.md`
