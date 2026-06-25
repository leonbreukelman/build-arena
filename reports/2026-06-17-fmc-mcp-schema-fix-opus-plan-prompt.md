You are Opus. Draw up a concrete implementation plan to fix a Build Arena live Project Model decomposer schema/gate issue, then stop. Do not use tools. Return JSON only.

Context:
- Target repo: <repo>
- Target behavior: Grok 4.3 high-reasoning live decomposition for <projects>/fmc-mcp should stop failing the deterministic Project Model gate due only to universal cross_cutting_concerns category/id drift.
- Scope: fix the schema/prompt/coercion issue. Do not weaken the gate. Do not touch scorer/, verifier/, schema/, or generated artifacts. Do not run intake/proposal/promotion.
- Required delivery flow after your plan: implement with tests first, run verification, get Opus review, rerun the high-reasoning decomposition, compare against previous run, confirm whether schema issue is resolved.

Observed previous failing run:
- Run root: <repo>/.arena/runs/fmc-mcp-decomposition-grok43-high-reasoning-20260617T205352Z
- Snapshot: snapshot-a623425c6db6a181
- Gate passed: false
- Gate violations:
  1. Missing universal concerns: anti_fabrication, determinism, no_live_paid_api_acceptance, provenance.
  2. Universal concern anti_fabrication does not cover components: comp:client, comp:config, comp:entry, comp:resources, comp:server, comp:tools.
  3. Universal concern provenance does not cover components: comp:client, comp:config, comp:entry, comp:resources, comp:server, comp:tools.
- Raw model output cross_cutting_concerns:
  - {id: anti_fabrication, category: integrity, component_ids: [comp:config, comp:client, comp:resources, comp:tools, comp:server, comp:entry]}
  - {id: determinism, category: reliability, component_ids: [same all components]}
  - {id: provenance, category: traceability, component_ids: [same all components]}
  - {id: no_live_paid_api_acceptance, category: compliance, component_ids: [same all components]}
- Snapshot persisted those categories unchanged, and the gate keys universal concerns by category, not id.

Relevant current code excerpts:

arena/project_model_gate.py:
```python
VAGUE_TERMS = {"misc", "miscellaneous", "general", "other", "stuff", "everything", "all", "bucket"}
UNIVERSAL_CONCERNS = {"anti_fabrication", "determinism", "provenance", "no_live_paid_api_acceptance"}
...
concern_categories = {concern.category for concern in snapshot_obj.cross_cutting_concerns}
missing_universal = UNIVERSAL_CONCERNS - concern_categories
if missing_universal:
    add("cross_cutting_concerns", f"Missing universal concerns: {', '.join(sorted(missing_universal))}.", "cross_cutting_concerns")
...
for universal_category in ("anti_fabrication", "provenance"):
    covered_components = {
        component_id
        for concern in snapshot_obj.cross_cutting_concerns
        if concern.category == universal_category
        for component_id in concern.component_ids
    }
    missing_components = component_ids - covered_components
    if missing_components:
        add(
            "cross_cutting_concerns",
            f"Universal concern {universal_category} does not cover components: {', '.join(sorted(missing_components))}.",
            "cross_cutting_concerns",
        )
```

arena/project_decomposer_ai.py ingestion:
```python
_TOP_LEVEL_ALIASES = {
    "observable_checks": ("observable_checks", "checks"),
    "cross_cutting_concerns": ("cross_cutting_concerns", "concerns"),
    ...
}

def _coerce_dataclass(cls, item, *, collection, index):
    # Unknown keys are dropped; missing list fields default to empty lists.
    # Present list fields must be JSON arrays. Missing scalar identities fail.
    ...
    return cls(**kwargs)

def _coerce_list(cls, raw, canonical):
    return [_coerce_dataclass(cls, item, collection=canonical, index=index)
            for index, item in enumerate(_resolve_list(raw, canonical))]

snapshot = ProjectModelSnapshot(
    ...
    cross_cutting_concerns=_coerce_list(CrossCuttingConcern, raw, "cross_cutting_concerns"),
    ...
)
```

arena/project_decomposer_ai.py current prompt schema/rule:
```python
'  "cross_cutting_concerns": [{"id": str, "category": str, "description": str, "component_ids": [component id],\n'
'     "contract_ids": [], "provenance_refs": [prov id]}],\n'
...
"- Include the universal cross_cutting_concerns: anti_fabrication, determinism, provenance, "
"no_live_paid_api_acceptance (each covering all components), plus protected_surface_integrity and "
"generated_artifact_integrity if such surfaces exist.\n"
```

Existing fixture output canonical shape in arena/project_meta_decomposer.py:
```python
{
    "id": "concern.anti-fabrication",
    "category": "anti_fabrication",
    "description": "Accepted decomposition claims must trace to deterministic graph provenance.",
    "component_ids": component_ids,
    "contract_ids": contract_ids,
    "provenance_refs": [first_prov],
    "triggered_by": [],
}
```

Existing tests:
- tests/test_project_decomposer_ai.py already tests recorded model output ingestion and gate behavior.
- tests/test_project_meta_decomposer.py tests fixture output/gate behavior.
- Use TDD: add failing regression before production code.

Constraints:
- Do not normalize away real unknown categories broadly. We need a narrow universal-concern schema drift fix, not a gate bypass.
- Do not weaken run_project_model_gate; it must still reject missing universal concerns when model output has no recoverable universal category signal.
- If adding coercion, keep raw model output persisted unchanged for audit.
- Prefer a prompt hardening plus deterministic normalization/repair only when the concern id is an exact known universal concern and category is a noncanonical synonym or wrong value. Avoid accepting arbitrary inferred categories.
- Component ids with colons such as comp:client were valid in the failing snapshot; the root issue is categories.

Ask:
Return JSON only with:
{
  "verdict": "PLAN",
  "root_cause": "...",
  "recommended_fix": "...",
  "tests_to_add_first": ["..."],
  "implementation_steps": ["..."],
  "verification_commands": ["..."],
  "rerun_plan": ["..."],
  "risks_and_guardrails": ["..."],
  "do_not_do": ["..."]
}
