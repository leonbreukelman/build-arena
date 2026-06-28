# fmc-mcp Production Pass Lessons — 2026-06-15

> Superseded for target mutation (2026-06-27): the target apply/promote roots
> were removed by `docs/specs/2026-06-27-propose-only-remediation.md`.
> This page remains historical evidence for the retired production loop's
> failure modes, not runnable guidance for future target mutation.

Source run: `/home/leonb/projects/build-arena/.arena/runs/fmc-mcp-production-20260615T001605Z`

Primary analysis: `docs/specs/2026-06-15-full-autonomy-gap-analysis.md`

## Lesson summary

- The run was a safe failure, not a production improvement.
- Live decomposition, model gate, freshness, and synced intake worked.
- The actual autonomy loop did not close: no candidate was promoted, and no re-decompose/re-intake happened after promotion.
- The top-ranked code finding was silently skipped because it had no verification commands.
- Ten proposal-pipeline runs produced the same four candidates; this is determinism, not duplicate handling.
- The live docs proposal failed because the model generated a doubled local path: `src/src/fmc_mcp/config.py`.

## Findings agents must remember

### code-findings-unrunnable

Problem: Intake ranked `code.component.untested.comp-server` (540.0) as the #1 improvement, but the live loop selected the rank-2 docs candidate `agent.agents-md.missing` instead and never even attempted the code finding. Every `code.*` and `architecture.*` finding this repo produced is non-selectable, so the system can only ever act on Markdown/docs targets.

Root cause: Two boundaries combine to a dead end: (1) `project_intake_scorecard` emits `verification: []` for `code.component.untested.*` findings (the recommended action is 'add an observable check' with no command attached); (2) `GenericFileDomain.candidates_for_finding` (arena/proposal_domains.py:212-228) only reuses `finding.verification`, so the candidate carries empty `verification_commands`; (3) `_select_promotable` (arena/repo_goal_loop.py:394) hard-skips any candidate with empty `verification_commands`. Net: the top finding is silently filtered out with no event emitted. The load-bearing code gate was explicitly deferred (GenericFileDomain docstring: 'does NOT add a load-bearing code gate; that is Phase 3 (#29)'), and Phase 3 only delivered a lint gate for `code.quality.lint.*`, not for component/coverage findings.

Acceptance signal: A live cycle selects `code.component.untested.comp-server`, applies a bounded change in a worktree, and passes a non-empty load-bearing gate (test + mypy/ruff/pytest) before promotion — visible in loop-events.jsonl with no silent rank-1 skip.

### no-proposal-registry

Problem: Running the proposal pipeline 10 times against the same base produced 10 byte-identical artifacts (one plan hash, 4 candidate keys each appearing 10×). There is no state layer that records pending/applied/failed/promoted/rejected proposals, so the system cannot tell a fresh proposal from one it already generated, applied in a worktree, or abandoned on a branch.

Root cause: `build_proposal_plan_with_registry` (arena/proposal_planner.py) is a pure function of (project model, intake scorecard) with no read/write of any persisted proposal store. The only 'registry' in the codebase is `ProposalDomainRegistry` (a domain-plugin list, arena/proposal_domains.py:63), which the prior report's code search conflated with a proposal registry. No table/file keyed by (project, base, target, finding, intent/diff hash) exists.

Acceptance signal: Ten pipeline runs against one base yield one active proposal plus nine duplicate/reused records (not ten indistinguishable artifacts), and a promoted finding is marked promoted so it is not re-proposed.

### no-base-lineage-tags

Problem: Proposal plans record only `snapshotId`, `sourceScorecardId`, and `repoFactsHash`. They do not carry the base branch, base head OID, dirty-state fingerprint, or a content/diff hash. The freshness snapshot shows four pre-existing `ba/fmc-mcp-grounded-proposal-*` branches on the target (all at an older OID `d60155b…` than current `25f4458…`) — prior invisible proposals the proposer is completely unaware of.

Root cause: `ProposalPlan.to_jsonable` (arena/proposal_planner.py:52-73) serializes scorecard/snapshot ids only; there is no capture of git base (branch/headOid/dirty) at proposal time and no diff hash. The live proposer prompt (`_diff_prompt`, arena/runners/diff_proposer.py:194-223) is seeded only from current file contents + repo facts, never from existing pending/unmerged proposals.

Acceptance signal: A proposal generated against branch A is refused (lineage mismatch event) when the target branch advances or switches, and a pending proposal absent from the working tree appears in the next live-proposer prompt.

### live-proposer-no-repair-retry

Problem: The live model emitted AGENTS.md Markdown links to `src/src/fmc_mcp/config.py` (doubled `src/` prefix). The link gate correctly rejected it, the diff was reversed, and the cycle failed with zero promotions. The proposer made exactly one attempt and had no path to repair the obvious doubled-prefix error or regenerate.

Root cause: `DiffProposerRunner.apply` is single-shot: one transport call, then gate. The repair helper `_unique_suffix_match` (arena/runners/diff_proposer.py:415-420) can only fix a link whose normalized form is a unique *suffix* of an existing path; `src/src/fmc_mcp/config.py` is not a suffix of `src/fmc_mcp/config.py`, so no repair occurs and it hard-fails (diff_proposer.py:376-378). The run was also configured with `--live-max-calls 2` / `--max-cycles 1`, leaving no budget to retry. The prompt already lists the correct path in repo facts, yet the model doubled it and nothing caught the prefix-doubling class of error.

Acceptance signal: A live cycle that first emits a malformed path produces a corrected, gate-passing diff on a bounded retry, recorded as a repair event, rather than a terminal CANDIDATE_APPLY_FAILED.

### single-file-contract-drops-findings

Problem: Three of seven intake findings were skipped with reason `no_single_file_target`: the multi-file entrypoints component (`__init__.py` + `__main__.py`), and two model-level findings (architecture open-questions, quality-gates-present) whose evidence is `iterationReadiness.*` rather than a file. The system recognizes these issues but cannot turn them into proposals.

Root cause: `_single_target_path` (arena/proposal_domains.py:234-247) returns None unless exactly one non-`iterationReadiness` path remains, and `iterationReadiness.*` evidence paths are filtered out entirely (line 240). The proposal contract (`ProposalCandidateDraft`) is single-`target_path` only, so any finding touching multiple files or no concrete file is dropped by `first_candidate` (proposal_planner.py:112-114).

Acceptance signal: `code.component.untested.comp-entrypoints` produces a valid multi-file proposal with a load-bearing gate instead of appearing in skippedFindings.

### loop-never-closed-live

Problem: The production pass ran a single cycle, promoted nothing, and budget-halted. The promote→re-decompose→re-intake path that defines the goal is present in code but has zero live evidence of executing. Success of the full loop is asserted by code structure, not by a recorded run.

Root cause: Configuration `--max-cycles 1` plus the first (and only) candidate failing the gate meant the loop emitted BUDGET_HALT after one cycle (repo_goal_loop.py:196-198). The re-decompose-after-promotion behavior (tried_finding_ids.discard on promotion, repo_goal_loop.py:191, then loop re-runs `_decompose_and_rank`) was never reached because promotions=0. No live run with max_cycles>1 and an actual promotion exists in the evidence.

Acceptance signal: A loop-events.jsonl shows CANDIDATE promoted, followed by a second DECOMPOSITION_COMPLETED with a new snapshot id and a fresh intake before the next CANDIDATE_SELECTED.

## Proposal prompt requirement

Future live proposal prompts must include:

- current branch/ref and head OID;
- snapshot and scorecard IDs/hashes when used;
- pending/unmerged proposals from the proposal registry;
- failed proposals and their failure reasons;
- exact gate recipes and known path pitfalls from this wiki.

## Budget requirement

Use generous but bounded investigation/tool budgets. Do not set tiny max-turn/tool caps that prevent real diagnosis. Keep mutation/promotion budgets tight, but allow enough read/search/retry budget for the agent to recover from one bad model output and try the next viable candidate.
