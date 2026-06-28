# Status Doc Index

Status docs are dated, point-in-time records. This index is the source of truth for which docs describe current reality and which are retained as historical evidence.

Maintenance rule: when a status doc's feature or run state changes, either update the doc in place and keep it under Active, or move it to Superseded/Historical with a successor or reason. Active docs tracked in git must not claim `not committed` or `implemented locally` after they have landed in `main`. Do not move a doc to Historical just to hide a still-active stale claim; Historical is for point-in-time evidence, not current-state truth.

## Active

- `2026-06-27-experiment-lane-divergent-hypothesis-admissibility-status.md` — local implementation status for the dream/v1 divergent-hypothesis admissibility contract and fixture replay gate.
- `2026-06-26-decomposer-v1-hardening-status.md` — local implementation and Opus certification status for Decomposer v1 hardening and legacy compatibility removal.
- `2026-06-23-dream-proposer-tier3-implementation-status.md` — local implementation status for the tier-3 advisory dream proposer lane.
- `2026-06-18-proposer-architecture-fitness-status.md` — in-progress status for the proposer architecture-fitness extension slice.
- `2026-06-16-project-graph-call-inheritance-treesitter.md` — project graph call/inheritance and JS/TS tree-sitter extraction; merged via PR #40 / 360e9a2.
- `2026-06-15-full-autonomy-gap-remediation-implementation-status.md` — current implementation status for the first full-autonomy gap-remediation slice.

## Superseded

- `2026-06-14-live-repo-goal-loop.md` → `2026-06-15-current-status-timeline-production-readiness.md` — pre-production-run readiness snapshot superseded by the June 15 production-readiness audit.
- `2026-06-14-progress-timeline-and-production-readiness-audit.md` → `2026-06-15-current-status-timeline-production-readiness.md` — pre-production-run audit superseded after the bounded fmc-mcp production-live attempt.

## Historical

- `2026-06-17-fmc-mcp-schema-fix-status.md` — point-in-time record for the Grok 4.3 high-reasoning universal concern category/id schema fix and decomposition-only rerun.
- `2026-06-15-current-status-timeline-production-readiness.md` — point-in-time audit with captured dirty-state and run evidence; use current git/docs before treating its repository-state details as live.
