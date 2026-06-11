# Real Adversarial Held-Out Probes Implementation Plan

> **For Hermes:** Use test-driven-development skill to implement this plan task-by-task. Do not write production code before observing the targeted test fail for the intended reason.

**Goal:** Implement one deterministic Project Model v1 adversarial held-out probe that distinguishes a valid import-backed decomposition from a planted path-bucket contract decoy and writes a machine-validated proof artifact that the gate replays instead of trusting.

**Architecture:** Add `arena/project_probe_runner.py` as the narrow probe module. It builds a deterministic planted negative, evaluates golden and decoy snapshots with the existing project model gate, writes stable proof JSON with an embedded planted-negative snapshot, and returns snapshot/proof sidecar data. Strengthen `arena/project_model_gate.py` so passed probes require parseable proof JSON, matching ids and graph hash, a recomputed control snapshot hash, an embedded negative hash, recomputed gate outcomes, a delta-based discrimination signal, and a recomputed stable result hash.

**Tech Stack:** Python 3.12, dataclasses/plain dicts, existing `ProjectModelSnapshot`, `HeldOutProbe`, `VerificationGap`, `run_project_model_gate`, `stable_hash_json`, pytest, ruff, pyright.

---

## Opus review status

Bounded Opus review path: `docs/verification/2026-06-09-real-adversarial-held-out-probes/opus-review.md`.

Verdict: `ACCEPT_WITH_CHANGES`.

Required changes incorporated before implementation:

- The proof artifact must not be self-certifying. It embeds the planted-negative snapshot, and the gate re-runs the gate on that negative.
- The gate compares a canonical golden/control hash computed from the snapshot under gate with `held_out_probes` removed.
- Discrimination is delta-based: expected gate/location/text must be present in the negative and absent in the golden/control report.
- The broad semantic-understanding gap is not removed by this first path-bucket probe; this slice proves one discrimination family only.
- Tests must include forged proof, replay, absolute/path traversal, and incidental unrelated failure cases.

## Research-backed smallest fixture

Use `tests/test_project_snapshot_gate.py::_write_repo` and `_base_snapshot` for the smallest deterministic fixture shape:

- `pkg/core.py` imports `pkg/worker.py`.
- `_base_snapshot` has two responsibility-bearing components and one import-backed contract.
- A planted negative can collapse the two source files into a path bucket and should fail the gate through `component_measurability` at the mutated component.

Keep the existing `tests/test_project_meta_decomposer.py::test_fixture_decomposer_marks_unrun_semantic_probe_quality_as_gap_not_passed` behavior: fixture generation without explicit probe execution must not silently reintroduce passed probe booleans.

## Task 1: Add RED tests for probe runner behavior

**Objective:** Prove the missing probe runner API and deterministic artifact behavior before production code exists.

**Files:**
- Create: `tests/test_project_probe_runner.py`
- Later create: `arena/project_probe_runner.py`

**Step 1: Write failing tests**

Add tests that import the wished-for API:

- `build_path_bucket_planted_negative`
- `run_path_bucket_adversarial_probe`
- `write_probe_proof_artifacts`
- `canonical_probe_control_snapshot`

Test cases:

1. `test_path_bucket_probe_passes_golden_and_rejects_planted_negative`
   - Build `_write_repo(tmp_path)`, graph, and `_base_snapshot(graph)`.
   - Remove the existing fake probe from `_base_snapshot` and add `gap.semantic-understanding-not-independently-validated` if needed.
   - Run `run_path_bucket_adversarial_probe(snapshot, graph)`.
   - Assert returned probe has both booleans true, `proof_artifact == "proofs/probe.path-bucket-contract-discrimination.json"`, no probe-level verification gaps, and proof payload says golden passed / planted negative failed.
   - Assert the proof embeds `planted_negative_input.snapshot` and `negative_mutation` metadata.

2. `test_planted_negative_is_path_bucket_and_gate_rejects_it`
   - Call `build_path_bucket_planted_negative(snapshot, graph)`.
   - Gate the decoy.
   - Assert gate fails with `component_measurability` at the mutated component and a file-bucket/path-bucket message.

3. `test_probe_result_is_deterministic_for_same_inputs`
   - Run the probe twice on deep copies of the same snapshot/graph.
   - Assert proof payloads are exactly equal and deterministic hashes match.

4. `test_probe_does_not_write_or_attach_proof_when_control_fails`
   - Break the control snapshot so the golden gate fails.
   - Run the probe.
   - Assert no proof payload is returned, `proof_artifact is None`, and `verification_gap_ids` references the semantic probe gap.

5. `test_canonical_probe_control_hash_ignores_attached_probes_only`
   - Attach a probe to a copy of the snapshot.
   - Assert `canonical_probe_control_snapshot(attached)` equals the original control snapshot except for `held_out_probes` removal.

**Step 2: Run RED**

Run:

```bash
uv run pytest tests/test_project_probe_runner.py -q
```

Expected: FAIL because `arena.project_probe_runner` does not exist.

## Task 2: Implement the minimal probe runner

**Objective:** Make the new probe runner tests pass without wiring snapshot generation yet.

**Files:**
- Create: `arena/project_probe_runner.py`
- Test: `tests/test_project_probe_runner.py`

**Implementation notes:**

- Constants:
  - `PROBE_PROOF_SCHEMA_VERSION = "arena.project_probe_proof/v0.1"`
  - `PROBE_RUNNER_VERSION = "arena.project_probe_runner/v0.1"`
  - `PATH_BUCKET_PROBE_ID = "probe.path-bucket-contract-discrimination"`
  - `PATH_BUCKET_NEGATIVE_ID = "negative.path-bucket-contract-decoy"`
  - `SEMANTIC_PROBE_GAP_ID = "gap.semantic-understanding-not-independently-validated"`
- Use `copy.deepcopy` for control and decoy snapshots.
- `canonical_probe_control_snapshot(snapshot)` returns a deep copy with `held_out_probes=[]` and no other mutation.
- Select the first contract in sorted order that has valid from/to components.
- Find source file nodes for target component owned nodes by matching graph node paths, sorted by id.
- Mutate the decoy from-component into a path bucket using those sorted file node ids and responsibility text containing `path/file-bucket` markers.
- Run `run_project_model_gate` on the canonical control and decoy.
- Proof passes only when control passes, decoy fails, and the expected gate/location/text delta is present in the decoy and absent from control.
- Use `stable_hash_json` to hash the canonical control snapshot, decoy snapshot, and proof payload.
- Embed the full planted-negative snapshot dict in `planted_negative_input.snapshot`.
- Add `deterministic_result_hash` after hashing the proof payload without that field.
- Do not write files in this task; return proof payloads for tests.
- Do not remove `gap.semantic-understanding-not-independently-validated` on pass in this slice.

**Step 3: Run GREEN**

Run:

```bash
uv run pytest tests/test_project_probe_runner.py -q
```

Expected: PASS.

## Task 3: Add RED tests for proof artifact writing and gate validation

**Objective:** Prove the gate rejects fake proof paths and accepts only valid replayable proof JSON.

**Files:**
- Modify: `tests/test_project_probe_runner.py`
- Modify: `tests/test_project_snapshot_gate.py`
- Later modify: `arena/project_model_gate.py`

**Step 1: Add failing tests**

Add tests:

1. `test_write_probe_proof_artifacts_writes_only_passed_payloads`
   - Run a passing probe and write artifacts under `tmp_path / "snapshot"`.
   - Assert `proofs/probe.path-bucket-contract-discrimination.json` exists.
   - Run a failed control probe and assert no proof file is written.

2. `test_gate_accepts_passed_probe_with_valid_replayable_proof_json`
   - Run passing probe, write proof under a temporary artifact base, and gate the returned snapshot with `proof_artifact_base=artifact_base`.
   - Assert gate passes.

3. `test_gate_rejects_passed_probe_when_proof_json_is_missing_or_invalid`
   - Use a passed probe with missing proof file and assert `held_out_probe_proof` violation.
   - Write malformed/mismatched proof JSON and assert `held_out_probe_proof` violation.

4. `test_gate_rejects_forged_internally_consistent_probe_proof`
   - Write a proof JSON whose `deterministic_result_hash` recomputes and whose booleans are true, but whose embedded planted-negative snapshot does not actually fail with the expected delta.
   - Assert `held_out_probe_proof` violation.

5. `test_gate_rejects_replayed_probe_proof_for_different_control_snapshot`
   - Generate a valid proof.
   - Attach it to a different snapshot with the same graph hash but changed component responsibility/ids.
   - Assert control hash mismatch causes `held_out_probe_proof` violation.

6. `test_gate_rejects_absolute_or_parent_relative_probe_proof_paths`
   - Set `proof_artifact` to an absolute path and to `../proof.json`.
   - Assert `held_out_probe_proof` violations.

7. `test_gate_rejects_negative_that_fails_for_unrelated_reason_only`
   - Create a proof where the embedded negative fails the gate, but not with the expected gate/location/text delta.
   - Assert `held_out_probe_proof` violation.

8. Update existing `_base_snapshot`/gate tests as needed so “well grounded snapshot” writes a valid replayable proof artifact before claiming passed probe success, or route that test through the new runner.

**Step 2: Run RED**

Run:

```bash
uv run pytest tests/test_project_probe_runner.py tests/test_project_snapshot_gate.py::test_gate_passes_minimal_well_grounded_snapshot tests/test_project_snapshot_gate.py::test_gate_rejects_probe_success_without_proof_artifact -q
```

Expected: FAIL because gate does not yet validate or replay proof JSON and does not accept `proof_artifact_base`.

## Task 4: Strengthen gate proof validation

**Objective:** Make passed probe success dependent on replayable proof artifact truth, not arbitrary prose/path strings or self-certified booleans.

**Files:**
- Modify: `arena/project_model_gate.py`
- Test: `tests/test_project_probe_runner.py`, `tests/test_project_snapshot_gate.py`

**Implementation notes:**

- Change `run_project_model_gate` signature to accept `proof_artifact_base: str | Path | None = None` and an internal recursion guard such as `_validate_probe_proofs: bool = True`.
- Thread the base into `_check_held_out_probe_metadata`.
- Use `Path(snapshot_obj.project_root)` as fallback base only when no explicit base is supplied.
- For passed probes, validate:
  - proof path is relative and contains no `..`;
  - file exists;
  - JSON parses as an object;
  - `schema_version == "arena.project_probe_proof/v0.1"`;
  - `probe_id`, `planted_negative_id`, and `graph_hash` match;
  - `deterministic_result_hash` recomputes from payload without that field;
  - canonical control hash equals the proof's `golden_control_input.snapshot_hash`;
  - re-running the gate on the canonical control passes;
  - embedded planted-negative snapshot canonical hash equals `planted_negative_input.snapshot_hash`;
  - re-running the gate on the embedded negative fails;
  - expected gate/location/text delta is present in the negative report and absent from the control report;
  - `golden_control_passed is True` and `discrimination_passed is True` agree with recomputed outcomes.
- When recursively re-running the gate on the control/negative, disable proof validation to avoid infinite recursion; these snapshots should have no passed probes for this slice.
- Update `run_project_model_gate_from_manifest` to pass `proof_artifact_base=manifest_path.parent`.

**Step 3: Run GREEN**

Run:

```bash
uv run pytest tests/test_project_probe_runner.py tests/test_project_snapshot_gate.py -q
```

Expected: PASS.

## Task 5: Wire optional probe execution into snapshot building

**Objective:** Allow Build Arena to produce real proven probes only when explicitly requested.

**Files:**
- Modify: `arena/project_decomposer_ai.py`
- Modify: `arena/project_model_cli.py`
- Modify: `tests/test_project_decomposer_ai.py`
- Modify: `tests/test_project_model_v1_contract.py` if schema/v1 snapshot assertions need proof-aware coverage.

**Step 1: Add failing tests**

Add tests:

1. `test_build_project_model_snapshot_can_run_real_adversarial_probe`
   - Call `build_project_model_snapshot(..., run_adversarial_probes=True, overwrite=True)`.
   - Assert gate passes.
   - Assert snapshot has one held-out probe with proof artifact.
   - Assert `snapshot_dir / proof_artifact` exists.
   - Assert `held-out-probes.json` and `planted-negatives.json` reflect the real probe/negative.
   - Assert `gap.semantic-understanding-not-independently-validated` remains present as the broad semantic gap, while the passed probe has `verification_gap_ids == []`.

2. Preserve existing behavior:
   - Existing fixture/meta-decomposer tests still assert no passed probe and semantic gap when probe execution is not enabled.

**Step 2: Run RED**

Run:

```bash
uv run pytest tests/test_project_decomposer_ai.py::test_build_project_model_snapshot_can_run_real_adversarial_probe tests/test_project_meta_decomposer.py::test_fixture_decomposer_marks_unrun_semantic_probe_quality_as_gap_not_passed -q
```

Expected: FAIL because `run_adversarial_probes` is unsupported.

**Step 3: Implement minimal wiring**

- Add `run_adversarial_probes: bool = False` to `build_project_model_snapshot`.
- In CLI, add `--run-adversarial-probes` to snapshot command.
- When enabled:
  1. Run probe before final identity is frozen.
  2. Attach passed probe only when evaluation passed.
  3. Keep the broad semantic-validation gap in this first slice.
  4. Finalize snapshot identity.
  5. Create snapshot dir.
  6. Write proof JSON under `snapshot_dir / "proofs"`.
  7. Run final gate with `proof_artifact_base=snapshot_dir`.
- When disabled, keep current no-probe/gap behavior.

**Step 4: Run GREEN**

Run:

```bash
uv run pytest tests/test_project_decomposer_ai.py::test_build_project_model_snapshot_can_run_real_adversarial_probe tests/test_project_meta_decomposer.py::test_fixture_decomposer_marks_unrun_semantic_probe_quality_as_gap_not_passed -q
```

Expected: PASS.

## Task 6: Schema/v1 and anti-regression tests

**Objective:** Prove Project Model v1 carries the proof-backed probe and fake booleans do not return.

**Files:**
- Modify: `tests/test_project_model_v1_contract.py`
- Modify: `tests/test_project_meta_decomposer.py` if more anti-hardcoding coverage is needed.

**Tests:**

- Add a v1 schema test with `run_adversarial_probes=True` and validate `project-model-v1.json` against `docs/schemas/project-model-v1.schema.json`.
- Assert embedded snapshot probe has `proof_artifact` only in the enabled case.
- Assert default fixture output still has `held_out_probes == []` and semantic gap.
- Assert source scan does not contain `discrimination_passed=True` hardcoded in fixture/meta-decomposer output paths without proof.

**Run:**

```bash
uv run pytest tests/test_project_model_v1_contract.py tests/test_project_meta_decomposer.py -q
```

Expected: PASS.

## Task 7: Focused and full verification

**Objective:** Prove the slice does not regress existing Project Model v1 paths.

Run, in order:

```bash
uv run pytest tests/test_project_probe_runner.py -q
uv run pytest tests/test_project_meta_decomposer.py tests/test_project_snapshot_gate.py tests/test_project_decomposer_ai.py tests/test_project_model_v1_contract.py -q
uv run pytest tests -q
uv run ruff check .
uv run pyright
make verify
git diff --check
```

Expected: all pass.

## Task 8: Artifact and safety checks

**Objective:** Prove the implementation respected repo boundaries and did not leak secrets.

Run:

```bash
git status --short --branch --untracked-files=all
git diff --name-only
python3 - <<'PY'
from pathlib import Path
protected = ('scorer/', 'verifier/', 'schema/', 'arena/generated/')
changed = [line.strip() for line in __import__('subprocess').check_output(['git','diff','--name-only'], text=True).splitlines() if line.strip()]
violations = [p for p in changed if p.startswith(protected)]
print({'changed': changed, 'protected_path_violations': violations})
raise SystemExit(1 if violations else 0)
PY
python3 - <<'PY'
import re, subprocess
paths = [p for p in subprocess.check_output(['git','diff','--name-only'], text=True).splitlines() if p]
pattern = re.compile(r'(?i)(api[_-]?key|secret|token|password|authorization|bearer)\s*[:=]\s*[A-Za-z0-9_./+\-]{12,}')
hits=[]
for p in paths:
    try:
        text=open(p, encoding='utf-8', errors='ignore').read()
    except OSError:
        continue
    for i,line in enumerate(text.splitlines(),1):
        if pattern.search(line):
            hits.append((p,i,line[:160]))
print({'credential_scan_hits': hits})
raise SystemExit(1 if hits else 0)
PY
```

Expected: no protected path violations, no credential-shaped hits.

## Task 9: PR update, commit, push

**Objective:** Deliver the working artifact into PR #7.

Commands:

```bash
git status --short --branch --untracked-files=all
git diff --stat
git add arena/project_probe_runner.py arena/project_model_gate.py arena/project_decomposer_ai.py arena/project_model_cli.py tests/test_project_probe_runner.py tests/test_project_snapshot_gate.py tests/test_project_decomposer_ai.py tests/test_project_model_v1_contract.py docs/specs/2026-06-09-real-adversarial-held-out-probes.md docs/plans/2026-06-09-real-adversarial-held-out-probes-plan.md docs/verification/2026-06-09-real-adversarial-held-out-probes/opus-review.md
git commit -m "feat: add real adversarial project model probe"
git push origin chore/decomposition-intake-housekeeping
```

Update PR #7 body with:

- summary of implemented probe slice;
- Opus verdict and review artifact path;
- exact verification results;
- remaining limitations.

## Deferred work

- More planted-negative families: wrong endpoint, missing import-backed contract, ignored graph edge, vague docs/tests/config-only components.
- A reusable probe corpus format beyond this single deterministic family.
- Live independent probe-builder review, still behind explicit authorization and cost boundaries.
- Integration into future broad autonomous loops after readiness blockers close.
