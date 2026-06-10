All evidence reviewed. Here is the strategic review.

---

# Build Arena Fable/Mythos-Class Strategic Review

## 1. Executive verdict

- **Keep going, but simplify hard.** The philosophy is sound and rarer than you think; the execution has inverted its own priorities. The verdict is *simplify and redirect*, not pivot or stop.
- The core problem: **Build Arena has never improved a real project.** Three-plus phases of infrastructure exist, all verified — against a synthetic calibration repo. The scorer is hardcoded to that repo's shape (`--cov=validatorlib`, `benchmarks/runtime_proxy.py` in `scorer/engine.py:202,240`). The loop cannot run on any repo Leon actually owns.
- There is **no proposer.** `arena/hypothesizer.py` is a UCB1 bandit over pre-configured symbolic arms emitting template strings ("Improve {cluster} with {technique}"). Nothing generates actual code changes. The two pieces that produce value — measure a real repo, propose a real patch — are the two pieces that don't exist.
- The project has over-rotated from "verify the loop" into **verifying the verifier of the decomposer of the loop**. The decomposition gate (`arena/project_model_gate.py`, ~730 lines, with probe-proof hash replay) is more elaborate than the improvement loop it is supposed to serve, and its consumer (hypothesis generation) was never built.
- The verification-first instinct was correct, but it has produced a failure mode the constitution doesn't name: **infinite regress of meta-verification as a substitute for closing the loop.** The docs/verification tree (reviews of reviews, re-review prompts, readiness registers, three project-model schema versions) is now a larger artifact than the system.
- Several "verified" claims are softer than their branding: the live verifier's "Lanham ablation" is a keyword check (`verifier/ablation.py:55-58` looks for the words "because", "score", "coverage" in the reasoning string). The docs disclose this, but the framing invites overestimation.
- The readiness register blocks Build Arena's own next steps on **other repos' adoption of Project Model v1** (PMV1-002/003). That coupling is wrong and should be cut.
- **What to do:** keep the constitution, worktree/promotion/budget/divergence machinery, and the anti-fabrication discipline. Build a generic scorer and a real LLM proposer, run worktree-only cycles on a real repo with *Leon merging PRs as the promotion gate*, and freeze all decomposition/scorecard/meta work until that loop has produced ten real merged improvements.

## 2. The core owner goal as you understand it

Leon wants a system that, with low ongoing effort from him, takes one of his repos and steadily makes it better: it understands the repo, picks sensible improvements, applies them in isolation, proves mechanically that they're improvements, learns from failures, and never lies about what it did. Leon's role is to anchor intent occasionally and approve, not to babysit each cycle.

**The repo is optimizing a narrower, different goal.** What it has actually been optimizing for months is: "build verification machinery whose own correctness is provable, and verify the artifacts that describe the machinery." That is a research program about trustworthy autonomous loops. It is a legitimate program — but it is not the owner goal, and the owner goal does not require most of it. The tell is that the constitution's own recipe (`GOAL → ANCHOR → DECOMPOSE → LOOP`) has never executed its LOOP stage against anything real, while the DECOMPOSE stage has three schema versions, an encyclopedia generator, and adversarial probe-proof replay.

## 3. What the current approach gets right

These are essential and should not be removed:

- **The axiom and the verification hierarchy.** "Every claim verifiable by something that is not the agent; mechanical first; LLMs propose and critique but never self-certify" is the correct foundation, and it is encoded consistently across docs and code. This is the project's genuine asset.
- **Worktree isolation + ff-only promotion** (`arena/worktrees.py`). Locked worktrees, separate promoter, runtime-artifact cleanup. Simple, correct, done.
- **Append-only JSONL events as canonical state** with SQLite as a disposable projection. Exactly right for auditability and the anti-fabrication rule.
- **Budget caps and divergence halts** (`arena/budget.py`, `arena/divergence.py`). Wall-clock, cycle counts, boundary-attempt thresholds, scorer/verifier disagreement streaks. Small, testable, load-bearing safety.
- **Boundary protection** — scorer/verifier/schema as read-only to autonomous runners, checked before runner spawn. This is the single most important guard against Goodhart-by-self-modification.
- **The failure ledger and fingerprints** — append-only memory of failed hypotheses, rejected before spend. Cheap and valuable.
- **Fail-closed LLM adapters** (`arena/project_model_llm.py`) — truncation, cancellation, empty content, invalid JSON all reject; provenance hashes recorded. This is the right pattern for every future LLM call.
- **The operator-as-editor model and the frontier constraint** (load vs. drift trade-off). The constitution's seven anchoring questions are the correct interface between Leon and the system.
- **F3 as a documented negative result.** Recording "Lanham accepts F3 and that's expected; axis 2 is needed" instead of hacking the test to pass is real intellectual honesty and worth preserving as method.

## 4. Where the current approach is overcomplicated or misweighted

- **The decomposition apparatus dwarfs its purpose.** Project graph, encyclopedia, snapshot, gate, v0 projection, v1 contract, held-out probes, planted negatives, near-neighbor alternatives, probe-proof deterministic-hash replay — all to answer "which parts of this repo should I try to improve, and how do I know the map is honest?" For the first hundred cycles, a ranked list of modules by churn, complexity, and coverage would answer that question well enough, and the loop's own verify stage catches a bad target choice anyway (the patch just fails to improve the score).
- **The gate verifies prose, not usefulness.** `project_model_gate.py` checks vague-name word lists, responsibility word counts (≥6 words), and "shares a significant word with the goal." These are mechanical, but they measure whether a decomposition *reads well-formed*, not whether it leads to better improvement selection. An LLM will trivially learn to pass them. The only real test of a decomposition is downstream: did cycles using it outperform cycles using a naive target list? That consumer doesn't exist, so the gate is calibrated against nothing.
- **Verification effort is aimed at the wrong layer.** The probe-proof replay machinery (hash-recomputed planted-negative gate replays) verifies that *the gate discriminates*. Impressive, recursive, and two layers removed from "did the project get better." Meanwhile the live loop's actual reasoning-ablation check is a keyword stand-in. The deepest verification exists where it matters least.
- **Three project-model schema versions before one consumer.** v0, internal v0.1, v1, plus compatibility projections and cross-repo adoption tracking. Contract versioning discipline for a contract nobody consumes yet.
- **Cross-repo blockers on the critical path.** PMV1-002/003 (Elenchus Core and Arena Calibration v1 adoption) block dry-run hypothesis generation *inside Build Arena*. Build Arena's internal loop should never wait on other repos.
- **The documentation corpus is becoming its own maintenance problem.** Dozens of dated review/re-review/prompt artifacts, multiple orientation docs with overlapping status claims, tests to guard docs against drift from other docs. The anti-drift tests are a good idea, but they're treating a symptom: there is too much status-bearing prose.
- **The weighted intake scorecard spec** is a well-written prioritization layer for a pipeline whose execution stage doesn't run. It got an Opus review, AGENTS.md integration rules, and weight profiles — before the loop it prioritizes for can act on anything. This is the over-indexing pattern in miniature.
- **The bandit is premature.** UCB1 over symbolic technique×cluster arms presumes a stream of cycles generating reward signal. With zero real cycles, it's optimization machinery with no gradient to climb.

## 5. The simpler viable architecture

The minimum loop that should exist before any more research layers:

1. **Goal config (per repo, written once with Leon):** the seven anchoring questions distilled to a small TOML/JSON file — check commands (test/lint/typecheck as *the project defines them*), pinned invariants, dimension weights, out-of-scope paths, diff-size cap. This replaces the calibration-repo hardcoding in the scorer.
2. **Generic scorer:** run the repo's own declared commands, parse pass/fail and counts, produce the existing ScoreVector. Same determinism/lock discipline as today, repo shape supplied by config instead of assumed.
3. **Target picker (boring on purpose):** rank candidate files/modules by mechanical signals — coverage gaps, complexity, churn, lint density. No graph, no encyclopedia, no LLM required. Optionally an LLM suggests targets, *advisory*.
4. **Proposer:** an LLM (Claude Code CLI or API, behind the existing fail-closed adapter pattern) receives the worktree, goal config, and one target, and produces a diff. One hypothesis, one fingerprint, one mechanical success criterion — exactly as the constitution already demands.
5. **Verify:** existing verifier shape — re-score the live worktree, reject test failures, pinned regressions, non-positive delta, oversize diffs, boundary violations. Drop or demote the ablation quorum to advisory until a real ablation runner exists; a keyword check must not be a load-bearing gate.
6. **Promotion = a branch and a PR. Leon merges.** This is the crucial simplification: owner review *is* the promotion gate for now. It dissolves the rollback-endpoint, dashboard, and broad-autonomy blockers — git revert of a reviewed PR is the rollback story — and it matches the readiness register's own conclusion that autonomy isn't ready.
7. **Memory:** the existing event log and failure ledger, unchanged.

Everything in this list except the generic scorer and the proposer **already exists and works**. This is roughly two modules of new code plus config plumbing, not a rewrite.

## 6. Critical gaps before self-sufficient intelligent improvement

Ranked by blocker severity:

1. **No generic scorer** — the system cannot measure any real repo. Absolute blocker; nothing downstream matters until this exists.
2. **No proposer** — the system cannot generate a change. Equal blocker.
3. **No end-to-end run on a real repo** — until propose→apply→verify completes once outside the calibration fixture, every architectural belief is untested. (LIVE-002 in the readiness register already hints at this: live model output was syntactically valid but gate-failing — the first contact with reality produced a surprise.)
4. **No goal-anchoring instance** — the constitution's seven questions have never been answered for a real project and encoded. Without it, "better" is undefined for any real target.
5. **Ablation gate is theater on the live path** — must become advisory or real before it gates anything that matters.
6. **No outcome learning loop** — ledger records failures, but nothing yet converts cycle outcomes into improved selection. Acceptable gap until cycles exist; meaningless before then.
7. **Patch-generalization axis (anti-F3)** — real, but diff caps + owner PR review + the project's own test suite cover most of the practical risk at current scale. Research item, not a blocker.

## 7. What to change / remove / add

### Change
- **Re-aim the build order at the loop's missing middle**: generic scorer, then proposer, then real-repo cycles. Treat every other workstream as frozen until then.
- **Rewrite the readiness register** so internal milestones (dry-run hypothesis generation, worktree cycles) are blocked only by internal criteria. Move cross-repo v1 adoption to a separate "ecosystem" tracker that blocks nothing.
- **Demote the ablation quorum to advisory** in `verifier/engine.py` until a real ablation runner exists, so a stand-in never silently becomes a load-bearing gate.
- **Reframe status language** in README/AGENTS: "Phase 1–4 verified" should read "verified against the synthetic calibration repo; not yet exercised on any real project." The docs are honest in detail but the headlines oversell.
- **Consolidate orientation docs**: one constitution (keep as-is — it's good), one brief, one README. Everything dated becomes explicitly historical.

### Remove / de-emphasize
- **Freeze the decomposition stack** (graph/encyclopedia/snapshot/gate/probe-proof machinery). Don't delete it — it's built and tested — but stop extending it, and stop letting it gate anything. Its real evaluation comes later: do model-informed targets beat naive targets over N cycles?
- **Shelve Project Model v0 compatibility and v1 cross-repo adoption** work entirely.
- **Defer the weighted intake scorecard** until the loop runs; then implement its first slice as the target picker's ranking input, where it has a consumer.
- **Park the bandit** until there are enough real cycles to produce reward signal (likely 30+).
- **Stop producing review-of-review artifacts** for specs. One review per spec, then build.

### Add
- **`goal.toml` / goal-config schema** — the anchoring answers, check commands, invariants, weights, scope boundaries, diff cap. The single per-project operator artifact.
- **Generic check-runner scorer** (config-driven; reuse the lock/determinism discipline).
- **LLM proposer adapter** with the same fail-closed, hash-everything pattern as `LiveProjectModelLLM`, plus diff-size and path-boundary enforcement on its output.
- **PR-based promotion path**: verified candidate → branch + structured evidence file (score before/after, commands run, events) → Leon merges.
- **A per-cycle one-paragraph evidence summary** for Leon — the owner-facing artifact that currently doesn't exist anywhere in the pipeline.

## 8. Recommended next three milestones

### Milestone 1 — Generic scorer + goal anchoring on a real repo
- **Goal:** `Scorer.score_repo()` works on any repo with a `goal.toml`, anchored by Leon's answers to the seven questions for one real project (FMC-MCP or build-arena itself).
- **Why first:** nothing can be verified on a real repo until it can be measured; it's also the smallest milestone and forces the first real anchoring exercise.
- **Scope:** config schema; config-driven command execution and parsing; determinism check on real repos.
- **Non-goals:** no LLM calls, no decomposition, no loop changes.
- **Acceptance gates:** scores two different real repos from their own declared commands with zero calibration-repo assumptions; re-scoring the same OID is deterministic within tolerance; a `goal.toml` for one real repo exists and Leon has approved it; existing calibration tests still green.
- **Proof artifacts:** committed goal config; two dated score records with command transcripts; passing test run output.

### Milestone 2 — One real cycle, worktree-only, no promotion
- **Goal:** propose→apply→verify completes on the anchored repo with a real LLM proposer; output is a branch plus an evidence report. Promotion deliberately absent.
- **Why second:** this is the first moment Build Arena does the thing it exists to do, and it surfaces real-world failure modes (LIVE-002-style surprises) at the cheapest possible point.
- **Scope:** proposer adapter (fail-closed, hashed, diff-capped); wire into the existing `run_loop` states; ablation gate demoted to advisory; run ~5 cycles.
- **Non-goals:** no promotion, no bandit learning, no decomposition input (naive target list), no dashboard.
- **Acceptance gates:** ≥5 cycles complete without manual intervention; ≥1 candidate passes all mechanical gates; zero writes outside cycle worktrees (audited from events + git); every accept/reject traceable to a command output; budget and one injected divergence halt fire correctly.
- **Proof artifacts:** event log; candidate branches; per-cycle evidence reports; halt records.

### Milestone 3 — Owner-gated improvement loop producing merged value
- **Goal:** a multi-cycle run that yields verified candidate PRs; Leon merges; ledger records outcomes; at least two real improvements land in a real repo.
- **Why third:** this closes the loop end-to-end with the owner as promotion gate — the first version of Build Arena that is *useful*, and the baseline against which all research layers (decomposition, bandit, scorecard) must later prove their marginal value.
- **Scope:** PR/branch packaging with evidence summaries; ledger-driven skip of failed fingerprints; a 10–20 cycle budgeted run.
- **Non-goals:** autonomous ff-only promotion to main; dashboard; rollback endpoint (git revert of a reviewed PR is the rollback story); multi-repo operation.
- **Acceptance gates:** ≥10 cycles within budget; ≥2 PRs merged by Leon with green project checks; ≥1 fingerprint rejected by ledger memory without re-spend; Leon's total review time logged and under ~15 minutes per merged PR; zero fabricated claims found in spot-audit of evidence vs. events.
- **Proof artifacts:** merged PR links; ledger entries; run summary with cost/time; Leon's review-time log.

## 9. How to use Mythos/Fable-class models here

The principle: a frontier model's edge is judgment under ambiguity and generation quality — so deploy it where the axiom *permits* judgment (proposing, critiquing, distilling) and never where the axiom forbids it (certifying).

1. **Proposer (highest value).** Patch quality is the loop's throughput ceiling: a stronger proposer means more candidates clear the same mechanical gates per dollar. Prompt = goal config + target + relevant code + explicit success criterion + diff cap; output = unified diff + stated reasoning (which later feeds real ablation). Guardrails: fail-closed adapter, hashes, diff cap, boundary check on touched paths — all patterns you already have.
2. **Adversarial critic, advisory channel.** Before verification spend, a "find the bug / find the F3" pass over a candidate patch — given the spec but *not* the proposer's reasoning. Its verdict never gates; it gets logged next to the mechanical verdict so you accumulate calibration data on whether critic warnings predict mechanical rejection. That data later tells you if the critic deserves a (still non-final) gate role.
3. **Strategy reviews like this one — periodic, not continuous.** Quarterly "is the methodology drifting from the owner goal" reviews against the repo's own evidence. This is tier-4 verification in your hierarchy, applied where it belongs: methodology, not correctness.
4. **Failure-ledger analysis.** After ~30 real cycles, hand the ledger + events to a frontier model to propose new heuristics, target rankings, or arms. Proposals enter as config changes Leon approves — the SkillOpt-shaped "strategy as trainable object" idea, with Leon as the gate.
5. **Documentation distillation.** A one-time pass to compress the orientation corpus and mark historical artifacts, reducing the drift surface your status tests guard.
6. **What NOT to use it for:** judging patch correctness as a final gate, replacing the scorer, generating "verification" prose, or certifying readiness. Also resist "the model is smarter now, so loosen the gates" — the architecture's correlated-failure argument doesn't weaken as models improve; capability and self-assessment improve together, which is exactly the trap.

## 10. Final recommendation to Leon

Build Arena's foundation is genuinely good — better than most attempts at this problem, because you correctly identified that verification, not cognition, is the bottleneck, and you encoded that into rules the system actually enforces. The worktree isolation, event sourcing, budgets, divergence halts, and anti-fabrication discipline are keepers, permanently.

But the project is currently solving a harder problem than the one you have, and not solving the one you have at all. You wanted a loop that improves your projects with low load on you. What exists is a deeply verified harness around a loop with two empty sockets: it cannot measure a real repo (the scorer is hardcoded to the calibration fixture) and it cannot propose a real change (the hypothesizer emits template strings). Meanwhile, the most sophisticated engineering in the repo — probe-proof replay, planted negatives, three project-model schema versions — verifies the *map-making*, two layers away from any improvement. Verifier-first was the right instinct; it has tipped into verification-instead-of-everything. The constitution warns against unbounded scope in the agent; the meta-work has had unbounded scope in the project.

The fix is small, not a rewrite. Two new modules — a config-driven scorer that runs each repo's own checks, and a fail-closed LLM proposer — plus one decision: **promotion is a pull request, and you are the merge button.** That single move dissolves most of your readiness blockers honestly (rollback = git revert of a reviewed PR), keeps you exactly as safe as the readiness register demands, and gets real improvements landing in weeks. Freeze the decomposition stack, the scorecard spec, the v0/v1 adoption work, and the bandit until the loop has produced ten merged improvements; then each frozen layer must buy its way back in by demonstrably beating the naive baseline over real cycles. That's your own axiom applied to your own architecture: the decomposer's claims of usefulness need a verifier too, and the only honest one is the running loop.

One honest risk to accept: the first real cycles will be humbling. LIVE-002 already showed that real model output passes syntax and fails substance. That's not a reason to add more pre-verification — it's the evidence the loop generates only when it runs, and it's worth more than any further meta-artifact.

---

**Main files inspected:** `AGENTS.md`, `README.md`, `docs/build-arena-project-brief.md`, `docs/build-arena-constitution.md`, `docs/build-arena-specification.md`, `docs/specs/2026-06-07-weighted-project-intake-prioritization.md`, `docs/verification/2026-06-05-pre-live-readiness-register.json`, `arena/loop.py`, `arena/hypothesizer.py`, `arena/budget.py`, `arena/divergence.py`, `arena/worktrees.py`, `arena/project_decomposer_ai.py`, `arena/project_model_llm.py`, `arena/project_model_gate.py`, `verifier/engine.py`, `verifier/ablation.py`, `scorer/engine.py`, plus directory surveys of `arena/`, `tests/`, and `docs/`.
