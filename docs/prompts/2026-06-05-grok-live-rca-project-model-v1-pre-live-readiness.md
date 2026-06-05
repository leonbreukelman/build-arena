# Fresh Hermes Session Prompt — Grok Live RCA, Project Model v1, and Pre-Live Readiness

## Direct goal

Investigate and fix the loose ends before any live Build Arena autonomous run. The primary suspicious issue is that the AI-first decomposer evidence says "Live Grok decomposition remains blocked by CLI/tool-loop/turn-limit behavior," but Leon expected the decomposer to use the already-working Grok/xAI API path rather than Grok Build CLI/agent mode. Treat this as a possible regression or wrong integration decision until proven otherwise.

The session must produce a verified, committed state that either:

1. fixes the Grok live decomposition path and resolves the pre-live readiness blockers; or
2. documents a true blocker with exact evidence, failing command, root cause, and the smallest next action.

Do not run a full live Build Arena autonomous improvement loop. The target is pre-live readiness and bounded live-model smoke testing only.

## Repository and related projects

Primary repository:

- `/home/leonb/projects/build-arena`

Related repositories to discover and inspect rather than assume:

- Elenchus Core, likely under `/home/leonb/projects/elenchus-core`
- Arena Calibration, likely under `/home/leonb/projects/arena-calibration`
- FMC-MCP pilot repo, likely under `/home/leonb/projects/fmc-mcp`
- Held-out pilot repo, previously `/home/leonb/projects/leonbreukelman-engineer`

If a related repo path differs, identify the canonical git repo by directory name, remote, README, and git status. Do not ask Leon unless no safe canonical candidate can be determined.

## Mandatory skills / operating mode

Before acting, load and follow these skills if available:

- `systematic-debugging`
- `test-driven-development`
- `writing-plans`
- `subagent-driven-development` if delegating implementation/review
- `hermes-provider-integration` or relevant Hermes/Grok provider skill if this becomes a Hermes provider/runtime issue

Use root-cause discipline:

- No fixes before reproducing and understanding the failure.
- Do not guess that Grok API is broken.
- Do not guess that Grok Build CLI was intentionally chosen.
- Inspect source, config, artifacts, and git history.
- Form explicit hypotheses and test them one at a time.

## Highest-priority safety and boundary rules

Follow `/home/leonb/projects/build-arena/AGENTS.md` exactly.

Important constraints:

- Never reason from imagined files. Read exact files before quoting or editing.
- Rebuild scanner/scorer/decomposer state from filesystem and git truth. Cached projections are not authoritative.
- Do not modify `scorer/`, `verifier/`, `schema/`, `.arena/scorer.lock.toml`, or `arena/generated/` unless you write a reviewed spec that explicitly justifies it and this work is clearly operator-directed rather than arena-generated.
- Do not hand-edit files under `arena/generated/`.
- Do not run a full Build Arena autonomous test run from the current Project Model v0/classified JSON.
- No public push, deploy, merge, or broad paid live API run without explicit Leon authorization.
- A small bounded Grok/xAI live smoke is expected if credentials and tooling are already configured locally, but stop if credentials are missing, if the path would require setting up a new paid account, or if spend would become non-routine.
- Redact any secrets in artifacts and final responses.

## Grounding artifacts to read first

In `/home/leonb/projects/build-arena`, inspect repo state first:

```bash
pwd
git rev-parse --show-toplevel
git status --short
git branch --show-current
git log --oneline -10
```

Then read these source-of-truth files before making claims:

- `AGENTS.md`
- `README.md`
- `docs/build-arena-specification.md`
- `docs/project-model-v0.md`
- `docs/schemas/project-model-v0.schema.json`
- `docs/specs/2026-06-04-ai-first-project-decomposer-spec.md`
- `docs/plans/2026-06-04-ai-first-project-decomposer-implementation-plan.md`
- `docs/verification/2026-06-04-ai-first-project-decomposer-final-report.md`
- `docs/verification/2026-06-04-ai-first-project-decomposer-pilot-opus-final-rereview.md`
- `arena/project_model_llm.py`
- `arena/project_decomposer_ai.py`
- `arena/project_model_cli.py`
- `arena/project_snapshot.py`
- `arena/project_model_gate.py`
- current tests touching the AI decomposer and project model CLI

Read Grok-specific artifacts:

- `docs/verification/2026-06-04-ai-first-project-decomposer-pilot-held-out/grok-decomposer-output.wrapper.json`
- `docs/verification/2026-06-04-ai-first-project-decomposer-pilot-held-out/grok-compact-decomposer-output.wrapper.json`
- `docs/verification/2026-06-04-ai-first-project-decomposer-pilot-held-out/grok-decomposer-prompt.md`
- `docs/verification/2026-06-04-ai-first-project-decomposer-pilot-held-out/grok-compact-decomposer-prompt.md`
- `docs/verification/2026-06-01-grok-build-arena-calibration-model-review.stderr`
- `docs/verification/2026-06-01-arena-calibration-decomposer-evaluation-report.md`

Known evidence from prior artifacts, to verify rather than blindly trust:

- The final report says live Grok decomposition was blocked by CLI/tool-loop/turn-limit behavior.
- The held-out Grok wrappers contain `"text": ""` and `"stopReason": "Cancelled"` while the internal `thought` shows Grok started working and began drafting/reading.
- Older Grok stderr showed unrelated MCP/Hugging Face auth warnings when path/full-artifact prompts caused Grok Build to attempt tool reads.
- A previous report says JSON-only Grok review worked better than prompts containing local file paths.

## Core questions to answer

Answer these with evidence from files, commands, artifacts, or git history:

1. Did the new AI-first decomposer actually use direct Grok/xAI API anywhere, or did it rely on Grok Build CLI/agent output wrappers?
2. If Grok Build CLI/agent was used, why was that decision made?
   - Was direct API support missing from the implementation?
   - Was the existing Hermes/xAI provider path not wired into this repo?
   - Was a CLI chosen for convenience during pilot evidence generation?
   - Was direct API blocked by credentials, model access, JSON-mode limitations, or token/context limits?
   - Did a regression replace a working API path with Grok Build CLI?
3. What exact command/tool produced the `stopReason: Cancelled` wrappers?
4. Can direct xAI/Grok API still be used successfully from this environment with the existing credentials/config?
5. What is the smallest reliable live-model decomposer path for Build Arena now?
   - direct xAI API
   - Hermes provider adapter
   - Grok ACP
   - Grok Build CLI with tools disabled
   - another leading model as a temporary provider
6. What code changes are needed so the decomposer uses the reliable path and records failure honestly?
7. What pre-live blockers remain besides Grok, and which are true blockers versus accepted dry-run-only limitations?

## Hypotheses to test

Treat these as hypotheses, not conclusions:

- H1: The decomposer implementation never implemented direct Grok/xAI API; pilot evidence was manually generated via Grok Build CLI wrappers.
- H2: Direct Grok/xAI API still works, but the decomposer CLI is not wired to it.
- H3: Direct Grok/xAI API support exists elsewhere in Hermes, but Build Arena used an unrelated CLI path because no adapter seam was implemented.
- H4: Grok Build CLI attempted tool use because prompts included local paths or because the CLI defaulted to agent mode; this caused MCP auth noise and/or turn-loop cancellation.
- H5: The `stopReason: Cancelled` output is a wrapper/protocol issue, not a model-quality issue.
- H6: A recent code change or ad hoc pilot script regressed from direct API use to Grok Build CLI.
- H7: The model output packet is too large for the selected Grok path, causing cancellation or non-final output.

## Required Phase 1 — RCA before fixing

Create an RCA artifact directory:

- `docs/verification/2026-06-05-grok-live-rca/`

Capture:

- repo state JSON or markdown,
- relevant command transcripts,
- search results for Grok/xAI/live provider references,
- source snippets or file references,
- artifact summaries,
- hypothesis table,
- final root-cause conclusion.

Required searches:

```bash
# Use ripgrep/search_files equivalent, not blind assumptions.
# Search Build Arena source/docs/tests for:
grok
xai
x-ai
XAI_API_KEY
GROK
LiveProjectModelLLM
ProjectModelLLM
llm-mode
recorded
wrapper
Cancelled
stopReason
claude
opus
sonnet
```

Also search the local Hermes repo/config only as needed to understand provider availability, but do not modify Hermes itself unless the root cause is proven to be there and Leon's requested outcome requires it.

Required RCA output:

- `docs/verification/2026-06-05-grok-live-rca/root-cause-report.md`
- `docs/verification/2026-06-05-grok-live-rca/hypotheses.json`
- command artifacts for every live smoke attempt, with secrets redacted

Do not patch implementation until the RCA report clearly identifies the failing boundary.

## Required Phase 2 — Minimal live Grok/xAI smoke

Run the smallest safe live smoke that can distinguish API availability from CLI/agent/tool failure.

Preferred order:

1. Inspect environment/config without printing secrets.
2. If direct xAI/Grok API credentials are present, run a tiny direct API JSON-only request that asks for a trivial JSON object.
3. If Hermes has a configured xAI/OpenAI-compatible provider, run the equivalent through the Hermes/provider path.
4. If using `grok` CLI, force non-agent/tool-disabled/JSON-only mode if supported; do not include local file paths.
5. Save every command, return code, stdout/stderr summary, and exact reason for failure/success.

The first smoke should not include a repository graph. It should prove the live model path returns valid JSON.

Then run a compact decomposer smoke on the smallest practical packet, preferably FMC-MCP or a minimized Build Arena packet:

- no local paths unless necessary,
- no tool use,
- strict JSON-only instruction,
- bounded token output,
- output parsed by Build Arena's recorded/live ingestion path,
- deterministic gate run on the returned output.

Acceptance:

- Empty text + `stopReason: Cancelled` is a failure, not success.
- Invalid JSON is a failure, not success.
- Tool-loop or MCP auth noise is a provider/tooling failure, not a model answer.
- A successful live smoke must produce valid JSON and record model id, prompt hash, output hash, return code/status, and gate result.

## Required Phase 3 — Fix the decomposer live-model path test-first

Depending on RCA, implement the smallest root-cause fix. Expected likely fixes include one or more of:

- add a direct xAI/Grok API adapter for `LiveProjectModelLLM`,
- add a Hermes-provider-backed adapter instead of shelling out to Grok Build,
- remove or quarantine Grok Build CLI/agent usage from delivery acceptance,
- enforce no-tool JSON-only mode for CLI calls if CLI remains supported,
- add hard failure handling for cancelled/empty/invalid model outputs,
- record live provider metadata and prompt/output hashes consistently,
- add compact packet generation to avoid unnecessary context/tool pressure.

Use TDD:

- Add tests that reproduce the current failure shape:
  - wrapper with `stopReason: Cancelled` and empty `text` is rejected;
  - wrapper with internal `thought` but no final text is rejected;
  - invalid JSON is rejected;
  - direct/API adapter success records model/prompt/output hashes;
  - recorded replay remains deterministic;
  - CI does not require live paid API calls.

Likely files to inspect/modify:

- `arena/project_model_llm.py`
- `arena/project_decomposer_ai.py`
- `arena/project_model_cli.py`
- `tests/test_project_decomposer_ai.py`
- `tests/test_project_model_cli_ai.py`
- new targeted tests if needed

Do not remove recorded/off/fixture modes; they are still needed for deterministic CI and replay. The fix is to make the live path real and reliable, not to make every test live.

## Required Phase 4 — Project Model v1 shared contract plan and implementation

Resolve the sidecar-vs-contract loose end. The current sidecar path is acceptable only as a candidate v1 proving ground. It should not remain a permanent shim.

Default target:

- Create/promote `project-model/v1` as the shared enriched contract across Build Arena, Elenchus Core, and Arena Calibration.
- Keep `project-model/v0` as legacy compatibility/projection.
- Do not force every rich artifact into `schema/arena.yaml` unless a reviewed spec justifies it. Prefer a project-model contract that the arena run-loop references by snapshot id/hash/manifest.

Create/update artifacts in Build Arena:

- `docs/specs/2026-06-05-project-model-v1-shared-contract-spec.md`
- `docs/plans/2026-06-05-project-model-v1-and-pre-live-readiness-plan.md`
- `docs/schemas/project-model-v1.schema.json` or a justified equivalent
- `docs/verification/2026-06-05-pre-live-readiness-register.json`

The v1 contract should include or reference:

- ProjectGraph
- GraphNode
- GraphEdge
- ProvenanceRef
- EncyclopediaPage / encyclopedia manifest references
- Component
- Contract
- CrossCuttingConcern
- ObservableCheck
- HeldOutProbe
- VerificationGap
- ProjectModelSnapshot
- GateReport
- git OID
- dirty-state fingerprint
- input hashes
- prompt hashes
- model IDs
- output hashes
- JSONL/SQLite/Markdown derived artifact strategy

Implement enough of v1 in this session to remove ambiguity about what is primary:

- Build Arena emits/validates v1 as primary for the AI decomposer path.
- v0 export remains available as compatibility projection.
- Tests prove v1 validates and v0 projection still works.

If full cross-repo implementation is too large for one session, complete the Build Arena v1 contract and save exact follow-up prompts for Elenchus Core and Arena Calibration. Do not pretend cross-repo work is done if it is not.

## Required Phase 5 — Elenchus Core v1 consumption

Inspect Elenchus Core current v0 API/docs/tests. Determine the smallest safe v1 consumer path.

Expected work:

- Add or plan a v1 adapter/parser.
- Ensure F3/advisory review can inspect v1 provenance, contracts, probes, verification gaps, and gate reports.
- Keep v0 compatibility if existing consumers require it.
- Add tests for v1-specific wrong-target/fabricated-provenance/weak-probe cases.

If modifying Elenchus Core in this session, commit there separately after verification. If not modifying it, save a precise implementation prompt under Build Arena docs or the Elenchus repo docs and mark this as a pre-live blocker/partial.

## Required Phase 6 — Arena Calibration v1 fixtures/evaluator

Inspect Arena Calibration current fixtures and project-model-v0 usage.

Expected v1 calibration fixture classes:

- valid rich snapshot,
- fluent file-bucket fake,
- fabricated provenance,
- missing import contract,
- reversed contract direction,
- self-referential contract,
- protected/generated ownership leak,
- weak held-out probe,
- verification gap mislabeled as success.

Expected tests:

- v1 schema validation,
- deterministic gate expected pass/fail,
- Elenchus advisory expected warning/failure mode,
- no Build Arena path overfit.

If modifying Arena Calibration in this session, commit there separately after verification. If not modifying it, save a precise implementation prompt and mark this as a pre-live blocker/partial.

## Required Phase 7 — Graph/indexing readiness decision

The current graph uses pragmatic AST/regex parsing. Decide what is necessary before live testing.

Investigate and document whether to add now or defer:

- Tree-sitter parser layer for JS/TS/Python/Markdown,
- ast-grep-style structural rules,
- Python import graph validation,
- optional SCIP/LSIF/CodeQL import,
- test-to-code and route/config edges.

Do not overbuild. The minimum acceptable pre-live outcome is a written decision plus tests/gates that prevent silent overclaiming. If a parser upgrade is necessary for the live target repos, implement it test-first.

## Required Phase 8 — Verification gap policy for live action

Build Arena snapshots can pass gates while carrying explicit verification gaps. That is honest, but live action needs policy.

Implement or specify gate policy so that:

- critical verification gaps block promotion,
- components with blocker gaps cannot be live-mutated,
- dry-run/read-only analysis can proceed with labeled gaps,
- protected/generated/scorer/verifier/schema surfaces remain blocked,
- gaps can become backlog items rather than hidden success.

Add tests if policy is implemented in Build Arena code.

## Required Phase 9 — Pre-live readiness gate and bounded live-test plan

Create a readiness gate that says whether Build Arena is allowed to proceed to live testing.

The readiness register should track each issue:

- id,
- title,
- severity,
- affected project,
- status,
- evidence path,
- proof command,
- blocks read-only live smoke?,
- blocks dry-run hypothesis generation?,
- blocks worktree-only patch cycle?,
- blocks promotion/merge?.

Default safe live-test ladder:

1. Read-only live decomposition on Build Arena.
2. Read-only live decomposition on FMC-MCP.
3. Read-only live decomposition on held-out repo.
4. Dry-run Build Arena hypothesis generation from v1 snapshot, no writes.
5. One-cycle worktree-only run, no promotion, no merge, no push.
6. Independent review of artifacts.
7. Only then consider broader live loop.

Do not execute steps 4-7 unless this session explicitly reaches the readiness criteria and Leon has authorized that mode. This prompt's default scope is to prepare and prove readiness, not to start the full live loop.

## Required independent review

Use Opus or the strongest available independent reviewer for read-only review after the RCA/fix/plan is drafted and again after implementation if substantial code changed.

Ask the reviewer to attack:

- whether Grok RCA actually identified root cause or just symptoms,
- whether direct API vs Grok Build CLI decision is now correct,
- whether v1 contract promotion removes the shim/debt concern,
- whether live tests could still pass while the decomposer is not AI-first,
- whether pre-live readiness blockers are honestly classified,
- whether deterministic tests can pass while live model behavior is still broken.

Save review artifacts under:

- `docs/verification/2026-06-05-grok-live-rca/opus-review.md`
- `docs/verification/2026-06-05-grok-live-rca/opus-review.json` if available

Patch valid critique before finalizing.

## Verification commands

At minimum, run and save command outputs:

Build Arena:

```bash
uv run pytest tests -q
uv run ruff check .
uv run pyright
git diff --check
```

Also run targeted tests added for Grok/live adapter failure handling.

Related repos:

- Discover each repo's test command from README/pyproject/package scripts.
- Run the closest safe local verification command for Elenchus Core and Arena Calibration if modified.
- Do not skip related repo verification if code changed there.

Artifact validation:

- Validate JSON artifacts parse.
- Validate `project-model-v1.schema.json` against produced v1 examples.
- Validate v0 projection still parses against `docs/schemas/project-model-v0.schema.json`.
- Validate no unresolved `TODO`, `FIXME`, `TBD`, or `PENDING` placeholders were added.
- Scan added lines for secret-like assignments before committing.

## Commit policy

Commit only after verification passes. Use separate commits per repo if multiple repos are modified.

Do not push, deploy, merge, or alter public state without explicit Leon authorization.

If the work cannot be completed in one session, commit only coherent verified slices and save exact follow-up prompts for unfinished slices.

## Final response requirements

Start with one of:

- `READY FOR BOUNDED LIVE TESTING`
- `NOT READY — BLOCKERS REMAIN`
- `BLOCKED — NEEDS OWNER ACTION`

Then list:

- root cause of Grok issue,
- whether the previous path used direct xAI/Grok API or Grok Build CLI/agent,
- why that decision happened, with evidence,
- what was fixed,
- which live smoke commands were run and results,
- v1 contract status,
- Elenchus Core status,
- Arena Calibration status,
- graph/indexing readiness decision,
- verification-gap policy status,
- readiness register path and status summary,
- artifact paths,
- verification commands and results,
- Opus/reviewer findings and how they were addressed,
- remaining risks/gaps,
- commits made,
- whether any push/deploy/merge/live autonomous run was performed.

Do not ask Leon for routine next steps. Escalate only true blockers: missing credentials/auth, destructive action, public push/deploy/merge, non-routine spend, or genuine product-owner ambiguity.
