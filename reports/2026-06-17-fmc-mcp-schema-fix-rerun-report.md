# fmc-mcp Grok 4.3 high-reasoning schema fix and rerun — 2026-06-17

## Owner verdict

Schema issue resolved.

The previous Grok 4.3 high-reasoning run failed the deterministic Project Model gate only because universal `cross_cutting_concerns` were keyed by canonical names in `id` but thematic labels in `category`. The gate keys universal concerns by `category`.

After the fix and rerun:

- Previous high-reasoning run: `FAIL_CLOSED_DECOMPOSITION_GATE`, 3 violations.
- New high-reasoning rerun: `PASS_DECOMPOSITION_GATE`, 0 violations.
- The three prior cross-cutting-concern violations are gone.
- No intake, scorecard, proposal, candidate runner, or promotion path was run.
- `fmc-mcp` target repo state after rerun remained `main...origin/main [ahead 1]`; Build Arena did not mutate it.

## Files changed

- `arena/project_decomposer_ai.py`
- `tests/test_project_decomposer_ai.py`
- `docs/status/2026-06-17-fmc-mcp-schema-fix-status.md`
- `docs/status/INDEX.md`

No edits under protected/generated paths: `scorer/`, `verifier/`, `schema/`, or `arena/generated/`.

## Root cause

Previous failing raw output:

| Concern id | Raw category |
|---|---|
| `anti_fabrication` | `integrity` |
| `determinism` | `reliability` |
| `provenance` | `traceability` |
| `no_live_paid_api_acceptance` | `compliance` |

The snapshot persisted those thematic categories unchanged, so the gate saw no categories matching:

- `anti_fabrication`
- `determinism`
- `provenance`
- `no_live_paid_api_acceptance`

That produced:

1. `Missing universal concerns: anti_fabrication, determinism, no_live_paid_api_acceptance, provenance.`
2. `Universal concern anti_fabrication does not cover components: ...`
3. `Universal concern provenance does not cover components: ...`

## Opus plan

Plan prompt:
`<repo>/reports/2026-06-17-fmc-mcp-schema-fix-opus-plan-prompt.md`

Opus plan result:
`<repo>/reports/2026-06-17-fmc-mcp-schema-fix-opus-plan-retry.json`

Opus root-cause summary: the deterministic gate keys universal concerns by `category`, while Grok put canonical universal names in `id` and thematic labels in `category`. Opus recommended a narrow two-part fix: prompt hardening plus in-memory canonicalization only when concern `id` exactly normalizes to a known universal concern.

## Implementation

Implemented:

1. Prompt hardening in `_decomposer_prompt(...)`:
   - states that universal concern `category` MUST be exactly one of the canonical enum values;
   - explicitly says not to use thematic labels such as `integrity`, `reliability`, `traceability`, or `compliance` in `category`;
   - includes an example with `"category": "anti_fabrication"`.

2. Narrow in-memory repair in AI ingestion:
   - imports `UNIVERSAL_CONCERNS` from `arena.project_model_gate` as the single source of truth;
   - normalizes only `CrossCuttingConcern.category` when the concern `id` exactly normalizes to a canonical universal key;
   - does not infer from descriptions;
   - does not map arbitrary unknown categories;
   - does not mutate persisted raw model output.

## Tests added

Added RED/GREEN regressions in `tests/test_project_decomposer_ai.py`:

- `test_recorded_model_output_repairs_universal_concern_category_from_exact_id`
  - reproduces the observed drift: canonical universal concern in `id`, thematic label in `category`;
  - asserts the gate passes after in-memory repair;
  - asserts persisted raw output still contains thematic categories.

- `test_recorded_model_output_does_not_repair_unknown_concern_category`
  - proves unknown thematic categories are not broadly remapped;
  - confirms the gate still fails for genuinely missing `anti_fabrication`.

- `test_live_decomposer_prompt_makes_universal_concern_categories_non_negotiable`
  - locks the prompt hardening text.

RED evidence before implementation:

```text
uv run pytest tests/test_project_decomposer_ai.py::test_recorded_model_output_repairs_universal_concern_category_from_exact_id tests/test_project_decomposer_ai.py::test_recorded_model_output_does_not_repair_unknown_concern_category tests/test_project_decomposer_ai.py::test_live_decomposer_prompt_makes_universal_concern_categories_non_negotiable -q
F.F [100%]
```

## Verification

Commands run after implementation:

```text
uv run pytest tests/test_project_decomposer_ai.py::test_recorded_model_output_repairs_universal_concern_category_from_exact_id tests/test_project_decomposer_ai.py::test_recorded_model_output_does_not_repair_unknown_concern_category tests/test_project_decomposer_ai.py::test_live_decomposer_prompt_makes_universal_concern_categories_non_negotiable -q
... [100%]

uv run pytest tests/test_project_decomposer_ai.py -q
................ [100%]

uv run pytest tests/test_project_meta_decomposer.py -q
.............. [100%]

uv run ruff check arena/project_decomposer_ai.py tests/test_project_decomposer_ai.py
All checks passed!

git diff --check -- arena/project_decomposer_ai.py tests/test_project_decomposer_ai.py
<no output, exit 0>

uv run pyright
0 errors, 0 warnings, 0 informations

uv run pytest tests -q
........................................................................ [ 13%]
........................................................................ [ 27%]
........................sssssssssss..................................... [ 41%]
........................................................................ [ 55%]
........................................................................ [ 69%]
........................................................................ [ 83%]
........................................................................ [ 97%]
..............                                                           [100%]

uv run ruff check .
All checks passed!

uv run pytest tests/test_project_status_docs.py -q
........................ [100%]
```

## Opus implementation review

Review packet:
`<repo>/reports/2026-06-17-fmc-mcp-schema-fix-opus-review-packet.md`

Review result:
`<repo>/reports/2026-06-17-fmc-mcp-schema-fix-opus-review-retry.json`

Opus verdict: `ACCEPT`

Opus blocking issues: none.

Opus summary:

> ACCEPT — the fix correctly targets the root cause (gate keys universal concerns by category; model put canonical names in id and thematic labels in category) by canonicalizing category from an exact id match against UNIVERSAL_CONCERNS, the gate's single source of truth. Normalization is appropriately narrow: exact known-universal id only, no description/theme inference, raw artifact preserved, gate logic untouched.

Nonblocking notes from Opus:

- Add a future test for dotted/prefixed id form such as `concern.anti-fabrication`.
- Add a one-line code comment documenting id-over-category precedence.
- Confirm downstream raw-output consumers do not key on raw `category`.

Opus explicitly said those did not block the rerun.

## Live high-reasoning rerun

Run root:
`<repo>/.arena/runs/fmc-mcp-decomposition-grok43-high-reasoning-schema-fix-20260617T221237Z`

Snapshot:
`<repo>/.arena/runs/fmc-mcp-decomposition-grok43-high-reasoning-schema-fix-20260617T221237Z/snapshot-3e9b19da00478bf8`

Wrapper:
`<repo>/.arena/runs/fmc-mcp-decomposition-grok43-high-reasoning-schema-fix-20260617T221237Z/run_high_reasoning_snapshot.py`

Command artifact:
`<repo>/.arena/runs/fmc-mcp-decomposition-grok43-high-reasoning-schema-fix-20260617T221237Z/command.txt`

Stdout artifact:
`<repo>/.arena/runs/fmc-mcp-decomposition-grok43-high-reasoning-schema-fix-20260617T221237Z/snapshot.stdout.json`

Rerun stdout:

```json
{
  "passed": true,
  "snapshot_id": "snapshot-3e9b19da00478bf8",
  "violation_count": 0
}
```

Deterministic gate rerun command:

```text
uv run python -m arena.project_model_cli gate --snapshot <repo>/.arena/runs/fmc-mcp-decomposition-grok43-high-reasoning-schema-fix-20260617T221237Z/snapshot-3e9b19da00478bf8/manifest.json
```

Gate output:

```json
{"passed": true, "violations": []}
```

## Previous vs new comparison

Comparison artifact:
`<repo>/reports/2026-06-17-fmc-mcp-schema-fix-rerun-comparison.json`

| Axis | Previous non-reasoning | Previous high-reasoning | New high-reasoning after fix |
|---|---:|---:|---:|
| Snapshot | `snapshot-ddb951deca8d5c7b` | `snapshot-a623425c6db6a181` | `snapshot-3e9b19da00478bf8` |
| Gate passed | yes | no | yes |
| Gate violations | 0 | 3 | 0 |
| Raw components | 7 | 6 | 6 |
| Raw contracts | 4 | 0 | 7 |
| Snapshot contracts after deterministic closure | 31 | 16 | 14 |
| Runtime contracts | 43 | 23 | 21 |
| External surfaces | 30 | 28 | 28 |
| Product invariants | 6 | 6 | 6 |
| Quality gates | 4 | 3 | 3 |
| Priority backlog | 5 | 5 | 5 |
| Open questions | 5 | 5 | 5 |
| Component rank 1 | `comp-tests` | `comp:client` | `component.client` |
| Reasoning tokens | 0 | 7,897 | 8,255 |
| Total tokens | 11,378 | 16,874 | 17,808 |
| Exact cost ticks | 189,303,000 | 326,678,000 | 348,540,500 |

New raw concerns:

| Concern id | Raw category |
|---|---|
| `concern.anti-fabrication` | `anti_fabrication` |
| `concern.determinism` | `determinism` |
| `concern.provenance` | `provenance` |
| `concern.no-live-paid-api-acceptance` | `no_live_paid_api_acceptance` |

New snapshot concerns matched the raw canonical categories. The prompt hardening caused Grok 4.3 high-reasoning to emit the correct categories directly; the in-memory repair path remains covered by regression tests for future drift.

## Intake/proposal boundary check

The rerun root contains no scorecard, intake, or proposal artifacts. The comparison script checked for files matching scorecard/proposal/intake under the new run root and found none.

Target repo state after rerun:

```text
## main...origin/main [ahead 1]
```

## Conclusion

The schema issue is resolved.

The new Grok 4.3 high-reasoning decomposition is now gate-clean while keeping the improved production-component ranking that the earlier high-reasoning run had. It is still a decomposition-only result; it does not prove intake/proposal/promotion readiness and was not fed into intake.
