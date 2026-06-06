from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def _run(cmd: list[str], cwd: Path, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=cwd, text=True, capture_output=True, check=check)


def _init_repo(root: Path) -> None:
    _run(["git", "init", "-b", "main"], root)
    _run(["git", "config", "user.email", "arena@example.invalid"], root)
    _run(["git", "config", "user.name", "Arena Tests"], root)
    _run(["git", "add", "."], root)
    _run(["git", "commit", "-m", "baseline"], root)


def _write_repo(root: Path) -> None:
    (root / "pkg").mkdir()
    (root / "tests").mkdir()
    (root / "pkg" / "__init__.py").write_text("", encoding="utf-8")
    (root / "pkg" / "core.py").write_text("def run() -> int:\n    return 1\n", encoding="utf-8")
    (root / "tests" / "test_core.py").write_text("from pkg.core import run\n\ndef test_run():\n    assert run() == 1\n", encoding="utf-8")
    (root / "pyproject.toml").write_text("[project]\nname='cli-project'\nversion='0.0.0'\n", encoding="utf-8")
    _init_repo(root)


def test_snapshot_cli_writes_artifacts_and_prints_summary_json(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _write_repo(repo)
    artifacts = tmp_path / "artifacts"

    proc = _run(
        [
            sys.executable,
            "-m",
            "arena.project_model_cli",
            "snapshot",
            "--project",
            str(repo),
            "--artifacts-root",
            str(artifacts),
            "--project-id",
            "cli-project",
            "--goal",
            "decompose this repository into responsibility-bearing components",
            "--non-goal",
            "do not treat file buckets as final components",
            "--llm-mode",
            "fixture",
            "--overwrite",
        ],
        cwd=Path.cwd(),
    )
    summary = json.loads(proc.stdout)

    assert summary["passed"] is True
    assert Path(summary["manifest_path"]).exists()
    assert Path(summary["gate_report_path"]).exists()


def test_snapshot_cli_returns_one_when_gate_fails_but_writes_diagnostics(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _write_repo(repo)
    artifacts = tmp_path / "artifacts"
    bad_output = tmp_path / "bad.json"
    bad_output.write_text(
        json.dumps(
            {
                "model_id": "bad-live-shaped-output",
                "components": [
                    {
                        "id": "component.misc",
                        "name": "Misc",
                        "responsibility": "Everything.",
                        "owned_node_ids": [],
                        "provenance_refs": [],
                        "contract_ids": [],
                        "check_ids": [],
                        "verification_gap_ids": [],
                    }
                ],
                "contracts": [],
                "cross_cutting_concerns": [],
                "observable_checks": [],
                "verification_gaps": [],
                "near_neighbor_alternatives": [],
                "held_out_probes": [],
            }
        ),
        encoding="utf-8",
    )

    proc = _run(
        [
            sys.executable,
            "-m",
            "arena.project_model_cli",
            "snapshot",
            "--project",
            str(repo),
            "--artifacts-root",
            str(artifacts),
            "--project-id",
            "cli-project",
            "--llm-mode",
            "recorded",
            "--model-output",
            str(bad_output),
            "--overwrite",
        ],
        cwd=Path.cwd(),
        check=False,
    )
    summary = json.loads(proc.stdout)

    assert proc.returncode == 1
    assert summary["passed"] is False
    assert Path(summary["gate_report_path"]).exists()


def test_snapshot_cli_refuses_live_mode_without_explicit_live_flag(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _write_repo(repo)
    proc = _run(
        [
            sys.executable,
            "-m",
            "arena.project_model_cli",
            "snapshot",
            "--project",
            str(repo),
            "--artifacts-root",
            str(tmp_path / "artifacts"),
            "--llm-mode",
            "live",
        ],
        cwd=Path.cwd(),
        check=False,
    )

    assert proc.returncode == 2
    assert "--allow-live" in proc.stderr


def test_gate_and_graph_cli(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _write_repo(repo)
    artifacts = tmp_path / "artifacts"
    snapshot_proc = _run(
        [sys.executable, "-m", "arena.project_model_cli", "snapshot", "--project", str(repo), "--artifacts-root", str(artifacts), "--project-id", "cli-project", "--llm-mode", "fixture", "--overwrite"],
        cwd=Path.cwd(),
    )
    summary = json.loads(snapshot_proc.stdout)
    gate_proc = _run([sys.executable, "-m", "arena.project_model_cli", "gate", "--snapshot", summary["manifest_path"]], cwd=Path.cwd())
    graph_path = tmp_path / "graph.json"
    graph_proc = _run([sys.executable, "-m", "arena.project_model_cli", "graph", "--project", str(repo), "--output", str(graph_path)], cwd=Path.cwd())

    assert json.loads(gate_proc.stdout)["passed"] is True
    assert json.loads(graph_proc.stdout)["node_count"] > 0
    assert graph_path.exists()
