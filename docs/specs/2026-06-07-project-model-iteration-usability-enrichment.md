# Project Model v1 Iteration Usability Enrichment Spec

Date: 2026-06-07
Status: proposed for implementation in this session
Source review: `docs/verification/2026-06-06-fmc-mcp-first-decomposition/three-model-project-model-usability-review.md`

## 1. Problem statement

The first FMC-MCP Project Model v1 was accepted by the deterministic Build Arena gate, but the Grok/Opus/Hermes review found that it is mostly a static ownership/import map. It orients an agent to files and tests, but it does not yet make the project easy to improve from the model alone.

The missing usability signals are:

1. semantic component responsibilities instead of tautological module ownership;
2. product invariants such as read-only behavior, secret safety, rate/concurrency limits, and live-test boundaries;
3. runtime/data-flow contracts such as construction, injection, registration, and delegation;
4. explicit external surfaces such as MCP resources/tools, console scripts, environment variables, and HTTP endpoint families;
5. risk/priority metadata that tells an agent where improvement effort should start;
6. configured quality checks beyond the nearest local pytest command;
7. a fix for combined import resolution so `from package import a, b` can generate separate component contracts when `a` and `b` are owned modules.

## 2. Lightweight weighted intake scorecard

This is a narrow Build Arena agent-usability improvement. The weighted intake dimensions from `AGENTS.md` are applied in lightweight mode:

| Dimension | Weight | Rationale |
| --- | ---: | --- |
| AI-agent usability | 30 | Directly improves whether Grok/Opus/Hermes can identify safe next work from the model. |
| Architecture/spec contracts | 24 | Adds runtime/data-flow/external-surface contract metadata. |
| Reproducible verification | 18 | Adds configured local quality checks and schema tests. |
| Documentation/project knowledge | 12 | Captures the review-derived contract in versioned repo docs. |
| Security/safety hygiene | 10 | Product invariants include secret handling, read-only defaults, live-test boundary, and rate limits. |
| Operations/rollback | 6 | Keeps all changes local, deterministic, and compatible with current gate artifacts. |

Decision: prioritize Project Model v1 enrichment before autonomous FMC-MCP implementation work.

## 3. Scope

### In scope

1. Extend newly emitted `project-model/v1` artifacts with an `iterationReadiness` top-level object.
2. Keep `schemaVersion: project-model/v1`. `iterationReadiness` is optional in the JSON schema so historical v1 artifacts remain valid, but this implementation's decomposer path must always emit it and tests must assert its presence on newly generated artifacts.
3. Keep `ProjectModelSnapshot.schema_version: project-model-snapshot/v0.1`; do not mutate the internal snapshot version unless required.
4. Improve deterministic fixture decomposition output so snapshots also contain better component responsibilities, product concerns, and configured quality checks.
5. Improve Python import resolution for combined absolute imports.
6. Regenerate the FMC-MCP model using the updated decomposer and verify that the new v1 artifact exposes the review findings.
7. Obtain post-implementation agreement from Grok, Opus, and Hermes that the review gaps are addressed or explicitly represented.

### Out of scope

1. No mutation under `scorer/`, `verifier/`, root `schema/`, or `arena/generated/`.
2. No autonomous FMC-MCP code changes in this slice.
3. No live FMC API calls.
4. No broad autonomous worktree patch/promotion loop.
5. No Tree-sitter/SCIP/CodeQL parser integration in this slice.

## 4. Contract extension

Newly generated `project-model-v1.json` artifacts must include this top-level field:

```json
"iterationReadiness": {
  "summary": "...",
  "componentProfiles": [],
  "runtimeContracts": [],
  "externalSurfaces": [],
  "productInvariants": [],
  "qualityGates": [],
  "priorityBacklog": [],
  "openQuestions": []
}
```

### 4.1 `componentProfiles`

Each selected production component gets a profile:

- `componentId`: existing snapshot component id.
- `ownedNodeIds`: owned graph nodes.
- `responsibilitySummary`: non-tautological summary derived from source evidence.
- `keySymbols`: classes/functions/public symbols from the component source.
- `behavioralTags`: deterministic tags such as `auth`, `rate_limit`, `concurrency`, `pagination`, `mcp_server`, `configuration`, `resource_handlers`, `tool_handlers`, `entrypoint`, `read_only`.
- `riskLevel`: `low`, `medium`, or `high`.
- `priorityRank`: integer; 1 is highest priority.
- `whyPriority`: short reason grounded in source facts.
- `provenanceRefs`: ProjectGraph provenance refs.

FMC-MCP acceptance target: `component.fmc-mcp-client` must explicitly mention auth/session lifecycle, rate limiting, retry/pagination, and endpoint wrappers. It must rank ahead of the tiny entrypoint.

Objective anti-tautology rule: a `responsibilitySummary` is acceptable only if it includes at least two source-derived symbols or behavioral tags and is not equivalent to the component id/module name with punctuation/title-case changes. Tests must reject summaries matching patterns like "own the responsibility represented by `<module>`."

### 4.2 `runtimeContracts`

Runtime/data-flow contracts are deterministic, evidence-backed records:

- `id`
- `kind`: one of `constructs`, `injects`, `registers_resource`, `registers_tool`, `delegates_to`, `exposes_runtime_mode`, `imports`
- `fromComponentId`
- `toComponentId` when applicable
- `description`
- `supportingNodeIds`
- `supportingEdgeIds`
- `provenanceRefs`

These records may be inferred from source-span text evidence rather than graph call edges. A runtime contract is not required to have a supporting import edge when its `kind` is not `imports`; in that case `supportingEdgeIds` may be empty, but `provenanceRefs` must point to source file/line provenance for the construct, registration, injection, or delegation text. This is intentionally separate from the deterministic gate's import-edge coverage checks.

FMC-MCP acceptance targets:

- server constructs or owns creation of `FMCClient` during lifespan;
- server injects the client through `resources.set_client`;
- tools obtain/depend on the injected resource client;
- server registers MCP resources;
- server registers MCP tools;
- server delegates MCP tool handlers to `tools.py`;
- stdio and HTTP/SSE runtime modes are surfaced.

### 4.3 `externalSurfaces`

External surfaces describe what users, CLIs, protocols, or remote services touch:

- `id`
- `surfaceType`: `mcp_resource`, `mcp_tool`, `console_script`, `environment_variable`, `http_endpoint_family`, `runtime_mode`, `dependency`
- `name`
- `ownerComponentIds`
- `description`
- `provenanceRefs`

FMC-MCP acceptance targets:

- resource URIs including `fmc://system/info`, `fmc://devices/list`, `fmc://objects/network`, `fmc://deployment/status`;
- MCP tools including IP object search and deployment-status check;
- console script `mcp-server-fmc`;
- relevant environment/settings names;
- FMC REST endpoint families;
- FastMCP and httpx dependencies.

### 4.4 `productInvariants`

Product invariants separate target-project safety from Build Arena process concerns:

- `id`
- `category`: examples `read_only_external_operations`, `secret_safety`, `rate_limit`, `concurrency_limit`, `live_test_boundary`, `public_mcp_contract`
- `description`
- `componentIds`
- `externalSurfaceIds`
- `enforcement`: `modeled`, `tested`, `configured`, or `gap`
- `provenanceRefs`

FMC-MCP acceptance targets:

- read-only external operations are modeled, with auth-token POSTs distinguished from domain-operation reads;
- `SecretStr`/settings redaction is modeled;
- 120 requests/minute and 10 concurrent requests are modeled when present in source;
- live/credentialed tests are distinguished from default local acceptance;
- public MCP resources/tools are modeled as contract surfaces.

### 4.5 `qualityGates`

Quality gates expose configured safe local commands and whether they are currently acceptance commands:

- `id`
- `command`
- `source`: `detected_pyproject`, `detected_package_json`, `snapshot_observable_check`, or `manual`
- `mode`: `test`, `lint`, `typecheck`, `build`, `other`
- `safeToRunByDefault`
- `includedInAcceptance`
- `provenanceRefs`

FMC-MCP acceptance target: pytest, ruff, and mypy are visible when configured. They may be separate observable checks; all acceptance commands must pass the existing no-live/paid API allowlist guard.

### 4.6 `priorityBacklog`

The model must include advisory improvement targets, not autonomous mutation instructions:

- `id`
- `rank`
- `title`
- `rationale`
- `componentIds`
- `relatedInvariantIds`
- `relatedSurfaceIds`
- `suggestedVerification`
- `provenanceRefs`

FMC-MCP expected top items:

1. verify or test read-only behavior;
2. verify server/resources/tools wiring;
3. run or expose configured lint/type checks;
4. document or refactor client sub-responsibilities.

### 4.7 `openQuestions`

Questions should be generated only when the model cannot prove the answer from source. They must help a future agent ask targeted clarification rather than rediscovering broad context.

Objective open-question rule: each question must be tied to a named source signal or absent verification signal, and questions must be stably ordered by category and id. Examples: if a live test file exists but no safe local live-smoke check is configured, emit the live-test-boundary question; if a high-risk client component has many behavioral tags but no helper/subcomponent boundary in the model, emit the client-splitting question.

FMC-MCP expected examples:

- Is `test_live.py` intentionally manual-only or should it become a credential-gated smoke profile?
- Should `client.py` remain a single responsibility component or be split into helpers?
- Should default acceptance become pytest + ruff + mypy, or should lint/typecheck remain advisory?

## 5. Deterministic generation rules

1. All records must be derived from `ProjectGraph` nodes/edges, source file text, and config files read from the target repo.
2. No cached prior Project Model may be used as source truth.
3. Every record must include provenance refs resolving to graph evidence.
4. Source-span provenance is acceptable evidence for inferred runtime contracts, product invariants, and external surfaces when no graph edge exists; these inferred records must not pretend to be graph call edges.
5. Heuristics may use source text patterns but must fail safe: if a signal is uncertain, emit an open question or verification gap rather than a hard invariant.
6. Priority ranking, backlog ordering, and open-question ordering must use stable deterministic sort keys.
7. The output must remain deterministic for a fixed git/filesystem state.
8. Additional snapshot observable checks must use safe local commands only.

## 6. Validation and acceptance

Minimum Build Arena acceptance:

1. Unit tests fail before implementation for:
   - combined Python import resolution;
   - `iterationReadiness` emitted presence and schema shape for newly generated artifacts;
   - semantic component profile/priority on a fixture repo;
   - configured ruff/mypy check discovery.
2. Unit tests pass after implementation.
3. `docs/schemas/project-model-v1.schema.json` validates generated artifacts.
4. `uv run pytest tests -q` passes.
5. `uv run ruff check .` passes.
6. `uv run pyright` passes, or any failure is diagnosed and fixed.
7. FMC-MCP snapshot regeneration passes deterministic gate.
8. FMC-MCP local checks that the model exposes as acceptance commands are actually run and recorded.
9. Grok, Opus, and Hermes all agree that the original review gaps are addressed or explicitly represented in the updated FMC-MCP model.

## 7. Non-regression requirements

1. Project Model v1 remains the active shared contract emitted by the decomposer.
2. Existing v1 top-level data remains stable; `iterationReadiness` is mandatory for this emitter's new artifacts and for core intake/proposal consumers.
3. The deterministic gate still rejects stale graph hashes, file buckets, missing provenance, unsafe acceptance commands, missing edge coverage, and protected/generated ownership.
4. No generated files under `arena/generated/` are hand-edited.
5. No root `schema/` files are modified.
