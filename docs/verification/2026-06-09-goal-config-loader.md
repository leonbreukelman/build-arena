# Build Arena BA-M3-01 Goal Config Loader Evidence

Date: 2026-06-10T04:36:51Z
Kanban card: `t_d099446a` — BA-M3-01 Phase 1: Add per-repo `goal.toml` schema and loader
Branch: `ba/m3-goal-config-loader`

## Scope completed

- Added `scorer/goal_config.py` as the per-target-repo goal configuration loader.
- Added `tests/test_goal_config.py` covering normalization, fail-closed command validation, deterministic defaults, path safety, bool numeric rejection, content hashing, missing config files, and real Build Arena/calibration fixture configs.
- Added `.arena/goal.toml` for Build Arena.
- Added `.arena/calibration/repo/.arena/goal.toml` for the calibration fixture.
- Updated `.arena/scorer.lock.toml` after adding the locked scorer module.

## TDD evidence

- Initial goal-config tests failed with `ModuleNotFoundError: No module named 'scorer.goal_config'` before `scorer/goal_config.py` existed.
- Repo fixture config tests failed because `.arena/goal.toml` files were missing, then passed after adding the configs.
- Scorer-lock tests failed after adding `scorer/goal_config.py`; `uv run python scripts/update_scorer_lock.py` refreshed the controller-owned scorer lock.
- Fable-requested tests for `src/..`, `.`, `coverage.floor = true`, and `diff_caps.max_files = true` failed before the validation fix, then passed after the loader rejected those inputs.

## Verification completed

- `uv run pytest tests/test_goal_config.py::test_load_goal_config_rejects_unsafe_paths tests/test_goal_config.py::test_load_goal_config_rejects_bool_numeric_fields -q` — passed: `5 passed`.
- `uv run pytest tests/test_goal_config.py tests/test_scorer_lock.py tests/test_scorer_determinism.py tests/test_calibration_ordering.py -q` — passed: `36 passed`.
- `uv run pytest tests -q` — passed.
- `uv run ruff check .` — passed.
- `uv run pyright` — passed: `0 errors, 0 warnings`.
- `git diff --check` — passed.
- Untracked whitespace checks for the new goal-config files, loader, and tests — passed.

## Fable review

Initial Fable verdict: `ACCEPT_WITH_CHANGES`, with no critical blockers. Required changes:

- Reject trailing/inner `..` and bare `.` path segments.
- Reject TOML booleans in numeric fields.

Both changes were implemented test-first.

### Initial review transcript

VERDICT:

```json
{
  "verdict": "ACCEPT_WITH_CHANGES",
  "critical_blockers": [],
  "required_changes_before_completion": [
    "Strengthen _normalize_relative_path: a trailing '..' segment slips through current checks ('src/..' normalizes to repo root, and '.' is accepted as-is). Reject any path whose PurePosixPath parts contain '..' or equal '.'. It cannot escape the repo today, but this is the path-safety primitive in a locked scorer file — fix it now while the lock is fresh rather than paying another controller-owned lock update later.",
    "Exclude bool from numeric validation: isinstance(value, int | float) accepts TOML 'true' for weights/coverage.floor (bool is an int subclass). Add an explicit isinstance(value, bool) rejection in _optional_float and _positive_int, with one RED test."
  ],
  "guidance_as_leon_representative": "Contract shape, fail-closed required-command validation, deterministic defaults documented in tests, and raw-bytes sha256 for provenance all meet the card gates — good work, and the TDD trail including the intentional scorer-lock RED is exactly the discipline we want. On the four risks: (1) read_only in .arena/goal.toml duplicating AGENTS.md protections is correct defense-in-depth, but treat the verifier as the enforcement authority and goal.toml as declarative input — never let a future card argue goal.toml absence means those paths are writable. (2) engine.py not consuming GoalConfig is correct sequencing; do not partially wire it here. (3) Keep the uv --with wrapper commands in the calibration fixture, but record explicitly on t_6ea789cf that calibration ordering must be re-proven with these commands actually executed, since they deviate from the hardcoded scorer commands and the loader only records them today — that equivalence is currently unverified. (4) Two small validation gaps above; also note unknown keys/tables are silently ignored (a typo'd '[coverge]' falls back to defaults), which is acceptable for goal-config/v1 but should be revisited as strict-unknown-key rejection in a schema bump, not patched ad hoc. One provenance caution: config_path is an absolute resolved path — use only content_hash and schema_version in scorer provenance, never the machine-specific path.",
  "next_cards_to_unblock_if_accepted": [
    "t_6ea789cf",
    "t_c3ad0d70 and t_eeafe5ff only if they consume the GoalConfig dataclass contract read-only and do not depend on engine wiring; otherwise sequence them after t_6ea789cf"
  ]
}
```

## Fable re-review

Fable re-review verdict: `ACCEPT`, with no remaining blockers.

### Re-review transcript

VERDICT:

```json
{
  "verdict": "ACCEPT",
  "remaining_blockers": [],
  "completion_guidance": "Both required changes are correctly implemented and verified. (1) Path safety: _normalize_relative_path now splits the normalized string and rejects any segment in {'', '.', '..'}, which catches the previously-escaping cases — 'src/..' (trailing '..' segment), the bare root '.', leading '../', and as a bonus absolute paths (leading '/' yields an empty first segment) and double slashes ('a//b' yields an empty segment). The check operates on the raw segments rather than PurePosixPath.parts, which is the stronger choice since PurePosixPath drops '.' segments during parsing. (2) Bool rejection: both _optional_float and _positive_int now check isinstance(value, bool) before the numeric isinstance, closing the bool-is-int subclass hole, with RED-first tests for coverage.floor=true and diff_caps.max_files=true. The scorer.lock.toml update is consistent: goal_config.py added to locked_files and scorer_sha regenerated, with test_scorer_lock passing. Test evidence is adequate — 5 targeted tests passed, full suite green, ruff and pyright clean. Non-blocking notes carried forward from the original review, no action needed on this card: unknown-key leniency stays deferred to a goal-config/v2 schema bump; use only content_hash and schema_version (never config_path) in scorer provenance; the backslash-to-slash conversion in _normalize_relative_path silently accepts Windows-style separators, which is acceptable normalization but worth a comment if it ever surprises anyone.",
  "next_cards_to_unblock": [
    "t_6ea789cf (calibration ordering must be re-proven with the goal.toml uv --with wrapper commands actually executed, per the note recorded on that card)",
    "t_c3ad0d70 and t_eeafe5ff — unblocked now if they consume the GoalConfig dataclass contract read-only; sequence after t_6ea789cf if they depend on engine wiring"
  ]
}
```

## Carry-forward notes for BA-M3-02

- Re-prove calibration ordering with the `goal.toml` commands actually executed once the scorer consumes `GoalConfig`.
- Use `content_hash` and `schema_version` in scorer provenance; do not persist machine-specific absolute `config_path` values as provenance.
- Treat unknown-key rejection as a possible future `goal-config/v2` schema tightening, not as a BA-M3-01 blocker.
