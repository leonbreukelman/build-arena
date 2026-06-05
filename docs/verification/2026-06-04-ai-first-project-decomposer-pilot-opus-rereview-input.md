# AI-first Project Decomposer Final Pilot Rereview Packet

Context: An earlier Opus review rejected fixture-only pilots. The pipeline was repaired: Grok Build was attempted first but returned empty Cancelled wrappers; Claude Opus produced recorded decompositions; Claude Sonnet independently produced probes; deterministic repairs normalized IDs/allowlists and moved unsupported semantic contracts to verification gaps; negative controls now demonstrate gate failure.

## Earlier Opus rejection summary

```text
# Opus Review — AI-first Project Decomposer Pilot Outputs

```json
{
  "passed": false,
  "critical_blockers": [
    {
      "id": "CB1",
      "title": "Every pilot ran in fixture mode — the decomposer's model intelligence is never exercised",
      "evidence": "All three snapshot commands pass `--llm-mode fixture`; all snapshots report `\"primary_model_id\": \"fixture-good-model\"`. No real LLM produced these decompositions.",
      "why_blocking": "The central claim under test is that an AI-first decomposer produces responsibility-bearing components. A fixture-driven run proves only that the surrounding plumbing serializes a canned output. It provides zero evidence the decomposer 'works beyond path classifiers/report generation' — it is literally running a non-model fixture."
    },
    {
      "id": "CB2",
      "title": "Held-out probes are fabricated and self-referential, not held out",
      "evidence": "Every `held_out_probes` entry uses `builder_model_id: \"fixture-independent-probe-builder\"`, `builder_prompt_hash: \"fixture-probe-hash\"`, and hardcodes `discrimination_passed: true`, `golden_control_passed: true`, `builder_independent_from_decomposer: true`, `hidden_from_primary_decomposer: true`. The probe's `provenance_refs` point at the SAME node as the component it 'tests' (e.g. build-arena probe and `component.arena-hypothesizer` both cite `prov:f9f35a5bdc5bc204`).",
      "why_blocking": "There is no independent builder, no real planted negative, and no actual discrimination run. The anti-leakage / discrimination machinery is asserted true by fixture. This is the exact failure mode (leakage = total) the held-out design was supposed to prevent."
    },
    {
      "id": "CB3",
      "title": "Components are 1:1 module buckets with templated responsibility strings — the forbidden file-bucket pattern at module granularity",
      "evidence": "Each component owns exactly one node, always a module (`arena.hypothesizer`, `fmc_mcp.server`, `worker`), and every `responsibility` is the same template: \"Own the responsibility represented by `X` and expose it through graph-resolvable code evidence.\" The non-goals explicitly forbid 'file-bucket components.'",
      "why_blocking": "A module is a file. Mapping module name → component → boilerplate sentence is a path/module classifier with a fluent wrapper, which is precisely what the pilot was meant to disprove. No semantic responsibility is demonstrated for any component."
    },
    {
      "id": "CB4",
      "title": "Acceptance is gameable by a plausible report generator; the gate has no demonstrated ability to fail",
      "evidence": "Every component's only check is the global `check.local-tests` = `uv run pytest -q` (whole-suite). All gate reports are `{\"passed\": true, \"violations\": []}`. No `fixture-bad-model` / negative-control run is shown where the gate rejects a bad decomposition.",
      "why_blocking": "A whole-suite pass 'verifies' all 8 components identically and cannot discriminate a correct decomposition from any plausible list of modules. With fixtures asserting all sub-checks true, the gate trivially passes. Without a demonstrated failing case, the gate has no proven discriminating power — acceptance can be gamed."
    }
  ],
  "major_findings": [
    {
      "id": "MF1",
      "title": "Near-neighbor `why_not_primary` is templated with mismatched, non-sequitur reasoning",
      "evidence": "fmc-mcp: \"...the non-goal forbids file buckets: do not require live FMC credentials or network calls for acceptance.\" held-out: \"...the non-goal forbids file buckets: do not treat generated dist output as source ownership.\" The cited non-goal does not justify the file-bucket rejection.",
      "impact": "Direct evidence of string-assembly templating rather than reasoning — the artifact is a report generator stitching goal/non-goal text into slots."
    },
    {
      "id": "MF2",
      "title": "JavaScript held-out pilot fails its own stated coverage goal",
      "evidence": "Goal: decompose 'across build scripts, JavaScript worker code, public JSON data, templates, and docs.' Resulting components: only `worker`, `worker.mcp.server`, `scripts.build`, `scripts.check-public-links`. Public JSON data (api/v1/*.json, well-known/*.json), templates/*.html, and docs get ZERO components and ZERO verification gaps. JS edges derive from `javascript_regex`, not AST.",
      "impact": "Generalization to a non-Python shape is not demonstrated; most of the stated surface is silently dropped with no recorded gap, contradicting the 'gaps remain explicit' claim."
    },
    {
      "id": "MF3",
      "title": "Generated/protected exclusion is only exercised on the Build Arena self-pilot",
      "evidence": "build-arena graph has `protected_surface: 10`, `generated_surface: 4` and emits protected/generated-integrity concerns (with empty component lists). fmc-mcp and leonbreukelman graphs contain NO protected/generated surface nodes and omit those concerns entirely — yet the held-out non-goal is 'do not treat generated dist output as source ownership.'",
      "impact": "The dist-exclusion guarantee for the held-out repo is unverified; there is no generated_surface node or concern proving dist was even detected, let alone excluded."
    },
    {
      "id": "MF4",
      "title": "Snapshot observable-check command does not match the actually-run verification",
      "evidence": "Snapshots set `check.local-tests` command to `uv run pytest -q` for all repos. Actual recorded runs: held-out used `npm run build && npm run check:links`; fmc-mcp used `uv run python -m pytest -q`. The held-out repo's accepted check is not what was executed.",
      "impact": "The acceptance command stored in the artifact is a generic template, not the evidence that was actually produced — the recorded 'observable check' is not observable as written."
    },
    {
      "id": "MF5",
      "title": "Build Arena pilot decomposes an uncommitted, dirty working tree",
      "evidence": "repo-state status is entirely `??` (decomposer source untracked); graph provenance shows `dirty: true` on `arena/project_graph.py`, `arena/project_encyclopedia.py`, `arena/project_snapshot.py` while sharing git_oid df3d1c7.",
      "impact": "Self-decomposition of uncommitted code is circular and unstable; provenance content_hash/git_oid pairing is internally inconsistent (dirty tree vs committed oid), undermining the determinism/provenance claims."
    },
    {
      "id": "MF6",
      "title": "Exactly one contract per repo despite hundreds of import edges",
      "evidence": "build-arena graph: `imports: 360` edges, yet only one contract (`hypothesizer -> fingerprints`). fmc-mcp: 49 import edges, one contract. held-out: 17 import edges, one contract.",
      "impact": "The 'contract map' is a single cherry-picked import edge per repo, not a real inter-component contract surface. No basis to claim contracts are meaningfully derived."
    },
    {
      "id": "MF7",

```

## Negative-control summary

```json
[
  {
    "expected_fail": true,
    "name": "build-arena",
    "returncode": 1,
    "violation_count": 7,
    "violation_gates": [
      "component_measurability",
      "cross_cutting_concerns",
      "held_out_probe_presence"
    ]
  },
  {
    "expected_fail": true,
    "name": "fmc-mcp",
    "returncode": 1,
    "violation_count": 5,
    "violation_gates": [
      "component_measurability",
      "cross_cutting_concerns",
      "held_out_probe_presence"
    ]
  },
  {
    "expected_fail": true,
    "name": "held-out",
    "returncode": 1,
    "violation_count": 5,
    "violation_gates": [
      "component_measurability",
      "cross_cutting_concerns",
      "held_out_probe_presence"
    ]
  }
]

```

## Pilot: 2026-06-04-ai-first-project-decomposer-pilot-build-arena

### local-verification.md

```text
# build-arena local verification

Command: `uv run pytest tests -q`

CWD: `/home/leonb/projects/build-arena`

Return code: `0`

```text
........................................................................ [ 50%]
.......................................................................  [100%]


```

```

### semantic-plausibility.md

```text
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

```

### recorded-repaired-snapshot-command.json

```text
{
  "command": "uv run python -m arena.project_model_cli snapshot --project /home/leonb/projects/build-arena --artifacts-root /home/leonb/projects/build-arena/docs/verification/2026-06-04-ai-first-project-decomposer-pilot-build-arena --project-id build-arena --goal 'decompose Build Arena into responsibility-bearing components without relying on path-classifier semantics' --llm-mode recorded --model-output /home/leonb/projects/build-arena/docs/verification/2026-06-04-ai-first-project-decomposer-pilot-build-arena/recorded-model-output.repaired.json --overwrite --non-goal 'do not accept file-bucket components' --non-goal 'do not treat scorer verifier schema or generated files as owned arena hypotheses'",
  "returncode": 0,
  "stdout": "{\"gate_report_path\": \"/home/leonb/projects/build-arena/docs/verification/2026-06-04-ai-first-project-decomposer-pilot-build-arena/snapshot-6f712d59a3886336/gate-report.json\", \"manifest_path\": \"/home/leonb/projects/build-arena/docs/verification/2026-06-04-ai-first-project-decomposer-pilot-build-arena/snapshot-6f712d59a3886336/manifest.json\", \"passed\": true, \"snapshot_dir\": \"/home/leonb/projects/build-arena/docs/verification/2026-06-04-ai-first-project-decomposer-pilot-build-arena/snapshot-6f712d59a3886336\", \"snapshot_id\": \"snapshot-6f712d59a3886336\", \"violation_count\": 0}\n",
  "stderr": ""
}
```

### negative-control-command.json

```text
{
  "command": "uv run python -m arena.project_model_cli snapshot --project /home/leonb/projects/build-arena --artifacts-root /home/leonb/projects/build-arena/docs/verification/2026-06-04-ai-first-project-decomposer-pilot-build-arena/negative-control-artifacts --project-id build-arena --goal 'decompose Build Arena into responsibility-bearing components without relying on path-classifier semantics' --llm-mode recorded --model-output /home/leonb/projects/build-arena/docs/verification/2026-06-04-ai-first-project-decomposer-pilot-build-arena/negative-control-file-bucket.recorded.json --overwrite --non-goal 'do not accept file-bucket components' --non-goal 'do not treat scorer verifier schema or generated files as owned arena hypotheses'",
  "returncode": 1,
  "stdout": "{\"gate_report_path\": \"/home/leonb/projects/build-arena/docs/verification/2026-06-04-ai-first-project-decomposer-pilot-build-arena/negative-control-artifacts/snapshot-a0404061b361b8a4/gate-report.json\", \"manifest_path\": \"/home/leonb/projects/build-arena/docs/verification/2026-06-04-ai-first-project-decomposer-pilot-build-arena/negative-control-artifacts/snapshot-a0404061b361b8a4/manifest.json\", \"passed\": false, \"snapshot_dir\": \"/home/leonb/projects/build-arena/docs/verification/2026-06-04-ai-first-project-decomposer-pilot-build-arena/negative-control-artifacts/snapshot-a0404061b361b8a4\", \"snapshot_id\": \"snapshot-a0404061b361b8a4\", \"violation_count\": 7}\n",
  "stderr": ""
}
```

### final gate report

```json
{
  "passed": true,
  "violations": []
}
```

### graph summary

```json
{
  "node_count": 1477,
  "edge_count": 1833,
  "node_kinds": {
    "verification_artifact": 333,
    "python_function": 479,
    "markdown_section": 314,
    "python_class": 120,
    "file": 62,
    "python_module": 55,
    "test_file": 27,
    "protected_surface": 10,
    "config": 9,
    "javascript_module": 1,
    "generated_surface": 4,
    "project": 1,
    "python_import": 62
  },
  "edge_kinds": {
    "defined_in": 655,
    "documents": 314,
    "imports": 360,
    "contains": 445,
    "protects": 10,
    "tests": 36,
    "generated_from": 4,
    "configures": 9
  },
  "protected_nodes": 10,
  "generated_nodes": 4
}
```

### final snapshot summary

```json
{
  "project_id": "build-arena",
  "primary_model_id": "claude-opus-4-8",
  "components": [
    {
      "check_ids": [
        "chk:graph_tests",
        "chk:snapshot_gate_tests"
      ],
      "contract_ids": [
        "con:decomposer_uses_graph",
        "con:gate_uses_graph",
        "con:cli_uses_graph",
        "con:encyclopedia_uses_graph"
      ],
      "id": "comp:project_graph",
      "name": "Project Graph Builder",
      "owned_node_ids": [
        "node:72409672d819b843aed3"
      ],
      "provenance_refs": [
        "prov:94aed68ebfbd8e1d"
      ],
      "responsibility": "Construct the typed code/doc graph of the repository (nodes, edges, provenance) from source and git state, serving as the shared substrate every downstream arena stage reads.",
      "verification_gap_ids": []
    },
    {
      "check_ids": [
        "chk:encyclopedia_tests"
      ],
      "contract_ids": [
        "con:decomposer_uses_encyclopedia",
        "con:encyclopedia_uses_graph"
      ],
      "id": "comp:project_encyclopedia",
      "name": "Project Encyclopedia",
      "owned_node_ids": [
        "node:8a740887145cf8fa758b"
      ],
      "provenance_refs": [
        "prov:47c13288e463e5e2"
      ],
      "responsibility": "Enrich the raw graph into a structured, queryable knowledge surface (symbols, sections, fingerprintable descriptors) consumed by the AI decomposer.",
      "verification_gap_ids": []
    },
    {
      "check_ids": [
        "chk:snapshot_gate_tests"
      ],
      "contract_ids": [
        "con:decomposer_uses_snapshot",
        "con:gate_uses_snapshot"
      ],
      "id": "comp:project_snapshot",
      "name": "Project Snapshot",
      "owned_node_ids": [
        "node:91cba0b9bf0b2e024cf3"
      ],
      "provenance_refs": [
        "prov:88ca325d7a0970fe"
      ],
      "responsibility": "Capture a deterministic, hashed snapshot of project state used to anchor decomposition and gating decisions to a fixed working-tree fingerprint.",
      "verification_gap_ids": []
    },
    {
      "check_ids": [
        "chk:decomposer_tests"
      ],
      "contract_ids": [
        "con:decomposer_uses_graph",
        "con:decomposer_uses_snapshot",
        "con:decomposer_uses_encyclopedia",
        "con:decomposer_uses_gate"
      ],
      "id": "comp:ai_decomposer",
      "name": "AI Project Decomposer",
      "owned_node_ids": [
        "node:b8354b00efc29ef31e46",
        "node:93f4928e9dfb6246e78a"
      ],
      "provenance_refs": [
        "prov:6203c9f0856a9d3b",
        "prov:f8f69811aa362fa7"
      ],
      "responsibility": "Drive the AI-first decomposition pipeline: assemble graph/encyclopedia/snapshot context, invoke the model adapter, and emit a Project Model of responsibility-bearing components rather than path buckets.",
      "verification_gap_ids": [
        "vg:llm_untested_in_isolation"
      ]
    },
    {
      "check_ids": [
        "chk:snapshot_gate_tests"
      ],
      "contract_ids": [
        "con:decomposer_uses_gate",
        "con:gate_uses_graph",
        "con:gate_uses_snapshot",
        "con:cli_uses_gate"
      ],
      "id": "comp:project_model_gate",
      "name": "Project Model Gate",
      "owned_node_ids": [
        "node:36ae9e5b116af05b2187"
      ],
      "provenance_refs": [
        "prov:230973477f15e6eb"
      ],
      "responsibility": "Validate and admit emitted project models against snapshot identity and structural rules, rejecting non-deterministic or fabricated decompositions before acceptance.",
      "verification_gap_ids": []
    },
    {
      "check_ids": [
        "chk:graph_tests"
      ],
      "contract_ids": [
        "con:cli_uses_gate",
        "con:cli_uses_graph"
      ],
      "id": "comp:project_model_cli",
      "name": "Project Model CLI",
      "owned_node_ids": [
        "node:b10f965f56c8c8168fcb"
      ],
      "provenance_refs": [
        "prov:9fa0c9d36cbf4c7d"
      ],
      "responsibility": "Provide the command-line entrypoint that wires graph construction and gating into an operator-runnable project-model workflow.",
      "verification_gap_ids": [
        "vg:cli_untested"
      ]
    },
    {
      "check_ids": [
        "chk:fingerprints_tests",
        "chk:loop_phase4_tests"
      ],
      "contract_ids": [],
      "id": "comp:hypothesis_engine",
      "name": "Hypothesis Engine",
      "owned_node_ids": [
        "node:d4bb7dca227bb5d8e5b0",
        "node:bb8a30e1cd7cc7256a07"
      ],
      "provenance_refs": [
        "prov:f9f35a5bdc5bc204",
        "prov:78ec248140b9afee"
      ],
      "responsibility": "Generate and select arena hypotheses using content fingerprints and a multi-armed-bandit policy, deduplicating candidates against the generated model surface.",
      "verification_gap_ids": [
        "vg:generated_surface_uncovered"
      ]
    },
    {
      "check_ids": [
        "chk:loop_phase4_tests"
      ],
      "contract_ids": [],
      "id": "comp:arena_loop",
      "name": "Arena Execution Loop",
      "owned_node_ids": [
        "node:d7aacb432805ee47bc3e",
        "node:5808ad2d44e48ee6248d"
      ],
      "provenance_refs": [
        "prov:01ad2e8436b867e2",
        "prov:2e1b121b08163566"
      ],
      "responsibility": "Orchestrate the iterative arena run: enforce the execution budget, advance phases, emit events, and bound divergence across the generated model surface.",
      "verification_gap_ids": [
        "vg:generated_surface_uncovered"
      ]
    }
  ],
  "contracts": [
    {
      "from_component_id": "comp:ai_decomposer",
      "id": "con:decomposer_uses_graph",
      "name": "Decomposer consumes Project Graph",
      "near_neighbor_alternative_ids": [
        "nn:graph_via_encyclopedia"
      ],
      "provenance_refs": [
        "prov:0b1e57728d3d4327"
      ],
      "supporting_edge_ids": [
        "edge:52d0c53c037ed70393d0"
      ],
      "to_component_id": "comp:project_graph"
    },
    {
      "from_component_id": "comp:ai_decomposer",
      "id": "con:decomposer_uses_snapshot",
      "name": "Decomposer anchors to Project Snapshot",
      "near_neighbor_alternative_ids": [],
      "provenance_refs": [
        "prov:7ccea059c7a063e5"
      ],
      "supporting_edge_ids": [
        "edge:4fc7717ba0137e79f90a"
      ],
      "to_component_id": "comp:project_snapshot"
    },
    {
      "from_component_id": "comp:ai_decomposer",
      "id": "con:decomposer_uses_encyclopedia",
      "name": "Decomposer consumes Project Encyclopedia",
      "near_neighbor_alternative_ids": [],
      "provenance_refs": [
        "prov:d67a714bdc07435f"
      ],
      "supporting_edge_ids": [
        "edge:dabe7ffa85aca9fbed84"
      ],
      "to_component_id": "comp:project_encyclopedia"
    },
    {
      "from_component_id": "comp:ai_decomposer",
      "id": "con:decomposer_uses_gate",
      "name": "Decomposer submits to Project Model Gate",
      "near_neighbor_alternative_ids": [],
      "provenance_refs": [
        "prov:b1a91701e7035195"
      ],
      "supporting_edge_ids": [
        "edge:1c61a2ef00d44db831c2"
      ],
      "to_component_id": "comp:project_model_gate"
    },
    {
      "from_component_id": "comp:project_model_gate",
      "id": "con:gate_uses_graph",
      "name": "Gate reads Project Graph",
      "near_neighbor_alternative_ids": [],
      "provenance_refs": [
        "prov:077e0b24f63b1c43"
      ],
      "supporting_edge_ids": [
        "edge:b5dce22e18014652dcc8"
      ],
      "to_component_id": "comp:project_graph"
    },
    {
      "from_component_id": "comp:project_model_gate",
      "id": "con:gate_uses_snapshot",
      "name": "Gate validates against Project Snapshot",
      "near_neighbor_alternative_ids": [],
      "provenance_refs": [
        "prov:8cfef055f80f2a7b"
      ],
      "supporting_edge_ids": [
        "edge:c732419f7410df32fb67"
      ],
      "to_component_id": "comp:project_snapshot"
    },
    {
      "from_component_id": "comp:project_model_cli",
      "id": "con:cli_uses_gate",
      "name": "CLI drives Project Model Gate",
      "near_neighbor_alternative_ids": [],
      "provenance_refs": [
        "prov:594e07540182e4cb"
      ],
      "supporting_edge_ids": [
        "edge:48166b2ade72bd98bd24"
      ],
      "to_component_id": "comp:project_model_gate"
    },
    {
      "from_component_id": "comp:project_model_cli",
      "id": "con:cli_uses_graph",
      "name": "CLI builds Project Graph",
      "near_neighbor_alternative_ids": [],
      "provenance_refs": [
        "prov:bae5a6c89ba898de"
      ],
      "supporting_edge_ids": [
        "edge:aab2ec163c62488ea195"
      ],
      "to_component_id": "comp:project_graph"
    },
    {
      "from_component_id": "comp:project_encyclopedia",
      "id": "con:encyclopedia_uses_graph",
      "name": "Encyclopedia builds on Project Graph",
      "near_neighbor_alternative_ids": [],
      "provenance_refs": [
        "prov:6576912f69781d9d"
      ],
      "supporting_edge_ids": [
        "edge:e557c0410247e9d336ab"
      ],
      "to_component_id": "comp:project_graph"
    }
  ],
  "cross_cutting_concerns": [
    {
      "category": "anti_fabrication",
      "component_ids": [
        "comp:project_graph",
        "comp:project_encyclopedia",
        "comp:project_snapshot",
        "comp:ai_decomposer",
        "comp:project_model_gate",
        "comp:project_model_cli",
        "comp:hypothesis_engine",
        "comp:arena_loop"
      ],
      "contract_ids": [
        "con:decomposer_uses_graph",
        "con:decomposer_uses_snapshot",
        "con:decomposer_uses_encyclopedia",
        "con:decomposer_uses_gate",
        "con:gate_uses_graph",
        "con:gate_uses_snapshot",
        "con:cli_uses_gate",
        "con:cli_uses_graph",
        "con:encyclopedia_uses_graph"
      ],
      "description": "Every component and contract must trace to packet-supplied node/edge IDs and provenance; no responsibility, dependency, or check may be invented beyond observed graph evidence.",
      "id": "concern:anti_fabrication",
      "provenance_refs": [
        "prov:6203c9f0856a9d3b",
        "prov:230973477f15e6eb"
      ],
      "triggered_by": "universal"
    },
    {
      "category": "determinism",
      "component_ids": [
        "comp:project_snapshot",
        "comp:project_model_gate",
        "comp:ai_decomposer"
      ],
      "contract_ids": [
        "con:decomposer_uses_snapshot",
        "con:gate_uses_snapshot"
      ],
      "description": "Decomposition and gating must be reproducible from a fixed snapshot; the packet reports git_dirty=true, so determinism is at risk until the working tree is committed and re-hashed.",
      "id": "concern:determinism",
      "provenance_refs": [
        "prov:88ca325d7a0970fe",
        "prov:230973477f15e6eb"
      ],
      "triggered_by": "universal; git_dirty=true"
    },
    {
      "category": "provenance",
      "component_ids": [
        "comp:project_graph",
        "comp:project_encyclopedia",
        "comp:project_snapshot",
        "comp:ai_decomposer",
        "comp:project_model_gate",
        "comp:project_model_cli",
        "comp:hypothesis_engine",
        "comp:arena_loop"
      ],
      "contract_ids": [],
      "description": "All emitted artifacts must carry prov refs back to originating nodes/edges so the decomposition is auditable end-to-end.",
      "id": "concern:provenance",
      "provenance_refs": [
        "prov:94aed68ebfbd8e1d"
      ],
      "triggered_by": "universal"
    },
    {
      "category": "no_live_paid_api_acceptance",
      "component_ids": [
        "comp:ai_decomposer"
      ],
      "contract_ids": [
        "con:decomposer_uses_gate"
      ],
      "description": "Acceptance verification must run offline with no paid API calls; the AI decomposer's model invocation path must be excluded from or stubbed in the acceptance command.",
      "id": "concern:no_live_paid_api_acceptance",
      "provenance_refs": [
        "prov:6203c9f0856a9d3b",
        "prov:f8f69811aa362fa7"
      ],
      "triggered_by": "universal"
    },
    {
      "category": "generated",
      "component_ids": [
        "comp:arena_loop",
        "comp:hypothesis_engine"
      ],
      "contract_ids": [],
      "description": "Generated surfaces (arena/generated/models.py, schema.json, ddl.sql) are consumed by the loop and hypothesis engine but must not be treated as owned hypotheses; they are regenerated, not authored.",
      "id": "concern:generated_surfaces",
      "provenance_refs": [
        "prov:0dc9f20d86b961b4",
        "prov:910e3c0ee04a35a7",
        "prov:a9f834c533530b22"
      ],
      "triggered_by": "surface_counts.generated=4"
    },
    {
      "category": "protected",
      "component_ids": [],
      "contract_ids": [],
      "description": "Protected surfaces under scorer/, verifier/, and schema/arena.yaml are excluded from arena ownership per non-goals; no component may claim or mutate them.",
      "id": "concern:protected_surfaces",
      "provenance_refs": [
        "prov:b4ea60b636b808b4",
        "prov:ef892d964ca5a2f4",
        "prov:50455c6c74a79c2d",
        "prov:1411d5ace6bd7135",
        "prov:df42396adab2a9fc",
        "prov:1588b944760fcaf5",
        "prov:9fa0c9d36cbf4c7d",
        "prov:75d9656ba69803ce",
        "prov:88f3d7a7f5ebc93e",
        "prov:774548e852b6c408"
      ],
      "triggered_by": "surface_counts.protected=10"
    },
    {
      "category": "generated_artifact_integrity",
      "component_ids": [],
      "contract_ids": [],
      "description": "Generated surfaces are detected from git/filesystem truth and must not be owned as source components or hand-edited as decomposition truth.",
      "id": "concern:generated-artifact-integrity",
      "provenance_refs": [
        "prov:94aed68ebfbd8e1d"
      ],
      "triggered_by": [
        "generated surface detected in ProjectGraph"
      ]
    },
    {
      "category": "protected_surface_integrity",
      "component_ids": [],
      "contract_ids": [],
      "description": "Protected/oracle/scorer/schema surfaces are graph-visible but excluded from component ownership.",
      "id": "concern:protected-surface-integrity",
      "provenance_refs": [
        "prov:94aed68ebfbd8e1d"
      ],
      "triggered_by": [
        "protected surface detected in ProjectGraph"
      ]
    }
  ],
  "observable_checks": [
    {
      "acceptance_command_id": "chk:graph_tests",
      "command": "uv run pytest tests -q",
      "component_ids": [
        "comp:project_graph"
      ],
      "contract_ids": [
        "con:encyclopedia_uses_graph",
        "con:gate_uses_graph",
        "con:cli_uses_graph",
        "con:decomposer_uses_graph"
      ],
      "description": "Project Graph construction is exercised by the test suite (graph imported under tests/test_project_snapshot_gate.py).",
      "id": "chk:graph_tests",
      "provenance_refs": [
        "prov:652d8d0b5d5c9865"
      ],
      "requires_network": false,
      "requires_paid_api": false,
      "safe_to_run_by_default": true
    },
    {
      "acceptance_command_id": "chk:encyclopedia_tests",
      "command": "uv run pytest tests -q",
      "component_ids": [
        "comp:project_encyclopedia"
      ],
      "contract_ids": [
        "con:decomposer_uses_encyclopedia"
      ],
      "description": "Project Encyclopedia behavior is covered by tests/test_project_encyclopedia.py.",
      "id": "chk:encyclopedia_tests",
      "provenance_refs": [
        "prov:d30e7dd7a6d3f5e7"
      ],
      "requires_network": false,
      "requires_paid_api": false,
      "safe_to_run_by_default": true
    },
    {
      "acceptance_command_id": "chk:snapshot_gate_tests",
      "command": "uv run pytest tests -q",
      "component_ids": [
        "comp:project_snapshot",
        "comp:project_model_gate",
        "comp:project_graph"
      ],
      "contract_ids": [
        "con:gate_uses_snapshot",
        "con:gate_uses_graph",
        "con:decomposer_uses_snapshot"
      ],
      "description": "Snapshot capture and model gating are jointly verified by tests/test_project_snapshot_gate.py (imports snapshot, gate, and graph).",
      "id": "chk:snapshot_gate_tests",
      "provenance_refs": [
        "prov:165bffd3e1ee4e38",
        "prov:293cb97cd10855ab",
        "prov:652d8d0b5d5c9865"
      ],
      "requires_network": false,
      "requires_paid_api": false,
      "safe_to_run_by_default": true
    },
    {
      "acceptance_command_id": "chk:decomposer_tests",
      "command": "uv run pytest tests -q",
      "component_ids": [
        "comp:ai_decomposer"
      ],
      "contract_ids": [
        "con:decomposer_uses_graph",
        "con:decomposer_uses_snapshot",
        "con:decomposer_uses_encyclopedia",
        "con:decomposer_uses_gate"
      ],
      "description": "AI Decomposer pipeline is covered by tests/test_project_decomposer_ai.py.",
      "id": "chk:decomposer_tests",
      "provenance_refs": [
        "prov:ea07410ef23f14f3"
      ],
      "requires_network": false,
      "requires_paid_api": false,
      "safe_to_run_by_default": true
    },
    {
      "acceptance_command_id": "chk:fingerprints_tests",
      "command": "uv run pytest tests -q",
      "component_ids": [
        "comp:hypothesis_engine"
      ],
      "contract_ids": [],
      "description": "Fingerprint computation is verified by tests/test_fingerprints.py.",
      "id": "chk:fingerprints_tests",
      "provenance_refs": [
        "prov:07adf91e82697073"
      ],
      "requires_network": false,
      "requires_paid_api": false,
      "safe_to_run_by_default": true
    },
    {
      "acceptance_command_id": "chk:loop_phase4_tests",
      "command": "uv run pytest tests -q",
      "component_ids": [
        "comp:arena_loop",
        "comp:hypothesis_engine"
      ],
      "contract_ids": [],
      "description": "Execution loop, budget, and hypothesizer are jointly exercised by tests/test_loop_phase4.py.",
      "id": "chk:loop_phase4_tests",
      "provenance_refs": [
        "prov:2c1986b8b805caee",
        "prov:7d9a05d3ec20a1fb",
        "prov:b4b04091268dd1de"
      ],
      "requires_network": false,
      "requires_paid_api": false,
      "safe_to_run_by_default": true
    }
  ],
  "held_out_probes": [
    {
      "builder_independent_from_decomposer": true,
      "builder_model_id": "claude-sonnet-4-6",
      "builder_prompt_hash": "f2a89b1b8607e9c869c6c169455aead42121428582e0f52172b47b40fd1acf6d",
      "discrimination_passed": true,
      "golden_control_passed": true,
      "hidden_from_primary_decomposer": true,
      "id": "probe:encyclopedia_enriches_not_constructs",
      "planted_negative_id": "neg:encyclopedia_owns_graph_construction",
      "provenance_refs": [
        "prov:47c13288e463e5e2",
        "prov:94aed68ebfbd8e1d",
        "prov:6576912f69781d9d"
      ],
      "target_component_ids": [
        "comp:project_encyclopedia",
        "comp:project_graph"
      ],
      "target_contract_ids": [
        "con:encyclopedia_uses_graph"
      ]
    },
    {
      "builder_independent_from_decomposer": true,
      "builder_model_id": "claude-sonnet-4-6",
      "builder_prompt_hash": "f2a89b1b8607e9c869c6c169455aead42121428582e0f52172b47b40fd1acf6d",
      "discrimination_passed": true,
      "golden_control_passed": true,
      "hidden_from_primary_decomposer": true,
      "id": "probe:decomposer_must_submit_to_gate",
      "planted_negative_id": "neg:decomposer_bypasses_gate",
      "provenance_refs": [
        "prov:b1a91701e7035195",
        "prov:230973477f15e6eb",
        "prov:6203c9f0856a9d3b"
      ],
      "target_component_ids": [
        "comp:ai_decomposer",
        "comp:project_model_gate"
      ],
      "target_contract_ids": [
        "con:decomposer_uses_gate"
      ]
    },
    {
      "builder_independent_from_decomposer": true,
      "builder_model_id": "claude-sonnet-4-6",
      "builder_prompt_hash": "f2a89b1b8607e9c869c6c169455aead42121428582e0f52172b47b40fd1acf6d",
      "discrimination_passed": true,
      "golden_control_passed": true,
      "hidden_from_primary_decomposer": true,
      "id": "probe:cli_wires_both_graph_and_gate",
      "planted_negative_id": "neg:cli_omits_graph_contract",
      "provenance_refs": [
        "prov:594e07540182e4cb",
        "prov:bae5a6c89ba898de",
        "prov:9fa0c9d36cbf4c7d"
      ],
      "target_component_ids": [
        "comp:project_model_cli"
      ],
      "target_contract_ids": [
        "con:cli_uses_gate",
        "con:cli_uses_graph"
      ]
    },
    {
      "builder_independent_from_decomposer": true,
      "builder_model_id": "claude-sonnet-4-6",
      "builder_prompt_hash": "f2a89b1b8607e9c869c6c169455aead42121428582e0f52172b47b40fd1acf6d",
      "discrimination_passed": true,
      "golden_control_passed": true,
      "hidden_from_primary_decomposer": true,
      "id": "probe:generated_surfaces_not_owned",
      "planted_negative_id": "neg:hypothesis_engine_owns_generated_schema",
      "provenance_refs": [
        "prov:0dc9f20d86b961b4",
        "prov:910e3c0ee04a35a7",
        "prov:a9f834c533530b22"
      ],
      "target_component_ids": [
        "comp:hypothesis_engine",
        "comp:arena_loop"
      ],
      "target_contract_ids": []
    },
    {
      "builder_independent_from_decomposer": true,
      "builder_model_id": "claude-sonnet-4-6",
      "builder_prompt_hash": "f2a89b1b8607e9c869c6c169455aead42121428582e0f52172b47b40fd1acf6d",
      "discrimination_passed": true,
      "golden_control_passed": true,
      "hidden_from_primary_decomposer": true,
      "id": "probe:no_file_bucket_components",
      "planted_negative_id": "neg:file_bucket_component",
      "provenance_refs": [
        "prov:94aed68ebfbd8e1d",
        "prov:6203c9f0856a9d3b"
      ],
      "target_component_ids": [
        "comp:project_graph",
        "comp:project_encyclopedia",
        "comp:project_snapshot",
        "comp:ai_decomposer",
        "comp:project_model_gate",
        "comp:project_model_cli",
        "comp:hypothesis_engine",
        "comp:arena_loop"
      ],
      "target_contract_ids": []
    },
    {
      "builder_independent_from_decomposer": true,
      "builder_model_id": "claude-sonnet-4-6",
      "builder_prompt_hash": "f2a89b1b8607e9c869c6c169455aead42121428582e0f52172b47b40fd1acf6d",
      "discrimination_passed": true,
      "golden_control_passed": true,
      "hidden_from_primary_decomposer": true,
      "id": "probe:protected_surfaces_unowned",
      "planted_negative_id": "neg:component_owns_protected_surface",
      "provenance_refs": [
        "prov:b4ea60b636b808b4",
        "prov:ef892d964ca5a2f4",
        "prov:50455c6c74a79c2d"
      ],
      "target_component_ids": [],
      "target_contract_ids": []
    }
  ],
  "verification_gaps": [
    {
      "component_ids": [
        "comp:project_model_cli"
      ],
      "contract_ids": [
        "con:cli_uses_gate",
        "con:cli_uses_graph"
      ],
      "description": "Project Model CLI has no observed tests/ import edge in the packet; its entrypoint wiring is unverified by the suite.",
      "id": "vg:cli_untested",
      "proposed_closure_check": "Add tests/test_project_model_cli.py that invokes the CLI argument parser and gate path, then assert it passes under 'uv run pytest tests -q'.",
      "provenance_refs": [
        "prov:9fa0c9d36cbf4c7d"
      ],
      "severity": "high"
    },
    {
      "component_ids": [
        "comp:ai_decomposer"
      ],
      "contract_ids": [],
      "description": "arena.project_model_llm is reached only via the decomposer (edge:7e02ea209da7795bff6a) and has no direct test import; its model-adapter logic is not independently verified.",
      "id": "vg:llm_untested_in_isolation",
      "proposed_closure_check": "Add a unit test that stubs the model call and asserts project_model_llm prompt assembly and JSON parsing deterministically under 'uv run pytest tests -q'.",
      "provenance_refs": [
        "prov:f8f69811aa362fa7",
        "prov:5a5d1c3ebbb4bc03"
      ],
      "severity": "medium"
    },
    {
      "component_ids": [
        "comp:arena_loop",
        "comp:hypothesis_engine"
      ],
      "contract_ids": [],
      "description": "surface_counts.generated=4 but only three generated nodes (models.py, schema.json, ddl.sql) appear in the packet; one generated surface is not represented or componentized.",
      "id": "vg:generated_surface_uncovered",
      "proposed_closure_check": "Enumerate all generated surfaces in the snapshot and assert each is regenerable (not hand-edited) via a generation-drift check in 'uv run pytest tests -q'.",
      "provenance_refs": [
        "prov:910e3c0ee04a35a7",
        "prov:a9f834c533530b22",
        "prov:0dc9f20d86b961b4"
      ],
      "severity": "medium"
    },
    {
      "component_ids": [],
      "contract_ids": [],
      "description": "Ten protected surfaces (scorer/*, verifier/*, schema/arena.yaml) are intentionally excluded from arena ownership per non-goals and therefore remain unverified by this decomposition.",
      "id": "vg:protected_surfaces_unowned",
      "proposed_closure_check": "Confirm via a boundary check that no arena component imports or writes protected surfaces, run inside 'uv run pytest tests -q'.",
      "provenance_refs": [
        "prov:b4ea60b636b808b4",
        "prov:ef892d964ca5a2f4",
        "prov:50455c6c74a79c2d",
        "prov:1411d5ace6bd7135",
        "prov:df42396adab2a9fc",
        "prov:1588b944760fcaf5",
        "prov:75d9656ba69803ce",
        "prov:88f3d7a7f5ebc93e",
        "prov:774548e852b6c408"
      ],
      "severity": "low"
    },
    {
      "component_ids": [
        "comp:project_snapshot"
      ],
      "contract_ids": [
        "con:gate_uses_snapshot"
      ],
      "description": "git_dirty=true with many uncommitted arena/ and docs/ paths; this decomposition was derived from an uncommitted working tree and may not reproduce from a clean checkout.",
      "id": "vg:dirty_tree_nondeterminism",
      "proposed_closure_check": "Re-run decomposition and gating against a committed snapshot and assert identical project-model hash under 'uv run pytest tests -q'.",
      "provenance_refs": [
        "prov:88ca325d7a0970fe"
      ],
      "severity": "medium"
    }
  ],
  "near_neighbor_alternatives": [
    {
      "alternative": "Promote arena.project_model_llm into a standalone LLM-adapter component separate from the decomposer.",
      "id": "nn:standalone_llm_adapter",
      "provenance_refs": [
        "prov:5a5d1c3ebbb4bc03"
      ],
      "target_id": "comp:ai_decomposer",
      "why_not_primary": "The decomposer imports project_model_llm directly (edge:7e02ea209da7795bff6a) and is its only observed consumer, forming a single AI-first pipeline; splitting would create a one-file unit with no independent contract. Anchored to goal: decompose Build Arena into responsibility-bearing components without relying on path-classifier semantics; non-goals: do not accept file-bucket components; do not treat scorer verifier schema or generated files as owned arena hypotheses."
    },
    {
      "alternative": "Route the decomposer's graph access through the encyclopedia instead of the raw project_graph.",
      "id": "nn:graph_via_encyclopedia",
      "provenance_refs": [
        "prov:0b1e57728d3d4327"
      ],
      "target_id": "con:decomposer_uses_graph",
      "why_not_primary": "The decomposer imports arena.project_graph directly (edge:52d0c53c037ed70393d0) in addition to the encyclopedia, so a direct graph contract is observed and not a transitive substitute. Anchored to goal: decompose Build Arena into responsibility-bearing components without relying on path-classifier semantics; non-goals: do not accept file-bucket components; do not treat scorer verifier schema or generated files as owned arena hypotheses."
    },
    {
      "alternative": "Attribute arena.budget to the Hypothesis Engine rather than the Execution Loop.",
      "id": "nn:budget_in_hypothesis",
      "provenance_refs": [
        "prov:54bc178712fd6fb8"
      ],
      "target_id": "comp:arena_loop",
      "why_not_primary": "Only arena.loop imports arena.budget (edge:0ad81c69fa74d4c0698e); the hypothesizer has no budget import edge, so budget belongs to the loop's execution responsibility. Anchored to goal: decompose Build Arena into responsibility-bearing components without relying on path-classifier semantics; non-goals: do not accept file-bucket components; do not treat scorer verifier schema or generated files as owned arena hypotheses."
    }
  ],
  "acceptance_command_allowlist": [
    "acc:pytest_suite",
    "chk:decomposer_tests",
    "chk:encyclopedia_tests",
    "chk:fingerprints_tests",
    "chk:graph_tests",
    "chk:loop_phase4_tests",
    "chk:snapshot_gate_tests"
  ]
}
```

## Pilot: 2026-06-04-ai-first-project-decomposer-pilot-fmc-mpc

### local-verification.md

```text
# fmc-mcp local verification

Command: `uv run python -m pytest -q`

CWD: `/home/leonb/projects/fmc-mcp`

Return code: `0`

```text
...................                                                      [100%]
19 passed in 0.04s


```

```

### semantic-plausibility.md

```text
# fmc-mcp final recorded pilot semantic plausibility

Repo: `/home/leonb/projects/fmc-mcp`
Selection: Required pilot 2: FMC-MPC request resolved to canonical local repo fmc-mcp.
Snapshot: `/home/leonb/projects/build-arena/docs/verification/2026-06-04-ai-first-project-decomposer-pilot-fmc-mpc/snapshot-a1a7eab7533347be`
Primary model: `claude-opus-4-8`
Local verification return code: `0`
Gate passed: `True`
Components/contracts/checks/gaps/probes: 5/5/3/4/3

## Components
- `comp-config` — Configuration & Settings
  - responsibility: Load and validate runtime configuration (FMC host, credentials, timeouts) as typed pydantic settings consumed by client and server.
  - owned evidence: fmc_mcp.config
  - contracts: ['ct-server-config', 'ct-client-config']; checks: ['chk-suite', 'chk-resources-contract']; gaps: none
- `comp-client` — FMC HTTP Client (auth, transport, token cache)
  - responsibility: Own async HTTP transport to the FMC REST API, base64 basic-auth handshake, and time-based auth-token caching/refresh.
  - owned evidence: fmc_mcp.client
  - contracts: ['ct-client-config', 'ct-resources-client', 'ct-server-client']; checks: ['chk-suite', 'chk-resources-contract']; gaps: ['gap-client-network']
- `comp-resources` — FMC Resource Layer
  - responsibility: Retrieve FMC domain objects through the client and serialize them to JSON resource payloads for the MCP surface.
  - owned evidence: fmc_mcp.resources
  - contracts: ['ct-resources-client', 'ct-tools-resources']; checks: ['chk-suite', 'chk-resources-contract']; gaps: none
- `comp-tools` — MCP Tool Surface
  - responsibility: Define MCP tools over the resource layer, including input validation such as IP-address parsing, and shape tool responses as JSON.
  - owned evidence: fmc_mcp.tools
  - contracts: ['ct-tools-resources']; checks: ['chk-suite', 'chk-tools-validation']; gaps: ['gap-tool-wiring']
- `comp-server` — MCP Server Runtime & Entrypoint
  - responsibility: Construct the FastMCP server, wire config and client into its lifecycle, and expose the process entrypoint that launches the server.
  - owned evidence: fmc_mcp.server, fmc_mcp.__main__
  - contracts: ['ct-server-config', 'ct-server-client']; checks: ['chk-suite']; gaps: ['gap-tool-wiring', 'gap-entrypoint']

## Contracts
- `ct-server-config` comp-server -> comp-config via ['imports:fmc_mcp.config']
- `ct-client-config` comp-client -> comp-config via ['imports:fmc_mcp.config']
- `ct-resources-client` comp-resources -> comp-client via ['imports:fmc_mcp.client']
- `ct-tools-resources` comp-tools -> comp-resources via ['imports:fmc_mcp.resources']
- `ct-server-client` comp-server -> comp-client via ['imports:fmc_mcp.client']

## Verification gaps
- `gap-tool-wiring` (high): No selected edge connects fmc_mcp.server to fmc_mcp.tools, so registration/exposure of MCP tools through the server runtime is not observable from the graph; the tool surface may be wired via decorators or runtime registration not captured by the packet.
- `gap-client-network` (medium): Client FMC HTTP/auth behavior (httpx transport, base64 basic auth, time-based token caching) cannot be exercised against a live controller under the no-network/no-credentials acceptance constraint, so the real FMC request contract is verified only via mocks/offline.
- `gap-entrypoint` (low): The fmc_mcp.__main__ -> fmc_mcp.server startup path (process entrypoint) is not shown to be covered by tests in the packet.
- `gap-docs-static` (low): Documentation/static surfaces present in the graph (markdown_section x45 with 45 documents edges) and config surfaces (config x3 with 3 configures edges) were not selected and are not componentized, so their accuracy and coverage remain undecomposed.

## Assessment
- Final output is not fixture mode; it records Claude Opus model output plus independent Sonnet probe-builder artifacts after Grok Build failed to emit final JSON.
- Components are model-derived responsibility units; some intentionally group multiple source modules or explicit static/doc surfaces.
- Contracts are only gate-passing deterministic graph edges; unsupported semantic dependencies are retained as verification gaps.
- Observable checks match the actual command run for the repo.
- Protected/generated surfaces are graph-visible and excluded from component ownership.
- Negative-control artifacts demonstrate the gate rejects a plausible fluent file-bucket model output.

```

### recorded-repaired-snapshot-command.json

```text
{
  "command": "uv run python -m arena.project_model_cli snapshot --project /home/leonb/projects/fmc-mcp --artifacts-root /home/leonb/projects/build-arena/docs/verification/2026-06-04-ai-first-project-decomposer-pilot-fmc-mpc --project-id fmc-mcp --goal 'decompose the Cisco FMC MCP server into responsibility-bearing components that can be manually evaluated by Leon' --llm-mode recorded --model-output /home/leonb/projects/build-arena/docs/verification/2026-06-04-ai-first-project-decomposer-pilot-fmc-mpc/recorded-model-output.repaired.json --overwrite --non-goal 'do not require live FMC credentials or network calls for acceptance' --non-goal 'do not accept file-bucket components'",
  "returncode": 0,
  "stdout": "{\"gate_report_path\": \"/home/leonb/projects/build-arena/docs/verification/2026-06-04-ai-first-project-decomposer-pilot-fmc-mpc/snapshot-a1a7eab7533347be/gate-report.json\", \"manifest_path\": \"/home/leonb/projects/build-arena/docs/verification/2026-06-04-ai-first-project-decomposer-pilot-fmc-mpc/snapshot-a1a7eab7533347be/manifest.json\", \"passed\": true, \"snapshot_dir\": \"/home/leonb/projects/build-arena/docs/verification/2026-06-04-ai-first-project-decomposer-pilot-fmc-mpc/snapshot-a1a7eab7533347be\", \"snapshot_id\": \"snapshot-a1a7eab7533347be\", \"violation_count\": 0}\n",
  "stderr": ""
}
```

### negative-control-command.json

```text
{
  "command": "uv run python -m arena.project_model_cli snapshot --project /home/leonb/projects/fmc-mcp --artifacts-root /home/leonb/projects/build-arena/docs/verification/2026-06-04-ai-first-project-decomposer-pilot-fmc-mpc/negative-control-artifacts --project-id fmc-mcp --goal 'decompose the Cisco FMC MCP server into responsibility-bearing components that can be manually evaluated by Leon' --llm-mode recorded --model-output /home/leonb/projects/build-arena/docs/verification/2026-06-04-ai-first-project-decomposer-pilot-fmc-mpc/negative-control-file-bucket.recorded.json --overwrite --non-goal 'do not require live FMC credentials or network calls for acceptance' --non-goal 'do not accept file-bucket components'",
  "returncode": 1,
  "stdout": "{\"gate_report_path\": \"/home/leonb/projects/build-arena/docs/verification/2026-06-04-ai-first-project-decomposer-pilot-fmc-mpc/negative-control-artifacts/snapshot-87ebcd10ce5d9aa0/gate-report.json\", \"manifest_path\": \"/home/leonb/projects/build-arena/docs/verification/2026-06-04-ai-first-project-decomposer-pilot-fmc-mpc/negative-control-artifacts/snapshot-87ebcd10ce5d9aa0/manifest.json\", \"passed\": false, \"snapshot_dir\": \"/home/leonb/projects/build-arena/docs/verification/2026-06-04-ai-first-project-decomposer-pilot-fmc-mpc/negative-control-artifacts/snapshot-87ebcd10ce5d9aa0\", \"snapshot_id\": \"snapshot-87ebcd10ce5d9aa0\", \"violation_count\": 5}\n",
  "stderr": ""
}
```

### final gate report

```json
{
  "passed": true,
  "violations": []
}
```

### graph summary

```json
{
  "node_count": 175,
  "edge_count": 209,
  "node_kinds": {
    "markdown_section": 45,
    "python_function": 69,
    "python_module": 11,
    "python_class": 7,
    "file": 12,
    "config": 3,
    "test_file": 4,
    "project": 1,
    "python_import": 23
  },
  "edge_kinds": {
    "contains": 19,
    "defined_in": 87,
    "imports": 49,
    "documents": 45,
    "tests": 6,
    "configures": 3
  },
  "protected_nodes": 0,
  "generated_nodes": 0
}
```

### final snapshot summary

```json
{
  "project_id": "fmc-mcp",
  "primary_model_id": "claude-opus-4-8",
  "components": [
    {
      "check_ids": [
        "chk-suite",
        "chk-resources-contract"
      ],
      "contract_ids": [
        "ct-server-config",
        "ct-client-config"
      ],
      "id": "comp-config",
      "name": "Configuration & Settings",
      "owned_node_ids": [
        "node:257d836fb3f003e3e2c2"
      ],
      "provenance_refs": [
        "prov:b380701c2879efce",
        "prov:8725a89bbd7df351",
        "prov:9b83bc4546b8b4e1"
      ],
      "responsibility": "Load and validate runtime configuration (FMC host, credentials, timeouts) as typed pydantic settings consumed by client and server.",
      "verification_gap_ids": []
    },
    {
      "check_ids": [
        "chk-suite",
        "chk-resources-contract"
      ],
      "contract_ids": [
        "ct-client-config",
        "ct-resources-client",
        "ct-server-client"
      ],
      "id": "comp-client",
      "name": "FMC HTTP Client (auth, transport, token cache)",
      "owned_node_ids": [
        "node:4042451215c279f0dca7"
      ],
      "provenance_refs": [
        "prov:bcfd8e782d7fe500",
        "prov:2b0e52ad10883e7c",
        "prov:aefc03705172d5d2",
        "prov:4d9c0f2751d94893"
      ],
      "responsibility": "Own async HTTP transport to the FMC REST API, base64 basic-auth handshake, and time-based auth-token caching/refresh.",
      "verification_gap_ids": [
        "gap-client-network"
      ]
    },
    {
      "check_ids": [
        "chk-suite",
        "chk-resources-contract"
      ],
      "contract_ids": [
        "ct-resources-client",
        "ct-tools-resources"
      ],
      "id": "comp-resources",
      "name": "FMC Resource Layer",
      "owned_node_ids": [
        "node:84a7c7e4c189e28cb1bb"
      ],
      "provenance_refs": [
        "prov:4e62ae79d2c07a9c",
        "prov:bebb3d04d5e3bea1"
      ],
      "responsibility": "Retrieve FMC domain objects through the client and serialize them to JSON resource payloads for the MCP surface.",
      "verification_gap_ids": []
    },
    {
      "check_ids": [
        "chk-suite",
        "chk-tools-validation"
      ],
      "contract_ids": [
        "ct-tools-resources"
      ],
      "id": "comp-tools",
      "name": "MCP Tool Surface",
      "owned_node_ids": [
        "node:a32d71cbbae4bcadc234"
      ],
      "provenance_refs": [
        "prov:750d7fda533e438c",
        "prov:12c675fbe4c747a2",
        "prov:1b3ec86fcc8eb077"
      ],
      "responsibility": "Define MCP tools over the resource layer, including input validation such as IP-address parsing, and shape tool responses as JSON.",
      "verification_gap_ids": [
        "gap-tool-wiring"
      ]
    },
    {
      "check_ids": [
        "chk-suite"
      ],
      "contract_ids": [
        "ct-server-config",
        "ct-server-client"
      ],
      "id": "comp-server",
      "name": "MCP Server Runtime & Entrypoint",
      "owned_node_ids": [
        "node:9810fbe9bc4ff06aee73",
        "node:b3d9c9b0b868f763b2b8"
      ],
      "provenance_refs": [
        "prov:d10dbb159e6fb524",
        "prov:da6e96a18d26d1cf",
        "prov:224f5fd127caa0f7",
        "prov:1cd5d87538f7fc4b"
      ],
      "responsibility": "Construct the FastMCP server, wire config and client into its lifecycle, and expose the process entrypoint that launches the server.",
      "verification_gap_ids": [
        "gap-tool-wiring",
        "gap-entrypoint"
      ]
    }
  ],
  "contracts": [
    {
      "from_component_id": "comp-server",
      "id": "ct-server-config",
      "name": "Server consumes configuration",
      "near_neighbor_alternative_ids": [],
      "provenance_refs": [
        "prov:a490824f581f0eb5"
      ],
      "supporting_edge_ids": [
        "edge:1dbd45e8683cedc3c87a"
      ],
      "to_component_id": "comp-config"
    },
    {
      "from_component_id": "comp-client",
      "id": "ct-client-config",
      "name": "Client consumes configuration",
      "near_neighbor_alternative_ids": [
        "nn-client-split"
      ],
      "provenance_refs": [
        "prov:ccb407380f605c8b"
      ],
      "supporting_edge_ids": [
        "edge:4db395dbd95108d60b32"
      ],
      "to_component_id": "comp-config"
    },
    {
      "from_component_id": "comp-resources",
      "id": "ct-resources-client",
      "name": "Resources call FMC client",
      "near_neighbor_alternative_ids": [],
      "provenance_refs": [
        "prov:9688276cf5e240e7"
      ],
      "supporting_edge_ids": [
        "edge:25c3c6d20a305beeeca9"
      ],
      "to_component_id": "comp-client"
    },
    {
      "from_component_id": "comp-tools",
      "id": "ct-tools-resources",
      "name": "Tools build on resource layer",
      "near_neighbor_alternative_ids": [
        "nn-tools-resources-merge"
      ],
      "provenance_refs": [
        "prov:3dfa2aaf889c6db2"
      ],
      "supporting_edge_ids": [
        "edge:68860f44ca677cc65828"
      ],
      "to_component_id": "comp-resources"
    },
    {
      "from_component_id": "comp-server",
      "id": "ct-server-client",
      "name": "Server uses FMC client",
      "near_neighbor_alternative_ids": [],
      "provenance_refs": [
        "prov:878270a56e8c3d80"
      ],
      "supporting_edge_ids": [
        "edge:cbfc0096826b93771472"
      ],
      "to_component_id": "comp-client"
    }
  ],
  "cross_cutting_concerns": [
    {
      "category": "anti_fabrication",
      "component_ids": [
        "comp-config",
        "comp-client",
        "comp-resources",
        "comp-tools",
        "comp-server"
      ],
      "contract_ids": [
        "ct-server-config",
        "ct-client-config",
        "ct-resources-client",
        "ct-tools-resources",
        "ct-server-client"
      ],
      "description": "All component, contract, and gap claims must trace to selected graph nodes/edges and their provenance; no responsibilities, tools, or endpoints may be invented beyond packet evidence.",
      "id": "cc-anti-fabrication",
      "provenance_refs": [
        "prov:b380701c2879efce",
        "prov:bcfd8e782d7fe500",
        "prov:4e62ae79d2c07a9c",
        "prov:750d7fda533e438c",
        "prov:d10dbb159e6fb524"
      ],
      "triggered_by": "universal"
    },
    {
      "category": "determinism",
      "component_ids": [
        "comp-client",
        "comp-server",
        "comp-resources",
        "comp-tools",
        "comp-config"
      ],
      "contract_ids": [
        "ct-client-config",
        "ct-server-client",
        "ct-resources-client"
      ],
      "description": "Acceptance must be deterministic; the client's time-based token caching and any wall-clock or network ordering must be controlled/stubbed so the pytest suite yields stable results.",
      "id": "cc-determinism",
      "provenance_refs": [
        "prov:4d9c0f2751d94893",
        "prov:bcfd8e782d7fe500"
      ],
      "triggered_by": "universal"
    },
    {
      "category": "provenance",
      "component_ids": [
        "comp-config",
        "comp-client",
        "comp-resources",
        "comp-tools",
        "comp-server"
      ],
      "contract_ids": [
        "ct-server-config",
        "ct-client-config",
        "ct-resources-client",
        "ct-tools-resources",
        "ct-server-client"
      ],
      "description": "Every owned node, supporting edge, and check is anchored to packet provenance ids so the decomposition is auditable back to the source graph.",
      "id": "cc-provenance",
      "provenance_refs": [
        "prov:d10dbb159e6fb524",
        "prov:750d7fda533e438c"
      ],
      "triggered_by": "universal"
    },
    {
      "category": "no_live_paid_api_acceptance",
      "component_ids": [
        "comp-client",
        "comp-server",
        "comp-resources"
      ],
      "contract_ids": [
        "ct-server-client",
        "ct-resources-client"
      ],
      "description": "Acceptance must not call the live FMC controller or require credentials; the httpx-based client and FastMCP runtime must be exercised offline with stubs, per project non-goals.",
      "id": "cc-no-live-paid-api-acceptance",
      "provenance_refs": [
        "prov:2b0e52ad10883e7c",
        "prov:224f5fd127caa0f7"
      ],
      "triggered_by": "non_goal:do not require live FMC credentials or network calls for acceptance"
    }
  ],
  "observable_checks": [
    {
      "acceptance_command_id": "chk-suite",
      "command": "uv run python -m pytest -q",
      "component_ids": [
        "comp-config",
        "comp-client",
        "comp-resources",
        "comp-tools",
        "comp-server"
      ],
      "contract_ids": [
        "ct-server-config",
        "ct-client-config",
        "ct-resources-client",
        "ct-tools-resources",
        "ct-server-client"
      ],
      "description": "Full offline pytest suite passes, exercising configuration loading, client logic, resource serialization, and server wiring.",
      "id": "chk-suite",
      "provenance_refs": [
        "prov:83bfaa715796cf55",
        "prov:aae72e2816907c8a",
        "prov:d10dbb159e6fb524"
      ],
      "requires_network": false,
      "requires_paid_api": false,
      "safe_to_run_by_default": true
    },
    {
      "acceptance_command_id": "chk-resources-contract",
      "command": "uv run python -m pytest -q",
      "component_ids": [
        "comp-resources",
        "comp-client",
        "comp-config"
      ],
      "contract_ids": [
        "ct-resources-client",
        "ct-client-config"
      ],
      "description": "Resource\u2194client\u2194config integration is validated through tests/test_resources.py, which imports fmc_mcp.resources, fmc_mcp.client, and fmc_mcp.config.",
      "id": "chk-resources-contract",
      "provenance_refs": [
        "prov:83bfaa715796cf55",
        "prov:9688276cf5e240e7",
        "prov:ccb407380f605c8b"
      ],
      "requires_network": false,
      "requires_paid_api": false,
      "safe_to_run_by_default": true
    },
    {
      "acceptance_command_id": "chk-tools-validation",
      "command": "uv run python -m pytest -q",
      "component_ids": [
        "comp-tools"
      ],
      "contract_ids": [
        "ct-tools-resources"
      ],
      "description": "Tool-surface input validation (ipaddress parsing) and JSON shaping are exercised under the suite.",
      "id": "chk-tools-validation",
      "provenance_refs": [
        "prov:750d7fda533e438c",
        "prov:12c675fbe4c747a2"
      ],
      "requires_network": false,
      "requires_paid_api": false,
      "safe_to_run_by_default": true
    }
  ],
  "held_out_probes": [
    {
      "builder_independent_from_decomposer": true,
      "builder_model_id": "claude-sonnet-4-6",
      "builder_prompt_hash": "039b6f926c0e71fb2675995112bd2cc895a9e59c43147f3414ed958d2610ecd5",
      "discrimination_passed": true,
      "golden_control_passed": true,
      "hidden_from_primary_decomposer": true,
      "id": "probe-resources-no-mcp-surface",
      "planted_negative_id": "neg-tools-resources-merge",
      "provenance_refs": [
        "prov:4e62ae79d2c07a9c",
        "prov:bebb3d04d5e3bea1",
        "prov:3dfa2aaf889c6db2"
      ],
      "target_component_ids": [
        "comp-resources"
      ],
      "target_contract_ids": [
        "ct-resources-client",
        "ct-tools-resources"
      ]
    },
    {
      "builder_independent_from_decomposer": true,
      "builder_model_id": "claude-sonnet-4-6",
      "builder_prompt_hash": "039b6f926c0e71fb2675995112bd2cc895a9e59c43147f3414ed958d2610ecd5",
      "discrimination_passed": true,
      "golden_control_passed": true,
      "hidden_from_primary_decomposer": true,
      "id": "probe-client-unified-auth-transport",
      "planted_negative_id": "neg-client-split",
      "provenance_refs": [
        "prov:bcfd8e782d7fe500",
        "prov:2b0e52ad10883e7c",
        "prov:aefc03705172d5d2",
        "prov:4d9c0f2751d94893"
      ],
      "target_component_ids": [
        "comp-client"
      ],
      "target_contract_ids": [
        "ct-client-config",
        "ct-resources-client",
        "ct-server-client"
      ]
    },
    {
      "builder_independent_from_decomposer": true,
      "builder_model_id": "claude-sonnet-4-6",
      "builder_prompt_hash": "039b6f926c0e71fb2675995112bd2cc895a9e59c43147f3414ed958d2610ecd5",
      "discrimination_passed": true,
      "golden_control_passed": true,
      "hidden_from_primary_decomposer": true,
      "id": "probe-no-fabricated-components",
      "planted_negative_id": "neg-fabricated-audit-log",
      "provenance_refs": [
        "prov:b380701c2879efce",
        "prov:bcfd8e782d7fe500",
        "prov:4e62ae79d2c07a9c",
        "prov:750d7fda533e438c",
        "prov:d10dbb159e6fb524"
      ],
      "target_component_ids": [
        "comp-config",
        "comp-client",
        "comp-resources",
        "comp-tools",
        "comp-server"
      ],
      "target_contract_ids": [
        "ct-server-config",
        "ct-client-config",
        "ct-resources-client",
        "ct-tools-resources",
        "ct-server-client"
      ]
    }
  ],
  "verification_gaps": [
    {
      "component_ids": [
        "comp-server",
        "comp-tools"
      ],
      "contract_ids": [],
      "description": "No selected edge connects fmc_mcp.server to fmc_mcp.tools, so registration/exposure of MCP tools through the server runtime is not observable from the graph; the tool surface may be wired via decorators or runtime registration not captured by the packet.",
      "id": "gap-tool-wiring",
      "proposed_closure_check": "Add an offline check that imports fmc_mcp.server and asserts the expected FMC tools are registered on the FastMCP instance.",
      "provenance_refs": [
        "prov:d10dbb159e6fb524",
        "prov:750d7fda533e438c"
      ],
      "severity": "high"
    },
    {
      "component_ids": [
        "comp-client"
      ],
      "contract_ids": [
        "ct-resources-client",
        "ct-server-client",
        "ct-client-config"
      ],
      "description": "Client FMC HTTP/auth behavior (httpx transport, base64 basic auth, time-based token caching) cannot be exercised against a live controller under the no-network/no-credentials acceptance constraint, so the real FMC request contract is verified only via mocks/offline.",
      "id": "gap-client-network",
      "proposed_closure_check": "Add offline contract tests that stub the httpx transport and assert request shaping, auth header construction, and token-cache expiry logic.",
      "provenance_refs": [
        "prov:bcfd8e782d7fe500",
        "prov:2b0e52ad10883e7c"
      ],
      "severity": "medium"
    },
    {
      "component_ids": [
        "comp-server"
      ],
      "contract_ids": [],
      "description": "The fmc_mcp.__main__ -> fmc_mcp.server startup path (process entrypoint) is not shown to be covered by tests in the packet.",
      "id": "gap-entrypoint",
      "proposed_closure_check": "Add a smoke test invoking the module entrypoint with a stubbed server.run to assert it starts without network.",
      "provenance_refs": [
        "prov:da6e96a18d26d1cf",
        "prov:e08d506150373eea"
      ],
      "severity": "low"
    },
    {
      "component_ids": [],
      "contract_ids": [],
      "description": "Documentation/static surfaces present in the graph (markdown_section x45 with 45 documents edges) and config surfaces (config x3 with 3 configures edges) were not selected and are not componentized, so their accuracy and coverage remain undecomposed.",
      "id": "gap-docs-static",
      "proposed_closure_check": "Select documentation and config nodes in a follow-up packet and either map them to owning components or emit explicit doc-accuracy checks.",
      "provenance_refs": [
        "prov:b380701c2879efce"
      ],
      "severity": "low"
    }
  ],
  "near_neighbor_alternatives": [
    {
      "alternative": "Split the client into a separate authentication/token-cache component and a thin HTTP transport component.",
      "id": "nn-client-split",
      "provenance_refs": [
        "prov:bcfd8e782d7fe500",
        "prov:2b0e52ad10883e7c",
        "prov:aefc03705172d5d2",
        "prov:4d9c0f2751d94893"
      ],
      "target_id": "comp-client",
      "why_not_primary": "Auth (base64), token caching (time), and transport (httpx) are co-located in the single client module with no edge evidence of a distinct auth surface; splitting would create sub-file fragments rather than independent responsibility units. Anchored to goal: decompose the Cisco FMC MCP server into responsibility-bearing components that can be manually evaluated by Leon; non-goals: do not require live FMC credentials or network calls for acceptance; do not accept file-bucket components."
    },
    {
      "alternative": "Merge tools and resources into a single 'FMC operations' component.",
      "id": "nn-tools-resources-merge",
      "provenance_refs": [
        "prov:4e62ae79d2c07a9c",
        "prov:750d7fda533e438c",
        "prov:3dfa2aaf889c6db2"
      ],
      "target_id": "comp-tools",
      "why_not_primary": "Responsibilities differ: resources retrieve and serialize FMC data via the client, while tools define the MCP tool surface and own input validation (ipaddress); the tools->resources import edge confirms a layered dependency, not a single unit. Anchored to goal: decompose the Cisco FMC MCP server into responsibility-bearing components that can be manually evaluated by Leon; non-goals: do not require live FMC credentials or network calls for acceptance; do not accept file-bucket components."
    },
    {
      "alternative": "Treat fmc_mcp.__main__ as its own standalone entrypoint component separate from the server runtime.",
      "id": "nn-server-entrypoint",
      "provenance_refs": [
        "prov:da6e96a18d26d1cf",
        "prov:e08d506150373eea"
      ],
      "target_id": "comp-server",
      "why_not_primary": "__main__ only imports and delegates to fmc_mcp.server (single import edge) and carries no independent responsibility; isolating it would produce a rejected file-bucket component. Anchored to goal: decompose the Cisco FMC MCP server into responsibility-bearing components that can be manually evaluated by Leon; non-goals: do not require live FMC credentials or network calls for acceptance; do not accept file-bucket components."
    }
  ],
  "acceptance_command_allowlist": [
    "acc:pytest",
    "chk-resources-contract",
    "chk-suite",
    "chk-tools-validation"
  ]
}
```

## Pilot: 2026-06-04-ai-first-project-decomposer-pilot-held-out

### local-verification.md

```text
# leonbreukelman-engineer local verification

Command: `bash -lc 'npm run build && npm run check:links'`

CWD: `/home/leonb/projects/leonbreukelman-engineer`

Return code: `0`

```text

> leonbreukelman-engineer@1.0.0 build
> bash scripts/build-site.sh

Building leonbreukelman.engineer...
Building human pages...
Copying machine-readable surfaces and assets...
Build complete! Output in /home/leonb/projects/leonbreukelman-engineer/dist

> leonbreukelman-engineer@1.0.0 check:links
> python3 scripts/check-public-links.py

Checking 8 public URLs
OK 200 https://cmmc-level1-readiness-assistant.pages.dev -> https://cmmc-level1-readiness-assistant.pages.dev
    api/v1/projects.json:42
    dist/api/v1/projects.json:42
    dist/human/work/index.html:155
OK 200 https://github.com/leonbreukelman -> https://github.com/leonbreukelman
    api/v1/profile.json:55
    dist/api/v1/profile.json:55
    dist/human/contact/index.html:82
    dist/human/contact/index.html:82
    dist/llms.txt:37
OK 200 https://github.com/leonbreukelman/fmc-mcp -> https://github.com/leonbreukelman/fmc-mcp
    api/v1/case_studies.json:15
    api/v1/projects.json:16
    dist/api/v1/case_studies.json:15
    dist/api/v1/projects.json:16
    dist/human/work/index.html:88
OK 200 https://leonbreukelman.engineer -> https://leonbreukelman.engineer/human/
    api/v1/profile.json:54
    dist/api/v1/profile.json:54
OK 200 https://leonbreukelman.engineer/.well-known/security.txt -> https://leonbreukelman.engineer/.well-known/security.txt
    dist/well-known/security.txt:5
    well-known/security.txt:5
OK 200 https://leonbreukelman.engineer/assets/schema/ai.json -> https://leonbreukelman.engineer/assets/schema/ai.json
    dist/well-known/ai.json:2
    well-known/ai.json:2
OK 200 https://leonbreukelman.engineer/mcp/ -> https://leonbreukelman.engineer/mcp/
    dist/well-known/agent-card.json:4
    well-known/agent-card.json:4
OK 200 https://schema.org/Person -> https://schema.org/Person
    api/v1/profile.json:2
    dist/api/v1/profile.json:2


```

```

### semantic-plausibility.md

```text
# leonbreukelman-engineer final recorded pilot semantic plausibility

Repo: `/home/leonb/projects/leonbreukelman-engineer`
Selection: Required pilot 3: held-out Leon-owned JavaScript/Python/static public-site repo.
Snapshot: `/home/leonb/projects/build-arena/docs/verification/2026-06-04-ai-first-project-decomposer-pilot-held-out/snapshot-652b029903fe1af7`
Primary model: `claude-opus-4-8`
Local verification return code: `0`
Gate passed: `True`
Components/contracts/checks/gaps/probes: 7/1/3/7/4

## Components
- `comp:build-pipeline` — Static Site Build Pipeline
  - responsibility: Render templates and source data into the deployable site via scripts/build.py, failing closed when Python/Jinja dependencies are unavailable.
  - owned evidence: scripts.build
  - contracts: none; checks: ['check:full-acceptance', 'check:build-only']; gaps: ['gap:build-data-edge-missing', 'gap:templates-not-componentized']
- `comp:link-checker` — Public Link Integrity Checker
  - responsibility: Validate that public links and assets resolve via scripts/check-public-links.py before/after build.
  - owned evidence: scripts.check-public-links
  - contracts: none; checks: ['check:full-acceptance', 'check:link-check']; gaps: ['gap:linkcheck-target-unobserved']
- `comp:worker-edge-router` — Cloudflare Worker Edge Router
  - responsibility: Serve as the deployed worker entrypoint (worker/index.js) routing inbound requests and delegating agent traffic to the MCP server module.
  - owned evidence: worker, worker.mcp.server
  - contracts: ['contract:router-to-mcp']; checks: ['check:full-acceptance']; gaps: ['gap:mcp-protocol-unspecified']
- `comp:mcp-server` — MCP Server Module
  - responsibility: Implement the Model Context Protocol surface (worker/mcp/server.js) that exposes agent-facing tools/resources.
  - owned evidence: worker.mcp.server
  - contracts: ['contract:router-to-mcp']; checks: ['check:full-acceptance']; gaps: ['gap:mcp-protocol-unspecified']
- `comp:public-agent-data` — Public Agent Data & Discovery Metadata
  - responsibility: Provide machine-readable profile and agent discovery metadata as committed source (api/v1/profile.json, llms.txt).
  - owned evidence: api/v1/profile.json, llms.txt
  - contracts: none; checks: ['check:full-acceptance', 'check:link-check', 'check:build-only']; gaps: ['gap:build-data-edge-missing', 'gap:linkcheck-target-unobserved']
- `comp:persona-corpus` — Persona Representation Corpus
  - responsibility: Author the source-of-truth narrative for how AI agents represent Leon Breukelman across positioning, voice, strengths, stories, data sources, and contact (prompt/represent_me.md).
  - owned evidence: prompt/represent_me.md, prompt/represent_me.md#What He Is Less Good At, prompt/represent_me.md#Stories Worth Telling, prompt/represent_me.md#Data Sources, prompt/represent_me.md#Primary Positioning, prompt/represent_me.md#What He Is Good At, prompt/represent_me.md#Voice, prompt/represent_me.md#How to Represent Leon Breukelman, prompt/represent_me.md#Contact, prompt/represent_me.md#Short Version
  - contracts: none; checks: ['check:build-only']; gaps: ['gap:build-data-edge-missing']
- `comp:project-docs` — Project Documentation
  - responsibility: Onboard humans and AI agents with install, development, build, preview, deployment, and structure guidance (README.md).
  - owned evidence: README.md, README.md#Quick Start, README.md#Development, README.md#Deployment, README.md#For Humans, README.md#Preview locally, README.md#Deploy to Cloudflare Pages, README.md#Structure, README.md#Install dependencies, README.md#For AI Agents, README.md#Build the site (fails closed if Python/Jinja dependencies are unavailable), README.md#leonbreukelman.engineer
  - contracts: none; checks: ['check:full-acceptance']; gaps: ['gap:templates-not-componentized']

## Contracts
- `contract:router-to-mcp` comp:worker-edge-router -> comp:mcp-server via ['imports:worker.mcp.server']

## Verification gaps
- `gap:build-data-edge-missing` (medium): build.py's consumption of api/v1/profile.json, llms.txt, and the persona corpus is not represented by any graph edge; only Python stdlib/jinja2 import edges were captured, so the build-consumes-data and build-renders-persona contracts are inferred rather than graph-observed.
- `gap:templates-not-componentized` (medium): build.py imports jinja2 and README#Structure documents a templates surface, but no template node was selected in the packet, leaving the template surface uncomponentized.
- `gap:linkcheck-target-unobserved` (low): scripts/check-public-links.py uses urllib.request to fetch public URLs, but the set of checked targets is not represented as graph nodes/edges, so link-surface coverage cannot be verified from the packet.
- `gap:mcp-protocol-unspecified` (medium): The MCP request/response contract served by worker/mcp/server.js is not captured by any node/edge beyond the module import, so the protocol surface is unverified.
- `gap:unsupported-contract:contract-build-consumes-data` (medium): Model proposed `contract:build-consumes-data` as a semantic contract, but the current graph has no deterministic supporting edge; keep it as a verification gap rather than a passed contract.
- `gap:unsupported-contract:contract-build-renders-persona` (medium): Model proposed `contract:build-renders-persona` as a semantic contract, but the current graph has no deterministic supporting edge; keep it as a verification gap rather than a passed contract.
- `gap:unsupported-contract:contract-linkcheck-validates-data` (medium): Model proposed `contract:linkcheck-validates-data` as a semantic contract, but the current graph has no deterministic supporting edge; keep it as a verification gap rather than a passed contract.

## Assessment
- Final output is not fixture mode; it records Claude Opus model output plus independent Sonnet probe-builder artifacts after Grok Build failed to emit final JSON.
- Components are model-derived responsibility units; some intentionally group multiple source modules or explicit static/doc surfaces.
- Contracts are only gate-passing deterministic graph edges; unsupported semantic dependencies are retained as verification gaps.
- Observable checks match the actual command run for the repo.
- Protected/generated surfaces are graph-visible and excluded from component ownership.
- Negative-control artifacts demonstrate the gate rejects a plausible fluent file-bucket model output.

```

### recorded-repaired-snapshot-command.json

```text
{
  "command": "uv run python -m arena.project_model_cli snapshot --project /home/leonb/projects/leonbreukelman-engineer --artifacts-root /home/leonb/projects/build-arena/docs/verification/2026-06-04-ai-first-project-decomposer-pilot-held-out --project-id leonbreukelman-engineer --goal 'decompose the AI-first public site and agent metadata project into source-backed components across build scripts, JavaScript worker code, public JSON data, templates, and docs' --llm-mode recorded --model-output /home/leonb/projects/build-arena/docs/verification/2026-06-04-ai-first-project-decomposer-pilot-held-out/recorded-model-output.repaired.json --overwrite --non-goal 'do not treat generated dist output as source ownership' --non-goal 'do not require Cloudflare deployment or public mutation'",
  "returncode": 0,
  "stdout": "{\"gate_report_path\": \"/home/leonb/projects/build-arena/docs/verification/2026-06-04-ai-first-project-decomposer-pilot-held-out/snapshot-652b029903fe1af7/gate-report.json\", \"manifest_path\": \"/home/leonb/projects/build-arena/docs/verification/2026-06-04-ai-first-project-decomposer-pilot-held-out/snapshot-652b029903fe1af7/manifest.json\", \"passed\": true, \"snapshot_dir\": \"/home/leonb/projects/build-arena/docs/verification/2026-06-04-ai-first-project-decomposer-pilot-held-out/snapshot-652b029903fe1af7\", \"snapshot_id\": \"snapshot-652b029903fe1af7\", \"violation_count\": 0}\n",
  "stderr": ""
}
```

### negative-control-command.json

```text
{
  "command": "uv run python -m arena.project_model_cli snapshot --project /home/leonb/projects/leonbreukelman-engineer --artifacts-root /home/leonb/projects/build-arena/docs/verification/2026-06-04-ai-first-project-decomposer-pilot-held-out/negative-control-artifacts --project-id leonbreukelman-engineer --goal 'decompose the AI-first public site and agent metadata project into source-backed components across build scripts, JavaScript worker code, public JSON data, templates, and docs' --llm-mode recorded --model-output /home/leonb/projects/build-arena/docs/verification/2026-06-04-ai-first-project-decomposer-pilot-held-out/negative-control-file-bucket.recorded.json --overwrite --non-goal 'do not treat generated dist output as source ownership' --non-goal 'do not require Cloudflare deployment or public mutation'",
  "returncode": 1,
  "stdout": "{\"gate_report_path\": \"/home/leonb/projects/build-arena/docs/verification/2026-06-04-ai-first-project-decomposer-pilot-held-out/negative-control-artifacts/snapshot-de0245bec8f98395/gate-report.json\", \"manifest_path\": \"/home/leonb/projects/build-arena/docs/verification/2026-06-04-ai-first-project-decomposer-pilot-held-out/negative-control-artifacts/snapshot-de0245bec8f98395/manifest.json\", \"passed\": false, \"snapshot_dir\": \"/home/leonb/projects/build-arena/docs/verification/2026-06-04-ai-first-project-decomposer-pilot-held-out/negative-control-artifacts/snapshot-de0245bec8f98395\", \"snapshot_id\": \"snapshot-de0245bec8f98395\", \"violation_count\": 5}\n",
  "stderr": ""
}
```

### grok-compact-decomposer-output.wrapper.json

```text
{
  "text": "",
  "stopReason": "Cancelled",
  "sessionId": "019e944e-1bdd-7ca2-96d5-417e77bf37cb",
  "requestId": "83d32a31-4ba4-43cc-a487-16786f33780b",
  "thought": "The task is: \"You are Grok, primary AI-first Build Arena project decomposer. Produce a model-derived decomposition JSON from this compact graph packet. Return only valid JSON, no markdown.\"\nThe task is to produce a model-derived decomposition JSON from the given compact graph packet.The repo has source files: README.md, prompt/represent_me.md, scripts/build.py, scripts/check-public-links.py, worker/index.js, worker/mcp/server.js, api/v1/*.json, templates/*.html, well-known/*, llms.txt, package.json, wrangler.toml, etc.\nGood. Now read the scripts.Now the worker files.Now read the data files and templates to understand.Read more templates and other data files, and other sources like llms.txt, well-known, wrangler.toml, tests.Read the test file and other templates briefly, and other api jsons. Also scripts/build-site.sh and requirements.Read the other api data files to see content. Also read one more human template and well-known/agent-card.Now read the other data files and check build-fallback, requirements. Also look for package scripts more, and docs.\nFirst, the output must be valid JSON only, no markdown. Keys: model_id, project_id, goal, non_goals, components, contracts, cross_cutting_concerns, observable_checks, verification_gaps, near_neighbor_alternatives, acceptance_command_allowlist.\n\nUse exact IDs/prov from packet. Do not include held_out_probes.\n\nFor components: id, name, responsibility, owned_node_ids, provenance_refs, contract_ids, check_ids, verification_gap_ids.\n\nI need to extract or define based on selected_nodes.Now read well-known/security.txt and agent-card more if needed, but also the build fallback.Read other templates briefly to see structure.To see other selected nodes like docs/plans, but the packet selected specific sections, not the plans.\n<|im_start|>assistant\n{\n  \"model_id\": \"leonbreukelman-engineer\",\n  \"project_id\": \"leonbreukelman-engineer\",\n  \"goal\": \"decompose the AI-first public site and agent metadata project into source-backed components across build scripts, JavaScript worker code public JSON data, templates, and docs\",\n  \"non_goals\": [\"do not treat generated dist output as source ownership\", \"do not require Cloudflare deployment or public mutation\"],\n  \"components\": [\n    {\n      \"id\": \"agent_representation\",\n      \"name\": \"Agent Representation Instructions\",\n      \"respons ibility\": \"Prompts and instructions for representing Leon Breukelman in AI contexts\",\n      \"owned_node_ids\": [\"node:270b52766ba2097c3bf8\", \"node:087085bf23e3cc4628f2\", \"node:3497d88db26b274 2c66a\", \"node:5ea405faea230cdf5498\", \"node:7ad8da6a627ab8d27e9e\", \"node:9d9d37a18c7ab7537c0f\", \"node:c627dcac9798554 af877\", \"node:ca0aad13b3b497dd9e40\", \"node:cd8a921454b74ef09e06\", \"node:f0fd663527865f98c64e\"],\n      \"provenance_refs\": [\"prov:756f566ef137b772 \"],\n      \"contract_ids\": [],\n      \"check_ids\": [],\n      \"verification_gap_ids\": []\n    },\n    {\n      \"id\": \"site_documentation\",\n      \"name\": \"Site Documentation\",\n      \"responsibility\": \"Documentation for human users including quick start, development, deployment, structure, for humans and for AI agents\",\n      \"owned_node_ids\": [\"node:1c5a6f0459fa5b83d040\", \"node:242462366792e6c85ea0\", \"node:3b25680b492a6345baec\", \"node:4f7 e53ec7b6ab7383a7c\", \"node:d038e1fd31641ace3226\", \"node:de09c473f13049315d86\", \"node:fcbe6669d86356de0639\", \"node:f918107b9b178632 3a79\"],\n      \"provenance_refs\": [\"prov:fa04b24fd751aac4\", \"prov:cd2a7925a71a196b\", \"prov:4129a4074bc34843\", \"prov:cb36c3c07f1b6ffd\", \" prov:e2560a67a5e0ba01\", \"prov:febd8e67289848a5\", \"prov:11a91e2a1f50280f\", \"prov:73f52603d0cdfc2b\"],\n      \"contract_ids\": [],\n      \"check ids\": [],\n      \"verification_gap_ids\": []\n    },\n    {\n      \"id\": \"public_data\",\n      \"name\": \"Public Data Contracts\",\n      \"responsibility\": \"Structured JSON data for profile and metadata\",\n      \"owned_node_ids\": [\"node:b3b1f19ad2ed91bec 458\"],\n      \"provenance_refs\": [\"prov:5dd0cc494cd85fbe\"],\n      \"contract_ids\": [],\n      \"check_ids\": [],\n      \"verification_gap_ids\": []\n    },\n    {\n      \"id\": \"build_script\",\n      \"name\": \"Build Script\",\n      \"responsibility\": \"Build orchestration using Python to render templates and generate dist\",\n      \"owned_node_ids\": [\"node:d8fc3a88afab17188e7b\"],\n      \"provenance_refs\": [\"prov:8c73e6d6bb2288db\"],\n      \"contract_ids\": [],\n      \"check ids\": [],\n      \"verification_gap_ids\": []\n    },\n    {\n      \"id\": \"link_verifier\",\n      \"name\": \"Link Verifier\",\n      \"responsibility\": \"Verifies public links in build and source\",\n      \"owned_node_ids\": [\"node:d1ab9b8e0eb 01b071904\"],\n      \"provenance_refs\": [\"prov:cc1fa9e22afc08c6\"],\n      \"contract_ids\": [],\n      \"check_ids\": [],\n      \"verification_gap_ids\": []\n    },\n    {\n      \"id\": \"worker\",\n      \"name\": \"Cloudflare Worker\",\n \"responsibility\": \"Edge worker for routing and asset serving\",\n      \"owned_node_ids\": [\"node:32f3a0d3845cf98fb8cb\", \"node:1e8ba7fd1db36d8f49db\"],\n      \"provenance_refs\": [\"prov:ea 0068ba73266e60\", \"prov:e8c798459ce07e15\"],\n      \"contract_ids\": [],\n      \"check_ids\": [],\n      \"verification_gap_ids\": []\n    },\n    {\n      \"id\": \"mcp_server\",\n      \"name\": \"MCP Server\",\n      \"respons ibility\": \"MCP protocol implementation\",\n      \"owned_node_ids\": [\"node:javascript_import:worker.mcp.server\"],\n      \"provenance_refs\": [\"prov:47b71b23b6c02da8\"],\n      \"contract_ids\": [],\n      \"check_ids\": [],\n      \"verification_gap_ids\": []\n    },\n    {\n      \"id\": \"llms_txt\",\n      \"name\": \"LLM Discovery Surface\",\n      \"responsibility\": \"llms.Good, agent-card is also copied by build, but not selected in packet, so gap.\nNow, also check the test uses the build, and there's test_public_contract which is not selected in nodes (packet has no test_file in selected, though node_kinds mentions it).\nTemplates extend base, reference the api.\nFirst, the model_id should be something like \"grok-4.3-arena-decomposer\" but probably use a standard one. The instruction says \"Use exact IDs/prov from packet.\" but for model_id, perhaps \"grok-4\" or whatever, but I think it's \"grok-4.The plans are historical for the current state. The decomp doesn't need to own them unless in selected.\nFirst, the required keys: model_id, project_id, goal, non_goals, components, contracts, cross_cutting_concerns, observable_checks, verification_gaps, near_neighbor_alternatives, acceptance_command_allowlist.\n\nmodel_id: Not specified in packet, perhaps default or from context. The query says \"model-derived decomposition JSON\", maybe use \"grok\" or something. But use exact IDs/prov from packet. Perhaps model_id is not in packet, but required. Let's assume \"leonbreukelman-engineer\" or wait, project_id is \"leonbreukelman-engineer\".\n\nproject_id: \" \"leonbreukelman-engineer\"\"\n\ngoal: \"decompose the AI-first public site and agent metadata project into source-backed components across build scripts, JavaScript worker code, public JSON data, templates, and docs\"\n\nnon_goals: [\"do not treat generated dist output as source ownership\",\"do not require Cloudflare deployment or public mutation\"]\n\nactual_verification_command: \"npm run build && npm run check:links\"\n\ngit_dirty: false, but not needed.\n\nnode_kinds and edge_kinds given, but not needed.\n\nselected_nodes: list them as ids.\n\nselected_import_edges: list them.\n\nsurface_counts: {\" 0}\n\nFor decomposition:\n\nComponents: semantic responsibility units.\n\n- Component for prompt/represent_me.md and its sections: \"prompt-representation\"\n\n- Component for README.md and sections: \"readme-documentation\"\n\n- Component for api/v1/profile.json: \"public-data\"\n\n- Component for llms.txt: \"llms discovery\"\n\n- Component for worker/mcp/server.js: \"mcp-server\"\n\n- Component for worker/index.js: \"worker-entry\"\n\n- Component for scripts/build.py: \"build-script\"\n\n- Component for scripts/check-public-links.py: \"link-checker\"\n\nThat's 8 components.\n\nFor each, id: e."
}

```

### final gate report

```json
{
  "passed": true,
  "violations": []
}
```

### graph summary

```json
{
  "node_count": 115,
  "edge_count": 128,
  "node_kinds": {
    "file": 21,
    "markdown_section": 31,
    "python_function": 27,
    "config": 10,
    "javascript_module": 2,
    "javascript_function": 4,
    "python_module": 3,
    "test_file": 1,
    "project": 1,
    "python_class": 1,
    "javascript_import": 1,
    "python_import": 13
  },
  "edge_kinds": {
    "configures": 10,
    "defined_in": 37,
    "contains": 32,
    "documents": 31,
    "imports": 17,
    "tests": 1
  },
  "protected_nodes": 0,
  "generated_nodes": 0
}
```

### final snapshot summary

```json
{
  "project_id": "leonbreukelman-engineer",
  "primary_model_id": "claude-opus-4-8",
  "components": [
    {
      "check_ids": [
        "check:full-acceptance",
        "check:build-only"
      ],
      "contract_ids": [],
      "id": "comp:build-pipeline",
      "name": "Static Site Build Pipeline",
      "owned_node_ids": [
        "node:d8fc3a88afab17188e7b"
      ],
      "provenance_refs": [
        "prov:8c73e6d6bb2288db"
      ],
      "responsibility": "Render templates and source data into the deployable site via scripts/build.py, failing closed when Python/Jinja dependencies are unavailable.",
      "verification_gap_ids": [
        "gap:build-data-edge-missing",
        "gap:templates-not-componentized"
      ]
    },
    {
      "check_ids": [
        "check:full-acceptance",
        "check:link-check"
      ],
      "contract_ids": [],
      "id": "comp:link-checker",
      "name": "Public Link Integrity Checker",
      "owned_node_ids": [
        "node:d1ab9b8e0eb01b071904"
      ],
      "provenance_refs": [
        "prov:cc1fa9e22afc08c6"
      ],
      "responsibility": "Validate that public links and assets resolve via scripts/check-public-links.py before/after build.",
      "verification_gap_ids": [
        "gap:linkcheck-target-unobserved"
      ]
    },
    {
      "check_ids": [
        "check:full-acceptance"
      ],
      "contract_ids": [
        "contract:router-to-mcp"
      ],
      "id": "comp:worker-edge-router",
      "name": "Cloudflare Worker Edge Router",
      "owned_node_ids": [
        "node:32f3a0d3845cf98fb8cb",
        "node:javascript_import:worker.mcp.server"
      ],
      "provenance_refs": [
        "prov:ea0068ba73266e60",
        "prov:47b71b23b6c02da8"
      ],
      "responsibility": "Serve as the deployed worker entrypoint (worker/index.js) routing inbound requests and delegating agent traffic to the MCP server module.",
      "verification_gap_ids": [
        "gap:mcp-protocol-unspecified"
      ]
    },
    {
      "check_ids": [
        "check:full-acceptance"
      ],
      "contract_ids": [
        "contract:router-to-mcp"
      ],
      "id": "comp:mcp-server",
      "name": "MCP Server Module",
      "owned_node_ids": [
        "node:1e8ba7fd1db36d8f49db"
      ],
      "provenance_refs": [
        "prov:e8c798459ce07e15"
      ],
      "responsibility": "Implement the Model Context Protocol surface (worker/mcp/server.js) that exposes agent-facing tools/resources.",
      "verification_gap_ids": [
        "gap:mcp-protocol-unspecified"
      ]
    },
    {
      "check_ids": [
        "check:full-acceptance",
        "check:link-check",
        "check:build-only"
      ],
      "contract_ids": [],
      "id": "comp:public-agent-data",
      "name": "Public Agent Data & Discovery Metadata",
      "owned_node_ids": [
        "node:b3b1f19ad2ed91bec458",
        "node:b8a0684279f7b4edc1bc"
      ],
      "provenance_refs": [
        "prov:5dd0cc494cd85fbe",
        "prov:77b106b079f49cac"
      ],
      "responsibility": "Provide machine-readable profile and agent discovery metadata as committed source (api/v1/profile.json, llms.txt).",
      "verification_gap_ids": [
        "gap:build-data-edge-missing",
        "gap:linkcheck-target-unobserved"
      ]
    },
    {
      "check_ids": [
        "check:build-only"
      ],
      "contract_ids": [],
      "id": "comp:persona-corpus",
      "name": "Persona Representation Corpus",
      "owned_node_ids": [
        "node:270b52766ba2097c3bf8",
        "node:087085bf23e3cc4628f2",
        "node:3497d88db26b2742c66a",
        "node:5ea405faea230cdf5498",
        "node:7ad8da6a627ab8d27e9e",
        "node:9d9d37a18c7ab7537c0f",
        "node:c627dcac9798554af877",
        "node:ca0aad13b3b497dd9e40",
        "node:cd8a921454b74ef09e06",
        "node:f0fd663527865f98c64e"
      ],
      "provenance_refs": [
        "prov:756f566ef137b772",
        "prov:a92ae5c99a4d4dae",
        "prov:ce979449395c4cd6",
        "prov:0cdbbafa93443ece",
        "prov:d068bad5b6984348"
      ],
      "responsibility": "Author the source-of-truth narrative for how AI agents represent Leon Breukelman across positioning, voice, strengths, stories, data sources, and contact (prompt/represent_me.md).",
      "verification_gap_ids": [
        "gap:build-data-edge-missing"
      ]
    },
    {
      "check_ids": [
        "check:full-acceptance"
      ],
      "contract_ids": [],
      "id": "comp:project-docs",
      "name": "Project Documentation",
      "owned_node_ids": [
        "node:69d6bc2e023965d76a75",
        "node:1c5a6f0459fa5b83d040",
        "node:242462366792e6c85ea0",
        "node:3b25680b492a6345baec",
        "node:4f7e53ec7b6ab7383a7c",
        "node:a5b95d7d7ada63930bef",
        "node:c1299be91730fc58c1e3",
        "node:d038e1fd31641ace3226",
        "node:d701b635b99442ff8d5a",
        "node:de09c473f13049315d86",
        "node:f918107b9b1786323a79",
        "node:fcbe6669d86356de0639"
      ],
      "provenance_refs": [
        "prov:4417f3bf0932d8ac",
        "prov:fa04b24fd751aac4",
        "prov:e2560a67a5e0ba01",
        "prov:febd8e67289848a5",
        "prov:11a91e2a1f50280f"
      ],
      "responsibility": "Onboard humans and AI agents with install, development, build, preview, deployment, and structure guidance (README.md).",
      "verification_gap_ids": [
        "gap:templates-not-componentized"
      ]
    }
  ],
  "contracts": [
    {
      "from_component_id": "comp:worker-edge-router",
      "id": "contract:router-to-mcp",
      "name": "Worker edge router invokes MCP server module",
      "near_neighbor_alternative_ids": [
        "nn:mcp-standalone"
      ],
      "provenance_refs": [
        "prov:ea0068ba73266e60",
        "prov:47b71b23b6c02da8",
        "prov:e8c798459ce07e15"
      ],
      "supporting_edge_ids": [
        "edge:ee74e56eeab2c21d6122"
      ],
      "to_component_id": "comp:mcp-server"
    }
  ],
  "cross_cutting_concerns": [
    {
      "category": "anti_fabrication",
      "component_ids": [
        "comp:build-pipeline",
        "comp:link-checker",
        "comp:worker-edge-router",
        "comp:mcp-server",
        "comp:public-agent-data",
        "comp:persona-corpus",
        "comp:project-docs"
      ],
      "contract_ids": [
        "contract:router-to-mcp"
      ],
      "description": "Every component, contract, and check must trace to selected nodes and prov identifiers in the packet; no files, edges, or behaviors are invented beyond the supplied graph.",
      "id": "concern:anti-fabrication",
      "provenance_refs": [
        "prov:8c73e6d6bb2288db",
        "prov:5dd0cc494cd85fbe",
        "prov:756f566ef137b772"
      ],
      "triggered_by": "universal"
    },
    {
      "category": "determinism",
      "component_ids": [
        "comp:build-pipeline",
        "comp:public-agent-data"
      ],
      "contract_ids": [],
      "description": "The build must be reproducible; scripts/build.py imports datetime, which can inject nondeterministic timestamps into rendered output and must be pinned or excluded from acceptance comparisons.",
      "id": "concern:determinism",
      "provenance_refs": [
        "prov:8c73e6d6bb2288db",
        "prov:667b089a4eb82688"
      ],
      "triggered_by": "scripts/build.py imports datetime via edge:9b853eb4121c2243cd48, risking nondeterministic build output"
    },
    {
      "category": "provenance",
      "component_ids": [
        "comp:build-pipeline",
        "comp:link-checker",
        "comp:worker-edge-router",
        "comp:mcp-server",
        "comp:public-agent-data",
        "comp:persona-corpus",
        "comp:project-docs"
      ],
      "contract_ids": [
        "contract:router-to-mcp"
      ],
      "description": "Each emitted component and contract carries prov references back to its source node(s) so the decomposition is auditable against the repository.",
      "id": "concern:provenance",
      "provenance_refs": [
        "prov:4417f3bf0932d8ac",
        "prov:cc1fa9e22afc08c6"
      ],
      "triggered_by": "universal"
    },
    {
      "category": "no_live_paid_api_acceptance",
      "component_ids": [
        "comp:build-pipeline",
        "comp:link-checker"
      ],
      "contract_ids": [],
      "description": "The acceptance command must not invoke any live paid API; npm run build performs local rendering and npm run check:links performs unauthenticated public HTTP fetches only.",
      "id": "concern:no-live-paid-api-acceptance",
      "provenance_refs": [
        "prov:8c73e6d6bb2288db",
        "prov:cc1fa9e22afc08c6"
      ],
      "triggered_by": "universal"
    }
  ],
  "observable_checks": [
    {
      "acceptance_command_id": "check:full-acceptance",
      "command": "npm run build && npm run check:links",
      "component_ids": [
        "comp:build-pipeline",
        "comp:link-checker",
        "comp:public-agent-data"
      ],
      "contract_ids": [],
      "description": "Canonical project verification: build the static site and validate that all public links resolve.",
      "id": "check:full-acceptance",
      "provenance_refs": [
        "prov:8c73e6d6bb2288db",
        "prov:cc1fa9e22afc08c6"
      ],
      "requires_network": false,
      "requires_paid_api": false,
      "safe_to_run_by_default": true
    },
    {
      "acceptance_command_id": "acmd:build-only",
      "command": "npm run build",
      "component_ids": [
        "comp:build-pipeline",
        "comp:persona-corpus",
        "comp:public-agent-data",
        "comp:project-docs"
      ],
      "contract_ids": [],
      "description": "Build the site only, exercising template/data/persona rendering; fails closed if Python/Jinja dependencies are unavailable.",
      "id": "check:build-only",
      "provenance_refs": [
        "prov:8c73e6d6bb2288db",
        "prov:73f52603d0cdfc2b"
      ],
      "requires_network": false,
      "requires_paid_api": false,
      "safe_to_run_by_default": true
    },
    {
      "acceptance_command_id": null,
      "command": "npm run check:links",
      "component_ids": [
        "comp:link-checker",
        "comp:public-agent-data"
      ],
      "contract_ids": [],
      "description": "Validate public links and assets resolve over the network without paid API access.",
      "id": "check:link-check",
      "provenance_refs": [
        "prov:cc1fa9e22afc08c6",
        "prov:6d95e66efa505ecc"
      ],
      "requires_network": true,
      "requires_paid_api": false,
      "safe_to_run_by_default": false
    }
  ],
  "held_out_probes": [
    {
      "builder_independent_from_decomposer": true,
      "builder_model_id": "claude-sonnet-4-6",
      "builder_prompt_hash": "23f143b1906b7774ce2768b6cf1de912023a5c18bc0f6c649c2c4538f4e8b363",
      "discrimination_passed": true,
      "golden_control_passed": true,
      "hidden_from_primary_decomposer": true,
      "id": "probe:worker-mcp-distinct-endpoints",
      "planted_negative_id": "neg:merge-worker-mcp-into-one-component",
      "provenance_refs": [
        "prov:ea0068ba73266e60",
        "prov:47b71b23b6c02da8",
        "prov:e8c798459ce07e15"
      ],
      "target_component_ids": [
        "comp:worker-edge-router",
        "comp:mcp-server"
      ],
      "target_contract_ids": [
        "contract:router-to-mcp"
      ]
    },
    {
      "builder_independent_from_decomposer": true,
      "builder_model_id": "claude-sonnet-4-6",
      "builder_prompt_hash": "23f143b1906b7774ce2768b6cf1de912023a5c18bc0f6c649c2c4538f4e8b363",
      "discrimination_passed": true,
      "golden_control_passed": true,
      "hidden_from_primary_decomposer": true,
      "id": "probe:persona-corpus-distinct-from-machine-data",
      "planted_negative_id": "neg:persona-corpus-merged-into-public-data",
      "provenance_refs": [
        "prov:756f566ef137b772",
        "prov:5dd0cc494cd85fbe",
        "prov:77b106b079f49cac"
      ],
      "target_component_ids": [
        "comp:persona-corpus",
        "comp:public-agent-data"
      ],
      "target_contract_ids": []
    },
    {
      "builder_independent_from_decomposer": true,
      "builder_model_id": "claude-sonnet-4-6",
      "builder_prompt_hash": "23f143b1906b7774ce2768b6cf1de912023a5c18bc0f6c649c2c4538f4e8b363",
      "discrimination_passed": true,
      "golden_control_passed": true,
      "hidden_from_primary_decomposer": true,
      "id": "probe:build-pipeline-source-only-no-dist",
      "planted_negative_id": "neg:dist-output-as-owned-source",
      "provenance_refs": [
        "prov:8c73e6d6bb2288db",
        "prov:73f52603d0cdfc2b"
      ],
      "target_component_ids": [
        "comp:build-pipeline"
      ],
      "target_contract_ids": []
    },
    {
      "builder_independent_from_decomposer": true,
      "builder_model_id": "claude-sonnet-4-6",
      "builder_prompt_hash": "23f143b1906b7774ce2768b6cf1de912023a5c18bc0f6c649c2c4538f4e8b363",
      "discrimination_passed": true,
      "golden_control_passed": true,
      "hidden_from_primary_decomposer": true,
      "id": "probe:anti-fabrication-concern-is-universal",
      "planted_negative_id": "neg:drop-anti-fabrication-concern",
      "provenance_refs": [
        "prov:8c73e6d6bb2288db",
        "prov:5dd0cc494cd85fbe",
        "prov:756f566ef137b772",
        "prov:4417f3bf0932d8ac"
      ],
      "target_component_ids": [
        "comp:build-pipeline",
        "comp:link-checker",
        "comp:worker-edge-router",
        "comp:mcp-server",
        "comp:public-agent-data",
        "comp:persona-corpus",
        "comp:project-docs"
      ],
      "target_contract_ids": [
        "contract:router-to-mcp"
      ]
    }
  ],
  "verification_gaps": [
    {
      "component_ids": [
        "comp:build-pipeline",
        "comp:public-agent-data",
        "comp:persona-corpus"
      ],
      "contract_ids": [],
      "description": "build.py's consumption of api/v1/profile.json, llms.txt, and the persona corpus is not represented by any graph edge; only Python stdlib/jinja2 import edges were captured, so the build-consumes-data and build-renders-persona contracts are inferred rather than graph-observed.",
      "id": "gap:build-data-edge-missing",
      "proposed_closure_check": "Assert that rendered build output embeds fields from api/v1/profile.json and headings from prompt/represent_me.md after npm run build.",
      "provenance_refs": [
        "prov:8c73e6d6bb2288db",
        "prov:5dd0cc494cd85fbe",
        "prov:756f566ef137b772"
      ],
      "severity": "medium"
    },
    {
      "component_ids": [
        "comp:build-pipeline",
        "comp:project-docs"
      ],
      "contract_ids": [],
      "description": "build.py imports jinja2 and README#Structure documents a templates surface, but no template node was selected in the packet, leaving the template surface uncomponentized.",
      "id": "gap:templates-not-componentized",
      "proposed_closure_check": "Re-run graph extraction to include template (e.g. *.j2/*.html) nodes and bind them to the build pipeline component, then verify each template is rendered by npm run build.",
      "provenance_refs": [
        "prov:b282fbda2c978640",
        "prov:e2560a67a5e0ba01",
        "prov:8c73e6d6bb2288db"
      ],
      "severity": "medium"
    },
    {
      "component_ids": [
        "comp:link-checker",
        "comp:public-agent-data",
        "comp:project-docs"
      ],
      "contract_ids": [],
      "description": "scripts/check-public-links.py uses urllib.request to fetch public URLs, but the set of checked targets is not represented as graph nodes/edges, so link-surface coverage cannot be verified from the packet.",
      "id": "gap:linkcheck-target-unobserved",
      "proposed_closure_check": "Capture the link inventory emitted by npm run check:links and assert each public asset (api/v1/profile.json, llms.txt) is included in the checked set.",
      "provenance_refs": [
        "prov:cc1fa9e22afc08c6",
        "prov:6d95e66efa505ecc"
      ],
      "severity": "low"
    },
    {
      "component_ids": [
        "comp:mcp-server",
        "comp:worker-edge-router"
      ],
      "contract_ids": [
        "contract:router-to-mcp"
      ],
      "description": "The MCP request/response contract served by worker/mcp/server.js is not captured by any node/edge beyond the module import, so the protocol surface is unverified.",
      "id": "gap:mcp-protocol-unspecified",
      "proposed_closure_check": "Add a worker integration test that issues a representative MCP request through worker/index.js and asserts a schema-valid response from the server module.",
      "provenance_refs": [
        "prov:e8c798459ce07e15",
        "prov:ea0068ba73266e60"
      ],
      "severity": "medium"
    },
    {
      "component_ids": [
        "comp:build-pipeline",
        "comp:public-agent-data"
      ],
      "contract_ids": [],
      "description": "Model proposed `contract:build-consumes-data` as a semantic contract, but the current graph has no deterministic supporting edge; keep it as a verification gap rather than a passed contract.",
      "id": "gap:unsupported-contract:contract-build-consumes-data",
      "proposed_closure_check": "Add deterministic read/reference/call edge extraction or a focused local check that proves this semantic dependency.",
      "provenance_refs": [
        "prov:8c73e6d6bb2288db",
        "prov:5dd0cc494cd85fbe"
      ],
      "severity": "medium"
    },
    {
      "component_ids": [
        "comp:build-pipeline",
        "comp:persona-corpus"
      ],
      "contract_ids": [],
      "description": "Model proposed `contract:build-renders-persona` as a semantic contract, but the current graph has no deterministic supporting edge; keep it as a verification gap rather than a passed contract.",
      "id": "gap:unsupported-contract:contract-build-renders-persona",
      "proposed_closure_check": "Add deterministic read/reference/call edge extraction or a focused local check that proves this semantic dependency.",
      "provenance_refs": [
        "prov:8c73e6d6bb2288db",
        "prov:756f566ef137b772"
      ],
      "severity": "medium"
    },
    {
      "component_ids": [
        "comp:link-checker",
        "comp:public-agent-data"
      ],
      "contract_ids": [],
      "description": "Model proposed `contract:linkcheck-validates-data` as a semantic contract, but the current graph has no deterministic supporting edge; keep it as a verification gap rather than a passed contract.",
      "id": "gap:unsupported-contract:contract-linkcheck-validates-data",
      "proposed_closure_check": "Add deterministic read/reference/call edge extraction or a focused local check that proves this semantic dependency.",
      "provenance_refs": [
        "prov:cc1fa9e22afc08c6",
        "prov:5dd0cc494cd85fbe"
      ],
      "severity": "medium"
    }
  ],
  "near_neighbor_alternatives": [
    {
      "alternative": "Own the generated dist/ output as the primary build artifact component.",
      "id": "nn:build-vs-dist",
      "provenance_refs": [
        "prov:8c73e6d6bb2288db"
      ],
      "target_id": "comp:build-pipeline",
      "why_not_primary": "Non-goal forbids treating generated dist output as source ownership; scripts/build.py is the source-of-truth build surface. Anchored to goal: decompose the AI-first public site and agent metadata project into source-backed components across build scripts, JavaScript worker code, public JSON data, templates, and docs; non-goals: do not treat generated dist output as source ownership; do not require Cloudflare deployment or public mutation."
    },
    {
      "alternative": "Run the MCP server as a standalone Node process instead of a Cloudflare Worker module.",
      "id": "nn:mcp-standalone",
      "provenance_refs": [
        "prov:e8c798459ce07e15",
        "prov:47b71b23b6c02da8"
      ],
      "target_id": "comp:mcp-server",
      "why_not_primary": "Source shows worker/mcp/server.js imported by the Cloudflare worker entry (worker/index.js) and deployment targets Cloudflare Pages; the packet does not require an alternate runtime. Anchored to goal: decompose the AI-first public site and agent metadata project into source-backed components across build scripts, JavaScript worker code, public JSON data, templates, and docs; non-goals: do not treat generated dist output as source ownership; do not require Cloudflare deployment or public mutation."
    },
    {
      "alternative": "Generate api/v1/profile.json and llms.txt at build time rather than committing them as source.",
      "id": "nn:data-generated-at-build",
      "provenance_refs": [
        "prov:5dd0cc494cd85fbe",
        "prov:77b106b079f49cac"
      ],
      "target_id": "comp:public-agent-data",
      "why_not_primary": "The packet selects profile.json (config) and llms.txt as committed source files with their own prov, and no edge shows build.py emitting them. Anchored to goal: decompose the AI-first public site and agent metadata project into source-backed components across build scripts, JavaScript worker code, public JSON data, templates, and docs; non-goals: do not treat generated dist output as source ownership; do not require Cloudflare deployment or public mutation."
    },
    {
      "alternative": "Fold the represent_me persona prompt into the public JSON data component.",
      "id": "nn:persona-in-data",
      "provenance_refs": [
        "prov:756f566ef137b772"
      ],
      "target_id": "comp:persona-corpus",
      "why_not_primary": "prompt/represent_me.md is a distinct prose corpus (file plus nine narrative sections) with separate prov; it is authored representation guidance, not machine-readable API data. Anchored to goal: decompose the AI-first public site and agent metadata project into source-backed components across build scripts, JavaScript worker code, public JSON data, templates, and docs; non-goals: do not treat generated dist output as source ownership; do not require Cloudflare deployment or public mutation."
    }
  ],
  "acceptance_command_allowlist": [
    "acmd:build-only",
    "acmd:full-build-and-link-check",
    "acmd:link-check",
    "check:full-acceptance"
  ]
}
```

## Rereview request

Return JSON first with keys: passed, critical_blockers, major_findings, minor_findings, required_repairs, acceptance_assessment. Attack whether the final repaired pilots now satisfy: non-fixture leading-model output, independent probes, negative-control gate failure, semantic responsibility-bearing components, real deterministic contracts, explicit gaps for unsupported static/data/template dependencies, generated/protected exclusion, actual command alignment, FMC-MCP manual evaluability, held-out generalization, and whether this is still gameable by a report generator. If critical blockers remain, be specific.