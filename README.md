# Autonomous Build Arena

Local-first autonomous build/optimization loop for a single operator.

Repo identity: this main loop/system repo is `build-arena`. Internal
`.arena/calibration/` artifacts are scorer/verifier calibration data, not the
repo identity. The separate `arena-calibration` repo is the smaller public
calibration harness.

Current implementation status: Phase 4 loop glue, budget, divergence, event projection, and worktree promotion foundation is complete.

Implemented acceptance gates:

- `.arena/scorer.lock.toml` pins scorer source by content hash.
- Re-scoring the same git OID is deterministic within `1e-6` on every axis.
- Calibration catalog has 13 diffs: 5 positive, 5 negative, 3 neutral.
- Phase 1 scorer ordering assertions pass across the full catalog.
- Hypotheses touching `scorer/`, `verifier/`, `schema/`, generated artifacts, or scorer lock files are rejected before runner spawn.
- Phase 2 verifier evaluates score delta, tests, pinned regressions, and ablation quorum independently.
- Coverage is a pinned axis by floor, not by monotonic movement: drops that remain above the configured floor are allowed, while drops below the floor reject.
- Ablation configuration defaults to the `ollama` runner identity with 3 Lanham probes and a 2-of-3 quorum; Phase 2 uses a deterministic no-API stand-in and defers the live Ollama adapter to the runner-integration phase.
- Verifier calibration separately measures false positives and false negatives over the curated diff catalog: FP = 0, FN rate <= 10%. On the current 5-positive catalog this means 0 missed positives.
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
- Phase 4 worktree management creates locked git worktrees and promotes verified changes via ff-only merge after runtime-artifact cleanup.
- Phase 4 loop glue is a plain async `match state:` orchestrator and the calibration E2E promotes at least one positive patch.
- `make generated`, `ruff`, `pyright`, and `pytest` are green.

No dashboard control plane, rollback endpoint, or live subscription-CLI subprocess execution is implemented yet; those are later phases after the loop foundation remains green.

## Project decomposition

Phase 5 begins with a deterministic project decomposer. It can be called before the normal optimization loop to emit a mechanically checkable project model:

```bash
uv run python -m arena.decomposer --project /path/to/project --output /tmp/project-model.json
```

Use `--output -` for canonical JSON on stdout, and `--fail-on-gap` when a caller wants explicit verification gaps to fail the command. The Python API is `arena.decomposer.decompose_project()` plus `validate_project_model()`.

To emit the shared cross-repo Project Model v0 contract from a primary task/backlog item before planning begins, request the v0 format explicitly:

```bash
uv run python -m arena.decomposer \
  --project /path/to/project \
  --format project-model-v0 \
  --source-task "Implement the primary task" \
  --primary-backlog-item "https://github.com/owner/repo/issues/123" \
  --output /tmp/project-model-v0.json
```

The default output remains the internal deterministic scanner model (`schema_version: project-model/v0.1`) for compatibility. Downstream repositories should consume the explicit v0 output (`schemaVersion: project-model/v0`) and run the deterministic quality gate via `arena.decomposer.validate_project_model_v0()` or `arena.project_model_v0.evaluate_quality_gate()`; ownership coverage remains separate from quality scoring. The CLI writes the JSON artifact before reporting validation failures, so non-zero output for unclassified surface or verification gaps still leaves an inspectable model for downstream triage.

The first pilot target is the separate `arena-calibration` checkout. A real local run should produce a model with covered components for fixture manifests, scorer, verifier, provider boundary, runner discrimination matrix, tests, docs, and configuration, plus the manifest-derived `patch_generalization_axis_missing` gap for `F3_bad_passes_tests`. Coverage is ownership accounting, not quality scoring; downstream gates should treat `verification_gaps` and any `unclassified_project_surface` component as the actionable quality signals.

For cross-repo Phase 5 coordination, the shared Project Model v0 compatibility target is documented in `docs/project-model-v0.md` with its machine-readable schema at `docs/schemas/project-model-v0.schema.json` and worked examples under `docs/examples/`.
