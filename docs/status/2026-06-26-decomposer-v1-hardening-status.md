# Decomposer v1 hardening status — 2026-06-26

Status: local implementation and Opus certification complete; PR/merge lifecycle pending.

Scope: harden `project-model/v1` as the active shared contract and remove the legacy compatibility runtime/docs/tests.

Implemented changes:

- Removed active v0 runtime surfaces from `arena/decomposer.py`, `arena/project_decomposer_ai.py`, and `arena/project_model_v1.py`.
- Removed the active legacy module/schema/test.
- Hardened `docs/schemas/project-model-v1.schema.json` so `iterationReadiness` is top-level required and `compatibility` is not part of the v1 contract.
- Added `docs/project-model-v1.md` as the active human reference and `docs/examples/project-model-v1-tiny.json` as a schema-valid example.
- Archived old active v0 docs/examples/reports/prompts/plans under `docs/archive/`.
- Updated active orientation/status/spec tests and docs to describe v1 as the only active shared project-model output.

Local verification run:

- `make generated` — PASS; generated/protected diff proof was empty afterward.
- Active v0 grep-clean excluding `docs/verification`, `docs/archive`, and `arena/generated` — PASS; no matches.
- Focused schema/off-path/docs tests: `uv run pytest tests/test_project_model_v1_contract.py tests/test_project_decomposer.py tests/test_project_decomposer_ai.py tests/test_coverage_closure.py tests/test_project_status_docs.py tests/test_proposal_run.py -q` — PASS.
- Full suite: `uv run pytest tests -q` — PASS.
- Lint: `uv run ruff check .` — PASS.
- Type check: `uv run pyright` — PASS; only upstream pyright-version notice.
- Whitespace: `git diff --check` — PASS.
- Protected-path diff proof: `git diff --name-status -- scorer verifier schema .arena/scorer.lock.toml arena/generated dashboard/src/lib/generated` — PASS; no output.

Certification:

- Claude Code Opus certification retry artifact is retained local-only under ignored `.arena/artifacts/`; the public PR carries this sanitized verdict summary instead of raw model JSON.
- Verdict: `PASS`.
- Blockers: none.
- Required pre-PR patches: none.
- Non-blocking review notes patched before PR: removed brittle line-number citations from `docs/project-model-v1.md` and added an archive banner to the old v0 mentor runbook.

Next gate:

- Push PR, watch CI, merge, clean branch, and verify `origin/main`.
