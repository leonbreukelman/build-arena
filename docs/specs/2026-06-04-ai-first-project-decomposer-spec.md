# AI-first Project Decomposer — Product and Architecture Specification

Date: 2026-06-04
Status: codeless implementation specification
Audience: Build Arena operators, implementers, reviewers, and future autonomous runners

## 0. Grounding summary

This specification is grounded in the current Build Arena repository state and the existing Project Model v0 work.

Repository facts observed before drafting:

- Working directory: `/home/leonb/projects/build-arena`.
- Git top-level: `/home/leonb/projects/build-arena`.
- Current branch: `coverage-100`.
- Working tree has pre-existing untracked documentation and verification artifacts. This spec must not assume those artifacts are authoritative runtime state.

Source-of-truth files read before drafting:

- `AGENTS.md`.
- `README.md`.
- `docs/build-arena-specification.md`.
- `docs/research/2026-06-03-ai-first-project-decomposition-pipeline.md`.
- `docs/project-model-v0.md`.
- `arena/decomposer.py`.
- `arena/project_model_v0.py`.
- `tests/test_project_decomposer.py`.

Relevant repo-local prior work:

- `arena/decomposer.py` implements the current deterministic scanner/decomposer and Project Model v0 compatibility path.
- `arena/project_model_v0.py` implements the Project Model v0 contract and meta-F3 quality gate.
- `tests/test_project_decomposer.py` verifies raw-byte hashing, git top-level resolution, no execution during decomposition, CLI behavior, validation of references, F3 gap derivation for arena-calibration fixtures, and Project Model v0 emission.
- `docs/research/2026-06-03-ai-first-project-decomposition-pipeline.md` defines the target graph/wiki/LLM/gate architecture that this spec turns into a buildable contract.
- `docs/plans/2026-06-01-project-decomposer.md` and its Opus reviews document why the current deterministic decomposer improved coverage and validation, but remained a compatibility/scanner substrate rather than the intended AI-first decomposer.

External research signals used as design input:

- Tree-sitter: fast, robust, incremental concrete syntax trees over many languages.
- ast-grep: Tree-sitter-backed structural search/rewrite/lint rules that match syntax shapes rather than raw text.
- SCIP and LSIF: language-agnostic code-intelligence indexes for definitions, references, symbols, implementations, and hover/doc data.
- Sourcegraph code graph: semantic code graph data covers definitions, references, symbols, doc comments, and relationships produced by indexers.
- CodeQL: queryable code databases containing AST, data-flow, and control-flow relations.
- import-linter/Grimp: Python import graphs and declarative architecture contracts.
- DeepWiki / Google Code Wiki / codebase knowledge-graph systems: AI-generated structured wiki pages are useful when they remain source-linked, synchronized with code, and treated as derived navigation, not authoritative truth.
- Architecture-recovery/program-comprehension literature: architecture reconstruction must combine source structure, runtime/config cues, documentation, and human intent; no single path classifier is enough.
- Agentic codebase-understanding systems and Codebase-Memory-style work: persistent Tree-sitter/code knowledge graphs reduce token use and file-by-file hallucination, but must expose provenance and deterministic validation.

## 1. Direct purpose and non-goals

### Purpose

Build Arena needs a proper AI-first project decomposer that can transform a real repository into a frozen, provenance-backed decomposition snapshot suitable for autonomous improvement loops.

The decomposer's job is to turn disk and git truth into a model of the project that answers:

1. What artifacts exist, and what do they mean?
2. What responsibility-bearing components make up the project?
3. What contracts connect those components?
4. What cross-cutting concerns must be evaluated orthogonally to the component tree?
5. Which checks mechanically observe each claim?
6. Which leaves are not yet mechanically verifiable and must be represented as verification gaps rather than passed work?
7. Which held-out probes can detect wrong-target decompositions and shallow file-bucket decompositions?
8. Can the resulting snapshot safely drive a Build Arena run?

The intended flow is:

```text
git/filesystem truth
-> code/doc/issue/config graph
-> provenance-backed project encyclopedia/wiki
-> Grok/leading-model recursive decomposer
-> components/contracts/cross-cutting concerns/checks/held-out probes/verification gaps
-> deterministic gate
-> frozen ProjectModelSnapshot usable by Build Arena
```

### Non-goals

This phase does not:

- Replace the Build Arena scorer, verifier, schema, or generated artifacts.
- Modify `scorer/`, `verifier/`, `schema/`, `.arena/scorer.lock.toml`, or `arena/generated/`.
- Run autonomous Build Arena optimization cycles from current Project Model v0/classified JSON.
- Treat LLM prose as authoritative without deterministic provenance and gate validation.
- Require live paid API calls in acceptance tests.
- Build a dashboard, rollback endpoint, or live subscription-CLI subprocess executor.
- Optimize for cheapest/local-only decomposition before quality is stabilized.
- Ask the operator to choose schema mechanics, weights, probe mechanics, dirty-tree heuristics, or pilot repos unless a true owner-level blocker exists.
- Hand-edit generated artifacts.

## 2. Why Project Model v0 and the current decomposer are insufficient

Project Model v0 is useful, but it is not the target decomposer.

The current implementation provides important infrastructure:

- Git-aware inventory with raw-byte hashes.
- Typed exclusions.
- Deterministic canonical JSON.
- Validation for exactly-one-owner coverage, bad references, missing checks/gaps, contract endpoint integrity, and stale coverage.
- A compatibility projection to `project-model/v0`.
- A known arena-calibration detector with manifest-derived F3 gap evidence.

Those are necessary substrate capabilities, but insufficient for best-in-class AI-first decomposition because they still primarily answer, "Which bucket owns this path?" rather than, "What project architecture, obligations, and verifiable improvement leaves exist?"

Specific insufficiencies:

1. Shallow semantic model.
   - The current model is mostly file inventory plus rule-based component ownership.
   - It does not build a rich graph of symbols, imports, tests, docs, configs, issue links, generated/oracle surfaces, and workflow relationships.

2. Path-classification bias.
   - Generic components such as tests, docs, config, source, package marker, or unclassified bucket can pass ownership checks without proving responsibility-bearing decomposition.
   - A path bucket is not necessarily a component.

3. Limited architecture recovery.
   - The current decomposer does not use Tree-sitter/AST, import graphs, code intelligence indexes, doc-to-code links, or config/test/workflow relations as first-class evidence.

4. No provenance-backed encyclopedia.
   - There is no derived project wiki that gives models and humans a source-linked understanding layer before decomposition.
   - Without this layer, LLM decomposition would either reread raw files ad hoc or hallucinate from incomplete context.

5. No AI-first recursive decomposition loop.
   - The current system can emit deterministic structures, but it does not run a leading-model decomposer over graph/wiki context with skeptic/F3 review and recursive refinement.

6. Weak held-out probe workflow.
   - Project Model v0 has held-out probe fields, but the current pipeline does not isolate probe construction from decomposition or test whether probes detect wrong-target decompositions.

7. Verification gaps are too narrow.
   - Existing gaps are valid, but mostly local to known fixture logic.
   - A general decomposer must mark ambiguous, unverifiable, missing-source, no-observable-check, stale-doc, and generated/oracle ambiguity leaves as explicit `VerificationGap` objects.

8. Snapshot lifecycle is incomplete.
   - A future Build Arena run needs a frozen snapshot tied to git OID, dirty-state fingerprint, input hashes, prompt hashes, model IDs, output hashes, and sidecar artifacts.
   - Current canonical JSON is not enough to represent the graph/wiki/decomposition/gate bundle as an immutable run input.

The decision for this phase is therefore:

- Keep Project Model v0 compatibility.
- Keep deterministic scanner/validator strengths.
- Add richer sidecars beside v0 rather than breaking v0.
- Do not treat the current v0 model as the run contract for the intended AI-first Build Arena decomposer.

## 3. Target architecture

### 3.1 Architecture overview

The decomposer is a staged pipeline. Each stage consumes immutable artifacts from earlier stages and emits content-addressed sidecars.

```text
ProjectRoot
  |
  v
Truth Scanner
  - git state
  - tracked/untracked inventory
  - file hashes
  - protected/generated/oracle classification
  - config/test/doc/issue discovery
  |
  v
ProjectGraph Builder
  - file/doc/config/test nodes
  - symbols/imports/references/checks/workflows edges
  - provenance refs on every node/edge
  |
  v
Encyclopedia Builder
  - Markdown pages for subsystems and project concepts
  - source-linked claims
  - uncertainty and contradiction sections
  |
  v
LLM Recursive Decomposer
  - Grok or leading model primary pass
  - component hierarchy
  - contracts
  - concerns
  - checks
  - gaps
  |
  v
Skeptic/F3 Review + Repair Loop
  - attacks wrong target, path buckets, ungrounded claims
  - forces ambiguous leaves into gaps
  |
  v
Held-Out Probe Builder
  - isolated from primary decomposer prompt
  - creates counterexamples and discriminators
  |
  v
Deterministic Gate
  - validates provenance, coverage, contracts, checks, probes, gaps, protected surfaces, freshness
  |
  v
ProjectModelSnapshot
  - frozen graph/wiki/decomposition/gate bundle
  - Project Model v0 compatibility projection
```

### 3.2 Stage authority model

Authority flows from disk/git truth outward, and each stage has a bounded kind of authority.

1. Disk/git truth is authoritative for files, hashes, git state, and raw content.
2. ProjectGraph is a deterministic representation of that truth. A graph may use cached or externally produced sub-indexes only when a local deterministic audit proves their input hashes, tool versions, and output hashes match the current run; otherwise it is rebuilt.
3. Encyclopedia pages are derived navigation aids and may be regenerated. They are never sole provenance for accepted code facts.
4. LLM decomposition is advisory until the local structural gates pass. It can propose semantic responsibilities and contracts, but it does not by itself authorize snapshot use.
5. Skeptic/F3 review is an adversarial semantic review stage. It can identify wrong-target, renamed-bucket, overfit, and missing-dimension risks that a deterministic gate cannot reliably infer. Its findings are recorded and used for repair, but future reusable snapshot acceptance must not depend on a live paid model call.
6. Held-out probes are adversarial validation artifacts, not training context for the same decomposition pass. Their presence, isolation, and discrimination against planted negatives are validated deterministically.
7. GateReport is the only blocking authority for snapshot usability. It decides structural, provenance, hash, policy, and probe-discrimination predicates that can be checked locally. It does not claim to solve semantic wrong-target judgment except through explicit deterministic predicates and recorded probe results.
8. ProjectModelSnapshot is immutable once frozen.

### 3.3 ProjectGraph

The ProjectGraph is the central source-linked index over repository artifacts. It must be rebuilt from filesystem/git truth each run. Cached graph projections may accelerate a run only if their input hashes match exactly; they are never authoritative.

The graph includes:

- Files and directories.
- Python modules/packages and, later, other language modules.
- Symbols: classes, functions, protocols, Pydantic models, CLI entrypoints, test functions.
- Imports and dependency edges.
- Test-to-code and check-to-surface edges where inferable.
- Documentation pages and headings.
- Config files and declared tool commands.
- GitHub/issue/task references when available from local docs, branch names, commit metadata, or authorized local issue caches.
- Generated, fixture, oracle, protected, and runtime/cache surfaces.
- Build/CI/workflow commands and their owning configs.
- Prior sidecar artifacts as excluded derived artifacts unless explicitly requested as historical evidence.

Implementation may start with Python AST, deterministic import graph extraction, Markdown heading/link parsing, TOML/YAML/JSON config parsing, git metadata, and test discovery. For Python repos, import/dependency edges are required in the first implementation slice rather than left to LLM inference. High-impact `calls`, `references`, `tests`, `depends_on`, and contract-supporting edges must be deterministic or downgraded to `VerificationGap` until Tree-sitter, ast-grep, SCIP/LSIF, CodeQL, coverage.py, or equivalent source-index tooling can ground them. Later enrichments should add stable symbol monikers, coverage-backed test-to-code edges, git-history/co-change edges, duplicate/dead-code signals, and per-file Merkle graph caching.

### 3.4 Provenance-backed Encyclopedia/Wiki

The Encyclopedia is a derived Markdown knowledge layer. It is not authoritative by itself.

It exists to:

- Give the LLM decomposer a compact, structured, source-linked project understanding layer.
- Give humans an inspectable explanation of the project structure.
- Preserve uncertainty instead of smoothing it away.
- Reduce repeated file-by-file context loading.

Each page must include:

- Page ID and title.
- Purpose statement.
- Source summary.
- Key artifacts and provenance references.
- Claimed responsibilities with provenance references.
- Known contracts/dependencies with provenance references.
- Observable checks with provenance references.
- Uncertainties, contradictions, stale-doc risk, and verification gaps.
- Generated/protected/oracle surface notes.
- Input hash and page output hash.

The wiki is regenerated for each snapshot. Manual edits to generated wiki pages are not authoritative. Operator notes may be ingested only as separate source nodes with provenance.

### 3.5 LLM recursive decomposer

The primary decomposer uses Grok or another leading model to reason over the ProjectGraph and Encyclopedia, not over a flat file list. It recursively decomposes the project into responsibility-bearing components and contracts.

The model must produce structured output. Every claim must either:

- cite `ProvenanceRef` evidence, or
- become a `VerificationGap`.

The decomposer must not mark vague or miscellaneous components as successful leaves. It must not allow "docs", "tests", or "config" to pass as final components unless the responsibility is explicit, source-backed, and mechanically checkable. Because deciding whether a polished description is still a renamed path bucket is partly semantic, the pipeline uses three layers: deterministic lexical/structural predicates, held-out probes against planted negatives, and independent skeptic review.

### 3.6 Deterministic gate

The deterministic gate validates the graph/wiki/decomposition/probe/snapshot bundle without trusting model prose. It is the final blocking authority for whether a snapshot can drive a Build Arena run, but it only blocks on predicates it can evaluate locally and reproducibly. Semantic wrong-target judgments are represented through explicit artifacts: planted-negative probe results, concrete structural predicates, accepted verification gaps, and recorded advisory review findings.

The gate fails on:

- missing inventory coverage;
- missing or non-transitively-resolvable provenance;
- concrete vague/bucket predicates, such as denylisted names, empty responsibilities, components whose owned nodes are almost entirely sibling files under one directory without symbol/contract/check references, or components whose responsibilities reference no graph-backed symbols, contracts, concerns, or checks;
- unchecked or ungapped components;
- contract endpoint/reference errors;
- unconditional cross-cutting concerns missing, or conditional concerns missing when their triggering surfaces are detected;
- missing, leaked, or non-discriminating held-out probes;
- ambiguous leaves represented as success when the ambiguity is structurally detectable or already recorded by review/probe findings;
- protected-surface mishandling;
- live-paid-API acceptance checks or checks outside the local acceptance-command allowlist;
- stale snapshot metadata;
- LLM outputs missing model/prompt/output hashes;
- cached projections treated as authoritative.

### 3.7 ProjectModelSnapshot

The snapshot is the frozen artifact used by Build Arena. It includes or references:

- Graph JSON.
- Encyclopedia Markdown pages plus page manifest.
- LLM decomposition JSON.
- Held-out probe JSON.
- Gate report JSON.
- Project Model v0 compatibility JSON.
- Metadata tying the bundle to git/disk/prompt/model/output hashes.

A snapshot with a failed gate is useful as a diagnostic artifact but must not be used to start an autonomous arena cycle.

## 4. Data contracts

The first implementation should define these contracts as sidecar JSON structures with stable `schema_version` strings. They may be Pydantic models internally, but this codeless spec defines behavior, not implementation syntax.

### 4.1 ProjectGraph

Purpose: deterministic, provenance-backed graph of repository truth.

Required fields:

- `schema_version`: e.g. `project-graph/v0.1`.
- `project_id`.
- `project_root`.
- `git`: git state object with toplevel, HEAD OID if available, branch if available, dirty paths, untracked paths, and inventory mode.
- `inventory`: included/excluded/missing file records with raw-byte hashes for included disk files.
- `nodes`: list of `GraphNode`.
- `edges`: list of `GraphEdge`.
- `protected_surfaces`: paths and reasons.
- `generated_surfaces`: paths and reasons.
- `oracle_surfaces`: paths and reasons.
- `input_hashes`: content hashes for scanner inputs.
- `builder`: tool versions and ruleset version.
- `created_at_utc`.
- `graph_hash`.

Graph invariants:

- Every included file has a file node.
- Every node has at least one provenance reference unless it is a synthetic grouping node, in which case it must cite child nodes.
- Every edge has provenance or a documented deterministic inference rule.
- Excluded/generated/protected/runtime files are represented intentionally, not silently omitted.
- The graph is rebuilt from git/filesystem truth each run.

### 4.2 GraphNode

Purpose: typed artifact or concept node in the graph.

Required fields:

- `id`: stable snapshot-local identifier.
- `kind`: one of file, directory, module, package, symbol, test, check, doc, doc_section, config, workflow, command, issue_ref, generated_surface, protected_surface, oracle_surface, runtime_surface, concept, external_dependency, synthetic_group.
- `label`.
- `path` when path-backed.
- `symbol` when symbol-backed.
- `language` when known.
- `summary`: deterministic or provenance-backed short description.
- `provenance_refs`.
- `hashes`: relevant content/symbol hashes.
- `attributes`: structured properties such as public/private, test marker, generated flag, protected flag, oracle flag, config type, command string.

Node invariants:

- Path-backed nodes must refer to paths in inventory.
- Generated/protected/oracle nodes must carry typed reasons.
- Symbol nodes must cite file and line/span provenance.
- Concept nodes must cite the evidence from which the concept was derived.

### 4.3 GraphEdge

Purpose: typed relationship between graph nodes.

Required fields:

- `id`.
- `kind`: contains, defines, imports, calls, references, tests, configures, invokes, documents, generates, protects, consumes, produces, depends_on, constrains, verifies, contradicts, duplicates, derived_from, mentions_issue, owns_surface_candidate.
- `from_node_id`.
- `to_node_id`.
- `label`.
- `provenance_refs`.
- `confidence`: deterministic, high, medium, low.
- `inference_rule` when not directly observed.
- `attributes`.

Edge invariants:

- Both endpoints must exist.
- Deterministic edges cite parser/config/git rules.
- LLM-inferred edges are advisory and must cite evidence; the gate may require confirmation or gap.

### 4.4 ProvenanceRef

Purpose: exact evidence pointer for a claim.

Required fields:

- `id`.
- `source_type`: file, git, command_output, doc_section, graph_node, graph_edge, issue, model_output, operator_note.
- `derived_by`: git, python_ast, tree_sitter, import_graph, doc_parser, config_parser, test_discovery, coverage_tool, code_intel_index, llm, operator, deterministic_rule.
- `confidence`: deterministic, high, medium, low.
- `path` when file-backed.
- `line_start` and `line_end` when text-backed.
- `byte_start` and `byte_end` when available.
- `git_oid` for the repository HEAD anchor when the referenced content matches HEAD.
- `content_hash` for the referenced file, span, command output, graph element, or model output. Text-backed refs must always include it.
- `dirty_content_hash` when the referenced file is dirty relative to HEAD.
- `symbol_moniker` when symbol-backed, using a stable snapshot-local SCIP-style identity such as `python package.module/Class.method` plus file hash.
- `claim` or `claim_id` that the ref supports.
- `excerpt` may be included, but the gate must validate the hash/path/line anchor rather than trust excerpts.

Provenance invariants:

- A claim cannot cite a missing path.
- A stale line anchor must be detected by content hash mismatch or snapshot freshness checks.
- Dirty file provenance anchors to disk `content_hash`/`dirty_content_hash`; HEAD `git_oid` alone is not sufficient for dirty spans.
- Model-generated prose, encyclopedia pages, and doc sections cannot be the sole provenance for accepted code facts. Accepted component/contract/concern claims must resolve transitively to at least one deterministic leaf provenance whose `derived_by` is git, parser, import graph, config parser, test discovery, coverage tool, code-intel index, command output, or deterministic rule.
- LLM- or operator-derived provenance may support interpretation, prioritization, or uncertainty, but never replaces the deterministic leaf evidence for repository facts.

### 4.5 EncyclopediaPage

Purpose: derived wiki page used by humans and LLMs.

Required fields:

- `schema_version`: `project-encyclopedia-page/v0.1`.
- `id`.
- `title`.
- `kind`: overview, subsystem, component_candidate, contract_candidate, concern, check_catalog, risk_register, protected_surface_map, verification_gap_map.
- `parent_id` when hierarchical.
- `source_graph_hash`.
- `source_node_ids` and `source_edge_ids`.
- `provenance_refs`.
- `markdown_path`.
- `summary`.
- `claims`: page-level structured claim IDs with provenance.
- `uncertainties`.
- `contradictions`.
- `output_hash`.

Page invariants:

- Every non-obvious claim cites provenance.
- Uncertainty is preserved explicitly.
- A page may propose component candidates but cannot make them accepted components by itself.

### 4.6 Component

Purpose: responsibility-bearing unit of decomposition.

Required fields:

- `id`.
- `name`.
- `kind`: extensible vocabulary such as runtime, library, CLI, data_model, orchestrator, adapter, verifier, scorer, workflow, test_harness, documentation_system, configuration_system, governance_process, generated_artifact_system, mixed_with_gap. Build-Arena-specific terms are optional, not required for unrelated repos.
- `level`: recursion depth.
- `parent_component_id` when nested.
- `responsibilities`: specific, source-backed responsibility statements.
- `owned_node_ids`.
- `owned_paths`: derived readability/compatibility projection from `owned_node_ids`; never authoritative for gates.
- `boundary`: in-scope/out-of-scope statements.
- `inputs`.
- `outputs`.
- `observable_check_ids`.
- `contract_ids`.
- `cross_cutting_concern_ids`.
- `near_neighbor_alternative_ids` for high-risk or F3-prone leaves.
- `verification_gap_ids`.
- `provenance_refs`.
- `model_claim_ids`: links to LLM output claims.
- `risk_level`: low, medium, high.

Component invariants:

- A component must own at least one graph-backed surface or explicitly be a conceptual process component with strong provenance.
- A component must have at least one observable check or verification gap.
- Vague names such as misc, general, other, utilities, stuff, everything, tests bucket, docs bucket, or config bucket fail under deterministic lexical rules. A renamed but still semantically wrong bucket is handled by planted-negative probes and skeptic review rather than pretending the deterministic gate can infer intent unaided.
- Included source/config/doc/check surfaces must be owned exactly once unless explicitly modeled as shared through a contract or cross-cutting concern.
- High-risk leaves require at least one near-neighbor alternative or a verification gap.
- Protected/generated/oracle ownership must respect policy.

### 4.7 Contract

Purpose: assume-guarantee relationship between components.

Required fields:

- `id`.
- `name`.
- `from_component_id`.
- `to_component_id`.
- `kind`: data_flow, control_flow, API, CLI, file_format, config_contract, schema_contract, prompt_contract, test_oracle_contract, generated_artifact_contract, verification_contract, governance_contract, sequencing_contract.
- `assumptions`.
- `guarantees`.
- `failure_modes`.
- `observable_check_ids`.
- `verification_gap_ids`.
- `near_neighbor_alternative_ids` for high-risk contracts.
- `supporting_edge_ids`.
- `provenance_refs`.

Contract invariants:

- Endpoints must exist.
- A contract must have checks or gaps.
- Contracts must not be only narrative dependencies; they must specify what one side assumes and the other guarantees.
- Contracts crossing protected/generated/oracle boundaries must identify the boundary explicitly.
- High-risk contracts require a near-neighbor alternative or a verification gap.

### 4.8 NearNeighborAlternative

Purpose: make wrong-target F3 visible by requiring plausible nearby decompositions or interpretations and why they are not primary.

Required fields:

- `id`.
- `target_component_ids`.
- `target_contract_ids`.
- `description`.
- `why_not_primary`.
- `distinguishing_evidence`.
- `observable_check_ids`.
- `held_out_probe_ids`.
- `verification_gap_ids`.
- `provenance_refs`.

Near-neighbor invariants:

- High-risk components and contracts need at least one near-neighbor alternative or an explicit verification gap.
- The alternative must be plausible enough that a shallow model might choose it.
- `why_not_primary` must cite project goal/non-goal anchors and deterministic provenance where available.
- A near-neighbor with no distinguishing evidence becomes a verification gap.

### 4.9 CrossCuttingConcern

Purpose: orthogonal axis that cuts across the component hierarchy.

Required fields:

- `id`.
- `name`.
- `category`: extensible vocabulary including determinism, provenance, security, privacy, provider_boundary, generated_artifact_integrity, oracle_integrity, fixture_integrity, rollback_safety, observability, performance, documentation_sync, schema_compatibility, cost_control, local_first, anti_fabrication, F3_resistance. Build-Arena-specific categories are optional and triggered only by evidence.
- `trigger`: unconditional, protected_surface_detected, generated_surface_detected, oracle_surface_detected, fixture_surface_detected, provider_edge_detected, schema_surface_detected, external_service_detected, high_risk_component_detected, repo_policy_detected.
- `description`.
- `component_ids`.
- `contract_ids`.
- `observable_check_ids`.
- `verification_gap_ids`.
- `provenance_refs`.

Concern invariants:

- The concern must touch at least one component or contract.
- Universally required concerns are anti-fabrication, determinism, provenance, and no-live-paid-API acceptance.
- Conditional concerns are required only when graph evidence triggers them: protected surface integrity when protected paths exist; generated artifact integrity when generated surfaces exist; oracle integrity when oracle surfaces exist; fixture integrity when fixtures exist; provider boundary when provider/API edges exist; schema compatibility when schemas exist; F3 resistance when high-risk wrong-target or decomposition-purpose claims are present.
- The gate must fail fabricated conditional concerns that have no triggering evidence unless they are explicitly recorded as operator/project policy.

### 4.10 ObservableCheck

Purpose: a mechanically observable signal for a component, contract, or concern.

Required fields:

- `id`.
- `name`.
- `mode`: unit_test, integration_test, static_analysis, typecheck, lint, schema_validation, command_smoke, artifact_validation, graph_query, import_contract, ast_pattern, doc_sync_check, manual_inspection_required, no_live_api_guard.
- `command` when executable.
- `acceptance_command_id` when the command is eligible for snapshot acceptance.
- `safe_to_run_by_default`: boolean.
- `requires_network`: boolean.
- `requires_paid_api`: boolean.
- `expected_signal`.
- `failure_signal`.
- `component_ids`.
- `contract_ids`.
- `concern_ids`.
- `provenance_refs`.

Check invariants:

- Acceptance checks must not require live paid APIs.
- Acceptance checks must appear in the snapshot's local acceptance-command allowlist or be validated in a network-disabled dry-run/sandbox. The `requires_network` and `requires_paid_api` booleans are not trusted by themselves.
- Commands must reference existing files/tools when resolvable.
- Non-executable checks must be labeled as inspection or gap, not silently treated as mechanical pass.
- A check's expected signal must be observable in output, artifact existence/hash, or deterministic query result.

### 4.11 HeldOutProbe

Purpose: adversarial probe that tests whether decomposition captures project intent rather than merely satisfying visible rules.

Required fields:

- `id`.
- `target_component_ids`.
- `target_contract_ids`.
- `target_concern_ids`.
- `probe_type`: counterexample, near_neighbor, missing_dimension, wrong_target, fabricated_provenance, generated_surface_leak, oracle_leak, vague_bucket, stale_snapshot, no_observable_check, F3_generalization.
- `scenario`.
- `expected_behavior`.
- `observable_check_ids`.
- `isolation_group`.
- `builder_model_id` or deterministic builder ID.
- `builder_prompt_hash`.
- `builder_independent_from_decomposer`: boolean, true when the builder model/provider/session differs from the primary decomposer or when a deterministic decoy generator is used.
- `paired_planted_negative_id`.
- `expected_negative_finding`.
- `discrimination_result`: fires, does_not_fire, inconclusive, not_run.
- `discrimination_evidence_refs`.
- `provenance_refs`.
- `hidden_from_primary_decomposer`: boolean.
- `output_hash`.

Probe invariants:

- High-risk components and contracts require at least one held-out probe or a justified gap.
- The primary decomposer must not receive the full probe corpus for the same snapshot before producing its decomposition.
- Probe builder independence is required for model-built probes unless a deterministic decoy/probe generator is used.
- Each high-risk probe must be paired with at least one planted negative or decoy decomposition and must record whether it fired on that decoy.
- Probes that do not discriminate are rejected or converted into verification gaps; mere probe presence is not enough.
- Probes are not themselves proof of correctness; they are discriminators for gate and reviewer use.

### 4.12 VerificationGap

Purpose: honest representation of ambiguity, unobservability, missing evidence, or unresolved target risk.

Required fields:

- `id`.
- `severity`: low, medium, high, blocker.
- `gap_type`: missing_provenance, ambiguous_responsibility, no_mechanical_check, stale_doc, missing_test_oracle, generated_surface_ambiguity, protected_surface_risk, model_uncertainty, F3_wrong_target, missing_issue_context, unsupported_language, external_service_unavailable, live_api_required, pilot_semantic_failure.
- `description`.
- `affected_component_ids`.
- `affected_contract_ids`.
- `affected_concern_ids`.
- `evidence_needed_to_close`.
- `safe_default`.
- `provenance_refs`.

Gap invariants:

- Ambiguous or unverifiable leaves become gaps, not success.
- Blocker gaps fail snapshot acceptance.
- Non-blocker gaps may pass only if the gate's configured acceptance policy allows them and the final report explains why the snapshot is still safe.

### 4.13 ProjectModelSnapshot

Purpose: immutable bundle handed to Build Arena.

Required fields:

- `schema_version`: `project-model-snapshot/v0.1`.
- `snapshot_id`.
- `project_id`.
- `project_root`.
- `goal`: the decomposition target statement used for this snapshot.
- `non_goals`: explicit out-of-scope targets used to detect wrong-target F3.
- `created_at_utc`.
- `git_oid`.
- `git_branch`.
- `dirty_state_fingerprint`.
- `input_hashes`.
- `prompt_hashes`.
- `model_ids`.
- `output_hashes`.
- `graph_path` and `graph_hash`.
- `encyclopedia_manifest_path` and hash.
- `decomposition_path` and hash.
- `near_neighbor_alternatives_path` and hash.
- `held_out_probe_path` and hash.
- `planted_negative_corpus_path` and hash.
- `acceptance_command_allowlist_path` and hash.
- `gate_report_path` and hash.
- `project_model_v0_path` and hash.
- `artifacts_root`.
- `status`: passed, failed, blocked.
- `blocking_gap_ids`.
- `warnings`.

Snapshot invariants:

- A snapshot must be reproducibly tied to the exact disk/git inputs used to create it.
- If dirty, disk hashes and dirty-state fingerprint are first-class; HEAD alone is not enough.
- A snapshot is immutable once frozen. Later repairs create a new snapshot.

### 4.14 GateReport

Purpose: deterministic acceptance report.

Required fields:

- `schema_version`: `project-model-gate-report/v0.1`.
- `snapshot_id`.
- `passed`: boolean.
- `findings`: list of structured findings.
- `summary_counts`.
- `gate_versions`.
- `input_hashes`.
- `created_at_utc`.

Finding fields:

- `id`.
- `severity`: info, warning, error, blocker.
- `gate`: inventory_coverage, provenance_completeness, transitive_source_provenance, component_measurability, contract_references, near_neighbor_alternatives, cross_cutting_concerns, held_out_probe_presence, held_out_probe_isolation, held_out_probe_discrimination, verification_gap_integrity, protected_surface_policy, no_live_paid_api_acceptance_tests, acceptance_command_allowlist, snapshot_freshness, output_hash_integrity, vague_component_rejection, cached_projection_authority.
- `message`.
- `affected_ids`.
- `provenance_refs` when applicable.
- `recommended_fix`.

Gate invariants:

- Gate output is deterministic for the same snapshot inputs.
- The gate never calls live LLM/API services.
- The gate may inspect model metadata and hashes but not trust model assertions.
- The gate must not pretend to make unconstrained semantic judgments; semantic risks become deterministic only when represented as concrete predicates, probe results against decoys, or explicitly accepted/rejected findings.

## 5. Recursive decomposition algorithm

### 5.1 Inputs

The decomposer consumes:

- Project root path.
- Optional project ID; default is resolved repo directory name.
- Goal statement; default is "decompose this repository into responsibility-bearing components that can safely drive Build Arena" when no task-specific goal is provided.
- Non-goals; default includes not modifying protected/generated/oracle surfaces, not running autonomous arena cycles from v0 output, and not treating file-bucket ownership as semantic decomposition.
- Optional source task/backlog item for compatibility output.
- Optional local issue/context bundle if available.
- Git/filesystem inventory.
- ProjectGraph.
- Encyclopedia manifest and pages.
- Protected-surface policy.
- Prompt templates and role instructions.
- Model selection defaults.

### 5.2 Default model choices

Default quality-first choices:

- Primary decomposer: Grok or strongest available leading model already authenticated in the environment.
- Skeptic/F3 reviewer: Opus where available; otherwise another independent leading model with artifact provenance labeled as fallback.
- Encyclopedia writer: lower-cost leading model or deterministic writer for simple pages, but source-linked claims remain required.
- Deterministic gate: local Python only, no LLM.

No owner choice is required for routine model mechanics. If credentials are missing, the pipeline must either use an available leading-model fallback and label it, or block with a clear missing-auth finding if no acceptable reviewer/decomposer model is available.

### 5.3 Recursion process

1. Build graph from git/filesystem truth.
2. Build encyclopedia pages from graph.
3. Ask the primary decomposer for a top-level project decomposition.
4. Validate top-level output structurally and by provenance references.
5. For each component:
   - If it is mechanically checkable and responsibility-bearing, keep it as a leaf.
   - If it is broad but decomposable, recurse using graph/wiki context scoped to the component.
   - If it is ambiguous, under-evidenced, or not mechanically checkable, create `VerificationGap` or ask for recursive refinement.
6. Add contracts between siblings and across levels.
7. Add cross-cutting concerns orthogonally.
8. Build or link observable checks.
9. Produce near-neighbor alternatives for high-risk components and contracts.
10. Run skeptic/F3 review against graph/wiki/decomposition.
11. Repair valid skeptic findings.
12. Build held-out probes using an isolated role.
13. Pair high-risk probes with planted negative/decoy decompositions and record whether the probes fire.
14. Run deterministic gates.
15. Freeze snapshot if gates pass; otherwise freeze failed diagnostic artifact and repair.

### 5.4 Stop conditions

A component stops decomposing when all are true:

- It has a specific responsibility not reducible to a generic file bucket.
- It owns source/config/doc/check surfaces exactly or explicitly shares through contracts/concerns.
- It has at least one mechanical observable check or an explicit verification gap.
- Its contracts to neighboring components are represented.
- Its claims have provenance.
- It has no unresolved blocker gap.
- High-risk or F3-prone leaves have a near-neighbor alternative.
- A held-out probe exists for high-risk or F3-prone leaves and discriminates against a paired planted negative.

A component must continue decomposing or become a gap when:

- It is named or described vaguely.
- It mixes unrelated responsibilities.
- It contains protected/generated/oracle surfaces with unclear authority.
- It has no checks.
- It cannot distinguish success from file-bucket coverage.
- It makes claims not supported by graph/wiki provenance.

### 5.5 Repair loop

The repair loop is bounded.

For each failed gate or skeptic finding:

1. Classify as valid, invalid, or needs evidence.
2. For valid findings, repair the smallest responsible artifact: graph builder rules, encyclopedia page, decomposition, probe set, or gate policy.
3. Re-run deterministic gates.
4. If the same class of issue recurs after two repair rounds, mark a `VerificationGap` or blocker instead of adding narrow special cases.

## 6. Prompt and agent roles

### 6.1 Index builder

Role: deterministic/local builder.

Responsibilities:

- Rebuild inventory and graph from git/filesystem truth.
- Parse code/docs/configs/tests using local tools.
- Mark generated/protected/oracle/runtime surfaces.
- Emit graph JSON and graph hash.

Allowed authority:

- May assert directly observed facts with provenance.
- May infer simple deterministic relationships using documented rules.

Forbidden:

- Must not call live LLM/API.
- Must not execute project checks except explicitly safe read-only discovery commands such as git status/ls-files/show.
- Must not treat cached graph projections as authoritative.

### 6.2 Encyclopedia writer

Role: derived documentation builder.

Responsibilities:

- Write source-linked project wiki pages.
- Explain project concepts and subsystems.
- Preserve uncertainty and contradictions.
- Avoid unsupported prose.

Allowed authority:

- May summarize graph evidence.
- May propose component candidates.

Forbidden:

- Must not decide final decomposition acceptance.
- Must not omit uncertainty for readability.

### 6.3 Grok decomposer

Role: primary AI-first decomposition reasoner.

Responsibilities:

- Produce recursive components, contracts, concerns, checks, and gaps.
- Prefer responsibility-bearing units over path buckets.
- Use graph/wiki evidence.
- Identify ambiguous leaves as gaps.

Allowed authority:

- Advisory until structural gates pass and advisory review/probe findings have been classified for repair or gap recording.

Forbidden:

- Must not invent file/symbol/contract facts.
- Must not mark `misc`, `general`, `tests`, `docs`, or `config` buckets as final success without responsibility and checks.
- Must not see held-out probes for the same snapshot before producing its decomposition.

### 6.4 Skeptic/F3 reviewer

Role: independent adversarial reviewer, preferably Opus.

Responsibilities:

- Attack wrong-target risk.
- Attack Build Arena overfit.
- Attack path-classifier leakage.
- Find missing architecture-recovery evidence.
- Find weak gates and unverifiable acceptance criteria.
- Ensure ambiguous leaves are gaps.
- Check held-out probe isolation.

Allowed authority:

- Findings are review leads until locally verified or accepted by implementation owner.
- In this task, Leon explicitly requested Opus review artifacts, so they are part of delivery evidence. For reusable future snapshot acceptance, live paid review is advisory and not required by the deterministic gate.

Forbidden:

- Must not modify files in read-only review mode.
- Must not run destructive commands or live paid acceptance tests.

### 6.5 Held-out probe builder

Role: isolated adversarial probe author.

Responsibilities:

- Build counterexamples and near-neighbor probes after primary decomposition is produced.
- Target high-risk components/contracts/concerns.
- Build or select planted negative/decoy decompositions for high-risk probes.
- Detect vague buckets, wrong target, fabricated provenance, protected-surface leakage, and no-check success.

Allowed authority:

- May read graph/wiki and the frozen decomposition summary needed to target probes.
- Must be independent from the primary decomposer by model/provider/session, or must use a deterministic planted-negative/probe generator.

Forbidden:

- Must not feed full probe corpus back into the primary decomposer for the same snapshot.
- Must not build probes from hidden operator knowledge not represented in provenance.
- Must not use repeated probe-derived repair to train the decomposer against the hidden corpus indefinitely; after two adjacent failures, record a gap or blocker.

### 6.6 Deterministic gate

Role: local validator.

Responsibilities:

- Validate graph/wiki/decomposition/probe/snapshot integrity.
- Produce pass/fail GateReport.
- Enforce no-live-paid-API acceptance checks through a command allowlist or network-disabled validation.
- Validate held-out probe presence, isolation, and discrimination results against planted negatives.

Allowed authority:

- Final blocking authority for structural snapshot usability.

Forbidden:

- Must not trust LLM prose without deterministic leaf provenance.
- Must not claim to decide unconstrained semantic wrong-targetness without explicit predicates or probe evidence.
- Must not repair artifacts; it only reports.

## 7. Held-out probe isolation policy

Held-out probes are valuable only if they are not leaked into the decomposition they test.

Policy:

1. The primary decomposer receives graph/wiki context and prompt instructions, not the generated held-out probe corpus.
2. The held-out probe builder runs after a decomposition draft exists.
3. The probe builder may see component/contract IDs and summaries, graph/wiki evidence, and gate findings, but its generated scenarios are not used to revise the same primary prompt unless a repair round explicitly creates a new snapshot attempt.
4. A repair round may use probe failures as findings, but then the next snapshot must record new prompt hashes and output hashes.
5. Prior snapshot probe directories are excluded from graph and decomposer input by default, including `.arena/project-model-snapshots/**`, `.arena/project-model/**`, and copied pilot verification outputs under `docs/verification/**`. They may be read only as historical verification artifacts when explicitly requested, and such use must be recorded as input provenance.
6. Pilot reports and `docs/verification/**` outputs are excluded from normal decomposer input to prevent report self-training.
7. Probe leakage is a gate failure when:
   - probe text appears in primary decomposer prompt inputs for the same snapshot;
   - probe IDs are referenced by decomposition before probe-building stage;
   - prior held-out-probe content hashes from earlier snapshots appear in current decomposer prompt/input bundles without historical-evidence classification;
   - prior pilot report content is treated as source truth without explicit historical-evidence classification.

Default isolation groups:

- `primary`: graph/wiki/decomposer context.
- `review`: skeptic findings.
- `probe_hidden`: held-out probe corpus not visible to primary decomposition.
- `repair_public`: validated findings allowed into a new repair attempt.

## 8. Protected-surface policy

The decomposer must identify protected surfaces and prevent arena-generated work from modifying or relying on them incorrectly.

Hard-protected in Build Arena:

- `scorer/`.
- `verifier/`.
- `schema/`.
- `.arena/scorer.lock.toml`.
- `arena/generated/` as generated output.

Policy by surface type:

1. Protected source surfaces.
   - May be read and represented in graph/wiki/decomposition.
   - Must not be proposed as modification targets for arena-generated hypotheses.
   - Must be tagged in graph and snapshot.

2. Generated surfaces.
   - Must identify generator command when known.
   - Must not be hand-edited.
   - Must not be treated as independent source truth when generator source exists.

3. Oracle/fixture/scorer/verifier surfaces.
   - Must be separated from candidate implementation surfaces.
   - Must not be used as training/context for proposed changes in a way that leaks held-out answers.
   - Must have explicit contracts to runner/scorer/verifier components.

4. Runtime/cache/build artifacts.
   - Excluded with typed reasons.
   - May appear in inventory exclusions and gate reports.

5. External credentials/secrets.
   - Must never be preserved in artifacts.
   - Credential-shaped content in local files must be redacted in wiki/model outputs and flagged if committed.

Protected-surface violations are deterministic gate blockers.

## 9. Deterministic gates

The gate suite must be deterministic, local-first, and no-live-paid-API.

Required gates:

1. Inventory coverage.
   - Every git-tracked or filesystem-discovered included file is represented.
   - Every excluded file has a typed reason.
   - Included surfaces are owned exactly once or explicitly shared through a modeled contract/concern.

2. Provenance completeness and transitive source grounding.
   - Every component, contract, concern, check, gap, and encyclopedia claim has provenance or an explicit gap.
   - Referenced paths/line anchors/hashes are resolvable.
   - Accepted repository-fact claims resolve transitively to deterministic leaf provenance, not only generated wiki/model prose.
   - Dirty-file claims cite disk hashes/dirty hashes rather than HEAD OID alone.

3. Component measurability.
   - Every component has mechanical checks or verification gaps.
   - Concrete vague/misc/general/file-bucket predicates fail.
   - Components must describe responsibilities, inputs/outputs, and boundaries.
   - High-risk or F3-prone components have near-neighbor alternatives or explicit gaps.

4. Contract references.
   - Contract endpoints exist.
   - Contracts specify assumptions, guarantees, checks/gaps, and supporting graph evidence.
   - High-risk contracts have near-neighbor alternatives or explicit gaps.

5. Cross-cutting concerns.
   - Universal concerns exist for determinism, provenance, anti-fabrication, and no-live-paid-API acceptance.
   - Conditional concerns exist only when graph evidence triggers them, such as protected/generated/oracle/fixture/provider/schema surfaces.
   - Concerns touch relevant components/contracts and cite triggering evidence.

6. Held-out probe presence, isolation, and discrimination.
   - High-risk components/contracts have probes or justified gaps.
   - Probe builder metadata and independence metadata exist.
   - Probe leakage checks pass.
   - High-risk probes are paired with planted negative/decoy decompositions and record discriminatory behavior.
   - Non-discriminating probes become gaps rather than pass signals.

7. Verification gaps.
   - Ambiguous/unverifiable leaves are represented as gaps.
   - Blocker gaps fail.
   - Gap closure criteria are explicit.

8. Protected surfaces.
   - Protected/generated/oracle surfaces are tagged.
   - Generated surfaces identify generator when known or record a gap.
   - Arena-generated hypotheses do not target protected surfaces.

9. No-live-paid-API acceptance checks.
   - Snapshot acceptance can be verified locally through an allowlisted command set or a network-disabled validation harness.
   - Any check requiring network or paid API is non-acceptance advisory or a gap.
   - The gate does not trust `requires_network=false` or `requires_paid_api=false` without allowlist/dry-run evidence.

10. Snapshot freshness.
   - Git OID, dirty fingerprint, inventory hashes, input hashes, prompt hashes, model IDs, and output hashes match the frozen artifact.
   - Dirty trees are represented honestly.

11. Output hash integrity.
   - Sidecar hashes match content.
   - ProjectModelSnapshot references the exact artifacts on disk.

12. Cached projection authority.
   - Cached graph/wiki/decomposition artifacts may only be reused if input hashes match and the run records cache use.
   - Cache mismatch fails or rebuilds.

## 10. Storage and versioning strategy

### 10.1 Artifact roots

Default local artifact root:

```text
.arena/project-model-snapshots/<snapshot_id>/
```

During documentation/pilot work, copied or summarized verification artifacts may live under:

```text
docs/verification/<date-purpose>/
```

Generated snapshot artifacts are operational sidecars. Verification docs are human-readable reports.

### 10.2 Snapshot directory layout

Default layout:

```text
.arena/project-model-snapshots/<snapshot_id>/
  manifest.json
  graph.json
  encyclopedia/
    manifest.json
    overview.md
    components/*.md
    concerns/*.md
    checks.md
    gaps.md
  decomposition.json
  near-neighbor-alternatives.json
  held-out-probes.json
  planted-negatives.json
  gate-report.json
  project-model-v0.json
  acceptance-command-allowlist.json
  prompts/
    index-builder-prompt.txt
    encyclopedia-writer-prompt.txt
    decomposer-prompt.txt
    skeptic-reviewer-prompt.txt
    held-out-probe-builder-prompt.txt
  model-outputs/
    decomposer.raw.json
    skeptic-review.raw.json
    probe-builder.raw.json
```

### 10.3 Version anchors

Each snapshot records:

- Git OID.
- Git branch.
- Dirty-state fingerprint.
- Untracked path list hash.
- Included file path/hash manifest hash.
- Excluded path/reason manifest hash.
- Graph ruleset version.
- Encyclopedia prompt hash.
- Decomposer prompt hash.
- Skeptic prompt hash.
- Held-out probe prompt hash.
- Planted-negative corpus hash.
- Acceptance command allowlist hash.
- Model IDs and provider labels.
- Raw model output hashes.
- Normalized structured output hashes.
- Gate version and gate input hash.

### 10.4 Artifact authority

Authoritative for a run:

- `manifest.json` plus referenced hashes.
- `gate-report.json` pass status.
- `decomposition.json` only if gate passes.

Derived/non-authoritative:

- Markdown encyclopedia pages.
- Human verification reports.
- Raw model outputs.
- Compatibility Project Model v0 projection.

Compatibility:

- The pipeline continues to emit Project Model v0 JSON for downstream consumers that need the older contract.
- Project Model v0 must not truncate or hide richer snapshot failures. If v0 cannot represent a blocker, the sidecar snapshot/gate remains authoritative.

## 11. Pilot and evaluation methodology

### 11.1 Pilot repos

Required pilots:

1. Build Arena itself: `/home/leonb/projects/build-arena`.
2. FMC-MPC: discover canonical local git repo under `/home/leonb/projects` or nearby project roots using path, remote, README, and status.
3. One additional Leon-owned held-out repo selected by sensible defaults:
   - different enough from Build Arena and FMC-MPC;
   - local and deterministic enough to evaluate;
   - safe to inspect without public push/deploy/merge;
   - representative of another technology/domain.

### 11.2 Per-pilot process

For each repo:

1. Inspect git status, branch, toplevel, README/docs/configs.
2. Run local tests or closest safe verification command.
3. Generate graph/wiki/decomposition/snapshot/gate report.
4. Inspect semantic plausibility:
   - components are responsibility-bearing;
   - contracts are real;
   - checks are observable;
   - protected/generated/oracle surfaces are handled;
   - verification gaps are honest;
   - no file-bucket-only decomposition passes.
5. Run deterministic gates.
6. Use Opus for read-only pilot output review.
7. Fix decomposer/spec/plan/tests based on valid issues.
8. Re-run until working or true blocker documented.

### 11.3 Evaluation dimensions

Evaluate:

- Grounding: claims cite real source.
- Generality: works across Build Arena, FMC-MPC, and held-out repo.
- Responsibility quality: components describe load-bearing project responsibilities, not paths.
- Contract quality: assume-guarantee relationships are specific and evidence-backed.
- Check quality: checks are observable and safe.
- Gap honesty: unverifiable leaves are gaps.
- Protected-surface safety.
- Held-out probe isolation and discrimination.
- Snapshot reproducibility.
- v0 compatibility.

### 11.4 Failure classification

Pilot failures are classified as:

- `BLOCKER`: snapshot unsafe to use.
- `REPAIRABLE`: decomposer/gate/spec can be fixed in this phase.
- `GAP_ACCEPTED`: honest limitation documented with safe default.
- `OUT_OF_SCOPE`: requires future phase such as live dashboard or paid model optimization.

## 12. Acceptance criteria for a working decomposer

The decomposer is working only when all are true:

1. It decomposes Build Arena without relying on current path-classifier semantics.
2. It decomposes FMC-MPC in a way that is easy for Leon to manually evaluate.
3. It decomposes one additional held-out repo without obvious Build Arena overfit.
4. It emits ProjectGraph, Encyclopedia, decomposition, held-out probe, GateReport, ProjectModelSnapshot, and Project Model v0 sidecars.
5. Sidecars are tied to git/disk truth through OIDs, dirty fingerprint, input hashes, prompt hashes, model IDs, and output hashes.
6. Every accepted claim has provenance.
7. It distinguishes mechanically testable leaves from verification gaps.
8. It represents contracts and cross-cutting concerns.
9. It protects generated/oracle/fixture/scorer/verifier/schema surfaces.
10. Deterministic gates pass for accepted snapshots, including transitive source provenance, near-neighbor alternatives, held-out-probe discrimination, conditional concern triggers, no-live-paid-API allowlist, and snapshot freshness.
11. No acceptance check requires live paid API calls.
12. Opus pilot review finds no unresolved critical blockers for this delivery, and any future reusable snapshot can still be accepted without a live Opus call if deterministic gates pass.
13. Local targeted tests, full relevant tests, lint/typecheck, artifact validation, JSON/schema validation, unresolved-placeholder scan, and `git diff --check` pass.
14. Final report explains what works, what remains weak, and what is safe to use next.

## 13. Explicit anti-patterns and mitigations

### Anti-pattern: file-bucket decomposition

Symptom: components named tests/docs/config/source/misc pass because every path has an owner.

Mitigation:

- Gate rejects concrete vague names and generic responsibilities.
- Components need inputs, outputs, responsibilities, contracts, and checks/gaps.
- High-risk components need near-neighbor alternatives.
- Held-out `vague_bucket` probes target this failure mode and must fire on planted path-bucket negatives.

### Anti-pattern: wiki becomes truth

Symptom: LLM cites generated wiki prose instead of source evidence.

Mitigation:

- Wiki claims carry provenance.
- Gate traces accepted claims back transitively to deterministic source graph/file refs.
- Wiki output hash is recorded as derived artifact only.

### Anti-pattern: LLM architecture fan fiction

Symptom: plausible components or contracts are invented without source support.

Mitigation:

- Every claim needs `ProvenanceRef` or `VerificationGap`.
- Skeptic reviewer attacks unsupported claims.
- Gate validates references and source spans.

### Anti-pattern: Project Model v0 leakage

Symptom: new pipeline just wraps current v0 buckets in richer names.

Mitigation:

- Graph/wiki must exist before decomposition.
- Components must cite graph nodes and contracts.
- Gate rejects bare path buckets.
- Pilots include FMC-MPC and held-out repo to detect Build Arena overfit.

### Anti-pattern: generated/protected/oracle leakage

Symptom: decomposer treats generated outputs or oracles as editable source surfaces.

Mitigation:

- Protected/generated/oracle classification in graph.
- Gate blockers for policy violations.
- Held-out probes target oracle/generated leakage.

### Anti-pattern: hidden live API dependency

Symptom: acceptance relies on Grok/Opus or paid APIs.

Mitigation:

- LLMs may generate artifacts, but deterministic gates and acceptance tests must run locally.
- Checks record `requires_paid_api` and `requires_network`.
- Gate fails live-paid-API acceptance tests.

### Anti-pattern: cached projection authority

Symptom: old graph/wiki/decomposition is reused after source changes.

Mitigation:

- Input hashes and dirty fingerprint required.
- Cache mismatch rebuilds or fails.
- Snapshot freshness gate validates artifact hashes.

### Anti-pattern: held-out probe leakage

Symptom: primary decomposer sees probes and learns to satisfy them superficially.

Mitigation:

- Isolation groups.
- Prompt/output hash chain.
- Gate checks stage ordering and references.

### Anti-pattern: verification gap laundering

Symptom: many severe gaps are recorded but snapshot still marked usable.

Mitigation:

- Severity policy.
- Blocker gaps fail.
- Non-blocker accepted gaps require safe default and final report disclosure.

### Anti-pattern: deterministic gate too weak

Symptom: JSON structure validates but semantics are nonsense.

Mitigation:

- Add deterministic gates for concrete vague names, generic responsibilities, absent contracts, absent checks, triggered cross-cutting concerns, transitive provenance, and held-out-probe isolation/discrimination.
- Add near-neighbor alternatives and planted negatives so wrong-target risk is visible instead of hidden behind fluent prose.
- Opus reviews pilot outputs for this delivery, while reusable acceptance remains local and deterministic.

### Anti-pattern: planted negatives become training data

Symptom: repair rounds leak decoys/probes into the primary decomposer until it overfits the hidden corpus.

Mitigation:

- Prior probe and planted-negative directories are excluded from graph/decomposer inputs by default.
- Probe-derived repair creates a new snapshot with new prompt/output hashes.
- After repeated adjacent failures, record a verification gap or blocker rather than keep tuning against the same hidden examples.

## 14. Default choices, not owner homework

The decomposer defaults are:

- Use git toplevel rather than partial subdirectory scans.
- Use git tracked inventory plus explicit untracked/dirty metadata.
- Hash raw disk bytes for included files.
- Exclude runtime/cache/build artifacts with typed reasons.
- Treat generated/protected/oracle surfaces as first-class graph nodes.
- Build graph before wiki; build wiki before LLM decomposition.
- Use Grok or strongest available leading model for primary decomposition.
- Use Opus for independent read-only review when available.
- Use local deterministic gates for pass/fail.
- Emit sidecars first; preserve Project Model v0 compatibility.
- Fail closed on vague components, missing provenance, missing checks/gaps, and protected-surface violations.
- Treat ambiguous leaves as `VerificationGap`.
- Select FMC-MPC automatically by canonical local repo discovery.
- Select a third held-out repo automatically using local ownership, domain difference, and safe deterministic verification.
- Do not ask Leon for schema mechanics, weights, probe mechanics, dirty-tree heuristics, or pilot repo selection unless no safe default can be identified.

## 15. Safe next implementation direction

The implementation should start with sidecar models and tests rather than a breaking schema rewrite.

Recommended first build slice:

1. Add failing tests for ProjectGraph sidecar creation from synthetic git repos.
2. Add deterministic graph nodes/edges for files, Python symbols/imports, tests, docs, configs, protected/generated surfaces.
3. Add encyclopedia page generation with provenance-backed Markdown.
4. Add snapshot manifest and hash validation.
5. Add structured LLM adapter seam with fixture/no-live mode for tests.
6. Add decomposition/gate sidecars and v0 compatibility output.
7. Add pilot artifact commands.

The first accepted implementation may use deterministic fixture LLM outputs in tests and live Grok/Opus only in manual pilot/review artifacts. Quality is stabilized with leading models; CI/acceptance remains local and deterministic.
