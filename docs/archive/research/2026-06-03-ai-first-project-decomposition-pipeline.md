# AI-first project decomposition pipeline for Build Arena

Date: 2026-06-03
Repo: `/home/leonb/projects/build-arena`
Branch observed during research: `coverage-100`
Working tree note: this research was written on a tree that already had multiple untracked docs and verification artifacts. This report only adds `docs/research/2026-06-03-ai-first-project-decomposition-pipeline.md`.

## 1. Direct verdict

Current decomposer is not sufficient for the intended Build Arena test run.

It is useful as a deterministic inventory, ownership, and structural quality gate. It is not the intended Build Arena decomposer: an AI-first project-understanding pipeline that builds a provenance-backed project encyclopedia from filesystem, code, docs, issues, configs, and workflow truth, then uses LLM agents to recursively decompose the project into components, contracts, cross-cutting concerns, observable checks, held-out probes, and verification gaps.

The current Project Model v0 path should not be frozen as the run contract. It can remain as a thin compatibility contract and scanner/gate substrate, but the next architecture must be:

`graph/wiki/index -> LLM decomposer -> recursive components/contracts/checks -> deterministic gate`

That pipeline needs a stronger provenance and snapshot layer than Project Model v0 currently exposes. The existing v0 wire model has components, dependencies, invariants, checks, risks, probes, gaps, and unclassified surfaces, but it does not carry mandatory file-span provenance, git object identity, content hashes, coverage, or graph snapshot identity. Those are not optional polish; they are the anti-fabrication anchor.

No Build Arena autonomous test run should start from the current classified JSON. It should be treated as evidence of the shallow path-classification approach and as a compatibility artifact, not as an approved decomposition of Build Arena.

## 2. Current decomposer diagnosis

### What it does

The current code provides a deterministic scanner and adapter:

- It discovers project files from git/filesystem truth.
- It records file inventory, hashes, typed exclusions, and git state in the internal scanner model.
- It maps files to components.
- It emits mechanical checks, contracts, cross-cutting concerns, and verification gaps.
- It exports Project Model v0 JSON through an adapter.
- It runs a deterministic quality gate that rejects missing components, missing observable checks, missing check references, vague components, missing dependencies, bad dependency references, unclassified project surfaces, and high-risk components without held-out probes.
- It keeps Project Model emission and validation no-live-API by design.

There are two important implementation shapes:

1. Generic path classification.
   The generic branch maps paths by syntax and location: `tests/` becomes `regression_tests`, `docs/` and markdown become documentation, Python files become `python_package`, known config files become `project_configuration`, and the remainder becomes `unclassified_project_surface`.

2. Arena-calibration special casing.
   The code has a detector for an arena-calibration-like repo. If it sees files such as `arena/fixtures.py`, `arena/scorer.py`, `arena/verifier.py`, `arena/runner.py`, and fixture manifests, it assigns files to hand-authored components such as fixture manifest model, mechanical scorer, reasoning ablation verifier, provider boundary, runner discrimination matrix, regression tests, documentation, configuration, and package marker. It also derives the high-severity `patch_generalization_axis_missing` gap by reading fixture manifests whose ground truth indicates `bad_passes_tests` / scorer promote / verifier reject with rationale terms such as Lanham, hardcoding, generalization, or lookup.

That is better than an arbitrary one-shot LLM summary. It is deterministic and inspectable. It is not enough.

### What it does not do

The current decomposer does not build an AI-first project understanding model:

- It does not build an AST/symbol/call/import graph beyond path/file inventory and hand-coded path rules.
- It does not recover architecture from code relationships, docs, workflows, specs, issues, generated artifacts, and operational constraints.
- It does not create a provenance-backed wiki or encyclopedia with source spans and claim-level citations.
- It does not recursively decompose components until leaves are mechanically testable.
- It does not use LLM agents to propose or challenge responsibilities, contracts, risks, cross-cutting axes, probes, or verification gaps.
- It does not isolate held-out probes from the decomposer that proposes the model.
- It does not distinguish wiki prose as a navigational cache from graph edges as ground truth.
- It does not carry mandatory provenance in Project Model v0. The v0 schema has no primitive for path plus line or byte span plus content hash plus derivation method.
- It does not carry git object identity, coverage, or file hashes in the v0 wire artifact. The internal scanner has this information, but the adapter drops it when emitting `project-model/v0`.
- It does not provide per-mode structural constraints for observable checks. A check can say it is a test, static analysis, artifact audit, inspection rubric, simulation, or stakeholder decision, but the gate does not yet require a command for runnable modes, an artifact path for artifact audit, a rubric for inspection, or a recorded decision id for stakeholder decision.
- It does not solve the model-use boundary. A future AI-first decomposer should use leading LLMs early to get the architecture right, starting with Grok, while deterministic acceptance tests remain local/hermetic and do not depend on paid live API calls.

### Why that blocks the intended run

Build Arena's risk is not only missing files. The project exists to prevent coherent automation from optimizing the wrong target. File ownership coverage is necessary, but it can still certify the wrong decomposition.

The current model can pass a quality gate by grouping every tracked file under plausible component labels. That proves there are no unowned included files and no obvious structural dangling references. It does not prove the components are the right units, that the contracts are load-bearing, that cross-cutting concerns are represented, that non-code process/spec/operator surfaces are understood, or that held-out probes test the actual high-risk failure modes.

This is the F3 danger at the decomposer layer: the agent can build a coherent ruler aimed at the wrong project target. A Build Arena test run driven by that ruler would produce attractive evidence while measuring the wrong thing.

## 3. Target architecture

The target pipeline should be a staged, provenance-first system:

1. Raw inventory layer
   Git and filesystem ground truth. This layer owns tracked files, untracked/dirty state, content hashes, typed exclusions, generated/oracle/fixture protection, and git object identity.

2. AST/symbol graph layer
   Static code structure. This layer extracts modules, packages, imports, classes, functions, public APIs, tests, fixtures, CLI entry points, config references, generated outputs, and where possible call/name-binding relationships.

3. Semantic graph layer
   Non-code and cross-surface truth. This layer links docs, specs, plans, verification reports, runbooks, issue references, configs, CI/workflow files, Makefile targets, generated artifacts, protected boundaries, and operational constraints.

4. AI-friendly wiki/encyclopedia layer
   Provenance-backed pages that explain modules, symbols, workflows, risks, contracts, commands, invariants, and unresolved gaps. These pages are for humans and LLM context routing. They are not authoritative by themselves; every claim must link back to graph nodes and source spans.

5. LLM decomposition layer
   LLM agents read bounded, provenance-backed context bundles and propose recursive components, responsibilities, contracts, cross-cutting concerns, observable checks, held-out probe ideas, near-neighbor alternatives, and verification gaps. LLM outputs are advisory until the deterministic gate accepts their structure and provenance.

6. Deterministic gate layer
   Structural and evidence checks that decide whether a decomposition may drive an autonomous run. This layer never asks an LLM if the decomposition is good. It verifies coverage, provenance, measurability, reference integrity, dependency consistency, held-out probe presence/isolation, no-live-API policy, protected surface handling, and snapshot freshness.

7. Storage/projection layer
   Versioned snapshots tied to git OID/run id/tool versions. JSONL remains the canonical event stream for Build Arena state. SQLite/FTS and graph edge tables are query projections. Wiki pages and summaries are content-addressed derived artifacts, invalidated on drift.

The operational shape is:

`git/filesystem truth -> code/doc/issue graph -> provenance-backed encyclopedia -> LLM recursive model proposal -> deterministic acceptance gate -> operator approval -> frozen decomposition snapshot -> autonomous Build Arena run`

In this report, `operator approval` means one simple owner checkpoint before an autonomous run is allowed: does the proposed decomposition target the right project goal and may Build Arena run from this frozen snapshot? It does not mean Leon must choose schema mechanics, model orchestration details, check weights, probe construction mechanics, dirty-tree policy, or pilot repo selection. Those are implementation defaults owned by the agent and recorded in the artifact.

## 4. Proposed data model

### ProjectGraph

Authoritative graph snapshot for one project at one git/disk state.

Core fields:

- `id`
- `projectRoot`
- `gitOid`
- `dirtyState`
- `inventoryHash`
- `toolVersions`
- `nodes`
- `edges`
- `coverage`
- `protectedSurfaces`
- `generatedSurfaces`
- `oracleSurfaces`
- `createdAt`

Node types:

- file
- directory
- package/module
- class
- function/method
- test
- fixture
- command
- config key
- doc section
- issue/backlog item
- workflow/CI job
- generated artifact
- runtime artifact
- schema
- external interface

Edge types:

- contains
- imports
- calls
- defines
- tests
- configures
- generates
- generatedFrom
- documents
- constrains
- consumes
- produces
- protects
- violatesBoundaryIfEdited
- referencesIssue
- hasCommand
- hasEvidence

Every node and edge needs provenance.

### Provenance

This should be a first-class required object, even though it was not in the requested list, because it is the anti-fabrication anchor.

Fields:

- `path`
- `span` with line range or byte range when applicable
- `contentHash`
- `gitOid` or disk snapshot id
- `derivedBy` such as `git`, `tree-sitter`, `python-ast`, `grimp`, `doc-parser`, `llm`, or `operator`
- `confidence` for advisory claims
- `notes` for limits of extraction

Mandatory provenance should attach to Component, Contract, CrossCuttingConcern, ObservableCheck, HeldOutProbe, VerificationGap, WikiPage claims, and ProjectGraph edges. A top-level provenance list is not enough because it can drift away from the claim it is meant to ground.

### WikiPage / EncyclopediaPage

AI-friendly pages generated from ProjectGraph and source truth.

Fields:

- `id`
- `title`
- `pageType` such as module, workflow, command, boundary, risk, architecture, test surface, issue, component candidate
- `summary`
- `claims`
- `sourceRefs`
- `graphNodeRefs`
- `outgoingLinks`
- `incomingLinks`
- `unknowns`
- `lastBuiltFromSnapshot`
- `contentHash`

Rules:

- Wiki pages are context, not ground truth.
- Each factual claim must cite graph nodes or source spans.
- LLM-generated prose must not become the only evidence for another LLM decision.
- Pages should be short enough for agent context bundles and stable enough to diff.

### Component

Recursive unit of decomposition.

Fields:

- `id`
- `name`
- `level`
- `parentComponentId`
- `kind`
- `responsibility`
- `ownedGraphNodes`
- `ownedSurfaces`
- `entrypoints`
- `publicInterfaces`
- `observableCheckIds`
- `contractIds`
- `crossCuttingConcernIds`
- `riskLevel`
- `provenance`
- `status` such as candidate, accepted, rejected, needs-operator-decision

A component is not just a folder or file bucket. It is a responsibility-bearing unit with explicit interfaces, checks, risks, and evidence.

### Contract

Assume-guarantee object between components.

Fields:

- `id`
- `producerComponentId`
- `consumerComponentId`
- `kind`
- `assumptions`
- `guarantees`
- `interfaceRefs`
- `observableCheckIds`
- `failureModes`
- `rationaleForCycle` if cyclic
- `provenance`

Contracts are required because Build Arena must avoid improving units in isolation while breaking integration. Contracts should cover code interfaces, data formats, generated artifacts, CLI behavior, config semantics, workflow sequencing, operator approval boundaries, and external provider seams.

### CrossCuttingConcern

Orthogonal axis that cuts across the hierarchy.

Fields:

- `id`
- `name`
- `description`
- `affectedComponentIds`
- `graphNodeRefs`
- `observableCheckIds`
- `riskLevel`
- `ownerDecisionRequired`
- `provenance`

Examples:

- no live paid API inside acceptance tests by default; model calls for decomposition/review are allowed in the model phase and recorded
- anti-fabrication and source-before-claim discipline
- fixture/oracle protection
- generated artifact reproducibility
- determinism
- security/privacy
- observability
- performance budget
- documentation/spec drift
- rollback safety

### ObservableCheck

A check that produces an observable signal.

Fields:

- `id`
- `componentId` or `contractId` or `concernId`
- `mode`
- `description`
- `signal`
- `command` for runnable checks
- `artifactPath` for artifact audits
- `staticQuery` for static analysis
- `rubricPath` for inspection rubric
- `decisionRecordRef` for stakeholder decision
- `noLiveApi`
- `timeout`
- `expectedArtifacts`
- `provenance`

Modes should have structural requirements:

- `test`: command, timeout, no-live-API flag, expected pass/fail semantics
- `static-analysis`: command or query, target paths, expected finding policy
- `artifact-audit`: artifact paths and deterministic audit rules
- `simulation`: command and fixture inputs
- `inspection-rubric`: rubric path, reviewer role, evidence record
- `stakeholder-decision`: decision id, owner, and exact question being decided

A leaf is mechanically testable only when its observable checks have concrete execution or audit semantics. If a stakeholder decision is required, it is observable but not autonomous; the run must stop for that decision.

### HeldOutProbe

A counterexample or probe not visible to the decomposer proposal path.

Fields:

- `id`
- `componentId` or `contractId` or `concernId`
- `probeType`
- `scenario`
- `expectedBehavior`
- `hiddenFromRoles`
- `constructedBy`
- `evidenceRequired`
- `activationPolicy`
- `provenance`

Held-out probes are hidden exam questions for the decomposition. Example: after the decomposer proposes the project structure, a probe may check whether it remembered that `schema/`, `scorer/`, `verifier/`, generated artifacts, and oracle fixtures have special protection instead of treating them as ordinary improvable code. The decomposer must not see the exact probe before proposing the model. By default, Hermes owns this: use a separate skeptic/probe-builder lane, do not include probe text in decomposer prompts, and record prompt hashes/model ids/probe activation evidence. Leon should not have to author these probes.

### VerificationGap

Explicit unknown or unverifiable leaf.

Fields:

- `id`
- `severity`
- `affectedComponentIds`
- `affectedContractIds`
- `description`
- `whyNotMechanicallyTestableYet`
- `evidence`
- `proposedClosureCheck`
- `ownerDecisionRequired`
- `expiresOnDrift`
- `provenance`

A verification gap is acceptable only when it is explicit, scoped, evidenced, and carried into the gate. It is not a miscellaneous bucket.

### ProjectModelSnapshot

Frozen, versioned artifact that may drive a run after passing gate and operator approval.

Fields:

- `id`
- `schemaVersion`
- `gitOid`
- `dirtyState`
- `graphSnapshotId`
- `graphHash`
- `wikiSnapshotHash`
- `modelHash`
- `toolVersions`
- `llmModelIds`
- `promptHashes`
- `operatorApprovalRef`
- `qualityGateReportRef`
- `createdAt`
- `invalidatedByDrift`

A stale snapshot must fail before an autonomous run starts.

## 5. Tooling comparison

### Recommended first

Git and filesystem scanner

- Use current scanner as the raw inventory foundation.
- Keep `git ls-files`, raw-byte hashing, typed exclusions, dirty/untracked reporting, and protected generated/oracle/fixture handling.
- Do not treat cached scanner output as truth. Rebuild from disk/git for each candidate snapshot.

Python `ast`

- Local, dependency-light, deterministic for Python syntax.
- Good for modules, classes, functions, imports, decorators, docstrings, and basic call/name references.
- Does not solve multi-language support or full semantic resolution.

Tree-sitter

- Tree-sitter is a parser generator and incremental parsing library that builds concrete syntax trees and supports many languages.
- Use it for multi-language syntax structure, robust parsing of partial code, and language-agnostic extraction of nodes/spans.
- It gives concrete syntax, not full semantics. It does not by itself solve name binding, type inference, or cross-file architecture.

Grimp and import-linter

- Grimp builds a queryable graph of imports within Python packages.
- Import-linter imposes constraints on Python module imports and can expose architecture violations.
- Good for Build Arena's Python import graph and future contract checks.
- Python-only and import-level; not enough for calls, protocols, generated artifacts, or docs/process surfaces.

Ruff

- Fast local Python linter/formatter with many rules.
- Keep as an observable static-analysis check and a source of lint findings.
- Ruff is not an architecture recovery tool.

Pyright or basedpyright

- Static type checking and import/name understanding for Python.
- Useful as an observable check and as a source of type/import errors.
- It should not be treated as a complete component graph.

SQLite with FTS and explicit edge tables

- Recommended first storage/query layer.
- Local-first, deterministic, easy to diff/export, simple to tie to JSONL events and content hashes.
- Use FTS for text search and explicit tables for graph edges rather than vector-only retrieval.

Markdown encyclopedia / LLM Wiki pattern

- Use the wiki pattern: continuously rebuilt, structured, provenance-linked pages that help agents and humans navigate the project.
- Keep it local-first and source-linked.
- Treat generated pages as cache/projection, not as authoritative truth.

### Useful but deferred

ast-grep

- ast-grep is a fast polyglot structural search/rewrite/lint tool using AST patterns.
- Good for later contract checks and structural smell detection.
- Defer until the graph prototype identifies repeated structural checks worth encoding.

SCIP / LSIF

- SCIP is a language-agnostic code intelligence protocol for definitions, references, and implementations and is the modern successor path in the Sourcegraph ecosystem.
- Useful when Build Arena needs precise code navigation across larger or multi-language repos.
- Defer until simple Python AST plus Tree-sitter plus import graph is insufficient.

CodeQL

- CodeQL treats code as queryable data and extracts AST, name binding, type, and semantic information, especially for vulnerability/security analysis.
- Powerful for security and semantic queries.
- Heavy for the first prototype and may require build extraction for compiled languages. Use later for security-critical gates or when query sophistication justifies the cost.

Sourcegraph-style code graph

- Sourcegraph's code graph concept uses definitions, references, symbols, doc comments, and relationships rather than plain text.
- This is the right conceptual direction.
- Do not require Sourcegraph infrastructure for acceptance. Adopt the local concept first with SQLite/edge tables.

Graph databases

- Neo4j, RDF stores, or other graph DBs are not needed for the first Build Arena decomposer.
- A graph DB may help with large multi-repo traversal later, but it adds operational surface and schema migration complexity.

Embedding search

- Useful as an auxiliary recall layer.
- Not sufficient as the main architecture because vector hits do not prove provenance, completeness, or contracts.
- If used, embeddings must point back to content-addressed source spans and graph nodes.

### Rejected as primary architecture

- Random repo reads by an LLM.
- One-shot summarization of a repository.
- Vector-only RAG with no explicit graph/provenance.
- File ownership accounting as the definition of decomposition.
- Hardcoded path classifiers as the core model.
- A paid live API as a required acceptance path.

## 6. Anti-patterns and mitigations

1. Random repo reads by an LLM
   Mitigation: route every LLM prompt through bounded context bundles built from ProjectGraph, encyclopedia pages, and source spans.

2. One-shot summarization
   Mitigation: recursive decomposition with critique, counterexamples, gate checks, and operator approval.

3. Vector-only RAG with no provenance
   Mitigation: embeddings can assist recall, but every retrieved chunk must point to content-addressed spans and graph nodes.

4. File ownership accounting mistaken for decomposition
   Mitigation: coverage is only one gate. Components need responsibilities, interfaces, contracts, checks, risks, and provenance.

5. Hardcoded path classifiers
   Mitigation: path rules may seed candidates, but architecture claims require graph evidence, docs/process evidence, or operator decisions.

6. Cached project models treated as truth
   Mitigation: snapshots are invalidated by git OID, dirty state, graph hash, wiki hash, tool versions, and prompt/model changes.

7. LLM self-judgment as verification
   Mitigation: LLM outputs are advisory. Deterministic gates and held-out probes decide whether the model may drive a run.

8. Miscellaneous or general components
   Mitigation: vague component ids should fail. Unknown surfaces become explicit `VerificationGap` or `UnclassifiedProjectSurface` with candidate owners and closure checks.

9. No contract objects between units
   Mitigation: every meaningful dependency/interface should be represented as an assume-guarantee Contract with observable checks or gaps.

10. No cross-cutting decomposition axis
   Mitigation: represent concerns such as no-live-API, generated artifact integrity, fixture protection, privacy, determinism, and documentation drift outside the component tree.

11. No held-out probes
   Mitigation: high-risk components and contracts require counterexamples or hidden probes, and the decomposer must not see probe content.

12. No deterministic gate
   Mitigation: fail before autonomous execution unless coverage, provenance, measurability, references, dependencies, probes, and snapshot freshness pass.

13. No owner checkpoint before freezing the run target
   Mitigation: the model becomes runnable only after one plain-English owner checkpoint: the decomposition is aimed at the right goal and Build Arena may run from the frozen snapshot. Hermes owns schema mechanics, probe construction, check details, pilot selection, and implementation defaults unless Leon corrects them.

14. Overfitting to Build Arena itself
   Mitigation: evaluate on self-host Build Arena, a warm-up small repo, and a held-out different repo. Keep fixture/oracle data hidden from optimization.

15. Treating fixture, oracle, or generated data as ordinary improvable source
   Mitigation: mark these surfaces in ProjectGraph and gate write eligibility. Generated outputs must be regenerated from sources. Oracle fixtures must be protected unless the operator explicitly starts a fixture-update task.

16. Wiki prose fed back as truth
   Mitigation: wiki pages are navigational caches. The decomposer must cite source spans and graph edges, not only wiki summaries.

17. Live API acceptance by accident
   Mitigation: decomposition/review may use Grok or another leading model during the model phase, but the final acceptance gates for an autonomous run must be reproducible without paid live API calls unless the run mode explicitly says otherwise. Model ids, prompt hashes, and outputs are recorded in the snapshot.

## 7. Deterministic gates required before a decomposition can drive a run

A decomposition can drive an autonomous Build Arena run only if these gates pass:

1. Inventory and coverage gate
   - Every significant tracked surface is owned or explicitly excluded with a typed reason.
   - Generated, runtime, oracle, and fixture surfaces are classified and protected.
   - Untracked/dirty state is recorded and either accepted by operator or blocks freezing.

2. Snapshot freshness gate
   - ProjectModelSnapshot ties to git OID, dirty-state fingerprint, inventory hash, graph hash, wiki hash, tool versions, prompt hashes, and model ids.
   - Any drift invalidates the snapshot before execution.

3. Provenance gate
   - Every component, contract, concern, check, probe, and gap has source provenance.
   - LLM-derived claims are marked as such and supported by source spans or operator decisions.
   - Claims without provenance fail or become verification gaps.

4. Component gate
   - Each component has a responsibility, owned graph nodes/surfaces, risk level, provenance, and at least one observable check or explicit verification gap.
   - Vague ids like misc/general/common fail.

5. Observable check gate
   - Each check maps to a runnable command, static query, artifact audit, simulation, inspection rubric, or stakeholder decision.
   - Runnable checks specify command, timeout, referenced paths, expected artifacts or pass policy, and no-live-API policy.
   - Stakeholder decision checks name the owner-level decision and cannot be consumed as autonomous acceptance.

6. Contract gate
   - Contract endpoints exist.
   - Each contract has assumptions, guarantees, interface/evidence refs, and a check or explicit gap.
   - Dependency graph cycles fail unless intentionally cyclic with rationale and observable integration checks.

7. Cross-cutting concern gate
   - Required concerns are present: no-live-paid-API for acceptance tests by default, explicit model-use recording for decomposition/review, anti-fabrication/provenance, deterministic outputs, protected generated/oracle/fixture surfaces, rollback boundaries, documentation/spec drift, provider boundary when relevant.

8. Held-out probe gate
   - High-risk components/contracts have held-out probes or counterexamples.
   - Probe contents are isolated from the decomposer role.
   - Probe construction and activation policy are recorded.

9. Verification gap gate
   - Unknowns are explicit, scoped, severity-ranked, evidenced, and paired with proposed closure checks or owner decisions.
   - A gap cannot be hidden by passing coverage.

10. No-live-API acceptance gate
   - Acceptance tests do not require live paid API calls in the default mode.
   - Grok-first or other leading-model decomposition/review is allowed in the model phase and must be recorded separately from acceptance tests.
   - Local/hermetic degraded mode must still emit graph, inventory, wiki, gaps, and a gate report.

11. Protected surface gate
   - `scorer/`, `verifier/`, `schema/`, `.arena/scorer.lock.toml`, and `arena/generated/` boundaries from AGENTS.md are represented and enforced for arena-generated hypotheses.
   - Fixture/oracle data is protected from ordinary optimization.

12. Run-freeze checkpoint
   - Before autonomous execution, Hermes presents a short owner-facing summary of the proposed target, non-goals, major gaps, and run mode.
   - Leon's role is only to correct the target or allow the run. Hermes owns implementation defaults and should not ask Leon to tune schema mechanics, probe construction, check weights, or pilot selection.

## 8. Recursive decomposition algorithm

### Inputs

- Project root and git toplevel.
- Git OID, dirty status, inventory, content hashes, typed exclusions.
- AST/symbol/import graph.
- Semantic graph from docs, issues, specs, configs, workflows, generated artifacts, plans, verification reports, and AGENTS.md rules.
- Provenance-backed encyclopedia pages.
- Primary task/backlog item and non-goals.
- Protected surfaces and operator constraints.
- Existing checks and commands.
- Existing Project Model v0 output as a compatibility artifact, not as ground truth.

### Agent roles

1. Index builder
   Deterministic tool role. Builds raw inventory, code graph, doc graph, command graph, and edge tables. No LLM authority.

2. Encyclopedia writer
   LLM-assisted but provenance-constrained role. Writes compact pages with citations to graph nodes and source spans. Outputs pages as derived cache, not truth.

3. Decomposer
   LLM role. Proposes components, responsibilities, contracts, checks, risks, concerns, probes, and gaps from bounded context bundles. Must cite provenance for every claim.

4. Skeptic / F3 reviewer
   LLM role with different prompt/context. Looks for wrong target, missing dimensions, overfitting to visible examples, unowned surfaces, missing contracts, no cross-cutting axis, and Goodhart proxies.

5. Probe builder
   Separate LLM or operator-assisted role. Builds held-out probes and counterexamples that are hidden from the decomposer proposal path.

6. Deterministic gate
   Non-LLM role. Validates structure, provenance, measurability, dependencies, snapshot freshness, and policy.

7. Run-freeze checkpoint
   Hermes presents a short, owner-facing summary before autonomous execution. Leon only needs to correct the target or allow the run; all routine decomposition mechanics stay with Hermes.

### Expected structured outputs

Each decomposition pass emits:

- `Component[]`
- `Contract[]`
- `CrossCuttingConcern[]`
- `ObservableCheck[]`
- `HeldOutProbe[]` or probe requirements
- `VerificationGap[]`
- `NearNeighborAlternative[]`
- `Assumption[]`
- `Risk[]`
- `EvidenceRequirement[]`
- `ProjectModelSnapshot` candidate
- gate report

### Recursion process

1. Start from the whole project and primary task.
2. Build deterministic graph and wiki context for the current node.
3. Ask the decomposer for a first-layer split into responsibility-bearing components and cross-cutting concerns.
4. Ask for contracts between components.
5. Ask for observable checks and risks per component and contract.
6. Run deterministic gate on structure and provenance.
7. Ask the skeptic to find F3-style wrong targets, near-neighbor alternatives, missing axes, missing contracts, overfit probes, and unverifiable leaves.
8. Repair by decomposing further, adding contracts/checks, or surfacing verification gaps.
9. Recurse into a component only when it is too broad to be tested mechanically or has unresolved internal contracts/risks.
10. Stop when leaves are mechanically testable, explicitly delegated to a stakeholder decision, or represented as verification gaps.
11. Cap depth at three by default; allow a fourth layer with rationale. Five or more layers are treated as a decomposition-quality smell and should block freezing unless the run-freeze summary explains why the depth is necessary.
12. Freeze only after deterministic gate passes and the short run-freeze checkpoint confirms the target is right.

### Stop conditions

A leaf stops as mechanically testable when:

- It has a clear responsibility.
- It owns explicit graph nodes/surfaces.
- Its interfaces or contracts are named.
- It has an ObservableCheck with mode-specific deterministic structure.
- Its acceptance checks require no live paid API in the default run mode.
- Its risks either have probes or are low enough with rationale.
- Its provenance is complete.

A leaf stops as a verification gap when:

- It cannot be mechanically checked with current tools.
- It requires owner preference or external truth not present in the repo.
- It depends on a live API or human judgment outside the recorded run mode.
- It is high-risk and lacks an isolated held-out probe.

A leaf must not stop merely because the LLM says it is reasonable.

### Preventing F3 at the decomposer layer

F3 means coherent, load-bearing reasoning aimed at the wrong target. The decomposer prevents this by:

- anchoring every claim to source provenance;
- requiring near-neighbor alternatives and why they are not primary;
- requiring held-out probes for high-risk units;
- separating decomposer and probe-builder roles;
- including cross-cutting concerns outside the component tree;
- requiring the run-freeze checkpoint before autonomous execution;
- using deterministic gates to reject vague, unmeasurable, unproven, or stale decompositions;
- evaluating on held-out projects, not only Build Arena itself.

## 9. Storage and versioning strategy

Use a layered local-first storage model:

1. JSONL canonical events
   Continue using JSONL events as canonical Build Arena runtime state.

2. Content-addressed blobs
   Store source extracts, parsed graph fragments, wiki pages, summaries, prompts, and LLM outputs by hash.

3. SQLite projection
   Use SQLite for queryable snapshots:
   - files
   - symbols
   - imports
   - calls where known
   - docs/sections
   - commands
   - configs
   - components
   - contracts
   - checks
   - gaps
   - provenance
   - FTS tables for text search

4. Markdown encyclopedia
   Store human-readable pages under a generated research/index area or `.arena` snapshot area, with source refs and content hashes. Do not hand-edit generated wiki pages unless the workflow marks them operator-authored.

5. Snapshot manifest
   Each ProjectModelSnapshot should record:
   - git OID
   - dirty-state fingerprint
   - inventory hash
   - graph hash
   - wiki hash
   - model hash
   - tool versions
   - prompt hashes
   - LLM model ids if used
   - operator approval ref
   - gate report ref

6. Invalidation
   Any change to git OID, dirty state, graph extraction version, wiki page hash, prompt hash, or model id invalidates the prior model unless the system can prove the changed surface is outside scope and the operator accepts that exclusion.

## 10. Pilot and evaluation plan

### Pilot 1: self-host Build Arena

Use Build Arena itself because it contains the exact target risks: scorer/verifier/schema boundaries, generated artifacts, event logs, worktree promotion rules, docs/spec/runbooks, F3 semantics, no-live-API concerns, and calibration fixture/oracle protection.

Purpose:

- validate that the graph/wiki/index can represent code plus process/spec/operator surfaces;
- expose whether the model overfits current path names;
- force the decomposer to represent cross-cutting concerns and protected boundaries.

Risk:

- too easy to overfit because Build Arena docs already describe the intended architecture. Counter this with held-out probes and different-repo pilots.

### Pilot 2: warm-up small repo

Use a small local Python repo with ordinary package/tests/config/docs but without Build Arena-specific terminology.

Purpose:

- validate basic graph extraction, wiki pages, import graph, components, contracts, and checks;
- keep debugging cheap;
- identify how much structure can be recovered without rich operator-written docs.

Criteria:

- no hardcoded Build Arena paths;
- components reflect actual package/test/config relationships;
- leaf checks are runnable locally.

### Pilot 3: held-out different repo

Use a repo in a different domain or language mix after the first two pilots. The decomposer prompts, gates, and graph schema should be fixed before this run.

Purpose:

- test generalization;
- catch path-classifier overfit;
- test docs/code/config semantic graph on unfamiliar architecture;
- validate that held-out probes can catch wrong-target decompositions.

Criteria:

- no code changes to the decomposer during evaluation except through a new approved phase;
- compare against a human-reviewed golden decomposition;
- record misses as calibration data.

### Golden decompositions

Build a small set of owner-reviewed decompositions:

- Build Arena self-host golden
- warm-up small repo golden
- held-out repo golden
- at least one process/spec-heavy decomposition
- at least one generated/oracle/fixture-heavy decomposition

Golden decompositions should not become training examples visible to the decomposer during held-out evaluation.

## 11. Phased implementation roadmap

### Phase A: current-state critique and target architecture

Output:

- this research report;
- corrected defaults for target architecture, schema strategy, model-use policy, held-out probes, protected surfaces, dirty snapshots, and pilots;
- default schema strategy: keep `project-model/v0` as the compatibility artifact and add ProjectGraph/Encyclopedia/Provenance/Snapshot sidecars first;
- default model-use strategy: Grok-first, high-effort decomposition/review while keeping autonomous-run acceptance gates reproducible without paid live APIs.

Exit criteria:

- Leon agrees the current Project Model v0 classifier is not frozen as the run contract;
- no Build Arena test run starts from the current classified JSON;
- no implementation begins until the report direction is corrected or accepted, but routine defaults are not pushed back to Leon.

### Phase B: graph/index prototype

Build deterministic graph extraction without LLM authority.

Scope:

- git/filesystem inventory;
- file hashes and typed exclusions;
- Python AST extraction;
- Tree-sitter experiment for multi-language syntax;
- grimp/import-linter import graph;
- Makefile/pyproject/CI command extraction;
- docs section extraction;
- edge-table storage in SQLite.

Exit criteria:

- graph snapshot tied to git OID and tool versions;
- graph can answer file/symbol/import/test/config/doc queries;
- generated/oracle/protected surfaces are represented;
- no live API required.

### Phase C: wiki/encyclopedia generator with provenance

Build AI-friendly pages from graph truth.

Scope:

- module pages;
- command pages;
- workflow pages;
- boundary/risk pages;
- docs/spec pages;
- source-linked claim lists;
- content-addressed wiki snapshot.

Exit criteria:

- every claim links to source spans or graph nodes;
- wiki pages are clearly marked as derived cache;
- stale pages are invalidated on graph drift.

### Phase D: LLM decomposer prompts and contracts

Add LLM proposal stage, Grok-first and provenance-constrained.

Scope:

- decomposer prompt;
- skeptic/F3 reviewer prompt;
- contract extraction prompt;
- cross-cutting concern prompt;
- observable check prompt;
- verification gap prompt;
- prompt hashing and model id recording;
- Grok-first high-effort model path for early stability;
- optional second leading-model review lane for high-risk decomposition changes;
- local/offline degraded path for graph/wiki/gap/report emission when model execution is unavailable.

Exit criteria:

- LLM outputs structured candidates with mandatory provenance refs;
- no claim is accepted without deterministic gate support;
- no paid API is required for autonomous-run acceptance tests by default, even though model calls may be used during decomposition/review.

### Phase E: deterministic quality gate

Extend the existing structural gate into a decomposition acceptance gate.

Scope:

- provenance gate;
- snapshot freshness gate;
- coverage gate;
- mode-specific ObservableCheck constraints;
- contract endpoint and cycle gate;
- cross-cutting concern gate;
- held-out probe isolation gate;
- verification gap gate;
- protected surface gate;
- no-live-API gate.

Exit criteria:

- gate can fail a plausible but wrong decomposition;
- gate cannot be satisfied by file buckets alone;
- gate report is actionable and deterministic.

### Phase F: golden decompositions and held-out projects

Build evaluation harness before operational use.

Scope:

- self-host Build Arena golden;
- warm-up small repo golden;
- held-out different repo golden;
- hand-crafted F3 decomposition probes;
- hidden probe isolation records;
- regression suite for gate behavior.

Exit criteria:

- decomposer passes known-good/good-bad cases;
- held-out project results are reviewed before changes;
- failures update the architecture through approved follow-up work, not silent prompt tweaking.

### Phase G: integration into Build Arena loop

Only after the above is green, wire the accepted snapshot into autonomous runs.

Scope:

- run preflight requires fresh ProjectModelSnapshot;
- operator approval record is checked;
- event log records snapshot id and gate report;
- worktree runners consume allowed components/contracts/checks;
- promotion refuses stale or unapproved decompositions;
- dashboard/control-plane integration remains later unless explicitly started.

Exit criteria:

- autonomous run cannot start without a fresh, approved, gate-passing decomposition;
- run evidence can be traced back to components, contracts, checks, and provenance;
- rollback and protected-surface rules remain enforced.

## 12. Defaults and true owner checkpoint

This section replaces the earlier question list. The earlier framing pushed implementation choices back to Leon. That is wrong for this project. Build Arena should use sensible defaults, document them, and ask Leon only when the decision is genuinely owner-level.

### Defaults Hermes should use

1. Schema strategy

Default: do not force Leon to choose `project-model/v1` now. Keep `project-model/v0` as the thin compatibility artifact and add ProjectGraph, EncyclopediaPage, Provenance, and ProjectModelSnapshot as sidecars. Revisit a breaking v1 only after pilots prove the fields that must become stable wire contract.

2. Model-use policy

Default: start with Grok and other leading models to stabilize the decomposition architecture. Optimize for cost/local execution later. Model calls are allowed for decomposition, critique, probe generation, and report review; every model id, prompt hash, output hash, and run mode is recorded. Acceptance tests for autonomous Build Arena runs remain local/hermetic by default and must not require paid live API calls.

3. Owner checkpoint

Default: Leon should not approve schema mechanics, check weights, probe construction, dirty-tree heuristics, or pilot selection. Before a decomposition can drive a run, Hermes presents one short run-freeze summary: target goal, non-goals, major components, major verification gaps, run mode, and protected-surface status. Leon either corrects the target or allows the run. Everything else is agent-owned toil.

4. Held-out probes

Default: Hermes owns held-out probes. A held-out probe is a hidden exam question that checks whether the decomposition generalizes instead of memorizing visible examples. The decomposer does not see the probe text before proposing the model. A separate skeptic/probe-builder lane creates probes from withheld context, near-neighbor cases, protected-boundary examples, and F3 counterexamples. Probe prompts and hashes are recorded so the gate can prove the decomposer did not receive the exact probe content.

5. Protected surfaces

Default: follow AGENTS.md as policy. `scorer/`, `verifier/`, `schema/`, `.arena/scorer.lock.toml`, and `arena/generated/` are protected during normal arena-generated hypotheses. Fixture, oracle, calibration, generated, and scorer-lock data are not ordinary improvable source. They change only in a dedicated operator/scorer/schema/calibration task, not as part of an autonomous cycle.

6. Snapshot drift

Default: no autonomous run starts from an unrecorded dirty state. Research/docs artifacts may exist while designing the system, but a run-driving ProjectModelSnapshot records git OID, dirty-state fingerprint, included/excluded paths, graph/wiki/model hashes, prompt hashes, and gate report. If dirty state affects the target, freezing blocks until it is intentionally included, excluded with a typed reason, or landed in source control.

7. Pilots

Default: Hermes selects pilots and documents why. Start with Build Arena self-host because it contains the real protected-boundary/process/spec risks. Then use a small ordinary Python repo to debug graph/wiki extraction cheaply. Then use a held-out different-domain repo to test generalization. Leon only needs to intervene if he wants a specific business-critical repo included or excluded.

### True owner-level questions

Only these are genuine owner checkpoints before implementation:

1. Is the target direction correct: Build Arena's decomposer should be an AI-first project-encyclopedia plus recursive LLM decomposition plus deterministic gate, not the current path-classifier Project Model v0?

2. May Hermes proceed to the next implementation phase using the defaults above, including Grok-first model assistance and no autonomous Build Arena test run until a fresh decomposition snapshot passes gates?

If Leon does not correct those two points, Hermes should proceed with the defaults instead of asking more planning questions.

## 13. Evidence and review notes

Repo files read before this report:

- `AGENTS.md`
- `README.md`
- `docs/build-arena-specification.md`
- `docs/project-model-v0.md`
- `docs/playbooks/2026-06-03-f3-project-model-mentor-runbook.md`
- `arena/decomposer.py`
- `arena/project_model_v0.py`
- `tests/test_project_decomposer.py`
- `docs/verification/2026-06-03-issue-3-project-model-v0-emit/mentor-run-report.md`
- `docs/verification/2026-06-03-issue-3-project-model-v0-emit/project-model-v0-classified.json`
- prior decomposer plan and Opus review artifacts under `docs/plans/` and `docs/verification/`

Repository search covered decomposition, ProjectModel, scanner, contract, F3, held-out probes, deterministic/quality gates, observable checks, unclassified surfaces, verification gaps, graph/wiki/tooling terms, and related phrases. Local search found no existing repo references for tree-sitter, ast-grep, SCIP, LSIF, CodeQL, Sourcegraph, codegraph, or wiki in the combined external-tooling query, so tooling comparison was based on external current documentation/search results.

External references consulted:

- Tree-sitter documentation: parser generator and incremental parsing library with concrete syntax trees.
- ast-grep documentation: structural search, lint, and rewrite over AST patterns.
- SCIP repository/documentation: language-agnostic code intelligence protocol for definitions, references, and implementations.
- CodeQL documentation: code analysis through queryable relational/semantic databases with AST, name binding, and type information.
- Sourcegraph Code Graph documentation: context from definitions, references, symbols, doc comments, and structural relationships.
- Ruff documentation: fast Python linter/formatter.
- Pyright documentation: Python static type checker.
- import-linter/grimp/module documentation: Python architecture/import constraints and queryable import graphs.
- Google Code Wiki / DeepWiki-style public descriptions: continuously updated repository wiki with source links and diagrams.

Independent Opus review:

Claude Opus reviewed the proposed thesis in read-only mode through Claude Code. It agreed with the verdict and pipeline framing, but required these improvements before the report should become a build directive:

- state that Project Model v0 currently lacks mandatory provenance, git OID, hashes, and coverage in the authoritative wire artifact;
- make Provenance a mandatory leaf-level field;
- resolve Project Model v1 versus sidecar strategy;
- resolve the model-use boundary between Grok/leading-model decomposition and local/hermetic acceptance tests;
- isolate held-out probes from the decomposer;
- temper claims about Tree-sitter and grimp as syntactic/import graph tools, not full semantic architecture recovery;
- treat wiki prose as a navigational cache, not authoritative ground truth;
- name current Build Arena/arena-calibration special casing as evidence of overfitting risk.

Those changes are incorporated in this report.
