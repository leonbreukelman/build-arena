from __future__ import annotations

import hashlib
import json
from typing import Any

from arena.project_graph import ProjectGraph, graph_to_dict
from arena.project_iteration_readiness import build_iteration_readiness
from arena.project_snapshot import (
    GateReport,
    ProjectModelSnapshot,
    gate_report_to_dict,
    snapshot_to_dict,
)

PROJECT_MODEL_V1_SCHEMA_VERSION = "project-model/v1"


def project_model_v1_from_snapshot(
    snapshot: ProjectModelSnapshot,
    graph: ProjectGraph,
    gate_report: GateReport,
    *,
    artifact_hashes: dict[str, str] | None = None,
    derived_artifacts: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    graph_dict = graph_to_dict(graph)
    git = graph_dict["git"]
    artifact_hashes = dict(artifact_hashes or {})
    default_derived_artifacts = [
        {
            "artifactType": "jsonl-events",
            "path": "events.jsonl",
            "strategy": "Canonical future run-loop events reference this project-model/v1 snapshot by id and hash.",
        },
        {
            "artifactType": "sqlite-projection",
            "path": "events.sqlite",
            "strategy": "SQLite is a query projection derived from JSONL events and project-model/v1 artifacts, not authoritative state.",
        },
        {
            "artifactType": "markdown-summary",
            "path": "summary.md",
            "strategy": "Markdown summaries are generated human-readable views and must carry snapshot id/hash provenance.",
        },
    ]
    graph_hash = snapshot.graph_hash or hashlib.sha256(json.dumps(graph_dict, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return {
        "schemaVersion": PROJECT_MODEL_V1_SCHEMA_VERSION,
        "id": snapshot.snapshot_id,
        "project": {
            "projectId": snapshot.project_id,
            "projectRoot": snapshot.project_root,
            "goal": snapshot.goal,
            "nonGoals": snapshot.non_goals,
        },
        "snapshot": snapshot_to_dict(snapshot),
        "projectGraph": {
            "schemaVersion": graph_dict["schema_version"],
            "graphHash": graph_hash,
            "projectRoot": graph_dict["project_root"],
            "nodes": graph_dict["nodes"],
            "edges": graph_dict["edges"],
        },
        "gateReport": gate_report_to_dict(gate_report),
        "provenance": {
            "git": {
                "available": git["available"],
                "root": git["root"],
                "headOid": git["head_oid"],
                "dirty": git["dirty"],
                "dirtyPaths": git["dirty_paths"],
                "dirtyStateFingerprint": _dirty_state_fingerprint(git),
            },
            "provenanceRefStrategy": "All graph, component, contract, check, probe, and gap claims must resolve to ProjectGraph ProvenanceRef ids or be declared as verification gaps.",
        },
        "hashes": {
            "inputHashes": snapshot.input_hashes,
            "promptHashes": snapshot.prompt_hashes,
            "outputHashes": snapshot.model_output_hashes,
            "artifactHashes": artifact_hashes,
        },
        "models": {
            "primary": snapshot.primary_model_id,
            "probeBuilders": sorted({probe.builder_model_id for probe in snapshot.held_out_probes}),
        },
        "derivedArtifacts": derived_artifacts or default_derived_artifacts,
        "iterationReadiness": build_iteration_readiness(snapshot, graph),
    }


def _dirty_state_fingerprint(git: dict[str, Any]) -> str:
    payload = {
        "headOid": git.get("head_oid"),
        "dirty": git.get("dirty"),
        "dirtyPaths": git.get("dirty_paths") or [],
    }
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
