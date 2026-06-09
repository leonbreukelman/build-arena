# Research Report: Project-Agnostic Multi-Root Graph Clustering and Observable-Check Discovery

Date: 2026-06-07
Project: Build Arena
Status: Research report prepared for Opus sign-off

## Executive conclusion

Build Arena should not grow a CMMC-specific decomposer, an FMC-specific decomposer, or any repo-specific adapters. The correct design is a single meta-decomposer whose core abstractions are:

1. A repository is a workspace that may contain multiple project roots.
2. A project root is discovered from manifests and build/test declarations, not from repository identity.
3. Observable checks are declared tasks bound to an execution directory.
4. Components are graph clusters seeded by root/directory/symbol evidence, not fixed taxonomies.
5. Contracts are derived from cross-component edges, with explicit gaps for real but unobservable relationships.
6. Coverage repair must assign all primary source nodes to components or specific verification gaps without blanket padding.

CMMC is therefore a held-out generalization failure signal, not a customization target. The correct next step is to generalize the decomposer so it can handle repo shapes like FMC-MCP, CMMC, and unrelated held-out projects without code paths that know any of their names or domain concepts.

## Problem observed in the current implementation

Grounded findings from the current Build Arena codebase:

- `arena/project_graph.py` resolves one git top-level project root and records config files as graph nodes, but it does not promote nested manifests to first-class project roots.
- `arena/decomposer.py` contains an arena calibration branch keyed on literal files such as `arena/fixtures.py`, `arena/scorer.py`, `arena/verifier.py`, and fixture manifests. That branch emits hardcoded component and contract shapes.
- The generic fallback in `arena/decomposer.py` groups files into broad buckets such as Python package, regression tests, documentation, project configuration, and unclassified surface. It emits no generic edge-derived contracts.
- The generic fallback emits root-level checks such as `uv run pytest -q` or `uv run python -m compileall .`, even when the target repository has nested execution roots.
- `arena/project_snapshot.py` currently represents `ObservableCheck` as a command string without an explicit execution directory field. In practice this makes commands ambiguous for monorepos and multi-root repos.
- `arena/project_model_gate.py` enforces inventory and edge coverage, but it does not currently verify that observable checks are executable in the correct working directory.

This explains the CMMC failure: the repo had a valid backend and frontend with checks under nested roots, but the generated model selected too few graph nodes and emitted a root-level Python check that was not the target repo’s declared execution root.

## External research synthesis

The research reviewed established patterns from monorepo build systems and architecture recovery:

### Build systems and monorepo tools

Relevant systems: Nx, Pants, Bazel, Cargo workspaces, Go modules, Node workspaces, Make/CI task graphs.

Common principles:

- The directory containing a manifest or build metadata is the natural unit of build/test execution.
- Repositories may contain a forest of project roots.
- Build/test/lint/typecheck commands are task declarations, not free-floating conventions.
- Dependency edges between targets, packages, modules, and tasks are first-class graph objects.
- Workspaces can be containers that declare child project roots rather than single execution roots.

Practical implication for Build Arena: a project model must preserve root identity and check execution directory. A command without its cwd is incomplete evidence.

### Static analysis and architecture recovery

Relevant concepts: module clustering, reflexion models, dependency structure matrices, cohesion/coupling, Bunch/ACDC-style recovery, community detection.

Common principles:

- File buckets alone are too shallow; architecture recovery needs dependency structure.
- A good decomposition maximizes internal cohesion and minimizes external coupling.
- Directory layout is useful prior evidence, but it must be checked against actual dependency edges.
- Cross-cluster edges are the important contract surface.
- Unobservable or dynamic relationships should become explicit findings/gaps rather than disappearing.

Practical implication for Build Arena: component candidates should be derived from graph communities seeded by project roots and directories. Contracts should be generated from cross-component graph edges.

## Independent Opus research memo summary

Claude Opus independently reviewed the problem and signed the same design direction at research-memo level. Its main verdict was:

- Collapse the arena-specific and generic paths into one manifest-anchored multi-root pipeline.
- Add project-root discovery, root-seeded clustering, edge-derived contracts, declared-task check discovery, and coverage repair with disciplined gaps.
- Add a check-executability gate and a no-identity-branch lint.
- Prove generality with warm-up and held-out repositories plus invariance tests.

The full Opus memo is saved at:

`docs/verification/2026-06-07-meta-decomposer-generalization/opus/opus-research-memo.md`

## Proposed meta-decomposer model

### Workspace

The git top-level remains the workspace boundary and provenance boundary. It is not automatically the execution root for every check.

### Project root

A project root is a directory with manifest/build evidence. Examples include Python, Node, Rust, Go, Make, Docker, and workspace manifests. The root owns:

- manifest evidence
- toolchain identity
- execution directory
- source/test/config nodes under its nearest-root scope
- declared tasks

Auxiliary files such as lockfiles, test configs, type configs, or Vite/pytest configs may reinforce a root but should not blindly create roots without source/build context.

### Component

A component is a responsibility-bearing cluster of graph nodes within one project root. It should be derived from:

- nearest project root
- directory structure
- package/module symbols
- deterministic dependency edges
- tests and config proximity
- cohesion/coupling thresholds

A component should not be a mere file bucket unless the model explicitly records a gap explaining why better structure could not be recovered.

### Contract

A contract is any meaningful relationship crossing component boundaries. Deterministic import/reference/test edges can directly support contracts. Weak or runtime-only relationships, such as frontend-to-backend HTTP coupling, should be represented as contracts with verification gaps when evidence exists but static proof is incomplete.

### Observable check

An observable check is not just a command. Functionally, it is:

- a purpose
- a command or task declaration
- an execution directory
- safety metadata
- provenance
- covered components/contracts
- proof or gap status

The model should never emit a runnable check at a directory without evidence that the command belongs there.

### Verification gap

A verification gap is a specific, scoped statement that a real surface or relationship is not yet mechanically verified. Gaps must be specific, typed, evidence-backed, and carry proposed closure checks. Blanket gaps should fail quality review.

## Anti-overfitting rules

The implementation must forbid:

- Branching on repository names.
- Branching on target-specific directory names to select semantic components.
- Hardcoding CMMC, FMC-MCP, Build Arena calibration, or any other project identity into decomposition logic.
- Fixed component taxonomies that force all projects into preselected domain labels.
- Fixed contract topologies.
- Fixed root-level check commands.
- Passing by assigning all unhandled files to a vague gap.

Allowed:

- Generic manifest-type tables.
- Generic language/toolchain recognizers.
- Generic path/graph heuristics.
- Generic safety allowlists.
- Generic exclusions for generated/vendor/cache artifacts.
- Validation fixtures that assert general behavior without steering implementation by identity.

## Acceptance criteria

Minimum acceptance for this implementation pass:

1. Existing Build Arena verification remains green.
2. A synthetic multi-root fixture passes: nested Python backend plus Node frontend, each with manifest-local checks.
3. Observable checks in the generated snapshot include execution-directory semantics in a deterministic, machine-readable way.
4. The CMMC decomposition improves versus the first run:
   - more primary source nodes owned or explicitly gapped
   - fewer inventory coverage violations
   - fewer edge coverage violations
   - more components that map to actual graph structure
   - checks scoped to `app/backend` and `app/frontend`, not a root-level `uv run pytest -q`
5. The implementation contains no CMMC/FMC repo-name branches or component identity hacks.
6. Opus reviews the research, functional spec, implementation plan, and final CMMC comparison.

Stretch acceptance:

- Add an explicit gate for check execution directory semantics.
- Add no-identity-branch lint.
- Add identity-blind/isomorphism tests.
- Add held-out project corpus beyond CMMC.

## Research verdict

Proceed with a project-agnostic implementation focused on these generic changes:

1. multi-root discovery from manifests
2. declared task/check discovery with cwd
3. root/directory/symbol seeded component clustering
4. edge-derived contract generation
5. disciplined coverage repair/gaps
6. anti-overfitting tests and gates

The purpose of the next CMMC run is to evaluate generalization improvement, not to make CMMC pass by special treatment.
