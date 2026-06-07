# Opus spec/plan review disposition

Date: 2026-06-07
Review artifact: `opus-spec-plan-review.md`

## Verdict

Opus returned `approve_with_required_changes`. All three required changes were accepted and patched before implementation.

## Required changes accepted

1. Schema/versioning contradiction resolved. `iterationReadiness` is optional in the JSON schema for legacy v1 reproducibility, but newly generated artifacts from this implementation must emit it and tests assert that.
2. Evidence model clarified. Inferred runtime contracts, product invariants, and external surfaces may use source-span provenance when no graph call edge exists; they must not pretend to be graph call edges and are separate from import-edge coverage.
3. Objective predicates added. Non-tautological responsibilities require source-derived symbols/tags and reject module-name-only templates; open questions must tie to named source or absent-verification signals and use deterministic ordering.

## Non-blocking suggestions accepted

- Deterministic ranking/question ordering is now explicit.
- `FMCClient.test_connection` naming smell and server-to-tools indirection are added to the plan as backlog/open-question/delegation outputs when source-supported.

## Rejected feedback

None.
