# Decision: keep decomposer universal-concern drift repair, document CI misconception

Date: 2026-06-24
Status: accepted / keep-but-document

## Context

A merged dream-package PR included an `arena/project_decomposer_ai.py` delta. The operator remembered the change as possibly “for identifying CI.” Forensics against git and repository evidence did not support that interpretation.

Evidence summary:

- `git diff 871c530d207bd95b821ef195159641a5e89ef204..HEAD -- arena/project_decomposer_ai.py` shows a pure move of the universal-concern normalizer functions, a prompt change from `>=8` to `>=6` responsibility words, and a universal cross-cutting-concern prompt rewrite that enumerates canonical categories.
- `git show 1c8d8c8 --stat` identifies the lineage as `Fix live decomposer universal concern drift`.
- `docs/status/2026-06-17-fmc-mcp-schema-fix-status.md:5` states the scope as universal `cross_cutting_concerns` category/id drift.
- The actual CI work is separate: `arena/ci_workflow.py` / `tests/test_ci_workflow.py` from commit `083ce51 feat: add deterministic CI workflow proposal domain`.

## Decision

Keep the decomposer change, but treat it as a universal-concern drift repair and prompt/gate alignment change — not a CI-identification change.

Specific interpretation:

1. `_normalise_universal_concern_id` and `_normalise_cross_cutting_concerns` are a deterministic repair layer for exact universal-concern id/category drift.
2. The `>=8` -> `>=6` prompt change aligns the prompt with the deterministic gate (`project_model_gate.py` rejects fewer than 6 words), while still requiring semantic responsibilities.
3. Universal concern `provenance_refs` backfill copies real provenance refs from covered components. It is not model-cited provenance. The raw model output remains persisted unchanged, so the repair remains auditable.

## Consequences

- Future docs and reviews must not describe this change as CI discovery.
- If provenance strictness is tightened later, distinguish “model cited this field” from “deterministic repair derived this field from model-covered components.”
- The anti-fabrication boundary remains: invented identifiers still fail; unknown category drift still fails; non-universal empty provenance is not backfilled.
- Any future redesign of provenance citation semantics is separate work; this decision only records the current repair’s intent and boundary.
