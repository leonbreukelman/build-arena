# Project graph call/inheritance + tree-sitter status — 2026-06-16

Status: implemented locally on branch `graph/call-inheritance-treesitter`; not committed.

Changed:
- Added Python `inherits` and `calls` edges using the existing `ast` path.
- Added import-resolved Python cross-file `calls` with `confidence="heuristic"`; unresolved/ambiguous/name-only targets are dropped.
- Added additive JS/TS tree-sitter extraction for classes, methods, arrow functions, `inherits`, and `calls`, while preserving existing regex JS module/function/import nodes and import edges.
- Pinned tree-sitter packages and recorded parser versions in graph metadata.
- Added regression/determinism tests and Opus Gate A/B/C review artifacts under `reports/`.

Verification:
- `make test` passed.
- `make lint` passed.
- `make typecheck` passed.
- arena-calibration graph deterministic after final fix: 810 nodes, 1526 edges, 267 calls, 109 heuristic calls, 2 inherits.
- Final arena-calibration snapshot gate passed with zero violations; intake scorecard ran with 7 findings.
- Opus Gate C follow-up verdict: `ACCEPT`, no `mustFixBeforeMerge` items.

Residual notes:
- Graph `schema_version` remains `project-graph/v0.1` even though the graph is additive-expanded with metadata/new edge kinds.
- Parser metadata is intentionally part of canonical graph JSON; parser version bumps will change graph output.
