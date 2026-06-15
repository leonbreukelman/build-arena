# Coding Agent Prompt — Implement Build Arena's Frozen Onboarding Cycle

Paste everything below the line into the coding agent (run the implementer on a fast
model, e.g. Sonnet). The Opus checkpoints define WHEN and WHAT to escalate; wire the
model switch on your side (switch to Opus for the review turn, or run the emitted
review packet in a separate Opus session).

---

You are implementing one component of the `build-arena` repository: a reliable,
deterministic onboarding cycle that decomposes a target repo into a Project Model.
Work in small, tested, committed steps. Be terse. Report what you VERIFIED versus
what you ASSUMED at each step.

## What you are given (frozen — do not edit to pass)

- `docs/schemas/project-model.frozen-v1.json` — the model contract.
- `tests/test_onboarding_acceptance.py` — the acceptance test (the ruler).
- `IMPLEMENTATION_PLAN.md` — the phased plan. Follow its phase order.

Your job is to make the acceptance test green by building `arena/onboard.py`. You may
ADD assertions/tests; you may NOT weaken the schema or the acceptance test.

## Definition of done (the only success condition)

1. `tests/test_onboarding_acceptance.py` green against the `arena-calibration` checkout
   at `$ARENA_CALIBRATION_PATH`.
2. `arena/repo_goal_loop.py` consumes the new model and completes a dry-run cycle on
   arena-calibration with a deterministic ranked finding list.
3. `ruff check .`, `pyright`, `uv run pytest -q` all green.
4. Nothing else added. If your change is not traceable to one of these lines, stop.

## Hard rules (violating any is an immediate STOP → Opus)

- **Deterministic, offline, no LLM in the producer.** Build from `git ls-files` +
  file contents only. No timestamps, RNG, network, or set-iteration-order leakage.
  Same HEAD in → byte-identical model out.
- **Anti-fabrication.** Read a path in the current step before asserting it exists or
  quoting it. Every node/component/gap id must reference something real.
- **Boundaries.** Do NOT modify or import `arena/decomposer.py`,
  `arena/project_decomposer_ai.py`, `arena/project_meta_decomposer.py`. Do NOT touch
  `scorer/`, `verifier/`, `schema/`, `.arena/scorer.lock.toml`.
- **One module:** all logic in `arena/onboard.py`, entrypoint
  `decompose_project(project_path: str) -> dict`. No new package.
- **`additionalProperties:false`:** emit EXACTLY the contract's fields. Scratch/debug
  data goes in a separate file, never in the model.

## The consumer contract you must satisfy (do not rename)

`arena/project_intake_scorecard.py` reads, and your model must populate:
`snapshot.components[].{id,name,owned_node_ids,check_ids}`,
`snapshot.observable_checks[].{id,command,component_ids}`,
`snapshot.verification_gaps[].{id,kind,componentId,path,description}`,
`snapshot.unclassified_node_ids`,
`projectGraph.nodes[].{id,path,kind}`,
`iterationReadiness.componentProfiles[].{componentId,riskLevel,provenanceRefs}`,
`iterationReadiness.qualityGates[].{command}`,
`iterationReadiness.openQuestions[]`,
`provenance.git.headOid`, `id`.

## riskLevel rule (transparent, not inferred by you)

`high` = component owns ≥1 `.py` node and has zero `check_ids`. `low` = covered by ≥1
check OR non-executable (docs/config/fixtures). `medium` = otherwise.

## Confidence + Opus escalation protocol

At every design decision and every phase boundary, state a confidence score 0.0–1.0.
**STOP immediately and emit an `### OPUS REVIEW REQUEST` (do not proceed) when ANY
trigger fires:**

- confidence < 0.7 on a design choice;
- the same test fails twice after an attempted fix;
- you are about to add a field, module, dependency, or artifact not in the schema/plan;
- you are about to introduce anything non-deterministic (time, randomness, order-dependent output);
- you are about to touch or import a boundary/quarantined path;
- the arena-calibration fixture's reality contradicts the plan (e.g. the F3 manifest
  format or field name differs from what the plan assumed).

An `OPUS REVIEW REQUEST` contains, tersely: (a) the exact decision or unified diff,
(b) why you are uncertain / which trigger fired, (c) the one specific question you need
answered, (d) the relevant test output. Then yield. Do not guess past it.

**Two mandatory Opus checkpoints regardless of confidence:**

- **Checkpoint A — before any implementation (after Phase 0).** Opus verifies the
  ruler discriminates: confirm the acceptance test FAILS on a deliberately empty,
  degenerate, and fabricated model, and PASSES on a hand-built correct one. If the
  ruler passes garbage, fix the ruler before writing the producer.
- **Checkpoint B — after Phase 5.** Opus verifies the implementation against the
  acceptance test, hunts determinism traps and fabrication, and greps `arena/onboard.py`
  for any `decomposer` import or boundary violation.

## Workflow per phase

1. State the phase and your plan in 2–3 lines + a confidence score.
2. If a trigger fires, emit an OPUS REVIEW REQUEST and yield.
3. Otherwise implement the smallest change for that phase.
4. Run the phase's unit tests, then `ruff`, `pyright`, and the acceptance test.
5. If green, commit with a one-line message and report verified-vs-assumed. If red
   after two fix attempts, STOP → Opus.

Begin with Phase 0: place nothing new yet — confirm the schema and acceptance test are
present, run the acceptance test, and report exactly why it is red. Then request Opus
Checkpoint A.
