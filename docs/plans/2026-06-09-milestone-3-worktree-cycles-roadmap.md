# Build Arena Milestone 3 Worktree-Cycle Roadmap

> **For Hermes:** Use `hermes-kanban-operations`, `writing-plans`, and `disciplined-project-delivery` when executing this roadmap. Do not start worker execution until Phase 0 is deliberately unblocked and completed.

**Goal:** Move Build Arena from verified synthetic infrastructure to a practical, real-repository improvement loop: choose a target, propose a bounded diff, apply it in a worktree, verify it mechanically, record evidence, and package owner-gated PR candidates.

**Architecture:** Keep the existing worktree, event-log, budget/divergence, failure-ledger, and fail-closed LLM-adapter foundations. Add only the missing middle: per-repo goal config, generic scorer, deterministic target picker, fail-closed diff proposer, worktree-only cycle wiring, mechanical evidence, and operator-invoked PR packaging.

**Source reviews:**
- Fable strategy artifact: `docs/verification/2026-06-09-fable-build-arena-strategy-review.md`
- Claude Code/Fable implementation-plan comparison: `docs/verification/2026-06-09-fable-milestone-3-plan-comparison.md`
- Claude Code/Fable roadmap/Kanban review: `docs/verification/2026-06-09-fable-roadmap-kanban-review.md`

**Kanban board:** `build-arena`

---

## Review status

Claude Code/Fable reviewed this roadmap and the `build-arena` Kanban card set after initial creation. Verdict: `ACCEPT_WITH_CHANGES`. The roadmap now incorporates the concrete fixes from that review:

- stable repo-local review artifacts instead of `/tmp` references
- explicit pilot-repo goal-config ownership
- explicit configured `worktree_root` safety audit
- `ablation_advisory` default semantics
- `AgentRunner` protocol requirement for the diff proposer
- candidate-branch-before-worktree-teardown ordering
- mechanical dry-run PR gate separated from live push/PR authorization
- explicit dependency links/comments on Kanban cards

---

## Roadmap position

Build Arena currently has strong anti-fabrication infrastructure, but has not yet improved a real repo. Fable’s core correction is to stop expanding decomposition/meta-verification and close the smallest useful loop:

1. Define what “better” means for a target repo through `goal.toml`.
2. Score real repos from their own commands, not calibration hardcoding.
3. Pick targets mechanically before LLM target selection.
4. Let an LLM propose one bounded diff.
5. Accept/reject via deterministic gates and command output.
6. Package verified candidates into owner-gated PRs.

Promotion remains human/owner-gated. LLMs propose and critique; deterministic checks decide acceptance.

---

## Global cut-lines

Do **not** build these in Milestone 3:

- dashboard
- bandit learning
- decomposition-informed target selection
- Project Model v0/v1 cross-repo adoption
- weighted intake scorecard integration
- multi-repo autonomous operation
- autonomous promotion/merge to main
- real ablation runner
- rollback endpoint beyond normal git/PR revert
- GitHub issue/project board automation beyond the requested Kanban tickets

---

## Phase 0 — Anchor and unblock

**Kanban:** `t_6ff0635f` — `BA-M3-00 Phase 0: Anchor roadmap and unblock worktree-only cycles`

**Owner:** controller only

**Intent:** Make the repo’s own governance agree with the desired next step before workers touch implementation.

**Expected changes:**
- Commit/land `docs/verification/2026-06-09-fable-build-arena-strategy-review.md` as the source artifact.
- Keep this roadmap current.
- Archive Fable review artifacts under `docs/verification/`, not `/tmp`.
- Verify pilot repo viability and record the selected pilot:
  - candidate default: `/home/leonb/projects/fmc-mcp`
  - prove the path is a git repo
  - identify its normal test/check command
  - prove the command can run, or record the blocker
  - record whether it has a GitHub remote if Phase 4 live PRs are expected
- Decide and record the production `worktree_root` location for cycle worktrees. Prefer a root outside the pilot repo so the pilot repo’s before/after `git status` audit remains clean. Later zero-write gates must audit against the configured `worktree_root` recorded in evidence, not an assumed literal path.
- Rewrite or supersede `docs/verification/2026-06-05-pre-live-readiness-register.json` so worktree-only cycles are blocked only by internal criteria:
  - generic scorer exists
  - fail-closed proposer tests pass
  - per-repo boundary config exists
- Move PMV1/cross-repo adoption blockers to non-blocking ecosystem/decomposition-informed tracking.
- Update `AGENTS.md` status language:
  - current verification is against the synthetic calibration repo unless otherwise proven
  - the ablation keyword gate is advisory for real cycles until a real ablation runner exists

**Acceptance gates:**
- Readiness register no longer blocks naive worktree-only cycles on PMV1/cross-repo adoption.
- Roadmap and governance changes are mechanically checked, not just “grep-verifiable.” Minimum proof commands:
  - `git diff --check`
  - scan readiness register for `blocksWorktreeOnlyPatchCycle` on PMV1/cross-repo adoption items and prove those no longer block naive cycles
  - scan this roadmap and card comments for dangling temporary source-file references
  - `git -C <pilot-repo> rev-parse --show-toplevel`
  - run or document the pilot repo’s normal check command
- No implementation workers start before this phase is completed.

---

## Phase 1 — Goal config and generic scoring

### Phase 1A — `goal.toml` schema and loader

**Kanban:** `t_d099446a` — `BA-M3-01 Phase 1: Add per-repo goal.toml schema and loader`

**Owner:** safe to delegate after Phase 0

**Expected files:**
- Create `scorer/goal_config.py`
- Create `tests/test_goal_config.py`
- Add `.arena/goal.toml` for Build Arena as part of this phase.
- Add/update fixture goal configs for calibration tests.

**Pilot ownership:** the pilot repo’s real `goal.toml` is **not** delegated to a worker by default. It is controller-owned after Phase 0 because it requires owner/pilot anchoring answers and real command verification.

**Contract fields:**
- test command
- coverage source/floor
- lint/typecheck commands
- optional runtime proxy command
- composite scoring weights
- out-of-scope paths
- read-only paths
- diff-size caps by lines/files

**Acceptance gates:**
- Missing required commands fail closed.
- Defaults are deterministic and tested.
- Config hash can be carried into scorer provenance.
- Existing calibration tests remain green or are updated through explicit compatibility fixtures.

### Phase 1B — Config-driven scorer

**Kanban:** `t_6ea789cf` — `BA-M3-02 Phase 1: Make scorer config-driven and update scorer lock`

**Owner:** implementation is delegable; scorer-lock update is controller/operator-owned

**Expected changes:**
- `scorer/engine.py`: remove hardcoded `--cov=validatorlib`.
- `scorer/engine.py`: remove hardcoded `benchmarks/runtime_proxy.py`.
- `scorer/engine.py`: stop assuming `repo/src` for complexity; Fable identified at least two assumptions to check (`repo/"src"` around current `scorer/engine.py` lines 134 and 179).
- `scorer/engine.py`: use goal-config weights in composite score.
- `arena/boundary.py`: accept goal-config read-only/out-of-scope paths.
- `ScoreRecord` provenance includes goal-config content hash.

**Tests:**
- `tests/test_generic_scorer.py` with at least two fixture repo layouts.
- Existing scorer determinism, lock, and calibration-ordering tests remain green.

**Acceptance gates:**
- Same git OID rescoring is deterministic within existing tolerance.
- No `validatorlib`, `runtime_proxy.py`, or fixed `repo/src` assumptions remain in generic scorer logic.
- `scripts/update_scorer_lock.py` is run by controller/operator after review.

---

## Phase 2 — Deterministic target and bounded diff proposal

### Phase 2A — Deterministic target picker

**Kanban:** `t_c3ad0d70` — `BA-M3-03 Phase 2: Add deterministic target picker`

**Owner:** safe to delegate after Phase 1

**Expected files:**
- Create `arena/target_picker.py`
- Create `tests/test_target_picker.py`

**Signals:**
- scorer output/coverage gaps where available
- lint density where available
- complexity
- git churn
- TODO count
- goal-config exclusions and read-only paths

**Acceptance gates:**
- Stable ordering on fixture repos.
- Excludes out-of-scope/read-only paths.
- No LLM calls.
- Output is a deterministic `TargetSelection` evidence record.

### Phase 2B — Patch gate and fail-closed diff proposer

**Kanban:** `t_eeafe5ff` — `BA-M3-04 Phase 2: Add patch gate and fail-closed diff proposer`

**Owner:** safe to delegate using fake transports only; no live LLM/API calls in this card

**Expected files:**
- Create `arena/patch_gate.py`
- Create `arena/runners/diff_proposer.py`
- Create `arena/proposer_hypothesizer.py`
- Create `tests/test_patch_gate.py`
- Create `tests/test_diff_proposer.py`

**Patch gate requirements:**
- `git apply --check` must pass.
- diff numstat must stay within goal-config caps.
- touched paths must pass boundary checks.
- malformed, binary, oversized, and out-of-bounds diffs reject without touching the worktree.

**Diff proposer requirements:**
- Inputs: goal config, one target, file contents, explicit success criterion.
- Output: unified diff plus stated intent/provenance.
- Empty, truncated, prose-only, cancelled, malformed, boundary-violating, or oversized outputs reject fail-closed.
- Fake-transport tests cover valid and invalid cases.
- The diff proposer implements the `AgentRunner` protocol from `arena/protocols.py` so `RunnerRouter` can work unchanged. Its `apply` behavior is: validate through `patch_gate`, apply with `git apply` inside the worktree, and return the patch path/provenance.

**Acceptance gates:**
- All invalid fake outputs reject without worktree mutation.
- Valid fake diff applies only after patch-gate acceptance.
- Hypothesis/fingerprint path integrates with existing ledger semantics.

---

## Phase 3 — Worktree-only cycle and mechanical evidence

**Kanban:** `t_d1682f0d` — `BA-M3-05 Phase 3: Wire worktree-only cycle and mechanical evidence`

**Owner:** controller only

**Expected changes:**
- `verifier/config.py` and `verifier/engine.py`: add `ablation_advisory` behavior.
  - Default must remain `False` so calibration/strict-gate behavior is unchanged.
  - Real-cycle/pilot config sets `ablation_advisory=True`.
  - `AblationResult` is emitted either way.
  - When advisory, keyword load-bearing rejection does not block real cycles.
  - The current ollama-only `VerifierConfig.__post_init__` constraint must be relaxed or scoped so advisory/non-ollama real-cycle config is valid without weakening strict calibration tests.
- `arena/loop.py`: replace real-repo `PROMOTE` path with candidate packaging; keep `GitPromoter` for calibration tests.
- Candidate branch ordering: create `arena/candidate/<cycle_id>` from the worktree HEAD **before** `WorktreeManager.teardown`, because teardown deletes `arena/cycle/<id>` branches.
- Create `arena/evidence.py` for mechanical per-cycle reports from event log, score records, command exits, diff numstat, configured `worktree_root`, budget config, and provenance hashes.
- Verify/fix ledger interface mismatch around `ctx.ledger.record` versus `record_failure`/`record_success`.

**Acceptance gates:**
- No baseline promotion to main.
- Candidate branches use `arena/candidate/<cycle_id>` semantics.
- Evidence files contain no model-written success claims; all claims trace to commands/events/scores.
- Budget breach and divergence halt tests produce `HaltRecord` evidence.
- Calibration tests remain green.

---

## Phase 4 — Owner-gated PR packaging

**Kanban:** `t_95049964` — `BA-M3-06 Phase 4: Add owner-gated PR packager`

**Owner:** controller only

**Expected files:**
- Create `arena/pr_packager.py`
- Create operator CLI entrypoint, for example `python -m arena.package_pr --candidate <id>`
- Create `tests/test_pr_packaging.py`

**Requirements:**
- Dry-run mode renders PR body without pushing.
- Push/open-PR mode uses `gh` only after explicit operator invocation.
- PRs target the target/pilot repo’s remote, never the Build Arena repo unless Build Arena itself is the selected pilot.
- PR body claims are byte-traceable to evidence files and score records.
- Fabricated-claim fixture fails.

**Acceptance gates:**
- No automatic merge.
- No loop-internal PR publishing.
- Owner merge/reject outcome can be recorded back into ledger as outcome data.

---

## Phase 5 — Milestone 3 proof run

**Kanban:** `t_5d7abe71` — `BA-M3-07 Milestone gate: Run pilot cycles and produce owner-gated PR evidence`

**Owner:** controller only

**Default pilot:** `/home/leonb/projects/fmc-mcp`, unless Phase 0 chooses a different pilot.

**Acceptance gates:**
- At least 5 cycles run within budget.
- At least 1 candidate passes all mechanical gates.
- Zero writes outside the configured `worktree_root` or the intended candidate branch path, audited from events, the evidence-recorded `worktree_root`, and before/after `git status` of the target repo.
- Every reject maps to a `RejectReason` and command transcript.
- One injected budget breach and one injected divergence halt fire and produce `HaltRecord` evidence.
- Budget config used for the run is recorded in evidence.
- At least 2 dry-run PR bodies render with byte-traceable claims from evidence and score records. Live push/open-PR is an operator-authorized outcome, not an unconditional gate.

**Non-goals:**
- no autonomous merge
- no dashboard
- no decomposition-informed target selection
- no bandit learning
- no multi-repo operation

---

## Kanban ticket index

Execution has started with Phase 0 (`t_6ff0635f`) by explicit Leon authorization. The root tracker and downstream implementation cards remain blocked intentionally so they do not auto-dispatch before their prerequisites are satisfied. Dependency links have been added through Kanban where applicable; card comments and bodies contain the post-review dependency and scope refinements.

Dependency summary:
- Depends on: `t_d099446a` depends on `t_6ff0635f`.
- Depends on: `t_6ea789cf` depends on `t_d099446a`.
- Depends on: `t_c3ad0d70` depends on `t_d099446a`.
- Depends on: `t_eeafe5ff` depends on `t_d099446a`.
- Depends on: `t_d1682f0d` depends on `t_d099446a`, `t_6ea789cf`, `t_c3ad0d70`, and `t_eeafe5ff`.
- Depends on: `t_95049964` depends on `t_d1682f0d`.
- Depends on: `t_5d7abe71` depends on all BA-M3-00 through BA-M3-06 cards.

| ID | Title | Execution owner | Branch/workspace |
|---|---|---|---|
| `t_bb1a675f` | BA-M3 Roadmap: Worktree-only autonomous improvement loop | Tracker | `dir:/home/leonb/projects/build-arena` |
| `t_6ff0635f` | BA-M3-00 Phase 0: Anchor roadmap and unblock worktree-only cycles | Controller | `ba/m3-phase0-anchor-unblock` |
| `t_d099446a` | BA-M3-01 Phase 1: Add per-repo goal.toml schema and loader | Delegable | `ba/m3-goal-config-loader` |
| `t_6ea789cf` | BA-M3-02 Phase 1: Make scorer config-driven and update scorer lock | Delegable + controller lock update | `ba/m3-generic-scorer` |
| `t_c3ad0d70` | BA-M3-03 Phase 2: Add deterministic target picker | Delegable | `ba/m3-target-picker` |
| `t_eeafe5ff` | BA-M3-04 Phase 2: Add patch gate and fail-closed diff proposer | Delegable with fake transports only | `ba/m3-patch-gate-diff-proposer` |
| `t_d1682f0d` | BA-M3-05 Phase 3: Wire worktree-only cycle and mechanical evidence | Controller | `ba/m3-worktree-cycle-evidence` |
| `t_95049964` | BA-M3-06 Phase 4: Add owner-gated PR packager | Controller | `ba/m3-owner-gated-pr-packager` |
| `t_5d7abe71` | BA-M3-07 Milestone gate: Run pilot cycles and produce owner-gated PR evidence | Controller | `ba/m3-pilot-acceptance-run` |

Useful commands:

```bash
hermes kanban --board build-arena list
hermes kanban --board build-arena show t_6ff0635f
hermes kanban --board build-arena unblock t_6ff0635f
```

---

## Execution policy

- Start with Phase 0 only.
- Do not unblock implementation cards until Phase 0 is complete and reviewed.
- At most three worker cards should run in the first implementation wave:
  - `t_d099446a` goal config
  - `t_c3ad0d70` target picker
  - `t_eeafe5ff` patch gate / diff proposer with fake transports
- Wave-one interface dependency: `t_d099446a` should either merge first, or `t_c3ad0d70` and `t_eeafe5ff` must code against a frozen goal-config interface stub documented by `t_d099446a`.
- Controller owns all `arena/loop.py` integration and all push/PR side effects.

---

## Milestone 3 close-out (BA-M3-07)

**Status:** BA-M3-07 acceptance gate passed and committed on `ba/m3-pilot-acceptance-run` (commit `688c182`, 2026-06-10).

**Evidence:** `docs/verification/2026-06-10-m3-pilot-cycle-evidence.md` plus the `docs/verification/2026-06-10-m3-pilot/` artifact tree (summary, per-cycle evidence, halt/reject evidence, dry-run PR bodies, candidate-branch diff audit, exact harness, candidate diff).

**Gate results:** 5 cycles, 5 promoted candidate branches, 2 dry-run PR bodies with byte-traceable claims, injected budget halt (`BUDGET_EXHAUSTED_ZERO_PROMOTIONS`) and divergence halt (`BOUNDARY_VIOLATION_ATTEMPT`), one reject mapped to a `RejectReason` with transcript, canonical pilot checkout head/status unchanged before vs. after, configured worktree root empty after teardown. Verified clean: `pytest`, `ruff`, `pyright`, `git diff --check`.

**Bug found and fixed during the pilot:** `CandidatePackager` used `git add -A` and could leak `.arena/` evidence/config/runtime artifacts into candidate branches. Fixed to reset all `.arena/` paths before the candidate commit with a fail-closed staged-path guard, with a regression test that plants `.arena/patches/` and a sibling `.arena/runtime.json` and asserts zero `.arena/` paths in the candidate diff while worktree evidence artifacts survive.

**Honesty notes (read before treating M3 as broadly proven):**
- The "every reject maps to a `RejectReason` and transcript" gate was exercised by exactly **one injected** `RUNNER_ERROR`. Organic reject-reason diversity is unproven.
- All five promoted candidates are the **same static fake-transport patch** with identical `score_delta` (25.854327). This proves cycle/packaging/evidence mechanics, **not** organic candidate variation. "5 candidates promoted" must not be read as five independent successes.
- Live LLM/API transport, organic rejects, and operator-authorized live PR push are explicitly deferred to M4.

**Follow-up cards filed:**
- `.arena/` allowlist enforcement as a standing boundary-invariant test (fold in the top-level `.arena` file edge case).
- Organic reject-reason coverage matrix once live transport exists.

**Fable review:** initial `ACCEPT_WITH_CHANGES` (widen artifact exclusion + commit), re-review `ACCEPT` after the `.arena/` widening. Transcripts embedded in the evidence report.
- Worker self-reports are not proof. Proof is file diff + test output + mechanical evidence.
