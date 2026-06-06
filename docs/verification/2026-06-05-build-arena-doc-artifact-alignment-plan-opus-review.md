# Build Arena Documentation/Artifact Alignment Plan Opus Review

Date: 2026-06-05
Reviewer: Claude Code
Requested model: Opus
Review mode: read-only, no tools allowed
Claude Code result is_error: `False`
Stop reason: `end_turn`
Total cost USD: `0.34113249999999995`

## Verdict

`ACCEPT_WITH_CHANGES`

## Critical blockers

- None

## Required Changes

### presence-only-tests-allow-residual-stale-text

- **where:** Task 1 / tests/test_project_status_docs.py
- **problem:** All three tests assert only the PRESENCE of new markers. They never assert the ABSENCE of the stale framing they are meant to replace. README.md can keep 'Current implementation status: Phase 4 foundation' as its headline AND have an appended AI-first section, and every test still passes. Likewise AGENTS.md can retain a 'Current phase: Phase 4' line. The plan's own acceptance criteria 1/3 ('accurately states the current status', 'reflects post-Phase-4 reality') are therefore not actually enforced by the tests — the docs can remain self-contradictory and green.
- **fix:** Add negative/consistency assertions: e.g. assert that README/AGENTS do not present Phase 4 as the latest/current state (e.g. that 'Project Model v1' appears, and that any phase-4 mention is qualified as 'foundation complete' rather than 'current phase'), and assert the specific stale headline strings observed during Task 0 read are gone. Tie the assertions to the exact stale sentences found, not just to added markers.

### fabricated-exact-string-for-final-report

- **where:** Task 4 Step 1 and Task 1 test_june5_final_report...
- **problem:** The plan hardcodes the replacement target 'This slice is ready to commit as one coherent verified change. It does not push, merge, deploy, start a broader live loop, or enable worktree mutation/promotion.' and the test asserts the first sentence is absent. The evidence packet only says the report 'still says the slice is "ready to commit"' — it does NOT quote this exact sentence. If the real wording differs, (a) the find/replace silently no-ops and (b) the test's `not in report` assertion passes anyway (false green), leaving the stale claim in place while reporting success.
- **fix:** Make Task 0 capture the ACTUAL stale sentence(s) from the report, then derive both the replacement edit and the test assertion from that observed text. Do not assert against an invented exact string.

### unverified-cli-flags-no-execution-test

- **where:** Task 2 Steps 3-4, Task 3 Step 3
- **problem:** The documented CLI examples assume flags not present in the evidence: --artifacts-root, --project-id, --goal, --output for project_model_cli snapshot/graph/gate, and --format project-model-v0/--source-task/--primary-backlog-item for arena.decomposer. Evidence only confirms the 'snapshot' subcommand, its --llm-mode {fixture,recorded,live,off} values, and the --allow-live guard. Shipping wrong invocations is itself doc-misalignment, and there is NO test (not even `--help`) that the documented commands are valid. Acceptance criterion 2 (correct CLI examples) is unbacked.
- **fix:** Add a verification step that runs each documented command's `--help` (no live spend) to confirm subcommands and flag names before writing them, and add a lightweight test that asserts documented invocation patterns match actual `--help` output (or at least that the legacy `arena.decomposer` example is present, which the current test omits).

### secret-scan-false-positive-on-env-var-name

- **where:** Task 6 secret scan + Task 2 (live setup) tension
- **problem:** The secret-scan regex `(?i)xai[_-]?api[_-]?key` and the api_key/token pattern will fire on the bare env-var NAME 'XAI_API_KEY' even with no value. Documenting that live mode reads XAI_API_KEY is legitimate and likely needed for the live example, but it will cause a hard SystemExit(1) failure (false positive), which an implementer may 'fix' by deleting needed documentation. The scan should match key=VALUE assignments, not mentions of the variable name.
- **fix:** Tighten the regex to require an actual assigned secret-like value (and explicitly allowlist bare env-var-name references), or scope the scan to exclude markdown inline-code mentions of XAI_API_KEY.


## Recommended Changes

### guard-known-stale-identifiers

- **problem:** Evidence flags stale/phantom identifiers that may live in the active docs: 'XAIProvider' (should be 'LiveProjectModelLLM'), and shorthand module names 'runner_router.py' / 'promoter.py' / 'failure_ledger.py' (actual: router.py, worktrees.py, ledger.py). The plan never checks whether README/AGENTS contain these, and the tests don't assert their absence. If present, the docs stay misaligned.
- **fix:** Add assertions that README/AGENTS do not contain 'XAIProvider', 'runner_router.py', 'promoter.py', or 'failure_ledger.py', and correct any occurrences found in Task 0.

### enum-token-as-readme-marker-is-brittle-and-poor-ux

- **problem:** Requiring the raw internal enum 'not_ready_blockers_remain' to appear verbatim in user-facing README.md is brittle and reads as an implementation leak. A prose statement of not-ready status is better doc quality.
- **fix:** Keep the enum requirement for AGENTS.md (agent context) but allow README to satisfy the readiness requirement via durable prose (e.g. 'not ready for broad autonomous live loops') rather than the raw token.

### no-overclaim-direction-guard

- **problem:** The regression test only prevents regressing to v0/Phase-4-only language; it does not prevent a future agent from over-claiming (e.g. 'production ready', 'fully autonomous live'). Given the explicit constraint against claiming broad live autonomous readiness, the drift guard is one-directional.
- **fix:** Add an assertion that README/AGENTS do NOT contain overclaim phrases such as 'production ready', 'fully autonomous', or 'live autonomous loop ready'.

### verified-tag-before-review

- **problem:** Task 8 commits with a '[verified]' prefix, but Task 7's independent review is optional/skippable. Using the project's '[verified]' convention when review was skipped may misrepresent assurance level versus other commits in the log.
- **fix:** Only apply '[verified]' when the full verification (and review, if that is what the tag connotes in this repo) actually ran; otherwise use a plain message.

### pending-marker-scan-collision

- **problem:** The draft-marker scan rejects 'PENDING'/'TBD' in changed docs, but legitimate status prose may use 'pending' (e.g. 'v1 adoption pending in related repos'). Case-insensitive intent is unclear and could force awkward wording or a false failure.
- **fix:** Make the marker scan word-boundary and case-sensitive to true uppercase draft-marker words, or allowlist legitimate 'pending' prose.


## Missing Tests

- No assertion that stale headline framing (Phase 4 as 'current phase'/'current status') is removed from README and AGENTS — only additive markers are checked.
- No test that the documented CLI invocations are valid (no `--help` smoke check), so wrong flags can ship green.
- No assertion that README contains the legacy `arena.decomposer` v0 example (acceptance criterion 2 covers it but the test only checks `arena.project_model_cli`).
- No guard against overclaim phrases ('production ready', 'fully autonomous live').
- No assertion that stale/phantom identifiers (XAIProvider, runner_router.py, promoter.py, failure_ledger.py) are absent from active docs.
- No test confirming AGENTS.md retains the blocked-paths/anti-fabrication/worktree rules after the rewrite (the plan instructs preservation but nothing enforces it — a rewrite could silently drop them).

## Unsafe Assumptions

- Assumes the June 5 final report contains the exact sentence the plan hardcodes; evidence only paraphrases 'ready to commit'. Exact-string edit + negative test can produce a false green if wording differs.
- Assumes specific CLI flags (--artifacts-root, --project-id, --goal, --output, --format project-model-v0, --source-task, --primary-backlog-item) exist; evidence confirms only the snapshot subcommand, --llm-mode values, and --allow-live.
- Assumes documenting live mode will not need to mention XAI_API_KEY, yet a usable live example arguably must — colliding with the secret scan.
- Assumes README/AGENTS do not already contain stale identifiers/overclaims; only checks for missing markers, not for wrong content.
- Assumes the pre-live readiness register is currently `not_ready_blockers_remain`; Task 0 reads it but no task reconciles its actual content with the readiness claims the docs will make, so docs could overclaim if the register changed.
- Assumes 'replace single Phase 4-only status sentence' — README may express phase-4 status in multiple places; a single-sentence replacement could leave other stale mentions.

## Reviewer comments

The plan is well-scoped and safety-conscious in the right ways: clear non-goals, explicit refusal to claim broad live autonomous readiness, correct instinct to preserve historical RCA artifacts while patching only stale post-commit wording, and explicit instructions NOT to weaken AGENTS.md anti-fabrication/blocked-path/worktree rules. The TDD-for-docs framing and the hygiene scans are good. The central weakness is that the regression tests are presence-only: they prove new markers were added but never prove the stale framing was removed, so README/AGENTS can pass all tests while remaining internally contradictory and still misaligned with code — which is exactly the failure mode the plan exists to prevent. Secondary real risks are the fabricated exact-string target for the final-report edit (false-green hazard) and the unverified CLI flags shipped with no execution check, which would replace one form of doc drift with another. The secret-scan/env-var collision and the lack of any test pinning AGENTS.md's safety rules after rewrite should also be addressed. None of these are blockers to the approach, but they must be fixed before the plan can credibly guarantee its acceptance criteria; hence ACCEPT_WITH_CHANGES.

## Required plan changes incorporated

The implementation plan was patched after this review to:

- add negative assertions for exact stale README/AGENTS/final-report strings;
- require Task 0 to capture actual stale final-report text before editing;
- verify CLI flags with `--help` before documenting invocation patterns;
- tune the secret scan so bare environment variable names are not treated as leaked secret values;
- add absence guards for stale identifiers and broad-live-readiness overclaims;
- test that AGENTS.md preserves anti-fabrication, blocked-path, and worktree safety rules;
- keep raw `not_ready_blockers_remain` as an agent-context marker while allowing README to use better human-facing prose;
- narrow draft-marker scans to true uppercase draft markers and avoid blocking legitimate status prose;
- make commit-message guidance conditional on full verification/review evidence.
