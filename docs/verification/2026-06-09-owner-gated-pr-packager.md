# Build Arena BA-M3-06 Owner-Gated PR Packager Evidence

Date: 2026-06-10T06:16:42Z
Kanban card: `t_95049964` — BA-M3-06 Phase 4: Add owner-gated PR packager
Branch: `ba/m3-owner-gated-pr-packager`

## Scope completed

- Added `arena/pr_packager.py`.
- Added CLI entrypoint `arena/package_pr.py` for `python -m arena.package_pr`.
- Added `tests/test_pr_packaging.py`.

## Behavior implemented

### Dry-run PR body rendering

- `package_candidate_pr(..., dry_run=True)` renders a PR body and executes no commands.
- CLI defaults to dry-run unless `--open-pr` is explicitly supplied.
- Dry-run output states that no `git push`, `gh pr create`, or merge was executed.

### Traceable claims only

- `render_pr_body(evidence_path, extra_claims=())` accepts only `cycle-evidence/v1` with a candidate record.
- PR body claims are generated from `TraceableClaim(text, pointer)` values and include JSON pointers back to the evidence file:
  - candidate branch and commit;
  - verdict outcome and score delta;
  - score-after composite;
  - tests-passed state;
  - patch line counts and touched files.
- Fabricated/untraceable extra claims raise `FabricatedClaimError`.

### Operator-gated publishing

- Non-dry-run packaging requires `allow_gh=True`; otherwise it raises `OperatorAuthorizationError` before executing commands.
- Authorized mode pushes `candidate_branch:arena/pr/<cycle_id>` and then calls `gh pr create`.
- No automatic merge command exists in the path.
- Remote safety rejects a target repo whose selected remote URL equals Build Arena's selected remote URL unless the target repo path is the Build Arena repo path.

### Owner outcome ledger feedback

- `record_owner_outcome(...)` appends `OWNER_MERGED` or `OWNER_REJECTED` rows with fingerprint, hypothesis, cycle, and optional PR URL.

## TDD evidence

- Tests were written before implementation.
- RED run failed with `No module named 'arena.pr_packager'`.
- Implementation followed and tests passed.

## Verification completed

- `uv run pytest tests/test_pr_packaging.py tests/test_worktree_cycle_evidence.py tests/test_failure_ledger.py -q` — passed.
- `uv run pytest tests -q` — passed.
- `uv run ruff check .` — passed.
- `uv run pyright` — passed: `0 errors, 0 warnings`.
- `git diff --check` — passed.
- New-file whitespace checks for `arena/pr_packager.py`, `arena/package_pr.py`, and `tests/test_pr_packaging.py` — passed.

## Fable review

Verdict: `ACCEPT`.

### Review transcript

VERDICT: ACCEPT

critical_blockers: None. All hard requirements from the card are satisfied with test evidence: dry-run renders without executing commands, non-dry-run fails closed on missing `allow_gh`, fabricated/untraceable claims raise `FabricatedClaimError` (with a failing fixture), no merge command exists in the execution path, packaging is operator-invoked rather than loop-internal, and owner merge/reject outcomes append to the ledger. TDD ordering is evidenced (RED on missing module), full suite, ruff, and pyright are green.

required_changes_before_completion: None for closing the card. Two hardening items to track before the first **live** (non-dry-run) use, as follow-ups rather than blockers since dry-run is the mechanical gate here:

1. Remote URL comparison should normalize before comparing. A literal string compare of `remote.<remote>.url` will not catch the same repo referenced via different forms (`git@github.com:owner/repo.git` vs `https://github.com/owner/repo` vs trailing-`.git` variants). Normalize host/owner/repo before the equality check so the "never the Build Arena remote" guarantee holds across URL schemes.
2. Confirm the CLI live path requires an explicit affirmative flag (e.g. `--push --allow-gh`) rather than merely the absence of `--dry-run`, and that this is covered by a test asserting the CLI defaults to dry-run.

guidance_as_leon_representative: This is the right shape for the trust boundary: the machine produces a byte-traceable artifact, the human authorizes publication, and the outcome flows back into the ledger as ground truth. Keep that asymmetry sacred — every claim in a PR body must point at evidence, and the loop must never gain the ability to publish on its own. When you commit, include the evidence artifact for this cycle as usual, and note the two hardening follow-ups on the board so they're not lost before the first live push against a pilot repo.

next_cards_to_claim_or_continue: After committing and recording the evidence artifact, claim the next critical-path M3 card: the end-to-end orchestrator that wires picker → proposer → worktree cycle → scorer → evidence → (operator-gated) packager into a single runnable arena cycle, since every component it depends on is now built. If that card doesn't exist yet on the board, the close second is the outcome-feedback card — feeding `OWNER_MERGED`/`OWNER_REJECTED` ledger rows back into target picking/scoring — followed by the live-push hardening items above as a small card of their own.

## Non-blocking follow-ups noted by Fable

These are not blockers for BA-M3-06, but should be tracked before first live non-dry-run use:

1. Normalize remote URLs before comparing Build Arena and target remotes, so equivalent HTTPS/SSH/trailing-`.git` forms are caught.
2. Add/keep a CLI-level test asserting live mode requires an explicit affirmative flag and defaults to dry-run.
