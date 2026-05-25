# Phase 4 — Loop glue, Budget, DivergenceDetector

## Goal

Implement the first autonomous state-machine shell around the verified Phase 1–3 components without adding dashboard control, live subscription-CLI process execution, or rollback/promotion API surfaces.

The Phase 4 objective is to prove that the arena can run a bounded SCAN → HYPOTHESIZE → APPLY → VERIFY → PROMOTE/DISCARD loop against isolated git worktrees, record canonical JSONL events, rebuild a SQLite projection from JSONL, and halt fail-closed on budget or divergence indicators.

## Acceptance criteria

1. `arena.loop.run_loop()` is a plain `async def` using `match state:` over `LoopState`.
2. `BudgetBreach` is raised by budget code and caught only at the loop top, where it becomes a `HaltRecord` plus halt event.
3. Divergence indicators trip deterministically for:
   - repeated boundary violation attempts,
   - fingerprint-cluster failure rate above threshold over distinct fingerprints,
   - scorer/verifier disagreement streaks.
4. JSONL is canonical:
   - every emitted event receives a monotonic per-run `seq`,
   - every line is fsynced,
   - deleting `projection.sqlite` and replaying JSONL fully rebuilds event state.
5. Worktrees are created under the configured arena worktree root from a baseline OID and torn down idempotently.
6. A calibration end-to-end loop applies one positive curated patch inside a git worktree, verifies it using the existing scorer/verifier, ff-merges it, advances the baseline, and records at least one promotion.
7. No dashboard, rollback endpoints, live Claude/Codex/Gemini/Copilot subprocesses, or public/network service is introduced in this phase.

## Files to add/change

- `arena/budget.py` — budget counters and fail-closed `BudgetBreach`.
- `arena/events.py` — append-only JSONL event log and SQLite projection replay.
- `arena/divergence.py` — rolling divergence indicator checks over event history.
- `arena/worktrees.py` — git worktree lifecycle plus ff-only promoter.
- `arena/loop.py` — state-machine glue and halt handling.
- `arena/protocols.py` — minor protocol alignment if loop integration needs it.
- `README.md` / `AGENTS.md` — status update after verification.
- Tests under `tests/` for Phase 4 behavior.

## TDD slices

1. Budget tests first:
   - wall/cycle cap raises `BudgetBreach`,
   - zero-promotion budget exhaustion reports `BUDGET_EXHAUSTED_ZERO_PROMOTIONS`,
   - promoted runs report `WALL_CLOCK_BREACH` for later caps.
2. Event/projection tests:
   - JSONL `seq` increments,
   - projection rebuild after deleting sqlite reproduces max seq and event count.
3. Divergence tests:
   - boundary attempts trip after threshold,
   - failure cluster rate trips only after minimum distinct fingerprints,
   - scorer/verifier disagreement streak trips after threshold.
4. Worktree tests:
   - create a branch worktree at a baseline OID,
   - modify/commit/ff-promote,
   - teardown leaves no worktree directory.
5. Loop tests:
   - fake components prove SCAN→...→PROMOTE event order,
   - budget breach becomes halt record,
   - calibration positive patch promotes at least once.

## Risks and deferred work

- Candidate score records currently score dirty worktrees before promotion commit; Phase 4 records the live worktree score but does not redesign the schema. A later integration phase can add candidate tree hashes or pre-verify candidate commits.
- Structural AST validation remains a later integration hook; Phase 4 accepts an injectable validator and defaults to pass-through for the deterministic calibration harness.
- SQLite projection intentionally starts as an event projection only. Rich tables for Run/Cycle/Verdict/Baseline can be added once dashboard Phase 5 needs them.
- Live subscription CLI subprocess orchestration remains deferred; the loop consumes the Phase 3 runner/router contract.

## Verification

- Targeted pytest for Phase 4 tests during implementation.
- Full `make verify` before review and commit.
- `git diff --check` and staged secret/static scan before commit.
- Opus read-only review focused on budget/divergence/JSONL/worktree/loop invariants before final commit.
