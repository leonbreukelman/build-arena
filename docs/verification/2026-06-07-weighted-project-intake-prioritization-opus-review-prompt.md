# Opus Review Prompt — Weighted Project Intake Prioritization

Date: 2026-06-07
Reviewer target: Claude Code model alias `opus`
Mode: read-only review; no edits; no commands required except reading provided files if tool access is available

## Review goal

Review the current conversation intent plus the drafted Build Arena specification, Hermes skill, and AGENTS.md instruction update for the weighted project-intake prioritization strategy.

Return a concise but adversarial review. Focus on whether anything important was missed, contradicted, overstated, or made too heavyweight.

## Conversation brief

Leon asked to preserve a strategy discussed in this session:

- For every project Leon works on with Hermes, apply an additional weighted project-intake scorecard.
- The scorecard should help decide which improvement to start with, especially when a new or unfamiliar repo is consumed.
- Leon suspects documentation/project knowledge, spec, architecture, and code/doc consistency should often be primary for new projects.
- The research synthesis agreed: documentation is not cosmetic for autonomous agents; it is part of the control system.
- Best canonical form: versioned repo docs and machine-readable sidecars, with GitHub Wiki or generated docs only as a navigation/projection layer unless mirrored/versioned.
- Weighting should be tunable so downstream autonomous improvement services can adjust priorities by project phase.
- The immediate task: save the Build Arena spec/backlog item, create a reusable Hermes skill, update durable instructions so agents use this across projects, use Opus to review the conversation and artifacts, incorporate fixes, and report.

Important Build Arena context:

- Build Arena is not ready for broad autonomous live loops while readiness blockers remain.
- Project Model v1 is the primary enriched artifact.
- The weighted scorecard should become a backlog item/later implementation layer, not be represented as already implemented.
- Anti-fabrication and filesystem/git-grounding rules are highest priority.
- Protected paths/scorer/schema/generated boundaries must remain intact.

## Files to review

Please read and review these files from `/home/leonb/projects/build-arena` and Hermes skill storage:

1. `/home/leonb/projects/build-arena/docs/specs/2026-06-07-weighted-project-intake-prioritization.md`
2. `/home/leonb/.hermes/skills/software-development/weighted-project-intake-prioritization/SKILL.md`
3. `/home/leonb/projects/build-arena/AGENTS.md`

## Required review output

Use this structure:

```text
REVIEWER: Claude Code model=<resolved model if visible> opus_confirmed=<yes/no/unknown>
VERDICT: ACCEPT / ACCEPT_WITH_CHANGES / REJECT

Critical blockers:
- ...

Important issues:
- ...

Missing content or contradictions:
- ...

Overreach / scope-risk:
- ...

Recommended edits before finalizing:
- ...

Final assessment:
- ...
```

## Review criteria

Check for:

- Captures Leon's actual intent: all projects should use this as a foundational meta-strategy, tunable by weights.
- Does not overclaim that the scorecard is implemented.
- Does not weaken Build Arena readiness boundaries or imply broad autonomous loops are now safe.
- Keeps GitHub Wiki correctly positioned as projection/navigation rather than canonical truth.
- Includes the right dimensions: docs, AI-agent usability, verification, architecture/spec/contracts, decision history, backlog/governance, security/supply-chain, operations/rollback.
- Makes the skill usable without causing heavyweight ceremony for trivial tasks.
- Separates durable user preference from project-specific Build Arena instructions.
- Includes enough acceptance criteria to become a real backlog item.
- Avoids contradictions between spec, skill, and AGENTS.md.
- Identifies any missing source references, tests, verification expectations, issue/backlog tracking, or implementation-slice risks.

Do not modify files. This is review only.
