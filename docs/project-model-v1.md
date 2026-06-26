# Project Model v1 Reference

Project Model v1 is the active shared project-model contract emitted by the AI-first decomposer as `project-model-v1.json`.

Schema: `docs/schemas/project-model-v1.schema.json`
Example: `docs/examples/project-model-v1-tiny.json`
Producer: `arena.project_model_cli snapshot` via `arena/project_decomposer_ai.py` and `arena/project_model_v1.py`

## Producer contract

Run an offline fixture snapshot:

```bash
uv run python -m arena.project_model_cli snapshot \
  --project /path/to/project \
  --artifacts-root /tmp/build-arena-snapshot \
  --project-id example-project \
  --goal "Decompose the project from git/filesystem truth" \
  --llm-mode fixture
```

The snapshot directory contains `project-model-v1.json` and a `manifest.json` whose `project_model_primary_path` points at that same v1 artifact. The runtime no longer emits a compatibility projection alongside it.

`fixture`, `recorded`, `live`, and `off` modes all flow through the same v1 builder. Live mode remains operator-gated by `--allow-live` and an explicit model ID.

## Required top-level fields

D4 rule: a top-level field is required iff a core proposal-loop consumer reads it. Advisory experiment-lane reads do not make a field required.

| Field | Required? | Core consumer evidence |
|---|---:|---|
| `schemaVersion` | yes | Contract discriminator checked by schema and contract tests. |
| `id` | yes | `arena/project_intake_scorecard.py` reads it into `snapshotId`. |
| `snapshot` | yes | `arena/project_intake_scorecard.py` reads `snapshot.components` and `snapshot.verification_gaps`; `arena/proposal_planner.py` forwards those gaps into advisory backlog material. |
| `projectGraph` | yes | `arena/project_intake_scorecard.py` reads `projectGraph.nodes` for node-path evidence. |
| `provenance` | yes | `arena/project_intake_scorecard.py` reads `provenance.git.headOid` into `repoHead`. |
| `iterationReadiness` | yes | `arena/project_intake_scorecard.py` reads component profiles, quality gates, and open questions; `arena/proposal_planner.py` forwards open questions; `arena/proposal_domains.py` and `arena/proposer_handoff.py` special-case readiness evidence paths. |
| `project` | no | Core consumers use CLI/project arguments or fallback data; advisory capability and experiment code can fall back to `snapshot.project_id`. |
| `gateReport` | no | No core proposal-loop consumer reads it directly; it remains useful metadata and is still emitted by the current producer. |
| `hashes` | no | No core proposal-loop consumer reads it directly; freshness and artifact checks use manifest/snapshot paths. |
| `models` | no | No core proposal-loop consumer reads it directly; it remains emitted metadata for auditability. |
| `derivedArtifacts` | no | No core proposal-loop consumer reads it directly; it remains emitted metadata for future projections. |

Advisory-only reads stay optional. Examples: `arena/capability_lift.py` and `arena/dream_generate.py` read `iterationReadiness.componentProfiles`, while `arena/dream_generate.py` also reads `snapshot.near_neighbor_alternatives`; these reads do not expand the required top-level set beyond the core-consumer evidence above.

## `iterationReadiness`

`iterationReadiness` is required and must include these subfields:

- `summary`
- `componentProfiles`
- `runtimeContracts`
- `externalSurfaces`
- `productInvariants`
- `qualityGates`
- `priorityBacklog`
- `openQuestions`

The `off`/noop path must still emit a present, schema-valid block. Empty arrays are valid where the schema allows arrays, but the block itself and its required subfields cannot be omitted.

## Validation

Validate an artifact against the schema:

```bash
uv run python - <<'PY'
import json
from pathlib import Path
from jsonschema import Draft202012Validator
schema = json.loads(Path('docs/schemas/project-model-v1.schema.json').read_text())
model = json.loads(Path('docs/examples/project-model-v1-tiny.json').read_text())
errors = sorted(Draft202012Validator(schema).iter_errors(model), key=lambda e: list(e.path))
raise SystemExit(1 if errors else 0)
PY
```

A model missing `iterationReadiness` must fail schema validation. `tests/test_project_model_v1_contract.py` contains both the positive example validation and the negative required-field test.
