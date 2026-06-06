# Build Arena — Specification

A complete specification of the build arena system: what it is, the architecture, the design decisions and the reasoning behind each, the calibration methodology, known limits, and the relation to existing work. This document is the canonical record. It explains not only *what* was decided but *why*, and what alternatives were rejected.

Companion documents:
- `build-arena-constitution.md` — the operating rules the agent follows (behavior layer).
- `build-arena-project-brief.md` — orientation for a fresh coding agent (what to act on).
- `build-arena-current-state.md` — volatile per-session task and findings.

This specification is the reference that sits behind all three.

---

## 1. Purpose and scope

Build arena is an autonomous iterative-improvement loop for software projects. The operator defines a goal and the dimensions along which "better" is measured. The system decomposes the project into measurable units, improves each through a bounded propose-verify-promote cycle, and treats the connections between units as first-class objects in their own right.

This document specifies the system, the verification architecture at its core, and the calibration phase currently under construction. It is written for an engineer or a coding agent who needs to understand the system completely, including the reasoning behind each decision.

The project exists to solve a specific, recurring failure: attempts to get an AI to perform iterative improvement work autonomously produce plausible-looking output that does not actually do the job ("slop"). Build arena is the structural answer to why that happens and how to prevent it.

---

## 2. Problem statement

The originating frustration: enormous effort spent making an AI capable of autonomous iterative improvement, with the result being low-quality output despite reusing patterns that appear well-established.

The diagnosis has three parts.

**The pattern is not established.** A general agent that iteratively improves itself and arbitrary projects from a simple foundation does not exist in production anywhere. Reflection, tool use, self-critique, and search exist as fragments. Assembling them into a reliable autonomous improvement loop is the current research frontier, not a stable engineering pattern. Treating it as established is the first mistake.

**The bottleneck is verification, not cognition.** Slop is produced by four mechanisms, in rough order of frequency:

1. *Verification gap.* Without a deterministic check for "this change is an improvement," the agent has no gradient to climb. It generates plausible changes, self-reports success, and proceeds. Output looks correct line by line and is structurally wrong.
2. *State fabrication.* Over multi-step loops the agent loses track of what is actually true versus what it asserted earlier. It will confidently report a build is passing when it never re-ran it.
3. *Unbounded scope.* If the exit condition is "the agent thinks it is done," the result is slop. Working systems have either a fixed contract per iteration or a hard external verifier the agent cannot self-satisfy.
4. *Planning/execution conflation.* When the same actor decides what to do, does it, and judges it, every adversarial signal is removed.

**The capability assumption is wrong.** No current model can hold and verify the scope of "build the whole self-improving frame." The reliable version of the task is bounded: implement individual increments inside a system the operator has built to verify them. The verification system is the part that must exist first and the part the operator cannot delegate wholesale.

---

## 3. Core thesis

Three claims structure the entire design.

**Verification is mechanical first, not cognitive.** The load-bearing check on any change must be something that is not the agent: a test, a type check, an AST comparison, a benchmark delta. An LLM judging output — its own or a peer's — is the weakest form of verification and is never the primary signal. Two instances of the same model class share correlated failure modes; they confabulate together and agree confidently on wrong answers.

**"Better" must be decomposed into measurable dimensions or it cannot be a target.** A goal expressed only as a holistic outcome provides no gradient. The model will report holistic improvement with equal fluency whether or not it occurred. The loop can iterate against a *defined* notion of good; it cannot synthesize good. The decomposition into measurable dimensions is the operator's work and the anchor between intent and system behavior.

**There is a fundamental trade-off between operator load and drift.** Each layer of automation placed above the base loop reduces the operator's workload and widens the gap between operator intent and system action. Closer to the metal: more work, less drift. Further up: less work, more drift. There is no configuration where both are zero. This is a property of the problem, not a tooling limitation. Prior projects failed by being built as if the zero-work, zero-drift level existed; when drift appeared it was treated as a bug rather than as the expected cost of the chosen automation level.

---

## 4. Foundational concepts

### 4.1 The axiom

Every claim the agent makes must be verifiable by something that is not the agent. This single rule generates most of the architecture. It rules out self-reported completion, self-graded quality, and reasoning from un-rechecked state.

### 4.2 The verification hierarchy

Verification mechanisms ranked strongest to weakest. Components are pinned to tiers.

1. **Mechanical / deterministic** — tests pass, type check, AST diff, benchmark delta, mutation tests, exit codes, observability signals. Output is a bit. No model judgment.
2. **Structural** — formal properties, reasoning ablation, property-based testing, fuzzing. Mechanical, but probing causal structure rather than surface correctness.
3. **Different-class model** — a small classifier, embedding similarity, a narrow purpose-trained model. Breaks correlated failures with the worker LLM. Useful for specific signals.
4. **Different-instance LLM, adversarial framing** — "find the bug," judging with information the worker lacked. Weak; supplement only.
5. **Same model, self-evaluation** — noise. Never used as a check.

The discipline: every load-bearing check must do work no model can fake. A second LLM "judge" is not a substitute for a mechanical check; where LLM judging appears in working systems it is paired with mechanical checks, or the judging task is genuinely easier than the work (style, format) rather than equally hard (correctness, causal reasoning).

### 4.3 Bounded fingerprints

A *fingerprint* is one unit of improvement work: one hypothesis, with one mechanically stated success criterion. Changes spanning multiple fingerprints require multiple cycles. No work begins on a fingerprint until success criteria, failure criteria, rollback condition, and scope boundary are all stated mechanically. This bounds scope and prevents the unbounded-exit failure mode.

### 4.4 The operator as editor

The operator does not write the decomposition, the dimensions, or the per-cycle work. The operator *edits*: approves the decomposition, anchors intent with a small set of examples, sets dimension weights, and periodically reviews whether the dimensions still capture intent. The cadence is per-goal at setup and monthly at review — not per-cycle. This is the high-judgment, low-volume work that cannot be delegated because it is the anchor between human intent and system action.

### 4.5 The question protocol

When the agent asks the operator (true blockers and intent-anchoring only):
- The goal admits multiple plausible decompositions with incompatible implications.
- A proposed dimension cannot be made mechanically measurable.
- Two dimensions trade off and weights are not defined.
- An invariant would have to be relaxed to proceed.
- The Verifier rejects what the Scorer would have promoted (a dimension-mismatch signal).
- A new scoring dimension is needed (always the operator's domain).

When the agent proceeds on its own (logging the choice):
- The decomposition is plausible and goal-consistent.
- A measurable proxy exists, even if imperfect.
- A default heuristic applies.
- The choice is within-fingerprint implementation detail.

### 4.6 Default heuristics under uncertainty

- Two decompositions plausible → prefer more mechanical leaves.
- Two implementations plausible → prefer smaller blast radius.
- Two test strategies plausible → prefer the one catching more mutants.
- Two changes both improving → prefer the smaller diff.
- Uncertain about scope → contract, never expand.
- Uncertain about effect → worktree first, never main.
- Verification ambiguous → treat as failure, never success.

---

## 5. The decomposition model

### 5.1 Goals to measurable dimensions

A goal is decomposed until each leaf is mechanically measurable. If a leaf is not measurable, decompose further; if it cannot be decomposed further and still is not measurable, escalate to the operator. Scoring is multi-dimensional: each dimension is mechanically measurable (test pass rate, benchmark delta, type coverage, architecture conformance via AST patterns, regression-suite status, deployment health, observability signals, documentation coverage), weighted by operator judgment. Acceptance is **comparative, not absolute** — score state at T+1 against T on the same dimensions; promote on strict improvement (Pareto, or weighted-sum within a Pareto-acceptable region). "Is this good" is never asked of the loop; "is this better on the declared dimensions" is.

The risk is Goodhart: optimize the measured proxies and the unmeasured dimensions may drift. The defenses are a regression suite encoding things-that-must-remain-true (auto-reject on breach regardless of local improvement), and the operator's monthly review of whether the dimensions still capture intent.

### 5.2 Can decomposition itself be automated?

Partially. The agent can generate candidate dimensions, map artifacts to them, propose measurable proxies, synthesize candidate tests, identify coverage gaps, and decompose recursively. It cannot reliably know which decomposition is correct when several are plausible, detect a missing dimension the operator cares about but has not articulated, distinguish genuine proxies from Goodhart proxies, or validate that the decomposition stays aligned with intent over time.

The pattern is recursive: a Decomposer stage is itself a loop needing its own verification. What verifies a decomposition? Mechanically: coverage of all source units, measurability of every dimension, discrimination on hand-crafted good/bad cases. By operator: alignment with actual intent. The first three are automatable; the fourth is the anchor and cannot be. A practical Decomposer proposes a decomposition, passes it through the mechanical coverage/measurability/discrimination checks, and presents it to the operator for approval and weighting — reducing decomposition work to minutes per goal, not to zero.

### 5.3 Hierarchical decomposition with contract objects

A project decomposes into primary units (a unit may be slightly more than one file). The connection between two units — where one depends on or feeds the other — is itself a first-class object one layer up: a **contract** with assume-guarantee semantics (unit A's outputs satisfy unit B's input assumptions). Decomposition proceeds top-down: define the overall object, decompose one layer, and for each first-layer unit add a further layer only if warranted, up to a discovered limit.

This is not speculative. It corresponds to established compositional verification (assume-guarantee reasoning), contract theory for layered architectures, component-based software engineering with contractually specified interfaces, and to recent agentic skill-library work that validates skills hierarchically and prunes dead branches.

**The failure mode this guards against:** improving each unit in isolation without regard to the units it depends on breaks integration. The named risk in the literature is the *quality ceiling* — without external grounding a self-improving library cannot exceed its own meta-capability and early errors propagate. The defenses: make contract objects first-class with their own measurable verification (catching integration regressions pure leaf-level optimization misses), ground externally at multiple layers, and use Pareto acceptance across layers rather than isolated strict-improvement at each.

### 5.4 Depth limits and cross-cutting concerns

Three layers is typical, four workable, five or more usually means upper layers are abstractions about abstractions with low signal. Progressive decomposition (add a layer only if warranted, to a discovered limit) is the right shape, but the empirical limit is tight.

Hierarchy does not capture cross-cutting concerns — logging, security, observability, error handling, performance cut across the unit graph at every layer. Pure tree decomposition leaves them homeless. They require an **orthogonal decomposition axis** (aspects, traits, or cross-cutting scoring dimensions), built in from the start rather than bolted on.

Verification cost compounds across layers — each layer needs its own scorer, invariants, and acceptance gate; budget cycle time accordingly. Decomposition is not stable under refactor — if the project restructures, the contract layer shifts shape; either accept periodic re-decomposition cost or design the decomposer to detect drift and re-emit.

---

## 6. The verification architecture

### 6.1 The Scorer (tier 1)

Strictly mechanical. Runs each fixture's measurement command against baseline and patched trees, counts failures, and emits promote/reject on strict-greater-than improvement (score delta = baseline failures − patched failures; promote iff delta > 0). Ties reject. Timeouts reject — a timed-out measurement cannot claim improvement. No LLM anywhere. The Scorer also emits an *integrity* signal (observed counts versus the fixture's manifest claims) on a separate channel, so the runner can distinguish "the fixture is broken" from "the verdict is correct on a working fixture." Verdict and integrity are independent: the verdict is always computed from observed counts; integrity reports whether to trust the fixture.

### 6.2 The Verifier (tier 2): the Lanham four-test

The Verifier asks whether the agent's stated reasoning was load-bearing — whether the reasoning actually constrained the patch, or was decoration. The mechanism is reasoning ablation, adapted from the Lanham four-test for chain-of-thought faithfulness. The stated reasoning is treated as the chain of thought; the patch is treated as the answer.

For each reasoning component, four perturbations are applied and a patch is regenerated from each:
- **Early Answering** — truncate before the component.
- **Adding Mistakes** — corrupt the component.
- **Paraphrasing** — restate the component with the same meaning. This is a *control*: for a genuinely load-bearing component, paraphrasing should NOT change the regenerated patch, because meaning is preserved.
- **Filler Tokens** — replace with semantically empty content.

A regenerated patch is compared to the reference patch under AST-normalized equivalence, with a majority vote across N samples to absorb non-determinism. A component is **load-bearing** if ≥2 of 4 perturbations change the patch. The patch-level verdict is *accept* if the load-bearing fraction ≥ threshold, with the threshold swept across {0.50, 0.66, 0.75} during calibration rather than frozen prematurely.

The Verifier emits **per-component** verdicts, not only the patch-level verdict. A Verifier that returns the correct top-level verdict for the wrong per-component reasons is silently broken; per-component output is how that is detected.

The Verifier's LLM use is a *mechanical probe* (does the regenerated patch change), not a quality judgment. This keeps it consistent with the axiom even though it calls a model.

### 6.3 Two orthogonal axes, and Deutsch's criterion at two layers

The Lanham four-test catches *fabricated* reasoning — reasoning that does not constrain the patch. It cannot catch *honest reasoning that constrains the patch to the wrong thing* (memorization, hardcoding, narrow special-casing). These are two distinct failure modes requiring two orthogonal axes, both of which must clear:

1. **Reasoning ablation** (Lanham) — is the reasoning load-bearing for the patch?
2. **Patch generalization** — does the patch generalize, or does honest reasoning justify a patch that only satisfies the specific test?

These are the same criterion — Deutsch's hard-to-vary explanation — applied at two layers. Axis 1 tests reasoning-to-patch. Axis 2 tests explanation-to-spec: an explanation that accounts for the test case but not the specification is easy-to-vary in Deutsch's sense, and therefore a bad explanation, even when it is honest and load-bearing for the patch it produced. Axis 2 is not yet built; it is the primary backlog item (see §8 and §11).

### 6.4 AST-normalized patch equivalence

Two patches are equivalent if, applied to the same baseline, they produce files whose Python ASTs are equal after normalization (whitespace and comments stripped; identifiers preserved, since renaming changes semantics). This is stricter than string match and looser than behavioral equivalence. Behavioral equivalence (re-running tests) is deliberately *not* used here because it confounds the Verifier with the Scorer, and the architecture separates them. If discrimination collapses (all components reading as load-bearing), patch equivalence being too strict — treating cosmetically different but equivalent patches as "changed" — is a prime suspect.

---

## 7. System components

The calibration repo (`arena-calibration`, deployed at the operator's path as `build-arena`).

- **fixtures.py** — Fixture dataclass, manifest loader, layout validation.
- **scorer.py** — Tier-1 mechanical scorer (§6.1).
- **patch_eq.py** — AST-normalized patch equivalence (§6.4).
- **lanham.py** — the four perturbations as pure functions (§6.2).
- **verifier.py** — orchestrates the four-test; per-component output; threshold sweep (§6.2). Public interface `verify(fixture) -> VerifyReport` is stable so the runner does not change when the Verifier body changes.
- **runner.py** — loads fixtures, calls Scorer, short-circuits to skip the Verifier on reject, calls the Verifier on promote, records mismatches and continues (rather than halting on first), emits a single timestamped YAML discrimination matrix, exits 0 iff all fixtures match ground truth and integrity is clean. Accepts injected worker/judge for hermetic testing.
- **llm.py** — the only module importing a provider SDK. `Worker` and `Judge` are typing protocols; real and fake implementations both satisfy them. Provider/model swaps happen here and nowhere else. This seam is load-bearing: it lets the calibration set run hermetically with scripted workers, and isolates provider changes from verifier logic.
- **exercise_verifier.py** — hermetic harness exercise; scripts deterministic worker behavior and asserts the Verifier produces predicted load-bearing patterns; prints `ALL HARNESS PREDICTIONS HOLD` on success. This is the axiom applied to the LLM layer: a scripted worker is a non-agent oracle for what the Verifier should do.

**Worker/Judge split.** The worker regenerates patches under perturbations; the judge produces the discrimination report. For calibration the worker is a canonical reference model, not the original patch author, because fixtures are agent-independent static artifacts (hand-written reasoning, not output from a specific agent). In the real loop the worker should be the agent that produced the patch — a backlog item, and an `llm.py` change, not a verifier change.

---

## 8. Calibration methodology

### 8.1 Verifier-first

The verification machinery is proven to discriminate good from bad on hand-crafted inputs *before* any optimization loop is built. A loop built on a verifier that cannot discriminate produces confident slop — the exact failure this architecture exists to prevent. Build order: Scorer (simplest mechanical check, gates the Verifier path) → Runner (so the Verifier is called from a tested driver) → Verifier (on a known-working harness) → per-component surfacing.

### 8.2 The frozen fixture set

Four hand-crafted fixtures with known-correct verdicts form a frozen ruler. Any Scorer/Verifier implementation is correct iff it reproduces the discrimination matrix.

| Fixture | Description | Scorer should | Verifier should |
|---|---|---|---|
| F1 loadbearing_good | Good patch, load-bearing reasoning | promote | accept |
| F2 fabricated_good | Good patch, fabricated reasoning (real fix, disconnected rationale) | promote | reject |
| F3 bad_passes_tests | Bad patch (hardcoded lookup), honest load-bearing reasoning | promote | reject |
| F4 trivial | No-op/docstring change, no behavioral delta | reject | n/a (Verifier not invoked) |

Construction discipline:
- **Same domain.** All fixtures share the tokenizer/span domain, so the Verifier cannot discriminate on domain features instead of reasoning structure.
- **Positional variation.** Component counts and conclusion-slot positions vary (F1: 4 components, conclusion slot 4; F2: 4, slot 4; F3: 5, slot 3; F4: 2) to break positional heuristics — a Verifier that "ignores the last slot" must not pass by accident.
- **F4 manifest shape.** F4 has zero baseline failures and zero patched failures, exercising the Scorer's no-failure-either-side path and the runner's short-circuit (Verifier never invoked).

### 8.3 F3 is a documented insufficiency, not a defect

F3's patch is bad (hardcodes test inputs, does not generalize) but its reasoning is honest and fully load-bearing. The Lanham four-test alone therefore ACCEPTS F3 — the wrong verdict. This is expected and recorded as a *calibrated negative result*. It proves the Verifier needs the patch-generalization axis (§6.3). Do not attempt to make Lanham reject F3 by tightening the reasoning ablation; that is the wrong fix. F3 is rejected by axis 2, a backlog item.

### 8.4 Hermetic versus live validation

The Verifier is verified in two stages. **Hermetic:** scripted deterministic workers exercise the harness logic with no API calls; success is `ALL HARNESS PREDICTIONS HOLD`. This proves the machinery is correct independent of any model. **Live:** a real worker model is run; this validates whether real model behavior produces reliable load-bearing discrimination. Separating them isolates fault: if a live run diverges from the hermetic prediction, the fault is in model behavior, not the harness.

---

## 9. Decision log

Each entry: the decision, the rationale, and the rejected alternatives.

**D1 — Verifier-first build order.**
*Decision:* Build and calibrate verification before the loop; within that, Scorer → Runner → Verifier.
*Rationale:* Verification soundness gates the entire architecture; a loop on an unsound verifier produces slop. Scorer first because it is mechanical and cheap; Runner second so the Verifier is called from a tested driver; Verifier last on a known harness.
*Rejected:* Scanner/ProjectModel first (clean plumbing but no signal it is the right plumbing until a consumer exists); building the loop first to "see it run" (the canonical path to slop).

**D2 — Verifier mechanism: Lanham four-test, LLM-driven, AST-equivalence on patches.**
*Decision:* Reasoning ablation via four perturbations; compare regenerated patches by AST-normalized equivalence; component load-bearing if ≥2/4 perturbations change the patch.
*Rationale:* Treats reasoning as CoT and patch as answer; AST-equivalence avoids string-match inflating load-bearing scores.
*Rejected:* String match (too loose, inflates load-bearing); behavioral equivalence (too strict here, confounds Verifier with Scorer).

**D3 — Two orthogonal axes, not a deeper hierarchy.**
*Decision:* Reasoning ablation and patch generalization are distinct axes both required to accept, not nested under one "verification" check.
*Rationale:* They catch distinct failure modes (F2 versus F3); both are Deutsch's criterion at different layers.
*Rejected:* A single, more-elaborate Lanham check that tries to catch F3 by tightening — wrong layer, would not generalize.

**D4 — Language: Python.**
*Decision:* Python for the calibration repo and arena stack.
*Rationale:* Prior art (atlas-elenchus, the Lanham driver) is Python; the LinkML toolchain is Python-native; the Anthropic SDK, DSPy, and the rest of the stack are Python.
*Rejected:* TypeScript — adds re-implementation cost and zero capability. (Note: elenchus-validator is TypeScript and will be integrated as a separate service, not rewritten.)

**D5 — Worker model for calibration: canonical reference model, not original author.**
*Decision:* Use a reference worker (cheap class) for perturbation regeneration during calibration.
*Rationale:* Fixtures are agent-independent static artifacts; there is no original author to be consistent with. Cheaper and reproducible.
*Rejected:* Worker = original agent (correct for the real loop, meaningless for hand-written fixtures; deferred to backlog). Worker = same expensive class as the real worker (most cost, least diversification benefit at this stage).

**D6 — Judge/worker model class during diagnosis: do not mix providers.**
*Decision:* Use one model for both worker and judge while diagnosing the discrimination failure.
*Rationale:* Fewest moving parts when isolating a fault. Mixing providers adds variables.
*Rejected:* Mixed-provider judge (a real long-term option per the verification hierarchy, but a confound during diagnosis).

**D7 — Fixture sourcing: mostly designed, one borrowed (deferred).**
*Decision:* Hand-craft F1–F4; defer borrowing a real empirical failure to the 6-fixture extension.
*Rationale:* Borrowing matters most for expanding coverage of unknown failure modes (F5/F6); it is hard to source cleanly under time pressure; designed fixtures suffice to prove discrimination of the obvious cases.
*Rejected:* All hand-crafted forever (risks fitting the verifier to operator imagination); all borrowed (hard to source into reproducible fixtures).

**D8 — Threshold calibration: sweep, freeze nothing yet.**
*Decision:* Report verdicts across {0.50, 0.66, 0.75}; freeze a threshold only after the 6-fixture set runs.
*Rationale:* Avoids fitting a single threshold to four data points.
*Rejected:* Pick 0.66 up front (prior value, but premature); continuous ROC sweep (overkill on four fixtures).

**D9 — Runner output shape: single YAML per run.**
*Decision:* One timestamped discrimination-matrix YAML per run.
*Rationale:* Simple; matches how calibration harnesses ship; the set is frozen at four fixtures, so per-fixture sharding is overkill.
*Rejected:* Per-fixture files plus an aggregate (better for diffing histories at scale; revisit at the 6-fixture milestone if diff signal-to-noise degrades).

**D10 — Remove dead `TIE` enum.**
*Decision:* Remove the unused `ScorerVerdict.TIE`; ties collapse to reject directly.
*Rationale:* The constitution favors clarity; an enum value no caller emits is a trap for future readers.
*Rejected:* Keep it as documentation (a trap).

**D11 — LLM access behind a Worker/Judge protocol with Real + Fake implementations.**
*Decision:* Confine all provider SDK use to `llm.py`; define protocols satisfied by both real and scripted-fake implementations.
*Rationale:* Lets the calibration set run hermetically without the SDK or a network; isolates provider/model changes from verifier logic; is the axiom applied to the LLM layer (scripted worker as non-agent oracle). This is what made it possible to ship and verify the Verifier in a sandbox with no API key.
*Rejected:* Skip live exercise and note the limitation (leaves the harness unproven beyond logic); fake API responses inline (fragile and confusing).

**D12 — Provider switch to xAI Grok (direct), paid, no data sharing.**
*Decision:* After a live run produced no discrimination, switch the worker to `grok-4.1-fast` via xAI's OpenAI-compatible endpoint, called directly (not via OpenRouter), on a paid path without data-sharing enrollment.
*Rationale:* The first live run routed through OpenRouter with a redirected base URL; the served model was unconfirmed and the worker was too noisy to discriminate. A cleaner, far cheaper path with the fewest intermediaries is the right diagnostic move. Paid path keeps prompts private; data-sharing is acceptable for toy fixtures but unnecessary given the small signup credit, and deferring it avoids an on-then-off switch.
*Open tripwire:* Before any real (non-toy) project data touches an external API, third-party retention / data-sharing must be resolved. This is a privacy/security value judgment reserved to the operator, never delegated.
*Rejected:* Continue via OpenRouter (the source of the model-identity ambiguity); enroll in data sharing now (introduces a tripwire to remember later); stay on the expensive direct-Anthropic path (cost-prohibitive for the operator).

**D13 — Documentation structure: three documents, not a README.**
*Decision:* Separate the behavior layer (constitution), the orientation layer (project brief), and the volatile task layer (current-state), with a thin README for run instructions. This specification sits behind all three.
*Rationale:* The three rot at different rates and serve different readers; cramming them into one README produces a document simultaneously too abstract to run from, too volatile to trust, and too long to hold. Once the operator drives the coding agent directly (without a human-language translation layer in chat), the documents must carry the project state that previously lived in conversation; a fresh session starts blank.
*Rejected:* A single detailed README (conflates stable and volatile content; rots as a whole).

---

## 10. Relation to existing work

The conceptual relationships below are confident. Specific paper identifiers come from this session's research and should be confirmed against source before being relied upon in any external document.

**SkillOpt** (operator-supplied arXiv reference, May 2026). Treats a small natural-language skill document as the trainable state of an otherwise-frozen agent; an optimizer LLM converts scored rollouts into bounded edits; a held-out validation split gates acceptance on strict improvement; rejected edits are retained as negative feedback within an epoch; an epoch-wise slow/meta-update writes longer-horizon lessons into a protected region. *Alignment with build arena:* the held-out gate is tier-1 mechanical verification; strict acceptance with ties rejected matches the Scorer; bounded edits match bounded fingerprints; the rejected-edit buffer matches "log failed branches"; the optimizer/target/gate separation is the verification-tier framing made operational (the LLM proposes, the mechanical gate disposes); its own limitations section states the decomposition constraint — the loop is most applicable where automatic verifiers or executable checks exist. *Extends build arena:* a protected slow-update region updated on a slower cadence with the same gate discipline (maps onto a SlowUpdate schema class); hierarchical merging of proposals before application (decomposition discipline applied to the proposer's output); training scaffolding never shipped with the deployed artifact (a separation to maintain). *Divergence:* SkillOpt optimizes a single text document against a fixed benchmark; build arena optimizes a multi-component project where "improved" is multi-dimensional, and so must do the decomposition work SkillOpt assumes is already done. SkillOpt makes visible an alternative architecture — optimize the agent's *strategy* for modifying the project rather than the project directly — recorded as a backlog item.

**Compositional verification and contracts.** Assume-guarantee reasoning, contract theory for layered architectures, component-based software engineering with contractually specified interfaces, and architecture-description languages support hierarchical composition at multiple abstraction levels. These give the contract objects of §5.3 their formal grounding: a contract between units is an assume-guarantee pair, and composition of layer contracts can be made to capture a system-wide specification.

**Hierarchical / self-evolving skill libraries.** Recent agentic work validates skills hierarchically (execution/smoke tests as gates), inserts passing skills as leaves, and prunes or merges failing or low-value ones. The named hazard is the *quality ceiling*: without external grounding a self-evolving library cannot exceed its meta-capability and early errors propagate. This is the formal name for the operator's own concern about units improved in isolation, and it motivates first-class contract verification and multi-layer external grounding.

---

## 11. Known limits and open problems

- **Lanham alone is insufficient (F3).** Honest reasoning can justify a non-generalizing patch. Requires the patch-generalization axis. *Status: open, primary backlog item.*
- **Worker-noise collapses discrimination.** A worker that regenerates a different patch under every perturbation (including paraphrasing controls) yields uniform load-bearing fractions and no discrimination. Observed in the first live run. *Status: under diagnosis via the provider switch.*
- **Model routing can substitute models silently.** A redirected base URL or an alias can serve a different model than requested. Always pin exact model strings and confirm the served model. *Status: mitigated by the direct-xAI switch and a served-model check.*
- **AST-equivalence may be too strict.** If discrimination collapses with a known-discriminating set, patch equivalence treating cosmetic differences as changes is a prime suspect; the fix is to loosen normalization carefully without crossing into behavioral/Scorer territory. *Status: contingent on the next live run.*
- **Decomposition depth and stability.** Practical depth limit is tight (≈3–4 layers); decomposition is not stable under refactor. *Status: design constraint, not yet exercised.*
- **Cross-cutting concerns need an orthogonal axis** not provided by the unit hierarchy. *Status: schema backlog item.*

---

## 12. Backlog (roughly ordered)

1. **Live validation** of the Verifier against a worker that discriminates. Current blocker on declaring calibration done.
2. **Patch-generalization axis** (rejects F3). Candidate: elenchus-validator (operator's TypeScript HTTP service) using `contextGrounding` and `alternativeResistance` subscores only — *not* `specificityMargin` or the overall `recommendation` (marked unreliable by the tool). Both axes must accept. Run as a separate service called from Python; extend its action-type taxonomy from SRE actions to "apply code patch" (propose the schema change before implementing). Integrate only after Lanham is independently sound on the live set. Note: two uncalibrated systems can agree on wrong answers — the fixture set can calibrate both, but track the dependency.
3. **6-fixture extension** — F5 Goodhart (passes both Scorer and Verifier; exposes the joint blind spot; motivates orthogonal measurement) and F6 bad-fails-tests (Scorer negative-path sanity). Borrow one fixture from a real empirical failure rather than designing it.
4. **Schema revision** of the goal model — add a Contract class (assume-guarantee edge objects), a SlowUpdate class (protected longitudinal guidance, epoch cadence, gate-tested), and an orthogonal-axis class for cross-cutting concerns. Reconcile the DivergenceKind enum against the loop spec (single source).
5. **First real Goal instance** — fill the schema against a real project and the seven anchoring questions; stress-test schema shape against reality.
6. **Worker = original-agent** in the real loop (the deferred `llm.py` change).
7. **Strategy-as-trainable-object** — optimize the agent's strategy for modifying the project rather than the project directly; deployed artifact becomes heuristics/decomposition policy, project metrics become the gate; collapses the decomposer-verification recursion into one project-level gate. Text substrate limits expressiveness. Revisit only after a working system exists.

---

## 13. Glossary

- **Assume-guarantee** — a contract form: a component guarantees certain outputs provided its input assumptions hold. Composing such contracts can capture a system-wide property.
- **AST (Abstract Syntax Tree)** — the structural representation of code as a tree, ignoring formatting. Two snippets with the same AST after normalization are structurally identical.
- **Calibration repo** — the frozen fixtures plus Scorer and Verifier, used as a ruler to test whether the verification machinery discriminates correctly. Becomes a permanent regression harness.
- **Contract object** — a first-class object representing the connection/dependency between two units, one layer up in the decomposition.
- **Deutsch's criterion (hard-to-vary)** — a good explanation is hard to vary while still accounting for what it explains. An explanation that fits the test case but not the specification is easy-to-vary, hence poor.
- **Discrimination matrix** — the table of expected verdicts (per fixture, for Scorer and Verifier) that defines ground truth for calibration.
- **Fingerprint** — one unit of improvement work: one hypothesis with one mechanical success criterion.
- **Goodhart** — when a measure becomes a target it ceases to be a good measure; optimizing measured proxies degrades unmeasured dimensions.
- **Hermetic exercise** — running the harness with deterministic scripted workers and no network/API, proving the logic independent of any model.
- **Integrity (Scorer)** — a side signal reporting whether observed measurements match the fixture's manifest claims; distinguishes a broken fixture from a correct verdict.
- **Lanham four-test** — a reasoning-faithfulness probe using four perturbations (Early Answering, Adding Mistakes, Paraphrasing, Filler Tokens) to test whether stated reasoning is load-bearing.
- **Load-bearing** — a reasoning component is load-bearing if perturbing it changes the regenerated patch; otherwise it is decoration.
- **Orthogonal axis** — a verification or decomposition dimension that cuts across the unit hierarchy (e.g., security, logging) rather than nesting within it.
- **Paraphrasing control** — the Lanham perturbation that preserves meaning; for a genuinely load-bearing component it should not change the patch. Frequent changes under paraphrasing indicate a worker brittle to surface form.
- **Promote / accept / reject** — Scorer verdicts are promote/reject (is this an improvement); Verifier verdicts are accept/reject (is the reasoning sound). A change must promote and then be accepted.
- **Short-circuit** — the runner skipping the Verifier when the Scorer rejects (e.g., F4).
- **Slow-update region** — a protected part of a trainable artifact, updated only on a slow (epoch) cadence and still gate-tested.
- **Worker / Judge** — in the Verifier, the worker regenerates patches under perturbations; the judge produces the discrimination report.

---

*This specification is a synthesis of the design conversation. Where it states component behavior, filenames, or fixture details, those should be confirmed against the repository on disk before being relied upon — the constitution's verify-don't-trust-memory rule applies to this document as much as to any other.*
