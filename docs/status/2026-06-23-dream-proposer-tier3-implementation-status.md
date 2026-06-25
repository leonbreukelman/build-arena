# Dream Proposer Tier 3 Implementation Status — 2026-06-23

Status: local implementation complete; offline suite/lint/type/generated checks green; Opus review returned `ACCEPT_WITH_CHANGES` and the required change was patched.

## Scope implemented

New contracts:

- `docs/schemas/capability-map-v0.schema.json`
- `docs/schemas/dream-v0.schema.json`

New modules:

- `arena/capability_lift.py`
- `arena/dream_generate.py`
- `arena/dream_research.py`
- `arena/dream_gate.py`
- `arena/dream_emit.py`
- `arena/dream_run.py`

New tests:

- `tests/test_capability_lift.py`
- `tests/test_dream_generate.py`
- `tests/test_dream_research.py`
- `tests/test_dream_gate.py`
- `tests/test_dream_emit.py`
- `tests/test_dream_run.py`

Docs:

- `docs/specs/2026-06-23-dream-proposer-tier3-spec.md`
- `docs/agent-wiki/2026-06-23-dream-proposer-failure-modes.md`
- README section: Advisory dream proposer lane

## Verification so far

Focused suite:

```text
uv run pytest tests/test_capability_lift.py tests/test_dream_generate.py tests/test_dream_research.py tests/test_dream_gate.py tests/test_dream_emit.py tests/test_dream_run.py -q
....................................                                     [100%]
```

Focused lint/type:

```text
uv run ruff check arena/capability_lift.py arena/dream_generate.py arena/dream_research.py arena/dream_gate.py arena/dream_emit.py arena/dream_run.py tests/test_capability_lift.py tests/test_dream_generate.py tests/test_dream_research.py tests/test_dream_gate.py tests/test_dream_emit.py tests/test_dream_run.py
All checks passed!

uv run pyright arena/capability_lift.py arena/dream_generate.py arena/dream_research.py arena/dream_gate.py arena/dream_emit.py arena/dream_run.py tests/test_capability_lift.py tests/test_dream_generate.py tests/test_dream_research.py tests/test_dream_gate.py tests/test_dream_emit.py tests/test_dream_run.py
0 errors, 0 warnings, 0 informations
```

Whole-repo checks:

```text
uv run pytest tests -q
........................................................................ [ 13%]
........................................................................ [ 26%]
..........................................................sssssssssss... [ 39%]
........................................................................ [ 52%]
........................................................................ [ 65%]
........................................................................ [ 78%]
........................................................................ [ 91%]
................................................                         [100%]

uv run ruff check .
All checks passed!

uv run pyright
0 errors, 0 warnings, 0 informations

make generated
mkdir -p arena/generated dashboard/src/lib/generated
uv run gen-pydantic schema/arena.yaml > arena/generated/models.py
uv run gen-json-schema schema/arena.yaml > arena/generated/schema.json
uv run gen-typescript schema/arena.yaml > dashboard/src/lib/generated/arena.d.ts
uv run gen-sqlddl schema/arena.yaml > arena/generated/ddl.sql
uv run python scripts/normalize_generated_artifacts.py
```

## Important checkout note

This implementation was done in the live checkout at `fe90dc0...`, which is behind `origin/main` and already had unrelated modified/untracked files. At implementation start, the exact design-grounding path `docs/specs/2026-06-21-proposal-run-and-emit.md` was absent from this checkout, although `origin/main` contains it. The dream lane was implemented without modifying or importing `arena/proposal_run.py`, `arena/proposal_emit.py`, or the frozen proposal stage modules.

## Independent review

Review artifact: `reports/2026-06-23-dream-proposer-tier3-opus-review.json`

Reviewer: Claude Code `--model opus`

Verdict: `ACCEPT_WITH_CHANGES`

Required change patched: `dream_gate` now stamps `provenance.gatedBy: arena.dream_gate`, `dream_emit` refuses artifacts lacking that marker and a gate prompt hash, `dream_gate` rejects capability maps whose `sourceModel.graphHash` diverges from the Project Model v1 graph hash, and `dream_emit` rejects `proposal.md` case-insensitively.

Advisory review note recorded in the spec/wiki: evidence anchor resolution does not prove the free-text `claim`; the lane remains advisory and requires downstream validation.

Post-review focused regression checks:

```text
uv run pytest tests/test_dream_emit.py tests/test_dream_gate.py tests/test_dream_run.py -q
.........................                                                [100%]

uv run ruff check arena/dream_emit.py arena/dream_gate.py tests/test_dream_emit.py tests/test_dream_gate.py tests/test_dream_run.py
All checks passed!

uv run pyright arena/dream_emit.py arena/dream_gate.py tests/test_dream_emit.py tests/test_dream_gate.py tests/test_dream_run.py
0 errors, 0 warnings, 0 informations
```

Post-review full checks:

```text
uv run pytest tests -q
........................................................................ [ 12%]
........................................................................ [ 25%]
............................................................sssssssssss. [ 38%]
........................................................................ [ 51%]
........................................................................ [ 64%]
........................................................................ [ 77%]
........................................................................ [ 90%]
..................................................                       [100%]

uv run ruff check .
All checks passed!

uv run pyright
0 errors, 0 warnings, 0 informations

make generated
mkdir -p arena/generated dashboard/src/lib/generated
uv run gen-pydantic schema/arena.yaml > arena/generated/models.py
uv run gen-json-schema schema/arena.yaml > arena/generated/schema.json
uv run gen-typescript schema/arena.yaml > dashboard/src/lib/generated/arena.d.ts
uv run gen-sqlddl schema/arena.yaml > arena/generated/ddl.sql
uv run python scripts/normalize_generated_artifacts.py
```

## Remaining verification

None for offline acceptance. The operator-gated live `dream_run` remains out of offline scope because it spends live model calls and requires a reviewed capability map.
