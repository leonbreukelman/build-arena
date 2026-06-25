# Dream Proposer functional run, review, and calibration map — 2026-06-24

Status: A1 plumbing run passed. A2 live product proof not run; blocked on operator decisions.
Baseline target: `build-arena` `main` at `2c6f6cb64ad987b772ccb684d4a67cb0d6987793`.
Scope: run-and-map only. No dream-lane source edits.

## Verdict

A1 produced a real rendered `dream.md` through the dream lane with no source change. It did not use the `dream_run` orchestrator; A1 was hand-assembled by an allowed throwaway driver because the public generation/research CLIs do not expose their injected fake-model seams.

- Rendered markdown: `docs/verification/dream-proposer-functional-run-a1/dream.md`
- Gated `dream/v0` artifact: `docs/verification/dream-proposer-functional-run-a1/gated-dreams.json`
- Gate trace: `docs/verification/dream-proposer-functional-run-a1/dream-gate-trace.json`
- Flow diagram: `docs/verification/2026-06-24-dream-proposer-functional-run-flow.mmd`

A1 is a plumbing proof, not a live product proof. It used the injected fake model seam exposed by `dream_generate` / `dream_research`; the public CLIs for those two stages do not expose that seam. The throwaway driver therefore invoked those module functions directly and invoked the deterministic stages as CLIs.

A2 requires two operator gates and is intentionally stopped:

1. live credentials/spend approval;
2. real operator review of `capability-map.json` before generation/research.

## Evidence ledger

### Repository baseline

Command run before A1 writes:

```text
$ git status --short && git rev-parse HEAD && git branch --show-current && git remote -v
2c6f6cb64ad987b772ccb684d4a67cb0d6987793
main
origin	<repo-remote> (fetch)
origin	<repo-remote> (push)
```

`git status --short` emitted no changed-file line before the SHA, so the working tree was clean at run start.

### A1 command ledger

The A1 throwaway driver and JSON ledger live under `<run-dir>` and are ephemeral. The durable evidence is this embedded transcript plus the committed A1 `dream.md`, `gated-dreams.json`, and gate trace.

The A1 throwaway driver was executed with:

```text
$ PYTHONPATH=. uv run python <run-driver>
{
  "acceptedDreamIds": [
    "dream.a1.carrier-survives"
  ],
  "dreamMarkdown": "<repo>/docs/verification/dream-proposer-functional-run-a1/dream.md",
  "gateTrace": "<repo>/docs/verification/dream-proposer-functional-run-a1/dream-gate-trace.json",
  "gateTraceSummary": {
    "accepted": 1,
    "killed": 1
  },
  "gatedDreams": "<repo>/docs/verification/dream-proposer-functional-run-a1/gated-dreams.json",
  "killedDreams": [
    {
      "id": "dream.a1.function-killed",
      "premiseConfidence": "unresolved",
      "reasons": [
        "citedEvidence[0] contentHash mismatch for component component.arena-runners"
      ]
    }
  ],
  "ledger": "<run-dir>/a1-run-ledger.json",
  "runRoot": "<run-dir>"
}
```

Raw per-stage ledger from `<run-dir>/a1-run-ledger.json`:

```text
project_model_cli snapshot
command: uv run python -m arena.project_model_cli snapshot --project <repo> --artifacts-root <run-dir>/snapshots --project-id build-arena --goal Dream proposer A1 fake-model functional run --llm-mode fixture --overwrite
returncode: 0
stdout: {"gate_report_path": "<run-dir>/snapshots/snapshot-63a959a94c1c8068/gate-report.json", "manifest_path": "<run-dir>/snapshots/snapshot-63a959a94c1c8068/manifest.json", "passed": true, "snapshot_dir": "<run-dir>/snapshots/snapshot-63a959a94c1c8068", "snapshot_id": "snapshot-63a959a94c1c8068", "violation_count": 0}
stderr:

project_intake_scorecard
command: uv run python -m arena.project_intake_scorecard --project <repo> --snapshot <run-dir>/snapshots/snapshot-63a959a94c1c8068/project-model-v1.json --profile active-development --output <run-dir>/scorecard.json
returncode: 0
stdout:
stderr:

capability_lift
command: uv run python -m arena.capability_lift --project-model <run-dir>/snapshots/snapshot-63a959a94c1c8068/project-model-v1.json --output <run-dir>/capability-map.generated.json
returncode: 0
stdout: <run-dir>/capability-map.generated.json
stderr:

capability-map review stand-in edit
command: python driver: set review.reviewed true in <run-dir>/capability-map.review-standin.json
returncode: 0
stdout: <run-dir>/capability-map.review-standin.json
stderr:

dream_generate injected fake model seam
command: python driver: arena.dream_generate.write_generated_dreams(..., model=fake_generate)
returncode: 0
stdout: <run-dir>/raw-dreams.json
stderr:

dream_research injected fake model seam
command: python driver: arena.dream_research.write_researched_dreams(..., model=fake_research)
returncode: 0
stdout: <run-dir>/researched-dreams.json
stderr:

dream_gate
command: uv run python -m arena.dream_gate --project-model <run-dir>/snapshots/snapshot-63a959a94c1c8068/project-model-v1.json --capability-map <run-dir>/capability-map.review-standin.json --dreams <run-dir>/researched-dreams.json --output <run-dir>/gated-dreams.json --trace <run-dir>/dream-gate-trace.json
returncode: 0
stdout: <run-dir>/gated-dreams.json
stderr:

dream_emit
command: uv run python -m arena.dream_emit --dreams <repo>/docs/verification/dream-proposer-functional-run-a1/gated-dreams.json --output <repo>/docs/verification/dream-proposer-functional-run-a1/dream.md
returncode: 0
stdout: <repo>/docs/verification/dream-proposer-functional-run-a1/dream.md
stderr:
```

Snapshot/scorecard/capability summary:

```text
$ uv run python - <<'PY'
import json
from pathlib import Path
model=Path('<run-dir>/snapshots/snapshot-63a959a94c1c8068/project-model-v1.json')
p=json.loads(model.read_text())
print({'schemaVersion': p.get('schemaVersion'), 'id': p.get('id'), 'components': len(p.get('snapshot', {}).get('components', [])), 'nodes': len(p.get('projectGraph', {}).get('nodes', [])), 'graphHash': p.get('projectGraph', {}).get('graphHash')})
PY
{'schemaVersion': 'project-model/v1', 'id': 'snapshot-63a959a94c1c8068', 'components': 13, 'nodes': 5347, 'graphHash': '15308551bebe583886efd75d470a61bdd2e1e1da785ecbd47cc04daf1309f2dc'}

$ uv run python - <<'PY'
import json
from pathlib import Path
scorecard=Path('<run-dir>/scorecard.json')
p=json.loads(scorecard.read_text())
print({'schemaVersion': p.get('schemaVersion'), 'profile': p.get('profile'), 'findings': len(p.get('findings', [])), 'firstFinding': (p.get('findings') or [{}])[0].get('id'), 'scorecard': str(scorecard)})
PY
{'schemaVersion': 'project-intake-scorecard/v0', 'profile': 'active-development', 'findings': 13, 'firstFinding': 'doc.index.missing', 'scorecard': '<run-dir>/scorecard.json'}

$ uv run python - <<'PY'
import json
from pathlib import Path
cap=Path('<run-dir>/capability-map.review-standin.json')
p=json.loads(cap.read_text())
print({'schemaVersion': p.get('schemaVersion'), 'capabilities': len(p.get('capabilities', [])), 'review': p.get('review')})
PY
{'schemaVersion': 'capability-map/v0', 'capabilities': 13, 'review': {'editedFromGenerated': False, 'reviewed': True, 'reviewedAtUtc': '2026-06-25T14:22:10Z', 'reviewedBy': 'A1 fake-model test stand-in; NOT operator review for A2'}}
```

### Gate trace

`docs/verification/dream-proposer-functional-run-a1/dream-gate-trace.json`:

```json
{
  "acceptedDreamIds": [
    "dream.a1.carrier-survives"
  ],
  "killedDreams": [
    {
      "id": "dream.a1.function-killed",
      "premiseConfidence": "unresolved",
      "reasons": [
        "citedEvidence[0] contentHash mismatch for component component.arena-runners"
      ]
    }
  ],
  "schemaVersion": "dream-gate-trace/v0",
  "summary": {
    "accepted": 1,
    "killed": 1
  }
}
```

### Gated dream validation

```text
$ uv run python - <<'PY'
from pathlib import Path
from arena.dream_emit import load_gated_dreams, render_dream_markdown
path = Path('docs/verification/dream-proposer-functional-run-a1/gated-dreams.json')
doc = load_gated_dreams(path)
print({'schemaVersion': doc['schemaVersion'], 'gatedBy': doc['provenance'].get('gatedBy'), 'dream_count': len(doc['dreams']), 'premiseConfidence': [d['premiseConfidence'] for d in doc['dreams']], 'render_starts': render_dream_markdown(doc).splitlines()[0]})
PY
{'schemaVersion': 'dream/v0', 'gatedBy': 'arena.dream_gate', 'dream_count': 1, 'premiseConfidence': ['all_resolved'], 'render_starts': '# Dream Proposals'}
```

`docs/verification/dream-proposer-functional-run-a1/gated-dreams.json` contains:

```json
{
  "schemaVersion": "dream/v0",
  "projectId": "build-arena",
  "provenance": {
    "gatedBy": "arena.dream_gate",
    "generatedBy": "arena.dream_generate",
    "researchedBy": "arena.dream_research",
    "modelId": "injected-model"
  },
  "dreams": [
    {
      "id": "dream.a1.carrier-survives",
      "mode": "carrier_swap",
      "premiseConfidence": "all_resolved",
      "conclusionConfidence": {"band": "medium", "value": 0.6},
      "targetCapabilityIds": ["capability.component.arena"]
    }
  ]
}
```

The committed JSON has the full evidence hashes; the excerpt above trims only non-load-bearing hash detail for readability.

### Rendered `dream.md`

`docs/verification/dream-proposer-functional-run-a1/dream.md` starts:

```text
# Dream Proposals

Advisory tier-3 hypotheses only. These are not deterministic changes and do not authorize mutation.

## 1. Consider replacing the current capability carrier with a narrower dream-lane seam.

- Dream id: `dream.a1.carrier-survives`
- Mode: `carrier_swap`
- Target capabilities: `capability.component.arena`
...
- Premise confidence (mechanical): `all_resolved`
- Conclusion confidence (speculative/capped): `medium` (0.6)
```

## A2 live run stop point

Not run. This is deliberate.

Required before A2:

1. Operator authorizes live model calls/spend and specifies provider/model/env.
2. Operator reviews the generated `capability-map.json` and sets `review.reviewed: true`; the A1 stand-in does not count.

The live run should resume from a genuinely reviewed map, for example:

```text
uv run python -m arena.dream_run run <repo> \
  --output docs/verification/dream-proposer-functional-run-live/dream.md \
  --profile active-development \
  --workdir <live-run-dir> \
  --keep-workdir \
  --capability-map /path/to/operator-reviewed-capability-map.json \
  --live-provider <provider> \
  --live-model <explicit-model> \
  --live-api-key-env <ENV_WITH_KEY>
```

## Code review as encountered

Scope: six dream modules only, run-correctness and contract fidelity against `docs/specs/2026-06-23-dream-proposer-tier3-spec.md`.

| Module | As-encountered review | Evidence |
|---|---|---|
| `arena.capability_lift` | Matches v0 contract for deterministic lift and fail-closed references. It generated a schema-valid map, defaulted `review.reviewed` to false, and A1 had to mark a copied map reviewed as a test stand-in. Quality boundary: current granularity is one capability per Project Model component, modulo slug-collision de-duplication; that is a tunable interpretation, not proven semantic capability truth. | Spec says capability refs resolve and review defaults false: `docs/specs/2026-06-23-dream-proposer-tier3-spec.md:43-53`, stage summary `:69-77`. Code loop emits one capability per component: `arena/capability_lift.py:61-92`; de-duplicates slug collisions at `arena/capability_lift.py:219-226`; review default: `arena/capability_lift.py:107-112`. A1 summary: `capabilities: 13`, stand-in review true. |
| `arena.dream_generate` | Function seam works; CLI fake seam does not exist. The module accepts `model: DreamModel | None`, but the CLI only exposes live provider/model flags. A1 therefore used the injected function seam from the throwaway driver. Minimum-grounding filter is real but shallow: it drops missing mode/target/evidence/recipe and rejects unknown target capability ids, but does not validate hashes. | Function signature: `arena/dream_generate.py:33-43`; live-only branch: `arena/dream_generate.py:54-72`; CLI args only live flags: `arena/dream_generate.py:261-270`; grounding filter: `arena/dream_generate.py:131-170`, including target-capability check at `arena/dream_generate.py:149-150`. A1 ledger: `dream_generate injected fake model seam`, returncode 0. |
| `arena.dream_research` | Same seam shape as generate. It can be injected for tests/runs through functions, but not via CLI. It rewrites raw dreams into premise-dense shape, rejects unknown target capability ids, and preserves/caps confidence; it does not certify quality. | Function signature: `arena/dream_research.py:32-42`; live-only branch: `arena/dream_research.py:53-72`; CLI args only live flags: `arena/dream_research.py:280-289`; target-capability check at `arena/dream_research.py:138-139`; prompt requires concrete current-state claims and content hashes: `arena/dream_research.py:189-205`; A1 ledger: `dream_research injected fake model seam`, returncode 0. |
| `arena.dream_gate` | Matches contract and was the load-bearing A1 trust boundary. It accepted the all-resolved carrier dream and killed the planted stale-hash dream. It verifies anchor existence/hash, capability ids, graph hash, recipe, modes, and confidence cap. It still does not judge usefulness or semantic truth of free-text claim, which the spec already declares. | Gate docstring boundary: `arena/dream_gate.py:1-6`; review/graph checks: `arena/dream_gate.py:73-83`; accept/kill branch: `arena/dream_gate.py:91-109`; hash mismatch check: `arena/dream_gate.py:214-220`; recipe/confidence checks: `arena/dream_gate.py:225-248`; trace above accepted 1/killed 1. Spec usefulness boundary: `docs/specs/2026-06-23-dream-proposer-tier3-spec.md:136-141`. |
| `arena.dream_emit` | Matches renderer contract. A1 wrote `dream.md`, required `arena.dream_gate` provenance, required all dreams to be `all_resolved`, and did not write `proposal.md`. Its ordering is deterministic and is itself a presentation-quality surface. | Gate marker: `arena/dream_emit.py:53-60`; all-resolved selection: `arena/dream_emit.py:62-76`; output refusal: `arena/dream_emit.py:95-103`; ranking: `arena/dream_emit.py:106-117`; A1 validation command above. |
| `arena.dream_run` | Thin live orchestrator is contract-aligned for A2, but not usable for A1 no-spend fake generation as a public CLI. It preflights `--live-model` and an API key before any stage, then enforces `review.reviewed` before generation. This means a strict no-credential A1 cannot use `dream_run run` directly; A1 needed the allowed throwaway driver. If CLI-only fake A1 is required later, the minimum source addition is an explicit fixture/model-output flag or offline stage seam in `dream_run`, not a change to the gate. | Stage order constants: `arena/dream_run.py:31-38`; preflight requires model/key: `arena/dream_run.py:130-138` and is called before stages at `arena/dream_run.py:342-343`; review gate: `arena/dream_run.py:208-219`; stage execution order: `arena/dream_run.py:231-339`; CLI flags: `arena/dream_run.py:369-379`. Spec says first real run normally stops at exit 4 after capability map review gate: `docs/specs/2026-06-23-dream-proposer-tier3-spec.md:101-111`. |

## Calibration map

Type legend:

- `Q`: quality-control surface. Changes what dreams are likely to be worth reading.
- `F`: fabrication-control surface. Kills false/ungrounded output; does not make weak ideas good.
- `OP`: operator gate / run-control surface.

| Surface | Location | Controls | Current value / A1 value | Type | How to adjust |
|---|---|---|---|---|---|
| Target repository | `arena/dream_run.py:369`, `resolve_target` at `arena/dream_run.py:106-114`; manual A1 driver `--project` args | Which repo supplies Project Model, scorecard, capability map, and evidence anchors. | A1 target: `<repo>`. | OP/Q | Pass a different repo path/git URL to `dream_run run` or to `project_model_cli snapshot --project`. |
| Project Model decomposition mode | `arena/project_model_cli.py:23-40`; `arena/dream_run.py:178-198` | Fixture vs recorded/live semantic decomposition; changes source model richness and spend. | A1: `--llm-mode fixture`. `dream_run` default: fixture unless `--decompose-live`. | Q/OP | Use `project_model_cli snapshot --llm-mode live --allow-live --live-model ...` or `dream_run --decompose-live --live-model ...` after spend approval. |
| Project Model goal/source context | `arena/project_model_cli.py:23-31`; `arena/dream_run.py:178-191` | Goal text included in snapshot construction. | A1: `--goal Dream proposer A1 fake-model functional run`; `dream_run` hardcodes `build-arena dream run`. | Q | Manual staged run: pass `--goal` / `--source-task`. In `dream_run`, edit `_decompose_args`. |
| Intake profile | `arena/project_intake_scorecard.py:24-65`; `arena/dream_run.py:56`, `:239-242`, `:371` | Weighting of scorecard findings included in generation prompt. | A1: `active-development`; `dream_run` default: `new-project`. | Q | Pass `--profile active-development|production|documentation-first|new-project`. |
| Scorecard top-finding count | `arena/dream_generate.py:184-191` | How many ranked findings are shown to the generator. | Current: first 8 findings: `scorecard.get("findings", [])[:8]`. | Q | Edit the slice in `_generation_prompt`; no CLI flag. |
| Capability granularity | `arena/capability_lift.py:61-92` | The capability map's unit of abstraction and target space. | Current: one capability per `snapshot.components[]`; A1 produced 13 capabilities. | Q | Operator-edit `capabilities[]` before review, or edit `build_capability_map` to merge/split components differently. |
| Capability lift prompt | `arena/capability_lift.py:26-30`, prompt hash at `:113-117` | Provenance/instruction for carrier-agnostic capability inference. Current deterministic lift only records the prompt; it does not call a model. | `Infer a carrier-agnostic capability map... operator-reviewed before use.` | Q | Edit `PROMPT`; rerun `capability_lift`; review changed map. |
| Capability lift model id/provenance | `arena/capability_lift.py:23-25`, CLI `:237-242` | Provenance label in generated map; not actual live model behavior in current deterministic lift. | Default: `deterministic-capability-lift-v0`. | OP | Pass `--model-id` to `arena.capability_lift`. |
| Capability map content | Schema `docs/schemas/capability-map-v0.schema.json:21-48`; generated by `arena/capability_lift.py:82-91` | Capability names, current carriers, supporting nodes, behavioral tags, provenance refs, component ids. This is a primary quality steering surface. | A1: generated map copied and marked reviewed without semantic edit as stand-in only. | Q/OP | Operator edits `capability-map.json`, then sets review fields. |
| Capability map review gate | Schema `docs/schemas/capability-map-v0.schema.json:49-59`; checks in `dream_generate.py:50-51`, `dream_research.py:49-50`, `dream_gate.py:73-74`, `dream_run.py:208-219` | Whether generation/research/gate may proceed. | Generated default false; A1 stand-in true; A2 must be real operator-reviewed true. | OP/F | Edit `review.reviewed` to true only after operator review; set reviewer metadata. |
| Generation prompt | `arena/dream_generate.py:184-198` | Candidate framing, expected fields, grounding instruction, and mode diversity pressure. | Current prompt asks for JSON dreams and at least one `carrier_swap` and `function_remap` when possible. | Q | Edit `_generation_prompt`; no external prompt file/flag. |
| Generation mode mix | `arena/dream_generate.py:193-196`; schema `docs/schemas/dream-v0.schema.json:39-42`; gate `arena/dream_gate.py:27`, `:178-180` | Encourages or restricts `carrier_swap` vs `function_remap`. | Prompt-only encouragement for both; hard allowed modes are exactly those two. | Q/F | For soft mix, edit prompt. For allowed set, edit schema + `ALLOWED_MODES` + tests. |
| Dream count | `arena/dream_generate.py:184-198`, live client at `:64`; no explicit count symbol/flag | How many raw candidates are requested/accepted. | No explicit count knob. Count is model-determined, prompt/token-budget constrained. A1 fake generated 2, gate emitted 1. | Q | Currently adjust prompt text or `max_tokens`; minimum missing runtime knob if count must be controlled. |
| Generation minimum-grounding filter | `arena/dream_generate.py:131-170` | Drops raw model items missing mode, target capability, citedEvidence, validationRecipe, idea/rationale/action. | Current: shallow structure filter; does not validate hashes. | F | Edit `_minimum_grounded_dreams` if the pre-gate filter should be stricter/looser. |
| Generation model/provider/key | `arena/dream_generate.py:39-43`, `:54-72`, CLI `:267-270`; provider resolver `arena/llm_adapter.py:50-127` | Which live model creates raw dreams and where credentials come from. | Live default provider `xai`, key env `XAI_API_KEY`; `--live-model` required for live path. A1 used injected model, no spend. | Q/OP | Pass `--live-provider`, `--live-base-url`, `--live-api-key-env`, `--live-model`; or set supported envs. |
| Generation temperature/token budget | `arena/dream_generate.py:63-64` | Diversity/randomness and response length for live generation. | `temperature=0.7`, `max_tokens=4096`. | Q | Edit `OpenAICompatibleChatClient(... temperature=0.7, max_tokens=4096)`; no CLI flag. |
| Research prompt | `arena/dream_research.py:189-205` | How raw dreams become premise-dense, including content-hash instruction and novelty preservation. | Current: asks for concrete current-state claims, no benefit certainty, canonical JSON SHA-256. | Q/F | Edit `_research_prompt`; no external prompt file/flag. |
| Research evidence payload depth | `arena/dream_research.py:190-199` | Which model fields the research pass sees: capabilities, components, contracts, verification gaps, near-neighbor alternatives, graph nodes/edges, raw dreams. | Current includes full listed fields. | Q | Edit `compact` payload in `_research_prompt`; no CLI flag. |
| Research model/provider/key | `arena/dream_research.py:38-42`, `:53-72`, CLI `:286-289` | Which live model researches and hashes premises. | Live default provider `xai`, key env `XAI_API_KEY`; `--live-model` required. A1 used injected model. | Q/OP | Pass live flags or edit defaults/resolver. |
| Research temperature/token budget | `arena/dream_research.py:62-63` | Determinism and response length for research pass. | `temperature=0.2`, `max_tokens=4096`. | Q | Edit `OpenAICompatibleChatClient(... temperature=0.2, max_tokens=4096)`; no CLI flag. |
| Allowed evidence anchor kinds | `arena/dream_gate.py:28-36`; schema `docs/schemas/dream-v0.schema.json:48-60` | Which current-state objects can ground a dream. | graphNode, graphEdge, component, contract, capability, verificationGap, nearNeighborAlternative. | F | Edit `ANCHOR_KINDS` and schema enum together, then tests. |
| Target capability resolution | `arena/dream_gate.py:85-87`, `:188-193`; schema `docs/schemas/dream-v0.schema.json:44-47` | Ensures target capabilities exist in reviewed capability map. | Required; unknown target kills dream. | F | Edit gate/schema only if changing contract. |
| `all_resolved` premise requirement | `arena/dream_gate.py:95-109`, `:258-265`; emit `arena/dream_emit.py:62-76`; schema `docs/schemas/dream-v0.schema.json:65-68` | Only fully resolved premises survive and render. | A1 accepted 1 all_resolved and killed 1 unresolved. | F | Edit gate acceptance branch or emit selector. Weakening this would lower safety. |
| `contentHash` checks | `arena/dream_gate.py:53-57`, `:214-220`; schema `docs/schemas/dream-v0.schema.json:52-57` | Detects stale/fabricated anchors. | A1 killed `dream.a1.function-killed` on contentHash mismatch. | F | Edit `anchor_content_hash` canonicalization or hash check. |
| Capability map graphHash check | `arena/dream_gate.py:75-83`; spec `docs/specs/2026-06-23-dream-proposer-tier3-spec.md:87-93` | Prevents using a map from a different Project Model graph. | Required when source map has graphHash. | F | Edit gate check; weakening is unsafe. |
| Validation recipe requirement | `arena/dream_gate.py:225-237`; schema `docs/schemas/dream-v0.schema.json:77-85` | Forces downstream repo-agent validation instructions. | Requires action + observable; expectedDirection in decrease/increase/unchanged/tests_pass. | F/Q | Edit schema/gate enum or prompt wording. It improves actionability only by filtering, not by making ideas good. |
| Conclusion confidence cap | `arena/dream_generate.py:173-181`, `arena/dream_research.py:208-216`, `arena/dream_gate.py:239-248`; schema `docs/schemas/dream-v0.schema.json:69-75` | Prevents pre-validation high-confidence claims. | Bands low/medium only; numeric max 0.7. | F | Edit schema + generator/research coercion + gate. Weakening raises laundering risk. |
| Gate provenance marker | `arena/dream_gate.py:307-339`; emit check `arena/dream_emit.py:53-60` | Prevents emit from trusting model-authored `premiseConfidence`. | Gate stamps `gatedBy: arena.dream_gate` and prompt hash; emit requires it. | F | Edit provenance or emit requirement. Weakening is unsafe. |
| Emit ordering | `arena/dream_emit.py:106-117`; schema neighbor field `docs/schemas/dream-v0.schema.json:86` | Presentation order: neighbor-backed carrier swaps first, then other carrier swaps, then function remaps; more evidence/targets earlier. | Current deterministic sort. A1 only one survivor. | Q | Edit `_rank_key`; no CLI flag. |
| Emit destination / proposal separation | `arena/dream_emit.py:95-103`, CLI `:183-186` | Where `dream.md` is written and blocks `proposal.md`. | A1 output: `docs/verification/dream-proposer-functional-run-a1/dream.md`; `proposal.md` refused. | OP/F | Pass `--output`; do not use `proposal.md`. |
| Orchestrator live preflight | `arena/dream_run.py:130-138`, called at `:342-343` | Requires live model and key before all stages. | Current: no live model/key means exit 3 before capability map. | OP | Pass `--live-model` and key env; source change needed for no-spend `dream_run` fake/offline CLI. |
| Orchestrator workdir retention | `arena/dream_run.py:62-64`, `:344-362`, CLI `:377-379` | Whether intermediates are retained and whether an existing reviewed map is reused. | Defaults temp cleanup on success; preserves on failure; A1 manual run used `/tmp` and committed final output copies. | OP | Pass `--workdir`, `--keep-workdir`, `--capability-map`. |

## Independent review

Fable preflight did not produce an available reviewer; Opus was used as fallback.

```text
$ preflight fable || preflight opus
UNKNOWN:fable
{"type":"result","subtype":"success","is_error":true,..."result":"Claude Fable 5 is currently unavailable. Learn more: https://www.anthropic.com/news/fable-mythos-access",...}
OK:opus
```

Opus review command completed successfully (`subtype=success`, `is_error=false`, `num_turns=14`, `total_cost_usd=1.28086`) and returned `verdict: ACCEPT` with no required changes. Valid nice-to-have corrections were patched into this document: explicit `dream_run` bypass disclosure, ephemeral `/tmp` driver/ledger disclosure, target-capability checks in generate/research, and capability slug de-duplication.

Reviewer summary excerpt:

```text
The deliverable satisfies the run-and-map scope with no dream-lane source edits ... A1 is honestly framed throughout as a plumbing proof ... A2 is correctly stopped on the two operator gates ... The calibration map covers all named surfaces ... No blocking corrections needed.
```

## Final verification

Repository verification after the review patch and handoff file addition:

```text
$ make test && make lint && make typecheck && make generated
uv run pytest tests -q
........................................................................ [ 10%]
........................................................................ [ 21%]
........................................................................ [ 32%]
................sssssssssss............................................. [ 43%]
........................................................................ [ 53%]
........................................................................ [ 64%]
........................................................................ [ 75%]
........................................................................ [ 86%]
........................................................................ [ 97%]
...................                                                      [100%]
uv run ruff check .
All checks passed!
uv run pyright
0 errors, 0 warnings, 0 informations
WARNING: there is a new pyright version available (v1.1.409 -> v1.1.411).
Please install the new version or set PYRIGHT_PYTHON_FORCE_VERSION to `latest`

mkdir -p arena/generated dashboard/src/lib/generated
uv run gen-pydantic schema/arena.yaml > arena/generated/models.py
uv run gen-json-schema schema/arena.yaml > arena/generated/schema.json
uv run gen-typescript schema/arena.yaml > dashboard/src/lib/generated/arena.d.ts
uv run gen-sqlddl schema/arena.yaml > arena/generated/ddl.sql
uv run python scripts/normalize_generated_artifacts.py
```

```text
$ git diff --check
<no output; exit 0>

$ git status --short
?? docs/specs/2026-06-24-dream-proposer-functional-run-handoff.md
?? docs/verification/2026-06-24-dream-proposer-functional-run-flow.mmd
?? docs/verification/2026-06-24-dream-proposer-functional-run.md
?? docs/verification/dream-proposer-functional-run-a1/

$ git ls-files --others --exclude-standard
docs/specs/2026-06-24-dream-proposer-functional-run-handoff.md
docs/verification/2026-06-24-dream-proposer-functional-run-flow.mmd
docs/verification/2026-06-24-dream-proposer-functional-run.md
docs/verification/dream-proposer-functional-run-a1/dream-gate-trace.json
docs/verification/dream-proposer-functional-run-a1/dream.md
docs/verification/dream-proposer-functional-run-a1/gated-dreams.json
```

Dream artifact verification after final doc writes:

```text
$ uv run python - <<'PY'
from pathlib import Path
from arena.dream_emit import load_gated_dreams, render_dream_markdown
path=Path('docs/verification/dream-proposer-functional-run-a1/gated-dreams.json')
doc=load_gated_dreams(path)
trace=Path('docs/verification/dream-proposer-functional-run-a1/dream-gate-trace.json').read_text(encoding='utf-8')
md=Path('docs/verification/dream-proposer-functional-run-a1/dream.md').read_text(encoding='utf-8')
print({'schemaVersion': doc['schemaVersion'], 'gatedBy': doc['provenance'].get('gatedBy'), 'dream_count': len(doc['dreams']), 'premises': [d['premiseConfidence'] for d in doc['dreams']], 'render_starts': render_dream_markdown(doc).splitlines()[0], 'dream_md_exists': md.startswith('# Dream Proposals'), 'trace_has_kill': 'contentHash mismatch' in trace})
PY
{'schemaVersion': 'dream/v0', 'gatedBy': 'arena.dream_gate', 'dream_count': 1, 'premises': ['all_resolved'], 'render_starts': '# Dream Proposals', 'dream_md_exists': True, 'trace_has_kill': True}
```

## Sufficiency verdict for calibration

No — the current surfaces are enough to make the lane run and to manually steer it, but not enough for disciplined output-quality refinement from live runs.

Evidence:

- The real quality surfaces are mostly prompt/code edits and operator capability-map edits: generation prompt (`arena/dream_generate.py:184-198`), research prompt (`arena/dream_research.py:189-205`), capability map (`docs/schemas/capability-map-v0.schema.json:21-48`), model/temperature (`arena/dream_generate.py:63-64`, `arena/dream_research.py:62-63`), intake profile (`arena/dream_run.py:371`).
- The hard deterministic surfaces are fabrication filters, not quality judges: gate docstring says it does not judge usefulness (`arena/dream_gate.py:1-6`); spec says the gate verifies premise resolution, not usefulness/buildability (`docs/specs/2026-06-23-dream-proposer-tier3-spec.md:136-141`).
- The repo-local wiki names the missing quality feedback loop: emitted dream -> attempted by repo agent -> tests/build/metric verdict; until a structured ledger exists, acceptance rate is untracked noise (`docs/agent-wiki/2026-06-23-dream-proposer-failure-modes.md:18-23`).
- A1 proves the point mechanically: the surviving dream is all-resolved and rendered, but the output itself is intentionally suboptimal fake text. Gate success says the premises resolved; it says nothing about whether the dream is worth attempting.

Single minimum missing piece: a structured dream outcome/quality ledger for live runs: record each emitted dream id, prompt/config/model/capability-map lineage, operator/downstream attempt verdict, validation recipe result, and reason for accept/reject. That one piece turns existing prompt/model/capability-map knobs into calibratable surfaces. Without it, changing prompts or temperatures is just manual taste-testing while the fabrication gate only changes survival rate.

Do not implement that in this task; it is the next product decision.
