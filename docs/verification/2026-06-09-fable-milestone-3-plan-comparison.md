I've finished the read-only inspection. I read the strategy review, `scorer/engine.py`, `arena/loop.py`, `arena/runners/claude_code.py`, `verifier/engine.py` + `config.py`, `arena/hypothesizer.py`, `router.py`, `boundary.py`, `worktrees.py`, `ledger.py`, `protocols.py`, `scorer/lock.py`, `project_model_llm.py`, `AGENTS.md`, and the pre-live readiness register. Here is the deliverable.

## VERDICT

The Hermes plan has the right skeleton (phase 0 first, worktree isolation, owner as merge gate, fail-closed proposer contract) but it is over-parallelized for what is genuinely ~3 small new modules plus wiring, and it misses three repo-specific blockers I confirmed by inspection: the readiness register *procedurally blocks worktree cycles on cross-repo adoption* (PMV1-002/003, GAP-001 all set `blocksWorktreeOnlyPatchCycle: true`), the verifier's keyword-based ablation gate is **load-bearing** and will reject real candidates as `ABLATION_REASONING_NOT_LOAD_BEARING` unless demoted, and the scorer is content-locked (`.arena/scorer.lock.toml`) so parallel workers editing `scorer/` will collide on lock updates. Its triple-review lanes per slice also reproduce the meta-verification regress the strategy review just diagnosed. Adopt a tighter version: phase 0 controller-only, then at most 3 workers on the two empty sockets plus deterministic gating, controller owns all loop integration.

## FABLE PLAN

**Target restated:** worktree-only autonomous improvement cycles on a real repo — naive mechanical target selection, fail-closed LLM diff proposer, mechanical verifier acceptance, append-only evidence, candidate branches packaged into owner-gated PRs. No baseline promotion to main, no decomposition stack, no bandit.

**What already exists and is reused unchanged:** loop state machine (`arena/loop.py`), `WorktreeManager` (`arena/worktrees.py`), budget/divergence (`arena/budget.py`, `arena/divergence.py`), event log (`arena/events.py`), fingerprints + failure ledger (`arena/fingerprints.py`, `arena/ledger.py`), runner router with credit fallback (`arena/router.py`), the fail-closed LLM transport pattern (`arena/project_model_llm.py:LiveProjectModelLLM`), `ClaudeStreamGuard` view-before-edit enforcement (`arena/runners/claude_code.py`).

### Phase 0 — Unblock and anchor (controller only, ~1 commit)
1. Commit `docs/verification/2026-06-09-fable-build-arena-strategy-review.md` (it is the direction source; currently untracked).
2. **Rewrite the readiness register** (`docs/verification/2026-06-05-pre-live-readiness-register.json` or a v2 successor): internal milestones (steps 4–5) gated only on internal criteria — generic scorer exists, proposer fail-closed tests pass, boundary config per repo. Move PMV1-002/003 to a separate ecosystem tracker that blocks nothing. Re-scope GAP-001/GRAPH-001 as blockers for *decomposition-informed* cycles only, not naive-target cycles. Without this, Milestone 3 is blocked by the project's own governance.
3. Update `AGENTS.md` status section: "verified against the synthetic calibration repo only"; record the ablation-advisory decision (Phase 2 below).
4. Write the orchestration plan doc `docs/plans/2026-06-09-milestone-3-worktree-cycles.md` with the gates below verbatim.

### Phase 1 — `goal.toml` + generic scorer (delegable, one worker)
- **New:** `scorer/goal_config.py` — schema + loader for a per-target-repo `goal.toml`: test command, coverage source/floor, lint/typecheck commands, optional runtime proxy command, composite weights, out-of-scope paths, read-only paths, diff-size cap (lines + files).
- **Change:** `scorer/engine.py` — `_pytest_coverage` (drop hardcoded `--cov=validatorlib`, `engine.py:201`), `_runtime_proxy` (drop `benchmarks/runtime_proxy.py`, `engine.py:240`), `_cyclomatic_average` (drop fixed `repo/"src"`, `engine.py:134`), `_composite` (weights from config, `engine.py:155-172`) — all driven by the goal config. Include the goal-config content hash in `ScoreRecord` provenance.
- **Change:** `arena/boundary.py` — accept per-repo read-only paths from goal config (current `DEFAULT_READ_ONLY_DIRS` are Build-Arena-specific).
- **New files:** `.arena/goal.toml` for build-arena itself; a `goal.toml` for the pilot repo (fmc-mcp), authored with Leon's anchoring answers; calibration repo gets its own `goal.toml` so existing calibration tests keep passing as "just another configured repo."
- **Tests:** `tests/test_goal_config.py` (parse, defaults, rejection of missing commands), `tests/test_generic_scorer.py` (two fixture repos with different layouts, determinism on same OID); `tests/test_scorer_determinism.py`, `test_scorer_lock.py`, `test_calibration_ordering.py` stay green.
- **Controller-owned step:** running `scripts/update_scorer_lock.py` after the scorer change — the lock is content-addressed over `scorer/**.py` and is an operator action per AGENTS.md.

### Phase 2 — target picker, patch gate, diff proposer (delegable, two workers)
- **New:** `arena/target_picker.py` — deterministic ranking of candidate files by lint density, complexity, coverage gaps (reusing scorer outputs), `git log` churn, TODO count; excludes goal-config out-of-scope and boundary paths; emits a `TargetSelection` evidence record. No LLM. Test: `tests/test_target_picker.py` (fixture repo, stable ordering, exclusion behavior).
- **New:** `arena/patch_gate.py` — pure deterministic gate on a unified diff: `git apply --check`, `git diff --numstat` size caps from goal config, touched-path boundary check. Test: `tests/test_patch_gate.py` (oversize, out-of-bounds, malformed, binary, clean cases).
- **New:** `arena/runners/diff_proposer.py` — fail-closed LLM proposer copying the `LiveProjectModelLLM` pattern (truncation/empty/cancelled/malformed all raise; provenance hashes recorded). Input: goal config + one target + file contents + explicit success criterion. Output: unified diff + stated intent. Implements the `AgentRunner.apply` protocol (`arena/protocols.py:42`) so `RunnerRouter` works unchanged: apply = validate via patch gate, `git apply` in worktree, return patch path. Test: `tests/test_diff_proposer.py` with fake transports — valid diff, prose-instead-of-diff, truncated, oversize, boundary-violating, empty; all non-valid cases must reject without touching the worktree.
- **New:** a real hypothesizer adapter `arena/proposer_hypothesizer.py` that turns (target, intent) into a `Hypothesis` + fingerprint so the existing ledger/fingerprint dedup keeps working (replaces `SymbolicHypothesizer` template arms on the real path; the bandit stays parked).

### Phase 3 — wire the worktree-only cycle (controller only)
- **Change:** `verifier/config.py` + `verifier/engine.py` — add `ablation_advisory: bool = True`; when advisory, `_reject_reason` skips the `load_bearing` rejection (`engine.py:135-136`) but the `AblationResult` is still emitted to the event log. Relax the ollama-only `__post_init__` constraint accordingly. Update `tests/test_verifier_gates.py`, `tests/test_ablation.py`. The keyword check (`verifier/ablation.py`) must not gate real work.
- **Change:** `arena/loop.py` — replace the PROMOTE branch on the real-repo path with a **CandidatePackager**: commit in worktree, create `arena/candidate/<cycle_id>` branch, write evidence report, tear down worktree, do *not* advance baseline (all cycles branch from the same baseline OID — one-cycle semantics). `GitPromoter` is untouched for calibration tests.
- **New:** `arena/evidence.py` — per-cycle evidence report generated mechanically from event log + score records: score before/after vectors, commands + exit codes, diff numstat, provenance hashes, event seq range. No model-written prose in the evidence file.
- **Fix:** verify the ledger interface — `loop.py:172` calls `ctx.ledger.record(...)` but `FingerprintFailureLedger` exposes `record_failure`/`record_success`; confirm an adapter exists in tests or add one.
- **Acceptance run (Milestone gate):** ≥5 cycles on the pilot repo within budget; ≥1 candidate passes all mechanical gates; zero writes outside `.arena/worktrees/` audited from events plus `git status` of the target repo before/after; every reject mapped to a `RejectReason` and a command transcript; one injected budget breach and one injected divergence halt fire and produce `HaltRecord`s.

### Phase 4 — owner-gated PR packaging (controller only, outward-facing)
- **New:** `arena/pr_packager.py` + `python -m arena.package_pr --candidate <id>` — operator-invoked only, never called by the loop: push candidate branch, open PR via `gh` with the evidence report as body. Dry-run mode renders the body without pushing.
- **Test:** `tests/test_pr_packaging.py` — generated PR body claims (deltas, commands) must be byte-traceable to the evidence file/score records; a fabricated-claim fixture must fail the test.
- **Milestone gate:** ≥2 candidate PRs opened with complete evidence; Leon merges or rejects; merge outcomes recorded back into the ledger. Merged count is an *outcome metric*, not a build gate.

### Delegation split
- **Safe to delegate** (bounded, deterministic acceptance, isolated worktrees): Phase 1 generic scorer + goal config; Phase 2 target picker, patch gate, diff proposer (fake-transport tests only — no live API calls by workers).
- **Controller must own:** readiness register/AGENTS.md truth edits; scorer lock updates; all `arena/loop.py` wiring; the live acceptance run (spend + side effects); anything that pushes or opens PRs; verification of every worker diff by actually running `uv run pytest -q`, `ruff`, `pyright` and reading the diff — never worker self-reports.

### Cut-lines (do not build)
Bandit learning, decomposition/encyclopedia/gate consumption, weighted intake scorecard, dashboard, rollback endpoint (git revert of a reviewed PR is the rollback), real ablation runner, multi-repo operation, autonomous promotion to main, v0/v1 cross-repo adoption, GitHub-issue work board.

### Risks
- First live proposer contact will likely fail gates (LIVE-002 pattern: syntactically valid, substantively bad). That's signal, not a defect — budget the acceptance run for mostly-reject cycles.
- Generic scorer on a real repo may be slow/flaky (real test suites aren't the calibration fixture); the determinism tolerance and timeouts in `_run` (`engine.py:175`, 120s) will need per-repo config.
- Scope creep back into meta-verification — the orchestration doc should state the freeze explicitly.

## COMPARISON TO HERMES PLAN

**Keep**
- Phase 0 before any workers; the "tighter authorization" option is the right default.
- Worktree-per-worker isolation; controller verifies with `git diff`/tests, not self-reports.
- Lane B/C/D acceptance criteria — they are genuinely mechanical and match what the code needs.
- Owner as the only merge gate; no auto-merge.
- Committing the Fable review artifact first.

**Change**
- **Missing the governance blocker:** the readiness register currently sets `blocksWorktreeOnlyPatchCycle: true` for PMV1-002/003, GAP-001, and GRAPH-001. The Hermes plan's Lane A mentions "normalize the readiness register" in passing but doesn't treat it as a hard phase-0 precondition. It is one — otherwise Lane E violates the project's own written gates.
- **Missing the ablation demotion entirely.** `verifier/engine.py:135` rejects candidates when the keyword-based Lanham probe quorum says reasoning isn't load-bearing. No Hermes lane touches this; Lane E's "5 cycles, one candidate passes" will likely fail on this gate for spurious reasons. It also requires relaxing `VerifierConfig.__post_init__`'s ollama-only constraint.
- **Missing the scorer lock interaction.** `scorer/` changes invalidate the content-addressed lock; `update_scorer_lock.py` is an operator action. A worker delegated Lane B cannot complete it alone, and two workers touching `scorer/` would collide. Controller owns lock updates; only one worker may touch `scorer/`.
- **Over-parallelized:** 5 worktrees / 6 lanes / multi-model splits ("Claude Code / Grok / Codex split" for one adapter) for what the strategy review correctly sizes as "two modules of new code plus config plumbing." Three workers max in wave one; Lane E (loop wiring) and Lane F (PR packaging) are controller work, not delegable — Hermes assigns Lane E to "Hermes/Codex," which puts the highest-regression-risk file (`arena/loop.py`) in a worker's hands.
- **Milestone definition drift:** Hermes' Lane F gate "at least two real improvements merged by Leon" makes the owner's judgment a system acceptance gate the orchestrator is incentivized to push on. Keep merges as an outcome metric; the buildable gate is "≥2 PRs opened with fully traceable evidence."
- **Authorization envelope is broader than needed:** GitHub issue creation, pushing, and PR opening are requested up front, but phases 0–3 need none of them. Grant push/PR rights only at Phase 4.
- **Under-specified integration details the repo makes concrete:** ledger interface mismatch at `loop.py:172`; `GitPromoter._remove_runtime_artifacts` hardcodes `src/`/`tests` (irrelevant if PROMOTE is replaced by packaging, which the Hermes plan never states); `boundary.py` defaults are Build-Arena-specific and must come from goal config for arbitrary repos; composite weights are hardcoded in `_composite`.

**Delete**
- The three-review-lane structure (spec-compliance + quality/security + integration review, multi-model, per lane). This is the meta-verification regress the strategy review diagnosed, rebuilt at the process level. One controller verification pass (run the suite, read the diff) per worker output is the gate; the test suite is the reviewer.
- GitHub-issue/Kanban work board for this push — ~6 work items; the plan doc and branches are sufficient durable state.
- Gemini "broad scan" review lane — no defined acceptance output; it produces prose, and prose isn't a gate.

## RECOMMENDED NEXT ACTION

Execute Phase 0 as the controller, alone, in one commit on a fresh branch: commit the Fable review artifact, write `docs/plans/2026-06-09-milestone-3-worktree-cycles.md` containing the phases and mechanical gates above, rewrite the readiness register so worktree-only cycles are gated solely on internal criteria (generic scorer, fail-closed proposer tests, per-repo boundary config) with cross-repo adoption moved to a non-blocking ecosystem tracker, and update the `AGENTS.md` status section including the ablation-advisory decision. Report back with the diff before spawning the first wave of (at most) three workers: generic scorer + goal config, target picker + patch gate, diff proposer with fake transports.
