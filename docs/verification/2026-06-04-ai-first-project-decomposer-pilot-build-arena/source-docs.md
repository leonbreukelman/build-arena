# build-arena pilot source docs

Repo: `/home/leonb/projects/build-arena`

Selection: Required pilot 1: Build Arena itself.

## AGENTS.md

```text
# AGENTS.md — Autonomous Build Arena

## Anti-fabrication rules (highest priority)

1. NEVER reason from an imagined file. Before quoting or editing any file content, read that exact path in the current turn.
2. NEVER guess at function/class/symbol existence. Inspect files or search first.
3. The scanner/scorer model must be rebuilt from filesystem and git ground truth. Cached projections are never authoritative.

## Boundary-violation rules

1. NEVER modify anything under `scorer/`, `verifier/`, or `schema/` as part of an arena-generated hypothesis. These paths are read-only to autonomous runners.
2. NEVER modify `.arena/scorer.lock.toml` from inside an arena cycle. Bumping the scorer requires a new run/operator action.
3. NEVER hand-edit files under `arena/generated/`. They are produced from `schema/arena.yaml` by `make generated`.
4. NEVER bypass `git worktree` for future APPLY/PROMOTE phases. Phase 1 tests may use temporary fixture repos only.

## Worktree rules for future runners

1. Runner writes are restricted to `.arena/worktrees/<cycle_id>/`.
2. Do not run `git checkout`, `git branch -f`, `git reset --hard`, `git rebase`, or `git push` inside a cycle worktree.
3. The promoter is the only component allowed to advance the internal baseline, and it must use `git merge --ff-only`.

## Current phase

Phase 4 loop glue, budget, divergence detection, event projection, and worktree promotion foundation are implemented and verified. Intent embeddings remain deterministic no-API stand-ins seeded by the pinned model name; live embedding execution is deferred. The loop now uses JSONL events as canonical state, locked git worktrees for cycle isolation, ff-only promotion, live wall-clock budget checks, and hard divergence halts. Do not implement the dashboard control plane, rollback endpoint, or live subscription-CLI subprocess execution until Phase 4 remains green and the next phase is explicitly started.

## Commands

- `make generated` — regenerate LinkML artifacts.
- `uv run pytest tests -q` — run tests.
- `uv run ruff check .` — lint source.
- `uv run pyright` — type-check source.
- `uv run python scripts/rebuild_calibration.py` — rebuild synthetic calibration repo and patch catalog.
- `uv run python scripts/update_scorer_lock.py` — update `.arena/scorer.lock.toml` after intentional scorer source changes.

```

## README.md

```text
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

```

## pyproject.toml

```text
[project]
name = "build-arena"
version = "0.1.0"
description = "Local-first autonomous build arena with anti-fabrication scorer calibration"
requires-python = ">=3.12"
dependencies = [
    "linkml>=1.8.7",
    "mabwiser>=2.7.4",
    "pydantic>=2.7",
    "pyyaml>=6.0",
    "tomli-w>=1.0",
]

[dependency-groups]
dev = [
    "pytest>=8.2",
    "pytest-cov>=5.0",
    "ruff>=0.6",
    "pyright>=1.1",
]

[tool.pytest.ini_options]
addopts = "-q"
testpaths = ["tests"]
pythonpath = ["."]

[tool.ruff]
target-version = "py312"
line-length = 100
exclude = ["arena/generated", ".arena/calibration/repo"]

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B", "SIM"]
ignore = ["E501"]

[tool.pyright]
include = ["arena", "scorer", "verifier", "scripts", "tests"]
exclude = ["arena/generated", ".arena/calibration/repo"]
typeCheckingMode = "standard"
pythonVersion = "3.12"
reportMissingTypeStubs = false

[tool.coverage.run]
source = ["arena", "scorer", "verifier", "scripts"]
omit = ["arena/generated/*"]

[tool.coverage.report]
fail_under = 100
show_missing = true
exclude_also = [
    "if __name__ == .__main__.:",
    "def .*: \\.\\.\\.",
]

```
