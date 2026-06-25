# Dream Proposer functional run handoff — 2026-06-24

Status: A1 fake-model plumbing run passed; A2 live product proof blocked on operator decisions.
Baseline target: `build-arena` `main` at `2c6f6cb64ad987b772ccb684d4a67cb0d6987793`.
Scope: run-and-map only. No dream-lane source edits.

## Deliverables

- Run/review/calibration report: `docs/verification/2026-06-24-dream-proposer-functional-run.md`
- Run-grounded flow diagram: `docs/verification/2026-06-24-dream-proposer-functional-run-flow.mmd`
- A1 rendered dream markdown: `docs/verification/dream-proposer-functional-run-a1/dream.md`
- A1 gated `dream/v0` artifact: `docs/verification/dream-proposer-functional-run-a1/gated-dreams.json`
- A1 gate trace: `docs/verification/dream-proposer-functional-run-a1/dream-gate-trace.json`

## Handoff summary

A1 produced a real `dream.md` through the dream-lane modules with no source change. It is a plumbing proof, not a live product proof. The run used the already-exposed fake/injected model seams for `dream_generate` and `dream_research` via a throwaway driver because the public CLIs for those stages do not expose fixture-model arguments.

Gate result:

- accepted: `dream.a1.carrier-survives`
- killed: `dream.a1.function-killed`
- kill reason: `citedEvidence[0] contentHash mismatch for component component.arena-runners`

A2 was not run. Required operator decisions:

1. live credentials/spend approval;
2. real operator review of `capability-map.json` before A2.

## Calibration verdict

No: the current adjustable surfaces are enough to run and manually steer output, but not enough for disciplined quality refinement from live runs. The fabrication-control surfaces mainly change what survives; the quality surfaces are mostly prompt/model/capability-map edits without an outcome ledger. The single minimum missing piece is a structured dream outcome/quality ledger for live runs.

See `docs/verification/2026-06-24-dream-proposer-functional-run.md` for raw evidence, six-module review, full calibration map, independent Opus review result, and verification commands.
