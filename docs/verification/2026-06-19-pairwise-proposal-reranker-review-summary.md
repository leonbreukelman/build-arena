# Pairwise Proposal Re-ranker Review Summary

Date: 2026-06-19

## Scope reviewed

Artifact reviewed:

- `docs/specs/2026-06-19-pairwise-proposal-reranker-design.md`

The reviewed design adds a narrow proposal re-ranker stage: mechanical pre-filter, pairwise king-of-the-hill comparisons using one default LLM, both candidate orderings per matchup, deterministic winner-as-rank-1 plan rewrite, and a sidecar trace. It does not add panels, multiple models, OpenRouter routing, new gates, schema versions, ticket logic, or changes to decompose/intake/emit.

## Independent review result

Fable was preflighted but not confirmed available, so the independent review used Claude Code Opus.

Initial Opus verdict: `ACCEPT_WITH_CHANGES`.

Required fixes from the initial review:

1. Creation targets such as a docs index file, `AGENTS.md`, and an agent backlog file must not be rejected merely because they do not already exist in the ProjectGraph.
2. Binding/no-op filtering must be deterministic and static; executing project verification commands in a pre-filter would add a flaky dynamic surface.
3. Pre-filter drops must map into the strict `proposal-plan-v0` `skippedFindings` shape with one singular `reason` field.
4. Judge evidence citations need deterministic citable tokens that can be validated exactly.
5. Source-plan lineage fields must be preserved verbatim in the derived plan.
6. The cost claim must remain truthful by avoiding dynamic binding-probe execution.

Patches applied to the design:

- Candidate `target_paths`/`target_path` are now validated for safe relative syntax and specificity, but exempt from graph-existence resolution.
- Only non-target file/symbol references must resolve to the ProjectGraph.
- Binding verification is now static classification: at least one known binding command must name a candidate target path; broad gates are supplemental only.
- `skippedFindings` mapping is specified as `{finding_id, rank, title, reason, evidence_paths}` with rich drop reasons kept in the trace.
- Citable evidence tokens are specified (`target_path:<path>`, `evidence:<kind>:<path>`, `evidence:provenance:<ref>`, `evidence:component:<componentId>`, `constraint:<index>`) and response validation accepts only exact tokens.
- `snapshotId`, `projectRoot`, `repoFactsHash`, `baseLineage`, and `sourceScorecardId` are explicitly preserved from the source plan.

Final Opus re-review verdict: `ACCEPT` with no remaining blockers.

## Publication boundary

The raw local Opus JSON captures, prompts, and stderr files were not published. This file is the public-safe review summary. It omits local host paths, raw tool metadata, and model-run transcripts while preserving the review decisions and required design changes.
