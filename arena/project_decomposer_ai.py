from __future__ import annotations

import json
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
from arena.project_model_gate import run_project_model_gate, write_gate_report
from arena.project_model_llm import (
    build_fixture_model_output,
    build_noop_model_output,
    load_recorded_model_output,
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
    source_task: str = "AI-first project decomposition",
    primary_backlog_item: str = "local-snapshot",
    llm_mode: str = "fixture",
    model_output_path: str | Path | None = None,
    overwrite: bool = False,
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
        raise RuntimeError("live mode requires explicit CLI --allow-live and is not implemented for CI")
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
    snapshot = finalize_snapshot_identity(snapshot)
    gate_report = run_project_model_gate(snapshot, graph)

    root = Path(artifacts_root)
    snapshot_dir = root / snapshot.snapshot_id
    if snapshot_dir.exists():
        if overwrite:
            shutil.rmtree(snapshot_dir)
        else:
            raise FileExistsError(f"snapshot directory already exists: {snapshot_dir}; pass overwrite=True/--overwrite to replace it")
    snapshot_dir.mkdir(parents=True, exist_ok=True)

    graph_file_hash = write_json(snapshot_dir / "graph.json", graph_to_dict(graph))
    encyclopedia_manifest = write_encyclopedia(graph, snapshot_dir / "encyclopedia")
    snapshot_hash = write_json(snapshot_dir / "snapshot.json", snapshot_to_dict(snapshot))
    write_gate_report(snapshot_dir / "gate-report.json", gate_report)
    gate_hash = _sha((snapshot_dir / "gate-report.json").read_text(encoding="utf-8"))
    v0 = _project_model_v0_projection(snapshot, graph, source_task=source_task, primary_backlog_item=primary_backlog_item)
    v0_hash = write_json(snapshot_dir / "project-model-v0.json", v0)

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
    planted_negatives = raw_output.get("planted_negatives") or [
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
        "project_model_v0_path": "project-model-v0.json",
        "project_model_v0_hash": v0_hash,
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
        "artifact_hashes": {
            "snapshot": snapshot_hash,
            "graph_file": graph_file_hash,
            "gate_report": gate_hash,
            "project_model_v0": v0_hash,
        },
    }
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
    return ProjectModelSnapshot(
        project_id=project_id,
        project_root=project_root,
        goal=str(raw.get("goal") or goal),
        non_goals=list(raw.get("non_goals") or non_goals),
        primary_model_id=str(raw.get("model_id") or "unknown-model"),
        graph_hash=graph_hash,
        components=[Component(**item) for item in raw.get("components", [])],
        contracts=[Contract(**item) for item in raw.get("contracts", [])],
        cross_cutting_concerns=[CrossCuttingConcern(**item) for item in raw.get("cross_cutting_concerns", [])],
        observable_checks=[ObservableCheck(**item) for item in raw.get("observable_checks", [])],
        held_out_probes=[HeldOutProbe(**item) for item in raw.get("held_out_probes", [])],
        verification_gaps=[VerificationGap(**item) for item in raw.get("verification_gaps", [])],
        near_neighbor_alternatives=[NearNeighborAlternative(**item) for item in raw.get("near_neighbor_alternatives", [])],
        acceptance_command_allowlist=list(raw.get("acceptance_command_allowlist", [])),
        prompt_hashes={"decomposer": prompt_hash},
    )


def _project_model_v0_projection(snapshot: ProjectModelSnapshot, graph: ProjectGraph, *, source_task: str, primary_backlog_item: str) -> dict[str, Any]:
    component_id_map = {component.id: _identifier(component.id) for component in snapshot.components}
    check_ids_by_component = {component.id: f"check-{component_id_map[component.id]}" for component in snapshot.components}
    node_paths = {node.id: node.path or node.label for node in graph.nodes}
    components = [
        {
            "id": component_id_map[component.id],
            "name": component.name,
            "kind": "source",
            "riskLevel": "medium",
            "responsibilities": [component.responsibility],
            "ownedSurfaces": [node_paths.get(node_id, node_id) for node_id in component.owned_node_ids] or [component.id],
            "observableCheckIds": [check_ids_by_component[component.id]],
        }
        for component in snapshot.components
    ]
    observable_checks = [
        {
            "id": check_ids_by_component[component.id],
            "componentId": component_id_map[component.id],
            "mode": "test",
            "description": f"Observable local check for {component.name}.",
            "observableSignal": snapshot.observable_checks[0].command if snapshot.observable_checks else "local deterministic verification command",
            "evidenceRequired": ["passing local command output", "gate-report.json"],
            "noLiveApi": True,
        }
        for component in snapshot.components
    ]
    dependencies = [
        {
            "id": _identifier(contract.id),
            "fromComponent": component_id_map.get(contract.from_component_id, next(iter(component_id_map.values()), "component")),
            "toComponent": component_id_map.get(contract.to_component_id, next(iter(component_id_map.values()), "component")),
            "kind": "requires",
            "description": contract.name,
            "observableCheckIds": [check_ids_by_component.get(contract.from_component_id, next(iter(check_ids_by_component.values()), "check-component"))],
        }
        for contract in snapshot.contracts
    ]
    all_check_ids = list(check_ids_by_component.values()) or ["check-component"]
    return {
        "schemaVersion": "project-model/v0",
        "id": _identifier(snapshot.project_id),
        "source": {
            "task": source_task,
            "primaryBacklogItem": primary_backlog_item,
            "repo": snapshot.project_root,
        },
        "goal": snapshot.goal,
        "nonGoals": snapshot.non_goals,
        "components": components,
        "dependencies": dependencies,
        "invariants": [
            {
                "id": _identifier(concern.id),
                "description": concern.description,
                "componentIds": [component_id_map[item] for item in concern.component_ids if item in component_id_map],
                "observableCheckIds": all_check_ids,
            }
            for concern in snapshot.cross_cutting_concerns
        ],
        "observableChecks": observable_checks,
        "evidenceRequirements": [
            {
                "id": "evidence-gate-report",
                "description": "Deterministic gate report and provenance-backed snapshot artifacts.",
                "acceptedArtifactTypes": ["json", "markdown", "command-output"],
                "requiredFor": list(component_id_map.values()),
            }
        ],
        "assumptions": [
            {
                "id": "assumption-llm-advisory",
                "description": "LLM claims are advisory until deterministic gates pass.",
                "status": "confirmed",
            }
        ],
        "risks": [
            {
                "id": "risk-f3-wrong-target",
                "level": "medium",
                "description": "A fluent decomposition could optimize the wrong target; near-neighbors and probes mitigate this.",
                "mitigation": "Run deterministic gates, held-out probes, and independent review.",
            }
        ],
        "nearNeighborAlternatives": [
            {
                "id": _identifier(near.id),
                "description": near.alternative,
                "whyNotPrimary": near.why_not_primary,
                "distinguishingEvidence": ["graph provenance", "held-out probe discrimination"],
            }
            for near in snapshot.near_neighbor_alternatives
        ],
        "heldOutProbes": [
            {
                "id": _identifier(probe.id),
                "componentId": component_id_map.get(probe.target_component_ids[0], next(iter(component_id_map.values()), "component")) if probe.target_component_ids else next(iter(component_id_map.values()), "component"),
                "probeType": "negative-control",
                "scenario": f"Reject planted negative {probe.planted_negative_id}.",
                "expectedBehavior": "Gate/probe rejects wrong-target or file-bucket decomposition and accepts golden control.",
                "evidenceRequired": ["held-out-probes.json", "planted-negatives.json", "gate-report.json"],
            }
            for probe in snapshot.held_out_probes
        ],
        "verificationGaps": [
            {
                "id": _identifier(gap.id),
                "severity": "high" if gap.severity == "blocker" else gap.severity,
                "description": gap.description,
                "affectedComponentIds": [component_id_map[item] for item in gap.component_ids if item in component_id_map],
                "proposedClosureCheck": gap.proposed_closure_check,
            }
            for gap in snapshot.verification_gaps
        ],
        "unclassifiedProjectSurface": [],
        "advisorySignalHandoff": {
            "consumer": "elenchus-core",
            "expectedFields": [
                "goal",
                "nonGoals",
                "components",
                "dependencies",
                "observableChecks",
                "verificationGaps",
            ],
            "optionalFLabelHint": True,
        },
    }


def _decomposer_prompt(*, project_id: str, goal: str, non_goals: list[str], graph: ProjectGraph) -> str:
    node_lines = "\n".join(f"- {node.kind}: {node.path or node.symbol or node.label}" for node in graph.nodes[:200])
    return (
        "Build an AI-first project decomposition from graph/wiki evidence only.\n"
        f"Project: {project_id}\nGoal: {goal}\nNon-goals: {json.dumps(non_goals, sort_keys=True)}\n"
        "Reject vague/file-bucket leaves; produce components, contracts, concerns, checks, gaps, near-neighbors, and probes.\n"
        f"Graph sample:\n{node_lines}\n"
    )


def _skeptic_prompt(*, goal: str, non_goals: list[str]) -> str:
    return (
        "Attack the candidate decomposition for F3 wrong-target risk, fluent file buckets, fabricated provenance, "
        "weak contracts, and held-out-probe leakage.\n"
        f"Goal: {goal}\nNon-goals: {json.dumps(non_goals, sort_keys=True)}\n"
    )


def _identifier(raw: str) -> str:
    cleaned = re.sub(r"[^a-z0-9_-]+", "-", raw.lower()).strip("-")
    if not cleaned:
        cleaned = "item"
    if not cleaned[0].isalpha():
        cleaned = "item-" + cleaned
    return cleaned[:64]


def _sha(text: str) -> str:
    import hashlib

    return hashlib.sha256(text.encode()).hexdigest()
