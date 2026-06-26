# Project Model v1 Shared Contract Specification

Date: 2026-06-05
Status: implemented Build Arena primary contract slice with cross-repo adoption still required

## Purpose

Project Model v1 is the primary enriched project-model contract for Build Arena AI decomposer snapshots. It resolves sidecar ambiguity by naming one authoritative artifact, `project-model-v1.json`, that binds the graph, model snapshot, provenance, and required iteration-readiness data into one versioned contract.

## Contract boundary

Build Arena owns and emits `project-model/v1`. The artifact is produced from filesystem and git truth during the AI decomposer path. Cached or prior sidecars are not authoritative unless their input hashes match the current graph and snapshot.

The primary AI decomposer output directory contains:

- `project-model-v1.json` as the primary enriched contract.

`manifest.json` names the primary path through:

- `project_model_primary_path: project-model-v1.json`
- `project_model_v1_path: project-model-v1.json`

## Machine-readable schema

Schema path:

- `docs/schemas/project-model-v1.schema.json`

Schema version constant:

- `project-model/v1`

The schema validates the emitted v1 artifact and rejects non-v1 JSON.

## Required top-level fields

Top-level fields are required only when a core proposal-loop consumer reads them. Advisory-only fields and metadata read only by experiment-lane consumers stay optional.

Required by core consumers:

- `schemaVersion` — contract discriminator.
- `id` — read by `arena/project_intake_scorecard.py` for `snapshotId`.
- `snapshot` — read by `arena/project_intake_scorecard.py` and `arena/proposal_planner.py` for components, checks, verification gaps, and advisory backlog material.
- `projectGraph` — read by `arena/project_intake_scorecard.py` for node-path evidence and by advisory capability/experiment consumers for graph hash and nodes.
- `provenance` — read by `arena/project_intake_scorecard.py` for `repoHead`.
- `iterationReadiness` — read by `arena/project_intake_scorecard.py`, `arena/proposal_planner.py`, `arena/proposal_domains.py`, and `arena/proposer_handoff.py` for component profiles, quality gates, open questions, and readiness-path handling.

Optional top-level metadata remains defined by the schema but is not required: `project`, `gateReport`, `hashes`, `models`, and `derivedArtifacts`.

### `schemaVersion`

Constant `project-model/v1`.

### `id`

The frozen `ProjectModelSnapshot.snapshot_id`. Build Arena run-loop events should reference this id plus hashes.

### `snapshot`

The full internal `ProjectModelSnapshot` payload. It currently carries `schema_version: project-model-snapshot/v0.1`; that internal version is preserved for existing gate code.

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

### `iterationReadiness`

Required block for iteration selection and proposal planning. It carries:

- `summary`
- `componentProfiles`
- `runtimeContracts`
- `externalSurfaces`
- `productInvariants`
- `qualityGates`
- `priorityBacklog`
- `openQuestions`

## Implementation scope completed in Build Arena

Implemented in this slice:

- `arena/project_model_v1.py` builds `project-model/v1` from a `ProjectModelSnapshot`, `ProjectGraph`, and `GateReport`.
- `arena/project_decomposer_ai.py` writes `project-model-v1.json` for every AI decomposer snapshot.
- The manifest marks v1 as the primary project-model artifact.
- `docs/schemas/project-model-v1.schema.json` validates the v1 artifact.
- `tests/test_project_model_v1_contract.py` proves the emitted v1 validates, the required `iterationReadiness` block is enforced, the off/noop path emits schema-valid v1, and a non-v1 shape is rejected by the v1 schema.

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
