# Opus Review — Project Decomposer Implementation

Reviewer: Claude Opus 4.8 via Claude Code
Mode: read-only implementation review
Artifacts:
- `/tmp/build-arena-decomposer-implementation-opus-review.json`
- `/tmp/build-arena-decomposer-focused-opus-review.json`

## Initial implementation review

Verdict: PASS_WITH_NONBLOCKING_SUGGESTIONS
Reported cost: $0.79686425

Blocking findings: none.

Confirmed plan-review blockers were resolved:
- split ownership coverage and explicit unclassified bucket/gap;
- validation of fabricated checks, contract endpoints, rollback stop conditions, and referenced paths;
- manifest-derived F3 patch-generalization gap rather than hardcoded fixture success.

Non-blocking findings from Opus:
- `git.dirty` over-reported on untracked-only trees;
- excluded records were hashed in filesystem fallback;
- coverage could be misread as quality rather than ownership accounting;
- `project_root` is machine-specific in canonical JSON;
- coverage validation only compared selected fields;
- porcelain dirty-path parsing remains informational and may be fragile for quoted paths.

## Hermes fixes after initial review

Applied and locally verified:
- added failing tests for untracked-only dirty semantics, deleted tracked files, excluded hashes, fresh repo without commits, multiple owners/stale coverage, and missing cross-cutting component references;
- changed `_git_dirty_paths()` to skip `??` untracked entries while preserving `untracked_paths` separately;
- changed excluded `FileRecord.sha256` to `None` so excluded artifacts are not hashed;
- changed validation to recompute and compare the complete `CoverageReport`;
- documented coverage as ownership accounting, not quality scoring.

## Focused re-review

Verdict: PASS
Reported cost: $0.45829875

Blocking findings: none.

Opus confirmed each Hermes fix and the current local verification:
- `uv run pytest tests -q` passed;
- `uv run ruff check .` passed;
- `uv run pyright` passed;
- `uv run python -m arena.decomposer --project /home/leonb/projects/arena-calibration --output /tmp/arena-calibration-project-model.json` passed, with 83 included files, no unowned files, 9 components, 4 contracts, and F3-only `patch_generalization_axis_missing` evidence.

Remaining non-blocking suggestions:
- document or revisit the CLI behavior that writes output before failing an invalid model;
- clarify that generated dir exclusion is top-level only;
- consider a CLI debug traceback option for unfamiliar scan failures;
- consider enforcing semantics for `MechanicalCheck.no_live_api` if downstream consumers rely on it.
