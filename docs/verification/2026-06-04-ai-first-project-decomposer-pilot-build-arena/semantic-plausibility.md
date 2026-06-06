# build-arena final recorded pilot semantic plausibility

Repo: `/home/leonb/projects/build-arena`
Selection: Required pilot 1: Build Arena itself; final acceptance uses repaired recorded Claude Opus model output after Grok Build failed to emit final JSON.
Snapshot: `/home/leonb/projects/build-arena/docs/verification/2026-06-04-ai-first-project-decomposer-pilot-build-arena/snapshot-6f712d59a3886336`
Primary model: `claude-opus-4-8`
Local verification return code: `0`
Gate passed: `True`
Components/contracts/checks/gaps/probes: 8/9/6/5/6

## Components
- `comp:project_graph` — Project Graph Builder
  - responsibility: Construct the typed code/doc graph of the repository (nodes, edges, provenance) from source and git state, serving as the shared substrate every downstream arena stage reads.
  - owned evidence: arena.project_graph
  - contracts: ['con:decomposer_uses_graph', 'con:gate_uses_graph', 'con:cli_uses_graph', 'con:encyclopedia_uses_graph']; checks: ['chk:graph_tests', 'chk:snapshot_gate_tests']; gaps: none
- `comp:project_encyclopedia` — Project Encyclopedia
  - responsibility: Enrich the raw graph into a structured, queryable knowledge surface (symbols, sections, fingerprintable descriptors) consumed by the AI decomposer.
  - owned evidence: arena.project_encyclopedia
  - contracts: ['con:decomposer_uses_encyclopedia', 'con:encyclopedia_uses_graph']; checks: ['chk:encyclopedia_tests']; gaps: none
- `comp:project_snapshot` — Project Snapshot
  - responsibility: Capture a deterministic, hashed snapshot of project state used to anchor decomposition and gating decisions to a fixed working-tree fingerprint.
  - owned evidence: arena.project_snapshot
  - contracts: ['con:decomposer_uses_snapshot', 'con:gate_uses_snapshot']; checks: ['chk:snapshot_gate_tests']; gaps: none
- `comp:ai_decomposer` — AI Project Decomposer
  - responsibility: Drive the AI-first decomposition pipeline: assemble graph/encyclopedia/snapshot context, invoke the model adapter, and emit a Project Model of responsibility-bearing components rather than path buckets.
  - owned evidence: arena.project_decomposer_ai, arena.project_model_llm
  - contracts: ['con:decomposer_uses_graph', 'con:decomposer_uses_snapshot', 'con:decomposer_uses_encyclopedia', 'con:decomposer_uses_gate']; checks: ['chk:decomposer_tests']; gaps: ['vg:llm_untested_in_isolation']
- `comp:project_model_gate` — Project Model Gate
  - responsibility: Validate and admit emitted project models against snapshot identity and structural rules, rejecting non-deterministic or fabricated decompositions before acceptance.
  - owned evidence: arena.project_model_gate
  - contracts: ['con:decomposer_uses_gate', 'con:gate_uses_graph', 'con:gate_uses_snapshot', 'con:cli_uses_gate']; checks: ['chk:snapshot_gate_tests']; gaps: none
- `comp:project_model_cli` — Project Model CLI
  - responsibility: Provide the command-line entrypoint that wires graph construction and gating into an operator-runnable project-model workflow.
  - owned evidence: arena.project_model_cli
  - contracts: ['con:cli_uses_gate', 'con:cli_uses_graph']; checks: ['chk:graph_tests']; gaps: ['vg:cli_untested']
- `comp:hypothesis_engine` — Hypothesis Engine
  - responsibility: Generate and select arena hypotheses using content fingerprints and a multi-armed-bandit policy, deduplicating candidates against the generated model surface.
  - owned evidence: arena.hypothesizer, arena.fingerprints
  - contracts: none; checks: ['chk:fingerprints_tests', 'chk:loop_phase4_tests']; gaps: ['vg:generated_surface_uncovered']
- `comp:arena_loop` — Arena Execution Loop
  - responsibility: Orchestrate the iterative arena run: enforce the execution budget, advance phases, emit events, and bound divergence across the generated model surface.
  - owned evidence: arena.loop, arena.budget
  - contracts: none; checks: ['chk:loop_phase4_tests']; gaps: ['vg:generated_surface_uncovered']

## Contracts
- `con:decomposer_uses_graph` comp:ai_decomposer -> comp:project_graph via ['imports:arena.project_graph']
- `con:decomposer_uses_snapshot` comp:ai_decomposer -> comp:project_snapshot via ['imports:arena.project_snapshot']
- `con:decomposer_uses_encyclopedia` comp:ai_decomposer -> comp:project_encyclopedia via ['imports:arena.project_encyclopedia']
- `con:decomposer_uses_gate` comp:ai_decomposer -> comp:project_model_gate via ['imports:arena.project_model_gate']
- `con:gate_uses_graph` comp:project_model_gate -> comp:project_graph via ['imports:arena.project_graph']
- `con:gate_uses_snapshot` comp:project_model_gate -> comp:project_snapshot via ['imports:arena.project_snapshot']
- `con:cli_uses_gate` comp:project_model_cli -> comp:project_model_gate via ['imports:arena.project_model_gate']
- `con:cli_uses_graph` comp:project_model_cli -> comp:project_graph via ['imports:arena.project_graph']
- `con:encyclopedia_uses_graph` comp:project_encyclopedia -> comp:project_graph via ['imports:arena.project_graph']

## Verification gaps
- `vg:cli_untested` (high): Project Model CLI has no observed tests/ import edge in the packet; its entrypoint wiring is unverified by the suite.
- `vg:llm_untested_in_isolation` (medium): arena.project_model_llm is reached only via the decomposer (edge:7e02ea209da7795bff6a) and has no direct test import; its model-adapter logic is not independently verified.
- `vg:generated_surface_uncovered` (medium): surface_counts.generated=4 but only three generated nodes (models.py, schema.json, ddl.sql) appear in the packet; one generated surface is not represented or componentized.
- `vg:protected_surfaces_unowned` (low): Ten protected surfaces (scorer/*, verifier/*, schema/arena.yaml) are intentionally excluded from arena ownership per non-goals and therefore remain unverified by this decomposition.
- `vg:dirty_tree_nondeterminism` (medium): git_dirty=true with many uncommitted arena/ and docs/ paths; this decomposition was derived from an uncommitted working tree and may not reproduce from a clean checkout.

## Assessment
- Final output is not fixture mode; it records Claude Opus model output plus independent Sonnet probe-builder artifacts after Grok Build failed to emit final JSON.
- Components are model-derived responsibility units; some intentionally group multiple source modules or explicit static/doc surfaces.
- Contracts are only gate-passing deterministic graph edges; unsupported semantic dependencies are retained as verification gaps.
- Observable checks match the actual command run for the repo.
- Protected/generated surfaces are graph-visible and excluded from component ownership.
- Negative-control artifacts demonstrate the gate rejects a plausible fluent file-bucket model output.
