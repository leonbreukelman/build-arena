# Build Arena BA-M3-07 Pilot Cycle Evidence

Date: 2026-06-10
Kanban card: `t_5d7abe71` — BA-M3-07 Milestone gate: Run pilot cycles and produce owner-gated PR evidence
Branch: `ba/m3-pilot-acceptance-run`
Pilot repository: `/home/leonb/projects/fmc-mcp`
Isolated pilot clone: `/tmp/build-arena-m3-07/fmc-mcp-pilot`
Configured worktree root: `/tmp/build-arena-m3-07/worktrees`

## Result

BA-M3-07 pilot proof passed after fixing a candidate-packager `.arena/` artifact-isolation bug discovered by the run.

## Acceptance gate evidence

- At least 5 cycles run within budget: `5` cycles.
- At least 1 candidate passes mechanical gates: `5` candidates promoted.
- Candidate branches produced: `arena/candidate/cycle-1, arena/candidate/cycle-2, arena/candidate/cycle-3, arena/candidate/cycle-4, arena/candidate/cycle-5`.
- Zero writes to canonical pilot checkout: before and after status/head matched exactly:
  - before: `{'head': '00a632ac950a8c411f8d8ac90197e28191f58619', 'status': '## main...origin/main'}`
  - after: `{'head': '00a632ac950a8c411f8d8ac90197e28191f58619', 'status': '## main...origin/main'}`
- Configured worktree root empty after teardown: `[]`.
- Every reject maps to a `RejectReason` and transcript: reject ledger contains `[{'cycle_id': 'cycle-1', 'fingerprint_id': 'fe58dbc059b7c0abd3ea42d1c7728fae', 'hypothesis_id': 'hyp-cycle-1-3b6d0436cb04', 'outcome': 'DISCARDED', 'reject_reason': 'RUNNER_ERROR'}]` and reject evidence is saved under `reject-evidence/`.
- Injected budget breach produced halt: `BUDGET_EXHAUSTED_ZERO_PROMOTIONS`.
- Injected divergence halt produced halt: `BOUNDARY_VIOLATION_ATTEMPT`.
- Budget config is recorded in every cycle/halt evidence JSON.
- Two dry-run PR bodies rendered with byte-traceable claims:
  - `/tmp/build-arena-m3-07/pr-bodies/cycle-1.md` copied to `pr-bodies/cycle-1.md`
  - `/tmp/build-arena-m3-07/pr-bodies/cycle-2.md` copied to `pr-bodies/cycle-2.md`
- Live push/open PR was intentionally not executed.
- No autonomous merge occurred.

## Candidate branch diff audit

The first two candidate branch diffs touch only target repo tests:

```text
## arena/candidate/cycle-1
 tests/test_client.py    | 172 ++++++++++++++++++++++++++++++++++++++++++++++++
 tests/test_resources.py |   3 +-
 tests/test_server.py    | 102 ++++++++++++++++++++++++++++
 3 files changed, 276 insertions(+), 1 deletion(-)

M	tests/test_client.py
M	tests/test_resources.py
A	tests/test_server.py

## arena/candidate/cycle-2
 tests/test_client.py    | 172 ++++++++++++++++++++++++++++++++++++++++++++++++
 tests/test_resources.py |   3 +-
 tests/test_server.py    | 102 ++++++++++++++++++++++++++++
 3 files changed, 276 insertions(+), 1 deletion(-)

M	tests/test_client.py
M	tests/test_resources.py
A	tests/test_server.py

```

No `.arena/` evidence/config/runtime artifacts are present in candidate branch diffs. Patch/provenance files remain evidence-only through the `patch.path` + `patch.sha256` fields in cycle evidence.

## Score proof

Baseline score vector:

```json
{
  "composite": 144.519508,
  "coverage_pct": 74.731183,
  "cyclomatic_avg": 1.942857,
  "pyright_errors": 2,
  "ruff_violations": 0,
  "runtime_p95_ms": 10.0,
  "tests_pass": true
}
```

Promoted candidate cycle evidence records `score_delta: 25.854327`, with coverage lifted above the hard pinned floor and pyright errors reduced to zero by the candidate patch.

## Durable artifacts

- `summary.json` — machine-readable run summary.
- `run_pilot.py.txt` — exact harness used for this proof run.
- `candidate.patch.json` — static candidate diff applied by the fake transport, JSON-wrapped to keep repo whitespace checks meaningful.
- `evidence/cycle-1.json` through `evidence/cycle-5.json` — candidate cycle evidence.
- `reject-evidence/cycle-1.json` — intentional reject evidence.
- `halt-evidence/` — budget and divergence halt evidence.
- `pr-bodies/cycle-1.md` and `pr-bodies/cycle-2.md` — dry-run PR bodies.
- `candidate-branch-diffs.txt` — audited candidate branch diffs.

## Implementation bug fixed during pilot

The pilot exposed that `CandidatePackager` could add `.arena/` evidence/config/runtime files to candidate branches because it used `git add -A` after the diff proposer restored patch artifacts for evidence hashing. A regression test was added and `CandidatePackager` now unstages all `.arena/` paths before candidate commits while preserving files in the worktree for the evidence writer.

## Fable review

Initial Fable verdict: `ACCEPT_WITH_CHANGES`.

Required change applied after review:

- Widened candidate-branch artifact exclusion from `.arena/patches/` to all `.arena/` paths.
- Re-ran targeted packager/worktree tests, full suite, ruff, pyright, artifact checks, and the pilot after the fix.

Review transcript:

VERDICT: ACCEPT_WITH_CHANGES

**critical_blockers**

None. All eight acceptance gates have direct, machine-readable evidence: 5 cycles with 5 promotions, before/after head and status identical on the canonical checkout, empty worktree root after teardown, RUNNER_ERROR reject in the ledger with reject-evidence, both injected halts (BUDGET_EXHAUSTED_ZERO_PROMOTIONS, BOUNDARY_VIOLATION_ATTEMPT), budget config in every evidence JSON, two dry-run PR bodies, no live push, no merge. The fake-transport candidate is explicitly within scope for this card — it proves cycle mechanics, not patch generation. Discovering and regression-testing the `git add -A` artifact-leak bug during the pilot is exactly what a milestone gate is for; that strengthens the close rather than weakening it.

**required_changes_before_completion**

1. **Commit the work.** The packager fix, the regression test, and the entire `docs/verification/2026-06-10-m3-pilot/` evidence tree are currently uncommitted on `ba/m3-pilot-acceptance-run`. Evidence that lives only in the working tree (and `/tmp`) doesn't satisfy an evidence-gated milestone. Verify the durable copies in `docs/verification/` actually contain the artifacts the report references (summary.json, evidence/, halt-evidence/, reject-evidence/, pr-bodies/, candidate-branch-diffs.txt, run_pilot.py.txt) — the report references both `/tmp` and repo paths; the repo copies are what count.
2. **Widen the artifact exclusion from `.arena/patches` to `.arena/`** (or invert to an allowlist of intended paths). The bug class you found is "evidence/config artifacts leak into candidate branches," and the fix only covers one subdirectory. `goal.toml` or any future `.arena/` runtime file would leak the same way. It's the same five-line shape as the current fix plus one test parameter, and the boundary guarantee is the heart of M3 — close the class, not the instance. Apply the same widening to the fail-closed staged-path check.

**guidance_as_leon_representative**

The fail-closed guard after the reset (raise on any staged `.arena/patches/` path rather than silently unstaging twice) is the right instinct — keep that pattern as you widen it. Two things to note honestly in the close-out rather than fix now: the "every reject maps to a RejectReason and transcript" gate was exercised by exactly one *injected* reject, and all five promoted candidates are the same static patch with identical score_delta. Both are fine for this card's stated scope, but they mean reject-path diversity and organic candidate variation are unproven — that's M4 territory with live transport, and the tracker should say so explicitly so nobody reads "5 candidates promoted" as five independent successes.

**next_cards_to_claim_or_continue**

1. Finish BA-M3-07: apply change #2, re-run the packager/worktree test files plus the full gate suite (pytest, ruff, pyright), commit evidence + fix on `ba/m3-pilot-acceptance-run`, close the card.
2. Update/close the M3 root tracker, noting the packager bug found-and-fixed and the explicit non-goals deferred to M4 (live transport, organic rejects, operator-authorized live PR push).
3. File two small hardening follow-up cards rather than doing them now: (a) `.arena/` allowlist enforcement as a standing boundary invariant test, (b) organic reject-reason coverage matrix once live transport exists.
4. Then stop and report — don't start M4 work inside this branch.


## Fable focused re-review

Focused re-review verdict after applying `.arena/` exclusion: `ACCEPT`.

Review transcript:

VERDICT: ACCEPT

**remaining_blockers**

None requiring code or evidence changes. Both required changes from the prior review are satisfied:

1. Change #2 (widen exclusion) is done correctly. The `git reset -- .arena` after `git add -A` covers the whole directory, the fail-closed staged-path check was widened to `.arena/`, and the regression test exercises the class, not the instance — it plants files in `.arena/patches/` *and* a sibling `.arena/runtime.json`, asserts the candidate diff contains the marker and zero `.arena/` paths, and asserts the worktree copies survive for the evidence writer. That is exactly the shape the review asked for. The post-fix pilot rerun confirming candidate diffs touch only `tests/test_client.py`, `tests/test_resources.py`, `tests/test_server.py` closes the loop with live evidence rather than just the unit test.
2. Change #1 (commit) is the only outstanding item, and it is procedural, not a defect — `git status` confirms the fix, test, and evidence tree are still uncommitted on `ba/m3-pilot-acceptance-run`. The verification battery (targeted tests, full suite, ruff, pyright clean, `git diff --check`, artifact checks) was run against the exact working tree that will be committed, so no re-review is needed after the commit as long as nothing else changes between now and `git commit`.

**required_changes_before_completion**

None beyond executing the already-mandated commit. Two non-blocking observations to carry as notes, not fixes:

- The `startswith(".arena/")` guard would miss a top-level *file* literally named `.arena` (no trailing slash in git's path output). Practically irrelevant given `.arena` is always a directory in this system; fold it into the already-planned `.arena/` allowlist-invariant follow-up card rather than touching this branch.
- The fail-closed raise is now effectively dead code unless `git reset` itself fails — that's intentional belt-and-suspenders and should stay, but the follow-up invariant test card is the right place to ensure it stays meaningful.

**close_guidance**

1. Commit everything on `ba/m3-pilot-acceptance-run` now: `arena/worktrees.py`, `tests/test_candidate_packager.py`, `docs/verification/2026-06-10-m3-pilot-cycle-evidence.md`, and the full `docs/verification/2026-06-10-m3-pilot/` tree. Before committing, do one last spot-check that the durable repo copies actually contain `summary.json`, `evidence/`, `halt-evidence/`, `reject-evidence/`, `pr-bodies/`, `candidate-branch-diffs.txt`, and `run_pilot.py.txt` — the report claims them; the commit is what makes the claim true. After committing, confirm `git status` is clean.
2. Close card `t_5d7abe71` (BA-M3-07) referencing the evidence report path and this verdict.
3. In the M3 root tracker close-out, include the two honesty notes from the prior review verbatim in spirit: the reject gate was exercised by one *injected* RUNNER_ERROR only, and all five promotions are the same static patch with identical `score_delta` — organic reject diversity and candidate variation are explicitly deferred to M4 live transport.
4. File the two follow-up cards already identified: (a) `.arena/` allowlist enforcement as a standing boundary-invariant test (fold the top-level-file edge case in there), (b) organic reject-reason coverage matrix once live transport exists.
5. Stop after closing — no M4 work on this branch.

## Commands run during proof/finalization

- `PYTHONPATH=/home/leonb/projects/build-arena uv run python /tmp/build_arena_m3_07_pilot.py > /tmp/build-arena-m3-07-run.out.json` — passed after the `.arena/` exclusion fix.
- Acceptance assertion/audit script over `/tmp/build-arena-m3-07/summary.json`, cycle evidence, candidate branch diffs, and canonical fmc-mcp status — passed.
- `uv run pytest tests/test_candidate_packager.py tests/test_worktrees.py tests/test_worktree_cycle_evidence.py -q` — passed after the packager fix.
- `uv run pytest tests/test_candidate_packager.py tests/test_worktrees.py tests/test_worktree_cycle_evidence.py tests/test_pr_packaging.py -q` — passed.
- `uv run pytest tests -q` — passed.
- `uv run ruff check .` — passed.
- `uv run pyright` — passed with `0 errors, 0 warnings`.
- `git diff --check` — passed.
- Artifact marker and whitespace checks — passed.

## Notes

The candidate patch itself is intentionally static/fake-transport for BA-M3-07: this card proves worktree-only cycle mechanics, candidate packaging, evidence, rejection/halt handling, and owner-gated PR rendering. Live LLM/API calls and autonomous merge are non-goals. The intentional reject path is a single injected `RUNNER_ERROR`; broader organic reject diversity is deferred to later live-transport work.
