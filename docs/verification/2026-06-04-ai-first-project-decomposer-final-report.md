# AI-first Project Decomposer Final Report — 2026-06-04

## Outcome

Working. The AI-first Build Arena project decomposer is implemented as a local-first sidecar pipeline that rebuilds graph/wiki/snapshot/gate artifacts from filesystem and git truth, ingests recorded leading-model decomposition output, keeps LLM claims advisory until deterministic gates pass, and preserves project-model/v0 compatibility.

## Implemented pipeline

- ProjectGraph: deterministic git/filesystem graph with code/doc/config/protected/generated nodes, provenance refs, Python AST import/symbol parsing, JavaScript import/function parsing, symlink identity handling, ignored generated-directory sentinels, and source-truth dirty-state metadata.
- Encyclopedia/wiki: Markdown pages derived from graph nodes with provenance-backed summaries and redaction of credential-shaped text.
- LLM decomposition bridge: fixture/off/recorded modes, recorded real-model output ingestion, prompt/model/output hashes, and preserved raw model/probe outputs.
- ProjectModelSnapshot: components, contracts, cross-cutting concerns, observable checks, held-out probes, verification gaps, near-neighbor alternatives, input/prompt/model hashes, and project-model/v0 projection.
- Deterministic gate: inventory coverage, provenance completeness, component measurability, contract references/direction/self-reference, edge coverage, protected/generated boundaries, cross-cutting concern coverage, held-out probe presence/isolation/discrimination, no-live-paid-API acceptance commands, snapshot freshness, and verification-gap honesty.

## Final pilot evidence

### Build Arena

- Repo: `/home/leonb/projects/build-arena`
- Final snapshot: `/home/leonb/projects/build-arena/docs/verification/2026-06-04-ai-first-project-decomposer-pilot-build-arena/snapshot-4cb7261dd9905984`
- Gate result: passed=True, violations=0
- Graph nodes/edges: 4674/5031
- Snapshot objects: components=8, contracts=10, checks=6, gaps=21, probes=6
- Probe controls: all_golden_passed=True, all_planted_negatives_failed=True, all_expected_gates_observed=True
- Distinct negative violation gates: ['component_measurability', 'contract_references', 'cross_cutting_concerns', 'edge_coverage', 'protected_surfaces']
- Command artifact: `/home/leonb/projects/build-arena/docs/verification/2026-06-04-ai-first-project-decomposer-pilot-build-arena/recorded-repaired-snapshot-command.json`

### FMC-MCP

- Repo: `/home/leonb/projects/fmc-mcp`
- Final snapshot: `/home/leonb/projects/build-arena/docs/verification/2026-06-04-ai-first-project-decomposer-pilot-fmc-mpc/snapshot-e43d7b1e7cfe791f`
- Gate result: passed=True, violations=0
- Graph nodes/edges: 175/209
- Snapshot objects: components=5, contracts=5, checks=3, gaps=4, probes=3
- Probe controls: all_golden_passed=True, all_planted_negatives_failed=True, all_expected_gates_observed=True
- Distinct negative violation gates: ['component_measurability', 'contract_references', 'cross_cutting_concerns', 'edge_coverage', 'inventory_coverage']
- Command artifact: `/home/leonb/projects/build-arena/docs/verification/2026-06-04-ai-first-project-decomposer-pilot-fmc-mpc/recorded-repaired-snapshot-command.json`

### Held-out leonbreukelman-engineer

- Repo: `/home/leonb/projects/leonbreukelman-engineer`
- Final snapshot: `/home/leonb/projects/build-arena/docs/verification/2026-06-04-ai-first-project-decomposer-pilot-held-out/snapshot-6a7e077842d60d81`
- Gate result: passed=True, violations=0
- Graph nodes/edges: 116/130
- Snapshot objects: components=7, contracts=1, checks=3, gaps=8, probes=4
- Probe controls: all_golden_passed=True, all_planted_negatives_failed=True, all_expected_gates_observed=True
- Distinct negative violation gates: ['component_measurability', 'contract_references', 'cross_cutting_concerns', 'edge_coverage', 'protected_surfaces']
- Command artifact: `/home/leonb/projects/build-arena/docs/verification/2026-06-04-ai-first-project-decomposer-pilot-held-out/recorded-repaired-snapshot-command.json`

## Opus reviews and repairs

- Spec review: `docs/verification/2026-06-04-ai-first-project-decomposer-spec-opus-review.md`; valid critiques were patched into the spec before planning.
- Plan review: `docs/verification/2026-06-04-ai-first-project-decomposer-plan-opus-review.md`; valid critiques were patched into the TDD implementation plan.
- Pilot review initially rejected fixture-only evidence; fixed by replacing fixture pilots with recorded real leading-model decompositions and independent probe-builder outputs.
- Pilot rereview rejected generic endpoint-reversal probe controls; fixed by adding gate coverage for protected/generated provenance claims, responsibility text file-buckets, concrete import edge coverage, universal anti-fabrication/provenance coverage, self-referential contracts, and concern reference resolution; then regenerated pattern-specific planted negatives.
- Final Opus rereview verdict: PASS, saved at `docs/verification/2026-06-04-ai-first-project-decomposer-pilot-opus-final-rereview.md`.

## Verification commands

- `uv run pytest tests -q` — passed.
- `uv run ruff check . && uv run pyright` — passed.
- `/home/leonb/projects/fmc-mcp`: `uv run python -m pytest -q` — 19 passed.
- `/home/leonb/projects/leonbreukelman-engineer`: `npm run build && npm run check:links` — passed.
- `git diff --check` — passed.
- Pilot JSON validation — 2898 JSON files parsed before pruning obsolete intermediate snapshots; 652 retained final pilot JSON files parsed after pruning.

## Remaining risks and gaps

- Live Grok decomposition remains blocked by CLI/tool-loop/turn-limit behavior in this run; acceptance uses recorded Opus leading-model outputs plus Sonnet probe-builder evidence. This is recorded transparently as a non-critical execution gap, not hidden as success.
- Build Arena itself is broad; the final snapshot includes explicit verification gaps for primary source modules outside the recorded high-level decomposer component set instead of silently claiming total semantic coverage.
- The current implementation is deliberately sidecar-first and not a schema rewrite; future phases can promote these contracts into schema once the sidecar path remains stable.
- The deterministic graph still uses pragmatic AST/regex parsing rather than full tree-sitter/SCIP/CodeQL integration; the spec documents those as next-quality upgrades.

## Safe next use

The decomposer is safe to use next as a local-first, anti-fabrication-first project model generator for Build Arena planning and review. LLM-produced claims should continue to be treated as advisory until the deterministic gate and probe controls pass for the target snapshot.
