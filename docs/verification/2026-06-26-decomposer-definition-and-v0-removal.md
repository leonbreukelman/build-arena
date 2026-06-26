# Decomposer definition and project-model/v0 removal audit

Audit scope: repository-to-project-model decomposition code and the immediate consumers that read the snapshot bundle or the v1 artifact. This document is evidence-backed from the repository at the checked revision below; it does not propose or apply code changes.

Repository state checked:

- `date +%F` returned `2026-06-25` from the local host.
- `git status --short --branch` returned `## main...origin/main`.
- `git rev-parse HEAD` and `git rev-parse origin/main` both returned `2f5286b1d0b6070bccab9a73fe067a8333ebbe96`.
- `git grep -l -E 'project-model/v0|project-model-v0|ProjectModelV0|project_model_v0|PROJECT_MODEL_V0|format.*project-model-v0|--format.*project-model-v0' -- . ':!docs/verification' ':!arena/generated'` returned the v0 reference inventory listed in section 5.

Terminology note:

- Several decomposer-area files use non-neutral project shorthand such as `F3`, `wrong-target`, `fluent`, and `Elenchus`: `arena/decomposer.py:337`, `arena/decomposer.py:357`, `arena/project_decomposer_ai.py:538-540`, `arena/project_decomposer_ai.py:674-675`, `arena/project_model_v0.py:223-228`, and `docs/project-model-v0.md:19-32`. This document treats those strings as current code/data facts only. It does not use them as new planning terminology.

## 1. What the decomposer does

### 1.1 Current entry points

The primary snapshot CLI is `arena.project_model_cli`:

- `arena/project_model_cli.py:23-40` defines the `snapshot` subcommand and its inputs: `--project`, `--artifacts-root`, `--project-id`, `--goal`, `--non-goal`, `--source-task`, `--primary-backlog-item`, `--llm-mode`, `--model-output`, live-provider flags, `--run-adversarial-probes`, and `--overwrite`.
- `arena/project_model_cli.py:31` constrains `--llm-mode` to `fixture`, `recorded`, `live`, or `off`; default is `fixture`.
- `arena/project_model_cli.py:66-72` refuses live mode if either required live control is absent: `--allow-live` is checked first, and `--live-model` is checked separately.
- `arena/project_model_cli.py:74-91` passes the CLI arguments into `build_project_model_snapshot(...)`.
- `arena/project_model_cli.py:95-104` prints a JSON summary containing `passed`, `snapshot_id`, `manifest_path`, `snapshot_dir`, `gate_report_path`, and `violation_count`, and exits non-zero when the gate report did not pass.

There is also a legacy scanner CLI in `arena.decomposer`:

- `arena/decomposer.py:838-858` defines `python -m arena.decomposer --project ... --format {scanner-v0.1,project-model-v0}`.
- `arena/decomposer.py:860-867` requires `--source-task` and `--primary-backlog-item` for `--format project-model-v0`.
- `arena/decomposer.py:870-887` emits either the `project-model/v0` adapter output or the internal scanner model.
- `arena/decomposer.py:897-912` writes output before reporting quality-gate or gap failures.

### 1.2 End-to-end path for the primary snapshot pipeline

The current primary path is:

1. Build a deterministic project graph.
   - `arena/project_decomposer_ai.py:86-90` calls `build_project_graph(project)`, derives `project_id`, default `goal`, default `non_goals`, and `graph_hash` from `canonical_graph_json(graph)`.
   - `arena/project_graph.py:1244-1317` implements `build_project_graph(...)`: resolves the git root, computes a project provenance record, enumerates tracked and untracked files, hashes file identity bytes, creates file/config/protected/generated nodes and edges, parses Python/JavaScript/Markdown where applicable, adds call/import/test edges, and returns `ProjectGraph(schema_version="project-graph/v0.1", ...)`.
   - `arena/project_graph.py:43-96` shows the graph contract: `ProvenanceRef`, `GraphNode`, `GraphEdge`, `GitState`, and `ProjectGraph`.

2. Build a decomposer prompt from the graph.
   - `arena/project_decomposer_ai.py:92` builds `_decomposer_prompt(...)` before selecting an LLM mode.
   - `arena/project_decomposer_ai.py:590-669` constructs that prompt. The prompt imports `primary_inventory_nodes` from the gate (`arena/project_decomposer_ai.py:598`) so the prompt's primary-module list matches the gate's coverage list. It lists primary nodes and symbol nodes (`arena/project_decomposer_ai.py:600-615`), import/test edges (`arena/project_decomposer_ai.py:616-618`), and the exact JSON shape expected from a model (`arena/project_decomposer_ai.py:619-638`).
   - The prompt instructs the model to reuse only shown node/edge/provenance ids (`arena/project_decomposer_ai.py:639`), own every primary module or record a gap (`arena/project_decomposer_ai.py:640-642`), create multiple components (`arena/project_decomposer_ai.py:644-645`), include universal concerns (`arena/project_decomposer_ai.py:649-655`), provide at least one observable check (`arena/project_decomposer_ai.py:656`), and record an unproven-probe gap instead of claiming probe results (`arena/project_decomposer_ai.py:657-659`).

3. Produce raw model output according to `--llm-mode`.
   - `arena/project_decomposer_ai.py:93-100` implements three non-live modes: `fixture` calls `build_fixture_model_output(...)`, `recorded` requires `model_output_path` and calls `load_recorded_model_output(...)`, and `off` calls `build_noop_model_output(...)`.
   - `arena/project_decomposer_ai.py:101-109` implements live mode by constructing `LiveProjectModelLLM(...)` unless an injected `live_llm` is supplied, then calling `adapter.generate(prompt)`.
   - `arena/project_model_llm.py:30-31` shows that recorded mode is a file replay: it reads JSON from `path` and normalizes it. It does not analyze the target repo.
   - `arena/project_model_llm.py:115-116` shows fixture mode delegates to `build_meta_model_output(...)`.
   - `arena/project_model_llm.py:119-144` shows off mode emits `model_id: noop-no-live-model`, empty components/contracts/checks, and one blocker verification gap.
   - `arena/project_model_llm.py:54-92` shows live mode uses `OpenAICompatibleChatClient`, requires explicit model resolution, asks for JSON output, validates the provider text as JSON, stamps `model_id`, and attaches `_provider_metadata`.

4. Coerce raw output into the internal snapshot contract.
   - `arena/project_decomposer_ai.py:113-121` calls `_snapshot_from_model_output(...)` with project id/root, goal, non-goals, graph hash, and prompt hash.
   - `arena/project_decomposer_ai.py:387-420` shows the exact coercion: `components`, `contracts`, `cross_cutting_concerns`, `observable_checks`, `held_out_probes`, `verification_gaps`, `near_neighbor_alternatives`, and `acceptance_command_allowlist` become a `ProjectModelSnapshot`.
   - `arena/project_snapshot.py:102-124` defines `ProjectModelSnapshot`: `project_id`, `project_root`, `goal`, `non_goals`, `primary_model_id`, `graph_hash`, `schema_version`, `snapshot_id`, `created_at_utc`, `components`, `contracts`, `cross_cutting_concerns`, `observable_checks`, `held_out_probes`, `verification_gaps`, `near_neighbor_alternatives`, `acceptance_command_allowlist`, `prompt_hashes`, `model_output_hashes`, and `input_hashes`.
   - `arena/project_decomposer_ai.py:122-125` then records graph/model-output hashes, closes import contracts for gate evaluation, and finalizes the snapshot identity.

5. Close mechanical import contracts, then run the deterministic gate.
   - `arena/project_model_gate.py:336-350` documents `close_import_contracts_for_gate(...)`: it preserves valid model contracts, removes invalid supporting-edge claims, and adds stable `contract.auto.<edge>` contracts for import edges whose endpoints map to existing components. It says it never invents components, reassigns ownership, relaxes the gate, or mutates raw model output.
   - `arena/project_decomposer_ai.py:124` calls that closure before snapshot identity finalization.
   - `arena/project_decomposer_ai.py:141-143` writes an import-closure report and runs `run_project_model_gate(snapshot, graph, proof_artifact_base=snapshot_dir)`.
   - `arena/project_model_gate.py:28-67` validates snapshot schema version, goal/non-goals, components, observable checks, and graph-hash equality.
   - `arena/project_model_gate.py:68-224` validates component names/responsibilities, node ownership, provenance, contract/check/gap references, import-edge coverage, universal concerns, primary inventory coverage, safe acceptance commands, near-neighbor references, and probe-or-gap presence.
   - `arena/project_model_gate.py:704-755` hard-codes the local command allowlist used for acceptance-command safety.

6. Write the snapshot bundle and both project-model projections.
   - `arena/project_decomposer_ai.py:131-138` creates the snapshot directory and enforces `overwrite` behavior.
   - `arena/project_decomposer_ai.py:141-150` writes the import-contract-closure, graph, encyclopedia, snapshot, gate-report, and v0 JSON sidecars.
   - `arena/project_decomposer_ai.py:158-165` creates the v1 JSON artifact via `project_model_v1_from_snapshot(...)` and writes it.
   - `arena/project_decomposer_ai.py:168-189` writes prompts and raw model outputs.
   - `arena/project_decomposer_ai.py:204-244` writes the manifest with snapshot metadata, graph/snapshot/gate paths and hashes, `project_model_primary_path` pointing at the v1 JSON artifact, `project_model_v1_path`, `project_model_v1_hash`, `project_model_v0_path`, `project_model_v0_hash`, dirty state, input hashes, prompt hashes, model ids, output hashes, and artifact hashes.

7. Return the build result.
   - `arena/project_decomposer_ai.py:56-64` defines `BuildProjectModelResult` with `snapshot`, `graph`, `gate_report`, `snapshot_dir`, `manifest_path`, and `manifest`.
   - `arena/project_decomposer_ai.py:245-252` returns that object after the manifest is written.

### 1.3 Exact current v1 output contract emitted by code

The emitted v1 object is constructed in one function:

- `arena/project_model_v1.py:49-94` returns the v1 object.
- `arena/project_model_v1.py:50-57` emits `schemaVersion`, `id`, and `project`.
- `arena/project_model_v1.py:58` embeds the full internal `snapshot` via `snapshot_to_dict(snapshot)`.
- `arena/project_model_v1.py:59-65` embeds `projectGraph` with `schemaVersion`, `graphHash`, `projectRoot`, `nodes`, and `edges`.
- `arena/project_model_v1.py:66` embeds `gateReport`.
- `arena/project_model_v1.py:67-77` embeds git provenance and the provenance-ref strategy.
- `arena/project_model_v1.py:78-83` embeds `hashes` for input, prompt, output, and artifacts.
- `arena/project_model_v1.py:84-87` embeds model ids.
- `arena/project_model_v1.py:88` embeds default derived-artifact descriptors unless overridden.
- `arena/project_model_v1.py:89` embeds `iterationReadiness` from `build_iteration_readiness(snapshot, graph)`.
- `arena/project_model_v1.py:90-93` embeds a `compatibility` block with `projectModelV0Path` and the role string saying v0 is legacy compatibility.

The JSON schema exists and partially matches the emitted contract:

- `docs/schemas/project-model-v1.schema.json:8-20` requires `schemaVersion`, `id`, `project`, `snapshot`, `projectGraph`, `gateReport`, `provenance`, `hashes`, `models`, `derivedArtifacts`, and `compatibility`.
- `docs/schemas/project-model-v1.schema.json:59-71` defines `iterationReadiness` and its required subfields, but it is not listed in the top-level required list at `docs/schemas/project-model-v1.schema.json:8-20`. That is a contract gap because downstream consumers read `iterationReadiness` as load-bearing data.

### 1.4 What each `--llm-mode` actually does

- `fixture` is deterministic local analysis over the deterministic graph, not a recorded canned JSON file and not a live LLM call. Evidence: `arena/project_decomposer_ai.py:93-94` calls `build_fixture_model_output(...)`; `arena/project_model_llm.py:115-116` delegates fixture output to `build_meta_model_output(...)`; `arena/project_meta_decomposer.py:84-123` computes components, contracts, checks, gaps, near-neighbor alternatives, and allowlist from `ProjectGraph` data.
- `recorded` replays a provided JSON model output file. It is not deterministic static analysis of the target repo. Evidence: `arena/project_decomposer_ai.py:95-98` requires and loads `model_output_path`; `arena/project_model_llm.py:30-31` only reads JSON and normalizes it. The graph and gate still run against the current target, so a mismatched recording can fail, but the semantic component proposal comes from the file.
- `off` emits a no-op JSON model output with no components/checks and one blocker gap. Evidence: `arena/project_decomposer_ai.py:99-100`; `arena/project_model_llm.py:119-144`. Reproduction on `/tmp/decomposer-audit.hIuO9O/repo` produced `model noop-no-live-model`, `gate_passed False`, `violations 5`, first violation `Snapshot must contain at least one component.`
- `live` calls an OpenAI-compatible client with explicit model resolution and JSON response format. Evidence: `arena/project_decomposer_ai.py:101-109`; `arena/project_model_llm.py:54-92`. The CLI refuses live mode unless `--allow-live` is set and `--live-model` is also supplied (`arena/project_model_cli.py:66-72`).

## 2. Component breakdown

Each item below names the real code surface, its input/output, determinism status, callers, and guarantee boundary.

### 2.1 Project graph builder

- Code shown: `arena/project_graph.py:1244-1317`.
- Input: `project_root: str | Path` (`arena/project_graph.py:1244`).
- Output: `ProjectGraph(schema_version="project-graph/v0.1", project_root, git, nodes, edges, metadata)` (`arena/project_graph.py:1310-1317`).
- Determinism status: deterministic filesystem/git/static parser pass. Evidence: it uses git commands and file bytes (`arena/project_graph.py:103-140`, `arena/project_graph.py:1271-1277`), Python/JavaScript/Markdown parsers (`arena/project_graph.py:1294-1301`), and deterministic provenance ids (`arena/project_graph.py:181-203`).
- Caller: `build_project_model_snapshot(...)` calls it at `arena/project_decomposer_ai.py:86`.
- Guarantee: the graph carries file/node/edge/provenance data; it does not produce semantic components by itself.

### 2.2 Prompt builder for live/recorded-model shape

- Code shown: `arena/project_decomposer_ai.py:590-669`.
- Input: `project_id`, `goal`, `non_goals`, `ProjectGraph` (`arena/project_decomposer_ai.py:590`).
- Output: a prompt string containing node ids, provenance ids, edge ids, and the required JSON shape (`arena/project_decomposer_ai.py:619-638`).
- Determinism status: deterministic prompt assembly.
- Caller: `build_project_model_snapshot(...)` at `arena/project_decomposer_ai.py:92`.
- Guarantee: prompt vocabulary is tied to the gate's `primary_inventory_nodes` selector (`arena/project_decomposer_ai.py:591-598`); the prompt itself does not validate output.

### 2.3 LLM/replay/fixture output selector

- Code shown: `arena/project_decomposer_ai.py:93-111`.
- Input: `llm_mode`, graph, prompt, optional recording path, optional live adapter/provider flags.
- Output: `raw_output: dict[str, Any]` consumed by `_snapshot_from_model_output(...)`.
- Determinism status by branch:
  - `fixture`: deterministic local meta-decomposer (`arena/project_model_llm.py:115-116`, `arena/project_meta_decomposer.py:84-123`).
  - `recorded`: replay of provided JSON (`arena/project_model_llm.py:30-31`).
  - `off`: deterministic no-op output (`arena/project_model_llm.py:119-144`).
  - `live`: LLM call (`arena/project_model_llm.py:64-92`).
- Caller: `project_model_cli.snapshot` (`arena/project_model_cli.py:74-91`), `repo_goal_loop` (`arena/repo_goal_loop.py:319-334`), and subprocess proposal/dream runs (`arena/proposal_run.py:216-243`, `arena/dream_run.py:178-223`).
- Guarantee: only the graph/gate and safety filters are deterministic. Fixture is local heuristic analysis. Recorded is replay. Live is model-generated output constrained after the fact.

### 2.4 Fixture/meta decomposer

- Code shown: `arena/project_meta_decomposer.py:84-123`.
- Input: deterministic `ProjectGraph`, `project_id`, `goal`, `non_goals`.
- Output: a model-output dict with `model_id`, `project_id`, `goal`, `non_goals`, `components`, `contracts`, `cross_cutting_concerns`, `observable_checks`, `held_out_probes`, `verification_gaps`, `near_neighbor_alternatives`, and `acceptance_command_allowlist` (`arena/project_meta_decomposer.py:102-123`).
- Determinism status: deterministic static graph heuristic. It is not canned replay and not a live LLM.
- Callers: fixture mode through `build_fixture_model_output(...)` (`arena/project_model_llm.py:115-116`).
- Guarantees and limits shown by code:
  - Project roots come from manifest nodes (`arena/project_meta_decomposer.py:137-168`).
  - Components are seeded from source/support nodes (`arena/project_meta_decomposer.py:249-328`).
  - Contracts are import-edge based (`arena/project_meta_decomposer.py:331-369`).
  - It always adds a semantic-validation gap when components exist (`arena/project_meta_decomposer.py:420-429`), so it does not claim independent semantic proof.
  - Component responsibility text is generated from root, seed, and role (`arena/project_meta_decomposer.py:679-683`).

### 2.5 Raw-output-to-snapshot coercion

- Code shown: `arena/project_decomposer_ai.py:387-420`.
- Input: raw model output dict, project id/root, goal, non-goals, graph hash, prompt hash.
- Output: `ProjectModelSnapshot` (`arena/project_snapshot.py:102-124`).
- Determinism status: deterministic coercion/normalization of model or fixture output.
- Caller: `build_project_model_snapshot(...)` at `arena/project_decomposer_ai.py:113-121`.
- Guarantee: required lists are coerced into dataclasses; `_safe_acceptance_commands(...)` filters model-controlled allowlist entries (`arena/project_decomposer_ai.py:423-456`).

### 2.6 Import-contract closure and project-model gate

- Code shown: `arena/project_model_gate.py:28-224` and `arena/project_model_gate.py:336-410`.
- Input: `ProjectModelSnapshot` plus `ProjectGraph`.
- Output: `GateReport(passed, violations)` via `arena/project_snapshot.py:134-138` and `gate_report_to_dict(...)` at `arena/project_snapshot.py:220-221`.
- Determinism status: deterministic local validation. No live provider.
- Callers: `build_project_model_snapshot(...)` (`arena/project_decomposer_ai.py:141-143`) and `project_model_cli gate` (`arena/project_model_cli.py:107-112`).
- Guarantee: validates structural/provenance/hash/safety properties. It does not prove the semantic correctness of responsibility summaries beyond measurable predicates like minimum words, non-file-bucket text, resolvable provenance, edge coverage, and explicit gaps (`arena/project_model_gate.py:68-224`).

### 2.7 v0 compatibility projection inside the AI decomposer

- Code shown: `arena/project_decomposer_ai.py:459-560`.
- Input: `ProjectModelSnapshot`, `ProjectGraph`, `source_task`, `primary_backlog_item`.
- Output: a dict with `schemaVersion: project-model/v0` (`arena/project_decomposer_ai.py:499-520` and following fields through the function).
- Determinism status: deterministic projection from snapshot/graph.
- Caller: `build_project_model_snapshot(...)` writes it at `arena/project_decomposer_ai.py:149-150`.
- Guarantee: compatibility output only. It maps snapshot components to v0 components with one generated check per component (`arena/project_decomposer_ai.py:459-486`) and projects contracts/gaps/near-neighbors/probes. It is not the primary model path (`arena/project_decomposer_ai.py:221-225`).

### 2.8 v1 assembler

- Code shown: `arena/project_model_v1.py:19-94`.
- Input: `ProjectModelSnapshot`, `ProjectGraph`, `GateReport`, artifact hashes, compatibility v0 path.
- Output: a single `project-model/v1` dict.
- Determinism status: deterministic assembly from already-produced artifacts.
- Caller: `build_project_model_snapshot(...)` (`arena/project_decomposer_ai.py:158-165`).
- Guarantee: v1 wraps the full snapshot, graph, gate report, provenance, hashes, models, derived-artifact descriptors, iteration-readiness projection, and a v0 compatibility pointer. It does not embed the v0 JSON content.

### 2.9 Iteration-readiness projection

- Code shown: `arena/project_iteration_readiness.py:82-105`.
- Input: `snapshot`, `graph`.
- Output: `summary`, `componentProfiles`, `runtimeContracts`, `externalSurfaces`, `productInvariants`, `qualityGates`, `priorityBacklog`, and `openQuestions`.
- Determinism status: deterministic heuristics over source text, graph, and snapshot.
- Caller: v1 assembler at `arena/project_model_v1.py:89`.
- Guarantee: produces the immediate downstream guidance most consumers read. Its responsibility summaries are heuristic text (`arena/project_iteration_readiness.py:24-44`, `arena/project_iteration_readiness.py:238-267`), not validated semantic truth.

### 2.10 Legacy deterministic scanner and v0 adapter

- Code shown: `arena/decomposer.py:192-220`, `arena/decomposer.py:223-246`, and `arena/decomposer.py:249-392`.
- Input: filesystem/git project root and required v0 source-task/backlog metadata.
- Output: either internal `ProjectModel(schema_version: project-model/v0.1)` or `ProjectModelV0(schemaVersion: project-model/v0)`.
- Determinism status: deterministic filesystem/git scanner; no LLM.
- Callers: legacy CLI (`arena/decomposer.py:838-912`) and tests. It is not used by the primary v1 snapshot pipeline except as a separate compatibility surface.
- Guarantee: scanner owns every included file exactly once or reports validation errors (`arena/decomposer.py:404-520`). Its generic mode groups files into broad buckets (`arena/decomposer.py:1439-1495`) and uses generic responsibilities (`arena/decomposer.py:1531-1537`).

## 3. Material gaps with evidence

### 3.1 `responsibility` in fixture mode is a seeded heuristic, not semantic analysis

Evidence:

- Fixture mode calls `build_meta_model_output(...)` (`arena/project_model_llm.py:115-116`).
- `build_meta_model_output(...)` builds components from roots/nodes/checks (`arena/project_meta_decomposer.py:84-96`).
- `_component_responsibility(...)` returns template strings: `Provide the {seed} responsibility within the {toolchain} project root using graph-resolved source evidence.` or `Support the {seed} responsibility for the {toolchain} project root with manifest, test, or documentation evidence.` (`arena/project_meta_decomposer.py:679-683`).

Reproduction on a small unrelated repo at `/tmp/decomposer-audit.hIuO9O/repo`:

- `uv run python -m arena.project_model_cli snapshot --project /tmp/decomposer-audit.hIuO9O/repo --artifacts-root /tmp/decomposer-audit.hIuO9O/artifacts-fixture --project-id audit-repro --goal "audit unrelated repo decomposition" --llm-mode fixture --overwrite` exited with `passed: true`.
- The emitted fixture components included:
  - `component.payments-client` responsibility: `Provide the payments-client responsibility within the python project root using graph-resolved source evidence.`
  - `component.workspace-guidance` responsibility: `Support the guidance responsibility for the python project root with manifest, test, or documentation evidence.`
  - `component.workspace-tooling` responsibility: `Support the tooling responsibility for the python project root with manifest, test, or documentation evidence.`

Conclusion: fixture mode can pass the deterministic gate while producing generic responsibility text. That is acceptable only if consumers treat `responsibility` as a grounded heuristic, not a proven semantic definition.

### 3.2 `responsibilitySummary` is a source-text keyword heuristic with special-case tags

Evidence:

- `component_responsibility_summary(...)` uses module label, key symbols, and behavioral tags to generate text (`arena/project_iteration_readiness.py:24-44`).
- Behavioral tags are keyword/marker detections over lowercased source and symbols (`arena/project_iteration_readiness.py:47-79`). Markers include auth, rate limits, concurrency, pagination, HTTP clients, MCP resources/tools, client injection, and entrypoint names.
- `_component_profiles(...)` reads owned-node source text, detects tags, computes key symbols, and writes `responsibilitySummary`, `behavioralTags`, `riskLevel`, and `whyPriority` (`arena/project_iteration_readiness.py:238-267`).

Reproduction on `/tmp/decomposer-audit.hIuO9O/repo`:

- `component.payments-client` summary became `Provide `payments.client.charge_card` behavior through source symbols charge_card, parse_invoice.` with no behavioral tags, even though the sample function performs an HTTP-like card charge through `client.post(...)`.
- This follows the code: HTTP tagging looks for `httpx`, `/api/fmc`, or `asyncclient` (`arena/project_iteration_readiness.py:64-65`), not arbitrary `client.post(...)` calls.

Conclusion: `responsibilitySummary` is useful as a deterministic summary, but it degrades outside the tuned marker families. It should not be treated as a complete domain responsibility.

### 3.3 Fixture mode is deterministic but not a replayed canned answer and not LLM semantics

Evidence:

- Fixture mode delegates to `build_meta_model_output(...)` (`arena/project_model_llm.py:115-116`), which computes from graph roots/nodes/edges/checks (`arena/project_meta_decomposer.py:84-123`).
- It records `model_id: fixture-meta-decomposer` (`arena/project_meta_decomposer.py:103`).

Conclusion: calling fixture mode "deterministic analysis" is accurate only for the implemented graph/path/source heuristic. It is not a live model and not a semantic oracle.

### 3.4 Recorded mode is replay, not analysis

Evidence:

- `arena/project_decomposer_ai.py:95-98` requires `model_output_path` and loads it.
- `arena/project_model_llm.py:30-31` reads JSON from that path and normalizes it.

Conclusion: recorded mode guarantees reproducible replay of a prior output plus current graph/gate checking. It does not guarantee that the recorded output was generated from the current target repo.

### 3.5 Off mode writes artifacts but intentionally fails the model gate

Evidence:

- `arena/project_model_llm.py:119-144` emits no components, no contracts, no observable checks, and one blocker gap.
- `arena/project_model_gate.py:58-61` requires at least one component and one observable check.

Reproduction on `/tmp/decomposer-audit.hIuO9O/repo`:

- The `off` snapshot command exited non-zero and still wrote a snapshot bundle.
- The v1 artifact had primary model `noop-no-live-model`, gate `passed: false`, and the first violation was `Snapshot must contain at least one component.`

Conclusion: `off` is a safe artifact-producing failure mode, not a usable project model.

### 3.6 v1 schema does not require `iterationReadiness`, but consumers require it

Evidence:

- Emitter always includes `iterationReadiness` (`arena/project_model_v1.py:89`).
- Schema defines `iterationReadiness` and its subfields (`docs/schemas/project-model-v1.schema.json:59-71`) but omits it from top-level `required` (`docs/schemas/project-model-v1.schema.json:8-20`).
- Immediate consumers read it: capability lift reads `iterationReadiness.componentProfiles` (`arena/capability_lift.py:55-58`), intake reads `iterationReadiness.componentProfiles`, `qualityGates`, and `openQuestions` (`arena/project_intake_scorecard.py:321-323`, `arena/project_intake_scorecard.py:797-807`, `arena/project_intake_scorecard.py:842-854`), proposal planner reads `iterationReadiness.openQuestions` through the scorecard's `snapshotPath` (`arena/proposal_planner.py:286-301`), and dream generation reads `iterationReadiness.componentProfiles` (`arena/dream_generate.py:182-188`).

Conclusion: the emitted artifact currently satisfies consumers, but the schema permits artifacts that consumers would silently degrade on or ignore.

### 3.7 v0 exists as both runtime compatibility output and a public/documented legacy contract

Evidence:

- AI snapshot writes the v0 JSON sidecar (`arena/project_decomposer_ai.py:149-150`), stores its hash (`arena/project_decomposer_ai.py:151-156`), and records its manifest path/hash (`arena/project_decomposer_ai.py:221-225`).
- v1 includes `compatibility.projectModelV0Path` and states v0 is a legacy compatibility projection (`arena/project_model_v1.py:90-93`).
- Legacy CLI still supports `--format project-model-v0` (`arena/decomposer.py:838-858`, `arena/decomposer.py:870-880`).
- Documentation describes downstream repos still consuming explicit v0 (`README.md:72-74`, `docs/project-model-v0.md:45-56`).

Conclusion: v0 is not a dead file. It is a compatibility surface backed by code, tests, schema/examples, and docs.

## 4. Required model contract derived from consumers

The needed model is the union of what immediate consumers actually read. Status values below mean:

- Delivered: the current v1 artifact or snapshot bundle writes the field and current consumers can read it.
- Partial: the field exists, but its semantics are heuristic, optional in schema despite load-bearing use, or not independently proven.
- Missing: a consumer needs it but the current v1 artifact/bundle does not supply it. No required downstream field was found to be fully missing; the main failures are partial contract/semantic guarantees.

| Consumer | Fields read | Evidence | Status |
|---|---|---|---|
| `project_model_gate` | Manifest `snapshot_path`, `graph_path`; snapshot `schema_version`, `goal`, `non_goals`, `components`, `contracts`, `cross_cutting_concerns`, `observable_checks`, `verification_gaps`, `near_neighbor_alternatives`, `held_out_probes`, `acceptance_command_allowlist`; graph `nodes`, `edges`, provenance refs | `arena/project_model_gate.py:251-257`, `arena/project_model_gate.py:28-224` | Delivered in bundle. Partial as v1 schema does not validate the manifest bundle shape. |
| `project_model_freshness` | v1 `schemaVersion`, `id`, `provenance.git.headOid`, `provenance.git.dirty`, `snapshot.graph_hash`, `projectGraph.graphHash` | `arena/project_model_freshness.py:58-68`, `arena/project_model_freshness.py:249-276` | Delivered. |
| `capability_lift` | v1 `snapshot.components`, `iterationReadiness.componentProfiles`, `projectGraph.nodes`, `projectGraph.graphHash`, `project.projectId` or `snapshot.project_id` | `arena/capability_lift.py:49-58`, `arena/capability_lift.py:63-90`, `arena/capability_lift.py:97-118`, `arena/capability_lift.py:134-162`, `arena/capability_lift.py:182-198` | Delivered. Partial because `responsibilitySummary` exists but is heuristic; `iterationReadiness` is not top-level-required by v1 schema. |
| `project_intake_scorecard` | v1 `id`, `provenance.git.headOid`, `iterationReadiness.componentProfiles`, `snapshot.components`, `projectGraph.nodes`, `snapshot.observable_checks`, `iterationReadiness.qualityGates`, `iterationReadiness.openQuestions`, `snapshot.verification_gaps` | `arena/project_intake_scorecard.py:127-165`, `arena/project_intake_scorecard.py:312-381`, `arena/project_intake_scorecard.py:384-407`, `arena/project_intake_scorecard.py:796-839`, `arena/project_intake_scorecard.py:842-867` | Delivered. Partial for same `iterationReadiness` schema gap and heuristic risk/responsibility semantics. |
| `proposal_planner` | Scorecard `snapshotPath`; then v1 `iterationReadiness.openQuestions` and `snapshot.verification_gaps`; uses fresh current graph slice instead of cached v1 graph | `arena/proposal_planner.py:264-290`, `arena/proposal_planner.py:293-315` | Delivered. Partial because missing/invalid `snapshotPath` silently returns empty context (`arena/proposal_planner.py:293-303`). |
| `proposal_pairwise_reranker` | `projectGraph.nodes` when a v1 artifact is passed as `--graph`; graph paths, symbols, node ids, provenance ids | `arena/proposal_pairwise_reranker.py:248-254`, `arena/proposal_pairwise_reranker.py:90-115` | Delivered. |
| `proposal_run` | Snapshot manifest `project_model_primary_path` or `project_model_v1_path`, then v1 path into intake/planner/reranker | `arena/proposal_run.py:178-193`, `arena/proposal_run.py:216-299` | Delivered. Runtime does not read v0; test fixtures still mention v0. |
| `repo_goal_loop` | Programmatic build result, gate report, v1 JSON artifact path, scorecard, ranked proposals, proposal plan | `arena/repo_goal_loop.py:313-391` | Delivered. Runtime does not read v0. |
| `dream_generate` | v1 `project.projectId` or `snapshot.project_id`, `projectGraph.graphHash`, `iterationReadiness.componentProfiles`, `snapshot.near_neighbor_alternatives` | `arena/dream_generate.py:182-195`, `arena/dream_generate.py:216-229` | Delivered. Partial because this is advisory/LLM generation and not a deterministic consumer. |
| `dream_research` | v1 `project.projectId` or `snapshot.project_id`, `projectGraph.graphHash`, `snapshot.components`, `snapshot.contracts`, `snapshot.verification_gaps`, `snapshot.near_neighbor_alternatives`, `projectGraph.nodes`, `projectGraph.edges` | `arena/dream_research.py:187-203`, `arena/dream_research.py:234-248` | Delivered. Partial because the research stage is live/injected model output (`arena/dream_research.py:50-79`). |
| `dream_gate` | v1 `projectGraph.graphHash`, `projectGraph.nodes`, `projectGraph.edges`, `snapshot.components`, `snapshot.contracts`, `snapshot.verification_gaps`, `snapshot.near_neighbor_alternatives` | `arena/dream_gate.py:73-83`, `arena/dream_gate.py:281-292`, `arena/dream_gate.py:350-354` | Delivered. |

Required union for a v0-free v1 contract:

- Top-level: `schemaVersion`, `id`, `project`, `snapshot`, `projectGraph`, `gateReport`, `provenance`, `hashes`, `models`, `derivedArtifacts`, `iterationReadiness`.
- `project`: `projectId`, `projectRoot`, `goal`, `nonGoals`.
- `snapshot`: `project_id`, `project_root`, `goal`, `non_goals`, `primary_model_id`, `graph_hash`, `schema_version`, `snapshot_id`, `components`, `contracts`, `cross_cutting_concerns`, `observable_checks`, `held_out_probes`, `verification_gaps`, `near_neighbor_alternatives`, `acceptance_command_allowlist`, `prompt_hashes`, `model_output_hashes`, `input_hashes`.
- `snapshot.components[]`: `id`, `name`, `responsibility`, `owned_node_ids`, `provenance_refs`, `contract_ids`, `check_ids`, `verification_gap_ids`.
- `snapshot.contracts[]`: `id`, `name`, `from_component_id`, `to_component_id`, `supporting_edge_ids`, `near_neighbor_alternative_ids`, `provenance_refs`.
- `snapshot.observable_checks[]`: `id`, `description`, `command`, `component_ids`, `contract_ids`, `provenance_refs`, `acceptance_command_id`, `safe_to_run_by_default`, `requires_network`, `requires_paid_api`, `execution_dir`, `safety_status`, `execution_status`, `proof_artifact`, `verification_gap_ids`.
- `projectGraph`: `schemaVersion`, `graphHash`, `projectRoot`, `nodes[]`, `edges[]`; nodes need at least `id`, `kind`, `label`, `path`, `symbol`, `tags`, `provenance_refs`; edges need at least `id`, `kind`, `from_node_id`, `to_node_id`, `label`, `provenance_refs`, `confidence`, `derived_by`.
- `iterationReadiness`: `summary`, `componentProfiles`, `runtimeContracts`, `externalSurfaces`, `productInvariants`, `qualityGates`, `priorityBacklog`, `openQuestions`.
- `iterationReadiness.componentProfiles[]`: `componentId`, `ownedNodeIds`, `responsibilitySummary`, `keySymbols`, `behavioralTags`, `riskLevel`, `priorityRank`, `whyPriority`, `provenanceRefs`.
- `provenance.git`: `available`, `root`, `headOid`, `dirty`, `dirtyPaths`, `dirtyStateFingerprint`.

No current immediate runtime consumer was found reading `project-model/v0` directly. The v0-dependent surfaces are compatibility writers, legacy CLI, docs/schema/examples, and tests.

## 5. The v0 question

### 5.1 Empirical v0 reference inventory

`git grep -l -E 'project-model/v0|project-model-v0|ProjectModelV0|project_model_v0|PROJECT_MODEL_V0|format.*project-model-v0|--format.*project-model-v0' -- . ':!docs/verification' ':!arena/generated' | sort` returned:

```text
AGENTS.md
arena/decomposer.py
arena/project_decomposer_ai.py
arena/project_model_v0.py
arena/project_model_v1.py
docs/build-arena-project-brief.md
docs/examples/project-model-v0-code-adjacent.json
docs/examples/project-model-v0-process-strategy.json
docs/plans/2026-06-01-project-decomposer.md
docs/plans/2026-06-04-ai-first-project-decomposer-implementation-plan.md
docs/plans/2026-06-05-build-arena-doc-artifact-alignment-plan.md
docs/plans/2026-06-05-project-model-v1-and-pre-live-readiness-plan.md
docs/playbooks/2026-06-03-f3-project-model-mentor-runbook.md
docs/project-model-v0.md
docs/prompts/2026-06-05-build-arena-doc-artifact-alignment-implementation-prompt.md
docs/prompts/2026-06-05-grok-live-rca-project-model-v1-pre-live-readiness.md
docs/research/2026-06-03-ai-first-project-decomposition-pipeline.md
docs/schemas/project-model-v0.schema.json
docs/specs/2026-06-04-ai-first-project-decomposer-spec.md
docs/specs/2026-06-05-project-model-v1-shared-contract-spec.md
proposal-run-and-emit.patch
README.md
reports/2026-06-23-dream-proposer-tier3-review-packet.md
tests/test_coverage_closure.py
tests/test_project_decomposer_ai.py
tests/test_project_decomposer.py
tests/test_project_model_v0_contract.py
tests/test_project_model_v1_contract.py
tests/test_project_status_docs.py
tests/test_proposal_run.py
```

Runtime v0 writers/readers:

- `arena/decomposer.py` imports v0 classes and gate helpers (`arena/decomposer.py:17-40`), builds Project Model v0 (`arena/decomposer.py:223-246`, `arena/decomposer.py:249-392`), validates/canonicalizes it (`arena/decomposer.py:395-400`), and exposes the legacy CLI format (`arena/decomposer.py:838-912`). This is both writer and validator.
- `arena/project_decomposer_ai.py` writes the v0 JSON sidecar from the AI snapshot (`arena/project_decomposer_ai.py:149-150`) and implements the projection (`arena/project_decomposer_ai.py:459-560`). This is a writer.
- `arena/project_model_v0.py` defines the v0 schema and quality gate (`arena/project_model_v0.py:8`, `arena/project_model_v0.py:190-207`, `arena/project_model_v0.py:222-437`). This is a reader/validator.
- `arena/project_model_v1.py` does not read v0 content; it carries the compatibility path and role (`arena/project_model_v1.py:25`, `arena/project_model_v1.py:90-93`).

Runtime non-readers confirmed by grep:

- `git grep` found no v0 references in `arena/proposal_planner.py`, `arena/capability_lift.py`, `arena/proposal_run.py`, `arena/project_model_freshness.py`, `arena/project_model_gate.py`, `arena/repo_goal_loop.py`, or `arena/dream_research.py`.
- These consumers read v1/snapshot/graph fields as shown in section 4.
- Writer/helper surfaces such as `arena/onboard.py`, `arena/proposer_handoff.py`, and `arena/project_encyclopedia.py` were not counted as immediate project-model consumers because the reviewed code either creates/imports adjacent artifacts or prepares downstream handoff data without reading `project-model/v0` as the runtime contract.

Web/status surface:

- There is no runtime web server consumer in the Python inventory that reads `project-model/v0`; the only web-adjacent match in the runtime grep was generated dashboard normalization (`scripts/normalize_generated_artifacts.py:6-9`), not project-model loading.
- Status/doc tests keep v0 visible in operator-facing surfaces: `tests/test_project_status_docs.py:137-155` requires README markers including the v0 JSON sidecar name, and `tests/test_project_status_docs.py:189-206` and `tests/test_project_status_docs.py:233-252` require `AGENTS.md` and `docs/build-arena-project-brief.md` to mention that same v0 sidecar alongside v1/current-readiness language.

Tests and docs that will break if v0 is removed without migration:

- `tests/test_project_decomposer.py` imports and asserts v0 CLI/API behavior (`tests/test_project_decomposer.py:24-32`, `tests/test_project_decomposer.py:89-119`, `tests/test_project_decomposer.py:472-505`, `tests/test_project_decomposer.py:524-576`).
- `tests/test_project_model_v0_contract.py` validates the schema/examples and strict Pydantic model (`tests/test_project_model_v0_contract.py:11-17`, `tests/test_project_model_v0_contract.py:150-202`).
- `tests/test_project_decomposer_ai.py` asserts the v0 JSON sidecar exists and has `schemaVersion: project-model/v0` (`tests/test_project_decomposer_ai.py:66-79`).
- `tests/test_project_model_v1_contract.py` asserts the manifest's v0 path and v1 compatibility path (`tests/test_project_model_v1_contract.py:35-53`).
- `tests/test_coverage_closure.py` imports v0 gate helpers and tests v0 CLI behavior (`tests/test_coverage_closure.py:47-48`, `tests/test_coverage_closure.py:755-903`, `tests/test_coverage_closure.py:1065-1086`).
- `tests/test_project_status_docs.py` asserts docs mention v0 and CLI help includes `project-model-v0` (`tests/test_project_status_docs.py:142-144`, `tests/test_project_status_docs.py:194-196`, `tests/test_project_status_docs.py:240-242`, `tests/test_project_status_docs.py:456-458`).
- `tests/test_proposal_run.py` has a manifest fixture containing `project_model_v0_path` (`tests/test_proposal_run.py:145-146`).
- Docs and examples listed in the grep output present v0 as active compatibility contract, especially `README.md:72-74` and `docs/project-model-v0.md:45-56`.

### 5.2 Relationship between v0 and v1

The v1 artifact does not wrap the v0 JSON content. Both are produced from the same snapshot bundle:

- `arena/project_decomposer_ai.py:149-150` first writes a deterministic v0 projection.
- `arena/project_decomposer_ai.py:158-165` then builds v1 from `snapshot`, `graph`, `gate_report`, and artifact hashes, with `compatibility_v0_path` set to the current v0 sidecar filename.
- `arena/project_model_v1.py:58-93` embeds the full snapshot, graph, gate report, provenance, hashes, models, iteration readiness, and only a v0 path/role.

Therefore:

- v0 duplicates/compresses part of the snapshot into the old `components`, `dependencies`, `invariants`, `observableChecks`, `verificationGaps`, and related fields.
- v1 extends beyond v0 by embedding graph, gate report, git provenance, hashes, model ids, derived artifacts, and iteration readiness.
- v1 references v0 as a compatibility sidecar; it does not depend on v0 content for its own construction except for recording the path.

### 5.3 Staged, reversible removal/migration plan

No code should be deleted first. The safe order is:

1. Harden v1 as the contract consumers already require.
   - Concrete mechanism: make `iterationReadiness` top-level required in `docs/schemas/project-model-v1.schema.json`, because `arena/project_model_v1.py:89` emits it and downstream consumers read it (`arena/capability_lift.py:55-58`, `arena/project_intake_scorecard.py:321-323`, `arena/proposal_planner.py:286-301`, `arena/dream_generate.py:182-188`).
   - What breaks if skipped: a schema-valid v1 artifact may omit `iterationReadiness`, causing capability/intake/proposal/dream consumers to silently degrade.
   - Reversible: schema-only tightening can be reverted independently.

2. Remove runtime consumers' reliance on manifest v0 fields by proving they already use v1.
   - Concrete mechanism: keep `arena/proposal_run.py:178-193` and `arena/dream_run.py:155-166` pointed at `project_model_primary_path` / `project_model_v1_path`; keep `arena/repo_goal_loop.py:376-391` pointed at the v1 JSON artifact; add/adjust tests so fixtures omit `project_model_v0_path` and still pass.
   - What breaks if done out of order: if tests still require `project_model_v0_path`, CI fails even though runtime consumers do not use v0.
   - Reversible: restore fixture field while leaving runtime unchanged.

3. Make AI-snapshot v0 emission optional, default-on for one compatibility step.
   - Concrete mechanism: add an `emit_compatibility_v0: bool = True` parameter to `build_project_model_snapshot(...)` near `arena/project_decomposer_ai.py:66-85`; guard `arena/project_decomposer_ai.py:149-156` so the v0 JSON sidecar and `artifact_hashes["project_model_v0"]` are written only when the flag is true; first widen `project_model_v1_from_snapshot(...)` and the v1 schema if `compatibility.projectModelV0Path` may be absent, then omit or explicitly mark the compatibility block inactive instead of passing an untyped `None` through the current `str` parameter at `arena/project_model_v1.py:19-25`; guard manifest keys at `arena/project_decomposer_ai.py:221-225` the same way.
   - What breaks if done out of order: `tests/test_project_decomposer_ai.py:66-79` and `tests/test_project_model_v1_contract.py:35-53` fail if the default behavior changes before tests/docs are migrated.
   - Reversible: set the flag default back to true and restore manifest compatibility keys.

4. Migrate docs and tests from "v0 is emitted" to "v0 is optional legacy output".
   - Concrete mechanism: update `README.md:40`, `README.md:72-74`, `AGENTS.md:40`, `docs/build-arena-project-brief.md:34`, `docs/project-model-v0.md:45-56`, and `tests/test_project_status_docs.py:142-144`, `tests/test_project_status_docs.py:194-196`, `tests/test_project_status_docs.py:240-242`, `tests/test_project_status_docs.py:456-458`.
   - What breaks if done out of order: documentation/status tests keep enforcing v0 as active output and block removal.
   - Reversible: docs/tests can be reverted without touching runtime.

5. Decide whether the legacy scanner CLI is frozen public surface.
   - Concrete mechanism if kept: leave `arena/decomposer.py:838-912`, `arena/project_model_v0.py`, `docs/schemas/project-model-v0.schema.json`, and v0 contract tests in place, but classify them as legacy scanner compatibility outside the primary AI decomposer.
   - Concrete mechanism if removed: remove `--format project-model-v0` from `arena/decomposer.py:843-848`, remove the v0 argument validation and branch at `arena/decomposer.py:860-881`, remove imports at `arena/decomposer.py:17-40`, remove `arena/project_model_v0.py`, and delete/migrate tests listed in section 5.1.
   - What breaks if done out of order: deleting `arena/project_model_v0.py` first breaks imports in `arena/decomposer.py:17-40` and tests; removing the CLI before docs/tests migration breaks CLI/status tests and documented commands.
   - Reversible: keep a branch/commit boundary before this stage; this is the first materially breaking step.

6. Stop AI-snapshot v0 emission by default.
   - Concrete mechanism: change the optional flag from stage 3 to default false or remove it, then remove v0 write/manifest/hash code at `arena/project_decomposer_ai.py:149-156` and `arena/project_decomposer_ai.py:221-225` after tests no longer expect it.
   - What breaks if done out of order: v1 compatibility tests and docs expecting the v0 JSON sidecar fail.
   - Reversible: restore the guarded emission block.

7. Delete v0 only after grep is clean.
   - Concrete mechanism: require `git grep -n -E 'project-model/v0|project-model-v0|ProjectModelV0|project_model_v0|PROJECT_MODEL_V0|format.*project-model-v0|--format.*project-model-v0' -- . ':!docs/verification' ':!arena/generated'` to return only intentionally archived historical docs, or return no runtime/test references if full deletion is chosen.
   - Deletion point: only after runtime, tests, active docs, examples, schemas, and status-doc assertions no longer reference v0 as an active contract.

Current deletion verdict:

- `project-model/v0` cannot be safely deleted now. It is still written by the primary snapshot pipeline (`arena/project_decomposer_ai.py:149-150`), exposed by the legacy CLI (`arena/decomposer.py:838-912`), defined and gated by `arena/project_model_v0.py:190-437`, recorded in v1 compatibility (`arena/project_model_v1.py:90-93`), asserted by tests, and documented as an active compatibility target.
- The immediate downstream runtime proposal/dream/freshness/capability consumers do not require v0. The blocker is the compatibility surface itself plus docs/tests, not current proposal-loop runtime logic.

## Source references

Primary source files for this audit include [arena/project_decomposer_ai.py](../../arena/project_decomposer_ai.py), [arena/project_model_v1.py](../../arena/project_model_v1.py), [arena/project_model_v0.py](../../arena/project_model_v0.py), [arena/decomposer.py](../../arena/decomposer.py), [arena/project_model_gate.py](../../arena/project_model_gate.py), [arena/project_iteration_readiness.py](../../arena/project_iteration_readiness.py), and [docs/schemas/project-model-v1.schema.json](../schemas/project-model-v1.schema.json).

## 6. Verified vs inferred

Verified from code and command output:

- Primary snapshot CLI modes and live guards: `arena/project_model_cli.py:23-40`, `arena/project_model_cli.py:66-72`.
- Primary build stages and artifact writes: `arena/project_decomposer_ai.py:66-244`.
- Graph contract and graph builder: `arena/project_graph.py:43-96`, `arena/project_graph.py:1244-1317`.
- Model-output mode behavior: `arena/project_decomposer_ai.py:93-111`, `arena/project_model_llm.py:30-31`, `arena/project_model_llm.py:54-92`, `arena/project_model_llm.py:115-144`.
- Snapshot and v1 contracts: `arena/project_snapshot.py:102-124`, `arena/project_model_v1.py:49-94`.
- Gate behavior: `arena/project_model_gate.py:28-224`, `arena/project_model_gate.py:336-410`, `arena/project_model_gate.py:704-755`.
- Iteration-readiness fields and responsibility-summary heuristics: `arena/project_iteration_readiness.py:24-44`, `arena/project_iteration_readiness.py:82-105`, `arena/project_iteration_readiness.py:238-267`, `arena/project_iteration_readiness.py:401-590`.
- Downstream fields read by capability lift, freshness, intake, planner, proposal run, repo goal loop, dream generation/research/gate, and reranker: section 4 citations.
- v0 reference inventory: `git grep -l ...` output in section 5.1.
- Fixture/off reproduction on `/tmp/decomposer-audit.hIuO9O/repo`: command output recorded in section 3.

Inferred from code structure:

- v1 is the practical current downstream runtime contract because proposal/dream/freshness/capability/runtime consumers read v1/snapshot/graph paths and grep found no v0 references in those runtime consumers.
- v0 exists mainly for compatibility and the legacy scanner/public docs/tests, not because proposal-loop runtime currently reads it.
- Removing v0 is a migration/release decision, not a local delete, because the legacy CLI and docs present it as an active supported contract.

Open decisions:

1. Is `python -m arena.decomposer --format project-model-v0` a frozen public CLI that must remain for a compatibility window, or may it be removed in the next breaking change?
2. Should v1 schema be tightened so `iterationReadiness` is required before any v0 removal work starts?
3. Should historical v0 docs/examples be archived, retained as legacy references, or deleted after migration?
4. Should advisory dream-lane fields be included in the required v1 contract, or should they remain outside the core proposal-loop contract?
5. Should fixture mode be described in docs as deterministic heuristic analysis instead of a model fixture to avoid implying canned replay or LLM semantics?

Readiness statement: the decomposition definition is complete enough to hand off a v1-contract-hardening and v0-deprecation build, but full v0 deletion is blocked until the legacy CLI/docs/tests compatibility decision is made and migrated.
