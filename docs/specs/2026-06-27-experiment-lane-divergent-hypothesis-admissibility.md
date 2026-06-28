# Experiment Lane — Divergent-Hypothesis Admissibility

Date: 2026-06-27
Status: implemented by `dream/v1` contract and frozen fixture suite

## Goal

The dream lane must emit divergent architectural hypotheses, not restatements of current state. A dream is admissible only when it:

1. cites a resolvable tension-bearing anchor;
2. names an explicit current -> proposed structural delta;
3. predicts a falsifiable measurable effect on a named metric or fitness function; and
4. remains an experiment-lane structural hypothesis rather than a single-file proposal-lane fix.

## Contract

`dream/v1` adds:

- `currentStructure`
- `proposedStructure`

Mode-specific discriminator:

- `carrier_swap`: `currentStructure.fromCarrier != proposedStructure.toCarrier`
- `function_remap`: `currentStructure.fromBinding != proposedStructure.toBinding`

`validationRecipe.expectedDirection` is restricted to:

- `decrease`
- `increase`
- `passes`

`unchanged` and legacy `tests_pass` are not admissible directions.

## Tension-bearing anchors

The deterministic admissibility check treats these anchor kinds as tension-bearing:

- `verificationGap`
- `priorityBacklog`
- `productInvariant` when enforcement is non-modeled or linked from a priority backlog item
- `graphStructural` computed anchors, including high fan-in nodes, multi-tag components, and simple import-cycle pairs

A capability anchor can still resolve as a premise, but capability-only evidence is not a cited tension and is inadmissible.

## Frozen fixtures

The regression suite commits the captured fmc-mcp restatements from the live run as:

- `tests/fixtures/dream_admissibility/captured-restatement-dreams-v0.json`

The captured input surface used for replay is committed as a sanitized minimal fixture set:

- `tests/fixtures/dream_admissibility/captured-project-model-v1.json`
- `tests/fixtures/dream_admissibility/captured-capability-map.json`
- `tests/fixtures/dream_admissibility/captured-scorecard.json`

The positive hand-authored divergent fixture is:

- `tests/fixtures/dream_admissibility/positive-divergent-dreams-v1.json`

## Done rule

Done means all of the following are true under tests and CI:

1. captured `dream-1` and `dream-2` are rejected, with requirement-2 structural-delta failure recorded;
2. the positive divergent fixture is accepted;
3. replaying the captured inputs through generate -> research with injected offline model callables yields at least one dream that passes the admissibility check; and
4. the lane gate kills inadmissible dreams before `experiment.md` emission.

`experiment.md` existing is not enough. A premise-resolving gate accept is not enough. The admissibility check is the load-bearing evidence.

## Verification commands

```bash
uv run pytest tests/test_dream_admissibility.py tests/test_dream_generate.py tests/test_dream_research.py tests/test_dream_gate.py tests/test_dream_emit.py tests/test_dream_run.py -q
uv run pytest tests -q
uv run ruff check .
uv run pyright
make generated
```

## Known boundary

The check proves shape, not truth or value. It verifies cited tension, explicit structural delta, measurable observable, and experiment-lane divergence. Whether the hypothesis is worth acting on remains downstream: attempt the mutation, measure the declared observable, and record the verdict.
