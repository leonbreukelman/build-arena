# Build Arena — Historical status snapshot

This file is superseded. It is kept only as a pointer so older references to
`docs/build-arena-current-state.md` do not lead a fresh agent into stale live
instructions.

For current Build Arena state, read these active sources instead:

1. `AGENTS.md` — active operating rules, boundaries, command reference, and current implementation status.
2. `README.md` — concise project status and CLI examples.
3. `docs/build-arena-project-brief.md` — architecture map, current blockers, and canonical orientation notes.

Last verified replacement: 2026-06-11.

## Why this file is not live truth

Earlier versions of this file were volatile per-session handoffs. That made it
easy for a dated calibration-run note to look authoritative after the project
moved on. Build Arena now keeps durable current-state claims in the active
orientation docs above and uses dated files under `docs/verification/` as point-
in-time evidence, not as live instructions.

If this file is ever made live again, update `tests/test_project_status_docs.py`
in the same change so stale path and status drift cannot silently return.
