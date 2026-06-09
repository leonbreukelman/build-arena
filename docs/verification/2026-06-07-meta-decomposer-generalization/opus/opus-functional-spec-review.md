I reviewed the functional spec against the five criteria. I did not use code-intelligence tooling here because this is a prose/specification review and the only available tool (LSP) operates on code symbols, not the markdown artifacts; my assessment is based on internal consistency, completeness, and alignment with the stated anti-overfitting and research constraints. One caveat: I could not independently open the referenced research report (`docs/research/2026-06-07-...md`), so the "carry-forward" check below is against what the spec itself enumerates, not a line-by-line diff with the research sign-off.

## 1. Verdict
NEEDS_REVISION

## 2. Blocking issues

**B1 — Executability-proof rule is internally contradictory and collides with the no-network/no-paid-API constraint.**
Section 8.4 states a hard rule: an unproven candidate "becomes a gap or a non-acceptance observation, not an accepted check," and defines "proven" as "run or otherwise validated in its execution directory." But §11.2.4 makes executability evidence *optional*, and §14's acceptance list never requires proof. Worse, "proven by running" tension with principle 9 and §8.3 (no network, no paid API, safe subset only): in a sandboxed run, many legitimate checks can never be executed, so under §8.4 they must all collapse to gaps. The spec must resolve (a) whether executability proof is required for acceptance or optional, and (b) what "otherwise validated" means when execution is forbidden. Without this, the plan cannot define what passes the acceptance/safety gates.

**B2 — Indirect inter-root contract discovery is underspecified and reopens the drift it forbids.**
Section 7.3 permits recording inter-root contracts from "client configuration, shared schema files, route names, generated clients, protocol files, or CI integration" when no static edge exists. Detecting "route names" or "shared schema" relationships without graph edges almost requires domain/keyword matching — which §3 explicitly bans ("Use target-domain keyword lists…"). The spec allows the *output* but never constrains the *discovery mechanism* to be generic and deterministic. This is a direct conflict between §7.3 and the anti-overfitting principles and is exactly the kind of CMMC-shaped temptation the spec is meant to prevent. Define a generic, evidence-typed, deterministic basis for indirect contracts (or downgrade indirect-only signals to verification gaps rather than contracts).

**B3 — Coverage gates depend on undefined terms ("primary source node"; test-file ownership).**
Sections 9.1/9.2 and the §13 metrics hinge on "primary source node," but the term is never defined relative to test, config, generated, vendor, and documentation nodes. Section 6.3 says tests are "grouped or linked," leaving it ambiguous whether a test file is a primary source node that must be *owned* (§9.1) or merely *linked*. Because these feed hard gates (inventory coverage, edge coverage), the ambiguity makes the gate behavior non-deterministic to implement. Provide a precise functional classification of which node classes are subject to ownership vs. linkage vs. exclusion.

## 3. Non-blocking improvements

- **Define "partial root."** §5.3.5 introduces "synthetic or partial root," but §4 defines only synthetic roots. Either add a definition or fold "partial" into the synthetic-root concept.
- **Specify component-id derivation.** §4.5 requires a "stable id" and principle 8 requires deterministic serialization, but §6 specifies deterministic *clustering* without a stated id-derivation rule (unlike §5.4 for roots). State the functional id scheme for components and contracts.
- **Define "cross-cutting concerns."** §11.1 retains a cross-cutting-concerns gate, but the conceptual model (§4) never represents cross-cutting concerns, and §4.5 forbids components crossing roots. Clarify how this concept is modeled so the gate is testable.
- **Add a CMMC improvement bar.** §13/§14.4 define a comparison surface but no minimum threshold; "improves" is left to Opus judgment. Consider stating which metrics must strictly improve vs. may regress, even if final acceptance stays qualitative.
- **Container-vs-child orchestration checks.** §5.3.4 allows parent orchestration tasks "if supported by root-local evidence"; cross-reference this explicitly with §8.5's mapping rule to prevent a workspace check from claiming child coverage.

## 4. Planning constraints

The implementation plan, once the blockers are fixed, must hold these invariants from this spec:
1. **Single pipeline, no identity branches** (§2.1–2.2, §3), enforced by the no-identity-branch lint (§11.2.5) and warm-up/held-out separation (§12).
2. **CMMC remains held-out** — no CMMC/FMC/calibration-specific logic; improvement must be attributable to generic behavior (§2, §12.2, §14).
3. **Determinism end-to-end** — root discovery (§5.4), clustering and tie-breaking (§6.4), and output serialization (principle 8); any community-detection must be wrapped for stable ordering.
4. **Execution-directory is mandatory** for every observable check and must be evidence-backed (§4.7, §8.2, §11.2.1–2).
5. **Coverage-or-specific-gap discipline** — every primary node owned/gapped, every cross-component edge contract-covered/gapped; blanket gaps fail (§9, §4.8).
6. **All existing gates remain binding and additive only** (§2.10, §11.1) — no relaxation of anti-fabrication, provenance, no-live-paid-API, protected/generated surface, held-out probe, near-neighbor, or verification-gap-validity gates.
7. **Backward-compatible schema migration** — legacy snapshots readable; new snapshots must carry execution-directory semantics; v0 projection preserves/explains it (§10).
8. **Required validation set is mandatory** — existing tests, synthetic nested multi-root fixture, CMMC rerun comparison, Opus review, plus the durable artifact set in §14.6.

## 5. Short rationale
The spec is largely strong: it stays functional rather than code-level, it carries the existing gate/provenance/anti-fabrication regime forward, and §3/§11.2.5/§12 give a credible anti-drift backbone. It does not yet warrant sign-off because three items would force the implementation plan to guess: the executability-proof rule contradicts itself and the safety constraints (B1), indirect inter-root contract discovery is permitted without a generic deterministic mechanism and thus reopens overfitting risk (B2), and the coverage gates rest on undefined node-class terms (B3). Each is a precision/consistency defect at a load-bearing point, so they should be resolved before planning rather than deferred into implementation.
