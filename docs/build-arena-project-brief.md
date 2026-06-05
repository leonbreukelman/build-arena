# Build Arena — Project Brief

Orientation document for a fresh coding-agent session. Read this after the constitution, before touching code. It describes what build arena is, the architecture, the design decisions and their rationale, the known limits, and the backlog. It does not describe today's task — that lives in the current-state file.

Read order each session: `build-arena-constitution.md` (how to behave) → this brief (what the project is) → current-state file (what to do now).

---

## What build arena is

An autonomous iterative-improvement loop for software projects. A project is decomposed into measurable units. Each unit is improved through a bounded propose-verify-promote cycle. Connections between units are first-class objects at the next layer up, with assume-guarantee contract semantics. The operator defines the goal and the scoring dimensions; the loop iterates against them.

The axiom governing everything: **every claim the agent makes must be verifiable by something that is not the agent.** Verification is mechanical first, not cognitive. An LLM judging its own or a peer's output is the weakest form of verification and is never the load-bearing check.

The project is being built verifier-first. The order is deliberate: prove the verification machinery discriminates good from bad on hand-crafted inputs before any optimization loop is wired up. A loop built on a verifier that cannot discriminate produces confident slop. That failure mode has already cost the operator a prior project; it is the thing this architecture exists to prevent.

---

## Current phase: calibration

The project is in the calibration phase, not the loop phase. The deliverable of this phase is a **calibration repo**: a frozen set of hand-crafted fixtures with known-correct verdicts, plus the Scorer and Verifier exercised against them. The calibration repo is the ruler used to measure whether the Scorer and Verifier work. It becomes a permanent regression harness — any future change to Scorer or Verifier is re-run against it.

The loop itself (Hypothesizer, promotion to a real project, divergence detection at scale) is not built and is out of scope until calibration is sound.

---

## Architecture

### Verification hierarchy

Strongest first. The Scorer and Verifier are pinned to specific tiers.

1. Mechanical / deterministic — tests pass, type check, AST diff, benchmark delta, mutation tests, exit codes. Output is a bit. No model judgment.
2. Structural — formal properties, reasoning ablation (Lanham four-test), property-based testing, fuzzing. Mechanical, probing causal structure.
3. Different-class model — small classifier, embedding similarity, a model trained for one narrow signal. Breaks correlated failures with the worker LLM.
4. Different-instance LLM, adversarial framing — "find the bug," judge with information the worker lacked. Weak; supplement only.
5. Same model, self-evaluation — noise. Never used.

The **Scorer** is strictly tier 1. It runs each fixture's measurement command against baseline and patched trees, counts failures, and emits promote/reject on strict-greater-than improvement. No LLM anywhere in the Scorer.

The **Verifier** is tier 2. It runs the Lanham four-test reasoning ablation. It does use LLM calls, but as a mechanical probe of causal structure (does perturbing this reasoning component change the regenerated patch), not as a judge of quality.

### Components

- **fixtures.py** — Fixture dataclass, manifest loader, layout validation. Loads the frozen fixture set.
- **scorer.py** — Tier-1 mechanical scorer. Subprocess + pytest-output parse. Promote/reject on strict-greater-than failure-count delta. Ties reject. Timeouts reject (a timed-out measurement cannot claim improvement). Emits a separate integrity signal (observed counts vs. manifest claims) so the runner can distinguish "fixture broke" from "verdict is correct on a working fixture."
- **patch_eq.py** — AST-normalized patch equivalence. Two patches are equivalent if, applied to the same baseline, they produce files whose Python ASTs are equal after normalization (whitespace and comments stripped; identifiers preserved, since renaming changes semantics). Stricter than string match, looser than behavioral equivalence. Behavioral equivalence is deliberately avoided here because it bleeds the Verifier into Scorer territory, which the architecture separates.
- **lanham.py** — The four perturbations as pure functions: Early Answering, Adding Mistakes, Paraphrasing, Filler Tokens. Paraphrasing is a semantic control — it should NOT change the regenerated patch for a load-bearing component. If paraphrasing frequently changes the patch, the worker is brittle to surface form and the signal from the other three perturbations is degraded.
- **verifier.py** — Orchestrates the four-test. For each reasoning component, generates 4 perturbed reasonings, regenerates a patch from each via the worker, compares to the reference patch under AST-equivalence, majority-votes across N samples. A component is load-bearing if ≥2 of 4 perturbations change the patch. Patch-level verdict is accept if load-bearing fraction ≥ threshold; threshold swept across {0.50, 0.66, 0.75}. Emits per-component verdicts, not just patch-level — a Verifier returning the right top-level verdict for the wrong per-component reasons is silently broken, and per-component output is how that is caught.
- **runner.py** — Loads fixtures, calls Scorer, short-circuits on reject (Verifier not invoked), calls Verifier on promote. Records mismatches and continues rather than halting on first mismatch. Emits a single timestamped YAML discrimination matrix per run. Exit 0 iff all fixtures match ground truth and integrity is clean; else exit 1. Accepts injected worker/judge for hermetic testing.
- **llm.py** — The only module that imports a provider SDK. Worker and Judge are typing protocols. Real and Fake implementations both satisfy them. Swapping providers is a change here and nowhere else. This seam is load-bearing: it lets the calibration set run hermetically with deterministic scripted workers, and it isolates provider/model changes from verifier logic.
- **exercise_verifier.py** — Hermetic harness exercise. Scripts deterministic worker behavior per fixture and asserts the Verifier produces predicted load-bearing patterns. Prints `ALL HARNESS PREDICTIONS HOLD` on success. This is the non-API proof that the harness logic is correct; it is the "verifiable by something that is not the agent" axiom applied to the LLM layer, with a scripted worker as the non-agent oracle.

### Worker / Judge split

The Verifier needs a **worker** model to regenerate patches under perturbations and a **judge** model for the discrimination report. For calibration the worker is a canonical reference model (not the original patch author), because fixtures are agent-independent static artifacts — the reasoning in each manifest is hand-written, not produced by a specific agent. In the real loop later, the worker should be the same agent that produced the patch (tests whether reasoning is load-bearing for that specific agent); that is a backlog item, an `llm.py` change, not a verifier change.

---

## The frozen fixture set

Four fixtures. Frozen. The discrimination matrix below is ground truth. Any Scorer/Verifier implementation is correct iff it reproduces it.

| Fixture | Description | Scorer should | Verifier should |
|---|---|---|---|
| F1_loadbearing_good | Good patch, load-bearing reasoning | promote | accept |
| F2_fabricated_good | Good patch, fabricated reasoning (real fix, disconnected rationale) | promote | reject |
| F3_bad_passes_tests | Bad patch (hardcoded lookup), honest load-bearing reasoning | promote | reject |
| F4_trivial | No-op/docstring change, no behavioral delta | reject | n/a (Verifier not invoked) |

All fixtures share the tokenizer/span domain so the Verifier cannot discriminate on domain features rather than reasoning structure. Component counts and conclusion-slot positions vary across fixtures (F1: 4 components, conclusion slot 4; F2: 4, slot 4; F3: 5, slot 3; F4: 2) specifically to break positional heuristics — a Verifier that "ignores the last slot" must not pass the set by accident.

### F3 is a documented insufficiency, not a defect

F3 is the critical fixture. Its patch is bad (hardcodes test inputs, does not generalize) but its reasoning is honest and fully load-bearing — perturbing any component changes the patch. Therefore the Lanham four-test alone will ACCEPT F3, which is the wrong verdict. This is expected and documented. It is a calibrated negative result that proves the Verifier needs a second, orthogonal axis: **patch generalization**. Lanham catches fabricated reasoning that doesn't constrain the patch (F2); it cannot catch honest reasoning that constrains the patch to the wrong thing (F3).

This is Deutsch's hard-to-vary criterion applied at two layers. Lanham tests reasoning-to-patch. The needed second axis tests explanation-to-spec: the F3 lookup-table explanation is easy-to-vary in Deutsch's sense — it explains the test case but not the spec. Same criterion, second instantiation. Do not attempt to make the Verifier reject F3 by tightening Lanham; that is the wrong fix. F3 is rejected by the second axis, which is a backlog item.

---

## Build status

Calibration phase, milestones complete except live validation:

- Calibration fixtures F1–F4: built, frozen, mechanically verified.
- Scorer: built. 4/4 against ground truth in hermetic and live runs. Negative paths (integrity mismatch, timeout, parser shapes) covered.
- Runner: built. Short-circuit invariant verified (Verifier invoked on F1–F3, not F4). Worker injection seam present.
- Verifier: built. Hermetic exercise passes — `ALL HARNESS PREDICTIONS HOLD`. Live validation against a real model is the open item.
- llm.py provider seam: present. Real + Fake worker/judge implementations.

Open item: **live validation.** The harness is mechanically correct (hermetic exercise + 4/4 Scorer prove it). What is unvalidated is whether a real worker model produces reliable load-bearing discrimination. See the current-state file for the live-run findings and today's task.

---

## Known findings and lessons

These are calibrated results, not speculation.

- **Worker-noise failure mode is real.** A live run produced `load_bearing_fraction: 1.0` on every fixture — the worker regenerated a different patch under every perturbation including paraphrasing controls. Result: no discrimination. The harness was correct; the worker was too noisy. Diagnostic signal: paraphrasing perturbations changing the patch indicates worker brittleness to surface form. If all fractions pin at 1.0, suspect either a noisy/wrong worker model or AST-equivalence being too strict.
- **Model routing matters.** That run went through OpenRouter with `ANTHROPIC_BASE_URL` redirected; the model actually served may not have been the one requested. Always pin exact model strings and confirm via the response which model served the request. Aliases that redirect to a default model are a known trap.
- **AST-equivalence is a suspect when discrimination collapses.** If a known-discriminating fixture set returns uniform load-bearing fractions, patch_eq may be treating cosmetically-different-but-equivalent patches as changed. This is a harness fix (loosen normalization toward behavioral equivalence carefully, without bleeding into the Scorer), distinct from a model swap.

---

## Backlog, roughly ordered

1. **Live validation** of the Verifier against a real worker that discriminates. Current blocker on declaring calibration done.
2. **Patch-generalization axis** — the second orthogonal verification axis that rejects F3. Candidate: elenchus-validator (operator's repo, TypeScript HTTP service) using its `contextGrounding` and `alternativeResistance` subscores; do NOT use its `specificityMargin` or overall `recommendation` (marked unreliable by elenchus itself). Integrate as a second required gate alongside Lanham — both must accept. Run as a separate service, call from Python. Action-type taxonomy needs extension from SRE actions to "apply code patch"; propose the schema change before implementing. Integrate only after Lanham is independently sound on the live set.
3. **6-fixture extension** — F5 Goodhart (passes both Scorer and Verifier, exposes joint blind spot, motivates orthogonal measurement), F6 bad-fails-tests (Scorer negative-path sanity). One fixture should be borrowed from a real empirical failure rather than designed, to avoid fitting the verifier to operator imagination.
4. **Schema revision** — extend the goal model (`arena-goal.linkml.yaml`) with a Contract class (assume-guarantee edge objects between primary units), a SlowUpdate class (protected longitudinal guidance, epoch cadence, gate-tested), and an orthogonal-axis class for cross-cutting concerns (logging, security, observability, performance) that do not fit the unit hierarchy. Reconcile DivergenceKind enum against the loop spec — single source.
5. **First real Goal instance** — fill the schema against a real project and the seven anchoring questions; stress-tests schema shape against reality.
6. **Worker = original-agent** option in the real loop (the `llm.py` change deferred from calibration).
7. **Strategy-as-trainable-object** — replace direct project modification with modification of the agent's strategy for modifying the project; deployed artifact becomes heuristics/decomposition policy, project metrics become the gate. Different architecture; substrate is text not code, limiting expressiveness but collapsing the decomposer-verification recursion into one project-level gate. Revisit only after a working system exists.

---

## Hard constraints for any session

- Do not modify frozen fixtures or the discrimination-matrix ground truth. The fixtures are the ruler; changing them invalidates every prior measurement.
- Do not attempt to make the Verifier reject F3 via Lanham. F3 is rejected by the patch-generalization axis (backlog item 2), not by tightening reasoning ablation.
- Do not introduce an LLM as a load-bearing verification check. The Verifier's LLM use is a mechanical probe (does the patch change), not a quality judgment.
- Provider/model changes are `llm.py` only. If a change appears to require touching verifier/runner/scorer/fixtures, stop and flag it.
- Pin exact model strings; confirm the served model matches the requested one. Do not trust aliases.
- Privacy/security value judgments (e.g., sending real project code to a third-party API, data-sharing enrollment) are operator decisions, never delegated. There is an open tripwire: data sharing / third-party retention must be resolved before any real (non-toy) project data touches an external API.

---

## Reference files

- `build-arena-constitution.md` — behavior layer, read first every session.
- this brief — orientation, read second.
- current-state file — today's task and latest findings, read third, rewritten per session.
- `arena-goal.linkml.yaml` — the goal model schema (per-project layer).
- `README.md` — run instructions (install, key, run, expected output).
