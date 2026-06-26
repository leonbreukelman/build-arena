# Build Arena current status, progress timeline, and production-readiness audit

Generated: 2026-06-15T19:51:32Z

## Bottom line

Build Arena has made real progress since the older Phase 4/v0 state. The current tree contains the intake -> proposal -> repo-goal loop, live decomposition/live diff plumbing, proposal registry/lineage primitives, repair-loop mechanics, agent-wiki scaffolding, and tests for those surfaces.

But the project is still not proven ready for broad unattended production runs on arbitrary target projects.

The last real `fmc-mcp` production-live attempt was not a smoke test. It was a bounded live repo-goal run against `/home/leonb/projects/fmc-mcp` with `--no-dry-run`, `--allow-promotion`, live decomposition, and live diff proposal. It promoted nothing. Live decomposition passed; candidate application failed safely at the Markdown link gate because the live model generated bad doubled `src/src/...` links.

Current owner-language status:

- Real bounded `fmc-mcp` production-live run: executed.
- Target mutation/promotion: none.
- Decomposition in that run: passed.
- Candidate application in that run: failed safely.
- End-to-end promotable surface today: effectively still documentation/Markdown only. Code/component findings are better represented than before, but they are not yet proven promotable end-to-end.
- Broad production autonomy: not proven.
- Current Build Arena worktree: dirty with many modified/untracked remediation artifacts; not committed/pushed. Additional untracked onboarding-contract artifacts are present (`tests/test_onboarding_acceptance.py`, `docs/inbox/`, `docs/schemas/project-model.frozen-v1.json`, `docs/files (11).zip`).
- Latest standard verification after the report edits: `pytest` passes and `ruff` passes, but `pyright` fails on the new untracked onboarding acceptance test importing missing `arena.onboard`. Opus reviewed earlier evidence/code but did not independently rerun commands.

## Important correction

I previously used "smoke" too loosely. That was wrong.

Use these terms instead:

1. `fmc-mcp-production-20260615T001605Z`: real bounded production-live repo-goal attempt, not a smoke.
2. Earlier `fmc-mcp-live-*` dry-run attempts: real live dry-run attempts; one failed decomposition due to provider truncation.
3. `reports/2026-06-15-grok43-verification-results.md`: bounded live Grok 4.3 project-model attempt against the Build Arena worktree, not `fmc-mcp`; it failed the deterministic decomposition gate with 22 violations. The report text was corrected to remove "smoke" and use `FAIL_CLOSED_DECOMPOSITION_GATE`.

## Evidence read for this audit

Conversation/session evidence:

- Prior June 5 expected-vs-actual audit session found Build Arena had progressed from Phase 1-4 to AI-first decomposer, Project Model v1, and bounded xAI live adapter, while README/AGENTS were stale at that time.
- Current June 14/15 work is mostly represented by repo artifacts and run logs rather than easily searchable session DB hits.

Repo and artifact evidence:

- `git status --short --branch`
- `git log -8 --oneline`
- `.arena/runs/fmc-mcp-production-20260615T001605Z/loop-events.jsonl`
- `reports/2026-06-15-fmc-mcp-production-pass-and-proposal-pipeline-report.md`
- `docs/specs/2026-06-15-full-autonomy-gap-analysis.md`
- `docs/status/2026-06-15-full-autonomy-gap-remediation-implementation-status.md`
- `reports/2026-06-15-full-autonomy-implementation-final-opus-review.json`
- `arena/repo_goal_loop.py`
- `arena/proposal_planner.py`
- `arena/proposal_registry.py`
- `arena/proposal_domains.py`
- `arena/runners/diff_proposer.py`
- `tests/test_proposal_registry.py`
- `tests/test_proposal_planner.py`
- `tests/test_repo_goal_loop.py`
- `tests/test_project_status_docs.py`

## Current git state

Observed command output:

```text
## main...origin/main [ahead 1]
 M AGENTS.md
 M README.md
 M arena/proposal_candidate_runner.py
 M arena/proposal_domains.py
 M arena/proposal_planner.py
 M arena/repo_goal_loop.py
 M arena/runners/diff_proposer.py
 M docs/build-arena-project-brief.md
 M docs/schemas/proposal-plan-v0.schema.json
 M docs/status/2026-06-14-live-repo-goal-loop.md
 M docs/verification/2026-06-05-pre-live-readiness-register.json
 M tests/fixtures/parity_plan_compliance.json
 M tests/fixtures/parity_plan_normal.json
 M tests/test_diff_proposer.py
 M tests/test_markdown_links.py
 M tests/test_project_intake_scorecard.py
 M tests/test_project_status_docs.py
 M tests/test_proposal_domains.py
 M tests/test_proposal_planner.py
 M tests/test_repo_goal_loop.py
?? arena/agent_wiki.py
?? arena/proposal_registry.py
?? docs/agent-wiki/
?? docs/plans/2026-06-14-fmc-mcp-production-run-blocker-remediation-plan.md
?? docs/plans/2026-06-15-full-autonomy-gap-remediation-plan.md
?? docs/specs/2026-06-15-full-autonomy-gap-analysis.md
?? docs/status/2026-06-14-progress-timeline-and-production-readiness-audit.md
?? docs/status/2026-06-15-full-autonomy-gap-remediation-implementation-status.md
?? reports/2026-06-14-fmc-mcp-production-run-final-readiness-report.md
?? reports/2026-06-15-fmc-mcp-production-pass-and-proposal-pipeline-report.md
?? reports/2026-06-15-full-autonomy-implementation-final-opus-review.json
?? reports/2026-06-15-grok43-verification-results.md
?? tests/test_agent_wiki.py
?? tests/test_proposal_registry.py
```

Recent committed baseline:

```text
a071011 feat: enable live repo-goal loop execution
2cc45a6 docs(arena): document the completed intake->proposal->loop pipeline (epic #25) (#38)
1f314cd feat(arena): Phase 5 — close the loop (repo-scale /goal) (#31) (#37)
9120242 feat(arena): Phase 4 — cross-domain proposal ranker (#30) (#36)
5e7c4ea feat(arena): Phase 3 — code-quality domain + load-bearing gate (#29) (#35)
b6b144e refactor(arena): Phase 2 — multi-domain proposal contract (#28) (#34)
d96ba55 feat(arena): Phase 1 — intake emits component-scoped non-doc findings (#27) (#33)
4f0ae5d Phase 0 — Correct intake/proposal status drift + bring pipeline through review (#26) (#32)
```

Interpretation: the repo is locally ahead and dirty. The latest remediation work is present in the working tree and tests pass, but it is not a clean committed state.

## Timeline of progress

### 1. Early foundation: scorer/verifier/runner/loop phases

Verified by git history and project docs.

- Phase 1: scorer calibration foundation.
- Phase 2: verifier calibration.
- Phase 3: runner routing contracts.
- Phase 4: loop budget/divergence/events/worktree promotion foundation.

Current status: implemented in repo history. Not the current limiting factor.

### 2. Legacy compatibility projection and deterministic decomposer

The project gained a deterministic repo scanner and an earlier compatibility projection. Earlier conversations correctly identified that projection as too shallow for the intended Build Arena direction.

Current status: the active runtime now emits Project Model v1 as the shared contract. The old compatibility projection is archived historical context, not an active output.

### 3. AI-first decomposer and Project Model v1 readiness

Later work added graph/encyclopedia/snapshot/gate surfaces and Project Model v1 as the primary enriched artifact.

Current status: implemented and covered by tests from earlier work. Broad live autonomy still not implied.

### 4. Intake -> proposal -> repo-goal pipeline

Recent commits show the pipeline has progressed through:

- component-scoped non-doc findings,
- multi-domain proposal contract,
- code-quality domain + load-bearing gate,
- cross-domain proposal ranker,
- repo-scale `/goal` loop,
- live repo-goal loop execution.

Current status: implemented enough to run a bounded live repo-goal attempt; not enough to guarantee promotion or broad autonomy.

### 5. `fmc-mcp` bounded production-live run

Run root:

`/home/leonb/projects/build-arena/.arena/runs/fmc-mcp-production-20260615T001605Z`

Event stream summary:

```text
0 RUN_STARTED {'decomposeMode': 'live', 'applyMode': 'live_diff', 'dryRun': False, 'liveModel': 'grok-4.20-0309-non-reasoning', 'liveMaxCalls': 2, 'plannedLiveCalls': 2}
1 CYCLE_STARTED {}
2 DECOMPOSITION_COMPLETED {'mode': 'live', 'gate_passed': True, 'violation_count': 0, 'snapshot_id': 'snapshot-f83afa04ea4a7dc8'}
3 CANDIDATE_SELECTED {'finding_id': 'agent.agents-md.missing', 'target_path': 'AGENTS.md'}
4 CANDIDATE_APPLY_FAILED {'finding_id': 'agent.agents-md.missing', 'target_path': 'AGENTS.md', 'error': 'RunnerError: missing Markdown link target: src/src/fmc_mcp/config.py->src/src/fmc_mcp/config.py, src/src/fmc_mcp/config.py->src/src/fmc_mcp/config.py'}
5 BUDGET_HALT {'reason': 'max_cycles'}
6 RUN_ENDED {'cyclesRun': 1, 'halted': 'budget', 'promotions': 0}
```

Current status: real production-live attempt; safe failure; no target repo mutation/promotion.

### 6. Full-autonomy gap analysis after failed production pass

`docs/specs/2026-06-15-full-autonomy-gap-analysis.md` correctly framed the result as safe failure, not autonomy.

Key gaps identified there:

1. Top code findings structurally unrunnable.
2. No persistent proposal registry.
3. No branch/base/diff lineage on proposals.
4. No repair/regenerate loop for one bad live diff.
5. Single-file proposal contract dropped multi-file/model-level findings.
6. No live promote -> re-decompose -> re-intake proof.
7. Need repo-local agent wiki / durable operational memory.
8. Execution budget too tight for recovery.

### 7. First remediation slice implemented in current dirty tree

`docs/status/2026-06-15-full-autonomy-gap-remediation-implementation-status.md` states the first remediation slice is implemented. I verified the main surfaces exist in code.

Implemented surfaces verified:

| Claim | Evidence | Status |
|---|---|---|
| Candidate skip observability | `_select_promotable` emits `CANDIDATE_SKIPPED` in `arena/repo_goal_loop.py:394-446` | Implemented |
| Proposal registry | `arena/proposal_registry.py` with `ProposalRegistry`, `ProposalLineage`, JSONL records, `mark`, `pending_for_prompt`, `check_lineage` | Implemented as primitive |
| Base lineage in plans | `ProposalPlan.to_jsonable` includes `baseLineage`; candidates include `base_lineage`, `target_paths`, `intent_hash`, `proposal_key`, `registry_status` | Implemented |
| Component verification domain | `ComponentVerificationDomain` in `arena/proposal_domains.py`, registered before generic file domain | Implemented |
| Live repair retry | `DiffProposerRunner(repair_budget=...)`, loop over attempts, repair context feedback | Implemented |
| Markdown doubled-prefix repair | `_collapsed_repeated_prefix_match` in `arena/runners/diff_proposer.py` | Implemented |
| Multi-target contract | proposal candidates carry `target_paths`; promotion stages/rechecks target set | Contract implemented; execution incomplete |
| Agent wiki scaffolding | `docs/agent-wiki/index.md`, `arena/agent_wiki.py`, wiki lesson pages | Implemented as initial scaffold |

Critical limitation on the `ComponentVerificationDomain` row: it means component/code findings now become proposal candidates with better metadata and inherited gate commands. It does not mean code/component findings are end-to-end promotable. A single-file code component still needs a configured and passing behaviour/test gate before promotion, and multi-file component findings still fail closed because the live diff runner accepts exactly one target file and deterministic apply edits only the primary target. So the keystone gap from the full-autonomy analysis — Build Arena can recognize code work but has not yet proven it can land code/component improvements autonomously — still effectively holds.

## What is verified vs what is merely present

### Verified as working by local tests

- Standard repo tests pass.
- Ruff passes.
- Pyright currently fails because the untracked onboarding acceptance contract imports missing `arena.onboard`. Earlier pyright green output is superseded by the latest run.
- Focused docs/status regression now prevents a failed live decomposition report from using unqualified `ACCEPT` and prevents the word `smoke` in that failed report.
- Proposal registry unit tests cover duplicate detection, promoted skip when manually marked, and lineage mismatch checks.
- Proposal planner tests cover `baseLineage`, candidate target paths, intent hashes.
- Repo goal loop tests cover candidate skip observability, live-call caps, code promotion fail-closed behavior, and target-boundary staging behavior.

### Present but not fully wired/proven

1. Registry lifecycle in the production loop
   - The planner writes registry records.
   - But `repo_goal_loop` does not currently mark proposals as `applied_in_worktree`, `failed_gate`, or `promoted` during real loop execution.
   - `pending_for_prompt()` exists but `_live_diff_apply` passes `pending_proposals=tuple()`.
   - Practical result: registry is a useful primitive, but not yet a complete lifecycle control plane.

2. Multi-target candidates
   - Candidates can carry multiple `target_paths`.
   - Promotion checks exact staged set against `target_paths`.
   - But live diff apply still requires exactly one target file: `DiffProposerRunner._single_target_path` raises `RunnerError('diff proposer requires exactly one target file')` for multi-file hypotheses.
   - Deterministic apply edits only the primary `target_path`.
   - Practical result: multi-target is safe/fail-closed but not yet capable of landing multi-file improvements.

3. Closed-loop live proof
   - Code path exists for promotion followed by another cycle/decomposition.
   - The `fmc-mcp` production run did not reach it because promotions were zero.
   - Current tests include fixture-level proof, but there is no real target-project live run showing promote -> re-decompose -> re-intake.

4. Broad unattended autonomy
   - Still lacks dashboard/control plane, rollback endpoint/operator path, and proven multi-cycle production behavior.
   - Semantic ablation gate remains advisory unless a real live ablation runner is added and validated.

## Latest verification run

After the latest terminology/report correction and status-report edits, these commands were rerun in this Hermes terminal session:

```text
uv run pytest tests -q
# PASS — full suite completed with skipped onboarding acceptance cases where ARENA_CALIBRATION_PATH was not set

uv run ruff check .
# PASS — All checks passed!

uv run pyright
# FAIL — 2 errors
# tests/test_onboarding_acceptance.py:95:10 - Import "arena.onboard" could not be resolved
# tests/test_onboarding_acceptance.py:118:10 - Import "arena.onboard" could not be resolved
```

Earlier in this same session, before the untracked onboarding acceptance file appeared in the status scan, `pyright` passed. The latest ground truth is the failing `pyright` result above. The failure is caused by an untracked RED contract file whose own header says `arena/onboard.py` is intentionally missing until implemented.

These are real command results from this session, but they were not independently re-executed by Opus. The Opus review below inspected the report/code/artifacts read-only and treated the previous test results as Hermes-provided evidence.

## Independent Opus verification already available

Artifact:

`reports/2026-06-15-full-autonomy-implementation-final-opus-review.json`

Opus verdict from that artifact: `pass`, blockers: none.

But Opus gave important non-blocking notes that are production-relevant:

1. Proposal registry is effectively write-only inside the loop.
2. Multi-path candidates fail closed but cannot make progress.
3. Docs candidates can fail on README-less repos due to required source-reference gate.
4. Markdown auto-repair can rewrite to an unintended-but-existing file; quality risk, not direct safety hole.
5. Agent-wiki secret rejection is best-effort, not complete DLP.
6. Deterministic mode on non-git targets may fail ungracefully; production targets are expected to be git repos.

I agree with those notes. They do not invalidate the implementation slice, but they do block a confident broad production-run claim.

## Independent Opus verification of this audit

Artifact:

`reports/2026-06-15-current-status-timeline-production-readiness-opus-review.json`

Opus verdict on this audit: initial `revise`, blockers: none. A second rereview also returned `revise` for one stale `Pyright passes` bullet. That contradiction was fixed. Final narrow Opus check artifact:

`reports/2026-06-15-current-status-timeline-production-readiness-opus-final-check.json`

Final Opus check verdict: `pass`; blockers: none.

Required corrections from Opus were applied in this report:

1. The report now explicitly says the keystone code-findings gap still effectively holds: code/component findings are better represented but not proven end-to-end promotable, so the only proven promotable surface remains documentation/Markdown.
2. The report now qualifies local verification as Hermes-terminal command evidence, not independently re-executed by Opus.

## Production-readiness verdict

### Safe to claim

Build Arena can run a bounded, operator-authorized live repo-goal attempt on a target git repo using live decomposition and live diff proposal. It has fail-closed gates that can prevent promotion when the model output is invalid.

### Not safe to claim

Do not claim Build Arena is ready for broad unattended production autonomy.

Do not claim the `fmc-mcp` run was a production improvement. It was a production attempt that promoted nothing.

Do not claim the closed loop is proven live. The live promote -> re-decompose -> re-intake sequence has not been demonstrated on a real target project.

## Blockers before a production run on a target project

This depends on what "production run" means.

### For one bounded operator-supervised target-project attempt

Blockers / required gates:

1. Target repo must be clean and git-backed.
2. Target repo must have a valid `.arena/goal.toml` and verified local quality/test commands.
3. Operator must explicitly authorize live model spend and local mutation/promotion scope.
4. Use explicit model and call budget; never implicit provider defaults.
5. Must preserve artifacts outside the target repo.
6. Must be prepared for safe zero-promotion outcome.
7. Current Build Arena dirty tree should be reviewed/committed or intentionally run from dirty state with the exact diff recorded.
8. The untracked onboarding acceptance contract (`tests/test_onboarding_acceptance.py`) must either be completed by implementing `arena/onboard.py` or explicitly excluded from the run's typecheck scope. Right now it makes `uv run pyright` fail.

I would allow a bounded supervised attempt only if the owner accepts "may promote nothing" as a valid outcome, if the dirty Build Arena implementation state is explicitly in scope, and if the pyright-failing onboarding RED contract is either resolved or deliberately out of scope for that attempt.

### For broad unattended production autonomy

Blockers:

1. Registry lifecycle not fully wired into loop execution.
   - Need mark `applied_in_worktree`, `failed_gate`, `promoted` and feed pending/failed records into live proposer prompts.

2. Multi-target execution incomplete.
   - Need live/deterministic apply support for multi-file candidates, or explicit skip behavior that avoids divergence churn.

3. No real live closed-loop proof.
   - Need a recorded run with promotion followed by fresh decomposition/intake before the next candidate.

4. Control plane and rollback still absent.
   - Need dashboard/operator status, pause/stop/rollback path, and auditable decision points.

5. Semantic ablation remains advisory.
   - Need real ablation/verifier runner if this is supposed to be load-bearing.

6. Documentation/reporting discipline still needs hardening.
   - The `ACCEPT`/failed-gate wording and "smoke" terminology confusion show the reporting layer can still mislead the owner unless tests lock the wording.

7. Current repo state is dirty.
   - Until committed or intentionally packaged, the latest implementation is not a stable handoff baseline.

## Recommended next action

Before another real target-project production attempt:

1. Commit or explicitly snapshot the current dirty Build Arena remediation state.
2. Add the additional tests Opus recommended for:
   - registry lifecycle after promotion,
   - live-diff multi-path fail-closed behavior,
   - deterministic docs candidate on README-less repo,
   - repair-then-still-failing cleanup.
3. Wire registry lifecycle into `repo_goal_loop` enough that failed/promoted/pending proposals are visible to the next live proposer prompt.
4. Run one supervised, bounded target-project attempt with enough cycles to recover from one candidate failure, but with strict promotion limits.
5. Do not call the result success unless it records an actual promoted change and then a fresh decomposition/intake afterward.
