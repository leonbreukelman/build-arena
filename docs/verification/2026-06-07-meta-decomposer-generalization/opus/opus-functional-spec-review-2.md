## 1. Verdict

**SIGN_OFF**

## 2. B1/B2/B3 resolution assessment

**B1 — Executability-proof vs. safety/no-network: RESOLVED.**
The spec now splits the previously conflated concept into two independent axes (§4.7, §8.4): a *safety status* (safe-by-default / unsafe / requires-network / requires-paid-API / destructive / unknown) and an *execution status* (declared-only / statically-validated / execution-proven / gapped). The contradiction is removed because:
- `execution-proven` is defined as "run successfully in the recorded execution directory under the safe boundary, **or** an explicit local proof artifact." A network/paid-API command cannot be run under the no-network/no-paid-API boundary, so it can never become execution-proven *by the decomposer itself* — it falls to `gapped`, or relies on an operator-supplied proof artifact (§8.4, gate 11.2.4).
- Acceptance is gated on `safe-by-default AND execution-proven` (or an explicitly attached operator proof artifact), and unsafe checks are explicitly demoted to declared candidates with gaps (§8.3).
This is internally consistent with principles 9 and 10 and the no-live-paid-API gate.

**B2 — Indirect inter-root contract discovery: RESOLVED.**
§7.3 replaces the prior open-ended language with a *closed* allow-list of generic, typed evidence (shared schema/protocol artifact, provenance-linked generated client/server artifact, multi-root CI/task/workspace declaration, generic-parser-identified protocol/address config tied to a root-owned client/server surface, multi-root test-fixture provenance) and an explicit forbidden list (domain keywords, route-name lists, repo-specific assumptions). The fallback rule — weak/suggestive evidence ⇒ verification gap, not a contract — directly counters the overfitting risk. This is consistent with §3's anti-overfitting prohibitions.

**B3 — Primary source/test/config coverage classification: RESOLVED.**
§9.0 introduces an explicit taxonomy (primary source / primary test / primary config-build / documentation / generated-protected-vendor-cache) with per-class coverage obligations, and §9.1–9.3 bind the gates to that taxonomy. The classification is generic and definitional rather than project-specific.

## 3. Remaining blocking issues

**None.** No issue rises to a level that prevents producing an implementation plan.

Non-blocking items to carry into planning (not blockers):
- **Dual "proof artifact" notion.** `execution-proven` already admits "an explicit local proof artifact" (§8.4), while acceptance separately allows "a separate operator-supplied proof artifact" (§8.4, §11.2.4). These two artifact concepts overlap and should be unified or clearly distinguished so the acceptance path is unambiguous.
- **"Safe boundary" is referenced but not defined** at the functional level (§8.4). It is implied by principles 9–10 and the no-network/no-paid-API gates; the plan should state it explicitly as the execution sandbox definition.
- **§7.3 config evidence ("generic protocol/address/reference form")** is the softest of the typed-evidence clauses; the plan should pin down what generic parsers qualify, to keep it from drifting toward heuristic guessing.

## 4. Planning constraints

1. Define one canonical proof-artifact concept and the exact acceptance precedence: `safe-by-default ∧ (execution-proven ∨ operator-proof-artifact)`. Eliminate the redundancy between §8.4's two artifact phrasings.
2. Specify the execution "safe boundary" concretely (no network, no paid API, no destructive FS/VCS, command-subset allowlist) as the precondition for `execution-proven`.
3. Enumerate the generic config parsers permitted under §7.3 and assert they carry no domain keyword tables, satisfying the §11.2.6 no-identity-branch lint.
4. Keep CMMC strictly held-out: validation logic (synthetic nested multi-root fixture) drives development; CMMC is measured only via §13 metrics and the §14 acceptance rule.
5. Honor the determinism requirements (§5.4, §6.4) as testable invariants — directory-rename isomorphism (§6.6) and stable tie-breaking are first-class plan deliverables, not afterthoughts.
6. The §13 improvement floor (notably: no incorrect root-level `uv run pytest -q` as sole CMMC check; backend/frontend execution-directory semantics) must be encoded as concrete before/after assertions, with any regression explained by generic behavior.

## 5. Short rationale

All three prior blockers are addressed at the right level: B1 by decoupling safety from execution proof and routing network/paid-API commands to gaps; B2 by a closed typed-evidence allow-list with a gap-fallback; B3 by an explicit, generic node-classification taxonomy bound to the coverage gates. The document remains purely functional — it specifies records, statuses, evidence types, determinism requirements, and gates without prescribing code. The residual items (artifact unification, safe-boundary definition, config-parser enumeration) are precision refinements appropriately resolved during implementation planning rather than gaps in functional intent, so the spec is precise enough to proceed.
