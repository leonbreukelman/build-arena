Review artifact: /home/leonb/projects/build-arena/reports/2026-06-15-doc-drift-review.md

You are an independent Opus reviewer. Do not edit files. Review the pasted report below for a concise owner-facing documentation drift review.

Focus:
- Is the bottom line faithful to the evidence cited?
- Are any findings overstated or stale based on the report itself?
- Is there any major missing contradiction/drift risk Leon should hear before implementing the frozen onboarding plan?
- Keep output short. Verdict one of: PASS, PASS_WITH_NOTES, REVISE. Then bullets.

Report content:

---
# Build Arena documentation drift review — 2026-06-15

Scope: README.md, AGENTS.md, docs/build-arena-project-brief.md, docs/agent-wiki/*, docs/status/*, docs/plans/*, docs/specs/*, docs/inbox/*, and doc-status tests. No source docs were edited.

Verification run: `uv run pytest tests/test_project_status_docs.py -q` passed.

## Tight findings

1. Biggest drift: the active orientation docs still point future agents at the old Project Model v1 / AI-first decomposer stack, while the inbox plan/prompt introduce a deliberate reset to one frozen deterministic spine: `docs/schemas/project-model.frozen-v1.json` + `arena/onboard.py`. AGENTS.md does not yet contain the onboarding-scope lock from the plan. Evidence: README.md:10, AGENTS.md:40, docs/build-arena-project-brief.md:30-42 vs docs/inbox/IMPLEMENTATION_PLAN.md:5-9, 32-36, 119-126.

2. Registry status is internally inconsistent. Active docs still say proposal registry/lineage is blocked or unimplemented, while the current tree has `arena/proposal_registry.py`, wiki records, plan lineage fields, and tests. The precise truth is: registry primitives exist, but lifecycle wiring is still thin and live proposer context is still empty. Evidence: docs/build-arena-project-brief.md:42, README.md:10, docs/status/2026-06-15-current-status-timeline-production-readiness.md:223-227, arena/repo_goal_loop.py:586-587.

3. Some June 14 readiness docs are now stale after the June 15 production attempt. They say the system is ready to perform one bounded fmc-mcp production run; that run has already happened and promoted nothing. These files need a clear historical/superseded banner or should be removed from the active read path. Evidence: docs/status/2026-06-14-progress-timeline-and-production-readiness-audit.md:5, docs/status/2026-06-14-live-repo-goal-loop.md:77, docs/status/2026-06-15-current-status-timeline-production-readiness.md:11-22.

4. The remediation plan is useful but stale as an execution guide. It says implementation was not started and that only docs/Markdown candidates are runnable; the later status says the first remediation slice landed, with component verification/domain/registry primitives present but not broad-autonomy proof. Evidence: docs/plans/2026-06-15-full-autonomy-gap-remediation-plan.md:15,27 vs docs/status/2026-06-15-full-autonomy-gap-remediation-implementation-status.md:3-8,63-68.

5. README.md, AGENTS.md, and docs/build-arena-project-brief.md duplicate large current-status blocks. That duplication is already causing the above contradictions. Recommendation: make AGENTS.md rules/boundaries only, README.md quickstart/status summary only, and one dated status/brief file the canonical current-state source.

6. Agent wiki is directionally right but under-specified for current truth. The fmc-mcp lessons page records pre-remediation failures (`no proposal registry`, code findings unrunnable) while the registry/repair page records partial fixes. Without a current-vs-historical label, a future agent can treat both as live facts. Evidence: docs/agent-wiki/2026-06-15-fmc-mcp-production-pass-lessons.md:18-64, docs/agent-wiki/2026-06-15-proposal-registry-lineage-and-repair-loop.md:13-38, docs/agent-wiki/records.jsonl.

7. The doc drift guard is now behind the north star. tests/test_project_status_docs.py still enforces AI-first v1 markers and does not enforce the new frozen-v1/onboard boundary. It will let the old decomposer framing remain canonical even while the onboarding acceptance contract moves the project elsewhere. Evidence: tests/test_project_status_docs.py:31-47,83-100; frozen-v1 appears only in docs/inbox and status references.

## Bottom line

The docs are mostly honest about "safe failure, not autonomy," but they are not aligned on the next north-star move. Before implementation, first patch the active orientation layer to say: frozen-v1/onboard is the next intended spine; old decomposers are legacy/deferred unless explicitly kept; registry primitives exist but are not a complete autonomy control plane; June 14 readiness docs are historical.
