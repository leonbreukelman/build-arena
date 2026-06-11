I attempted to independently verify the report's grounding claims against the cited source files (`arena/decomposer.py`, `arena/project_snapshot.py`, `arena/project_graph.py`, `arena/project_model_gate.py`), but no Python LSP server is configured and this toolset has no file-read/search access. My assessment therefore rests on the report's internal specificity and self-consistency, not direct inspection of those files. I flag this honestly below.

---

## 1. Verdict

**SIGN_OFF** — conditional on the required constraints in section 4 being carried verbatim into the functional spec.

## 2. Blocking issues

None that block progression to a *no-code functional spec*. The report preserves the meta-decomposer goal, is concretely grounded, and supplies enough of a conceptual data model (workspace / root / component / contract / observable-check / gap) and anti-overfitting boundary to write a spec. The unresolved items below are properly spec-stage decisions, not research-stage blockers.

Two items are **near-blocking** and must not be allowed to slip past the functional spec without an explicit decision:

- **Clustering determinism is unspecified.** The design leans on community detection / Bunch/ACDC-style recovery, which are commonly non-deterministic. Yet the model is run-to-run gated and compared (acceptance criterion 4 compares "versus the first run"). Non-deterministic clustering would make the gate and the CMMC-improvement comparison unreliable. The report mandates deterministic *edges* and deterministic *check serialization* but never mandates deterministic/stable *clustering*. This must be pinned down.
- **Nested / workspace root resolution is undefined.** This is the exact mechanism behind the CMMC failure (root-level check instead of `app/backend`, `app/frontend`). The report introduces "nearest-root scope" and "workspaces can declare child roots" but gives no rule for resolving a manifest at the workspace root that *coexists* with nested manifests (parent-vs-child ownership, when a parent root is a container vs. an executable root). Without a stated resolution rule, the spec cannot deterministically reproduce the desired CMMC outcome.

## 3. Non-blocking improvements

- **Generalization evidence is too thin to be left as "stretch."** The entire thesis is "generalizes to unrelated held-out projects," yet validation is effectively one synthetic fixture plus one held-out repo (CMMC), with the additional held-out corpus and identity-blind/isomorphism tests deferred to stretch. At least one identity-blind/isomorphism test and one additional held-out repo should be required *before the implementation sign-off gate* (criterion 6's final review), even if not before the spec.
- **Acceptance criterion 4 uses a soft, relative bar** ("more/fewer"). A trivial delta could satisfy it. Pair the relative metrics with a minimum absolute target (e.g., a floor on primary-source-node ownership) and an explicit statement that any improvement must come from generic paths (already implied by criterion 5).
- **Self-decomposition tension is unaddressed.** Anti-overfitting correctly forbids a "Build Arena calibration" branch, but acceptance criterion 1 requires Build Arena's own verification to stay green. The report should state explicitly that Build Arena's self-model is henceforth produced by the generic path, so removing the calibration branch is a behavioral change to validate, not a regression to suppress.
- **The cited independent Opus memo is corroboration, not independent verification.** Using a prior Opus memo to support an Opus sign-off is mildly circular; my verdict rests on the report's own merits.
- **ObservableCheck schema migration** (adding execution directory) touches the snapshot, gate, and consumers; the spec should note back-compat/migration of existing snapshots.

## 4. Required constraints to carry into the functional spec

1. **No project identity in logic.** No branching on repo names or target-specific directory names; no fixed component taxonomies, fixed contract topologies, or fixed root-level check commands; no CMMC/FMC/Build-Arena calibration branch. Allowed: generic manifest/toolchain tables, path/graph heuristics, safety allowlists, generated/vendor exclusions.
2. **Roots from manifests, not repo identity.** A project root requires manifest/build evidence with source/build context; auxiliary files (lockfiles, test/type/Vite configs) reinforce but do not create roots. Specify the nested/workspace resolution rule (parent container vs. executable child; nearest-root ownership).
3. **Checks carry execution directory.** ObservableCheck is {purpose, command/task, execution directory, safety metadata, provenance, covered components/contracts, proof-or-gap}. Never emit a runnable check at a directory lacking evidence the command belongs there. Add a check-executability gate keyed on cwd.
4. **Contracts derive from cross-component edges.** Deterministic import/reference/test edges support contracts directly; real-but-unprovable relationships (e.g., frontend↔backend HTTP) become contracts with explicit, typed, evidence-backed verification gaps.
5. **Coverage repair without padding.** Every primary source node is owned by a component or assigned to a specific, scoped, typed gap with a proposed closure check. Blanket/"assign all unhandled to a vague gap" fails quality review.
6. **Determinism/stability.** Clustering and serialization must be deterministic and stable across runs for identical inputs, so gating and run-to-run comparison are meaningful.
7. **CMMC is a held-out signal, not a target.** The next CMMC run measures generalization; no special-casing to make it pass.
8. **Safety boundary for discovered tasks.** Declared/discovered commands are untrusted; execution is constrained by a generic safety allowlist and sandbox boundary, defined generically.

## 5. Short rationale

The report does the one thing this review most needs: it reframes CMMC as a held-out generalization-failure signal and explicitly forbids per-project customization, with a concrete allowed/forbidden anti-overfitting list. It is grounded — it names specific code paths (the literal-file arena calibration branch, the broad-bucket generic fallback, ObservableCheck-as-string, the cwd-blind gate) and ties the CMMC failure mechanically to them, which is specific and falsifiable. It supplies a coherent data model and acceptance criteria, which is sufficient scaffolding for a no-code functional spec. The remaining weaknesses — undefined clustering determinism, unspecified nested-root resolution, and a thin generalization-evidence bar — are exactly the decisions a functional spec exists to make, so they are constraints to carry forward rather than research blockers. I sign off on that condition, with the caveat that I could not directly inspect the cited files and relied on the report's internal specificity.
