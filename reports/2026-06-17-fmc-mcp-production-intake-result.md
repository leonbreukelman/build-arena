# fmc-mcp production intake result — 2026-06-17

## Verdict

Intake completed against the fresh Grok 4.3 high-reasoning Project Model snapshot.

- Target repo: `<projects>/fmc-mcp`
- Build Arena snapshot: `snapshot-3e9b19da00478bf8`
- Snapshot path: `<repo>/.arena/runs/fmc-mcp-decomposition-grok43-high-reasoning-schema-fix-20260617T221237Z/snapshot-3e9b19da00478bf8/project-model-v1.json`
- Intake profile: `production`
- Gate rerun: `passed=true`, `violations=[]`
- Freshness: `fresh`, `safeForReadOnlyReview=true`, `safeForMutation=true`
- Mutation/proposal status: none run; scorecard and handoff are advisory only.

## Artifacts

- Freshness: `<repo>/.arena/runs/fmc-mcp-decomposition-grok43-high-reasoning-schema-fix-20260617T221237Z/intake/freshness.json`
- Gate rerun: `<repo>/.arena/runs/fmc-mcp-decomposition-grok43-high-reasoning-schema-fix-20260617T221237Z/intake/gate-rerun.json`
- Scorecard JSON: `<repo>/.arena/runs/fmc-mcp-decomposition-grok43-high-reasoning-schema-fix-20260617T221237Z/intake/scorecard-production.json`
- Scorecard Markdown: `<repo>/.arena/runs/fmc-mcp-decomposition-grok43-high-reasoning-schema-fix-20260617T221237Z/intake/scorecard-production.md`
- Proposer handoff packet: `<repo>/.arena/runs/fmc-mcp-decomposition-grok43-high-reasoning-schema-fix-20260617T221237Z/intake/proposer-handoff.json`

## Commands run

```text
uv run python -m arena.project_model_cli freshness \
  --project <projects>/fmc-mcp \
  --snapshot <repo>/.arena/runs/fmc-mcp-decomposition-grok43-high-reasoning-schema-fix-20260617T221237Z/snapshot-3e9b19da00478bf8/project-model-v1.json
```

Output summary:

```json
{
  "status": "fresh",
  "snapshotId": "snapshot-3e9b19da00478bf8",
  "currentHeadOid": "25f445806d5221f21d7ac675799db5c30499f1b7",
  "snapshotHeadOid": "25f445806d5221f21d7ac675799db5c30499f1b7",
  "currentDirty": false,
  "safeForReadOnlyReview": true,
  "safeForMutation": true,
  "aheadBehind": {"ahead": 1, "behind": 0, "available": true}
}
```

```text
uv run python -m arena.project_model_cli gate \
  --snapshot <repo>/.arena/runs/fmc-mcp-decomposition-grok43-high-reasoning-schema-fix-20260617T221237Z/snapshot-3e9b19da00478bf8/manifest.json
```

Output:

```json
{"passed": true, "violations": []}
```

```text
uv run python -m arena.project_intake_scorecard \
  --project <projects>/fmc-mcp \
  --snapshot <repo>/.arena/runs/fmc-mcp-decomposition-grok43-high-reasoning-schema-fix-20260617T221237Z/snapshot-3e9b19da00478bf8/project-model-v1.json \
  --profile production \
  --output <repo>/.arena/runs/fmc-mcp-decomposition-grok43-high-reasoning-schema-fix-20260617T221237Z/intake/scorecard-production.json \
  --markdown-output <repo>/.arena/runs/fmc-mcp-decomposition-grok43-high-reasoning-schema-fix-20260617T221237Z/intake/scorecard-production.md
```

Output summary:

```json
{
  "schemaVersion": "project-intake-scorecard/v0",
  "profile": "production",
  "finding_count": 5,
  "top_ids": [
    "ops.runbooks.missing",
    "verification.quality-gates.present",
    "agent.agents-md.missing",
    "architecture.open-questions-or-gaps",
    "decision.history.missing"
  ]
}
```

```text
uv run python -m arena.proposer_handoff \
  --scorecard <repo>/.arena/runs/fmc-mcp-decomposition-grok43-high-reasoning-schema-fix-20260617T221237Z/intake/scorecard-production.json \
  --freshness <repo>/.arena/runs/fmc-mcp-decomposition-grok43-high-reasoning-schema-fix-20260617T221237Z/intake/freshness.json \
  --output <repo>/.arena/runs/fmc-mcp-decomposition-grok43-high-reasoning-schema-fix-20260617T221237Z/intake/proposer-handoff.json
```

Handoff output summary:

```json
{
  "schemaVersion": "proposer-handoff/v0",
  "snapshotId": "snapshot-3e9b19da00478bf8",
  "freshnessStatus": "fresh",
  "selectedFindingId": "ops.runbooks.missing",
  "notAuthorizedForMutation": true,
  "targetFiles": ["docs/runbooks"]
}
```

## Ranked findings

1. `ops.runbooks.missing` — Runbooks are missing — score `418.0`
   - Dimension: `operations_release_rollback`
   - Severity/confidence: `medium` / `high`
   - Boundary: `safe_to_patch_docs_only`
   - Evidence: absence of `docs/runbooks`
   - Recommended action: document start/stop/deploy/rollback/troubleshooting procedures.
   - Verification: `test -e docs/runbooks`

2. `verification.quality-gates.present` — Project Model exposes local quality gates — score `216.0`
   - Dimension: `reproducible_verification`
   - Severity/confidence: `low` / `high`
   - Boundary: `advisory_only`
   - Evidence: `iterationReadiness.qualityGates`
   - Commands surfaced:
     - `uv run --extra dev mypy src/fmc_mcp`
     - `uv run --extra dev python -m pytest -q`
     - `uv run --extra dev ruff check .`

3. `agent.agents-md.missing` — AGENTS.md is missing — score `192.0`
   - Dimension: `ai_agent_usability`
   - Severity/confidence: `high` / `high`
   - Boundary: `safe_to_patch_docs_only`
   - Evidence: absence of `AGENTS.md`
   - Recommended action: create `AGENTS.md` with commands, boundaries, and definition of done.
   - Verification: `test -e AGENTS.md`

4. `architecture.open-questions-or-gaps` — Project Model contains open questions or verification gaps — score `126.0`
   - Dimension: `architecture_specs_contracts`
   - Severity/confidence: `medium` / `high`
   - Boundary: `advisory_only`
   - Evidence: `iterationReadiness.openQuestions/snapshot.verification_gaps`
   - Recommended action: convert high-impact gaps into explicit backlog or verification tasks.

5. `decision.history.missing` — Decision records are missing — score `110.0`
   - Dimension: `decision_history`
   - Severity/confidence: `medium` / `high`
   - Boundary: `safe_to_patch_docs_only`
   - Evidence: absence of `docs/decisions`
   - Recommended action: create decision records for architecture-significant constraints.
   - Verification: `test -e docs/decisions`

## First recommended improvement

`ops.runbooks.missing` is the first recommendation under the production profile because operations/release/rollback carries high production weight and `docs/runbooks` is absent.

The generated handoff packet targets `docs/runbooks`, includes `test -e docs/runbooks` as the success check, and remains `notAuthorizedForMutation: true`.

## Boundary notes

- This was intake only. I did not run proposal planner, proposal ranker, candidate runner, repo goal loop, promotion, merge, or push.
- The target repo was clean at the freshness check and matched the snapshot head.
- The target repo is one commit ahead of `origin/main`; freshness still passed because snapshot and current local head match.
