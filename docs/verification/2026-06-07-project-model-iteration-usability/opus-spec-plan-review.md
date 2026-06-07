I have no source-read or Python LSP available in this environment, so this is a document-level review grounded in the spec, plan, and original review text (which are complete and self-contained for that purpose). Where I flag a code-reality risk, I base it on internal contradictions in the documents themselves.

---

VERDICT: approve_with_required_changes

REQUIRED CHANGES:
- **Resolve the schema version / authority contradiction.** The spec keeps `schemaVersion: project-model/v1` while adding `iterationReadiness` as a **required** field and calls this "backward-compatible." Adding a required field is a breaking change: every previously emitted v1 artifact (the originally accepted FMC-MCP snapshot and any durable v1 artifacts under `docs/verification/`) becomes schema-invalid, which directly conflicts with the non-regression and reproducibility/provenance claims. Pick one and state it: (a) make `iterationReadiness` optional, or (b) bump to a minor (`project-model/v1.1`) with explicit legacy-artifact validation behavior. **Also pin which schema the deterministic gate enforces.** The plan forbids touching root `schema/` but only updates `docs/schemas/project-model-v1.schema.json`. If the gate validates against the frozen root `schema/`, then acceptance item 6.3 ("schema validates generated artifacts") and the new required field are never actually enforced by the gate — the new contract becomes cosmetic. This must be resolved before Phase 3.
- **Specify the evidence/provenance model for inferred runtime contracts and invariants.** `runtimeContracts` (`constructs`, `injects`, `registers_resource/tool`, `delegates_to`) and read-only invariants require call/registration-level facts. The only parser change in the plan is combined-import resolution; Tree-sitter/SCIP/CodeQL/call-graph are explicitly out of scope, and the original review notes the graph is import-only (it even mis-resolved `server -> tools`). As written these records are either unfillable from graph edges or risk fabrication. State explicitly that they are backed by **source-span provenance (file/line text evidence)** under rule 5.1, and confirm that text-span provenance satisfies the anti-fabrication gate and is exempt from the "missing edge coverage" check (since they are not import edges). Without this, the highest-value sections (gaps 3 and 2) are the most likely to fail the gate or be hand-waved.
- **Give "non-tautological responsibility" and "open question" generation an objective, testable predicate.** The core original complaint was tautological summaries; the plan only commits to "summaries based on detected tags/symbols," which can still be a templated tag list. Phase 2's red test "emits non-tautological responsibilities" has no deterministic pass condition, so success effectively defers to the non-deterministic Phase 6 three-model vote — contrary to the gate-first philosophy. Add a concrete rule (e.g., summary must not be reconstructible from the module name alone and must cite ≥N source symbols; open questions emitted only when a named source signal is absent), so the red/green tests are real.

NON-BLOCKING SUGGESTIONS:
- Make `priorityRank` tie-breaking and `openQuestions` ordering deterministic (stable sort key) so artifacts are byte-stable across runs for a fixed git state.
- Surface the two FMC-MCP smells the original review raised that the spec drops: the `FMCClient.test_connection` naming smell and the server→tools indirection — capture them as `priorityBacklog`/`openQuestions` items (delegation is captured via `delegates_to`, but the "is this indirection intentional" question and the naming smell are not).
- Optionally add churn/git-history to risk metadata (original review item 5) when history is available; currently only LOC/tags/flags are used.
- Add a v0→v1 round-trip non-regression test asserting prior accepted artifacts still validate under whatever versioning decision is made (ties off the first required change).

COVERAGE CHECK:
1. semantic responsibilities — addressed (componentProfiles 4.1; needs the testable anti-tautology predicate above to be verifiable).
2. product invariants — addressed (productInvariants 4.4; fail-safe `gap`/`enforcement` handling is correct).
3. runtime/data-flow contracts — addressed at the contract level (runtimeContracts 4.2), contingent on the evidence-model required change.
4. external surfaces — addressed (externalSurfaces 4.3 covers resources, tools, console script, env vars, endpoint families, dependencies).
5. risk/priority metadata — addressed (riskLevel/priorityRank/whyPriority 4.1 + priorityBacklog 4.6; client-ahead-of-entrypoint is an explicit acceptance target).
6. configured quality checks — addressed (qualityGates 4.5 detects ruff/mypy; allowlist guard preserved).
7. combined import resolution — addressed (scope item 5, plan 3.1, with a dedicated red test).

IMPLEMENTATION RISKS:
- Evidence ceiling: import-level graph + regex text heuristics may be too thin to deterministically and credibly back `injects`/`delegates_to`/read-only distinctions; biggest risk of either gate rejection (fabrication) or shallow output that fails the three-model bar.
- Success criterion is partly non-deterministic: Phase 6 (Grok/Opus/Hermes agreement) is a hard exit gate but cannot be guaranteed by the spec; if the anti-tautology predicate is weak, this becomes the only real arbiter and may loop.
- Schema enforcement gap: if the gate reads frozen root `schema/`, the enriched contract ships unvalidated and silently drifts.
- Backward-compat breakage of existing v1 artifacts from a newly-required field (reproducibility/provenance regression).
- Determinism leaks: text-pattern heuristics (rate limits "120/min", "10 connections", read-only POST vs GET) are brittle across formatting/refactors; mitigated by the fail-safe-to-`gap` rule but still a stability risk for the snapshot hash.
- Overfitting: acceptance targets are stated in FMC-MCP-specific terms (specific URIs, client responsibilities); guard against heuristics that only fire on this repo (the fixture-repo tests in Phase 2 partially mitigate this).
