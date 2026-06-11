# Opus Review — Project Intake First Slice Plan

Date: 2026-06-11
Model: opus via Claude CLI
Mode: read-only, no tools, budget cap $5

Verdict: `ACCEPT_WITH_CHANGES`

## Summary

The slice is well-scoped and correctly ordered: freshness (#19) feeds both the scorecard (#6) and the handoff packet, and the scorecard feeds the handoff, so the freshness -> scorecard -> handoff dependency chain is sound and deterministic. Protected surfaces are respected (schemas under docs/schemas/, not root schema/; new modules under arena/ but not arena/generated/; no scorer/verifier/lock edits), the scorecard stays correctly advisory and non-authorizing, and Elenchus is correctly deferred to a backlog issue only. The main gaps are under-specified deterministic contracts (priority formula, exit-code/status precedence), an incomplete prohibited-path set in the handoff packet, a thin test plan around read-only/determinism/no-live guarantees, and one hidden live risk in the pilot step (Project Model v1 snapshot generation against fmc-mcp).

## Required changes

- Specify the deterministic priorityScore formula explicitly (how severity, confidence, impact, effort, and profile weights combine) so test case 2 in Task 3 is reproducible; an undefined formula makes #6 non-deterministic and un-testable.
- Define an explicit exit-code-per-status and status-precedence contract for freshness. The plan only commits 'fresh -> 0' and 'unsafe for mutation -> non-zero', but does not say which of dirty-worktree / base-advanced / branch-diverged / snapshot-mismatch / unknown are non-zero, nor which status wins when multiple conditions hold (e.g. dirty worktree AND base advanced). Add a precedence table and test each mapping.
- Make the handoff packet's prohibitedPaths the full protected-surface set. The example omits .arena/scorer.lock.toml (and arguably should be sourced from a single canonical constant shared with the boundary docs) so it cannot drift from the real protected list.
- Add an explicit no-live / read-only guard for the Task 7 pilot: confirm that generating a fresh fmc-mcp Project Model v1 snapshot (when none exists) does not invoke paid/live providers. The plan defers to 'fixture/no-live mode' but does not assert that snapshot generation itself is non-live; this is the one place a live call could leak in.

## Recommended changes

- Clarify the aheadBehind contract under the 'no fetch by default' rule: values are computed against last-known local remote refs and may be stale; aheadBehind.available should be false when there is no upstream/remote tracking branch.
- Reproduce or pin the four profile weight vectors (across all eight dimensions) from the spec into the plan or a fixture, and fail Task 3 case 1 if the spec does not actually define complete weights for all four profiles.
- Consider narrowing the first slice to a core subset of the eight dimensions with the rest as explicit stubs; eight dimensions x four profiles x a full finding taxonomy is broad for a first slice, even if deterministic.
- Tighten Task 1 case 5: define a single deterministic mapping for graph/snapshot hash mismatch (snapshot-mismatch) rather than 'snapshot-mismatch OR warning', and state how it relates to the existing project_model_gate behavior.
- Avoid coupling the handoff writer into the scorecard CLI via --handoff-output unless needed; keeping proposer_handoff a standalone module/CLI preserves the clean intake/proposer boundary the deliverable is meant to make explicit.

## Missing tests

- Determinism/golden test: identical inputs produce stable (ideally byte-identical) JSON for all three artifacts; the plan states 'keep output stable' but never tests it.
- Read-only/no-mutation test: assert freshness, scorecard, and handoff never write into the target repo or any protected path, and only invoke read-only git/gh commands.
- Freshness output schema-validation test against project-model-freshness-v0 (scorecard and handoff have schema-validation tests, freshness does not).
- Exit-code-per-status tests for every freshness status, not just 'fresh -> 0'.
- aheadBehind-unavailable test (no upstream / no remote) returning available=false without error.
- Fail-closed test: missing git binary or unparseable git output maps to 'unknown' with warnings rather than raising.
- Handoff prohibited-paths completeness test asserting the full protected set (including .arena/scorer.lock.toml) is always present.
- No-live-provider assertion test for scorecard/handoff (e.g. patching the provider/transport layer and asserting it is never called).

## Scope risks

- Pilot step (Task 7) is the only place a live provider could be triggered, via fmc-mcp Project Model v1 snapshot generation; must be proven non-live before running.
- Eight dimensions plus four profiles plus a full finding taxonomy is a large surface for a 'first slice' and could expand mid-implementation; deterministic existence checks keep it bounded but finding-generator breadth is the likely scope-creep point.
- Priority formula and profile weights being under-specified risks the scorecard quietly becoming non-deterministic or being treated as a truth oracle if ranking logic grows.
- Optional --handoff-output coupling into the scorecard CLI slightly blurs the intake/proposer boundary the slice is trying to harden.

## Issue split feedback

Clean and non-overlapping. #19 (freshness/branch tracking) and #6 (weighted scorecard) are reused for matching scope rather than duplicated; the new 'proposer handoff packet schema' issue is a genuinely distinct artifact that does not overlap #6; and the Elenchus backlog issue is correctly isolated as advisory-only, post-slice, budgeted/cached, and explicitly not a scorer/verifier/gate/promoter. Recommend the handoff issue explicitly state its dependency on #19 and #6 and that it produces a non-authorizing packet (no runner mutation), to prevent it being mistaken for the mutation step.

## Final recommendation

Accept the plan and proceed, but patch in the four required changes before implementation: pin the deterministic priority formula, define the freshness exit-code/status-precedence contract, complete the handoff prohibited-path set, and add an explicit no-live guard around the pilot snapshot generation. Strengthen the test plan with determinism, read-only, freshness-schema, and no-live-provider tests. The ordering (freshness -> scorecard -> handoff), the advisory-only scorecard stance, the protected-surface handling, and the Elenchus deferral are all correct as written.
