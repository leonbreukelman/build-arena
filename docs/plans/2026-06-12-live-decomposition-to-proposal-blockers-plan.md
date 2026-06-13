# Plan — live decomposition-to-proposal blockers

Date: 2026-06-12
Scope: Build Arena live `fmc-mcp` flow from decomposition through proposal-in-hand.

## Confirmed issue

A real live Grok 4.3 run against `fmc-mcp` completed provider calls but stopped before proposal because the live Project Model failed the deterministic gate, and the subsequent intake selected a missing-file docs target that the current diff proposer cannot handle.

## Confirmed root causes

Opus confirmed high-confidence root causes in `docs/verification/2026-06-12-opus-fmc-live-root-cause-review.json`:

1. Build Arena is asking the live LLM to perform exact directed import-edge bookkeeping that the gate can already derive deterministically from graph evidence plus component ownership.
2. Intake can select an absence finding (`docs/index.md`), but `DiffProposerRunner` rejects non-existent target files before transport, so the top handoff cannot become a patch proposal.

Important precision from Opus:

- Contract direction is mechanical given graph + ownership, but component ownership is still partly LLM-provided. The fix must not claim to make ownership deterministic.
- Edge-coverage closure will make the edge-coverage check validate Build Arena’s generated closure. That is acceptable only because import-edge contract closure is mechanical; the LLM is still constrained by ownership, responsibility quality, provenance, checks/gaps, and non-import semantic claims.
- Do not relax the gate.

## Additional evidence gathered after Opus review

Representative raw gate failures from the second live attempt:

- `component_measurability`: `Component comp:resources has no contracts, checks, or gaps.`
- `component_measurability`: `Component comp:tools has no contracts, checks, or gaps.`
- `contract_references`: `Contract contract:server-init supporting edge edge:2f396cd20dda22594653 does not connect the declared from/to components.`
- `edge_coverage`: `Owned import edge edge:25c3c6d20a305beeeca9 from comp:resources to comp:client is not covered by any contract between those components.`
- `edge_coverage`: `Owned import edge edge:36e31fda6d2df7b6c8ff from comp:server to comp:tools is not covered by any contract between those components.`

The two residual component failures were the contract/check/gap sub-check only, not weak responsibility text.

Exploratory pure transform on the saved second live snapshot:

- Remove model contract supporting-edge refs that do not support their declared endpoints.
- Drop model contracts that become empty after invalid-edge stripping.
- Add stable `contract.auto.<edge-id>` contracts for every owned cross-component import edge derived by the same gate helper.
- Attach each auto contract to the from/to components.
- Result: deterministic gate passes with zero violations.

Patch-gate exploratory check:

- Existing `validate_unified_diff` accepts a proper single new-file diff for `docs/index.md`.
- It rejects a protected/read-only new-file diff (`private/new.py`) as `boundary_violation`.

## Implementation strategy

### Principle

Keep this simple and deterministic. Do not add another LLM call, another review loop, a gate bypass, or a broad runner architecture.

### Change 1 — deterministic import contract closure

Add a small pure transform in `arena.project_decomposer_ai` after `_snapshot_from_model_output(...)` and before `finalize_snapshot_identity(...)`:

```text
snapshot = _close_import_contracts(snapshot, graph)
```

Behavior:

1. Build `nodes`, `edges`, and `components` from deterministic graph + snapshot ownership.
2. Validate existing model contracts:
   - Keep only supporting edge IDs for which `_edge_supports_contract(edge, nodes, from_component, to_component)` is true.
   - Drop model contracts that have no valid supporting edges after filtering.
   - Remove dropped contract IDs from every component’s `contract_ids`.
3. For every import edge, call `_component_pairs_for_import_edge(edge, nodes, components)`.
4. For each non-self pair without an already-valid contract supporting that edge, add one stable deterministic contract:
   - id: `contract.auto.<edge-id-without-prefix>`
   - from/to: derived pair
   - supporting_edge_ids: `[edge_id]`
   - provenance_refs: edge provenance if present, otherwise from-component provenance if present
   - near_neighbor_alternative_ids: `[]`
5. Attach the auto contract ID to both endpoint components if not already present.
6. Sort deterministic contracts, component contract IDs, and supporting edge IDs for stable snapshot hashes.

Constraints:

- Do not invent components.
- Do not reassign ownership.
- Do not change graph/gate behavior.
- Do not mutate raw model output artifacts.
- If an edge cannot map to endpoint components, leave it for the gate to reject.
- If an auto contract cannot cite edge provenance or endpoint-component provenance, do not emit it; leave the failure visible to the gate.
- Closure may satisfy a component's contract/check/gap measurability only when that component participates in real graph-derived cross-component import contracts. It must not rescue an isolated/no-edge component that the model left without contracts, checks, or gaps.
- Keep one gate-aligned closure entrypoint as the shared source of truth so decomposer code does not duplicate the gate's import-edge pair logic.

### Change 2 — narrow new-file support in diff proposer

Patch `DiffProposerRunner.apply()` in `arena/runners/diff_proposer.py`:

1. Preserve existing single-target and boundary checks via `_single_target_path()` before file existence relaxation.
2. If `target / target_path` exists and is a file, keep existing behavior.
3. If it exists but is not a file, reject.
4. If it does not exist:
   - Verify parent directory is inside the repo and not a file.
   - Send `file_contents=""` to the transport.
   - The prompt should explicitly say the target file does not exist and the response must be a single-file new-file unified diff.
5. Keep `validate_unified_diff` and `git apply --check` as the real proof.
6. Do not add multi-target or directory-wide support.

### Tests first

#### Decomposer contract closure tests

Add to `tests/test_project_decomposer_ai.py`:

1. `test_recorded_live_shaped_output_gets_deterministic_import_contract_closure`
   - Create a small repo with `server -> client -> config` imports.
   - Use recorded model output with plausible components but missing/reversed contracts.
   - Assert before/failing failure is represented by saved fixture shape or by direct helper if available.
   - Run `build_project_model_snapshot(... llm_mode="recorded")`.
   - Assert gate passes.
   - Assert `contract.auto.*` contracts exist in correct directions.
   - Assert raw model output sidecar remains missing/reversed, proving audit preservation.

2. `test_contract_closure_does_not_mask_unowned_edges`
   - Use recorded model output that fails to own one imported target module.
   - Assert gate still fails with inventory/edge coverage rather than being papered over.

3. `test_contract_closure_is_idempotent_and_stable`
   - Run recorded output through snapshot build twice with overwrite.
   - Assert snapshot contracts and snapshot hash are stable.
   - Assert running closure on an already-closed snapshot is a no-op.
   - Assert `contract.auto.<edge-id>` IDs do not collide with model-provided contract IDs.

4. `test_contract_closure_does_not_mask_unmeasurable_no_edge_component`
   - Use a component with no owned import edges and no contracts/checks/gaps.
   - Assert it still fails component measurability.

5. `test_contract_closure_requires_provenance_for_auto_contracts`
   - Exercise the closure helper with an edge/component provenance gap.
   - Assert no unprovenanced auto contract is emitted and the gate remains non-passing.

6. Auto-contract shape assertions:
   - Assert generated contract endpoint direction satisfies `contract_references`.
   - Assert generated contract closes `edge_coverage`.
   - Assert generated contract carries non-empty provenance.
   - Assert `near_neighbor_alternative_ids == []`.

#### Diff proposer new-file tests

Add to `tests/test_diff_proposer.py`:

1. `test_diff_proposer_applies_single_new_file_diff_after_patch_gate`
   - Hypothesis target: `docs/index.md`.
   - Fake transport returns valid `/dev/null -> b/docs/index.md` new-file diff.
   - Assert file exists, patch/provenance sidecars exist, and request file_contents is empty.

2. `test_diff_proposer_rejects_protected_missing_target_without_transport_call`
   - Hypothesis target: protected/read-only missing path.
   - Assert RunnerError and FakeTransport.requests remains empty.

3. `test_diff_proposer_applies_nested_new_file_diff_when_parent_is_missing`
   - Hypothesis target: `docs/sub/index.md`.
   - Assert `git apply --check` creates parent directories through the patch path and stays inside repo.

4. Existing multi-target rejection remains unchanged.

## Verification plan

1. RED: run the new targeted tests and verify failures.
2. GREEN: implement minimal code.
3. Run targeted tests:
   - `uv run pytest tests/test_project_decomposer_ai.py::<new tests> tests/test_diff_proposer.py::<new tests> -q`
4. Run broader affected tests:
   - `uv run pytest tests/test_project_decomposer_ai.py tests/test_diff_proposer.py tests/test_project_model_cli_ai.py -q`
5. Run full suite:
   - `uv run pytest tests -q`
6. Static checks:
   - `uv run ruff check .`
   - `uv run pyright`
7. Re-run recorded second live raw output through `llm_mode=recorded` against the live `fmc-mcp` repo to prove the previously failing Grok output now gates green without another paid model call.
8. Re-run freshness, intake, and handoff.
9. Produce a bounded proposal-in-hand using fake/new-file diff path or live Grok diff transport only after gate/freshness pass and a single-target handoff exists.

## Review sequence

1. Opus plan review before implementation.
2. Implement and verify.
3. Fable review implementation and feedback.
4. Fix any blockers Fable identifies.
5. Opus final result review/sign-off.
6. Return to Leon with plain-English assurance.

## Definition of done

- Saved failing evidence and reviews in `docs/verification/`.
- Tests prove the two blockers are fixed.
- Full test suite, ruff, and pyright pass.
- The saved live Grok 4.3 raw output can be replayed through recorded mode and pass the deterministic Project Model gate.
- A handoff-selected `docs/index.md` proposal can be materialized as a patch artifact without mutating protected paths.
- No live calls beyond the explicitly authorized smoke/decomposition calls unless needed and justified after gate/freshness pass.
