# Opus Review — AI-first Project Decomposer Spec

Reviewer: Claude Opus via Claude Code
Model usage: claude-opus-4-8
Mode: read-only architecture review
Spec: `docs/specs/2026-06-04-ai-first-project-decomposer-spec.md`
Claude Code subtype: `success`
Reported cost: 1.5919815 USD-equivalent
Session: `4db637a8-098c-45dd-8387-e656caf5f4d5`

I've now grounded the review in the spec, the research it derives from, the Project Model v0 contract, the actual decomposer/gate code, the tests, and the real repository layout. One grounding fact shaped several findings: the **real** `build-arena` repo does *not* match `_looks_like_arena_calibration()` (it has top-level `scorer/`, `verifier/`, `schema/`, plus `dashboard/` and a nested `arena-calibration/`; the special-case keys on `arena/scorer.py` etc.), so on Build Arena itself the current decomposer runs the **generic path classifier** — the exact baseline the spec is reacting against.

Here is the adversarial architecture review.

---

# Adversarial Architecture Review — AI-first Project Decomposer Spec

**Spec under review:** `docs/specs/2026-06-04-ai-first-project-decomposer-spec.md`
**Reviewer/model:** Claude Opus (`claude-opus-4-8`), acting as independent read-only adversarial architecture reviewer. No files modified; no tests run; review based on reading the spec, source docs, current implementation, tests, and `git ls-files`/filesystem layout.

**Verdict: REQUEST_CHANGES**

The spec is a genuine, well-structured advance over Project Model v0 and correctly diagnoses the path-classifier problem. But it contains a load-bearing internal contradiction (the deterministic gate is assigned semantic judgments it provably cannot make without an LLM), it silently *dropped* two anti-F3 mechanisms that the source research and `project-model-v0.md` treat as primary (leaf-level provenance derivation method; near-neighbor alternatives + explicit goal/non-goals), and its strongest *enforced* property is still v0's "every file owned exactly once." As written, a richer deterministic classifier with fabricated-but-resolvable provenance would pass every automated acceptance gate. These are fixable at the spec level, hence REQUEST_CHANGES rather than a softer accept.

---

## blocking_findings

### B1 — The deterministic gate is assigned semantic judgments it cannot make deterministically (central)
- **Severity:** blocker
- **Evidence:** §3.2(6) "GateReport is the only source of pass/fail authority"; §3.6 / §9.3 gate "fails on … vague/misc/general components", "ambiguous leaves represented as success", "file-bucket components fail", "Components must describe responsibilities, inputs/outputs, and boundaries"; §13 "Gate rejects bare path buckets." Compare to the only mechanism that exists today: `arena/project_model_v0.py:50-73` (`_VAGUE_IDS`, `_VAGUE_PHRASES`, `_VAGUE_SURFACES`) — a lexical denylist.
- **Why it matters:** "Is this a responsibility-bearing component or a renamed path bucket?" and "is this leaf aimed at the right target?" are semantic judgments. A deterministic, no-LLM gate (§9 preamble, §6.6 "Must not trust LLM prose") can only do lexical/structural checks. A component named `Calibration Fixture Integrity Subsystem`, owning real file nodes, with invented-but-plausible responsibilities and a real `uv run pytest -q` check, passes every predicate the spec actually defines. The spec never specifies the deterministic predicate that separates a bucket from a component — so its most important gate is unenforceable. This is the same weakness the spec accuses v0 of, relocated upward.
- **Recommended spec patch:** Split authority honestly. (a) Keep the deterministic gate for what it *can* decide: coverage, reference integrity, provenance resolvability, hash/freshness, lexical vague-name denylist, protected-surface tagging, no-live-API flags. (b) Add an explicit **non-deterministic review gate** (skeptic + held-out probes) to the authority model in §3.2, and state plainly that wrong-target/file-bucket detection is *probe/review-enforced, not gate-enforced*. (c) For any criterion you keep in the deterministic gate, define the concrete predicate (e.g., "file-bucket" = component whose `owned_node_ids` are ≥90% sibling files under one directory AND whose responsibilities contain no symbol/contract reference resolvable in the graph). Do not leave "rejects bare path buckets" undefined.

### B2 — Provenance lost its derivation-method and confidence fields — the anti-fabrication anchor is broken
- **Severity:** blocker
- **Evidence:** §4.4 `ProvenanceRef` fields: `source_type`, `path`, `line/byte`, `git_oid`, `content_hash` ("when feasible"), `claim`, `excerpt`. The source research explicitly required `derivedBy` (`git`/`tree-sitter`/`python-ast`/`grimp`/`doc-parser`/`llm`/`operator`) and `confidence` as the "anti-fabrication anchor" (`docs/research/…pipeline.md:164-178`), and the research's own Opus review made "make Provenance a mandatory leaf-level field" a precondition (`…pipeline.md:1015-1018`). The spec dropped `derived_by` and `confidence`.
- **Why it matters:** Without `derived_by`, a deterministic gate cannot distinguish a ProvenanceRef produced by a parser from one asserted by the LLM. Since `source_type` already allows `model_output` and `doc_section`, an LLM can "ground" a fabricated component on an encyclopedia page (itself LLM prose) and the gate cannot tell. The invariant "model-generated prose cannot be provenance for code facts unless it itself cites underlying source evidence" (§4.4) is unenforceable without a derivation field and a requirement that provenance chains resolve transitively to a `file`/`git`/`command_output` leaf.
- **Recommended spec patch:** Add mandatory `derived_by` (enum incl. `git`, `python_ast`, `tree_sitter`, `import_graph`, `doc_parser`, `llm`, `operator`) and `confidence` to `ProvenanceRef`. Make `content_hash` **mandatory** for text-backed refs (not "when feasible"). Add a gate rule: every accepted Component/Contract/Concern claim must have at least one provenance leaf with `derived_by ∈ {deterministic set}` resolving to a real file span; `model_output`/`doc_section` may never be the *sole* provenance for a code fact.

### B3 — Near-neighbor alternatives and explicit project goal/non-goals were dropped — the primary F3 discriminator is gone
- **Severity:** blocker
- **Evidence:** §4 data contracts define Component, Contract, CrossCuttingConcern, ObservableCheck, HeldOutProbe, VerificationGap, Snapshot, GateReport — **no** near-neighbor-alternative type and **no** top-level `goal`/`non_goals` object on `ProjectModelSnapshot` (§4.12). Contrast `docs/project-model-v0.md:226-237` ("Near-neighbors are what make wrong-target F3 visible") and the research `…pipeline.md:622-636` which keeps `NearNeighborAlternative[]` as a required decomposition output. The current code even emits them (`arena/decomposer.py:353-366`).
- **Why it matters:** F3 = coherent, well-grounded reasoning aimed at the *wrong* target. A fully-provenanced, internally-consistent decomposition can still be F3. The mechanism `project-model-v0.md` relies on to make wrong-target visible is forcing the model to state the plausible nearby alternative and why it isn't primary, plus a concrete project goal/non-goals to test "right target" against. The spec removed both. With them gone, nothing in the model represents "what this decomposition is *not* about," so the skeptic/probes have no anchor to attack wrong-targetness.
- **Recommended spec patch:** Add a top-level `goal` + `non_goals` block to `ProjectModelSnapshot` (carried from §5.1 inputs), and reintroduce a `NearNeighborAlternative` contract (id, description, why_not_primary, distinguishing_evidence/provenance) required for every high-risk component and contract. Add a gate rule: high-risk leaves without a near-neighbor alternative fail or become a `VerificationGap`.

### B4 — Held-out probes are asserted but never validated for discriminative power; the F3 thesis is therefore unproven
- **Severity:** blocker
- **Evidence:** §4.10 / §7 / §9.6 require probe *presence* and *isolation* and record builder metadata, but no stage ever checks that a probe *fires* on a wrong decomposition. The research had the missing half: "golden decompositions," "good-bad cases," and "validate that held-out probes can catch wrong-target decompositions" (`…pipeline.md:776-792, 894-916`). The spec dropped golden decompositions and planted negatives entirely.
- **Why it matters:** A probe that never discriminates is theater. "Held-out probes detect wrong-target decompositions" (Purpose §1.7) is an empirical claim the spec never tests. Presence + isolation gates can be satisfied by vacuous probes, giving false assurance — itself a meta-F3 (a coherent verification ritual aimed at the wrong target).
- **Recommended spec patch:** Require each held-out probe to be validated against ≥1 *planted negative* (a deliberately wrong-target / file-bucket / oracle-leak decomposition decoy) and record the firing result. Add a deterministic gate (`held_out_probe_discrimination`): a high-risk probe that does not fire on its paired decoy is rejected or downgraded to a gap. Reintroduce a small golden/decoy corpus as an acceptance artifact (see B6, axis 10).

### B5 — Internal contradiction: gate is "sole pass/fail authority" yet acceptance requires a paid Opus review, breaking the no-live-API principle
- **Severity:** blocker
- **Evidence:** §3.2(6) "GateReport is the only source of pass/fail authority for snapshot usability"; §6.6 gate "Final pass/fail authority." But §12(12) acceptance criterion: "Opus pilot review finds no unresolved critical blockers," and §11.2(6)/§13 lean on Opus review. The whole no-goal/non-goal §1, §9.9, §13 insist acceptance must not require live paid APIs (`Non-goal`: "Require live paid API calls in acceptance tests").
- **Why it matters:** Three claims cannot all be true: (a) the gate is sole authority, (b) Opus review is an acceptance criterion, (c) acceptance requires no paid API. As written, snapshot acceptance depends on a non-reproducible paid-model judgment, contradicting the spec's own thesis and making criterion #12 unverifiable in CI.
- **Recommended spec patch:** Make the deterministic gate the sole *blocking* authority; reclassify Opus pilot review as a **non-gating advisory** artifact (clearly outside acceptance), exactly as the research framed model review as recorded-but-not-acceptance (`…pipeline.md:949, 525`). Update §12 to remove #12 as a pass/fail criterion (or rephrase as "advisory review recorded").

### B6 — Mandatory cross-cutting concerns force overfit/fabrication on non-Build-Arena repos
- **Severity:** blocker (it is a gate that *induces* fabrication, undermining the generality goal)
- **Evidence:** §4.8 concern invariant "Required concerns for Build Arena-class repos include … F3 resistance"; §9.5 gate "Required concerns exist for determinism, provenance, anti-fabrication, protected surfaces, no-live-paid-API, generated/oracle integrity, and F3 resistance"; §12(3) demands "one additional held-out repo without obvious Build Arena overfit." The enum sets also leak Build-Arena worldview: §4.6 `kind` incl. `verifier`, `scorer`, `governance_process`; §4.8 `category` incl. `F3_resistance`, `provider_boundary`, `local_first`; §4.10 `probe_type` incl. `F3_generalization`, `oracle_leak`, `generated_surface_leak`.
- **Why it matters:** A held-out repo with no oracle surfaces and no provider boundary will be *forced* by the gate to emit an "oracle integrity" / "F3 resistance" concern to pass — i.e., the gate rewards inventing concerns that don't apply. That is fabrication, the exact failure §13 "LLM architecture fan fiction" warns against, and it directly defeats the generality pilots (§11/§12).
- **Recommended spec patch:** Make required concerns **conditional on detected surfaces** (e.g., require `oracle_integrity` only if oracle surfaces are tagged; require `provider_boundary` only if external-provider edges exist). Keep only universally-applicable required concerns (determinism, provenance, anti-fabrication, no-live-API) unconditional. Mark Build-Arena-specific enum members as an extensible/optional vocabulary, not a closed required set, so a general repo isn't pushed into them.

---

## nonblocking_findings

- **N1 — "Deterministically audited" graph is an undefined loophole.** §3.2(2)/§3.3 allow the ProjectGraph to be "deterministic *or deterministically audited*." Undefined; could legitimize an LLM-built graph with a thin audit. Define "audited" or drop it. (architecture correctness)
- **N2 — `owned_paths` re-introduces path-bucket thinking as first-class.** §4.6 keeps `owned_paths` "for compatibility/readability." Combined with B1, the enforced backbone remains ownership accounting. Mark it explicitly derived/non-authoritative and ensure no gate keys off it. (v0 leakage)
- **N3 — no-live-API gate trusts self-declared booleans.** §4.9 `requires_paid_api`/`requires_network` and §9.9 — a check can simply declare `false`; the deterministic gate cannot verify without executing. Add an acceptance-command allowlist or a network-isolated dry-run, or state that the flag is advisory. (weak gate)
- **N4 — Spec does not retire the existing hard-coded arena-calibration special case.** `arena/decomposer.py:1104-1333` (`_looks_like_arena_calibration`, `_arena_*`) is the canonical overfit example the research flagged, yet §2/§14 say only "keep scanner strengths." Explicitly quarantine or remove it; otherwise it survives as latent overfit beside the new pipeline. (overfit / v0 leakage)
- **N5 — Encyclopedia (LLM prose) feeds the decomposer; doc_section is a valid provenance source_type.** §3.4/§5.3(2-3) + §4.4. The "wiki becomes truth" mitigation (§13) depends on transitive provenance resolution that the gate can't do without B2's derivation field. Couple this fix to B2. (codegraph/wiki/provenance)
- **N6 — Cross-snapshot probe leakage within the same repo is not gated.** §7.5-7.7 only check same-snapshot prompt leakage; committed `.arena/project-model-snapshots/<id>/held-out-probes.json` from snapshot N could enter snapshot N+1's inventory/decomposer inputs. (held-out probe leakage; see dedicated section)
- **N7 — Probe builder is not required to be an independent model from the decomposer.** §4.10/§6.5 record `builder_model_id` but never require it ≠ the decomposer model/family. Shared model ⇒ shared blind spots ⇒ probes can't catch the decomposer's systematic errors. (held-out probe leakage / F3)
- **N8 — Misrepresented baseline.** §0/§2/§11.1 imply the current decomposer's "arena-calibration detector" is the Build Arena baseline, but on the real repo that detector does not fire (top-level `scorer/`, `verifier/`, `schema/`; nested `arena-calibration/`; `dashboard/`), so the actual baseline is the generic bucket classifier. Minor accuracy fix; strengthens, not weakens, the "v0 insufficient" case. (architecture correctness)
- **N9 — `git_oid` HEAD anchor on a dirty tree is misleading.** §4.4 pins `git_oid` to HEAD while §4.12 carries a `dirty_state_fingerprint`. For dirty spans the HEAD oid doesn't match disk; require provenance on dirty files to anchor to the disk content_hash, not HEAD. (provenance)

---

## missing_best_practices

- **M1 — No def→reference / call-graph resolution in the first slice.** §3.3/§15 defer SCIP/LSIF/CodeQL/Sourcegraph/ast-grep to "enrichments," leaving only Python AST + imports + markdown/config. Yet edge kinds (`calls`, `references`, `depends_on`, `data_flow`-adjacent) are in §4.3 — so the most architecturally important edges would be **LLM-inferred** (confidence medium/low), reintroducing fabrication exactly where it hurts. Best practice: ground call/reference edges deterministically (grimp for imports is in the research; add a concrete plan), and forbid accepting high-impact edges that are LLM-only without a gap.
- **M2 — No stable symbol identity (SCIP-style monikers).** Provenance relies on path+line/byte+hash, which the spec itself says goes stale (§4.4 invariants). Best-in-class indexes use stable symbol IDs as anchors. Add a symbol-moniker scheme so provenance survives edits.
- **M3 — No use of git history as architecture signal.** Co-change/logical coupling, churn hotspots, and blame are standard architecture-recovery signals; the graph uses only HEAD state. Add temporal-coupling edges (deferred is fine, but name it).
- **M4 — No test→code coverage mapping.** §3.3 only has "test-to-code edges where inferable." `coverage.py` gives ground-truth test→code edges and would make ObservableCheck quality measurable. Missing.
- **M5 — Golden decompositions / planted negatives dropped from the research.** `…pipeline.md:783-792, 899-916` specified a golden set + good/bad cases + held-out comparison; the spec replaced it with subjective pilot prose (§11). Reinstate a small golden+decoy corpus (ties to B4).
- **M6 — No incremental/Merkle graph design.** §3.3 caches "only if input hashes match" wholesale; a per-file content-addressed incremental graph is the scalable best practice and is unspecified.
- **M7 — Dead-code / duplication detection absent** as graph signals even though `duplicates` is an edge kind (§4.3) — the kind exists with no production rule.

---

## acceptance_criteria_issues

§12 mixes mechanical predicates with unverifiable judgments and a deliverable:

- **#1** "decomposes Build Arena without relying on current path-classifier semantics" — **unverifiable/undefined**: no gate detects "produced by a path classifier." Define a deterministic discriminator or move to advisory review.
- **#2** "easy for Leon to manually evaluate" — **subjective**, not pass/fail.
- **#3** "without *obvious* Build Arena overfit" — **subjective**; needs a metric (e.g., zero fabricated required-concerns on the held-out repo; enum members used only where evidence exists). Ties to B6.
- **#12** "Opus pilot review finds no unresolved critical blockers" — **contradicts** §3.2(6) sole-authority and the no-live-API principle (B5). Make advisory/non-gating.
- **#14** "Final report explains what works…" — a **deliverable**, not a pass/fail criterion; move to outputs.
- **Structural fix:** Split §12 into (a) *Deterministic acceptance gates* (mechanically checkable: emits all sidecars; hashes tie to git/disk; every accepted claim has resolvable deterministic provenance; coverage exactly-once; required-conditional concerns present; no-live-API acceptance; probes present+isolated+**discriminating**; protected surfaces tagged; freshness/hash integrity), and (b) *Advisory review* (Opus, manual plausibility) clearly labeled non-gating. Only (a) determines snapshot usability.

---

## held_out_probe_leakage_issues

- **HP1 (forward leak — handled):** §7.1/§7.7 keep probe corpus out of the same-snapshot decomposer prompt. Adequate as stated.
- **HP2 (cross-snapshot leak — gap, N6):** Committed prior `held-out-probes.json` under `.arena/project-model-snapshots/**` can re-enter a later run's inventory/decomposer input. The leakage gate (§7.7) only checks same-snapshot prompt text. **Patch:** add `.arena/project-model-snapshots/**` to default decomposer-input exclusions and add a gate rule that no prior held-out-probe content hash appears in the current decomposer input hashes.
- **HP3 (shared-model blindspot — gap, N7):** Probe builder may share model/family with the decomposer. Independence is the whole point of held-out exams. **Patch:** require `builder_model_id` ≠ decomposer `model_id` (preferably different family); gate fails if equal for high-risk probes.
- **HP4 (repair-channel slow leak):** §7.3-7.4 allow probe failures into repair rounds (new snapshot). Over repeated repairs on the same repo the decomposer effectively learns the probe distribution. **Patch:** hold out a never-used-in-repair probe subset per repo; cap repair rounds that consume probe findings (the spec already bounds repair to 2 rounds in §5.5 — extend that bound explicitly to probe-derived findings).
- **HP5 (discrimination unproven — see B4):** isolation without proven firing gives false assurance. **Patch:** require planted-negative validation per high-risk probe.

---

## f3_wrong_target_risks

- **F3-1 (thesis-level):** F3 is, by definition (`docs/project-model-v0.md:20-33`), coherent load-bearing reasoning at the wrong target — so a fully-provenanced, gate-passing decomposition can still be F3. The spec leans on the deterministic gate for "F3 resistance" (§4.8, §9.5) but the gate cannot detect wrong-targetness (B1). **Risk:** the spec over-claims deterministic F3 safety. **Mitigation:** state explicitly that F3 detection is probe/review-enforced; make probes discriminating (B4); restore near-neighbors + goal/non-goals (B3).
- **F3-2 (missing discriminator):** dropping `NearNeighborAlternative` and project `goal`/`non_goals` (B3) removes the only structural representation of "the plausible wrong target." Without it, neither the skeptic nor probes have an anchor to argue wrong-targetness.
- **F3-3 (meta-F3 in the verification ritual):** required-but-vacuous concerns (B6) and present-but-non-firing probes (B4) are themselves F3 — a coherent verification apparatus aimed at the wrong target (satisfying gate fields rather than catching real wrong-target decompositions).
- **F3-4 (encyclopedia-grounded fan fiction):** LLM encyclopedia prose as a citable `doc_section` provenance source (N5) lets the decomposer ground a wrong-target component on its own earlier prose. Fix via B2 transitive-to-source provenance.

---

## recommended_patch_plan (ordered by priority)

1. **B1** — Restructure the authority model: deterministic gate for structural/provenance/coverage/hash checks; add an explicit non-deterministic review-gate stage for wrong-target/file-bucket detection; define concrete predicates for any semantic check kept in the gate. (Unblocks everything else.)
2. **B2** — Restore mandatory `derived_by` + `confidence` on `ProvenanceRef`, make `content_hash` mandatory for text refs, and add the transitive-to-source resolution gate. (Anti-fabrication anchor.)
3. **B3** — Reintroduce top-level `goal`/`non_goals` on the snapshot and a required `NearNeighborAlternative` contract for high-risk leaves. (F3 discriminator.)
4. **B4 + M5** — Add planted-negative/golden corpus and a `held_out_probe_discrimination` gate; require probes to fire on paired decoys. (Proves the F3 thesis.)
5. **B6** — Make required cross-cutting concerns conditional on detected surfaces; mark Build-Arena-flavored enum members optional/extensible. (Generality; stops induced fabrication.)
6. **B5** — Demote Opus review to non-gating advisory; rewrite §12 into deterministic-gate criteria vs. advisory review (acceptance_criteria_issues).
7. **HP2/HP3/HP4** — Exclude `.arena/project-model-snapshots/**` from decomposer inputs + cross-snapshot leak gate; require probe-builder model independence; bound probe-derived repair.
8. **M1/M2** — Specify deterministic grounding for call/reference edges (grimp/import graph required, not optional) and forbid LLM-only high-impact edges without a gap; add stable symbol monikers for provenance.
9. **N1–N4, N8, M3/M4** — Define "deterministically audited"; mark `owned_paths` derived; harden no-live-API beyond honor-system booleans; explicitly retire the arena-calibration special case; correct the baseline description; name git-history and coverage signals (even if deferred).

---

## concise_final_summary

The spec is a real architectural upgrade and the staged graph → encyclopedia → LLM-decomposer → probe → deterministic-gate → frozen-snapshot pipeline is the right shape. But it does not yet hold together as a *codeless contract that prevents F3*, because: (1) it assigns the deterministic, no-LLM gate semantic judgments (vague/file-bucket/wrong-target) that only an LLM or human can make, leaving its load-bearing criteria undefined and unenforceable; (2) it dropped the anti-fabrication primitives its own source research and Opus precondition required — leaf-level provenance *derivation method/confidence*, and near-neighbor alternatives + explicit goal/non-goals — so the F3 discriminators are gone and provenance can't be distinguished from LLM assertion; (3) held-out probes are required to *exist* and be *isolated* but never proven to *discriminate*, so the F3-resistance claim is untested theater; (4) required cross-cutting concerns and Build-Arena-flavored enums force overfit/fabrication on the held-out pilots, defeating the generality goal; and (5) acceptance depends on a paid Opus review that contradicts both the "gate is sole authority" and "no live paid API" principles. The net effect today: the strongest *enforced* property is still v0's exactly-one-owner coverage, so a richer deterministic classifier with resolvable-but-fabricated provenance would pass automated acceptance. All five blockers are fixable at the spec level without code; fix them in the order above and re-review. **REQUEST_CHANGES.**
