# Arena-calibration decomposer evaluation

Date: 2026-06-01

## Scope

Evaluate the merged Build Arena project decomposer against `/home/leonb/projects/arena-calibration` and obtain read-only external reviews from Grok Build and Claude Opus.

## Artifacts

- Full model JSON: `docs/verification/2026-06-01-arena-calibration-decomposer-model.json`
- Local evaluation JSON: `docs/verification/2026-06-01-arena-calibration-decomposer-local-evaluation.json`
- Full prompt package: `docs/verification/2026-06-01-arena-calibration-model-review-prompt.md`
- Distilled prompt package: `docs/verification/2026-06-01-arena-calibration-model-review-prompt-distilled.md`
- Grok Build prompt: `docs/verification/2026-06-01-arena-calibration-model-review-prompt-grok.md`
- Grok Build review: `docs/verification/2026-06-01-grok-build-arena-calibration-model-review.md`
- Grok Build stderr/auth-noise capture: `docs/verification/2026-06-01-grok-build-arena-calibration-model-review.stderr`
- Opus review JSON: `docs/verification/2026-06-01-opus-arena-calibration-model-review.json`
- Opus review markdown: `docs/verification/2026-06-01-opus-arena-calibration-model-review.md`

## Mechanical results

Decomposer command:

```bash
uv run python -m arena.decomposer \
  --project /home/leonb/projects/arena-calibration \
  --project-id arena-calibration \
  --output docs/verification/2026-06-01-arena-calibration-decomposer-model.json
```

Output:

- Size: 71,316 bytes
- SHA-256: `d8d1614af725c989d8a390b5d2df1e3b8c40b20d0e35f008b545479eae59ca16`
- Validation: valid
- Included files: 83
- Excluded files: 0
- Coverage: 83/83 owned, no unowned files, no multiply-owned files
- Components: 9
- Contracts: 4
- Verification gaps: 2

Expected fail-on-gap behavior:

```bash
uv run python -m arena.decomposer \
  --project /home/leonb/projects/arena-calibration \
  --project-id arena-calibration \
  --output /tmp/arena-calibration-gap-check.json \
  --fail-on-gap
```

Returned exit code `3` with stderr: `decomposition model has 2 verification gap(s)`.

## Local verification commands run

Build Arena:

- `uv run pytest tests/test_project_decomposer.py -q` passed: 17 tests
- `uv run pytest tests -q` passed: 98 tests
- `uv run ruff check .` passed
- `uv run pyright` passed

Arena-calibration:

- `uv run pytest tests -q` passed: 47 tests
- `uv run pytest --collect-only -q` collected 47 tests
- `uv run pytest -q` passed: 47 tests
- `uv run python exercise_verifier.py` ended with `ALL HARNESS PREDICTIONS HOLD`
- `uv run python -m py_compile $(git ls-files '*.py')` passed
- `uv run python -m arena.runner --llm-provider xai --dry-run` reported 168 total model calls and did not require keys
- `git diff --check` passed
- `git status --short --branch --untracked-files=all` was clean for arena-calibration

## Model contents summary

Components:

1. `documentation_and_operator_guidance`
2. `fixture_manifest_model`
3. `mechanical_scorer`
4. `package_marker`
5. `project_configuration`
6. `provider_boundary`
7. `reasoning_ablation_verifier`
8. `regression_tests`
9. `runner_discrimination_matrix`

Contracts:

1. `fixture_manifest_to_scorer`
2. `provider_boundary_to_verifier`
3. `scorer_to_runner`
4. `verifier_to_runner`

Verification gaps:

1. `doc_spec_drift_check_missing` on `documentation_and_operator_guidance`
2. `patch_generalization_axis_missing` on `reasoning_ablation_verifier`

The expected F3 gap is present as `patch_generalization_axis_missing`.

## External review synthesis

### Grok Build

Verdict: `PASS_WITH_WARNINGS`

Grok's main findings:

- The decomposer is a sound Stage 0/pre-loop calibration artifact.
- It correctly elevates `patch_generalization_axis_missing` on `reasoning_ablation_verifier` as the high-severity F3 signal.
- It records 100% file ownership and clear component/contract structure.
- The documentation drift gap is real but not blocking at this phase.
- The model records checks but does not execute them, which is the intended decomposer scope.
- Recommended ensuring downstream consumers treat `verification_gaps`, especially `patch_generalization_axis_missing`, as a hard precondition for promotion decisions.

Note: Grok Build review was run on a JSON-only summary with no file paths because path/full-artifact prompts caused Grok to attempt a read_file tool and hit unrelated MCP auth warnings. The successful Grok review used the same components/contracts/gaps/coverage/local-validation facts from the full model.

### Opus

Verdict: `PASS_WITH_WARNINGS`

Opus agreed that the model is suitable as Stage 0/pre-loop decomposition and that F3 is correctly exposed first-class, but raised several stronger structural warnings:

Important findings:

1. `fixture_manifest_model` currently owns the calibration fixture data and has an improvement fingerprint template over all 45 fixture files, including `fixtures/F3_bad_passes_tests/manifest.yaml` and `fixtures/F3_bad_passes_tests/patch.diff`. If a future optimization loop is allowed to edit those files, it can game the calibration by changing ground truth.
2. There is no explicit scorer-promote-to-verifier contract. The model captures scorer-to-runner short-circuiting on reject, but does not state the complementary invariant that scorer promotion must route through verifier rather than being accepted directly.
3. No executable check can currently catch F3. The gap is correctly recorded, but the proposed patch-generalization axis is still free text rather than a runnable check.

Minor findings:

- `reasoning_ablation_verifier` has a check referencing `exercise_verifier.py`, but that file is owned by `runner_discrimination_matrix`, creating hidden ownership/check coupling.
- `mechanical_scorer` has no gap annotation for its known absence of held-out/generalization checking.
- Component `purpose` fields are all null.
- The fixture set is modeled as one 45-file monolith instead of splitting F1/F2/F3/F4 or immutable fixture data from fixture-loading code.

I verified Opus's structural claims directly against the JSON model after review.

## Overall verdict

`PASS_WITH_WARNINGS`.

The decomposer build is successful for the arena-calibration pilot: it emits a valid, deterministic, mechanically validated project model and correctly exposes the required F3 `bad_passes_tests` gap as `patch_generalization_axis_missing` on `reasoning_ablation_verifier`.

However, it is not yet safe to let an optimization loop freely act on every modeled component/fingerprint. Before using this as active loop input, freeze fixture ground-truth files and add an explicit promote-to-verifier routing contract. Before claiming the loop can discriminate F3, implement the patch-generalization gap as a runnable check.

## Recommended next actions

1. Mark calibration fixture data immutable/out-of-scope for optimization. Split fixture loader code from fixture ground-truth data or remove fixture data from improvement fingerprint templates.
2. Add an explicit contract that scorer promotion must route through verifier; only scorer rejection may short-circuit.
3. Convert `patch_generalization_axis_missing` from proposed text into an executable mechanical check: held-out generated inputs, patch-locality bounds, and/or AST literal/test-input memorization detection.
4. Resolve the `exercise_verifier.py` ownership/check coupling, either by moving ownership to the verifier component or modeling the dependency as a contract.
5. Fill component `purpose` fields and add a scorer annotation for the known no-held-out/generalization limitation.
6. Ensure downstream Build Arena loop code treats non-empty `verification_gaps` as promotion blockers or explicit budgeted work items, not as informational notes.
