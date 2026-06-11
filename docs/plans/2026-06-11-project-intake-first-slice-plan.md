# Project Intake First Slice Implementation Plan

> **For Hermes:** Use subagent-driven-development skill to implement this plan task-by-task.

**Goal:** Implement the deterministic foundation that lets Build Arena move from a fresh Project Model v1 artifact to a ranked intake result and a bounded proposer handoff, while leaving Elenchus as a later advisory backlog item.

**Architecture:** Build this as three deterministic, hash-linked artifacts after Project Model v1 generation: freshness status, weighted intake scorecard, and proposer handoff packet. Each artifact is derived from repo/git/filesystem/Project Model evidence, emits JSON plus concise human-readable output where useful, and does not mutate target repos or run paid/live providers. Elenchus is not implemented in this slice; it remains a future advisory critique over synthesized handoff claims.

**Tech Stack:** Python 3.12, `uv`, existing Build Arena modules, `gh` as optional enrichment only, JSON schemas under `docs/schemas/`, pytest/ruff/pyright verification.

---

## 0. Review status

Read-only Opus review completed on 2026-06-11:

- Review artifact: `docs/verification/2026-06-11-opus-project-intake-first-slice-plan-review.md`
- Raw JSON: `docs/verification/2026-06-11-opus-project-intake-first-slice-plan-review.json`
- Verdict: `ACCEPT_WITH_CHANGES`

Accepted changes incorporated here:

1. Deterministic scorecard priority formula is pinned.
2. Freshness status precedence and exit-code mapping are explicit.
3. Handoff prohibited paths include the full protected-surface set, including `.arena/scorer.lock.toml`.
4. FMC-MCP pilot snapshot generation is explicitly fixture/off/no-live only unless separately authorized.
5. Determinism, read-only/no-mutation, schema-validation, and no-live tests are added to the task list.

---

## 1. Current status and constraints

Existing backlog items:

- #19 `Project Model freshness and branch-tracking contract for autonomous loops`
  - URL: https://github.com/leonbreukelman/build-arena/issues/19
  - Covers deterministic freshness/branch/ref state.
- #6 `Add weighted project-intake scorecard for AI-usable repo housekeeping and improvement prioritization`
  - URL: https://github.com/leonbreukelman/build-arena/issues/6
  - Covers the scorecard model and CLI/report path.

Known implementation facts from repo evidence:

- `arena.project_model_cli snapshot` already emits Project Model v1 artifacts.
- `arena/project_model_v1.py` adds `iterationReadiness` to newly emitted v1 artifacts.
- `iterationReadiness` includes `componentProfiles`, `runtimeContracts`, `externalSurfaces`, `productInvariants`, `qualityGates`, `priorityBacklog`, and `openQuestions`.
- `arena/project_model_gate.py` checks snapshot/graph hash freshness inside a snapshot bundle, but does not yet compare a stored Project Model to the live repo/ref/branch state.
- `docs/specs/2026-06-07-weighted-project-intake-prioritization.md` says the scorecard should run after Project Model v1 generation and before hypothesis selection.
- The scorecard spec is not implemented yet and must not be claimed as a current CLI/gate.

Hard boundaries:

- Do not modify `scorer/`, `verifier/`, root `schema/`, `.arena/scorer.lock.toml`, or `arena/generated/` in this slice.
- Do not run live paid/provider calls.
- Do not enable broad autonomous live loops.
- Do not make GitHub/`gh` mandatory for local-only operation.
- Do not let scorecard output become permission to mutate.
- Do not implement Elenchus in this slice.

---

## 2. Deliverables

### Deliverable A — Project Model freshness artifact and CLI

Purpose: answer whether a Project Model v1/manifest is safe to consume for read-only review or proposer/worktree mutation against the current repo state.

Proposed files:

- Create: `arena/project_model_freshness.py`
- Modify: `arena/project_model_cli.py`
- Test: `tests/test_project_model_freshness.py`
- Create: `docs/schemas/project-model-freshness-v0.schema.json`
- Update docs as needed: `docs/specs/2026-06-05-project-model-v1-shared-contract-spec.md` or a new focused spec under `docs/specs/`

CLI shape:

```bash
uv run python -m arena.project_model_cli freshness \
  --project /path/to/repo \
  --snapshot /path/to/project-model-v1.json
```

JSON output shape, versioned as `project-model-freshness/v0`:

```json
{
  "schemaVersion": "project-model-freshness/v0",
  "projectRoot": "/path/to/repo",
  "snapshotPath": "/path/to/project-model-v1.json",
  "snapshotId": "...",
  "snapshotHeadOid": "...",
  "currentHeadOid": "...",
  "snapshotDirty": false,
  "currentDirty": false,
  "currentDirtyPaths": [],
  "currentBranch": "main",
  "defaultBranch": "main",
  "remoteName": "origin",
  "aheadBehind": {"ahead": 0, "behind": 0, "available": true},
  "activeBranches": [],
  "openPullRequests": [],
  "status": "fresh",
  "safeForReadOnlyReview": true,
  "safeForMutation": true,
  "warnings": []
}
```

Status values:

- `fresh`
- `dirty-worktree`
- `base-advanced`
- `branch-diverged`
- `snapshot-mismatch`
- `unknown`

Exit behavior:

- Exit `0` for `fresh`.
- Exit `2` for every non-fresh state.
- Always emit JSON diagnostics even on non-zero exit.
- Missing `gh` is not an error; record `openPullRequests.available=false` or equivalent.
- `aheadBehind` must be computed only from local ref metadata unless an explicit future flag authorizes fetch/network refresh. If no upstream/default tracking ref is available, set `aheadBehind.available=false` rather than guessing.

Status precedence when multiple conditions are true:

| Rank | Status | Meaning | Exit | Read-only review | Mutation |
| ---: | --- | --- | ---: | --- | --- |
| 1 | `snapshot-mismatch` | Snapshot/model/hash identity cannot be reconciled with the supplied artifact/manifest. | 2 | warn-only | blocked |
| 2 | `dirty-worktree` | Current target repo has uncommitted changes not represented by the snapshot. | 2 | warn-only | blocked |
| 3 | `branch-diverged` | Snapshot head and current/default ref have both changed, or current branch is not a clean descendant of the snapshot base. | 2 | warn-only | blocked |
| 4 | `base-advanced` | Default/base branch advanced beyond the snapshot head without local dirtiness. | 2 | warn-only | blocked |
| 5 | `unknown` | Required git/ref data is unavailable or ambiguous. | 2 | warn-only | blocked |
| 6 | `fresh` | Snapshot head, current head, dirty fingerprint, and local ref metadata match. | 0 | allowed | allowed |

If the implementation later supports explicit branch-overlay snapshots, those overlays must be a new status or a documented `fresh` subtype; do not silently treat branch divergence as fresh.

### Deliverable B — Weighted project-intake scorecard artifact and CLI

Purpose: produce the first implemented version of #6 as a deterministic derived artifact, not a mutation gate.

Proposed files:

- Create: `arena/project_intake_scorecard.py`
- Test: `tests/test_project_intake_scorecard.py`
- Create: `docs/schemas/project-intake-scorecard-v0.schema.json`
- Optionally create concise markdown report writer in same module; do not split early unless code becomes unclear.

CLI shape:

```bash
uv run python -m arena.project_intake_scorecard \
  --project /path/to/repo \
  --snapshot /path/to/project-model-v1.json \
  --profile new-project \
  --output /tmp/intake-scorecard.json \
  --markdown-output /tmp/intake-scorecard.md
```

Profiles for first slice:

- `new-project`
- `active-development`
- `production`
- `documentation-first`

Dimensions:

- `documentation_project_knowledge`
- `reproducible_verification`
- `architecture_specs_contracts`
- `ai_agent_usability`
- `decision_history`
- `backlog_change_governance`
- `security_supply_chain_hygiene`
- `operations_release_rollback`

Scorecard output must include:

- model hash / snapshot id / repo head used;
- profile and weights;
- ranked findings with evidence refs or absence checks;
- ranked improvement candidates;
- one first recommended improvement;
- explicit note that output is advisory and does not authorize mutation.

Deterministic priority formula for first slice:

```text
priorityScore =
  profileDimensionWeight
  * severityMultiplier
  * confidenceMultiplier
  * (impactOnFutureIteration + riskReduction + verificationGain + docKnowledgeGain)
  / effortMultiplier
```

Multipliers:

- severity: `low=1`, `medium=2`, `high=3`, `critical=4`
- confidence: `low=0.5`, `medium=0.75`, `high=1.0`
- effort: `small=1`, `medium=2`, `large=3`, `unknown=4`
- each gain field: integer `1..5`

Tie-break order:

1. higher `priorityScore`;
2. higher severity multiplier;
3. higher confidence multiplier;
4. lower effort multiplier;
5. stable lexicographic `id`.

The implementation must pin all four profile weight vectors from `docs/specs/2026-06-07-weighted-project-intake-prioritization.md` into tests so future drift is visible.

Finding shape:

```json
{
  "id": "doc-readme-missing",
  "dimension": "documentation_project_knowledge",
  "title": "README is missing",
  "severity": "high",
  "confidence": "high",
  "evidence": [{"kind": "absence", "path": "README.md", "checked": true}],
  "whyItMatters": "A fresh agent has no stable entrypoint.",
  "recommendedAction": "Create a README with purpose, setup, commands, status, and links.",
  "verification": ["test -f README.md"],
  "autonomyBoundary": "safe_to_patch_docs_only",
  "estimatedEffort": "small",
  "priorityScore": 123.0
}
```

First-slice evidence extraction should be deterministic:

- Existence checks for `README.md`, `AGENTS.md`, `docs/index.md`, `docs/specs/`, `docs/decisions/` or `docs/adr/`, `docs/runbooks/`, issue/PR templates.
- Project Model v1 `iterationReadiness.qualityGates` for tests/lint/type/build signals.
- Project Model v1 `iterationReadiness.openQuestions` and `snapshot.verification_gaps` for known uncertainties.
- Git state from the freshness module.
- Optional `gh` issue/PR metadata if available, but local scoring must work without it.

Do not include LLM interpretation in the first slice. The first implementation can have simple, deterministic text summaries.

### Deliverable C — Proposer handoff packet schema and writer

Purpose: make the boundary between intake and proposer explicit before attempting autonomous mutation.

Proposed files:

- Create: `arena/proposer_handoff.py`
- Test: `tests/test_proposer_handoff.py`
- Create: `docs/schemas/proposer-handoff-v0.schema.json`
- Prefer standalone CLI support in `arena.proposer_handoff` such as `uv run python -m arena.proposer_handoff --scorecard ... --freshness ... --output ...`; avoid coupling this into the scorecard CLI unless a later implementation proves it is simpler without blurring boundaries.

Schema version: `proposer-handoff/v0`.

Handoff fields:

```json
{
  "schemaVersion": "proposer-handoff/v0",
  "sourceScorecardId": "...",
  "snapshotId": "...",
  "freshnessStatus": "fresh",
  "selectedFindingId": "...",
  "hypothesisIntent": "...",
  "targetFiles": [],
  "successCriteria": [],
  "failureCriteria": [],
  "verificationCommands": [],
  "rollbackCondition": "...",
  "prohibitedPaths": ["scorer/", "verifier/", "schema/", "arena/generated/", ".arena/scorer.lock.toml"],
  "requiresOwnerApproval": false,
  "evidenceRefs": [],
  "advisoryNotes": [],
  "notAuthorizedForMutation": true
}
```

Key rule for first slice:

- The handoff packet prepares the proposer boundary, but does not yet cause a runner to mutate anything.
- If freshness is not `fresh`, `notAuthorizedForMutation` must be `true`.
- If the selected finding has no verification commands, `requiresOwnerApproval` or an explicit blocker must be set.
- `prohibitedPaths` must come from one canonical constant or helper shared by handoff generation and tests so it cannot drift from Build Arena protected-surface policy.

### Deliverable D — Elenchus backlog issue only

Purpose: preserve the future advisory idea without implementing it now.

Planned issue:

- Title: `Backlog: advisory Elenchus critique for intake handoff packets`
- Scope: post-first-slice optional critique over synthesized top leverage claim and handoff packet.
- Non-goal: no per-question oracle, no scorer/verifier/gate/promoter role.

---

## 3. Implementation order

### Task 1: Add Project Model freshness tests

**Objective:** Define the freshness contract before production code.

**Files:**

- Create: `tests/test_project_model_freshness.py`
- Create later: `arena/project_model_freshness.py`

**Test cases:**

1. Fresh repo and matching snapshot returns `fresh`, `safeForMutation=true`, exit code `0` through CLI wrapper.
2. Dirty worktree returns `dirty-worktree`, `safeForMutation=false`, JSON still emitted.
3. Current head differs from snapshot head returns `base-advanced` or `branch-diverged` depending on ancestry.
4. Missing `gh` or failing PR lookup does not fail local freshness; it records PR data unavailable.
5. Manifest/snapshot graph hash mismatch maps to `snapshot-mismatch` with exit code `2`.
6. Every non-fresh status in the precedence table exits `2` while still emitting schema-valid JSON.
7. Identical inputs produce stable JSON.
8. Freshness checks do not write into the target repo and only invoke read-only git/gh commands.

**Verification:**

```bash
uv run pytest tests/test_project_model_freshness.py -q
```

Expected before implementation: failures for missing module/CLI.

### Task 2: Implement freshness module and CLI subcommand

**Objective:** Make freshness a deterministic artifact and CLI path.

**Files:**

- Create: `arena/project_model_freshness.py`
- Modify: `arena/project_model_cli.py`
- Create: `docs/schemas/project-model-freshness-v0.schema.json`

**Implementation notes:**

- Use `subprocess.run(..., cwd=project, capture_output=True, text=True)` with fixed git commands.
- Keep all command parsing deterministic and fail-closed to `unknown` with warnings when git data is unavailable.
- Use `gh` only if available and only for optional PR metadata.
- Do not mutate branches or fetch by default.

**Verification:**

```bash
uv run pytest tests/test_project_model_freshness.py -q
uv run python -m arena.project_model_cli freshness --help
```

### Task 3: Add scorecard data model and scoring tests

**Objective:** Encode the #6 scorecard contract without adding mutation behavior.

**Files:**

- Create: `tests/test_project_intake_scorecard.py`
- Create later: `arena/project_intake_scorecard.py`
- Create later: `docs/schemas/project-intake-scorecard-v0.schema.json`

**Test cases:**

1. Profile weights match the spec for all four profiles.
2. Priority formula ranks a high-confidence/small-effort/high-impact docs finding above a low-impact code cleanup.
3. Missing `README.md` produces an absence finding.
4. Missing `AGENTS.md` produces an AI-agent-usability finding.
5. Stale/conflicting status strings can be represented separately from missing docs.
6. Quality gates are imported from Project Model v1 `iterationReadiness.qualityGates`.
7. JSON output validates against the sidecar schema.
8. Identical inputs produce stable JSON and stable markdown ordering.
9. Scorecard extraction does not write into the target repo.
10. No live/provider modules or API clients are imported or constructed by scorecard code.

**Verification:**

```bash
uv run pytest tests/test_project_intake_scorecard.py -q
```

### Task 4: Implement scorecard CLI and markdown report

**Objective:** Emit machine-readable and concise human-readable intake artifacts.

**Files:**

- Create: `arena/project_intake_scorecard.py`
- Create: `docs/schemas/project-intake-scorecard-v0.schema.json`

**Implementation notes:**

- Start as one module with pure functions plus `main()`.
- Avoid root `schema/` and generated artifacts.
- Do not require GitHub API.
- Do not use live LLM calls.
- Keep output stable for fixed inputs.

**Verification:**

```bash
uv run pytest tests/test_project_intake_scorecard.py -q
uv run python -m arena.project_intake_scorecard --help
```

### Task 5: Add proposer handoff packet tests

**Objective:** Define the intake-to-proposer contract independently of runner mutation.

**Files:**

- Create: `tests/test_proposer_handoff.py`
- Create later: `arena/proposer_handoff.py`
- Create later: `docs/schemas/proposer-handoff-v0.schema.json`

**Test cases:**

1. Fresh scorecard with first recommendation produces a handoff packet.
2. Non-fresh freshness status marks packet `notAuthorizedForMutation=true`.
3. Missing verification commands marks owner approval/blocker.
4. Protected paths are always present in prohibited paths.
5. JSON validates against schema.
6. Identical inputs produce stable JSON.
7. Handoff generation does not invoke runners, live providers, or mutation code.

**Verification:**

```bash
uv run pytest tests/test_proposer_handoff.py -q
```

### Task 6: Implement handoff packet writer

**Objective:** Produce a bounded hypothesis packet from a scorecard recommendation.

**Files:**

- Create: `arena/proposer_handoff.py`
- Create: `docs/schemas/proposer-handoff-v0.schema.json`
- Optionally modify: `arena/project_intake_scorecard.py` for `--handoff-output`

**Implementation notes:**

- The first slice should generate a packet from the scorecard’s first recommended improvement.
- Do not call `arena.loop`, runners, proposer transports, or live providers.
- Keep packet status explicit: prepared handoff is not mutation authorization.

**Verification:**

```bash
uv run pytest tests/test_proposer_handoff.py -q
```

### Task 7: Docs and integration verification

**Objective:** Document the deterministic flow and prove no readiness overclaim.

**Files:**

- Modify or create focused docs under `docs/specs/` and/or `docs/verification/`.
- Update `docs/build-arena-project-brief.md` only if current-state wording needs the new feature after implementation.

**Verification commands:**

```bash
uv run pytest tests/test_project_model_freshness.py tests/test_project_intake_scorecard.py tests/test_proposer_handoff.py -q
uv run pytest tests -q
uv run ruff check .
uv run pyright
```

Run a pilot after the first slice exists:

```bash
uv run python -m arena.project_model_cli freshness \
  --project /home/leonb/projects/fmc-mcp \
  --snapshot <fmc-mcp-project-model-v1.json>

uv run python -m arena.project_intake_scorecard \
  --project /home/leonb/projects/fmc-mcp \
  --snapshot <fmc-mcp-project-model-v1.json> \
  --profile new-project \
  --output docs/verification/<date>-fmc-mcp-intake-scorecard.json \
  --markdown-output docs/verification/<date>-fmc-mcp-intake-scorecard.md
```

If no fresh FMC-MCP snapshot exists at implementation time, generate one only with fixture/off/no-live mode first, for example:

```bash
uv run python -m arena.project_model_cli snapshot \
  --project /home/leonb/projects/fmc-mcp \
  --artifacts-root <local-artifacts-dir> \
  --project-id fmc-mcp \
  --goal "Build a safe Project Model v1 snapshot for deterministic intake" \
  --llm-mode fixture \
  --overwrite
```

The pilot must include a guard test or command assertion proving no `--allow-live`, no `--llm-mode live`, and no paid/provider client construction occurred. Do not run live providers without separate explicit authorization.

---

## 4. Issue split

Use existing issues where they already match scope:

- #19: freshness/branch tracking.
- #6: weighted scorecard.

Open new issues for missing backlog surfaces:

1. `Add proposer handoff packet schema between intake scorecard and hypothesis generation`
2. `Backlog: advisory Elenchus critique for intake handoff packets`

The Elenchus issue must explicitly say it is after the deterministic slice, advisory only, budgeted/cached, and not a scorer/verifier/gate/promoter.

---

## 5. Opus review request

Ask Opus to review this plan for:

- whether the slice order is correct;
- whether #19 before #6 before handoff is the right dependency chain;
- whether scorecard should be advisory or gate-like in first slice;
- whether any file paths violate Build Arena protected-surface rules;
- whether Elenchus is correctly left as backlog;
- missing tests or overbroad scope;
- issue split quality.

Patch this plan if Opus returns `ACCEPT_WITH_CHANGES` or `REJECT` with valid objections.

---

## 6. Definition of done for this planning pass

This planning pass is complete when:

- this plan exists under `docs/plans/`;
- a read-only Opus review artifact exists under `docs/verification/`;
- valid Opus feedback is incorporated into this plan;
- GitHub issues exist for all implementation/backlog surfaces without duplicating #6/#19;
- final report names exact artifact paths and issue URLs.

Implementation is still required after this planning pass. No production code should be changed as part of this pass.
