# Decision: verification evidence retention

Date: 2026-06-11

## Decision

The `docs/verification` corpus is intentionally retained for now. A live count on
2026-06-11 found 1043/1218 tracked files under `docs/verification`, so the
corpus clearly dominates the tree. This batch records the policy and guardrail;
it does not prune evidence.

Existing in-tree evidence remains immutable unless a separate operator-approved
migration is planned and verified. Future bulky evidence should prefer summary
reports, manifests, and hash pointers over committing entire generated snapshot
trees. Full trees may still be retained when auditability requires exact local
artifacts, but that should be an explicit exception with a short rationale.

## Migration stance

The current stance is non-destructive migration. If the project later moves old
snapshots to an artifact store, the migration must preserve enough manifests and
hash pointers for a fresh agent or operator to verify what was moved, where it
lives, and which report or run it supports.

## Consequences

- Do not delete `docs/verification` files as incidental cleanup.
- New verification work should normally produce concise summary reports plus hashes.
- Any future pruning must be a dedicated change with verification, not a hidden
  side effect of unrelated implementation work.
