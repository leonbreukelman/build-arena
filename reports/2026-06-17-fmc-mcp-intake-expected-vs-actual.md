# fmc-mcp intake: expected vs actual — 2026-06-17

## Bottom line

The intake run delivered the narrow first-slice scorecard contract, but it did not deliver the stronger Build Arena outcome we actually care about: a decomposition-informed, component-aware first improvement that can feed the next proposal/runner stage without collapsing back to generic docs hygiene.

In plain terms: the tool ran correctly, but the result is weak for the Build Arena north star. It selected `ops.runbooks.missing` and produced an advisory docs handoff, not a code/component/test improvement candidate from the high-reasoning Project Model.

## Documentation: what intake is supposed to deliver

### 1. Place in the pipeline

The canonical scorecard spec says intake sits after Project Model decomposition and before hypothesis selection:

- `docs/specs/2026-06-07-weighted-project-intake-prioritization.md:77`: the scorecard should not replace decomposition, verification, security scanning, tests, or owner judgment; it sits between project understanding and work selection.
- `docs/specs/2026-06-07-weighted-project-intake-prioritization.md:79-86`: flow is `repo/git/filesystem truth -> decomposition / Project Model v1 -> weighted project-intake scorecard -> ranked maintenance-risk register -> weighted improvement backlog -> selected first improvement or blocker -> implementation/review loop only when authorized and gates pass`.
- `weighted-project-intake-prioritization/references/build-arena-project-model-freshness-and-loop-handoff.md`: loop handoff sequence is decompose -> gate -> weighted intake/review -> validate synced/fresh model -> select bounded target/hypothesis -> proposer/runner -> verify -> promote -> refresh.

So intake is not mutation. It is the decision layer that says what should be worked on first and why.

### 2. First-slice artifact contract

The spec defines a mature vision and a smaller first slice:

- Mature intake should produce repo health model, documentation knowledge graph, AI usability score, maintenance risk register, weighted improvement backlog, first recommended improvement, accepted deferrals, and machine-readable sidecar (`docs/specs/2026-06-07-weighted-project-intake-prioritization.md:357-378`).
- First slice only needs:
  - machine-readable scorecard JSON,
  - concise markdown report,
  - ranked findings,
  - one first recommended improvement,
  - enough evidence links to verify why it outranks alternatives (`docs/specs/2026-06-07-weighted-project-intake-prioritization.md:378`).

Acceptance criteria require:

- JSON + markdown report,
- support for profiles including production,
- real filesystem/git/doc evidence or explicit absence checks,
- every finding linked to evidence,
- ranked list and first recommendation explaining why it outranks alternatives,
- no auto-editing and no treating scorecard output as authorization (`docs/specs/2026-06-07-weighted-project-intake-prioritization.md:437-463`).

The current implemented command contract adds:

- Freshness JSON via `project_model_cli freshness`; `safeForMutation` true only when status is `fresh`.
- Scorecard JSON + optional markdown via `project_intake_scorecard`.
- Advisory handoff JSON via `proposer_handoff`; hard-pinned `notAuthorizedForMutation: true`; includes protected paths (`weighted-project-intake-prioritization/references/build-arena-project-model-freshness-and-loop-handoff.md`).

### 3. Evolved Build Arena expectation: component-aware, non-doc findings

The newer Build Arena docs make the important correction: intake must not be docs-only.

- `weighted-project-intake-prioritization/references/build-arena-intake-component-findings.md`: previous docs-only behavior happened because intake used hardcoded documentation absence findings and discarded decomposer output.
- Same reference says the fix pattern is to read `iterationReadiness.componentProfiles`, `snapshot.components`, `snapshot.observable_checks`, and `projectGraph.nodes`, then emit component-scoped findings such as `code.component.untested.<componentId>` with real source-file targets.
- `docs/agent-wiki/2026-06-15-proposal-registry-lineage-and-repair-loop.md:15-17`: current rules say component findings should route through `component_verification` and receive load-bearing quality-gate commands from the `verification.quality-gates.present` intake finding.
- `docs/agent-wiki/2026-06-15-fmc-mcp-production-pass-lessons.md:18-24`: previous fmc-mcp failure was that the top code finding was skipped, turning the loop back into docs-only. The acceptance signal was a live cycle selecting `code.component.untested.comp-server` with a non-empty test+mypy/ruff/pytest gate.

This means the practical result we wanted from fmc-mcp intake was not merely “some scorecard exists.” We wanted intake to convert the fresh high-reasoning Project Model into a ranked, evidence-backed next-work decision that preserves component/code/test leverage where the model exposes it.

## Result we wanted from this intake

For this specific run, the desired result was:

1. Use the fresh, gate-clean high-reasoning fmc-mcp Project Model snapshot.
2. Confirm freshness and gate status before trusting the model.
3. Run the weighted production intake profile because fmc-mcp is an external-user/production-like target.
4. Emit the expected first-slice artifacts:
   - freshness JSON,
   - scorecard JSON,
   - markdown scorecard/report,
   - advisory handoff JSON.
5. Produce ranked findings that are grounded in the Project Model and repo evidence.
6. Interpret the evolved Build Arena intent, not just the first-slice acceptance test: prefer a genuinely high-leverage first improvement, ideally component/test/code/verification work if the Project Model shows high-risk components without adequate checks.
7. Interpret the evolved Build Arena intent: if the first recommendation is docs, it should be because docs/ops risk genuinely outranks component/code/test risk under the production weights, not because intake failed to express component findings.
8. Stop before proposal, runner, promotion, merge, or push.

## Actual result

Artifacts generated:

- Freshness: `.arena/runs/fmc-mcp-decomposition-grok43-high-reasoning-schema-fix-20260617T221237Z/intake/freshness.json`
- Gate rerun: `.arena/runs/fmc-mcp-decomposition-grok43-high-reasoning-schema-fix-20260617T221237Z/intake/gate-rerun.json`
- Scorecard JSON: `.arena/runs/fmc-mcp-decomposition-grok43-high-reasoning-schema-fix-20260617T221237Z/intake/scorecard-production.json`
- Scorecard markdown: `.arena/runs/fmc-mcp-decomposition-grok43-high-reasoning-schema-fix-20260617T221237Z/intake/scorecard-production.md`
- Advisory handoff: `.arena/runs/fmc-mcp-decomposition-grok43-high-reasoning-schema-fix-20260617T221237Z/intake/proposer-handoff.json`
- Summary report: `reports/2026-06-17-fmc-mcp-production-intake-result.md`

Freshness/gate:

- Freshness status: `fresh`
- Snapshot/current head: `25f445806d5221f21d7ac675799db5c30499f1b7`
- Target repo dirty: `false`
- Target repo ahead/behind: ahead 1, behind 0
- Gate rerun: `{"passed": true, "violations": []}`

Scorecard output:

| Rank | Finding | Score | Boundary | Notes |
|---:|---|---:|---|---|
| 1 | `ops.runbooks.missing` | 418.0 | `safe_to_patch_docs_only` | Absence of `docs/runbooks`; selected first recommendation. |
| 2 | `verification.quality-gates.present` | 216.0 | `advisory_only` | Surfaced `mypy`, `pytest`, and `ruff` commands. |
| 3 | `agent.agents-md.missing` | 192.0 | `safe_to_patch_docs_only` | Absence of `AGENTS.md`. |
| 4 | `architecture.open-questions-or-gaps` | 126.0 | `advisory_only` | Project Model open questions/gaps exist. |
| 5 | `decision.history.missing` | 110.0 | `safe_to_patch_docs_only` | Absence of `docs/decisions`. |

Handoff output:

- `selectedFindingId`: `ops.runbooks.missing`
- `targetFiles`: `["docs/runbooks"]`
- `successCriteria`: `Document start/stop/deploy/rollback/troubleshooting procedures`, `test -e docs/runbooks`
- `notAuthorizedForMutation`: `true`

Project Model evidence relevant to why no `code.component.untested.*` finding appeared:

- Snapshot has six high-reasoning components: `component.client`, `component.server`, `component.config`, `component.tools`, `component.resources`, `component.entry`.
- Component profiles rank `component.client` first and `component.server` second; five of six components are `riskLevel=high`.
- Snapshot has one observable check: `check.lint-and-type`, command `ruff check src/fmc_mcp && mypy src/fmc_mcp`.
- That one check declares coverage of all six components.
- The intake component-finding rule treats a component as checked if it has `check_ids` OR appears in any `observable_checks[].component_ids`. Since the single check references all components, no untested-component findings were emitted.

Mechanism evidence:

- Snapshot observable check: `snapshot.json:396-422` shows `check.lint-and-type` with `component_ids` containing all six components.
- Intake rule: `arena/project_intake_scorecard.py:351-361` builds `checked_component_ids` from component `check_ids` and from every `observable_checks[].component_ids`; `arena/project_intake_scorecard.py:292-293` skips any profile whose component id is in that checked set.
- The consequence is structural: there was no competing component finding for runbooks to beat. The broad lint/type check precluded the `code.component.untested.*` finding class before ranking.

## Comparison to expected result

| Expected | Actual | Verdict |
|---|---|---|
| Fresh gated Project Model before intake | Freshness status `fresh`; gate passed with no violations | Met |
| Production weighting profile | Used `--profile production` | Met |
| Machine-readable scorecard JSON | `scorecard-production.json` emitted | Met |
| Concise markdown scorecard/report | `scorecard-production.md` and separate report emitted | Met |
| Ranked findings | Five ranked findings emitted | Met narrowly |
| First recommended improvement | `ops.runbooks.missing` selected | Met mechanically, weak strategically |
| Evidence-backed findings or explicit absence checks | Findings cite absence paths or Project Model paths | Met |
| Advisory-only / no mutation | Handoff says `notAuthorizedForMutation=true`; no proposal/runner/promotion | Met |
| Decomposition-informed component/code/test leverage | No `code.component.*`, no `code.quality.*`, no component-scoped code/test target | Not met in spirit |
| High-risk component profiles influence first work | Five high-risk components did not create first-class findings because one broad lint/type check marked every component checked | Structurally precluded by current intake rule |
| Proposal-ready handoff | Handoff targets `docs/runbooks` with only `test -e docs/runbooks`; no non-empty content/link gate; no proposal plan | Not proposal-ready |
| Full mature intake vision: maintenance risk register + weighted improvement backlog + accepted deferrals | Only first-slice scorecard/handoff exists | Not mature/full vision |

## Assessment

Narrow answer: the intake command succeeded. It delivered the implemented first-slice artifacts and respected the no-mutation boundary.

Useful answer: this intake result is not the result we wanted if the goal was to use the newly fixed high-reasoning decomposition to drive a real next Build Arena improvement. It fell back to generic repo hygiene, with runbooks as the top finding. That is defensible under the production profile because operations/rollback has a high weight and `docs/runbooks` is absent. But it does not exercise the component-aware, multi-domain promise of the pipeline.

The main reason is not a command failure. It is a semantic weakness in the intake criteria: a single broad lint/type observable check covering every component prevents `code.component.untested.*` findings, even though the Project Model still marks core components as high-risk and only exposes one coarse check. Intake is treating broad static checks as enough component coverage.

## What this means next

If the next step is just to patch the first intake recommendation, the next proposal would be docs/runbooks. That is safe but low ambition.

If the next step is to validate Build Arena’s repo-scale autonomy path, this intake output is insufficient. The better target is to improve intake so it distinguishes coarse all-component quality checks from meaningful component-specific behavioral verification, then emits a high-risk component verification finding with a load-bearing gate.

Concrete correction target:

- Add an intake finding class such as `code.component.weak_behavioral_coverage.<componentId>` or refine `code.component.untested.*` logic so a component is not considered adequately checked solely because a generic lint/type command lists it in `observable_checks.component_ids`.
- Evidence should include component profile risk, owned source paths, the broad check command, and absence of component-specific behavioral tests.
- Verification for proposal candidates should reuse the surfaced quality gates plus a focused test requirement, not `[]` and not only docs existence.

That is the gap between “intake ran” and “intake produced the Build Arena result we wanted.”
