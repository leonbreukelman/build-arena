# Build Arena Agent Wiki

This directory is the repo-local agent wiki for Build Arena.

Purpose: give future agents persistent operational memory that is versioned with the repo, grounded in artifacts, and safe to feed into proposal/development prompts.

## Required use

Before a production pass, proposal run, or implementation of the autonomy loop, read this wiki alongside `AGENTS.md`, the latest relevant report in `reports/`, and the current plan in `docs/plans/`.

Future implementation should make this more than prose: the proposal registry, live proposer prompt, and repair loop should be able to consume the relevant wiki records so prior invisible proposals and failure modes are not rediscovered from scratch.

## Initial pages

- `2026-06-15-fmc-mcp-production-pass-lessons.md` — safe failed live run, full-autonomy deviations, and proposal-registry lesson.
- `2026-06-15-proposal-registry-lineage-and-repair-loop.md` — implemented registry/lineage, candidate-skip observability, repair retry, and multi-target proposal mechanics.
- `2026-06-23-dream-proposer-failure-modes.md` — tier-3 dream proposer lane boundaries, capability-map review gate, premise-kill gate, novelty floor, and acceptance-rate failure modes.

## Minimum wiki sections to grow

- Gate catalog: commands, invariants, and concrete recipes for passing each gate.
- Known failure modes: failed candidate events and deterministic repair notes.
- Proposal registry view: pending, applied, failed, promoted, rejected, and duplicate proposals with lineage.
- Target branch/lineage map: base refs, head OIDs, dirty-state fingerprints, latest accepted model and scorecard IDs.
- Per-finding recipes: how each finding type becomes a runnable proposal with load-bearing verification.
- Promotion definition of done: what proof is needed before a change counts as a real autonomous improvement.

## Anti-patterns

- Do not use this wiki as a stale chat log.
- Do not store credentials, raw secrets, or one-off temporary task state here.
- Do not let wiki prose replace deterministic gates; the wiki informs agents, gates decide.
