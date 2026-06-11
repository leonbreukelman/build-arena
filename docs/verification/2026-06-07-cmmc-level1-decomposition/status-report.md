# CMMC Level 1 Readiness Assistant decomposition status

Date: 2026-06-07

## Target and sync status

Requested target: https://github.com/leonbreukelman/cmmc-level1-readiness-assistant

Canonical local checkout: `/home/leonb/projects/cmmc-level1-readiness-assistant`

The canonical checkout's committed branch state was synced with `origin/master`, but that checkout had substantial local dirty/untracked work. To avoid mixing local WIP into the decomposition, the run used a clean detached git worktree at:

`/home/leonb/projects/.decomposition-targets/cmmc-level1-readiness-assistant`

Clean decomposition target commit:

`b39562c3af0d8c3ed595088f9306a37945bb0eb2`

That equals `origin/master` at the time of the run. The clean target had no non-ignored dirty files before decomposition. The only generated local files after verification were ignored dependency/cache/build outputs such as `.venv`, `node_modules`, `.pytest_cache`, `__pycache__`, and `dist`.

## Target verification performed

From the clean remote-synced worktree:

- Backend: `cd app/backend && uv run pytest -q`
  - Result: pass, all backend tests passed.
- Frontend setup: `cd app/frontend && npm ci`
  - Result: pass, installed dependencies.
  - Note: npm reported 3 moderate vulnerabilities; no automatic audit fix was run because that would mutate dependency state and is outside decomposition.
- Frontend tests: `cd app/frontend && npm test -- --run`
  - Result: pass, 9 test files / 73 tests passed.
- Frontend build: `cd app/frontend && npm run build`
  - Result: pass.

Build Arena self-verification was also rerun after moving the clean target outside the Build Arena tree:

- `make verify`
  - Result: pass.

## Decomposition artifact

Snapshot directory:

`/home/leonb/projects/build-arena/docs/verification/2026-06-07-cmmc-level1-decomposition/artifacts/snapshot-25eb081bd3f1ba3b`

Important files:

- Manifest: `manifest.json`
- Primary Project Model v1: `project-model-v1.json`
- Compatibility Project Model v0: `project-model-v0.json`
- Graph sidecar: `graph.json`
- Gate report: `gate-report.json`
- Decomposer prompt: `prompts/decomposer-prompt.txt`
- Decomposer raw output: `model-outputs/decomposer.raw.json`

Snapshot id:

`snapshot-25eb081bd3f1ba3b`

## Gate result

The snapshot was generated, but the deterministic Project Model gate failed:

- Passed: false
- Violation count: 70
- Violation classes:
  - `inventory_coverage`: 63
  - `edge_coverage`: 7

Primary cause:

The fixture decomposer selected only 8 frontend-oriented components and 1 contract from a much larger full-stack graph. The graph contains 1,774 nodes and 2,201 edges. Many backend, frontend, database, security, LLM, Alembic, report, and test modules were therefore neither component-owned nor explicitly covered by verification gaps.

Examples of missing inventory coverage include:

- `app.backend.src.main`
- `app.backend.src.assessment.state_machine`
- `app.backend.src.reports.generator`
- `app.backend.src.security.information_boundary`
- `app.backend.src.llm.client`
- `app.backend.src.auth.dependencies`
- `app.frontend.src.pages.AssessmentApp`
- `app.frontend.src.components.ScopePanel`
- `app.frontend.src.api.config`
- Alembic migration modules

Examples of uncovered import-edge contracts include frontend component/test imports into `api-client`, `ChatPanel`, `ReportPreview`, and `RemediationDashboard`.

## Emitted observable check result

The generated model emitted only one observable check:

`uv run pytest -q`

Run exactly from the clean target root, this failed with:

`Failed to spawn: pytest` / `No such file or directory`

That is a model usability defect for this repo shape, not a target project failure. The actual safe target checks are directory-specific:

- backend: `app/backend`: `uv run pytest -q`
- frontend: `app/frontend`: `npm test -- --run`
- frontend: `app/frontend`: `npm run build`

## Readiness assessment

This decomposition is filesystem/git-grounded and useful as a failing pilot artifact, but it is not gate-passing and should not be treated as an accepted decomposition.

Readiness level: blocked for action-ready decomposition.

What is ready:

- Local/remote sync was established via a clean worktree at `origin/master`.
- Target backend and frontend verification passed.
- Build Arena generated a reproducible snapshot and full graph sidecar.
- The gate failure is deterministic and well-scoped.

What is blocked:

- The fixture decomposer is not yet robust for this larger full-stack repo.
- Component selection is too narrow.
- Contract generation is too sparse.
- Observable check extraction does not understand multi-root repos with backend/frontend subprojects.
- The generic `iterationReadiness` enrichment from the FMC-MCP pass is not sufficient by itself for this repo class.

## Recommended next Build Arena changes

1. Add multi-root project detection for repos with nested `app/backend/pyproject.toml` and `app/frontend/package.json`.
2. Promote directory-specific safe checks into observable checks:
   - `cd app/backend && uv run pytest -q`
   - `cd app/frontend && npm test -- --run`
   - `cd app/frontend && npm run build`
3. Add component clustering for full-stack apps instead of selecting only first graph-owned source nodes.
   Suggested CMMC clusters:
   - backend API/app entrypoint
   - assessment workflow/state machine
   - CMMC control library
   - evidence/data-boundary enforcement
   - report generation/readiness language
   - auth/tenant isolation
   - database/Alembic migrations
   - LLM sidecar/provider/policy boundary
   - frontend assessment app shell
   - frontend API client/auth/config
   - frontend evidence/finding/report UI components
   - deployment scripts/config
4. Ensure every primary source node is either owned by a component or explicitly listed in a scoped verification gap.
5. Ensure every owned import edge between selected components has a contract or a justified gap.
6. Add a regression test using a small synthetic full-stack nested backend/frontend fixture before rerunning CMMC.

## Bottom line

The CMMC project was successfully synced, verified, and decomposed into artifacts, but the decomposition is not accepted by Build Arena gates. This is the first useful generalization failure after FMC-MCP: it shows the current Project Model path is still too optimized for small Python/MCP-style repositories and needs multi-root full-stack decomposition support before CMMC can become a passing reference target.
