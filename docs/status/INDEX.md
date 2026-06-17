# Status Doc Index

Status docs are dated, point-in-time records. This index is the source of truth for which docs describe current reality and which are retained as historical evidence.

Maintenance rule: when a status doc's feature or run state changes, either update the doc in place and keep it under Active, or move it to Superseded/Historical with a successor or reason. Active docs tracked in git must not claim `not committed` or `implemented locally` after they have landed in `main`. Do not move a doc to Historical just to hide a still-active stale claim; Historical is for point-in-time evidence, not current-state truth.

## Active

- `2026-06-16-project-graph-call-inheritance-treesitter.md` — project graph call/inheritance and JS/TS tree-sitter extraction; merged via PR #40 / 360e9a2.
- `2026-06-15-full-autonomy-gap-remediation-implementation-status.md` — current implementation status for the first full-autonomy gap-remediation slice.

## Superseded

- `2026-06-14-live-repo-goal-loop.md` → `2026-06-15-current-status-timeline-production-readiness.md` — pre-production-run readiness snapshot superseded by the June 15 production-readiness audit.
- `2026-06-14-progress-timeline-and-production-readiness-audit.md` → `2026-06-15-current-status-timeline-production-readiness.md` — pre-production-run audit superseded after the bounded fmc-mcp production-live attempt.

## Historical

- `2026-06-15-current-status-timeline-production-readiness.md` — point-in-time audit with captured dirty-state and run evidence; use current git/docs before treating its repository-state details as live.
