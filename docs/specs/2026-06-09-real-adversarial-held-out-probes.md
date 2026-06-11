# Real Adversarial Held-Out Probes for Project Model v1

Date: 2026-06-09
Status: Patched after bounded Opus review (`ACCEPT_WITH_CHANGES`)
Scope: First narrow deterministic vertical slice

## Goal

Build Arena must be able to attach a held-out probe only when it actually evaluated a golden control and a planted negative, wrote a deterministic proof artifact, and the deterministic gate can validate that artifact without trusting prose or self-reported booleans.

This slice targets Project Model v1 fixture/meta-decomposer snapshots. It does not make probe execution a live LLM/API dependency.

## Research summary and chosen slice

Relevant current facts from repo inspection:

- `arena/project_meta_decomposer.py` currently emits `held_out_probes: []` and `gap.semantic-understanding-not-independently-validated` when no probe proof exists.
- `arena/project_model_gate.py` currently rejects passed probe booleans without a `proof_artifact`, but only checks that the path is workspace-relative.
- `arena/project_decomposer_ai.py` already writes `held-out-probes.json` and `planted-negatives.json` sidecars for snapshot bundles.
- `tests/test_project_snapshot_gate.py::_write_repo` and `_base_snapshot` provide the smallest deterministic fixture with a real import-backed contract: `pkg.core.run` imports `pkg.worker.work`.
- Existing final-report risk explicitly says independent adversarial probe generation remains future work.

Selected scorecard profile: active development project. The highest-leverage improvement is a reproducible verification/contract slice that closes one fake-proof class without expanding live provider scope.

## Opus review changes incorporated

The bounded Opus review found the first draft still allowed self-certifying proof artifacts: a forged JSON object could recompute its own result hash without proving the planted negative was actually rejected. This spec is patched so the proof artifact embeds the planted-negative snapshot and the gate re-runs the golden/control and planted-negative gate checks itself. The gate must compare recomputed outcomes against the proof and reject mismatches, stale attachments, traversal paths, forged hashes, and incidental unrelated failures.

## What counts as a real adversarial probe

A real adversarial probe is an executable/checkable comparison over two concrete decomposition inputs for the same graph:

1. Golden/control input: the intended snapshot/decomposition, canonicalized as the final snapshot with `held_out_probes` removed.
2. Planted-negative input: a deliberately bad decomposition built from the same graph and target contract/component evidence, embedded in the proof artifact.
3. Deterministic evaluator: the Build Arena project model gate plus explicit delta-based probe checks.
4. Proof artifact: machine-readable JSON containing the canonical control hash, embedded planted-negative snapshot, mutation metadata, checks, recomputed gate outcomes, and a stable result hash.

For this first slice, the planted negative is a path/file-bucket contract decoy. It collapses the source evidence behind an import-backed contract into sibling file ownership and path-bucket responsibility text. The probe succeeds only if:

- the golden/control snapshot passes the gate;
- the planted-negative snapshot fails the gate; and
- the planted-negative has a deterministic discrimination violation that is absent from the golden/control report and tied to the mutated component.

## Out of scope

- Live or paid LLM calls during probe execution.
- General-purpose semantic judging beyond deterministic gate output.
- Multiple probe families.
- External held-out repo selection.
- Full adversarial corpus management.
- Modifying `schema/`, `scorer/`, `verifier/`, or hand-editing `arena/generated/`.
- Claiming broad autonomous readiness or complete semantic understanding.

## Probe artifact format

Proof artifact JSON for this slice uses:

```json
{
  "schema_version": "arena.project_probe_proof/v0.1",
  "probe_id": "probe.path-bucket-contract-discrimination",
  "probe_kind": "path_bucket_planted_negative_gate_discrimination",
  "graph_hash": "<snapshot graph hash>",
  "golden_control_input": {
    "kind": "project_model_snapshot_without_held_out_probes",
    "snapshot_hash": "<sha256 over final snapshot with held_out_probes removed>",
    "gate_passed": true
  },
  "planted_negative_input": {
    "kind": "embedded_project_model_snapshot",
    "planted_negative_id": "negative.path-bucket-contract-decoy",
    "snapshot_hash": "<sha256 over canonical planted-negative snapshot>",
    "gate_passed": false,
    "snapshot": {"...": "full planted-negative ProjectModelSnapshot dict"}
  },
  "negative_mutation": {
    "type": "path_bucket_component_rewrite",
    "mutated_component_id": "component.runtime-core",
    "source_file_node_ids": ["node:...", "node:..."],
    "expected_violation_gate": "component_measurability",
    "expected_violation_location": "components[component.runtime-core]",
    "expected_violation_text": "file-bucket"
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
      "id": "expected-discrimination-delta",
      "kind": "gate_violation_delta",
      "expected_gate": "component_measurability",
      "expected_location": "components[component.runtime-core]",
      "expected_text": "file-bucket",
      "present_in_planted_negative": true,
      "absent_from_golden_control": true,
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
3. Rewrites the from component into a path-bucket decoy that owns sorted sibling file node ids from both sides of the contract.
4. Uses a responsibility string that explicitly describes a path/file bucket.
5. Preserves sorted provenance refs from the original target evidence.
6. Embeds the full planted-negative snapshot in the proof artifact.
7. Records `negative.path-bucket-contract-decoy` metadata in `planted-negatives.json`.

If no import-backed contract or source files exist, this probe is not run and the semantic validation gap remains.

## Golden control pass/fail computation

The golden/control input is the final snapshot under gate with `held_out_probes` removed. This avoids circular hashing: attaching the passed probe changes the final snapshot, but the control hash is always computed over the final snapshot minus probe claims.

Golden control passes only if `run_project_model_gate(control_snapshot, graph)` passes. The current explicit semantic-validation gap is acceptable for the control snapshot before proof is attached. This first probe proves one path-bucket discrimination class; it does not prove complete semantic understanding.

## Discrimination pass/fail computation

The planted-negative input is evaluated by the same deterministic gate. Discrimination passes only if:

- the planted-negative gate report fails;
- the expected violation gate, location, and text are present in the planted-negative report;
- the same expected discrimination violation is absent from the golden/control report; and
- the gate re-runs both evaluations from the artifact/control data and gets the same result.

A negative that fails for incidental unrelated reasons is not a passing discrimination proof.

## Determinism

Determinism is maintained by:

- stable sorted contract/component selection;
- stable sorted node ids and provenance refs;
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

A passed path-bucket probe does not remove the broad semantic-understanding gap for the whole model in this slice. It proves only this specific discrimination family. The passed `HeldOutProbe` itself should have no `verification_gap_ids`; missing, unrun, or failed probes must keep gap references.

## Gate validation without trusting prose

The gate must validate passed probes mechanically:

1. `proof_artifact` is relative and does not contain `..`.
2. The JSON proof artifact exists under the supplied artifact base.
3. The artifact parses as JSON object, not arbitrary prose.
4. `schema_version`, `probe_id`, `planted_negative_id`, and `graph_hash` match the snapshot/probe.
5. `deterministic_result_hash` recomputes exactly from the proof JSON with that field removed.
6. The gate recomputes the golden/control snapshot hash by removing `held_out_probes` from the snapshot under gate and comparing it to `golden_control_input.snapshot_hash`.
7. The gate re-runs `run_project_model_gate` on that golden/control snapshot and requires it to pass.
8. The gate loads the embedded planted-negative snapshot, verifies its canonical hash, verifies the declared mutation shape, and re-runs `run_project_model_gate` on it.
9. The planted-negative report must fail with the expected gate/location/text delta, and the golden/control report must not contain that same violation.
10. `golden_control_passed` and `discrimination_passed` in the artifact must agree with the recomputed outcomes; they are never trusted by themselves.

A path pointing to missing JSON, arbitrary prose, mismatched ids, mismatched graph hash, stale/replayed control hash, missing embedded negative, missing expected delta, traversal path, or a wrong result hash is fake success and must fail the gate.

## Security and cost boundaries

Probe execution is deterministic local Python only. It must not call live LLM providers, network APIs, credentials, GitHub, deployment tools, or paid services. It must not modify protected paths or generated artifacts. It writes only snapshot-bundle artifacts and test temp files.

## Acceptance criteria

This slice is accepted when tests prove:

1. A valid golden fixture passes the probe.
2. A path-bucket planted negative fails the probe.
3. Proof is written only when evaluation ran and passed.
4. Gate accepts a passed probe with valid proof JSON and recomputed gate outcomes.
5. Gate rejects passed probe with missing/invalid proof JSON.
6. Gate rejects forged-but-internally-consistent proof whose embedded negative does not actually discriminate.
7. Gate rejects replaying a valid proof onto a different snapshot with the same graph hash but different canonical control hash.
8. Gate rejects absolute or `..` proof paths.
9. Gate rejects planted negatives that fail only for incidental unrelated violations.
10. Gate rejects or gaps failed/unrun probes.
11. Re-running the same probe on the same inputs is deterministic.
12. Fixture/meta-decomposer still emits no passed probe when probe execution is not enabled.
