# Phase 5 — Project Decomposer

## Goal

Build a deterministic Project Decomposer that a project can call before the normal Build Arena loop. It scans filesystem and git ground truth, emits a structured project model, and makes the model ready for calibration against `arena-calibration`.

First target: `/home/leonb/projects/arena-calibration`.

## Design changes adopted from Opus review

- Coverage is total over tracked files, but tracked files are classified as either owned or excluded with a typed reason. Source coverage requires zero unowned included files; runtime/generated/docs artifacts can be explicitly excluded or owned by docs/config components.
- Mechanical checks and contract edges are validated for referential integrity instead of accepted as arbitrary strings.
- Arena-specific facts, especially the F3 patch-generalization gap, are derived from fixture manifests rather than hardcoded prose.
- Decomposition does not execute tests, runners, or live APIs. It only reads files and runs read-only git discovery commands.

## Public interface

1. Python API:
   - `from arena.decomposer import decompose_project, validate_project_model, canonical_project_model_json`
   - `decompose_project(project_root: Path, project_id: str | None = None) -> ProjectModel`
   - `validate_project_model(model: ProjectModel) -> DecompositionValidationReport`
2. CLI:
   - `uv run python -m arena.decomposer --project /path/to/project --output /tmp/model.json`
   - `--output -` writes canonical JSON to stdout.
   - `--fail-on-gap` exits non-zero when the validated model contains verification gaps.

## Output model shape

Pydantic-backed, JSON-serializable, deterministic ordering:

- `schema_version`: `project-model/v0.1`.
- `project_id`: explicit ID or root directory name.
- `project_root`: absolute resolved path used for scan.
- `git`: availability, toplevel, HEAD OID, branch, dirty flag, dirty/untracked paths, and inventory mode.
- `file_inventory`: included files with raw-byte SHA-256 plus excluded files with typed reasons.
- `components`: decomposition units with owned files, responsibilities, mechanical checks, scoring dimensions, fingerprint templates, rollback boundaries, scope boundaries, and optional verification gaps.
- `contracts`: assume-guarantee edges between components. Each contract must have a mechanical check or an explicit verification gap.
- `cross_cutting_concerns`: orthogonal axes such as provider boundary, fixture integrity, determinism, and docs/spec sync.
- `verification_gaps`: first-class gaps; for arena-calibration, include the derived F3 patch-generalization gap.
- `coverage`: total tracked/inventoried files, included/owned/excluded counts, unowned included files, and exact coverage numerator/denominator.

The validation report is returned separately; it is not baked into canonical model bytes.

## Scanner rules

- Resolve git toplevel before inventory. If the requested project path is a subdirectory of a git repository, scan the toplevel rather than claiming partial coverage.
- Prefer `git ls-files` when git is available; fallback to filesystem traversal otherwise.
- Hash disk contents as raw bytes. If the tree is dirty, report `git.dirty = true` so HEAD and disk content are not conflated.
- Exclude by rule with a typed reason: `.git`, `.venv`, `__pycache__`, `.pytest_cache`, egg-info, `results`, coverage caches, build artifacts, generated review output, and runtime DB/log/archive files.
- No tracked file may disappear: every discovered path is either in `included_files` or `excluded_files` with reason.

## Arena-calibration detector

Triggered only when the project contains `arena/fixtures.py`, `arena/scorer.py`, `arena/verifier.py`, `arena/runner.py`, and `fixtures/*/manifest.yaml`.

Components:

1. `fixture_manifest_model`
   - Owns `arena/fixtures.py` and fixture manifests/reasoning/patch metadata.
   - Check: manifest files resolve and fixture tests are covered by `uv run pytest -q`.
2. `mechanical_scorer`
   - Owns `arena/scorer.py`.
   - Contract: consumes fixture measurement commands and emits fail counts/promote-reject verdicts.
3. `reasoning_ablation_verifier`
   - Owns `arena/verifier.py`, `arena/lanham.py`, `arena/patch_eq.py`.
   - Check: `uv run python exercise_verifier.py`.
4. `provider_boundary`
   - Owns `arena/llm.py`, `arena/api_llm.py`, `arena/cli_llm.py`, and provider tests by filename rule.
   - Check: provider wrapper tests only; no live spend by default.
5. `runner_discrimination_matrix`
   - Owns `arena/runner.py`, `exercise_verifier.py`.
   - Check: `uv run python -m arena.runner --dry-run --llm-provider xai`.
6. `regression_tests`
   - Owns remaining `tests/*.py`.
   - Check: `uv run pytest -q`.
7. `documentation_and_operator_guidance`
   - Owns docs, README, prompts/specs/plans/verification notes.
   - Gap if no mechanical doc/spec drift check exists.
8. `project_configuration`
   - Owns `pyproject.toml`, `uv.lock`, `.gitignore`, and package metadata files.
   - Check: `uv run pytest -q` and `uv run pyright` when available.
9. `package_marker`
   - Owns package marker files such as `arena/__init__.py`.
   - Check: import/package discovery via test suite.

F3 gap derivation:

- Read each fixture manifest.
- When a fixture has `ground_truth.scorer_should == promote` and `ground_truth.verifier_should == reject` and a rationale mentioning Lanham/patch generalization/hardcoding, emit gap `patch_generalization_axis_missing` against `reasoning_ablation_verifier`.
- Evidence includes the fixture ID and manifest path.

## Validation rules

`validate_project_model(model)` returns a structured report with errors/warnings/gap count.

Errors:

- included file is owned by zero or multiple components;
- excluded file has empty reason;
- component has no owned files;
- component has neither mechanical checks nor verification gaps;
- component check references missing paths/modules when resolvable;
- contract endpoint does not exist;
- contract has neither checks nor verification gaps;
- verification gap references a missing component;
- fingerprint template references missing files;
- rollback boundary has an empty stop condition;
- source coverage denominator is non-zero and owned included files do not equal included files.

Warnings:

- dirty tree;
- docs component has no mechanical drift check;
- filesystem fallback was used.

## TDD plan

1. Add failing tests in `tests/test_project_decomposer.py` for:
   - synthetic git project canonical model generation and exactly-one-owner coverage;
   - validation failures for unowned files, bad check references, missing contract endpoints, contract without checks/gaps, gap with missing component, and empty rollback stop condition;
   - deterministic double-run bytes;
   - raw-byte hash mutation;
   - no test/runner execution during `decompose_project`;
   - non-git fallback denylist;
   - CLI stdout/file/fail-on-gap behavior;
   - external integration against `/home/leonb/projects/arena-calibration` when present.
2. Implement Pydantic model classes and scanner in `arena/decomposer.py`.
3. Run targeted tests, then full checks.
4. Generate `/tmp/arena-calibration-project-model.json` from the real arena-calibration checkout and inspect validation-critical fields.
5. Ask Opus for a read-only implementation review and fix confirmed blockers.

## Acceptance criteria

- A project can call the decomposer through Python or CLI.
- The emitted model is canonical JSON with enough structure for a future arena calibration gate.
- The real arena-calibration model covers every included tracked file exactly once, records typed exclusions, has explicit contracts, contains mechanical checks or gaps for every component/contract, and derives the F3 patch-generalization gap from manifests.
- `uv run pytest tests/test_project_decomposer.py -q`, `uv run pytest tests -q`, `uv run ruff check .`, and `uv run pyright` pass.
