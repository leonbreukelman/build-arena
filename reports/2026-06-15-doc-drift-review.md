# Build Arena documentation drift review — 2026-06-15

Scope: README.md, AGENTS.md, docs/build-arena-project-brief.md, docs/agent-wiki/*, docs/status/*, docs/plans/*, docs/specs/*, docs/inbox/*, and doc-status tests. No source docs were edited.

Verification run: `uv run pytest tests/test_project_status_docs.py -q` passed.

## Tight findings

1. Biggest alignment risk if the inbox plan is accepted: the active orientation docs still point future agents at the Project Model v1 / AI-first decomposer stack, while the inbox plan/prompt introduce a deliberate reset to one frozen deterministic spine: `docs/schemas/project-model.frozen-v1.json` + `arena/onboard.py`. The active docs are not necessarily wrong until that reset is ratified, but they will become wrong immediately if implementation starts without first updating the orientation layer. AGENTS.md also does not yet contain the onboarding-scope lock from the plan. Evidence: README.md:10, AGENTS.md:40, docs/build-arena-project-brief.md:30-42 vs docs/inbox/IMPLEMENTATION_PLAN.md:5-9, 32-36, 119-126.

2. Registry status is internally inconsistent. Active docs still say proposal registry/lineage is blocked or unimplemented, while the current tree has `arena/proposal_registry.py`, wiki records, plan lineage fields, and tests. The precise truth is: registry primitives exist, but lifecycle wiring is still thin and live proposer context is still empty. Evidence: docs/build-arena-project-brief.md:42, README.md:10, docs/status/2026-06-15-current-status-timeline-production-readiness.md:223-227, arena/repo_goal_loop.py:586-587.

3. Some June 14 readiness docs are now stale after the June 15 production attempt. They say the system is ready to perform one bounded fmc-mcp production run; that run has already happened and promoted nothing. These files need a clear historical/superseded banner or should be removed from the active read path. Evidence: docs/status/2026-06-14-progress-timeline-and-production-readiness-audit.md:5, docs/status/2026-06-14-live-repo-goal-loop.md:77, docs/status/2026-06-15-current-status-timeline-production-readiness.md:11-22.

4. The remediation plan is useful but stale as an execution guide. It says implementation was not started and that only docs/Markdown candidates are runnable; the later status says the first remediation slice landed, with component verification/domain/registry primitives present but not broad-autonomy proof. Evidence: docs/plans/2026-06-15-full-autonomy-gap-remediation-plan.md:15,27 vs docs/status/2026-06-15-full-autonomy-gap-remediation-implementation-status.md:3-8,63-68.

5. README.md, AGENTS.md, and docs/build-arena-project-brief.md duplicate large current-status blocks. That duplication is already causing the above contradictions. Recommendation: make AGENTS.md rules/boundaries only, README.md quickstart/status summary only, and one dated status/brief file the canonical current-state source.

6. Agent wiki is directionally right but under-specified for current truth. The fmc-mcp lessons page records pre-remediation failures (`no proposal registry`, code findings unrunnable) while the registry/repair page records partial fixes. Without a current-vs-historical label, a future agent can treat both as live facts. Evidence: docs/agent-wiki/2026-06-15-fmc-mcp-production-pass-lessons.md:18-64, docs/agent-wiki/2026-06-15-proposal-registry-lineage-and-repair-loop.md:13-38, docs/agent-wiki/records.jsonl.

7. The doc drift guard will be behind the north star if the frozen onboarding reset is ratified. `tests/test_project_status_docs.py` still enforces AI-first v1 markers and does not enforce the new frozen-v1/onboard boundary. That is fine for the current canonical docs, but it will lock in the old decomposer framing unless the guard is updated as part of adopting the onboarding contract. Evidence: tests/test_project_status_docs.py:31-47,83-100; frozen-v1 appears only in docs/inbox and status references.

## Bottom line

The docs are mostly honest about "safe failure, not autonomy," but they are not aligned on the proposed next north-star move. Sequence matters: first decide/ratify whether the frozen-v1/onboard reset is now the canonical path; then patch the active orientation layer and drift guards to say that frozen-v1/onboard is the intended spine, old decomposers are legacy/deferred unless explicitly kept, registry primitives exist but are not a complete autonomy control plane, and June 14 readiness docs are historical.
