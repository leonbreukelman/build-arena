# Autonomous Build Arena

Local-first autonomous build/optimization loop for a single operator.

Current implementation status: Phase 1 foundation is the active target.

Phase 1 acceptance gates:

- `.arena/scorer.lock.toml` pins scorer source by content hash.
- Re-scoring the same git OID is deterministic within `1e-6` on every axis.
- Calibration catalog has 13 diffs: 5 positive, 5 negative, 3 neutral.
- Ordering assertions pass across the full catalog.
- Hypotheses touching `scorer/`, `verifier/`, or `schema/` are rejected before runner spawn.
- `make generated`, `ruff`, `pyright`, and `pytest` are green.

No dashboard, runner loop, or autonomous patch promotion is implemented yet; those are later phases after scorer calibration is stable.
