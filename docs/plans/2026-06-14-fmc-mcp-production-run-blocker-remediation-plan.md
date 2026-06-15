# fmc-mcp Production-Run Blocker Remediation Implementation Plan

> **For Hermes:** Implement this plan directly in the Build Arena repo using strict TDD for production-code changes. Use Opus for the requested independent review gates before and after implementation.

**Goal:** Close the concrete blockers that prevent a controlled first production run of Build Arena against `/home/leonb/projects/fmc-mcp`, without overclaiming broad unattended autonomy.

**Architecture:** Keep the existing repo-goal loop shape: live decomposition and live diff proposal remain opt-in; promotion remains ff-only and operator-gated. Add a planned live-call budget pre-flight gate, strengthen documentation candidate verification with source-reference requirements, reconcile active docs/readiness governance to the implemented local state, and produce a final production-run readiness artifact.

**Tech Stack:** Python 3.12, uv, pytest, ruff, pyright, JSON readiness register, Markdown docs.

---

## Evidence status before implementation

Confirmed:

- Build Arena is `main...origin/main [ahead 1]` at `a071011fe3c5a969684eaf800ca2b15eae6d9da6`.
- `fmc-mcp` is `main...origin/main [ahead 1]` at `25f445806d5221f21d7ac675799db5c30499f1b7`.
- `/home/leonb/projects/fmc-mcp/.arena/goal.toml` exists and is locally committed.
- `arena.repo_goal_loop` already supports live decomposition, live diff proposal, explicit live authorization, goal-config enforcement, candidate verification, behavior-gated code promotion, and target-only ff promotion.
- Opus accepted the previous audit only with corrections; the major unresolved issue was readiness-register reconciliation and promotion-readiness overclaim risk.

Confirmed blockers/risk items to address now:

1. No explicit planned live-call cap exists; live spend is bounded only indirectly by max cycles and max tokens. The fix will be a pre-flight planned-maximum gate, not a runtime provider retry counter.
2. Documentation candidates can pass with only `test -s` plus link validation unless source-reference mode is required.
3. `docs/verification/2026-06-05-pre-live-readiness-register.json` is stale relative to the local live-loop implementation. Its promotion-blocking issues include `RCA-002`, `LIVE-002`, `GRAPH-001`, `GAP-001`, and `M3-001`; every one must be explicitly reconciled or retained as a blocker.
4. Active docs conflict: `docs/status/2026-06-14-live-repo-goal-loop.md` says ready, while the audit/register/docs require a narrower statement.
5. The production command should include explicit credential env and call budget flags.
6. Remote reproducibility remains blocked until local commits are pushed/PR'd; this plan will not push because this task is to prepare for the local production run, not publish upstream.

Non-goals:

- Do not run the actual production promotion command in this implementation pass.
- Do not implement dashboard control plane, rollback endpoint, PR wrapper, or broad autonomous cross-repo loop.
- Do not push, merge, or deploy.
- Do not mutate `/home/leonb/projects/fmc-mcp` except by read-only verification commands.

---

## Task 1: Add a planned live-call budget pre-flight gate to repo_goal_loop

**Objective:** A live repo-goal run must declare a maximum number of planned provider calls and must fail before any live adapter call if the planned maximum exceeds that cap. This is a pre-flight budget gate over Build Arena's own planned calls, not a runtime retry counter inside provider libraries.

**Files:**

- Modify: `arena/repo_goal_loop.py`
- Test: `tests/test_repo_goal_loop.py`
- Docs: later tasks update `README.md`, `AGENTS.md`, and status docs.

**Step 1: Write failing tests**

Add tests covering:

1. live modes require `live_max_calls` before any cycle starts;
2. single-live-mode runs estimate one live call per cycle for `decompose_mode=live` and one live call per cycle for `apply_mode=live_diff`;
3. both-live-mode runs estimate two live calls per cycle;
4. `live_max_calls <= 0` fails closed;
5. a cap below the planned live calls fails before injected adapters are called;
6. `RUN_STARTED` records the cap and planned calls for auditability.

Expected assertions:

- `run_repo_goal_loop(_config(repo, decompose_mode="live", allow_live=True, live_model="test-live-model"))` raises a `ValueError` matching `live_max_calls`.
- With `max_cycles=2`, `decompose_mode="live"`, `apply_mode="live_diff"`, `live_max_calls=3`, the loop raises before `_FixtureLiveLLM.calls` increments and before any provider transport can be constructed.
- With `max_cycles=1`, both live modes and `live_max_calls=2`, the run can proceed with fake adapters.
- The first event payload contains `liveMaxCalls: 2` and `plannedLiveCalls: 2`.

**Step 2: Run the targeted failing tests**

Run:

```bash
uv run pytest tests/test_repo_goal_loop.py::test_live_modes_require_explicit_live_call_budget_before_any_cycle tests/test_repo_goal_loop.py::test_live_call_budget_estimates_single_and_dual_live_modes tests/test_repo_goal_loop.py::test_live_call_budget_rejects_non_positive_cap tests/test_repo_goal_loop.py::test_live_call_budget_cap_fails_before_adapter_calls tests/test_repo_goal_loop.py::test_run_started_records_live_call_budget -q
```

Expected: FAIL because `RepoGoalLoopConfig` has no `live_max_calls` field and validation does not enforce the cap.

**Step 3: Implement minimal code**

In `RepoGoalLoopConfig`, add:

```python
live_max_calls: int | None = None
```

In `_validate_live_config()`:

- calculate planned calls with a helper such as `_planned_live_calls(config)`;
- if live requested and `live_max_calls is None`, raise `ValueError("live repo-goal modes require explicit live_max_calls")`;
- if `live_max_calls <= 0`, raise;
- if planned calls exceed cap, raise before any adapter construction;
- keep current `allow_live`, `live_model`, and `goal.toml` checks fail-closed.

In `RUN_STARTED`, log:

```python
"liveMaxCalls": config.live_max_calls if live_requested else None,
"plannedLiveCalls": _planned_live_calls(config),
```

In CLI argparse, add:

```python
parser.add_argument("--live-max-calls", type=int)
```

Thread it into `RepoGoalLoopConfig`.

**Step 4: Run targeted tests**

Run the same targeted tests. Expected: PASS.

**Step 5: Run full repo-goal loop tests**

Run:

```bash
uv run pytest tests/test_repo_goal_loop.py -q
```

Expected: PASS.

---

## Task 2: Strengthen docs-candidate verification with source references by default

**Objective:** A docs candidate should not be promotable merely because it is non-empty and has resolvable links; it should include a `## Source references` section citing existing repository files.

**Files:**

- Modify: `arena/proposal_planner.py`
- Modify: `arena/repo_goal_loop.py`
- Test: `tests/test_proposal_planner.py`
- Test: `tests/test_repo_goal_loop.py`
- Test: `tests/test_markdown_links.py`

`arena/proposal_ranker.py` does not need to change for this slice because executable verification commands come from `build_proposal_plan()`, not from ranked entries.

**Step 1: Write failing tests**

Update/add tests so ordinary repos, not just compliance-named repos, require source references for Markdown candidates:

- `test_proposal_plan_builds_grounded_top_n_without_copying_recommended_action` expects `python3 -m arena.markdown_links --repo . --path AGENTS.md --require-source-references`.
- `test_proposal_plan_maps_missing_docs_directories_to_index_markdown_targets` expects `--require-source-references`.
- Add a repo-goal loop test proving deterministic generated Markdown includes `## Source references` and passes the source-reference gate.
- Add a Markdown-link test proving `--require-source-references` rejects a `## Source references` citation to a non-existent local file.

**Step 2: Run targeted failing tests**

Run:

```bash
uv run pytest tests/test_proposal_planner.py::test_proposal_plan_builds_grounded_top_n_without_copying_recommended_action tests/test_proposal_planner.py::test_proposal_plan_maps_missing_docs_directories_to_index_markdown_targets tests/test_markdown_links.py::test_source_references_reject_missing_local_file_citations tests/test_repo_goal_loop.py::test_deterministic_docs_generation_includes_source_references -q
```

Expected: FAIL until the planner and deterministic doc generator are updated.

**Step 3: Implement minimal code**

- Change proposal planning domain context to require source references for all documentation candidates.
- Replace or simplify `_requires_source_references()` so the code is not misleading dead compliance-term matching. If retained, document that source references are now the default for all docs candidates.
- Update `_generate_doc()` to emit a `## Source references` section citing `README.md` when present. Use only existing files.

**Step 4: Run targeted tests**

Run the targeted tests. Expected: PASS.

---

## Task 3: Reconcile readiness register for the bounded fmc-mcp production-run mode

**Objective:** Preserve broad-autonomy blockers while removing stale blockers for the narrow one-cycle local `fmc-mcp` production run, backed by source/test evidence.

**Files:**

- Modify: `docs/verification/2026-06-05-pre-live-readiness-register.json`
- Test: `tests/test_project_status_docs.py`

**Step 1: Write failing doc-governance tests**

Add/modify tests to assert the register now contains:

- a fresh `boundedFmcMcpProductionRun` block;
- `status: ready_after_operator_authorization` or equivalent for one local bounded CLI run;
- explicit remaining gates: operator live spend/mutation authorization, provider credentials, `live_max_calls`, explicit `--live-api-key-env`, clean/known target repo state, and no claim of broad autonomy;
- RCA-002 explicitly scoped as non-blocking for this OpenAI-compatible direct-provider CLI path, because the production command does not use the old unrecorded Grok Build wrapper; retain it as a historical evidence gap for that older wrapper lineage;
- M3-001 marked closed/superseded for the naive worktree-only prerequisites now implemented;
- LIVE-002 and GRAPH-001 do not block the narrow naive/live CLI run when the decomposition gate passes, but still block broader decomposition-informed confidence claims;
- GAP-001 is closed or narrowed because mutation now requires deterministic verification commands, docs source references, behavior gate for code, and target-only promotion.
- `overallStatus` remains `not_ready_blockers_remain`, with `boundedFmcMcpProductionRun` recorded as a scoped exception rather than a top-level broad-readiness status.

Expected: FAIL until JSON is updated.

**Step 2: Update the register**

Update only the readiness register, preserving historical issue entries and audit trail. Do not delete old evidence. Add fields that make mode boundaries explicit, for example:

```json
"boundedFmcMcpProductionRun": {
  "status": "ready_after_operator_authorization",
  "scope": "one local CLI run against /home/leonb/projects/fmc-mcp, max_cycles=1, live decompose + live_diff, promotion allowed, explicit live_max_calls=2",
  "remainingOperatorGates": [...],
  "notProofOf": ["broad unattended autonomy", "remote reproducibility", "dashboard rollback", "Cisco FMC live integration", "live code-promotion was proven"]
}
```

**Step 3: Run doc-governance test**

Run:

```bash
uv run pytest tests/test_project_status_docs.py -q
```

Expected: PASS.

---

## Task 4: Align active docs and production command

**Objective:** A fresh agent/operator should see one consistent story: ready to attempt one bounded local fmc-mcp production run after explicit authorization, not ready for broad unattended production.

**Files:**

- Modify: `README.md`
- Modify: `AGENTS.md`
- Modify: `docs/build-arena-project-brief.md`
- Modify: `docs/status/2026-06-14-live-repo-goal-loop.md`
- Modify: `docs/status/2026-06-14-progress-timeline-and-production-readiness-audit.md`
- Test: `tests/test_project_status_docs.py`

**Step 1: Write failing doc tests**

Update tests to require these markers in active docs:

- `--live-max-calls`
- `--live-api-key-env XAI_API_KEY`
- `ready to perform one bounded local fmc-mcp production run after explicit operator authorization`
- `not proof of broad unattended autonomy`
- `docs/verification/2026-06-05-pre-live-readiness-register.json`
- no stale use of `provider acceptance remains unverified until live smoke` in docs that discuss the 2026-06-14 verified xAI/Grok live dry-run. Also update/replace the existing `test_docs_describe_bounded_real_run_attempt_not_unqualified_readiness` marker assertion so the test suite does not require the old phrase. Preserve the neighboring provider-doc markers from `test_live_provider_docs_disclose_credentials_and_model_enforcement`: `~/.hermes/.env`, `api_key_source`, `explicit model ID`, and `served-model match`.

**Step 2: Patch docs**

Patch active docs to state:

- live provider acceptance for xAI/Grok was verified for the 2026-06-14 dry-run path;
- one bounded local production run is ready after explicit operator authorization;
- remote/reproducible handoff still requires pushing/PR'ing local commits;
- broad unattended mode remains blocked by dashboard/rollback/subscription-CLI and unproven live promotions at scale;
- production command includes `--live-max-calls 2` and `--live-api-key-env XAI_API_KEY`.

**Step 3: Run doc tests**

Run:

```bash
uv run pytest tests/test_project_status_docs.py -q
```

Expected: PASS.

---

## Task 5: Verify both repos and create the final readiness report

**Objective:** Prove implementation works locally and leave a durable report for the handoff.

**Files:**

- Create: `reports/2026-06-14-fmc-mcp-production-run-readiness-implementation-report.md`
- Create/update after Opus: `reports/2026-06-14-fmc-mcp-production-run-readiness-opus-review.json`

**Step 1: Run Build Arena checks**

Run:

```bash
uv run pytest tests/test_repo_goal_loop.py tests/test_proposal_planner.py tests/test_project_status_docs.py -q
make verify
```

Expected: PASS.

**Step 2: Run fmc-mcp checks**

Run in `/home/leonb/projects/fmc-mcp`:

```bash
uv run ruff check .
uv run python -m pytest -q
uv run python -m mypy src tests
```

Expected: PASS.

**Step 3: Run fail-closed no-spend guard**

Run a no-live-spend command that proves missing budget fails closed before provider calls:

```bash
uv run python -m arena.repo_goal_loop \
  --project /home/leonb/projects/fmc-mcp \
  --goal 'guard smoke' \
  --artifacts-root /tmp/build-arena-live-budget-guard \
  --max-cycles 1 \
  --decompose-mode live \
  --apply-mode live_diff \
  --allow-live \
  --live-model dummy \
  --live-provider xai
```

Expected: non-zero with an error mentioning `live_max_calls`, before any network call. This uses `fmc-mcp` specifically so the tracked goal-config precondition is satisfied and the budget error is the intended failure.

**Step 4: Write final report**

Include:

- changed files;
- commands and exit codes;
- current git state of both repos;
- readiness statement;
- production command;
- remaining non-blocking risks.

**Step 5: Opus implementation review**

Bundle source/docs/tests/report and ask Opus to verify:

- the code changes actually address the blockers;
- tests cover the new live-call budget and docs source-reference gate;
- readiness wording is not overclaimed;
- the production command is explicit and bounded;
- any blocker that still prevents the first local `fmc-mcp` production run.

Patch valid criticism and rerun the relevant checks.

---

## Expected final production command after implementation

Do not execute until Leon explicitly authorizes the live mutation/spend:

```bash
cd /home/leonb/projects/build-arena && \
uv run python -m arena.repo_goal_loop \
  --project /home/leonb/projects/fmc-mcp \
  --goal 'Improve fmc-mcp with bounded, verified, repository-grounded changes using live LLM decomposition and live LLM diff proposal.' \
  --artifacts-root /home/leonb/projects/build-arena/.arena/runs/fmc-mcp-production-live-$(date -u +%Y%m%dT%H%M%SZ) \
  --max-cycles 1 \
  --decompose-mode live \
  --apply-mode live_diff \
  --allow-live \
  --live-provider xai \
  --live-model grok-4.20-0309-non-reasoning \
  --live-api-key-env XAI_API_KEY \
  --live-max-tokens 12000 \
  --live-max-calls 2 \
  --test-command 'uv run python -m pytest -q' \
  --allow-promotion \
  --no-dry-run
```

## Acceptance criteria

- `repo_goal_loop` refuses live modes without explicit `live_max_calls`.
- `repo_goal_loop` refuses a planned run whose maximum live calls exceed `live_max_calls`.
- `repo_goal_loop` records planned live calls in the run-start event and documents the cap as a pre-flight planned maximum, not a provider-library retry counter.
- Production command includes `--live-api-key-env` and `--live-max-calls`.
- Docs candidates require source references in proposal verification commands.
- Deterministic docs generation emits source references to existing files.
- Source-reference verification rejects non-existent local file citations.
- Readiness register has a mode-specific bounded `fmc-mcp` production-run status and no longer treats obsolete M3 internal prerequisites as blocking that narrow run.
- Active docs agree on bounded local readiness and broad-autonomy non-readiness.
- Build Arena `make verify` passes.
- `fmc-mcp` ruff, pytest, and mypy pass.
- Opus implementation review returns ACCEPT or ACCEPT_WITH_NONBLOCKING_ISSUES for the first bounded local `fmc-mcp` production run.
