# Fable Review — Build Arena Milestone 3 Phase 0

Date: 2026-06-10T04:12Z
Model: claude-fable-5 via Claude Code CLI
Mode: read-only/no-tools prompt review

VERDICT: ACCEPT_WITH_CHANGES

```json
{
  "verdict": "ACCEPT_WITH_CHANGES",
  "critical_blockers": [],
  "required_changes_before_phase0_completion": [
    "Reconcile register step 4: its status string still says 'blocked_until_build_arena_v1_consumer_and_gap_policy_enforcement', but GAP-001 now has blocksDryRunHypothesisGeneration=false. Either GAP-001 keeps blocking dry-run or the step-4 status wording drops gap-policy; pick one source of truth so the register doesn't contradict itself on day one.",
    "Record explicitly in the Phase 0 evidence artifact that PMV1-002/003 also had blocksPromotionMerge flipped to false. The stated decision covered dry-run/worktree scoping; the promotion flip is defensible (promotion stays blocked via LIVE-002, GRAPH-001, GAP-001, M3-001) but it is a wider change than the decision log claims and must be visible, not incidental.",
    "M3-001's proofCommand is prose ('Complete BA-M3-01 through BA-M3-04...'), not a command, in a register where proofCommand is meant to be mechanical. Either rename/annotate it as a closure criterion or give it a mechanical form (e.g. the test files that must exist and pass). Also verify the 'BA-M3-05/07' card reference is real and not a typo for BA-M3-05/06."
  ],
  "guidance_as_leon_representative": "The Phase 0 policy direction is correct and is exactly the correction I asked for: stop gating Build Arena's own smallest loop on ecosystem adoption it doesn't control. Specifically: (1) No over-unblocking detected — overallStatus stays not_ready_blockers_remain, promotion remains blocked by four independent items, dry-run-from-v1 remains blocked, and the only thing that opened is a narrower path that immediately re-closes behind M3-001 (severity critical, blocksWorktreeOnlyPatchCycle=true). Net effect: nothing is runnable today that wasn't runnable yesterday. (2) Removing PMV1 cross-repo adoption as a blocker for naive cycles is right — related-repo v1 adoption was never a logical prerequisite for build-arena proposing a bounded diff in its own worktree; it was scope creep acting as a safety blanket. (3) M3-001 is the right replacement blocker because its three criteria (generic scorer, fail-closed proposer tests, per-repo boundary config) are the actual safety properties the PMV1 blockers were standing in for. (4) Pilot/worktree-root choices are sound: fmc-mcp is small, clean, remoted, and tested; the worktree root matches the existing AGENTS write-boundary rule and keeps the pilot repo's before/after git-status audit clean. The pytest console-script workaround is honestly documented rather than papered over — good; Phase 1 must pin those test deps in the pilot goal config rather than relying on ad-hoc --with flags. One standing caution: the docs now declare the ablation keyword gate advisory ahead of the code change (ablation_advisory lands in Phase 3, default False). That's acceptable only because M3-001 blocks all pilot cycles until then — do not let any cycle run under the doc-level 'advisory' claim before the code flag exists.",
  "next_card_after_phase0_if_accepted": {
    "card": "t_d099446a",
    "reason": "BA-M3-01 (goal.toml schema/loader) is the only Phase 1 entry point, is explicitly marked safe to delegate after Phase 0, and both Phase 2 cards (t_c3ad0d70, t_eeafe5ff) depend on its contract."
  }
}
```

Summary for Hermes: the governance change is accepted in direction — the three required changes are register-consistency fixes, not policy reversals, and all are doc/JSON edits within Phase 0's existing scope. Fix them, re-run the same mechanical proofs (`python3 -m json.tool`, the blocker scan, `git diff --check`, the status-docs test), then close t_6ff0635f and unblock t_d099446a only. Downstream cards stay blocked, and no live provider calls or code-path changes are authorized by this acceptance.
