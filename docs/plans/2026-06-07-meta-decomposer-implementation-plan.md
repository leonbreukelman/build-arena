# Implementation Plan: Project-Agnostic Multi-Root Meta-Decomposer

Date: 2026-06-07
Project: Build Arena
Status: Signed off by Opus; amended with required non-blocking follow-ups
Basis:
- Research report: `docs/research/2026-06-07-project-agnostic-multi-root-decomposition.md`
- Functional spec: `docs/specs/2026-06-07-meta-decomposer-functional-spec.md`
- Opus sign-offs: `docs/verification/2026-06-07-meta-decomposer-generalization/opus/`

## 1. Objective

Replace the current fixture snapshot generator’s shallow single-root behavior with a project-agnostic, manifest-rooted, deterministic meta-decomposition pipeline that can handle multi-root repositories without project-specific logic.

The plan targets the Project Model snapshot path used by:

`uv run python -m arena.project_model_cli snapshot --llm-mode fixture`

That path currently calls `arena.project_model_llm.build_fixture_model_output`, which selected too few CMMC nodes and emitted a root-level `uv run pytest -q`. The older `arena/decomposer.py` contains hardcoded calibration behavior and should not be extended for CMMC; it may later be collapsed into the same generic approach, but this implementation pass focuses on the AI-first Project Model snapshot pipeline.

## 2. Non-goals

- Do not create a CMMC-specific decomposer.
- Do not add CMMC/FMC/Build-Arena identity branches.
- Do not hardcode CMMC component names or directories as semantic cases.
- Do not relax existing Project Model gates to make the model pass.
- Do not require live LLM/API calls.
- Do not run unsafe, networked, paid, deployment, publish, destructive, or credential-touching commands as acceptance checks.

## 3. Target files

Primary implementation files:

- `arena/project_snapshot.py`
  - Extend `ObservableCheck` with execution-directory and status semantics using backward-compatible defaults.

- `arena/project_model_llm.py`
  - Replace the shallow fixture model generator with a generic deterministic builder or delegate to a new helper module.
  - Preserve live/recorded/noop behavior.

- `arena/project_model_gate.py`
  - Strengthen gates for check execution-directory presence, safe acceptance checks, and status consistency.

- `arena/project_model_v1.py`
  - Ensure Project Model v1 exposes check execution-directory/status data.

- `arena/project_decomposer_ai.py`
  - Ensure artifact writing and v0 projection preserve or explain execution directory information.

Likely new helper module:

- `arena/project_meta_decomposer.py`
  - Generic manifest-root discovery.
  - Root-scoped task/check extraction.
  - Deterministic component clustering.
  - Edge-derived contract generation.
  - Coverage/gap generation helpers.

Tests:

- `tests/test_project_model_cli_ai.py`
  - CLI-level multi-root snapshot fixture.

- New `tests/test_project_meta_decomposer.py`
  - Unit tests for root discovery, check discovery, clustering, contracts, and anti-overfitting lint.

- Existing tests remain unchanged except where schema defaults require expected-output updates.

## 4. Data model changes

### 4.1 ObservableCheck compatibility

Add fields with backward-compatible defaults so existing JSON snapshots remain readable:

- `execution_dir`
  - Relative path from workspace root.
  - Default: `.` for legacy snapshots.

- `safety_status`
  - Values: safe_by_default, unsafe, requires_network, requires_paid_api, destructive, unknown.
  - Default: safe_by_default for legacy checks that already passed old acceptance gates.

- `execution_status`
  - Values: declared_only, statically_validated, execution_proven, gapped.
  - Default: execution_proven for legacy acceptance-allowlisted checks so old passing snapshots remain accepted; default statically_validated for non-acceptance legacy checks.

- `proof_artifact`
  - Optional path or id for a local proof artifact.
  - This is the single canonical proof-artifact concept for this pass. It may represent operator-supplied proof or a locally captured safe execution proof, but acceptance logic treats both the same way.

- `verification_gap_ids`
  - Optional gap ids explaining missing proof.

The canonical acceptance rule is:

`safe_by_default AND (execution_status == execution_proven OR proof_artifact is present)`

For this pass, generated fixture checks that are not executed by the decomposer are statically validated and should not be acceptance-allowlisted unless a proof artifact is attached. Legacy snapshots that already had accepted local checks keep backward-compatible acceptance through the execution-proven default, and new tests must prove that compatibility.

## 5. Generic root discovery

### 5.1 Root candidates

Discover root candidates from generic manifest evidence:

- Python: `pyproject.toml`, `setup.cfg`, `setup.py`, `requirements.txt` with source context.
- Node: `package.json` with source/test/build context.
- Rust: `Cargo.toml`.
- Go: `go.mod`.
- Make/task root: `Makefile` with source context.
- Workspace/container manifests: workspace-specific manifests or manifest files declaring child packages.

### 5.2 Root classification

Classify candidates as:

- executable root: has manifest/task evidence and source/test/build context.
- container root: workspace/orchestration evidence but child roots own nested source.
- synthetic root: source context exists without executable evidence.

### 5.3 Ownership rule

Assign each graph node with a path to the nearest enclosing executable root. Parent/container roots own workspace-level configuration and docs but not child source/test nodes.

### 5.4 Determinism

All candidate paths, root ids, and ownership assignments are sorted and tie-broken deterministically.

## 6. Generic check discovery

### 6.1 Extraction

For each root, discover candidate checks from root-local evidence:

- Node `package.json` scripts:
  - Prefer local task names: test, build, typecheck, lint.
  - Convert to package-manager commands based on lockfile/manager evidence where possible.
  - Classify script commands conservatively. A declared script is not automatically safe-by-default because package scripts can execute arbitrary lifecycle behavior. Commands with install, network, publish, deployment, env/secret, or shell-metaprogramming risk are unknown/unsafe/gapped. Local test/build commands may be statically validated only when the script body passes the generic safety parser, and they are not acceptance-proven unless a proof artifact exists.

- Python manifest/test evidence:
  - If tests exist under the root and Python project metadata exists, discover a pytest check.
  - Prefer `uv run pytest -q` when uv/pyproject evidence supports it.
  - Otherwise use a conservative statically-validated check or gap.

- Make/CI/task evidence:
  - Only model if command is safe and local by generic allowlist.

### 6.2 Safety boundary

The safe boundary is:

- no network by default;
- no paid API by default;
- no deployment/publish/release commands;
- no destructive filesystem/VCS operations;
- no credential/token/secret exposure;
- no shell metaprogramming that hides unsafe behavior.

### 6.3 Execution status

For snapshot generation, discovered checks are at least statically validated. If the decomposer itself does not run them, they are not acceptance-proven unless a proof artifact is attached.

During CMMC validation after implementation, we will run the backend/frontend commands manually and save proof outputs in the verification artifact directory. The implementation should support a proof-artifact field, but the decomposer must not manufacture proof. If proof-artifact ingestion is not wired into snapshot generation in this pass, generated checks remain statically validated and the external proof is reported separately rather than falsely upgrading model acceptance.

### 6.4 CMMC expected generic outcome

When applied to CMMC, generic root discovery should detect at least:

- one Python root from backend manifest evidence;
- one Node root from frontend manifest evidence.

Generic check discovery should produce root-scoped checks with execution directories under those roots. This expectation is generic because it follows manifest evidence, not project identity.

## 7. Generic component clustering

### 7.1 Node classification

Classify graph nodes into coverage classes:

- primary source
- primary test
- primary config/build
- documentation
- generated/protected/vendor/cache

### 7.2 Seeds

Within each root, form component seeds from:

- top source directories;
- package/module prefixes;
- manifest/config ownership;
- test-to-source edges;
- entrypoint-like files by generic evidence.

### 7.3 Deterministic grouping

For this pass, use deterministic root/directory/module-prefix grouping rather than probabilistic community detection. This is simpler, testable, and stable.

Rules:

- Components never cross roots.
- A root with multiple stable top-level source subdirectories should produce at least one component per non-excluded top-level source subdirectory unless deterministic cohesion evidence merges them.
- A root with a single package/module tree should produce at least one source component plus root/tooling/docs/test components where primary nodes require them.
- Config/build nodes attach to a root-level config/tooling component or nearby source component.
- Tests attach to a verification component or source component based on deterministic test edges/proximity.
- Documentation attaches to a docs/guidance component or gap.

### 7.4 Resolution control

Avoid the previous `8 selected nodes out of 1,774` collapse by owning all primary nodes through root-local components or gaps. Component count should scale with actual roots and source subdirectories, not a fixed cap.

## 8. Generic contract generation

### 8.1 Deterministic edge contracts

Generate contracts for owned cross-component edges of kinds relevant to architecture:

- imports
- references
- tests
- configures/build edges where meaningful

Aggregate multiple edges between the same component pair into one contract preserving all supporting edge ids.

### 8.2 Direction

For imports, the importer component consumes the imported component. Direction must match existing gate expectations for from/to components.

### 8.3 Gaps

If an owned cross-component edge cannot be represented safely as a contract, generate a specific gap referencing the edge provenance.

Indirect inter-root contracts are allowed only from typed generic evidence defined by the functional spec. For this pass, do not overreach: prefer gaps over weak indirect contracts.

## 9. Coverage repair and gaps

After root discovery, clustering, checks, and contracts:

1. Compute primary node ownership.
2. Assign uncovered primary nodes to the nearest deterministic component when evidence supports it.
3. Generate specific verification gaps for remaining uncovered nodes.
4. Compute cross-component edge coverage.
5. Generate contracts or specific edge gaps.
6. Reject blanket leftovers.

## 10. Gate updates

Strengthen `project_model_gate.py` so it verifies:

- every observable check has an execution directory;
- execution directory is relative and non-empty;
- accepted checks are safe-by-default;
- accepted checks are execution-proven or have proof artifact;
- checks with gapped execution reference valid gap ids;
- no check claims a component/contract outside its mapped scope;
- legacy snapshots still load through dataclass defaults.

Add no-identity-branch lint as a test. It should scan relevant decomposer files for forbidden repo identity strings and hardcoded calibration indicators. The lint should focus on decomposition logic files, not documentation or historical verification artifacts.

## 11. TDD sequence

### Phase 1: Schema red/green

Red tests:

- `ObservableCheck` accepts and serializes `execution_dir`, `safety_status`, `execution_status`, `proof_artifact`, and `verification_gap_ids`.
- Legacy minimal check JSON still loads with defaults.
- A previously passing legacy snapshot with an acceptance-allowlisted local check remains accepted through deterministic compatibility defaults.
- Gate rejects an observable check with missing/empty execution directory.
- Gate rejects an acceptance-allowlisted check that is not execution-proven and has no proof artifact.

Green implementation:

- Extend dataclass and snapshot loading defaults.
- Add gate checks.
- Update v1/v0 projection as needed.

### Phase 2: Root/check discovery red/green

Red tests with synthetic repos:

- A CMMC-shaped fixture, `app/backend/pyproject.toml` plus `app/frontend/package.json`, is detected as two generic manifest roots.
- A structurally different fixture with non-`app` root names and at least three roots is detected without special cases.
- Checks include per-root execution directories.
- No root-level pytest check is emitted unless root-local evidence exists.

Green implementation:

- Add generic root discovery and check discovery helpers.
- Keep test assertions phrased in manifest/toolchain terms, not target-domain terms.

### Phase 3: Component/contract coverage red/green

Red tests:

- Synthetic multi-root model owns all primary source/test/config nodes or emits specific gaps.
- Cross-component import edges are covered by contracts.
- Component count is not fixed to an arbitrary cap.
- Output is deterministic across two runs.

Green implementation:

- Add deterministic clustering and edge-derived contract generation.
- Add coverage repair/gap generation.

### Phase 4: Anti-overfitting red/green

Red tests:

- Decomposer logic must not contain CMMC/FMC project identity strings or old calibration branch indicators.
- Renaming a synthetic root produces an isomorphic decomposition modulo remapped ids.

Green implementation:

- Remove or isolate identity-specific logic from the snapshot path.
- Add lint test.

### Phase 5: CLI and full verification

Run:

- targeted new tests
- `uv run pytest tests -q`
- `uv run ruff check .`
- `uv run pyright`
- `make verify`

## 12. CMMC rerun and comparison plan

Use the clean worktree:

`/home/leonb/projects/.decomposition-targets/cmmc-level1-readiness-assistant`

Confirm it remains synced to remote HEAD before rerun.

Run target checks again for external proof:

- backend: `app/backend`, `uv run pytest -q`
- frontend: `app/frontend`, `npm test -- --run`
- frontend: `app/frontend`, `npm run build`

Generate new snapshot under:

`docs/verification/2026-06-07-meta-decomposer-generalization/artifacts/`

Compare against first CMMC snapshot:

`docs/verification/2026-06-07-cmmc-level1-decomposition/artifacts/snapshot-25eb081bd3f1ba3b/`

Comparison metrics:

- graph nodes and edges
- components
- contracts
- observable checks
- check execution directories
- gate pass/fail
- violation counts by gate
- owned/gapped primary nodes
- contract/gapped cross-component edges
- removal of incorrect root-level sole pytest check
- gap specificity

Save comparison to:

`docs/verification/2026-06-07-meta-decomposer-generalization/compare/cmmc-before-after.md`

## 13. Opus review points after implementation

Ask Opus to review:

1. The updated implementation plan conformance.
2. The before/after CMMC comparison.
3. The new generated `project-model-v1.json` versus the first model.
4. Any remaining gaps/findings and whether they indicate generic decomposer defects or acceptable project ambiguity.

## 14. Iteration loop after first rerun

For each finding:

1. Classify as implementation bug, spec gap, project ambiguity, or acceptable limitation.
2. If implementation bug, add/adjust a generic test first.
3. Fix without project-specific logic.
4. Rerun targeted tests and CMMC snapshot.
5. Update comparison artifacts.
6. Recheck no-identity lint.

Stop only when:

- quality/completeness improves under section 12 metrics;
- no CMMC-specific logic exists;
- Build Arena verification is green;
- Opus has reviewed the final model/comparison;
- remaining findings are documented with clear next steps.

## 15. Risks

- Schema defaults may hide missing execution-dir data in new snapshots. Mitigation: gate rejects missing/empty dirs and tests assert new snapshots include non-default dirs when roots are nested.
- Contract generation may overproduce low-value contracts. Mitigation: aggregate by component pair and preserve edge support.
- Component clustering may be too directory-shaped. Mitigation: responsibilities must reference root/module responsibility, and gate still rejects file-bucket responsibilities.
- CMMC may still not fully pass. Mitigation: compare improvements, document findings, and keep iterating generically.
- Anti-overfitting lint may flag documentation strings. Mitigation: scope lint to source implementation files.
