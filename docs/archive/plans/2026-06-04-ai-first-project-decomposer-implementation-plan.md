# AI-first Project Decomposer — TDD Implementation Plan

Date: 2026-06-04
Status: phase-gated implementation plan after codeless spec + Opus review
Spec: `docs/specs/2026-06-04-ai-first-project-decomposer-spec.md`
Spec review: `docs/verification/2026-06-04-ai-first-project-decomposer-spec-opus-review.md`

## 1. Direct outcome

Build the AI-first project decomposer as sidecar-first infrastructure beside the existing deterministic Project Model v0 compatibility path.

The implementation must produce, from git/filesystem truth each run:

1. `ProjectGraph` JSON.
2. Provenance-backed Markdown encyclopedia/wiki pages.
3. Recursive decomposition JSON with components, contracts, concerns, checks, near-neighbor alternatives, held-out probes, planted negatives, and verification gaps.
4. `ProjectModelSnapshot` manifest.
5. Deterministic `GateReport`.
6. Project Model v0 compatibility JSON.
7. CLI and Python API.

The implementation must not run a Build Arena autonomous cycle from current Project Model v0 output and must not modify `scorer/`, `verifier/`, `schema/`, `.arena/scorer.lock.toml`, or `arena/generated/`.

## 2. Non-negotiable implementation posture

- TDD first: each phase starts with failing tests and ends with green targeted tests.
- Sidecars first: do not rewrite the LinkML schema and do not break existing Project Model v0 tests.
- Rebuild from disk/git truth every run: cached sidecars are never authoritative unless their input hashes match.
- LLM claims are advisory: CI tests and local acceptance use deterministic fixture/no-live adapters, but delivery acceptance must include at least one recorded real leading-model decomposition artifact (live Grok/leading model or a captured real-model output fixture) that exercises the same model-output ingestion path.
- Live Grok/Opus may be used for pilot-quality artifacts and reviews, but no acceptance test may require live paid APIs.
- If live credentials/auth are unavailable during implementation, the delivery must use a frozen real-model output fixture captured from an authorized prior run and clearly label the live path as blocked for this session. A purely deterministic synthesizer is not sufficient for final acceptance.
- No owner homework: implement default schema mechanics, gate predicates, probe mechanics, dirty-tree heuristics, and pilot repo selection.

## 3. Files to add

Implementation source:

- `arena/project_graph.py`
  - Pydantic contracts for `ProjectGraph`, `GraphNode`, `GraphEdge`, `ProvenanceRef`, graph inventory, graph build metadata, and graph validation helpers.
  - Deterministic graph builder from git/filesystem truth.
  - Python AST extraction for modules/classes/functions/imports.
  - Markdown heading/link extraction and config/test discovery.
  - Protected/generated/oracle/runtime surface classification.

- `arena/project_encyclopedia.py`
  - Pydantic `EncyclopediaPage` and manifest contracts.
  - Deterministic Markdown page writer with provenance citations.
  - No generated wiki claim may be accepted unless it cites graph/source provenance.

- `arena/project_snapshot.py`
  - Pydantic contracts for `Component`, `Contract`, `CrossCuttingConcern`, `ObservableCheck`, `HeldOutProbe`, `VerificationGap`, `NearNeighborAlternative`, `ProjectModelSnapshot`, `GateReport`, and gate findings.
  - Hash/canonical JSON utilities.
  - Snapshot directory writer/reader.

- `arena/project_decomposer_ai.py`
  - High-level Python API: `build_project_model_snapshot(...)`.
  - Deterministic orchestration around graph/wiki/model-output evidence, not a competing deterministic semantic decomposer.
  - In fixture/off mode, consume hand-authored good/bad decomposition fixtures that mimic real LLM output; do not hardcode a project-specific deterministic decomposer to make tests pass.
  - In live/recorded mode, ingest real model output through the same normalizer/gate path.
  - Project Model v0 compatibility projection.

- `arena/project_model_gate.py`
  - Deterministic gate predicates:
    - inventory coverage;
    - provenance completeness;
    - transitive deterministic source provenance;
    - component measurability;
    - contract references;
    - near-neighbor alternatives;
    - conditional/universal cross-cutting concerns;
    - held-out probe presence/isolation/discrimination;
    - verification gap integrity;
    - protected-surface policy;
    - no-live-paid-API acceptance allowlist;
    - snapshot freshness;
    - output hash integrity;
    - vague component rejection;
    - cached projection authority.

- `arena/project_model_cli.py`
  - CLI wrapper for AI-first sidecar pipeline.
  - Main command planned as `uv run python -m arena.project_model_cli snapshot --project <repo> --artifacts-root <dir> [--project-id <id>] [--goal <text>] [--non-goal <text> ...] [--source-task <text>] [--primary-backlog-item <text>] [--llm-mode fixture|recorded|live|off] [--model-output <json>] [--overwrite]`.
  - Secondary command `uv run python -m arena.project_model_cli gate --snapshot <manifest.json>`.
  - Secondary command `uv run python -m arena.project_model_cli graph --project <repo> --output <graph.json>`.

- `arena/project_model_llm.py`
  - LLM adapter interface, prompt hashing, model/output metadata, fixture adapter.
  - Live Grok/leading-model support only behind explicit `llm_mode="live"`; tests use fixture/off.

Tests:

- `tests/test_project_graph.py`
- `tests/test_project_encyclopedia.py`
- `tests/test_project_snapshot_gate.py`
- `tests/test_project_decomposer_ai.py`
- `tests/test_project_model_cli_ai.py`

Test fixtures:

- `tests/fixtures/project_model/good_decomposition.json`
  - hand-authored, graph-grounded, responsibility-bearing decomposition.
- `tests/fixtures/project_model/fluent_file_bucket_decomposition.json`
  - hand-authored negative control with polished non-vague component names but sibling-file bucket ownership and shallow provenance.
- `tests/fixtures/project_model/real_llm_decomposition_output.json`
  - captured real leading-model output from an authorized run; exercises real model-output ingestion path without live CI spend. If this cannot be captured, delivery records a blocker instead of substituting deterministic output.
- `tests/fixtures/project_model/independent_planted_negative.json`
  - hand-authored decoy not generated by the probe builder.
- `tests/fixtures/project_model/golden_probe_control.json`
  - known-good decomposition used to assert probes do not false-positive.

Verification support:

- `docs/verification/2026-06-04-ai-first-project-decomposer-final-report.md` written during final phase.
- Pilot output directories already specified by the user.

## 4. Files to modify

- `arena/decomposer.py`
  - Preserve current CLI default and Project Model v0 behavior.
  - Optionally add a compatibility function that delegates to new sidecar API only when explicitly requested.
  - Do not change existing `--format scanner-v0.1` or `--format project-model-v0` semantics.

- `arena/project_model_v0.py`
  - Prefer no changes unless projection needs a tiny compatibility helper.
  - If changed, only strengthen quality-gate behavior without weakening existing contract tests.

- `arena/__init__.py`
  - Optional exports for new API.

- `tests/test_project_decomposer.py`
  - Keep current tests passing.
  - Add at most compatibility assertions if existing CLI gains an explicit new mode.

Do not modify:

- `scorer/`
- `verifier/`
- `schema/`
- `.arena/scorer.lock.toml`
- `arena/generated/`

## 5. Artifact layout and CLI behavior

Default snapshot output:

```text
<artifacts-root>/<snapshot_id>/
  manifest.json
  graph.json
  encyclopedia/
    manifest.json
    overview.md
    components/*.md
    concerns/*.md
    checks.md
    gaps.md
  decomposition.json
  near-neighbor-alternatives.json
  held-out-probes.json
  planted-negatives.json
  acceptance-command-allowlist.json
  gate-report.json
  project-model-v0.json
  prompts/
    index-builder-prompt.txt
    encyclopedia-writer-prompt.txt
    decomposer-prompt.txt
    skeptic-reviewer-prompt.txt
    held-out-probe-builder-prompt.txt
  model-outputs/
    decomposer.raw.json
    skeptic-review.raw.json
    probe-builder.raw.json
```

CLI examples:

```bash
uv run python -m arena.project_model_cli snapshot \
  --project /home/leonb/projects/build-arena \
  --artifacts-root docs/verification/2026-06-04-ai-first-project-decomposer-pilot-build-arena \
  --project-id build-arena \
  --source-task "AI-first project decomposition pilot" \
  --primary-backlog-item "local-pilot" \
  --goal "decompose this repository into responsibility-bearing components that can safely drive Build Arena" \
  --non-goal "do not treat file buckets as final components" \
  --non-goal "do not target protected/generated/oracle surfaces for arena hypotheses" \
  --llm-mode fixture \
  --overwrite

uv run python -m arena.project_model_cli gate \
  --snapshot docs/verification/2026-06-04-ai-first-project-decomposer-pilot-build-arena/<snapshot_id>/manifest.json
```

Exit codes:

- `0`: snapshot written and gate passed.
- `1`: gate failed but diagnostic artifacts were written.
- `2`: CLI/input error.
- `3`: live LLM requested but auth/model unavailable or not allowed.

Stdout:

- `snapshot` prints a compact JSON object with `snapshot_id`, `manifest_path`, `gate_report_path`, `passed`, and `status`.
- `gate` prints compact JSON with `snapshot_id`, `passed`, finding counts, and gate report path.

## 6. Phase-gated TDD plan

### Phase A — ProjectGraph contract and truth inventory

Failing tests first in `tests/test_project_graph.py`:

1. `test_graph_rebuilds_from_git_toplevel_and_records_dirty_state`.
2. `test_graph_hashes_raw_disk_bytes_and_never_trusts_cache`.
3. `test_graph_discovers_python_symbols_imports_tests_docs_configs`.
4. `test_graph_tags_protected_generated_oracle_runtime_surfaces`.
5. `test_graph_provenance_refs_have_derivation_confidence_hashes_and_paths`.

Implementation:

- Add `arena/project_graph.py` models.
- Slice-1 produced node kinds are: `file`, `python_module`, `python_class`, `python_function`, `python_import`, `markdown_section`, `config`, `test_file`, `protected_surface`, `generated_surface`, `runtime_surface`, `verification_artifact`.
- Slice-1 produced edge kinds are: `contains`, `imports`, `defined_in`, `tests`, `documents`, `configures`, `protects`, `generated_from`, `excluded_as`, `verification_artifact_of`.
- Other spec vocabulary remains reserved until a production rule and gate test are added.
- Use `git rev-parse --show-toplevel`, `git ls-files -z`, `git status --porcelain=v1`, `git ls-files --others --exclude-standard -z`.
- Fall back to filesystem scan if not in a git repo.
- Parse Python with `ast`:
  - file nodes;
  - module nodes;
  - class/function nodes;
  - import edges;
  - test edges by import/call-name heuristics.
- Parse Markdown headings and links.
- Parse `pyproject.toml`, `pytest.ini`, `tox.ini`, `uv.lock`, `requirements.txt`, YAML/JSON/TOML configs as config nodes.
- Emit deterministic canonical JSON.

Targeted command:

```bash
uv run pytest tests/test_project_graph.py -q
```

Rollback point:

- If this phase fails badly, remove `arena/project_graph.py` and `tests/test_project_graph.py`; no downstream files should depend on it yet.

### Phase B — Encyclopedia pages with provenance-backed Markdown

Failing tests first in `tests/test_project_encyclopedia.py`:

1. `test_encyclopedia_writes_manifest_and_source_linked_pages`.
2. `test_encyclopedia_claims_reference_graph_provenance`.
3. `test_encyclopedia_excludes_prior_verification_outputs_from_source_truth`.
4. `test_encyclopedia_redacts_secret_shaped_content`.

Implementation:

- Add deterministic writer in `arena/project_encyclopedia.py`.
- Pages are generated from graph nodes/edges only.
- Include `ProvenanceRef` citations inline as stable IDs and path/line/hash summaries.
- Redact credential-shaped strings as `[REDACTED]`.

Targeted command:

```bash
uv run pytest tests/test_project_encyclopedia.py -q
```

Rollback point:

- Delete encyclopedia module/tests if necessary; graph remains independent.

### Phase C — Snapshot contract and deterministic gate

Failing tests first in `tests/test_project_snapshot_gate.py`:

1. `test_gate_passes_minimal_well_grounded_snapshot`.
2. `test_gate_fails_missing_transitive_source_provenance`.
3. `test_gate_fails_vague_or_file_bucket_components`.
4. `test_gate_fails_fluent_non_vague_sibling_file_bucket_decomposition`.
5. `test_gate_fails_contract_endpoint_and_supporting_edge_errors`.
6. `test_gate_requires_universal_and_triggered_conditional_concerns`.
7. `test_gate_requires_goal_non_goals_and_near_neighbor_anchors`.
8. `test_gate_requires_held_out_probe_isolation_independence_and_planted_negative_discrimination`.
9. `test_gate_probe_false_positive_control_allows_known_good_decomposition`.
10. `test_gate_fails_cross_snapshot_probe_leakage`.
11. `test_gate_fails_llm_only_high_impact_edges_without_gap`.
12. `test_gate_fails_live_paid_api_acceptance_checks_not_allowlisted`.
13. `test_gate_fails_stale_snapshot_hashes_and_dirty_head_only_provenance`.
14. `test_gate_fails_protected_surface_policy_violations`.
15. `test_canonical_snapshot_artifacts_are_byte_reproducible_for_same_inputs`.

Implementation:

- Add `arena/project_snapshot.py` models.
- Add `arena/project_model_gate.py` deterministic gates.
- Gate never calls LLM/API.
- Gate accepts structural/semantic predicates it can prove locally; unconstrained semantic risks become `VerificationGap`.
- Concrete file-bucket predicate: a component fails when its owned nodes are predominantly sibling files under one directory, it has no deterministic symbol/config/test/contract-supporting graph edges, and its checks are project-wide rather than component-specific, even if its name is polished and non-vague.
- LLM-only high-impact edges: `calls`, `references`, `depends_on`, and contract-supporting edges with only LLM provenance fail unless converted into `VerificationGap`.
- Probe discrimination requires an independently authored decoy plus a known-good false-positive control for high-risk probes.
- Goal/non-goals are required on snapshots, and near-neighbor `why_not_primary` must cite them.

Targeted command:

```bash
uv run pytest tests/test_project_snapshot_gate.py -q
```

Rollback point:

- Remove snapshot/gate modules/tests; graph/wiki remain intact.

### Phase D1 — Decomposer API: model-output ingestion, skeptic stage, snapshot/v0 write

Failing tests first in `tests/test_project_decomposer_ai.py`:

1. `test_build_project_model_snapshot_writes_core_sidecars`.
2. `test_snapshot_project_model_v0_projection_remains_compatible`.
3. `test_decomposer_rebuilds_from_filesystem_truth_each_run`.
4. `test_decomposer_records_prompt_model_output_hashes_in_fixture_mode`.
5. `test_recorded_real_model_output_uses_same_ingestion_path_as_live_output`.
6. `test_llm_claims_are_advisory_until_gate_passes`.
7. `test_ambiguous_leaf_becomes_verification_gap_not_success`.
8. `test_fluent_file_bucket_model_output_is_rejected`.
9. `test_python_project_decomposition_uses_symbols_imports_contracts_not_only_paths`.
10. `test_prior_probe_artifacts_are_excluded_from_primary_context`.
11. `test_skeptic_findings_are_classified_and_valid_findings_create_repair_snapshot_hash_chain`.
12. `test_two_adjacent_skeptic_repair_failures_become_gap_or_blocker`.

Implementation:

- Add `arena/project_model_llm.py` adapter seam:
  - `FixtureProjectModelLLM` loads hand-authored good/bad decomposition fixtures instead of synthesizing a fake semantic decomposition.
  - `RecordedProjectModelLLM` loads captured real leading-model output and exercises the same output normalizer as live mode.
  - `NoopProjectModelLLM` returns no advisories and forces gaps for unsupported semantic claims.
  - `LiveProjectModelLLM` seam exists and is exercised manually in pilots when auth is available; CI does not require live spend.
- Add `arena/project_decomposer_ai.py` orchestration:
  - build graph;
  - build encyclopedia;
  - resolve goal/non-goals;
  - run fixture/recorded/off/live adapter;
  - normalize model output into candidate decomposition without inventing missing claims;
  - run skeptic/F3 adapter in fixture/recorded/off/live mode;
  - classify skeptic findings as valid, invalid, or needs-evidence;
  - valid findings drive a repair attempt with new prompt/output hashes;
  - after two adjacent same-class repair failures, emit a `VerificationGap` or blocker;
  - run gate;
  - write core snapshot bundle;
  - emit v0 compatibility JSON.
- Quarantine the existing `_looks_like_arena_calibration` special case from the new AI-first path. Existing `arena.decomposer` v0 compatibility may keep it for legacy tests, but `arena.project_decomposer_ai` must not call it or use its component map.

Targeted command:

```bash
uv run pytest tests/test_project_decomposer_ai.py -q
```

Rollback point:

- Remove API module/tests and any optional `arena/__init__.py` exports.

### Phase D2 — Near-neighbor alternatives, probes, planted negatives, discrimination

Additional failing tests in `tests/test_project_decomposer_ai.py` and `tests/test_project_snapshot_gate.py`:

1. `test_near_neighbor_alternatives_reference_goal_and_non_goals`.
2. `test_independent_planted_negative_fires_probe`.
3. `test_golden_decomposition_does_not_fire_probe_false_positive_control`.
4. `test_probe_builder_independence_metadata_is_enforced`.
5. `test_cross_snapshot_probe_hash_leakage_blocks_gate`.

Implementation:

- Build near-neighbor alternatives only after candidate decomposition exists.
- Build/select planted negatives from independent hand-authored fixtures or a model/provider/session distinct from the decomposer.
- Record discrimination results against both decoy and golden controls.
- Never let probe text or prior probe hashes into primary decomposer context for the same snapshot.

Targeted command:

```bash
uv run pytest tests/test_project_decomposer_ai.py tests/test_project_snapshot_gate.py -q
```

Rollback point:

- Remove D2 probe/near-neighbor extensions while preserving D1 core snapshot path.

### Phase E — CLI

Failing tests first in `tests/test_project_model_cli_ai.py`:

1. `test_snapshot_cli_writes_artifacts_and_prints_summary_json`.
2. `test_snapshot_cli_requires_or_defaults_goal_and_non_goals`.
3. `test_snapshot_cli_returns_one_when_gate_fails_but_writes_diagnostics`.
4. `test_snapshot_cli_refuses_live_mode_without_explicit_live_flag_or_auth`.
5. `test_snapshot_cli_accepts_recorded_model_output_without_live_api`.
6. `test_gate_cli_revalidates_existing_manifest_without_llm_calls`.
7. `test_graph_cli_outputs_graph_json_without_writing_snapshot`.

Implementation:

- Add `arena/project_model_cli.py` argparse CLI.
- Existing `python -m arena.decomposer` remains unchanged by default.

Targeted command:

```bash
uv run pytest tests/test_project_model_cli_ai.py -q
```

Rollback point:

- Delete CLI module/tests; API remains usable.

### Phase F — Integration and current-contract preservation

Tests:

```bash
uv run pytest tests/test_project_graph.py tests/test_project_encyclopedia.py tests/test_project_snapshot_gate.py tests/test_project_decomposer_ai.py tests/test_project_model_cli_ai.py tests/test_project_decomposer.py tests/test_project_model_v0_contract.py -q
```

Checks:

```bash
uv run ruff check .
uv run pyright
uv run python -m arena.project_model_cli snapshot --project /home/leonb/projects/build-arena --artifacts-root /tmp/build-arena-ai-first-smoke --project-id build-arena --source-task "smoke" --primary-backlog-item "local" --goal "decompose this repository into responsibility-bearing components that can safely drive Build Arena" --non-goal "do not accept file-bucket components" --llm-mode fixture --overwrite
uv run python -m arena.project_model_cli gate --snapshot /tmp/build-arena-ai-first-smoke/<snapshot_id>/manifest.json
git diff --check
```

Rollback point:

- Revert new files and any `arena/decomposer.py`/`arena/__init__.py` glue. Existing v0 implementation must remain clean.

## 7. Pilot plan

### Pilot 1: Build Arena

Artifact directory:

```text
docs/verification/2026-06-04-ai-first-project-decomposer-pilot-build-arena/
```

Process:

1. Inspect repo state and source docs.
2. Run local verification:
   - `uv run pytest tests/test_project_decomposer.py tests/test_project_model_v0_contract.py tests/test_project_graph.py tests/test_project_encyclopedia.py tests/test_project_snapshot_gate.py tests/test_project_decomposer_ai.py tests/test_project_model_cli_ai.py -q`
   - `uv run ruff check .`
   - `uv run pyright`
3. Generate snapshot using fixture/no-live mode first.
4. Generate or replay at least one recorded real leading-model decomposition output for this delivery. Prefer live Grok if authenticated and within routine spend; otherwise use a frozen captured real-model fixture and document live auth/spend as blocked. This artifact is non-gating for CI but gating for delivery acceptance.
5. Run the same normalizer/gate path on fixture, recorded/live model output, fluent file-bucket negative, independent planted negative, and golden false-positive control.
6. Run Opus read-only review of pilot outputs.
7. Repair valid issues and re-run.

### Pilot 2: FMC-MPC

Discovery command default:

```bash
python3 - <<'PY'
from pathlib import Path
roots = [Path('/home/leonb/projects'), Path('/home/leonb/maei/projects'), Path('/home/leonb')]
for root in roots:
    if root.exists():
        for candidate in root.rglob('*'):
            if candidate.is_dir() and 'fmc' in candidate.name.lower() and (candidate/'.git').exists():
                print(candidate)
PY
```

Then inspect README, remote, branch/status, and choose canonical repo without asking Leon unless no safe candidate exists. If no canonical FMC-MPC repo can be found after searching `/home/leonb/projects`, `/home/leonb/maei/projects`, and `/home/leonb`, create the pilot directory with `pilot-status.json` status `blocked_missing_repo`, include discovery evidence, and do not fake a manifest.

Artifact directory:

```text
docs/verification/2026-06-04-ai-first-project-decomposer-pilot-fmc-mpc/
```

Verification command:

- Prefer repo-native test command from README/pyproject/package scripts.
- If no safe test exists, run the closest deterministic local check and record a verification gap.

### Pilot 3: held-out Leon repo

Default selection heuristic:

1. Local git repo under `/home/leonb/projects`.
2. Not Build Arena and not FMC-MPC.
3. Has README and deterministic local test/lint command.
4. Different technology/domain when possible.
5. No public deploy/push/merge required.

Artifact directory:

```text
docs/verification/2026-06-04-ai-first-project-decomposer-pilot-held-out/
```

Record why chosen in final report. If no safe held-out repo exists, write `pilot-status.json` with status `blocked_missing_safe_repo`, discovery evidence, and no fake manifest; the final report must classify this as a delivery blocker unless Leon explicitly accepts the gap.

## 8. Opus review points for implementation plan

Ask Opus to attack:

- feasibility;
- missing tests;
- wrong sequencing;
- overengineering;
- underbuilding;
- places implementation could pass tests but still be a report generator;
- insufficient pilot validation;
- F3/held-out-probe failure modes;
- whether this produces a working decomposer rather than plausible JSON.

Save:

- `docs/verification/2026-06-04-ai-first-project-decomposer-plan-opus-review.md`
- `docs/verification/2026-06-04-ai-first-project-decomposer-plan-opus-review.json` if available.

Patch this plan based on valid critique before implementation.

## 9. Verification commands before final acceptance

Required local verification commands:

```bash
uv run pytest tests/test_project_graph.py tests/test_project_encyclopedia.py tests/test_project_snapshot_gate.py tests/test_project_decomposer_ai.py tests/test_project_model_cli_ai.py -q
uv run pytest tests/test_project_decomposer.py tests/test_project_model_v0_contract.py -q
uv run pytest tests -q
uv run ruff check .
uv run pyright
git diff --check
```

Artifact validation:

```bash
python3 - <<'PY'
import json
from pathlib import Path
roots = [
    Path('docs/verification/2026-06-04-ai-first-project-decomposer-pilot-build-arena'),
    Path('docs/verification/2026-06-04-ai-first-project-decomposer-pilot-fmc-mpc'),
    Path('docs/verification/2026-06-04-ai-first-project-decomposer-pilot-held-out'),
]
for root in roots:
    manifests = list(root.rglob('manifest.json'))
    if not manifests:
        status_path = root / 'pilot-status.json'
        assert status_path.exists(), f'no manifest or pilot-status under {root}'
        status = json.loads(status_path.read_text())
        assert status['status'] in {'blocked_missing_repo', 'blocked_missing_safe_repo'}, status
        continue
    for manifest in manifests:
        data = json.loads(manifest.read_text())
        assert data['schema_version'] == 'project-model-snapshot/v0.1'
        gate = manifest.parent / 'gate-report.json'
        assert gate.exists(), gate
        report = json.loads(gate.read_text())
        assert report['passed'] is True, gate
print('artifact validation passed')
PY
```

Placeholder scan:

```bash
python3 - <<'PY'
from pathlib import Path
bad = []
tokens = ['TO' + 'DO', 'T' + 'BD', 'FIX' + 'ME', 'PEND' + 'ING', '[' + 'placeholder' + ']']
for path in [*Path('arena').rglob('*.py'), *Path('tests').rglob('*.py'), *Path('docs/specs').rglob('*.md'), *Path('docs/plans').rglob('*.md')]:
    text = path.read_text(encoding='utf-8')
    for token in tokens:
        if token in text:
            bad.append((str(path), token))
assert not bad, bad
print('placeholder scan passed')
PY
```

## 10. Final report contents

Write `docs/verification/2026-06-04-ai-first-project-decomposer-final-report.md` with:

- working/not working/blocked status;
- files changed;
- spec and plan review artifacts;
- implementation summary;
- repos piloted and why;
- exact commands/results;
- artifact paths;
- recorded real leading-model decomposition artifact path or explicit blocker if unavailable;
- top Opus findings and repairs;
- remaining risks/gaps;
- whether commits were made.

## 11. Rollback strategy

Safe rollback points are phase boundaries.

- Before implementation: spec/plan/review docs only.
- After graph/wiki: delete new graph/wiki modules/tests.
- After gate: delete snapshot/gate modules/tests.
- After API/CLI: delete new sidecar modules/tests and optional exports.
- After pilots: pilot docs are safe to delete without changing code.

Use git diff, not guesswork, before rollback. Do not use destructive git operations unless Leon explicitly authorizes them.
