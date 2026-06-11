# Opus Review — Real Adversarial Held-Out Probes

Date: 2026-06-09
Reviewer path: Claude Code `--model opus` resolved to `claude-opus-4-8`
Mode: read-only, no tools for successful compact review
Verdict: ACCEPT_WITH_CHANGES
Cost USD (successful compact review): 0.342625

## Budget-failed full-context attempt

A first read-only Claude Code Opus attempt allowed read-only file tools and hit the explicit budget cap before returning a usable review.

- raw JSON: `docs/verification/2026-06-09-real-adversarial-held-out-probes/opus-review.raw.json`
- subtype: `error_max_budget_usd`
- cost USD: 1.93574725
- model usage keys: claude-opus-4-8

The successful review below used the same Opus model with the exact spec and plan text embedded in the prompt and no tools.

## Exact successful review prompt

```text
Read-only Opus review. Do not use tools. Review only the included Build Arena spec and plan. Return the required concise structure.

Required structure:
REVIEWER: Claude Code model=<resolved model if visible> opus_confirmed=<yes/no/unknown>
VERDICT: ACCEPT / ACCEPT_WITH_CHANGES / REJECT

Critical flaws:
- ...

Missing tests:
- ...

Ways the proposed probe could still be fake or gameable:
- ...

Determinism risks:
- ...

Gate bypass risks:
- ...

Simpler vertical slice if the plan is too broad:
- ...

Required changes before implementation:
- ...

Final assessment:
- ...

Context: Build Arena Project Model v1 currently forbids fake held-out probe booleans without proof. This plan should implement one real deterministic path-bucket planted-negative probe with machine-validated proof JSON. Protected paths are scorer/, verifier/, schema/, arena/generated/.

Review criteria: Is this a real probe, not a schema field? Is proof machine-checkable? Does TDD RED-GREEN order hold? Are failed/unrun probes gaps? Does gate reject fake/missing/malformed/mismatched proof? Is scope one-session reasonable?

## SPEC

# Real Adversarial Held-Out Probes for Project Model v1

Date: 2026-06-09
Status: Draft for bounded Opus review
Scope: First narrow deterministic vertical slice

## Goal

Build Arena must be able to attach a held-out probe only when it actually evaluated a golden control and a planted negative, wrote a deterministic proof artifact, and the deterministic gate can validate that artifact without trusting prose.

This slice targets Project Model v1 fixture/meta-decomposer snapshots. It does not make probe execution a live LLM/API dependency.

## Research summary and chosen slice

Relevant current facts from repo inspection:

- `arena/project_meta_decomposer.py` currently emits `held_out_probes: []` and `gap.semantic-understanding-not-independently-validated` when no probe proof exists.
- `arena/project_model_gate.py` currently rejects passed probe booleans without a `proof_artifact`, but only checks that the path is workspace-relative.
- `arena/project_decomposer_ai.py` already writes `held-out-probes.json` and `planted-negatives.json` sidecars for snapshot bundles.
- `tests/test_project_snapshot_gate.py::_write_repo` and `_base_snapshot` provide the smallest deterministic fixture with a real import-backed contract: `pkg.core.run` imports `pkg.worker.work`.
- Existing final-report risk explicitly says independent adversarial probe generation remains future work.

Selected scorecard profile: active development project. The highest-leverage improvement is a reproducible verification/contract slice that closes one fake-proof class without expanding live provider scope.

## What counts as a real adversarial probe

A real adversarial probe is an executable/checkable comparison over two concrete decomposition inputs for the same graph:

1. Golden/control input: the intended snapshot/decomposition.
2. Planted-negative input: a deliberately bad decomposition built from the same graph and target contract/component evidence.
3. Deterministic evaluator: the Build Arena project model gate plus explicit probe checks.
4. Proof artifact: machine-readable JSON containing the inputs, hashes, checks, gate outcomes, and a stable result hash.

For this first slice, the planted negative is a path/file-bucket contract decoy. It collapses the source evidence behind an import-backed contract into sibling file ownership and path-bucket responsibility text. The probe succeeds only if:

- the golden/control snapshot passes the gate; and
- the planted-negative snapshot fails the gate for the expected deterministic discrimination signal, such as `component_measurability` path/file-bucket rejection or contract/edge coverage breakage.

## Out of scope

- Live or paid LLM calls during probe execution.
- General-purpose semantic judging beyond deterministic gate output.
- Multiple probe families.
- External held-out repo selection.
- Full adversarial corpus management.
- Modifying `schema/`, `scorer/`, `verifier/`, or hand-editing `arena/generated/`.
- Claiming broad autonomous readiness.

## Probe artifact format

Proof artifact JSON for this slice uses:

```json
{
  "schema_version": "arena.project_probe_proof/v0.1",
  "probe_id": "probe.path-bucket-contract-discrimination",
  "probe_kind": "path_bucket_planted_negative_gate_discrimination",
  "graph_hash": "<snapshot graph hash>",
  "golden_control_input": {
    "kind": "project_model_snapshot",
    "snapshot_hash": "<sha256 over canonical control snapshot>",
    "gate_passed": true
  },
  "planted_negative_input": {
    "kind": "project_model_snapshot",
    "planted_negative_id": "negative.path-bucket-contract-decoy",
    "snapshot_hash": "<sha256 over canonical planted-negative snapshot>",
    "gate_passed": false
  },
  "target_component_ids": ["..."],
  "target_contract_ids": ["..."],
  "planted_negative_id": "negative.path-bucket-contract-decoy",
  "checks": [
    {
      "id": "golden-control-gate",
      "kind": "project_model_gate",
      "expected_passed": true,
      "actual_passed": true,
      "violation_gates": []
    },
    {
      "id": "planted-negative-gate",
      "kind": "project_model_gate",
      "expected_passed": false,
      "actual_passed": false,
      "violation_gates": ["component_measurability"]
    },
    {
      "id": "expected-discrimination-violation",
      "kind": "gate_violation_match",
      "expected_gate": "component_measurability",
      "matched": true
    }
  ],
  "golden_control_passed": true,
  "discrimination_passed": true,
  "provenance_refs": ["prov:..."],
  "tool_versions": {
    "probe_runner": "arena.project_probe_runner/v0.1",
    "gate": "arena.project_model_gate"
  },
  "deterministic_result_hash": "<sha256 over this object excluding deterministic_result_hash>"
}
```

The field name `deterministic_result_hash` is part of the stable artifact contract. Timestamps are omitted from the stable proof artifact in this slice.

## Proof artifact location

When probe execution is enabled for a snapshot bundle, proof files are written under the snapshot directory:

- `proofs/probe.path-bucket-contract-discrimination.json`

`HeldOutProbe.proof_artifact` stores that workspace/snapshot-bundle relative path. The gate must reject absolute paths and paths containing `..`.

## Planted-negative generation

The deterministic planted-negative builder:

1. Selects the first import-backed contract in stable sorted order.
2. Locates the from/to components and source file nodes behind their owned symbols.
3. Rewrites the from component into a path-bucket decoy that owns sibling file nodes from both sides of the contract.
4. Uses a responsibility string that explicitly describes a path/file bucket.
5. Preserves provenance refs from the original target evidence.
6. Records `negative.path-bucket-contract-decoy` metadata in `planted-negatives.json`.

If no import-backed contract or source files exist, this probe is not run and the semantic validation gap remains.

## Golden control pass/fail computation

The golden/control input is evaluated by `run_project_model_gate(control_snapshot, graph)`. Golden control passes only if the gate report passes. The current explicit semantic-validation gap is acceptable for the control snapshot before the proof is attached, because the whole point of the probe is to close that gap after proof exists.

## Discrimination pass/fail computation

The planted-negative input is evaluated by the same deterministic gate. Discrimination passes only if:

- the planted-negative gate report fails; and
- at least one violation matches the expected deterministic discrimination signal for this slice, initially `component_measurability` with path/file-bucket text or an equivalent contract/edge coverage break caused by the decoy.

## Determinism

Determinism is maintained by:

- stable sorted contract/component selection;
- no randomness;
- no live/provider calls;
- canonical JSON hashing with sorted keys and compact separators;
- proof hash excluding only `deterministic_result_hash`;
- no timestamps inside the stable proof payload;
- stable proof path relative to the snapshot bundle.

Re-running the same probe on the same graph and snapshot must produce identical proof JSON and identical `deterministic_result_hash`.

## Failed, missing, or unrun probes

- Missing probe: `held_out_probes` remains empty and `gap.semantic-understanding-not-independently-validated` remains present.
- Unrun probe because no suitable target exists: no proof artifact is written; the same gap remains.
- Failed probe: `HeldOutProbe` may be recorded with `golden_control_passed: false` or `discrimination_passed: false`, `proof_artifact: null`, and `verification_gap_ids` referencing an existing semantic/probe validation gap.
- Passed probe: `HeldOutProbe.proof_artifact` is populated only after evaluation ran, both booleans passed, and the proof artifact was written.

On pass, the semantic-validation gap may be removed for the target snapshot because the proof now closes that specific gap. Other unrelated verification gaps must remain.

## Gate validation without trusting prose

The gate must validate passed probes mechanically:

1. `proof_artifact` is relative and does not contain `..`.
2. The JSON proof artifact exists under the supplied artifact base.
3. `schema_version`, `probe_id`, `planted_negative_id`, and `graph_hash` match the snapshot/probe.
4. `golden_control_passed` and `discrimination_passed` are exactly `true`.
5. The proof contains structured checks for golden-control gate pass and planted-negative gate failure.
6. `deterministic_result_hash` recomputes exactly from the proof JSON with that field removed.

A path pointing to missing JSON, arbitrary prose, mismatched ids, mismatched graph hash, missing checks, or a wrong result hash is fake success and must fail the gate.

## Security and cost boundaries

Probe execution is deterministic local Python only. It must not call live LLM providers, network APIs, credentials, GitHub, deployment tools, or paid services. It must not modify protected paths or generated artifacts. It writes only snapshot-bundle artifacts and test temp files.

## Acceptance criteria

This slice is accepted when tests prove:

1. A valid golden fixture passes the probe.
2. A path-bucket planted negative fails the probe.
3. Proof is written only when evaluation ran and passed.
4. Gate accepts a passed probe with valid proof JSON.
5. Gate rejects passed probe with missing/invalid proof JSON.
6. Gate rejects or gaps failed/unrun probes.
7. Re-running the same probe on the same inputs is deterministic.
8. Fixture/meta-decomposer still emits no passed probe when probe execution is not enabled.

## PLAN

# Real Adversarial Held-Out Probes Implementation Plan

> **For Hermes:** Use test-driven-development skill to implement this plan task-by-task. Do not write production code before observing the targeted test fail for the intended reason.

**Goal:** Implement one deterministic Project Model v1 adversarial held-out probe that distinguishes a valid import-backed decomposition from a planted path-bucket contract decoy and writes a machine-validated proof artifact.

**Architecture:** Add `arena/project_probe_runner.py` as the narrow probe module. It builds a deterministic planted negative, evaluates golden and decoy snapshots with the existing project model gate, writes stable proof JSON, and returns snapshot/proof sidecar data. Strengthen `arena/project_model_gate.py` so passed probes require parseable proof JSON with matching ids, graph hash, structured checks, and a recomputed stable result hash.

**Tech Stack:** Python 3.12, dataclasses/plain dicts, existing `ProjectModelSnapshot`, `HeldOutProbe`, `VerificationGap`, `run_project_model_gate`, `stable_hash_json`, pytest, ruff, pyright.

---

## Research-backed smallest fixture

Use `tests/test_project_snapshot_gate.py::_write_repo` and `_base_snapshot` for the smallest deterministic fixture shape:

- `pkg/core.py` imports `pkg/worker.py`.
- `_base_snapshot` has two responsibility-bearing components and one import-backed contract.
- A planted negative can collapse the two source files into a path bucket and should fail the gate through `component_measurability`.

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

Test cases:

1. `test_path_bucket_probe_passes_golden_and_rejects_planted_negative`
   - Build `_write_repo(tmp_path)`, graph, and `_base_snapshot(graph)`.
   - Remove the existing fake probe from `_base_snapshot` and add `gap.semantic-understanding-not-independently-validated` if needed.
   - Run `run_path_bucket_adversarial_probe(snapshot, graph)`.
   - Assert returned probe has both booleans true, `proof_artifact == "proofs/probe.path-bucket-contract-discrimination.json"`, no verification gaps, and proof payload says golden passed / planted negative failed.

2. `test_planted_negative_is_path_bucket_and_gate_rejects_it`
   - Call `build_path_bucket_planted_negative(snapshot, graph)`.
   - Gate the decoy.
   - Assert gate fails with `component_measurability` and a file-bucket/path-bucket message.

3. `test_probe_result_is_deterministic_for_same_inputs`
   - Run the probe twice on deep copies of the same snapshot/graph.
   - Assert proof payloads are exactly equal and deterministic hashes match.

4. `test_probe_does_not_write_or_attach_proof_when_control_fails`
   - Break the control snapshot so the golden gate fails.
   - Run the probe.
   - Assert no proof payload is returned, `proof_artifact is None`, and `verification_gap_ids` references the semantic probe gap.

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
- Select the first contract in sorted order that has valid from/to components.
- Find source file nodes for target component owned nodes by matching graph node paths.
- Mutate the decoy from-component into a path bucket using those file node ids and responsibility text containing `path/file-bucket` markers.
- Run `run_project_model_gate` on control and decoy.
- Proof passes only when control passes and decoy fails with expected discrimination.
- Use `stable_hash_json` to hash the control snapshot, decoy snapshot, and proof payload.
- Add `deterministic_result_hash` after hashing the proof payload without that field.
- Do not write files in this task; return proof payloads for tests.

**Step 3: Run GREEN**

Run:

```bash
uv run pytest tests/test_project_probe_runner.py -q
```

Expected: PASS.

## Task 3: Add RED tests for proof artifact writing and gate validation

**Objective:** Prove the gate rejects fake proof paths and accepts only valid proof JSON.

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

2. `test_gate_accepts_passed_probe_with_valid_proof_json`
   - Run passing probe, write proof under a temporary artifact base, and gate the returned snapshot with `proof_artifact_base=artifact_base`.
   - Assert gate passes.

3. `test_gate_rejects_passed_probe_when_proof_json_is_missing_or_invalid`
   - Use a passed probe with missing proof file and assert `held_out_probe_proof` violation.
   - Write malformed/mismatched proof JSON and assert `held_out_probe_proof` violation.

4. Update existing `_base_snapshot`/gate tests as needed so “well grounded snapshot” writes a valid proof artifact before claiming passed probe success, or route that test through the new runner.

**Step 2: Run RED**

Run:

```bash
uv run pytest tests/test_project_probe_runner.py tests/test_project_snapshot_gate.py::test_gate_passes_minimal_well_grounded_snapshot tests/test_project_snapshot_gate.py::test_gate_rejects_probe_success_without_proof_artifact -q
```

Expected: FAIL because gate does not yet validate or load proof JSON and does not accept `proof_artifact_base`.

## Task 4: Strengthen gate proof validation

**Objective:** Make passed probe success dependent on valid proof artifact metadata, not arbitrary prose/path strings.

**Files:**
- Modify: `arena/project_model_gate.py`
- Test: `tests/test_project_probe_runner.py`, `tests/test_project_snapshot_gate.py`

**Implementation notes:**

- Change `run_project_model_gate` signature to accept `proof_artifact_base: str | Path | None = None`.
- Thread the base into `_check_held_out_probe_metadata`.
- Use `Path(snapshot_obj.project_root)` as fallback base only when no explicit base is supplied.
- For passed probes, validate:
  - proof path is relative and contains no `..`;
  - file exists;
  - JSON parses as an object;
  - `schema_version == "arena.project_probe_proof/v0.1"`;
  - `probe_id`, `planted_negative_id`, and `graph_hash` match;
  - `golden_control_passed is True` and `discrimination_passed is True`;
  - structured checks include a passing `golden-control-gate`, failing `planted-negative-gate`, and matched expected discrimination check;
  - `deterministic_result_hash` recomputes from payload without that field.
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
   - Assert `gap.semantic-understanding-not-independently-validated` is absent from the passed-probe snapshot.

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
  2. Attach passed probe and remove the semantic validation gap only on pass.
  3. Finalize snapshot identity.
  4. Create snapshot dir.
  5. Write proof JSON under `snapshot_dir / "proofs"`.
  6. Run final gate with `proof_artifact_base=snapshot_dir`.
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


```

## Opus response

```text
REVIEWER: Claude Code model=claude-opus-4-8 opus_confirmed=yes
VERDICT: ACCEPT_WITH_CHANGES

Critical flaws:
- **Self-certifying proof = gate bypass.** The gate validates the proof's *internal consistency* (recomputed `deterministic_result_hash`, matching ids, recorded booleans) but never re-executes the discrimination. The proof embeds only `snapshot_hash` strings for the planted negative, not the negative snapshot itself, so the gate cannot re-run `run_project_model_gate` on the decoy. A fabricated-but-internally-consistent proof (correct hash, correct ids, `discrimination_passed: true`) passes. "Validate without trusting prose" is satisfied, but it still *trusts recorded booleans*. This is the central weakness.
- **Control `snapshot_hash` matching is undefined and circular.** `golden_control_input.snapshot_hash` is "sha256 over canonical control snapshot," but attaching the passed probe (with `proof_artifact`) mutates the snapshot and changes its hash. The gate's validation list (Task 4) only checks `graph_hash` — it never says how/whether it re-derives and matches the control snapshot hash against the snapshot under gate. Without a pinned "snapshot-minus-probes" canonical form, this either can't be verified or won't match deterministically.
- **Discrimination signal is a loose OR.** `component_measurability` *or* "an equivalent contract/edge coverage break" with a match rule that only checks `violation_gates` *contains* `component_measurability`. The negative could trip `component_measurability` for a reason unrelated to the planted contract collapse, yielding a spurious pass. There's no causal link asserting the failure stems from the decoy mutation.
- **Tautology risk on gap closure.** The runner builds both control and negative, then proves the gate rejects the runner's own synthetic mutation. That validates the path-bucket check works — it does not independently validate the *original* decomposition's semantics. Removing `gap.semantic-understanding-not-independently-validated` overclaims; the gap closed is narrower ("gate discriminates one synthetic path-bucket decoy").

Missing tests:
- Forged-but-consistent proof: correct `deterministic_result_hash`/ids/`graph_hash` but `discrimination_passed: true` where the negative was never actually rejected. Current gate cannot catch this — add a test that forces the gate to detect it (requires re-execution or embedded negative).
- Replay/attachment: a valid proof attached to a *different* snapshot with the same `graph_hash` — must be rejected via control `snapshot_hash` match.
- Path traversal / absolute path rejection at the gate (spec requires `..` and absolute rejection; plan tests only list missing/malformed/mismatched).
- Negative that fails the gate for an *unrelated* violation while incidentally containing `component_measurability` — must not count as discrimination.

Ways the proposed probe could still be fake or gameable:
- Hand-author a consistent proof JSON (the hash is recomputable by anyone) → gate accepts. The hash only proves "I computed this object," not "the gate produced this outcome."
- Borrow a valid proof from another snapshot sharing the graph.
- Negative passes-as-rejected for incidental reasons (loose OR / contains-check).

Determinism risks:
- Owned-node lists, provenance refs, and file-node selection must be explicitly sorted; "matching graph node paths" is underspecified. Any set/dict iteration order leaks into `snapshot_hash`.
- The control-snapshot-vs-attached-snapshot hashing ambiguity (above) is also a determinism risk.
- Confirm `stable_hash_json` truly canonicalizes nested structures (sorted keys + compact separators all the way down), not just top level.

Gate bypass risks:
- Self-certifying proof (primary, above).
- Missing control `snapshot_hash` equality check → valid proof reattached to a bad snapshot.
- `tool_versions`/`schema_version` inside the hashed payload but no gate assertion that the *gate's own* version matches — a stale-runner proof could pass a newer gate.

Simpler vertical slice if the plan is too broad:
- Ship **Tasks 1–4 only**: `project_probe_runner.py` + strengthened gate validation + their tests. Defer Task 5 (decomposer wiring), Task 6 (CLI + schema/v1 contract), and the PR/verify automation tasks. That delivers the real, testable proof-or-reject core in one session and isolates the gate-bypass fix without touching snapshot-build ordering and CLI surface.

Required changes before implementation:
1. Make the proof *reproducible by the gate*, not just consistent: embed the planted-negative snapshot (or have the gate deterministically rebuild it from the graph) and have the gate **re-run `run_project_model_gate` on the negative** and confirm it fails with the expected signal. Internal hash alone is insufficient.
2. Define and enforce a canonical control hash (e.g., snapshot with `held_out_probes` excluded) and have the gate assert `golden_control_input.snapshot_hash` equals that hash of the snapshot under gate.
3. Tighten the discrimination match to assert causation: the expected violation must be present in the negative gate report **and absent in the control gate report** (delta-based), not merely "contains."
4. Narrow the gap-closure claim: rename/scope the closed gap to the path-bucket-discrimination class, or keep the broad semantic gap and add a narrower satisfied marker.
5. Add the four missing tests above (forged proof, replay, path traversal, incidental-violation).
6. Pin explicit sort order for component/file-node/provenance selection.

Final assessment:
- The design is a genuine probe, not a schema field — it runs the gate over two real inputs and discriminates. RED→GREEN ordering is correct and the fixture choice is sound. But as specified the proof is *self-certifying*: the gate checks consistency, not truth, so a fabricated proof passes and a valid proof can be replayed onto a different snapshot. Fix the re-execution + control-hash-match gaps and tighten the discrimination signal, and this becomes a real non-gameable slice. Accept with the changes above; do not implement the gate as currently described.

(Note: per your "do not use tools" instruction, I did not create a plan file or invoke planning/ExitPlanMode tools — this review is the deliverable.)
```

## Raw response metadata

```json
{
  "duration_api_ms": 69890,
  "duration_ms": 70048,
  "is_error": false,
  "modelUsage": {
    "claude-opus-4-8": {
      "cacheCreationInputTokens": 30520,
      "cacheReadInputTokens": 0,
      "contextWindow": 1000000,
      "costUSD": 0.342625,
      "inputTokens": 4350,
      "maxOutputTokens": 64000,
      "outputTokens": 5205,
      "webSearchRequests": 0
    }
  },
  "subtype": "success",
  "total_cost_usd": 0.342625,
  "type": "result"
}
```
