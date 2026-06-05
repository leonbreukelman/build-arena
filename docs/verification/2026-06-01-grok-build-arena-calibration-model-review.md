**Verdict: PASS_WITH_WARNINGS**

The decomposer ProjectModel is a sound Stage 0/pre-loop calibration artifact. It achieves complete file ownership, records contracts, and surfaces the critical F3 gap explicitly. The single high-severity item is the intended signal rather than a defect. The medium documentation warning is minor and expected at this phase.

**Strengths**
- 100% file coverage (83/83) with no unowned or multiply-owned files and zero local validation errors.
- Explicit, first-class recording of the patch-generalization gap tied directly to F3_bad_passes_tests with rich diagnostic evidence.
- Clear component boundaries and four typed contracts between core subsystems (manifest ↔ scorer, provider ↔ verifier, scorer/verifier ↔ runner).
- The high-severity gap is attributed to the correct component (reasoning_ablation_verifier) and paired with a concrete proposed check.
- Local validation correctly flags the documentation component's missing mechanical check while still marking the model valid.

**Findings by severity**

**High**
- `patch_generalization_axis_missing` in `reasoning_ablation_verifier` is correctly elevated. The provided evidence accurately describes the F3 failure mode: tests pass, Scorer promotes, but the patch is a non-generalizing lookup-table memorization that fails on held-out inputs of the same distribution. The JSON notes that Lanham-style reasoning checks alone are insufficient and that F3 exists precisely to motivate an orthogonal verifier axis (held-out generation, locality bounds, AST anti-patterns). This is the expected critical calibration signal.

**Medium**
- `doc_spec_drift_check_missing` on `documentation_and_operator_guidance`. The component owns 20 files and is treated as operator guidance, yet no mechanical drift checker exists. The local validation warning correctly surfaces this.

**Low / informational**
- Several components carry regression or exercise checks (fixture_loader, scorer, provider_boundary, runner_dry_run_plan, full_regression_tests, hermetic_verifier) but the model itself only records the existence of those checks; it does not execute tests. This matches the known decomposer scope.

**Missing/weak coverage**
- No mechanical documentation/spec drift check (already flagged).
- The patch-generalization axis is recorded as a gap with a proposed future check; it is not yet implemented. This is appropriate for pre-loop input.
- The JSON does not surface any test-execution results or live verification outcomes; the decomposer’s role is limited to static structural decomposition and gap registration, which is consistent with the stated expectation.
- No evidence of over-claiming test execution or false confidence in the verifier’s current discrimination power.

**Recommended next actions**
1. Keep the high-severity `patch_generalization_axis_missing` gap as the primary calibration signal for Phase 0/early loop runs; do not demote it until an orthogonal verifier axis (held-out tests, locality, or anti-memorization) is added and shown to reject F3-style patches.
2. Treat the documentation drift warning as a planned follow-up once the goal schema stabilizes; do not block loop entry on it.
3. Confirm that downstream consumers (runner, scorer lock, verifier harness) consume the `verification_gaps` list and treat `patch_generalization_axis_missing` as a hard precondition for promotion decisions.
4. After the first calibration loop iteration, re-export the ProjectModel and verify the same gap remains the dominant high-severity item and that no new gaps were silently dropped.

**One-sentence answer on F3 exposure**: Yes, F3_bad_passes_tests is correctly exposed first-class as the canonical motivating example for the high-severity `patch_generalization_axis_missing` gap in the reasoning_ablation_verifier component, with explicit evidence that the current verifier would accept it under reasoning checks alone.
