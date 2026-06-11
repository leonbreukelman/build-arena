I attempted to verify the plan's code-level claims (existence/behavior of `build_fixture_model_output`, `ObservableCheck`, gate logic) but no Python LSP server is available and remote file access wasn't permitted. This review is therefore of the plan text against the five criteria; I flag where an unverified code assumption matters.

---

## 1. Verdict

**SIGN_OFF**

The plan is project-agnostic by construction, targets the correct pipeline, is genuinely TDD-structured, preserves the no-live/no-paid/safety constraints, and has a concrete CMMC rerun/comparison/iteration loop. The remaining concerns are refinements that the plan's own iteration structure will surface; none fundamentally violates a criterion.

## 2. Blocking issues

None.

## 3. Non-blocking improvements

**a. Test fixtures structurally mirror CMMC — weakens the anti-overfitting proof (criterion 1).** Phase 2/3 synthetic repos use `app/backend/pyproject.toml` (Python) + `app/frontend/package.json` (Node) — i.e., CMMC's exact topology. Phase 4's rename/isomorphism test only proves *id-relabeling* invariance, not *shape* invariance. An implementation could pass every test while being quietly tuned to "one Python root + one Node root under `app/`." Add at least one structurally different fixture to discovery/clustering tests: e.g., 3+ roots, different languages (Rust/Go), and a nested/container monorepo. This is the single most important addition to substantiate "project-agnostic."

**b. Backward-compat default for `execution_status` may silently invalidate or relax existing accepted checks (criteria 2 & 4).** Section 4.1 defaults legacy checks to `statically_validated`, but the canonical acceptance rule requires `execution_proven OR proof_artifact`. A legacy check that was previously acceptance-allowlisted would, under the new rule + default, *lose* acceptance — or, if the gate is loosened to tolerate it, that is a gate relaxation. The hedge "unless acceptance metadata requires stronger validation" is too vague. Pin this down: legacy checks that were acceptance-allowlisted must deterministically map to `execution_proven` (or carry a proof_artifact), and Phase 1 should add an explicit red test that a previously-accepted legacy snapshot remains accepted (not just "loads with defaults").

**c. Safety classification of `npm run build` / test commands (criterion 4).** Marking script-declared build/test commands `safe_by_default` is too generous: `npm run build` on a cold cache may trigger dependency resolution/network, and build scripts can run arbitrary lifecycle hooks. The decomposer not executing them (6.3) mitigates risk for snapshot generation, but the *classification* still feeds acceptance. Specify that commands implying install/network/lifecycle hooks are `requires_network`/`unknown`, not `safe_by_default`, unless dependencies are provably already resolved.

**d. Clustering specificity (criterion 3).** Section 7.3's "many modules should produce multiple components" and 7.4's "not fixed to an arbitrary cap" are negative/under-specified for TDD. Replace with a concrete assertion, e.g., per root, component count ≥ number of stable top-level source subdirectories (minus excluded classes), and every primary node is owned-or-gapped. A negative "no fixed cap" assertion is hard to make meaningful.

**e. Proof-artifact wiring is left optional.** Section 6.3/12 say the model "can reference those proof artifacts… if supported by the implementation; if not… treat execution proof as external validation." Decide this before implementation rather than at report time, because it directly determines whether the regenerated CMMC model can pass its own acceptance gate or is expected to remain gapped.

## 4. Implementation constraints

- Implement strictly via the listed TDD phases; each red test must precede its green code. Do not skip Phase 1 backward-compat tests.
- All new logic lives in the AI-first snapshot path (`build_fixture_model_output` / new `project_meta_decomposer.py`). Do **not** extend `arena/decomposer.py`, and do not add any repo-identity (CMMC/FMC/Build-Arena) or hardcoded-component branch in decomposition logic.
- No live/recorded-to-live, paid-API, network, deploy/publish, destructive, or credential-touching command may be invoked by the decomposer or as an acceptance check. CMMC target checks in §12 are run **manually by the operator** in the clean worktree and captured as external proof artifacts — not by the pipeline.
- Do not relax existing Project Model gates to make the regenerated model pass; gate changes may only *strengthen* (execution-dir presence, safety, status consistency) and must preserve legacy-snapshot loadability.
- Determinism is mandatory: sorted/tie-broken roots, ids, ownership, contracts; the two-run identical-output test (Phase 3) and rename-isomorphism test (Phase 4) must pass.
- Anti-identity lint must be scoped to decomposition source files only (not docs/verification artifacts) and run in CI (`make verify`).
- CMMC rerun must confirm the worktree is synced to remote HEAD; comparison must populate every §12 metric and be written to the specified compare path.

## 5. Short rationale

The plan cleanly separates generic, evidence-driven mechanics (manifest-rooted discovery, deterministic clustering, edge-derived contracts, coverage repair) from project identity, and explicitly forbids the prior calibration/identity branches and the spurious root-level `uv run pytest -q`. It targets the right entry point and enumerates the schema/gate/projection files that must change, with backward-compatible defaults. The TDD sequence is specific enough to implement and ends in full verification. Safety is preserved primarily because the decomposer never executes checks — it only statically validates them — keeping snapshot generation offline; the §12 CMMC proofs are operator-run and stored as artifacts. The §12–§14 rerun/compare/iterate loop with concrete metrics and a generic-only stop condition is sound. The flagged items (CMMC-shaped fixtures, legacy `execution_status` default, build/test safety classing, clustering thresholds, proof-artifact wiring) are concrete but addressable within the existing TDD structure and do not undermine the design, hence sign-off with required follow-ups rather than revision.
