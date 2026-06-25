You are Opus reviewing Build Arena's fmc-mcp live decomposition expectations before the decomposition is run.

Task: Define what the NEW live Project Model v1 decomposition result should look like to be considered good after Build Arena's recent improvements. Do not review a real output yet. Return compact JSON only.

Context:
- Target repo: <projects>/fmc-mcp, local main clean at 25f445806d5221f21d7ac675799db5c30499f1b7, ahead of origin by one commit adding .arena/goal.toml.
- Goal: Improve the read-only Cisco Firepower Management Center MCP server with bounded, verified, single-file changes that preserve local tests, lint, and typing.
- This step is decomposition only: run live Project Model snapshot, gate, artifact generation. Do NOT expect intake/scorecard/proposals.
- Previous live fmc-mcp decomposition passed gate, but later proposal work exposed gaps: docs-only effective path, weak proposal registry/lifecycle, stale proposal branches, and no live closed-loop proof. Those are downstream; decomposition quality should not be judged by whether it selects/promotes a candidate.
- Recent Build Arena improvements relevant to the Project Model: Project Model v1 primary artifact, enriched iterationReadiness/component profiles/contracts/external surfaces/invariants/quality gates/priority backlog/open questions, deterministic graph/provenance, import-contract closure, provider metadata, and deterministic gate.

Known fmc-mcp acceptance targets from repo specs:
- component.fmc-mcp-client must explicitly mention auth/session lifecycle, rate limiting, retry/pagination, and endpoint wrappers. It must rank ahead of the tiny entrypoint.
- Responsibility summaries must include at least two source-derived symbols or behavioral tags and must not be tautological file-bucket summaries.
- Runtime contracts should include: server constructs/owns FMCClient during lifespan; server injects client through resources.set_client; tools obtain/depend on injected resource client; server registers MCP resources; server registers MCP tools; server delegates tool handlers to tools.py; stdio and HTTP/SSE modes are surfaced.
- External surfaces should include: fmc://system/info, fmc://devices/list, fmc://objects/network, fmc://deployment/status; MCP tools for IP object search and deployment status; console script mcp-server-fmc; environment/settings names; FMC REST endpoint families; FastMCP and httpx dependencies.
- Product invariants should model read-only external operations while distinguishing auth-token POSTs from domain-operation reads; SecretStr/settings redaction; 120 req/min and 10 concurrent requests; live/credentialed test boundary; public MCP resource/tool contract.
- Quality gates should expose pytest, ruff, and mypy when configured, and only safe local commands should be included in acceptance.
- Expected priority backlog examples: verify/test read-only behavior; verify server/resources/tools wiring; run/expose lint/type checks; document/refactor client sub-responsibilities.
- Expected open questions examples: whether live tests are manual-only/credential-gated; whether client.py should split; whether default acceptance should be pytest+ruff+mypy or lint/type remains advisory.
- Deterministic requirements: every record derived from ProjectGraph/source/config; provenance refs resolve; source-span provenance is acceptable for inferred contracts; uncertain signals become gaps/open questions; no cached prior model as source truth.

Return JSON only:
{
  "verdict_definition": "what would count as good enough",
  "must_have": ["..."],
  "should_have": ["..."],
  "red_flags": ["..."],
  "not_required_for_this_step": ["..."],
  "review_checklist": ["..."],
  "summary": "..."
}
