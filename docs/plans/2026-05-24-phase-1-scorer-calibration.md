# Phase 1 Scorer + Calibration Implementation Plan

> **For Hermes:** Use strict TDD and Opus read-only reviews. Do not ask Leon unless Opus plus local debugging cannot unblock the work.

**Goal:** Build the Phase 1 foundation for Autonomous Build Arena: deterministic scorer, scorer lock, boundary rejection, and 13-diff calibration suite.

**Architecture:** A standalone Python project under `/home/leonb/projects/build-arena`. LinkML owns schema artifacts. The top-level `scorer/` package is intentionally treated as read-only to future arena-generated hypotheses and is pinned by `.arena/scorer.lock.toml`. Calibration uses a synthetic Python repository plus patch catalog under `.arena/calibration/`.

**Tech Stack:** Python 3.12, uv, pytest, pytest-cov, ruff, pyright, LinkML, git fixtures.

---

## Acceptance criteria

1. `make generated` regenerates Python, JSON Schema, TypeScript, and SQL artifacts from `schema/arena.yaml`.
2. `.arena/scorer.lock.toml` exists and `scorer.lock.load_scorer_lock(..., validate=True)` refuses mismatches.
3. Re-scoring an unchanged git OID returns identical scores within `1e-6`.
4. Calibration catalog has exactly 13 patches: 5 positive, 5 negative, 3 neutral.
5. Positives score above baseline, negatives score below baseline or trip pinned regressions, neutrals remain within epsilon.
6. `arena.boundary.is_boundary_violation()` rejects `scorer/`, `verifier/`, and `schema/` targets before runner spawn.
7. `uv run ruff check .`, `uv run pyright`, and `uv run pytest tests -q` pass.
8. Opus read-only review finds no Phase 1 blocker, or any blocker is fixed and re-reviewed.

## Task slices

### Task 1: Create standalone project scaffold

Files: `pyproject.toml`, `.gitignore`, `README.md`, `AGENTS.md`, `Makefile`, package directories.

Verification: `git status --short` shows only expected new source files.

### Task 2: Write failing boundary and scorer-lock tests

Files: `tests/test_boundary.py`, `tests/test_scorer_lock.py`.

Expected RED: imports fail or lock file missing before implementation.

### Task 3: Implement boundary and lock helpers

Files: `arena/boundary.py`, `scorer/lock.py`, `scorer/exceptions.py`, `.arena/scorer.lock.toml`.

Verification: targeted tests pass.

### Task 4: Write failing calibration scorer tests

Files: `tests/test_scorer_determinism.py`, `tests/test_calibration_ordering.py`.

Expected RED: scorer/calibration files missing before implementation.

### Task 5: Build calibration repo and scorer

Files: `scripts/rebuild_calibration.py`, `.arena/calibration/**`, `scorer/engine.py`.

Verification: 13 ordering assertions pass.

### Task 6: Add schema and generated artifacts

Files: `schema/arena.yaml`, `arena/generated/*`, `dashboard/src/lib/generated/arena.d.ts`.

Verification: `make generated` and schema import test pass.

### Task 7: Full local verification and Opus review

Commands:

- `make generated`
- `uv run ruff check .`
- `uv run pyright`
- `uv run pytest tests -q`
- Claude Code Opus read-only review against spec and git diff.

### Task 8: Fix review blockers and commit local state

Use local debugging first. If genuinely blocked, ask Opus for targeted advice. Ask Leon only if no local/Opus path exists.
