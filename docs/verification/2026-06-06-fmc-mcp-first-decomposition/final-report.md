# FMC-MCP first real decomposition final report

Date: 2026-06-06
Status: accepted for review use
Target project: `/home/leonb/projects/fmc-mcp`
Target project HEAD: `00a632ac950a8c411f8d8ac90197e28191f58619`
Mode: non-live fixture decomposition, durable artifact bundle, no live FMC/API calls, no paid LLM/API calls.

## Final accepted artifact

Final snapshot ID: `snapshot-e75be06540a3883d`

Primary Project Model v1:

`/home/leonb/projects/build-arena/docs/verification/2026-06-06-fmc-mcp-first-decomposition/artifacts/snapshot-e75be06540a3883d/project-model-v1.json`

Manifest:

`/home/leonb/projects/build-arena/docs/verification/2026-06-06-fmc-mcp-first-decomposition/artifacts/snapshot-e75be06540a3883d/manifest.json`

Manual source-truth checklist:

`/home/leonb/projects/build-arena/docs/verification/2026-06-06-fmc-mcp-first-decomposition/manual-golden-decomposition.md`

Important hashes from manifest:

- graph hash: `d7dce5e7a40e7ac3fd2b905e509c0e5b6473c39a94c9326b9c12e1ae71f190b3`
- Project Model v1 hash: `0f5a7ce3d3d00a9f9f58f1b468e3ab65080bebcf7484032ed824fb97920e77b3`
- Project Model v0 compatibility hash: `8baca1ba79b705112c4b13be2a0e0370b536d62177f0ef071f5186d7ae46dbf4`
- target repo dirty state: clean / `dirty=false`

## Model contents

Graph:

- 175 nodes
- 209 edges

Accepted Project Model snapshot:

- 6 components
- 7 contracts
- 1 observable check
- 4 cross-cutting concerns
- 1 held-out probe
- 0 verification gaps
- gate violations: 0

Accepted components:

1. `component.fmc-mcp-server` owning `fmc_mcp.server`
2. `component.fmc-mcp-config` owning `fmc_mcp.config`
3. `component.fmc-mcp-resources` owning `fmc_mcp.resources`
4. `component.fmc-mcp-client` owning `fmc_mcp.client`
5. `component.fmc-mcp-tools` owning `fmc_mcp.tools`
6. `component.fmc-mcp-main` owning `fmc_mcp.__main__`

The model intentionally treats tests as observable verification rather than production responsibility components.

Observable check:

- command: `uv run python -m pytest -q`
- acceptance allowlist: `local-pytest`, `uv run python -m pytest -q`
- safe to run by default: yes
- requires network: no
- requires paid API: no

## Gate and downstream consumption results

Build Arena deterministic gate:

```text
uv run python -m arena.project_model_cli gate --snapshot docs/verification/2026-06-06-fmc-mcp-first-decomposition/artifacts/snapshot-e75be06540a3883d/manifest.json
{"passed": true, "violations": []}
```

FMC-MCP local acceptance check:

```text
uv run python -m pytest -q
19 passed in 0.04s
```

Elenchus Core v1 advisory consumption:

```text
validity valid True []
dependency_violations 0
evidence_gaps 0
held_out_failures 0
near_neighbor_status resistant
```

Repository-level verification after repairs:

```text
# Build Arena
make verify
0 ruff issues, 0 pyright errors, pytest green

# Elenchus Core
uv run pytest tests -q
all tests passed, 1 existing Starlette/httpx deprecation warning
```

## Issues found and repaired during this first real run

This first real decomposition exposed two Build Arena decomposer issues before the final accepted snapshot was produced.

1. Missing contracts for owned cross-component import edges

Initial durable snapshot failed the gate with 5 `edge_coverage` errors. Root cause: the fixture decomposer emitted only the first discovered import contract, then stopped. FMC-MCP has multiple real cross-component import contracts: resources -> client, client -> config, tools -> resources, __main__ -> server, server -> client, server -> resources, and server -> config.

Repair:

- Added a regression test: `test_fixture_decomposer_covers_every_owned_cross_component_import_edge`.
- Updated `arena/project_model_llm.py` to emit contracts for every owned cross-component import edge, deduplicated by component pair, with supporting edges and provenance retained.

2. Acceptance command did not actually run in FMC-MCP

The regenerated model originally used `uv run pytest -q`. The Build Arena gate accepted it, but running it in `/home/leonb/projects/fmc-mcp` failed with:

```text
error: Failed to spawn: `pytest`
Caused by: No such file or directory
```

The target repo’s working command is `uv run python -m pytest -q`.

Repair:

- Added a regression assertion that generated observable checks use `uv run python -m pytest -q`.
- Updated the decomposer’s generated acceptance allowlist to include both the command ID (`local-pytest`) and the concrete command string (`uv run python -m pytest -q`).
- This also cleared Elenchus Core’s advisory allowlist warning.

## Acceptance decision

Accepted for review use.

The FMC-MCP first real Project Model v1 decomposition is now durable, gate-passing, locally executable, and consumable by Elenchus Core without v1 validity/dependency/evidence warnings.

Boundary note: this accepted decomposition is suitable as review/decomposition evidence. It is not authorization for broad autonomous live loops, FMC live calls, worktree mutation/promotion, or paid/live decomposition runs. Build Arena’s existing broader readiness caveats still apply.
