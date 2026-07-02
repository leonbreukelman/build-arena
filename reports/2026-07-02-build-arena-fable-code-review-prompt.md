# Claude Code Fable read-only code review request

You are reviewing a sanitized tracked-file snapshot of the Build Arena repository. The snapshot was created with `git archive HEAD`, so it contains tracked files only and no local `.git`, `.env`, or untracked operator artifacts.

Snapshot root available to you through `--add-dir`:
`/tmp/build-arena-fable-review-j5sNZW`

Current repo posture from the live checkout:
- Branch: `docs/reframe-agents-status-guards`
- Untracked operator artifacts exist in `reports/2026-06-28-*`; ignore them because they are not in the snapshot.
- Recent local checks before this review:
  - `uv run ruff check .` -> `All checks passed!`
  - `uv run pyright` -> `0 errors, 0 warnings, 0 informations`

Governing project facts to enforce during review:
- Build Arena is propose-only. No entrypoint may apply, promote, auto-merge, or mutate a target repository.
- Retired roots must remain absent: `arena.repo_goal_loop`, `arena.patch_gate`, `arena.runners.diff_proposer`, `arena.proposal_candidate_runner`.
- `scorer/`, `verifier/`, `schema/`, `.arena/scorer.lock.toml`, and `arena/generated/` are sensitive/read-only surfaces for arena-generated hypotheses.
- `arena.proposal_run` emits `proposal.md` only; `arena.dream_run` emits `experiment.md` only.
- Live provider paths require explicit `--allow-live` and explicit `--live-model`; served-model mismatch should fail closed.
- Deterministic no-API verifier/ablation stand-in is only a coherence check, not a live semantic gate.
- Broad autonomous live loops are not ready while readiness blockers remain.

Your task:
Perform a code review and architecture analysis focused on:
1. Any code path that appears to violate or weaken the propose-only boundary.
2. Any live-provider/spend/auth path that can run without explicit operator intent or fails open.
3. Any stale-cache/stale-artifact issue where cached projections could be treated as authoritative filesystem/git truth.
4. Any generated/schema/scorer/verifier boundary risks.
5. High-value maintainability or correctness issues in the intake -> proposal/dream pipeline.
6. Test gaps that would let the above regressions slip.

Use only read-only inspection. Do not edit files. If you run shell commands, use only read-only commands inside `/tmp/build-arena-fable-review-j5sNZW`.

Return a concise but concrete report in this structure:

VERDICT: ACCEPT | ACCEPT_WITH_FINDINGS | REQUEST_CHANGES
MODEL_NOTE: state you are Claude Code Fable if that is the model actually running.
SCOPE_CAVEAT: mention that this is a tracked-file snapshot review, not a live worktree mutation review.
TOP_FINDINGS:
- For each finding: severity (critical/high/medium/low), file:line if possible, evidence, why it matters, and suggested fix/test.
BOUNDARY_ASSESSMENT:
- Explicit assessment of propose-only, live-provider gates, and sensitive generated/scorer/verifier/schema boundaries.
TEST_GAPS:
- Concrete missing or weak tests.
POSITIVE_SIGNALS:
- Brief list of existing safeguards that are visible in code/tests.
NEXT_STEPS:
- Prioritized patch list, no more than 7 items.

Be skeptical. Prefer fewer, well-evidenced findings over broad speculation. If you cannot prove a suspected issue from files, label it as `needs follow-up`, not a finding.