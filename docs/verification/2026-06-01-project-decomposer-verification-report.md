# Project Decomposer Verification Report

Date: 2026-06-01
Worktree: `/home/leonb/projects/build-arena/.arena/worktrees/project-decomposer`
Pilot target: `/home/leonb/projects/arena-calibration`

## Commands run

```bash
uv run pytest tests -q
uv run ruff check .
uv run pyright
uv run python -m arena.decomposer --project /home/leonb/projects/arena-calibration --output /tmp/arena-calibration-project-model.json
```

## Results

- pytest: passed, 98 tests
- ruff: passed
- pyright: passed, 0 errors
- CLI decomposer: passed
- Python API validation: `validate_project_model(decompose_project('/home/leonb/projects/arena-calibration')).valid == True`
- Post-PR Copilot review fix: missing or non-directory `--project` paths now fail explicitly before git/filesystem inventory, with regression tests.

## Pilot output summary

- output file: `/tmp/arena-calibration-project-model.json`
- output bytes: 71316
- project_id: `arena-calibration`
- schema_version: `project-model/v0.1`
- git inventory mode: `git`
- git dirty: `False`
- included files: 83
- excluded files: 0
- unowned included files: 0
- components: 9
  - `documentation_and_operator_guidance`
  - `fixture_manifest_model`
  - `mechanical_scorer`
  - `package_marker`
  - `project_configuration`
  - `provider_boundary`
  - `reasoning_ablation_verifier`
  - `regression_tests`
  - `runner_discrimination_matrix`
- contracts: 4
  - `fixture_manifest_to_scorer`
  - `provider_boundary_to_verifier`
  - `scorer_to_runner`
  - `verifier_to_runner`
- verification gaps: 2
  - `doc_spec_drift_check_missing` on `documentation_and_operator_guidance`
  - `patch_generalization_axis_missing` on `reasoning_ablation_verifier`, with evidence from `fixtures/F3_bad_passes_tests/manifest.yaml`

## Callable usage

CLI:

```bash
uv run python -m arena.decomposer --project /path/to/project --output /tmp/project-model.json
```

Python API:

```python
from arena.decomposer import decompose_project, validate_project_model

model = decompose_project('/path/to/project')
report = validate_project_model(model)
assert report.valid
```
