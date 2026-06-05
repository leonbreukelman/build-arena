# F3 Project Model mentor run report

Primary task: https://github.com/leonbreukelman/build-arena/issues/3
Run directory: `docs/verification/2026-06-03-issue-3-project-model-v0-emit/`

## Milestone: Bootstrap complete

What I did:
- Ran the runbook bootstrap/safety checks from `/home/leonb/projects/build-arena`.

Evidence:
- Branch: `coverage-100`
- Commit: `df3d1c7`
- Required local contract files were present:
  - `docs/project-model-v0.md`
  - `docs/schemas/project-model-v0.schema.json`
  - `docs/examples/project-model-v0-code-adjacent.json`
  - `docs/examples/project-model-v0-process-strategy.json`
- Required cross-repo paths were present:
  - `/home/leonb/projects/elenchus-core/docs/api-project-model-v0.md`
  - `/home/leonb/projects/arena-calibration/fixtures/project_model_v0`
- Required decomposer flags were present:
  - `--format`, `--source-task`, `--primary-backlog-item`, `--repo`, `--issue`, `--output`, `--fail-on-gap`
- Quality-gate import passed:
  - `from arena.project_model_v0 import evaluate_quality_gate`

Interesting result:
- The working tree already had many untracked docs/playbooks/verification artifacts before this run. I did not touch or stage those unrelated files.

## Milestone: Task understood

Plain-English goal:
- Build Arena should emit a mechanically checkable Project Model v0 from issue #3 before planning/architecture/code work begins.

What success changes:
- The issue #3 backlog task becomes a concrete Project Model with components, checks, dependencies, invariants, gaps, and advisory handoff data.

Likely in scope:
- Project Model v0 emission.
- Local deterministic quality-gate behavior.
- No-live-API/default deterministic behavior.
- Documentation of Elenchus/arena-calibration consumption boundaries.

Likely out of scope:
- Live paid LLM/API calls.
- Elenchus truth/oracle behavior.
- arena-calibration fixture harness implementation.
- Dashboard control-plane implementation.

Main F3 risk:
- A coherent plan could optimize around visible file ownership or generated artifacts while missing the actual Project Model responsibility boundaries and cross-repo advisory contract.

## Milestone: Project Model emitted

Artifacts:
- Primary task: `primary-task.md`
- Initial generated model: `project-model-v0.json`
- Decomposer stdout: `decomposer.stdout.txt`
- Decomposer stderr: `decomposer.stderr.txt`

Command summary:
- `uv run python -m arena.decomposer --project /home/leonb/projects/build-arena --format project-model-v0 --source-task <issue #3 text> --primary-backlog-item https://github.com/leonbreukelman/build-arena/issues/3 --repo leonbreukelman/build-arena --issue https://github.com/leonbreukelman/build-arena/issues/3 --output docs/verification/2026-06-03-issue-3-project-model-v0-emit/project-model-v0.json`

Result:
- Exit code: 2
- The CLI still wrote valid JSON.
- Initial model: `schemaVersion: project-model/v0`, 5 components, 2 verification gaps, 24 unclassified project surfaces.

Why this matters:
- This exercised the runbook's rule that a failing quality gate can still leave a useful artifact. The model exposed exactly where the decomposition was incomplete.

## Milestone: Model quality gate checked

Artifacts:
- Initial quality gate: `quality-gate-report.json`
- Revised/classified model: `project-model-v0-classified.json`
- Revised quality gate: `quality-gate-report-classified.json`

Initial quality-gate result:
- Failed with `unclassified_project_surface`.
- The model left 24 surfaces unclassified, including calibration fixtures, runtime/scorer lock config, generated schema/dashboard artifacts, and `schema/arena.yaml`.

Repair applied after the operator response timed out and the tool instructed me to use best judgment:
- Classified the 24 surfaces into four explicit components:
  - `calibration_fixture_data`
  - `runtime_and_lock_configuration`
  - `schema_and_generated_contracts`
  - `dashboard_placeholder_contract`
- Added observable checks for each new component.
- Removed the unclassified-surface gap.
- Preserved a manual-review assumption: `manual_surface_classification_pending_operator_review`.

Revised quality-gate result:
- Passed.
- `quality-gate-report-classified.json` contains `{ "findings": [], "passed": true }`.

## Milestone: Project Model walkthrough

The model says the real goal is:
- Emit Project Model v0 from Build Arena issue #3 before planning, architecture, or code work.

The load-bearing components are:
1. `documentation_and_operator_guidance`: docs/spec/playbook guidance, observed by `documentation_and_operator_guidance_verification_gap_observed`.
2. `project_configuration`: repo configuration, observed by `project_configuration_check`.
3. `python_package`: source package behavior, observed by `python_compile_check`.
4. `regression_tests`: test surface, observed by `regression_tests`.
5. `calibration_fixture_data`: in-repo calibration patch fixtures and expected labels, observed by `calibration_fixture_data_check`.
6. `runtime_and_lock_configuration`: arena runtime config/tooling/scorer lock boundary, observed by `runtime_and_lock_configuration_check`.
7. `schema_and_generated_contracts`: LinkML schema and generated artifacts, observed by `schema_and_generated_contracts_check`.
8. `dashboard_placeholder_contract`: placeholder/generated dashboard surfaces without implementing the dashboard control plane, observed by `dashboard_placeholder_contract_check`.

The ordering/dependencies are:
- Python package feeds regression tests.
- Project configuration informs docs, Python package, and regression tests.
- Calibration fixture data feeds regression tests.
- Runtime/lock configuration informs the Python package.
- Schema/generated contracts feed Python package and dashboard placeholder/generated surfaces.

The invariants are:
- Every included file is owned exactly once or the model is invalid.
- Emission and validation do not require live paid LLM/API calls.

The held-out probes are:
- None in this model. No component is marked high-risk after classification; near-neighbor alternatives carry the main F3 traps instead.

The biggest F3 traps are:
- Skipping the Project Model and starting implementation directly.
- Treating file ownership coverage as the whole decomposition.

My confidence:
- Medium. The deterministic quality gate now passes, but the revised classification is still an operator-review assumption and the docs/spec drift check remains a medium verification gap.

Decision needed:
- Leon should approve this revised Project Model v0 as the run contract, or correct the goal/components/checks before implementation/proposal work begins.

## Current stop/approval gate

I have not frozen the model and have not moved to candidate proposal, Elenchus advisory preflight, or TDD implementation.

Reason:
- The runbook requires explicit operator approval before freezing the Project Model. The revised model includes a manual classification assumption that Leon has not approved yet.

Recommended next step:
- Approve `project-model-v0-classified.json` as the run contract, or correct any component/check before I freeze it and write the candidate implementation proposal.
