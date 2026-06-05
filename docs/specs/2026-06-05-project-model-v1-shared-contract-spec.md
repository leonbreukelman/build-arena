# Project Model v1 Shared Contract Specification

Date: 2026-06-05
Status: implemented Build Arena primary contract slice with cross-repo adoption still required

## Purpose

Project Model v1 is the primary enriched project-model contract for Build Arena AI decomposer snapshots. It resolves the previous sidecar ambiguity by naming one authoritative artifact, `project-model-v1.json`, that binds the graph, model snapshot, gate report, provenance, hashes, models, and derived-artifact strategy into one versioned contract.

Project Model v0 remains available as a legacy compatibility projection. Downstream consumers should migrate to v1 when they need provenance, contracts, held-out probes, verification gaps, graph nodes/edges, gate reports, or artifact hashes.

## Contract boundary

Build Arena owns and emits `project-model/v1`. The artifact is produced from filesystem and git truth during the AI decomposer path. Cached or prior sidecars are not authoritative unless their input hashes match the current graph and snapshot.

The primary AI decomposer output directory now contains both:

- `project-model-v1.json` as the primary enriched contract.
- `project-model-v0.json` as the legacy compatibility projection.

`manifest.json` names the primary path through:

- `project_model_primary_path: project-model-v1.json`
- `project_model_v1_path: project-model-v1.json`
- `project_model_v0_path: project-model-v0.json`

## Machine-readable schema

Schema path:

- `docs/schemas/project-model-v1.schema.json`

Schema version constant:

- `project-model/v1`

The schema validates the emitted v1 artifact and rejects legacy v0-shaped JSON.

## Required top-level fields

### `schemaVersion`

Constant `project-model/v1`.

### `id`

The frozen `ProjectModelSnapshot.snapshot_id`. Build Arena run-loop events should reference this id plus hashes.

### `project`

Human-readable project identity and intent:

- `projectId`
- `projectRoot`
- `goal`
- `nonGoals`

### `snapshot`

The full internal `ProjectModelSnapshot` payload. It currently carries `schema_version: project-model-snapshot/v0.1`; that internal version is preserved so existing gate code and v0 projection do not regress.

The snapshot includes:

- `Component`
- `Contract`
- `CrossCuttingConcern`
- `ObservableCheck`
- `HeldOutProbe`
- `VerificationGap`
- `NearNeighborAlternative`
- acceptance command allowlist
- input hashes
- prompt hashes
- model output hashes

### `projectGraph`

The graph evidence bundle:

- graph schema version
- graph hash
- project root
- `GraphNode` list
- `GraphEdge` list

Each node/edge carries `ProvenanceRef` records rather than unsupported prose claims.

### `gateReport`

The deterministic `GateReport` for the same snapshot and graph. A v1 artifact can exist with `passed: false`; this is intentional. Failed gate output is evidence, not acceptance.

### `provenance`

Git and provenance policy metadata:

- git availability
- git root
- head OID
- dirty flag
- dirty paths
- dirty-state fingerprint
- provenance-ref strategy

Dirty-state fingerprint is derived from head OID, dirty flag, and dirty paths. It prevents silent reuse of a snapshot across changed worktrees.

### `hashes`

Hash namespaces:

- `inputHashes`
- `promptHashes`
- `outputHashes`
- `artifactHashes`

### `models`

Model identities:

- primary decomposer model
- independent probe-builder model ids when present

### `derivedArtifacts`

Strategy records for derived artifacts. The default contract names:

- JSONL events as canonical future run-loop state.
- SQLite projections as query-only derived state.
- Markdown summaries as generated human-readable views.

### `compatibility`

Legacy v0 projection path and role:

- `projectModelV0Path`
- `projectModelV0Role`

## Implementation scope completed in Build Arena

Implemented in this slice:

- `arena/project_model_v1.py` builds `project-model/v1` from a `ProjectModelSnapshot`, `ProjectGraph`, and `GateReport`.
- `arena/project_decomposer_ai.py` writes `project-model-v1.json` for every AI decomposer snapshot.
- The manifest marks v1 as the primary project-model artifact and keeps v0 as compatibility output.
- `docs/schemas/project-model-v1.schema.json` validates the v1 artifact.
- `tests/test_project_model_v1_contract.py` proves the emitted v1 validates, the v0 projection still exists, and a legacy v0 shape is rejected by the v1 schema.

## Live-action policy for verification gaps

Build Arena can produce read-only analysis when verification gaps exist, but live mutation must be stricter:

1. `critical` or `blocker` gaps block promotion and any live mutation against affected components.
2. `high` gaps block promotion and require either a local deterministic closure check or independent review before worktree-only patching.
3. `medium` gaps allow read-only decomposition and dry-run hypothesis generation, but must be surfaced as backlog items before mutation.
4. `low` and `info` gaps are advisory but still appear in v1 and the readiness register.
5. Protected, generated, scorer, verifier, and schema surfaces remain non-mutable regardless of gap severity.

This policy is specified here and represented in the readiness register. Code-level mutation enforcement is not yet implemented because this session does not start a full autonomous live loop.

## Graph and indexing readiness decision

Decision: defer Tree-sitter, ast-grep, SCIP/LSIF, and CodeQL integration for this bounded pre-live slice.

Reasoning:

- Current ProjectGraph already provides deterministic git/filesystem truth, Python AST import/symbol extraction, Markdown/config/test discovery, provenance refs, and dirty-state tracking.
- The immediate blocker was live-provider wiring and primary v1 contract ambiguity, not parser coverage.
- Adding a parser/indexing layer now would expand scope before v1 consumption and readiness policy are proven.

Guardrail: current graph limitations are explicit readiness-register entries. Live read-only decomposition can continue on small repos, but worktree patch cycles and promotion remain blocked until the target repo's language surfaces are proven adequate or indexed by a stronger parser layer.

## Cross-repo status

Build Arena now emits the v1 contract. Elenchus Core and Arena Calibration still need adoption work. Exact status and follow-up prompts are recorded separately after repository inspection.
