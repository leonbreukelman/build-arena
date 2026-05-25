# Phase 3 Hypothesizer + Fingerprinting + RunnerRouter Implementation Plan

> **For Hermes:** Use test-driven-development and requesting-code-review. Implement only Phase 3; do not start dashboard, loop glue, promoter/rollbacker, or real external CLI process execution beyond parser/router contracts.

**Goal:** Add the hypothesis-selection, reproducible fingerprinting, failure-ledger collision checks, runner fallback, and ViewBeforeEdit parser invariants required before the autonomous loop can call real adapters.

**Architecture:** Keep Phase 3 deterministic and no-API by implementing pure components plus injectable subprocess/event streams. The default adapters expose the final command/parser semantics but tests use in-memory streams so verification never spends subscription credits. Failure ledger remains append-only JSONL and runner fallback preserves the exact Hypothesis identity.

**Tech Stack:** Python 3.12, stdlib hashing/json/math/dataclasses, generated LinkML enums/models where useful, pytest, ruff, pyright.

---

## Acceptance criteria

1. Bandit/Hypothesizer
   - Arms are `(technique_tag, target_cluster)` pairs.
   - Cold start pulls one of each configured arm before UCB1 scoring.
   - UCB1 uses alpha = 1.25 by default after cold start.
   - Empty project models or unaddressable arms fail closed without filesystem writes.

2. Fingerprints
   - Fingerprint id is `blake2b(sha256(quantized_intent_embedding) || sorted_target_files_hash || technique_tag || ast_diff_pattern_hash)[:16]`, represented as 32 lowercase hex characters.
   - Phase 3 uses a deterministic no-API SHA-256 expansion seeded by the pinned embedding model name as the quantized-intent stand-in; live embedding execution is deferred.
   - Embedding model is part of the Fingerprint metadata and is pinned in config.
   - Fingerprints are reproducible across processes and insensitive to target-file order.
   - Target path hash and AST diff pattern hash are SHA-256 hex strings.

3. Failure ledger
   - Ledger is append-only JSONL.
   - Recorded failed fingerprints reject later hypotheses before runner spawn.
   - Successful fingerprints do not block retry by themselves.

4. RunnerRouter
   - Primary runner defaults to `claude_code`, fallback to `ollama`.
   - A fault-injection event containing the verbatim string `You've hit your weekly limit` raises `CreditExhausted` for Claude.
   - Router emits a `RUNNER_FALLBACK` event and retries the same Hypothesis object/id/fingerprint with Ollama.
   - Two consecutive credit exhaustions in one cycle return an ERROR-style result without swallowing identity.

5. ViewBeforeEdit
   - Claude stream parser records reads per turn.
   - Any Edit/Write without a fresh same-turn Read raises `ViewBeforeEditViolation` before patch materialization.
   - Read set resets on a new assistant turn.

## Files

Create:
- `arena/fingerprints.py`
- `arena/ledger.py`
- `arena/hypothesizer.py`
- `arena/runners/__init__.py`
- `arena/runners/base.py`
- `arena/runners/claude_code.py`
- `arena/runners/ollama.py`
- `arena/router.py`
- `tests/test_fingerprints.py`
- `tests/test_failure_ledger.py`
- `tests/test_hypothesizer_bandit.py`
- `tests/test_runner_router.py`
- `tests/test_view_before_edit.py`

Modify:
- `pyproject.toml` pyright include list if needed.
- `README.md` and `AGENTS.md` status once Phase 3 is verified.
- `.arena/config.toml` runner/fingerprint defaults.

## TDD sequence

### Task 1: Fingerprint tests and implementation

RED:
- Same intent/targets/technique/diff produces same 32-hex id across calls.
- Target-file order does not change fingerprint.
- Changing technique or AST diff changes fingerprint.

GREEN:
- Implement deterministic lexical hashing and quantized intent embedding with stdlib SHA-256 chunks, no model download.

### Task 2: Failure ledger tests and implementation

RED:
- Append failure record, reopen ledger, collision check returns true.
- Append success only, collision check returns false.

GREEN:
- Implement JSONL append/read, fail closed on malformed rows by ignoring only that row with no mutation.

### Task 3: Bandit/hypothesizer tests and implementation

RED:
- First three selections follow configured cold-start arm order.
- After rewards, UCB1 picks the higher-scoring arm.
- Empty arms raise a typed error.

GREEN:
- Implement `Arm`, `ArmStats`, `UCB1Bandit`, and `SymbolicHypothesizer` that creates symbolic hypotheses without touching the filesystem.

### Task 4: ViewBeforeEdit tests and implementation

RED:
- Read then Edit same path passes.
- Edit without Read raises.
- Read in prior turn does not authorize Edit in next turn.

GREEN:
- Implement Claude stream parser with turn-scoped read set.

### Task 5: RunnerRouter tests and implementation

RED:
- Claude event containing `You've hit your weekly limit` triggers fallback to Ollama.
- Fallback receives the same Hypothesis identity and fingerprint.
- Fallback also exhausted returns a `RUNNER_ERROR` style result and records two attempts.

GREEN:
- Implement base exceptions/result types, test doubles, Claude parser credit regex, Ollama stub runner, router fallback logic.

### Task 6: Verification and review

Run:
- `make verify`
- `git diff --check -- ':!*.patch'`
- staged path/secret scan from requesting-code-review
- Opus read-only review focused on Phase 3 done-when

Commit only after Opus ACCEPT and clean verification.
