# Final Opus rereview input: AI-first project decomposer repaired evidence

Read-only adversarial review. The prior critical blocker was that probe controls all used generic endpoint reversal. This packet is current after pattern-specific negative repair. Return PASS / PASS_WITH_NONCRITICAL_GAPS / FAIL_WITH_CRITICAL_BLOCKERS.

## Gate repairs since prior FAIL
- protected/generated provenance claims on components now fail.
- responsibility text path/file buckets now fail.
- owned concrete import component pairs require a contract.
- anti_fabrication and provenance concerns must cover every component.
- contracts cannot be self-referential.
- concern component/contract references must resolve.
- regression tests added in tests/test_project_snapshot_gate.py.

## Build Arena
- snapshot_dir: /home/leonb/projects/build-arena/docs/verification/2026-06-04-ai-first-project-decomposer-pilot-build-arena/snapshot-4cb7261dd9905984
- gate passed: True; violations: []
- graph nodes/edges: 4674/5031
- components/contracts/checks/gaps/probes: 8/10/6/21/6
- probe controls: count=6; all_golden_passed=True; all_planted_negatives_failed=True; all_expected_gates_observed=True
- distinct negative violation gates: ['component_measurability', 'contract_references', 'cross_cutting_concerns', 'edge_coverage', 'protected_surfaces']
- strong negative failed as expected: True; gates=['contract_references', 'contract_references', 'contract_references', 'contract_references', 'contract_references', 'edge_coverage', 'edge_coverage', 'cross_cutting_concerns', 'cross_cutting_concerns', 'component_measurability', 'component_measurability']

### Probe results
- probe:encyclopedia_enriches_not_constructs / neg:encyclopedia_owns_graph_construction
  - actual_mutation: merged/deleted comp:project_graph into encyclopedia
  - golden_passed: True
  - negative_passed: False
  - expected_violation_gates: ['contract_references', 'cross_cutting_concerns']
  - negative_violation_gates: ['contract_references', 'contract_references', 'contract_references', 'contract_references', 'edge_coverage', 'edge_coverage', 'cross_cutting_concerns', 'cross_cutting_concerns', 'component_measurability', 'component_measurability']
  - expected_gate_observed: True
  - negative_command_artifact: /home/leonb/projects/build-arena/docs/verification/2026-06-04-ai-first-project-decomposer-pilot-build-arena/probe-controls-current/probe_encyclopedia_enriches_not_constructs/planted-negative-command.json
- probe:decomposer_must_submit_to_gate / neg:decomposer_bypasses_gate
  - actual_mutation: removed con:decomposer_uses_gate
  - golden_passed: True
  - negative_passed: False
  - expected_violation_gates: ['edge_coverage']
  - negative_violation_gates: ['edge_coverage']
  - expected_gate_observed: True
  - negative_command_artifact: /home/leonb/projects/build-arena/docs/verification/2026-06-04-ai-first-project-decomposer-pilot-build-arena/probe-controls-current/probe_decomposer_must_submit_to_gate/planted-negative-command.json
- probe:cli_wires_both_graph_and_gate / neg:cli_omits_graph_contract
  - actual_mutation: removed con:cli_uses_graph
  - golden_passed: True
  - negative_passed: False
  - expected_violation_gates: ['edge_coverage']
  - negative_violation_gates: ['edge_coverage']
  - expected_gate_observed: True
  - negative_command_artifact: /home/leonb/projects/build-arena/docs/verification/2026-06-04-ai-first-project-decomposer-pilot-build-arena/probe-controls-current/probe_cli_wires_both_graph_and_gate/planted-negative-command.json
- probe:generated_surfaces_not_owned / neg:hypothesis_engine_owns_generated_schema
  - actual_mutation: added generated surface ownership to hypothesis engine
  - golden_passed: True
  - negative_passed: False
  - expected_violation_gates: ['protected_surfaces']
  - negative_violation_gates: ['protected_surfaces']
  - expected_gate_observed: True
  - negative_command_artifact: /home/leonb/projects/build-arena/docs/verification/2026-06-04-ai-first-project-decomposer-pilot-build-arena/probe-controls-current/probe_generated_surfaces_not_owned/planted-negative-command.json
- probe:no_file_bucket_components / neg:file_bucket_component
  - actual_mutation: path/file-bucket responsibility
  - golden_passed: True
  - negative_passed: False
  - expected_violation_gates: ['component_measurability']
  - negative_violation_gates: ['component_measurability']
  - expected_gate_observed: True
  - negative_command_artifact: /home/leonb/projects/build-arena/docs/verification/2026-06-04-ai-first-project-decomposer-pilot-build-arena/probe-controls-current/probe_no_file_bucket_components/planted-negative-command.json
- probe:protected_surfaces_unowned / neg:component_owns_protected_surface
  - actual_mutation: added protected provenance to arena loop
  - golden_passed: True
  - negative_passed: False
  - expected_violation_gates: ['protected_surfaces']
  - negative_violation_gates: ['protected_surfaces']
  - expected_gate_observed: True
  - negative_command_artifact: /home/leonb/projects/build-arena/docs/verification/2026-06-04-ai-first-project-decomposer-pilot-build-arena/probe-controls-current/probe_protected_surfaces_unowned/planted-negative-command.json

## FMC-MCP
- snapshot_dir: /home/leonb/projects/build-arena/docs/verification/2026-06-04-ai-first-project-decomposer-pilot-fmc-mpc/snapshot-e43d7b1e7cfe791f
- gate passed: True; violations: []
- graph nodes/edges: 175/209
- components/contracts/checks/gaps/probes: 5/5/3/4/3
- probe controls: count=3; all_golden_passed=True; all_planted_negatives_failed=True; all_expected_gates_observed=True
- distinct negative violation gates: ['component_measurability', 'contract_references', 'cross_cutting_concerns', 'edge_coverage', 'inventory_coverage']
- strong negative failed as expected: True; gates=['contract_references', 'contract_references', 'contract_references', 'edge_coverage', 'edge_coverage', 'cross_cutting_concerns', 'cross_cutting_concerns', 'cross_cutting_concerns', 'cross_cutting_concerns', 'component_measurability', 'contract_references', 'component_measurability', 'contract_references']

### Probe results
- probe-resources-no-mcp-surface / neg-tools-resources-merge
  - actual_mutation: merged tools/resources and removed contract
  - golden_passed: True
  - negative_passed: False
  - expected_violation_gates: ['contract_references', 'cross_cutting_concerns']
  - negative_violation_gates: ['contract_references', 'edge_coverage', 'cross_cutting_concerns', 'cross_cutting_concerns', 'cross_cutting_concerns', 'cross_cutting_concerns', 'component_measurability', 'contract_references', 'component_measurability', 'contract_references']
  - expected_gate_observed: True
  - negative_command_artifact: /home/leonb/projects/build-arena/docs/verification/2026-06-04-ai-first-project-decomposer-pilot-fmc-mpc/probe-controls-current/probe-resources-no-mcp-surface/planted-negative-command.json
- probe-client-unified-auth-transport / neg-client-split
  - actual_mutation: fabricated client split
  - golden_passed: True
  - negative_passed: False
  - expected_violation_gates: ['inventory_coverage', 'contract_references', 'cross_cutting_concerns']
  - negative_violation_gates: ['inventory_coverage', 'inventory_coverage', 'contract_references', 'contract_references', 'contract_references', 'contract_references', 'cross_cutting_concerns', 'cross_cutting_concerns', 'cross_cutting_concerns', 'cross_cutting_concerns', 'cross_cutting_concerns', 'cross_cutting_concerns', 'component_measurability', 'component_measurability']
  - expected_gate_observed: True
  - negative_command_artifact: /home/leonb/projects/build-arena/docs/verification/2026-06-04-ai-first-project-decomposer-pilot-fmc-mpc/probe-controls-current/probe-client-unified-auth-transport/planted-negative-command.json
- probe-no-fabricated-components / neg-fabricated-audit-log
  - actual_mutation: fabricated audit component and edge
  - golden_passed: True
  - negative_passed: False
  - expected_violation_gates: ['inventory_coverage', 'contract_references', 'cross_cutting_concerns']
  - negative_violation_gates: ['inventory_coverage', 'contract_references', 'cross_cutting_concerns', 'cross_cutting_concerns']
  - expected_gate_observed: True
  - negative_command_artifact: /home/leonb/projects/build-arena/docs/verification/2026-06-04-ai-first-project-decomposer-pilot-fmc-mpc/probe-controls-current/probe-no-fabricated-components/planted-negative-command.json

## Held-out leonbreukelman-engineer
- snapshot_dir: /home/leonb/projects/build-arena/docs/verification/2026-06-04-ai-first-project-decomposer-pilot-held-out/snapshot-6a7e077842d60d81
- gate passed: True; violations: []
- graph nodes/edges: 116/130
- components/contracts/checks/gaps/probes: 7/1/3/8/4
- probe controls: count=4; all_golden_passed=True; all_planted_negatives_failed=True; all_expected_gates_observed=True
- distinct negative violation gates: ['component_measurability', 'contract_references', 'cross_cutting_concerns', 'edge_coverage', 'protected_surfaces']
- strong negative failed as expected: True; gates=['contract_references', 'edge_coverage']

### Probe results
- probe:worker-mcp-distinct-endpoints / neg:merge-worker-mcp-into-one-component
  - actual_mutation: self-referential router-to-mcp contract
  - golden_passed: True
  - negative_passed: False
  - expected_violation_gates: ['contract_references']
  - negative_violation_gates: ['contract_references', 'edge_coverage']
  - expected_gate_observed: True
  - negative_command_artifact: /home/leonb/projects/build-arena/docs/verification/2026-06-04-ai-first-project-decomposer-pilot-held-out/probe-controls-current/probe_worker-mcp-distinct-endpoints/planted-negative-command.json
- probe:persona-corpus-distinct-from-machine-data / neg:persona-corpus-merged-into-public-data
  - actual_mutation: merged persona corpus into public data and deleted component
  - golden_passed: True
  - negative_passed: False
  - expected_violation_gates: ['cross_cutting_concerns', 'component_measurability']
  - negative_violation_gates: ['component_measurability', 'cross_cutting_concerns', 'cross_cutting_concerns', 'component_measurability']
  - expected_gate_observed: True
  - negative_command_artifact: /home/leonb/projects/build-arena/docs/verification/2026-06-04-ai-first-project-decomposer-pilot-held-out/probe-controls-current/probe_persona-corpus-distinct-from-machine-data/planted-negative-command.json
- probe:build-pipeline-source-only-no-dist / neg:dist-output-as-owned-source
  - actual_mutation: added generated dist surface to build-pipeline ownership
  - golden_passed: True
  - negative_passed: False
  - expected_violation_gates: ['protected_surfaces']
  - negative_violation_gates: ['protected_surfaces']
  - expected_gate_observed: True
  - negative_command_artifact: /home/leonb/projects/build-arena/docs/verification/2026-06-04-ai-first-project-decomposer-pilot-held-out/probe-controls-current/probe_build-pipeline-source-only-no-dist/planted-negative-command.json
- probe:anti-fabrication-concern-is-universal / neg:drop-anti-fabrication-concern
  - actual_mutation: removed anti_fabrication concern
  - golden_passed: True
  - negative_passed: False
  - expected_violation_gates: ['cross_cutting_concerns']
  - negative_violation_gates: ['cross_cutting_concerns', 'cross_cutting_concerns']
  - expected_gate_observed: True
  - negative_command_artifact: /home/leonb/projects/build-arena/docs/verification/2026-06-04-ai-first-project-decomposer-pilot-held-out/probe-controls-current/probe_anti-fabrication-concern-is-universal/planted-negative-command.json

## Verification commands just run
- uv run pytest tests -q: pass
- uv run ruff check . && uv run pyright: pass
- /home/leonb/projects/fmc-mcp: uv run python -m pytest -q: 19 passed
- /home/leonb/projects/leonbreukelman-engineer: npm run build && npm run check:links: pass
- git diff --check: pass
- pilot JSON validation: 2898 JSON files parsed
