from __future__ import annotations

import dataclasses
import json
import logging
import re
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from arena.project_encyclopedia import write_encyclopedia
from arena.project_graph import (
    ProjectGraph,
    build_project_graph,
    canonical_graph_json,
    graph_to_dict,
)
from arena.project_model_gate import (
    UNIVERSAL_CONCERNS,
    close_import_contracts_for_gate,
    run_project_model_gate,
    write_gate_report,
)
from arena.project_model_llm import (
    LiveProjectModelLLM,
    build_fixture_model_output,
    build_noop_model_output,
    load_recorded_model_output,
)
from arena.project_model_v1 import project_model_v1_from_snapshot
from arena.project_probe_runner import (
    PathBucketProbeRun,
    run_path_bucket_adversarial_probe,
    write_probe_proof_artifacts,
)
from arena.project_snapshot import (
    Component,
    Contract,
    CrossCuttingConcern,
    GateReport,
    HeldOutProbe,
    NearNeighborAlternative,
    ObservableCheck,
    ProjectModelSnapshot,
    VerificationGap,
    finalize_snapshot_identity,
    snapshot_to_dict,
    stable_hash_json,
    write_json,
)

_LOG = logging.getLogger(__name__)


@dataclass(slots=True)
class BuildProjectModelResult:
    snapshot: ProjectModelSnapshot
    gate_report: GateReport
    graph: ProjectGraph
    snapshot_dir: Path
    manifest_path: Path
    manifest: dict[str, Any]


def build_project_model_snapshot(
    project: str | Path,
    artifacts_root: str | Path,
    *,
    project_id: str | None = None,
    goal: str | None = None,
    non_goals: list[str] | None = None,
    llm_mode: str = "fixture",
    model_output_path: str | Path | None = None,
    live_llm: Any | None = None,
    live_provider: str = "xai",
    live_model: str | None = None,
    live_base_url: str | None = None,
    live_api_key_env: str | None = None,
    live_max_tokens: int = 4096,
    overwrite: bool = False,
    run_adversarial_probes: bool = False,
) -> BuildProjectModelResult:
    graph = build_project_graph(project)
    project_id = project_id or Path(graph.project_root).name
    goal = goal or "decompose this repository into responsibility-bearing components"
    non_goals = non_goals or ["do not treat file buckets as final components"]
    graph_hash = _sha(canonical_graph_json(graph))

    prompt = _decomposer_prompt(project_id=project_id, goal=goal, non_goals=non_goals, graph=graph)
    if llm_mode == "fixture":
        raw_output = build_fixture_model_output(graph, project_id=project_id, goal=goal, non_goals=non_goals)
    elif llm_mode == "recorded":
        if model_output_path is None:
            raise ValueError("recorded mode requires model_output_path")
        raw_output = load_recorded_model_output(model_output_path)
    elif llm_mode == "off":
        raw_output = build_noop_model_output(graph, project_id=project_id, goal=goal, non_goals=non_goals)
    elif llm_mode == "live":
        adapter = live_llm or LiveProjectModelLLM(
            provider=live_provider,
            model=live_model,
            base_url=live_base_url,
            api_key_env=live_api_key_env,
            max_tokens=live_max_tokens,
        )
        raw_output = adapter.generate(prompt)
    else:
        raise ValueError(f"unsupported llm_mode {llm_mode!r}")

    snapshot = _snapshot_from_model_output(
        raw_output,
        project_id=project_id,
        project_root=graph.project_root,
        goal=goal,
        non_goals=non_goals,
        graph_hash=graph_hash,
        prompt_hash=_sha(prompt),
    )
    snapshot.input_hashes = {"graph": graph_hash}
    snapshot.model_output_hashes["decomposer"] = stable_hash_json(raw_output)
    snapshot = close_import_contracts_for_gate(snapshot, graph)
    snapshot = finalize_snapshot_identity(snapshot)
    probe_result: PathBucketProbeRun | None = None
    if run_adversarial_probes:
        probe_result = run_path_bucket_adversarial_probe(snapshot, graph)
        snapshot = probe_result.snapshot

    root = Path(artifacts_root)
    snapshot_dir = root / snapshot.snapshot_id
    if snapshot_dir.exists():
        if overwrite:
            shutil.rmtree(snapshot_dir)
        else:
            raise FileExistsError(f"snapshot directory already exists: {snapshot_dir}; pass overwrite=True/--overwrite to replace it")
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    if probe_result is not None:
        write_probe_proof_artifacts(snapshot_dir, probe_result)
    closure_hash = write_json(snapshot_dir / "import-contract-closure.json", _import_contract_closure_report(snapshot))
    gate_report = run_project_model_gate(snapshot, graph, proof_artifact_base=snapshot_dir)

    graph_file_hash = write_json(snapshot_dir / "graph.json", graph_to_dict(graph))
    encyclopedia_manifest = write_encyclopedia(graph, snapshot_dir / "encyclopedia")
    snapshot_hash = write_json(snapshot_dir / "snapshot.json", snapshot_to_dict(snapshot))
    write_gate_report(snapshot_dir / "gate-report.json", gate_report)
    gate_hash = _sha((snapshot_dir / "gate-report.json").read_text(encoding="utf-8"))
    artifact_hashes = {
        "snapshot": snapshot_hash,
        "graph_file": graph_file_hash,
        "gate_report": gate_hash,
        "import_contract_closure": closure_hash,
    }
    v1 = project_model_v1_from_snapshot(
        snapshot,
        graph,
        gate_report,
        artifact_hashes=artifact_hashes,
    )
    v1_hash = write_json(snapshot_dir / "project-model-v1.json", v1)
    artifact_hashes["project_model_v1"] = v1_hash

    prompt_dir = snapshot_dir / "prompts"
    prompt_dir.mkdir(exist_ok=True)
    (prompt_dir / "decomposer-prompt.txt").write_text(prompt, encoding="utf-8")
    skeptic_prompt = _skeptic_prompt(goal=goal, non_goals=non_goals)
    (prompt_dir / "skeptic-reviewer-prompt.txt").write_text(skeptic_prompt, encoding="utf-8")

    model_dir = snapshot_dir / "model-outputs"
    model_dir.mkdir(exist_ok=True)
    write_json(model_dir / "decomposer.raw.json", raw_output)
    if raw_output.get("probe_builder_output"):
        write_json(model_dir / "probe-builder.raw.json", raw_output["probe_builder_output"])
    if raw_output.get("negative_control_summary"):
        write_json(snapshot_dir / "negative-control-summary.json", raw_output["negative_control_summary"])
    if raw_output.get("probe_evaluation_results"):
        write_json(snapshot_dir / "probe-evaluation-results.json", raw_output["probe_evaluation_results"])
    skeptic_output = {
        "model_id": "fixture-skeptic-f3-reviewer",
        "findings": [],
        "classification": "no_blocking_findings_in_fixture_review",
        "bounded_repair_rounds": 0,
    }
    write_json(model_dir / "skeptic-review.raw.json", skeptic_output)
    write_json(snapshot_dir / "near-neighbor-alternatives.json", snapshot.near_neighbor_alternatives)
    write_json(snapshot_dir / "held-out-probes.json", snapshot.held_out_probes)
    planted_negatives = (probe_result.planted_negatives if probe_result is not None and probe_result.planted_negatives else raw_output.get("planted_negatives")) or [
        {
            "id": probe.planted_negative_id,
            "kind": "fluent_file_bucket_negative",
            "independent_from_probe_builder": True,
            "target_probe_id": probe.id,
        }
        for probe in snapshot.held_out_probes
    ]
    write_json(snapshot_dir / "planted-negatives.json", planted_negatives)
    write_json(snapshot_dir / "acceptance-command-allowlist.json", snapshot.acceptance_command_allowlist)

    manifest = {
        "schema_version": snapshot.schema_version,
        "snapshot_id": snapshot.snapshot_id,
        "project_id": snapshot.project_id,
        "project_root": snapshot.project_root,
        "goal": snapshot.goal,
        "non_goals": snapshot.non_goals,
        "created_at_utc": snapshot.created_at_utc,
        "graph_path": "graph.json",
        "graph_hash": graph_hash,
        "graph_file_hash": graph_file_hash,
        "encyclopedia_manifest_path": "encyclopedia/manifest.json",
        "encyclopedia_manifest_hash": stable_hash_json(encyclopedia_manifest),
        "snapshot_path": "snapshot.json",
        "snapshot_hash": snapshot_hash,
        "gate_report_path": "gate-report.json",
        "gate_report_hash": gate_hash,
        "project_model_primary_path": "project-model-v1.json",
        "project_model_v1_path": "project-model-v1.json",
        "project_model_v1_hash": v1_hash,
        "dirty_state": {
            "dirty": graph.git.dirty,
            "dirty_paths": graph.git.dirty_paths,
            "head_oid": graph.git.head_oid,
        },
        "input_hashes": snapshot.input_hashes,
        "prompt_hashes": snapshot.prompt_hashes,
        "model_ids": {
            "decomposer": snapshot.primary_model_id,
            "skeptic": skeptic_output["model_id"],
            "probe_builder": snapshot.held_out_probes[0].builder_model_id if snapshot.held_out_probes else "none",
        },
        "output_hashes": snapshot.model_output_hashes,
        "artifact_hashes": artifact_hashes,
    }
    if raw_output.get("_provider_metadata"):
        manifest["live_provider_metadata"] = raw_output["_provider_metadata"]
    manifest_path = snapshot_dir / "manifest.json"
    write_json(manifest_path, manifest)
    return BuildProjectModelResult(
        snapshot=snapshot,
        gate_report=gate_report,
        graph=graph,
        snapshot_dir=snapshot_dir,
        manifest_path=manifest_path,
        manifest=manifest,
    )


_TOP_LEVEL_ALIASES: dict[str, tuple[str, ...]] = {
    "observable_checks": ("observable_checks", "checks"),
    "cross_cutting_concerns": ("cross_cutting_concerns", "concerns"),
    "verification_gaps": ("verification_gaps", "gaps"),
    "near_neighbor_alternatives": ("near_neighbor_alternatives", "near_neighbors"),
    "held_out_probes": ("held_out_probes", "probes"),
    "components": ("components",),
    "contracts": ("contracts",),
}


def _resolve_list(raw: dict[str, Any], canonical: str) -> list[Any]:
    """Return a list for a canonical key, accepting known provider aliases.

    Fail-closed: a present-but-non-list value is an error rather than silently
    coerced, so a malformed model response surfaces a clear diagnostic.
    """
    for key in _TOP_LEVEL_ALIASES.get(canonical, (canonical,)):
        if key in raw and raw[key] is not None:
            value = raw[key]
            if not isinstance(value, list):
                raise ValueError(f"model output field {key!r} must be a JSON array, got {type(value).__name__}")
            return value
    return []


def _is_list_type(type_repr: str) -> bool:
    # Only treat a field as list-typed when one of its union members is itself a
    # list[...] at the top level. Checking each "|" member's prefix (rather than a
    # substring search) avoids false positives like dict[str, list[str]].
    normalized = type_repr.replace(" ", "")
    return any(member.startswith(("list[", "List[")) for member in normalized.split("|"))


def _is_dict_type(type_repr: str) -> bool:
    normalized = type_repr.replace(" ", "")
    return any(member.startswith(("dict[", "Dict[")) for member in normalized.split("|"))


def _normalise_universal_concern_id(raw_id: str) -> str | None:
    normalised = re.sub(r"[^a-z0-9]+", "_", raw_id.lower()).strip("_")
    if normalised in UNIVERSAL_CONCERNS:
        return normalised
    for prefix in ("ccc_", "concern_"):
        if normalised.startswith(prefix) and normalised.removeprefix(prefix) in UNIVERSAL_CONCERNS:
            return normalised.removeprefix(prefix)
    return None


def _normalise_cross_cutting_concerns(
    concerns: list[CrossCuttingConcern], components: list[Component]
) -> list[CrossCuttingConcern]:
    provenance_by_component = {component.id: list(component.provenance_refs) for component in components}
    for concern in concerns:
        canonical = _normalise_universal_concern_id(concern.id)
        if concern.category not in UNIVERSAL_CONCERNS and canonical is not None:
            _LOG.warning(
                "Canonicalized universal concern category from id",
                extra={"concern_id": concern.id, "old_category": concern.category, "new_category": canonical},
            )
            concern.category = canonical
        if concern.category not in UNIVERSAL_CONCERNS or concern.provenance_refs:
            continue
        refs: list[str] = []
        for component_id in concern.component_ids:
            refs.extend(provenance_by_component.get(component_id, []))
        concern.provenance_refs = list(dict.fromkeys(ref for ref in refs if ref))
        if concern.provenance_refs:
            _LOG.warning(
                "Backfilled universal concern provenance from covered components",
                extra={"concern_id": concern.id, "category": concern.category, "count": len(concern.provenance_refs)},
            )
    return concerns


def _coerce_dataclass(cls: type, item: Any, *, collection: str, index: int) -> Any:
    """Build a dataclass from a model-produced dict, fail-closed on identity gaps.

    - Unknown keys the model invents are dropped (the full raw output is still
      persisted to disk for audit).
    - Missing list-typed fields default to empty lists so a structurally valid
      decomposition still builds and reaches the deterministic gate. Note: empty
      defaults are only safe because the deterministic gate independently rejects
      components with empty owned_node_ids / provenance_refs; coercion does not
      vouch for completeness, it only prevents a crash.
    - A present list-typed field that is NOT a JSON array (e.g. the model emits a
      bare string for owned_node_ids) is rejected with a clear error rather than
      splatted into the dataclass to detonate or silently iterate downstream.
    - Missing required scalar identity fields (no dataclass default) raise a
      clear error instead of a raw TypeError, so non-conforming model output is
      a diagnostic, not a crash.
    """
    if not isinstance(item, dict):
        raise ValueError(f"{collection}[{index}] must be a JSON object, got {type(item).__name__}")
    fields = {f.name: f for f in dataclasses.fields(cls)}
    kwargs: dict[str, Any] = {}
    missing_required: list[str] = []
    for name, spec in fields.items():
        type_repr = str(spec.type)
        if name in item and item[name] is not None:
            value = item[name]
            if _is_list_type(type_repr) and not isinstance(value, list):
                raise ValueError(
                    f"{collection}[{index}].{name} must be a JSON array, got {type(value).__name__}"
                )
            kwargs[name] = value
            continue
        has_default = spec.default is not dataclasses.MISSING or spec.default_factory is not dataclasses.MISSING  # type: ignore[misc]
        if has_default:
            continue
        if _is_list_type(type_repr):
            kwargs[name] = []
            continue
        if _is_dict_type(type_repr):
            kwargs[name] = {}
            continue
        missing_required.append(name)
    if missing_required:
        raise ValueError(
            f"{collection}[{index}] is missing required field(s) {sorted(missing_required)}; "
            f"model output did not conform to the {cls.__name__} schema"
        )
    return cls(**kwargs)


def _coerce_list(cls: type, raw: dict[str, Any], canonical: str) -> list[Any]:
    return [
        _coerce_dataclass(cls, item, collection=canonical, index=index)
        for index, item in enumerate(_resolve_list(raw, canonical))
    ]


def _snapshot_from_model_output(
    raw: dict[str, Any],
    *,
    project_id: str,
    project_root: str,
    goal: str,
    non_goals: list[str],
    graph_hash: str,
    prompt_hash: str,
) -> ProjectModelSnapshot:
    if not isinstance(raw, dict):
        raise ValueError(f"model output must be a JSON object, got {type(raw).__name__}")
    components = _coerce_list(Component, raw, "components")
    cross_cutting_concerns = _normalise_cross_cutting_concerns(
        _coerce_list(CrossCuttingConcern, raw, "cross_cutting_concerns"), components
    )
    observable_checks = _coerce_list(ObservableCheck, raw, "observable_checks")
    return ProjectModelSnapshot(
        project_id=project_id,
        project_root=project_root,
        goal=str(raw.get("goal") or goal),
        non_goals=list(raw.get("non_goals") or non_goals),
        primary_model_id=str(raw.get("model_id") or "unknown-model"),
        graph_hash=graph_hash,
        components=components,
        contracts=_coerce_list(Contract, raw, "contracts"),
        cross_cutting_concerns=cross_cutting_concerns,
        observable_checks=observable_checks,
        held_out_probes=_coerce_list(HeldOutProbe, raw, "held_out_probes"),
        verification_gaps=_coerce_list(VerificationGap, raw, "verification_gaps"),
        near_neighbor_alternatives=_coerce_list(NearNeighborAlternative, raw, "near_neighbor_alternatives"),
        acceptance_command_allowlist=_safe_acceptance_commands(raw.get("acceptance_command_allowlist", []), observable_checks),
        prompt_hashes={"decomposer": prompt_hash},
    )


# Shell metacharacters that must never appear in an acceptance command string.
_UNSAFE_COMMAND_CHARS = frozenset(";|&`$><\n\\\"'(){}")
# The ONLY acceptance-allowlist entries trusted from model output: a fixed,
# harness-defined set of symbolic labels and known-safe literal commands. This set
# is a constant in the codebase, NOT derived from model output, so it cannot be
# widened by the model. Anything the model proposes that is not in this exact set
# is dropped (raw command strings are never trusted, even if the model also
# "declares" them as a check command, since that source is model-controlled too).
_SAFE_ACCEPTANCE_ENTRIES = frozenset({"local-pytest", "uv run python -m pytest -q"})


def _safe_acceptance_commands(raw_allowlist: Any, observable_checks: list[Any]) -> list[str]:
    """Fail-closed filter for the model-controlled acceptance command allowlist.

    The allowlist is model-produced and is a latent command-execution surface.
    An entry is admitted only if it is in the fixed, harness-defined
    ``_SAFE_ACCEPTANCE_ENTRIES`` set (constant in code, outside model control) and
    contains no shell metacharacters. Model-declared observable_check command
    strings are intentionally NOT a trust source, because the model controls those
    too. ``observable_checks`` is accepted for signature stability but unused.
    Anything else is dropped, not run.
    """
    if not isinstance(raw_allowlist, list):
        return []
    safe: list[str] = []
    for entry in raw_allowlist:
        command = str(entry).strip()
        if not command or command not in _SAFE_ACCEPTANCE_ENTRIES:
            continue
        if any(char in _UNSAFE_COMMAND_CHARS for char in command):
            continue
        if command not in safe:
            safe.append(command)
    return safe



def _decomposer_prompt(*, project_id: str, goal: str, non_goals: list[str], graph: ProjectGraph) -> str:
    # Give the model the real identifier vocabulary it must reuse. The deterministic
    # gate resolves component.owned_node_ids against graph node ids, component
    # provenance_refs against graph provenance ids, and contract.supporting_edge_ids
    # against graph edge ids. Critically, inventory_coverage is scored against the
    # gate's *primary inventory* module set, so the prompt must show that exact set
    # (not an arbitrary sample) or a perfect model still cannot pass. We reuse the
    # gate's own selector as the single source of truth to prevent prompt/gate drift.
    from arena.project_model_gate import primary_inventory_nodes

    graph_dict = graph_to_dict(graph)
    nodes_by_id = {node["id"]: node for node in graph_dict["nodes"]}
    primary_nodes = primary_inventory_nodes(nodes_by_id)
    primary_ids = {node["id"] for node in primary_nodes}

    node_lines = []
    for node in primary_nodes:
        prov = (node.get("provenance_refs") or [{}])[0].get("id", "")
        node_lines.append(f"- node_id={node['id']} kind={node['kind']} path={node.get('path')} prov={prov}")
    # Also expose the symbol-level nodes that belong to those primary modules so the
    # model can own functions/classes, plus the import/call/test edges for contracts.
    symbol_kinds = {"python_class", "python_function"}
    for node in graph_dict["nodes"]:
        if node.get("kind") in symbol_kinds and len(node_lines) < 200:
            prov = (node.get("provenance_refs") or [{}])[0].get("id", "")
            node_lines.append(f"- node_id={node['id']} kind={node['kind']} path={node.get('path')} prov={prov}")
    edge_lines = []
    for edge in [e for e in graph_dict["edges"] if e["kind"] in {"imports", "tests"}][:80]:
        edge_lines.append(f"- edge_id={edge['id']} kind={edge['kind']} from={edge['from_node_id']} to={edge['to_node_id']}")
    schema = (
        "Output STRICT JSON with these exact keys (no markdown):\n"
        '{\n'
        '  "model_id": str, "project_id": str, "goal": str, "non_goals": [str],\n'
        '  "components": [{"id": str, "name": str, "responsibility": str (>=6 words, a semantic responsibility not a file list),\n'
        '     "owned_node_ids": [node_id from the list below], "provenance_refs": [prov id from a node you own],\n'
        '     "contract_ids": [id of a contract you declare], "check_ids": [id of an observable_check you declare],\n'
        '     "verification_gap_ids": [id of a verification_gap you declare]}],\n'
        '  "contracts": [{"id": str, "name": str, "from_component_id": component id, "to_component_id": component id,\n'
        '     "supporting_edge_ids": [edge_id from the list below connecting the two components],\n'
        '     "near_neighbor_alternative_ids": [], "provenance_refs": [prov id]}],\n'
        '  "cross_cutting_concerns": [{"id": str, "category": str (for universal concerns, category MUST be exactly one of anti_fabrication|determinism|provenance|no_live_paid_api_acceptance), "description": str, "component_ids": [component id],\n'
        '     "contract_ids": [], "provenance_refs": [prov id]}],\n'
        '  "observable_checks": [{"id": str, "description": str, "command": str, "component_ids": [component id],\n'
        '     "contract_ids": [], "provenance_refs": [prov id]}],\n'
        '  "verification_gaps": [{"id": str, "description": str, "severity": "low|medium|high|blocker",\n'
        '     "component_ids": [component id], "contract_ids": [], "provenance_refs": [prov id]}],\n'
        '  "near_neighbor_alternatives": [{"id": str, "target_id": component id, "alternative": str,\n'
        '     "why_not_primary": str, "provenance_refs": [prov id]}]\n'
        '}\n'
        "Rules: reuse only node_id/edge_id/prov ids shown below; never invent ids.\n"
        "- EVERY primary module node listed below must be owned by exactly one component "
        "(or, if you cannot responsibly place it, covered by a verification_gap whose provenance_refs "
        "includes that node's prov id). Uncovered primary modules fail the inventory gate.\n"
        "- Every component must own >=1 node, cite a provenance id from a node it owns, and declare >=1 of contract/check/gap.\n"
        "- Decompose into MULTIPLE components (one per distinct responsibility); a single component covering the whole "
        "repo is a file-bucket and fails the gate. Each listed primary module must be owned by some component.\n"
        "- Every contract must connect TWO DISTINCT components (from_component_id != to_component_id) and cite at least "
        "one supporting_edge_id from the edges below whose endpoints map to those two components. A self-referential "
        "contract or one with no supporting edge fails the gate.\n"
        "- Include the universal cross_cutting_concerns: anti_fabrication, determinism, provenance, "
        "no_live_paid_api_acceptance (each covering all components), plus protected_surface_integrity and "
        "generated_artifact_integrity if such surfaces exist. For each universal concern, category MUST be exactly one of "
        "anti_fabrication, determinism, provenance, no_live_paid_api_acceptance. Do not use thematic labels such as integrity, "
        "reliability, traceability, or compliance in category. Example: {\"id\": \"concern.anti-fabrication\", "
        "\"category\": \"anti_fabrication\", \"component_ids\": [\"component.example\"], \"contract_ids\": [], "
        "\"provenance_refs\": [\"prov:example\"]}.\n"
        "- Provide at least one observable_check.\n"
        "- HELD-OUT PROBES: you have no probe-execution artifacts, so do NOT claim probe pass/fail. Instead record at "
        "least one verification_gap whose description mentions 'probe' and one of: 'semantic', 'independent', "
        "'held-out', or 'planted-negative' (this is the accepted unproven-probe gap).\n"
        "- Reject vague/file-bucket leaves.\n"
    )
    return (
        "Build an AI-first project decomposition from the deterministic graph evidence below. "
        "You enrich the graph into responsibility-bearing components; you do not invent identifiers.\n"
        f"Project: {project_id}\nGoal: {goal}\nNon-goals: {json.dumps(non_goals, sort_keys=True)}\n\n"
        f"{schema}\n"
        f"Primary modules to fully cover ({len(primary_ids)} total):\n" + "\n".join(node_lines) + "\n\n"
        "Graph edges (reuse these ids for contract support):\n" + "\n".join(edge_lines) + "\n"
    )


def _skeptic_prompt(*, goal: str, non_goals: list[str]) -> str:
    return (
        "Attack the candidate decomposition for F3 wrong-target risk, fluent file buckets, fabricated provenance, "
        "weak contracts, fake probe-proof claims, and unclosed semantic-validation gaps.\n"
        f"Goal: {goal}\nNon-goals: {json.dumps(non_goals, sort_keys=True)}\n"
    )


def _import_contract_closure_report(snapshot: ProjectModelSnapshot) -> dict[str, Any]:
    auto_contract_ids = sorted(contract.id for contract in snapshot.contracts if contract.id.startswith("contract.auto."))
    return {
        "schemaVersion": "import-contract-closure/v0",
        "snapshotId": snapshot.snapshot_id,
        "autoContractCount": len(auto_contract_ids),
        "autoContractIds": auto_contract_ids,
        "note": "Auto contracts are deterministic import-edge closure derived from graph evidence and model component ownership.",
    }


def _sha(text: str) -> str:
    import hashlib

    return hashlib.sha256(text.encode()).hexdigest()
