# Build Arena — Project Brief

Orientation document for a fresh coding-agent session. Read this after the constitution and AGENTS.md, before touching code. It describes what Build Arena is, what is implemented now, which modules carry the implementation, which claims remain blocked, and the rules that keep autonomous runs verifiable.

Read order each session: `AGENTS.md` and `docs/build-arena-constitution.md` for behavior and boundaries → this brief for the project model → `README.md` for commands → dated plans/verification artifacts only when the current task points at them. Older `docs/build-arena-current-state.md` snapshots are historical unless their date and git state match the live repo.

---

## What Build Arena is

Build Arena is a local-first autonomous iterative-improvement loop for software projects. A project is decomposed into responsibility-bearing units, each unit is improved through a bounded propose-verify-promote cycle, and cross-unit contracts are modeled explicitly instead of being left as agent intuition. The operator defines the goal and scoring dimensions; the loop proposes changes, applies them in isolated worktrees, verifies them mechanically, and advances the internal baseline only through a safe promotion path.

The governing axiom is unchanged: every claim the agent makes must be verifiable by something that is not the agent. Verification is mechanical first, not cognitive. LLM output can help propose or decompose, but it is not allowed to be the load-bearing proof that a change is correct.

The project was originally built verifier-first to avoid a loop that optimizes confident slop. That calibration foundation now exists inside a broader Phase 1-4 loop foundation and a post-Phase-4 AI-first decomposer.

---

## Current implementation status

Phase 1-4 foundation is implemented and verified against the synthetic calibration repo. The codebase now contains:

- Phase 1 scorer calibration: `.arena/scorer.lock.toml`, the deterministic `scorer/engine.py`, scorer-lock validation in `scorer/lock.py`, and a 13-diff synthetic calibration catalog with positive, negative, and neutral patches rebuilt by `scripts/rebuild_calibration.py`. The scorer is configurable through each target's per-repo goal config, but genericity depends on protecting read-only measurement surfaces such as `benchmarks/runtime_proxy.py`.
- Phase 2 verifier calibration: `verifier/engine.py`, `verifier/ablation.py`, `verifier/config.py`, and `verifier/calibration.py`. Verification combines score delta, test status, pinned regressions, and a deterministic ablation quorum. The deterministic no-API stand-in is not a live Lanham ablation gate; its replacement decision is `docs/decisions/2026-06-11-ablation-runner-replacement.md`.
- Phase 3 runner-selection primitives: `arena/fingerprints.py`, `arena/ledger.py`, `arena/hypothesizer.py`, `arena/router.py`, and runner adapters under `arena/runners/`. Fingerprints are deterministic, model-scoped, and target-order-insensitive.
- Phase 4 loop foundation: `arena/loop.py`, `arena/events.py`, `arena/budget.py`, `arena/divergence.py`, and `arena/worktrees.py`. The loop uses append-only JSONL as canonical state, rebuildable SQLite event projections, live wall-clock budget checks, hard divergence halts, locked git worktrees, and ff-only promotion mechanics.
- Boundary protection: `arena/boundary.py` rejects hypotheses that target scorer/verifier/schema/generated surfaces or `.arena/scorer.lock.toml` before runner spawn.
- Generated LinkML models: `arena/generated/` is produced from `schema/arena.yaml` by `make generated` and must not be hand-edited.

The post-Phase-4 AI-first decomposer is also implemented:

- `arena/decomposer.py` emits the deterministic scanner model and Project Model v0 compatibility output.
- `arena/project_graph.py`, `arena/project_snapshot.py`, `arena/project_encyclopedia.py`, and `arena/project_model_gate.py` build the graph, snapshot, encyclopedia, and deterministic gate sidecars from git/filesystem truth.
- `arena/project_decomposer_ai.py` creates snapshot bundles and writes `project-model-v1.json` as the primary Project Model v1 enriched artifact plus `project-model-v0.json` as compatibility output for v0 consumers.
- `arena/project_model_v1.py` wraps the enriched snapshot, graph, gate report, provenance, hashes, model IDs, derived-artifact strategy, and v0 compatibility pointer in the shared v1 contract.
- `arena/project_model_llm.py` contains fixture, recorded, off/noop, and live LLM adapters. `LiveProjectModelLLM` is the direct xAI/OpenAI-compatible live path, backed by the shared OpenAI-compatible client. Live credentials may come from the environment or `~/.hermes/.env`; provider metadata records only `api_key_source`, and live paths require an explicit model ID plus a strict served-model match.
- `arena/runners/diff_proposer.py` contains the deterministic diff proposer runner plus an OpenAI-compatible proposal transport. The shared LLM path is operator-switchable for decomposition and proposal transport by provider/base URL/model/API-key-env configuration; the proposal transport can request a unified diff from an explicit Grok/OpenAI-compatible model and then hands the output to the deterministic patch gate.
- `arena/project_model_cli.py` exposes `snapshot`, `graph`, and `gate`; live mode is guarded by `--allow-live` and refuses routine live spend without that explicit flag.

With mock/no-network verification green, Build Arena is ready to attempt a bounded, operator-authorized real run, not an unattended broad live loop; provider acceptance remains unverified until live smoke and any real attempt still needs an explicit model ID plus call budget.

Build Arena is not ready for broad autonomous live loops. The pre-live readiness register at `docs/verification/2026-06-05-pre-live-readiness-register.json` remains `not_ready_blockers_remain`. Decomposition-informed dry-run hypothesis generation from Project Model v1, real promotion, dashboard control plane, rollback endpoint, and live subscription-CLI subprocess execution remain blocked or unimplemented. Milestone 3 now tracks a narrower naive worktree-only pilot path; it is blocked by internal Build Arena prerequisites (generic scorer, fail-closed proposer tests, and per-repo boundary config) rather than Project Model v1 cross-repo adoption.

---

## Architecture map

### Scoring and verification

`scorer/engine.py` is the deterministic scoring layer. It scores candidate repositories on tests, coverage floor, pyright errors, ruff violations, cyclomatic average, and a deterministic runtime proxy. It validates the scorer lock before each score and exposes drift checks so cached projections cannot masquerade as live truth.

`verifier/engine.py` is the advisory verifier gate for candidate patches. It rescans the live worktree through the scorer, rejects test failures, pinned metric regressions, non-positive score deltas, and non-load-bearing ablation results. It does not judge semantic quality by LLM opinion.

`verifier/calibration.py` runs the curated patch catalog through scorer and verifier to measure false positives and false negatives against the configured targets.

### Autonomous loop foundation

`arena/loop.py` is the async state machine: scan → hypothesize → apply → verify → promote or discard. It emits events for each transition and halts on budget or divergence breaches.

`arena/events.py` is the canonical state layer. JSONL events are append-only and fsynced. SQLite is only a rebuildable projection and can be deleted without changing loop truth.

`arena/worktrees.py` owns cycle worktree creation, locking, teardown, runtime-artifact cleanup, and ff-only promotion from the cycle branch into the main checkout.

`arena/budget.py` enforces wall-clock, cycle-count, and runner-credit caps. `arena/divergence.py` halts on repeated boundary violations, failed fingerprint clusters, and scorer/verifier disagreement streaks.

`arena/fingerprints.py`, `arena/ledger.py`, and `arena/hypothesizer.py` provide repeatable fingerprints, append-only failure-memory, and UCB1 bandit selection over symbolic arms. `arena/router.py` preserves hypothesis identity across primary/fallback runner attempts.

### Project modeling and decomposer

The deterministic scanner path in `arena/decomposer.py` reads git/filesystem state only. It can emit the internal scanner model or the shared Project Model v0 compatibility contract.

The AI-first path starts with a mechanically built graph, asks an LLM path only to enrich/decompose that graph, then runs deterministic gates against provenance. The primary artifact is Project Model v1; v0 is retained as a compatibility projection for downstream repositories that have not adopted v1.

The snapshot bundle contains `graph.json`, `snapshot.json`, `gate-report.json`, `project-model-v1.json`, `project-model-v0.json`, prompts, model outputs, held-out probes, planted negatives, near-neighbor alternatives, and a manifest with paths and hashes.

### Safety boundaries

Autonomous runners must not write outside their cycle worktree. They must not modify `scorer/`, `verifier/`, `schema/`, `.arena/scorer.lock.toml`, or generated artifacts as part of a hypothesis. Promotion is a separate step and must be ff-only. These rules are encoded in AGENTS.md and partially enforced in `arena/boundary.py` and `arena/worktrees.py`.

---

## Commands to trust

Core verification:

```bash
make generated
uv run pytest tests -q
uv run ruff check .
uv run pyright
uv run python scripts/rebuild_calibration.py
uv run python scripts/update_scorer_lock.py
```

Deterministic decomposer:

```bash
uv run python -m arena.decomposer --project <repo> --output <model.json>
uv run python -m arena.decomposer --project <repo> --format project-model-v0 --source-task <task> --output <model-v0.json>
```

AI-first snapshot and sidecars without live provider calls:

```bash
uv run python -m arena.project_model_cli snapshot --project <repo> --artifacts-root <dir> --project-id <id> --goal <goal> --llm-mode fixture
uv run python -m arena.project_model_cli graph --project <repo> --output <graph.json>
uv run python -m arena.project_model_cli gate --snapshot <manifest.json>
```

Bounded read-only live smoke, only when explicitly authorized and with an explicit model ID:

```bash
uv run python -m arena.project_model_cli snapshot --project <repo> --artifacts-root <dir> --project-id <id> --goal <goal> --llm-mode live --allow-live --live-model <explicit-model>
```

Provider/base URL/API-key-env are operator-switchable with `--live-provider`, `--live-base-url`, and `--live-api-key-env`.

---

## Known findings and lessons

- Verification must be rebuilt from filesystem and git ground truth. Cached projections and stale generated outputs are never authoritative.
- F3/generalization is pre-code proposal reasoning: goal, decomposition, process, architecture, spec, and action should be tested for generalization before code is treated as the only artifact. Elenchus Core is advisory, not a standalone truth oracle.
- Project Model v0 remains useful as a compatibility layer, but Project Model v1 is now the primary enriched artifact for the AI-first decomposer.
- Live provider paths are intentionally bounded. The code has a direct xAI/OpenAI-compatible adapter, but routine broad loops must stay on fixture/recorded/off modes until readiness blockers are resolved.
- Historical docs and verification artifacts may describe earlier calibration-only states. Treat dated artifacts as evidence for their point in time, not as current status unless AGENTS.md, README.md, and this brief agree with them.

---

## Current blockers and backlog

Blockers before broad live autonomy:

1. Dry-run hypothesis generation from Project Model v1 is not implemented.
2. Worktree patch cycles driven by v1 snapshots are not implemented. A narrower naive Milestone 3 worktree-only pilot is planned separately and remains blocked until generic scoring, fail-closed proposal, and per-repo boundary config land.
3. Real promotion remains blocked behind readiness-register closure and operator-controlled rollout.
4. Dashboard control plane is not implemented.
5. Rollback endpoint is not implemented.
6. Live subscription-CLI subprocess execution is not implemented.
7. Related downstream repos that consume Project Model v0 still need v1 adoption plans.

Near-term useful work:

1. Keep doc/status tests guarding active orientation docs against calibration-era drift.
2. Exercise fixture-mode AI-first snapshots against this repo and held-out repos without live spend.
3. Define the dry-run hypothesis-generation contract over Project Model v1.
4. Prove the Milestone 3 naive worktree-only pilot with no promotion first, then evaluate decomposition-informed/v1 cycles and promotion only after their separate blockers close.
5. Update dated current-state artifacts or mark them historical when they conflict with README.md, AGENTS.md, or this brief.

---

## Hard constraints for any session

- Before quoting or editing a file, read that exact path in the current turn.
- Do not guess at function/class/symbol existence; inspect files or search first.
- Do not modify `scorer/`, `verifier/`, `schema/`, `.arena/scorer.lock.toml`, or `arena/generated/` as part of an arena-generated hypothesis.
- Do not run `git checkout`, `git branch -f`, `git reset --hard`, `git rebase`, or `git push` inside a cycle worktree.
- Do not hand-edit generated artifacts. Run `make generated` after intentional schema changes.
- Do not run live Build Arena provider/decomposition calls unless explicitly authorized.
- Do not claim broad loop readiness while `not_ready_blockers_remain` is still present in the readiness register. Treat the current verifier ablation keyword gate as advisory for real cycles until a real ablation runner exists.
- Keep commits and promotions separate: normal repo commits are operator/agent packaging; arena promotions must use the promoter path and ff-only merge semantics.

---

## Reference files

- `AGENTS.md` — active operating rules, status summary, command reference, and read-only boundary rules.
- `README.md` — concise implementation status and CLI examples.
- `docs/build-arena-constitution.md` — behavior layer and project philosophy.
- This brief — orientation and current architecture map.
- `docs/verification/2026-06-05-pre-live-readiness-register.json` — current readiness register and blocker status.
- `docs/specs/2026-06-05-project-model-v1-shared-contract-spec.md` — Project Model v1 contract context.
- `docs/project-model-v0.md` and `docs/schemas/project-model-v0.schema.json` — compatibility contract for existing v0 consumers.
- `schema/arena.yaml` — source schema for generated models.
- `tests/test_project_status_docs.py` — guardrails for active documentation/status alignment.
