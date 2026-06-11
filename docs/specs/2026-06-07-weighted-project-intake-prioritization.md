# Weighted Project Intake and Self-Improvement Prioritization Specification

Date: 2026-06-07
Status: backlog specification; not implemented; Opus reviewed with accepted changes incorporated
Audience: Build Arena operators, future autonomous runners, Hermes agents, project maintainers
Canonical backlog title: Add weighted project-intake scorecard for AI-usable repo housekeeping and improvement prioritization
Canonical backlog issue: https://github.com/leonbreukelman/build-arena/issues/6

Review status: `claude-opus-4-8` reviewed this spec, the companion Hermes skill, and `AGENTS.md` on 2026-06-07 with verdict `ACCEPT_WITH_CHANGES`. The accepted fixes are incorporated here: decision-history weighting, canonical title unification, source links, first-slice scope clarification, and lightweight-mode guidance.

## 0. Executive summary

Build Arena needs a project-intake scorecard that ranks which improvement should be done first when a new or unfamiliar repository is consumed.

The central thesis is:

> Documentation and project knowledge are maintenance infrastructure. For a new or unfamiliar project, weak docs, stale architecture notes, missing setup instructions, or absent agent guidance can be more dangerous to autonomous improvement than ordinary low-priority code cleanup.

The scorecard should therefore make documentation, architecture/spec clarity, verification reproducibility, and AI-agent usability first-class scoring dimensions before an autonomous loop chooses implementation work.

This is a backlog item, not a completed feature. It should become a Build Arena evaluation/prioritization layer that runs after project decomposition and before hypothesis selection or autonomous worktree patching.

## 1. Grounding and source inputs

This specification is grounded in:

- Leon's stated operating preference: every project he works on with Hermes should get an additional weighted project-intake scorecard that can be tuned by weighting, so downstream autonomous improvement services choose better first work.
- The prior Build Arena/FMC-MCP decomposition-readiness discussion: FMC-MCP remains a good first small pilot repository for real decomposition review, but a prior fixture-mode smoke showed model-quality gaps rather than an accepted action-ready decomposition.
- The research summary captured in the current conversation.
- Build Arena repository rules in `AGENTS.md`, especially anti-fabrication and filesystem/git-grounding requirements.
- Existing Build Arena direction: Project Model v1 is the primary enriched artifact, but broad autonomous live loops are still blocked until readiness blockers close.

External research signals used as design input:

- GitHub community profile guidance: recommended repository health files include `README`, `CODE_OF_CONDUCT`, `LICENSE`, `CONTRIBUTING`, `SECURITY`, issue templates, and pull request templates. Source: <https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/about-community-profiles-for-public-repositories>.
- Diataxis documentation framework: documentation should satisfy four distinct user needs: tutorials, how-to guides, reference, and explanation. Source: <https://diataxis.fr/>.
- DORA documentation-quality capability: internal documentation quality is a fundamental software-development capability linked to organizational performance; quality attributes include clarity, findability, and reliability. Source: <https://dora.dev/capabilities/documentation-quality/>.
- DORA delivery metrics: change lead time, deployment frequency, failed deployment recovery time, and change failure rate are useful signals for delivery throughput and stability. Source: <https://dora.dev/guides/dora-metrics/>.
- OpenSSF Scorecard: security/repository-health checks include branch protection, CI tests, code review, dependency update tooling, maintained status, SAST, security policy, token permissions, dangerous workflows, and known vulnerabilities. Sources: <https://scorecard.dev/> and <https://github.com/ossf/scorecard/blob/main/docs/checks.md>.
- OpenAI Codex `AGENTS.md`, Claude Code `CLAUDE.md`, and GitHub Copilot repository instructions: AI coding agents benefit from durable repo-local instructions that describe project layout, commands, engineering conventions, constraints, and definition of done. Sources: <https://developers.openai.com/codex/guides/agents-md>, <https://docs.anthropic.com/en/docs/claude-code/memory>, and <https://docs.github.com/en/copilot/customizing-copilot/adding-repository-custom-instructions-for-github-copilot>.
- Architecture Decision Records / MADR: architecture-significant decisions should be captured as concise markdown records with context, decision, rationale, and consequences. Source: <https://adr.github.io/madr/>.
- Google developer documentation style guidance: project-specific style and clear, consistent technical documentation improve developer usability. Source: <https://developers.google.com/style>.

## 2. Problem statement

When a new project is consumed, autonomous agents often ask the wrong first question:

> What code change should I make?

For reliable maintenance, the better first question is:

> What weakness most reduces future safe iteration?

A project can have passing tests and still be unsafe or inefficient for autonomous improvement if:

- the README is missing or misleading;
- setup/test/build commands are undocumented or stale;
- architecture boundaries are implicit;
- specs and current implementation disagree;
- generated/protected surfaces are not marked;
- no ADRs explain important constraints;
- security and contribution policies are absent;
- issue/backlog state is disconnected from docs;
- agent instructions are missing, over-specific, or stale;
- there is no provenance-backed project model linking docs, code, tests, contracts, and verification.

These are not cosmetic issues. They directly determine whether an AI agent can understand the project, make bounded changes, verify them, and explain them to Leon without fabricating or over-asking.

## 3. Design principle

The scorecard must prioritize work that increases future safe iteration.

In plain language:

> Prefer small improvements that make every future improvement clearer, safer, easier to verify, and easier for Leon to audit.

The scorecard should not replace decomposition, verification, security scanning, tests, or owner judgment. It should sit between project understanding and work selection.

```text
repo/git/filesystem truth
-> decomposition / Project Model v1
-> weighted project-intake scorecard
-> ranked maintenance-risk register
-> weighted improvement backlog
-> selected first improvement or blocker
-> implementation/review loop only when authorized and gates pass
```

## 4. Canonical score dimensions

Each finding must be evidence-backed by paths, commands, issue URLs, or explicit absence checks. Missing evidence is itself a finding.

### 4.1 Documentation and project knowledge

Purpose: can a fresh human or agent understand what the project is and how to use it?

Score surfaces:

- README exists, is current, and describes purpose, status, setup, commands, and links.
- `docs/index.md` or equivalent navigation exists.
- Product/spec docs exist and match implementation status.
- Glossary/domain terms are defined when the domain is non-obvious.
- Current-state/status docs are dated and do not conflict with active orientation docs.
- GitHub Wiki, if used, is generated/mirrored from repo docs or explicitly marked non-authoritative.

High-risk findings:

- README makes readiness/deployment/autonomy claims contradicted by tests or status docs.
- Historical artifacts are presented as current truth.
- No clear entrypoint tells an agent where to start.

### 4.2 AI-agent usability

Purpose: can an AI agent safely work in the repo without repeated human steering?

Score surfaces:

- `AGENTS.md`, `CLAUDE.md`, `.github/copilot-instructions.md`, or equivalent exists where appropriate.
- Instructions name repo layout, commands, boundaries, generated/protected paths, and definition of done.
- Instructions distinguish read-only status checks from mutation authorization.
- Instructions are concise, durable, and not full of stale task progress.
- Agent instructions link to scorecard/spec/runbook docs.

High-risk findings:

- Agent instructions omit destructive/protected path boundaries.
- Agent instructions duplicate stale implementation status from older docs.
- Instructions contain secrets, private credentials, or brittle one-off session details.

### 4.3 Reproducible verification

Purpose: can changes be proven locally and in CI?

Score surfaces:

- Setup command is documented.
- Test, lint, typecheck, build, smoke, and generated-artifact commands are documented.
- CI exists and maps to local commands.
- Expected failure modes and blocked commands are explicit.
- Fixture data or smoke inputs exist for meaningful verification.

High-risk findings:

- The project cannot run tests from a clean checkout using documented commands.
- CI exists but local docs point to different commands.
- A feature is marked ready without a meaningful smoke or regression path.

### 4.4 Architecture, specs, and contracts

Purpose: can the system be changed without guessing boundaries?

Score surfaces:

- Architecture overview exists.
- Component boundaries are named.
- APIs, schemas, data contracts, and generated artifacts are documented.
- Ownership of source vs generated/runtime artifacts is explicit.
- Tests or gates map to important contracts.
- Project Model v1 components/contracts/checks reflect the real repo.

High-risk findings:

- Components are only path buckets, not responsibility-bearing units.
- Contracts exist in code but are undocumented.
- Generated/protected surfaces can be accidentally edited by an autonomous runner.

### 4.5 Decision history

Purpose: can future agents understand why the project is built this way?

Score surfaces:

- ADRs or decision records exist for architecture-significant choices.
- Major rejected alternatives and constraints are recorded.
- Migration notes and status transitions are dated.
- Previous incidents/RCAs are linked from current docs when still relevant.

High-risk findings:

- Important constraints exist only in conversation history.
- A future agent could easily reverse a deliberate decision because no rationale is visible in repo docs.

### 4.6 Backlog and change governance

Purpose: can work be selected, reviewed, and tracked consistently?

Score surfaces:

- Issue/backlog state exists and is linked from docs.
- Issue templates and PR templates exist where useful.
- CONTRIBUTING / definition-of-done guidance exists.
- Labels/project fields distinguish ready, blocked, verified-local, owner-review, done.
- Backlog items name acceptance criteria and verification commands.

High-risk findings:

- Work is chosen from chat memory instead of durable backlog state.
- Issues are too vague for a fresh agent to execute safely.
- Human-gated work is mixed with autonomous-ready work.

### 4.7 Security and supply-chain hygiene

Purpose: can the project be maintained without preventable security risk?

Score surfaces:

- LICENSE and SECURITY policy exist where appropriate.
- Secret scanning / dependency scanning / SAST / OpenSSF-style checks are present or intentionally deferred.
- Branch protection and review policy are documented for shared repos.
- Workflow token permissions are least-privilege.
- Dependency update tooling exists or is intentionally deferred.

High-risk findings:

- Secrets are stored in source or docs.
- GitHub Actions use broad token permissions unnecessarily.
- Known vulnerabilities or dangerous workflows are unresolved without explicit acceptance.

### 4.8 Operations, release, and rollback

Purpose: can deployed or long-running systems be operated and recovered?

Score surfaces:

- Runbooks exist for start/stop/deploy/rollback/troubleshooting.
- Live/provider/spend/destructive boundaries are explicit.
- Observability and incident evidence are documented when applicable.
- DORA-style delivery/recovery metrics can be approximated or tracked.

High-risk findings:

- Deployment is documented but rollback is absent.
- Live provider calls are possible but not gated.
- Readiness claims do not name known blockers.

## 5. Default weighting profiles

Weights must be configurable. A finding's priority should be calculated from both dimension weight and local evidence severity.

### 5.1 New or unfamiliar project profile

Use when first consuming a repo, resuming an old project, or evaluating a candidate for autonomous improvement.

| Dimension | Weight |
|---|---:|
| Documentation and project knowledge | 28 |
| Reproducible verification | 20 |
| Architecture, specs, and contracts | 14 |
| AI-agent usability | 14 |
| Security and supply-chain hygiene | 9 |
| Decision history | 7 |
| Backlog and change governance | 4 |
| Operations, release, and rollback | 4 |

Rationale: the first job is to make the project understandable, navigable, and verifiable.

### 5.2 Active development project profile

| Dimension | Weight |
|---|---:|
| Reproducible verification | 24 |
| Documentation and project knowledge | 19 |
| Architecture, specs, and contracts | 18 |
| Security and supply-chain hygiene | 10 |
| AI-agent usability | 9 |
| Decision history | 8 |
| Backlog and change governance | 8 |
| Operations, release, and rollback | 4 |

Rationale: a project already under active work needs high confidence that changes can land safely.

### 5.3 Production or external-user project profile

| Dimension | Weight |
|---|---:|
| Reproducible verification | 24 |
| Security and supply-chain hygiene | 20 |
| Operations, release, and rollback | 19 |
| Documentation and project knowledge | 14 |
| Architecture, specs, and contracts | 9 |
| Decision history | 5 |
| Backlog and change governance | 5 |
| AI-agent usability | 4 |

Rationale: live users raise the cost of unsafe change, weak rollback, and security gaps.

### 5.4 Documentation-first owner override

Use when Leon explicitly asks to improve clarity, consistency, specs, architecture, wiki, README, or agent usability.

| Dimension | Weight |
|---|---:|
| Documentation and project knowledge | 33 |
| AI-agent usability | 18 |
| Architecture, specs, and contracts | 18 |
| Reproducible verification | 14 |
| Decision history | 10 |
| Backlog and change governance | 4 |
| Security and supply-chain hygiene | 2 |
| Operations, release, and rollback | 1 |

Rationale: documentation is the work product, but it must remain tied to architecture and verification truth.

## 6. Finding model

Each scorecard finding should be represented with enough structure for humans and agents.

```json
{
  "id": "doc-readme-status-conflict",
  "dimension": "documentation_project_knowledge",
  "title": "README readiness claim conflicts with readiness register",
  "severity": "high",
  "confidence": "high",
  "evidence": [
    {"kind": "file", "path": "README.md", "line": 42, "quote": "..."},
    {"kind": "file", "path": "docs/verification/pre-live-readiness-register.json", "json_pointer": "/status"}
  ],
  "why_it_matters": "A future agent may start live autonomous loops from a false readiness claim.",
  "recommended_action": "Patch active orientation docs to say broad live autonomy remains blocked.",
  "verification": ["uv run pytest tests/test_project_status_docs.py -q"],
  "autonomy_boundary": "safe_to_patch_docs_only",
  "estimated_effort": "small",
  "impact_on_future_iteration": 5,
  "risk_reduction": 5,
  "verification_gain": 3,
  "doc_knowledge_gain": 5
}
```

## 7. Priority formula

The implementation may tune exact math, but the first version should be explainable.

Recommended formula:

```text
priority_score =
  dimension_weight
  * severity_multiplier
  * confidence_multiplier
  * (impact_on_future_iteration + risk_reduction + verification_gain + doc_knowledge_gain)
  / effort_multiplier
```

Plain-English interpretation:

> The top item should be a grounded, high-confidence, low-to-medium effort improvement that reduces future misunderstanding or unsafe iteration more than it merely tidies code.

Suggested scales:

- severity: low=1, medium=2, high=3, critical=4
- confidence: low=0.5, medium=0.75, high=1.0
- impact/risk/verification/doc gain: 1-5 each
- effort: small=1, medium=2, large=3, unknown=4

## 8. Full intake-run vision and first-slice outputs

A mature project intake run should produce:

1. Repo Health Model
   - Dimensions, scores, findings, evidence, and risk summary.
2. Documentation Knowledge Graph
   - Docs, specs, ADRs, runbooks, README, AGENTS.md, issue links, and source/provenance links.
3. AI Usability Score
   - Whether a fresh agent can safely understand, edit, verify, and report on the repo.
4. Maintenance Risk Register
   - High-risk gaps that should block autonomous work or require owner review.
5. Weighted Improvement Backlog
   - Ranked candidate improvements with evidence and verification commands.
6. First Recommended Improvement
   - One concrete first task with a short proof of why it outranks alternatives.
7. Accepted Deferrals
   - Lower-ranked or intentionally deferred findings with rationale.
8. Machine-readable sidecar
   - JSON representation suitable for Project Model v1 sidecar consumption.

The first implementation slice is intentionally smaller: it only needs the machine-readable scorecard JSON, a concise markdown report, ranked findings, one first recommended improvement, and enough evidence links to verify why that recommendation outranks alternatives. The remaining artifacts above are the full product direction, not mandatory first-slice scope.

## 9. AI-usable documentation structure

For Leon's projects, the preferred durable project-knowledge structure is:

```text
README.md                         # human entrypoint and current status summary
AGENTS.md                         # agent operating rules, commands, boundaries, definition of done
docs/index.md                     # docs navigation / wiki source
docs/specs/                       # product and architecture specs
docs/adr/                         # architecture decision records
docs/runbooks/                    # operations, deployment, rollback, troubleshooting
docs/plans/                       # implementation plans and fresh-session handoffs
docs/verification/                # dated proof, reviews, RCA, readiness registers
docs/schemas/                     # machine-readable contracts and scorecard schemas
.github/ISSUE_TEMPLATE/           # backlog capture templates when GitHub is used
.github/PULL_REQUEST_TEMPLATE.md  # review and verification checklist when useful
```

GitHub Wiki guidance:

- Good use: generated or manually curated navigation layer for humans.
- Risky use: sole source of project truth, because it is weaker than docs-as-code for review, versioning, CI checks, and agent grounding.
- Preferred rule: canonical docs live in repo; wiki/docs site is generated, mirrored, or explicitly marked as non-authoritative.

## 10. Build Arena integration points

This scorecard should become part of Build Arena after Project Model v1 snapshot generation and before autonomous hypothesis selection.

Potential flow:

```text
arena.project_model_cli snapshot
-> Project Model v1 artifact
-> scorecard extractor over repo + v1 + docs + issue data
-> weighted findings
-> scorecard gate
-> ranked improvement backlog
-> dry-run hypothesis generation
```

Suggested CLI shape:

```bash
uv run python -m arena.project_intake_scorecard \
  --project /path/to/repo \
  --snapshot /path/to/project-model-v1.json \
  --profile new-project \
  --output docs/verification/<date>-<repo>-intake-scorecard.json
```

Suggested fixture pilot sequence:

1. FMC-MCP as the first small real repo.
2. Build Arena itself as the self-hosting repo.
3. Arena Calibration as a held-out related repo.
4. One unrelated held-out repo after the local projects pass.

## 11. Acceptance criteria for implementation

The first implementation slice is accepted only if it:

- Emits a machine-readable scorecard JSON and a concise markdown report.
- Supports at least the `new-project`, `active-development`, `production`, and `documentation-first` profiles.
- Reads real filesystem/git/doc state; does not invent files, symbols, commands, or repo health claims.
- Links every finding to evidence or records it as an absence finding with the checked path/pattern.
- Separates missing docs from stale/conflicting docs.
- Separates human docs from AI-agent instructions.
- Treats docs-as-code as canonical and GitHub Wiki as a projection unless configured otherwise.
- Produces a ranked list with at least one recommended first improvement and an explanation of why it outranks the next candidates.
- Provides deterministic tests for scoring math, missing-file detection, stale-doc conflict detection, profile weight selection, and JSON schema validity.
- Does not modify `scorer/`, `verifier/`, `schema/`, `.arena/scorer.lock.toml`, or `arena/generated/` unless a separate operator action explicitly changes schema/generated artifacts.
- Does not run live provider calls by default.

## 12. Non-goals for the first implementation slice

The first implementation slice should not:

- Auto-edit repos based on scorecard output.
- Auto-create issues in every target repo.
- Depend on live paid LLM calls.
- Require GitHub API access for local-only scoring.
- Treat scorecard output as permission to run broad autonomous loops.
- Replace Project Model v1 decomposition or deterministic gates.
- Treat a single aggregate score as the only decision signal.

## 13. Backlog item body

Title:

> Add weighted project-intake scorecard for AI-usable repo housekeeping and improvement prioritization

Problem:

> Build Arena can decompose projects, but it still needs a weighted project-intake layer that decides which repo weaknesses most block reliable future iteration. Documentation, architecture/spec clarity, verification reproducibility, AI-agent instructions, security hygiene, and backlog governance should be scored before autonomous improvement work is selected.

Acceptance criteria:

- Add a scorecard model and CLI/report path for project-intake assessment.
- Provide configurable weighting profiles.
- Use docs/code/git/issue evidence and absence checks.
- Produce ranked improvement candidates and one first recommended improvement.
- Pilot on `/home/leonb/projects/fmc-mcp` before using it on broad autonomous Build Arena loops.
- Keep all live/provider/spend/autonomous patching gated.

## 14. Open questions for later implementation

These are implementation questions, not blockers for saving the spec:

1. Whether the scorecard schema should live under existing `schema/arena.yaml` or start as a separate JSON schema sidecar first.
2. Whether GitHub issue/project data should be optional input or a separate enrichment phase.
3. How much of stale-doc detection should be deterministic string/status checks versus LLM-assisted review.
4. How scorecard findings should feed Project Model v1 gates without overstating their authority.
5. Which minimum score should block autonomous patching versus merely warn.

Default answers for first slice:

- Start with a separate JSON schema sidecar to avoid early schema churn.
- Make GitHub data optional.
- Use deterministic checks first; add LLM review later.
- Treat scorecard findings as advisory/blocking by severity, not as proof of correctness.
- Block autonomous patching only on critical/high-confidence findings that affect verification, safety, or target understanding.

## 15. Review and provenance

A read-only Opus/Claude Code review was completed and saved under `docs/verification/2026-06-07-weighted-project-intake-prioritization-opus-review.md`.

Reviewer provenance:

- Reviewer: Claude Code
- Model: `claude-opus-4-8`
- Opus confirmed: yes
- Verdict: `ACCEPT_WITH_CHANGES`
- Cost reported by Claude Code: USD 0.411193

Accepted critique incorporated:

- Added `Decision history` to every weight profile and to `AGENTS.md` scorecard dimensions.
- Unified the canonical backlog title.
- Added source links for external frameworks and repo-health guidance.
- Reframed required outputs as full product vision plus smaller first implementation slice.
- Added lightweight-mode guidance to `AGENTS.md` and tightened the skill trigger wording.

The review also found no critical blockers and confirmed that the artifacts do not overclaim implementation, do not weaken Build Arena readiness boundaries, and keep anti-fabrication/protected-path rules intact.
