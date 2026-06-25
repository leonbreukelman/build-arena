# Decomposer universal-concern change forensics — 2026-06-24

Status: keep-but-document.

Verdict: the evidence does **not** support “for identifying CI.” The `arena/project_decomposer_ai.py` delta in `b2aa47f` is a universal cross-cutting-concern drift repair / prompt-alignment change. Separate CI work exists in `arena/ci_workflow.py` and `tests/test_ci_workflow.py` from commit `083ce51`, unrelated to this decomposer delta.

## Required raw diff and log evidence

```text
$ git diff 871c530d207bd95b821ef195159641a5e89ef204..HEAD -- arena/project_decomposer_ai.py
diff --git a/arena/project_decomposer_ai.py b/arena/project_decomposer_ai.py
index 117cb68..8259972 100644
--- a/arena/project_decomposer_ai.py
+++ b/arena/project_decomposer_ai.py
@@ -291,6 +291,42 @@ def _is_dict_type(type_repr: str) -> bool:
     return any(member.startswith(("dict[", "Dict[")) for member in normalized.split("|"))


+def _normalise_universal_concern_id(raw_id: str) -> str | None:
+    normalised = re.sub(r"[^a-z0-9]+", "_", raw_id.lower()).strip("_")
+    if normalised in UNIVERSAL_CONCERNS:
+        return normalised
+    for prefix in ("ccc_", "concern_"):
+        if normalised.startswith(prefix) and normalised.removeprefix(prefix) in UNIVERSAL_CONCERNS:
+            return normalised.removeprefix(prefix)
+    return None
+
+
+def _normalise_cross_cutting_concerns(
+    concerns: list[CrossCuttingConcern], components: list[Component]
+) -> list[CrossCuttingConcern]:
+    provenance_by_component = {component.id: list(component.provenance_refs) for component in components}
+    for concern in concerns:
+        canonical = _normalise_universal_concern_id(concern.id)
+        if concern.category not in UNIVERSAL_CONCERNS and canonical is not None:
+            _LOG.warning(
+                "Canonicalized universal concern category from id",
+                extra={"concern_id": concern.id, "old_category": concern.category, "new_category": canonical},
+            )
+            concern.category = canonical
+        if concern.category not in UNIVERSAL_CONCERNS or concern.provenance_refs:
+            continue
+        refs: list[str] = []
+        for component_id in concern.component_ids:
+            refs.extend(provenance_by_component.get(component_id, []))
+        concern.provenance_refs = list(dict.fromkeys(ref for ref in refs if ref))
+        if concern.provenance_refs:
+            _LOG.warning(
+                "Backfilled universal concern provenance from covered components",
+                extra={"concern_id": concern.id, "category": concern.category, "count": len(concern.provenance_refs)},
+            )
+    return concerns
+
+
 def _coerce_dataclass(cls: type, item: Any, *, collection: str, index: int) -> Any:
     """Build a dataclass from a model-produced dict, fail-closed on identity gaps.

@@ -348,42 +384,6 @@ def _coerce_list(cls: type, raw: dict[str, Any], canonical: str) -> list[Any]:
     ]


-def _normalise_universal_concern_id(raw_id: str) -> str | None:
-    normalised = re.sub(r"[^a-z0-9]+", "_", raw_id.lower()).strip("_")
-    if normalised in UNIVERSAL_CONCERNS:
-        return normalised
-    for prefix in ("ccc_", "concern_"):
-        if normalised.startswith(prefix) and normalised.removeprefix(prefix) in UNIVERSAL_CONCERNS:
-            return normalised.removeprefix(prefix)
-    return None
-
-
-def _normalise_cross_cutting_concerns(
-    concerns: list[CrossCuttingConcern], components: list[Component]
-) -> list[CrossCuttingConcern]:
-    provenance_by_component = {component.id: list(component.provenance_refs) for component in components}
-    for concern in concerns:
-        canonical = _normalise_universal_concern_id(concern.id)
-        if concern.category not in UNIVERSAL_CONCERNS and canonical is not None:
-            _LOG.warning(
-                "Canonicalized universal concern category from id",
-                extra={"concern_id": concern.id, "old_category": concern.category, "new_category": canonical},
-            )
-            concern.category = canonical
-        if concern.category not in UNIVERSAL_CONCERNS or concern.provenance_refs:
-            continue
-        refs: list[str] = []
-        for component_id in concern.component_ids:
-            refs.extend(provenance_by_component.get(component_id, []))
-        concern.provenance_refs = list(dict.fromkeys(ref for ref in refs if ref))
-        if concern.provenance_refs:
-            _LOG.warning(
-                "Backfilled universal concern provenance from covered components",
-                extra={"concern_id": concern.id, "category": concern.category, "count": len(concern.provenance_refs)},
-            )
-    return concerns
-
-
 def _snapshot_from_model_output(
     raw: dict[str, Any],
     *,
@@ -620,15 +620,15 @@ def _decomposer_prompt(*, project_id: str, goal: str, non_goals: list[str], grap
         "Output STRICT JSON with these exact keys (no markdown):\n"
         '{\n'
         '  "model_id": str, "project_id": str, "goal": str, "non_goals": [str],\n'
-        '  "components": [{"id": str, "name": str, "responsibility": str (>=8 words, a semantic responsibility not a file list),\n'
+        '  "components": [{"id": str, "name": str, "responsibility": str (>=6 words, a semantic responsibility not a file list),\n'
         '     "owned_node_ids": [node_id from the list below], "provenance_refs": [prov id from a node you own],\n'
         '     "contract_ids": [id of a contract you declare], "check_ids": [id of an observable_check you declare],\n'
         '     "verification_gap_ids": [id of a verification_gap you declare]}],\n'
         '  "contracts": [{"id": str, "name": str, "from_component_id": component id, "to_component_id": component id,\n'
         '     "supporting_edge_ids": [edge_id from the list below connecting the two components],\n'
         '     "near_neighbor_alternative_ids": [], "provenance_refs": [prov id]}],\n'
-        '  "cross_cutting_concerns": [{"id": str, "category": str (exact canonical category), "description": str, "component_ids": [component id],\n'
-        '     "contract_ids": [], "provenance_refs": [prov id from covered components]}],\n'
+        '  "cross_cutting_concerns": [{"id": str, "category": str (for universal concerns, category MUST be exactly one of anti_fabrication|determinism|provenance|no_live_paid_api_acceptance), "description": str, "component_ids": [component id],\n'
+        '     "contract_ids": [], "provenance_refs": [prov id]}],\n'
         '  "observable_checks": [{"id": str, "description": str, "command": str, "component_ids": [component id],\n'
         '     "contract_ids": [], "provenance_refs": [prov id]}],\n'
         '  "verification_gaps": [{"id": str, "description": str, "severity": "low|medium|high|blocker",\n'
@@ -646,11 +646,13 @@ def _decomposer_prompt(*, project_id: str, goal: str, non_goals: list[str], grap
         "- Every contract must connect TWO DISTINCT components (from_component_id != to_component_id) and cite at least "
         "one supporting_edge_id from the edges below whose endpoints map to those two components. A self-referential "
         "contract or one with no supporting edge fails the gate.\n"
-        "- Include the universal cross_cutting_concerns with category EXACTLY one of: anti_fabrication, "
-        "determinism, provenance, no_live_paid_api_acceptance. Do not put thematic labels such as "
-        "integrity, reliability, traceability, or compliance in category. Each universal concern must cover "
-        "all components and include at least one provenance_refs entry copied from a covered component. Also "
-        "include protected_surface_integrity and generated_artifact_integrity if such surfaces exist.\n"
+        "- Include the universal cross_cutting_concerns: anti_fabrication, determinism, provenance, "
+        "no_live_paid_api_acceptance (each covering all components), plus protected_surface_integrity and "
+        "generated_artifact_integrity if such surfaces exist. For each universal concern, category MUST be exactly one of "
+        "anti_fabrication, determinism, provenance, no_live_paid_api_acceptance. Do not use thematic labels such as integrity, "
+        "reliability, traceability, or compliance in category. Example: {\"id\": \"concern.anti-fabrication\", "
+        "\"category\": \"anti_fabrication\", \"component_ids\": [\"component.example\"], \"contract_ids\": [], "
+        "\"provenance_refs\": [\"prov:example\"]}.\n"
         "- Provide at least one observable_check.\n"
         "- HELD-OUT PROBES: you have no probe-execution artifacts, so do NOT claim probe pass/fail. Instead record at "
         "least one verification_gap whose description mentions 'probe' and one of: 'semantic', 'independent', "
```
```text
$ git log --oneline 871c530d207bd95b821ef195159641a5e89ef204..HEAD -- arena/project_decomposer_ai.py
b2aa47f feat: publish dream proposer package
```

## Characterization of sub-changes

### 1. Normalizer relocation is a pure move in the b2aa diff

The functions `_normalise_universal_concern_id` and `_normalise_cross_cutting_concerns` moved above `_coerce_dataclass`, but the bodies are byte-identical between the baseline copy and current copy.

```text
$ python3 moved-function-byte-identity-check
$ python3 moved-function-byte-identity-check
old_lines 34
new_lines 34
byte_identical True
old_sha256 5d5f20caae0503d73fdcb6e53f0d9ffb8287670ce848157edbf734c28a5ac8e8
new_sha256 5d5f20caae0503d73fdcb6e53f0d9ffb8287670ce848157edbf734c28a5ac8e8
```

Current function body evidence:

```text
arena/project_decomposer_ai.py excerpts
--- arena/project_decomposer_ai.py:294-327 ---
294|def _normalise_universal_concern_id(raw_id: str) -> str | None:
295|    normalised = re.sub(r"[^a-z0-9]+", "_", raw_id.lower()).strip("_")
296|    if normalised in UNIVERSAL_CONCERNS:
297|        return normalised
298|    for prefix in ("ccc_", "concern_"):
299|        if normalised.startswith(prefix) and normalised.removeprefix(prefix) in UNIVERSAL_CONCERNS:
300|            return normalised.removeprefix(prefix)
301|    return None
302|
303|
304|def _normalise_cross_cutting_concerns(
305|    concerns: list[CrossCuttingConcern], components: list[Component]
306|) -> list[CrossCuttingConcern]:
307|    provenance_by_component = {component.id: list(component.provenance_refs) for component in components}
308|    for concern in concerns:
309|        canonical = _normalise_universal_concern_id(concern.id)
310|        if concern.category not in UNIVERSAL_CONCERNS and canonical is not None:
311|            _LOG.warning(
312|                "Canonicalized universal concern category from id",
313|                extra={"concern_id": concern.id, "old_category": concern.category, "new_category": canonical},
314|            )
315|            concern.category = canonical
316|        if concern.category not in UNIVERSAL_CONCERNS or concern.provenance_refs:
317|            continue
318|        refs: list[str] = []
319|        for component_id in concern.component_ids:
320|            refs.extend(provenance_by_component.get(component_id, []))
321|        concern.provenance_refs = list(dict.fromkeys(ref for ref in refs if ref))
322|        if concern.provenance_refs:
323|            _LOG.warning(
324|                "Backfilled universal concern provenance from covered components",
325|                extra={"concern_id": concern.id, "category": concern.category, "count": len(concern.provenance_refs)},
326|            )
327|    return concerns
--- arena/project_decomposer_ai.py:387-402 ---
387|def _snapshot_from_model_output(
388|    raw: dict[str, Any],
389|    *,
390|    project_id: str,
391|    project_root: str,
392|    goal: str,
393|    non_goals: list[str],
394|    graph_hash: str,
395|    prompt_hash: str,
396|) -> ProjectModelSnapshot:
397|    if not isinstance(raw, dict):
398|        raise ValueError(f"model output must be a JSON object, got {type(raw).__name__}")
399|    components = _coerce_list(Component, raw, "components")
400|    cross_cutting_concerns = _normalise_cross_cutting_concerns(
401|        _coerce_list(CrossCuttingConcern, raw, "cross_cutting_concerns"), components
402|    )
--- arena/project_decomposer_ai.py:620-655 ---
620|        "Output STRICT JSON with these exact keys (no markdown):\n"
621|        '{\n'
622|        '  "model_id": str, "project_id": str, "goal": str, "non_goals": [str],\n'
623|        '  "components": [{"id": str, "name": str, "responsibility": str (>=6 words, a semantic responsibility not a file list),\n'
624|        '     "owned_node_ids": [node_id from the list below], "provenance_refs": [prov id from a node you own],\n'
625|        '     "contract_ids": [id of a contract you declare], "check_ids": [id of an observable_check you declare],\n'
626|        '     "verification_gap_ids": [id of a verification_gap you declare]}],\n'
627|        '  "contracts": [{"id": str, "name": str, "from_component_id": component id, "to_component_id": component id,\n'
628|        '     "supporting_edge_ids": [edge_id from the list below connecting the two components],\n'
629|        '     "near_neighbor_alternative_ids": [], "provenance_refs": [prov id]}],\n'
630|        '  "cross_cutting_concerns": [{"id": str, "category": str (for universal concerns, category MUST be exactly one of anti_fabrication|determinism|provenance|no_live_paid_api_acceptance), "description": str, "component_ids": [component id],\n'
631|        '     "contract_ids": [], "provenance_refs": [prov id]}],\n'
632|        '  "observable_checks": [{"id": str, "description": str, "command": str, "component_ids": [component id],\n'
633|        '     "contract_ids": [], "provenance_refs": [prov id]}],\n'
634|        '  "verification_gaps": [{"id": str, "description": str, "severity": "low|medium|high|blocker",\n'
635|        '     "component_ids": [component id], "contract_ids": [], "provenance_refs": [prov id]}],\n'
636|        '  "near_neighbor_alternatives": [{"id": str, "target_id": component id, "alternative": str,\n'
637|        '     "why_not_primary": str, "provenance_refs": [prov id]}]\n'
638|        '}\n'
639|        "Rules: reuse only node_id/edge_id/prov ids shown below; never invent ids.\n"
640|        "- EVERY primary module node listed below must be owned by exactly one component "
641|        "(or, if you cannot responsibly place it, covered by a verification_gap whose provenance_refs "
642|        "includes that node's prov id). Uncovered primary modules fail the inventory gate.\n"
643|        "- Every component must own >=1 node, cite a provenance id from a node it owns, and declare >=1 of contract/check/gap.\n"
644|        "- Decompose into MULTIPLE components (one per distinct responsibility); a single component covering the whole "
645|        "repo is a file-bucket and fails the gate. Each listed primary module must be owned by some component.\n"
646|        "- Every contract must connect TWO DISTINCT components (from_component_id != to_component_id) and cite at least "
647|        "one supporting_edge_id from the edges below whose endpoints map to those two components. A self-referential "
648|        "contract or one with no supporting edge fails the gate.\n"
649|        "- Include the universal cross_cutting_concerns: anti_fabrication, determinism, provenance, "
650|        "no_live_paid_api_acceptance (each covering all components), plus protected_surface_integrity and "
651|        "generated_artifact_integrity if such surfaces exist. For each universal concern, category MUST be exactly one of "
652|        "anti_fabrication, determinism, provenance, no_live_paid_api_acceptance. Do not use thematic labels such as integrity, "
653|        "reliability, traceability, or compliance in category. Example: {\"id\": \"concern.anti-fabrication\", "
654|        "\"category\": \"anti_fabrication\", \"component_ids\": [\"component.example\"], \"contract_ids\": [], "
655|        "\"provenance_refs\": [\"prov:example\"]}.\n"
```

### 2. Prompt responsibility minimum changed from >=8 words to >=6 words

Raw diff evidence is embedded above. Current prompt line evidence is `arena/project_decomposer_ai.py:623`:

```text
623|        '  "components": [{"id": str, "name": str, "responsibility": str (>=6 words, a semantic responsibility not a file list),\n'
```

Gate evidence: the deterministic gate rejects fewer than six words, not fewer than eight.

```text
arena/project_model_gate.py excerpt
--- arena/project_model_gate.py:68-75 ---
68|    for component in snapshot_obj.components:
69|        loc = f"components[{component.id}]"
70|        lower_name = component.name.lower().replace("-", " ").replace("_", " ")
71|        if any(term in lower_name.split() for term in VAGUE_TERMS) or component.id.split(".")[-1] in VAGUE_TERMS:
72|            add("component_measurability", f"Component {component.id} has a vague name.", loc)
73|        if len(component.responsibility.split()) < 6:
74|            add("component_measurability", f"Component {component.id} has an underspecified responsibility.", loc)
75|        if _looks_like_responsibility_file_bucket(component.responsibility):
```

Assessment: this weakens the prompt relative to the prior `>=8` instruction, but it aligns the prompt with the actual deterministic gate. It is not CI-related. The test suite contains a negative that a five-word responsibility still fails and is not padded.

```text
tests/test_project_decomposer_live_repair.py responsibility/backfill excerpts
--- tests/test_project_decomposer_live_repair.py:60-107 ---
60|def test_recorded_live_output_repairs_universal_concern_provenance(tmp_path: Path, caplog) -> None:
61|    repo = tmp_path / "live-drift"
62|    repo.mkdir()
63|    _write_contract_repo(repo)
64|    artifacts = tmp_path / "artifacts"
65|    raw = _fixture_raw(repo, artifacts, "live-drift")
66|    components = raw["components"]
67|    assert isinstance(components, list)
68|    target_component = components[0]
69|    assert isinstance(target_component, dict)
70|    target_component["name"] = "Reporting Module"
71|    target_component["responsibility"] = "Generate reporting summaries for validation decisions"
72|    concerns = raw["cross_cutting_concerns"]
73|    assert isinstance(concerns, list)
74|    drifted_concern_ids: set[str] = set()
75|    for concern in concerns:
76|        assert isinstance(concern, dict)
77|        if concern["category"] in UNIVERSAL_CATEGORIES:
78|            concern["id"] = f"ccc:{concern['category']}"
79|            concern["provenance_refs"] = []
80|            drifted_concern_ids.add(str(concern["id"]))
81|    recorded_path = tmp_path / "recorded-live-drift.json"
82|    recorded_path.write_text(json.dumps(raw, indent=2), encoding="utf-8")
83|
84|    caplog.set_level(logging.WARNING, logger="arena.project_decomposer_ai")
85|    result = build_project_model_snapshot(
86|        repo,
87|        artifacts,
88|        project_id="live-drift",
89|        llm_mode="recorded",
90|        model_output_path=recorded_path,
91|        overwrite=True,
92|    )
93|
94|    assert result.gate_report.passed is True
95|    repaired_component = next(component for component in result.snapshot.components if component.id == target_component["id"])
96|    assert repaired_component.responsibility == "Generate reporting summaries for validation decisions"
97|    repaired_concerns = {concern.id: concern for concern in result.snapshot.cross_cutting_concerns}
98|    assert all(repaired_concerns[concern_id].provenance_refs for concern_id in drifted_concern_ids)
99|    assert any("Backfilled universal concern provenance" in record.message for record in caplog.records)
100|    persisted_raw = json.loads((result.snapshot_dir / "model-outputs" / "decomposer.raw.json").read_text(encoding="utf-8"))
101|    assert persisted_raw["components"][0]["responsibility"] == "Generate reporting summaries for validation decisions"
102|    assert all(
103|        concern["provenance_refs"] == []
104|        for concern in persisted_raw["cross_cutting_concerns"]
105|        if concern["id"] in drifted_concern_ids
106|    )
107|
--- tests/test_project_decomposer_live_repair.py:109-153 ---
109|def test_recorded_live_output_canonicalizes_universal_concern_category_from_exact_id(tmp_path: Path, caplog) -> None:
110|    repo = tmp_path / "thematic-category"
111|    repo.mkdir()
112|    _write_contract_repo(repo)
113|    artifacts = tmp_path / "artifacts"
114|    raw = _fixture_raw(repo, artifacts, "thematic-category")
115|    thematic = {
116|        "anti_fabrication": "integrity",
117|        "determinism": "reliability",
118|        "provenance": "traceability",
119|        "no_live_paid_api_acceptance": "compliance",
120|    }
121|    concerns = raw["cross_cutting_concerns"]
122|    assert isinstance(concerns, list)
123|    for concern in concerns:
124|        assert isinstance(concern, dict)
125|        if concern["category"] in thematic:
126|            canonical = str(concern["category"])
127|            concern["id"] = f"ccc:{canonical}"
128|            concern["category"] = thematic[canonical]
129|            concern["provenance_refs"] = []
130|    recorded_path = tmp_path / "recorded-thematic-category.json"
131|    recorded_path.write_text(json.dumps(raw, indent=2), encoding="utf-8")
132|
133|    caplog.set_level(logging.WARNING, logger="arena.project_decomposer_ai")
134|    result = build_project_model_snapshot(
135|        repo,
136|        artifacts,
137|        project_id="thematic-category",
138|        llm_mode="recorded",
139|        model_output_path=recorded_path,
140|        overwrite=True,
141|    )
142|
143|    assert result.gate_report.passed is True
144|    categories = {concern.category for concern in result.snapshot.cross_cutting_concerns}
145|    assert set(thematic) <= categories
146|    assert any("Canonicalized universal concern category" in record.message for record in caplog.records)
147|    assert any("Backfilled universal concern provenance" in record.message for record in caplog.records)
148|    persisted_raw = json.loads((result.snapshot_dir / "model-outputs" / "decomposer.raw.json").read_text(encoding="utf-8"))
149|    persisted_concerns = persisted_raw["cross_cutting_concerns"]
150|    assert isinstance(persisted_concerns, list)
151|    drifted = [concern for concern in persisted_concerns if isinstance(concern, dict) and str(concern["id"]).startswith("ccc:")]
152|    assert {concern["category"] for concern in drifted} == set(thematic.values())
153|    assert all(concern["provenance_refs"] == [] for concern in drifted)
--- tests/test_project_decomposer_live_repair.py:211-277 ---
211|def test_recorded_live_output_does_not_backfill_non_universal_concern(tmp_path: Path) -> None:
212|    repo = tmp_path / "non-universal-empty"
213|    repo.mkdir()
214|    _write_contract_repo(repo)
215|    artifacts = tmp_path / "artifacts"
216|    raw = _fixture_raw(repo, artifacts, "non-universal-empty")
217|    concerns = raw["cross_cutting_concerns"]
218|    components = raw["components"]
219|    assert isinstance(concerns, list)
220|    assert isinstance(components, list)
221|    component_ids = [component["id"] for component in components if isinstance(component, dict)]
222|    concerns.append(
223|        {
224|            "id": "concern.custom-integrity",
225|            "category": "custom_integrity",
226|            "description": "A non-universal concern with deliberately missing provenance.",
227|            "component_ids": component_ids,
228|            "contract_ids": [],
229|            "provenance_refs": [],
230|        }
231|    )
232|    recorded_path = tmp_path / "recorded-non-universal-empty.json"
233|    recorded_path.write_text(json.dumps(raw, indent=2), encoding="utf-8")
234|
235|    result = build_project_model_snapshot(
236|        repo,
237|        artifacts,
238|        project_id="non-universal-empty",
239|        llm_mode="recorded",
240|        model_output_path=recorded_path,
241|        overwrite=True,
242|    )
243|
244|    custom = next(concern for concern in result.snapshot.cross_cutting_concerns if concern.id == "concern.custom-integrity")
245|    assert custom.provenance_refs == []
246|    assert result.gate_report.passed is False
247|    assert any(violation.location == "cross_cutting_concerns[concern.custom-integrity]" for violation in result.gate_report.violations)
248|
249|
250|def test_recorded_live_output_does_not_pad_borderline_responsibility(tmp_path: Path) -> None:
251|    repo = tmp_path / "borderline-short"
252|    repo.mkdir()
253|    _write_contract_repo(repo)
254|    artifacts = tmp_path / "artifacts"
255|    raw = _fixture_raw(repo, artifacts, "borderline-short")
256|    components = raw["components"]
257|    assert isinstance(components, list)
258|    first_component = components[0]
259|    assert isinstance(first_component, dict)
260|    first_component["name"] = "Reporting Module"
261|    first_component["responsibility"] = "Generate reports and confidence summaries"
262|    recorded_path = tmp_path / "recorded-borderline-short.json"
263|    recorded_path.write_text(json.dumps(raw, indent=2), encoding="utf-8")
264|
265|    result = build_project_model_snapshot(
266|        repo,
267|        artifacts,
268|        project_id="borderline-short",
269|        llm_mode="recorded",
270|        model_output_path=recorded_path,
271|        overwrite=True,
272|    )
273|
274|    assert result.gate_report.passed is False
275|    assert result.snapshot.components[0].responsibility == "Generate reports and confidence summaries"
276|    assert any(violation.gate == "component_measurability" for violation in result.gate_report.violations)
```

### 3. Universal concern category prompt rewrite + provenance backfill

Prompt evidence in the diff shows the category instruction changed from generic “exact canonical category” to enumerating the four universal categories and warning against thematic labels. Current prompt evidence appears in `arena/project_decomposer_ai.py:630-655` in the excerpt above.

The provenance backfill behavior is in `_normalise_cross_cutting_concerns`: only universal concerns with empty `provenance_refs` are backfilled from provenance refs of covered components. This function predates `b2aa` via lineage commit `1c8d8c8`; in the `b2aa` diff it is moved without behavior change.

## Intent trace

```text
$ git log --oneline 871c530d207bd95b821ef195159641a5e89ef204..HEAD
08d67d6 Merge pull request #51 from leonbreukelman/dream-proposer-tier3-package
b2aa47f feat: publish dream proposer package
58e69eb Merge pull request #50 from leonbreukelman/ci-workflow-proposer
083ce51 feat: add deterministic CI workflow proposal domain
```
```text
$ git show 1c8d8c8 --stat && git show -s --format=fuller 1c8d8c8
commit 1c8d8c8e4914852c7a1196e9d8549db2c3d66974
Author: Leon Breukelman <leon.breukelman@gmail.com>
Date:   Sun Jun 21 19:04:49 2026 -0500

    Fix live decomposer universal concern drift

 arena/project_decomposer_ai.py               |  62 +++++-
 tests/test_project_decomposer_live_repair.py | 276 +++++++++++++++++++++++++++
 2 files changed, 330 insertions(+), 8 deletions(-)

commit 1c8d8c8e4914852c7a1196e9d8549db2c3d66974
Author:     Leon Breukelman <leon.breukelman@gmail.com>
AuthorDate: Sun Jun 21 19:04:49 2026 -0500
Commit:     Leon Breukelman <leon.breukelman@gmail.com>
CommitDate: Sun Jun 21 19:04:49 2026 -0500

    Fix live decomposer universal concern drift
```
```text
$ git grep selected universal/cross_cutting intent lines
$ git grep -n -i -E "universal concern|cross_cutting|provenance backfill|>=6 words|>=8 words" -- docs AGENTS.md
docs/specs/2026-06-04-ai-first-project-decomposer-spec.md:1021:   - Universal concerns exist for determinism, provenance, anti-fabrication, and no-live-paid-API acceptance.
docs/specs/2026-06-07-meta-decomposer-functional-spec.md:162:A cross-cutting concern is a model-level invariant that applies across components, contracts, roots, or the whole workspace. It does not own source nodes. It records the concern category, affected components/contracts, provenance, and triggered-by evidence. Existing universal concerns remain required even when components are root-local.
docs/status/2026-06-17-fmc-mcp-schema-fix-status.md:5:Scope: Build Arena decomposer schema/prompt fix for Grok 4.3 high-reasoning universal `cross_cutting_concerns` category/id drift, followed by a production-profile intake scorecard. No proposal/promotion.
docs/status/2026-06-17-fmc-mcp-schema-fix-status.md:8:- `arena/project_decomposer_ai.py`: prompt hardening plus narrow in-memory universal concern category canonicalization from exact known-universal concern id.
docs/status/INDEX.md:21:- `2026-06-17-fmc-mcp-schema-fix-status.md` — point-in-time record for the Grok 4.3 high-reasoning universal concern category/id schema fix and decomposition-only rerun.

$ git grep -n -i -E "\\bCI\\b|ci_workflow|ci workflow|github actions|workflow" -- docs/specs docs/decisions docs/status AGENTS.md
docs/specs/2026-06-04-ai-first-project-decomposer-spec.md:111:   - It does not build a rich graph of symbols, imports, tests, docs, configs, issue links, generated/oracle surfaces, and workflow relationships.
docs/specs/2026-06-04-ai-first-project-decomposer-spec.md:118:   - The current decomposer does not use Tree-sitter/AST, import graphs, code intelligence indexes, doc-to-code links, or config/test/workflow relations as first-class evidence.
docs/specs/2026-06-04-ai-first-project-decomposer-spec.md:127:6. Weak held-out probe workflow.
docs/specs/2026-06-04-ai-first-project-decomposer-spec.md:165:  - symbols/imports/references/checks/workflows edges
docs/specs/2026-06-04-ai-first-project-decomposer-spec.md:231:- Build/CI/workflow commands and their owning configs.
docs/specs/2026-06-04-ai-first-project-decomposer-spec.md:347:- `kind`: one of file, directory, module, package, symbol, test, check, doc, doc_section, config, workflow, command, issue_ref, generated_surface, protected_surface, oracle_surface, runtime_surface, concept, external_dependency, synthetic_group.
docs/specs/2026-06-04-ai-first-project-decomposer-spec.md:449:- `kind`: extensible vocabulary such as runtime, library, CLI, data_model, orchestrator, adapter, verifier, scorer, workflow, test_harness, documentation_system, configuration_system, governance_process, generated_artifact_system, mixed_with_gap. Build-Arena-specific terms are optional, not required for unrelated repos.
docs/specs/2026-06-04-ai-first-project-decomposer-spec.md:1377:The first accepted implementation may use deterministic fixture LLM outputs in tests and live Grok/Opus only in manual pilot/review artifacts. Quality is stabilized with leading models; CI/acceptance remains local and deterministic.
docs/specs/2026-06-07-meta-decomposer-functional-spec.md:300:- a CI/task/workspace declaration that explicitly invokes tasks in more than one root;
docs/specs/2026-06-07-meta-decomposer-functional-spec.md:319:- CI workflow steps mapped to a root
docs/specs/2026-06-07-weighted-project-intake-prioritization.md:39:- OpenSSF Scorecard: security/repository-health checks include branch protection, CI tests, code review, dependency update tooling, maintained status, SAST, security policy, token permissions, dangerous workflows, and known vulnerabilities. Sources: <https://scorecard.dev/> and <https://github.com/ossf/scorecard/blob/main/docs/checks.md>.
docs/specs/2026-06-07-weighted-project-intake-prioritization.md:132:Purpose: can changes be proven locally and in CI?
docs/specs/2026-06-07-weighted-project-intake-prioritization.md:138:- CI exists and maps to local commands.
docs/specs/2026-06-07-weighted-project-intake-prioritization.md:145:- CI exists but local docs point to different commands.
docs/specs/2026-06-07-weighted-project-intake-prioritization.md:210:- Workflow token permissions are least-privilege.
docs/specs/2026-06-07-weighted-project-intake-prioritization.md:216:- GitHub Actions use broad token permissions unnecessarily.
docs/specs/2026-06-07-weighted-project-intake-prioritization.md:217:- Known vulnerabilities or dangerous workflows are unresolved without explicit acceptance.
docs/specs/2026-06-07-weighted-project-intake-prioritization.md:401:- Risky use: sole source of project truth, because it is weaker than docs-as-code for review, versioning, CI checks, and agent grounding.
docs/specs/2026-06-21-proposal-run-and-emit.md:26:- panels, UI, dashboards, Docker, or CI;
docs/status/2026-06-14-progress-timeline-and-production-readiness-audit.md:197:- Remote/CI consumers do not have the latest state because both Build Arena and `fmc-mcp` are ahead of `origin/main` by one commit.
```

PR #51 body proves the dream package PR also intentionally published prior local reports and pairwise artifacts, but it does not describe the decomposer delta as CI work:

```text
$ gh pr view 51 --json number,title,body,mergeCommit,headRefName,baseRefName,state,url
number: 51
title: Publish dream proposer package
state: MERGED
mergeCommit: 08d67d6db78f1ce5f6d6d8eeeb875182417dc9a3
headRefName: dream-proposer-tier3-package
body excerpt:
- add the tier-3 advisory Dream Proposer lane (`capability_lift`, `dream_generate`, `dream_research`, `dream_gate`, `dream_emit`, `dream_run`) with schemas, docs, wiki, and tests
- publish prior local reports/verification artifacts and pairwise reranker design/status artifacts
- add `.env` / `.env.*` to `.gitignore` so local secrets stay out of git
No PR body line says the decomposer delta was for CI discovery.
```

## CI reconciliation

The decomposer diff contains no `CI`, `workflow`, or `github actions` text. The separate real CI work is commit `083ce51 feat: add deterministic CI workflow proposal domain`, which touched `arena/ci_workflow.py` and `tests/test_ci_workflow.py`.

```text
$ decomposer CI grep + CI file log
$ git diff 871c530d207bd95b821ef195159641a5e89ef204..HEAD -- arena/project_decomposer_ai.py | grep -niE "\\bCI\\b|workflow|github actions" || true
$ git log --oneline 871c530d207bd95b821ef195159641a5e89ef204..HEAD -- arena/ci_workflow.py tests/test_ci_workflow.py
083ce51 feat: add deterministic CI workflow proposal domain
```

CI implementation excerpts:

```text
arena/ci_workflow.py excerpts
--- arena/ci_workflow.py:12-16 ---
12|CI_WORKFLOW_TARGET = ".github/workflows/ci.yml"
13|_PYTHON_PACKAGE_MANAGERS = {"uv", "poetry", "pip"}
14|
15|
16|@dataclass(frozen=True)
--- arena/ci_workflow.py:46-87 ---
46|def canonical_ci_text(inputs: CiInputs) -> str:
47|    if inputs.test_command is None:
48|        raise ValueError("cannot render CI workflow without a detected test command")
49|
50|    lines = [
51|        "name: CI",
52|        "",
53|        "on:",
54|        "  pull_request:",
55|        "  push:",
56|        f"    branches: [{json.dumps(inputs.default_branch)}]",
57|        "",
58|        "jobs:",
59|        "  ci:",
60|        "    runs-on: ubuntu-latest",
61|        "    steps:",
62|    ]
63|    _append_uses_step(lines, "Check out repository", "actions/checkout@v4")
64|
65|    if _needs_python_setup(inputs):
66|        with_items: tuple[tuple[str, str], ...] = ()
67|        if inputs.python_version:
68|            with_items = (("python-version", inputs.python_version),)
69|        _append_uses_step(lines, "Set up Python", "actions/setup-python@v5", with_items)
70|
71|    if inputs.package_manager == "uv":
72|        _append_uses_step(lines, "Set up uv", "astral-sh/setup-uv@v5")
73|    elif inputs.package_manager == "poetry":
74|        _append_run_step(lines, "Set up Poetry", ("pipx install poetry",))
75|    elif inputs.package_manager == "npm":
76|        _append_uses_step(lines, "Set up Node.js", "actions/setup-node@v4")
77|
78|    if inputs.install_commands:
79|        _append_run_step(lines, "Install dependencies", inputs.install_commands)
80|
81|    _append_run_step(lines, "Run tests", (inputs.test_command,))
82|    if inputs.lint_commands:
83|        _append_run_step(lines, "Run lint", inputs.lint_commands)
84|    if inputs.typecheck_commands:
85|        _append_run_step(lines, "Run typecheck", inputs.typecheck_commands)
86|
87|    return "\n".join(lines) + "\n"
--- arena/ci_workflow.py:94-116 ---
94|def check_ci_workflow(repo: str | Path) -> dict[str, Any]:
95|    root = Path(repo).resolve()
96|    inputs = detect_ci_inputs(root)
97|    target = root / ci_workflow_target()
98|    if inputs.test_command is None:
99|        return {"ok": False, "reason": "missing_test_command", "target": ci_workflow_target()}
100|    try:
101|        expected = canonical_ci_text(inputs)
102|    except ValueError as exc:
103|        return {"ok": False, "reason": str(exc), "target": ci_workflow_target()}
104|    try:
105|        actual = target.read_text(encoding="utf-8")
106|    except FileNotFoundError:
107|        return {"ok": False, "reason": "missing_workflow", "target": ci_workflow_target(), "expectedDigest": ci_digest(expected)}
108|    if actual != expected:
109|        return {
110|            "ok": False,
111|            "reason": "workflow_drift",
112|            "target": ci_workflow_target(),
113|            "expectedDigest": ci_digest(expected),
114|            "actualDigest": ci_digest(actual),
115|        }
116|    return {"ok": True, "reason": "accepted", "target": ci_workflow_target(), "digest": ci_digest(expected)}
```
```text
tests/test_ci_workflow.py excerpts
--- tests/test_ci_workflow.py:8-15 ---
8|from arena.ci_workflow import (
9|    canonical_ci_text,
10|    check_ci_workflow,
11|    ci_digest,
12|    ci_workflow_target,
13|    detect_ci_inputs,
14|    main,
15|)
--- tests/test_ci_workflow.py:79-104 ---
79|def test_lint_and_typecheck_steps_only_when_tools_are_configured(tmp_path: Path) -> None:
80|    _write(
81|        tmp_path / "pyproject.toml",
82|        "\n".join(
83|            [
84|                "[project]",
85|                "requires-python = '>=3.12'",
86|                "[tool.pytest.ini_options]",
87|                "[tool.ruff]",
88|                "[tool.pyright]",
89|            ]
90|        ),
91|    )
92|    _write(tmp_path / "uv.lock", "")
93|
94|    inputs = detect_ci_inputs(tmp_path)
95|    assert inputs.lint_commands == ("uv run ruff check .",)
96|    assert inputs.typecheck_commands == ("uv run pyright",)
97|
98|    text = canonical_ci_text(inputs)
99|    assert text == canonical_ci_text(inputs)
100|    assert "uv sync --frozen" in text
101|    assert "uv run pytest" in text
102|    assert "uv run ruff check ." in text
103|    assert "uv run pyright" in text
104|    assert "mypy" not in text
--- tests/test_ci_workflow.py:130-160 ---
130|def test_check_mode_passes_for_canonical_workflow_and_fails_on_drift(tmp_path: Path) -> None:
131|    _write(tmp_path / "uv.lock", "")
132|    _write(tmp_path / "pyproject.toml", "[tool.pytest.ini_options]\n")
133|    target = tmp_path / ci_workflow_target()
134|    _write(target, canonical_ci_text(detect_ci_inputs(tmp_path)))
135|
136|    assert main(["--repo", str(tmp_path), "--check"]) == 0
137|    assert check_ci_workflow(tmp_path)["ok"] is True
138|
139|    _write(target, target.read_text(encoding="utf-8") + "# drift\n")
140|
141|    result = check_ci_workflow(tmp_path)
142|    assert result["ok"] is False
143|    assert result["reason"] == "workflow_drift"
144|    assert main(["--repo", str(tmp_path), "--check"]) == 1
145|
146|
147|def test_python_module_check_mode_exits_zero_for_canonical_workflow(tmp_path: Path) -> None:
148|    _write(tmp_path / "pyproject.toml", "[tool.pytest.ini_options]\n")
149|    _write(tmp_path / ci_workflow_target(), canonical_ci_text(detect_ci_inputs(tmp_path)))
150|
151|    result = subprocess.run(
152|        ["python3", "-m", "arena.ci_workflow", "--repo", str(tmp_path), "--check"],
153|        cwd=Path(__file__).resolve().parents[1],
154|        capture_output=True,
155|        text=True,
156|        check=False,
157|    )
158|
159|    assert result.returncode == 0
160|    assert '"ok": true' in result.stdout
```

Conclusion: the operator likely conflated the separate CI workflow proposer with the decomposer universal-concern drift repair.

## Test output

```text
$ uv run pytest tests/test_project_decomposer_ai.py tests/test_project_decomposer_live_repair.py -q
$ uv run pytest tests/test_project_decomposer_ai.py tests/test_project_decomposer_live_repair.py -q
......................                                                   [100%]
EXIT:0
```

## Coverage mapping

`tests/test_project_decomposer_ai.py` gained prompt/category-drift regression coverage in `b2aa`:

```text
tests/test_project_decomposer_ai.py added-test excerpts
--- tests/test_project_decomposer_ai.py:180-304 ---
180|def test_recorded_model_output_repairs_universal_concern_category_from_exact_id(
181|    tmp_path: Path,
182|) -> None:
183|    repo = tmp_path / "repo"
184|    repo.mkdir()
185|    _write_repo(repo)
186|    artifacts = tmp_path / "artifacts"
187|    fixture = build_project_model_snapshot(
188|        repo,
189|        artifacts,
190|        project_id="api-project",
191|        llm_mode="fixture",
192|        overwrite=True,
193|    )
194|    raw = json.loads(
195|        (fixture.snapshot_dir / "model-outputs" / "decomposer.raw.json").read_text(
196|            encoding="utf-8"
197|        )
198|    )
199|    thematic_categories = {
200|        "anti_fabrication": "integrity",
201|        "determinism": "reliability",
202|        "provenance": "traceability",
203|        "no_live_paid_api_acceptance": "compliance",
204|    }
205|    for concern in raw["cross_cutting_concerns"]:
206|        canonical = concern["category"]
207|        if canonical in thematic_categories:
208|            concern["id"] = canonical
209|            concern["category"] = thematic_categories[canonical]
210|    raw["model_id"] = "recorded-universal-concern-id-category-drift"
211|    recorded_path = tmp_path / "recorded-concern-drift.json"
212|    recorded_path.write_text(json.dumps(raw, indent=2), encoding="utf-8")
213|
214|    result = build_project_model_snapshot(
215|        repo,
216|        artifacts,
217|        project_id="api-project",
218|        llm_mode="recorded",
219|        model_output_path=recorded_path,
220|        overwrite=True,
221|    )
222|
223|    assert result.gate_report.passed is True
224|    categories = {concern.category for concern in result.snapshot.cross_cutting_concerns}
225|    assert set(thematic_categories) <= categories
226|    assert categories.isdisjoint(thematic_categories.values())
227|    persisted_raw = json.loads(
228|        (result.snapshot_dir / "model-outputs" / "decomposer.raw.json").read_text(
229|            encoding="utf-8"
230|        )
231|    )
232|    persisted_themes = {
233|        concern["category"]
234|        for concern in persisted_raw["cross_cutting_concerns"]
235|        if concern["id"] in thematic_categories
236|    }
237|    assert persisted_themes == set(thematic_categories.values())
238|
239|
240|def test_recorded_model_output_does_not_repair_unknown_concern_category(
241|    tmp_path: Path,
242|) -> None:
243|    repo = tmp_path / "repo"
244|    repo.mkdir()
245|    _write_repo(repo)
246|    artifacts = tmp_path / "artifacts"
247|    fixture = build_project_model_snapshot(
248|        repo,
249|        artifacts,
250|        project_id="api-project",
251|        llm_mode="fixture",
252|        overwrite=True,
253|    )
254|    raw = json.loads(
255|        (fixture.snapshot_dir / "model-outputs" / "decomposer.raw.json").read_text(
256|            encoding="utf-8"
257|        )
258|    )
259|    for concern in raw["cross_cutting_concerns"]:
260|        if concern["category"] == "anti_fabrication":
261|            concern["id"] = "integrity-envelope"
262|            concern["category"] = "integrity"
263|            break
264|    raw["model_id"] = "recorded-unknown-concern-category"
265|    recorded_path = tmp_path / "recorded-unknown-concern.json"
266|    recorded_path.write_text(json.dumps(raw, indent=2), encoding="utf-8")
267|
268|    result = build_project_model_snapshot(
269|        repo,
270|        artifacts,
271|        project_id="api-project",
272|        llm_mode="recorded",
273|        model_output_path=recorded_path,
274|        overwrite=True,
275|    )
276|
277|    assert result.gate_report.passed is False
278|    assert any(
279|        violation.gate == "cross_cutting_concerns"
280|        and "Missing universal concerns" in violation.message
281|        and "anti_fabrication" in violation.message
282|        for violation in result.gate_report.violations
283|    )
284|
285|
286|def test_live_decomposer_prompt_makes_universal_concern_categories_non_negotiable(
287|    tmp_path: Path,
288|) -> None:
289|    repo = tmp_path / "repo"
290|    repo.mkdir()
291|    _write_repo(repo)
292|    graph = build_project_graph(repo)
293|
294|    prompt = _decomposer_prompt(
295|        project_id="api-project",
296|        goal="decompose this repository into responsibility-bearing components",
297|        non_goals=["do not treat file buckets as final components"],
298|        graph=graph,
299|    )
300|
301|    assert "category MUST be exactly one of" in prompt
302|    assert '"category": "anti_fabrication"' in prompt
303|    assert "Do not use thematic labels such as integrity" in prompt
304|
```

Those tests assert:

- exact-id category drift from thematic labels is repaired to canonical categories;
- unknown thematic categories still fail closed;
- the prompt explicitly enumerates the canonical universal concern categories and rejects thematic labels.

`tests/test_project_decomposer_live_repair.py` is lineage coverage from `1c8d8c8`, already present at the review baseline. It asserts:

- empty universal concern provenance is backfilled from covered components;
- raw persisted model output remains unmodified with empty `provenance_refs` even though the snapshot is repaired;
- non-universal empty refs are not repaired and the gate fails;
- a five-word responsibility remains failed and is not padded.

## Quality assessment

### `>=8` -> `>=6`

Evidence:

- Diff: prompt changed from `>=8 words` to `>=6 words`.
- Gate: `arena/project_model_gate.py:73` rejects `len(component.responsibility.split()) < 6`.
- Test: `tests/test_project_decomposer_live_repair.py:250-276` keeps a five-word responsibility failed.

Determination: intended alignment to the actual gate is plausible and tested at the lower boundary; it is also a silent lowering from the previous stricter prompt. Keep it, but document it so future reviewers do not mistake the change for CI discovery.

### `provenance_refs` backfill

Evidence:

- `arena/project_decomposer_ai.py:316-325` only backfills when `concern.category in UNIVERSAL_CONCERNS` and `concern.provenance_refs` is empty.
- `tests/test_project_decomposer_live_repair.py:94-106` asserts the gate-passing snapshot has repaired refs while persisted raw output still has empty refs.
- `tests/test_project_decomposer_live_repair.py:211-247` asserts non-universal empty refs are not repaired and the gate fails.

Determination: the backfilled refs are real graph provenance refs copied from components the model already covered, not invented identifiers. But the model did not cite them on the universal concern itself, so this is a deterministic repair layer, not model citation. It softens the strict anti-fabrication/provenance posture unless clearly documented. The raw model output remains preserved for audit, which mitigates the risk.

## Recommendation

Recommendation: `keep-but-document`.

Rationale:

- Correctness: scoped decomposer tests pass.
- Intent: durable status docs and lineage commit identify universal concern category/id drift, not CI.
- Risk: provenance backfill is safe enough only if documented as deterministic repair, not as model-cited provenance.
- Action taken: add decision record `docs/decisions/2026-06-24-decomposer-universal-concern-drift.md`.

No revert branch/PR was prepared because the change is tested and intended; the unresolved decision is documentation/OPSEC cleanup, not a code revert.
