# fmc-mcp proposer run + advisory actionability report — 2026-06-18

## Owner answer

We ran the current proposer. It is not clean enough even for the top docs candidate yet.

Result: fail-closed. No target repo mutation. No patch recorded. The isolated worktree is clean.

The docs run failed on a narrower path-resolution/prompt mismatch. The advisory architecture/verification gap is distinct and deeper. Both sit in the target/gate-semantics layer, but they are not the same defect.

Separately, Opus inspected the current proposer code. Its finding is blunt:

- `verification.quality-gates.present` should not become a standalone proposal. It is context already consumed by the planner.
- `architecture.open-questions-or-gaps` should become an actionable advisory/backlog candidate, but current code excludes it because `ModelLevelDomain` only accepts `safe_to_patch_docs_only`, while the finding is `advisory_only`.
- A minimal patch can make architecture advisory findings produce `docs/agent-backlog.md`, but a durable fix requires content-aware gates so the proposer cannot pass by writing generic prose.

## 1. Bounded proposer run result

Command shape:

```text
uv run python -m arena.proposal_candidate_runner \
  --worktree <build-arena>/.arena/worktrees/fmc-mcp-proposer-docs-rank1-20260618T013019Z \
  --proposal-plan <build-arena>/.arena/runs/fmc-mcp-proposer-docs-rank1-20260618T013019Z/proposal-plan.json \
  --candidate-rank 1 \
  --provider xai \
  --api-key-env XAI_API_KEY \
  --model grok-4.3 \
  --output <build-arena>/.arena/runs/fmc-mcp-proposer-docs-rank1-20260618T013019Z/proposal-result.json
```

Inputs:

- Target repo: `<fmc-mcp>`
- Base head: `25f445806d5221f21d7ac675799db5c30499f1b7`
- Worktree: `<build-arena>/.arena/worktrees/fmc-mcp-proposer-docs-rank1-20260618T013019Z`
- Run dir: `<build-arena>/.arena/runs/fmc-mcp-proposer-docs-rank1-20260618T013019Z`
- Candidate: `ops.runbooks.missing`
- Target: `docs/runbooks/index.md`

Structured output:

```json
{"error": "RunnerError: missing Markdown link target: docs/index.md->docs/runbooks/docs/index.md, README.md->docs/runbooks/README.md", "ok": false}
```

Post-run evidence:

```text
=== worktree status ===
## HEAD (no branch)
=== patches ===
no patch dir
```

Interpretation:

- The proposer attempted the docs candidate.
- The markdown gate rejected the output.
- The worktree was left clean and no patch artifact was recorded, consistent with the failed diff being discarded/reversed by the runner.
- This is a safe failure, not an improvement.

Opus diagnosed the docs failure as a prompt/checker mismatch:

- The prompt tells the model to use repo-relative paths like `docs/index.md` and `README.md`.
- `markdown_links._resolve_target` resolves non-absolute markdown links relative to the current markdown file’s parent.
- From `docs/runbooks/index.md`, `docs/index.md` resolves to `docs/runbooks/docs/index.md`, and `README.md` resolves to `docs/runbooks/README.md`.
- Both are missing, so the gate rejects.

Verified code:

- `arena/markdown_links.py:186-190` resolves non-absolute links relative to `markdown_path.parent`.

This must be fixed before trusting nested docs targets such as `docs/runbooks/index.md` or `docs/agent-backlog.md`.

## 2. What Opus found in the proposer code

Opus inspection artifact:

- Raw: `<build-arena>/reports/2026-06-18-fmc-mcp-advisory-proposer-opus-inspection.json`
- Normalized: `<build-arena>/reports/2026-06-18-fmc-mcp-advisory-proposer-opus-inspection.normalized.json`

Main code findings:

### 2.1 Architecture advisory is excluded by boundary logic

Evidence:

- `arena/proposal_domains.py:359-367` `_is_model_level_finding`
- `arena/proposal_domains.py:362` requires `boundary == "safe_to_patch_docs_only"`
- `arena/project_intake_scorecard.py:451-462` emits `architecture.open-questions-or-gaps` with boundary `advisory_only`

Effect:

`ModelLevelDomain` is already the domain intended to handle no-file model-level findings by targeting `docs/agent-backlog.md`, but it refuses the architecture advisory finding before it reaches the `architecture.*` branch.

Required change:

Allow architecture advisory findings to route into a model/advisory domain. Do not rely on a filesystem evidence path for these.

### 2.2 Project Model evidence paths are stripped before target selection

Evidence:

- `arena/proposal_domains.py:311-323` `_target_paths_for_finding`
- `arena/proposal_domains.py:317` filters paths starting with `iterationReadiness`

Effect:

Findings backed by `iterationReadiness.*` or `snapshot.verification_gaps` have no concrete target path. This is correct for preventing fabricated source paths, but it means advisory findings need policy-based target synthesis, not path-derived targets.

Required change:

Create an advisory/model-level domain that synthesizes a stable target, e.g. `docs/agent-backlog.md`, and uses the actual gap/question content for grounding.

### 2.3 Advisory content is not plumbed into the proposer

Evidence:

- `arena/proposal_planner.py:141-149` passes only `quality_gate_commands` into `DomainContext.extras`
- `arena/proposal_domains.py:282-300` `ModelLevelDomain` uses finding id/title, not the actual open questions or verification gaps

Effect:

Even if `ModelLevelDomain` fires, the model would only see generic text like “Project Model contains open questions or verification gaps,” not the actual gap list.

Required change:

Pass actual `openQuestions` and `verification_gaps` into `DomainContext.extras`, and make advisory candidates enumerate them.

### 2.4 Markdown gate is too weak for advisory backlog work

Evidence:

- `arena/proposal_domains.py:332-344` `_markdown_success_contract`
- Gate today is mostly file non-empty + local markdown links resolve + optional source references

Effect:

A generic `docs/agent-backlog.md` could pass while ignoring the actual architecture gaps.

Required change:

Add a content-aware backlog gate. It should fail unless every expected open question / verification gap id or normalized text appears as a structured task entry.

### 2.5 Quality gates present is context, not a candidate

Evidence:

- `arena/proposal_planner.py:358-366` `_quality_gate_commands`
- Those commands already flow into planner context and are reused by component verification

Effect:

`verification.quality-gates.present` should not be proposed as a file change. It should be labeled `consumed_as_context`, not `no_single_file_target`.

Required change:

Improve skip/route reasons:

- `consumed_as_context` for positive informational findings like gates-present;
- `advisory_backlogged` for architecture advisory converted to a backlog candidate;
- `no_single_file_target` only for truly unhandled findings.

## 3. External patterns that solve this class of problem

### 3.1 ATAM / lightweight architecture evaluation — best fit for architecture advisory findings

Source:

- SEI ATAM fact sheet: `https://www.sei.cmu.edu/library/architecture-tradeoff-analysis-method-atam/`
- SEI ATAM method report: `https://www.sei.cmu.edu/library/atam-method-for-architecture-evaluation/`
- SEI ATAM PDF fact sheet: `https://www.sei.cmu.edu/documents/6513/Architecture_Tradeoff_Analysis_Method_ATAM_Fact_Sheet.pdf`

Relevant facts:

- ATAM evaluates architecture relative to quality attribute goals.
- It maps business drivers and architecture to scenarios.
- It identifies risks, non-risks, sensitivity points, and tradeoff points.
- It synthesizes risks into risk themes that threaten business drivers.
- Lightweight evaluation can focus on what changed or on previously unexamined architecture portions.

How it maps to Build Arena:

- Project Model `openQuestions` and `verification_gaps` are basically raw ATAM-style risk/scenario material.
- Proposer should convert each architecture advisory finding into scenario/risk tasks:
  - quality attribute affected;
  - scenario or question;
  - affected component/contract;
  - proposed mitigation type: ADR, test/fitness function, code investigation, or blocked owner decision;
  - verification gate.

What it solves:

- Prevents “architecture gap” from becoming vague prose.
- Gives proposer a formal transformation: diagnostic -> scenario/risk -> mitigation candidate.

Recommended use:

Use ATAM-lite as the advisory architecture domain’s internal model.

### 3.2 Evolutionary Architecture / fitness functions — best fit for turning architecture concerns into gates

Sources:

- Neal Ford page: `https://nealford.com/books/buildingevolutionaryarchitectures.html`
- Thoughtworks second edition page: `https://www.thoughtworks.com/insights/books/building-evolutionaryarchitectures-second-edition`

Relevant facts:

- An architectural fitness function is an objective integrity assessment of an architectural characteristic.
- Fitness functions can be tests, metrics, monitoring, logging, automated checks, or deployment pipeline verification.
- The method is explicitly about guided incremental architectural change across multiple dimensions.

How it maps to Build Arena:

- `architecture.open-questions-or-gaps` should not only create a note. For any gap that can be mechanically checked, proposer should generate a fitness-function candidate.
- Examples:
  - dependency direction rule;
  - “no cyclic imports” check;
  - public API contract check;
  - command-level smoke test;
  - schema/protocol contract validation;
  - rollback/runbook completeness check.

What it solves:

- Gives advisory architecture findings a load-bearing gate.
- Prevents documentation-only “fixes” from masquerading as architecture improvement.

Recommended use:

Every advisory architecture candidate should try this order:

1. Can this become a fitness function / test / metric?
2. If yes, propose that.
3. If no, create an ADR/backlog item with explicit blocked reason.

### 3.3 ArchUnit-style architecture tests — concrete project/tool precedent

Sources:

- ArchUnit home: `https://www.archunit.org/`
- ArchUnit user guide: `https://www.archunit.org/userguide/html/000_Index.html`

Relevant facts:

- ArchUnit checks dependencies between packages/classes, layers/slices, cyclic dependencies, naming, annotations, PlantUML conformance, and architecture metrics.
- It runs architecture rules as ordinary unit tests.

How it maps to Build Arena:

- Build Arena should implement language-appropriate architecture gates, not necessarily Java ArchUnit itself.
- For Python/fmc-mcp, equivalents could be:
  - import graph rule checks;
  - module-boundary checks;
  - no dependency from tools/resources back into server if that boundary matters;
  - public API surface preservation;
  - contract tests over MCP tools/resources.

What it solves:

- Makes architecture advisory findings mechanically verifiable.
- Gives the proposer a target: add or update an architecture rule/test, not just write prose.

Recommended use:

Treat ArchUnit as the reference shape for Build Arena’s future `architecture_fitness_gate`.

### 3.4 Test gap analysis / requirements traceability — best fit for verification advisory findings

Sources:

- SeaLights test gaps: `https://docs.sealights.io/knowledgebase/guides/quality-improvement/quality-improvement-solution-overview/release-quality-improvement-guide/step-5-analyze-test-gaps`
- Qodo test gap analysis: `https://www.qodo.ai/blog/gap-analysis-in-software-testing/`

Relevant facts:

- Test gap analysis compares current testing state to desired testing state.
- It identifies untested code changes or critical gaps.
- The action is to create or modify tests to cover critical areas.
- Qodo frames it as: define desired state, collect data, analyze gaps, prioritize, define action plan.

How it maps to Build Arena:

- `verification.quality-gates.present` is not a gap; it is context.
- Actual verification gaps should become test-gap candidates:
  - component or contract affected;
  - current checks covering it;
  - missing behavioral scenario;
  - proposed test target;
  - quality gate commands to run.

What it solves:

- Separates “we have gates” from “we have meaningful coverage.”
- Turns weak coverage into focused test proposals.

Recommended use:

Add a `VerificationGapDomain` that consumes `snapshot.verification_gaps` and component risk data, then emits either:

- a focused test candidate when targetable;
- an advisory backlog item when not targetable.

### 3.5 ADR / RFC decision records — best fit when the advisory gap is a decision, not a code/test issue

Sources:

- ADR site: `https://adr.github.io/`
- Microsoft Azure Well-Architected ADR guidance: `https://learn.microsoft.com/en-us/azure/well-architected/architect-role/architecture-decision-record`

Relevant facts:

- An ADR captures one architecturally significant decision and its rationale.
- It should include context, alternatives considered/rejected, decision, consequences, status, and confidence.
- Microsoft says ADRs are append-only; if a decision changes, write a new record that supersedes the old one.
- Only architecturally significant requirements should get ADRs: decisions affecting structure, key quality attributes, or hard-to-reverse tradeoffs.

How it maps to Build Arena:

- Some architecture advisory findings are not immediately code-actionable.
- Proposer should classify those as decision-record candidates rather than forcing a code patch.
- Gate should verify template completeness and source references, not just file existence.

What it solves:

- Provides a legitimate non-code output for architecture uncertainty.
- Avoids fabricating implementation when the real work is to capture a decision boundary.

Recommended use:

Use ADR when Project Model gaps are about unresolved choices, boundaries, or tradeoffs.

### 3.6 Agentless / SWE-bench-style localization → repair → validation — best fit for proposer workflow shape

Sources:

- Agentless repo: `https://github.com/OpenAutoCoder/Agentless`
- Agentless paper page: `https://huggingface.co/papers/2407.01489`

Relevant facts:

- Agentless uses a structured workflow: localization, repair, patch validation.
- Localization narrows from files to classes/functions to fine-grained edit locations.
- Repair samples candidate patches in diff format.
- Validation filters/ranks patches using tests and syntax checks.

How it maps to Build Arena:

- Current Build Arena proposer jumps from finding -> single target -> one diff.
- Advisory architecture/verification findings need a localization stage first.
- Candidate generation should produce multiple candidate types, then validation/ranking should choose.

What it solves:

- Avoids forcing a no-target advisory finding into a fake single file.
- Gives Build Arena a known effective decomposition: localize -> propose -> validate.

Recommended use:

Use Agentless-style staging inside each domain, especially architecture/verification:

1. localize affected component/contract/files;
2. choose candidate class: test, architecture gate, ADR, backlog;
3. generate patch;
4. validate with domain gate;
5. rank remaining candidates.

## 4. Which combination solves Build Arena’s requirements

No single external method solves this alone. The right combination is:

1. ATAM-lite for advisory architecture interpretation
   - Convert open questions/gaps into quality-attribute scenarios, risks, sensitivity/tradeoff points, and mitigation classes.

2. Fitness functions / architecture tests for mechanical verification
   - Prefer turning architecture concerns into automated checks when possible.

3. Test gap analysis for verification gaps
   - Convert weak coverage into focused test candidates or explicit blocked backlog items.

4. ADR/RFC records for non-code decisions
   - Use when the correct output is a durable decision, not a test/code patch.

5. Agentless-style localization/repair/validation for proposer mechanics
   - Add a localization stage before choosing target files; generate multiple candidate options; validate before ranking.

This combination fits Build Arena’s actual needs:

- No fabricated target paths.
- Advisory findings become candidate-producing domains.
- Positive informational findings become context, not bogus proposals.
- Every proposal carries a load-bearing gate.
- Architecture/code/docs/test/process candidates can be ranked across domains.

## 5. Required Build Arena changes

### Immediate prerequisite: fix nested Markdown links

Before advisory backlog proposals, fix the docs gate mismatch.

Options:

1. Allow repo-root resolution fallback for repo-relative-looking links.
2. Require root-absolute links like `/README.md` and `/docs/index.md`.
3. Put generated advisory backlog at repo root.

Best path: support root-absolute or repo-root fallback in `markdown_links`, then adjust prompt rules accordingly. Add regression for the exact failure:

- target: `docs/runbooks/index.md`
- links: `docs/index.md`, `README.md`
- current behavior: resolves under `docs/runbooks/`
- desired behavior must be explicit and tested.

### Minimal architecture advisory slice

1. Change `ModelLevelDomain` or add `AdvisoryDomain` so `architecture.*` + `advisory_only` can produce a candidate.
2. Target `docs/agent-backlog.md` for now.
3. Plumb actual open question / verification gap content into `DomainContext.extras`.
4. Generate candidate intent from the real item list, not just finding title.
5. Add `arena.backlog_gate`:
   - target file exists and non-empty;
   - markdown links resolve;
   - every expected advisory item appears as a task entry;
   - no fabricated source links.
6. Label quality-gates-present as `consumed_as_context`, not skipped.

This would make current advisory architecture findings usable without pretending they are code changes.

### Proper durable architecture

Add explicit domains:

- `AdvisoryArchitectureDomain`
  - ATAM-lite classification;
  - outputs ADR/backlog/fitness-function candidates.

- `VerificationGapDomain`
  - test gap analysis;
  - outputs focused test or gate candidates.

- `ArchitectureFitnessDomain`
  - architecture rule/fitness function proposals;
  - gates with import graph / contract / dependency checks.

- `DecisionRecordDomain`
  - ADR candidates;
  - gate verifies ADR template completeness, alternatives, consequences, source refs.

- `ContextOnlyDomain`
  - consumes informational positives like `verification.quality-gates.present` and records `consumed_as_context`.

Then update the ranker/planner to rank candidates, not merely findings, because one advisory finding may produce several candidate types.

## 6. Recommended next implementation slice

Do not jump straight to a broad architecture-proposer rebuild.

Do this sequence:

1. Fix nested docs link semantics and add the exact regression from this run.
2. Add explicit route accounting: `consumed_as_context`, `advisory_backlogged`, `no_single_file_target`.
3. Add `AdvisoryDomain` for `architecture.open-questions-or-gaps` only.
4. Plumb actual `openQuestions` / `verification_gaps` into the domain context.
5. Add `arena.backlog_gate` that rejects boilerplate/no-op backlog output.
6. Rerun the docs-addressed simulation and prove:
   - `verification.quality-gates.present` is consumed as context;
   - `architecture.open-questions-or-gaps` produces `docs/agent-backlog.md` candidate;
   - a no-op backlog fails;
   - a complete backlog passes.
7. Only after that, add test/fitness-function proposal domains for code-facing verification gaps.

## 7. Final verdict

Current proposer can attempt docs candidates, but the live run shows it cannot currently succeed on even the top docs candidate when the target is nested under `docs/`; the nested-doc link contract is broken and must be fixed.

Current proposer is not ready to solve advisory architecture/verification findings.

The good news: the required path is clear and not speculative. Use ATAM-lite to interpret architecture advisories, fitness functions/architecture tests to make them verifiable, test gap analysis for verification findings, ADRs for true decisions, and Agentless-style localization/repair/validation to keep proposer mechanics disciplined.
