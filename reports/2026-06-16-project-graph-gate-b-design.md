# Project Graph Gate B — Python cross-file call resolution design

## P1 checkpoint packet

CHANGED: Added Python `inherits` edges from `ast.ClassDef.bases` and same-file `calls` edges from `ast.Call`, both `confidence="deterministic"`, `derived_by="python_ast"`, and with provenance at the base/call site. Added tests for resolved and unresolved targets.
VERIFY: Focused P1 tests passed; full `tests/test_project_graph.py` passed; `ruff` and `pyright` passed; decomposer/meta/snapshot-gate tests passed; old nodes and old edge kinds are byte-identical to the baseline implementation; `arena-calibration` graph is deterministic and now has 162 `calls` / 2 `inherits`; project-model snapshot gate and intake scorecard passed.
RISK: Cross-file calls are the ambiguous part. P2 must remain heuristic, order-independent, and must not mint internal targets.

## Gate A result incorporated

Opus Gate A returned `ACCEPT_WITH_CHANGES`. Implemented/accepted constraints:
- New `calls`/`inherits` edge ids include confidence/derived_by in the hash path so future confidence variants do not collide.
- Resolution that depends on the whole graph must happen after the symbol table exists, not during one-file parse order.
- Determinism tests cover new edge paths.
- Unresolved P1 targets are dropped, not fabricated.

## Proposed P2 strategy

1. Keep Python parsing on `ast` only.
2. Add a second Python-only pass after all file/module/function/class nodes exist in `build_project_graph`.
3. The second pass reparses eligible Python files deterministically in sorted path order and builds:
   - `function_by_symbol`: existing `python_function` graph nodes by full `node.symbol`.
   - `module_by_symbol`: existing `python_module` graph nodes by full `node.symbol`.
   - `function_by_path_and_name`: existing function nodes grouped by `(path, label)` so same-file deterministic calls can be skipped/left to P1.
4. For each file, build an import alias map from AST import statements:
   - `from pkg.worker import work` maps local `work` to target symbol `pkg.worker.work` when that function node exists.
   - `from pkg import resources` maps local `resources` to module symbol `pkg.resources`, allowing `resources.get_client()` -> `pkg.resources.get_client` when that function node exists.
   - `import pkg.worker as worker` maps local `worker` to module symbol `pkg.worker`, allowing `worker.work()` -> `pkg.worker.work`.
   - `import pkg.worker` allows dotted callee `pkg.worker.work` to match an existing function symbol exactly.
   - Relative `from .worker import work` reuses existing `_resolve_python_import(...)` behavior for module normalization.
5. Traverse calls under the current function scope. For each call:
   - if P1 already resolves it as same-file deterministic, do nothing in P2.
   - if an import alias/dotted import resolves to exactly one existing `python_function` node in another file, emit `calls` with `confidence="heuristic"`, `derived_by="python_ast"`, provenance at the call site.
   - unresolved or multi-candidate calls are dropped in P2. No `external` placeholder nodes yet.
6. Edge endpoints are always existing graph nodes. No fabricated internals.
7. Edge labels are stable strings using existing source/target symbols.
8. Ordering is deterministic: sorted paths, AST source order, final graph sort by id.

## Explicit non-goals for P2

- No dynamic dispatch, type inference, or method receiver resolution beyond imported module/name calls.
- No ambiguous name-only edges in P2 unless Opus explicitly asks for them; dropping is safer and still satisfies no-fabrication.
- No downstream consumer opt-in yet; consumers can continue filtering `imports`/`tests`.

## Questions for Gate B

1. Is dropping unresolved/multi-candidate cross-file calls acceptable for this phase, or should we mint explicit external placeholder nodes?
2. Is `confidence="heuristic"` correct for all import-resolved cross-file calls, including exact full-symbol matches through imports?
3. Should ambiguous name-only matches be deferred, or should P2 emit them with `confidence="ambiguous"` when exactly one same-name function exists in the whole repo?
4. Any hidden consumer/versioning risk before implementing this second pass?
