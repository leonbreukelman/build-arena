# Build Arena progress timeline and production-readiness audit — 2026-06-14

## Executive status

Build Arena is ready to perform one bounded local fmc-mcp production run after explicit operator authorization in the narrow sense that the code now supports live Project Model decomposition plus live LLM diff proposal, guarded by explicit spend/promotion flags, `--live-max-calls`, a target `.arena/goal.toml`, patch gates, deterministic verification commands, source-reference documentation gates, and ff-only promotion.

It is not production-proven yet in the sense of a completed promotion. The last real live run was a verified xAI/Grok live dry-run, selected a documentation candidate, and did not promote anything. The code path for actual promotion exists and is test-covered, but no target baseline has been advanced by a live `--no-dry-run --allow-promotion` run.

Broad unattended production use across arbitrary target projects remains blocked. The readiness register still says `not_ready_blockers_remain` for broad autonomy while recording a scoped `boundedFmcMcpProductionRun` exception for this local CLI run.

## Current repository state verified in this audit

Build Arena:

- Path: `/home/leonb/projects/build-arena`
- Branch: `main`
- HEAD: `a071011fe3c5a969684eaf800ca2b15eae6d9da6` — `feat: enable live repo-goal loop execution`
- Remote state: `main...origin/main [ahead 1]`
- Dirty state after verification before this audit artifact was written: no uncommitted changes reported
- Dirty state after this audit/review work: this audit artifact and the Opus review artifact are untracked until deliberately packaged
- Important implication: the live-loop implementation is committed locally but not pushed to `origin/main`.

`fmc-mcp` target repo:

- Path: `/home/leonb/projects/fmc-mcp`
- Branch: `main`
- HEAD: `25f445806d5221f21d7ac675799db5c30499f1b7` — `chore: add Build Arena goal config`
- Remote state: `main...origin/main [ahead 1]`
- Dirty state after verification: no uncommitted changes reported
- Important implication: the target `.arena/goal.toml` required by `live_diff` is committed locally but not pushed to `origin/main`.

Open backlog verified through GitHub:

- Epic #25 and children #26-#31 are closed.
- Issues #23 and #24 are closed.
- Issue #21 remains open: advisory Elenchus critique for intake handoff packets.

## Conversation-derived progress timeline

### 2026-06-12/13 — Epic #25 closed the multi-domain offline loop

From session `20260613_210612_388d81`, the reported state was:

- Phase 0 (#26): fixed false status drift around intake/proposal implementation and added drift guards.
- Phase 1 (#27): intake began consuming decomposer component profiles and emitting component-scoped non-doc findings.
- Phase 2 (#28): proposal generation was partitioned into domains; documentation became one domain rather than the whole component.
- Phase 3 (#29): code-quality became the first non-doc domain, with a load-bearing `code_quality_gate`.
- Phase 4 (#30): cross-domain ranked proposals were added as `ranked-proposals/v0` with score breakdowns.
- Phase 5 (#31): the repo-scale `/goal` loop closed select -> apply -> verify -> dry-run/promote.
- Opus rejected two high-risk gate/safety defects before merge: the `# ruff: noqa` linter-bypass hole in Phase 3 and the Phase 5 holes where code promotion could rely on lint alone and promotion could stage an entire dirty worktree. The report says those were fixed and re-reviewed.
- Boundary explicitly stated then: offline/deterministic dry-run loop was built and reviewed, but it had not produced an operator-authorized live promotion on a real target.

Current audit result: this historical timeline aligns with git history, GitHub issues/PRs, active modules, and current tests. The exact test count has changed since that conversation: the old report said 438 tests; current collection is 457 tests.

### 2026-06-13/14 — first real target monitoring exposed the docs-only/live gap

From session `20260614_123310_d26219`, the earlier run against `fmc-mcp` was a dry-run using the offline path:

- Run root: `/home/leonb/projects/build-arena/.arena/runs/fmc-mcp-20260614T042002Z`
- It ran four cycles, selected documentation candidates only, and promoted zero changes.
- `fmc-mcp` local gates passed at the time: ruff, pytest, and mypy.
- The important correction was that this did not satisfy the intended meaning of `live`; `repo_goal_loop` still hardcoded fixture decomposition and deterministic apply.

Current audit result: the stored `loop-events.jsonl` corroborates the docs-only dry-run shape and zero promotions.

### 2026-06-14 — live loop implementation landed locally

The same session then pivoted to implementing actual live loop support. The final report claimed:

- `repo_goal_loop` now exposes live flags: `--decompose-mode live`, `--apply-mode live_diff`, `--allow-live`, `--live-provider`, `--live-model`, `--live-base-url`, `--live-api-key-env`, `--live-max-tokens`, and `--live-max-calls`.
- Live modes fail closed without `--allow-live`, explicit `--live-model`, and an explicit planned-call budget. Inert live flags now fail closed if neither `--decompose-mode live` nor `--apply-mode live_diff` is selected.
- `live_diff` requires the target repo `.arena/goal.toml` to be valid and tracked in HEAD.
- Live patch/provenance artifacts are preserved outside temporary worktrees.
- Candidate selection skips candidates with no deterministic verification commands.
- Code promotions require a configured and passing behaviour/test gate; promotion stages only the approved target path and re-checks boundaries.
- A live `fmc-mcp` dry-run succeeded through live decomposition and live diff proposal.

Current audit result: these implementation claims are corroborated by source inspection, CLI help, fail-closed guard execution, the latest live dry-run event log, and tests. The implementation is local-only until pushed.

## Implemented work verified from source

`arena/repo_goal_loop.py`:

- `RepoGoalLoopConfig` contains `decompose_mode`, `apply_mode`, `allow_live`, provider/model/base URL/API-key-env/max-token settings, and test-only seams.
- `_validate_live_config()` rejects unsupported modes, live mode without `allow_live`, live mode without explicit `live_model`, and `live_diff` without a loadable `.arena/goal.toml` tracked in target HEAD.
- `_decompose_and_rank()` threads live provider/model/base URL/API-key-env/max tokens into `build_project_model_snapshot()` and logs provider/model/gate metadata.
- `_select_promotable()` skips candidates without deterministic `verification_commands`.
- `_live_diff_apply()` builds an `OpenAICompatibleDiffTransport` and applies one selected proposal through `DiffProposerRunner`.
- `_apply_and_verify()` runs the candidate domain gate and only treats code candidates as promotable when the configured behaviour/test gate passes.
- `_promote()` stages exactly the approved target path, refuses staged path drift/boundary violations, commits in the cycle worktree, and ff-only merges the cycle branch.
- The CLI exposes the live/promotion flags shown above.

`arena/runners/diff_proposer.py`:

- `OpenAICompatibleDiffTransport` requires an explicit model or provider config, enforces served-model match through `OpenAICompatibleChatClient`, rejects empty/non-diff/truncated outputs, and records provider/model metadata.
- `DiffProposerRunner.apply()` runs the deterministic patch gate before apply, validates changed Markdown links, records patch and provenance under `.arena/patches`, and the loop then copies those artifacts out to the run artifact directory before worktree teardown.
- The Opus-noted recorded-patch fallback has been hardened: if Markdown repair happened and no current diff can be recorded, the runner discards the touched paths and raises `RunnerError("Markdown repair produced no recordable diff")`.

`/home/leonb/projects/fmc-mcp/.arena/goal.toml`:

- Present in target HEAD locally.
- Defines test/lint/typecheck/coverage commands.
- Defines source roots, out-of-scope paths, read-only `uv.lock`, and single-file/120-line diff caps.

## Verification commands run in this audit

Build Arena CLI surface:

```text
uv run python -m arena.repo_goal_loop --help
```

Confirmed the live/promotion flags are present.

Build Arena full gate:

```text
make verify
```

Result:

- `make generated` completed.
- `git diff --exit-code -- arena/generated dashboard/src/lib/generated` passed.
- `uv run ruff check .` passed.
- `uv run pyright` passed with 0 errors / 0 warnings / 0 informations.
- `uv run pytest tests -q` passed.
- Current collected test count: 457 tests.

`fmc-mcp` target gates:

```text
uv run ruff check .
uv run python -m pytest -q
uv run python -m mypy src tests
```

Result:

- Ruff passed.
- Pytest passed: 19 tests.
- Mypy passed: no issues in 11 source files.

Fail-closed live guard:

```text
uv run python -m arena.repo_goal_loop \
  --project /home/leonb/projects/fmc-mcp \
  --goal 'guard smoke' \
  --artifacts-root /tmp/build-arena-live-guard-<pid> \
  --max-cycles 1 \
  --decompose-mode live \
  --apply-mode live_diff \
  --live-model dummy
```

Result: exit 1 before any live work with `ValueError: live repo-goal modes require allow_live=True; refusing routine live spend`.

Latest live dry-run event proof:

- Run root: `/home/leonb/projects/build-arena/.arena/runs/fmc-mcp-live-20260614T174137Z`
- `RUN_STARTED`: `decomposeMode=live`, `applyMode=live_diff`, `dryRun=true`, provider xAI, model `grok-4.20-0309-non-reasoning`.
- `DECOMPOSITION_COMPLETED`: gate passed, zero violations, served model matched requested model, provider metadata recorded.
- `CANDIDATE_SELECTED`: documentation candidate `agent.agents-md.missing`, target `AGENTS.md`.
- `CANDIDATE_APPLIED`: live diff patch applied and preserved under `cycle-1/candidate-artifacts/`.
- `CANDIDATE_VERIFIED`: `test -s AGENTS.md` and `python3 -m arena.markdown_links --repo . --path AGENTS.md` both exited 0.
- `CANDIDATE_PACKAGED`: not promoted, reason `dry_run`.
- `RUN_ENDED`: `cyclesRun=1`, `promotions=0`, halted by budget.

Preserved provenance confirms:

- provider: `xai`
- requested model: `grok-4.20-0309-non-reasoning`
- served model: `grok-4.20-0309-non-reasoning`
- transport: `openai_compatible_diff`
- target path: `AGENTS.md`
- patch gate: accepted, touched only `AGENTS.md`
- API key source recorded as source metadata, not key value.

## What is verified vs. what is not

Verified:

- The offline multi-domain intake/proposal/loop pipeline exists and is test-covered.
- The live-loop plumbing exists in local Build Arena HEAD.
- The live flags are on the CLI.
- Live modes fail closed without explicit live authorization.
- The `fmc-mcp` target has a local committed goal config.
- A real live dry-run executed live decomposition and live diff proposal and preserved patch/provenance artifacts.
- The latest local code passes `make verify`; `fmc-mcp` passes its local gates.

Not verified:

- No actual live production promotion has been run. There is no `PROMOTED` or `BASELINE_ADVANCED` event in the latest live run.
- The live run selected a documentation candidate, so it did not prove a live code-edit promotion against `fmc-mcp`.
- The `--test-command` behavior gate was not exercised in the latest live run because docs candidates have `behaviour_gate=not_applicable`.
- Remote/CI consumers do not have the latest state because both Build Arena and `fmc-mcp` are ahead of `origin/main` by one commit.
- Broad unattended cross-repo autonomy remains unproven and explicitly out of scope.

## Current blockers or gates before a production run on a target project

Hard blockers for any remote/reproducible production run:

1. Push or PR the local commits. Build Arena is ahead of `origin/main` by `a071011`; `fmc-mcp` is ahead of `origin/main` by `25f4458`. A local run can use them now, but a remote or reproducible team run cannot.
2. Target repo must have a valid `.arena/goal.toml` committed in HEAD. `fmc-mcp` has this locally; another target project will not unless configured.
3. Live spend and mutation must be explicitly authorized at run time: `--allow-live`, explicit `--live-model`, `--allow-promotion`, and `--no-dry-run`.
4. Live provider credentials/model availability must be valid at run time. The production command now sets credential provenance explicitly with `--live-api-key-env XAI_API_KEY`; key values must remain secret.
5. Live spend must be explicitly bounded. The production command now includes `--live-max-calls 2`, a planned-call pre-flight gate for one live decomposition call plus one live diff call.

Not hard blockers for one bounded local `fmc-mcp` run, but real production risks:

1. The latest live run proved a documentation-candidate path, not a code-candidate path. If the next production run selects code, the behavior gate should run, but that specific live scenario has not been exercised against `fmc-mcp`; first live code promotion remains unproven.
2. The docs-candidate verification is stronger after this remediation because docs candidates require source references, but it still cannot prove semantic truth; an inaccurate LLM-authored documentation file that cites real files could still pass deterministic gates.
3. Promotion mutates the checked-out target branch in place by ff-only merge from the cycle worktree. There is no PR/branch-review wrapper and no rollback endpoint in this path; the rollback handle is git history plus the run artifact.
4. `fmc-mcp`'s goal config uses local unit/type/lint commands. If "production" means validating against a real Cisco FMC service, the target repo still needs a documented live-test credential/policy gate.
5. `repo_goal_loop` now has a planned-call pre-flight budget cap through `--live-max-calls`; it is not a provider-library retry counter or dollar-denominated spend cap.
6. Markdown repair has a remaining defense-in-depth concern from Opus: repaired Markdown content is not re-run through the full patch gate after repair. The current implementation is structurally constrained to in-place replacements on the already-validated Markdown file and re-checks links, so Opus accepted it as minor, not blocking.
7. No dashboard control plane, rollback endpoint, or live subscription-CLI subprocess execution exists. Those are broad-autonomy blockers, not blockers for one CLI-run bounded cycle.

## Latest status statement to reuse

Build Arena's local HEAD is ready to perform one bounded local `fmc-mcp` production run using live decomposition plus live diff proposal, provided the operator intentionally authorizes live spend/local mutation and accepts that the run may mutate the local target repo baseline. This is not broad unattended production readiness: no live promotion has actually been executed, both required commits are still local-only, the latest live run exercised a docs candidate rather than live code promotion, and broad unattended use remains blocked.

## Independent Opus review of this audit

New review artifact: `/home/leonb/projects/build-arena/reports/2026-06-14-progress-status-opus-review.json`.

Result: `ACCEPT_WITH_CORRECTIONS`.

Corrections applied here:

- Downgraded the headline from “locally ready for production-live promotion” to “mechanics can execute; promotion not production-ready until register reconciliation.”
- Added the readiness-register promotion blockers instead of calling the register merely stale.
- Clarified current dirty state: the audit/review artifacts are untracked after this reporting work.
- Elevated the weak docs-candidate gate, in-place promotion mutation, missing explicit cost cap, implicit credential-env dependency, and unexercised live code-promotion path.

## Production command, if explicitly authorized

```bash
cd /home/leonb/projects/build-arena && \
uv run python -m arena.repo_goal_loop \
  --project /home/leonb/projects/fmc-mcp \
  --goal 'Improve fmc-mcp with bounded, verified, repository-grounded changes using live LLM decomposition and live LLM diff proposal.' \
  --artifacts-root /home/leonb/projects/build-arena/.arena/runs/fmc-mcp-production-live-$(date -u +%Y%m%dT%H%M%SZ) \
  --max-cycles 1 \
  --decompose-mode live \
  --apply-mode live_diff \
  --allow-live \
  --live-provider xai \
  --live-model grok-4.20-0309-non-reasoning \
  --live-api-key-env XAI_API_KEY \
  --live-max-tokens 12000 \
  --live-max-calls 2 \
  --test-command 'uv run python -m pytest -q' \
  --allow-promotion \
  --no-dry-run
```

Do not run this from a fresh clone until the local commits are pushed or otherwise transferred.
