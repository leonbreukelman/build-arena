# Autonomous Build Arena

Local-first autonomous build/optimization loop for a single operator.

Current implementation status: Phase 3 hypothesizer + fingerprinting + runner router is complete.

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
- `make generated`, `ruff`, `pyright`, and `pytest` are green.

No dashboard, autonomous loop glue, promotion/rollback machinery, or live subscription-CLI subprocess execution is implemented yet; those are later phases after runner/router contracts are stable.
