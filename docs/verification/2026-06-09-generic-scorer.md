# Build Arena BA-M3-02 Generic Scorer Evidence

Date: 2026-06-10T05:03:54Z
Kanban card: `t_6ea789cf` — BA-M3-02 Phase 1: Make scorer config-driven and update scorer lock
Branch: `ba/m3-generic-scorer`

## Scope completed

- `scorer/engine.py` now loads target repo `.arena/goal.toml` through `GoalConfig` and fails closed when it is missing.
- Test, coverage, lint, typecheck, runtime proxy, source roots, coverage floor, and composite weights are now driven by `GoalConfig` instead of calibration-specific assumptions.
- `ScoreRecord` includes `goal_config_sha` and `goal_config_schema_version`; score IDs include the goal-config hash prefix.
- `drift_check` rejects goal-config hash drift.
- `arena/boundary.py` accepts a `goal_config=` keyword and treats goal-config `read_only` and `out_of_scope` paths as protected.
- Build Arena and calibration fixture goal configs now use machine-readable lint/typecheck output.
- Calibration fixture commands use `uv run --no-project --with ...` so scoring temp repos does not create `uv.lock`.
- Scorer execution sets `PYTHONDONTWRITEBYTECODE=1` and removes configured coverage outputs after reading to avoid mutating target repos.
- `.arena/scorer.lock.toml` was refreshed after locked scorer changes.

## TDD and regression evidence

- `tests/test_generic_scorer.py` first failed for missing provenance fields, ignored goal-config coverage, missing-config behavior, and missing boundary `goal_config` support.
- Calibration ordering tests exposed text-mode ruff/pyright command flattening; configs were corrected to emit JSON metrics.
- Loop promotion tests exposed `uv.lock` mutation from `uv run --with`; calibration commands were corrected to `--no-project`.
- Fable required fail-closed unreadable ruff/pyright output; tests were updated to prove unreadable output returns `999`.
- Fable requested multi-source-root coverage; added a `lib` + `plugins` fixture test covering PYTHONPATH and complexity scanning.
- Mutation scan found coverage/bytecode artifacts; added and passed `test_scorer_does_not_leave_runtime_artifacts_in_target_repo`.

## Verification completed

- `uv run pytest tests/test_coverage_closure.py::test_scorer_error_and_fallback_paths tests/test_loop_phase4.py::test_calibration_loop_promotes_one_positive_patch -q` — passed: `2 passed`.
- `uv run pytest tests/test_generic_scorer.py tests/test_boundary.py tests/test_goal_config.py tests/test_scorer_lock.py tests/test_scorer_determinism.py tests/test_calibration_ordering.py -q` — passed.
- `uv run pytest tests -q` — passed.
- `uv run ruff check .` — passed.
- `uv run pyright` — passed: `0 errors, 0 warnings`.
- Hardcoded scorer assumption scan for `--cov=validatorlib`, `benchmarks/runtime_proxy.py`, and `repo / "src"` — passed: no hits.
- Calibration repo mutation scan after `Scorer.score_repo` — passed: clean git status.
- `git diff --check` — passed.
- New-file whitespace check for `tests/test_generic_scorer.py` — passed.

## Fable review

Initial verdict: `ACCEPT_WITH_CHANGES`, with no critical blockers. Required changes:

- Confirm `scorer/goal_config.py` is listed in `.arena/scorer.lock.toml`.
- Fail closed on unreadable ruff/pyright output instead of treating it as zero findings.

Additional guidance was to add multi-source-root fixture coverage.

### Initial review transcript

VERDICT:

```json
{
  "verdict": "ACCEPT_WITH_CHANGES",
  "critical_blockers": [],
  "required_changes_before_completion": [
    "Confirm scorer/goal_config.py is listed in .arena/scorer.lock.toml locked_files. The diff only shows the first two entries; the goal-config loader is now load-bearing safety surface (it decides commands, weights, and boundary paths), and if it is not hash-locked the lock no longer covers the scorer's actual behavior.",
    "Reconsider the new fail-open path in _ruff_violations/_pyright_errors: returncode 0 + unparseable stdout now returns 0 instead of 999, and tests/test_coverage_closure.py was rewritten to bless that. In an arena where a misconfigured or gamed tool command can exit 0 with garbage output, 'unreadable signal = perfect score' is exactly the failure mode this project exists to prevent. Either keep fail-closed (penalize unparseable output regardless of exit code) or record an explicit degraded-signal marker in the ScoreVector so promotion logic can refuse it. If you keep the lenient behavior, document the rationale next to the code, because the old characterization test asserted the opposite."
  ],
  "guidance_as_leon_representative": [
    "The core design is right: fail-closed config load, goal_config_sha in provenance and the score ID, drift_check raising on config-hash change, and the calibration fixture moving to machine-readable tool output are all what BA-M3-02 asked for. The uv.lock/--no-project fix is a good catch and correctly scoped to the fixture.",
    "Card scope says 'at least two fixture repo layouts/signals'. The new test file has one substantive layout (lib/ roots) plus a missing-config repo and a floor-failure variant; the src/ layout is only covered indirectly via calibration tests. Add one fixture with multiple source_roots (e.g. ['lib', 'plugins']) — that is the only path where PYTHONPATH joining and multi-root complexity scanning are exercised, and neither is currently tested with more than one root.",
    "Minor, non-blocking: _cyclomatic_average still does bare ast.parse(path.read_text()); a syntax-error file in a target repo crashes scoring rather than degrading. Pre-existing behavior, but it becomes more likely now that arbitrary repos are scored — fine as a follow-up card.",
    "Note the dependency direction: arena/boundary.py now imports from scorer.goal_config. Acceptable for Phase 1, but it couples the boundary checker to the locked scorer package; if that bothers you later, move GoalConfig to a neutral module."
  ],
  "next_cards_to_claim_or_continue": [
    "Finish the two required changes above on ba/m3-generic-scorer, then close BA-M3-02 — do not start new scope on this branch.",
    "t_c3ad0d70 and t_eeafe5ff can remain ready; scorer completion unblocks rather than resequences them. One caveat: any card that calls scorer internals must be rebased onto the new signatures (_test_and_coverage, goal_config-threaded helpers, is_boundary_violation's goal_config kwarg), since the old helper names are gone. Claim whichever of the two consumes the generic scorer end-to-end first, so the new GoalConfig plumbing gets exercised by a real consumer before more surface is built on top of it."
  ]
}
```

## Fable re-review

Re-review verdict: `ACCEPT`, with no remaining blockers.

### Re-review transcript

VERDICT:

```json
{
  "verdict": "ACCEPT",
  "remaining_blockers": [],
  "verification_of_required_changes": [
    "Required change 1 (lock coverage): satisfied. scorer/goal_config.py appears in .arena/scorer.lock.toml locked_files and scorer_sha was refreshed after the final scorer edit, so the lock now covers the config loader that determines commands, weights, and boundary paths.",
    "Required change 2 (fail-open signal): satisfied. _ruff_violations returns 999 on JSONDecodeError and also on parseable-but-non-list payloads, independent of exit code; _pyright_errors returns 999 on unparseable stdout; the characterization test in test_coverage_closure.py asserts 999 for returncode-0 garbage stdout, restoring the fail-closed contract. The goal.toml commands moving to --exit-zero/--outputjson is the right companion change: exit code no longer carries signal, the parsed payload does, and an unreadable payload is now maximally penalized.",
    "Strong recommendation (multi-root fixture): satisfied. test_scorer_uses_all_configured_source_roots_for_commands_and_complexity exercises ['lib', 'plugins'] for both PYTHONPATH joining and multi-root complexity — the two code paths that were previously untested with more than one root."
  ],
  "notes_on_unrequested_additions": [
    "The artifact-hygiene work (PYTHONDONTWRITEBYTECODE=1, coverage.json/.coverage cleanup, test_scorer_does_not_leave_runtime_artifacts_in_target_repo, --no-project on fixture commands) is in-scope hardening, not scope creep: a scorer that mutates the target repo would break git_oid-based determinism and drift_check, so this directly protects the card's core invariant. The clean-git-status mutation scan is the right verification.",
    "tests_pass now additionally requires coverage_pct >= goal_config.coverage.floor and coverage command success — a behavior tightening beyond the original card text, but consistent with fail-closed scoring and covered by the floor-failure test. Acceptable."
  ],
  "completion_guidance": [
    "Close BA-M3-02 and commit/PR this branch as-is. Full suite, ruff, pyright, determinism, ordering, and boundary tests all pass; both required items are verified in the diff, not just claimed.",
    "Carry forward as a follow-up hardening card (do NOT reopen this one): (a) _cyclomatic_average still does bare ast.parse, so a syntax-error file in a scored repo raises instead of degrading; (b) _pyright_errors with valid-JSON-but-wrong-shape stdout (e.g. a JSON string or list) will hit attribute access on a non-dict and crash rather than return 999 — same class of unreadable-signal, currently un-handled. Both should degrade to the fail-closed value, mirroring the ruff isinstance guard you just added.",
    "Also note for the follow-up card: arena/boundary.py importing scorer.goal_config is fine for Phase 1 but couples the boundary checker to the locked scorer package; move GoalConfig to a neutral module if that coupling starts to bite."
  ],
  "next_cards_to_claim_or_continue": [
    "Finish: commit and close BA-M3-02 on ba/m3-generic-scorer — no new scope on this branch.",
    "Then claim whichever of t_c3ad0d70 / t_eeafe5ff consumes the generic scorer end-to-end first, so GoalConfig plumbing gets a real consumer immediately. Rebase any scorer-internal call sites onto the new signatures: _test_and_coverage replaces _pytest_coverage, all signal helpers take goal_config, _cyclomatic_average takes an iterable of roots, and is_boundary_violation grew a keyword-only goal_config parameter.",
    "File the small hardening card described above (syntax-error degradation + pyright payload-shape guard) so it doesn't get lost."
  ]
}
```

## Non-blocking follow-up requested by Fable

Create a separate hardening card for:

- Degrading syntax-error files in complexity scanning to a fail-closed score instead of crashing.
- Guarding pyright valid-JSON-but-wrong-shape payloads so unreadable signals return `999` instead of raising.

Fable explicitly said not to reopen BA-M3-02 for this follow-up.
