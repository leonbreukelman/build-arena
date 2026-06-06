# fmc-mcp final recorded pilot semantic plausibility

Repo: `/home/leonb/projects/fmc-mcp`
Selection: Required pilot 2: FMC-MPC request resolved to canonical local repo fmc-mcp.
Snapshot: `/home/leonb/projects/build-arena/docs/verification/2026-06-04-ai-first-project-decomposer-pilot-fmc-mpc/snapshot-a1a7eab7533347be`
Primary model: `claude-opus-4-8`
Local verification return code: `0`
Gate passed: `True`
Components/contracts/checks/gaps/probes: 5/5/3/4/3

## Components
- `comp-config` — Configuration & Settings
  - responsibility: Load and validate runtime configuration (FMC host, credentials, timeouts) as typed pydantic settings consumed by client and server.
  - owned evidence: fmc_mcp.config
  - contracts: ['ct-server-config', 'ct-client-config']; checks: ['chk-suite', 'chk-resources-contract']; gaps: none
- `comp-client` — FMC HTTP Client (auth, transport, token cache)
  - responsibility: Own async HTTP transport to the FMC REST API, base64 basic-auth handshake, and time-based auth-token caching/refresh.
  - owned evidence: fmc_mcp.client
  - contracts: ['ct-client-config', 'ct-resources-client', 'ct-server-client']; checks: ['chk-suite', 'chk-resources-contract']; gaps: ['gap-client-network']
- `comp-resources` — FMC Resource Layer
  - responsibility: Retrieve FMC domain objects through the client and serialize them to JSON resource payloads for the MCP surface.
  - owned evidence: fmc_mcp.resources
  - contracts: ['ct-resources-client', 'ct-tools-resources']; checks: ['chk-suite', 'chk-resources-contract']; gaps: none
- `comp-tools` — MCP Tool Surface
  - responsibility: Define MCP tools over the resource layer, including input validation such as IP-address parsing, and shape tool responses as JSON.
  - owned evidence: fmc_mcp.tools
  - contracts: ['ct-tools-resources']; checks: ['chk-suite', 'chk-tools-validation']; gaps: ['gap-tool-wiring']
- `comp-server` — MCP Server Runtime & Entrypoint
  - responsibility: Construct the FastMCP server, wire config and client into its lifecycle, and expose the process entrypoint that launches the server.
  - owned evidence: fmc_mcp.server, fmc_mcp.__main__
  - contracts: ['ct-server-config', 'ct-server-client']; checks: ['chk-suite']; gaps: ['gap-tool-wiring', 'gap-entrypoint']

## Contracts
- `ct-server-config` comp-server -> comp-config via ['imports:fmc_mcp.config']
- `ct-client-config` comp-client -> comp-config via ['imports:fmc_mcp.config']
- `ct-resources-client` comp-resources -> comp-client via ['imports:fmc_mcp.client']
- `ct-tools-resources` comp-tools -> comp-resources via ['imports:fmc_mcp.resources']
- `ct-server-client` comp-server -> comp-client via ['imports:fmc_mcp.client']

## Verification gaps
- `gap-tool-wiring` (high): No selected edge connects fmc_mcp.server to fmc_mcp.tools, so registration/exposure of MCP tools through the server runtime is not observable from the graph; the tool surface may be wired via decorators or runtime registration not captured by the packet.
- `gap-client-network` (medium): Client FMC HTTP/auth behavior (httpx transport, base64 basic auth, time-based token caching) cannot be exercised against a live controller under the no-network/no-credentials acceptance constraint, so the real FMC request contract is verified only via mocks/offline.
- `gap-entrypoint` (low): The fmc_mcp.__main__ -> fmc_mcp.server startup path (process entrypoint) is not shown to be covered by tests in the packet.
- `gap-docs-static` (low): Documentation/static surfaces present in the graph (markdown_section x45 with 45 documents edges) and config surfaces (config x3 with 3 configures edges) were not selected and are not componentized, so their accuracy and coverage remain undecomposed.

## Assessment
- Final output is not fixture mode; it records Claude Opus model output plus independent Sonnet probe-builder artifacts after Grok Build failed to emit final JSON.
- Components are model-derived responsibility units; some intentionally group multiple source modules or explicit static/doc surfaces.
- Contracts are only gate-passing deterministic graph edges; unsupported semantic dependencies are retained as verification gaps.
- Observable checks match the actual command run for the repo.
- Protected/generated surfaces are graph-visible and excluded from component ownership.
- Negative-control artifacts demonstrate the gate rejects a plausible fluent file-bucket model output.
