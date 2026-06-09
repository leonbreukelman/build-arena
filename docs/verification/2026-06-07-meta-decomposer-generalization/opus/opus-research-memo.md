# Research / Design Memo — Project-Agnostic Multi-Root Decomposition for Build Arena

**Reviewer:** Claude Opus (independent research/design reviewer)
**Date:** 2026-06-07
**Status:** Design memo (no implementation code).
**Validation fixtures referenced (only as fixtures):** FMC-MCP (passed), CMMC Level 1 readiness (failed).

---

## Context — why this memo exists

Build Arena must be a **meta-decomposer**: one decomposition algorithm that works on arbitrary repositories, not a hand-tuned decomposer per repo. Today it is the latter in disguise.

Grounding from the current code:
- `arena/decomposer.py::_looks_like_arena_calibration()` hard-matches on the literal file set `{arena/fixtures.py, arena/scorer.py, arena/verifier.py, arena/runner.py}` + `fixtures/*/manifest.yaml`, then `_arena_calibration_decomposition()` emits **hardcoded component IDs**, a **hardcoded 4-contract topology**, and gaps derived from literal keyword scans (`"lanham"`, `"hardcod"`, `"generaliz"`, `"lookup"`).
- Anything not matching that signature falls to `_generic_component_for_path()`: a path bucketer that emits **no contracts** and root-scoped checks only.
- Root discovery is **single-root**: `project_graph.py::_resolve_root()` uses `git rev-parse --show-toplevel`. `CONFIG_NAMES` recognizes `package.json`, `Cargo.toml`, etc., but they are only node tags — never used to partition the repo into subproject roots.
- Checks are emitted **at repo root unconditionally** (`uv run pytest -q`), independent of where the manifest that declares the test runner actually lives.

Consequences, measured:
- **FMC-MCP passed** because it is a single-root Python repo that fits the generic/arena-shaped assumptions.
- **CMMC failed** (1,774 nodes / 2,201 edges, only 8 components, 1 contract, 70 violations: 63 `inventory_coverage` + 7 `edge_coverage`). The emitted check `uv run pytest -q` was run from the repo root, where there is no Python project. The real checks live at subproject roots: `app/backend` → `uv run pytest -q`, `app/frontend` → `npm test -- --run` / `npm run build`.

The failure is not "CMMC is hard." It is that the pipeline has **no abstraction for a repository that contains more than one project**, and **no notion that a check has an execution directory**. Both gaps are project-agnostic to fix.

---

## 1. Best-practice principles

**From build systems and monorepo tooling:**
- A project root is a directory that declares a build/package manifest. The manifest's directory is the unit of toolchain identity and the execution root for that project's tasks.
- A repository is a forest of project roots, not a single tree.
- Tasks/targets are declared data (`package.json` scripts, pytest/tox/nox config, Makefile targets, CI workflow steps), not inferred conventions.
- Visibility/dependency edges are first-class: cross-package references are exactly the contracts that need governance.

**From software architecture recovery and clustering:**
- Recover modules by maximizing cohesion and minimizing coupling on the dependency graph.
- Directory layout and manifest boundaries are strong priors for clustering; pure graph community detection refines within those priors.
- Compare coarse hypothesized architecture from roots/directories against actual graph edges; divergences are findings, not invisible omissions.
- Cross-cluster edges are the contract surface.

**From static analysis discipline:**
- Distinguish observable facts from inferred facts.
- What cannot be observed statically must be recorded as a typed gap, not omitted.

**Synthesis principle:** manifests define roots; roots scope checks; the graph seeded by roots defines components; cross-cluster edges define contracts; everything unobservable becomes a typed gap.

---

## 2. Project-agnostic abstraction model

Repository → Workspace → ProjectRoots → Components and DeclaredTasks.

Each ProjectRoot has:
- manifest
- toolchain
- exec_dir
- components
- declared tasks

Contracts are edges crossing component boundaries. Observable checks are declared tasks bound to an execution directory and mapped to components/contracts. Verification gaps cover real but unobservable or currently unverified nodes/edges/contracts.

Key invariants:
- Every primary source node belongs to exactly one ProjectRoot and one Component, or is covered by a VerificationGap.
- Every ObservableCheck carries an exec_dir.
- Arena calibration and generic decomposition collapse into one path; Build Arena decomposing itself is just a Python project root at repo top.

---

## 3. Generic signals

### Root detection
- Primary signal: recognized manifest file in a directory.
- Nesting: nearest enclosing manifest defines source ownership; workspace manifests can act as containers.
- Lockfiles and auxiliary config reinforce roots but should not always create roots by themselves.
- No-manifest fallback: synthetic root plus explicit gap.

### Component clustering
- Use the existing node/edge graph.
- Seed clusters by `(ProjectRoot, directory)`.
- Merge/split deterministically by cohesion/coupling.
- Components never span roots.
- Names derive from dominant package/path/symbol evidence, not a fixed taxonomy.

### Contract inference
- Any edge crossing component boundaries becomes a contract.
- Intra-root contracts come from deterministic import/call/reference edges.
- Inter-root relationships without static edges become contracts-with-gaps when there is evidence such as HTTP clients, schemas, config, RPC/proto files, or CI integration.

### Observable check discovery
- Extract, don't assume.
- Node: `package.json` scripts such as test/build/lint/typecheck.
- Python: pytest/tox/nox/pyproject evidence and safe runner availability.
- Other ecosystems: Cargo, Go, Make, CI steps.
- Bind every check to the manifest directory.
- Prove executability before treating a check as accepted; otherwise record a gap.

### Coverage repair and gap semantics
- Compute coverage after clustering/check discovery.
- Assign uncovered nodes to nearest cohesive component when evidence supports it.
- Use typed, specific, capped gaps for genuinely unobservable items.
- Do not allow broad blanket gaps to game the gate.

---

## 4. Anti-overfitting rules

Forbidden:
1. Matching on repository name, file identity, directory identity, or component identity.
2. Domain/keyword allowlists steering control flow.
3. Fixed component taxonomies or fixed contract topologies.
4. Fixed root-level check command lists.
5. A warm-up repo registry.

Required tests:
- Code-invariance scan for warm-up/held-out repo names and hand-authored component IDs.
- Leave-one-out invariance.
- Identity-blind rename/isomorphism test.

---

## 5. Acceptance criteria

Per-repo:
- Existing gate passes.
- Inventory coverage is 100% owned-or-gapped.
- Cross-component edge contract/gap coverage is 100%.
- Emitted checks are executable at their exec_dir.
- Cluster count scales with graph size and cohesion/coupling, not fixed constants.
- Gaps are specific and capped.

Cross-corpus:
- Warm-up and held-out pass rates are close.
- Invariance tests pass.
- Multi-root repos emit checks from all relevant manifest roots and no checks from directories without manifests.

Verdict rule: Build Arena earns “meta-decomposer” status only when held-out repos pass without code changes and no project-identity-specific code paths exist.

---

## 6. Risks

- Clustering nondeterminism.
- Over/under-clustering from one global resolution.
- Invisible cross-process contracts.
- Declared checks requiring network/secrets.
- Unknown toolchains.
- Gap gaming.
- Workspace semantics and path aliases.
- Generated/vendored graph noise.
- Over-rotating on CMMC.

---

## 7. Opus verdict

Pursue one manifest-anchored, multi-root meta-decomposer pipeline:
1. workspace/root discovery
2. deterministic root-seeded graph clustering
3. edge-derived contracts
4. declared-task check discovery scoped to exec_dir and proven runnable
5. coverage repair with disciplined gaps

Add two gates:
- check-executability gate
- no-identity-branch lint

Prove with warm-up plus held-out shape-diverse repos. CMMC passing should mean the design generalized, not that it was taught CMMC.
