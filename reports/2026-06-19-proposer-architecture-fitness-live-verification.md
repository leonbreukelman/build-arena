# Proposer architecture-fitness live verification

Raw run dir: `/tmp/build-arena-proposer-architecture-fitness-live-verify`
Summary JSON: `/home/leonb/projects/build-arena-proposer-architecture-fitness/reports/2026-06-19-proposer-architecture-fitness-live-verification.json`

## fmc-mcp route table
```tsv
finding_id	disposition	domain	target_path
agent.agents-md.missing	docs_candidate	documentation	AGENTS.md
architecture.open-questions-or-gaps	fitness_function_candidate	architecture_fitness	tests/architecture/architecture-fitness-bb5e598eb664.json
verification.quality-gates.present	consumed_as_context
decision.history.missing	docs_candidate	documentation	docs/decisions/index.md
ops.runbooks.missing	docs_candidate	documentation	docs/runbooks/index.md
```

## arena-calibration route table
```tsv
finding_id	disposition	domain	target_path
doc.index.missing	docs_candidate	documentation	docs/index.md
agent.agents-md.missing	docs_candidate	documentation	AGENTS.md
architecture.open-questions-or-gaps	advisory_backlogged	advisory_backlog	docs/agent-backlog.md
verification.quality-gates.present	consumed_as_context
decision.history.missing	docs_candidate	documentation	docs/decisions/index.md
code.quality.lint.arena/verifier.py	code_candidate	code_quality	arena/verifier.py
code.quality.lint.exercise_verifier.py	code_candidate	code_quality	exercise_verifier.py
ops.runbooks.missing	docs_candidate	documentation	docs/runbooks/index.md
```

## Real fmc-mcp architecture contract
Contract target: `tests/architecture/architecture-fitness-bb5e598eb664.json`
```json
{
  "description": "Prevent the graph-evidenced import cycle fmc_mcp -> fmc_mcp.server -> fmc_mcp.",
  "findingId": "architecture.open-questions-or-gaps",
  "forbiddenEdges": [
    {
      "from": "fmc_mcp",
      "to": "fmc_mcp.server"
    },
    {
      "from": "fmc_mcp.server",
      "to": "fmc_mcp"
    }
  ],
  "id": "architecture-fitness-bb5e598eb664",
  "kind": "forbid_import_cycle",
  "modules": [
    "fmc_mcp",
    "fmc_mcp.server"
  ],
  "schemaVersion": "architecture-fitness-contract/v0"
}
```
Graph import edges proving the cycle:
```json
[
  {
    "edge_id": "edge:c9d784d508ce31bca57a",
    "from_symbol": "fmc_mcp",
    "git_oid": "25f445806d5221f21d7ac675799db5c30499f1b7",
    "kind": "imports",
    "label": "fmc_mcp.server",
    "line_start": 5,
    "path": "src/fmc_mcp/__init__.py",
    "to_symbol": "fmc_mcp.server"
  },
  {
    "edge_id": "edge:f5439cc4db4e0ea6bf94",
    "from_symbol": "fmc_mcp.server",
    "git_oid": "25f445806d5221f21d7ac675799db5c30499f1b7",
    "kind": "imports",
    "label": "fmc_mcp",
    "line_start": 11,
    "path": "src/fmc_mcp/server.py",
    "to_symbol": "fmc_mcp"
  }
]
```
Gate output:
```json
{
  "accepted": true,
  "boundEdges": [
    {
      "from": "fmc_mcp",
      "to": "fmc_mcp.server"
    },
    {
      "from": "fmc_mcp.server",
      "to": "fmc_mcp"
    }
  ],
  "contractPath": "tests/architecture/architecture-fitness-bb5e598eb664.json",
  "currentStatus": "failing",
  "derivedFindings": [
    {
      "autonomyBoundary": "needs_code_change",
      "id": "code.change.break-import-cycle.bb5e598eb664",
      "sourceContract": "tests/architecture/architecture-fitness-bb5e598eb664.json",
      "title": "Break graph-evidenced import cycle among fmc_mcp, fmc_mcp.server"
    }
  ],
  "groundedModules": [
    "fmc_mcp",
    "fmc_mcp.server"
  ],
  "reason": "accepted"
}
```
Gate exit code: `1`

## Gate rejection reasons
- fabricated contract: `unknown_module`
- vacuous contract: `non_binding_contract`
- duplicate contract: `duplicate_contract`
- no-op backlog: `boilerplate_entry`

## Not-promoted proof
Selected candidate: `None`
Events:
```json
[
  {
    "cycle": 1,
    "payload": {
      "finding_id": "architecture.open-questions-or-gaps",
      "rank": 0,
      "reason": "fitness_guardrail_not_promotable"
    },
    "seq": 0,
    "type": "CANDIDATE_SKIPPED"
  }
]
```
Derived follow-up from accepted guardrail:
```json
[
  {
    "autonomyBoundary": "needs_code_change",
    "id": "code.change.break-import-cycle.bb5e598eb664",
    "sourceContract": "tests/architecture/architecture-fitness-bb5e598eb664.json",
    "title": "Break graph-evidenced import cycle among fmc_mcp, fmc_mcp.server"
  }
]
```

## Determinism
fmc-mcp proposal plans identical: `True`; ranked proposals identical: `True`
arena-calibration proposal plans identical: `True`; ranked proposals identical: `True`

## Additive-only docs/lint comparison against base commit
```json
{
  "arena-calibration": {
    "base_candidate_count": 6,
    "changed_common_docs_lint_candidates": [],
    "common_docs_lint_candidate_ids": [
      "agent.agents-md.missing",
      "code.quality.lint.arena/verifier.py",
      "code.quality.lint.exercise_verifier.py",
      "decision.history.missing",
      "doc.index.missing",
      "ops.runbooks.missing"
    ],
    "current_candidate_count": 7,
    "unchanged": true
  },
  "fmc-mcp": {
    "base_candidate_count": 3,
    "changed_common_docs_lint_candidates": [],
    "common_docs_lint_candidate_ids": [
      "agent.agents-md.missing",
      "decision.history.missing",
      "ops.runbooks.missing"
    ],
    "current_candidate_count": 4,
    "unchanged": true
  }
}
```

## Protected paths
```json
{
  "diff_name_only": [],
  "status_short": []
}
```

## Command log index
```json
[
  {
    "cmd": [
      "uv",
      "run",
      "python",
      "-m",
      "arena.project_model_cli",
      "snapshot",
      "--project",
      "/home/leonb/projects/fmc-mcp",
      "--artifacts-root",
      "/tmp/build-arena-proposer-architecture-fitness-live-verify/fmc-mcp/snapshot-artifacts",
      "--project-id",
      "fmc-mcp",
      "--goal",
      "Verify proposer architecture-fitness and advisory backlog routing",
      "--llm-mode",
      "fixture",
      "--overwrite"
    ],
    "cwd": "/home/leonb/projects/build-arena-proposer-architecture-fitness",
    "exit_code": 0,
    "name": "fmc-mcp-snapshot",
    "stderr_log": "/tmp/build-arena-proposer-architecture-fitness-live-verify/logs/fmc-mcp-snapshot.stderr.txt",
    "stdout_log": "/tmp/build-arena-proposer-architecture-fitness-live-verify/logs/fmc-mcp-snapshot.stdout.txt"
  },
  {
    "cmd": [
      "uv",
      "run",
      "python",
      "-m",
      "arena.project_model_cli",
      "gate",
      "--snapshot",
      "/tmp/build-arena-proposer-architecture-fitness-live-verify/fmc-mcp/snapshot-artifacts/snapshot-d54244b880d0918f/manifest.json"
    ],
    "cwd": "/home/leonb/projects/build-arena-proposer-architecture-fitness",
    "exit_code": 0,
    "name": "fmc-mcp-snapshot-gate",
    "stderr_log": "/tmp/build-arena-proposer-architecture-fitness-live-verify/logs/fmc-mcp-snapshot-gate.stderr.txt",
    "stdout_log": "/tmp/build-arena-proposer-architecture-fitness-live-verify/logs/fmc-mcp-snapshot-gate.stdout.txt"
  },
  {
    "cmd": [
      "uv",
      "run",
      "python",
      "-m",
      "arena.project_intake_scorecard",
      "--project",
      "/home/leonb/projects/fmc-mcp",
      "--snapshot",
      "/tmp/build-arena-proposer-architecture-fitness-live-verify/fmc-mcp/snapshot-artifacts/snapshot-d54244b880d0918f/project-model-v1.json",
      "--profile",
      "active-development",
      "--output",
      "/tmp/build-arena-proposer-architecture-fitness-live-verify/fmc-mcp/scorecard.json"
    ],
    "cwd": "/home/leonb/projects/build-arena-proposer-architecture-fitness",
    "exit_code": 0,
    "name": "fmc-mcp-scorecard",
    "stderr_log": "/tmp/build-arena-proposer-architecture-fitness-live-verify/logs/fmc-mcp-scorecard.stderr.txt",
    "stdout_log": "/tmp/build-arena-proposer-architecture-fitness-live-verify/logs/fmc-mcp-scorecard.stdout.txt"
  },
  {
    "cmd": [
      "uv",
      "run",
      "python",
      "-m",
      "arena.proposal_planner",
      "--project",
      "/home/leonb/projects/fmc-mcp",
      "--scorecard",
      "/tmp/build-arena-proposer-architecture-fitness-live-verify/fmc-mcp/scorecard.json",
      "--output",
      "/tmp/build-arena-proposer-architecture-fitness-live-verify/fmc-mcp/proposal-plan-1.json",
      "--max-candidates",
      "10"
    ],
    "cwd": "/home/leonb/projects/build-arena-proposer-architecture-fitness",
    "exit_code": 0,
    "name": "fmc-mcp-proposal-plan-1",
    "stderr_log": "/tmp/build-arena-proposer-architecture-fitness-live-verify/logs/fmc-mcp-proposal-plan-1.stderr.txt",
    "stdout_log": "/tmp/build-arena-proposer-architecture-fitness-live-verify/logs/fmc-mcp-proposal-plan-1.stdout.txt"
  },
  {
    "cmd": [
      "uv",
      "run",
      "python",
      "-m",
      "arena.proposal_planner",
      "--project",
      "/home/leonb/projects/fmc-mcp",
      "--scorecard",
      "/tmp/build-arena-proposer-architecture-fitness-live-verify/fmc-mcp/scorecard.json",
      "--output",
      "/tmp/build-arena-proposer-architecture-fitness-live-verify/fmc-mcp/proposal-plan-2.json",
      "--max-candidates",
      "10"
    ],
    "cwd": "/home/leonb/projects/build-arena-proposer-architecture-fitness",
    "exit_code": 0,
    "name": "fmc-mcp-proposal-plan-2",
    "stderr_log": "/tmp/build-arena-proposer-architecture-fitness-live-verify/logs/fmc-mcp-proposal-plan-2.stderr.txt",
    "stdout_log": "/tmp/build-arena-proposer-architecture-fitness-live-verify/logs/fmc-mcp-proposal-plan-2.stdout.txt"
  },
  {
    "cmd": [
      "uv",
      "run",
      "python",
      "-m",
      "arena.proposal_ranker",
      "--project",
      "/home/leonb/projects/fmc-mcp",
      "--scorecard",
      "/tmp/build-arena-proposer-architecture-fitness-live-verify/fmc-mcp/scorecard.json",
      "--output",
      "/tmp/build-arena-proposer-architecture-fitness-live-verify/fmc-mcp/ranked-proposals-1.json",
      "--max-candidates",
      "10"
    ],
    "cwd": "/home/leonb/projects/build-arena-proposer-architecture-fitness",
    "exit_code": 0,
    "name": "fmc-mcp-ranked-proposals-1",
    "stderr_log": "/tmp/build-arena-proposer-architecture-fitness-live-verify/logs/fmc-mcp-ranked-proposals-1.stderr.txt",
    "stdout_log": "/tmp/build-arena-proposer-architecture-fitness-live-verify/logs/fmc-mcp-ranked-proposals-1.stdout.txt"
  },
  {
    "cmd": [
      "uv",
      "run",
      "python",
      "-m",
      "arena.proposal_ranker",
      "--project",
      "/home/leonb/projects/fmc-mcp",
      "--scorecard",
      "/tmp/build-arena-proposer-architecture-fitness-live-verify/fmc-mcp/scorecard.json",
      "--output",
      "/tmp/build-arena-proposer-architecture-fitness-live-verify/fmc-mcp/ranked-proposals-2.json",
      "--max-candidates",
      "10"
    ],
    "cwd": "/home/leonb/projects/build-arena-proposer-architecture-fitness",
    "exit_code": 0,
    "name": "fmc-mcp-ranked-proposals-2",
    "stderr_log": "/tmp/build-arena-proposer-architecture-fitness-live-verify/logs/fmc-mcp-ranked-proposals-2.stderr.txt",
    "stdout_log": "/tmp/build-arena-proposer-architecture-fitness-live-verify/logs/fmc-mcp-ranked-proposals-2.stdout.txt"
  },
  {
    "cmd": [
      "uv",
      "run",
      "python",
      "-m",
      "arena.project_model_cli",
      "snapshot",
      "--project",
      "/home/leonb/projects/arena-calibration",
      "--artifacts-root",
      "/tmp/build-arena-proposer-architecture-fitness-live-verify/arena-calibration/snapshot-artifacts",
      "--project-id",
      "arena-calibration",
      "--goal",
      "Verify proposer architecture-fitness and advisory backlog routing",
      "--llm-mode",
      "fixture",
      "--overwrite"
    ],
    "cwd": "/home/leonb/projects/build-arena-proposer-architecture-fitness",
    "exit_code": 0,
    "name": "arena-calibration-snapshot",
    "stderr_log": "/tmp/build-arena-proposer-architecture-fitness-live-verify/logs/arena-calibration-snapshot.stderr.txt",
    "stdout_log": "/tmp/build-arena-proposer-architecture-fitness-live-verify/logs/arena-calibration-snapshot.stdout.txt"
  },
  {
    "cmd": [
      "uv",
      "run",
      "python",
      "-m",
      "arena.project_model_cli",
      "gate",
      "--snapshot",
      "/tmp/build-arena-proposer-architecture-fitness-live-verify/arena-calibration/snapshot-artifacts/snapshot-5950f57c7c56385c/manifest.json"
    ],
    "cwd": "/home/leonb/projects/build-arena-proposer-architecture-fitness",
    "exit_code": 0,
    "name": "arena-calibration-snapshot-gate",
    "stderr_log": "/tmp/build-arena-proposer-architecture-fitness-live-verify/logs/arena-calibration-snapshot-gate.stderr.txt",
    "stdout_log": "/tmp/build-arena-proposer-architecture-fitness-live-verify/logs/arena-calibration-snapshot-gate.stdout.txt"
  },
  {
    "cmd": [
      "uv",
      "run",
      "python",
      "-m",
      "arena.project_intake_scorecard",
      "--project",
      "/home/leonb/projects/arena-calibration",
      "--snapshot",
      "/tmp/build-arena-proposer-architecture-fitness-live-verify/arena-calibration/snapshot-artifacts/snapshot-5950f57c7c56385c/project-model-v1.json",
      "--profile",
      "active-development",
      "--output",
      "/tmp/build-arena-proposer-architecture-fitness-live-verify/arena-calibration/scorecard.json"
    ],
    "cwd": "/home/leonb/projects/build-arena-proposer-architecture-fitness",
    "exit_code": 0,
    "name": "arena-calibration-scorecard",
    "stderr_log": "/tmp/build-arena-proposer-architecture-fitness-live-verify/logs/arena-calibration-scorecard.stderr.txt",
    "stdout_log": "/tmp/build-arena-proposer-architecture-fitness-live-verify/logs/arena-calibration-scorecard.stdout.txt"
  },
  {
    "cmd": [
      "uv",
      "run",
      "python",
      "-m",
      "arena.proposal_planner",
      "--project",
      "/home/leonb/projects/arena-calibration",
      "--scorecard",
      "/tmp/build-arena-proposer-architecture-fitness-live-verify/arena-calibration/scorecard.json",
      "--output",
      "/tmp/build-arena-proposer-architecture-fitness-live-verify/arena-calibration/proposal-plan-1.json",
      "--max-candidates",
      "10"
    ],
    "cwd": "/home/leonb/projects/build-arena-proposer-architecture-fitness",
    "exit_code": 0,
    "name": "arena-calibration-proposal-plan-1",
    "stderr_log": "/tmp/build-arena-proposer-architecture-fitness-live-verify/logs/arena-calibration-proposal-plan-1.stderr.txt",
    "stdout_log": "/tmp/build-arena-proposer-architecture-fitness-live-verify/logs/arena-calibration-proposal-plan-1.stdout.txt"
  },
  {
    "cmd": [
      "uv",
      "run",
      "python",
      "-m",
      "arena.proposal_planner",
      "--project",
      "/home/leonb/projects/arena-calibration",
      "--scorecard",
      "/tmp/build-arena-proposer-architecture-fitness-live-verify/arena-calibration/scorecard.json",
      "--output",
      "/tmp/build-arena-proposer-architecture-fitness-live-verify/arena-calibration/proposal-plan-2.json",
      "--max-candidates",
      "10"
    ],
    "cwd": "/home/leonb/projects/build-arena-proposer-architecture-fitness",
    "exit_code": 0,
    "name": "arena-calibration-proposal-plan-2",
    "stderr_log": "/tmp/build-arena-proposer-architecture-fitness-live-verify/logs/arena-calibration-proposal-plan-2.stderr.txt",
    "stdout_log": "/tmp/build-arena-proposer-architecture-fitness-live-verify/logs/arena-calibration-proposal-plan-2.stdout.txt"
  },
  {
    "cmd": [
      "uv",
      "run",
      "python",
      "-m",
      "arena.proposal_ranker",
      "--project",
      "/home/leonb/projects/arena-calibration",
      "--scorecard",
      "/tmp/build-arena-proposer-architecture-fitness-live-verify/arena-calibration/scorecard.json",
      "--output",
      "/tmp/build-arena-proposer-architecture-fitness-live-verify/arena-calibration/ranked-proposals-1.json",
      "--max-candidates",
      "10"
    ],
    "cwd": "/home/leonb/projects/build-arena-proposer-architecture-fitness",
    "exit_code": 0,
    "name": "arena-calibration-ranked-proposals-1",
    "stderr_log": "/tmp/build-arena-proposer-architecture-fitness-live-verify/logs/arena-calibration-ranked-proposals-1.stderr.txt",
    "stdout_log": "/tmp/build-arena-proposer-architecture-fitness-live-verify/logs/arena-calibration-ranked-proposals-1.stdout.txt"
  },
  {
    "cmd": [
      "uv",
      "run",
      "python",
      "-m",
      "arena.proposal_ranker",
      "--project",
      "/home/leonb/projects/arena-calibration",
      "--scorecard",
      "/tmp/build-arena-proposer-architecture-fitness-live-verify/arena-calibration/scorecard.json",
      "--output",
      "/tmp/build-arena-proposer-architecture-fitness-live-verify/arena-calibration/ranked-proposals-2.json",
      "--max-candidates",
      "10"
    ],
    "cwd": "/home/leonb/projects/build-arena-proposer-architecture-fitness",
    "exit_code": 0,
    "name": "arena-calibration-ranked-proposals-2",
    "stderr_log": "/tmp/build-arena-proposer-architecture-fitness-live-verify/logs/arena-calibration-ranked-proposals-2.stderr.txt",
    "stdout_log": "/tmp/build-arena-proposer-architecture-fitness-live-verify/logs/arena-calibration-ranked-proposals-2.stdout.txt"
  },
  {
    "cmd": [
      "git",
      "-C",
      "/home/leonb/projects/fmc-mcp",
      "worktree",
      "add",
      "--detach",
      "/tmp/build-arena-proposer-architecture-fitness-live-verify/fmc-mcp-contract-worktree",
      "HEAD"
    ],
    "cwd": "/home/leonb/projects/build-arena-proposer-architecture-fitness",
    "exit_code": 0,
    "name": "fmc-worktree-add",
    "stderr_log": "/tmp/build-arena-proposer-architecture-fitness-live-verify/logs/fmc-worktree-add.stderr.txt",
    "stdout_log": "/tmp/build-arena-proposer-architecture-fitness-live-verify/logs/fmc-worktree-add.stdout.txt"
  },
  {
    "cmd": [
      "uv",
      "run",
      "python",
      "-m",
      "arena.architecture_fitness_gate",
      "--repo",
      "/tmp/build-arena-proposer-architecture-fitness-live-verify/fmc-mcp-contract-worktree",
      "--contract",
      "tests/architecture/architecture-fitness-bb5e598eb664.json"
    ],
    "cwd": "/home/leonb/projects/build-arena-proposer-architecture-fitness",
    "exit_code": 1,
    "name": "fmc-real-contract-gate",
    "stderr_log": "/tmp/build-arena-proposer-architecture-fitness-live-verify/logs/fmc-real-contract-gate.stderr.txt",
    "stdout_log": "/tmp/build-arena-proposer-architecture-fitness-live-verify/logs/fmc-real-contract-gate.stdout.txt"
  },
  {
    "cmd": [
      "git",
      "-C",
      "/home/leonb/projects/fmc-mcp",
      "worktree",
      "remove",
      "--force",
      "/tmp/build-arena-proposer-architecture-fitness-live-verify/fmc-mcp-contract-worktree"
    ],
    "cwd": "/home/leonb/projects/build-arena-proposer-architecture-fitness",
    "exit_code": 0,
    "name": "fmc-worktree-remove",
    "stderr_log": "/tmp/build-arena-proposer-architecture-fitness-live-verify/logs/fmc-worktree-remove.stderr.txt",
    "stdout_log": "/tmp/build-arena-proposer-architecture-fitness-live-verify/logs/fmc-worktree-remove.stdout.txt"
  },
  {
    "cmd": [
      "uv",
      "run",
      "python",
      "-m",
      "arena.architecture_fitness_gate",
      "--repo",
      "/tmp/build-arena-proposer-architecture-fitness-live-verify/gate-proofs/architecture-repo",
      "--contract",
      "tests/architecture/architecture-fitness-943bf4434d58.json"
    ],
    "cwd": "/home/leonb/projects/build-arena-proposer-architecture-fitness",
    "exit_code": 1,
    "name": "gate-proof-accepted_failing_contract",
    "stderr_log": "/tmp/build-arena-proposer-architecture-fitness-live-verify/logs/gate-proof-accepted_failing_contract.stderr.txt",
    "stdout_log": "/tmp/build-arena-proposer-architecture-fitness-live-verify/logs/gate-proof-accepted_failing_contract.stdout.txt"
  },
  {
    "cmd": [
      "uv",
      "run",
      "python",
      "-m",
      "arena.architecture_fitness_gate",
      "--repo",
      "/tmp/build-arena-proposer-architecture-fitness-live-verify/gate-proofs/architecture-repo",
      "--contract",
      "tests/architecture/architecture-fitness-f8e7a2724fe6.json"
    ],
    "cwd": "/home/leonb/projects/build-arena-proposer-architecture-fitness",
    "exit_code": 1,
    "name": "gate-proof-fabricated_contract_rejection",
    "stderr_log": "/tmp/build-arena-proposer-architecture-fitness-live-verify/logs/gate-proof-fabricated_contract_rejection.stderr.txt",
    "stdout_log": "/tmp/build-arena-proposer-architecture-fitness-live-verify/logs/gate-proof-fabricated_contract_rejection.stdout.txt"
  },
  {
    "cmd": [
      "uv",
      "run",
      "python",
      "-m",
      "arena.architecture_fitness_gate",
      "--repo",
      "/tmp/build-arena-proposer-architecture-fitness-live-verify/gate-proofs/architecture-repo",
      "--contract",
      "tests/architecture/architecture-fitness-71c19bcd649f.json"
    ],
    "cwd": "/home/leonb/projects/build-arena-proposer-architecture-fitness",
    "exit_code": 1,
    "name": "gate-proof-vacuous_contract_rejection",
    "stderr_log": "/tmp/build-arena-proposer-architecture-fitness-live-verify/logs/gate-proof-vacuous_contract_rejection.stderr.txt",
    "stdout_log": "/tmp/build-arena-proposer-architecture-fitness-live-verify/logs/gate-proof-vacuous_contract_rejection.stdout.txt"
  },
  {
    "cmd": [
      "uv",
      "run",
      "python",
      "-m",
      "arena.architecture_fitness_gate",
      "--repo",
      "/tmp/build-arena-proposer-architecture-fitness-live-verify/gate-proofs/architecture-repo",
      "--contract",
      "tests/architecture/nested/architecture-fitness-943bf4434d58.json"
    ],
    "cwd": "/home/leonb/projects/build-arena-proposer-architecture-fitness",
    "exit_code": 1,
    "name": "gate-proof-duplicate_contract_rejection",
    "stderr_log": "/tmp/build-arena-proposer-architecture-fitness-live-verify/logs/gate-proof-duplicate_contract_rejection.stderr.txt",
    "stdout_log": "/tmp/build-arena-proposer-architecture-fitness-live-verify/logs/gate-proof-duplicate_contract_rejection.stdout.txt"
  },
  {
    "cmd": [
      "uv",
      "run",
      "python",
      "-m",
      "arena.backlog_gate",
      "--repo",
      "/tmp/build-arena-proposer-architecture-fitness-live-verify/gate-proofs/backlog-repo",
      "--path",
      "docs/agent-backlog.md",
      "--expected",
      "docs/advisory-backlog-expected-a5cb4784a09b.json"
    ],
    "cwd": "/home/leonb/projects/build-arena-proposer-architecture-fitness",
    "exit_code": 1,
    "name": "gate-proof-noop-backlog-rejection",
    "stderr_log": "/tmp/build-arena-proposer-architecture-fitness-live-verify/logs/gate-proof-noop-backlog-rejection.stderr.txt",
    "stdout_log": "/tmp/build-arena-proposer-architecture-fitness-live-verify/logs/gate-proof-noop-backlog-rejection.stdout.txt"
  },
  {
    "cmd": [
      "uv",
      "run",
      "python",
      "-m",
      "arena.backlog_gate",
      "--repo",
      "/tmp/build-arena-proposer-architecture-fitness-live-verify/gate-proofs/backlog-repo",
      "--path",
      "docs/agent-backlog.md",
      "--expected",
      "docs/advisory-backlog-expected-a5cb4784a09b.json"
    ],
    "cwd": "/home/leonb/projects/build-arena-proposer-architecture-fitness",
    "exit_code": 0,
    "name": "gate-proof-accepted-backlog",
    "stderr_log": "/tmp/build-arena-proposer-architecture-fitness-live-verify/logs/gate-proof-accepted-backlog.stderr.txt",
    "stdout_log": "/tmp/build-arena-proposer-architecture-fitness-live-verify/logs/gate-proof-accepted-backlog.stdout.txt"
  },
  {
    "cmd": [
      "git",
      "-C",
      "/home/leonb/projects/build-arena-proposer-architecture-fitness",
      "worktree",
      "add",
      "--detach",
      "/tmp/build-arena-proposer-architecture-fitness-live-verify/base-worktree",
      "fe90dc060efa148af8b42b4e1b069617eca05d6b"
    ],
    "cwd": "/home/leonb/projects/build-arena-proposer-architecture-fitness",
    "exit_code": 0,
    "name": "base-worktree-add",
    "stderr_log": "/tmp/build-arena-proposer-architecture-fitness-live-verify/logs/base-worktree-add.stderr.txt",
    "stdout_log": "/tmp/build-arena-proposer-architecture-fitness-live-verify/logs/base-worktree-add.stdout.txt"
  },
  {
    "cmd": [
      "uv",
      "run",
      "python",
      "-m",
      "arena.proposal_planner",
      "--project",
      "/home/leonb/projects/fmc-mcp",
      "--scorecard",
      "/tmp/build-arena-proposer-architecture-fitness-live-verify/fmc-mcp/scorecard.json",
      "--output",
      "/tmp/build-arena-proposer-architecture-fitness-live-verify/fmc-mcp/base-proposal-plan.json",
      "--max-candidates",
      "10"
    ],
    "cwd": "/tmp/build-arena-proposer-architecture-fitness-live-verify/base-worktree",
    "exit_code": 0,
    "name": "fmc-mcp-base-proposal-plan",
    "stderr_log": "/tmp/build-arena-proposer-architecture-fitness-live-verify/logs/fmc-mcp-base-proposal-plan.stderr.txt",
    "stdout_log": "/tmp/build-arena-proposer-architecture-fitness-live-verify/logs/fmc-mcp-base-proposal-plan.stdout.txt"
  },
  {
    "cmd": [
      "uv",
      "run",
      "python",
      "-m",
      "arena.proposal_planner",
      "--project",
      "/home/leonb/projects/arena-calibration",
      "--scorecard",
      "/tmp/build-arena-proposer-architecture-fitness-live-verify/arena-calibration/scorecard.json",
      "--output",
      "/tmp/build-arena-proposer-architecture-fitness-live-verify/arena-calibration/base-proposal-plan.json",
      "--max-candidates",
      "10"
    ],
    "cwd": "/tmp/build-arena-proposer-architecture-fitness-live-verify/base-worktree",
    "exit_code": 0,
    "name": "arena-calibration-base-proposal-plan",
    "stderr_log": "/tmp/build-arena-proposer-architecture-fitness-live-verify/logs/arena-calibration-base-proposal-plan.stderr.txt",
    "stdout_log": "/tmp/build-arena-proposer-architecture-fitness-live-verify/logs/arena-calibration-base-proposal-plan.stdout.txt"
  },
  {
    "cmd": [
      "git",
      "-C",
      "/home/leonb/projects/build-arena-proposer-architecture-fitness",
      "worktree",
      "remove",
      "--force",
      "/tmp/build-arena-proposer-architecture-fitness-live-verify/base-worktree"
    ],
    "cwd": "/home/leonb/projects/build-arena-proposer-architecture-fitness",
    "exit_code": 0,
    "name": "base-worktree-remove",
    "stderr_log": "/tmp/build-arena-proposer-architecture-fitness-live-verify/logs/base-worktree-remove.stderr.txt",
    "stdout_log": "/tmp/build-arena-proposer-architecture-fitness-live-verify/logs/base-worktree-remove.stdout.txt"
  },
  {
    "cmd": [
      "git",
      "diff",
      "--name-only",
      "fe90dc060efa148af8b42b4e1b069617eca05d6b..HEAD",
      "--",
      "scorer",
      "verifier",
      "schema",
      ".arena/scorer.lock.toml"
    ],
    "cwd": "/home/leonb/projects/build-arena-proposer-architecture-fitness",
    "exit_code": 0,
    "name": "protected-path-diff",
    "stderr_log": "/tmp/build-arena-proposer-architecture-fitness-live-verify/logs/protected-path-diff.stderr.txt",
    "stdout_log": "/tmp/build-arena-proposer-architecture-fitness-live-verify/logs/protected-path-diff.stdout.txt"
  },
  {
    "cmd": [
      "git",
      "status",
      "--short",
      "--",
      "scorer",
      "verifier",
      "schema",
      ".arena/scorer.lock.toml"
    ],
    "cwd": "/home/leonb/projects/build-arena-proposer-architecture-fitness",
    "exit_code": 0,
    "name": "protected-path-status",
    "stderr_log": "/tmp/build-arena-proposer-architecture-fitness-live-verify/logs/protected-path-status.stderr.txt",
    "stdout_log": "/tmp/build-arena-proposer-architecture-fitness-live-verify/logs/protected-path-status.stdout.txt"
  }
]
```
