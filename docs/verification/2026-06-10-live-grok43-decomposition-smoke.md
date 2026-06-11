# Build Arena — Live grok-4.3 Read-Only Decomposition Smoke

Date: 2026-06-10
Branch: `ba/live-decomposer-fail-closed`
Model: grok-4.3 (xAI), live, read-only, bounded single call
Scope authorization: pre-live readiness register marks
`read_only_live_decomposition_build_arena` as `allowed_with_guardrails`.
No code changes proposed by the model, no promotion, no broad loop.

## Why this run happened

Leon asked to set grok as the model and perform a REAL run (not a fixture),
find issues, resolve them, and iterate to a clean run, then have Fable review
adversarially. The AI-first decomposition path had a live grok adapter but had
NEVER actually been exercised against a live model — only against fixtures that
emit perfectly-shaped dicts.

## What the first live call exposed (real bugs, not model noise)

1. CRASH: `Component.__init__() got an unexpected keyword argument 'evidence'`.
   Root cause: the build path splatted raw model JSON into strict dataclasses
   (`Component(**item)`) with no validation. `REQUIRED_MODEL_OUTPUT_KEYS` was
   defined but never enforced (dead code).
2. PROMPT/GATE CONTRADICTIONS (found via Fable adversarial review):
   - The prompt said "checks/concerns/gaps/near_neighbors"; the parser required
     "observable_checks/cross_cutting_concerns/verification_gaps/
     near_neighbor_alternatives".
   - The prompt never gave the model the opaque graph identifiers
     (`node:...`, `prov:...`, `edge:...`) the deterministic gate requires.
   - The gate scores inventory coverage against the FULL primary-module set,
     but the prompt only showed an arbitrary 120-node sample — a structural
     ceiling that no model could clear.
   - The gate accepts a held-out-probe OR an explicit probe-validation gap, but
     the prompt told the model neither, so `held_out_probe_presence` was
     guaranteed to fail regardless of model quality.

## Fixes applied (non-protected files: project_decomposer_ai.py, project_model_gate.py)

- Fail-closed coercion: provider key aliases accepted, unknown invented keys
  dropped (raw still persisted to `model-outputs/decomposer.raw.json` for
  audit), missing list fields defaulted, **present-but-non-list fields rejected**
  with a clear error, missing required identity fields raise a named ValueError
  instead of a raw TypeError.
- Security: the model-controlled `acceptance_command_allowlist` is now
  filtered fail-closed — only known symbolic labels or exact declared-check
  command strings, never shell metacharacters — closing a latent command
  execution surface.
- Single source of truth: the prompt now lists the EXACT primary-inventory
  modules the gate scores (via the shared `primary_inventory_nodes` selector),
  teaches the held-out-probe gap escape hatch, and instructs the universal +
  conditional concerns. A drift-guard test asserts the prompt schema keys match
  the snapshot collection fields so this class of bug cannot silently return.
- Regression tests: crash/coercion, scalar-for-list rejection, allowlist
  security filter, prompt/schema drift guard.

## Honest result (the baseline every future decision depends on)

The crash is gone; the run completes end-to-end and emits a real deterministic
gate verdict. After removing the harness-induced contradictions, the same
bounded grok-4.3 call went from 44 violations to 4.

- Gate passed: False
- Violation count: 4 (down from 44 pre-fix)
- Model output counts: {"components": 1, "contracts": 1, "cross_cutting_concerns": 4, "near_neighbor_alternatives": 0, "non_goals": 2, "observable_checks": 1, "verification_gaps": 1}
- By gate: {"contract_references": 2, "cross_cutting_concerns": 2}
- Token usage: prompt=12717 completion=1340 total=15017

Remaining violations (all model-attributable, NOT harness):

- contract_references | error | Contract contract:decomp-core is self-referential after component merge.
- contract_references | error | Contract contract:decomp-core has no supporting graph edges.
- cross_cutting_concerns | error | Protected surfaces exist but protected_surface_integrity concern is missing.
- cross_cutting_concerns | error | Generated surfaces exist but generated_artifact_integrity concern is missing.

Root cause of all 4: grok produced only 1 component for a ~40-module repo
(severe under-decomposition). One component makes every contract
self-referential, and grok also skipped the two conditional cross-cutting
concerns (protected/generated surface integrity) that the prompt explicitly
requested and that apply to this repo. These are genuine single-call model
quality limits, not harness sabotage.

## Interpretation

"Clean run" is satisfied at the honest, defensible line Fable defined:
- CODE path: clean — no crash, fail-closed, full pytest/ruff/pyright green,
  `git diff --check` clean.
- HARNESS: clean — zero harness-induced violations remain; the prompt no longer
  makes gate-passing impossible.
- MODEL: a single bounded grok-4.3 call under-decomposes and does not yet
  produce a gate-passing decomposition. The deterministic gate correctly
  refuses to bless it. The gate was NOT forced green.

This is the system working as designed: the LLM proposes, deterministic checks
decide, and they decided "not good enough yet." Closing that remaining gap is a
model-quality / multi-pass-decomposition problem (more components, iterative
refinement, or a stronger reasoning model), not a code bug — and it is the
correct next investment, not something to paper over.

## Artifacts

Live snapshot dir: `/tmp/build-arena-live-grok43/1781135270-v3/snapshot-a2525bafcf584411`
- `model-outputs/decomposer.raw.json` — exact grok-4.3 output
- `gate-report.json` — deterministic verdict
- `prompts/decomposer-prompt.txt` — the schema-exact prompt actually sent
- `snapshot.json`, `graph.json`, `project-model-v0.json`, `project-model-v1.json`

(Artifacts live under /tmp for this smoke; the durable record is this doc plus
the committed code + regression tests.)


## Update: iterating the prompt toward the gate spec (v3 -> v4)

After Fable's first re-review, I stated more of the gate's rules in the prompt
and reran twice more. Each iteration revealed the next unstated gate rule. This
progression is itself the most important finding.

### v3 (prompt states: schema, ids, primary-module coverage, probe hatch, universal concerns)
- Violations: 4 (by gate: {"contract_references": 2, "cross_cutting_concerns": 2})
- grok produced 1 component -> self-referential contract + 2 missing conditional concerns.

### v4 (prompt additionally states: decompose into MULTIPLE components; contracts must connect two distinct components with a supporting edge)
- Violations: 88 (by gate: {"component_measurability": 5, "edge_coverage": 82, "inventory_coverage": 1})
- grok now produced 7 coherent components covering the repo:
  - comp:decomposer: owns 6 nodes | Manages AI-driven project decomposition and iteration readiness
  - comp:model: owns 5 nodes | Enforces model versioning gates and snapshot integrity
  - comp:graph: owns 4 nodes | Builds and maintains project graph with provenance tracking
  - comp:runners: owns 5 nodes | Executes model runners and diff proposal logic
  - comp:scripts: owns 3 nodes | Performs calibration rebuilds and artifact normalization
  - comp:gates: owns 9 nodes | Validates patches and boundary conditions for safety
  - comp:probe: owns 7 nodes | Runs project probes and meta decompositions
- contracts declared: 0

### Why v4 violations went UP (4 -> 88) — and what it means
The jump is NOT a regression in model quality; grok's decomposition got
materially BETTER (7 sensible components vs 1 file-bucket). The violations rose
because a real multi-component decomposition activates a gate rule the prompt
never stated: `edge_coverage` requires that EVERY import edge between two owned
components be covered by a declared contract. With 7 components and real import
relationships, the gate demanded ~82 contracts; grok declared 0 (the prompt had
implied contracts were optional via "declare >=1 of contract/check/gap").

So 82 of the 88 are an uncommunicated-spec gap (harness), not model
incapability — the same class of bug found and fixed earlier, now one layer
deeper.

## The definitive honest conclusion

The AI-first decomposition gate encodes a large, interlocking specification.
Each prompt iteration surfaces the next unstated rule:
crash -> key-name mismatch -> missing id vocabulary -> inventory sampling cap ->
probe hatch -> single-component file-bucket -> contract edge-coverage.

This is the real, valuable result of the live run — worth more than a green
gate:

1. The code path is now robust and fail-closed (no crash on any real model
   output; verified by tests).
2. grok-4.3 CAN produce a coherent multi-component decomposition with real
   graph-grounded identifiers when the prompt states the rules.
3. Driving the gate to GREEN is not a prompt-tuning task and must not be chased
   by ever-more-specific coaxing (that drifts into overfitting one model to one
   gate). It requires either (a) completing the prompt as a faithful, generated-
   from-the-gate specification of ALL rules, or (b) a multi-pass decomposition
   architecture where the model proposes, sees gate feedback, and revises. Both
   are NEW scope beyond "exercise the live path," and (b) is the more honest
   long-term answer.

The gate was never forced green. A gate that honestly refuses incomplete model
output is the system working as designed.

## Recommended next work (not done here)

- Generate the decomposer prompt's rule list directly from the gate's checks
  (single source of truth) so prompt and gate cannot drift — the recurring bug
  class. A drift test should assert gate-enforced rule coverage, not just key
  names.
- Then decide explicitly: faithful one-shot spec prompt vs. iterative
  gate-feedback decomposition loop. That is a design decision for Leon, not a
  bug fix.
