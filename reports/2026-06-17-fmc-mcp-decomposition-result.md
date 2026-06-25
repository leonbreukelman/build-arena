# fmc-mcp live decomposition result — 2026-06-17

## Owner verdict

Decomposition-only run completed and passed the deterministic Project Model gate.

Run verdict: `PASS_DECOMPOSITION_GATE`

Opus review verdict on the real decomposition: `MIXED`

Meaning: the live Grok decomposition produced a usable Project Model v1 with zero gate violations and substantially better enriched model surfaces, but Opus flagged real quality weaknesses before we should let intake/proposal trust the ranking blindly.

I stopped before intake. No scorecard, proposal, or intake artifacts exist under this run root.

## Command scope

This run used the Grok/xAI key from `<repo>/.env` without printing or recording the key value.

Command class:

```text
uv run python -m arena.project_model_cli snapshot \
  --project <projects>/fmc-mcp \
  --artifacts-root <repo>/.arena/runs/fmc-mcp-decomposition-20260617T195758Z \
  --project-id fmc-mcp \
  --goal "Improve the read-only Cisco Firepower Management Center MCP server with bounded, verified, single-file changes that preserve local tests, lint, and typing." \
  --source-task "live decomposition only; stop before intake" \
  --primary-backlog-item decomposition-only \
  --llm-mode live \
  --allow-live \
  --live-provider xai \
  --live-model grok-4.20-0309-non-reasoning \
  --live-api-key-env XAI_API_KEY \
  --live-max-tokens 12000
```

No intake command was run.

## Artifacts

- Run root: `<repo>/.arena/runs/fmc-mcp-decomposition-20260617T195758Z`
- Snapshot dir: `<repo>/.arena/runs/fmc-mcp-decomposition-20260617T195758Z/snapshot-ddb951deca8d5c7b`
- Project Model v1: `<repo>/.arena/runs/fmc-mcp-decomposition-20260617T195758Z/snapshot-ddb951deca8d5c7b/project-model-v1.json`
- Gate report: `<repo>/.arena/runs/fmc-mcp-decomposition-20260617T195758Z/snapshot-ddb951deca8d5c7b/gate-report.json`
- Manifest: `<repo>/.arena/runs/fmc-mcp-decomposition-20260617T195758Z/snapshot-ddb951deca8d5c7b/manifest.json`
- Raw model output: `<repo>/.arena/runs/fmc-mcp-decomposition-20260617T195758Z/snapshot-ddb951deca8d5c7b/model-outputs/decomposer.raw.json`
- Real-result summary: `<repo>/reports/2026-06-17-fmc-mcp-decomposition-real-summary.json`
- Opus expected-good criteria: `<repo>/reports/2026-06-17-fmc-mcp-decomposition-expected-opus-retry.json`
- Opus real-result review: `<repo>/reports/2026-06-17-fmc-mcp-decomposition-real-opus-review-retry.json`

## Mechanical result

CLI result:

```json
{
  "passed": true,
  "snapshot_id": "snapshot-ddb951deca8d5c7b",
  "violation_count": 0
}
```

Gate report:

```json
{"passed": true, "violations": []}
```

Target repo state after run:

```text
## main...origin/main [ahead 1]
```

Build Arena did not mutate `fmc-mcp` during decomposition.

Provider metadata recorded in the manifest:

- Provider: `xai`
- Requested model: `grok-4.20-0309-non-reasoning`
- Served model: `grok-4.20-0309-non-reasoning`
- Served model matches requested: `true`
- API key source: `environment`
- Finish reason: `stop`
- Usage: 7,558 prompt tokens; 3,820 completion tokens; 11,378 total tokens

## What the decomposition produced

Counts from Project Model v1 / raw output:

```json
{
  "raw_components": 7,
  "raw_contracts": 4,
  "raw_observable_checks": 6,
  "raw_verification_gaps": 2,
  "componentProfiles": 7,
  "runtimeContracts": 43,
  "externalSurfaces": 30,
  "productInvariants": 6,
  "qualityGates": 4,
  "priorityBacklog": 5,
  "openQuestions": 5
}
```

Runtime contract kind counts:

```json
{
  "constructs": 2,
  "delegates_to": 4,
  "exposes_runtime_mode": 1,
  "imports": 31,
  "injects": 2,
  "registers_resource": 2,
  "registers_tool": 1
}
```

Strong signals:

- Project Model v1 is primary and `iterationReadiness` is populated.
- Client component exists as `comp-client`, rank 2, ahead of tiny entrypoint `comp-entry` rank 7.
- Runtime contracts cover server constructing `FMCClient`, server injecting resources, server registering resources/tools, server delegating to tools, and runtime mode exposure.
- External surfaces include the expected `fmc://...` resources, MCP tools, console script, environment/settings names, FMC REST endpoint families, FastMCP, and httpx.
- Product invariants include read-only external operations, secret safety, rate limit, concurrency limit, live-test boundary, and public MCP contract.
- Quality gates expose pytest, ruff, mypy, and pyright signals.
- Priority backlog includes read-only verification, server/resources/tools wiring, lint/type checks, client responsibility split/docs, and `test_connection` naming.
- Open questions include client boundary, live-test boundary, quality default, server-tools indirection, and production `test_connection` naming.

## Opus expected-good criteria

Opus said a good decomposition should be judged only on model/snapshot/gate/artifact quality, not on downstream intake/proposal/promotion. Required criteria included:

- Project Model v1 primary artifact with `iterationReadiness` populated.
- Deterministic gate passes.
- Client component ranked ahead of tiny entrypoint and explicitly captures auth/session, rate limiting, retry/pagination, and endpoint wrappers.
- Non-tautological summaries with source-derived symbols/tags.
- Runtime contracts for client construction, injection, resource/tool registration, delegation, and runtime modes.
- External surfaces for resources, tools, console script, env/settings, REST endpoint families, FastMCP/httpx.
- Product invariants for read-only vs auth POSTs, secret safety, rate/concurrency, live-test boundary, public MCP contract.
- Safe local quality gates only.
- Gaps/open questions for uncertainty.

## Opus review of real result

Opus verdict: `MIXED`

Blockers: none.

Met expectations called out by Opus:

- Gate passed with zero violations.
- Project Model v1 and `iterationReadiness` are present.
- Client is ranked ahead of entrypoint and server.
- Runtime contracts are rich and cover the key expected classes.
- External surfaces and invariants are broad and materially match expectations.
- Quality gates include pytest, ruff, mypy, and pyright, with safe local acceptance commands.
- Backlog and open questions are good and source-derived.
- Provider metadata is recorded and served model matches requested.

Weaknesses called out by Opus:

1. Ranking distortion: `comp-tests` is rank 1/high-risk above the production client. Opus says that conflates test code with product responsibility.
2. Responsibility summaries are formulaic: they clear the mechanical non-tautology bar but read like tag/symbol restatement.
3. Client profile does not explicitly name retry or endpoint wrappers in the component summary itself, even though those are visible elsewhere in backlog/open questions.
4. `comp-entry` has an empty key-symbol sample and weak one-tag summary; acceptable for a tiny entrypoint but not rich.

Opus recommended next step:

> Re-rank so the production client (`comp-client`) leads priority and demote the test suite below production components (or model tests as verification coverage rather than a high-risk production responsibility); enrich the client component summary to explicitly name retry and endpoint wrappers, and de-templatize responsibility summaries toward behavior rather than tag/symbol restatement. No gate or provenance blocker requires re-running before proceeding.

## My read

This is a real improvement over the old decomposition shape: the model is not docs-only, the enriched `iterationReadiness` surfaces are populated, and the gate is clean.

But I agree with Opus that the ranking still has a semantic defect: tests being rank 1/high-risk is not the owner-useful priority shape we want. Before intake/proposal, we should decide whether to patch Build Arena's component-profile risk/ranking logic so test components are modeled as verification support instead of top production-risk targets.

Stopping point: decomposition complete, intake not run.
