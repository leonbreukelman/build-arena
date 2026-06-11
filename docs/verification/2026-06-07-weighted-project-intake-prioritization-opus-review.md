# Opus Review — Weighted Project Intake Prioritization

Date: 2026-06-07
Claude result subtype: success
Model usage keys: claude-opus-4-8
Cost USD: 0.41119300000000003

## Review output

I've reviewed all three artifacts against the conversation brief and review criteria. Here is the adversarial review.

```text
REVIEWER: Claude Code model=claude-opus-4-8 opus_confirmed=yes
VERDICT: ACCEPT_WITH_CHANGES

Critical blockers:
- None. The artifacts do not overclaim implementation, do not weaken Build Arena
  readiness boundaries, and keep anti-fabrication / protected-path rules intact.

Important issues:
- DIMENSION/WEIGHT MISMATCH (cross-artifact). Section 4 of the spec and the skill's
  "Canonical Dimensions" both define EIGHT dimensions, including 4.5 "Decision
  history." But all four weight tables (spec §5.1–5.4 and skill) list only SEVEN
  dimensions — "Decision history" has NO weight in any profile. The priority
  formula multiplies by `dimension_weight`, so decision-history findings are
  unscorable (effectively weight 0). AGENTS.md §2 repeats the same omission (lists
  7 dimensions, drops decision history). This is a real internal contradiction.
  Fix: either add "Decision history" to every profile (and renormalize each table
  to 100) or explicitly fold it into "Architecture, specs, and contracts" and say so.
- WEIGHT TABLES verified to sum to 100 each (30+20+15+15+10+5+5; 25+20+20+10+10+10+5;
  25+20+20+15+10+5+5; 35+20+20+15+5+3+2) — but only because decision history is
  excluded. Adding it back requires re-balancing; flag so this isn't done carelessly.

Missing content or contradictions:
- Two different canonical backlog titles. Spec line 6: "Add weighted project-intake
  scorecard and AI-usable housekeeping prioritization." Spec §13: "Add weighted
  project-intake scorecard for AI-usable repo housekeeping and improvement
  prioritization." Pick one so backlog/issue tracking stays unambiguous.
- No source references/links for external design inputs (Diátaxis, DORA, OpenSSF,
  MADR/ADR, Google doc style) — they are named but uncited. Acceptable for a spec,
  but the review criteria asks about source references; add URLs/versions to make
  the grounding auditable and avoid drift.
- The required review output file (`docs/verification/2026-06-07-weighted-project-
  intake-prioritization-opus-review.md`) does not yet exist; only a `.raw.json` and
  `.stderr.txt` from a prior automated run are present. This human-readable review
  still needs to be saved there per spec §15.

Overreach / scope-risk:
- Section 8 "Required outputs" lists EIGHT heavyweight artifacts (Repo Health Model,
  Documentation Knowledge Graph, AI Usability Score, Maintenance Risk Register,
  Weighted Improvement Backlog, First Recommended Improvement, Accepted Deferrals,
  machine-readable sidecar) and says a run "should produce" all of them. That reads
  as first-slice scope and conflicts with the leaner §11 acceptance criteria / §12
  non-goals. Clarify that §8 is the full vision and the first slice need only emit
  the JSON scorecard + markdown report + ranked first improvement.
- AGENTS.md §1 mandates applying the skill "before selecting the first improvement"
  for any consume/resume/decompose/audit/prioritize/plan task, with no lightweight
  escape hatch. The skill HAS a lightweight mode, but AGENTS.md doesn't reference it,
  so the durable Build Arena instruction reads as always-heavyweight. Add a one-line
  pointer to lightweight mode for trivial edits to avoid ceremony creep.
- Skill "When to Use" trigger list is very broad (≈20 keywords). Combined with the
  AGENTS.md mandate this risks firing on nearly every task. Lightweight mode mitigates
  it, but consider tightening to planning/audit/intake/prioritization shapes.

Recommended edits before finalizing:
- Resolve the decision-history dimension: add it to all weight profiles (renormalized
  to 100) or merge it into "Architecture, specs, and contracts" and update spec §4,
  skill canonical dimensions, and AGENTS.md §2 consistently.
- Unify the canonical backlog title across spec line 6 and §13.
- Reframe spec §8 as "full intake-run vision" and cross-reference §11/§12 for the
  first-slice subset.
- Add a lightweight-mode reference to AGENTS.md §1 so trivial tasks aren't forced
  into full scoring.
- Add source links/versions for the cited external frameworks.
- Save this review to the §15 path.

Final assessment:
- Strong, well-grounded set of artifacts. Intent is captured: a tunable, cross-project
  meta-strategy with documentation/verification weighted first for new repos; durable
  user preference (Hermes skill) is cleanly separated from project-specific Build Arena
  instruction (AGENTS.md); the scorecard is consistently framed as a not-yet-implemented
  backlog layer that does not grant autonomous-loop permission; GitHub Wiki is correctly
  positioned as projection, not canonical truth. The blocking defect is the
  decision-history dimension defined but unweighted everywhere — fix that plus the
  title/scope/lightweight clarifications and this is ready to accept as a backlog spec.
```

Note: per the prompt this was review-only — I made no edits. The single must-fix before treating the spec as implementation-ready is the **decision-history dimension having no weight in any profile** (and the same omission in AGENTS.md §2); everything else is consistency/scope tightening.
