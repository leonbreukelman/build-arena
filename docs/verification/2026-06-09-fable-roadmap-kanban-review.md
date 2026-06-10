Review complete. I read the roadmap, the Kanban export, and the prior Fable plan, then verified the load-bearing claims directly against the repo: the readiness register really does set `blocksWorktreeOnlyPatchCycle: true` on the PMV1/GAP items, `arena/loop.py:172` calls `ctx.ledger.record(...)` while `arena/ledger.py` only exposes `record_failure`/`record_success`, the scorer hardcodes `--cov=validatorlib`, `benchmarks/runtime_proxy.py`, and `repo/"src"` (`scorer/engine.py:134,179,201,240`), and the verifier's keyword ablation gate is load-bearing with an ollama-only constraint (`verifier/engine.py:135`, `verifier/config.py:33`). The roadmap correctly carries all of these forward.

## VERDICT: ACCEPT_WITH_CHANGES

The roadmap faithfully preserves the prior critique: scope matches the cut-lines, wave one is capped at three workers, the triple-review-lane meta-verification structure is gone ("worker self-reports are not proof"), deterministic gating precedes any LLM step, the merged-PR gate was correctly converted to "PRs can be opened," and the controller owns `arena/loop.py`, scorer-lock updates, and all push/PR side effects. The remaining problems are a small number of concrete gaps that would cause real confusion or an unfalsifiable safety gate at execution time.

## CRITICAL CHANGES

1. **No card produces the pilot repo's `goal.toml`.** BA-M3-01 covers Build Arena's own config and calibration fixtures only, but BA-M3-07 runs against `/home/leonb/projects/fmc-mcp`, which needs a goal config (test command, boundaries, caps) authored with Leon's input. As written, Phase 5 is unrunnable and a worker has nowhere to look. Assign it explicitly — recommend controller-authored as Phase 3 or Phase 5 prep, since it requires owner answers.

2. **The Phase 5 zero-writes gate names a path the code doesn't define.** `WorktreeManager` takes `worktree_root` as an injected parameter with no production default; nothing in the repo establishes `.arena/worktrees`. The roadmap's central safety audit ("zero writes outside `.arena/worktrees`") is therefore unfalsifiable against actual config. Phase 0 or Phase 3 must pin the worktree-root location, and Phase 5 should audit against "the configured `worktree_root` recorded in evidence." Recommend a root *outside* the pilot repo so the before/after `git status` audit of the pilot stays clean.

3. **`ablation_advisory` default semantics are ambiguous.** "Add `ablation_advisory=True` behavior" doesn't say whether the default flips. If it defaults True, existing strict-gate tests (`tests/test_verifier_gates.py`, `tests/test_ablation.py`) change meaning; if False, the pilot config must set it. Specify: field defaults **False** (calibration behavior unchanged), real-cycle config sets True, `AblationResult` still emitted either way, and state how the ollama-only `__post_init__` constraint (`verifier/config.py:33-34`) is handled.

## IMPORTANT IMPROVEMENTS

- **`/tmp` source references will dangle.** The roadmap and tracker card cite `/tmp/build-arena-m3-...` and `/tmp/build-arena-fable-milestone3-plan-report.md` as source inputs. Future workers won't have them. Phase 0 should archive the plan report into `docs/verification/` and the references updated.
- **Cards have no explicit dependency lines.** Blocking-by-default is correct, but ordering lives only in priority numbers and the roadmap's execution policy. A controller unblocking out of order gets no in-card warning. Add one "Depends on: <card id(s)>" line per card.
- **BA-M3-04 dropped the runner-protocol contract.** The prior Fable plan specified the diff proposer implements the `AgentRunner` protocol (`arena/protocols.py`) so `RunnerRouter` works unchanged; the roadmap and card omit it. Without it a worker will invent an interface and Phase 3 wiring becomes rework.
- **Wave-one interface dependency.** Execution policy runs BA-M3-01, -03, -04 in parallel, but -03 and -04 consume goal-config types (exclusions, caps) from -01. Add one sentence: either -01 merges first within the wave, or -03/-04 code against a frozen interface stub.
- **Candidate branch vs. teardown ordering.** `WorktreeManager.teardown` deletes the `arena/cycle/<id>` branch (`arena/worktrees.py:46`). Phase 3 must create `arena/candidate/<cycle_id>` from the worktree HEAD *before* teardown, or candidates evaporate. One sentence in the card prevents a confusing bug.
- **Phase 5 PR gate is conditional, hence weakly falsifiable.** "2 PRs can be opened if operator authorizes" mixes a mechanical claim with an authorization. Split it: the gate is "2 dry-run PR bodies render with byte-traceable claims" (unconditional, mechanical); live push/PR is an operator-authorized outcome, not a gate. Also state in Phase 4 that PRs target the *pilot repo's* remote, not build-arena's.
- **Phase 0 should verify pilot viability.** I could not confirm `/home/leonb/projects/fmc-mcp` exists from this session. Add to Phase 0: confirm the pilot exists, its test suite runs, and (if Phase 4 push is wanted) it has a GitHub remote. Also replace "grep-verifiable" with the actual proof commands, mirroring the register's existing `proofCommand` convention.

## CARD UPDATES

- `t_bb1a675f`: replace the `/tmp/build-arena-fable-milestone3-plan-report.md` source reference with the archived `docs/verification/` path once Phase 0 lands it.
- `t_6ff0635f`: add four expected changes — archive the plan report into `docs/verification/`; verify pilot repo viability (exists, tests run, GitHub remote present) and record the choice; decide and record the production `worktree_root` location; list explicit proof commands for the "grep-verifiable" gate.
- `t_d099446a`: resolve "if scope allows" to an explicit in/out decision; state that the *pilot* repo's `goal.toml` is out of scope here and controller-owned in Phase 3/5 prep; add "Depends on: t_6ff0635f".
- `t_6ea789cf`: add "Depends on: t_d099446a"; note there are two `repo/"src"` assumptions in `scorer/engine.py` (lines 134 and 179), not one.
- `t_c3ad0d70`: add "Depends on: t_d099446a (goal-config exclusion types; frozen interface stub acceptable if not yet merged)".
- `t_eeafe5ff`: same depends-on line; add requirement "diff proposer implements the `AgentRunner` protocol from `arena/protocols.py` so `RunnerRouter` works unchanged; apply = patch-gate validate, `git apply` in worktree, return patch path".
- `t_d1682f0d`: specify `ablation_advisory` defaults False with real-cycle config setting True, and the `__post_init__` ollama-constraint handling; pin `worktree_root`; add "create candidate branch from worktree HEAD before `WorktreeManager.teardown` deletes `arena/cycle/<id>`"; add "Depends on: t_d099446a, t_6ea789cf, t_c3ad0d70, t_eeafe5ff".
- `t_95049964`: add "PRs are opened against the target/pilot repo's remote, never build-arena's"; add "Depends on: t_d1682f0d".
- `t_5d7abe71`: rephrase the PR gate as dry-run-mechanical plus authorized-live-optional; audit zero-writes against the configured `worktree_root` recorded in evidence rather than a literal path; require the budget config be recorded in evidence; add "Depends on: all BA-M3-00..06".

## ROADMAP UPDATES

- **Source reviews**: swap the `/tmp` reference for the archived path (post-Phase 0).
- **Phase 0**: add pilot-viability verification, plan-report archival, the `worktree_root` decision, and concrete proof commands replacing "grep-verifiable".
- **Phase 1A**: resolve "if scope allows"; add a line assigning pilot `goal.toml` authoring to the controller.
- **Phase 2B**: add the `AgentRunner` protocol requirement.
- **Phase 3**: state `ablation_advisory` default semantics and the candidate-branch-before-teardown ordering.
- **Phase 5**: split the PR gate (dry-run mechanical vs. authorized live); reference configured `worktree_root`.
- **Execution policy**: one sentence on the wave-one interface dependency (BA-M3-01 first, or stub).

## DO NOT CHANGE

The global cut-lines list, the three-worker wave cap, controller ownership of `loop.py`/lock/push, the blocked-by-default card semantics, priority ordering, branch naming (`ba/m3-*` cards; `arena/candidate/*` doesn't collide with the existing `arena/cycle/*` convention), skill assignments (TDD + disciplined-project-delivery for workers, github-pr-and-review-operations only on the packager card), the Phase 1–2 acceptance gates (genuinely mechanical), and the merged-PRs→opened-PRs correction. Do not add timelines, review lanes, or per-card multi-model review — the absence of those is the point.

## FINAL PATCH PLAN

1. Phase 0 additions: archive plan report to `docs/verification/`, pilot viability check, `worktree_root` decision, explicit proof commands (roadmap + `t_6ff0635f`).
2. Assign pilot `goal.toml` authoring to controller; resolve "if scope allows" (`t_d099446a` + Phase 1A).
3. Specify `ablation_advisory` default False / pilot True / ollama-constraint handling (`t_d1682f0d` + Phase 3).
4. Add `AgentRunner` protocol requirement to `t_eeafe5ff` + Phase 2B.
5. Add "Depends on" lines to all eight execution cards.
6. Add candidate-branch-before-teardown note (`t_d1682f0d`).
7. Rewrite Phase 5 gates: configured-`worktree_root` audit, budget config in evidence, dry-run PR gate split (`t_5d7abe71`).
8. Add PR-target-remote clarification to `t_95049964`.
9. Swap `/tmp` references in roadmap + `t_bb1a675f`.
10. Add wave-one sequencing sentence to Execution policy.

These are all small, precise edits — the artifact's architecture, scope discipline, and gate philosophy are sound and should be used as-is once items 1–3 (the critical ones) are applied.
