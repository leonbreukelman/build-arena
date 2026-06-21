# Proposal Run and Emit Design

Date: 2026-06-21

## Goal

Add the final two stages of the proposal pipeline so a single command turns a target repository into one ticket-ready `proposal.md`:

1. `arena.proposal_emit` — render the rank-1 candidate of a reranked `proposal-plan/v0` to ticket-ready markdown.
2. `arena.proposal_run` — orchestrate decompose → intake → propose → pairwise re-rank → emit as one sequential, fail-closed command.

Emit closes the open `proposal_emit` reference in the pairwise re-ranker design (`docs/specs/2026-06-19-pairwise-proposal-reranker-design.md`). The orchestrator is the operator entry point that chains the five existing stage CLIs; it does not add a new pipeline, gate, or autonomy surface.

## Scope lock

Build only this:

1. `proposal_emit`: load + schema-validate a reranked `proposal-plan/v0`, select the single `rank == 1` candidate, render it to markdown, write the file. Pure and deterministic.
2. `proposal_run`: a thin sequential driver that runs each stage as an isolated subprocess through its existing CLI, checks the artifact + exit after each, and emits one `proposal.md`.
3. Tests for both, run entirely offline (injected stage runner + injected git runner; fake re-rank writes a real schema-valid plan; fake emit calls the real `emit_proposal`).
4. An additive README section and this design record.

Do not build:

- any change to the logic of the five frozen stage CLIs (decompose, intake, propose, re-rank, emit-internals beyond this new renderer);
- panels, UI, dashboards, Docker, or CI;
- the apply/promote path, `repo_goal_loop`, or `proposal_ranker` invocation;
- a build backend / console-script entry without operator sign-off (see D2);
- any new auth surface, model routing, or token-in-config.

## Emit contract

- Input: a reranked `proposal-plan/v0` document. `load_reranked_plan` reads it, requires `schemaVersion == proposal-plan/v0`, and validates against `docs/schemas/proposal-plan-v0.schema.json` with `Draft202012Validator` (the same idiom the re-ranker's own tests use). Any read/parse/schema/version failure raises `EmitError` and writes nothing (fail closed).
- Selection: exactly one `rank == 1` candidate. Zero or multiple rank-1 candidates is an `EmitError`.
- Rendered (human-meaningful): title; intent (Proposed change); `source_recommended_action` (Why); target files (`target_paths` ∪ `target_path`, de-duplicated); `success_criterion` (Definition of done); `verification_commands` verbatim inside a ` ```sh ` fence; `grounding_constraints`; `evidence_refs` as readable lines (`path (kind)` plus provenance `ref`/`componentId`), never a raw JSON dump; and a provenance footer of `finding_id` · plan `id` · `snapshotId`.
- Never rendered (read but withheld): `priority_score`, `repo_facts_block`, `repo_facts_hash`, `intent_hash`, `proposal_key`, `registry_status`, `base_lineage`. Showing the discarded `priority_score` in particular would mislead a reader into thinking the absolute score, not the pairwise tournament, picked the winner. Leak-freedom is asserted in tests with distinctive per-field sentinels.
- Determinism: identical input renders byte-identical output. No timestamps, host paths, randomness, model, or network.

## Orchestrator contract

- Stages run as subprocesses (`python -m <module>`) with `cwd` = repo root and the repo root prepended to `PYTHONPATH`; all path arguments are passed absolute. The stage runner is an injectable seam (`StageRunner`) so tests never spawn a process or make a live call.
- Project Model v1 is resolved from the snapshot **manifest**, not by globbing for the model file: glob the single `snap/*/manifest.json` in the fresh workdir, then read `project_model_primary_path` (fallback `project_model_v1_path`) relative to the manifest directory. That resolved v1 path is what intake (`--snapshot`) and re-rank (`--graph`) receive.
- Fail closed after every stage: a non-zero exit, or a missing expected artifact, stops the run, writes no `proposal.md`, and preserves the workdir. Decompose returning non-zero (including a failed snapshot gate) is treated as a stage failure.
- The re-ranker's judge is an unavoidable live model call. Provider selection is threaded to it via the `BUILD_ARENA_LLM_*` contract — `--live-model` → `BUILD_ARENA_LLM_MODEL`, `--live-api-key-env` → `BUILD_ARENA_LLM_API_KEY_ENV`, `--live-base-url` → `BUILD_ARENA_LLM_BASE_URL` — because `DefaultLLMProposalJudge.create()` resolves model/base-url/key-env from the environment and otherwise silently falls back to a preset model. The judge is xAI-only; `--live-provider`/`--live-base-url` therefore affect live decomposition, while the judge stays on xAI. The key **value** is never injected or written — only the env-var name is passed; the stages resolve the value from the environment or `~/.hermes/.env`.
- No-proposal vs failure: the re-ranker writes its trace first and only then raises when no candidate survives the pre-filter, so a non-zero exit **with** a trace whose `preFilter.survivorCount == 0` is the no-proposal outcome — print a one-line explanation pointing at the trace, write no `proposal.md`, exit `2`. Any other non-zero (trace missing, or `survivorCount != 0`) is a genuine stage failure, exit `1`.
- Exit codes: `0` success, `1` stage failure, `2` no proposal met the bar, `3` usage/preflight error.

## Design decisions

- **D1 — decompose default.** Fixture (deterministic, offline) by default; `--decompose-live` opts into the live AI decomposer. Keeps the common run free and reproducible up to the re-rank boundary.
- **D2 — packaging (deferred to operator).** The repo has no `[build-system]` and multiple top-level packages (`arena`, `scorer`, `verifier`, `scripts`), so uv runs it as a virtual (deps-only) project. `[project.scripts]` alone yields no working `proposal` binary, and adding a build backend risks the existing `import scorer` / `import verifier`. This change ships the always-available module path (`uv run python -m arena.proposal_run run <repo>`) and leaves the console-script/packaging as an explicit operator decision rather than silently introducing a risky backend.
- **D3 — workdir lifecycle.** Default workdir is a `mkdtemp`, deleted on success and preserved on failure (and on no-proposal, so the trace is inspectable). `--keep-workdir` retains a temp workdir on success; an explicit `--workdir` is never auto-deleted.
- **D5 — provenance footer.** Emit includes a footer with `finding_id`, plan `id`, and `snapshotId` so a rendered proposal is traceable back to its run without exposing internal scoring/registry fields.
- **Preflight.** `--live-model` is required (the judge always spends), and the key named by `--live-api-key-env` must resolve, or the run fails closed with exit `3` before doing any work — consistent with the rest of the repo refusing live attempts without an explicit model.

## Verification

- `tests/test_proposal_emit.py` (rank-1 selection regardless of order, all sections present, leak-freedom via sentinels, byte-identical repeat, verbatim verification fence, readable evidence refs, target de-duplication, and the fail-closed paths) and `tests/test_proposal_run.py` (stage order, manifest-driven v1 resolution, fail-closed-on-stage-failure with workdir preserved and later stages skipped, no-proposal UX, re-rank-crash-with-survivors vs trace-missing both as stage failures, target resolution local/URL/reject, preflight missing-model and missing-key, workdir lifecycle, env threading, and `main` exit mapping) — all offline.
- Whole-repo `uv run pytest tests -q`, `uv run ruff check .`, and `uv run pyright` are green, with the pre-existing frozen suite unchanged.

## Known boundaries and open items

- A full `proposal run` is not byte-reproducible: the judge is a live model call, so the selected winner and the no-proposal outcome can vary across runs. The deterministic boundary is the reranked plan; pin or record it (e.g. via `--workdir`) when a reproducible `proposal.md` is required.
- The live end-to-end run (real judge spend) is the remaining acceptance step and is operator-gated; it is not exercised by the offline test suite.
- D2 (console script / build backend) remains an open operator decision.
