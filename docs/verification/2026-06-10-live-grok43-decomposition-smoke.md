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
