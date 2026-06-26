# AGENTS.md — Autonomous Build Arena

## Anti-fabrication rules (highest priority)

1. NEVER reason from an imagined file. Before quoting or editing any file content, read that exact path in the current turn.
2. NEVER guess at function/class/symbol existence. Inspect files or search first.
3. The scanner/scorer model must be rebuilt from filesystem and git ground truth. Cached projections are never authoritative.

## Boundary-violation rules

1. NEVER modify anything under `scorer/`, `verifier/`, or `schema/` as part of an arena-generated hypothesis. These paths are read-only to autonomous runners.
2. NEVER modify `.arena/scorer.lock.toml` from inside an arena cycle. Bumping the scorer requires a new run/operator action.
3. NEVER hand-edit files under `arena/generated/`. They are produced from `schema/arena.yaml` by `make generated`.
4. NEVER bypass `git worktree` for future APPLY/PROMOTE phases. Phase 1 tests may use temporary fixture repos only.

## Worktree rules for future runners

1. Runner writes are restricted to `.arena/worktrees/<cycle_id>/`.
2. Do not run `git checkout`, `git branch -f`, `git reset --hard`, `git rebase`, or `git push` inside a cycle worktree.
3. The promoter is the only component allowed to advance the internal baseline, and it must use `git merge --ff-only`.

## Cross-project intake and prioritization rule

1. For any Build Arena task that consumes, resumes, decomposes, audits, prioritizes, or plans work for a project, apply the `weighted-project-intake-prioritization` Hermes skill before selecting the first improvement. Use the skill's lightweight mode for trivial/narrow edits so this rule does not create unnecessary ceremony.
2. Treat documentation/project knowledge, reproducible verification, architecture/spec contracts, AI-agent usability, decision history, security hygiene, backlog governance, and operations/rollback as scorecard dimensions. Adjust weights by project phase instead of using one universal priority order.
3. Canonical project knowledge should live in versioned repo docs and agent instructions. GitHub Wiki or generated encyclopedia output may be used as a navigation layer, but not as the only source of truth unless explicitly mirrored/versioned.
4. The Build Arena backlog specification for this strategy is `docs/specs/2026-06-07-weighted-project-intake-prioritization.md`. The deterministic intake scorecard described there is implemented as the `arena/project_intake_scorecard.py` CLI; its output is advisory ranking only and does not authorize mutation.
5. Scorecard output is advisory: it ranks findings but does not override anti-fabrication rules, protected-path boundaries, live-provider authorization gates, or the current broad-autonomy blockers.

## Agent wiki rule

1. Before a production pass, proposal run, live proposer change, or autonomy-loop implementation, read `docs/agent-wiki/index.md` and the relevant linked wiki pages in addition to this file and the latest status/report artifact.
2. The agent wiki is versioned operational memory for recurring Build Arena failure modes, gate recipes, proposal lineage/registry state, and promotion definition-of-done. It informs prompts and implementation; it does not replace deterministic gates.
3. New failed candidate events, proposal-registry lessons, gate recipes, or recurring path/prompt mistakes should be recorded in `docs/agent-wiki/` as durable reference material, not left only in chat or run logs.

## Current implementation status

Phase 1-4 foundation is implemented and verified against the synthetic calibration repo. The loop uses JSONL events as canonical state, locked git worktrees for cycle isolation, ff-only promotion foundation, live wall-clock budget checks, and hard divergence halts. It has not yet produced a verified improvement on a real target repo.

The post-Phase-4 AI-first decomposer is also implemented. AI decomposer snapshots now write `project-model-v1.json` as the primary Project Model v1 enriched artifact; `iterationReadiness` is required in v1 because the core intake/proposal loop reads it. `LiveProjectModelLLM` provides the direct xAI/OpenAI-compatible bounded live path behind the CLI `--allow-live` guard. The shared OpenAI-compatible LLM path is operator-switchable for decomposition and proposal transport by provider/base URL/model/API-key-env configuration; credentials can come from the environment or `~/.hermes/.env`, metadata records only `api_key_source`, live surfaces require an explicit model ID, and served-model match failures fail closed. The proposal transport can request a unified diff from an explicit Grok/OpenAI-compatible model and then hands the output to the deterministic patch gate; live proposal/decomposition runs must keep explicit controls such as `--live-api-key-env XAI_API_KEY` and `--live-max-calls`. The 2026-06-15 bounded `fmc-mcp` live production pass executed but promoted nothing: live decomposition, gate, freshness, and synced intake worked; the selected docs proposal hit a safe gate failure at the Markdown link gate; the target repo was not mutated. This did not prove a production improvement or broad unattended autonomy. The current full-autonomy gap analysis is `docs/specs/2026-06-15-full-autonomy-gap-analysis.md`.

The pre-live readiness register at `docs/verification/2026-06-05-pre-live-readiness-register.json` remains `not_ready_blockers_remain` for broad autonomy while recording a scoped `boundedFmcMcpProductionRun` exception. Build Arena is not ready for broad autonomous live loops: dashboard control plane, rollback endpoint, multi-cycle unattended production autonomy, and live subscription-CLI subprocess execution remain blocked or unimplemented. The current ablation keyword gate is advisory for real cycles until a real ablation runner exists; the verifier uses a deterministic no-API stand-in, not a live Lanham ablation gate, and it must not be treated as a load-bearing semantic gate for broad autonomy.

## Intake → proposal → loop pipeline (implemented, advisory; promotion operator-gated)

A deterministic intake → proposal → loop pipeline is implemented downstream of the Project Model. Intake/ranking are advisory; autonomous mutation only happens in the loop's explicitly operator-authorized promotion path (dry-run by default). Epic #25 (children #26–#31) generalized the proposal component from documentation-only to multi-domain (documentation + code-quality) and closed the loop:

- `arena/project_intake_scorecard.py` — weighted project-intake scorecard CLI. Reads a Project Model snapshot, emits ranked evidence-backed findings with the explainable priority formula and profile weights. Now emits **component-scoped non-doc findings** from the decomposer's `componentProfiles` (e.g. high-risk untested components) and **code.quality.lint.<path>** findings, not only the hardcoded documentation absence list. Advisory only.
- `arena/proposal_domains.py` — the multi-domain proposal contract. Each improvement domain (documentation, code_quality, generic_file) implements `find_candidates`/`first_candidate` behind a shared registry; documentation is one domain, not the whole component.
- `arena/proposal_planner.py` — turns the scorecard into a deterministic `proposal-plan/v0` artifact via the domain registry: ranked single-file candidates with grounded intent, repo-facts block, success criterion, verification commands, and skipped-finding accounting.
- `arena/proposal_ranker.py` — the cross-domain ranker. Produces one `ranked-proposals/v0` artifact (`docs/schemas/ranked-proposals-v0.schema.json`) spanning all domains, ranked by the same explainable weighted formula with an auditable per-entry score breakdown. Ranks from the scorecard's stored weights (faithful to the intake run); profile weighting demonstrably re-ranks security/verification above docs on a `production` profile.
- `arena/code_quality_gate.py` — the load-bearing code-quality gate. Compares ruff violation counts for one file between git HEAD and the worktree; ACCEPTS only on a real reduction with public-symbol preservation and no new suppressions (per-line or file-level `ruff:`/`flake8:` noqa, `type: ignore`). Documented KNOWN BOUNDARY: lint-delta + symbol preservation, NOT full behaviour.
- `arena/repo_goal_loop.py` — **the repo-scale `/goal` loop (capstone).** Each cycle: decompose → intake → cross-domain rank → select top promotable candidate → boundary check → apply a deterministic offline fix in an isolated worktree (`ruff --fix` for `.py`, grounded generator for `.md`) → run the domain gate → dry-run record / authorized ff-only promote → re-decompose. Guards: `max_cycles` budget, consecutive-failure divergence halt, boundary check before apply. Fail-closed promotion: code (`.py`/`needs_code_change`) requires a configured+passing behaviour/test gate; promotion stages only the approved target and re-checks the boundary before ff-only merge; dry-run is the default and never touches the repo.
- `arena/proposal_candidate_runner.py` — selects a ranked candidate, drives `arena/runners/diff_proposer.py`, applies the diff in a worktree, runs the candidate's verification gate. Live transport requires an explicit `--model`; otherwise it fails closed or uses `--fake-diff-file` for tests.
- `arena/repo_facts.py` — deterministic repository fact collection (top-level files/dirs, docs/markdown inventory, truncation flags) used to ground proposal prompts.
- `arena/markdown_links.py` — deterministic local Markdown link + source-reference validation gate for documentation proposals (`--require-source-references` is the default planner gate for docs candidates).

Status: the proposal component is **no longer documentation-only** — it produces and verifies real code-quality changes alongside documentation, ranks them cross-domain, and can run them in a closed dry-run loop. Promotion (baseline mutation) remains operator-gated and fail-closed; the default loop path is dry-run, deterministic, and offline (no live model). The pre-live readiness register remains the authority on broad live autonomy.

## Experiment proposer lane (advisory; autonomous emit; no mid-run human gate)

The tier-3 experiment lane (`arena.dream_run`; modules currently named `arena.dream_*`
pending a rename) generates advisory experiment proposals autonomously and writes
`experiment.md`. Hard constraints:

1. No human is a mid-run gate. The capability map is auto-generated and used as-is; there
   is no `review.reviewed` precondition for generation, research, the gate, or emit.
   `review.reviewed` is an honest provenance label only, never a blocker.
2. The lane is advisory-only: it never applies, promotes, or mutates a target repo, and
   `dream_emit` never writes `proposal.md`.
3. The only in-lane kill gate is `arena.dream_gate`'s mechanical premise resolution
   (anchors/contentHash/mode/recipe resolve; graphHash matches). It judges coherence, not
   usefulness, and not human-review state.
4. Trust that a proposal is worth acting on comes from the mechanical gate plus the
   downstream evaluation loop (attempt → measure the declared observable → verdict), not
   from a human reviewing the capability map. Judgment happens at the output or in
   evaluation, never as a mandatory mid-run stop.
5. Do not reintroduce a mid-run human review gate in this lane. If a future change needs
   operator review, it must be opt-in (default off) and must not block the default run.

## Commands

- `make generated` — regenerate LinkML artifacts.
- `uv run pytest tests -q` — run tests.
- `uv run ruff check .` — lint source.
- `uv run pyright` — type-check source.
- `uv run python scripts/rebuild_calibration.py` — rebuild synthetic calibration repo and patch catalog.
- `uv run python scripts/update_scorer_lock.py` — update `.arena/scorer.lock.toml` after intentional scorer source changes.
- `uv run python -m arena.decomposer --project <repo> --output <model.json>` — emit the deterministic scanner model.

- `uv run python -m arena.project_model_cli snapshot --project <repo> --artifacts-root <dir> --project-id <id> --goal <goal> --llm-mode fixture` — build AI-first snapshot artifacts without live provider calls.
- `uv run python -m arena.project_model_cli snapshot --project <repo> --artifacts-root <dir> --project-id <id> --goal <goal> --llm-mode live --allow-live --live-model <explicit-model>` — run a bounded read-only live smoke only when explicitly authorized; provider/base URL/API-key-env can also be selected with `--live-provider`, `--live-base-url`, and `--live-api-key-env`.
- `uv run python -m arena.project_model_cli gate --snapshot <manifest.json>` — rerun the deterministic gate for a snapshot manifest.
- `uv run python -m arena.project_model_cli graph --project <repo> --output <graph.json>` — emit the project graph sidecar.
- `uv run python -m arena.project_intake_scorecard --project <repo> --snapshot <project-model-v1.json> --profile <profile> --output <scorecard.json>` — emit the advisory weighted intake scorecard.
- `uv run python -m arena.proposal_planner --project <repo> --scorecard <scorecard.json> --output <proposal-plan.json> --max-candidates 10` — emit the deterministic `proposal-plan/v0` ranked candidate artifact.
- `uv run python -m arena.proposal_candidate_runner --worktree <worktree> --proposal-plan <proposal-plan.json> --candidate-rank 1 --output <result.json>` — apply and verify a ranked candidate inside a worktree (live transport needs an explicit `--model`).
- `uv run python -m arena.proposal_ranker --project <repo> --scorecard <scorecard.json> --output <ranked-proposals.json> --max-candidates 10` — emit the cross-domain `ranked-proposals/v0` artifact with auditable per-entry score breakdowns.
- `uv run python -m arena.code_quality_gate --repo <repo> --path <file.py>` — run the load-bearing code-quality gate (HEAD vs worktree ruff delta, public-symbol preservation, no new suppressions).
- `uv run python -m arena.repo_goal_loop --project <repo> --goal <goal> --artifacts-root <dir> --max-cycles 5` — run the bounded repo-scale `/goal` improvement loop (dry-run by default; add `--no-dry-run --allow-promotion --test-command <cmd>` for operator-authorized fail-closed promotion).
- `uv run python -m arena.markdown_links --repo <repo> --path <doc.md> --require-source-references` — deterministic Markdown local-link and source-reference gate for documentation proposals.
