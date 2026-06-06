# Build Arena — Current State

Volatile. Rewrite this at the end of each session. It tells a fresh agent what is true right now and what to do next. Read it third, after the constitution and the project brief.

Last updated: 2026-05-28

---

## Status in one line

Calibration harness built and hermetically verified. Live validation in progress — first live run produced no discrimination (worker too noisy via OpenRouter); switching to xAI Grok direct to retest.

---

## What is true right now

- Project is on disk at `/home/leonb/projects/build-arena`. Pre-promotion backup at `/home/leonb/projects/build-arena.pre-calibration-promotion.20260528T014850Z`.
- Venv created with `uv venv .venv --python python3.12 --seed` (system lacks `python3.12-venv`; `python3 -m venv` fails — use `uv`).
- `exercise_verifier.py` passes from the installed tree: `ALL HARNESS PREDICTIONS HOLD`, exit 0. Harness logic confirmed correct on this machine.
- Scorer: 4/4 against ground truth on the live run. Mechanical layer is sound.

## The open problem

First live run (`results/run_20260528T025111Z.yaml`) returned `load_bearing_fraction: 1.0` on F1, F2, and F3 — every component of every fixture judged load-bearing. No discrimination. `verifier_matches_ground_truth: 2/4` (only F1 and F4 correct, and F1 only by coincidence since everything accepts).

Two facts about that run:
- It routed through OpenRouter: `ANTHROPIC_BASE_URL=https://openrouter.ai/api`, `ANTHROPIC_AUTH_TOKEN` set, no `ANTHROPIC_API_KEY`. The model actually served is unconfirmed and may not match what was requested.
- The harness is correct (hermetic exercise + 4/4 Scorer). The fault is in the worker layer: the worker regenerated a different patch under every perturbation, including paraphrasing controls, which is the signature of a worker too brittle/noisy to produce a discrimination signal.

## Today's task

Switch the worker/judge to xAI Grok (direct, not via OpenRouter) and re-run calibration to test whether a cleaner model path discriminates.

Decisions already made by the operator:
- Path: xAI direct. Endpoint `https://api.x.ai/v1`, OpenAI-compatible. Key in `XAI_API_KEY`. Use the `openai` Python package.
- Model: `grok-4.1-fast` for both worker and judge during diagnosis (do not mix providers yet). Pin exact strings; confirm the served model matches.
- Paid path, no data sharing. (Tripwire still open for real project data later — not relevant to toy fixtures.)
- Clear the OpenRouter redirect first: `unset ANTHROPIC_BASE_URL ANTHROPIC_AUTH_TOKEN`.

Scope: modify `arena/llm.py` only. Do not touch verifier/runner/scorer/fixtures/lanham/patch_eq. If the protocol forces a change outside `llm.py`, stop and flag.

## What success looks like

The discrimination matrix matches ground truth on the Verifier's three invoked fixtures:
- F1 accept, low-ish but ≥threshold load-bearing fraction
- F2 reject, low fraction (~0.25), paraphrasing perturbations NOT changing the patch
- F3 accept (the documented Lanham insufficiency)
- F4 not invoked
- Summary: `scorer 4/4`, `verifier 3/4`, `overall_pass false` (false is correct — F3's documented mismatch)

If that holds, calibration is validated and the next milestone is backlog item 2 (patch-generalization axis to reject F3).

## What failure tells us

- If Grok also pins everything at `1.0`: the problem is not the model. Suspect `patch_eq.py` AST-equivalence being too strict — cosmetically different but equivalent patches read as "changed." Next step becomes a harness fix to patch equivalence, carefully, without bleeding into behavioral/Scorer territory. Do NOT swap models again first; the model has been ruled out at that point.
- If the served model ≠ `grok-4.1-fast`: a redirect is in play; pin harder or change the request path.
- Capture F2's per-perturbation, per-sample detail either way — it is the sharpest diagnostic.

## Immediate next actions for the agent

1. Read `arena/llm.py`, report structure.
2. Add xAI worker/judge in `llm.py` only.
3. Install `openai`, report version.
4. Confirm `XAI_API_KEY` present, redirect vars unset, make one test call, report which model served it.
5. Run `python -m arena.runner`, report mechanically (exit code, YAML path, summary block, per-fixture verifier values + load_bearing_fraction, F2 per-perturbation detail, all non-empty notes). No interpretation. Hold.
