# Fable Sign-off — Project Intake Issues #6/#19/#20/#21

Date: 2026-06-11
Model: fable via Claude CLI
Mode: read-only, no tools, budget cap $5

Overall verdict: `SIGN_OFF`

## Per-issue verdicts

### Issue #6

- Verdict: `SIGN_OFF`
- Close recommendation: `close_completed`
- Reason: The weighted project-intake scorecard is implemented as specified: all four profile weight vectors are pinned across all eight dimensions and locked in tests, the deterministic priorityScore formula matches the plan (weight x severity x confidence x summed gains / effort) with the full five-level tie-break order, output is advisory-only with an explicit non-authorization flag, a sidecar JSON schema exists and is validated in tests, and the hardening pass added the two guarantees that were previously missing: a no-write-to-target-repo test and a no-live-provider source check. Determinism, CLI, and markdown output are all covered by passing tests, and the full suite, ruff, and pyright pass.

### Issue #19

- Verdict: `SIGN_OFF`
- Close recommendation: `close_completed`
- Reason: The freshness contract is now complete and fail-closed. Status precedence matches the documented table (snapshot-mismatch > dirty-worktree > branch-diverged > base-advanced > unknown > fresh), every non-fresh status exits 2 with schema-valid JSON, safeForMutation is true only for fresh, and the hardening pass closed the two real gaps from the prior round: missing git binary now fails closed to unknown with a warning (tested), and a no-write-to-target-repo test exists. The ahead/behind computation now correctly uses the detected remote name rather than hardcoded origin, still with no fetch or network refresh, and aheadBehind.available=false is asserted when no remote tracking ref exists. gh remains optional enrichment with availability flagged rather than failing.

### Issue #20

- Verdict: `SIGN_OFF`
- Close recommendation: `close_completed`
- Reason: The proposer handoff packet is implemented as a standalone module and CLI without coupling into the scorecard, preserving the intake/proposer boundary. prohibitedPaths is sourced from the canonical arena.boundary constants rather than a local copy, and the hardening pass added literal assertions for the full protected set including .arena/scorer.lock.toml, so drift between the constant and policy is now visible in tests. notAuthorizedForMutation is hard-pinned (const true in the schema and a default-true dataclass field), non-fresh freshness adds an explicit blocking advisory note, missing verification commands force requiresOwnerApproval, and the no-live-provider/runner source check covers arena.loop and transport tokens. Schema validation, determinism, and CLI tests all pass.

### Issue #21

- Verdict: `SIGN_OFF`
- Close recommendation: `keep_open`
- Reason: Elenchus is correctly and deliberately not implemented in this slice, which matches both the owner's instruction to leave it as backlog and the Opus-reviewed plan that defers it as a post-slice advisory critique. Nothing in this diff partially implements or forecloses it, and no code falsely claims it exists. Because the issue's scope is genuinely future work that the owner still intends, it should remain open as the backlog tracker rather than being closed as completed or not-planned. Sign-off here is on the deferral decision, not on closure.

## Must-fix before close

- None.

## Final summary

All previously identified hardening gaps are resolved: literal protected-path assertions including .arena/scorer.lock.toml, fail-closed missing-git handling, no-write-to-target-repo tests for both freshness and scorecard, no-live-provider source checks for scorecard and handoff, and remote-name detection replacing the hardcoded origin without introducing any fetch/network behavior. Verification is comprehensive and green (23 targeted tests, full suite, ruff, pyright, CLI help checks, git diff --check, clean secret scan), no protected surfaces are touched, and all three artifacts remain deterministic, read-only, and explicitly non-authorizing. Issues #6, #19, and #20 are complete and safe to close as completed. Issue #21 (Elenchus) is correctly deferred per owner direction and should remain open as the backlog item; do not close it.
