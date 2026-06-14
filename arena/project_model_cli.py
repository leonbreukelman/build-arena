from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from arena.project_decomposer_ai import build_project_model_snapshot
from arena.project_graph import build_project_graph, graph_to_dict, write_graph_json
from arena.project_model_freshness import assess_project_model_freshness, freshness_to_dict
from arena.project_model_gate import (
    gate_report_to_dict,
    run_project_model_gate_from_manifest,
    write_gate_report,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m arena.project_model_cli")
    sub = parser.add_subparsers(dest="command", required=True)

    snapshot = sub.add_parser("snapshot")
    snapshot.add_argument("--project", required=True)
    snapshot.add_argument("--artifacts-root", required=True)
    snapshot.add_argument("--project-id")
    snapshot.add_argument("--goal")
    snapshot.add_argument("--non-goal", dest="non_goals", action="append", default=[])
    snapshot.add_argument("--source-task", default="AI-first project decomposition")
    snapshot.add_argument("--primary-backlog-item", default="local-snapshot")
    snapshot.add_argument("--llm-mode", choices=["fixture", "recorded", "live", "off"], default="fixture")
    snapshot.add_argument("--model-output")
    snapshot.add_argument("--allow-live", action="store_true")
    snapshot.add_argument("--live-provider", default="xai")
    snapshot.add_argument("--live-base-url")
    snapshot.add_argument("--live-model")
    snapshot.add_argument("--live-api-key-env")
    snapshot.add_argument("--live-max-tokens", type=int, default=4096)
    snapshot.add_argument("--run-adversarial-probes", action="store_true")
    snapshot.add_argument("--overwrite", action="store_true")

    gate = sub.add_parser("gate")
    gate.add_argument("--snapshot", required=True)

    graph = sub.add_parser("graph")
    graph.add_argument("--project", required=True)
    graph.add_argument("--output", required=True)

    freshness = sub.add_parser("freshness")
    freshness.add_argument("--project", required=True)
    freshness.add_argument("--snapshot", required=True)

    args = parser.parse_args(argv)
    if args.command == "snapshot":
        return _snapshot(args)
    if args.command == "gate":
        return _gate(args)
    if args.command == "graph":
        return _graph(args)
    if args.command == "freshness":
        return _freshness(args)
    parser.error("unknown command")
    return 2


def _snapshot(args: argparse.Namespace) -> int:
    if args.llm_mode == "live" and not args.allow_live:
        print("live mode requires --allow-live and configured auth; refusing routine live spend", file=sys.stderr)
        return 2
    if args.llm_mode == "live" and not args.live_model:
        print("live mode requires --live-model so real attempts do not rely on an unverified fallback model", file=sys.stderr)
        return 2
    try:
        result = build_project_model_snapshot(
            args.project,
            args.artifacts_root,
            project_id=args.project_id,
            goal=args.goal,
            non_goals=args.non_goals or None,
            source_task=args.source_task,
            primary_backlog_item=args.primary_backlog_item,
            llm_mode=args.llm_mode,
            model_output_path=args.model_output,
            live_provider=args.live_provider,
            live_model=args.live_model,
            live_base_url=args.live_base_url,
            live_api_key_env=args.live_api_key_env,
            live_max_tokens=args.live_max_tokens,
            overwrite=args.overwrite,
            run_adversarial_probes=args.run_adversarial_probes,
        )
    except Exception as exc:  # noqa: BLE001 - CLI must print concise diagnostics.
        print(str(exc), file=sys.stderr)
        return 2
    summary: dict[str, Any] = {
        "passed": result.gate_report.passed,
        "snapshot_id": result.snapshot.snapshot_id,
        "manifest_path": str(result.manifest_path),
        "snapshot_dir": str(result.snapshot_dir),
        "gate_report_path": str(result.snapshot_dir / "gate-report.json"),
        "violation_count": len(result.gate_report.violations),
    }
    print(json.dumps(summary, sort_keys=True))
    return 0 if result.gate_report.passed else 1


def _gate(args: argparse.Namespace) -> int:
    report = run_project_model_gate_from_manifest(args.snapshot)
    manifest_path = Path(args.snapshot)
    write_gate_report(manifest_path.parent / "gate-report.json", report)
    print(json.dumps(gate_report_to_dict(report), sort_keys=True))
    return 0 if report.passed else 1


def _graph(args: argparse.Namespace) -> int:
    graph = build_project_graph(args.project)
    write_graph_json(graph, args.output)
    summary = {
        "schema_version": graph.schema_version,
        "project_root": graph.project_root,
        "node_count": len(graph.nodes),
        "edge_count": len(graph.edges),
        "output": str(Path(args.output)),
        "dirty": graph.git.dirty,
    }
    # Touch graph_to_dict here so CLI graph output uses the same serializable contract as snapshots.
    if not isinstance(graph_to_dict(graph), dict):
        raise TypeError("graph serialization failed")
    print(json.dumps(summary, sort_keys=True))
    return 0


def _freshness(args: argparse.Namespace) -> int:
    report = assess_project_model_freshness(args.project, args.snapshot)
    payload = freshness_to_dict(report)
    print(json.dumps(payload, sort_keys=True))
    return report.exit_code


if __name__ == "__main__":
    raise SystemExit(main())
