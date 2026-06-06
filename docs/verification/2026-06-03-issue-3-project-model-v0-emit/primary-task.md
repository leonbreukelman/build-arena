# Issue #3: Emit Project Model v0 from primary tasks before planning or architecture work

## Purpose

Implement the Build Arena side of Project Model v0.

Build Arena's role is to turn a primary task/backlog item into a mechanically checkable Project Model before planning, architecture selection, or code work begins.

Parent coordination issue: https://github.com/leonbreukelman/build-arena/issues/2

## Agent role

You are the Build Arena implementation agent.

Your job is to emit the Project Model. Do not implement Elenchus evaluation logic here, and do not build the arena-calibration fixture harness here.

## Agent instructions

1. Read the parent Project Model v0 contract first.
2. Inspect the existing deterministic decomposer path, especially the README's Phase 5 notes and any `arena.decomposer` implementation.
3. Update or implement the decomposer so a primary task/backlog item can produce a Project Model v0 document.
4. Keep the implementation deterministic and local-first. Do not require live paid LLM/API calls for tests.
5. Add validation for the Project Model quality gate:
   - every component has a responsibility;
   - every component has at least one observable/measurable check;
   - dependencies are explicit and non-contradictory;
   - invariants are represented separately from ordinary goals;
   - verification gaps are surfaced rather than hidden;
   - unclassified project surfaces are reported.
6. Preserve the distinction between ownership accounting and quality scoring. Build Arena may say "this surface is covered/missing"; Elenchus/arena-calibration decide whether a proposal's rationale aligns.
7. Add or update CLI/API behavior so callers can request Project Model v0 in canonical JSON.

## Expected output shape

The emitted model should include, at minimum:

- `schemaVersion`
- `sourceTask`
- `goal`
- `nonGoals`
- `components`
- `dependencies`
- `invariants`
- `observableChecks`
- `evidenceRequirements`
- `assumptions`
- `risks`
- `nearNeighbors`
- `heldOutProbes`
- `verificationGaps`
- `unclassifiedProjectSurface`

## Acceptance criteria

- [ ] A primary task can be converted into Project Model v0 JSON.
- [ ] The JSON validates against the parent contract.
- [ ] `--fail-on-gap` or equivalent behavior fails/flags missing checks, missing components, and unclassified project surface.
- [ ] At least one non-code task example is covered, not only code-patch examples.
- [ ] Tests prove the decomposer catches a shallow/vague decomposition as a quality-gate failure.
- [ ] Existing deterministic behavior and current green gates are preserved.
- [ ] README/docs explain how `elenchus-core` and `arena-calibration` should consume the emitted model.

## Non-goals

- Do not score proposal truth or optimality.
- Do not add live-provider dependency for acceptance.
- Do not implement the Elenchus advisory signal protocol beyond producing the model it consumes.
- Do not treat F3 as only a code-patch/generalization problem.
