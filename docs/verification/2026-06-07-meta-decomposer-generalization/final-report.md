# Meta-decomposer generalization final report

## Decision

Build Arena is now ready to perform an actual decomposition run using the fixture/meta-decomposer path.

Recommended next target: `/home/leonb/projects/fmc-mcp`.

Reason: it is a small, clean Python MCP-server repo with 19 non-cache/non-venv project files, a clean git status on `main`, a straightforward `src/` + `tests/` shape, and it already passes a dry Build Arena decomposition gate. This is the right first real target before using larger multi-root projects as stress tests.

Note: the user said `FMC-MPC`; the local repo found is `fmc-mcp`. No `/home/leonb/projects/*mpc*` match was found except this likely intended repo.

## Final CMMC stress-test baseline

Final CMMC snapshot:

`docs/verification/2026-06-07-meta-decomposer-generalization/artifacts/cmmc/snapshot-92b2bb5139d78b15/`

Final gate:

- `passed: true`
- `violation_count: 0`
- components: 35
- contracts: 57
- backend contracts: 43
- frontend contracts: 14
- observable checks: 2
- gaps: 0

Comparison against first CMMC model:

- first snapshot: `snapshot-25eb081bd3f1ba3b`
- first gate: failed with 70 violations (`inventory_coverage: 63`, `edge_coverage: 7`)
- first model components/contracts: 8 / 1
- final model components/contracts: 35 / 57
- final gate: passed with 0 violations

Comparison files:

- `docs/verification/2026-06-07-meta-decomposer-generalization/cmmc-final-comparison-summary.md`
- `docs/verification/2026-06-07-meta-decomposer-generalization/cmmc-final-comparison-summary.json`

## Implemented improvements

1. Added a project-agnostic meta-decomposer in `arena/project_meta_decomposer.py`.
2. Routed fixture model generation through the meta-decomposer in `arena/project_model_llm.py`.
3. Extended the Project Model v1 snapshot schema and JSON schema for observable check execution/safety/proof fields.
4. Added collision-resistant IDs with a hash suffix to avoid long-name truncation collisions.
5. Added Python src-root-relative import resolution so imports such as `assessment.text_analysis` resolve to fully-qualified graph symbols such as `app.backend.src.assessment.text_analysis`.
6. Guarded suffix matching so single-segment imports such as `html` do not falsely match unrelated files such as `index.html`.
7. Kept test-path symbols out of source components, routing them to verification/support components.
8. Added a self-surfacing unresolved-source-contract gap for multi-component roots with no source-to-source contracts.
9. Aligned `edge_coverage` with guarded suffix matching and changed source-side edge ownership to prefer direct graph node ownership over ancestor package-prefix inference.
10. Added regression coverage for all above fixes in `tests/test_project_meta_decomposer.py` and gate tests.

## Verification executed

Build Arena verification:

- `uv run pytest tests -q`: passed
- `uv run ruff check .`: passed
- `uv run pyright`: passed
- `make verify`: passed

CMMC final snapshot:

- command: `uv run python -m arena.project_model_cli snapshot --project /home/leonb/projects/.decomposition-targets/cmmc-level1-readiness-assistant ... --llm-mode fixture --overwrite`
- result: `snapshot-92b2bb5139d78b15`, gate passed, 0 violations

CMMC declared proof checks:

- `/home/leonb/projects/.decomposition-targets/cmmc-level1-readiness-assistant/app/backend`: `uv run pytest -q` exited 0
- `/home/leonb/projects/.decomposition-targets/cmmc-level1-readiness-assistant/app/frontend`: `npm test -- --run` exited 0

Proof files:

- `docs/verification/2026-06-07-meta-decomposer-generalization/artifacts/cmmc/snapshot-92b2bb5139d78b15/proof-runs/check.app-backend-python-tests.txt`
- `docs/verification/2026-06-07-meta-decomposer-generalization/artifacts/cmmc/snapshot-92b2bb5139d78b15/proof-runs/check.app-frontend-node-test.txt`

Opus reviews:

- `docs/verification/2026-06-07-meta-decomposer-generalization/opus/opus-cmmc-model-review.md`
- `docs/verification/2026-06-07-meta-decomposer-generalization/opus/opus-cmmc-model-review-final.md`
- `docs/verification/2026-06-07-meta-decomposer-generalization/opus/opus-cmmc-r1-closure.md`

Final Opus closure verdict:

- SIGN_OFF: YES
- R1 resolved: YES
- no new blocker introduced

## FMC-MCP candidate verification

Local candidate found:

`/home/leonb/projects/fmc-mcp`

Shape excluding `.git`, `.venv`, `.pytest_cache`, `.ruff_cache`, and `__pycache__`:

- 19 project files
- Python package under `src/fmc_mcp/`
- tests under `tests/`
- clean git status: `main...origin/main`

Build Arena dry decomposition:

- snapshot: `docs/verification/2026-06-07-meta-decomposer-generalization/artifacts/fmc-mcp/snapshot-4b632e983ebc77a0/`
- gate passed: true
- violation count: 0
- components: 7
- contracts: 1
- checks: 1
- gaps: 0

Candidate test execution:

- generated check `uv run pytest -q` fails because `pytest` is not spawnable through the current uv environment.
- `pytest` is present in the existing local venv and the project tests pass with `/home/leonb/projects/fmc-mcp/.venv/bin/python -m pytest -q`.
- result: 19 passed in 0.04s

Candidate readiness note: before using `fmc-mcp` as a full APPLY/PROMOTE target, either normalize its uv dev environment so `uv run pytest -q` works, or teach check discovery to prefer the project’s actual known test invocation when optional dev dependencies are not synced.

## Recommended plan for the first actual decomposition run

1. Use `/home/leonb/projects/fmc-mcp` as the first simple real target.
2. Run a fresh snapshot under a new verification directory.
3. Treat the generated model as the planning baseline only if the deterministic gate passes.
4. Run the project check using the currently working command: `.venv/bin/python -m pytest -q` from `/home/leonb/projects/fmc-mcp`.
5. Inspect the 7-component / 1-contract model for whether it is semantically useful or too coarse.
6. If useful, generate one small hypothesis/work item from it.
7. Only after that, move to larger multi-root projects such as CMMC again.

## Remaining non-blocking risks

1. Fixture probe is still scaffolding, not true adversarial proof. The held-out probe booleans are not yet independently computed.
2. Responsibility prose is still generic and directory-derived, not deeply semantic.
3. Matcher logic is duplicated across decomposer and gate; future drift is possible.
4. Single-segment import recall is conservative by design to avoid false positives.
5. Some gate exclusions remain repo-shaped and should eventually become config-driven.
6. The workspace currently contains many untracked verification artifacts from the iterative CMMC runs; final artifacts are clearly identified above, but cleanup/commit selection should be deliberate.

## Current repo state

Code and verification artifacts are present in the working tree. They have not been committed in this session.
