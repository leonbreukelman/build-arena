You are the required Opus certifier for the FINAL Build Arena repo change. Do NOT use tools; all evidence is embedded. Return JSON only with keys: verdict (ACCEPT or REQUEST_CHANGES), summary, blockingFindings, nonBlockingFindings, evidenceChecked.

Scope:
- Consolidate dream-lane graph import cycle anchors onto arena.architecture_fitness.import_cycles.
- Add provenanceClass labels to anchor catalog records and resolved citedEvidence, and render the label in experiment.md.
- provenanceClass is a LABEL only; it must not reject/filter dreams.
- Do not change dream_generate prompt semantics, admissibility requirements, free-text carrier/binding semantics, or architecture_fitness cycle semantics.

Evidence and implementation notes:
- Real artifact casing verification command output: projectGraph artifacts=6, sampled snake_case edge key occurrences=28, camelCase occurrences=0. Examples included docs/examples/project-model-v1-tiny.json, reports/.../project-model-v1.json, tests/fixtures/dream_admissibility/captured-project-model-v1.json.
- import_cycles behavior check with a 3-cycle returned (("pkg.a", "pkg.b", "pkg.c"),), so architecture_fitness already returns unique canonical rotations for that case; dream_admissibility still defensively canonicalizes and dedupes.
- Base->head RED proof used `git archive HEAD` checkout plus copied new tests and failed on base with ImportError for missing anchor_provenance_class.
- Focused dream-lane tests passed after final patch: `uv run pytest tests/test_dream_admissibility.py tests/test_dream_gate.py tests/test_dream_emit.py tests/test_dream_generate.py tests/test_dream_research.py tests/test_dream_run.py -q` => 49 passed.
- Full local gates passed after final patch:
  - `uv run pytest tests -q` => all tests passed with 11 skips shown in output.
  - `uv run ruff check .` => All checks passed.
  - `uv run pyright` => 0 errors, 0 warnings, 0 informations.
  - `make generated` ran; no generated files changed in git status.
- Schema update: docs/schemas/dream-v1.schema.json allows optional citedEvidence.provenanceClass enum. `make generated` touched no generated artifacts because schema/arena.yaml was not changed.
- Out-of-scope note recorded in docs/inbox/dream-lane-known-issues.md:
# Dream Lane Known Issues

- 2026-07-04 handoff: `graphStructural.high_fan_in` currently counts incoming edges of all graph kinds (`defined_in`, `imports`, `calls`, `tests`, etc.), so the signal is semantically mushy; recorded only, no code change in the cycle-anchor/provenance slice.


Current git status includes unrelated pre-existing dirty files plus certification artifacts; scoped diff below is the intended code/schema/test/doc-note change. Current status:
M AGENTS.md
 M README.md
 M arena/dream_admissibility.py
 M arena/dream_emit.py
 M arena/dream_gate.py
 M arena/issue_packager.py
 M arena/proposal_run.py
 M docs/build-arena-current-state.md
 M docs/build-arena-project-brief.md
 M docs/schemas/dream-v1.schema.json
 M tests/test_dream_admissibility.py
 M tests/test_dream_emit.py
 M tests/test_dream_gate.py
 M tests/test_issue_packaging.py
 M tests/test_project_status_docs.py
 M tests/test_proposal_run.py
?? docs/inbox/dream-lane-known-issues.md
?? reports/2026-07-04-dream-anchor-provenance-opus-cert-prompt.md
?? reports/2026-07-04-dream-anchor-provenance-opus-cert.json
?? reports/20260704T011629Z-fmc-mcp-issue-artifacts/
?? reports/20260704T013533Z-fmc-mcp-live-grok4/

Scoped diff:
```diff
diff --git a/arena/dream_admissibility.py b/arena/dream_admissibility.py
index ad2adae..ae2f12c 100644
--- a/arena/dream_admissibility.py
+++ b/arena/dream_admissibility.py
@@ -17,9 +17,14 @@ from dataclasses import dataclass
 from pathlib import Path
 from typing import Any

+from arena.architecture_fitness import import_cycles
+from arena.graph_slice import graph_slice_from_graph_data
+
 ALLOWED_DIRECTIONS = {"decrease", "increase", "passes"}
 TENSION_ANCHOR_KINDS = {"verificationGap", "priorityBacklog", "productInvariant", "graphStructural"}
 GRAPH_STRUCTURAL_KIND = "graphStructural"
+DETERMINISTIC = "deterministic"
+LLM_DERIVED = "llm_derived"
 MULTI_TAG_THRESHOLD = 5
 HIGH_FAN_IN_THRESHOLD = 3

@@ -106,6 +111,7 @@ def anchor_catalog_records(model: dict[str, Any], capability_map: dict[str, Any]
                 "anchorKind": anchor_kind,
                 "anchorId": anchor_id,
                 "contentHash": anchor_content_hash(anchor),
+                "provenanceClass": anchor_provenance_class(anchor_kind, anchor),
                 "tensionBearing": tension,
             }
             if tension:
@@ -114,6 +120,25 @@ def anchor_catalog_records(model: dict[str, Any], capability_map: dict[str, Any]
     return records


+def anchor_provenance_class(anchor_kind: str, anchor: dict[str, Any]) -> str:
+    """Classify anchor provenance by its weakest source link.
+
+    ``deterministic`` means every link from filesystem/git/AST truth to the
+    anchor content is deterministic code. Any LLM-authored link in the chain
+    makes the anchor ``llm_derived``; deterministic thresholding or lifting over
+    LLM-authored data stays ``llm_derived``.
+    """
+
+    if anchor_kind in {"graphNode", "graphEdge"}:
+        return DETERMINISTIC
+    if anchor_kind == GRAPH_STRUCTURAL_KIND:
+        structural_kind = _clean(anchor.get("kind"))
+        if structural_kind in {"high_fan_in", "import_cycle"}:
+            return DETERMINISTIC
+        return LLM_DERIVED
+    return LLM_DERIVED
+
+
 def check_dream_admissibility(
     dream: dict[str, Any], *, project_model: dict[str, Any], capability_map: dict[str, Any]
 ) -> AdmissibilityResult:
@@ -378,17 +403,13 @@ def _graph_structural_anchors(model: dict[str, Any]) -> list[dict[str, Any]]:
     edges = _get(model, "projectGraph", "edges", default=[])
     node_index = _index_by_id(nodes)
     incoming: dict[str, list[dict[str, Any]]] = defaultdict(list)
-    adjacency: dict[str, set[str]] = defaultdict(set)
     if isinstance(edges, list):
         for edge in edges:
             if not isinstance(edge, dict):
                 continue
-            source = _clean(edge.get("from_node_id")) or _clean(edge.get("fromNodeId"))
             target = _clean(edge.get("to_node_id")) or _clean(edge.get("toNodeId"))
             if target:
                 incoming[target].append(edge)
-            if source and target:
-                adjacency[source].add(target)
     for node_id, node_edges in sorted(incoming.items()):
         if len(node_edges) >= HIGH_FAN_IN_THRESHOLD:
             node = node_index.get(node_id, {})
@@ -422,21 +443,37 @@ def _graph_structural_anchors(model: dict[str, Any]) -> list[dict[str, Any]]:
                     "provenanceRefs": _string_list(profile.get("provenanceRefs")),
                 }
             )
-    for source, targets in sorted(adjacency.items()):
-        for target in sorted(targets):
-            if source < target and source in adjacency.get(target, set()):
-                anchors.append(
-                    {
-                        "id": f"graph.importCycle.{source}.{target}",
-                        "kind": "import_cycle_pair",
-                        "nodeIds": [source, target],
-                        "cycleLength": 2,
-                        "provenanceRefs": [],
-                    }
-                )
+    graph_data = _get(model, "projectGraph", default={})
+    if isinstance(graph_data, dict):
+        graph_slice = graph_slice_from_graph_data(graph_data)
+        module_by_symbol = {module.symbol: module for module in graph_slice.modules}
+        seen_cycles: set[tuple[str, ...]] = set()
+        for cycle in import_cycles(graph_slice):
+            canonical = _canonical_module_cycle(cycle)
+            if not canonical or canonical in seen_cycles:
+                continue
+            seen_cycles.add(canonical)
+            anchors.append(
+                {
+                    "id": "graph.importCycle." + "->".join(canonical),
+                    "kind": "import_cycle",
+                    "moduleSymbols": list(canonical),
+                    "cycleLength": len(canonical),
+                    "nodeIds": [module_by_symbol[symbol].node_id for symbol in canonical],
+                    "provenanceRefs": [],
+                }
+            )
     return anchors


+def _canonical_module_cycle(cycle: tuple[str, ...]) -> tuple[str, ...]:
+    symbols = tuple(symbol for symbol in cycle if symbol)
+    if not symbols:
+        return ()
+    rotations = [symbols[index:] + symbols[:index] for index in range(len(symbols))]
+    return min(rotations)
+
+
 def _observable_is_metric_like(value: str) -> bool:
     lowered = value.lower()
     metric_markers = (
diff --git a/arena/dream_emit.py b/arena/dream_emit.py
index 74765f2..af8d5b7 100644
--- a/arena/dream_emit.py
+++ b/arena/dream_emit.py
@@ -154,7 +154,9 @@ def _render_one(index: int, dream: dict[str, Any]) -> list[str]:
         kind = str(evidence.get("anchorKind", "")).strip()
         anchor_id = str(evidence.get("anchorId", "")).strip()
         claim = str(evidence.get("claim", "")).strip() or "current-state premise resolved"
-        lines.append(f"- {kind} `{anchor_id}` — {claim}")
+        provenance_class = str(evidence.get("provenanceClass", "")).strip()
+        provenance_suffix = f" (provenance: {provenance_class})" if provenance_class else ""
+        lines.append(f"- {kind} `{anchor_id}` — {claim}{provenance_suffix}")
     lines.extend(
         [
             "",
diff --git a/arena/dream_gate.py b/arena/dream_gate.py
index 14e69d3..ca24503 100644
--- a/arena/dream_gate.py
+++ b/arena/dream_gate.py
@@ -22,6 +22,7 @@ from jsonschema import Draft202012Validator
 from arena.capability_lift import CapabilityLiftError, validate_capability_map
 from arena.dream_admissibility import (
     admissibility_reasons,
+    anchor_provenance_class,
     build_anchor_indexes,
     check_dream_admissibility,
 )
@@ -237,6 +238,7 @@ def _evaluate_dream(
         elif content_hash != anchor_content_hash(anchor):
             reasons.append(f"citedEvidence[{index}] contentHash mismatch for {anchor_kind} {anchor_id}")
         else:
+            normalized_evidence["provenanceClass"] = anchor_provenance_class(anchor_kind, anchor)
             resolved_count += 1
         evidence_items.append(normalized_evidence)

diff --git a/docs/schemas/dream-v1.schema.json b/docs/schemas/dream-v1.schema.json
index 6ee54ce..73d7d4a 100644
--- a/docs/schemas/dream-v1.schema.json
+++ b/docs/schemas/dream-v1.schema.json
@@ -55,7 +55,8 @@
                 "anchorKind": { "enum": ["graphNode", "graphEdge", "component", "contract", "capability", "verificationGap", "nearNeighborAlternative", "priorityBacklog", "productInvariant", "graphStructural"] },
                 "anchorId": { "type": "string", "minLength": 1, "description": "MUST resolve to a real id of the named kind in the source model / capability map / computed graph-structural anchor set." },
                 "contentHash": { "type": "string", "pattern": "^[a-f0-9]{64}$" },
-                "claim": { "type": "string", "minLength": 1, "description": "The current-state tension this anchor is asserted to support." }
+                "claim": { "type": "string", "minLength": 1, "description": "The current-state tension this anchor is asserted to support." },
+                "provenanceClass": { "enum": ["deterministic", "llm_derived"], "description": "Set by the gate for resolved evidence. Label only; not an acceptance gate." }
               }
             }
           },
diff --git a/tests/test_dream_admissibility.py b/tests/test_dream_admissibility.py
index 68db39f..bdb4c61 100644
--- a/tests/test_dream_admissibility.py
+++ b/tests/test_dream_admissibility.py
@@ -5,6 +5,9 @@ from pathlib import Path
 from typing import Any

 from arena.dream_admissibility import (
+    anchor_catalog_records,
+    anchor_provenance_class,
+    build_anchor_indexes,
     check_document_admissibility,
     check_document_admissibility_from_paths,
 )
@@ -26,6 +29,108 @@ def _load(path: Path) -> dict[str, Any]:
     return payload


+def _cycle_model(edges: list[tuple[str, str]]) -> dict[str, Any]:
+    modules = {
+        "pkg.a": "node.a",
+        "pkg.b": "node.b",
+        "pkg.c": "node.c",
+    }
+    return {
+        "snapshot": {"components": [], "contracts": [], "verification_gaps": [], "near_neighbor_alternatives": []},
+        "projectGraph": {
+            "graphHash": "a" * 64,
+            "nodes": [
+                {
+                    "id": node_id,
+                    "kind": "python_module",
+                    "symbol": symbol,
+                    "label": symbol,
+                    "path": f"{symbol.replace('.', '/')}.py",
+                }
+                for symbol, node_id in modules.items()
+            ],
+            "edges": [
+                {
+                    "id": f"edge.{source}.{target}",
+                    "kind": "imports",
+                    "from_node_id": modules[source],
+                    "to_node_id": modules[target],
+                    "label": target,
+                    "provenance_refs": [],
+                }
+                for source, target in edges
+            ],
+        },
+        "iterationReadiness": {"componentProfiles": []},
+    }
+
+
+def test_graph_structural_import_cycle_anchor_detects_three_node_cycle() -> None:
+    indexes = build_anchor_indexes(_cycle_model([("pkg.a", "pkg.b"), ("pkg.b", "pkg.c"), ("pkg.c", "pkg.a")]), {})
+
+    cycle_anchors = [anchor for anchor in indexes["graphStructural"].values() if anchor["kind"] == "import_cycle"]
+
+    assert cycle_anchors == [
+        {
+            "id": "graph.importCycle.pkg.a->pkg.b->pkg.c",
+            "kind": "import_cycle",
+            "moduleSymbols": ["pkg.a", "pkg.b", "pkg.c"],
+            "cycleLength": 3,
+            "nodeIds": ["node.a", "node.b", "node.c"],
+            "provenanceRefs": [],
+        }
+    ]
+
+
+def test_graph_structural_import_cycle_anchor_preserves_two_node_parity() -> None:
+    indexes = build_anchor_indexes(_cycle_model([("pkg.a", "pkg.b"), ("pkg.b", "pkg.a")]), {})
+
+    cycle_anchors = [anchor for anchor in indexes["graphStructural"].values() if anchor["kind"] == "import_cycle"]
+
+    assert cycle_anchors == [
+        {
+            "id": "graph.importCycle.pkg.a->pkg.b",
+            "kind": "import_cycle",
+            "moduleSymbols": ["pkg.a", "pkg.b"],
+            "cycleLength": 2,
+            "nodeIds": ["node.a", "node.b"],
+            "provenanceRefs": [],
+        }
+    ]
+
+
+def test_graph_structural_import_cycle_anchor_absent_for_dag() -> None:
+    indexes = build_anchor_indexes(_cycle_model([("pkg.a", "pkg.b"), ("pkg.b", "pkg.c")]), {})
+
+    assert [anchor for anchor in indexes["graphStructural"].values() if anchor["kind"] == "import_cycle"] == []
+
+
+def test_anchor_catalog_records_include_provenance_class() -> None:
+    model = _cycle_model([("pkg.a", "pkg.b"), ("pkg.b", "pkg.c"), ("pkg.c", "pkg.a")])
+    model["iterationReadiness"]["componentProfiles"] = [
+        {
+            "componentId": "comp.many-tags",
+            "behavioralTags": ["a", "b", "c", "d", "e"],
+            "provenanceRefs": ["prov:profile"],
+        }
+    ]
+    model["snapshot"]["components"] = [{"id": "comp.snapshot", "name": "Snapshot-authored component"}]
+
+    records = anchor_catalog_records(model, {})
+    by_id = {record["anchorId"]: record for record in records}
+
+    assert by_id["graph.importCycle.pkg.a->pkg.b->pkg.c"]["provenanceClass"] == "deterministic"
+    assert by_id["graph.multiTagComponent.comp.many-tags"]["provenanceClass"] == "llm_derived"
+    assert by_id["comp.snapshot"]["provenanceClass"] == "llm_derived"
+
+
+def test_anchor_provenance_class_mapping_is_pinned() -> None:
+    assert anchor_provenance_class("graphStructural", {"kind": "import_cycle"}) == "deterministic"
+    assert anchor_provenance_class("graphStructural", {"kind": "high_fan_in"}) == "deterministic"
+    assert anchor_provenance_class("graphStructural", {"kind": "multi_tag_component"}) == "llm_derived"
+    assert anchor_provenance_class("component", {"id": "comp.snapshot"}) == "llm_derived"
+
+
 def _prompt_json(prompt: str, marker: str) -> dict[str, Any]:
     assert marker in prompt
     payload = json.loads(prompt.split(marker, 1)[1])
diff --git a/tests/test_dream_emit.py b/tests/test_dream_emit.py
index 10a62b1..e4a40b8 100644
--- a/tests/test_dream_emit.py
+++ b/tests/test_dream_emit.py
@@ -26,6 +26,7 @@ def _dream(**overrides: Any) -> dict[str, Any]:
                 "anchorId": "comp.runner",
                 "contentHash": CONTENT_HASH,
                 "claim": "The runner component owns stage orchestration.",
+                "provenanceClass": "llm_derived",
             }
         ],
         "currentStructure": {"fromCarrier": "stage execution in runner"},
@@ -75,7 +76,7 @@ def test_all_resolved_dream_renders_readable_sections(tmp_path: Path) -> None:
     assert text.startswith("# Experiment Proposals")
     assert "Advisory tier-3 experiment proposals" in text
     assert "Premised on an operator-reviewed capability map." in text
-    assert "component `comp.runner` — The runner component owns stage orchestration." in text
+    assert "component `comp.runner` — The runner component owns stage orchestration. (provenance: llm_derived)" in text
     assert "Premise confidence (mechanical): `all_resolved`" in text
     assert "Conclusion confidence (speculative/capped): `medium` (0.6)" in text
     assert "To validate, try `try an injected runner seam`; check `stage-order coverage` moves `increase`." in text
diff --git a/tests/test_dream_gate.py b/tests/test_dream_gate.py
index cc46847..37b54d4 100644
--- a/tests/test_dream_gate.py
+++ b/tests/test_dream_gate.py
@@ -150,6 +150,7 @@ def test_grounded_dream_passes_with_all_resolved(tmp_path: Path) -> None:
     accepted = result.document["dreams"][0]
     assert accepted["premiseConfidence"] == "all_resolved"
     assert accepted["targetCapabilityIds"] == [cap_map["capabilities"][0]["id"]]
+    assert accepted["citedEvidence"][0]["provenanceClass"] == "llm_derived"
     assert result.document["provenance"]["gatedBy"] == "arena.dream_gate"
```

Certify against these questions:
1. Does cycle anchor generation use the shared architecture_fitness.import_cycles without changing architecture_fitness semantics?
2. Are cycle anchors canonical/deduped with id `graph.importCycle.` + symbols joined by `->`, kind `import_cycle`, moduleSymbols, cycleLength, nodeIds, provenanceRefs=[]?
3. Is provenanceClass classification consistent with the rule: deterministic iff every source link is deterministic; any LLM-authored link makes it llm_derived? Check especially import_cycle deterministic, high_fan_in deterministic, multi_tag_component llm_derived, component/contract/capability/gap/near/backlog/invariant llm_derived.
4. Is provenanceClass only a label and not a rejection/filter gate?
5. Does gate->emit annotate resolved evidence and render the suffix without changing the premise-confidence line?
6. Did the change avoid prompt semantic changes and admissibility/free-text constraint changes?
7. Are tests adequate, including 3-cycle, 2-cycle, DAG, classification, and render/gate annotation?
