# Opus Review — AI-first Project Decomposer Implementation Plan

Source plan: `docs/plans/2026-06-04-ai-first-project-decomposer-implementation-plan.md`

Claude result metadata: subtype=success, cost_usd=1.1908642500000002, turns=9

## Parsed review JSON

```json
{
  "overall_verdict": "pass_with_changes",
  "blocking_findings": [
    {
      "id": "B1",
      "title": "Fixture/no-live mode is the only tested path, so acceptance proves a deterministic report generator — not the AI decomposer",
      "evidence": [
        "Plan §2: 'LLM claims are advisory: tests and acceptance use deterministic fixture/no-live adapters.'",
        "Plan Phase D implementation: 'deterministic synthesis of recursive components/contracts/concerns/checks/gaps' with FixtureProjectModelLLM/NoopProjectModelLLM; 'LiveProjectModelLLM seam exists but is not exercised in tests.'",
        "Plan §7 Pilot 1 step 4: live Grok used only 'If live Grok is available and not blocked'; §9 artifact validation asserts only `report['passed'] is True` and manifest schema_version, which a deterministic synthesizer satisfies trivially.",
        "Spec §1.7/§12 require the decomposer to actually distinguish responsibility-bearing components from file buckets via the LLM pass."
      ],
      "why_it_matters": "Every acceptance gate, pilot validation, and the final artifact check can be satisfied by the deterministic in-process synthesizer with no real LLM call ever made. The thing the spec exists to build — an AI-first decomposer whose LLM output is validated as non-bucket — is never exercised by any green test or any required pilot. The plan can ship a fully 'passing' deliverable that is a plausible JSON/report generator, which is exactly the failure mode the review was asked to attack.",
      "recommended_change": "Require at least one recorded live decomposition pilot (or a frozen, committed real-LLM output fixture captured once and replayed) as a non-optional acceptance artifact, clearly labeled non-gating-for-CI but gating-for-delivery. Add a test that feeds a realistic LLM-shaped decomposition fixture (buckets with polished names) and asserts the gate+probes reject it, separating 'gate accepts well-grounded JSON' from 'gate rejects fluent file-bucket JSON.'"
    },
    {
      "id": "B2",
      "title": "Held-out probe discrimination is circular: the same deterministic builder authors both probe and planted negative in fixture mode",
      "evidence": [
        "Plan Phase D: orchestration 'build held-out probes and planted negatives' both produced by the same deterministic synthesizer in fixture/off mode.",
        "Plan Phase C test 6 `test_gate_requires_held_out_probe_isolation_and_planted_negative_discrimination` validates that a probe fires on its paired decoy, but both come from one code path.",
        "Spec §4.11 requires `builder_independent_from_decomposer` and §6.5/HP3 require builder model independence; plan records the boolean but no test enforces builder ≠ decomposer."
      ],
      "why_it_matters": "If one deterministic function emits the probe and the decoy it must fire on, discrimination is guaranteed by construction and proves nothing — it is the meta-F3 'present-but-vacuous probe' theater the spec review (B4/F3-3) flagged. The discrimination gate becomes a self-fulfilling ritual rather than evidence the probes catch wrong-target decompositions.",
      "recommended_change": "Add a test that a planted negative authored independently of the probe builder (e.g., a hand-crafted file-bucket decoy committed as a fixture) is correctly fired on, AND that a known-good (golden) decomposition does NOT trip the probe (false-positive control). Enforce `builder_independent_from_decomposer`/model-id inequality in the gate for high-risk model-built probes."
    },
    {
      "id": "B3",
      "title": "Skeptic/F3 review stage from the spec is dropped from the build and from all tests",
      "evidence": [
        "Spec §3.1, §5.3 steps 10-11, §6.4 require a Skeptic/F3 review + repair loop as a pipeline stage; storage layout in plan §5 even reserves `prompts/skeptic-reviewer-prompt.txt` and `model-outputs/skeptic-review.raw.json`.",
        "Plan Phase D orchestration lists: build graph; build encyclopedia; run adapter; deterministic synthesis; near-neighbor; probes/planted negatives; gate; write; v0 — no skeptic review step.",
        "No test in `tests/test_project_decomposer_ai.py` exercises skeptic findings, repair classification, or the bounded two-round repair loop (spec §5.5)."
      ],
      "why_it_matters": "The spec's own authority model (revised per spec-review B1) makes wrong-target/file-bucket detection probe- and review-enforced, not gate-enforced. Dropping the review stage removes half of that non-deterministic enforcement, leaving only the deterministic gate to catch semantic wrong-targetness — the precise overreach the spec was rewritten to avoid. The artifact layout writes empty review slots, creating the appearance of a review that never runs.",
      "recommended_change": "Add the skeptic review + bounded-repair stage to Phase D orchestration and add tests: skeptic findings are classified valid/invalid/needs-evidence, valid findings drive repair, repair creates a new snapshot with new prompt/output hashes, and recurrence after two rounds becomes a VerificationGap/blocker. Keep it advisory/non-gating for CI but present as a real stage."
    },
    {
      "id": "B4",
      "title": "goal/non_goals (the wrong-target anchor) are not surfaced by the CLI, snapshot writer, or any test",
      "evidence": [
        "Spec §4.13 requires top-level `goal` and `non_goals` on ProjectModelSnapshot; spec-review B3 made this a blocker and the spec adopted it.",
        "Plan §5 CLI signature exposes `--source-task`, `--primary-backlog-item`, `--project-id` but no `--goal`/`--non-goals`; plan §5 manifest layout and Phase C/D tests never assert goal/non_goals presence or that near-neighbor `why_not_primary` cites goal/non-goal anchors (spec §4.8 invariant).",
        "Spec §5.1 defines defaults for goal/non-goals, but the plan never threads them into the snapshot or validates them."
      ],
      "why_it_matters": "Without goal/non_goals represented on the snapshot, there is no structural anchor for 'what this decomposition is NOT about,' so neither the skeptic nor near-neighbor alternatives have a target to test wrong-targetness against. This is the primary F3 discriminator the spec restored; the plan silently re-drops it at the implementation layer.",
      "recommended_change": "Add goal/non_goals to the snapshot manifest contract, default them per spec §5.1, surface optional `--goal`/`--non-goals` CLI flags, and add a gate/test that near-neighbor `why_not_primary` references the snapshot's goal/non-goals and that the snapshot carries non-empty non_goals."
    },
    {
      "id": "B5",
      "title": "No concrete deterministic file-bucket predicate test; the deterministic synthesizer is itself a renamed path-bucket classifier and the existing arena-calibration overfit is preserved",
      "evidence": [
        "Plan Phase C test 3 `test_gate_fails_vague_or_file_bucket_components` is the only bucket test; the spec's concrete predicate (spec §3.6/§4.6: owned nodes ≥ near-entirely sibling files under one directory with no symbol/contract/check references) is never given a dedicated test with non-vague names.",
        "Plan Phase D deterministic synthesis derives components from graph structure only (in fixture/off mode); with no LLM, the only available signal is path/symbol grouping — i.e., buckets with richer names that pass a lexical denylist (spec-review B1/N2).",
        "Plan §4 'Files to modify' keeps `arena/decomposer.py` `_looks_like_arena_calibration`/`_arena_*` overfit intact ('Preserve current CLI default and Project Model v0 behavior'); spec-review N4 asked to quarantine/retire it."
      ],
      "why_it_matters": "The strongest enforced property remains v0's exactly-one-owner coverage plus a lexical name denylist. A component named 'Calibration Fixture Integrity Subsystem' owning sibling files with invented-but-resolvable provenance passes every predicate the plan tests. The fixture-mode synthesizer will, to make `test_python_project_decomposition_uses_symbols_imports_contracts_not_only_paths` pass, hardcode synthetic mappings — re-creating the overfit it was meant to replace.",
      "recommended_change": "Implement and test the concrete structural file-bucket predicate (owned-node sibling-ratio + zero graph-resolvable symbol/contract/check references → fail) with non-vague names. Explicitly quarantine or remove the `_looks_like_arena_calibration` special case so it cannot be the latent baseline beside the new pipeline. Avoid building a deterministic 'decomposer' that competes with the LLM; instead test the gate against hand-authored good/bad decomposition fixtures."
    }
  ],
  "nonblocking_findings": [
    {
      "id": "N1",
      "title": "Cross-snapshot probe leakage gate is not tested",
      "evidence": [
        "Spec §7.5/§7.7 and spec-review HP2/N6 require excluding `.arena/project-model-snapshots/**` and prior held-out-probe hashes from decomposer inputs.",
        "Plan Phase B test 3 excludes prior verification outputs from encyclopedia source truth, but no Phase C/D gate test asserts that prior-snapshot held-out-probe content hashes are absent from current decomposer input hashes."
      ],
      "recommended_change": "Add a gate test that a committed prior `held-out-probes.json` hash appearing in current decomposer input fails the leakage gate."
    },
    {
      "id": "N2",
      "title": "High-impact LLM-only edges (calls/references) are not forced into gaps",
      "evidence": [
        "Spec §3.3 and spec-review M1: high-impact `calls`/`references`/`depends_on` edges must be deterministic or downgraded to VerificationGap.",
        "Plan Phase A grounds only import edges + 'test edges by import/call-name heuristics'; no test asserts LLM-inferred high-impact edges without deterministic grounding become gaps."
      ],
      "recommended_change": "Add a gate test: an LLM-confidence calls/references edge with no deterministic supporting rule must be rejected or converted to a VerificationGap."
    },
    {
      "id": "N3",
      "title": "FMC-MPC discovery and held-out-repo selection have no fallback path, but §9 verification hard-asserts their pilot manifests exist",
      "evidence": [
        "Plan §7 Pilot 2 discovery `rglob('*')` over `/home/leonb` may be slow/unreadable; if no FMC repo exists the plan says choose canonical 'unless no safe candidate exists' but defines no behavior when none exists.",
        "Plan §9 artifact-validation script asserts `manifests, f'no manifest under {root}'` for all three pilot roots, so a missing FMC-MPC or held-out repo hard-fails final verification."
      ],
      "recommended_change": "Define explicit fallback when a pilot repo cannot be found (record an OUT_OF_SCOPE/GAP_ACCEPTED entry) and make the §9 validation tolerate documented-absent pilots instead of asserting presence."
    },
    {
      "id": "N4",
      "title": "Phase D bundles the entire snapshot surface at once, contradicting the spec's smaller recommended first slice",
      "evidence": [
        "Spec §15 recommends incremental slices (graph → wiki → manifest/hash → adapter seam → decomposition/gate → pilots).",
        "Plan Phase D simultaneously builds synthesis + near-neighbors + held-out probes + planted negatives + gate + v0 projection, the heaviest phase with 8 tests and the most coupling."
      ],
      "recommended_change": "Split Phase D into D1 (decomposition + gate + v0) and D2 (near-neighbors + probes + planted negatives + discrimination) so each lands with a smaller rollback surface."
    },
    {
      "id": "N5",
      "title": "Several edge kinds and concern categories are specified with no production rule (dead vocabulary)",
      "evidence": [
        "Spec §4.3 includes `duplicates`, `derived_from`; spec-review M7 noted no production rule. Plan Phase A graph builder lists no rule for these.",
        "Plan does not state which GraphEdge kinds are actually produced in the first slice vs left as latent enum members."
      ],
      "recommended_change": "Enumerate which node/edge kinds are produced in slice 1; mark the rest as reserved/unused to avoid implying coverage that does not exist."
    }
  ],
  "missing_tests": [
    "A test that a fluent, non-vague file-bucket decomposition (polished names, sibling-file ownership, resolvable-but-shallow provenance) is REJECTED by the gate — separating structural validity from semantic responsibility (spec §3.6/§4.6, review B1).",
    "A false-positive control: a known-good 'golden' decomposition must NOT trip held-out probes/discrimination (review B4/M5).",
    "A test enforcing probe-builder independence from the decomposer model for high-risk probes (spec §4.11, review HP3).",
    "A skeptic/F3 review-stage test: finding classification, repair, new-snapshot hash chain, and two-round repair bound (spec §5.3/§5.5/§6.4).",
    "Tests asserting goal/non_goals are present on the snapshot and that near-neighbor `why_not_primary` cites them (spec §4.8/§4.13, review B3).",
    "A cross-snapshot probe-leakage gate test (spec §7.7, review HP2/N6).",
    "A test that LLM-only high-impact edges (calls/references) without deterministic grounding are downgraded to VerificationGap (spec §3.3, review M1).",
    "A byte-for-byte reproducibility test: two runs over identical git/disk inputs produce identical canonical snapshot artifacts (spec §3.3, §10.3).",
    "A protected-surface enforcement test that an arena-generated hypothesis targeting `scorer/`/`verifier/`/`schema/` is a gate blocker, not merely that surfaces are tagged (spec §8).",
    "A live-vs-fixture parity test (even with a recorded real-LLM fixture) proving the orchestration path that consumes actual model output is exercised at least once (review B1)."
  ],
  "overengineering_risks": [
    "Building a full deterministic in-process 'decomposer' (component/contract/concern/check/probe synthesis) solely to make tests pass duplicates the LLM's job, will drift from real LLM output shape, and risks becoming the de-facto product; testing the gate against hand-authored fixtures would be lighter and more honest.",
    "Front-loading the entire 8-file snapshot bundle (prompts/, model-outputs/, encyclopedia subtree, near-neighbors, planted negatives, allowlist) in slice 1 is a large surface versus the spec's recommended incremental build (spec §15).",
    "Large node/edge/concern/probe enum vocabularies with no production rules add schema weight without behavior (duplicates, derived_from, several concern categories)."
  ],
  "underbuilding_risks": [
    "Skeptic/F3 review + repair loop is entirely absent from orchestration and tests despite being a required spec stage with reserved artifact slots.",
    "goal/non_goals are not threaded into CLI/snapshot/tests, removing the primary wrong-target anchor at the implementation layer.",
    "Deterministic grounding for call/reference edges is deferred, leaving the most architecturally important edges to LLM inference without a gap-downgrade rule.",
    "The live LLM path is never exercised, so the actual decomposition behavior (the deliverable's whole point) has no executed code path in the test suite.",
    "No retirement/quarantine of the existing `_looks_like_arena_calibration` overfit, which survives as a latent baseline."
  ],
  "pilot_validation_risks": [
    "All three pilots can pass on fixture/no-live mode; §9 validation only checks artifact presence + gate pass, so pilots prove the deterministic synthesizer generalizes, not that the AI decomposer produces non-bucket decompositions.",
    "Live Grok pilots are optional ('if available and not blocked'), so a 'passing' delivery may contain zero real LLM decompositions and zero real evidence of working AI-first behavior.",
    "Opus pilot review is correctly advisory/non-gating, but because it is the only stage that could catch fluent file-bucket output, dropping it (when Grok/Opus unavailable) leaves no wrong-target check at all on real output.",
    "Planted-negative discrimination in pilots is builder-circular (B2), so pilot 'discrimination passed' results do not evidence real F3 resistance.",
    "FMC-MPC and held-out-repo discovery may fail silently or hard-fail §9; pilot generality (spec §12.2/§12.3) is asserted subjectively with no metric for 'no obvious Build Arena overfit' beyond Opus prose."
  ],
  "summary": "The plan is structurally sound, TDD-disciplined, sidecar-first, and faithfully operationalizes most of the spec-review blockers the spec itself absorbed: transitive source provenance and dirty-file hashes (Phase C tests 2/8), planted-negative discrimination (test 6), no-live-API acceptance allowlist (test 7), conditional cross-cutting concerns (test 5), and cached-projection authority. That earns pass_with_changes rather than fail. But it has five plan-level blockers that, uncorrected, would yield a plausible report generator rather than a working decomposer: (B1) fixture/no-live mode is the only tested and only required path, so acceptance never exercises the real LLM decomposer and a deterministic synthesizer satisfies every gate and pilot; (B2) probe and planted negative are authored by the same deterministic builder, making discrimination circular and the F3 thesis unproven; (B3) the spec-required skeptic/F3 review stage is dropped from orchestration and tests while its artifact slots are still written; (B4) goal/non_goals — the restored wrong-target anchor — are not surfaced in the CLI, snapshot, or any test; and (B5) there is no concrete structural file-bucket predicate test, the in-process synthesizer is itself a renamed path-bucket classifier, and the existing arena-calibration overfit is preserved. Fix order: B1 (require a real/recorded-live decomposition as gating-for-delivery and add a fluent-bucket rejection test), B5 (concrete bucket predicate + retire the special case), B2 (independent decoy + golden false-positive control), B3 (add the review stage), B4 (thread goal/non_goals), then the nonblocking provenance-edge, cross-snapshot-leakage, and pilot-fallback hardening."
}
```

## Raw Opus result

Based on my review of the plan against the spec, the spec's Opus review, and the existing code, here is my adversarial assessment.

{
  "overall_verdict": "pass_with_changes",
  "blocking_findings": [
    {
      "id": "B1",
      "title": "Fixture/no-live mode is the only tested path, so acceptance proves a deterministic report generator — not the AI decomposer",
      "evidence": [
        "Plan §2: 'LLM claims are advisory: tests and acceptance use deterministic fixture/no-live adapters.'",
        "Plan Phase D implementation: 'deterministic synthesis of recursive components/contracts/concerns/checks/gaps' with FixtureProjectModelLLM/NoopProjectModelLLM; 'LiveProjectModelLLM seam exists but is not exercised in tests.'",
        "Plan §7 Pilot 1 step 4: live Grok used only 'If live Grok is available and not blocked'; §9 artifact validation asserts only `report['passed'] is True` and manifest schema_version, which a deterministic synthesizer satisfies trivially.",
        "Spec §1.7/§12 require the decomposer to actually distinguish responsibility-bearing components from file buckets via the LLM pass."
      ],
      "why_it_matters": "Every acceptance gate, pilot validation, and the final artifact check can be satisfied by the deterministic in-process synthesizer with no real LLM call ever made. The thing the spec exists to build — an AI-first decomposer whose LLM output is validated as non-bucket — is never exercised by any green test or any required pilot. The plan can ship a fully 'passing' deliverable that is a plausible JSON/report generator, which is exactly the failure mode the review was asked to attack.",
      "recommended_change": "Require at least one recorded live decomposition pilot (or a frozen, committed real-LLM output fixture captured once and replayed) as a non-optional acceptance artifact, clearly labeled non-gating-for-CI but gating-for-delivery. Add a test that feeds a realistic LLM-shaped decomposition fixture (buckets with polished names) and asserts the gate+probes reject it, separating 'gate accepts well-grounded JSON' from 'gate rejects fluent file-bucket JSON.'"
    },
    {
      "id": "B2",
      "title": "Held-out probe discrimination is circular: the same deterministic builder authors both probe and planted negative in fixture mode",
      "evidence": [
        "Plan Phase D: orchestration 'build held-out probes and planted negatives' both produced by the same deterministic synthesizer in fixture/off mode.",
        "Plan Phase C test 6 `test_gate_requires_held_out_probe_isolation_and_planted_negative_discrimination` validates that a probe fires on its paired decoy, but both come from one code path.",
        "Spec §4.11 requires `builder_independent_from_decomposer` and §6.5/HP3 require builder model independence; plan records the boolean but no test enforces builder ≠ decomposer."
      ],
      "why_it_matters": "If one deterministic function emits the probe and the decoy it must fire on, discrimination is guaranteed by construction and proves nothing — it is the meta-F3 'present-but-vacuous probe' theater the spec review (B4/F3-3) flagged. The discrimination gate becomes a self-fulfilling ritual rather than evidence the probes catch wrong-target decompositions.",
      "recommended_change": "Add a test that a planted negative authored independently of the probe builder (e.g., a hand-crafted file-bucket decoy committed as a fixture) is correctly fired on, AND that a known-good (golden) decomposition does NOT trip the probe (false-positive control). Enforce `builder_independent_from_decomposer`/model-id inequality in the gate for high-risk model-built probes."
    },
    {
      "id": "B3",
      "title": "Skeptic/F3 review stage from the spec is dropped from the build and from all tests",
      "evidence": [
        "Spec §3.1, §5.3 steps 10-11, §6.4 require a Skeptic/F3 review + repair loop as a pipeline stage; storage layout in plan §5 even reserves `prompts/skeptic-reviewer-prompt.txt` and `model-outputs/skeptic-review.raw.json`.",
        "Plan Phase D orchestration lists: build graph; build encyclopedia; run adapter; deterministic synthesis; near-neighbor; probes/planted negatives; gate; write; v0 — no skeptic review step.",
        "No test in `tests/test_project_decomposer_ai.py` exercises skeptic findings, repair classification, or the bounded two-round repair loop (spec §5.5)."
      ],
      "why_it_matters": "The spec's own authority model (revised per spec-review B1) makes wrong-target/file-bucket detection probe- and review-enforced, not gate-enforced. Dropping the review stage removes half of that non-deterministic enforcement, leaving only the deterministic gate to catch semantic wrong-targetness — the precise overreach the spec was rewritten to avoid. The artifact layout writes empty review slots, creating the appearance of a review that never runs.",
      "recommended_change": "Add the skeptic review + bounded-repair stage to Phase D orchestration and add tests: skeptic findings are classified valid/invalid/needs-evidence, valid findings drive repair, repair creates a new snapshot with new prompt/output hashes, and recurrence after two rounds becomes a VerificationGap/blocker. Keep it advisory/non-gating for CI but present as a real stage."
    },
    {
      "id": "B4",
      "title": "goal/non_goals (the wrong-target anchor) are not surfaced by the CLI, snapshot writer, or any test",
      "evidence": [
        "Spec §4.13 requires top-level `goal` and `non_goals` on ProjectModelSnapshot; spec-review B3 made this a blocker and the spec adopted it.",
        "Plan §5 CLI signature exposes `--source-task`, `--primary-backlog-item`, `--project-id` but no `--goal`/`--non-goals`; plan §5 manifest layout and Phase C/D tests never assert goal/non_goals presence or that near-neighbor `why_not_primary` cites goal/non-goal anchors (spec §4.8 invariant).",
        "Spec §5.1 defines defaults for goal/non-goals, but the plan never threads them into the snapshot or validates them."
      ],
      "why_it_matters": "Without goal/non_goals represented on the snapshot, there is no structural anchor for 'what this decomposition is NOT about,' so neither the skeptic nor near-neighbor alternatives have a target to test wrong-targetness against. This is the primary F3 discriminator the spec restored; the plan silently re-drops it at the implementation layer.",
      "recommended_change": "Add goal/non_goals to the snapshot manifest contract, default them per spec §5.1, surface optional `--goal`/`--non-goals` CLI flags, and add a gate/test that near-neighbor `why_not_primary` references the snapshot's goal/non-goals and that the snapshot carries non-empty non_goals."
    },
    {
      "id": "B5",
      "title": "No concrete deterministic file-bucket predicate test; the deterministic synthesizer is itself a renamed path-bucket classifier and the existing arena-calibration overfit is preserved",
      "evidence": [
        "Plan Phase C test 3 `test_gate_fails_vague_or_file_bucket_components` is the only bucket test; the spec's concrete predicate (spec §3.6/§4.6: owned nodes ≥ near-entirely sibling files under one directory with no symbol/contract/check references) is never given a dedicated test with non-vague names.",
        "Plan Phase D deterministic synthesis derives components from graph structure only (in fixture/off mode); with no LLM, the only available signal is path/symbol grouping — i.e., buckets with richer names that pass a lexical denylist (spec-review B1/N2).",
        "Plan §4 'Files to modify' keeps `arena/decomposer.py` `_looks_like_arena_calibration`/`_arena_*` overfit intact ('Preserve current CLI default and Project Model v0 behavior'); spec-review N4 asked to quarantine/retire it."
      ],
      "why_it_matters": "The strongest enforced property remains v0's exactly-one-owner coverage plus a lexical name denylist. A component named 'Calibration Fixture Integrity Subsystem' owning sibling files with invented-but-resolvable provenance passes every predicate the plan tests. The fixture-mode synthesizer will, to make `test_python_project_decomposition_uses_symbols_imports_contracts_not_only_paths` pass, hardcode synthetic mappings — re-creating the overfit it was meant to replace.",
      "recommended_change": "Implement and test the concrete structural file-bucket predicate (owned-node sibling-ratio + zero graph-resolvable symbol/contract/check references → fail) with non-vague names. Explicitly quarantine or remove the `_looks_like_arena_calibration` special case so it cannot be the latent baseline beside the new pipeline. Avoid building a deterministic 'decomposer' that competes with the LLM; instead test the gate against hand-authored good/bad decomposition fixtures."
    }
  ],
  "nonblocking_findings": [
    {
      "id": "N1",
      "title": "Cross-snapshot probe leakage gate is not tested",
      "evidence": [
        "Spec §7.5/§7.7 and spec-review HP2/N6 require excluding `.arena/project-model-snapshots/**` and prior held-out-probe hashes from decomposer inputs.",
        "Plan Phase B test 3 excludes prior verification outputs from encyclopedia source truth, but no Phase C/D gate test asserts that prior-snapshot held-out-probe content hashes are absent from current decomposer input hashes."
      ],
      "recommended_change": "Add a gate test that a committed prior `held-out-probes.json` hash appearing in current decomposer input fails the leakage gate."
    },
    {
      "id": "N2",
      "title": "High-impact LLM-only edges (calls/references) are not forced into gaps",
      "evidence": [
        "Spec §3.3 and spec-review M1: high-impact `calls`/`references`/`depends_on` edges must be deterministic or downgraded to VerificationGap.",
        "Plan Phase A grounds only import edges + 'test edges by import/call-name heuristics'; no test asserts LLM-inferred high-impact edges without deterministic grounding become gaps."
      ],
      "recommended_change": "Add a gate test: an LLM-confidence calls/references edge with no deterministic supporting rule must be rejected or converted to a VerificationGap."
    },
    {
      "id": "N3",
      "title": "FMC-MPC discovery and held-out-repo selection have no fallback path, but §9 verification hard-asserts their pilot manifests exist",
      "evidence": [
        "Plan §7 Pilot 2 discovery `rglob('*')` over `/home/leonb` may be slow/unreadable; if no FMC repo exists the plan says choose canonical 'unless no safe candidate exists' but defines no behavior when none exists.",
        "Plan §9 artifact-validation script asserts `manifests, f'no manifest under {root}'` for all three pilot roots, so a missing FMC-MPC or held-out repo hard-fails final verification."
      ],
      "recommended_change": "Define explicit fallback when a pilot repo cannot be found (record an OUT_OF_SCOPE/GAP_ACCEPTED entry) and make the §9 validation tolerate documented-absent pilots instead of asserting presence."
    },
    {
      "id": "N4",
      "title": "Phase D bundles the entire snapshot surface at once, contradicting the spec's smaller recommended first slice",
      "evidence": [
        "Spec §15 recommends incremental slices (graph → wiki → manifest/hash → adapter seam → decomposition/gate → pilots).",
        "Plan Phase D simultaneously builds synthesis + near-neighbors + held-out probes + planted negatives + gate + v0 projection, the heaviest phase with 8 tests and the most coupling."
      ],
      "recommended_change": "Split Phase D into D1 (decomposition + gate + v0) and D2 (near-neighbors + probes + planted negatives + discrimination) so each lands with a smaller rollback surface."
    },
    {
      "id": "N5",
      "title": "Several edge kinds and concern categories are specified with no production rule (dead vocabulary)",
      "evidence": [
        "Spec §4.3 includes `duplicates`, `derived_from`; spec-review M7 noted no production rule. Plan Phase A graph builder lists no rule for these.",
        "Plan does not state which GraphEdge kinds are actually produced in the first slice vs left as latent enum members."
      ],
      "recommended_change": "Enumerate which node/edge kinds are produced in slice 1; mark the rest as reserved/unused to avoid implying coverage that does not exist."
    }
  ],
  "missing_tests": [
    "A test that a fluent, non-vague file-bucket decomposition (polished names, sibling-file ownership, resolvable-but-shallow provenance) is REJECTED by the gate — separating structural validity from semantic responsibility (spec §3.6/§4.6, review B1).",
    "A false-positive control: a known-good 'golden' decomposition must NOT trip held-out probes/discrimination (review B4/M5).",
    "A test enforcing probe-builder independence from the decomposer model for high-risk probes (spec §4.11, review HP3).",
    "A skeptic/F3 review-stage test: finding classification, repair, new-snapshot hash chain, and two-round repair bound (spec §5.3/§5.5/§6.4).",
    "Tests asserting goal/non_goals are present on the snapshot and that near-neighbor `why_not_primary` cites them (spec §4.8/§4.13, review B3).",
    "A cross-snapshot probe-leakage gate test (spec §7.7, review HP2/N6).",
    "A test that LLM-only high-impact edges (calls/references) without deterministic grounding are downgraded to VerificationGap (spec §3.3, review M1).",
    "A byte-for-byte reproducibility test: two runs over identical git/disk inputs produce identical canonical snapshot artifacts (spec §3.3, §10.3).",
    "A protected-surface enforcement test that an arena-generated hypothesis targeting `scorer/`/`verifier/`/`schema/` is a gate blocker, not merely that surfaces are tagged (spec §8).",
    "A live-vs-fixture parity test (even with a recorded real-LLM fixture) proving the orchestration path that consumes actual model output is exercised at least once (review B1)."
  ],
  "overengineering_risks": [
    "Building a full deterministic in-process 'decomposer' (component/contract/concern/check/probe synthesis) solely to make tests pass duplicates the LLM's job, will drift from real LLM output shape, and risks becoming the de-facto product; testing the gate against hand-authored fixtures would be lighter and more honest.",
    "Front-loading the entire 8-file snapshot bundle (prompts/, model-outputs/, encyclopedia subtree, near-neighbors, planted negatives, allowlist) in slice 1 is a large surface versus the spec's recommended incremental build (spec §15).",
    "Large node/edge/concern/probe enum vocabularies with no production rules add schema weight without behavior (duplicates, derived_from, several concern categories)."
  ],
  "underbuilding_risks": [
    "Skeptic/F3 review + repair loop is entirely absent from orchestration and tests despite being a required spec stage with reserved artifact slots.",
    "goal/non_goals are not threaded into CLI/snapshot/tests, removing the primary wrong-target anchor at the implementation layer.",
    "Deterministic grounding for call/reference edges is deferred, leaving the most architecturally important edges to LLM inference without a gap-downgrade rule.",
    "The live LLM path is never exercised, so the actual decomposition behavior (the deliverable's whole point) has no executed code path in the test suite.",
    "No retirement/quarantine of the existing `_looks_like_arena_calibration` overfit, which survives as a latent baseline."
  ],
  "pilot_validation_risks": [
    "All three pilots can pass on fixture/no-live mode; §9 validation only checks artifact presence + gate pass, so pilots prove the deterministic synthesizer generalizes, not that the AI decomposer produces non-bucket decompositions.",
    "Live Grok pilots are optional ('if available and not blocked'), so a 'passing' delivery may contain zero real LLM decompositions and zero real evidence of working AI-first behavior.",
    "Opus pilot review is correctly advisory/non-gating, but because it is the only stage that could catch fluent file-bucket output, dropping it (when Grok/Opus unavailable) leaves no wrong-target check at all on real output.",
    "Planted-negative discrimination in pilots is builder-circular (B2), so pilot 'discrimination passed' results do not evidence real F3 resistance.",
    "FMC-MPC and held-out-repo discovery may fail silently or hard-fail §9; pilot generality (spec §12.2/§12.3) is asserted subjectively with no metric for 'no obvious Build Arena overfit' beyond Opus prose."
  ],
  "summary": "The plan is structurally sound, TDD-disciplined, sidecar-first, and faithfully operationalizes most of the spec-review blockers the spec itself absorbed: transitive source provenance and dirty-file hashes (Phase C tests 2/8), planted-negative discrimination (test 6), no-live-API acceptance allowlist (test 7), conditional cross-cutting concerns (test 5), and cached-projection authority. That earns pass_with_changes rather than fail. But it has five plan-level blockers that, uncorrected, would yield a plausible report generator rather than a working decomposer: (B1) fixture/no-live mode is the only tested and only required path, so acceptance never exercises the real LLM decomposer and a deterministic synthesizer satisfies every gate and pilot; (B2) probe and planted negative are authored by the same deterministic builder, making discrimination circular and the F3 thesis unproven; (B3) the spec-required skeptic/F3 review stage is dropped from orchestration and tests while its artifact slots are still written; (B4) goal/non_goals — the restored wrong-target anchor — are not surfaced in the CLI, snapshot, or any test; and (B5) there is no concrete structural file-bucket predicate test, the in-process synthesizer is itself a renamed path-bucket classifier, and the existing arena-calibration overfit is preserved. Fix order: B1 (require a real/recorded-live decomposition as gating-for-delivery and add a fluent-bucket rejection test), B5 (concrete bucket predicate + retire the special case), B2 (independent decoy + golden false-positive control), B3 (add the review stage), B4 (thread goal/non_goals), then the nonblocking provenance-edge, cross-snapshot-leakage, and pilot-fallback hardening."
}
