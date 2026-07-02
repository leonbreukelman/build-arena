# Build Arena — Current State

This file is the compact current-state anchor for facts that should not live in `AGENTS.md`. It superseded the previous `Historical status snapshot` placeholder after the root operating contract stopped carrying status narrative. `AGENTS.md` is the operating contract; `README.md` is the concise entrypoint; `docs/build-arena-project-brief.md` is the longer orientation brief. This file carries status narrative, module catalog, blockers, and relocation targets for facts removed from the root agent instructions. Dated files under `docs/status/` and `docs/verification/` remain point-in-time evidence unless their index says they are active.

Last reconciled: 2026-06-30.

## Current posture

Build Arena is a local-first, propose-only improvement system. A project is decomposed into responsibility-bearing units, candidate improvements are ranked into proposal artifacts, and cross-unit contracts are modeled explicitly instead of being left as agent intuition.

The current system posture is:

- Phase 1-4 foundation is implemented and verified against the synthetic calibration repo.
- The post-Phase-4 AI-first decomposer is implemented locally.
- `project-model-v1.json` is the primary Project Model v1 enriched artifact; `docs/project-model-v1.md` is the human reference.
- `iterationReadiness` is required in v1 because the core intake/proposal loop reads it.
- `arena.proposal_run` emits `proposal.md`.
- `arena.dream_run` emits `experiment.md`.
- Target apply/promote machinery is retired. No Build Arena entrypoint may apply or promote code to a target repo.
- Build Arena is not ready for broad autonomous live loops while the readiness register under `docs/verification/` reports `not_ready_blockers_remain`.

The proposal-only remediation record is `docs/specs/2026-06-27-propose-only-remediation.md`. The pre-live readiness register is `docs/verification/2026-06-05-pre-live-readiness-register.json` until a stable index/latest readiness artifact exists.

## Phase 1-4 foundation

The Phase 1-4 foundation is implemented and verified against the synthetic calibration repo. It uses JSONL events as canonical state, locked git worktrees for cycle isolation, ff-only promotion foundation for the historical/internal calibration baseline, live wall-clock budget checks, and hard divergence halts. It has not produced a verified improvement on a real target repo.

Implemented foundation surfaces:

- Phase 1 scorer calibration: `.arena/scorer.lock.toml`, deterministic `scorer/engine.py`, scorer-lock validation in `scorer/lock.py`, and a 13-diff synthetic calibration catalog with positive, negative, and neutral patches rebuilt by `scripts/rebuild_calibration.py`.
- Phase 2 verifier calibration: `verifier/engine.py`, `verifier/ablation.py`, `verifier/config.py`, and `verifier/calibration.py`. Verification combines score delta, test status, pinned regressions, and a deterministic ablation quorum.
- Phase 3 runner-selection primitives: `arena/fingerprints.py`, `arena/ledger.py`, `arena/hypothesizer.py`, `arena/router.py`, and runner adapters under `arena/runners/`.
- Phase 4 loop foundation: `arena/loop.py`, `arena/events.py`, `arena/budget.py`, `arena/divergence.py`, and `arena/worktrees.py`.
- Boundary protection: `arena/boundary.py` rejects hypotheses that target scorer/verifier/schema/generated surfaces or `.arena/scorer.lock.toml` before runner spawn.
- Generated LinkML models: `arena/generated/` is produced from `schema/arena.yaml` by `make generated` and must not be hand-edited.

The historical/internal calibration loop uses append-only JSONL as canonical state, rebuildable SQLite event projections, live wall-clock budget checks, hard divergence halts, locked git worktrees, and ff-only internal-baseline mechanics. It is not a target-repo apply/promote surface.

## AI-first decomposer and Project Model v1

The post-Phase-4 AI-first decomposer is implemented. AI decomposer snapshots write `project-model-v1.json` as the primary Project Model v1 enriched artifact. Project Model v1 wraps the enriched snapshot, graph, gate report, provenance, hashes, model IDs, derived-artifact strategy, and required `iterationReadiness` block in the shared v1 contract.

Relevant modules:

- `arena/decomposer.py` emits the deterministic scanner model.
- `arena/project_graph.py`, `arena/project_snapshot.py`, `arena/project_encyclopedia.py`, and `arena/project_model_gate.py` build the graph, snapshot, encyclopedia, and deterministic gate sidecars from git/filesystem truth.
- `arena/project_decomposer_ai.py` creates snapshot bundles and writes `project-model-v1.json` as the primary Project Model v1 enriched artifact.
- `arena/project_model_v1.py` owns the Project Model v1 contract wrapper.
- `arena/project_model_llm.py` contains fixture, recorded, off/noop, and live LLM adapters. `LiveProjectModelLLM` is the direct xAI/OpenAI-compatible live path backed by the shared OpenAI-compatible client.
- `arena/project_model_cli.py` exposes `snapshot`, `graph`, `gate`, and `freshness`.

Live model paths are bounded. Credentials can come from the environment or `~/.hermes/.env`; provider metadata records only `api_key_source`, never the key. Live surfaces require an explicit model ID and strict served-model match checks. `project_model_cli snapshot --llm-mode live` is guarded by `--allow-live` and refuses routine live spend without explicit authorization.

## Intake → proposal pipeline

A deterministic intake → proposal pipeline is implemented downstream of the Project Model. Intake and ranking are advisory. Generated outputs are proposals or experiments only.

Stage chain:

`Project Model v1 → intake scorecard → cross-domain ranker → proposal plan → proposal_run/dream_run emit`

Retired target apply/promote roots must remain absent:

- `arena.repo_goal_loop`
- `arena.patch_gate`
- `arena.runners.diff_proposer`
- `arena.proposal_candidate_runner`

The delete set and trace rationale live in `docs/specs/2026-06-27-propose-only-remediation.md`; `tests/test_apply_promote_retired.py` guards the absence.

Active intake/proposal modules:

- `arena/project_intake_scorecard.py` reads a Project Model snapshot and emits ranked, evidence-backed findings using the explainable priority formula and profile weights. It emits component-scoped non-doc findings from the decomposer's `componentProfiles` and `code.quality.lint.<path>` findings, not only hardcoded documentation absence targets. Output is advisory ranking only.
- `arena/proposal_domains.py` is the multi-domain proposal contract. Each improvement domain (`documentation`, `code_quality`, `generic_file`) implements `find_candidates`/`first_candidate` behind a shared registry, so documentation is one domain rather than the whole component.
- `arena/proposal_planner.py` converts the scorecard into a deterministic `proposal-plan/v0` artifact via the domain registry: ranked single-file candidates carrying grounded intent, a repo-facts block, success criterion, verification commands, and skipped-finding accounting.
- `arena/proposal_ranker.py` produces one `ranked-proposals/v0` artifact spanning all domains, ranked by the same weighted formula with an auditable per-entry score breakdown, scored from the scorecard's stored weights so the artifact stays faithful to the intake run. Profile weighting demonstrably re-ranks security/verification above documentation on a `production` profile.
- `arena/code_quality_gate.py` is the load-bearing code-quality check used in proposal success criteria. It compares ruff violation counts for one file between git HEAD and a worktree and accepts only a real reduction with public-symbol preservation and no new suppressions (per-line or file-level `ruff:`/`flake8:` noqa, `type: ignore`). Known boundary: lint-delta plus symbol preservation, not full behavior.
- `arena/repo_facts.py` collects deterministic repository facts such as top-level files/dirs, docs and markdown inventory, and truncation flags to ground proposal prompts.
- `arena/markdown_links.py` validates local Markdown links and, with `--require-source-references`, requires documentation candidates to cite an existing source. The planner uses this source-reference gate for docs candidates by default.

Status: the proposal component is no longer documentation-only. It ranks code-quality and documentation findings cross-domain and emits grounded proposal artifacts. Build Arena no longer runs target apply/promote loops.

## Experiment proposer lane

`arena.dream_run` is the tier-3 advisory experiment lane. Modules are currently named `arena.dream_*` pending a rename. The lane generates advisory experiment proposals autonomously and writes `experiment.md`.

Hard constraints:

1. No human is a mid-run gate. The capability map is auto-generated and used as-is; there is no `review.reviewed` precondition for generation, research, gate, or emit. `review.reviewed` is an honest provenance label only, never a blocker.
2. The lane is advisory-only: it never applies, promotes, or mutates a target repo, and `dream_emit` never writes `proposal.md`.
3. The only in-lane kill gate is `arena.dream_gate` mechanical premise resolution: anchors, contentHash, mode, and recipe resolve; graphHash matches. It judges coherence, not usefulness and not human-review state.
4. Trust that a proposal is worth acting on comes from the mechanical gate plus the downstream evaluation loop: attempt → measure the declared observable → verdict. Judgment happens at the output or in evaluation, never as a mandatory mid-run stop.
5. Do not reintroduce a mid-run human review gate in this lane. If a future change needs operator review, it must be opt-in, default off, and non-blocking.

## Broad-autonomy blockers

The readiness register at `docs/verification/2026-06-05-pre-live-readiness-register.json` remains `not_ready_blockers_remain` for broad autonomy while recording a scoped historical `boundedFmcMcpProductionRun` exception that is now retired after propose-only remediation.

Current broad-autonomy blockers include:

- dashboard control plane is not implemented.
- rollback endpoint is not implemented.
- Multi-cycle unattended production autonomy remains unproven.
- live subscription-CLI subprocess execution is not implemented.
- Related downstream repos that consumed older project-model compatibility output still need v1 adoption plans.

The current ablation keyword gate is advisory for real cycles until a real ablation runner exists. The verifier uses a deterministic no-API stand-in, not a live Lanham ablation gate, and it must not be treated as a load-bearing semantic gate for broad autonomy.

## Status and verification references

- `docs/status/INDEX.md` lists active, superseded, and historical status docs.
- `docs/verification/2026-06-05-pre-live-readiness-register.json` is the current readiness register until a stable readiness index/latest artifact exists.
- `docs/specs/2026-06-15-full-autonomy-gap-analysis.md` is the current full-autonomy gap analysis.
- `docs/specs/2026-06-27-propose-only-remediation.md` records apply/promote retirement and the retired root delete set.
- `docs/build-arena-project-brief.md` remains the longer architecture and orientation brief.
- `README.md` remains the concise entrypoint and CLI example surface.

## Commands to trust

Core verification:

```bash
make generated
uv run pytest tests -q
uv run ruff check .
uv run pyright
uv run python scripts/rebuild_calibration.py
uv run python scripts/update_scorer_lock.py
```

Deterministic decomposer:

```bash
uv run python -m arena.decomposer --project <repo> --output <model.json>
```

AI-first snapshot and sidecars without live provider calls:

```bash
uv run python -m arena.project_model_cli snapshot --project <repo> --artifacts-root <dir> --project-id <id> --goal <goal> --llm-mode fixture
uv run python -m arena.project_model_cli graph --project <repo> --output <graph.json>
uv run python -m arena.project_model_cli gate --snapshot <manifest.json>
```

Bounded read-only live smoke, only when explicitly authorized and with an explicit model ID:

```bash
uv run python -m arena.project_model_cli snapshot --project <repo> --artifacts-root <dir> --project-id <id> --goal <goal> --llm-mode live --allow-live --live-model <explicit-model>
```

Provider/base URL/API-key-env are operator-switchable with `--live-provider`, `--live-base-url`, and `--live-api-key-env`.
