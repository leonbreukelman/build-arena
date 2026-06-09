# Functional Specification: Project-Agnostic Multi-Root Meta-Decomposer

Date: 2026-06-07
Project: Build Arena
Status: Revised after Opus review
Scope: Functional behavior only; no implementation code.

## 1. Purpose

Build Arena must produce Project Model decompositions for arbitrary repositories without custom logic for individual projects. This specification defines the required functional behavior for a project-agnostic multi-root meta-decomposer.

The immediate validation pressure comes from a CMMC decomposition failure, but CMMC must remain a held-out generalization signal. The implementation must not contain CMMC-specific, FMC-specific, or Build-Arena-calibration-specific decomposition branches.

## 2. Non-negotiable principles

1. One decomposer pipeline handles all repositories.
2. Repository identity must not steer decomposition.
3. Project roots are discovered from manifest/build evidence.
4. Component boundaries are derived from graph structure and source layout evidence.
5. Contracts are derived from cross-component relationships.
6. Observable checks must carry execution-directory semantics.
7. Unobservable or unverified surfaces become specific verification gaps, not silent omissions.
8. Clustering and output serialization must be deterministic for identical inputs.
9. Discovered commands are untrusted. A command may be modeled only with explicit safety status, execution-directory evidence, and either executable proof or a scoped gap explaining why proof was not obtained.
10. Existing anti-fabrication, provenance, no-live-paid-API, protected-surface, generated-surface, held-out-probe, and coverage gates remain binding.

## 3. Explicit anti-overfitting requirements

The decomposer must not:

- Branch on repository names.
- Branch on known target project names.
- Branch on CMMC, FMC-MCP, or Build Arena calibration identities.
- Use target-domain keyword lists to select semantic component names.
- Emit a fixed component taxonomy for all projects.
- Emit a fixed contract topology for all projects.
- Emit root-level check commands without root-local evidence.
- Assign all unhandled surfaces to one vague component or one broad verification gap.

The decomposer may use:

- Generic manifest and toolchain recognition tables.
- Generic source/test/config/documentation classification.
- Generic language parsers and import/reference graph evidence.
- Generic path, package, module, and directory cohesion signals.
- Generic safety allowlists for command execution.
- Generic generated/vendor/cache exclusions.

## 4. Conceptual model

### 4.1 Workspace

The workspace is the version-controlled repository boundary. It provides:

- Git root and commit identity.
- File inventory boundary.
- Provenance scope.
- Dirty-state reporting.

The workspace is not automatically the execution directory for all checks.

### 4.2 Project root

A project root is a directory with manifest/build evidence and source/build context. It is the functional unit for toolchain identity and task execution.

A project root records:

- Root path relative to the workspace.
- Manifest evidence.
- Toolchain family.
- Execution directory.
- Owned source/test/config/documentation scope.
- Declared or inferred safe local tasks.
- Whether it is executable, a container, or synthetic.

### 4.3 Workspace/container root

Some manifests define a workspace/container rather than a directly executable project. Examples include workspace manifests that point at child packages.

A container root may own workspace-level configuration and orchestration checks, but it must not steal source ownership from more specific child project roots.

### 4.4 Synthetic root

If source files exist without any recognized enclosing manifest/build evidence, the decomposer creates a synthetic root for ownership and records a verification gap explaining that execution semantics could not be proven.

If a child root has source context but incomplete executable evidence, it is represented as a synthetic root with a verification gap. The term partial root means this synthetic-root case; it is not a separate root category.

### 4.5 Component

A component is a responsibility-bearing cluster of graph nodes inside one project root.

A component records:

- Stable id.
- Human-readable name.
- Responsibility statement.
- Owned graph nodes.
- Provenance references.
- Related contracts.
- Related observable checks.
- Related verification gaps.

Components must not cross project-root boundaries in the initial implementation. Cross-root relationships are represented as contracts.

### 4.6 Contract

A contract is a relationship crossing component boundaries. It may be intra-root or inter-root.

A contract records:

- Stable id.
- Name.
- From component.
- To component.
- Supporting graph edges where available.
- Provenance references.
- Near-neighbor alternatives where appropriate.
- Related verification gaps if support is partial or indirect.

### 4.7 Observable check

An observable check is a local verification action with enough metadata to run and interpret it safely.

An observable check records:

- Stable id.
- Purpose/description.
- Command or task signal.
- Execution directory relative to workspace.
- Components and contracts it covers.
- Provenance references supporting the command.
- Safety metadata: safe-by-default, requires network, requires paid API.
- Acceptance-command metadata if it is part of the acceptance allowlist.
- Execution status: declared, safety-validated, execution-proven, or gapped.
- Linked verification gap when execution proof is absent or unsafe to attempt.

The execution directory is mandatory for every check. A command without an execution directory is incomplete.

Execution proof is not identical to safety. A check may be declared and safety-classified from manifest evidence without being accepted as proven. A check may be acceptance-allowlisted only when it is safe-by-default and either execution-proven or explicitly accepted by a separate operator-supplied proof artifact. Otherwise it remains a modeled check candidate with a gap, not a passing acceptance signal.

### 4.8 Verification gap

A verification gap is a scoped, evidence-backed limitation of the model.

A gap records:

- Stable id.
- Description.
- Severity.
- Covered components/contracts.
- Provenance references.
- Proposed closure check.

Gaps must be specific. Blanket gaps that cover arbitrary unhandled files or edges fail the quality bar.

### 4.9 Cross-cutting concern

A cross-cutting concern is a model-level invariant that applies across components, contracts, roots, or the whole workspace. It does not own source nodes. It records the concern category, affected components/contracts, provenance, and triggered-by evidence. Existing universal concerns remain required even when components are root-local.

## 5. Project-root discovery behavior

### 5.1 Primary root evidence

A directory becomes a project-root candidate when it contains manifest/build evidence such as:

- Python project metadata.
- Node package metadata.
- Rust package/workspace metadata.
- Go module metadata.
- Build/task metadata such as Make or equivalent.
- Recognized workspace manifests.

The evidence must be interpreted generically by manifest/toolchain type, not by project name.

### 5.2 Auxiliary evidence

Auxiliary files reinforce an existing root but should not necessarily create a root by themselves. Examples:

- lockfiles
- test configuration
- type-check configuration
- bundler configuration
- formatter/linter configuration
- environment-version files

These files can increase confidence in a nearby project root, help discover declared checks, and help classify toolchain, but they do not automatically define executable roots without source/build context.

### 5.3 Nested-root resolution

When roots are nested:

1. Each source/test/config node belongs to the nearest enclosing executable project root unless it is explicitly workspace-level configuration.
2. A parent workspace/container root may own workspace-level manifests, lockfiles, orchestration config, and root-level docs.
3. A parent root must not claim child source/test nodes that are under a more specific child executable root.
4. If both parent and child have executable manifests, child-owned paths remain child-owned; parent tasks may exist as orchestration checks if supported by root-local evidence.
5. If a child root lacks executable evidence but has source context, it is represented as a synthetic root with a verification gap.
6. Parent orchestration checks may mention child roots, but they do not automatically verify child components unless the check evidence explicitly invokes or covers those child-root tasks.

### 5.4 Root determinism

Root discovery must be stable across runs:

- Sort candidate paths deterministically.
- Resolve parent/child conflicts by fixed rules.
- Emit root identifiers from normalized relative paths and manifest types.
- Do not depend on filesystem traversal order.

## 6. Component clustering behavior

### 6.1 Inputs

The clustering stage uses:

- Project roots.
- File inventory nodes.
- Symbol/module nodes.
- Import/reference/test/config edges.
- Directory hierarchy.
- Manifest ownership.
- Provenance confidence.

### 6.2 Seed formation

Initial seeds are formed from generic evidence:

- Project root.
- Dominant source directory.
- Package/module namespace.
- Tests mapped to source modules.
- Config files mapped to the root or nearby component.

### 6.3 Merge and split behavior

The decomposer should merge or split seeds based on deterministic cohesion and coupling signals:

- Strong internal import/reference density supports merging.
- Strong cross-seed dependency concentration supports contract generation instead of blind merging.
- Tests and source with direct test edges should be grouped or linked in a way that preserves measurability.
- Generated/vendor/cache surfaces are excluded or handled under existing generated-surface rules.

### 6.4 Determinism

Clustering must be deterministic:

- Stable sorted input ordering.
- Stable tie-breaking.
- Fixed thresholds or threshold derivation from deterministic graph metrics.
- No non-seeded random behavior.

If a community-detection technique is used later, it must be configured to produce stable results or wrapped with deterministic ordering and tie-breaking.

### 6.5 Naming

Component names are derived from dominant structural evidence:

- package/module path
- top-level source directory under a root
- entrypoint or test mapping
- manifest/toolchain role

Names must avoid vague bucket labels unless accompanied by a gap that explains why semantic recovery failed.

### 6.6 Stable identifiers

Component identifiers are derived from normalized structural evidence rather than discovered domain labels. The identifier basis is the project-root id plus the dominant package/module/directory seed. If a component changes only because a repository directory is renamed, the decomposition should remain structurally isomorphic with remapped identifiers.

Contract identifiers are derived from the normalized from-component id, to-component id, and relationship kind. Aggregated contracts preserve all supporting evidence even when the stable identifier is pair-based.

## 7. Contract discovery behavior

### 7.1 Deterministic contract support

A contract is generated when deterministic graph evidence crosses component boundaries, including:

- import edges
- reference edges
- test-to-source edges
- config-to-source or build-to-source edges where supported

The direction follows graph semantics. For imports, the importer is the consumer and the imported component is the provider.

### 7.2 Contract aggregation

Multiple edges between the same component pair may be aggregated into one contract when they represent the same dependency relationship. Aggregation must preserve supporting edge ids and provenance.

### 7.3 Inter-root contracts

Cross-root relationships are high-value, but indirect discovery must not become domain-specific guessing.

If deterministic static edges exist, they support contracts directly.

If no deterministic edge exists, the decomposer may record an indirect inter-root contract only when the relationship is supported by generic, typed evidence. Allowed typed evidence includes:

- a machine-readable schema or protocol artifact referenced by both roots;
- a generated client/server artifact with provenance linking it to another root;
- a CI/task/workspace declaration that explicitly invokes tasks in more than one root;
- a config value whose parser identifies a generic protocol/address/reference form and whose provenance is tied to a root-owned client/server surface;
- a test fixture or integration test whose path/provenance references files from multiple roots.

Forbidden indirect evidence includes project-domain keyword matches, target-specific route-name lists, and repository-specific assumptions. When evidence is weak or only suggestive, the model must create a verification gap instead of a supported contract.

### 7.4 Contract coverage

Every owned cross-component import/reference/test edge must be covered by a contract or a specific verification gap.

## 8. Observable-check discovery behavior

### 8.1 Check extraction

Checks are extracted from project-root-local evidence such as:

- package scripts
- Python test/tool config
- Make or task runner targets
- CI workflow steps mapped to a root
- language-standard test/build commands when supported by manifest evidence

The decomposer must prefer declared tasks over guessed commands.

### 8.2 Execution directory

Every check is bound to an execution directory. The execution directory is normally the project root that declares the task.

A workspace-level check may be emitted only when there is workspace-level evidence for it.

### 8.3 Check safety

Discovered commands are untrusted. Before a check can be acceptance-allowlisted or considered safe-by-default, it must pass generic safety rules:

- No live paid API requirement by default.
- No network requirement by default unless explicitly marked unsafe for default acceptance.
- No destructive filesystem or VCS operations.
- No credential exposure.
- No deployment/publish/release commands.
- No shell constructs outside the safe command subset unless explicitly blocked or gapped.

Unsafe checks are not accepted checks. They can be represented as declared candidates linked to verification gaps with proposed closure.

### 8.4 Executability proof

A check has two independent statuses:

1. Safety status: whether the command is safe-by-default, unsafe, requires network, requires paid API, destructive, or unknown.
2. Execution status: whether the command is declared-only, statically validated, execution-proven, or gapped.

Execution-proven means the command was run successfully in the recorded execution directory under the safe boundary, or an explicit local proof artifact records that result.

Statically validated means the command was found in root-local manifest/task evidence and passes generic safety parsing, but was not run during decomposition.

Declared-only means the command was found but has not yet passed safety validation.

Gapped means execution proof was not obtained, was unsafe to attempt, required missing dependencies, required network/paid API, or otherwise could not be made acceptance-grade.

Acceptance checks must be safe-by-default and execution-proven unless a separate operator-supplied proof artifact is explicitly attached. Non-acceptance checks may be statically validated if they are linked to gaps where proof is missing.

### 8.5 Mapping to components/contracts

Checks are mapped to components and contracts using:

- Path containment under the project root.
- Test-to-source edges.
- Manifest script scope.
- Supporting contract edges.

A root-level test command for a backend should not claim to verify an unrelated frontend unless evidence supports that mapping.

## 9. Coverage and gap behavior

### 9.0 Node classification for coverage

Nodes are classified before coverage gates run:

- Primary source nodes: first-party source symbols/modules/files that define runtime or library behavior.
- Primary test nodes: first-party tests and fixtures that verify primary source behavior.
- Primary config/build nodes: manifests, task declarations, schemas, migrations, and configuration that shape build/runtime/test behavior.
- Documentation nodes: docs and markdown/rst guidance.
- Generated/protected/vendor/cache nodes: excluded or governed by their existing dedicated rules.

Primary source, primary test, and primary config/build nodes require ownership or a specific verification gap. Documentation nodes require ownership or a documentation-specific gap. Generated/protected/vendor/cache nodes must not be silently owned as normal source; they are excluded or handled by protected/generated-surface rules.

Tests may be owned by a test/verification component or by the component whose behavior they primarily verify. Either is acceptable if the ownership is deterministic and measurability is preserved.

### 9.1 Node coverage

Every primary node subject to ownership must be:

- owned by exactly one component, or
- covered by a specific verification gap.

### 9.2 Edge coverage

Every owned cross-component edge relevant to architecture must be:

- covered by a contract, or
- covered by a specific verification gap.

### 9.3 Gap discipline

A gap is acceptable only if:

- it references concrete provenance;
- it identifies specific affected components/contracts;
- it explains what is unverified;
- it includes a proposed closure check;
- it is not a blanket placeholder for arbitrary leftovers.

## 10. Schema and compatibility behavior

### 10.1 ObservableCheck extension

The project snapshot/model must expose execution-directory semantics for checks. Existing consumers must be migrated or given a compatibility representation.

Functional requirement: a reader of `project-model-v1.json` and `snapshot.json` must be able to determine where each check should run.

### 10.2 Backward compatibility

Existing snapshots without execution-directory fields may be read as legacy artifacts, but newly generated snapshots must include execution-directory semantics.

### 10.3 Projection behavior

Project Model v0 compatibility output should preserve or explain check execution directory information where the older schema lacks a native field.

## 11. Gate behavior

### 11.1 Existing gates

Existing gates continue to apply:

- schema validity
- snapshot freshness
- inventory coverage
- component measurability
- contract references
- edge coverage
- cross-cutting concerns
- no-live-paid-API acceptance
- provenance completeness
- protected/generated surface integrity
- near-neighbor alternatives
- held-out probe presence/isolation/discrimination
- verification gap validity

### 11.2 New or strengthened gates

The updated gate behavior should include:

1. Check execution-directory presence for every observable check.
2. Rejection of acceptance checks whose execution directory lacks supporting project-root evidence.
3. Rejection of unsafe accepted commands under generic safety rules.
4. Acceptance checks must be safe-by-default and execution-proven unless an operator-supplied proof artifact is attached.
5. Non-acceptance checks may be statically validated but must expose their execution status and any missing-proof gap.
6. No-identity-branch lint in tests or verification to prevent project-specific logic.

## 12. Validation corpus behavior

### 12.1 Warm-up projects

Warm-up projects may be inspected during development and used for regression tests, but they must not appear in decomposition logic.

### 12.2 Held-out projects

Held-out projects are used to evaluate generalization. CMMC is one such held-out shape signal for this pass.

### 12.3 Required validation for this pass

This implementation pass must validate at least:

1. Existing Build Arena tests pass.
2. A synthetic nested multi-root fixture passes deterministically.
3. CMMC decomposition improves versus the first run without project-specific code.
4. Opus reviews the resulting CMMC model and comparison.

### 12.4 Preferred validation beyond this pass

The decomposer should later be evaluated on additional shape-diverse held-out repos:

- TypeScript monorepo/workspace.
- Rust workspace.
- Go module or multi-module repo.
- Python src-layout library.
- Polyglot repo.

## 13. Success metrics

For the CMMC rerun, compare against the first failed snapshot:

- Number of graph nodes.
- Number of components.
- Number of contracts.
- Number of observable checks.
- Execution directories of checks.
- Gate pass/fail.
- Inventory coverage violations.
- Edge coverage violations.
- Primary source nodes owned or explicitly gapped.
- Cross-component edges contract-covered or explicitly gapped.
- Presence or absence of root-level incorrect checks.
- Specificity and usefulness of verification gaps.

Required improvement floor for this pass:

1. The generated model must not emit the prior incorrect root-level `uv run pytest -q` as the only target check for CMMC.
2. The model must include check execution-directory semantics for backend and frontend roots when those roots are detected from generic manifest evidence.
3. Inventory coverage violations must decrease, or the model must provide specific verification gaps that explain any remaining uncovered primary nodes.
4. Edge coverage violations must decrease, or the model must provide specific contracts/gaps that explain remaining cross-component edges.
5. Any metric regression must be explained and must not be caused by project-specific logic.

Improvement must be explained by generic behavior, not by target-specific hacks.

## 14. Functional acceptance decision

The implementation is acceptable for this pass if:

1. It passes Build Arena’s verification suite.
2. It adds and passes a synthetic multi-root test.
3. It generates check execution-directory semantics.
4. It improves CMMC model quality and completeness versus the first run under the improvement floor in section 13.
5. It does not introduce project identity branches.
6. It produces durable artifacts: research report, Opus sign-offs, functional spec, implementation plan, before/after CMMC comparison, Opus model review, and final findings.

The implementation is not acceptable if CMMC improves only because CMMC-specific logic was added.
