# Meta-decomposer PR packaging plan

Date: 2026-06-08
Project: Build Arena
Branch target: update the existing open PR branch `chore/decomposition-intake-housekeeping` rather than create a second overlapping PR.

## Goal

Package the local project-agnostic meta-decomposer work into a reviewable GitHub PR with only durable source, tests, plans, specs, and final verification evidence.

## Scope to include

Source and tests:

- `arena/project_meta_decomposer.py`
- `arena/project_model_llm.py`
- `arena/project_model_gate.py`
- `arena/project_snapshot.py`
- `docs/schemas/project-model-v1.schema.json`
- `tests/test_project_meta_decomposer.py`

Planning/spec/research:

- `docs/research/2026-06-07-project-agnostic-multi-root-decomposition.md`
- `docs/specs/2026-06-07-meta-decomposer-functional-spec.md`
- `docs/plans/2026-06-07-meta-decomposer-implementation-plan.md`
- this packaging plan

Verification evidence:

- initial failing CMMC decomposition baseline under `docs/verification/2026-06-07-cmmc-level1-decomposition/`
- final CMMC passing snapshot `snapshot-92b2bb5139d78b15`
- final FMC-MCP candidate snapshot `snapshot-4b632e983ebc77a0`
- final comparison summaries and final report under `docs/verification/2026-06-07-meta-decomposer-generalization/`
- Opus review/sign-off artifacts under `docs/verification/2026-06-07-meta-decomposer-generalization/opus/`

## Housekeeping exclusions

Do not commit intermediate CMMC rerun snapshots that are superseded by the final `snapshot-92b2bb5139d78b15` baseline:

- `snapshot-5f0cccffcd05c7d6`
- `snapshot-720fa50220b9fe5d`
- `snapshot-8cceaecfd2c6c540`
- `snapshot-975dafce4f66f985`
- `snapshot-b56809b1b6abc8a5`
- `snapshot-dd822196b18690b9`

Do not commit the earlier non-final comparison report files that reference superseded snapshots:

- `cmmc-comparison-report.md`
- `cmmc-comparison-summary.json`

## Verification gates before push

Run from the packaged branch:

- `uv run pytest tests/test_project_meta_decomposer.py -q`
- `uv run pytest tests -q`
- `uv run ruff check .`
- `uv run pyright`
- `make verify`
- `git diff --check`
- lightweight added-file secret/credential scan

## PR handling

- Stage explicit pathspecs only.
- Commit the meta-decomposer package on top of the existing PR branch.
- Push `chore/decomposition-intake-housekeeping`.
- Update PR #7 with a concise summary, verification evidence, and remaining risks.
- Do not merge or deploy in this pass.
