# Opus implementation review packet — fmc-mcp schema fix

## Scope
Review the implemented Build Arena schema/prompt/coercion fix for the Grok 4.3 high-reasoning universal cross_cutting_concerns category/id drift.

Task requested by Leon:
- Use Opus to plan the fix.
- Implement it.
- Have Opus review the result.
- If signed off, rerun fmc-mcp high-reasoning decomposition and compare against previous run.

## Root cause
Previous high-reasoning raw output contained universal concerns with canonical names in `id`, but thematic labels in `category`:
- id anti_fabrication, category integrity
- id determinism, category reliability
- id provenance, category traceability
- id no_live_paid_api_acceptance, category compliance

The gate keys universal concerns by `category`, so it emitted:
- Missing universal concerns: anti_fabrication, determinism, no_live_paid_api_acceptance, provenance.
- anti_fabrication coverage missing all components.
- provenance coverage missing all components.

## Opus plan artifact
`<repo>/reports/2026-06-17-fmc-mcp-schema-fix-opus-plan-retry.json`

## Implementation summary
Changed:
- `arena/project_decomposer_ai.py`
  - imports `UNIVERSAL_CONCERNS` from the gate as the single source of truth.
  - adds `_canonical_universal_concern_id(raw_id)` for exact id-based canonicalization.
  - only for `CrossCuttingConcern`, rewrites in-memory `category` to the canonical universal key when `id` exactly normalizes to a known universal concern.
  - hardens live decomposer prompt with exact category enum instructions and an example.
- `tests/test_project_decomposer_ai.py`
  - adds RED/GREEN regression proving id/category drift is repaired in-memory while raw artifact remains unchanged.
  - adds guard proving unknown thematic categories are not repaired.
  - adds prompt-hardening regression.

No changes under scorer/, verifier/, schema/, or arena/generated/.

## Verification already run
RED before implementation:
```text
uv run pytest tests/test_project_decomposer_ai.py::test_recorded_model_output_repairs_universal_concern_category_from_exact_id tests/test_project_decomposer_ai.py::test_recorded_model_output_does_not_repair_unknown_concern_category tests/test_project_decomposer_ai.py::test_live_decomposer_prompt_makes_universal_concern_categories_non_negotiable -q
F.F [100%]
```

GREEN / regression verification:
```text
uv run pytest tests/test_project_decomposer_ai.py::test_recorded_model_output_repairs_universal_concern_category_from_exact_id tests/test_project_decomposer_ai.py::test_recorded_model_output_does_not_repair_unknown_concern_category tests/test_project_decomposer_ai.py::test_live_decomposer_prompt_makes_universal_concern_categories_non_negotiable -q
... [100%]

uv run pytest tests/test_project_decomposer_ai.py -q
................ [100%]

uv run pytest tests/test_project_meta_decomposer.py -q
.............. [100%]

uv run ruff check arena/project_decomposer_ai.py tests/test_project_decomposer_ai.py
All checks passed!

git diff --check -- arena/project_decomposer_ai.py tests/test_project_decomposer_ai.py
<no output, exit 0>

uv run pyright
0 errors, 0 warnings, 0 informations

uv run pytest tests -q
........................................................................ [ 13%]
........................................................................ [ 27%]
........................sssssssssss..................................... [ 41%]
........................................................................ [ 55%]
........................................................................ [ 69%]
........................................................................ [ 83%]
........................................................................ [ 97%]
..............                                                           [100%]

uv run ruff check .
All checks passed!
```

## Git status before review
```text
## main...origin/main
 M arena/project_decomposer_ai.py
 M tests/test_project_decomposer_ai.py
?? .env
?? reports/2026-06-17-build-arena-decomposer-model-candidates-opus-prompt.md
?? reports/2026-06-17-build-arena-decomposer-model-candidates-opus-review-retry.err
?? reports/2026-06-17-build-arena-decomposer-model-candidates-opus-review-retry.json
?? reports/2026-06-17-build-arena-decomposer-model-candidates-opus-review.err
?? reports/2026-06-17-build-arena-decomposer-model-candidates-opus-review.json
?? reports/2026-06-17-build-arena-decomposer-model-candidates.md
?? reports/2026-06-17-build-arena-decomposer-model-shortlist.json
?? reports/2026-06-17-fmc-mcp-decomposition-expected-opus-prompt.md
?? reports/2026-06-17-fmc-mcp-decomposition-expected-opus-retry.err
?? reports/2026-06-17-fmc-mcp-decomposition-expected-opus-retry.json
?? reports/2026-06-17-fmc-mcp-decomposition-expected-opus.err
?? reports/2026-06-17-fmc-mcp-decomposition-expected-opus.json
?? reports/2026-06-17-fmc-mcp-decomposition-real-opus-review-prompt.md
?? reports/2026-06-17-fmc-mcp-decomposition-real-opus-review-retry.err
?? reports/2026-06-17-fmc-mcp-decomposition-real-opus-review-retry.json
?? reports/2026-06-17-fmc-mcp-decomposition-real-opus-review.err
?? reports/2026-06-17-fmc-mcp-decomposition-real-opus-review.json
?? reports/2026-06-17-fmc-mcp-decomposition-real-summary.json
?? reports/2026-06-17-fmc-mcp-decomposition-result.md
?? reports/2026-06-17-fmc-mcp-grok43-high-reasoning-preflight.json
?? reports/2026-06-17-fmc-mcp-grok43-high-vs-nonreasoning-comparison.json
?? reports/2026-06-17-fmc-mcp-grok43-high-vs-nonreasoning-opus-brief.json
?? reports/2026-06-17-fmc-mcp-grok43-high-vs-nonreasoning-opus-prompt.md
?? reports/2026-06-17-fmc-mcp-grok43-high-vs-nonreasoning-opus-review.err
?? reports/2026-06-17-fmc-mcp-grok43-high-vs-nonreasoning-opus-review.json
?? reports/2026-06-17-fmc-mcp-grok43-high-vs-nonreasoning-opus-review.normalized.json
?? reports/2026-06-17-fmc-mcp-grok43-high-vs-nonreasoning-report.md
?? reports/2026-06-17-fmc-mcp-run-prep-opus-rereview.err
?? reports/2026-06-17-fmc-mcp-run-prep-opus-rereview.json
?? reports/2026-06-17-fmc-mcp-run-prep-opus-review-retry.err
?? reports/2026-06-17-fmc-mcp-run-prep-opus-review-retry.json
?? reports/2026-06-17-fmc-mcp-run-prep-opus-review.err
?? reports/2026-06-17-fmc-mcp-run-prep-opus-review.json
?? reports/2026-06-17-fmc-mcp-run-prep-review-prompt.md
?? reports/2026-06-17-fmc-mcp-run-prep.md
?? reports/2026-06-17-fmc-mcp-schema-fix-opus-plan-prompt.md
?? reports/2026-06-17-fmc-mcp-schema-fix-opus-plan-retry.err
?? reports/2026-06-17-fmc-mcp-schema-fix-opus-plan-retry.json
?? reports/2026-06-17-fmc-mcp-schema-fix-opus-plan.err
?? reports/2026-06-17-fmc-mcp-schema-fix-opus-plan.json
?? reports/2026-06-17-model-candidate-research-raw.json
```

## Diff under review
```diff
diff --git a/arena/project_decomposer_ai.py b/arena/project_decomposer_ai.py
index 0cc4f5a..1712de1 100644
--- a/arena/project_decomposer_ai.py
+++ b/arena/project_decomposer_ai.py
@@ -16,6 +16,7 @@ from arena.project_graph import (
     graph_to_dict,
 )
 from arena.project_model_gate import (
+    UNIVERSAL_CONCERNS,
     close_import_contracts_for_gate,
     run_project_model_gate,
     write_gate_report,
@@ -287,6 +288,13 @@ def _is_dict_type(type_repr: str) -> bool:
     return any(member.startswith(("dict[", "Dict[")) for member in normalized.split("|"))


+def _canonical_universal_concern_id(raw_id: Any) -> str | None:
+    normalized = re.sub(r"[^a-z0-9]+", "_", str(raw_id).strip().lower()).strip("_")
+    if normalized.startswith("concern_"):
+        normalized = normalized.removeprefix("concern_")
+    return normalized if normalized in UNIVERSAL_CONCERNS else None
+
+
 def _coerce_dataclass(cls: type, item: Any, *, collection: str, index: int) -> Any:
     """Build a dataclass from a model-produced dict, fail-closed on identity gaps.

@@ -334,6 +342,10 @@ def _coerce_dataclass(cls: type, item: Any, *, collection: str, index: int) -> A
             f"{collection}[{index}] is missing required field(s) {sorted(missing_required)}; "
             f"model output did not conform to the {cls.__name__} schema"
         )
+    if cls is CrossCuttingConcern:
+        canonical_category = _canonical_universal_concern_id(kwargs.get("id", ""))
+        if canonical_category is not None:
+            kwargs["category"] = canonical_category
     return cls(**kwargs)


@@ -583,7 +595,7 @@ def _decomposer_prompt(*, project_id: str, goal: str, non_goals: list[str], grap
         '  "contracts": [{"id": str, "name": str, "from_component_id": component id, "to_component_id": component id,\n'
         '     "supporting_edge_ids": [edge_id from the list below connecting the two components],\n'
         '     "near_neighbor_alternative_ids": [], "provenance_refs": [prov id]}],\n'
-        '  "cross_cutting_concerns": [{"id": str, "category": str, "description": str, "component_ids": [component id],\n'
+        '  "cross_cutting_concerns": [{"id": str, "category": str (for universal concerns, category MUST be exactly one of anti_fabrication|determinism|provenance|no_live_paid_api_acceptance), "description": str, "component_ids": [component id],\n'
         '     "contract_ids": [], "provenance_refs": [prov id]}],\n'
         '  "observable_checks": [{"id": str, "description": str, "command": str, "component_ids": [component id],\n'
         '     "contract_ids": [], "provenance_refs": [prov id]}],\n'
@@ -604,7 +616,11 @@ def _decomposer_prompt(*, project_id: str, goal: str, non_goals: list[str], grap
         "contract or one with no supporting edge fails the gate.\n"
         "- Include the universal cross_cutting_concerns: anti_fabrication, determinism, provenance, "
         "no_live_paid_api_acceptance (each covering all components), plus protected_surface_integrity and "
-        "generated_artifact_integrity if such surfaces exist.\n"
+        "generated_artifact_integrity if such surfaces exist. For each universal concern, category MUST be exactly one of "
+        "anti_fabrication, determinism, provenance, no_live_paid_api_acceptance. Do not use thematic labels such as integrity, "
+        "reliability, traceability, or compliance in category. Example: {\"id\": \"concern.anti-fabrication\", "
+        "\"category\": \"anti_fabrication\", \"component_ids\": [\"component.example\"], \"contract_ids\": [], "
+        "\"provenance_refs\": [\"prov:example\"]}.\n"
         "- Provide at least one observable_check.\n"
         "- HELD-OUT PROBES: you have no probe-execution artifacts, so do NOT claim probe pass/fail. Instead record at "
         "least one verification_gap whose description mentions 'probe' and one of: 'semantic', 'independent', "
diff --git a/tests/test_project_decomposer_ai.py b/tests/test_project_decomposer_ai.py
index 2bf2bba..8545d4b 100644
--- a/tests/test_project_decomposer_ai.py
+++ b/tests/test_project_decomposer_ai.py
@@ -4,7 +4,7 @@ import json
 import subprocess
 from pathlib import Path

-from arena.project_decomposer_ai import build_project_model_snapshot
+from arena.project_decomposer_ai import _decomposer_prompt, build_project_model_snapshot
 from arena.project_graph import build_project_graph, graph_to_dict
 from arena.project_model_gate import close_import_contracts_for_gate, run_project_model_gate
 from arena.project_snapshot import Component, ProjectModelSnapshot, snapshot_to_dict
@@ -177,6 +177,132 @@ def test_recorded_model_output_uses_same_ingestion_path_and_bad_bucket_is_reject
     assert any(v.gate == "component_measurability" for v in rejected.gate_report.violations)


+def test_recorded_model_output_repairs_universal_concern_category_from_exact_id(
+    tmp_path: Path,
+) -> None:
+    repo = tmp_path / "repo"
+    repo.mkdir()
+    _write_repo(repo)
+    artifacts = tmp_path / "artifacts"
+    fixture = build_project_model_snapshot(
+        repo,
+        artifacts,
+        project_id="api-project",
+        llm_mode="fixture",
+        overwrite=True,
+    )
+    raw = json.loads(
+        (fixture.snapshot_dir / "model-outputs" / "decomposer.raw.json").read_text(
+            encoding="utf-8"
+        )
+    )
+    thematic_categories = {
+        "anti_fabrication": "integrity",
+        "determinism": "reliability",
+        "provenance": "traceability",
+        "no_live_paid_api_acceptance": "compliance",
+    }
+    for concern in raw["cross_cutting_concerns"]:
+        canonical = concern["category"]
+        if canonical in thematic_categories:
+            concern["id"] = canonical
+            concern["category"] = thematic_categories[canonical]
+    raw["model_id"] = "recorded-universal-concern-id-category-drift"
+    recorded_path = tmp_path / "recorded-concern-drift.json"
+    recorded_path.write_text(json.dumps(raw, indent=2), encoding="utf-8")
+
+    result = build_project_model_snapshot(
+        repo,
+        artifacts,
+        project_id="api-project",
+        llm_mode="recorded",
+        model_output_path=recorded_path,
+        overwrite=True,
+    )
+
+    assert result.gate_report.passed is True
+    categories = {concern.category for concern in result.snapshot.cross_cutting_concerns}
+    assert set(thematic_categories) <= categories
+    assert categories.isdisjoint(thematic_categories.values())
+    persisted_raw = json.loads(
+        (result.snapshot_dir / "model-outputs" / "decomposer.raw.json").read_text(
+            encoding="utf-8"
+        )
+    )
+    persisted_themes = {
+        concern["category"]
+        for concern in persisted_raw["cross_cutting_concerns"]
+        if concern["id"] in thematic_categories
+    }
+    assert persisted_themes == set(thematic_categories.values())
+
+
+def test_recorded_model_output_does_not_repair_unknown_concern_category(
+    tmp_path: Path,
+) -> None:
+    repo = tmp_path / "repo"
+    repo.mkdir()
+    _write_repo(repo)
+    artifacts = tmp_path / "artifacts"
+    fixture = build_project_model_snapshot(
+        repo,
+        artifacts,
+        project_id="api-project",
+        llm_mode="fixture",
+        overwrite=True,
+    )
+    raw = json.loads(
+        (fixture.snapshot_dir / "model-outputs" / "decomposer.raw.json").read_text(
+            encoding="utf-8"
+        )
+    )
+    for concern in raw["cross_cutting_concerns"]:
+        if concern["category"] == "anti_fabrication":
+            concern["id"] = "integrity-envelope"
+            concern["category"] = "integrity"
+            break
+    raw["model_id"] = "recorded-unknown-concern-category"
+    recorded_path = tmp_path / "recorded-unknown-concern.json"
+    recorded_path.write_text(json.dumps(raw, indent=2), encoding="utf-8")
+
+    result = build_project_model_snapshot(
+        repo,
+        artifacts,
+        project_id="api-project",
+        llm_mode="recorded",
+        model_output_path=recorded_path,
+        overwrite=True,
+    )
+
+    assert result.gate_report.passed is False
+    assert any(
+        violation.gate == "cross_cutting_concerns"
+        and "Missing universal concerns" in violation.message
+        and "anti_fabrication" in violation.message
+        for violation in result.gate_report.violations
+    )
+
+
+def test_live_decomposer_prompt_makes_universal_concern_categories_non_negotiable(
+    tmp_path: Path,
+) -> None:
+    repo = tmp_path / "repo"
+    repo.mkdir()
+    _write_repo(repo)
+    graph = build_project_graph(repo)
+
+    prompt = _decomposer_prompt(
+        project_id="api-project",
+        goal="decompose this repository into responsibility-bearing components",
+        non_goals=["do not treat file buckets as final components"],
+        graph=graph,
+    )
+
+    assert "category MUST be exactly one of" in prompt
+    assert '"category": "anti_fabrication"' in prompt
+    assert "Do not use thematic labels such as integrity" in prompt
+
+
 def test_fixture_decomposer_handles_javascript_import_contracts(tmp_path: Path) -> None:
     repo = tmp_path / "js-repo"
     repo.mkdir()
```

## Review ask
Return JSON only:
{
  "verdict": "ACCEPT" | "ACCEPT_WITH_CHANGES" | "REQUEST_CHANGES",
  "blocking_issues": ["..."],
  "nonblocking_issues": ["..."],
  "verification_gaps": ["..."],
  "patch_before_rerun": ["..."],
  "owner_summary": "..."
}

Review criteria:
- Does this fix the root cause without weakening `run_project_model_gate`?
- Is the normalization narrow enough: exact known-universal id only, no description/theme inference, raw unchanged?
- Are tests sufficient to catch the observed drift and prevent broad category remapping?
- Is prompt hardening clear enough?
- Is it safe to proceed to the requested live fmc-mcp high-reasoning rerun if verdict is ACCEPT or only cheap nonblocking changes remain?
