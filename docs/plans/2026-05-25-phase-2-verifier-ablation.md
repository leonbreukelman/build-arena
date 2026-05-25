# Phase 2 Verifier + Ablation Implementation Plan

> **For Hermes:** Use test-driven-development and requesting-code-review. Keep Phase 2 scoped to verifier behavior; do not start runners, dashboard, or loop glue.

**Goal:** Add a deterministic Phase 2 verifier that evaluates score/test/pinned-regression gates plus Lanham-style ablation quorum, then calibrates false positives and false negatives on the Phase 1 curated diff catalog.

**Architecture:** The verifier consumes Phase 1 `scorer.engine.ScoreRecord` values for baseline and candidate worktrees. It returns LinkML-generated `Verdict` and `AblationResult` models. Ablation is behind an `AblationRunner` protocol; the default configured runner name is `ollama`, with a deterministic local runner used for testable no-API Phase 2 semantics until the real runner adapter phase.

**Tech Stack:** Python 3.12, pytest, generated LinkML Pydantic models, existing deterministic scorer.

---

## Task 1: Add failing verifier-gate tests

**Objective:** Specify that verifier evaluates all four gates and chooses granular reject reasons.

**Files:**
- Create: `tests/test_verifier_gates.py`
- Later create: `verifier/engine.py`, `verifier/ablation.py`, `verifier/config.py`

**Test behaviors:**
- A positive candidate with tests passing, positive score delta, no pinned regression, and ablation quorum promotes.
- A candidate with failed tests rejects with `TEST_FAILURE`.
- A nonpositive score delta rejects with `SCORE_DELTA_NONPOSITIVE`.
- A pinned metric regression rejects with `PINNED_METRIC_REGRESSION`.
- A candidate with ablation quorum failure rejects with `ABLATION_REASONING_NOT_LOAD_BEARING`.
- Ablation probes run independently even if an earlier gate would reject.

**RED command:** `uv run pytest tests/test_verifier_gates.py -q`

## Task 2: Add failing ablation/config tests

**Objective:** Specify default `ollama` runner naming, 3-of-4 Lanham probe validation, default quorum 2-of-3, and no cached probe reuse.

**Files:**
- Create: `tests/test_ablation.py`
- Modify later: `verifier/ablation.py`, `verifier/config.py`, `.arena/config.toml`

**Test behaviors:**
- Default config uses `RunnerName.ollama`, probe set `EARLY_ANSWERING`, `FILLER_TOKENS`, `PARAPHRASING`, quorum 2.
- Config rejects probe sets whose length is not exactly 3.
- Config rejects quorum outside `1..len(probe_set)`.
- Repeated `Verifier.verify(...)` calls rerun every active probe; call count doubles.

**RED command:** `uv run pytest tests/test_ablation.py -q`

## Task 3: Add failing calibration FP/FN tests

**Objective:** Prove Phase 2 calibration separately measures false positives and false negatives against the 13 curated diffs.

**Files:**
- Create: `tests/test_verifier_calibration.py`
- Later create: `verifier/calibration.py`

**Test behaviors:**
- Negative + neutral diffs have FP count 0.
- Positive diffs have FN count = 0 on the 5-positive catalog, satisfying `fn_target = 0.10`.
- Coverage pinned regression means the candidate falls below the configured coverage floor. A small coverage decrease that remains above the floor is allowed and still represented in the composite score.
- The report exposes `false_positive_rate`, `false_negative_rate`, `meets_targets`, promoted/discarded IDs, and per-case reject reasons.

**RED command:** `uv run pytest tests/test_verifier_calibration.py -q`

## Task 4: Implement minimal verifier and ablation code

**Objective:** Make tests pass without introducing runners/dashboard/loop glue.

**Files:**
- Create: `verifier/__init__.py`
- Create: `verifier/config.py`
- Create: `verifier/ablation.py`
- Create: `verifier/engine.py`
- Create: `verifier/calibration.py`
- Create: `.arena/config.toml`

**Implementation notes:**
- Use generated enums/models: `RejectReason`, `VerdictOutcome`, `AblationProbe`, `RunnerName`, `Verdict`, `AblationResult`.
- Build ids deterministically from hypothesis id + score ids + probe outputs where possible.
- `Verifier.verify` must call ablation runner for all configured probes every call; no memoization.
- `Verifier.verify_worktree` must rescore the live worktree on every call; no cached candidate score records.
- Reject reason precedence after all gates are evaluated: tests failure, pinned regression, nonpositive delta, ablation not load-bearing.
- `CalibrationCase` should include patch path and class label (`positive`, `negative`, `neutral`).
- Phase 2 uses a deterministic local runner with `RunnerName.ollama` identity as a no-API stand-in; the real Ollama adapter remains a later runner-integration task.

## Task 5: Verification, Opus review, commit

**Objective:** Ship a reviewed, committed Phase 2 slice.

**Commands:**
- `make verify`
- staged path/static scans from requesting-code-review
- Opus read-only review focused on Phase 2 done-when
- fix blockers and rerun `make verify`
- commit with `[verified]` prefix
