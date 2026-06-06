# Project Model v0 shared contract

Compatibility target for child agents: `schemaVersion: project-model/v0`, this document, and `docs/schemas/project-model-v0.schema.json`.

Parent issue: <https://github.com/leonbreukelman/build-arena/issues/2>

Child implementation tickets should link back here and should not redefine `decomposition`, `observable check`, or `F3` locally.

## Purpose

Project Model v0 is the thin shared contract between:

- `build-arena`: owns and emits the Project Model from a primary task/backlog item.
- `elenchus-core`: consumes the Project Model and emits advisory alignment / explanation-quality signals.
- `arena-calibration`: proves the contract and evaluator with labeled fixtures, including non-code F3 cases.

The model is pre-code. It can describe source code, but it can also describe architecture, process, strategy, policy, documentation, fixtures, or operating-loop surfaces.

## F3 definition

F3 means real, load-bearing reasoning aimed at the wrong target.

More precisely: the rationale or proposal can be coherent and causally tied to the proposed artifact/action, but it is aimed at the wrong objective, wrong component, wrong sequence, or a too-narrow visible example rather than the decomposed project goal.

F3 is not just code-patch generalization. A code patch that hardcodes a visible test is one low-level F3 example. The same failure can happen when:

- an architecture proposal optimizes a dashboard while the actual blocker is event provenance;
- a process proposal adds a review ritual but misses the sequencing dependency that makes the workflow safe;
- a strategy proposal solves the demonstration case while ignoring held-out customer/operator cases;
- a spec proposal names components correctly but leaves the high-risk surface unclassified.

Do not collapse F3 into F2. F2 is decorative or fabricated rationale; F3 is load-bearing rationale pointed at the wrong thing.

## Machine-readable representation

The v0 JSON Schema lives at:

- `docs/schemas/project-model-v0.schema.json`

Worked examples live at:

- `docs/examples/project-model-v0-code-adjacent.json`
- `docs/examples/project-model-v0-process-strategy.json`

The current `arena.decomposer.ProjectModel` in `arena/decomposer.py` is the Phase 5 scanner model (`schema_version: project-model/v0.1`) and remains supported. The shared contract is emitted through an explicit adapter so existing scanner CLI/API consumers do not regress:

```bash
uv run python -m arena.decomposer \
  --project /path/to/project \
  --format project-model-v0 \
  --source-task "Primary task being decomposed" \
  --primary-backlog-item "https://github.com/owner/repo/issues/123" \
  --output project-model-v0.json
```

`--source-task` maps to `source.task` and `goal`; `--primary-backlog-item` maps to `source.primaryBacklogItem`. Optional `--repo` and `--issue` populate the remaining `source` metadata. Downstream repos should consume the `schemaVersion: project-model/v0` JSON and should not consume the internal `schema_version: project-model/v0.1` scanner shape as the cross-repo contract. The CLI writes the JSON before returning quality-gate failures, so unclassified surface and verification gaps remain visible artifacts instead of being hidden by the exit code.

## Required top-level fields

### `schemaVersion`

Required constant: `project-model/v0`.

This is the compatibility target child repos must name in issues, fixtures, adapters, and tests.

### `id`

Stable model id for the decomposed task/project surface.

### `source`

Object describing where the model came from.

Required:

- `task`: plain-language task or prompt being decomposed.
- `primaryBacklogItem`: canonical backlog item or issue URL.

Optional but recommended:

- `repo`
- `issue`

### `goal`

One concrete objective. It must be more specific than “improve the project.”

A good goal states what success changes in the world or project state.

### `nonGoals`

Explicit exclusions. Non-goals prevent downstream agents from treating nearby work as in scope.

Examples:

- no live paid LLM/API calls for acceptance;
- no Elenchus production allow/deny gate;
- no arena-calibration fixture implementation in the parent contract issue.

### `components`

The project surfaces that matter for the goal. A component is not merely a file group; it is a load-bearing responsibility boundary.

Required per component:

- `id`
- `name`
- `kind`: one of source, test, documentation, configuration, spec, process, architecture, strategy, data, integration, operations, fixture, unknown.
- `riskLevel`: low, medium, high.
- `responsibilities`: what this component owns.
- `ownedSurfaces`: files, issues, docs, artifacts, decisions, workflows, APIs, fixtures, or other surfaces owned by the component.
- `observableCheckIds`: ids of checks that can observe whether this component is doing its job.

A component with no observable check is not acceptable in v0. If it cannot be observed yet, represent that as a verification gap and keep the quality gate failing until a check or deliberate human decision exists.

### `dependencies`

Directed dependency or sequencing constraints between components.

Required per dependency:

- `id`
- `fromComponent`
- `toComponent`
- `kind`: requires, precedes, blocks, feeds, or informs.
- `description`
- optional `observableCheckIds`

For directional kinds (`requires`, `precedes`, `blocks`), cycles or direct reverse dependencies are contradictions.

### `invariants`

Rules that must not be violated while pursuing the goal.

Required per invariant:

- `id`
- `description`
- `componentIds`
- `observableCheckIds`

Examples:

- no live API spend required by acceptance;
- Elenchus is advisory, not an oracle;
- F3 must remain distinct from F2;
- scorer/verifier calibration fixtures are oracle data, not optimization targets.

### `observableChecks`

Named checks that produce inspectable evidence.

Required per check:

- `id`
- `componentId`
- `mode`
- `description`
- `observableSignal`
- `evidenceRequired`
- optional `noLiveApi`

Allowed modes:

- `test`
- `static-analysis`
- `simulation`
- `inspection`
- `artifact-audit`
- `stakeholder-decision`
- `non-code-rubric`
- `external-observation`

#### Observable/measurable for non-code work

A non-code check is observable when a reviewer can inspect a concrete artifact and decide pass/fail without trusting the agent’s vibes.

Good non-code checks include:

- an ADR or spec section containing named decisions and non-goals;
- child issue bodies that link the same compatibility target;
- a tabletop transcript with expected/actual decisions;
- a process dry-run log showing sequence and stop conditions;
- a checklist/rubric with item-level outcomes;
- stakeholder approval recorded as a named decision, when the decision is genuinely human-owned.

Bad non-code checks:

- “review architecture” with no reviewer, artifact, or pass/fail condition;
- “ensure alignment” with no issue/doc evidence;
- “make strategy robust” with no held-out scenario.

### `evidenceRequirements`

Evidence classes accepted by the model.

Required per item:

- `id`
- `description`
- `acceptedArtifactTypes`
- `requiredFor`

Evidence can be terminal output, a JSON artifact, a diff, an issue URL, an ADR excerpt, a dry-run log, a test transcript, or a human decision record.

### `assumptions`

Known assumptions, preferably with `status` = assumed, confirmed, or disputed.

Assumptions are not evidence. Elenchus should be able to flag unsupported assumptions separately from invariant violations.

### `risks`

Known failure risks.

Required per risk:

- `id`
- `level`
- `description`
- optional `componentId`
- optional `mitigation`

A high-risk component must have at least one held-out probe or counterexample.

### `nearNeighborAlternatives`

Plausible nearby proposals that are not the primary choice.

Required per alternative:

- `id`
- `description`
- `whyNotPrimary`
- `distinguishingEvidence`

Near-neighbors are what make wrong-target F3 visible. If the model has no alternatives, a proposal can sound specific while ignoring the real target distinction.

### `heldOutProbes`

Examples, counterexamples, perturbations, tabletops, or negative controls used to detect too-narrow reasoning.

Required per probe:

- `id`
- `componentId`
- `probeType`: held-out-example, counterexample, perturbation, tabletop, or negative-control.
- `scenario`
- `expectedBehavior`
- `evidenceRequired`

Code probes can be executable tests. Non-code probes can be tabletop scenarios or artifact reviews, but they still need expected behavior and evidence.

### `verificationGaps`

Known missing checks or unresolved validation holes.

A verification gap is not a success criterion. It is an explicit “do not trust this surface yet” marker with a proposed closure check.

Required per gap:

- `id`
- `severity`
- `description`
- `affectedComponentIds`
- `proposedClosureCheck`

### `unclassifiedProjectSurface`

Significant surfaces that are not owned by any component.

This is required even when empty. Non-empty `unclassifiedProjectSurface` fails the quality gate until each surface is classified or explicitly removed from scope.

Required per item:

- `id`
- `description`
- `reasonUnclassified`
- `candidateOwners`

### `advisorySignalHandoff`

The expected Elenchus consumer contract.

Required in v0:

```json
{
  "consumer": "elenchus-core",
  "expectedFields": [
    "componentAlignment",
    "invariantViolations",
    "dependencyViolations",
    "unsupportedAssumptions",
    "evidenceGroundingGaps",
    "nearNeighborResistance",
    "fLabelHint"
  ],
  "optionalFLabelHint": true
}
```

## Expected Elenchus advisory signal shape

Elenchus should consume a candidate proposal/rationale plus a Project Model v0 document and emit advisory evidence shaped like:

```json
{
  "schemaVersion": "project-model-advisory-signal/v0",
  "projectModelId": "...",
  "candidateId": "...",
  "componentAlignment": [
    {
      "componentId": "...",
      "status": "aligned|misaligned|unsupported|not-addressed",
      "explanation": "...",
      "evidenceRefs": ["..."]
    }
  ],
  "invariantViolations": [
    { "invariantId": "...", "explanation": "...", "evidenceRefs": ["..."] }
  ],
  "dependencyViolations": [
    { "dependencyId": "...", "explanation": "...", "evidenceRefs": ["..."] }
  ],
  "unsupportedAssumptions": [
    { "assumptionId": "...", "explanation": "..." }
  ],
  "evidenceGroundingGaps": [
    { "checkId": "...", "missingEvidence": "..." }
  ],
  "nearNeighborResistance": [
    {
      "alternativeId": "...",
      "status": "distinguished|not-distinguished|contradicted",
      "explanation": "..."
    }
  ],
  "fLabelHint": {
    "label": "F1|F2|F3|F4",
    "confidence": "low|medium|high",
    "explanation": "optional advisory hint, not an oracle verdict"
  }
}
```

This signal is advisory. Build Arena must not treat it as objective truth, automatic acceptance, or a production allow/deny gate until calibration proves the signal separates labeled cases.

## Decomposition quality gate / meta-F3 guard

The quality gate protects against a bad Project Model becoming the ruler that downstream evaluators optimize against.

The deterministic implementation lives in `arena/project_model_v0.py` as `evaluate_quality_gate(model)`.

It fails on:

1. `component_without_observable_check`
   - A component has no linked observable check.
2. `vague_decomposition`
   - A component is named or described as misc/general/stuff/various/etc. rather than a responsibility boundary.
3. `missing_dependencies`
   - Multiple components exist but no dependency or sequencing constraints are declared.
4. `contradictory_dependencies`
   - Directional dependencies directly reverse each other or form a cycle.
5. `unclassified_project_surface`
   - Significant project surface is left unowned.
6. `missing_held_out_probe`
   - A high-risk component has no held-out probe or counterexample.

The gate can also report structural compatibility errors such as Pydantic/schema validation errors, unsupported `schemaVersion`, missing components/check collections, missing check references, observable-check component mismatches, or dependencies pointing to unknown components.

## Worked examples

### Code-adjacent example

`docs/examples/project-model-v0-code-adjacent.json` models the arena-calibration tokenizer F3 case. It keeps continuity with current fixture language but frames the failure as explanation-to-spec / proposal-to-project generalization, not merely “patch generalization.”

The held-out probes check whether a visible-test-passing tokenizer proposal also handles unseen span inputs and whether a hardcoded lookup is rejected.

### Non-code architecture/process/strategy example

`docs/examples/project-model-v0-process-strategy.json` models the cross-repo rollout process itself. Components are architecture/process/strategy surfaces, and their checks are issue-body inspection, non-code rubric review, and fixture-feedback artifact audit.

This demonstrates that non-code project reasoning can still have observable checks, dependencies, invariants, near-neighbor alternatives, and held-out probes.

## Child ticket compatibility requirements

All child tickets should target:

- `schemaVersion: project-model/v0`
- `docs/project-model-v0.md`
- `docs/schemas/project-model-v0.schema.json`
- the two worked examples under `docs/examples/`

Expected ownership split:

- build-arena issue #3: emit or map the current decomposer output into Project Model v0 while preserving existing decomposer behavior and no-live-API guarantees.
- elenchus-core issue #4: consume Project Model v0 and emit the advisory signal shape above; do not redefine the Project Model or become a truth oracle.
- arena-calibration issue #3: add fixtures/harness cases that prove F1/F2/F3/F4 separation against this contract, including at least one non-code F3 case.

Open compatibility question for implementers: whether build-arena should keep `schema_version: project-model/v0.1` as an internal scanner model and add a separate exporter, or rename the emitted wire format once all current decomposer tests are adjusted. Until issue #3 resolves that, the compatibility target remains the docs/schema/examples listed above.
