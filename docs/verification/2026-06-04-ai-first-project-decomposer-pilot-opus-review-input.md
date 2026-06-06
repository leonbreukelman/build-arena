# AI-first Project Decomposer Pilot Review Packet

Review mode: read-only. Attack whether these pilots prove the decomposer works beyond path classifiers/report generation.

## Pilot: 2026-06-04-ai-first-project-decomposer-pilot-build-arena

### repo-state.json

```text
{
  "branch": {
    "command": "git branch --show-current",
    "cwd": "/home/leonb/projects/build-arena",
    "returncode": 0,
    "stderr": "",
    "stdout": "coverage-100\n"
  },
  "git_toplevel": {
    "command": "git rev-parse --show-toplevel",
    "cwd": "/home/leonb/projects/build-arena",
    "returncode": 0,
    "stderr": "",
    "stdout": "/home/leonb/projects/build-arena\n"
  },
  "pwd": {
    "command": "pwd",
    "cwd": "/home/leonb/projects/build-arena",
    "returncode": 0,
    "stderr": "",
    "stdout": "/home/leonb/projects/build-arena\n"
  },
  "repo": "/home/leonb/projects/build-arena",
  "selection_note": "Required pilot 1: Build Arena itself.",
  "status_short": {
    "command": "git status --short",
    "cwd": "/home/leonb/projects/build-arena",
    "returncode": 0,
    "stderr": "",
    "stdout": "?? arena/project_decomposer_ai.py\n?? arena/project_encyclopedia.py\n?? arena/project_graph.py\n?? arena/project_model_cli.py\n?? arena/project_model_gate.py\n?? arena/project_model_llm.py\n?? arena/project_snapshot.py\n?? docs/build-arena-constitution.md\n?? docs/build-arena-current-state.md\n?? docs/build-arena-project-brief.md\n?? docs/build-arena-specification.md\n?? docs/plans/2026-06-04-ai-first-project-decomposer-implementation-plan.md\n?? docs/playbooks/\n?? docs/research/\n?? docs/specs/\n?? docs/verification/2026-06-01-arena-calibration-decomposer-evaluation-report.md\n?? docs/verification/2026-06-01-arena-calibration-decomposer-local-evaluation.json\n?? docs/verification/2026-06-01-arena-calibration-decomposer-model.json\n?? docs/verification/2026-06-01-arena-calibration-model-review-prompt-distilled.md\n?? docs/verification/2026-06-01-arena-calibration-model-review-prompt-grok.md\n?? docs/verification/2026-06-01-arena-calibration-model-review-prompt.md\n?? docs/verification/2026-06-01-grok-build-arena-calibration-model-review.md\n?? docs/verification/2026-06-01-grok-build-arena-calibration-model-review.stderr\n?? docs/verification/2026-06-01-opus-arena-calibration-model-review.json\n?? docs/verification/2026-06-01-opus-arena-calibration-model-review.md\n?? docs/verification/2026-06-03-issue-3-project-model-v0-emit/\n?? docs/verification/2026-06-03-opus-f3-project-model-mentor-runbook-rereview-prompt.md\n?? docs/verification/2026-06-03-opus-f3-project-model-mentor-runbook-rereview.json\n?? docs/verification/2026-06-03-opus-f3-project-model-mentor-runbook-rereview.md\n?? docs/verification/2026-06-03-opus-f3-project-model-mentor-runbook-rereview.stderr.txt\n?? docs/verification/2026-06-03-opus-f3-project-model-mentor-runbook-review-prompt.md\n?? docs/verification/2026-06-03-opus-f3-project-model-mentor-runbook-review.json\n?? docs/verification/2026-06-03-opus-f3-project-model-mentor-runbook-review.md\n?? docs/verification/2026-06-03-opus-f3-project-model-mentor-runbook-review.stderr.txt\n?? docs/verification/2026-06-04-ai-first-project-decomposer-pilot-build-arena/\n?? docs/verification/2026-06-04-ai-first-project-decomposer-pilot-fmc-mpc/\n?? docs/verification/2026-06-04-ai-first-project-decomposer-plan-opus-review.json\n?? docs/verification/2026-06-04-ai-first-project-decomposer-plan-opus-review.md\n?? docs/verification/2026-06-04-ai-first-project-decomposer-spec-opus-review.json\n?? docs/verification/2026-06-04-ai-first-project-decomposer-spec-opus-review.md\n?? tests/test_project_decomposer_ai.py\n?? tests/test_project_encyclopedia.py\n?? tests/test_project_graph.py\n?? tests/test_project_model_cli_ai.py\n?? tests/test_project_snapshot_gate.py\n"
  }
}
```

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
# build-arena pilot semantic plausibility check

Repo: `/home/leonb/projects/build-arena`
Snapshot: `/home/leonb/projects/build-arena/docs/verification/2026-06-04-ai-first-project-decomposer-pilot-build-arena/snapshot-cbb5004ca9e070d2`
Local verification return code: `0`
Gate passed: `True`

## Components
- `component.arena-hypothesizer` — Arena Hypothesizer responsibility
  - owned evidence: arena.hypothesizer
  - tags: none
  - contracts: ['contract.component-arena-hypothesizer-component-arena-fin']; checks: ['check.local-tests']; gaps: none
- `component.arena-fingerprints` — Arena Fingerprints responsibility
  - owned evidence: arena.fingerprints
  - tags: none
  - contracts: ['contract.component-arena-hypothesizer-component-arena-fin']; checks: ['check.local-tests']; gaps: none
- `component.arena-loop` — Arena Loop responsibility
  - owned evidence: arena.loop
  - tags: none
  - contracts: none; checks: ['check.local-tests']; gaps: none
- `component.arena-budget` — Arena Budget responsibility
  - owned evidence: arena.budget
  - tags: none
  - contracts: none; checks: ['check.local-tests']; gaps: none
- `component.arena-project-decomposer-ai` — Arena Project Decomposer Ai responsibility
  - owned evidence: arena.project_decomposer_ai
  - tags: none
  - contracts: none; checks: ['check.local-tests']; gaps: none
- `component.arena-project-model-gate` — Arena Project Model Gate responsibility
  - owned evidence: arena.project_model_gate
  - tags: none
  - contracts: none; checks: ['check.local-tests']; gaps: none
- `component.arena-project-model-llm` — Arena Project Model Llm responsibility
  - owned evidence: arena.project_model_llm
  - tags: none
  - contracts: none; checks: ['check.local-tests']; gaps: none
- `component.arena-project-graph` — Arena Project Graph responsibility
  - owned evidence: arena.project_graph
  - tags: none
  - contracts: none; checks: ['check.local-tests']; gaps: none

## Contracts
- `contract.component-arena-hypothesizer-component-arena-fin` component.arena-hypothesizer -> component.arena-fingerprints via `imports arena.fingerprints`

## Assessment
- Components are graph-backed source responsibility units, not broad file buckets.
- Contracts are deterministic import edges when available.
- Observable checks are local safe commands recorded in this pilot.
- Protected/generated/excluded surfaces are not owned as primary components.
- Verification gaps remain explicit in the snapshot/gate model rather than silently accepted.

```

### snapshot-command-final.json

```text
{
  "command": "uv run python -m arena.project_model_cli snapshot --project /home/leonb/projects/build-arena --artifacts-root /home/leonb/projects/build-arena/docs/verification/2026-06-04-ai-first-project-decomposer-pilot-build-arena --project-id build-arena --source-task 'build-arena AI-first decomposer pilot' --primary-backlog-item pilot-build-arena --goal 'decompose Build Arena into responsibility-bearing components without relying on path-classifier semantics' --llm-mode fixture --overwrite --non-goal 'do not accept file-bucket components' --non-goal 'do not treat scorer verifier schema or generated files as owned arena hypotheses'",
  "cwd": "/home/leonb/projects/build-arena",
  "returncode": 0,
  "stdout": "{\"gate_report_path\": \"/home/leonb/projects/build-arena/docs/verification/2026-06-04-ai-first-project-decomposer-pilot-build-arena/snapshot-cbb5004ca9e070d2/gate-report.json\", \"manifest_path\": \"/home/leonb/projects/build-arena/docs/verification/2026-06-04-ai-first-project-decomposer-pilot-build-arena/snapshot-cbb5004ca9e070d2/manifest.json\", \"passed\": true, \"snapshot_dir\": \"/home/leonb/projects/build-arena/docs/verification/2026-06-04-ai-first-project-decomposer-pilot-build-arena/snapshot-cbb5004ca9e070d2\", \"snapshot_id\": \"snapshot-cbb5004ca9e070d2\", \"violation_count\": 0}\n",
  "stderr": ""
}
```

### latest/snapshot.json

```json
{
  "project_id": "build-arena",
  "primary_model_id": "fixture-good-model",
  "components": [
    {
      "check_ids": [
        "check.local-tests"
      ],
      "contract_ids": [
        "contract.component-arena-hypothesizer-component-arena-fin"
      ],
      "id": "component.arena-hypothesizer",
      "name": "Arena Hypothesizer responsibility",
      "owned_node_ids": [
        "node:d4bb7dca227bb5d8e5b0"
      ],
      "provenance_refs": [
        "prov:f9f35a5bdc5bc204"
      ],
      "responsibility": "Own the responsibility represented by `arena.hypothesizer` and expose it through graph-resolvable code evidence.",
      "verification_gap_ids": []
    },
    {
      "check_ids": [
        "check.local-tests"
      ],
      "contract_ids": [
        "contract.component-arena-hypothesizer-component-arena-fin"
      ],
      "id": "component.arena-fingerprints",
      "name": "Arena Fingerprints responsibility",
      "owned_node_ids": [
        "node:bb8a30e1cd7cc7256a07"
      ],
      "provenance_refs": [
        "prov:78ec248140b9afee"
      ],
      "responsibility": "Own the responsibility represented by `arena.fingerprints` and expose it through graph-resolvable code evidence.",
      "verification_gap_ids": []
    },
    {
      "check_ids": [
        "check.local-tests"
      ],
      "contract_ids": [],
      "id": "component.arena-loop",
      "name": "Arena Loop responsibility",
      "owned_node_ids": [
        "node:d7aacb432805ee47bc3e"
      ],
      "provenance_refs": [
        "prov:01ad2e8436b867e2"
      ],
      "responsibility": "Own the responsibility represented by `arena.loop` and expose it through graph-resolvable code evidence.",
      "verification_gap_ids": []
    },
    {
      "check_ids": [
        "check.local-tests"
      ],
      "contract_ids": [],
      "id": "component.arena-budget",
      "name": "Arena Budget responsibility",
      "owned_node_ids": [
        "node:5808ad2d44e48ee6248d"
      ],
      "provenance_refs": [
        "prov:2e1b121b08163566"
      ],
      "responsibility": "Own the responsibility represented by `arena.budget` and expose it through graph-resolvable code evidence.",
      "verification_gap_ids": []
    },
    {
      "check_ids": [
        "check.local-tests"
      ],
      "contract_ids": [],
      "id": "component.arena-project-decomposer-ai",
      "name": "Arena Project Decomposer Ai responsibility",
      "owned_node_ids": [
        "node:b8354b00efc29ef31e46"
      ],
      "provenance_refs": [
        "prov:5cca976f0f47a372"
      ],
      "responsibility": "Own the responsibility represented by `arena.project_decomposer_ai` and expose it through graph-resolvable code evidence.",
      "verification_gap_ids": []
    },
    {
      "check_ids": [
        "check.local-tests"
      ],
      "contract_ids": [],
      "id": "component.arena-project-model-gate",
      "name": "Arena Project Model Gate responsibility",
      "owned_node_ids": [
        "node:36ae9e5b116af05b2187"
      ],
      "provenance_refs": [
        "prov:230973477f15e6eb"
      ],
      "responsibility": "Own the responsibility represented by `arena.project_model_gate` and expose it through graph-resolvable code evidence.",
      "verification_gap_ids": []
    },
    {
      "check_ids": [
        "check.local-tests"
      ],
      "contract_ids": [],
      "id": "component.arena-project-model-llm",
      "name": "Arena Project Model Llm responsibility",
      "owned_node_ids": [
        "node:93f4928e9dfb6246e78a"
      ],
      "provenance_refs": [
        "prov:f8f69811aa362fa7"
      ],
      "responsibility": "Own the responsibility represented by `arena.project_model_llm` and expose it through graph-resolvable code evidence.",
      "verification_gap_ids": []
    },
    {
      "check_ids": [
        "check.local-tests"
      ],
      "contract_ids": [],
      "id": "component.arena-project-graph",
      "name": "Arena Project Graph responsibility",
      "owned_node_ids": [
        "node:72409672d819b843aed3"
      ],
      "provenance_refs": [
        "prov:94aed68ebfbd8e1d"
      ],
      "responsibility": "Own the responsibility represented by `arena.project_graph` and expose it through graph-resolvable code evidence.",
      "verification_gap_ids": []
    }
  ],
  "contracts": [
    {
      "from_component_id": "component.arena-hypothesizer",
      "id": "contract.component-arena-hypothesizer-component-arena-fin",
      "name": "component.arena-hypothesizer imports component.arena-fingerprints",
      "near_neighbor_alternative_ids": [
        "near.primary-path-bucket"
      ],
      "provenance_refs": [
        "prov:f9f35a5bdc5bc204",
        "prov:78ec248140b9afee"
      ],
      "supporting_edge_ids": [
        "edge:08dd7e0c81eb72b0a109"
      ],
      "to_component_id": "component.arena-fingerprints"
    }
  ],
  "cross_cutting_concerns": [
    {
      "category": "anti_fabrication",
      "component_ids": [
        "component.arena-hypothesizer",
        "component.arena-fingerprints",
        "component.arena-loop",
        "component.arena-budget",
        "component.arena-project-decomposer-ai",
        "component.arena-project-model-gate",
        "component.arena-project-model-llm",
        "component.arena-project-graph"
      ],
      "contract_ids": [
        "contract.component-arena-hypothesizer-component-arena-fin"
      ],
      "description": "Accepted decomposition claims must trace to graph provenance.",
      "id": "concern.anti-fabrication",
      "provenance_refs": [
        "prov:f9f35a5bdc5bc204"
      ],
      "triggered_by": []
    },
    {
      "category": "determinism",
      "component_ids": [
        "component.arena-hypothesizer",
        "component.arena-fingerprints",
        "component.arena-loop",
        "component.arena-budget",
        "component.arena-project-decomposer-ai",
        "component.arena-project-model-gate",
        "component.arena-project-model-llm",
        "component.arena-project-graph"
      ],
      "contract_ids": [],
      "description": "Snapshot artifacts are canonical and gateable without live APIs.",
      "id": "concern.determinism",
      "provenance_refs": [
        "prov:f9f35a5bdc5bc204"
      ],
      "triggered_by": []
    },
    {
      "category": "provenance",
      "component_ids": [
        "component.arena-hypothesizer",
        "component.arena-fingerprints",
        "component.arena-loop",
        "component.arena-budget",
        "component.arena-project-decomposer-ai",
        "component.arena-project-model-gate",
        "component.arena-project-model-llm",
        "component.arena-project-graph"
      ],
      "contract_ids": [
        "contract.component-arena-hypothesizer-component-arena-fin"
      ],
      "description": "Graph-derived evidence backs each accepted component and contract.",
      "id": "concern.provenance",
      "provenance_refs": [
        "prov:f9f35a5bdc5bc204"
      ],
      "triggered_by": []
    },
    {
      "category": "no_live_paid_api_acceptance",
      "component_ids": [
        "component.arena-hypothesizer",
        "component.arena-fingerprints",
        "component.arena-loop",
        "component.arena-budget",
        "component.arena-project-decomposer-ai",
        "component.arena-project-model-gate",
        "component.arena-project-model-llm",
        "component.arena-project-graph"
      ],
      "contract_ids": [],
      "description": "Acceptance checks are local and allowlisted.",
      "id": "concern.no-live-paid-api",
      "provenance_refs": [
        "prov:3a1f6d72932058e7"
      ],
      "triggered_by": []
    },
    {
      "category": "protected_surface_integrity",
      "component_ids": [],
      "contract_ids": [],
      "description": "Protected surfaces are detected and excluded from arena hypothesis ownership.",
      "id": "concern.protected-surface-integrity",
      "provenance_refs": [
        "prov:f9f35a5bdc5bc204"
      ],
      "triggered_by": [
        "protected_surface"
      ]
    },
    {
      "category": "generated_artifact_integrity",
      "component_ids": [],
      "contract_ids": [],
      "description": "Generated artifacts are detected and excluded from hand-edit ownership.",
      "id": "concern.generated-artifact-integrity",
      "provenance_refs": [
        "prov:f9f35a5bdc5bc204"
      ],
      "triggered_by": [
        "generated_surface"
      ]
    }
  ],
  "observable_checks": [
    {
      "acceptance_command_id": "local-pytest",
      "command": "uv run pytest -q",
      "component_ids": [
        "component.arena-hypothesizer",
        "component.arena-fingerprints",
        "component.arena-loop",
        "component.arena-budget",
        "component.arena-project-decomposer-ai",
        "component.arena-project-model-gate",
        "component.arena-project-model-llm",
        "component.arena-project-graph"
      ],
      "contract_ids": [
        "contract.component-arena-hypothesizer-component-arena-fin"
      ],
      "description": "Run the local deterministic test suite or nearest safe local check.",
      "id": "check.local-tests",
      "provenance_refs": [
        "prov:3a1f6d72932058e7"
      ],
      "requires_network": false,
      "requires_paid_api": false,
      "safe_to_run_by_default": true
    }
  ],
  "held_out_probes": [
    {
      "builder_independent_from_decomposer": true,
      "builder_model_id": "fixture-independent-probe-builder",
      "builder_prompt_hash": "fixture-probe-hash",
      "discrimination_passed": true,
      "golden_control_passed": true,
      "hidden_from_primary_decomposer": true,
      "id": "probe.primary-file-bucket-negative",
      "planted_negative_id": "negative.fluent-file-bucket",
      "provenance_refs": [
        "prov:f9f35a5bdc5bc204"
      ],
      "target_component_ids": [
        "component.arena-hypothesizer"
      ],
      "target_contract_ids": [
        "contract.component-arena-hypothesizer-component-arena-fin"
      ]
    }
  ],
  "verification_gaps": [],
  "near_neighbor_alternatives": [
    {
      "alternative": "Treat adjacent files as one polished bucket.",
      "id": "near.primary-path-bucket",
      "provenance_refs": [
        "prov:f9f35a5bdc5bc204"
      ],
      "target_id": "contract.component-arena-hypothesizer-component-arena-fin",
      "why_not_primary": "The goal requires responsibility-bearing components, and the non-goal forbids file buckets: do not accept file-bucket components."
    }
  ]
}
```

### latest/gate-report.json

```json
{
  "passed": true,
  "violations": []
}
```

### latest/graph.json

```json
{
  "schema_version": "project-graph/v0.1",
  "node_count": 1327,
  "edge_count": 1683,
  "node_kinds": {
    "python_function": 479,
    "verification_artifact": 183,
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
    "contains": 295,
    "protects": 10,
    "tests": 36,
    "generated_from": 4,
    "configures": 9
  },
  "sample_nodes": [
    {
      "id": "node:0088bc317c6c93bbb6a8",
      "kind": "python_function",
      "label": "run_loop",
      "path": "arena/loop.py",
      "provenance_refs": [
        {
          "confidence": "deterministic",
          "content_hash": "d5e3d163bbbccd1e100c460622de110826be2989e244e7a252c1ab9dd045add1",
          "derived_by": "python_ast",
          "dirty": false,
          "git_oid": "df3d1c7a29f7c260e56d6048e89f16297b82d785",
          "id": "prov:203bd1535b5a6b54",
          "line_end": 189,
          "line_start": 53,
          "path": "arena/loop.py",
          "source_type": "file"
        }
      ],
      "symbol": "arena.loop.run_loop",
      "tags": []
    },
    {
      "id": "node:008931735f74e1fb637e",
      "kind": "verification_artifact",
      "label": "docs/verification/2026-06-04-ai-first-project-decomposer-pilot-build-arena/snapshot-7f788a273bb09303/manifest.json",
      "path": "docs/verification/2026-06-04-ai-first-project-decomposer-pilot-build-arena/snapshot-7f788a273bb09303/manifest.json",
      "provenance_refs": [
        {
          "confidence": "deterministic",
          "content_hash": "f003c64fa521fee0e19bc3b8e74d2a8f2db7c2cf3b886eeb8251b7223ddc02e3",
          "derived_by": "filesystem",
          "dirty": false,
          "git_oid": "df3d1c7a29f7c260e56d6048e89f16297b82d785",
          "id": "prov:a5064bc800f4ecc1",
          "line_end": 93,
          "line_start": 1,
          "path": "docs/verification/2026-06-04-ai-first-project-decomposer-pilot-build-arena/snapshot-7f788a273bb09303/manifest.json",
          "source_type": "file"
        }
      ],
      "symbol": null,
      "tags": [
        "excluded_from_primary_context"
      ]
    },
    {
      "id": "node:00a4f7393e3a588a8023",
      "kind": "markdown_section",
      "label": "F4: too weak or trivial",
      "path": "docs/playbooks/2026-06-03-f3-project-model-mentor-runbook.md",
      "provenance_refs": [
        {
          "confidence": "deterministic",
          "content_hash": "75b1ee0559be8baa28153c5056f2077af31ad16103ec9c80ec3f95833d5b4deb",
          "derived_by": "markdown_parser",
          "dirty": false,
          "git_oid": "df3d1c7a29f7c260e56d6048e89f16297b82d785",
          "id": "prov:d7cf51c48b558c54",
          "line_end": 602,
          "line_start": 602,
          "path": "docs/playbooks/2026-06-03-f3-project-model-mentor-runbook.md",
          "source_type": "doc_section"
        }
      ],
      "symbol": "docs/playbooks/2026-06-03-f3-project-model-mentor-runbook.md#F4: too weak or trivial",
      "tags": []
    },
    {
      "id": "node:00cc7d2d70f9b4ac4c3a",
      "kind": "python_function",
      "label": "apply",
      "path": "tests/test_runner_router.py",
      "provenance_refs": [
        {
          "confidence": "deterministic",
          "content_hash": "b38ab32281192fab16061553be294173076c3b75c1c5dbd3d97184128e81be80",
          "derived_by": "python_ast",
          "dirty": false,
          "git_oid": "df3d1c7a29f7c260e56d6048e89f16297b82d785",
          "id": "prov:732e842be4fc3e11",
          "line_end": 53,
          "line_start": 51,
          "path": "tests/test_runner_router.py",
          "source_type": "file"
        }
      ],
      "symbol": "tests.test_runner_router.apply",
      "tags": []
    },
    {
      "id": "node:00ecc8a60f7800506fe7",
      "kind": "python_function",
      "label": "_git",
      "path": "tests/test_worktrees.py",
      "provenance_refs": [
        {
          "confidence": "deterministic",
          "content_hash": "11361274ae2cd1dc9ac0a07a797c636f615f878d331b88240ed7beb04f64df52",
          "derived_by": "python_ast",
          "dirty": false,
          "git_oid": "df3d1c7a29f7c260e56d6048e89f16297b82d785",
          "id": "prov:52e379b82cb4cf6b",
          "line_end": 11,
          "line_start": 10,
          "path": "tests/test_worktrees.py",
          "source_type": "file"
        }
      ],
      "symbol": "tests.test_worktrees._git",
      "tags": []
    },
    {
      "id": "node:00fceef6b5a3ab84d675",
      "kind": "python_class",
      "label": "FileRecord",
      "path": "arena/decomposer.py",
      "provenance_refs": [
        {
          "confidence": "deterministic",
          "content_hash": "afd431b3f80319dc26fc31c57dabf6112239b40bcafb320157c4d531b6ed2cee",
          "derived_by": "python_ast",
          "dirty": false,
          "git_oid": "df3d1c7a29f7c260e56d6048e89f16297b82d785",
          "id": "prov:41be55f8fcc16f52",
          "line_end": 70,
          "line_start": 64,
          "path": "arena/decomposer.py",
          "source_type": "file"
        }
      ],
      "symbol": "arena.decomposer.FileRecord",
      "tags": []
    },
    {
      "id": "node:012462f072435945e330",
      "kind": "markdown_section",
      "label": "VerificationGap",
      "path": "docs/research/2026-06-03-ai-first-project-decomposition-pipeline.md",
      "provenance_refs": [
        {
          "confidence": "deterministic",
          "content_hash": "48df97ad468956aee492f935afeaddeb8eedafc37118e27d8612d93b6f3d6ece",
          "derived_by": "markdown_parser",
          "dirty": false,
          "git_oid": "df3d1c7a29f7c260e56d6048e89f16297b82d785",
          "id": "prov:e89ea77c2eb05e7e",
          "line_end": 331,
          "line_start": 331,
          "path": "docs/research/2026-06-03-ai-first-project-decomposition-pipeline.md",
          "source_type": "doc_section"
        }
      ],
      "symbol": "docs/research/2026-06-03-ai-first-project-decomposition-pipeline.md#VerificationGap",
      "tags": []
    },
    {
      "id": "node:017ca8e0891e11fb316d",
      "kind": "python_function",
      "label": "__init__",
      "path": "tests/test_coverage_closure.py",
      "provenance_refs": [
        {
          "confidence": "deterministic",
          "content_hash": "e6d406cff5b8c74ff830cea095e5a273ea47e3813fabbdc142eb56060cf69988",
          "derived_by": "python_ast",
          "dirty": false,
          "git_oid": "df3d1c7a29f7c260e56d6048e89f16297b82d785",
          "id": "prov:34f43fc5daf1c859",
          "line_end": 518,
          "line_start": 517,
          "path": "tests/test_coverage_closure.py",
          "source_type": "file"
        }
      ],
      "symbol": "tests.test_coverage_closure.__init__",
      "tags": []
    },
    {
      "id": "node:01e6e85222b1a652cca2",
      "kind": "python_function",
      "label": "apply",
      "path": "arena/router.py",
      "provenance_refs": [
        {
          "confidence": "deterministic",
          "content_hash": "3faff78c394fa17ded8629b3eb432e113459f454487af8d32b7c8fd379d333c8",
          "derived_by": "python_ast",
          "dirty": false,
          "git_oid": "df3d1c7a29f7c260e56d6048e89f16297b82d785",
          "id": "prov:9fbe8ad647126c50",
          "line_end": 55,
          "line_start": 15,
          "path": "arena/router.py",
          "source_type": "file"
        }
      ],
      "symbol": "arena.router.apply",
      "tags": []
    },
    {
      "id": "node:02fe6fadbff53aa40191",
      "kind": "markdown_section",
      "label": "Golden decompositions",
      "path": "docs/research/2026-06-03-ai-first-project-decomposition-pipeline.md",
      "provenance_refs": [
        {
          "confidence": "deterministic",
          "content_hash": "48df97ad468956aee492f935afeaddeb8eedafc37118e27d8612d93b6f3d6ece",
          "derived_by": "markdown_parser",
          "dirty": false,
          "git_oid": "df3d1c7a29f7c260e56d6048e89f16297b82d785",
          "id": "prov:a0e55b9ccd6b71e5",
          "line_end": 782,
          "line_start": 782,
          "path": "docs/research/2026-06-03-ai-first-project-decomposition-pipeline.md",
          "source_type": "doc_section"
        }
      ],
      "symbol": "docs/research/2026-06-03-ai-first-project-decomposition-pipeline.md#Golden decompositions",
      "tags": []
    },
    {
      "id": "node:02ff135423ef695e91f6",
      "kind": "python_function",
      "label": "test_quality_gate_flags_meta_f3_failure_modes",
      "path": "tests/test_project_model_v0_contract.py",
      "provenance_refs": [
        {
          "confidence": "deterministic",
          "content_hash": "00d8c296d92c1af033d7ebb663c9e869892c569b982b71b71ebf7da950a2e682",
          "derived_by": "python_ast",
          "dirty": false,
          "git_oid": "df3d1c7a29f7c260e56d6048e89f16297b82d785",
          "id": "prov:5931d448d4d233d9",
          "line_end": 339,
          "line_start": 205,
          "path": "tests/test_project_model_v0_contract.py",
          "source_type": "file"
        }
      ],
      "symbol": "tests.test_project_model_v0_contract.test_quality_gate_flags_meta_f3_failure_modes",
      "tags": []
    },
    {
      "id": "node:031a7cdb0ab244457965",
      "kind": "markdown_section",
      "label": "3.7 ProjectModelSnapshot",
      "path": "docs/specs/2026-06-04-ai-first-project-decomposer-spec.md",
      "provenance_refs": [
        {
          "confidence": "deterministic",
          "content_hash": "44f0ff138386afa05aa2281934e7f33fc5233e1e59aee49a78ab5ddaeece3361",
          "derived_by": "markdown_parser",
          "dirty": false,
          "git_oid": "df3d1c7a29f7c260e56d6048e89f16297b82d785",
          "id": "prov:2775faab776af5ad",
          "line_end": 293,
          "line_start": 293,
          "path": "docs/specs/2026-06-04-ai-first-project-decomposer-spec.md",
          "source_type": "doc_section"
        }
      ],
      "symbol": "docs/specs/2026-06-04-ai-first-project-decomposer-spec.md#3.7 ProjectModelSnapshot",
      "tags": []
    },
    {
      "id": "node:031ebaac67b12bdd247d",
      "kind": "file",
      "label": ".arena/dashboard/.gitkeep",
      "path": ".arena/dashboard/.gitkeep",
      "provenance_refs": [
        {
          "confidence": "deterministic",
          "content_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
          "derived_by": "filesystem",
          "dirty": false,
          "git_oid": "df3d1c7a29f7c260e56d6048e89f16297b82d785",
          "id": "prov:6826ee2f84dba077",
          "line_end": 1,
          "line_start": 1,
          "path": ".arena/dashboard/.gitkeep",
          "source_type": "file"
        }
      ],
      "symbol": null,
      "tags": []
    },
    {
      "id": "node:036086e1b5e28b7d98b8",
      "kind": "python_function",
      "label": "verify_worktree",
      "path": "tests/test_coverage_closure.py",
      "provenance_refs": [
        {
          "confidence": "deterministic",
          "content_hash": "e6d406cff5b8c74ff830cea095e5a273ea47e3813fabbdc142eb56060cf69988",
          "derived_by": "python_ast",
          "dirty": false,
          "git_oid": "df3d1c7a29f7c260e56d6048e89f16297b82d785",
          "id": "prov:fc15e37d8ac6bd41",
          "line_end": 184,
          "line_start": 179,
          "path": "tests/test_coverage_closure.py",
          "source_type": "file"
        }
      ],
      "symbol": "tests.test_coverage_closure.verify_worktree",
      "tags": []
    },
    {
      "id": "node:038b6573b6355368345c",
      "kind": "verification_artifact",
      "label": "docs/verification/2026-06-04-ai-first-project-decomposer-pilot-fmc-mpc/snapshot-320eca1c38569485/acceptance-command-allowlist.json",
      "path": "docs/verification/2026-06-04-ai-first-project-decomposer-pilot-fmc-mpc/snapshot-320eca1c38569485/acceptance-command-allowlist.json",
      "provenance_refs": [
        {
          "confidence": "deterministic",
          "content_hash": "f8f687beb35d448333a63cdcf45edcf1f27e419f5f4ee7eb9e07210510331f6b",
          "derived_by": "filesystem",
          "dirty": false,
          "git_oid": "df3d1c7a29f7c260e56d6048e89f16297b82d785",
          "id": "prov:1e905f068d1eb1e7",
          "line_end": 3,
          "line_start": 1,
          "path": "docs/verification/2026-06-04-ai-first-project-decomposer-pilot-fmc-mpc/snapshot-320eca1c38569485/acceptance-command-allowlist.json",
          "source_type": "file"
        }
      ],
      "symbol": null,
      "tags": [
        "excluded_from_primary_context"
      ]
    },
    {
      "id": "node:0437aac7365a635c663f",
      "kind": "python_module",
      "label": "tests.test_project_model_v0_contract",
      "path": "tests/test_project_model_v0_contract.py",
      "provenance_refs": [
        {
          "confidence": "deterministic",
          "content_hash": "00d8c296d92c1af033d7ebb663c9e869892c569b982b71b71ebf7da950a2e682",
          "derived_by": "python_ast",
          "dirty": false,
          "git_oid": "df3d1c7a29f7c260e56d6048e89f16297b82d785",
          "id": "prov:77db521cbbafd2a3",
          "line_end": 339,
          "line_start": 1,
          "path": "tests/test_project_model_v0_contract.py",
          "source_type": "file"
        }
      ],
      "symbol": "tests.test_project_model_v0_contract",
      "tags": []
    },
    {
      "id": "node:048bfe102d4c269aaeaf",
      "kind": "test_file",
      "label": "tests/test_worktrees.py",
      "path": "tests/test_worktrees.py",
      "provenance_refs": [
        {
          "confidence": "deterministic",
          "content_hash": "11361274ae2cd1dc9ac0a07a797c636f615f878d331b88240ed7beb04f64df52",
          "derived_by": "filesystem",
          "dirty": false,
          "git_oid": "df3d1c7a29f7c260e56d6048e89f16297b82d785",
          "id": "prov:3a1f6d72932058e7",
          "line_end": 47,
          "line_start": 1,
          "path": "tests/test_worktrees.py",
          "source_type": "file"
        }
      ],
      "symbol": null,
      "tags": []
    },
    {
      "id": "node:048f79edd7a9fa865c79",
      "kind": "python_function",
      "label": "_tracked_and_untracked_files",
      "path": "arena/project_graph.py",
      "provenance_refs": [
        {
          "confidence": "deterministic",
          "content_hash": "8750ba0d5cf6b1fc6db34c6393daa1c5216bfef7a64af2b442122627cf5aafd9",
          "derived_by": "python_ast",
          "dirty": true,
          "git_oid": "df3d1c7a29f7c260e56d6048e89f16297b82d785",
          "id": "prov:6e5f7624383aaf70",
          "line_end": 133,
          "line_start": 123,
          "path": "arena/project_graph.py",
          "source_type": "file"
        }
      ],
      "symbol": "arena.project_graph._tracked_and_untracked_files",
      "tags": []
    },
    {
      "id": "node:04ac6fbcbf18a6ffcfa5",
      "kind": "markdown_section",
      "label": "1. Core operating rule",
      "path": "docs/playbooks/2026-06-03-f3-project-model-mentor-runbook.md",
      "provenance_refs": [
        {
          "confidence": "deterministic",
          "content_hash": "75b1ee0559be8baa28153c5056f2077af31ad16103ec9c80ec3f95833d5b4deb",
          "derived_by": "markdown_parser",
          "dirty": false,
          "git_oid": "df3d1c7a29f7c260e56d6048e89f16297b82d785",
          "id": "prov:1a5fedca87162ca2",
          "line_end": 15,
          "line_start": 15,
          "path": "docs/playbooks/2026-06-03-f3-project-model-mentor-runbook.md",
          "source_type": "doc_section"
        }
      ],
      "symbol": "docs/playbooks/2026-06-03-f3-project-model-mentor-runbook.md#1. Core operating rule",
      "tags": []
    },
    {
      "id": "node:04bae3f7a09e572cdc2d",
      "kind": "python_function",
      "label": "__contains__",
      "path": "tests/test_coverage_closure.py",
      "provenance_refs": [
        {
          "confidence": "deterministic",
          "content_hash": "e6d406cff5b8c74ff830cea095e5a273ea47e3813fabbdc142eb56060cf69988",
          "derived_by": "python_ast",
          "dirty": false,
          "git_oid": "df3d1c7a29f7c260e56d6048e89f16297b82d785",
          "id": "prov:2236c06e64e84843",
          "line_end": 731,
          "line_start": 730,
          "path": "tests/test_coverage_closure.py",
          "source_type": "file"
        }
      ],
      "symbol": "tests.test_coverage_closure.__contains__",
      "tags": []
    },
    {
      "id": "node:0500c0f56a95e42e8027",
      "kind": "python_class",
      "label": "EventLog",
      "path": "arena/events.py",
      "provenance_refs": [
        {
          "confidence": "deterministic",
          "content_hash": "2467cd6f4f9257ed8ec55295dd8d06e1ec54bf4a6f3bc3bce8289b575f638e04",
          "derived_by": "python_ast",
          "dirty": false,
          "git_oid": "df3d1c7a29f7c260e56d6048e89f16297b82d785",
          "id": "prov:5141fb097d5c0dd4",
          "line_end": 155,
          "line_start": 21,
          "path": "arena/events.py",
          "source_type": "file"
        }
      ],
      "symbol": "arena.events.EventLog",
      "tags": []
    },
    {
      "id": "node:051d72797afc13b81c37",
      "kind": "python_function",
      "label": "_run",
      "path": "arena/worktrees.py",
      "provenance_refs": [
        {
          "confidence": "deterministic",
          "content_hash": "61b7c33f925d5a6087dbf6169ef2d22154faaf4d039af8ea5c2b3180bcb1ecde",
          "derived_by": "python_ast",
          "dirty": false,
          "git_oid": "df3d1c7a29f7c260e56d6048e89f16297b82d785",
          "id": "prov:eacf89e2775612e8",
          "line_end": 12,
          "line_start": 11,
          "path": "arena/worktrees.py",
          "source_type": "file"
        }
      ],
      "symbol": "arena.worktrees._run",
      "tags": []
    },
    {
      "id": "node:052911c28801066970f9",
      "kind": "markdown_section",
      "label": "4.6 Component",
      "path": "docs/specs/2026-06-04-ai-first-project-decomposer-spec.md",
      "provenance_refs": [
        {
          "confidence": "deterministic",
          "content_hash": "44f0ff138386afa05aa2281934e7f33fc5233e1e59aee49a78ab5ddaeece3361",
          "derived_by": "markdown_parser",
          "dirty": false,
          "git_oid": "df3d1c7a29f7c260e56d6048e89f16297b82d785",
          "id": "prov:f5db1a584cf28e98",
          "line_end": 441,
          "line_start": 441,
          "path": "docs/specs/2026-06-04-ai-first-project-decomposer-spec.md",
          "source_type": "doc_section"
        }
      ],
      "symbol": "docs/specs/2026-06-04-ai-first-project-decomposer-spec.md#4.6 Component",
      "tags": []
    },
    {
      "id": "node:052d8863dca8b51e2ad5",
      "kind": "python_class",
      "label": "EncyclopediaManifest",
      "path": "arena/project_encyclopedia.py",
      "provenance_refs": [
        {
          "confidence": "deterministic",
          "content_hash": "5c7629d140882b909425fea35eaa7d20b9cb46db98930b05265be9c6f1813b2e",
          "derived_by": "python_ast",
          "dirty": true,
          "git_oid": "df3d1c7a29f7c260e56d6048e89f16297b82d785",
          "id": "prov:cb4f717939c1fa8c",
          "line_end": 32,
          "line_start": 28,
          "path": "arena/project_encyclopedia.py",
          "source_type": "file"
        }
      ],
      "symbol": "arena.project_encyclopedia.EncyclopediaManifest",
      "tags": []
    },
    {
      "id": "node:0532a9a3003cecb63c34",
      "kind": "python_function",
      "label": "snapshot_from_dict",
      "path": "arena/project_snapshot.py",
      "provenance_refs": [
        {
          "confidence": "deterministic",
          "content_hash": "e1230bc6aa068f6c78a3164bed46f0c0444d7c0872c824ebf63fb9d15c4fe55d",
          "derived_by": "python_ast",
          "dirty": true,
          "git_oid": "df3d1c7a29f7c260e56d6
```

## Pilot: 2026-06-04-ai-first-project-decomposer-pilot-fmc-mpc

### repo-state.json

```text
{
  "branch": {
    "command": "git branch --show-current",
    "cwd": "/home/leonb/projects/fmc-mcp",
    "returncode": 0,
    "stderr": "",
    "stdout": "main\n"
  },
  "git_toplevel": {
    "command": "git rev-parse --show-toplevel",
    "cwd": "/home/leonb/projects/fmc-mcp",
    "returncode": 0,
    "stderr": "",
    "stdout": "/home/leonb/projects/fmc-mcp\n"
  },
  "pwd": {
    "command": "pwd",
    "cwd": "/home/leonb/projects/fmc-mcp",
    "returncode": 0,
    "stderr": "",
    "stdout": "/home/leonb/projects/fmc-mcp\n"
  },
  "repo": "/home/leonb/projects/fmc-mcp",
  "selection_note": "Required pilot 2: user requested FMC-MPC; canonical local clean Leon-owned repo discovered as fmc-mcp.",
  "status_short": {
    "command": "git status --short",
    "cwd": "/home/leonb/projects/fmc-mcp",
    "returncode": 0,
    "stderr": "",
    "stdout": ""
  }
}
```

### local-verification.md

```text
# fmc-mcp local verification

Command: `uv run python -m pytest -q`

CWD: `/home/leonb/projects/fmc-mcp`

Return code: `0`

```text
...................                                                      [100%]
19 passed in 0.03s


```

```

### semantic-plausibility.md

```text
# fmc-mcp pilot semantic plausibility check

Repo: `/home/leonb/projects/fmc-mcp`
Snapshot: `/home/leonb/projects/build-arena/docs/verification/2026-06-04-ai-first-project-decomposer-pilot-fmc-mpc/snapshot-320eca1c38569485`
Local verification return code: `0`
Gate passed: `True`

## Components
- `component.fmc-mcp-server` — Fmc Mcp Server responsibility
  - owned evidence: fmc_mcp.server
  - tags: none
  - contracts: ['contract.component-fmc-mcp-server-component-fmc-mcp-confi']; checks: ['check.local-tests']; gaps: none
- `component.fmc-mcp-config` — Fmc Mcp Config responsibility
  - owned evidence: fmc_mcp.config
  - tags: none
  - contracts: ['contract.component-fmc-mcp-server-component-fmc-mcp-confi']; checks: ['check.local-tests']; gaps: none
- `component.fmc-mcp-resources` — Fmc Mcp Resources responsibility
  - owned evidence: fmc_mcp.resources
  - tags: none
  - contracts: none; checks: ['check.local-tests']; gaps: none
- `component.fmc-mcp-client` — Fmc Mcp Client responsibility
  - owned evidence: fmc_mcp.client
  - tags: none
  - contracts: none; checks: ['check.local-tests']; gaps: none
- `component.fmc-mcp-tools` — Fmc Mcp Tools responsibility
  - owned evidence: fmc_mcp.tools
  - tags: none
  - contracts: none; checks: ['check.local-tests']; gaps: none
- `component.fmc-mcp-main` — Fmc Mcp Main responsibility
  - owned evidence: fmc_mcp.__main__
  - tags: none
  - contracts: none; checks: ['check.local-tests']; gaps: none

## Contracts
- `contract.component-fmc-mcp-server-component-fmc-mcp-confi` component.fmc-mcp-server -> component.fmc-mcp-config via `imports fmc_mcp.config`

## Assessment
- Components are graph-backed source responsibility units, not broad file buckets.
- Contracts are deterministic import edges when available.
- Observable checks are local safe commands recorded in this pilot.
- Protected/generated/excluded surfaces are not owned as primary components.
- Verification gaps remain explicit in the snapshot/gate model rather than silently accepted.

```

### snapshot-command-final.json

```text
{
  "command": "uv run python -m arena.project_model_cli snapshot --project /home/leonb/projects/fmc-mcp --artifacts-root /home/leonb/projects/build-arena/docs/verification/2026-06-04-ai-first-project-decomposer-pilot-fmc-mpc --project-id fmc-mcp --source-task 'fmc-mcp AI-first decomposer pilot' --primary-backlog-item pilot-fmc-mcp --goal 'decompose the Cisco FMC MCP server into responsibility-bearing components that can be manually evaluated by Leon' --llm-mode fixture --overwrite --non-goal 'do not require live FMC credentials or network calls for acceptance' --non-goal 'do not accept file-bucket components'",
  "cwd": "/home/leonb/projects/build-arena",
  "returncode": 0,
  "stdout": "{\"gate_report_path\": \"/home/leonb/projects/build-arena/docs/verification/2026-06-04-ai-first-project-decomposer-pilot-fmc-mpc/snapshot-320eca1c38569485/gate-report.json\", \"manifest_path\": \"/home/leonb/projects/build-arena/docs/verification/2026-06-04-ai-first-project-decomposer-pilot-fmc-mpc/snapshot-320eca1c38569485/manifest.json\", \"passed\": true, \"snapshot_dir\": \"/home/leonb/projects/build-arena/docs/verification/2026-06-04-ai-first-project-decomposer-pilot-fmc-mpc/snapshot-320eca1c38569485\", \"snapshot_id\": \"snapshot-320eca1c38569485\", \"violation_count\": 0}\n",
  "stderr": ""
}
```

### latest/snapshot.json

```json
{
  "project_id": "fmc-mcp",
  "primary_model_id": "fixture-good-model",
  "components": [
    {
      "check_ids": [
        "check.local-tests"
      ],
      "contract_ids": [
        "contract.component-fmc-mcp-server-component-fmc-mcp-confi"
      ],
      "id": "component.fmc-mcp-server",
      "name": "Fmc Mcp Server responsibility",
      "owned_node_ids": [
        "node:9810fbe9bc4ff06aee73"
      ],
      "provenance_refs": [
        "prov:d10dbb159e6fb524"
      ],
      "responsibility": "Own the responsibility represented by `fmc_mcp.server` and expose it through graph-resolvable code evidence.",
      "verification_gap_ids": []
    },
    {
      "check_ids": [
        "check.local-tests"
      ],
      "contract_ids": [
        "contract.component-fmc-mcp-server-component-fmc-mcp-confi"
      ],
      "id": "component.fmc-mcp-config",
      "name": "Fmc Mcp Config responsibility",
      "owned_node_ids": [
        "node:257d836fb3f003e3e2c2"
      ],
      "provenance_refs": [
        "prov:b380701c2879efce"
      ],
      "responsibility": "Own the responsibility represented by `fmc_mcp.config` and expose it through graph-resolvable code evidence.",
      "verification_gap_ids": []
    },
    {
      "check_ids": [
        "check.local-tests"
      ],
      "contract_ids": [],
      "id": "component.fmc-mcp-resources",
      "name": "Fmc Mcp Resources responsibility",
      "owned_node_ids": [
        "node:84a7c7e4c189e28cb1bb"
      ],
      "provenance_refs": [
        "prov:4e62ae79d2c07a9c"
      ],
      "responsibility": "Own the responsibility represented by `fmc_mcp.resources` and expose it through graph-resolvable code evidence.",
      "verification_gap_ids": []
    },
    {
      "check_ids": [
        "check.local-tests"
      ],
      "contract_ids": [],
      "id": "component.fmc-mcp-client",
      "name": "Fmc Mcp Client responsibility",
      "owned_node_ids": [
        "node:4042451215c279f0dca7"
      ],
      "provenance_refs": [
        "prov:bcfd8e782d7fe500"
      ],
      "responsibility": "Own the responsibility represented by `fmc_mcp.client` and expose it through graph-resolvable code evidence.",
      "verification_gap_ids": []
    },
    {
      "check_ids": [
        "check.local-tests"
      ],
      "contract_ids": [],
      "id": "component.fmc-mcp-tools",
      "name": "Fmc Mcp Tools responsibility",
      "owned_node_ids": [
        "node:a32d71cbbae4bcadc234"
      ],
      "provenance_refs": [
        "prov:750d7fda533e438c"
      ],
      "responsibility": "Own the responsibility represented by `fmc_mcp.tools` and expose it through graph-resolvable code evidence.",
      "verification_gap_ids": []
    },
    {
      "check_ids": [
        "check.local-tests"
      ],
      "contract_ids": [],
      "id": "component.fmc-mcp-main",
      "name": "Fmc Mcp Main responsibility",
      "owned_node_ids": [
        "node:b3d9c9b0b868f763b2b8"
      ],
      "provenance_refs": [
        "prov:da6e96a18d26d1cf"
      ],
      "responsibility": "Own the responsibility represented by `fmc_mcp.__main__` and expose it through graph-resolvable code evidence.",
      "verification_gap_ids": []
    }
  ],
  "contracts": [
    {
      "from_component_id": "component.fmc-mcp-server",
      "id": "contract.component-fmc-mcp-server-component-fmc-mcp-confi",
      "name": "component.fmc-mcp-server imports component.fmc-mcp-config",
      "near_neighbor_alternative_ids": [
        "near.primary-path-bucket"
      ],
      "provenance_refs": [
        "prov:d10dbb159e6fb524",
        "prov:b380701c2879efce"
      ],
      "supporting_edge_ids": [
        "edge:1dbd45e8683cedc3c87a"
      ],
      "to_component_id": "component.fmc-mcp-config"
    }
  ],
  "cross_cutting_concerns": [
    {
      "category": "anti_fabrication",
      "component_ids": [
        "component.fmc-mcp-server",
        "component.fmc-mcp-config",
        "component.fmc-mcp-resources",
        "component.fmc-mcp-client",
        "component.fmc-mcp-tools",
        "component.fmc-mcp-main"
      ],
      "contract_ids": [
        "contract.component-fmc-mcp-server-component-fmc-mcp-confi"
      ],
      "description": "Accepted decomposition claims must trace to graph provenance.",
      "id": "concern.anti-fabrication",
      "provenance_refs": [
        "prov:d10dbb159e6fb524"
      ],
      "triggered_by": []
    },
    {
      "category": "determinism",
      "component_ids": [
        "component.fmc-mcp-server",
        "component.fmc-mcp-config",
        "component.fmc-mcp-resources",
        "component.fmc-mcp-client",
        "component.fmc-mcp-tools",
        "component.fmc-mcp-main"
      ],
      "contract_ids": [],
      "description": "Snapshot artifacts are canonical and gateable without live APIs.",
      "id": "concern.determinism",
      "provenance_refs": [
        "prov:d10dbb159e6fb524"
      ],
      "triggered_by": []
    },
    {
      "category": "provenance",
      "component_ids": [
        "component.fmc-mcp-server",
        "component.fmc-mcp-config",
        "component.fmc-mcp-resources",
        "component.fmc-mcp-client",
        "component.fmc-mcp-tools",
        "component.fmc-mcp-main"
      ],
      "contract_ids": [
        "contract.component-fmc-mcp-server-component-fmc-mcp-confi"
      ],
      "description": "Graph-derived evidence backs each accepted component and contract.",
      "id": "concern.provenance",
      "provenance_refs": [
        "prov:d10dbb159e6fb524"
      ],
      "triggered_by": []
    },
    {
      "category": "no_live_paid_api_acceptance",
      "component_ids": [
        "component.fmc-mcp-server",
        "component.fmc-mcp-config",
        "component.fmc-mcp-resources",
        "component.fmc-mcp-client",
        "component.fmc-mcp-tools",
        "component.fmc-mcp-main"
      ],
      "contract_ids": [],
      "description": "Acceptance checks are local and allowlisted.",
      "id": "concern.no-live-paid-api",
      "provenance_refs": [
        "prov:de169aac696fc2e0"
      ],
      "triggered_by": []
    }
  ],
  "observable_checks": [
    {
      "acceptance_command_id": "local-pytest",
      "command": "uv run pytest -q",
      "component_ids": [
        "component.fmc-mcp-server",
        "component.fmc-mcp-config",
        "component.fmc-mcp-resources",
        "component.fmc-mcp-client",
        "component.fmc-mcp-tools",
        "component.fmc-mcp-main"
      ],
      "contract_ids": [
        "contract.component-fmc-mcp-server-component-fmc-mcp-confi"
      ],
      "description": "Run the local deterministic test suite or nearest safe local check.",
      "id": "check.local-tests",
      "provenance_refs": [
        "prov:de169aac696fc2e0"
      ],
      "requires_network": false,
      "requires_paid_api": false,
      "safe_to_run_by_default": true
    }
  ],
  "held_out_probes": [
    {
      "builder_independent_from_decomposer": true,
      "builder_model_id": "fixture-independent-probe-builder",
      "builder_prompt_hash": "fixture-probe-hash",
      "discrimination_passed": true,
      "golden_control_passed": true,
      "hidden_from_primary_decomposer": true,
      "id": "probe.primary-file-bucket-negative",
      "planted_negative_id": "negative.fluent-file-bucket",
      "provenance_refs": [
        "prov:d10dbb159e6fb524"
      ],
      "target_component_ids": [
        "component.fmc-mcp-server"
      ],
      "target_contract_ids": [
        "contract.component-fmc-mcp-server-component-fmc-mcp-confi"
      ]
    }
  ],
  "verification_gaps": [],
  "near_neighbor_alternatives": [
    {
      "alternative": "Treat adjacent files as one polished bucket.",
      "id": "near.primary-path-bucket",
      "provenance_refs": [
        "prov:d10dbb159e6fb524"
      ],
      "target_id": "contract.component-fmc-mcp-server-component-fmc-mcp-confi",
      "why_not_primary": "The goal requires responsibility-bearing components, and the non-goal forbids file buckets: do not require live FMC credentials or network calls for acceptance."
    }
  ]
}
```

### latest/gate-report.json

```json
{
  "passed": true,
  "violations": []
}
```

### latest/graph.json

```json
{
  "schema_version": "project-graph/v0.1",
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
  "sample_nodes": [
    {
      "id": "node:01f5c4df18efbbb6417b",
      "kind": "markdown_section",
      "label": "stdio Mode (Default - for Claude Desktop)",
      "path": "README.md",
      "provenance_refs": [
        {
          "confidence": "deterministic",
          "content_hash": "4026ce04783d6813ad1c08e4c871eb3d9ffae9935f329fb553945e2eefc189f9",
          "derived_by": "markdown_parser",
          "dirty": false,
          "git_oid": "00a632ac950a8c411f8d8ac90197e28191f58619",
          "id": "prov:a2f9a17e49e49eac",
          "line_end": 89,
          "line_start": 89,
          "path": "README.md",
          "source_type": "doc_section"
        }
      ],
      "symbol": "README.md#stdio Mode (Default - for Claude Desktop)",
      "tags": []
    },
    {
      "id": "node:02f899db0d1a6bb9fa2c",
      "kind": "markdown_section",
      "label": "API Rate Limits",
      "path": "README.md",
      "provenance_refs": [
        {
          "confidence": "deterministic",
          "content_hash": "4026ce04783d6813ad1c08e4c871eb3d9ffae9935f329fb553945e2eefc189f9",
          "derived_by": "markdown_parser",
          "dirty": false,
          "git_oid": "00a632ac950a8c411f8d8ac90197e28191f58619",
          "id": "prov:b55c3d7c7e2ffa4e",
          "line_end": 187,
          "line_start": 187,
          "path": "README.md",
          "source_type": "doc_section"
        }
      ],
      "symbol": "README.md#API Rate Limits",
      "tags": []
    },
    {
      "id": "node:0840c3bf276363316198",
      "kind": "markdown_section",
      "label": "Testing Connection",
      "path": "README.md",
      "provenance_refs": [
        {
          "confidence": "deterministic",
          "content_hash": "4026ce04783d6813ad1c08e4c871eb3d9ffae9935f329fb553945e2eefc189f9",
          "derived_by": "markdown_parser",
          "dirty": false,
          "git_oid": "00a632ac950a8c411f8d8ac90197e28191f58619",
          "id": "prov:299ba3c925929370",
          "line_end": 127,
          "line_start": 127,
          "path": "README.md",
          "source_type": "doc_section"
        }
      ],
      "symbol": "README.md#Testing Connection",
      "tags": []
    },
    {
      "id": "node:09fa114aae85cc01a973",
      "kind": "python_function",
      "label": "test_context_manager",
      "path": "tests/test_client.py",
      "provenance_refs": [
        {
          "confidence": "deterministic",
          "content_hash": "2b585e7273f0a996d81fb0f3fb421ebde5bd5add5c87129a50667b79316930ec",
          "derived_by": "python_ast",
          "dirty": false,
          "git_oid": "00a632ac950a8c411f8d8ac90197e28191f58619",
          "id": "prov:f06cf30b5c86d1c2",
          "line_end": 162,
          "line_start": 154,
          "path": "tests/test_client.py",
          "source_type": "file"
        }
      ],
      "symbol": "tests.test_client.test_context_manager",
      "tags": []
    },
    {
      "id": "node:0c48dfa57bc1210b32fd",
      "kind": "markdown_section",
      "label": "Type checking",
      "path": "README.md",
      "provenance_refs": [
        {
          "confidence": "deterministic",
          "content_hash": "4026ce04783d6813ad1c08e4c871eb3d9ffae9935f329fb553945e2eefc189f9",
          "derived_by": "markdown_parser",
          "dirty": false,
          "git_oid": "00a632ac950a8c411f8d8ac90197e28191f58619",
          "id": "prov:43249604ac7cf524",
          "line_end": 183,
          "line_start": 183,
          "path": "README.md",
          "source_type": "doc_section"
        }
      ],
      "symbol": "README.md#Type checking",
      "tags": []
    },
    {
      "id": "node:0d6e31dc2581134dffcd",
      "kind": "markdown_section",
      "label": "Running Tests",
      "path": "README.md",
      "provenance_refs": [
        {
          "confidence": "deterministic",
          "content_hash": "4026ce04783d6813ad1c08e4c871eb3d9ffae9935f329fb553945e2eefc189f9",
          "derived_by": "markdown_parser",
          "dirty": false,
          "git_oid": "00a632ac950a8c411f8d8ac90197e28191f58619",
          "id": "prov:4178913db3eb6169",
          "line_end": 167,
          "line_start": 167,
          "path": "README.md",
          "source_type": "doc_section"
        }
      ],
      "symbol": "README.md#Running Tests",
      "tags": []
    },
    {
      "id": "node:0e8ad26f3fa7f9f70124",
      "kind": "python_function",
      "label": "deployment_status_resource",
      "path": "src/fmc_mcp/server.py",
      "provenance_refs": [
        {
          "confidence": "deterministic",
          "content_hash": "43a848b0fccc4162216e55eacdc422dc9aaa529fddd5295d1923baf85e1ec180",
          "derived_by": "python_ast",
          "dirty": false,
          "git_oid": "00a632ac950a8c411f8d8ac90197e28191f58619",
          "id": "prov:4de3689c602c27c8",
          "line_end": 87,
          "line_start": 85,
          "path": "src/fmc_mcp/server.py",
          "source_type": "file"
        }
      ],
      "symbol": "fmc_mcp.server.deployment_status_resource",
      "tags": []
    },
    {
      "id": "node:0f2924d0972b4ea19f44",
      "kind": "python_function",
      "label": "system_info_resource",
      "path": "src/fmc_mcp/server.py",
      "provenance_refs": [
        {
          "confidence": "deterministic",
          "content_hash": "43a848b0fccc4162216e55eacdc422dc9aaa529fddd5295d1923baf85e1ec180",
          "derived_by": "python_ast",
          "dirty": false,
          "git_oid": "00a632ac950a8c411f8d8ac90197e28191f58619",
          "id": "prov:9044166d96fafc27",
          "line_end": 69,
          "line_start": 67,
          "path": "src/fmc_mcp/server.py",
          "source_type": "file"
        }
      ],
      "symbol": "fmc_mcp.server.system_info_resource",
      "tags": []
    },
    {
      "id": "node:127af2b0f9d32f8164c6",
      "kind": "python_module",
      "label": "fmc_mcp",
      "path": "src/fmc_mcp/__init__.py",
      "provenance_refs": [
        {
          "confidence": "deterministic",
          "content_hash": "e3b410a40e58a96510ea9292af866db1c2a7df6d1361a1b377524fc7e9c0d927",
          "derived_by": "python_ast",
          "dirty": false,
          "git_oid": "00a632ac950a8c411f8d8ac90197e28191f58619",
          "id": "prov:aeec7a1dae758e4e",
          "line_end": 7,
          "line_start": 1,
          "path": "src/fmc_mcp/__init__.py",
          "source_type": "file"
        }
      ],
      "symbol": "fmc_mcp",
      "tags": []
    },
    {
      "id": "node:129f8a03fb8f09f4c107",
      "kind": "python_function",
      "label": "_authenticate",
      "path": "src/fmc_mcp/client.py",
      "provenance_refs": [
        {
          "confidence": "deterministic",
          "content_hash": "a86716583c10e80add24766ae14f0f4392ed61dc5ac69753c0a4d81d442689a2",
          "derived_by": "python_ast",
          "dirty": false,
          "git_oid": "00a632ac950a8c411f8d8ac90197e28191f58619",
          "id": "prov:4a7607b917067ce1",
          "line_end": 168,
          "line_start": 136,
          "path": "src/fmc_mcp/client.py",
          "source_type": "file"
        }
      ],
      "symbol": "fmc_mcp.client._authenticate",
      "tags": []
    },
    {
      "id": "node:136a3d4798dcdcba19ed",
      "kind": "python_function",
      "label": "list_devices",
      "path": "src/fmc_mcp/resources.py",
      "provenance_refs": [
        {
          "confidence": "deterministic",
          "content_hash": "259e9b783053fa5b30c8f74ce995551396615a1d18314cf3ea902574b48b00ea",
          "derived_by": "python_ast",
          "dirty": false,
          "git_oid": "00a632ac950a8c411f8d8ac90197e28191f58619",
          "id": "prov:bec0ec8d4b515a01",
          "line_end": 64,
          "line_start": 40,
          "path": "src/fmc_mcp/resources.py",
          "source_type": "file"
        }
      ],
      "symbol": "fmc_mcp.resources.list_devices",
      "tags": []
    },
    {
      "id": "node:1498bdfe6a32f0ebb94a",
      "kind": "python_function",
      "label": "test_list_network_objects",
      "path": "tests/test_resources.py",
      "provenance_refs": [
        {
          "confidence": "deterministic",
          "content_hash": "70e75562f3a1f919f51d21f75ac0d0fce8dda53414e9f8a590a80f162a6de0f6",
          "derived_by": "python_ast",
          "dirty": false,
          "git_oid": "00a632ac950a8c411f8d8ac90197e28191f58619",
          "id": "prov:20e2b0c7e921513b",
          "line_end": 79,
          "line_start": 70,
          "path": "tests/test_resources.py",
          "source_type": "file"
        }
      ],
      "symbol": "tests.test_resources.test_list_network_objects",
      "tags": []
    },
    {
      "id": "node:18cb6e0edd2c101a1f7d",
      "kind": "python_class",
      "label": "RateLimiter",
      "path": "src/fmc_mcp/client.py",
      "provenance_refs": [
        {
          "confidence": "deterministic",
          "content_hash": "a86716583c10e80add24766ae14f0f4392ed61dc5ac69753c0a4d81d442689a2",
          "derived_by": "python_ast",
          "dirty": false,
          "git_oid": "00a632ac950a8c411f8d8ac90197e28191f58619",
          "id": "prov:6922c4cbc76c847b",
          "line_end": 62,
          "line_start": 16,
          "path": "src/fmc_mcp/client.py",
          "source_type": "file"
        }
      ],
      "symbol": "fmc_mcp.client.RateLimiter",
      "tags": []
    },
    {
      "id": "node:1a5ef0e0e3112f273bf9",
      "kind": "markdown_section",
      "label": "Run all tests",
      "path": "README.md",
      "provenance_refs": [
        {
          "confidence": "deterministic",
          "content_hash": "4026ce04783d6813ad1c08e4c871eb3d9ffae9935f329fb553945e2eefc189f9",
          "derived_by": "markdown_parser",
          "dirty": false,
          "git_oid": "00a632ac950a8c411f8d8ac90197e28191f58619",
          "id": "prov:cae380c529d7841a",
          "line_end": 170,
          "line_start": 170,
          "path": "README.md",
          "source_type": "doc_section"
        }
      ],
      "symbol": "README.md#Run all tests",
      "tags": []
    },
    {
      "id": "node:1d2a834c8820935eace9",
      "kind": "markdown_section",
      "label": "Or using the CLI entry point",
      "path": "README.md",
      "provenance_refs": [
        {
          "confidence": "deterministic",
          "content_hash": "4026ce04783d6813ad1c08e4c871eb3d9ffae9935f329fb553945e2eefc189f9",
          "derived_by": "markdown_parser",
          "dirty": false,
          "git_oid": "00a632ac950a8c411f8d8ac90197e28191f58619",
          "id": "prov:88928758b6659453",
          "line_end": 95,
          "line_start": 95,
          "path": "README.md",
          "source_type": "doc_section"
        }
      ],
      "symbol": "README.md#Or using the CLI entry point",
      "tags": []
    },
    {
      "id": "node:1d75af7c314b243d00a0",
      "kind": "markdown_section",
      "label": "Configuration",
      "path": "README.md",
      "provenance_refs": [
        {
          "confidence": "deterministic",
          "content_hash": "4026ce04783d6813ad1c08e4c871eb3d9ffae9935f329fb553945e2eefc189f9",
          "derived_by": "markdown_parser",
          "dirty": false,
          "git_oid": "00a632ac950a8c411f8d8ac90197e28191f58619",
          "id": "prov:be98bfb144d0d63d",
          "line_end": 55,
          "line_start": 55,
          "path": "README.md",
          "source_type": "doc_section"
        }
      ],
      "symbol": "README.md#Configuration",
      "tags": []
    },
    {
      "id": "node:1efcc1df855ff3e35524",
      "kind": "markdown_section",
      "label": "Code Quality",
      "path": "README.md",
      "provenance_refs": [
        {
          "confidence": "deterministic",
          "content_hash": "4026ce04783d6813ad1c08e4c871eb3d9ffae9935f329fb553945e2eefc189f9",
          "derived_by": "markdown_parser",
          "dirty": false,
          "git_oid": "00a632ac950a8c411f8d8ac90197e28191f58619",
          "id": "prov:de1084c7bd850c00",
          "line_end": 177,
          "line_start": 177,
          "path": "README.md",
          "source_type": "doc_section"
        }
      ],
      "symbol": "README.md#Code Quality",
      "tags": []
    },
    {
      "id": "node:1f10c097e41d6872b3bb",
      "kind": "file",
      "label": "src/fmc_mcp/__init__.py",
      "path": "src/fmc_mcp/__init__.py",
      "provenance_refs": [
        {
          "confidence": "deterministic",
          "content_hash": "e3b410a40e58a96510ea9292af866db1c2a7df6d1361a1b377524fc7e9c0d927",
          "derived_by": "filesystem",
          "dirty": false,
          "git_oid": "00a632ac950a8c411f8d8ac90197e28191f58619",
          "id": "prov:b4741bc92619f465",
          "line_end": 7,
          "line_start": 1,
          "path": "src/fmc_mcp/__init__.py",
          "source_type": "file"
        }
      ],
      "symbol": null,
      "tags": []
    },
    {
      "id": "node:21d196f71ac6bb3d518a",
      "kind": "markdown_section",
      "label": "Security Notes",
      "path": "README.md",
      "provenance_refs": [
        {
          "confidence": "deterministic",
          "content_hash": "4026ce04783d6813ad1c08e4c871eb3d9ffae9935f329fb553945e2eefc189f9",
          "derived_by": "markdown_parser",
          "dirty": false,
          "git_oid": "00a632ac950a8c411f8d8ac90197e28191f58619",
          "id": "prov:7f1ebd28e645bb3d",
          "line_end": 203,
          "line_start": 203,
          "path": "README.md",
          "source_type": "doc_section"
        }
      ],
      "symbol": "README.md#Security Notes",
      "tags": []
    },
    {
      "id": "node:242462366792e6c85ea0",
      "kind": "markdown_section",
      "label": "Development",
      "path": "README.md",
      "provenance_refs": [
        {
          "confidence": "deterministic",
          "content_hash": "4026ce04783d6813ad1c08e4c871eb3d9ffae9935f329fb553945e2eefc189f9",
          "derived_by": "markdown_parser",
          "dirty": false,
          "git_oid": "00a632ac950a8c411f8d8ac90197e28191f58619",
          "id": "prov:b8550b04f85c10ae",
          "line_end": 165,
          "line_start": 165,
          "path": "README.md",
          "source_type": "doc_section"
        }
      ],
      "symbol": "README.md#Development",
      "tags": []
    },
    {
      "id": "node:24b7fac72b5fafcca05d",
      "kind": "python_function",
      "label": "test_connection",
      "path": "src/fmc_mcp/client.py",
      "provenance_refs": [
        {
          "confidence": "deterministic",
          "content_hash": "a86716583c10e80add24766ae14f0f4392ed61dc5ac69753c0a4d81d442689a2",
          "derived_by": "python_ast",
          "dirty": false,
          "git_oid": "00a632ac950a8c411f8d8ac90197e28191f58619",
          "id": "prov:92742fc0a75e8da2",
          "line_end": 371,
          "line_start": 365,
          "path": "src/fmc_mcp/client.py",
          "source_type": "file"
        }
      ],
      "symbol": "fmc_mcp.client.test_connection",
      "tags": []
    },
    {
      "id": "node:257d836fb3f003e3e2c2",
      "kind": "python_module",
      "label": "fmc_mcp.config",
      "path": "src/fmc_mcp/config.py",
      "provenance_refs": [
        {
          "confidence": "deterministic",
          "content_hash": "f83817eb06683ce22213016ca31e89076ac8fe68e0d0255d11e1752472d57cba",
          "derived_by": "python_ast",
          "dirty": false,
          "git_oid": "00a632ac950a8c411f8d8ac90197e28191f58619",
          "id": "prov:b380701c2879efce",
          "line_end": 57,
          "line_start": 1,
          "path": "src/fmc_mcp/config.py",
          "source_type": "file"
        }
      ],
      "symbol": "fmc_mcp.config",
      "tags": []
    },
    {
      "id": "node:2931ded44efc706fee80",
      "kind": "python_function",
      "label": "initialized_client",
      "path": "tests/test_resources.py",
      "provenance_refs": [
        {
          "confidence": "deterministic",
          "content_hash": "70e75562f3a1f919f51d21f75ac0d0fce8dda53414e9f8a590a80f162a6de0f6",
          "derived_by": "python_ast",
          "dirty": false,
          "git_oid": "00a632ac950a8c411f8d8ac90197e28191f58619",
          "id": "prov:33210c991062bd14",
          "line_end": 34,
          "line_start": 14,
          "path": "tests/test_resources.py",
          "source_type": "file"
        }
      ],
      "symbol": "tests.test_resources.initialized_client",
      "tags": []
    },
    {
      "id": "node:2de54a4e65b20280ce26",
      "kind": "python_function",
      "label": "mock_server_version",
      "path": "tests/conftest.py",
      "provenance_refs": [
        {
          "confidence": "deterministic",
          "content_hash": "0d437b7a9fc1827e52264b387a7dc2fa59689cf5b0c63b2412f71aed09f974cd",
          "derived_by": "python_ast",
          "dirty": false,
          "git_oid": "00a632ac950a8c411f8d8ac90197e28191f58619",
          "id": "prov:6766d512b10bb683",
          "line_end": 56,
          "line_start": 46,
          "path": "tests/conftest.py",
          "source_type": "file"
        }
      ],
      "symbol": "tests.conftest.mock_server_version",
      "tags": []
    },
    {
      "id": "node:2dfb6c0f7f92da0973b4",
      "kind": "python_function",
      "label": "search_object_by_ip",
      "path": "src/fmc_mcp/server.py",
      "provenance_refs": [
        {
          "confidence": "deterministic",
          "content_hash": "43a848b0fccc4162216e55eacdc422dc9aaa529fddd5295d1923baf85e1ec180",
          "derived_by": "python_ast",
          "dirty": false,
          "git_oid": "00a632ac950a8c411f8d8ac90197e28191f58619",
          "id": "prov:85323dd67853d257",
          "line_end": 101,
          "line_start": 92,
          "path": "src/fmc_mcp/server.py",
          "source_type": "file"
        }
      ],
      "symbol": "fmc_mcp.server.search_object_by_ip",
      "tags": []
    }
  ],
  "sample_edges": [
    {
      "confidence": "deterministic",
      "derived_by": "project_graph",
      "from_node_id": "node:853dc2d2ace128c51380",
      "id": "edge:0042063de7ec2e8f5a05",
      "kind": "contains",
      "label": "contains",
      "provenance_refs": [
        {
          "confidence": "deterministic",
          "content_hash": "a86716583c10e80add24766ae14f0f4392ed61dc5ac69753c0a4d81d442689a2",
          "derived_by": "filesystem",
          "dirty": false,
          "git_oid": "00a632ac950a8c411f8d8ac90197e28191f58619",
          "id": "prov:cb622961650cd965",
          "line_end": 371,
          "line_start": 1,
          "path": "src/fmc_mcp/client.py",
          "source_type": "file"
        }
      ],
      "to_node_id": "node:9e6f4be5a0a17edb1a5d"
    },
    {
      "confidence": "deterministic",
      "derived_by": "project_graph",
      "from_node_id": "node:98dc68c534a0acf6545d",
      "id": "edge:016cab9070b08ca6d0f8",
      "kind": "defined_in",
      "label": "defined_in",
      "provenance_refs": [
        {
          "confidence": "deterministic",
          "content_hash": "2b585e7273f0a996d81fb0f3fb421ebde5bd5add5c87129a50667b79316930ec",
          "derived_by": "python_ast",
          "dirty": false,
          "git_oid": "00a632ac950a8c411f8d8ac90197e28191f58619",
          "id": "prov:74a62232073e2d4d",
          "line_end": 89,
          "line_start": 78,
          "path": "tests/test_client.py",
          "source_type": "file"
        }
      ],
      "to_node_id": "node:8ff2e095ade3b2a987b8"
    },
    {
      "confidence": "deterministic",
      "derived_by": "project_graph",
      "from_node_id": "node:b74698bb7eda4aa768bd",

```

## Pilot: 2026-06-04-ai-first-project-decomposer-pilot-held-out

### repo-state.json

```text
{
  "branch": {
    "command": "git branch --show-current",
    "cwd": "/home/leonb/projects/leonbreukelman-engineer",
    "returncode": 0,
    "stderr": "",
    "stdout": "main\n"
  },
  "git_toplevel": {
    "command": "git rev-parse --show-toplevel",
    "cwd": "/home/leonb/projects/leonbreukelman-engineer",
    "returncode": 0,
    "stderr": "",
    "stdout": "/home/leonb/projects/leonbreukelman-engineer\n"
  },
  "pwd": {
    "command": "pwd",
    "cwd": "/home/leonb/projects/leonbreukelman-engineer",
    "returncode": 0,
    "stderr": "",
    "stdout": "/home/leonb/projects/leonbreukelman-engineer\n"
  },
  "repo": "/home/leonb/projects/leonbreukelman-engineer",
  "selection_note": "Required pilot 3: clean Leon-owned public-site/agent-metadata repo, JavaScript/Python/static-data shape differs from Build Arena and FMC-MCP.",
  "status_short": {
    "command": "git status --short",
    "cwd": "/home/leonb/projects/leonbreukelman-engineer",
    "returncode": 0,
    "stderr": "",
    "stdout": ""
  }
}
```

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
# leonbreukelman-engineer pilot semantic plausibility check

Repo: `/home/leonb/projects/leonbreukelman-engineer`
Snapshot: `/home/leonb/projects/build-arena/docs/verification/2026-06-04-ai-first-project-decomposer-pilot-held-out/snapshot-6844d7f53c770da9`
Local verification return code: `0`
Gate passed: `True`

## Components
- `component.worker` — Worker responsibility
  - owned evidence: worker
  - tags: none
  - contracts: ['contract.component-worker-component-worker-mcp-server']; checks: ['check.local-tests']; gaps: none
- `component.worker-mcp-server` — Worker Mcp Server responsibility
  - owned evidence: worker.mcp.server
  - tags: none
  - contracts: ['contract.component-worker-component-worker-mcp-server']; checks: ['check.local-tests']; gaps: none
- `component.scripts-build` — Scripts Build responsibility
  - owned evidence: scripts.build
  - tags: none
  - contracts: none; checks: ['check.local-tests']; gaps: none
- `component.scripts-check-public-links` — Scripts Check Public Links responsibility
  - owned evidence: scripts.check-public-links
  - tags: none
  - contracts: none; checks: ['check.local-tests']; gaps: none

## Contracts
- `contract.component-worker-component-worker-mcp-server` component.worker -> component.worker-mcp-server via `imports worker.mcp.server`

## Assessment
- Components are graph-backed source responsibility units, not broad file buckets.
- Contracts are deterministic import edges when available.
- Observable checks are local safe commands recorded in this pilot.
- Protected/generated/excluded surfaces are not owned as primary components.
- Verification gaps remain explicit in the snapshot/gate model rather than silently accepted.

```

### snapshot-command-final.json

```text
{
  "command": "uv run python -m arena.project_model_cli snapshot --project /home/leonb/projects/leonbreukelman-engineer --artifacts-root /home/leonb/projects/build-arena/docs/verification/2026-06-04-ai-first-project-decomposer-pilot-held-out --project-id leonbreukelman-engineer --source-task 'leonbreukelman-engineer AI-first decomposer pilot' --primary-backlog-item pilot-leonbreukelman-engineer --goal 'decompose the AI-first public site and agent metadata project into source-backed components across build scripts, JavaScript worker code, public JSON data, templates, and docs' --llm-mode fixture --overwrite --non-goal 'do not treat generated dist output as source ownership' --non-goal 'do not require Cloudflare deployment or public mutation'",
  "cwd": "/home/leonb/projects/build-arena",
  "returncode": 0,
  "stdout": "{\"gate_report_path\": \"/home/leonb/projects/build-arena/docs/verification/2026-06-04-ai-first-project-decomposer-pilot-held-out/snapshot-6844d7f53c770da9/gate-report.json\", \"manifest_path\": \"/home/leonb/projects/build-arena/docs/verification/2026-06-04-ai-first-project-decomposer-pilot-held-out/snapshot-6844d7f53c770da9/manifest.json\", \"passed\": true, \"snapshot_dir\": \"/home/leonb/projects/build-arena/docs/verification/2026-06-04-ai-first-project-decomposer-pilot-held-out/snapshot-6844d7f53c770da9\", \"snapshot_id\": \"snapshot-6844d7f53c770da9\", \"violation_count\": 0}\n",
  "stderr": ""
}
```

### latest/snapshot.json

```json
{
  "project_id": "leonbreukelman-engineer",
  "primary_model_id": "fixture-good-model",
  "components": [
    {
      "check_ids": [
        "check.local-tests"
      ],
      "contract_ids": [
        "contract.component-worker-component-worker-mcp-server"
      ],
      "id": "component.worker",
      "name": "Worker responsibility",
      "owned_node_ids": [
        "node:32f3a0d3845cf98fb8cb"
      ],
      "provenance_refs": [
        "prov:ea0068ba73266e60"
      ],
      "responsibility": "Own the responsibility represented by `worker` and expose it through graph-resolvable code evidence.",
      "verification_gap_ids": []
    },
    {
      "check_ids": [
        "check.local-tests"
      ],
      "contract_ids": [
        "contract.component-worker-component-worker-mcp-server"
      ],
      "id": "component.worker-mcp-server",
      "name": "Worker Mcp Server responsibility",
      "owned_node_ids": [
        "node:1e8ba7fd1db36d8f49db"
      ],
      "provenance_refs": [
        "prov:e8c798459ce07e15"
      ],
      "responsibility": "Own the responsibility represented by `worker.mcp.server` and expose it through graph-resolvable code evidence.",
      "verification_gap_ids": []
    },
    {
      "check_ids": [
        "check.local-tests"
      ],
      "contract_ids": [],
      "id": "component.scripts-build",
      "name": "Scripts Build responsibility",
      "owned_node_ids": [
        "node:d8fc3a88afab17188e7b"
      ],
      "provenance_refs": [
        "prov:8c73e6d6bb2288db"
      ],
      "responsibility": "Own the responsibility represented by `scripts.build` and expose it through graph-resolvable code evidence.",
      "verification_gap_ids": []
    },
    {
      "check_ids": [
        "check.local-tests"
      ],
      "contract_ids": [],
      "id": "component.scripts-check-public-links",
      "name": "Scripts Check Public Links responsibility",
      "owned_node_ids": [
        "node:d1ab9b8e0eb01b071904"
      ],
      "provenance_refs": [
        "prov:cc1fa9e22afc08c6"
      ],
      "responsibility": "Own the responsibility represented by `scripts.check-public-links` and expose it through graph-resolvable code evidence.",
      "verification_gap_ids": []
    }
  ],
  "contracts": [
    {
      "from_component_id": "component.worker",
      "id": "contract.component-worker-component-worker-mcp-server",
      "name": "component.worker imports component.worker-mcp-server",
      "near_neighbor_alternative_ids": [
        "near.primary-path-bucket"
      ],
      "provenance_refs": [
        "prov:ea0068ba73266e60",
        "prov:e8c798459ce07e15"
      ],
      "supporting_edge_ids": [
        "edge:ee74e56eeab2c21d6122"
      ],
      "to_component_id": "component.worker-mcp-server"
    }
  ],
  "cross_cutting_concerns": [
    {
      "category": "anti_fabrication",
      "component_ids": [
        "component.worker",
        "component.worker-mcp-server",
        "component.scripts-build",
        "component.scripts-check-public-links"
      ],
      "contract_ids": [
        "contract.component-worker-component-worker-mcp-server"
      ],
      "description": "Accepted decomposition claims must trace to graph provenance.",
      "id": "concern.anti-fabrication",
      "provenance_refs": [
        "prov:ea0068ba73266e60"
      ],
      "triggered_by": []
    },
    {
      "category": "determinism",
      "component_ids": [
        "component.worker",
        "component.worker-mcp-server",
        "component.scripts-build",
        "component.scripts-check-public-links"
      ],
      "contract_ids": [],
      "description": "Snapshot artifacts are canonical and gateable without live APIs.",
      "id": "concern.determinism",
      "provenance_refs": [
        "prov:ea0068ba73266e60"
      ],
      "triggered_by": []
    },
    {
      "category": "provenance",
      "component_ids": [
        "component.worker",
        "component.worker-mcp-server",
        "component.scripts-build",
        "component.scripts-check-public-links"
      ],
      "contract_ids": [
        "contract.component-worker-component-worker-mcp-server"
      ],
      "description": "Graph-derived evidence backs each accepted component and contract.",
      "id": "concern.provenance",
      "provenance_refs": [
        "prov:ea0068ba73266e60"
      ],
      "triggered_by": []
    },
    {
      "category": "no_live_paid_api_acceptance",
      "component_ids": [
        "component.worker",
        "component.worker-mcp-server",
        "component.scripts-build",
        "component.scripts-check-public-links"
      ],
      "contract_ids": [],
      "description": "Acceptance checks are local and allowlisted.",
      "id": "concern.no-live-paid-api",
      "provenance_refs": [
        "prov:4748fccbacbd25ea"
      ],
      "triggered_by": []
    }
  ],
  "observable_checks": [
    {
      "acceptance_command_id": "local-pytest",
      "command": "uv run pytest -q",
      "component_ids": [
        "component.worker",
        "component.worker-mcp-server",
        "component.scripts-build",
        "component.scripts-check-public-links"
      ],
      "contract_ids": [
        "contract.component-worker-component-worker-mcp-server"
      ],
      "description": "Run the local deterministic test suite or nearest safe local check.",
      "id": "check.local-tests",
      "provenance_refs": [
        "prov:4748fccbacbd25ea"
      ],
      "requires_network": false,
      "requires_paid_api": false,
      "safe_to_run_by_default": true
    }
  ],
  "held_out_probes": [
    {
      "builder_independent_from_decomposer": true,
      "builder_model_id": "fixture-independent-probe-builder",
      "builder_prompt_hash": "fixture-probe-hash",
      "discrimination_passed": true,
      "golden_control_passed": true,
      "hidden_from_primary_decomposer": true,
      "id": "probe.primary-file-bucket-negative",
      "planted_negative_id": "negative.fluent-file-bucket",
      "provenance_refs": [
        "prov:ea0068ba73266e60"
      ],
      "target_component_ids": [
        "component.worker"
      ],
      "target_contract_ids": [
        "contract.component-worker-component-worker-mcp-server"
      ]
    }
  ],
  "verification_gaps": [],
  "near_neighbor_alternatives": [
    {
      "alternative": "Treat adjacent files as one polished bucket.",
      "id": "near.primary-path-bucket",
      "provenance_refs": [
        "prov:ea0068ba73266e60"
      ],
      "target_id": "contract.component-worker-component-worker-mcp-server",
      "why_not_primary": "The goal requires responsibility-bearing components, and the non-goal forbids file buckets: do not treat generated dist output as source ownership."
    }
  ]
}
```

### latest/gate-report.json

```json
{
  "passed": true,
  "violations": []
}
```

### latest/graph.json

```json
{
  "schema_version": "project-graph/v0.1",
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
  "sample_nodes": [
    {
      "id": "node:016549f456f6ba3ecbb6",
      "kind": "file",
      "label": "templates/human/services.html",
      "path": "templates/human/services.html",
      "provenance_refs": [
        {
          "confidence": "deterministic",
          "content_hash": "619baf7c904626869c61e7b0d2983659ae995c169ce829e18dca31e1a6d78fda",
          "derived_by": "filesystem",
          "dirty": false,
          "git_oid": "63fabf075f29610f80eb326c7b2a644ec5891cbb",
          "id": "prov:a426998abe16a1d3",
          "line_end": 50,
          "line_start": 1,
          "path": "templates/human/services.html",
          "source_type": "file"
        }
      ],
      "symbol": null,
      "tags": []
    },
    {
      "id": "node:087085bf23e3cc4628f2",
      "kind": "markdown_section",
      "label": "What He Is Less Good At",
      "path": "prompt/represent_me.md",
      "provenance_refs": [
        {
          "confidence": "deterministic",
          "content_hash": "7a2d4255ca67bfc01eccc247a76ac812fe7ca59c211497da67db8c10316a87ae",
          "derived_by": "markdown_parser",
          "dirty": false,
          "git_oid": "63fabf075f29610f80eb326c7b2a644ec5891cbb",
          "id": "prov:505ad7266a711b66",
          "line_end": 55,
          "line_start": 55,
          "path": "prompt/represent_me.md",
          "source_type": "doc_section"
        }
      ],
      "symbol": "prompt/represent_me.md#What He Is Less Good At",
      "tags": []
    },
    {
      "id": "node:0b296c8c603b4645bd9d",
      "kind": "python_function",
      "label": "render_page",
      "path": "scripts/build.py",
      "provenance_refs": [
        {
          "confidence": "deterministic",
          "content_hash": "1dbfb30e20f3e171666c97ff15be753cbde042f775eecae8770ccfbbc4753e03",
          "derived_by": "python_ast",
          "dirty": false,
          "git_oid": "63fabf075f29610f80eb326c7b2a644ec5891cbb",
          "id": "prov:171ec312e6eb8703",
          "line_end": 48,
          "line_start": 44,
          "path": "scripts/build.py",
          "source_type": "file"
        }
      ],
      "symbol": "scripts.build.render_page",
      "tags": []
    },
    {
      "id": "node:0e05f1db4adb3bbc9e83",
      "kind": "markdown_section",
      "label": "Strategy Decision",
      "path": "docs/plans/2026-05-09-income-oriented-ai-first-refactor.md",
      "provenance_refs": [
        {
          "confidence": "deterministic",
          "content_hash": "bbd48d3fb1fa32ac51407470e08772488e76502499a5f761b5bab294e7c64db3",
          "derived_by": "markdown_parser",
          "dirty": false,
          "git_oid": "63fabf075f29610f80eb326c7b2a644ec5891cbb",
          "id": "prov:edfff9996d5380e1",
          "line_end": 11,
          "line_start": 11,
          "path": "docs/plans/2026-05-09-income-oriented-ai-first-refactor.md",
          "source_type": "doc_section"
        }
      ],
      "symbol": "docs/plans/2026-05-09-income-oriented-ai-first-refactor.md#Strategy Decision",
      "tags": []
    },
    {
      "id": "node:0f29b2589c8192bfd049",
      "kind": "python_function",
      "label": "test_worker_returns_gone_for_retired_article_routes",
      "path": "tests/test_public_contract.py",
      "provenance_refs": [
        {
          "confidence": "deterministic",
          "content_hash": "d1c374ffe9f565ae456c447573cf9ce61f8adb8d8054186e4748c493733fdf74",
          "derived_by": "python_ast",
          "dirty": false,
          "git_oid": "63fabf075f29610f80eb326c7b2a644ec5891cbb",
          "id": "prov:b3a339052ff65c4a",
          "line_end": 89,
          "line_start": 80,
          "path": "tests/test_public_contract.py",
          "source_type": "file"
        }
      ],
      "symbol": "tests.test_public_contract.test_worker_returns_gone_for_retired_article_routes",
      "tags": []
    },
    {
      "id": "node:14b22207cea9242c6f34",
      "kind": "config",
      "label": "api/v1/projects.json",
      "path": "api/v1/projects.json",
      "provenance_refs": [
        {
          "confidence": "deterministic",
          "content_hash": "3c232b5eef279854ceafb395064ab4ac3b602b361fcf34951690b88f2836b78e",
          "derived_by": "filesystem",
          "dirty": false,
          "git_oid": "63fabf075f29610f80eb326c7b2a644ec5891cbb",
          "id": "prov:c6056aa2fba92b85",
          "line_end": 73,
          "line_start": 1,
          "path": "api/v1/projects.json",
          "source_type": "file"
        }
      ],
      "symbol": null,
      "tags": []
    },
    {
      "id": "node:151cf959b51dafbd619e",
      "kind": "config",
      "label": "well-known/agent-card.json",
      "path": "well-known/agent-card.json",
      "provenance_refs": [
        {
          "confidence": "deterministic",
          "content_hash": "89706b0c13f3dfe1df9ecde46d75d8ee3452994a3b18024b0b4f1ac661d86fad",
          "derived_by": "filesystem",
          "dirty": false,
          "git_oid": "63fabf075f29610f80eb326c7b2a644ec5891cbb",
          "id": "prov:813acff12ec619c1",
          "line_end": 109,
          "line_start": 1,
          "path": "well-known/agent-card.json",
          "source_type": "file"
        }
      ],
      "symbol": null,
      "tags": []
    },
    {
      "id": "node:177414d555e0bb8188d6",
      "kind": "file",
      "label": "scripts/build.py",
      "path": "scripts/build.py",
      "provenance_refs": [
        {
          "confidence": "deterministic",
          "content_hash": "1dbfb30e20f3e171666c97ff15be753cbde042f775eecae8770ccfbbc4753e03",
          "derived_by": "filesystem",
          "dirty": false,
          "git_oid": "63fabf075f29610f80eb326c7b2a644ec5891cbb",
          "id": "prov:d181fbbe3ffc8c31",
          "line_end": 163,
          "line_start": 1,
          "path": "scripts/build.py",
          "source_type": "file"
        }
      ],
      "symbol": null,
      "tags": []
    },
    {
      "id": "node:182d7abe7007643cd122",
      "kind": "python_function",
      "label": "setup_jinja",
      "path": "scripts/build.py",
      "provenance_refs": [
        {
          "confidence": "deterministic",
          "content_hash": "1dbfb30e20f3e171666c97ff15be753cbde042f775eecae8770ccfbbc4753e03",
          "derived_by": "python_ast",
          "dirty": false,
          "git_oid": "63fabf075f29610f80eb326c7b2a644ec5891cbb",
          "id": "prov:84fab95b9de823c6",
          "line_end": 41,
          "line_start": 37,
          "path": "scripts/build.py",
          "source_type": "file"
        }
      ],
      "symbol": "scripts.build.setup_jinja",
      "tags": []
    },
    {
      "id": "node:19cc14e2a3828fc1d1f4",
      "kind": "file",
      "label": "worker/index.js",
      "path": "worker/index.js",
      "provenance_refs": [
        {
          "confidence": "deterministic",
          "content_hash": "eb5094f5cdaebb154b48ca06dfbddd52646968c36bbfca9395a4d5857594011f",
          "derived_by": "filesystem",
          "dirty": false,
          "git_oid": "63fabf075f29610f80eb326c7b2a644ec5891cbb",
          "id": "prov:609857db3c01b3a6",
          "line_end": 147,
          "line_start": 1,
          "path": "worker/index.js",
          "source_type": "file"
        }
      ],
      "symbol": null,
      "tags": []
    },
    {
      "id": "node:1a2e01373efe55ff7c11",
      "kind": "markdown_section",
      "label": "Risks",
      "path": "docs/plans/2026-05-09-income-oriented-ai-first-refactor.md",
      "provenance_refs": [
        {
          "confidence": "deterministic",
          "content_hash": "bbd48d3fb1fa32ac51407470e08772488e76502499a5f761b5bab294e7c64db3",
          "derived_by": "markdown_parser",
          "dirty": false,
          "git_oid": "63fabf075f29610f80eb326c7b2a644ec5891cbb",
          "id": "prov:df7a443405848b30",
          "line_end": 116,
          "line_start": 116,
          "path": "docs/plans/2026-05-09-income-oriented-ai-first-refactor.md",
          "source_type": "doc_section"
        }
      ],
      "symbol": "docs/plans/2026-05-09-income-oriented-ai-first-refactor.md#Risks",
      "tags": []
    },
    {
      "id": "node:1c5a6f0459fa5b83d040",
      "kind": "markdown_section",
      "label": "Quick Start",
      "path": "README.md",
      "provenance_refs": [
        {
          "confidence": "deterministic",
          "content_hash": "da8338ce170047944572d052c65315740173ba250c7687f0233ad79c65d4368c",
          "derived_by": "markdown_parser",
          "dirty": false,
          "git_oid": "63fabf075f29610f80eb326c7b2a644ec5891cbb",
          "id": "prov:fa04b24fd751aac4",
          "line_end": 5,
          "line_start": 5,
          "path": "README.md",
          "source_type": "doc_section"
        }
      ],
      "symbol": "README.md#Quick Start",
      "tags": []
    },
    {
      "id": "node:1d60c7274d548dafd5d3",
      "kind": "markdown_section",
      "label": "Humble Positioning and Social De-integration Plan",
      "path": "docs/plans/2026-05-10-humble-positioning-social-deintegration.md",
      "provenance_refs": [
        {
          "confidence": "deterministic",
          "content_hash": "6bb5304f18c132f6b48bb96aecdb53e48b63e66ca0b524f6a925398e0fc5dc0f",
          "derived_by": "markdown_parser",
          "dirty": false,
          "git_oid": "63fabf075f29610f80eb326c7b2a644ec5891cbb",
          "id": "prov:8a927950f229cc59",
          "line_end": 1,
          "line_start": 1,
          "path": "docs/plans/2026-05-10-humble-positioning-social-deintegration.md",
          "source_type": "doc_section"
        }
      ],
      "symbol": "docs/plans/2026-05-10-humble-positioning-social-deintegration.md#Humble Positioning and Social De-integration Plan",
      "tags": []
    },
    {
      "id": "node:1e8ba7fd1db36d8f49db",
      "kind": "javascript_module",
      "label": "worker.mcp.server",
      "path": "worker/mcp/server.js",
      "provenance_refs": [
        {
          "confidence": "deterministic",
          "content_hash": "777fe36caf41d739a653fcb0d4373de723e9692ed398fd894a3700b05da727d9",
          "derived_by": "javascript_regex",
          "dirty": false,
          "git_oid": "63fabf075f29610f80eb326c7b2a644ec5891cbb",
          "id": "prov:e8c798459ce07e15",
          "line_end": 261,
          "line_start": 1,
          "path": "worker/mcp/server.js",
          "source_type": "file"
        }
      ],
      "symbol": "worker.mcp.server",
      "tags": []
    },
    {
      "id": "node:1f369583c733a0e4788e",
      "kind": "markdown_section",
      "label": "Task 2: Remove article build path and add work/services generation",
      "path": "docs/plans/2026-05-09-income-oriented-ai-first-refactor.md",
      "provenance_refs": [
        {
          "confidence": "deterministic",
          "content_hash": "bbd48d3fb1fa32ac51407470e08772488e76502499a5f761b5bab294e7c64db3",
          "derived_by": "markdown_parser",
          "dirty": false,
          "git_oid": "63fabf075f29610f80eb326c7b2a644ec5891cbb",
          "id": "prov:86bf0c396bc0df4c",
          "line_end": 43,
          "line_start": 43,
          "path": "docs/plans/2026-05-09-income-oriented-ai-first-refactor.md",
          "source_type": "doc_section"
        }
      ],
      "symbol": "docs/plans/2026-05-09-income-oriented-ai-first-refactor.md#Task 2: Remove article build path and add work/services generation",
      "tags": []
    },
    {
      "id": "node:242462366792e6c85ea0",
      "kind": "markdown_section",
      "label": "Development",
      "path": "README.md",
      "provenance_refs": [
        {
          "confidence": "deterministic",
          "content_hash": "da8338ce170047944572d052c65315740173ba250c7687f0233ad79c65d4368c",
          "derived_by": "markdown_parser",
          "dirty": false,
          "git_oid": "63fabf075f29610f80eb326c7b2a644ec5891cbb",
          "id": "prov:cd2a7925a71a196b",
          "line_end": 48,
          "line_start": 48,
          "path": "README.md",
          "source_type": "doc_section"
        }
      ],
      "symbol": "README.md#Development",
      "tags": []
    },
    {
      "id": "node:265a520d06ab9e3d76cd",
      "kind": "python_function",
      "label": "test_public_positioning_is_humble_and_not_credential_forward",
      "path": "tests/test_public_contract.py",
      "provenance_refs": [
        {
          "confidence": "deterministic",
          "content_hash": "d1c374ffe9f565ae456c447573cf9ce61f8adb8d8054186e4748c493733fdf74",
          "derived_by": "python_ast",
          "dirty": false,
          "git_oid": "63fabf075f29610f80eb326c7b2a644ec5891cbb",
          "id": "prov:fdeaea75119ca8d3",
          "line_end": 178,
          "line_start": 123,
          "path": "tests/test_public_contract.py",
          "source_type": "file"
        }
      ],
      "symbol": "tests.test_public_contract.test_public_positioning_is_humble_and_not_credential_forward",
      "tags": []
    },
    {
      "id": "node:270b52766ba2097c3bf8",
      "kind": "file",
      "label": "prompt/represent_me.md",
      "path": "prompt/represent_me.md",
      "provenance_refs": [
        {
          "confidence": "deterministic",
          "content_hash": "7a2d4255ca67bfc01eccc247a76ac812fe7ca59c211497da67db8c10316a87ae",
          "derived_by": "filesystem",
          "dirty": false,
          "git_oid": "63fabf075f29610f80eb326c7b2a644ec5891cbb",
          "id": "prov:756f566ef137b772",
          "line_end": 78,
          "line_start": 1,
          "path": "prompt/represent_me.md",
          "source_type": "file"
        }
      ],
      "symbol": null,
      "tags": []
    },
    {
      "id": "node:2bb51f976c64d4211590",
      "kind": "python_function",
      "label": "extract_urls",
      "path": "scripts/check-public-links.py",
      "provenance_refs": [
        {
          "confidence": "deterministic",
          "content_hash": "8127b6a188f5f0c00ac25c2d75b61297ec4a073c24dfc6ef5f2664598d0d7455",
          "derived_by": "python_ast",
          "dirty": false,
          "git_oid": "63fabf075f29610f80eb326c7b2a644ec5891cbb",
          "id": "prov:d61ae4c462fc6458",
          "line_end": 60,
          "line_start": 51,
          "path": "scripts/check-public-links.py",
          "source_type": "file"
        }
      ],
      "symbol": "scripts.check-public-links.extract_urls",
      "tags": []
    },
    {
      "id": "node:2e14c1247beb5519c591",
      "kind": "file",
      "label": "scripts/build-fallback.sh",
      "path": "scripts/build-fallback.sh",
      "provenance_refs": [
        {
          "confidence": "deterministic",
          "content_hash": "7eaf81e99bd2434adaed615590b2cba9340c6531ffe6edce43a1cb93dff393dd",
          "derived_by": "filesystem",
          "dirty": false,
          "git_oid": "63fabf075f29610f80eb326c7b2a644ec5891cbb",
          "id": "prov:0383de06a8a36ed1",
          "line_end": 12,
          "line_start": 1,
          "path": "scripts/build-fallback.sh",
          "source_type": "file"
        }
      ],
      "symbol": null,
      "tags": []
    },
    {
      "id": "node:32d0bb23216b301cf16b",
      "kind": "markdown_section",
      "label": "Task 1: Contract test for the new public shape",
      "path": "docs/plans/2026-05-09-income-oriented-ai-first-refactor.md",
      "provenance_refs": [
        {
          "confidence": "deterministic",
          "content_hash": "bbd48d3fb1fa32ac51407470e08772488e76502499a5f761b5bab294e7c64db3",
          "derived_by": "markdown_parser",
          "dirty": false,
          "git_oid": "63fabf075f29610f80eb326c7b2a644ec5891cbb",
          "id": "prov:070b33867ef6318a",
          "line_end": 29,
          "line_start": 29,
          "path": "docs/plans/2026-05-09-income-oriented-ai-first-refactor.md",
          "source_type": "doc_section"
        }
      ],
      "symbol": "docs/plans/2026-05-09-income-oriented-ai-first-refactor.md#Task 1: Contract test for the new public shape",
      "tags": []
    },
    {
      "id": "node:32f3a0d3845cf98fb8cb",
      "kind": "javascript_module",
      "label": "worker",
      "path": "worker/index.js",
      "provenance_refs": [
        {
          "confidence": "deterministic",
          "content_hash": "eb5094f5cdaebb154b48ca06dfbddd52646968c36bbfca9395a4d5857594011f",
          "derived_by": "javascript_regex",
          "dirty": false,
          "git_oid": "63fabf075f29610f80eb326c7b2a644ec5891cbb",
          "id": "prov:ea0068ba73266e60",
          "line_end": 147,
          "line_start": 1,
          "path": "worker/index.js",
          "source_type": "file"
        }
      ],
      "symbol": "worker",
      "tags": []
    },
    {
      "id": "node:346f9b3cd2dde3c5d686",
      "kind": "file",
      "label": "templates/human/work.html",
      "path": "templates/human/work.html",
      "provenance_refs": [
        {
          "confidence": "deterministic",
          "content_hash": "4137fbc9bcf79b228913a988ac9524fc0dbdfe55c503692c52a0ca8d0616f041",
          "derived_by": "filesystem",
          "dirty": false,
          "git_oid": "63fabf075f29610f80eb326c7b2a644ec5891cbb",
          "id": "prov:06bd972541318fd3",
          "line_end": 54,
          "line_start": 1,
          "path": "templates/human/work.html",
          "source_type": "file"
        }
      ],
      "symbol": null,
      "tags": []
    },
    {
      "id": "node:3497d88db26b2742c66a",
      "kind": "markdown_section",
      "label": "Stories Worth Telling",
      "path": "prompt/represent_me.md",
      "provenance_refs": [
        {
          "confidence": "deterministic",
          "content_hash": "7a2d4255ca67bfc01eccc247a76ac812fe7ca59c211497da67db8c10316a87ae",
          "derived_by": "markdown_parser",
          "dirty": false,
          "git_oid": "63fabf075f29610f80eb326c7b2a644ec5891cbb",
          "id": "prov:ecf942bf7ef015fa",
          "line_end": 36,
          "line_start": 36,
          "path": "prompt/represent_me.md",
          "source_type": "doc_section"
        }
      ],
      "symbol": "prompt/represent_me.md#Stories Worth Telling",
      "tags": []
    },
    {
      "id": "node:351b0cf821ac5d85e952",
      "kind": "python_function",
      "label": "test_build_fails_closed_instead_of_falling_back_to_article_archive",
      "path": "tests/test_public_contract.py",
      "provenance_refs": [
        {
          "confidence": "deterministic",
          "content_hash": "d1c374ffe9f565ae456c447573cf9ce61f8adb8d8054186e4748c493733fdf74",
          "derived_by": "python_ast",
          "dirty": false,
          "git_oid": "63fabf075f29610f80eb326c7b2a644ec5891cbb",
          "id": "prov:97384f644806c1ae",
          "line_end": 232,
          "line_start": 225,
          "path": "tests/test_public_contract.py",
          "source_type": "file"
        }
      ],
      "symbol": "tests.test_public_contract.test_build_fails_closed_instead_of_falling_back_to_article_archive",
      "tags": []
    }
  ],
  "sample_edges": [
    {
      "confidence": "deterministic",
      "derived_by": "project_graph",
      "from_node_id": "node:14b22207cea9242c6f34",
      "id": "edge:0067e60854acb22b8307",
      "kind": "configures",
      "label": "configures",
      "provenance_refs": [
        {
          "confidence": "deterministic",
          "content_hash": "3c232b5eef279854ceafb395064ab4ac3b602b361fcf34951690b88f2836b78e",
          "derived_by": "filesystem",
          "dirty": false,
          "git_oid": "63fabf075f29610f80eb326c7b2a644ec5891
```

## Review request

Return JSON first if possible with fields: passed, critical_blockers, major_findings, minor_findings, required_repairs, acceptance_assessment. Then provide markdown explanation. Specifically attack: semantic components, real contracts, generated/protected exclusion, held-out leakage, deterministic gate weaknesses, Build Arena overfit, FMC-MCP manual evaluability, JavaScript held-out generalization, and whether acceptance can be gamed by a plausible report generator.
