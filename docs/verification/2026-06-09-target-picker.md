# Build Arena BA-M3-03 Target Picker Evidence

Date: 2026-06-10T05:15:52Z
Kanban card: `t_c3ad0d70` — BA-M3-03 Phase 2: Add deterministic target picker
Branch: `ba/m3-target-picker`

## Scope completed

- Added `arena/target_picker.py`.
- Added `tests/test_target_picker.py`.
- Implemented `select_targets(repo, max_candidates=5, lint_path=None, coverage_path=None, goal_config=None)`.
- Candidate files come from `GoalConfig.paths.source_roots`.
- Goal-config `read_only` / `out_of_scope` paths and default Build Arena boundary paths are excluded through `is_boundary_violation(..., goal_config=config)`.
- Raw candidate signals include:
  - coverage gap from configured coverage JSON when present;
  - lint violations and lint density from optional ruff JSON when present;
  - static AST complexity;
  - git churn count;
  - TODO/FIXME count;
  - line count.
- Ranking is deterministic by score descending, then path ascending.
- `TargetSelection` evidence includes version, deterministic ID, git OID, goal-config hash/schema, candidate counts, omitted count, ranked candidates, and raw signal values.
- Selection IDs are content hashes over deterministic inputs; no wall-clock timestamp is embedded.

## TDD evidence

- `tests/test_target_picker.py` was written before production code.
- RED run: `uv run pytest tests/test_target_picker.py -q` failed during collection with `ModuleNotFoundError: No module named 'arena.target_picker'`.
- Production implementation was added only after RED.
- GREEN run: `uv run pytest tests/test_target_picker.py -q` passed: `5 passed`.

## Verification completed

- `uv run pytest tests/test_target_picker.py tests/test_boundary.py tests/test_goal_config.py tests/test_generic_scorer.py -q` — passed.
- `uv run pytest tests -q` — passed.
- `uv run ruff check .` — passed.
- `uv run pyright` — passed: `0 errors, 0 warnings`.
- Static provider scan of `arena/target_picker.py` for provider/model-call imports/strings — passed: no hits.
- `git diff --check` — passed.
- New-file whitespace checks for `arena/target_picker.py` and `tests/test_target_picker.py` — passed.

## Fable review

Verdict: `ACCEPT` with no code blockers. Fable required committing the two new files before card closure.

### Review transcript

VERDICT:

```json
{
  "verdict": "ACCEPT",
  "critical_blockers": [],
  "required_changes_before_completion": [
    "Commit arena/target_picker.py and tests/test_target_picker.py — both are still untracked (?? in git status). The card is not closeable on an uncommitted working tree.",
    "Use a conventional commit consistent with the branch history, e.g. 'feat: add deterministic target picker'."
  ],
  "advisory_non_blocking": [
    "_candidate_for calls path.read_text(encoding='utf-8') unguarded; a non-UTF-8 source file will crash the whole selection. Consider errors='replace' or skip-with-zero-signals in a follow-up — real repos will hit this.",
    "_todo_count uses substring matching, so words containing 'todo' (e.g. 'mastodon') inflate the signal. Word-boundary regex would be cleaner; raw values are logged so it's auditable, not wrong.",
    "_ComplexityVisitor does not handle ast.TryStar (except*), undercounting on 3.11+ syntax. Harmless for now.",
    "git churn shells out once per candidate file; fine at this scale, but worth a single 'git log --name-only' pass if candidate sets grow.",
    "The 'scorer/engine.py not in paths' assertion is vacuously true on the fixture (no scorer/ dir exists there); it documents intent but tests nothing. Optional tightening.",
    "Score weights (4/100/2/3/5) are unexplained magic numbers; acceptable for v1 since SELECTION_VERSION gates the contract, but consider naming them as module constants when tuning starts."
  ],
  "guidance_as_leon_representative": "This meets the card contract: deterministic signals only, goal-config-driven exclusions via the shared boundary check, stable path tiebreak ordering, no wall-clock in the evidence ID, raw signal values preserved in the record, and graceful zero-signal degradation for missing coverage/lint inputs. TDD evidence (RED on ModuleNotFoundError, then GREEN) and the full verification battery (suite, ruff, pyright, provider scan) are exactly the bar we want for M3. Versioning the record as target-selection/v1 and hashing over git oid + goal-config sha is the right evidence design — downstream consumers can detect drift. Ship it after committing; fold the UTF-8 robustness note into the next card that touches this module rather than reopening this one.",
  "next_cards_to_claim_or_continue": "Claim t_eeafe5ff next if it is the Phase 3 card that consumes TargetSelection (worktree cycle / executor) — it sits directly on this output and on the boundary/goal-config work already merged, so it's the critical path. t_5d7abe71 and t_d1682f0d should follow only if they don't depend on Phase 3 output; if they are independent (e.g. evidence-log plumbing or scorer-side), they're safe parallel work, but don't start them before t_eeafe5ff if they consume the worktree-cycle contract. I can't read the card bodies in this review pass, so verify the dependency direction on the board before claiming."
}
```

One process note: the verification story is strong, but the close-out step (commit on `ba/m3-target-picker`) is the only thing standing between this and done — the verdict is ACCEPT conditioned on that commit landing, not on any code change.

## Non-blocking follow-ups noted by Fable

- Consider robust handling for non-UTF-8 source files.
- Consider word-boundary TODO/FIXME counting.
- Consider `ast.TryStar` complexity counting.
- Consider batching git churn if candidate sets grow.
- Consider naming/tuning target-picker score weights as constants in a future scoring-tuning slice.

These were explicitly non-blocking for BA-M3-03.
