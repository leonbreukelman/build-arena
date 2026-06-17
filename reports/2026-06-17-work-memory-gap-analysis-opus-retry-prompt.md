No tools. Do not request tools. Read the embedded artifact below and return concise JSON only.

Review task:
1. Check whether the artifact answers Leon's question about the apparent gap between work done and memory/status.
2. Check for factual overclaim about readiness register, agent wiki, proposal registry, Hermes memory, and status docs.
3. Check whether recommendations avoid conflating broad-autonomy readiness with feature-level work tracking.

Return only:
{"verdict":"ACCEPT|ACCEPT_WITH_CHANGES|REJECT","mustFixBeforeFinal":[...],"notes":[...]}

ARTIFACT:
---
# Work done vs memory/status gap analysis — 2026-06-17

## Question

Leon asked why there appears to be a gap between work done and memory, whether docs/wiki/register updates would resolve it, and whether this was already in place.

## Short answer

The gap is real, but it is not because Build Arena has no memory/status system. It has several partially overlapping systems:

- durable repo orientation docs (`README.md`, `AGENTS.md`, `docs/build-arena-project-brief.md`),
- dated status/report artifacts under `docs/status/` and `reports/`,
- an agent wiki under `docs/agent-wiki/`,
- a broad pre-live readiness register at `docs/verification/2026-06-05-pre-live-readiness-register.json`,
- code-level proposal registry primitives (`arena/proposal_registry.py`) and per-run `proposal-registry.jsonl` files,
- Hermes conversation/session search and assistant memory outside the repo.

The miss is that these systems do not yet form one automatically reconciled current-state ledger. Some are broad readiness gates, some are historical lessons, some are per-run state, and some are local assistant recall. A dated status file can therefore remain stale after a PR merge unless a workflow explicitly updates or supersedes it.

## Grounded evidence checked

- Current git state: `main...origin/main`, HEAD `360e9a2 Merge pull request #40 from leonbreukelman/graph/call-inheritance-treesitter`.
- The stale file is in HEAD and was committed by `af48ead feat: add project graph call and inheritance edges`.
- `docs/status/2026-06-16-project-graph-call-inheritance-treesitter.md:3` still says: `Status: implemented locally on branch graph/call-inheritance-treesitter; not committed.`
- `AGENTS.md:32-34` requires reading `docs/agent-wiki/index.md` for production/proposal/autonomy-loop work and says new failed candidate events/registry lessons/gate recipes should be recorded there.
- `docs/agent-wiki/index.md:20-25` explicitly says the wiki should grow gate catalog, known failure modes, proposal registry view, lineage map, per-finding recipes, and promotion definition of done.
- `docs/status/2026-06-15-full-autonomy-gap-remediation-implementation-status.md:23-31` says proposal registry/lineage primitives and repair context were implemented.
- `docs/status/2026-06-15-full-autonomy-gap-remediation-implementation-status.md:63-68` says remaining blockers include richer registry status transitions in the production loop and incomplete broad autonomy proof.
- `docs/agent-wiki/2026-06-15-proposal-registry-lineage-and-repair-loop.md:30-38` says the implementation is still not broad-autonomy proof and still needs real target-project promotion, control plane/rollback, fuller registry transitions, and multi-file apply support.
- `docs/verification/2026-06-05-pre-live-readiness-register.json` is a broad live-autonomy readiness register. It has statuses for live/decomposition/promotion readiness, not a row per merged feature/status-doc supersession.
- `tests/test_project_status_docs.py` guards specific broad orientation claims in README/AGENTS/project brief, but it does not currently check every dated `docs/status/*` file for stale branch/commit claims after PR merge.

## Why the gap happened

1. The status file was written at the correct point in time: before the branch was committed/pushed/merged. After PR #40 merged, the repo code advanced but the dated status file was not patched or superseded.
2. The current guardrails focus on broad readiness and orientation-doc drift, not per-feature lifecycle transitions such as `local -> PR opened -> merged`.
3. The agent wiki exists, but the index itself says several useful sections are still future growth areas. It is versioned operational memory, not an automatic current-state database.
4. The proposal registry exists for generated Build Arena proposals/runs. It is not a general repo worklog for human/agent feature work unless a workflow writes feature lifecycle records into it.
5. Hermes memory is intentionally not used for stale task progress, PR numbers, commit SHAs, or temporary completion logs. That is correct: those facts belong in repo docs/git/session search, not global assistant memory.

## Does updating docs/wiki/register resolve it?

Partially, yes, but only if the source-of-truth boundaries are clarified.

Recommended shape:

1. Patch or supersede the stale dated status file so it does not claim `not committed` after merge.
2. Add a tiny `docs/status/index.md` or `docs/status/current.md` that says which dated status file is current and which are historical/superseded. This reduces the need to infer from filenames.
3. Keep the readiness register for broad live-autonomy readiness only. Do not overload it with every feature merge.
4. Add a lightweight feature/workstream register only if Build Arena needs durable lifecycle tracking across sessions. A minimal JSONL or Markdown table would track: workstream id, branch, PR, merge commit, current state, verification commands, supersedes/superseded-by, and evidence paths.
5. Expand agent-wiki records for recurring failure modes and proposal/loop lessons, not one-off local PR state. Use it when a lesson should affect future proposal prompts or gates.
6. Add/extend a doc-status test if this class matters: scan active status docs for phrases such as `not committed`, `implemented locally`, or deleted branch names when git says the branch was merged.

## Does Leon misunderstand?

No. The expectation was reasonable because the repo already has a wiki, readiness register, status docs, proposal registry primitives, and doc-drift tests. The misunderstanding is about coverage: those systems are in place for broad autonomy/readiness/proposal state, but they do not yet automatically reconcile ordinary feature lifecycle docs after a PR merge.

## Proposed next action

Treat this as a docs/status lifecycle hygiene gap, not a code defect:

- immediate fix: patch `docs/status/2026-06-16-project-graph-call-inheritance-treesitter.md:3` to say it was merged via PR #40 / merge commit `360e9a2`;
- durable fix: add `docs/status/index.md` or a small lifecycle register and a test that catches stale `implemented locally/not committed` claims in active status docs.

---
