# Dream Proposer Tier 3 Review Packet

Review target: new advisory dream proposer lane only. Ignore pre-existing dirty files not listed here.

## File list
- `docs/schemas/capability-map-v0.schema.json`
- `docs/schemas/dream-v0.schema.json`
- `arena/capability_lift.py`
- `arena/dream_generate.py`
- `arena/dream_research.py`
- `arena/dream_gate.py`
- `arena/dream_emit.py`
- `arena/dream_run.py`
- `tests/test_capability_lift.py`
- `tests/test_dream_generate.py`
- `tests/test_dream_research.py`
- `tests/test_dream_gate.py`
- `tests/test_dream_emit.py`
- `tests/test_dream_run.py`
- `docs/specs/2026-06-23-dream-proposer-tier3-spec.md`
- `docs/agent-wiki/2026-06-23-dream-proposer-failure-modes.md`
- `README.md`
- `docs/agent-wiki/index.md`
- `docs/status/2026-06-23-dream-proposer-tier3-implementation-status.md`
- `docs/status/INDEX.md`

## Git status (full, to show dirty checkout context)
```text
M README.md
 M arena/project_decomposer_ai.py
 M docs/agent-wiki/index.md
 M docs/status/INDEX.md
 M tests/test_project_decomposer_ai.py
?? .env
?? arena/capability_lift.py
?? arena/dream_emit.py
?? arena/dream_gate.py
?? arena/dream_generate.py
?? arena/dream_research.py
?? arena/dream_run.py
?? docs/agent-wiki/2026-06-23-dream-proposer-failure-modes.md
?? docs/schemas/capability-map-v0.schema.json
?? docs/schemas/dream-v0.schema.json
?? docs/specs/2026-06-19-pairwise-proposal-reranker-design.md
?? docs/specs/2026-06-23-dream-proposer-tier3-spec.md
?? docs/status/2026-06-17-fmc-mcp-schema-fix-status.md
?? docs/status/2026-06-23-dream-proposer-tier3-implementation-status.md
?? docs/verification/2026-06-19-pairwise-proposal-reranker-opus-rereview-prompt.md
?? docs/verification/2026-06-19-pairwise-proposal-reranker-opus-rereview.err
?? docs/verification/2026-06-19-pairwise-proposal-reranker-opus-rereview.json
?? docs/verification/2026-06-19-pairwise-proposal-reranker-opus-review-prompt.md
?? docs/verification/2026-06-19-pairwise-proposal-reranker-opus-review.err
?? docs/verification/2026-06-19-pairwise-proposal-reranker-opus-review.json
?? proposal-run-and-emit.patch
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
?? reports/2026-06-17-fmc-mcp-intake-expected-vs-actual-opus-review-prompt.md
?? reports/2026-06-17-fmc-mcp-intake-expected-vs-actual-opus-review.err
?? reports/2026-06-17-fmc-mcp-intake-expected-vs-actual-opus-review.json
?? reports/2026-06-17-fmc-mcp-intake-expected-vs-actual.md
?? reports/2026-06-17-fmc-mcp-production-intake-result.md
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
?? reports/2026-06-17-fmc-mcp-schema-fix-opus-review-packet.md
?? reports/2026-06-17-fmc-mcp-schema-fix-opus-review-retry.err
?? reports/2026-06-17-fmc-mcp-schema-fix-opus-review-retry.json
?? reports/2026-06-17-fmc-mcp-schema-fix-opus-review.err
?? reports/2026-06-17-fmc-mcp-schema-fix-opus-review.json
?? reports/2026-06-17-fmc-mcp-schema-fix-rerun-comparison.json
?? reports/2026-06-17-fmc-mcp-schema-fix-rerun-report.md
?? reports/2026-06-17-model-candidate-research-raw.json
?? reports/2026-06-18-fmc-mcp-advisory-proposer-opus-inspection-prompt.md
?? reports/2026-06-18-fmc-mcp-advisory-proposer-opus-inspection.err
?? reports/2026-06-18-fmc-mcp-advisory-proposer-opus-inspection.json
?? reports/2026-06-18-fmc-mcp-proposer-run-and-advisory-actionability-opus-review.err
?? reports/2026-06-18-fmc-mcp-proposer-run-and-advisory-actionability-opus-review.json
?? reports/2026-06-18-fmc-mcp-proposer-run-and-advisory-actionability-review-prompt.md
?? reports/2026-06-21-elenchus-core-proposal-run-opus-review.err
?? reports/2026-06-21-elenchus-core-proposal-run-opus-review.json
?? reports/2026-06-21-elenchus-core-proposal-run-report.md
?? reports/2026-06-21-elenchus-core-proposal-run-review-prompt.md
?? tests/test_capability_lift.py
?? tests/test_dream_emit.py
?? tests/test_dream_gate.py
?? tests/test_dream_generate.py
?? tests/test_dream_research.py
?? tests/test_dream_run.py
```

## Verification commands already run
### `uv run pytest tests/test_capability_lift.py tests/test_dream_generate.py tests/test_dream_research.py tests/test_dream_gate.py tests/test_dream_emit.py tests/test_dream_run.py -q`
Exit: 0
```text
..................................                                       [100%]
```

### `uv run pytest tests -q`
Exit: 0
```text
........................................................................ [ 13%]
........................................................................ [ 26%]
..........................................................sssssssssss... [ 39%]
........................................................................ [ 52%]
........................................................................ [ 65%]
........................................................................ [ 78%]
........................................................................ [ 91%]
................................................                         [100%]
```

### `uv run ruff check .`
Exit: 0
```text
All checks passed!
```

### `uv run pyright`
Exit: 0
```text
0 errors, 0 warnings, 0 informations
WARNING: there is a new pyright version available (v1.1.409 -> v1.1.410).
Please install the new version or set PYRIGHT_PYTHON_FORCE_VERSION to `latest`
```

### `make generated`
Exit: 0
```text
mkdir -p arena/generated dashboard/src/lib/generated
uv run gen-pydantic schema/arena.yaml > arena/generated/models.py
uv run gen-json-schema schema/arena.yaml > arena/generated/schema.json
uv run gen-typescript schema/arena.yaml > dashboard/src/lib/generated/arena.d.ts
uv run gen-sqlddl schema/arena.yaml > arena/generated/ddl.sql
uv run python scripts/normalize_generated_artifacts.py
```

## Tracked diff for existing files touched by this task
```diff
diff --git a/README.md b/README.md
index ec1da93..6ea9a48 100644
--- a/README.md
+++ b/README.md
@@ -108,3 +108,20 @@ uv run python -m arena.project_model_cli gate --snapshot /tmp/build-arena-snapsh
 ```

 The AI-first snapshot command emits `project-model-v1.json` as the Project Model v1 primary artifact and `project-model-v0.json` for compatibility. Live mode is only for bounded read-only smoke under the readiness ladder; Build Arena remains not ready for broad autonomous live loops.
+
+## Advisory dream proposer lane
+
+`arena.dream_run` is a separate tier-3 advisory lane for architectural hypotheses that do not fit the single-file deterministic proposal contract. It chains snapshot/decompose → intake → capability lift → operator review gate → dream generation → dream research → premise gate → emit, and writes `dream.md` only. It never writes `proposal.md` and never applies or promotes a change.
+
+```bash
+uv run python -m arena.dream_run run /path/to/target-repo \
+  --live-model <explicit-model> \
+  --live-api-key-env XAI_API_KEY \
+  --output dream.md
+```
+
+The capability map is the intent-anchoring artifact. `arena.capability_lift` writes `capability-map.json` with `review.reviewed: false`; `dream_run` stops with exit `4` until the operator reviews/edits that map. To continue from a reviewed map, pass `--capability-map <path>`.
+
+The deterministic boundary is the gated `dream/v0` artifact. Generation and research are live model stages and require an explicit `--live-model`; `arena.dream_gate` then kills any dream whose cited anchors or target capabilities do not resolve against the real Project Model v1 and reviewed capability map. `arena.dream_emit` renders only `premiseConfidence == all_resolved` dreams, with premise confidence and speculative conclusion confidence shown separately.
+
+Exit codes: `0` success (`dream.md` written); `1` stage failure; `2` no dream survived the premise gate; `3` usage/preflight error; `4` capability map not reviewed.
diff --git a/docs/agent-wiki/index.md b/docs/agent-wiki/index.md
index 444d3d3..352121d 100644
--- a/docs/agent-wiki/index.md
+++ b/docs/agent-wiki/index.md
@@ -14,6 +14,7 @@ Future implementation should make this more than prose: the proposal registry, l

 - `2026-06-15-fmc-mcp-production-pass-lessons.md` — safe failed live run, full-autonomy deviations, and proposal-registry lesson.
 - `2026-06-15-proposal-registry-lineage-and-repair-loop.md` — implemented registry/lineage, candidate-skip observability, repair retry, and multi-target proposal mechanics.
+- `2026-06-23-dream-proposer-failure-modes.md` — tier-3 dream proposer lane boundaries, capability-map review gate, premise-kill gate, novelty floor, and acceptance-rate failure modes.

 ## Minimum wiki sections to grow

diff --git a/docs/status/INDEX.md b/docs/status/INDEX.md
index aa4ddb9..3045ae7 100644
--- a/docs/status/INDEX.md
+++ b/docs/status/INDEX.md
@@ -6,6 +6,7 @@ Maintenance rule: when a status doc's feature or run state changes, either updat

 ## Active

+- `2026-06-23-dream-proposer-tier3-implementation-status.md` — local implementation status for the tier-3 advisory dream proposer lane.
 - `2026-06-16-project-graph-call-inheritance-treesitter.md` — project graph call/inheritance and JS/TS tree-sitter extraction; merged via PR #40 / 360e9a2.
 - `2026-06-15-full-autonomy-gap-remediation-implementation-status.md` — current implementation status for the first full-autonomy gap-remediation slice.

@@ -16,4 +17,5 @@ Maintenance rule: when a status doc's feature or run state changes, either updat

 ## Historical

+- `2026-06-17-fmc-mcp-schema-fix-status.md` — point-in-time record for the Grok 4.3 high-reasoning universal concern category/id schema fix and decomposition-only rerun.
 - `2026-06-15-current-status-timeline-production-readiness.md` — point-in-time audit with captured dirty-state and run evidence; use current git/docs before treating its repository-state details as live.
```

## New/changed file contents
### `docs/schemas/capability-map-v0.schema.json`
```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://arena.local/schemas/capability-map-v0.schema.json",
  "title": "Capability Map v0",
  "description": "Agnostic function/capability overlay over a Project Model v1 structural model. Interpretive, advisory, operator-reviewed. Not produced by the deterministic decomposer.",
  "type": "object",
  "additionalProperties": false,
  "required": ["schemaVersion", "projectId", "sourceModel", "capabilities", "review", "provenance"],
  "properties": {
    "schemaVersion": { "const": "capability-map/v0" },
    "projectId": { "type": "string", "minLength": 1 },
    "sourceModel": {
      "type": "object",
      "additionalProperties": false,
      "required": ["projectModelV1Path", "graphHash"],
      "properties": {
        "projectModelV1Path": { "type": "string", "minLength": 1 },
        "graphHash": { "type": "string", "pattern": "^[a-f0-9]{64}$" }
      }
    },
    "capabilities": {
      "type": "array",
      "minItems": 1,
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": ["id", "capability", "realizedByComponentIds", "currentCarrier", "provenanceRefs"],
        "properties": {
          "id": { "type": "string", "minLength": 1 },
          "capability": {
            "type": "string", "minLength": 1,
            "description": "Carrier-agnostic role, e.g. 'durable analytical storage', 'event-triggered worker', 'cross-domain ranking'."
          },
          "realizedByComponentIds": {
            "type": "array", "minItems": 1,
            "items": { "type": "string", "minLength": 1 },
            "description": "Each MUST equal a snapshot.components[].id in the source Project Model v1."
          },
          "currentCarrier": {
            "type": "string", "minLength": 1,
            "description": "What concretely fills the role today, e.g. 'AST walk in arena.decomposer', 'ruff subprocess'."
          },
          "supportingNodeIds": { "type": "array", "items": { "type": "string", "minLength": 1 } },
          "behavioralTags": { "type": "array", "items": { "type": "string", "minLength": 1 } },
          "provenanceRefs": { "type": "array", "minItems": 1, "items": { "type": "string", "minLength": 1 } }
        }
      }
    },
    "review": {
      "type": "object",
      "additionalProperties": false,
      "required": ["reviewed"],
      "properties": {
        "reviewed": { "type": "boolean" },
        "reviewedBy": { "type": ["string", "null"] },
        "reviewedAtUtc": { "type": ["string", "null"] },
        "editedFromGenerated": { "type": "boolean" }
      }
    },
    "provenance": {
      "type": "object",
      "additionalProperties": false,
      "required": ["generatedBy", "promptHash", "modelId", "inputHashes"],
      "properties": {
        "generatedBy": { "type": "string", "minLength": 1 },
        "promptHash": { "type": "string", "pattern": "^[a-f0-9]{64}$" },
        "modelId": { "type": "string", "minLength": 1 },
        "inputHashes": { "type": "object", "additionalProperties": { "type": "string", "pattern": "^[a-f0-9]{64}$" } }
      }
    }
  }
}

```

### `docs/schemas/dream-v0.schema.json`
```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://arena.local/schemas/dream-v0.schema.json",
  "title": "Dream Proposals v0",
  "description": "Advisory architectural hypotheses (tier 3). Speculative invention grounded in cited current-state evidence; never a deterministic change.",
  "type": "object",
  "additionalProperties": false,
  "required": ["schemaVersion", "projectId", "sourceModel", "capabilityMap", "dreams", "provenance"],
  "properties": {
    "schemaVersion": { "const": "dream/v0" },
    "projectId": { "type": "string", "minLength": 1 },
    "sourceModel": {
      "type": "object", "additionalProperties": false,
      "required": ["projectModelV1Path", "graphHash"],
      "properties": {
        "projectModelV1Path": { "type": "string", "minLength": 1 },
        "graphHash": { "type": "string", "pattern": "^[a-f0-9]{64}$" }
      }
    },
    "capabilityMap": {
      "type": "object", "additionalProperties": false,
      "required": ["path", "reviewed"],
      "properties": {
        "path": { "type": "string", "minLength": 1 },
        "reviewed": { "const": true }
      }
    },
    "dreams": {
      "type": "array",
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": [
          "id", "mode", "idea", "targetCapabilityIds", "citedEvidence",
          "rationale", "premiseConfidence", "conclusionConfidence", "validationRecipe"
        ],
        "properties": {
          "id": { "type": "string", "minLength": 1 },
          "mode": {
            "enum": ["carrier_swap", "function_remap"],
            "description": "carrier_swap = same capability, different realization (cheaper to ground; may map to a known near_neighbor_alternative). function_remap = redraw the capability map (merge/split roles; wilder; harder to ground)."
          },
          "idea": { "type": "string", "minLength": 1, "description": "The hypothesis as 'consider X'." },
          "targetCapabilityIds": {
            "type": "array", "minItems": 1, "items": { "type": "string", "minLength": 1 },
            "description": "Each MUST equal a capabilities[].id in the reviewed capability map."
          },
          "citedEvidence": {
            "type": "array", "minItems": 1,
            "items": {
              "type": "object", "additionalProperties": false,
              "required": ["anchorKind", "anchorId", "contentHash"],
              "properties": {
                "anchorKind": { "enum": ["graphNode", "graphEdge", "component", "contract", "capability", "verificationGap", "nearNeighborAlternative"] },
                "anchorId": { "type": "string", "minLength": 1, "description": "MUST resolve to a real id of the named kind in the source model / capability map." },
                "contentHash": { "type": "string", "pattern": "^[a-f0-9]{64}$" },
                "claim": { "type": "string", "minLength": 1, "description": "The current-state fact this anchor is asserted to support." }
              }
            }
          },
          "rationale": {
            "type": "string", "minLength": 1,
            "description": "Why the idea follows from the cited evidence. MUST be hard-to-vary: it should specifically support THIS idea over the capability's near-neighbor alternatives, not justify any change."
          },
          "premiseConfidence": {
            "enum": ["all_resolved", "partial", "unresolved"],
            "description": "MECHANICAL. Set by the gate: all_resolved iff every citedEvidence anchor resolves. dream_emit renders only all_resolved."
          },
          "conclusionConfidence": {
            "type": "object", "additionalProperties": false,
            "required": ["band", "value"],
            "properties": {
              "band": { "enum": ["low", "medium"], "description": "SOFT and CAPPED. 'high' is forbidden pre-emission: benefit is structurally unverifiable before the repo agent tries it." },
              "value": { "type": "number", "minimum": 0, "maximum": 0.7 }
            }
          },
          "validationRecipe": {
            "type": "object", "additionalProperties": false,
            "required": ["action", "observable", "expectedDirection"],
            "properties": {
              "action": { "type": "string", "minLength": 1, "description": "What the repo agent should TRY, e.g. 'replace the ruff subprocess carrier with a libcst pass behind the same gate interface'." },
              "observable": { "type": "string", "minLength": 1, "description": "What to MEASURE, e.g. 'import-cycle count', 'gate wall-clock', 'lines of glue in arena.proposal_run'." },
              "expectedDirection": { "enum": ["decrease", "increase", "unchanged", "tests_pass"] }
            }
          },
          "neighborAlternativeId": { "type": ["string", "null"], "description": "For carrier_swap: the snapshot.near_neighbor_alternatives[].id this swap corresponds to, if any. Raises rank (cheaper to validate)." }
        }
      }
    },
    "provenance": {
      "type": "object", "additionalProperties": false,
      "required": ["generatedBy", "researchedBy", "promptHashes", "modelId", "inputHashes"],
      "properties": {
        "generatedBy": { "type": "string", "minLength": 1 },
        "researchedBy": { "type": "string", "minLength": 1 },
        "promptHashes": { "type": "object", "additionalProperties": { "type": "string", "pattern": "^[a-f0-9]{64}$" } },
        "modelId": { "type": "string", "minLength": 1 },
        "inputHashes": { "type": "object", "additionalProperties": { "type": "string", "pattern": "^[a-f0-9]{64}$" } }
      }
    }
  }
}

```

### `arena/capability_lift.py`
```python
"""Build an advisory capability overlay for a Project Model v1 snapshot.

The capability map is intentionally separate from Project Model v1: it is an
operator-reviewed interpretation of what roles the current structural components
serve. This module keeps the v0 lift deterministic and auditable: every emitted
capability cites concrete component/node/provenance ids from the source model and
``review.reviewed`` defaults to ``False`` so downstream dream runs fail closed
until the operator edits/reviews the map.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

SCHEMA_VERSION = "capability-map/v0"
GENERATED_BY = "arena.capability_lift"
DEFAULT_MODEL_ID = "deterministic-capability-lift-v0"
PROMPT = (
    "Infer a carrier-agnostic capability map from Project Model v1 components. "
    "Every capability must cite real component ids, supporting node ids, and provenance refs. "
    "The artifact is advisory and must be operator-reviewed before use."
)

_SCHEMA_PATH = Path(__file__).resolve().parents[1] / "docs" / "schemas" / "capability-map-v0.schema.json"


class CapabilityLiftError(Exception):
    """Raised when a capability map cannot be built or validated."""


def load_json_object(path: str | Path) -> dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise CapabilityLiftError(f"{path} must contain a JSON object")
    return payload


def build_capability_map(project_model_path: str | Path, *, model_id: str = DEFAULT_MODEL_ID) -> dict[str, Any]:
    """Build and self-validate a ``capability-map/v0`` document."""

    model_path = Path(project_model_path).resolve()
    model = load_json_object(model_path)
    components = [item for item in _get(model, "snapshot", "components", default=[]) if isinstance(item, dict)]
    if not components:
        raise CapabilityLiftError("Project Model v1 snapshot has no components to lift")

    profiles = {
        str(item.get("componentId")): item
        for item in _get(model, "iterationReadiness", "componentProfiles", default=[])
        if isinstance(item, dict) and item.get("componentId")
    }

    capabilities: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for component in components:
        component_id = str(component.get("id", "")).strip()
        if not component_id:
            continue
        profile = profiles.get(component_id, {})
        cap_id = _unique_id(f"capability.{_slug(component_id)}", seen_ids)
        responsibility = _first_nonempty(
            profile.get("responsibilitySummary"),
            component.get("responsibility"),
            component.get("name"),
            component_id,
        )
        carrier = _first_nonempty(component.get("name"), component.get("responsibility"), component_id)
        supporting_nodes = _dedupe_strings(
            [*component.get("owned_node_ids", []), *profile.get("ownedNodeIds", [])]
        )
        provenance_refs = _dedupe_strings(
            [*component.get("provenance_refs", []), *profile.get("provenanceRefs", [])]
        ) or [f"component:{component_id}"]
        capabilities.append(
            {
                "id": cap_id,
                "capability": responsibility,
                "realizedByComponentIds": [component_id],
                "currentCarrier": carrier,
                "supportingNodeIds": supporting_nodes,
                "behavioralTags": _dedupe_strings(profile.get("behavioralTags", [])),
                "provenanceRefs": provenance_refs,
            }
        )

    if not capabilities:
        raise CapabilityLiftError("Project Model v1 snapshot has no liftable component ids")

    graph_hash = _graph_hash(model)
    project_id = _project_id(model)
    document = {
        "schemaVersion": SCHEMA_VERSION,
        "projectId": project_id,
        "sourceModel": {
            "projectModelV1Path": str(model_path),
            "graphHash": graph_hash,
        },
        "capabilities": capabilities,
        "review": {
            "reviewed": False,
            "reviewedBy": None,
            "reviewedAtUtc": None,
            "editedFromGenerated": False,
        },
        "provenance": {
            "generatedBy": GENERATED_BY,
            "promptHash": _sha_text(PROMPT),
            "modelId": model_id,
            "inputHashes": {"projectModelV1": _file_sha(model_path)},
        },
    }
    validate_capability_map(document, model)
    validate_schema(document)
    return document


def validate_schema(document: dict[str, Any]) -> None:
    schema = load_json_object(_SCHEMA_PATH)
    errors = sorted(Draft202012Validator(schema).iter_errors(document), key=lambda error: list(error.path))
    if errors:
        first = errors[0]
        location = "/".join(str(part) for part in first.path) or "<root>"
        raise CapabilityLiftError(f"capability map failed schema validation at {location}: {first.message}")


def validate_capability_map(document: dict[str, Any], model: dict[str, Any]) -> None:
    """Validate that every capability reference resolves in the source model."""

    component_ids = {
        str(item.get("id"))
        for item in _get(model, "snapshot", "components", default=[])
        if isinstance(item, dict) and item.get("id")
    }
    node_ids = {
        str(item.get("id"))
        for item in _get(model, "projectGraph", "nodes", default=[])
        if isinstance(item, dict) and item.get("id")
    }
    capability_ids: set[str] = set()
    for index, capability in enumerate(document.get("capabilities", [])):
        if not isinstance(capability, dict):
            raise CapabilityLiftError(f"capabilities[{index}] must be an object")
        capability_id = str(capability.get("id", ""))
        if capability_id in capability_ids:
            raise CapabilityLiftError(f"duplicate capability id: {capability_id}")
        capability_ids.add(capability_id)
        for component_id in capability.get("realizedByComponentIds", []):
            if str(component_id) not in component_ids:
                raise CapabilityLiftError(
                    f"capability {capability_id} references unknown component {component_id}"
                )
        for node_id in capability.get("supportingNodeIds", []):
            if str(node_id) not in node_ids:
                raise CapabilityLiftError(f"capability {capability_id} references unknown graph node {node_id}")


def write_capability_map(project_model_path: str | Path, output_path: str | Path, *, model_id: str = DEFAULT_MODEL_ID) -> Path:
    document = build_capability_map(project_model_path, model_id=model_id)
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return output


def _get(payload: dict[str, Any], *keys: str, default: Any = None) -> Any:
    current: Any = payload
    for key in keys:
        if not isinstance(current, dict):
            return default
        current = current.get(key)
    return default if current is None else current


def _project_id(model: dict[str, Any]) -> str:
    return _first_nonempty(
        _get(model, "project", "projectId"),
        _get(model, "snapshot", "project_id"),
        model.get("id"),
        "project",
    )


def _graph_hash(model: dict[str, Any]) -> str:
    graph_hash = _first_nonempty(
        _get(model, "projectGraph", "graphHash"),
        _get(model, "snapshot", "graph_hash"),
    )
    if not re.fullmatch(r"[a-f0-9]{64}", graph_hash):
        raise CapabilityLiftError("Project Model v1 does not expose a valid 64-hex graph hash")
    return graph_hash


def _first_nonempty(*values: Any) -> str:
    for value in values:
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def _dedupe_strings(values: Any) -> list[str]:
    if not isinstance(values, list):
        return []
    return list(dict.fromkeys(str(value).strip() for value in values if str(value).strip()))


def _slug(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", ".", value.lower()).strip(".")
    return slug or "capability"


def _unique_id(base: str, seen: set[str]) -> str:
    candidate = base
    suffix = 2
    while candidate in seen:
        candidate = f"{base}.{suffix}"
        suffix += 1
    seen.add(candidate)
    return candidate


def _sha_text(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def _file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m arena.capability_lift")
    parser.add_argument("--project-model", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--model-id", default=DEFAULT_MODEL_ID)
    args = parser.parse_args(argv)
    try:
        output = write_capability_map(args.project_model, args.output, model_id=args.model_id)
    except (CapabilityLiftError, OSError, json.JSONDecodeError) as exc:
        print(f"capability lift failed: {exc}", file=sys.stderr)
        return 1
    print(str(output))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())

```

### `arena/dream_generate.py`
```python
"""Live-gated typed generation for advisory dream proposals.

The generator is intentionally not trusted. It only produces raw dream candidates
with minimum structure; ``arena.dream_gate`` later decides which premises resolve.
Tests inject a model callable, so the offline suite never spends or calls a live
provider.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

from arena.llm_adapter import OpenAICompatibleChatClient, resolve_provider_config

SCHEMA_VERSION = "dream/v0"
GENERATED_BY = "arena.dream_generate"
PROMPT_VERSION = "dream-generate-v0"
ALLOWED_MODES = {"carrier_swap", "function_remap"}

DreamModel = Callable[[str], dict[str, Any]]


class DreamGenerateError(Exception):
    """Raised when raw dream generation fails closed."""


def generate_dreams(
    *,
    project_model_path: str | Path,
    capability_map_path: str | Path,
    scorecard_path: str | Path,
    model: DreamModel | None = None,
    live_provider: str = "xai",
    live_base_url: str | None = None,
    live_model: str | None = None,
    live_api_key_env: str = "XAI_API_KEY",
) -> dict[str, Any]:
    model_path = Path(project_model_path).resolve()
    cap_path = Path(capability_map_path).resolve()
    scorecard = Path(scorecard_path).resolve()
    project_model = _load_json_object(model_path)
    capability_map = _load_json_object(cap_path)
    scorecard_doc = _load_json_object(scorecard)
    if capability_map.get("review", {}).get("reviewed") is not True:
        raise DreamGenerateError("capability map must be operator-reviewed before dream generation")

    prompt = _generation_prompt(project_model, capability_map, scorecard_doc)
    if model is None:
        if not live_model:
            raise DreamGenerateError("--live-model is required for dream generation")
        provider_config = resolve_provider_config(
            live_provider,
            base_url=live_base_url,
            api_key_env=live_api_key_env,
            model=live_model,
            require_explicit_model=True,
        )
        client = OpenAICompatibleChatClient(provider_config, temperature=0.7, max_tokens=4096)
        result = client.complete(
            messages=[
                {"role": "system", "content": "Return only JSON with a top-level dreams array."},
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
        )
        raw = _parse_model_json(result.text)
        model_id = result.model
    else:
        raw = model(prompt)
        if not isinstance(raw, dict):
            raise DreamGenerateError("injected model must return a JSON object")
        model_id = "injected-model"

    dreams = _minimum_grounded_dreams(raw.get("dreams", []), capability_map=capability_map)
    if not dreams:
        raise DreamGenerateError("generation produced no dreams with the required minimum grounding")
    return {
        "schemaVersion": SCHEMA_VERSION,
        "projectId": _project_id(project_model, capability_map),
        "sourceModel": {"projectModelV1Path": str(model_path), "graphHash": _graph_hash(project_model)},
        "capabilityMap": {"path": str(cap_path), "reviewed": True},
        "dreams": dreams,
        "provenance": {
            "generatedBy": GENERATED_BY,
            "researchedBy": "unresearched",
            "promptHashes": {"generate": _sha_text(prompt), "generatePromptVersion": _sha_text(PROMPT_VERSION)},
            "modelId": model_id,
            "inputHashes": {
                "projectModelV1": _file_sha(model_path),
                "capabilityMap": _file_sha(cap_path),
                "scorecard": _file_sha(scorecard),
            },
        },
    }


def write_generated_dreams(
    *,
    project_model_path: str | Path,
    capability_map_path: str | Path,
    scorecard_path: str | Path,
    output_path: str | Path,
    model: DreamModel | None = None,
    live_provider: str = "xai",
    live_base_url: str | None = None,
    live_model: str | None = None,
    live_api_key_env: str = "XAI_API_KEY",
) -> Path:
    document = generate_dreams(
        project_model_path=project_model_path,
        capability_map_path=capability_map_path,
        scorecard_path=scorecard_path,
        model=model,
        live_provider=live_provider,
        live_base_url=live_base_url,
        live_model=live_model,
        live_api_key_env=live_api_key_env,
    )
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return output


def _minimum_grounded_dreams(raw_dreams: Any, *, capability_map: dict[str, Any]) -> list[dict[str, Any]]:
    if not isinstance(raw_dreams, list):
        return []
    capability_ids = {
        str(item.get("id"))
        for item in capability_map.get("capabilities", [])
        if isinstance(item, dict) and item.get("id")
    }
    out: list[dict[str, Any]] = []
    for raw in raw_dreams:
        if not isinstance(raw, dict):
            continue
        mode = _clean(raw.get("mode"))
        targets = _string_list(raw.get("targetCapabilityIds"))
        evidence = [item for item in raw.get("citedEvidence", []) if isinstance(item, dict)] if isinstance(raw.get("citedEvidence"), list) else []
        recipe = raw.get("validationRecipe") if isinstance(raw.get("validationRecipe"), dict) else {}
        if mode not in ALLOWED_MODES or not targets or not evidence or not recipe:
            continue
        if any(target not in capability_ids for target in targets):
            continue
        normalized = {
            "id": _clean(raw.get("id")) or f"dream-{len(out) + 1}",
            "mode": mode,
            "idea": _clean(raw.get("idea")),
            "targetCapabilityIds": targets,
            "citedEvidence": evidence,
            "rationale": _clean(raw.get("rationale")),
            "premiseConfidence": _clean(raw.get("premiseConfidence")) or "unresolved",
            "conclusionConfidence": _conclusion(raw.get("conclusionConfidence")),
            "validationRecipe": {
                "action": _clean(recipe.get("action")),
                "observable": _clean(recipe.get("observable")),
                "expectedDirection": _clean(recipe.get("expectedDirection")),
            },
        }
        if raw.get("neighborAlternativeId") is not None:
            normalized["neighborAlternativeId"] = _clean(raw.get("neighborAlternativeId")) or None
        if normalized["idea"] and normalized["rationale"] and normalized["validationRecipe"]["action"]:
            out.append(normalized)
    return out


def _conclusion(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        return {"band": "low", "value": 0.1}
    band = _clean(value.get("band"))
    if band not in {"low", "medium"}:
        band = "low"
    raw_number = value.get("value")
    number = float(raw_number) if isinstance(raw_number, int | float) else 0.1
    return {"band": band, "value": min(max(number, 0.0), 0.7)}


def _generation_prompt(project_model: dict[str, Any], capability_map: dict[str, Any], scorecard: dict[str, Any]) -> str:
    compact = {
        "projectId": _project_id(project_model, capability_map),
        "capabilities": capability_map.get("capabilities", []),
        "componentProfiles": _get(project_model, "iterationReadiness", "componentProfiles", default=[]),
        "nearNeighborAlternatives": _get(project_model, "snapshot", "near_neighbor_alternatives", default=[]),
        "topFindings": scorecard.get("findings", [])[:8] if isinstance(scorecard.get("findings"), list) else [],
    }
    return (
        "Generate advisory tier-3 dream proposals for Build Arena. Return JSON only: "
        "{\"dreams\":[...]}. Include at least one carrier_swap and one function_remap when possible. "
        "Every dream must include mode, idea, targetCapabilityIds, citedEvidence with anchorKind/anchorId/contentHash/claim, "
        "rationale, conclusionConfidence capped at medium/0.7, and validationRecipe. Current facts:\n"
        + json.dumps(compact, sort_keys=True, ensure_ascii=False)
    )


def _parse_model_json(text: str) -> dict[str, Any]:
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        raise DreamGenerateError("live model did not return valid JSON") from exc
    if not isinstance(payload, dict):
        raise DreamGenerateError("live model JSON must be an object")
    return payload


def _load_json_object(path: str | Path) -> dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise DreamGenerateError(f"{path} must contain a JSON object")
    return payload


def _project_id(project_model: dict[str, Any], capability_map: dict[str, Any]) -> str:
    return (
        _clean(capability_map.get("projectId"))
        or _clean(_get(project_model, "project", "projectId"))
        or _clean(_get(project_model, "snapshot", "project_id"))
        or "project"
    )


def _graph_hash(project_model: dict[str, Any]) -> str:
    graph_hash = _clean(_get(project_model, "projectGraph", "graphHash")) or _clean(_get(project_model, "snapshot", "graph_hash"))
    if len(graph_hash) != 64:
        raise DreamGenerateError("Project Model v1 does not expose a valid graph hash")
    return graph_hash


def _get(payload: dict[str, Any], *keys: str, default: Any = None) -> Any:
    current: Any = payload
    for key in keys:
        if not isinstance(current, dict):
            return default
        current = current.get(key)
    return default if current is None else current


def _clean(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return list(dict.fromkeys(str(item).strip() for item in value if str(item).strip()))


def _sha_text(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def _file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m arena.dream_generate")
    parser.add_argument("--project-model", required=True)
    parser.add_argument("--capability-map", required=True)
    parser.add_argument("--scorecard", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--live-model")
    parser.add_argument("--live-provider", default="xai")
    parser.add_argument("--live-base-url")
    parser.add_argument("--live-api-key-env", default="XAI_API_KEY")
    args = parser.parse_args(argv)
    try:
        output = write_generated_dreams(
            project_model_path=args.project_model,
            capability_map_path=args.capability_map,
            scorecard_path=args.scorecard,
            output_path=args.output,
            live_provider=args.live_provider,
            live_base_url=args.live_base_url,
            live_model=args.live_model,
            live_api_key_env=args.live_api_key_env,
        )
    except (DreamGenerateError, OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"dream generate failed: {exc}", file=sys.stderr)
        return 3 if "--live-model" in str(exc) else 1
    print(str(output))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())

```

### `arena/dream_research.py`
```python
"""Research raw dream proposals into premise-dense advisory hypotheses.

This is the tier-3 to tier-2 handoff: a soft model maps each divergent idea onto
concrete current-state claims. The output is still untrusted; the deterministic
``dream_gate`` must resolve every cited anchor before emit.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

from arena.llm_adapter import OpenAICompatibleChatClient, resolve_provider_config

SCHEMA_VERSION = "dream/v0"
RESEARCHED_BY = "arena.dream_research"
PROMPT_VERSION = "dream-research-v0"
ALLOWED_MODES = {"carrier_swap", "function_remap"}

DreamResearchModel = Callable[[str], dict[str, Any]]


class DreamResearchError(Exception):
    """Raised when dream research fails closed."""


def research_dreams(
    *,
    project_model_path: str | Path,
    capability_map_path: str | Path,
    dreams_path: str | Path,
    model: DreamResearchModel | None = None,
    live_provider: str = "xai",
    live_base_url: str | None = None,
    live_model: str | None = None,
    live_api_key_env: str = "XAI_API_KEY",
) -> dict[str, Any]:
    model_path = Path(project_model_path).resolve()
    cap_path = Path(capability_map_path).resolve()
    raw_path = Path(dreams_path).resolve()
    project_model = _load_json_object(model_path)
    capability_map = _load_json_object(cap_path)
    raw_doc = _load_json_object(raw_path)
    if capability_map.get("review", {}).get("reviewed") is not True:
        raise DreamResearchError("capability map must be operator-reviewed before dream research")

    prompt = _research_prompt(project_model, capability_map, raw_doc)
    if model is None:
        if not live_model:
            raise DreamResearchError("--live-model is required for dream research")
        provider_config = resolve_provider_config(
            live_provider,
            base_url=live_base_url,
            api_key_env=live_api_key_env,
            model=live_model,
            require_explicit_model=True,
        )
        client = OpenAICompatibleChatClient(provider_config, temperature=0.2, max_tokens=4096)
        result = client.complete(
            messages=[
                {"role": "system", "content": "Return only JSON with a top-level dreams array."},
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
        )
        researched = _parse_model_json(result.text)
        model_id = result.model
    else:
        researched = model(prompt)
        if not isinstance(researched, dict):
            raise DreamResearchError("injected model must return a JSON object")
        model_id = _clean(raw_doc.get("provenance", {}).get("modelId")) or "injected-model"

    dreams = _researched_dreams(researched.get("dreams", []), capability_map=capability_map)
    if not dreams:
        raise DreamResearchError("research produced no dreams with required premise surface")
    return {
        "schemaVersion": SCHEMA_VERSION,
        "projectId": _project_id(project_model, capability_map, raw_doc),
        "sourceModel": {"projectModelV1Path": str(model_path), "graphHash": _graph_hash(project_model)},
        "capabilityMap": {"path": str(cap_path), "reviewed": True},
        "dreams": dreams,
        "provenance": _provenance(raw_doc, prompt, model_id, model_path, cap_path, raw_path),
    }


def write_researched_dreams(
    *,
    project_model_path: str | Path,
    capability_map_path: str | Path,
    dreams_path: str | Path,
    output_path: str | Path,
    model: DreamResearchModel | None = None,
    live_provider: str = "xai",
    live_base_url: str | None = None,
    live_model: str | None = None,
    live_api_key_env: str = "XAI_API_KEY",
) -> Path:
    document = research_dreams(
        project_model_path=project_model_path,
        capability_map_path=capability_map_path,
        dreams_path=dreams_path,
        model=model,
        live_provider=live_provider,
        live_base_url=live_base_url,
        live_model=live_model,
        live_api_key_env=live_api_key_env,
    )
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return output


def _researched_dreams(raw_dreams: Any, *, capability_map: dict[str, Any]) -> list[dict[str, Any]]:
    if not isinstance(raw_dreams, list):
        return []
    capability_ids = {
        str(item.get("id"))
        for item in capability_map.get("capabilities", [])
        if isinstance(item, dict) and item.get("id")
    }
    out: list[dict[str, Any]] = []
    for raw in raw_dreams:
        if not isinstance(raw, dict):
            continue
        mode = _clean(raw.get("mode"))
        targets = _string_list(raw.get("targetCapabilityIds"))
        evidence = [item for item in raw.get("citedEvidence", []) if isinstance(item, dict)] if isinstance(raw.get("citedEvidence"), list) else []
        recipe = raw.get("validationRecipe") if isinstance(raw.get("validationRecipe"), dict) else {}
        if mode not in ALLOWED_MODES or not targets or not evidence or not recipe:
            continue
        if any(target not in capability_ids for target in targets):
            continue
        normalized = {
            "id": _clean(raw.get("id")) or f"dream-{len(out) + 1}",
            "mode": mode,
            "idea": _clean(raw.get("idea")),
            "targetCapabilityIds": targets,
            "citedEvidence": evidence,
            "rationale": _clean(raw.get("rationale")),
            "premiseConfidence": _clean(raw.get("premiseConfidence")) or "unresolved",
            "conclusionConfidence": _conclusion(raw.get("conclusionConfidence")),
            "validationRecipe": {
                "action": _clean(recipe.get("action")),
                "observable": _clean(recipe.get("observable")),
                "expectedDirection": _clean(recipe.get("expectedDirection")),
            },
        }
        if raw.get("neighborAlternativeId") is not None:
            normalized["neighborAlternativeId"] = _clean(raw.get("neighborAlternativeId")) or None
        if normalized["idea"] and normalized["rationale"] and normalized["validationRecipe"]["observable"]:
            out.append(normalized)
    return out


def _provenance(
    raw_doc: dict[str, Any], prompt: str, model_id: str, model_path: Path, cap_path: Path, raw_path: Path
) -> dict[str, Any]:
    previous_raw = raw_doc.get("provenance")
    previous: dict[str, Any] = previous_raw if isinstance(previous_raw, dict) else {}
    prompt_hashes_raw = previous.get("promptHashes")
    prompt_hashes = dict(prompt_hashes_raw) if isinstance(prompt_hashes_raw, dict) else {}
    prompt_hashes["research"] = _sha_text(prompt)
    prompt_hashes["researchPromptVersion"] = _sha_text(PROMPT_VERSION)
    input_hashes_raw = previous.get("inputHashes")
    input_hashes = dict(input_hashes_raw) if isinstance(input_hashes_raw, dict) else {}
    input_hashes.update(
        {
            "projectModelV1": _file_sha(model_path),
            "capabilityMap": _file_sha(cap_path),
            "rawDreams": _file_sha(raw_path),
        }
    )
    return {
        "generatedBy": _clean(previous.get("generatedBy")) or "arena.dream_generate",
        "researchedBy": RESEARCHED_BY,
        "promptHashes": prompt_hashes,
        "modelId": model_id,
        "inputHashes": input_hashes,
    }


def _research_prompt(project_model: dict[str, Any], capability_map: dict[str, Any], raw_doc: dict[str, Any]) -> str:
    compact = {
        "capabilities": capability_map.get("capabilities", []),
        "components": _get(project_model, "snapshot", "components", default=[]),
        "contracts": _get(project_model, "snapshot", "contracts", default=[]),
        "verificationGaps": _get(project_model, "snapshot", "verification_gaps", default=[]),
        "nearNeighborAlternatives": _get(project_model, "snapshot", "near_neighbor_alternatives", default=[]),
        "graphNodes": _get(project_model, "projectGraph", "nodes", default=[]),
        "graphEdges": _get(project_model, "projectGraph", "edges", default=[]),
        "rawDreams": raw_doc.get("dreams", []),
    }
    return (
        "Research these raw tier-3 dream proposals into concrete current-state claims. "
        "Do not claim benefit certainty. Preserve novelty, add/check citedEvidence anchors, and return JSON only: {\"dreams\":[...]}. "
        "Every citedEvidence contentHash must be the SHA-256 of the canonical JSON for the cited anchor object. Current model:\n"
        + json.dumps(compact, sort_keys=True, ensure_ascii=False)
    )


def _conclusion(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        return {"band": "low", "value": 0.1}
    band = _clean(value.get("band"))
    if band not in {"low", "medium"}:
        band = "low"
    raw_number = value.get("value")
    number = float(raw_number) if isinstance(raw_number, int | float) else 0.1
    return {"band": band, "value": min(max(number, 0.0), 0.7)}


def _parse_model_json(text: str) -> dict[str, Any]:
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        raise DreamResearchError("live model did not return valid JSON") from exc
    if not isinstance(payload, dict):
        raise DreamResearchError("live model JSON must be an object")
    return payload


def _load_json_object(path: str | Path) -> dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise DreamResearchError(f"{path} must contain a JSON object")
    return payload


def _project_id(project_model: dict[str, Any], capability_map: dict[str, Any], raw_doc: dict[str, Any]) -> str:
    return (
        _clean(raw_doc.get("projectId"))
        or _clean(capability_map.get("projectId"))
        or _clean(_get(project_model, "project", "projectId"))
        or _clean(_get(project_model, "snapshot", "project_id"))
        or "project"
    )


def _graph_hash(project_model: dict[str, Any]) -> str:
    graph_hash = _clean(_get(project_model, "projectGraph", "graphHash")) or _clean(_get(project_model, "snapshot", "graph_hash"))
    if len(graph_hash) != 64:
        raise DreamResearchError("Project Model v1 does not expose a valid graph hash")
    return graph_hash


def _get(payload: dict[str, Any], *keys: str, default: Any = None) -> Any:
    current: Any = payload
    for key in keys:
        if not isinstance(current, dict):
            return default
        current = current.get(key)
    return default if current is None else current


def _clean(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return list(dict.fromkeys(str(item).strip() for item in value if str(item).strip()))


def _sha_text(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def _file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m arena.dream_research")
    parser.add_argument("--project-model", required=True)
    parser.add_argument("--capability-map", required=True)
    parser.add_argument("--dreams", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--live-model")
    parser.add_argument("--live-provider", default="xai")
    parser.add_argument("--live-base-url")
    parser.add_argument("--live-api-key-env", default="XAI_API_KEY")
    args = parser.parse_args(argv)
    try:
        output = write_researched_dreams(
            project_model_path=args.project_model,
            capability_map_path=args.capability_map,
            dreams_path=args.dreams,
            output_path=args.output,
            live_provider=args.live_provider,
            live_base_url=args.live_base_url,
            live_model=args.live_model,
            live_api_key_env=args.live_api_key_env,
        )
    except (DreamResearchError, OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"dream research failed: {exc}", file=sys.stderr)
        return 3 if "--live-model" in str(exc) else 1
    print(str(output))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())

```

### `arena/dream_gate.py`
```python
"""Deterministic premise-resolution gate for tier-3 dream proposals.

The gate is the trust boundary for the dream lane. It does not judge whether a
dream is useful. It only proves that every cited current-state premise resolves
against the real Project Model v1 / reviewed capability map and that the dream
carries a validation recipe. Dreams that fail this check are killed before emit.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from arena.capability_lift import CapabilityLiftError, validate_capability_map

SCHEMA_VERSION = "dream/v0"
TRACE_SCHEMA_VERSION = "dream-gate-trace/v0"
GATED_BY = "arena.dream_gate"
ALLOWED_MODES = {"carrier_swap", "function_remap"}
ANCHOR_KINDS = {
    "graphNode",
    "graphEdge",
    "component",
    "contract",
    "capability",
    "verificationGap",
    "nearNeighborAlternative",
}

_SCHEMA_PATH = Path(__file__).resolve().parents[1] / "docs" / "schemas" / "dream-v0.schema.json"


class DreamGateError(Exception):
    """Raised when the gate cannot evaluate its inputs fail-closed."""


@dataclass(frozen=True, slots=True)
class GateResult:
    document: dict[str, Any]
    trace: dict[str, Any]
    accepted_count: int
    killed_count: int


def anchor_content_hash(anchor: dict[str, Any]) -> str:
    """Canonical content hash for a resolved evidence anchor."""

    encoded = json.dumps(anchor, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(encoded).hexdigest()


def gate_dreams(
    *,
    project_model_path: str | Path,
    capability_map_path: str | Path,
    dreams_path: str | Path,
) -> GateResult:
    model_path = Path(project_model_path).resolve()
    cap_path = Path(capability_map_path).resolve()
    source_path = Path(dreams_path).resolve()
    model = _load_json_object(model_path)
    capability_map = _load_json_object(cap_path)
    dreams_doc = _load_json_object(source_path)

    if capability_map.get("review", {}).get("reviewed") is not True:
        raise DreamGateError("capability map is not operator-reviewed")
    try:
        validate_capability_map(capability_map, model)
    except CapabilityLiftError as exc:
        raise DreamGateError(str(exc)) from exc

    indexes = _anchor_indexes(model, capability_map)
    capability_ids = set(indexes["capability"])
    near_neighbor_ids = set(indexes["nearNeighborAlternative"])
    accepted: list[dict[str, Any]] = []
    killed: list[dict[str, Any]] = []

    for raw in dreams_doc.get("dreams", []):
        if not isinstance(raw, dict):
            killed.append({"id": "<non-object>", "premiseConfidence": "unresolved", "reasons": ["dream is not an object"]})
            continue
        normalized, reasons, premise_confidence = _evaluate_dream(
            raw,
            indexes=indexes,
            capability_ids=capability_ids,
            near_neighbor_ids=near_neighbor_ids,
        )
        if not reasons and premise_confidence == "all_resolved":
            accepted.append(normalized)
        else:
            killed.append(
                {
                    "id": str(raw.get("id", "<missing>")),
                    "premiseConfidence": premise_confidence,
                    "reasons": reasons or ["premise confidence was not all_resolved"],
                }
            )

    document = {
        "schemaVersion": SCHEMA_VERSION,
        "projectId": _project_id(model, capability_map, dreams_doc),
        "sourceModel": {
            "projectModelV1Path": str(model_path),
            "graphHash": _graph_hash(model),
        },
        "capabilityMap": {
            "path": str(cap_path),
            "reviewed": True,
        },
        "dreams": accepted,
        "provenance": _provenance(dreams_doc, model_path, cap_path, source_path),
    }
    validate_dream_schema(document)
    trace = {
        "schemaVersion": TRACE_SCHEMA_VERSION,
        "acceptedDreamIds": [dream["id"] for dream in accepted],
        "killedDreams": killed,
        "summary": {"accepted": len(accepted), "killed": len(killed)},
    }
    return GateResult(document=document, trace=trace, accepted_count=len(accepted), killed_count=len(killed))


def write_gated_dreams(
    *,
    project_model_path: str | Path,
    capability_map_path: str | Path,
    dreams_path: str | Path,
    output_path: str | Path,
    trace_path: str | Path | None = None,
) -> GateResult:
    result = gate_dreams(
        project_model_path=project_model_path,
        capability_map_path=capability_map_path,
        dreams_path=dreams_path,
    )
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result.document, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if trace_path is not None:
        trace = Path(trace_path)
        trace.parent.mkdir(parents=True, exist_ok=True)
        trace.write_text(json.dumps(result.trace, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def validate_dream_schema(document: dict[str, Any]) -> None:
    schema = _load_json_object(_SCHEMA_PATH)
    errors = sorted(Draft202012Validator(schema).iter_errors(document), key=lambda error: list(error.path))
    if errors:
        first = errors[0]
        location = "/".join(str(part) for part in first.path) or "<root>"
        raise DreamGateError(f"dream/v0 failed schema validation at {location}: {first.message}")


def _evaluate_dream(
    dream: dict[str, Any], *, indexes: dict[str, dict[str, dict[str, Any]]], capability_ids: set[str], near_neighbor_ids: set[str]
) -> tuple[dict[str, Any], list[str], str]:
    reasons: list[str] = []
    resolved_count = 0
    evidence_items: list[dict[str, Any]] = []

    dream_id = _clean(dream.get("id"))
    if not dream_id:
        reasons.append("missing id")
    mode = _clean(dream.get("mode"))
    if mode not in ALLOWED_MODES:
        reasons.append("mode must be carrier_swap or function_remap")
    idea = _clean(dream.get("idea"))
    if not idea:
        reasons.append("missing idea")
    rationale = _clean(dream.get("rationale"))
    if not rationale:
        reasons.append("missing rationale")

    target_capabilities = _string_list(dream.get("targetCapabilityIds"))
    if not target_capabilities:
        reasons.append("missing targetCapabilityIds")
    for capability_id in target_capabilities:
        if capability_id not in capability_ids:
            reasons.append(f"unknown target capability {capability_id}")

    raw_evidence = dream.get("citedEvidence")
    if not isinstance(raw_evidence, list) or not raw_evidence:
        reasons.append("missing citedEvidence")
        raw_evidence = []
    for index, evidence in enumerate(raw_evidence):
        if not isinstance(evidence, dict):
            reasons.append(f"citedEvidence[{index}] is not an object")
            continue
        normalized_evidence = {
            "anchorKind": _clean(evidence.get("anchorKind")),
            "anchorId": _clean(evidence.get("anchorId")),
            "contentHash": _clean(evidence.get("contentHash")),
        }
        claim = _clean(evidence.get("claim"))
        if claim:
            normalized_evidence["claim"] = claim
        anchor_kind = normalized_evidence["anchorKind"]
        anchor_id = normalized_evidence["anchorId"]
        content_hash = normalized_evidence["contentHash"]
        anchor = indexes.get(anchor_kind, {}).get(anchor_id)
        if anchor_kind not in ANCHOR_KINDS:
            reasons.append(f"citedEvidence[{index}] has invalid anchorKind {anchor_kind!r}")
        elif anchor is None:
            reasons.append(f"citedEvidence[{index}] unresolved {anchor_kind} {anchor_id}")
        elif content_hash != anchor_content_hash(anchor):
            reasons.append(f"citedEvidence[{index}] contentHash mismatch for {anchor_kind} {anchor_id}")
        else:
            resolved_count += 1
        evidence_items.append(normalized_evidence)

    recipe = dream.get("validationRecipe")
    if not isinstance(recipe, dict):
        reasons.append("missing validationRecipe")
        recipe = {}
    validation_recipe = {
        "action": _clean(recipe.get("action")),
        "observable": _clean(recipe.get("observable")),
        "expectedDirection": _clean(recipe.get("expectedDirection")),
    }
    if not validation_recipe["action"] or not validation_recipe["observable"]:
        reasons.append("validationRecipe action and observable are required")
    if validation_recipe["expectedDirection"] not in {"decrease", "increase", "unchanged", "tests_pass"}:
        reasons.append("validationRecipe expectedDirection is invalid")

    conclusion = dream.get("conclusionConfidence")
    if not isinstance(conclusion, dict):
        reasons.append("missing conclusionConfidence")
        conclusion = {}
    band = _clean(conclusion.get("band"))
    value = conclusion.get("value")
    if band not in {"low", "medium"}:
        reasons.append("conclusionConfidence.band must be low or medium")
    if not isinstance(value, int | float) or value < 0 or value > 0.7:
        reasons.append("conclusionConfidence.value must be between 0 and 0.7")
        numeric_value = 0.0
    else:
        numeric_value = float(value)

    neighbor = dream.get("neighborAlternativeId")
    neighbor_id = _clean(neighbor) if neighbor is not None else None
    if neighbor_id and neighbor_id not in near_neighbor_ids:
        reasons.append(f"unknown neighborAlternativeId {neighbor_id}")

    if not evidence_items:
        premise_confidence = "unresolved"
    elif resolved_count == len(evidence_items) and not any(reason.startswith("citedEvidence") for reason in reasons):
        premise_confidence = "all_resolved"
    elif resolved_count > 0:
        premise_confidence = "partial"
    else:
        premise_confidence = "unresolved"

    normalized = {
        "id": dream_id,
        "mode": mode,
        "idea": idea,
        "targetCapabilityIds": target_capabilities,
        "citedEvidence": evidence_items,
        "rationale": rationale,
        "premiseConfidence": premise_confidence,
        "conclusionConfidence": {"band": band, "value": numeric_value},
        "validationRecipe": validation_recipe,
    }
    if neighbor is not None:
        normalized["neighborAlternativeId"] = neighbor_id
    return normalized, reasons, premise_confidence


def _anchor_indexes(model: dict[str, Any], capability_map: dict[str, Any]) -> dict[str, dict[str, dict[str, Any]]]:
    return {
        "graphNode": _index_by_id(_get(model, "projectGraph", "nodes", default=[])),
        "graphEdge": _index_by_id(_get(model, "projectGraph", "edges", default=[])),
        "component": _index_by_id(_get(model, "snapshot", "components", default=[])),
        "contract": _index_by_id(_get(model, "snapshot", "contracts", default=[])),
        "capability": _index_by_id(capability_map.get("capabilities", [])),
        "verificationGap": _index_by_id(_get(model, "snapshot", "verification_gaps", default=[])),
        "nearNeighborAlternative": _index_by_id(
            _get(model, "snapshot", "near_neighbor_alternatives", default=[])
        ),
    }


def _index_by_id(items: Any) -> dict[str, dict[str, Any]]:
    if not isinstance(items, list):
        return {}
    return {
        str(item.get("id")): item
        for item in items
        if isinstance(item, dict) and isinstance(item.get("id"), str) and item.get("id")
    }


def _provenance(dreams_doc: dict[str, Any], model_path: Path, cap_path: Path, dreams_path: Path) -> dict[str, Any]:
    original_raw = dreams_doc.get("provenance")
    original: dict[str, Any] = original_raw if isinstance(original_raw, dict) else {}
    prompt_hashes_raw = original.get("promptHashes")
    prompt_hashes = prompt_hashes_raw if isinstance(prompt_hashes_raw, dict) else {}
    prompt_hashes = {
        str(key): str(value)
        for key, value in prompt_hashes.items()
        if isinstance(value, str) and re.fullmatch(r"[a-f0-9]{64}", value)
    }
    prompt_hashes.setdefault("gate", hashlib.sha256(GATED_BY.encode()).hexdigest())
    input_hashes_raw = original.get("inputHashes")
    input_hashes = input_hashes_raw if isinstance(input_hashes_raw, dict) else {}
    normalized_input_hashes = {
        str(key): str(value)
        for key, value in input_hashes.items()
        if isinstance(value, str) and re.fullmatch(r"[a-f0-9]{64}", value)
    }
    normalized_input_hashes.update(
        {
            "projectModelV1": _file_sha(model_path),
            "capabilityMap": _file_sha(cap_path),
            "researchedDreams": _file_sha(dreams_path),
        }
    )
    return {
        "generatedBy": _clean(original.get("generatedBy")) or "arena.dream_generate",
        "researchedBy": _clean(original.get("researchedBy")) or "arena.dream_research",
        "promptHashes": prompt_hashes,
        "modelId": _clean(original.get("modelId")) or "unknown",
        "inputHashes": normalized_input_hashes,
    }


def _project_id(model: dict[str, Any], capability_map: dict[str, Any], dreams_doc: dict[str, Any]) -> str:
    return (
        _clean(dreams_doc.get("projectId"))
        or _clean(capability_map.get("projectId"))
        or _clean(_get(model, "project", "projectId"))
        or _clean(_get(model, "snapshot", "project_id"))
        or "project"
    )


def _graph_hash(model: dict[str, Any]) -> str:
    graph_hash = _clean(_get(model, "projectGraph", "graphHash")) or _clean(_get(model, "snapshot", "graph_hash"))
    if not re.fullmatch(r"[a-f0-9]{64}", graph_hash):
        raise DreamGateError("Project Model v1 does not expose a valid 64-hex graph hash")
    return graph_hash


def _get(payload: dict[str, Any], *keys: str, default: Any = None) -> Any:
    current: Any = payload
    for key in keys:
        if not isinstance(current, dict):
            return default
        current = current.get(key)
    return default if current is None else current


def _load_json_object(path: str | Path) -> dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise DreamGateError(f"{path} must contain a JSON object")
    return payload


def _clean(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return list(dict.fromkeys(str(item).strip() for item in value if str(item).strip()))


def _file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m arena.dream_gate")
    parser.add_argument("--project-model", required=True)
    parser.add_argument("--capability-map", required=True)
    parser.add_argument("--dreams", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--trace")
    args = parser.parse_args(argv)
    try:
        result = write_gated_dreams(
            project_model_path=args.project_model,
            capability_map_path=args.capability_map,
            dreams_path=args.dreams,
            output_path=args.output,
            trace_path=args.trace,
        )
    except (DreamGateError, OSError, json.JSONDecodeError) as exc:
        print(f"dream gate failed: {exc}", file=sys.stderr)
        return 1
    print(str(args.output))
    if result.accepted_count == 0:
        return 2
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())

```

### `arena/dream_emit.py`
```python
"""Render gated ``dream/v0`` advisory hypotheses to ``dream.md``.

Emit is deterministic and faithful. It does not call a model, does not re-rank via
soft judgment, and refuses any input containing unresolved/partial dreams. The
dream lane is also hard-separated from the deterministic proposal lane: this
module refuses to write ``proposal.md``.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

SCHEMA_VERSION = "dream/v0"
_SCHEMA_PATH = Path(__file__).resolve().parents[1] / "docs" / "schemas" / "dream-v0.schema.json"


class DreamEmitError(Exception):
    """Raised when gated dreams cannot be faithfully rendered."""


def load_gated_dreams(path: str | Path) -> dict[str, Any]:
    dream_path = Path(path)
    try:
        payload = json.loads(dream_path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise DreamEmitError(f"cannot read dream artifact: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise DreamEmitError(f"dream artifact is not valid JSON: {exc}") from exc
    if not isinstance(payload, dict):
        raise DreamEmitError("dream artifact must be a JSON object")
    if payload.get("schemaVersion") != SCHEMA_VERSION:
        raise DreamEmitError(f"dream artifact must have schemaVersion {SCHEMA_VERSION}")
    validate_schema(payload)
    return payload


def validate_schema(document: dict[str, Any]) -> None:
    schema = json.loads(_SCHEMA_PATH.read_text(encoding="utf-8"))
    errors = sorted(Draft202012Validator(schema).iter_errors(document), key=lambda error: list(error.path))
    if errors:
        first = errors[0]
        location = "/".join(str(part) for part in first.path) or "<root>"
        raise DreamEmitError(f"dream artifact failed schema validation at {location}: {first.message}")


def select_renderable_dreams(document: dict[str, Any]) -> list[dict[str, Any]]:
    dreams = document.get("dreams")
    if not isinstance(dreams, list):
        raise DreamEmitError("dream artifact has no dreams array")
    unresolved = [
        str(dream.get("id", "<missing>"))
        for dream in dreams
        if isinstance(dream, dict) and dream.get("premiseConfidence") != "all_resolved"
    ]
    if unresolved:
        raise DreamEmitError(f"refusing to render non-all_resolved dream(s): {', '.join(unresolved)}")
    renderable = [dream for dream in dreams if isinstance(dream, dict)]
    if not renderable:
        raise DreamEmitError("dream artifact has no all_resolved dreams to render")
    return sorted(renderable, key=_rank_key)


def render_dream_markdown(document: dict[str, Any]) -> str:
    dreams = select_renderable_dreams(document)
    lines: list[str] = [
        "# Dream Proposals",
        "",
        "Advisory tier-3 hypotheses only. These are not deterministic changes and do not authorize mutation.",
        "",
    ]
    for index, dream in enumerate(dreams, start=1):
        lines.extend(_render_one(index, dream))
        lines.append("")
    lines.extend(_footer(document))
    return "\n".join(lines) + "\n"


def emit_dream(dream_path: str | Path, output_path: str | Path = "dream.md") -> Path:
    output = Path(output_path)
    if output.name == "proposal.md":
        raise DreamEmitError("dream_emit refuses to write proposal.md; use dream.md for the advisory lane")
    document = load_gated_dreams(dream_path)
    markdown = render_dream_markdown(document)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(markdown, encoding="utf-8")
    return output


def _rank_key(dream: dict[str, Any]) -> tuple[int, int, int, str]:
    mode = str(dream.get("mode", ""))
    neighbor = dream.get("neighborAlternativeId")
    if mode == "carrier_swap" and isinstance(neighbor, str) and neighbor:
        mode_rank = 0
    elif mode == "carrier_swap":
        mode_rank = 1
    else:
        mode_rank = 2
    evidence_count = len(dream.get("citedEvidence", [])) if isinstance(dream.get("citedEvidence"), list) else 0
    target_count = len(dream.get("targetCapabilityIds", [])) if isinstance(dream.get("targetCapabilityIds"), list) else 0
    return (mode_rank, -evidence_count, -target_count, str(dream.get("id", "")))


def _render_one(index: int, dream: dict[str, Any]) -> list[str]:
    confidence_raw = dream.get("conclusionConfidence")
    confidence: dict[str, Any] = confidence_raw if isinstance(confidence_raw, dict) else {}
    recipe_raw = dream.get("validationRecipe")
    recipe: dict[str, Any] = recipe_raw if isinstance(recipe_raw, dict) else {}
    lines = [
        f"## {index}. {str(dream.get('idea', '')).strip()}",
        "",
        f"- Dream id: `{str(dream.get('id', '')).strip()}`",
        f"- Mode: `{str(dream.get('mode', '')).strip()}`",
        "- Target capabilities: " + ", ".join(f"`{item}`" for item in dream.get("targetCapabilityIds", [])),
        "",
        "### Cited current-state evidence",
    ]
    for evidence in dream.get("citedEvidence", []):
        if not isinstance(evidence, dict):
            continue
        kind = str(evidence.get("anchorKind", "")).strip()
        anchor_id = str(evidence.get("anchorId", "")).strip()
        claim = str(evidence.get("claim", "")).strip() or "current-state premise resolved"
        lines.append(f"- {kind} `{anchor_id}` — {claim}")
    lines.extend(
        [
            "",
            "### Rationale",
            str(dream.get("rationale", "")).strip(),
            "",
            "### Confidence",
            f"- Premise confidence (mechanical): `{str(dream.get('premiseConfidence', '')).strip()}`",
            "- Conclusion confidence (speculative/capped): "
            f"`{str(confidence.get('band', '')).strip()}` ({confidence.get('value')})",
            "",
            "### Validation recipe",
            "To validate, try `"
            + str(recipe.get("action", "")).strip()
            + "`; check `"
            + str(recipe.get("observable", "")).strip()
            + "` moves `"
            + str(recipe.get("expectedDirection", "")).strip()
            + "`.",
        ]
    )
    return lines


def _footer(document: dict[str, Any]) -> list[str]:
    source_raw = document.get("sourceModel")
    source: dict[str, Any] = source_raw if isinstance(source_raw, dict) else {}
    provenance_raw = document.get("provenance")
    provenance: dict[str, Any] = provenance_raw if isinstance(provenance_raw, dict) else {}
    prompt_hashes_raw = provenance.get("promptHashes")
    prompt_hashes: dict[str, Any] = prompt_hashes_raw if isinstance(prompt_hashes_raw, dict) else {}
    prompt_bits = ", ".join(f"{key}={prompt_hashes[key]}" for key in sorted(prompt_hashes))
    return [
        "---",
        "Provenance:",
        f"- Model id: `{str(provenance.get('modelId', '')).strip()}`",
        f"- Source graphHash: `{str(source.get('graphHash', '')).strip()}`",
        f"- Prompt hashes: {prompt_bits or '_none recorded_'}",
    ]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m arena.dream_emit")
    parser.add_argument("--dreams", required=True)
    parser.add_argument("--output", default="dream.md")
    args = parser.parse_args(argv)
    try:
        output = emit_dream(args.dreams, args.output)
    except DreamEmitError as exc:
        print(f"dream emit failed: {exc}", file=sys.stderr)
        return 1
    print(str(output))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())

```

### `arena/dream_run.py`
```python
"""``dream run <repo>`` -- orchestrate the advisory tier-3 dream lane.

This is a thin, fail-closed driver parallel to the proposal lane. It wires
existing/new stage CLIs through subprocess boundaries and preserves the workdir on
any failed or review-blocked run. The generated capability map is intentionally
unreviewed by default, so a normal first run stops at exit 4 until the operator
reviews/edits the map; tests inject stages to exercise the full offline path.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from arena.llm_adapter import resolve_api_key_with_source

EXIT_OK = 0
EXIT_STAGE_FAILURE = 1
EXIT_NO_DREAM = 2
EXIT_USAGE = 3
EXIT_UNREVIEWED_CAPABILITY_MAP = 4

_REPO_ROOT = Path(__file__).resolve().parents[1]
_DECOMPOSE_MODULE = "arena.project_model_cli"
_INTAKE_MODULE = "arena.project_intake_scorecard"
_CAPABILITY_MODULE = "arena.capability_lift"
_GENERATE_MODULE = "arena.dream_generate"
_RESEARCH_MODULE = "arena.dream_research"
_GATE_MODULE = "arena.dream_gate"
_EMIT_MODULE = "arena.dream_emit"


@dataclass(frozen=True, slots=True)
class StageResult:
    returncode: int
    stdout: str = ""
    stderr: str = ""


StageRunner = Callable[[str, list[str], dict[str, str]], StageResult]
GitRunner = Callable[[list[str]], None]


@dataclass(slots=True)
class RunConfig:
    repo: str
    output: Path
    profile: str = "new-project"
    decompose_live: bool = False
    live_model: str | None = None
    live_api_key_env: str = "XAI_API_KEY"
    live_provider: str = "xai"
    live_base_url: str | None = None
    workdir: Path | None = None
    keep_workdir: bool = False
    capability_map: Path | None = None


class DreamRunError(Exception):
    """Terminal run outcome with a process exit code."""

    def __init__(self, message: str, exit_code: int, *, already_reported: bool = False) -> None:
        super().__init__(message)
        self.exit_code = exit_code
        self.already_reported = already_reported


def _subprocess_stage(module: str, args: list[str], env: dict[str, str]) -> StageResult:
    proc = subprocess.run(
        [sys.executable, "-m", module, *args],
        cwd=_REPO_ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    return StageResult(proc.returncode, stdout=proc.stdout, stderr=proc.stderr)


def _run_git(args: list[str]) -> None:
    try:
        subprocess.run(["git", *args], check=True, capture_output=True, text=True)
    except FileNotFoundError as exc:
        raise DreamRunError("git is not available on PATH", EXIT_STAGE_FAILURE) from exc
    except subprocess.CalledProcessError as exc:
        detail = (exc.stderr or "").strip() or f"git exited {exc.returncode}"
        raise DreamRunError(f"git clone failed: {detail}", EXIT_STAGE_FAILURE) from exc


def _looks_like_git_url(value: str) -> bool:
    lowered = value.lower()
    if lowered.endswith(".git") or lowered.startswith(("http://", "https://", "git://", "ssh://")):
        return True
    head = value.split("/", 1)[0]
    return "@" in head and ":" in head


def resolve_target(repo: str, workdir: Path, git_runner: GitRunner) -> Path:
    local = Path(repo).expanduser()
    if local.is_dir():
        return local.resolve()
    if _looks_like_git_url(repo):
        dest = workdir / "target"
        git_runner(["clone", "--depth", "1", repo, str(dest)])
        return dest.resolve()
    raise DreamRunError(f"repo must be an existing local directory or a git URL: {repo!r}", EXIT_USAGE)


def _subprocess_env(config: RunConfig) -> dict[str, str]:
    env = dict(os.environ)
    existing = env.get("PYTHONPATH", "")
    parts = [str(_REPO_ROOT), *(part for part in existing.split(os.pathsep) if part)]
    env["PYTHONPATH"] = os.pathsep.join(parts)
    env["BUILD_ARENA_LLM_API_KEY_ENV"] = config.live_api_key_env
    if config.live_model:
        env["BUILD_ARENA_LLM_MODEL"] = config.live_model
    if config.live_base_url:
        env["BUILD_ARENA_LLM_BASE_URL"] = config.live_base_url
    return env


def _preflight(config: RunConfig) -> None:
    if not config.live_model:
        raise DreamRunError("--live-model is required: generation and research are live model stages", EXIT_USAGE)
    try:
        resolve_api_key_with_source(config.live_api_key_env)
    except ValueError as exc:
        raise DreamRunError(
            f"{exc} (set the key, or choose another env var with --live-api-key-env)", EXIT_USAGE
        ) from exc


def _derive_project_id(target: Path) -> str:
    return target.name or "project"


def _glob_manifest(snap_root: Path) -> Path:
    matches = sorted(snap_root.glob("*/manifest.json"))
    if len(matches) != 1:
        raise DreamRunError(
            f"expected exactly one snapshot manifest under {snap_root}, found {len(matches)}",
            EXIT_STAGE_FAILURE,
        )
    return matches[0]


def _resolve_model_v1(manifest_path: Path) -> Path:
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise DreamRunError(f"cannot read snapshot manifest: {exc}", EXIT_STAGE_FAILURE) from exc
    rel = manifest.get("project_model_primary_path") or manifest.get("project_model_v1_path")
    if not isinstance(rel, str) or not rel:
        raise DreamRunError("snapshot manifest does not record a project-model v1 path", EXIT_STAGE_FAILURE)
    resolved = (manifest_path.parent / rel).resolve()
    if not resolved.is_file():
        raise DreamRunError(f"project model v1 artifact missing at {resolved}", EXIT_STAGE_FAILURE)
    return resolved


def _fail_stage(stage: str, result: StageResult, workdir: Path) -> DreamRunError:
    detail = (result.stderr or result.stdout or "").strip()
    suffix = f": {detail}" if detail else ""
    return DreamRunError(
        f"stage '{stage}' failed (exit {result.returncode}){suffix}. Workdir preserved at {workdir}",
        EXIT_STAGE_FAILURE,
    )


def _decompose_args(config: RunConfig, target: Path, snap_root: Path) -> list[str]:
    args = [
        "snapshot",
        "--project",
        str(target),
        "--artifacts-root",
        str(snap_root),
        "--project-id",
        _derive_project_id(target),
        "--goal",
        "build-arena dream run",
        "--llm-mode",
        "live" if config.decompose_live else "fixture",
    ]
    if config.decompose_live:
        args += ["--allow-live", "--live-provider", config.live_provider, "--live-api-key-env", config.live_api_key_env]
        if config.live_model:
            args += ["--live-model", config.live_model]
        if config.live_base_url:
            args += ["--live-base-url", config.live_base_url]
    return args


def _live_stage_flags(config: RunConfig) -> list[str]:
    flags = ["--live-model", str(config.live_model), "--live-provider", config.live_provider, "--live-api-key-env", config.live_api_key_env]
    if config.live_base_url:
        flags += ["--live-base-url", config.live_base_url]
    return flags


def _require_reviewed(capability_map_path: Path, workdir: Path) -> None:
    try:
        capability_map = json.loads(capability_map_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise DreamRunError(f"cannot read capability map: {exc}", EXIT_STAGE_FAILURE) from exc
    if not isinstance(capability_map, dict):
        raise DreamRunError("capability map must be a JSON object", EXIT_STAGE_FAILURE)
    if capability_map.get("review", {}).get("reviewed") is not True:
        raise DreamRunError(
            f"capability map is not operator-reviewed; edit {capability_map_path} so review.reviewed is true, then rerun. Workdir preserved at {workdir}",
            EXIT_UNREVIEWED_CAPABILITY_MAP,
        )


def _dream_count(path: Path) -> int:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return 0
    dreams = payload.get("dreams") if isinstance(payload, dict) else None
    return len(dreams) if isinstance(dreams, list) else 0


def _execute_stages(config: RunConfig, target: Path, workdir: Path, stage_runner: StageRunner, env: dict[str, str]) -> int:
    snap_root = workdir / "snap"
    decompose = stage_runner(_DECOMPOSE_MODULE, _decompose_args(config, target, snap_root), env)
    if decompose.returncode != 0:
        raise _fail_stage("decompose", decompose, workdir)
    model_v1 = _resolve_model_v1(_glob_manifest(snap_root))

    scorecard = workdir / "scorecard.json"
    intake = stage_runner(
        _INTAKE_MODULE,
        ["--project", str(target), "--snapshot", str(model_v1), "--profile", config.profile, "--output", str(scorecard)],
        env,
    )
    if intake.returncode != 0:
        raise _fail_stage("intake", intake, workdir)
    if not scorecard.is_file():
        raise _fail_stage("intake", StageResult(0, stderr="scorecard not written"), workdir)

    if config.capability_map is None:
        capability_map = workdir / "capability-map.json"
        lift = stage_runner(
            _CAPABILITY_MODULE,
            ["--project-model", str(model_v1), "--output", str(capability_map)],
            env,
        )
        if lift.returncode != 0:
            raise _fail_stage("capability_lift", lift, workdir)
        if not capability_map.is_file():
            raise _fail_stage("capability_lift", StageResult(0, stderr="capability map not written"), workdir)
    else:
        capability_map = config.capability_map.expanduser().resolve()
        if not capability_map.is_file():
            raise DreamRunError(f"capability map not found: {capability_map}", EXIT_USAGE)
    _require_reviewed(capability_map, workdir)

    raw_dreams = workdir / "raw-dreams.json"
    generate = stage_runner(
        _GENERATE_MODULE,
        [
            "--project-model",
            str(model_v1),
            "--capability-map",
            str(capability_map),
            "--scorecard",
            str(scorecard),
            "--output",
            str(raw_dreams),
            *_live_stage_flags(config),
        ],
        env,
    )
    if generate.returncode != 0:
        raise _fail_stage("dream_generate", generate, workdir)
    if not raw_dreams.is_file():
        raise _fail_stage("dream_generate", StageResult(0, stderr="raw dreams not written"), workdir)

    researched_dreams = workdir / "researched-dreams.json"
    research = stage_runner(
        _RESEARCH_MODULE,
        [
            "--project-model",
            str(model_v1),
            "--capability-map",
            str(capability_map),
            "--dreams",
            str(raw_dreams),
            "--output",
            str(researched_dreams),
            *_live_stage_flags(config),
        ],
        env,
    )
    if research.returncode != 0:
        raise _fail_stage("dream_research", research, workdir)
    if not researched_dreams.is_file():
        raise _fail_stage("dream_research", StageResult(0, stderr="researched dreams not written"), workdir)

    gated_dreams = workdir / "gated-dreams.json"
    gate_trace = workdir / "dream-gate-trace.json"
    gate = stage_runner(
        _GATE_MODULE,
        [
            "--project-model",
            str(model_v1),
            "--capability-map",
            str(capability_map),
            "--dreams",
            str(researched_dreams),
            "--output",
            str(gated_dreams),
            "--trace",
            str(gate_trace),
        ],
        env,
    )
    if gate.returncode == EXIT_NO_DREAM or (gated_dreams.is_file() and _dream_count(gated_dreams) == 0):
        print(f"No dream survived the premise gate (see {gate_trace}).")
        raise DreamRunError("", EXIT_NO_DREAM, already_reported=True)
    if gate.returncode != 0:
        raise _fail_stage("dream_gate", gate, workdir)
    if not gated_dreams.is_file():
        raise _fail_stage("dream_gate", StageResult(0, stderr="gated dreams not written"), workdir)

    emit = stage_runner(_EMIT_MODULE, ["--dreams", str(gated_dreams), "--output", str(config.output)], env)
    if emit.returncode != 0:
        raise _fail_stage("dream_emit", emit, workdir)
    if not config.output.is_file():
        raise _fail_stage("dream_emit", StageResult(0, stderr="dream.md not written"), workdir)
    return EXIT_OK


def run(config: RunConfig, *, stage_runner: StageRunner = _subprocess_stage, git_runner: GitRunner = _run_git) -> int:
    _preflight(config)
    if config.workdir is not None:
        workdir = config.workdir.expanduser().resolve()
        workdir.mkdir(parents=True, exist_ok=True)
        is_temp = False
    else:
        workdir = Path(tempfile.mkdtemp(prefix="build-arena-dream-")).resolve()
        is_temp = True
    env = _subprocess_env(config)
    succeeded = False
    try:
        target = resolve_target(config.repo, workdir, git_runner)
        code = _execute_stages(config, target, workdir, stage_runner, env)
        succeeded = code == EXIT_OK
        if succeeded and config.keep_workdir:
            print(f"Intermediate artifacts kept at {workdir}", file=sys.stderr)
        return code
    finally:
        if is_temp and succeeded and not config.keep_workdir:
            shutil.rmtree(workdir, ignore_errors=True)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="dream")
    sub = parser.add_subparsers(dest="command", required=True)
    run_parser = sub.add_parser("run", help="emit advisory dream.md for a repository")
    run_parser.add_argument("repo", help="local path or git URL of the target repository")
    run_parser.add_argument("--output", default="dream.md", help="output path (default dream.md)")
    run_parser.add_argument("--profile", default="new-project", help="intake profile passthrough")
    run_parser.add_argument("--decompose-live", action="store_true", help="use live AI decomposition (else fixture)")
    run_parser.add_argument("--live-model", help="model id for generation/research; required")
    run_parser.add_argument("--live-api-key-env", default="XAI_API_KEY", help="env var holding the provider key")
    run_parser.add_argument("--live-provider", default="xai", help="OpenAI-compatible provider")
    run_parser.add_argument("--live-base-url", help="provider base URL override")
    run_parser.add_argument("--workdir", help="override workdir (default mkdtemp)")
    run_parser.add_argument("--keep-workdir", action="store_true", help="retain intermediates even on success")
    run_parser.add_argument("--capability-map", help="use an existing reviewed capability-map.json")
    return parser


def _config_from_args(args: argparse.Namespace) -> RunConfig:
    return RunConfig(
        repo=args.repo,
        output=Path(args.output).expanduser().resolve(),
        profile=args.profile,
        decompose_live=args.decompose_live,
        live_model=args.live_model,
        live_api_key_env=args.live_api_key_env,
        live_provider=args.live_provider,
        live_base_url=args.live_base_url,
        workdir=Path(args.workdir) if args.workdir else None,
        keep_workdir=args.keep_workdir,
        capability_map=Path(args.capability_map) if args.capability_map else None,
    )


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    if args.command == "run":
        try:
            return run(_config_from_args(args))
        except DreamRunError as exc:
            if not exc.already_reported:
                print(f"dream run failed: {exc}", file=sys.stderr)
            return exc.exit_code
    parser.error("unknown command")
    return EXIT_USAGE


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())

```

### `tests/test_capability_lift.py`
```python
from __future__ import annotations

import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from arena.capability_lift import (
    CapabilityLiftError,
    build_capability_map,
    validate_capability_map,
    write_capability_map,
)

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "docs" / "schemas" / "capability-map-v0.schema.json"
GRAPH_HASH = "a" * 64


def _model() -> dict[str, object]:
    return {
        "id": "model-1",
        "project": {"projectId": "fixture-project"},
        "snapshot": {
            "project_id": "fixture-project",
            "graph_hash": GRAPH_HASH,
            "components": [
                {
                    "id": "comp.decomposer",
                    "name": "Project decomposer",
                    "responsibility": "Build Project Model v1 snapshots from repository facts",
                    "owned_node_ids": ["node.decomposer"],
                    "provenance_refs": ["prov:component"],
                    "contract_ids": ["contract.decomposer"],
                    "check_ids": [],
                    "verification_gap_ids": ["gap.semantic"],
                }
            ],
            "contracts": [],
            "verification_gaps": [],
            "near_neighbor_alternatives": [],
        },
        "projectGraph": {
            "graphHash": GRAPH_HASH,
            "nodes": [
                {"id": "node.decomposer", "kind": "module", "label": "arena.decomposer", "path": "arena/decomposer.py"}
            ],
            "edges": [],
        },
        "iterationReadiness": {
            "componentProfiles": [
                {
                    "componentId": "comp.decomposer",
                    "ownedNodeIds": ["node.decomposer"],
                    "responsibilitySummary": "repository decomposition",
                    "behavioralTags": ["decompose", "gate"],
                    "provenanceRefs": ["prov:profile"],
                }
            ]
        },
    }


def _write_model(tmp_path: Path) -> Path:
    path = tmp_path / "project-model-v1.json"
    path.write_text(json.dumps(_model()), encoding="utf-8")
    return path


def test_capability_lift_emits_schema_valid_review_false_map(tmp_path: Path) -> None:
    model_path = _write_model(tmp_path)
    output = write_capability_map(model_path, tmp_path / "capability-map.json")
    payload = json.loads(output.read_text(encoding="utf-8"))

    assert payload["schemaVersion"] == "capability-map/v0"
    assert payload["review"]["reviewed"] is False
    assert payload["capabilities"][0]["realizedByComponentIds"] == ["comp.decomposer"]
    assert payload["capabilities"][0]["supportingNodeIds"] == ["node.decomposer"]

    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    errors = sorted(Draft202012Validator(schema).iter_errors(payload), key=lambda error: list(error.path))
    assert errors == []


def test_capability_lift_fails_closed_for_bad_component_ref(tmp_path: Path) -> None:
    model = _model()
    document = build_capability_map(_write_model(tmp_path))
    document["capabilities"][0]["realizedByComponentIds"] = ["comp.fabricated"]

    with pytest.raises(CapabilityLiftError, match="unknown component"):
        validate_capability_map(document, model)  # type: ignore[arg-type]


def test_capability_lift_fails_closed_for_bad_node_ref(tmp_path: Path) -> None:
    model = _model()
    document = build_capability_map(_write_model(tmp_path))
    document["capabilities"][0]["supportingNodeIds"] = ["node.fabricated"]

    with pytest.raises(CapabilityLiftError, match="unknown graph node"):
        validate_capability_map(document, model)  # type: ignore[arg-type]

```

### `tests/test_dream_generate.py`
```python
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from arena.capability_lift import build_capability_map
from arena.dream_generate import DreamGenerateError, generate_dreams, write_generated_dreams

GRAPH_HASH = "1" * 64


def _model() -> dict[str, Any]:
    return {
        "id": "model-1",
        "project": {"projectId": "fixture-project"},
        "snapshot": {
            "project_id": "fixture-project",
            "graph_hash": GRAPH_HASH,
            "components": [
                {
                    "id": "comp.runner",
                    "name": "Runner",
                    "responsibility": "Run stages",
                    "owned_node_ids": ["node.runner"],
                    "provenance_refs": ["prov:runner"],
                    "contract_ids": [],
                    "check_ids": [],
                    "verification_gap_ids": [],
                }
            ],
            "near_neighbor_alternatives": [{"id": "near.runner", "target_id": "comp.runner", "alternative": "in-process seam"}],
        },
        "projectGraph": {"graphHash": GRAPH_HASH, "nodes": [{"id": "node.runner", "path": "arena/runner.py"}], "edges": []},
        "iterationReadiness": {
            "componentProfiles": [
                {
                    "componentId": "comp.runner",
                    "ownedNodeIds": ["node.runner"],
                    "responsibilitySummary": "stage orchestration",
                    "behavioralTags": ["stage"],
                    "provenanceRefs": ["prov:profile"],
                }
            ]
        },
    }


def _write_inputs(tmp_path: Path, *, reviewed: bool = True) -> tuple[Path, Path, Path, str]:
    model_path = tmp_path / "project-model-v1.json"
    model_path.write_text(json.dumps(_model()), encoding="utf-8")
    cap_map = build_capability_map(model_path)
    cap_map["review"]["reviewed"] = reviewed
    cap_path = tmp_path / "capability-map.json"
    cap_path.write_text(json.dumps(cap_map), encoding="utf-8")
    scorecard = tmp_path / "scorecard.json"
    scorecard.write_text(json.dumps({"findings": [{"id": "verification.gap", "rank": 1}]}), encoding="utf-8")
    return model_path, cap_path, scorecard, cap_map["capabilities"][0]["id"]


def _fake_model(capability_id: str) -> Any:
    def _model_call(prompt: str) -> dict[str, Any]:
        assert "tier-3 dream proposals" in prompt
        return {
            "dreams": [
                {
                    "id": "dream.carrier",
                    "mode": "carrier_swap",
                    "idea": "Consider replacing subprocess glue with an injected stage seam.",
                    "targetCapabilityIds": [capability_id],
                    "citedEvidence": [{"anchorKind": "capability", "anchorId": capability_id, "contentHash": "a" * 64, "claim": "Runner capability exists."}],
                    "rationale": "The carrier swap specifically targets the runner capability.",
                    "conclusionConfidence": {"band": "medium", "value": 0.9},
                    "validationRecipe": {"action": "try the seam", "observable": "test coverage", "expectedDirection": "increase"},
                    "neighborAlternativeId": "near.runner",
                },
                {
                    "id": "dream.function",
                    "mode": "function_remap",
                    "idea": "Consider splitting proposal selection from execution orchestration.",
                    "targetCapabilityIds": [capability_id],
                    "citedEvidence": [{"anchorKind": "capability", "anchorId": capability_id, "contentHash": "b" * 64, "claim": "Runner combines stage orchestration today."}],
                    "rationale": "The remap changes the capability boundary rather than patching one file.",
                    "conclusionConfidence": {"band": "low", "value": 0.3},
                    "validationRecipe": {"action": "try the split", "observable": "orchestration coupling", "expectedDirection": "decrease"},
                },
            ]
        }

    return _model_call


def test_generate_yields_typed_diversity_and_minimum_grounding(tmp_path: Path) -> None:
    model_path, cap_path, scorecard, capability_id = _write_inputs(tmp_path)
    document = generate_dreams(
        project_model_path=model_path,
        capability_map_path=cap_path,
        scorecard_path=scorecard,
        model=_fake_model(capability_id),
    )

    modes = {dream["mode"] for dream in document["dreams"]}
    assert modes == {"carrier_swap", "function_remap"}
    for dream in document["dreams"]:
        assert dream["targetCapabilityIds"] == [capability_id]
        assert dream["citedEvidence"]
        assert dream["validationRecipe"]["action"]
    assert document["dreams"][0]["conclusionConfidence"]["value"] == 0.7  # capped


def test_generate_writes_output_file(tmp_path: Path) -> None:
    model_path, cap_path, scorecard, capability_id = _write_inputs(tmp_path)
    output = write_generated_dreams(
        project_model_path=model_path,
        capability_map_path=cap_path,
        scorecard_path=scorecard,
        output_path=tmp_path / "raw-dreams.json",
        model=_fake_model(capability_id),
    )
    assert json.loads(output.read_text(encoding="utf-8"))["dreams"][0]["id"] == "dream.carrier"


def test_generate_requires_reviewed_capability_map(tmp_path: Path) -> None:
    model_path, cap_path, scorecard, capability_id = _write_inputs(tmp_path, reviewed=False)
    with pytest.raises(DreamGenerateError, match="operator-reviewed"):
        generate_dreams(
            project_model_path=model_path,
            capability_map_path=cap_path,
            scorecard_path=scorecard,
            model=_fake_model(capability_id),
        )


def test_generate_drops_ungrounded_model_items_and_fails_if_none_remain(tmp_path: Path) -> None:
    model_path, cap_path, scorecard, _capability_id = _write_inputs(tmp_path)

    def fake(_prompt: str) -> dict[str, Any]:
        return {"dreams": [{"id": "bad", "mode": "carrier_swap"}]}

    with pytest.raises(DreamGenerateError, match="no dreams"):
        generate_dreams(project_model_path=model_path, capability_map_path=cap_path, scorecard_path=scorecard, model=fake)

```

### `tests/test_dream_research.py`
```python
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from arena.capability_lift import build_capability_map
from arena.dream_research import DreamResearchError, research_dreams, write_researched_dreams

GRAPH_HASH = "2" * 64


def _model() -> dict[str, Any]:
    return {
        "id": "model-1",
        "project": {"projectId": "fixture-project"},
        "snapshot": {
            "project_id": "fixture-project",
            "graph_hash": GRAPH_HASH,
            "components": [
                {
                    "id": "comp.runner",
                    "name": "Runner",
                    "responsibility": "Run stages",
                    "owned_node_ids": ["node.runner"],
                    "provenance_refs": ["prov:runner"],
                    "contract_ids": [],
                    "check_ids": [],
                    "verification_gap_ids": [],
                }
            ],
            "contracts": [],
            "verification_gaps": [],
            "near_neighbor_alternatives": [],
        },
        "projectGraph": {"graphHash": GRAPH_HASH, "nodes": [{"id": "node.runner", "path": "arena/runner.py"}], "edges": []},
        "iterationReadiness": {
            "componentProfiles": [
                {
                    "componentId": "comp.runner",
                    "ownedNodeIds": ["node.runner"],
                    "responsibilitySummary": "stage orchestration",
                    "behavioralTags": ["stage"],
                    "provenanceRefs": ["prov:profile"],
                }
            ]
        },
    }


def _write_inputs(tmp_path: Path, *, reviewed: bool = True) -> tuple[Path, Path, Path, str]:
    model_path = tmp_path / "project-model-v1.json"
    model_path.write_text(json.dumps(_model()), encoding="utf-8")
    cap_map = build_capability_map(model_path)
    cap_map["review"]["reviewed"] = reviewed
    cap_path = tmp_path / "capability-map.json"
    cap_path.write_text(json.dumps(cap_map), encoding="utf-8")
    capability_id = cap_map["capabilities"][0]["id"]
    raw = {
        "dreams": [
            {
                "id": "dream.raw",
                "mode": "function_remap",
                "idea": "Split orchestration roles.",
                "targetCapabilityIds": [capability_id],
                "citedEvidence": [{"anchorKind": "capability", "anchorId": capability_id, "contentHash": "a" * 64, "claim": "Capability exists."}],
                "rationale": "Raw rationale.",
                "conclusionConfidence": {"band": "low", "value": 0.2},
                "validationRecipe": {"action": "try split", "observable": "coupling", "expectedDirection": "decrease"},
            }
        ],
        "provenance": {
            "generatedBy": "arena.dream_generate",
            "researchedBy": "unresearched",
            "promptHashes": {"generate": "3" * 64},
            "modelId": "raw-model",
            "inputHashes": {"scorecard": "4" * 64},
        },
    }
    raw_path = tmp_path / "raw-dreams.json"
    raw_path.write_text(json.dumps(raw), encoding="utf-8")
    return model_path, cap_path, raw_path, capability_id


def _fake_research(capability_id: str) -> Any:
    def _call(prompt: str) -> dict[str, Any]:
        assert "Research these raw tier-3 dream proposals" in prompt
        return {
            "dreams": [
                {
                    "id": "dream.researched",
                    "mode": "function_remap",
                    "idea": "Consider separating selection orchestration from stage execution orchestration.",
                    "targetCapabilityIds": [capability_id],
                    "citedEvidence": [
                        {"anchorKind": "component", "anchorId": "comp.runner", "contentHash": "5" * 64, "claim": "Runner is the current carrier."},
                        {"anchorKind": "capability", "anchorId": capability_id, "contentHash": "6" * 64, "claim": "The capability exists in the reviewed map."},
                    ],
                    "rationale": "The researched claim names the specific carrier and capability boundary being redrawn.",
                    "conclusionConfidence": {"band": "medium", "value": 0.5},
                    "validationRecipe": {"action": "try the split", "observable": "runner coupling", "expectedDirection": "decrease"},
                }
            ]
        }

    return _call


def test_research_rewrites_raw_dream_into_premise_dense_shape(tmp_path: Path) -> None:
    model_path, cap_path, raw_path, capability_id = _write_inputs(tmp_path)
    document = research_dreams(
        project_model_path=model_path,
        capability_map_path=cap_path,
        dreams_path=raw_path,
        model=_fake_research(capability_id),
    )

    dream = document["dreams"][0]
    assert dream["id"] == "dream.researched"
    assert len(dream["citedEvidence"]) == 2
    assert dream["validationRecipe"]["observable"] == "runner coupling"
    assert document["provenance"]["generatedBy"] == "arena.dream_generate"
    assert document["provenance"]["researchedBy"] == "arena.dream_research"


def test_research_writes_output_file(tmp_path: Path) -> None:
    model_path, cap_path, raw_path, capability_id = _write_inputs(tmp_path)
    output = write_researched_dreams(
        project_model_path=model_path,
        capability_map_path=cap_path,
        dreams_path=raw_path,
        output_path=tmp_path / "researched.json",
        model=_fake_research(capability_id),
    )
    assert json.loads(output.read_text(encoding="utf-8"))["dreams"][0]["id"] == "dream.researched"


def test_research_requires_reviewed_capability_map(tmp_path: Path) -> None:
    model_path, cap_path, raw_path, capability_id = _write_inputs(tmp_path, reviewed=False)
    with pytest.raises(DreamResearchError, match="operator-reviewed"):
        research_dreams(
            project_model_path=model_path,
            capability_map_path=cap_path,
            dreams_path=raw_path,
            model=_fake_research(capability_id),
        )


def test_research_fails_if_model_returns_no_researchable_dreams(tmp_path: Path) -> None:
    model_path, cap_path, raw_path, _capability_id = _write_inputs(tmp_path)

    def fake(_prompt: str) -> dict[str, Any]:
        return {"dreams": [{"id": "bad", "mode": "function_remap"}]}

    with pytest.raises(DreamResearchError, match="no dreams"):
        research_dreams(project_model_path=model_path, capability_map_path=cap_path, dreams_path=raw_path, model=fake)

```

### `tests/test_dream_gate.py`
```python
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from arena.capability_lift import build_capability_map
from arena.dream_gate import DreamGateError, anchor_content_hash, gate_dreams, write_gated_dreams

GRAPH_HASH = "b" * 64


def _model() -> dict[str, Any]:
    return {
        "id": "model-1",
        "project": {"projectId": "fixture-project"},
        "snapshot": {
            "project_id": "fixture-project",
            "graph_hash": GRAPH_HASH,
            "components": [
                {
                    "id": "comp.runner",
                    "name": "Runner",
                    "responsibility": "Run proposal stages",
                    "owned_node_ids": ["node.runner"],
                    "provenance_refs": ["prov:runner"],
                    "contract_ids": ["contract.runner"],
                    "check_ids": [],
                    "verification_gap_ids": ["gap.behaviour"],
                }
            ],
            "contracts": [
                {
                    "id": "contract.runner",
                    "name": "stage contract",
                    "from_component_id": "comp.runner",
                    "to_component_id": "comp.runner",
                    "supporting_edge_ids": ["edge.self"],
                    "near_neighbor_alternative_ids": ["near.subprocess"],
                    "provenance_refs": ["prov:contract"],
                }
            ],
            "verification_gaps": [
                {
                    "id": "gap.behaviour",
                    "description": "behaviour gate missing",
                    "severity": "high",
                    "component_ids": ["comp.runner"],
                    "contract_ids": ["contract.runner"],
                    "provenance_refs": ["prov:gap"],
                    "proposed_closure_check": "run tests",
                }
            ],
            "near_neighbor_alternatives": [
                {
                    "id": "near.subprocess",
                    "target_id": "contract.runner",
                    "alternative": "in-process stage seam",
                    "why_not_primary": "subprocess boundary is simpler",
                    "provenance_refs": ["prov:near"],
                }
            ],
        },
        "projectGraph": {
            "graphHash": GRAPH_HASH,
            "nodes": [{"id": "node.runner", "kind": "module", "label": "runner", "path": "arena/runner.py"}],
            "edges": [
                {
                    "id": "edge.self",
                    "kind": "calls",
                    "from_node_id": "node.runner",
                    "to_node_id": "node.runner",
                    "label": "self",
                    "provenance_refs": [],
                    "confidence": "high",
                    "derived_by": "fixture",
                }
            ],
        },
        "iterationReadiness": {
            "componentProfiles": [
                {
                    "componentId": "comp.runner",
                    "ownedNodeIds": ["node.runner"],
                    "responsibilitySummary": "stage orchestration",
                    "behavioralTags": ["orchestrate"],
                    "provenanceRefs": ["prov:profile"],
                }
            ]
        },
    }


def _write_inputs(tmp_path: Path) -> tuple[Path, Path, dict[str, Any], dict[str, Any]]:
    model = _model()
    model_path = tmp_path / "project-model-v1.json"
    model_path.write_text(json.dumps(model), encoding="utf-8")
    cap_map = build_capability_map(model_path)
    cap_map["review"]["reviewed"] = True
    cap_path = tmp_path / "capability-map.json"
    cap_path.write_text(json.dumps(cap_map), encoding="utf-8")
    return model_path, cap_path, model, cap_map


def _dream(model: dict[str, Any], cap_map: dict[str, Any], **overrides: Any) -> dict[str, Any]:
    component = model["snapshot"]["components"][0]
    dream = {
        "id": "dream.runner-carrier",
        "mode": "carrier_swap",
        "idea": "Consider replacing subprocess-only stage wiring with an injected stage seam.",
        "targetCapabilityIds": [cap_map["capabilities"][0]["id"]],
        "citedEvidence": [
            {
                "anchorKind": "component",
                "anchorId": "comp.runner",
                "contentHash": anchor_content_hash(component),
                "claim": "The runner component owns stage orchestration today.",
            }
        ],
        "rationale": "The seam targets the runner capability specifically rather than arbitrary cleanup.",
        "premiseConfidence": "unresolved",
        "conclusionConfidence": {"band": "medium", "value": 0.6},
        "validationRecipe": {
            "action": "try an injected runner seam behind the same CLI",
            "observable": "stage-order test coverage",
            "expectedDirection": "increase",
        },
        "neighborAlternativeId": "near.subprocess",
    }
    dream.update(overrides)
    return dream


def _write_dreams(tmp_path: Path, dreams: list[dict[str, Any]]) -> Path:
    path = tmp_path / "dreams.json"
    path.write_text(json.dumps({"dreams": dreams, "provenance": {"modelId": "fixture"}}), encoding="utf-8")
    return path


def test_grounded_dream_passes_with_all_resolved(tmp_path: Path) -> None:
    model_path, cap_path, model, cap_map = _write_inputs(tmp_path)
    result = gate_dreams(project_model_path=model_path, capability_map_path=cap_path, dreams_path=_write_dreams(tmp_path, [_dream(model, cap_map)]))

    assert result.accepted_count == 1
    assert result.killed_count == 0
    accepted = result.document["dreams"][0]
    assert accepted["premiseConfidence"] == "all_resolved"
    assert accepted["targetCapabilityIds"] == [cap_map["capabilities"][0]["id"]]


def test_planted_fabricated_anchor_is_killed(tmp_path: Path) -> None:
    model_path, cap_path, model, cap_map = _write_inputs(tmp_path)
    fabricated = _dream(model, cap_map)
    fabricated["citedEvidence"][0]["anchorId"] = "comp.fabricated"

    result = gate_dreams(project_model_path=model_path, capability_map_path=cap_path, dreams_path=_write_dreams(tmp_path, [fabricated]))

    assert result.accepted_count == 0
    assert result.trace["killedDreams"][0]["premiseConfidence"] == "unresolved"
    assert "unresolved component comp.fabricated" in result.trace["killedDreams"][0]["reasons"][0]


def test_missing_recipe_is_killed(tmp_path: Path) -> None:
    model_path, cap_path, model, cap_map = _write_inputs(tmp_path)
    bad = _dream(model, cap_map)
    del bad["validationRecipe"]

    result = gate_dreams(project_model_path=model_path, capability_map_path=cap_path, dreams_path=_write_dreams(tmp_path, [bad]))

    assert result.accepted_count == 0
    assert any("validationRecipe" in reason for reason in result.trace["killedDreams"][0]["reasons"])


def test_invalid_mode_is_killed(tmp_path: Path) -> None:
    model_path, cap_path, model, cap_map = _write_inputs(tmp_path)
    bad = _dream(model, cap_map, mode="patch_file")

    result = gate_dreams(project_model_path=model_path, capability_map_path=cap_path, dreams_path=_write_dreams(tmp_path, [bad]))

    assert result.accepted_count == 0
    assert any("mode" in reason for reason in result.trace["killedDreams"][0]["reasons"])


def test_unreviewed_capability_map_fails_closed(tmp_path: Path) -> None:
    model_path, cap_path, model, cap_map = _write_inputs(tmp_path)
    cap_map["review"]["reviewed"] = False
    cap_path.write_text(json.dumps(cap_map), encoding="utf-8")

    with pytest.raises(DreamGateError, match="not operator-reviewed"):
        gate_dreams(project_model_path=model_path, capability_map_path=cap_path, dreams_path=_write_dreams(tmp_path, [_dream(model, cap_map)]))


def test_gate_writes_trace_for_killed_dream(tmp_path: Path) -> None:
    model_path, cap_path, model, cap_map = _write_inputs(tmp_path)
    bad = _dream(model, cap_map)
    bad["citedEvidence"][0]["contentHash"] = "0" * 64
    output = tmp_path / "gated.json"
    trace = tmp_path / "trace.json"

    result = write_gated_dreams(
        project_model_path=model_path,
        capability_map_path=cap_path,
        dreams_path=_write_dreams(tmp_path, [bad]),
        output_path=output,
        trace_path=trace,
    )

    assert result.accepted_count == 0
    assert output.exists()
    assert trace.exists()
    assert "contentHash mismatch" in trace.read_text(encoding="utf-8")

```

### `tests/test_dream_emit.py`
```python
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from arena.dream_emit import DreamEmitError, emit_dream, load_gated_dreams, render_dream_markdown

GRAPH_HASH = "c" * 64
PROMPT_HASH = "d" * 64
CONTENT_HASH = "e" * 64
INPUT_HASH = "f" * 64


def _dream(**overrides: Any) -> dict[str, Any]:
    dream = {
        "id": "dream.test",
        "mode": "carrier_swap",
        "idea": "Consider moving stage execution behind an injected seam.",
        "targetCapabilityIds": ["capability.runner"],
        "citedEvidence": [
            {
                "anchorKind": "component",
                "anchorId": "comp.runner",
                "contentHash": CONTENT_HASH,
                "claim": "The runner component owns stage orchestration.",
            }
        ],
        "rationale": "The idea specifically targets the current runner carrier, not arbitrary cleanup.",
        "premiseConfidence": "all_resolved",
        "conclusionConfidence": {"band": "medium", "value": 0.6},
        "validationRecipe": {
            "action": "try an injected runner seam",
            "observable": "stage-order coverage",
            "expectedDirection": "increase",
        },
        "neighborAlternativeId": "near.runner",
    }
    dream.update(overrides)
    return dream


def _doc(dreams: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "schemaVersion": "dream/v0",
        "projectId": "fixture-project",
        "sourceModel": {"projectModelV1Path": "/tmp/project-model-v1.json", "graphHash": GRAPH_HASH},
        "capabilityMap": {"path": "/tmp/capability-map.json", "reviewed": True},
        "dreams": dreams,
        "provenance": {
            "generatedBy": "arena.dream_generate",
            "researchedBy": "arena.dream_research",
            "promptHashes": {"generate": PROMPT_HASH, "research": "a" * 64},
            "modelId": "fixture-model",
            "inputHashes": {"rawDreams": INPUT_HASH},
        },
    }


def _write(tmp_path: Path, document: dict[str, Any], name: str = "gated-dreams.json") -> Path:
    path = tmp_path / name
    path.write_text(json.dumps(document), encoding="utf-8")
    return path


def test_all_resolved_dream_renders_readable_sections(tmp_path: Path) -> None:
    output = emit_dream(_write(tmp_path, _doc([_dream()])), tmp_path / "dream.md")
    text = output.read_text(encoding="utf-8")

    assert text.startswith("# Dream Proposals")
    assert "Advisory tier-3 hypotheses" in text
    assert "component `comp.runner` — The runner component owns stage orchestration." in text
    assert "Premise confidence (mechanical): `all_resolved`" in text
    assert "Conclusion confidence (speculative/capped): `medium` (0.6)" in text
    assert "To validate, try `try an injected runner seam`; check `stage-order coverage` moves `increase`." in text


def test_byte_identical_repeat(tmp_path: Path) -> None:
    path = _write(tmp_path, _doc([_dream()]))
    first = emit_dream(path, tmp_path / "a.md").read_bytes()
    second = emit_dream(path, tmp_path / "b.md").read_bytes()
    assert first == second


def test_internal_hashes_do_not_leak_into_body(tmp_path: Path) -> None:
    text = emit_dream(_write(tmp_path, _doc([_dream()])), tmp_path / "dream.md").read_text("utf-8")
    body = text.split("---", 1)[0]

    assert CONTENT_HASH not in text
    assert INPUT_HASH not in text
    assert "contentHash" not in text
    assert "inputHashes" not in text
    assert PROMPT_HASH not in body  # prompt hashes are footer-only provenance


def test_partial_dream_never_reaches_dream_md(tmp_path: Path) -> None:
    path = _write(tmp_path, _doc([_dream(premiseConfidence="partial")]))
    output = tmp_path / "dream.md"

    with pytest.raises(DreamEmitError, match="non-all_resolved"):
        emit_dream(path, output)
    assert not output.exists()


def test_no_dreams_fails_closed(tmp_path: Path) -> None:
    path = _write(tmp_path, _doc([]))
    with pytest.raises(DreamEmitError, match="no all_resolved"):
        emit_dream(path, tmp_path / "dream.md")


def test_fail_closed_bad_schema_version(tmp_path: Path) -> None:
    doc = _doc([_dream()])
    doc["schemaVersion"] = "dream/v1"
    with pytest.raises(DreamEmitError, match="schemaVersion"):
        load_gated_dreams(_write(tmp_path, doc))


def test_never_writes_proposal_md(tmp_path: Path) -> None:
    path = _write(tmp_path, _doc([_dream()]))
    proposal = tmp_path / "proposal.md"
    with pytest.raises(DreamEmitError, match="refuses to write proposal.md"):
        emit_dream(path, proposal)
    assert not proposal.exists()


def test_render_orders_neighbor_backed_carrier_swap_first() -> None:
    doc = _doc(
        [
            _dream(id="z-function", mode="function_remap", idea="Function remap", neighborAlternativeId=None),
            _dream(id="a-carrier", idea="Carrier swap with neighbor"),
        ]
    )
    text = render_dream_markdown(doc)
    assert text.index("Carrier swap with neighbor") < text.index("Function remap")

```

### `tests/test_dream_run.py`
```python
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from arena import dream_run
from arena.capability_lift import build_capability_map
from arena.dream_emit import emit_dream
from arena.dream_gate import anchor_content_hash, write_gated_dreams
from arena.dream_run import (
    EXIT_NO_DREAM,
    EXIT_OK,
    EXIT_STAGE_FAILURE,
    EXIT_UNREVIEWED_CAPABILITY_MAP,
    EXIT_USAGE,
    DreamRunError,
    RunConfig,
    StageResult,
    _subprocess_env,
    main,
    run,
)

GRAPH_HASH = "7" * 64


def _argd(args: list[str]) -> dict[str, str]:
    out: dict[str, str] = {}
    i = 0
    while i < len(args):
        token = args[i]
        if token.startswith("--"):
            if i + 1 < len(args) and not args[i + 1].startswith("--"):
                out[token] = args[i + 1]
                i += 2
            else:
                out[token] = "true"
                i += 1
        else:
            i += 1
    return out


def _model() -> dict[str, Any]:
    return {
        "id": "model-1",
        "project": {"projectId": "fixture-project"},
        "snapshot": {
            "project_id": "fixture-project",
            "graph_hash": GRAPH_HASH,
            "components": [
                {
                    "id": "comp.runner",
                    "name": "Runner",
                    "responsibility": "Run dream stages",
                    "owned_node_ids": ["node.runner"],
                    "provenance_refs": ["prov:runner"],
                    "contract_ids": [],
                    "check_ids": [],
                    "verification_gap_ids": [],
                }
            ],
            "contracts": [],
            "verification_gaps": [],
            "near_neighbor_alternatives": [],
        },
        "projectGraph": {"graphHash": GRAPH_HASH, "nodes": [{"id": "node.runner", "path": "arena/dream_run.py"}], "edges": []},
        "iterationReadiness": {
            "componentProfiles": [
                {
                    "componentId": "comp.runner",
                    "ownedNodeIds": ["node.runner"],
                    "responsibilitySummary": "dream stage orchestration",
                    "behavioralTags": ["dream"],
                    "provenanceRefs": ["prov:profile"],
                }
            ],
            "qualityGates": [{"command": "uv run pytest tests -q"}],
        },
    }


class FakeStages:
    SNAPSHOT_ID = "snap-1"

    def __init__(self, *, reviewed: bool = True, gate_mode: str = "ok", fail: set[str] | None = None) -> None:
        self.reviewed = reviewed
        self.gate_mode = gate_mode
        self.fail = fail or set()
        self.calls: list[tuple[str, dict[str, str]]] = []

    def run(self, module: str, args: list[str], _env: dict[str, str]) -> StageResult:
        argd = _argd(args)
        self.calls.append((module, argd))
        if module in self.fail:
            return StageResult(1, stderr=f"{module} forced failure")
        if module == dream_run._DECOMPOSE_MODULE:
            return self._decompose(argd)
        if module == dream_run._INTAKE_MODULE:
            Path(argd["--output"]).write_text(json.dumps({"findings": []}), encoding="utf-8")
            return StageResult(0)
        if module == dream_run._CAPABILITY_MODULE:
            return self._capability(argd)
        if module == dream_run._GENERATE_MODULE:
            return self._dreams(argd, bad=False)
        if module == dream_run._RESEARCH_MODULE:
            return self._dreams(argd, bad=self.gate_mode == "no_survivors")
        if module == dream_run._GATE_MODULE:
            return self._gate(argd)
        if module == dream_run._EMIT_MODULE:
            emit_dream(argd["--dreams"], argd["--output"])
            return StageResult(0)
        raise AssertionError(f"unexpected module {module}")

    def _decompose(self, argd: dict[str, str]) -> StageResult:
        snap_dir = Path(argd["--artifacts-root"]) / self.SNAPSHOT_ID
        snap_dir.mkdir(parents=True, exist_ok=True)
        (snap_dir / "project-model-v1.json").write_text(json.dumps(_model()), encoding="utf-8")
        (snap_dir / "manifest.json").write_text(
            json.dumps({"snapshot_id": self.SNAPSHOT_ID, "project_model_primary_path": "project-model-v1.json"}),
            encoding="utf-8",
        )
        return StageResult(0)

    def _capability(self, argd: dict[str, str]) -> StageResult:
        cap_map = build_capability_map(argd["--project-model"])
        cap_map["review"]["reviewed"] = self.reviewed
        Path(argd["--output"]).write_text(json.dumps(cap_map), encoding="utf-8")
        return StageResult(0)

    def _dreams(self, argd: dict[str, str], *, bad: bool) -> StageResult:
        model = json.loads(Path(argd["--project-model"]).read_text(encoding="utf-8"))
        cap_map = json.loads(Path(argd["--capability-map"]).read_text(encoding="utf-8"))
        component = model["snapshot"]["components"][0]
        capability_id = cap_map["capabilities"][0]["id"]
        anchor_id = "comp.fabricated" if bad else "comp.runner"
        document = {
            "dreams": [
                {
                    "id": "dream.runner",
                    "mode": "carrier_swap",
                    "idea": "Consider an injected dream stage seam.",
                    "targetCapabilityIds": [capability_id],
                    "citedEvidence": [
                        {
                            "anchorKind": "component",
                            "anchorId": anchor_id,
                            "contentHash": anchor_content_hash(component),
                            "claim": "Runner owns dream orchestration.",
                        }
                    ],
                    "rationale": "The dream targets the current orchestration carrier specifically.",
                    "premiseConfidence": "unresolved",
                    "conclusionConfidence": {"band": "medium", "value": 0.5},
                    "validationRecipe": {"action": "try seam", "observable": "stage tests", "expectedDirection": "increase"},
                }
            ],
            "provenance": {"generatedBy": "arena.dream_generate", "researchedBy": "arena.dream_research", "modelId": "fake", "promptHashes": {"fake": "8" * 64}, "inputHashes": {}},
        }
        Path(argd["--output"]).write_text(json.dumps(document), encoding="utf-8")
        return StageResult(0)

    def _gate(self, argd: dict[str, str]) -> StageResult:
        result = write_gated_dreams(
            project_model_path=argd["--project-model"],
            capability_map_path=argd["--capability-map"],
            dreams_path=argd["--dreams"],
            output_path=argd["--output"],
            trace_path=argd["--trace"],
        )
        return StageResult(EXIT_NO_DREAM if result.accepted_count == 0 else 0)


def _fake_git(_record: list[list[str]]) -> dream_run.GitRunner:
    def _git(args: list[str]) -> None:
        _record.append(args)
        if args and args[0] == "clone":
            Path(args[-1]).mkdir(parents=True, exist_ok=True)

    return _git


def _config(repo: Path, output: Path, **overrides: Any) -> RunConfig:
    values: dict[str, Any] = {"repo": str(repo), "output": output, "live_model": "grok-test"}
    values.update(overrides)
    return RunConfig(**values)


@pytest.fixture
def repo_dir(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    return repo


@pytest.fixture(autouse=True)
def _key_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("XAI_API_KEY", "test-key")


def test_happy_path_writes_dream_and_cleans_temp_workdir(tmp_path: Path, repo_dir: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    temp_workdir = tmp_path / "temp-wd"

    def _mkdtemp(*_a: Any, **_k: Any) -> str:
        temp_workdir.mkdir()
        return str(temp_workdir)

    monkeypatch.setattr(dream_run.tempfile, "mkdtemp", _mkdtemp)
    output = tmp_path / "out" / "dream.md"
    stages = FakeStages()

    rc = run(_config(repo_dir, output), stage_runner=stages.run, git_runner=_fake_git([]))

    assert rc == EXIT_OK
    assert output.is_file()
    assert "Consider an injected dream stage seam" in output.read_text(encoding="utf-8")
    assert not temp_workdir.exists()


def test_stage_order_and_manifest_driven_v1_resolution(tmp_path: Path, repo_dir: Path) -> None:
    workdir = tmp_path / "wd"
    stages = FakeStages()
    rc = run(_config(repo_dir, tmp_path / "dream.md", workdir=workdir), stage_runner=stages.run, git_runner=_fake_git([]))

    assert rc == EXIT_OK
    assert [module for module, _args in stages.calls] == [
        dream_run._DECOMPOSE_MODULE,
        dream_run._INTAKE_MODULE,
        dream_run._CAPABILITY_MODULE,
        dream_run._GENERATE_MODULE,
        dream_run._RESEARCH_MODULE,
        dream_run._GATE_MODULE,
        dream_run._EMIT_MODULE,
    ]
    expected_v1 = workdir / "snap" / FakeStages.SNAPSHOT_ID / "project-model-v1.json"
    assert Path(stages.calls[1][1]["--snapshot"]) == expected_v1
    assert Path(stages.calls[2][1]["--project-model"]) == expected_v1
    assert Path(stages.calls[3][1]["--project-model"]) == expected_v1


def test_fail_closed_on_stage_failure_preserves_workdir(tmp_path: Path, repo_dir: Path) -> None:
    workdir = tmp_path / "wd"
    output = tmp_path / "dream.md"
    stages = FakeStages(fail={dream_run._RESEARCH_MODULE})
    with pytest.raises(DreamRunError) as excinfo:
        run(_config(repo_dir, output, workdir=workdir), stage_runner=stages.run, git_runner=_fake_git([]))

    assert excinfo.value.exit_code == EXIT_STAGE_FAILURE
    assert workdir.exists()
    assert not output.exists()
    assert dream_run._GATE_MODULE not in [module for module, _args in stages.calls]


def test_unreviewed_capability_map_exits_four_and_skips_later_stages(tmp_path: Path, repo_dir: Path) -> None:
    stages = FakeStages(reviewed=False)
    with pytest.raises(DreamRunError) as excinfo:
        run(_config(repo_dir, tmp_path / "dream.md", workdir=tmp_path / "wd"), stage_runner=stages.run, git_runner=_fake_git([]))

    assert excinfo.value.exit_code == EXIT_UNREVIEWED_CAPABILITY_MAP
    modules = [module for module, _args in stages.calls]
    assert dream_run._CAPABILITY_MODULE in modules
    assert dream_run._GENERATE_MODULE not in modules


def test_no_dream_survived_gate_exits_two(tmp_path: Path, repo_dir: Path, capsys: pytest.CaptureFixture[str]) -> None:
    stages = FakeStages(gate_mode="no_survivors")
    output = tmp_path / "dream.md"
    with pytest.raises(DreamRunError) as excinfo:
        run(_config(repo_dir, output, workdir=tmp_path / "wd"), stage_runner=stages.run, git_runner=_fake_git([]))

    assert excinfo.value.exit_code == EXIT_NO_DREAM
    assert excinfo.value.already_reported is True
    assert "No dream survived" in capsys.readouterr().out
    assert not output.exists()
    assert dream_run._EMIT_MODULE not in [module for module, _args in stages.calls]


def test_preflight_requires_live_model(tmp_path: Path, repo_dir: Path) -> None:
    stages = FakeStages()
    with pytest.raises(DreamRunError) as excinfo:
        run(_config(repo_dir, tmp_path / "dream.md", live_model=None), stage_runner=stages.run, git_runner=_fake_git([]))

    assert excinfo.value.exit_code == EXIT_USAGE
    assert stages.calls == []


def test_preflight_missing_key_is_usage_error(tmp_path: Path, repo_dir: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    def _raise(_env: str) -> Any:
        raise ValueError("missing key")

    monkeypatch.setattr(dream_run, "resolve_api_key_with_source", _raise)
    stages = FakeStages()
    with pytest.raises(DreamRunError) as excinfo:
        run(_config(repo_dir, tmp_path / "dream.md"), stage_runner=stages.run, git_runner=_fake_git([]))

    assert excinfo.value.exit_code == EXIT_USAGE
    assert stages.calls == []


def test_subprocess_env_threads_live_model_settings() -> None:
    env = _subprocess_env(
        RunConfig(
            repo="/tmp/repo",
            output=Path("/tmp/dream.md"),
            live_model="grok-x",
            live_base_url="https://api.example/v1",
            live_api_key_env="MY_KEY",
        )
    )
    assert env["BUILD_ARENA_LLM_MODEL"] == "grok-x"
    assert env["BUILD_ARENA_LLM_BASE_URL"] == "https://api.example/v1"
    assert env["BUILD_ARENA_LLM_API_KEY_ENV"] == "MY_KEY"
    assert str(dream_run._REPO_ROOT) in env["PYTHONPATH"]


def test_main_maps_errors(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    def _fake_run(_config: RunConfig, **_kw: Any) -> int:
        raise DreamRunError("boom", EXIT_STAGE_FAILURE)

    monkeypatch.setattr(dream_run, "run", _fake_run)
    rc = main(["run", "/repo", "--live-model", "m"])
    assert rc == EXIT_STAGE_FAILURE
    assert "boom" in capsys.readouterr().err

```

### `docs/specs/2026-06-23-dream-proposer-tier3-spec.md`
```markdown
# Dream Proposer (Tier 3) — Design Record

Date: 2026-06-23
Status: implemented locally in this checkout; offline acceptance added.

## Goal

Add a tier-3 divergent proposer lane that emits advisory architectural hypotheses as `dream.md`. The lane is for improvements that do not fit the single-file deterministic proposal contract: carrier swaps, capability remaps, redrawn boundaries, and added capabilities. It never applies a patch, never promotes a branch, and never writes `proposal.md`.

The working artifact is a `dream.md` produced from a gated `dream/v0` document. Each rendered dream must carry:

- cited current-state evidence;
- mechanically separated premise confidence;
- capped speculative conclusion confidence;
- a concrete validation recipe for a downstream repo agent.

## Architecture decision

The dream proposer is a parallel track, not a `ProposalDomainRegistry` member.

Reasons:

1. `arena/proposal_domains.py` is explicitly offline and file-patch-centric.
2. `ProposalCandidateDraft` requires a target path and verification commands for a concrete patch candidate; a dream has no single-file target.
3. The existing proposal path ranks actionable patch candidates. A divergent architectural hypothesis would pollute that ranking and launder speculation as deterministic work.

The dream lane shares inputs with the proposal pipeline — Project Model v1 and intake scorecard — and adds a reviewed capability map. It then runs:

```text
Project Model v1 + intake scorecard
  -> arena.capability_lift        -> capability-map/v0 (review.reviewed false)
  -> operator review gate          -> review.reviewed true required
  -> arena.dream_generate          -> raw dreams (live / injected in tests)
  -> arena.dream_research          -> premise-dense dreams (live / injected in tests)
  -> arena.dream_gate              -> gated dream/v0 (deterministic kill gate)
  -> arena.dream_emit              -> dream.md (deterministic advisory renderer)
```

`arena.dream_run` is the thin orchestrator for the lane.

## Contracts

### `capability-map/v0`

File: `docs/schemas/capability-map-v0.schema.json`

An advisory, operator-reviewed function/capability overlay over Project Model v1. It is a separate artifact, not a Project Model v1 field, because capability inference is interpretive and may be edited by the operator. Every capability cites real Project Model component ids and optional graph node ids.

Load-bearing invariant:

- every `capabilities[].realizedByComponentIds[]` resolves to `snapshot.components[].id`;
- every `capabilities[].supportingNodeIds[]` resolves to `projectGraph.nodes[].id`;
- `review.reviewed` defaults to `false`.

### `dream/v0`

File: `docs/schemas/dream-v0.schema.json`

A gated advisory hypothesis artifact. Schema-level constraints keep the lane honest:

- `mode` is one of `carrier_swap` or `function_remap`;
- every dream has target capabilities, cited evidence, rationale, separated confidences, and a validation recipe;
- `conclusionConfidence.band` is only `low` or `medium`;
- `conclusionConfidence.value` is capped at `0.7`;
- rendered artifacts require `premiseConfidence == all_resolved`.

## Stage summaries

### `arena.capability_lift`

Deterministic v0 lift from `snapshot.components[]` and `iterationReadiness.componentProfiles[]`. It emits schema-valid `capability-map/v0`, self-validates references, and marks the map unreviewed.

CLI:

```bash
uv run python -m arena.capability_lift --project-model project-model-v1.json --output capability-map.json
```

### `arena.dream_generate`

Typed single-shot generation. The production path requires `--live-model`; tests use an injected model callable. It drops candidates missing the minimum grounding surface: mode, target capability id, cited evidence, and validation recipe.

### `arena.dream_research`

LLM-driven change-impact/research pass. It rewrites raw dreams into premise-dense hypotheses by adding concrete cited anchors. It does not certify benefit; that remains speculative and capped.

### `arena.dream_gate`

Deterministic kill gate. It resolves each `citedEvidence` anchor against the real Project Model v1 / capability map and verifies `contentHash` consistency using canonical JSON SHA-256 of the resolved anchor object. It also verifies target capability ids, mode, conclusion-confidence bounds, and recipe presence.

Accepted dreams are emitted with `premiseConfidence: all_resolved`. Unresolved, partial, malformed, or fabricated-premise dreams are killed and recorded in the gate trace.

### `arena.dream_emit`

Deterministic markdown renderer. It validates `dream/v0`, refuses any non-`all_resolved` dream, renders readable evidence lines, shows premise and conclusion confidence separately, includes the validation recipe, and writes `dream.md` only. It refuses to write `proposal.md`.

### `arena.dream_run`

Thin fail-closed orchestrator. It runs stages through injectable subprocess seams and preserves the workdir on failure. Exit codes:

- `0`: success, `dream.md` written;
- `1`: stage failure;
- `2`: no dream survived the premise gate;
- `3`: usage/preflight error;
- `4`: capability map not reviewed.

A first real run normally stops at exit `4` after writing `capability-map.json`; the operator reviews/edits that file and reruns with `--capability-map <reviewed-map>`.

## Acceptance tests

Implemented offline tests:

- `tests/test_capability_lift.py`
- `tests/test_dream_generate.py`
- `tests/test_dream_research.py`
- `tests/test_dream_gate.py`
- `tests/test_dream_emit.py`
- `tests/test_dream_run.py`

Required safety assertions covered:

1. capability references resolve and bad refs fail closed;
2. generation keeps typed diversity and minimum grounding;
3. research preserves a checkable premise surface;
4. grounded dreams pass and planted fabricated anchors are killed;
5. missing recipe / invalid mode are killed;
6. emit is byte-identical for fixed input;
7. partial/unresolved dreams never reach `dream.md`;
8. `dream_emit` never writes `proposal.md`;
9. `dream_run` enforces stage order, manifest-driven Project Model v1 resolution, preflight, unreviewed-map exit `4`, no-dream exit `2`, and workdir preservation.

## Known boundaries

- Live generation/research are not byte-reproducible. The deterministic boundary is the gated `dream/v0` artifact.
- The gate verifies premise resolution, not usefulness or buildability.
- Elenchus alignment, loop-back re-research, population/QD generation, reference-architecture retrieval, dashboards, promotion, and repo-agent execution are out of scope for v0.
- The current implementation remains advisory. A real live `dream_run` with operator-reviewed capability map is still operator-gated because it spends model calls.

```

### `docs/agent-wiki/2026-06-23-dream-proposer-failure-modes.md`
```markdown
# Dream Proposer Failure Modes — 2026-06-23

## Why this page exists

The dream proposer is allowed to invent advisory architecture hypotheses, so its failure mode is not merely bad code. The dangerous failure is laundering speculation as grounded deterministic work. Future agents must preserve the lane boundary and the kill gate.

## New lane rules

1. `dream.md` is advisory only. It never authorizes mutation, promotion, or a patch.
2. `dream_emit` must not write `proposal.md`. A dream is not a proposal candidate.
3. `capability-map/v0` is operator-reviewed intent. `review.reviewed: true` is required before generation/research/gate can produce an emitted dream.
4. `dream_gate` is the trust boundary. It kills dreams whose cited anchors, target capabilities, content hashes, mode, or validation recipe do not resolve.
5. `conclusionConfidence` is soft and capped. It is not a pre-emission proof of benefit.

## Failure modes to remember

### F-MAEI: means displacing ends

Problem: the team optimizes dream-generation volume or prettiness instead of proving emitted dreams lead to downstream successful attempts.

Guard: the external license for this lane is emitted -> attempted by repo agent -> tests/build/metric verdict. Until a structured ledger exists, record live dream ids and downstream attempt outcomes in this wiki or a versioned report. If acceptance-rate is zero or untracked, the dreamer is noise.

### F-neuter: safe but non-novel output

Problem: anti-fabrication pressure collapses tier 3 into another grounded proposer that only says what already exists.

Guard: keep the novelty-floor test. The generator path must be able to produce at least one `function_remap` dream that describes a boundary/capability change rather than a single-file patch.

### F-drift: wrong capability map becomes truth

Problem: the capability lift guesses intent incorrectly, and every dream optimizes that wrong map.

Guard: the capability map is never truth until operator review. The gate checks coherence given the reviewed map; it does not retire the review gate and does not prove the map is semantically right.

### F-false: confident nonsense from fabricated premises

Problem: a dream cites an anchor that does not exist or whose content changed.

Guard: maintain the planted-fabrication test. A fabricated `citedEvidence.anchorId` must be killed by `dream_gate`, with no `dream.md` written by the orchestrator for that survivor set.

### F-invalid: real premises, bad conclusion

Problem: every anchor resolves, but the conclusion is still wrong or not worth doing.

Guard: do not promote conclusion confidence above `medium` / `0.7`; require a validation recipe and let the downstream repo agent/test reality judge benefit.

## Gate recipe

Focused local verification for this lane:

```bash
uv run pytest tests/test_capability_lift.py tests/test_dream_generate.py tests/test_dream_research.py tests/test_dream_gate.py tests/test_dream_emit.py tests/test_dream_run.py -q
uv run ruff check arena/capability_lift.py arena/dream_generate.py arena/dream_research.py arena/dream_gate.py arena/dream_emit.py arena/dream_run.py tests/test_capability_lift.py tests/test_dream_generate.py tests/test_dream_research.py tests/test_dream_gate.py tests/test_dream_emit.py tests/test_dream_run.py
uv run pyright arena/capability_lift.py arena/dream_generate.py arena/dream_research.py arena/dream_gate.py arena/dream_emit.py arena/dream_run.py tests/test_capability_lift.py tests/test_dream_generate.py tests/test_dream_research.py tests/test_dream_gate.py tests/test_dream_emit.py tests/test_dream_run.py
```

Whole-repo gates remain `uv run pytest tests -q`, `uv run ruff check .`, `uv run pyright`, and `make generated`, but this checkout may contain unrelated dirty files from other work. Do not attribute unrelated failures to the dream lane without isolating them.

```

### `docs/status/2026-06-23-dream-proposer-tier3-implementation-status.md`
```markdown
# Dream Proposer Tier 3 Implementation Status — 2026-06-23

Status: local implementation complete; offline suite/lint/type/generated checks green. Independent review pending in this working session.

## Scope implemented

New contracts:

- `docs/schemas/capability-map-v0.schema.json`
- `docs/schemas/dream-v0.schema.json`

New modules:

- `arena/capability_lift.py`
- `arena/dream_generate.py`
- `arena/dream_research.py`
- `arena/dream_gate.py`
- `arena/dream_emit.py`
- `arena/dream_run.py`

New tests:

- `tests/test_capability_lift.py`
- `tests/test_dream_generate.py`
- `tests/test_dream_research.py`
- `tests/test_dream_gate.py`
- `tests/test_dream_emit.py`
- `tests/test_dream_run.py`

Docs:

- `docs/specs/2026-06-23-dream-proposer-tier3-spec.md`
- `docs/agent-wiki/2026-06-23-dream-proposer-failure-modes.md`
- README section: Advisory dream proposer lane

## Verification so far

Focused suite:

```text
uv run pytest tests/test_capability_lift.py tests/test_dream_generate.py tests/test_dream_research.py tests/test_dream_gate.py tests/test_dream_emit.py tests/test_dream_run.py -q
..................................                                       [100%]
```

Focused lint/type:

```text
uv run ruff check arena/capability_lift.py arena/dream_generate.py arena/dream_research.py arena/dream_gate.py arena/dream_emit.py arena/dream_run.py tests/test_capability_lift.py tests/test_dream_generate.py tests/test_dream_research.py tests/test_dream_gate.py tests/test_dream_emit.py tests/test_dream_run.py
All checks passed!

uv run pyright arena/capability_lift.py arena/dream_generate.py arena/dream_research.py arena/dream_gate.py arena/dream_emit.py arena/dream_run.py tests/test_capability_lift.py tests/test_dream_generate.py tests/test_dream_research.py tests/test_dream_gate.py tests/test_dream_emit.py tests/test_dream_run.py
0 errors, 0 warnings, 0 informations
```

Whole-repo checks:

```text
uv run pytest tests -q
........................................................................ [ 13%]
........................................................................ [ 26%]
..........................................................sssssssssss... [ 39%]
........................................................................ [ 52%]
........................................................................ [ 65%]
........................................................................ [ 78%]
........................................................................ [ 91%]
................................................                         [100%]

uv run ruff check .
All checks passed!

uv run pyright
0 errors, 0 warnings, 0 informations

make generated
mkdir -p arena/generated dashboard/src/lib/generated
uv run gen-pydantic schema/arena.yaml > arena/generated/models.py
uv run gen-json-schema schema/arena.yaml > arena/generated/schema.json
uv run gen-typescript schema/arena.yaml > dashboard/src/lib/generated/arena.d.ts
uv run gen-sqlddl schema/arena.yaml > arena/generated/ddl.sql
uv run python scripts/normalize_generated_artifacts.py
```

## Important checkout note

This implementation was done in the live checkout at `fe90dc0...`, which is behind `origin/main` and already had unrelated modified/untracked files. At implementation start, the exact design-grounding path `docs/specs/2026-06-21-proposal-run-and-emit.md` was absent from this checkout, although `origin/main` contains it. The dream lane was implemented without modifying or importing `arena/proposal_run.py`, `arena/proposal_emit.py`, or the frozen proposal stage modules.

## Remaining verification

- One independent review pass, then patch valid criticism.

```
