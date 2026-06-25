# fmc-mcp Grok 4.3 high-reasoning decomposition comparison — 2026-06-17

## Owner verdict

The Grok 4.3 high-reasoning decomposition ran, but it failed the deterministic Project Model gate.

Run verdict, high reasoning: `FAIL_CLOSED_DECOMPOSITION_GATE`

Previous non-reasoning run verdict: `PASS_DECOMPOSITION_GATE`

Opus comparison review verdict: `MIXED`

Which artifact is safer for next intake right now: previous non-reasoning, because it passed the gate. High reasoning had a better component ranking, but a fail-closed gate beats better-looking semantics.

I stopped before intake again. No scorecard, proposal, or intake artifacts were created under the high-reasoning run root.

## Important implementation detail

Build Arena's current `project_model_cli snapshot` path exposes `--live-model` but does not expose an xAI `reasoning_effort` CLI flag.

To make this run actually use high reasoning without changing source code, I used a run-local wrapper that calls `build_project_model_snapshot(...)` and injects this into the OpenAI-compatible request payload:

```json
{"model": "grok-4.3", "reasoning_effort": "high"}
```

The high-reasoning preflight proved xAI accepted that shape:

- Requested model: `grok-4.3`
- Served model: `grok-4.3`
- Reasoning effort: `high`
- Finish reason: `stop`
- Reasoning tokens on preflight: 263

Preflight artifact:
`<repo>/reports/2026-06-17-fmc-mcp-grok43-high-reasoning-preflight.json`

## High-reasoning run artifacts

- Run root: `<repo>/.arena/runs/fmc-mcp-decomposition-grok43-high-reasoning-20260617T205352Z`
- Snapshot dir: `<repo>/.arena/runs/fmc-mcp-decomposition-grok43-high-reasoning-20260617T205352Z/snapshot-a623425c6db6a181`
- Project Model v1: `<repo>/.arena/runs/fmc-mcp-decomposition-grok43-high-reasoning-20260617T205352Z/snapshot-a623425c6db6a181/project-model-v1.json`
- Gate report: `<repo>/.arena/runs/fmc-mcp-decomposition-grok43-high-reasoning-20260617T205352Z/snapshot-a623425c6db6a181/gate-report.json`
- Manifest: `<repo>/.arena/runs/fmc-mcp-decomposition-grok43-high-reasoning-20260617T205352Z/snapshot-a623425c6db6a181/manifest.json`
- Raw model output: `<repo>/.arena/runs/fmc-mcp-decomposition-grok43-high-reasoning-20260617T205352Z/snapshot-a623425c6db6a181/model-outputs/decomposer.raw.json`
- Mechanical comparison JSON: `<repo>/reports/2026-06-17-fmc-mcp-grok43-high-vs-nonreasoning-comparison.json`
- Opus comparison review: `<repo>/reports/2026-06-17-fmc-mcp-grok43-high-vs-nonreasoning-opus-review.normalized.json`

## High-reasoning mechanical result

CLI/wrapper result:

```json
{
  "passed": false,
  "snapshot_id": "snapshot-a623425c6db6a181",
  "violation_count": 3
}
```

Gate violations:

```json
[
  {
    "gate": "cross_cutting_concerns",
    "message": "Missing universal concerns: anti_fabrication, determinism, no_live_paid_api_acceptance, provenance.",
    "severity": "error"
  },
  {
    "gate": "cross_cutting_concerns",
    "message": "Universal concern anti_fabrication does not cover components: comp:client, comp:config, comp:entry, comp:resources, comp:server, comp:tools.",
    "severity": "error"
  },
  {
    "gate": "cross_cutting_concerns",
    "message": "Universal concern provenance does not cover components: comp:client, comp:config, comp:entry, comp:resources, comp:server, comp:tools.",
    "severity": "error"
  }
]
```

Provider metadata from the high-reasoning manifest:

- Provider: `xai`
- Requested model: `grok-4.3`
- Served model: `grok-4.3`
- Served model matches requested: `true`
- Reasoning effort: `high`
- Finish reason: `stop`
- Prompt tokens: 7,560
- Visible completion tokens: 1,417
- Reasoning tokens: 7,897
- Total tokens: 16,874
- Exact cost ticks: 326,678,000
- Exact cost, using xAI tick scale: about `$0.0326678`

Target repo state after run:

```text
## main...origin/main [ahead 1]
```

Build Arena did not mutate `fmc-mcp`.

## Side-by-side comparison

| Axis | Previous non-reasoning | New Grok 4.3 high reasoning |
|---|---:|---:|
| Snapshot | `snapshot-ddb951deca8d5c7b` | `snapshot-a623425c6db6a181` |
| Gate passed | yes | no |
| Gate violations | 0 | 3 |
| Model | `grok-4.20-0309-non-reasoning` | `grok-4.3` + `reasoning_effort=high` |
| Reasoning tokens | 0 | 7,897 |
| Exact cost | about `$0.0189303` | about `$0.0326678` |
| Raw components | 7 | 6 |
| Raw contracts | 4 | 0 |
| Raw observable checks | 6 | 1 |
| Component profiles | 7 | 6 |
| Runtime contracts | 43 | 23 |
| External surfaces | 30 | 28 |
| Product invariants | 6 | 6 |
| Quality gates | 4 | 3 |
| Priority backlog | 5 | 5 |
| Open questions | 5 | 5 |

## What high reasoning improved

High reasoning fixed the biggest semantic annoyance in the previous result:

- `comp:client` is rank 1.
- The test suite is not rank 1.
- The previous `comp-tests` high-risk distortion is gone.
- The component ranking is more owner-useful: production client first, server second, entrypoint last.

High-reasoning component ranks:

1. `comp:client` — high risk
2. `comp:server` — high risk
3. `comp:config` — high risk
4. `comp:tools` — high risk
5. `comp:resources` — high risk
6. `comp:entry` — low risk

That is better than the previous non-reasoning ranking where `comp-tests` was rank 1/high-risk above the production client.

## What high reasoning broke or weakened

High reasoning failed the deterministic gate. That is the load-bearing result.

It also produced a thinner artifact:

- raw contracts dropped from 4 to 0;
- observable checks dropped from 6 to 1;
- runtime contracts dropped from 43 to 23;
- quality gates dropped from 4 to 3;
- pyright visibility disappeared from quality gates;
- external surfaces dropped from 30 to 28.

The raw high-reasoning output did include cross-cutting concerns named `anti_fabrication`, `determinism`, `provenance`, and `no_live_paid_api_acceptance`, and each listed the production components. But the deterministic gate still rejected the artifact as missing/undercovering universal concerns. The likely issue to inspect before another paid rerun is the exact ID/field/schema shape expected by the gate versus what Grok 4.3 emitted, especially the colon-style component IDs such as `comp:client`.

## Opus review

Opus review verdict: `MIXED`

Opus run verdicts:

- High reasoning: `FAIL_CLOSED`; gate failed with 3 cross-cutting-concern errors.
- Previous non-reasoning: `PASS`; gate passed with 0 violations, but had ranking distortion.

Opus picked `previous_non_reasoning` as better for next intake right now.

Opus summary:

> High-reasoning Grok 4.3 produced the better component ranking (production client at rank 1, no test-component distortion) but FAILED the deterministic cross_cutting_concerns gate with 3 errors and shipped a materially thinner, more expensive artifact. The previous non-reasoning run passed the gate cleanly and is richer, but ranks comp-tests #1 above the real client. Because the gate is fail-closed, the previous non-reasoning run is the only intake-ready artifact today; high-reasoning is the better model output but must be re-run to clear the gate before it can be promoted.

## My recommendation

Do not feed the high-reasoning artifact into intake.

Next best engineering move: inspect/fix the decomposition prompt or coercion/gate compatibility around universal cross-cutting concerns before another high-reasoning paid run. The ideal target is:

- keep high reasoning's production-client-first component ranking;
- preserve or improve the previous non-reasoning artifact richness;
- clear the deterministic gate.

If you want to proceed immediately without another decomposer fix, the previous non-reasoning artifact is the safer input because it passed the gate, but its `comp-tests` rank-1 distortion should be treated as a known advisory flaw before selecting work.

## Notes

One run-local wrapper attempt failed before any model call because the wrapper script was outside Python's import path. I fixed that by setting `PYTHONPATH=<repo>` and reran. The actual high-reasoning live run is the `20260617T205352Z` run above.
