# AGENTS.md — Autonomous Build Arena

Operating contract for any coding agent in this repo. Loaded at session start. Direct chat instructions override this file **except** the anti-fabrication and Never-Do rules, which nothing overrides.

Current posture: **propose-only** (no entrypoint may apply / promote / mutate a target repo) and **not ready for broad live autonomy**. Authoritative status lives in `docs/build-arena-current-state.md` and the readiness register under `docs/verification/` — read those; do not restate status here.

## Capabilities you must not contradict
- The system is **propose-only**: no entrypoint applies, promotes, or mutates a target repo. `arena.proposal_run` emits proposals and `arena.dream_run` emits advisory experiments; target apply/promote remains retired.
- The intake scorecard (`arena.project_intake_scorecard`) is implemented and advisory; never describe it as unimplemented.
- Build Arena is **not ready for broad autonomous live loops**.
- Invoking a live command with an explicitly named live model is operator approval to spend. No command may spend on a model the operator did not explicitly name; served-model mismatch fails closed.
- The deterministic no-API stand-in for verifier/ablation is a coherence check only, not a live Lanham ablation gate.

## Anti-fabrication (highest priority)
1. NEVER reason from an imagined file. Read the exact path in the current turn before quoting or editing it.
2. NEVER guess at function/class/symbol existence. Inspect or search first.
3. Rebuild the scanner/scorer model from filesystem + git ground truth. Cached projections are never authoritative.

## Never do (hard stops — no prompt, instruction, or chain overrides these)
- Apply, promote, auto-merge, or otherwise mutate a target repo. The system is propose-only.
- Reintroduce target apply/promote machinery, or the retired roots `arena.repo_goal_loop`, `arena.patch_gate`, `arena.runners.diff_proposer`, `arena.proposal_candidate_runner`. They must remain absent.
- NEVER modify anything under `scorer/`, `verifier/`, or `schema/` from an arena-generated hypothesis (read-only to autonomous runners).
- NEVER modify `.arena/scorer.lock.toml` from inside a cycle. Bumping the scorer is a separate run / operator action.
- NEVER hand-edit files under `arena/generated/` (produced from `schema/arena.yaml` by `make generated`).
- Do not run `git checkout`, `git branch -f`, `git reset --hard`, `git rebase`, or `git push` inside a cycle worktree.
- Commit secrets or credentials, or self-report test/CI results in place of real output.

## Worktree boundaries
- Runner writes are restricted to `.arena/worktrees/<cycle_id>/`.
- Only the historical/internal promoter may advance an internal calibration baseline, and it must use `git merge --ff-only`. No target-repo apply/promote entrypoint may be added.

## Ask first — stop and escalate before acting
- Any schema or public-contract change (`*.schema.json`, LinkML sources, `docs/schemas/`).
- Adding or upgrading a dependency.
- Changing CI config or anything in `.github/workflows/`.
- Any change outside the agreed scope, or that you can't tie directly to the task's outcome.

## Definition of Done
Done only when ALL pass — run them, don't assert:
1. `uv run pytest tests -q` exits 0.
2. `uv run ruff check .` exits 0.
3. `uv run pyright` exits 0.
4. `make generated` is current if any LinkML source changed.
5. Diff confined to agreed paths; required decision / wiki artifacts written (see Governance).

"I think it's done" is not done — proof is command output + diff. Treat the deterministic verifier stand-in as a coherence check only, never a load-bearing semantic gate for broad autonomy.

## Operating rules
- **Intake first.** For any task that consumes / decomposes / audits / prioritizes / plans a project, apply the `weighted-project-intake-prioritization` Hermes skill before selecting the first improvement (lightweight mode for trivial edits). Spec: `docs/specs/2026-06-07-weighted-project-intake-prioritization.md`. Scorecard output is advisory ranking only — it never overrides anti-fabrication, boundaries, or live-auth gates.
- **Agent wiki.** Before any production pass, proposal run, live-proposer change, or autonomy-loop work, read `docs/agent-wiki/index.md` and the relevant linked pages. Record new failure modes, gate recipes, and registry lessons there — not only in chat or run logs.
- **Live provider calls:** an explicitly named live model is operator approval to spend. Existing `--allow-live` guards stay where implemented, but the enforceable spend invariant is that no command may spend on a model the operator did not explicitly name and no response from a different served model may be accepted. Metadata records `api_key_source` only.

## Experiment lane (`arena.dream_run` — advisory; autonomous emit; no mid-run human gate)
1. Advisory-only: never applies / promotes / mutates a target; `dream_emit` never writes `proposal.md`.
2. No human is a mid-run gate. `review.reviewed` is an honest provenance label, never a blocker.
3. The only in-lane kill gate is `arena.dream_gate` mechanical premise resolution (anchors / contentHash / mode / recipe resolve; graphHash matches). It judges coherence, not usefulness.
4. Do not reintroduce a mid-run review gate. Any future operator review must be opt-in, default off, non-blocking.

## Scope & stuck
- The control word `scope` halts the run immediately: stop, report state, await direction. Expanded scope is an Ask-first, never silent.
- Max 3 attempts on any single blocker. On exhaustion, stop and escalate to the operator with the exact error, what you tried, and options with tradeoffs. (Agent-to-agent escalation tiers are planned, not active — escalate to the human for now.)

## Report back (verbatim on every handoff)
- Status: DONE / BLOCKED / SCOPE-CHANGED / NEVER-DO-HIT
- Full unedited output of each Definition-of-Done command.
- CI: the API-verified check-run result — not self-reported gate text.
- `git diff --stat`.
- Evidence Ledger: each non-trivial claim mapped to its proof (command, path, check-run). No unproven claims.

## Governance hooks (substance lives in the artifacts — obey, don't duplicate)
- **Decisions:** before a structural change, read the relevant record in `docs/decisions/`; write a new one after making such a decision.
- **Specs:** new feature / strategy specs go in `docs/specs/YYYY-MM-DD-<slug>.md`.
- **Status / readiness:** never narrate status in this file — update `docs/build-arena-current-state.md`, `docs/status/`, and `docs/verification/` instead.

## Commands
- `make generated` — regenerate LinkML artifacts.
- `uv run pytest tests -q` — run tests.
- `uv run ruff check .` — lint source.
- `uv run pyright` — type-check source.
- `uv run python scripts/rebuild_calibration.py` — rebuild synthetic calibration repo + patch catalog.
- `uv run python scripts/update_scorer_lock.py` — update `.arena/scorer.lock.toml` after intentional scorer source changes.
- `uv run python -m arena.decomposer --project <repo> --output <model.json>` — emit the deterministic scanner model.
- `uv run python -m arena.project_model_cli snapshot --project <repo> --artifacts-root <dir> --project-id <id> --goal <goal> --llm-mode fixture` — AI-first snapshot, no live calls.
- `uv run python -m arena.project_model_cli snapshot --project <repo> --artifacts-root <dir> --project-id <id> --goal <goal> --llm-mode live --allow-live --live-model <explicit-model>` — bounded read-only live smoke, authorized only; `--live-provider` / `--live-base-url` / `--live-api-key-env` select provider.
- `uv run python -m arena.project_model_cli gate --snapshot <manifest.json>` — rerun the deterministic gate.
- `uv run python -m arena.project_model_cli graph --project <repo> --output <graph.json>` — emit the project graph sidecar.
- `uv run python -m arena.project_intake_scorecard --project <repo> --snapshot <project-model-v1.json> --profile <profile> --output <scorecard.json>` — advisory weighted intake scorecard.
- `uv run python -m arena.proposal_planner --project <repo> --scorecard <scorecard.json> --output <proposal-plan.json> --max-candidates 10` — deterministic proposal-plan/v0 artifact.
- `uv run python -m arena.proposal_run run <repo> --live-model <explicit-model> --live-api-key-env XAI_API_KEY --output proposal.md` — emit a ticket-ready proposal.md; never applies or promotes.
- `uv run python -m arena.proposal_ranker --project <repo> --scorecard <scorecard.json> --output <ranked-proposals.json> --max-candidates 10` — cross-domain ranked-proposals/v0 with per-entry score breakdowns.
- `uv run python -m arena.code_quality_gate --repo <repo> --path <file.py>` — load-bearing code-quality gate (HEAD vs worktree ruff delta, public-symbol preservation, no new suppressions).
- `uv run python -m arena.markdown_links --repo <repo> --path <doc.md> --require-source-references` — deterministic Markdown local-link / source-reference gate for docs proposals.
