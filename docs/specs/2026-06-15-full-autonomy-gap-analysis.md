# Full Autonomy Gap Analysis — fmc-mcp Production Pass

Generated: 2026-06-15T00:44:42Z

Source run: `/home/leonb/projects/build-arena/.arena/runs/fmc-mcp-production-20260615T001605Z`

Opus diagnosis artifact: `reports/2026-06-15-full-autonomy-gap-opus-diagnosis.json`

## Verdict

Safe failure, not autonomy. The production pass promoted nothing, mutated nothing, and the one cycle it ran failed at the Markdown link gate. Decomposition, freshness, and intake-sync work; the actual autonomy spine — select-any-domain → apply → verify → promote → re-decompose — never executed end-to-end live. The system's effective autonomous capability today is 'write a docs file that passes a link checker,' not 'improve a repository.' The highest-priority finding every cycle is silently unrunnable, proposals have no registry or lineage, and a single 1-cycle/2-call budget let one bad path end the entire run. Build Arena is far short of full repo-scale autonomy.

## One-sentence gap

Build Arena can only mutate-and-promote documentation files, has no persistent proposal registry/lineage to prevent duplicate churn or branch unsafety, silently skips its own top-ranked code findings for lack of verification commands, and has never completed a single live promote→re-decompose cycle — so the closed autonomous loop in the goal remains unproven.

## Deviation findings

### 1. The highest-priority finding is structurally unrunnable; only docs candidates can ever be selected

- ID: `code-findings-unrunnable`
- Severity: `critical`

**Problem statement**

Intake ranked `code.component.untested.comp-server` (540.0) as the #1 improvement, but the live loop selected the rank-2 docs candidate `agent.agents-md.missing` instead and never even attempted the code finding. Every `code.*` and `architecture.*` finding this repo produced is non-selectable, so the system can only ever act on Markdown/docs targets.

**Root cause**

Two boundaries combine to a dead end: (1) `project_intake_scorecard` emits `verification: []` for `code.component.untested.*` findings (the recommended action is 'add an observable check' with no command attached); (2) `GenericFileDomain.candidates_for_finding` (arena/proposal_domains.py:212-228) only reuses `finding.verification`, so the candidate carries empty `verification_commands`; (3) `_select_promotable` (arena/repo_goal_loop.py:394) hard-skips any candidate with empty `verification_commands`. Net: the top finding is silently filtered out with no event emitted. The load-bearing code gate was explicitly deferred (GenericFileDomain docstring: 'does NOT add a load-bearing code gate; that is Phase 3 (#29)'), and Phase 3 only delivered a lint gate for `code.quality.lint.*`, not for component/coverage findings.

**Evidence**

- loop-events.jsonl:4 CANDIDATE_SELECTED finding_id=agent.agents-md.missing (rank 2), not comp-server (rank 1)
- post-run-pipeline/proposal-runs/proposal-plan-01.json:107-121 comp-server candidate has verification_commands: []
- intake-scorecard.json:120 finding code.component.untested.comp-server verification: []
- arena/repo_goal_loop.py:394 `if not tuple(plan_candidate.get('verification_commands', [])): continue`
- arena/proposal_domains.py:221 GenericFileDomain verification = finding.get('verification', [])

**Deviation from full autonomy**

Full repo-scale autonomy requires acting across domains on the genuinely highest-leverage work (here, untested core server runtime). Instead the system is permanently restricted to documentation files, and its own ranking is overridden by an invisible filter — it cannot improve code, the thing repos are mostly made of.

**Implementation implication**

Component/coverage findings must synthesize a real load-bearing verification gate (e.g. generate-or-require a focused test plus the project's existing quality-gate commands) rather than inheriting an empty list, and `_select_promotable` skipping a top finding must emit a CANDIDATE_SKIPPED event with reason so the silent override is observable.

**Acceptance signal**

A live cycle selects `code.component.untested.comp-server`, applies a bounded change in a worktree, and passes a non-empty load-bearing gate (test + mypy/ruff/pytest) before promotion — visible in loop-events.jsonl with no silent rank-1 skip.

### 2. No persistent proposal registry; repeated runs emit byte-identical duplicate plans

- ID: `no-proposal-registry`
- Severity: `high`

**Problem statement**

Running the proposal pipeline 10 times against the same base produced 10 byte-identical artifacts (one plan hash, 4 candidate keys each appearing 10×). There is no state layer that records pending/applied/failed/promoted/rejected proposals, so the system cannot tell a fresh proposal from one it already generated, applied in a worktree, or abandoned on a branch.

**Root cause**

`build_proposal_plan_with_registry` (arena/proposal_planner.py) is a pure function of (project model, intake scorecard) with no read/write of any persisted proposal store. The only 'registry' in the codebase is `ProposalDomainRegistry` (a domain-plugin list, arena/proposal_domains.py:63), which the prior report's code search conflated with a proposal registry. No table/file keyed by (project, base, target, finding, intent/diff hash) exists.

**Evidence**

- proposal-duplicate-summary.json uniquePlanArtifactHashes=1, uniqueRankedArtifactHashes=1, planCandidatesPerRun=4, proposalPlanRunCount=10
- md5sum of all 10 proposal-plan-*.json collapses to a single hash (a271553893511f71d2af79677d2fa028)
- arena/proposal_planner.py has no persistence; grep for registry/dedup/pending found only domain-plugin registry

**Deviation from full autonomy**

The goal explicitly demands the loop 'avoid duplicate/invisible proposal churn.' Without a registry the system will re-propose the same change every cycle forever and cannot maintain a managed proposal queue, making unattended multi-cycle operation produce noise rather than progress.

**Implementation implication**

Add a persistent proposal registry keyed at minimum by project id, base head OID/branch-overlay, target path(s), finding id/domain, normalized intent hash, and diff/content hash, with lifecycle states (pending, applied-in-worktree, failed-gate, promoted, rejected/duplicate); the planner must consult it to suppress duplicates and surface reuse.

**Acceptance signal**

Ten pipeline runs against one base yield one active proposal plus nine duplicate/reused records (not ten indistinguishable artifacts), and a promoted finding is marked promoted so it is not re-proposed.

### 3. Proposals carry no branch/base/diff lineage, so they cannot be safely bound to a snapshot or branch

- ID: `no-base-lineage-tags`
- Severity: `high`

**Problem statement**

Proposal plans record only `snapshotId`, `sourceScorecardId`, and `repoFactsHash`. They do not carry the base branch, base head OID, dirty-state fingerprint, or a content/diff hash. The freshness snapshot shows four pre-existing `ba/fmc-mcp-grounded-proposal-*` branches on the target (all at an older OID `d60155b…` than current `25f4458…`) — prior invisible proposals the proposer is completely unaware of.

**Root cause**

`ProposalPlan.to_jsonable` (arena/proposal_planner.py:52-73) serializes scorecard/snapshot ids only; there is no capture of git base (branch/headOid/dirty) at proposal time and no diff hash. The live proposer prompt (`_diff_prompt`, arena/runners/diff_proposer.py:194-223) is seeded only from current file contents + repo facts, never from existing pending/unmerged proposals.

**Evidence**

- proposal-plan-01.json:210-248 fields: id, snapshotId, sourceScorecardId, repoFactsHash — no base branch/headOid/diffHash
- freshness.json activeBranches lists ba/fmc-mcp-grounded-proposal-20260613T0517/0521/0524Z at d60155b… (stale) plus ba/fmc-mcp-proposal-20260612T025323Z
- arena/runners/diff_proposer.py:194-223 _diff_prompt includes no prior-proposal context

**Deviation from full autonomy**

The goal requires proposals 'against a specific branch/snapshot/base' and re-intake before the next cycle. Without lineage, a proposal generated against branch A could be applied to branch B, and the model regenerates work that already exists on an unmerged branch — violating the grounded, branch-safe, non-duplicative requirement.

**Implementation implication**

Stamp every proposal input and output with project id, base branch/ref, base head OID, dirty fingerprint, snapshot id/hash, scorecard id/hash, run id, target paths, and diff/content hash; feed existing pending/unmerged proposals from the registry into the live-proposer prompt; enforce a freshness/lineage check that blocks applying a proposal whose base no longer matches the target.

**Acceptance signal**

A proposal generated against branch A is refused (lineage mismatch event) when the target branch advances or switches, and a pending proposal absent from the working tree appears in the next live-proposer prompt.

### 4. A single malformed path from the live model ends the run; there is no repair/regenerate loop

- ID: `live-proposer-no-repair-retry`
- Severity: `high`

**Problem statement**

The live model emitted AGENTS.md Markdown links to `src/src/fmc_mcp/config.py` (doubled `src/` prefix). The link gate correctly rejected it, the diff was reversed, and the cycle failed with zero promotions. The proposer made exactly one attempt and had no path to repair the obvious doubled-prefix error or regenerate.

**Root cause**

`DiffProposerRunner.apply` is single-shot: one transport call, then gate. The repair helper `_unique_suffix_match` (arena/runners/diff_proposer.py:415-420) can only fix a link whose normalized form is a unique *suffix* of an existing path; `src/src/fmc_mcp/config.py` is not a suffix of `src/fmc_mcp/config.py`, so no repair occurs and it hard-fails (diff_proposer.py:376-378). The run was also configured with `--live-max-calls 2` / `--max-cycles 1`, leaving no budget to retry. The prompt already lists the correct path in repo facts, yet the model doubled it and nothing caught the prefix-doubling class of error.

**Evidence**

- loop-events.jsonl:5 CANDIDATE_APPLY_FAILED error 'missing Markdown link target: src/src/fmc_mcp/config.py->src/src/fmc_mcp/config.py'
- arena/runners/diff_proposer.py:376-378 raises RunnerError on missing link with no retry
- arena/runners/diff_proposer.py:415-420 _unique_suffix_match handles suffix dupes only, not prefix doubling
- report lines 38-39 live-max-calls 2, max-cycles 1

**Deviation from full autonomy**

Autonomy means recovering from a recoverable model error, not aborting the whole run. A grounded proposer that knows the exact path but emits a doubled prefix, with no self-repair and no retry budget, cannot reliably land even the docs changes it is restricted to.

**Implementation implication**

Add a bounded repair/regenerate loop: on gate rejection, feed the specific gate error back to the model for a correction attempt (within a per-cycle call budget), and extend deterministic path normalization to collapse repeated repo-root prefixes (e.g. `src/src/` → `src/`) before failing.

**Acceptance signal**

A live cycle that first emits a malformed path produces a corrected, gate-passing diff on a bounded retry, recorded as a repair event, rather than a terminal CANDIDATE_APPLY_FAILED.

### 5. Single-file proposal contract silently drops multi-file and model-level findings

- ID: `single-file-contract-drops-findings`
- Severity: `medium`

**Problem statement**

Three of seven intake findings were skipped with reason `no_single_file_target`: the multi-file entrypoints component (`__init__.py` + `__main__.py`), and two model-level findings (architecture open-questions, quality-gates-present) whose evidence is `iterationReadiness.*` rather than a file. The system recognizes these issues but cannot turn them into proposals.

**Root cause**

`_single_target_path` (arena/proposal_domains.py:234-247) returns None unless exactly one non-`iterationReadiness` path remains, and `iterationReadiness.*` evidence paths are filtered out entirely (line 240). The proposal contract (`ProposalCandidateDraft`) is single-`target_path` only, so any finding touching multiple files or no concrete file is dropped by `first_candidate` (proposal_planner.py:112-114).

**Evidence**

- proposal-plan-01.json:215-246 skippedFindings: comp-entrypoints (src/fmc_mcp/__init__.py + __main__.py), architecture.open-questions-or-gaps, verification.quality-gates.present — all reason no_single_file_target
- arena/proposal_domains.py:234-247 _single_target_path requires len(unique)==1
- arena/proposal_domains.py:240 evidence paths starting with iterationReadiness are skipped

**Deviation from full autonomy**

Repo-scale autonomy must decompose and address cross-cutting and multi-file work, not only single-file edits. A contract that drops architecture gaps and multi-file components confines the system to the easiest slice of the backlog.

**Implementation implication**

Extend the proposal contract to support multi-file targets and model-level (non-file) improvement intents (e.g. converting open-questions into backlog/verification tasks), with gates appropriate to each shape.

**Acceptance signal**

`code.component.untested.comp-entrypoints` produces a valid multi-file proposal with a load-bearing gate instead of appearing in skippedFindings.

### 6. The closed loop (promote → re-decompose → re-intake) has never run end-to-end live

- ID: `loop-never-closed-live`
- Severity: `high`

**Problem statement**

The production pass ran a single cycle, promoted nothing, and budget-halted. The promote→re-decompose→re-intake path that defines the goal is present in code but has zero live evidence of executing. Success of the full loop is asserted by code structure, not by a recorded run.

**Root cause**

Configuration `--max-cycles 1` plus the first (and only) candidate failing the gate meant the loop emitted BUDGET_HALT after one cycle (repo_goal_loop.py:196-198). The re-decompose-after-promotion behavior (tried_finding_ids.discard on promotion, repo_goal_loop.py:191, then loop re-runs `_decompose_and_rank`) was never reached because promotions=0. No live run with max_cycles>1 and an actual promotion exists in the evidence.

**Evidence**

- loop-events.jsonl:6-7 BUDGET_HALT reason=max_cycles cap=1; RUN_ENDED promotions=0 cyclesRun=1
- arena/repo_goal_loop.py:188-194 promotion + re-decompose path; arena/repo_goal_loop.py:134 cycle loop bounded by max_cycles
- report line 8 'it promoted nothing'

**Deviation from full autonomy**

The entire goal is the closed autonomous cycle under bounded controls. A loop that has never completed promote→re-decompose→re-intake live is unproven for its core claim, regardless of how the code reads.

**Implementation implication**

Run a live pass with max_cycles greater than the count of viable candidates and a real promotable code/docs candidate, and capture a full cycle that promotes, then re-decomposes and re-intakes before selecting the next candidate.

**Acceptance signal**

A loop-events.jsonl shows CANDIDATE promoted, followed by a second DECOMPOSITION_COMPLETED with a new snapshot id and a fresh intake before the next CANDIDATE_SELECTED.

## Agent wiki requirement

**Problem statement**

Every run rebuilds its entire understanding of the target from decomposition + intake + a flat repo-facts block, and learns nothing across runs. The live proposer re-made a path error the system had no memory of; prior proposal branches on the target are invisible to it; gate semantics (what each gate requires, how to satisfy the source-references rule) live only in code; and there is no shared place recording conventions, known failure modes, verification recipes, or definition-of-done. Without a durable shared knowledge base, agents cannot work effectively or accumulate competence.

**Root cause**

There is no persistent, agent-readable knowledge store. Context is reconstructed per run from artifacts only (project model, scorecard, repo_facts string in proposal-plan-01.json:114), and failures/learnings are written to event logs that are never fed back into any prompt. The proposer prompt (diff_proposer.py:194-223) is seeded with facts but no accumulated knowledge, registry state, or prior-failure memory.

**Minimum contents**

- Repo conventions and structure facts (canonical paths, package layout) so prefix-doubling errors like src/src/ are pre-empted
- Gate catalog: each gate's command, what it checks, and concrete recipes for passing it (e.g. markdown source-references requirement, code_quality_gate anti-suppression rules)
- Known failure modes and their fixes, harvested from CANDIDATE_APPLY_FAILED / DIVERGENCE events (doubled prefixes, invented links, empty-verification skips)
- Live proposal registry state: pending/applied-in-worktree/failed-gate/promoted/rejected proposals with lineage, so agents see invisible/unmerged work
- Per-finding-type verification recipes (how to synthesize an observable check for an untested component)
- Boundary rules, read-only directories, and definition-of-done for promotion
- Branch/lineage map of the target (active branches, base OIDs) and the latest accepted project model + scorecard ids

**Acceptance signal**

A new live-proposer prompt is seeded from the wiki and (a) does not repeat a previously recorded failure (no re-emission of a doubled-prefix path), and (b) lists existing pending/unmerged proposals so it does not regenerate them; a fresh implementation agent reaches the same gate-passing behavior without re-deriving conventions from scratch.

## Execution budget guidance

**Problem statement**

The production pass was run with max_cycles=1 and live_max_calls=2. One bad docs patch ended the entire run, and the loop never fell through to the three other runnable docs candidates (decision records, runbooks) that the report itself notes were 'not attempted because max cycles was 1.' Tiny caps turned a recoverable single-candidate failure into a total run failure and prevented any real investigation. The same anti-pattern must not be imposed on the implementation agents that build Build Arena: starving an agent of turns/tools mid-investigation produces shallow, truncated work, not safety.

**Root cause**

Conflation of two different budgets: investigation/read budget (should be generous so agents and the loop can explore alternatives and recover) and mutation/promotion budget (should be tight so the target is never churned). The run set a single tiny cap that bounded both, and the loop's max_cycles=1 meant a per-candidate failure equals run failure because a failed candidate only advances on the next cycle (repo_goal_loop.py:156,169-176).

**Recommended limits**

- Separate read/investigation budget (generous) from write/mutation budget (strict): never cap reading, searching, or reasoning so low that an agent cannot finish investigating
- Set high per-phase ceilings rather than tiny global max-turn/max-tool caps; e.g. decomposition: a bounded number of live calls; investigation/repair: generous turn and tool budget; mutation+promotion: strictly bounded calls and one promote per cycle
- Set the loop's max_cycles strictly greater than the number of viable candidates so a single gate failure does not end the run before the next candidate is tried
- Give the live proposer a small but nonzero repair/retry budget per cycle so one malformed diff does not abort the cycle
- Bound by outcome/divergence (consecutive-failure streak, divergence halt) and total token/cost ceilings, not by artificially small turn/tool counts
- Make every truncation or cap-hit an explicit logged event so silent under-investigation is visible

**Acceptance signal**

A run where the first candidate fails the gate continues to the next viable candidate within budget and either promotes one or halts on a real divergence/cost ceiling; implementation agents complete their investigation with no mid-task max-turn/max-tool truncation events in the logs.

## Priority order

1. `code-findings-unrunnable`
2. `no-proposal-registry`
3. `no-base-lineage-tags`
4. `live-proposer-no-repair-retry`
5. `loop-never-closed-live`
6. `single-file-contract-drops-findings`

## Notes for implementation planner

- The report's framing ('safe failure, not success') is accurate and should be preserved — do not let any downstream summary upgrade a zero-promotion run to a success.
- The single most autonomy-limiting fact is that only docs/Markdown candidates are runnable today; fixing the empty-verification skip for code findings (a real load-bearing gate for component/coverage findings) unlocks the rest. Treat code-findings-unrunnable as the keystone.
- Registry and lineage (findings no-proposal-registry + no-base-lineage-tags) are one coherent workstream: a persistent, lineage-stamped proposal store that the planner reads to dedupe and the live proposer reads to avoid regenerating invisible branch work. The four pre-existing ba/fmc-mcp-grounded-proposal-* branches in freshness.json are concrete invisible-work the registry must capture.
- Make the silent skip in _select_promotable (repo_goal_loop.py:394) observable: emit a CANDIDATE_SKIPPED event with reason. The rank-1 finding was dropped with no trace, which is how a 540-priority item became invisible.
- Prove the closed loop live before claiming it: one recorded run with a promotion followed by re-decompose/re-intake. Until that exists, the 'close the loop' epic is code, not capability.
- Stand up the agent wiki early — it is the substrate the registry, gate recipes, and failure-memory all write into, and the source the live-proposer/implementation-agent prompts read from.
- Apply the execution-budget guidance to your own implementation runs: generous investigation budgets, tight mutation budgets, high per-phase ceilings, and loop max_cycles > viable-candidate count.
