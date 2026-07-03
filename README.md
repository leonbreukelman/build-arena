# Autonomous Build Arena

Local-first autonomous build/optimization loop for a single operator.

Repo identity: this main loop/system repo is `build-arena`. Internal
`.arena/calibration/` artifacts are scorer/verifier calibration data, not the
repo identity. The separate `arena-calibration` repo is the smaller public
calibration harness.

Current implementation status: Phase 1-4 foundation is implemented and verified against the synthetic calibration repo, and the post-Phase-4 AI-first decomposer is implemented locally. The AI decomposer writes `project-model-v1.json` as the primary Project Model v1 enriched artifact; `iterationReadiness` is a required v1 field because the core intake/proposal pipeline reads it. The human reference is `docs/project-model-v1.md`, with an example instance under `docs/examples/`. `LiveProjectModelLLM` provides a bounded read-only xAI/OpenAI-compatible live path behind the CLI `--allow-live` guard. Advisory proposal and dream stages are operator-switchable by provider/base URL/model/API-key-env. Invoking a live command with an explicitly named live model is operator approval to spend; no command may spend on an unnamed/default model or accept a response from a different served model. Target apply/promote machinery was retired after the 2026-06-28 local `fmc-mcp` run proved the old production loop could mutate a target outside the propose-only policy. Build Arena is now propose-only and issue-oriented: `arena.proposal_run` emits `proposal.md`, `arena.dream_run` emits `experiment.md`, and `arena.package_issue` can render or explicitly open a GitHub issue for the target project's coding agent to accept or reject. Build Arena must never open a PR, push a branch, apply code, promote code, or otherwise mutate a target repo. Build Arena is not ready for broad autonomous live loops: the pre-live readiness register at `docs/verification/2026-06-05-pre-live-readiness-register.json` still reports `not_ready_blockers_remain`, but that register scopes retired broad-autonomy / target-mutation concepts rather than the current issue-only proposal artifact lane.

Implemented acceptance gates:

- `.arena/scorer.lock.toml` pins scorer source by content hash.
- Re-scoring the same git OID is deterministic within `1e-6` on every axis.
- Calibration catalog has 13 diffs: 5 positive, 5 negative, 3 neutral.
- Phase 1 scorer ordering assertions pass across the full catalog. The scorer is configurable through each target's per-repo goal config, but genericity depends on protecting read-only measurement surfaces such as `benchmarks/runtime_proxy.py`.
- Hypotheses touching `scorer/`, `verifier/`, `schema/`, generated artifacts, or scorer lock files are rejected before runner spawn.
- Phase 2 verifier evaluates score delta, tests, pinned regressions, and ablation quorum independently.
- Coverage is a pinned axis by floor, not by monotonic movement: drops that remain above the configured floor are allowed, while drops below the floor reject.
- Ablation configuration defaults to the `ollama` runner identity with 3 Lanham probes and a 2-of-3 quorum; Phase 2 uses a deterministic no-API stand-in, not a live Lanham ablation gate. The replacement target is recorded in `docs/decisions/2026-06-11-ablation-runner-replacement.md`.
- Verifier calibration separately measures false positives and false negatives over the curated diff catalog against that deterministic stand-in: FP = 0, FN rate <= 10%. On the current 5-positive catalog this means 0 missed positives; it is not a live ablation-performance claim.
- Verifier calls rescore live worktrees and rerun probes instead of reusing cached probe results.
- Phase 3 fingerprints are deterministic, model-scoped, target-order-insensitive, and shaped as 32-hex blake2b ids with SHA-256 component metadata.
- Phase 3 intent embeddings are deterministic no-API SHA-256 expansions seeded by the pinned embedding model name; the live `BAAI/bge-small-en-v1.5` embedding adapter is deferred to the loop/integration phase.
- Phase 3 failure ledger is append-only JSONL and rejects previously failed fingerprints before runner spawn.
- Phase 3 bandit uses MABWiser UCB1 after deterministic cold-start pulls over configured symbolic arms.
- Phase 3 runner router preserves Hypothesis identity across `claude_code` credit exhaustion fallback to `ollama`.
- Phase 3 Claude stream parser enforces ViewBeforeEdit within the same assistant turn.
- Phase 4 event storage writes append-only, fsynced JSONL as canonical state and mirrors/replays into a SQLite projection.
- Phase 4 budget checks run from the loop with live wall-clock time and convert breaches into `HaltRecord`s.
- Phase 4 divergence detection halts on boundary-attempt thresholds, failed fingerprint clusters, and wired scorer/verifier disagreement streaks.
- Phase 4 worktree management creates locked git worktrees for the synthetic calibration foundation and keeps historical ff-only internal-baseline mechanics covered by tests.
- Phase 4 loop glue is a plain async `match state:` orchestrator for the synthetic calibration foundation. Unexpected loop exceptions are converted into `HaltRecord` evidence and active worktree teardown is attempted before halt.
- `make generated`, `ruff`, `pyright`, and `pytest` are green.

Post-Phase-4 decomposer status:

- The AI-first decomposer builds a graph, wiki/encyclopedia, snapshot, deterministic gate report, and sidecar manifest from git/filesystem truth.
- AI decomposer snapshots write `project-model-v1.json` as the primary enriched artifact.
- The v1 manifest records the primary v1 artifact path, hash, and provenance so downstream consumers do not have to infer the authoritative model from sidecars.
- The direct xAI/OpenAI-compatible adapter is fail-closed for cancelled, empty, invalid, truncated, and strict served-model match failures and remains behind existing live CLI gates where implemented. Credentials can come from the environment or `~/.hermes/.env`; provider metadata records only `api_key_source`, never the key.
- The shared OpenAI-compatible LLM path is operator-switchable for read-only decomposition and advisory proposal/dream stages by provider/base URL/model/API-key-env configuration. Live surfaces treat an explicit model ID as spend approval, require that model to be named, and enforce served-model match checks.
- The target apply/promote roots were removed in the 2026-06-27 propose-only remediation. Historical production-run reports remain evidence for their point in time, not runnable guidance.
- Downstream consumers should read Project Model v1 directly; compatibility projection output has been removed from the active runtime.

No dashboard control plane, rollback endpoint, or live subscription-CLI subprocess execution is implemented; those are stale broad-autonomy concepts for the current issue-only proposal artifact lane unless the operator explicitly reopens a target-mutation product goal.

## Project decomposition

### Deterministic scanner and Project Model v1

The deterministic decomposer can be called before the normal optimization loop to emit a mechanically checkable scanner model:

```bash
uv run python -m arena.decomposer --project /path/to/project --output /tmp/project-model.json
```

Use `--output -` for canonical JSON on stdout, and `--fail-on-gap` when a caller wants explicit verification gaps to fail the command. The Python API is `arena.decomposer.decompose_project()` plus `validate_project_model()`.

The deterministic scanner output uses `schema_version: project-scanner/v0.1`. It is an internal scanner artifact, not the shared project-model contract. For the active shared contract, use `arena.project_model_cli snapshot` and consume `project-model-v1.json`. The v1 schema is `docs/schemas/project-model-v1.schema.json`; the reference is `docs/project-model-v1.md`; examples live under `docs/examples/`.

### AI-first snapshot, graph, and gate commands

The post-Phase-4 AI-first path uses `arena.project_model_cli` to create a sidecar bundle and Project Model v1 primary artifact:

```bash
uv run python -m arena.project_model_cli snapshot \
  --project /path/to/project \
  --artifacts-root /tmp/build-arena-snapshot \
  --project-id example-project \
  --goal "Decompose the project from git/filesystem truth" \
  --llm-mode fixture
```

A bounded read-only decomposer live smoke still uses the existing `--allow-live` and live-mode guard. Provider settings are operator-switchable with `--live-provider`, `--live-base-url`, `--live-model`, and `--live-api-key-env`. An explicit `--live-model` is required for any real attempt and constitutes spend approval for that named model only; broad loops must not use this path until readiness blockers close:

```bash
uv run python -m arena.project_model_cli snapshot \
  --project /path/to/project \
  --artifacts-root /tmp/build-arena-live-snapshot \
  --project-id example-project \
  --goal "Read-only live decomposition smoke" \
  --llm-mode live \
  --live-model <explicit-model> \
  --allow-live
```

Graph and gate sidecars can be exercised without live provider calls:

```bash
uv run python -m arena.project_model_cli graph --project /path/to/project --output /tmp/project-graph.json
uv run python -m arena.project_model_cli gate --snapshot /tmp/build-arena-snapshot/<snapshot-id>/manifest.json
```

The AI-first snapshot command emits `project-model-v1.json` as the Project Model v1 primary artifact. Live mode is only for bounded read-only smoke under the readiness ladder; Build Arena remains not ready for broad autonomous live loops.

## Experiment proposer lane

`arena.dream_run` is a separate tier-3 advisory lane for experiment proposals that do not fit the single-file deterministic proposal contract. The code modules are still named `arena.dream_*` pending a dedicated rename pass. The lane chains snapshot/decompose → intake → capability lift → dream generation → dream research → premise gate → emit, runs end-to-end with no mid-run human review gate, and writes `experiment.md` only. It never writes `proposal.md` and never applies or promotes a change.

```bash
uv run python -m arena.dream_run run /path/to/target-repo \
  --live-model <explicit-model> \
  --live-api-key-env XAI_API_KEY \
  --output experiment.md
```

The capability map is the intent-anchoring artifact. `arena.capability_lift` writes `capability-map.json` with `review.reviewed: false`; `dream_run` uses that auto-generated map as-is. `review.reviewed` is an honest provenance label carried into the output, not a blocker.

The deterministic boundary is the gated `dream/v1` artifact. Generation and research are live model stages and require an explicit `--live-model`; `arena.dream_gate` then kills any experiment proposal whose cited anchors or target capabilities do not resolve against the real Project Model v1 and capability map, stamps gate provenance, rejects capability maps whose graph hash no longer matches the model, and runs `arena.dream_admissibility` so premise-resolved current-state restatements are not emitted. `arena.dream_emit` renders only gate-marked `premiseConfidence == all_resolved` proposals, with premise confidence, speculative conclusion confidence, explicit structural delta, validation recipe, and the capability-map provenance label shown separately.

Exit codes: `0` success (`experiment.md` written); `1` stage failure; `2` no proposal survived the premise gate; `3` usage/preflight error.

## Ticket-ready proposal lane

`arena.proposal_run` is the propose-only lane for GitHub-issue-ready improvement signals. It chains snapshot/decompose → intake → proposal plan → pairwise rerank → emit and writes `proposal.md`. It never applies a patch, promotes a branch, opens a PR, pushes a branch, or mutates the target repository. The target project's coding agent owns analysis, acceptance/rejection, implementation, and any PRs in that target project.

```bash
uv run python -m arena.proposal_run run /path/to/target-repo \
  --live-model <explicit-model> \
  --live-api-key-env XAI_API_KEY \
  --output proposal.md
```
