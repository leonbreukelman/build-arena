"""CLI tests for dry-run maintainer delegation bundle preparation."""

from __future__ import annotations

import json
import stat
import subprocess
import sys
from hashlib import sha256
from pathlib import Path
from typing import Any


def _packet(**overrides: object) -> dict[str, object]:
    data: dict[str, object] = {
        "objective": "Prepare a dry-run delegated coding task.",
        "mode": "dry_run",
        "allowed_paths": ["arena/maintainer", "tests/test_maintainer_cli.py"],
        "forbidden_paths": ["scorer", "verifier", "schema", "arena/generated"],
        "required_reads": ["AGENTS.md", "README.md", "pyproject.toml"],
        "required_commands": ["uv run pytest tests -q", "uv run ruff check .", "uv run pyright"],
        "stop_conditions": ["stop on live execution request"],
    }
    data.update(overrides)
    return data


def _write_packet(tmp_path: Path, data: dict[str, object] | str) -> Path:
    path = tmp_path / "packet.json"
    if isinstance(data, str):
        path.write_text(data, encoding="utf-8")
    else:
        path.write_text(json.dumps(data), encoding="utf-8")
    return path


def _run_prepare(packet: Path, out: Path, *extra: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "arena.maintainer.cli",
            "prepare",
            "--packet",
            str(packet),
            "--out",
            str(out),
            *extra,
        ],
        check=False,
        capture_output=True,
        text=True,
    )


def _load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def test_prepare_cli_writes_allowed_dry_run_bundle(tmp_path: Path) -> None:
    out = tmp_path / "bundle"
    result = _run_prepare(_write_packet(tmp_path, _packet()), out)

    assert result.returncode == 0, result.stderr
    assert "bundle written" in result.stdout
    assert "policy allowed: True" in result.stdout
    expected = {
        "packet.json",
        "policy-result.json",
        "task.md",
        "openshell-policy.yaml",
        "runner-command.sh",
        "manifest.json",
    }
    assert {path.name for path in out.iterdir()} == expected

    policy = _load(out / "policy-result.json")
    assert policy == {
        "allowed": True,
        "execution": "not_run",
        "reasons": [],
        "runtime": "openshell_planned",
        "verification_owner": "hermes",
        "verification_status": "not_verified",
    }

    manifest = _load(out / "manifest.json")
    assert manifest["schemaVersion"] == "maintainer-delegation-bundle/v0"
    assert manifest["hashAlgorithm"] == "sha256"
    assert manifest["hashScope"] == "on-disk artifact bytes excluding manifest.json"
    assert manifest["policyAllowed"] is True
    assert manifest["execution"] == "not_run"
    assert manifest["runtime"] == "openshell_planned"
    assert manifest["verificationOwner"] == "hermes"
    assert manifest["verificationStatus"] == "not_verified"
    assert {item["path"] for item in manifest["artifacts"]} == expected - {"manifest.json"}
    for item in manifest["artifacts"]:
        artifact = out / item["path"]
        assert item["sha256"] == sha256(artifact.read_bytes()).hexdigest()
        assert not artifact.stat().st_mode & stat.S_IXUSR

    task = (out / "task.md").read_text(encoding="utf-8")
    assert "# Build Arena maintainer delegation task" in task
    assert "Do not execute OpenHands" in task

    policy_yaml = (out / "openshell-policy.yaml").read_text(encoding="utf-8")
    assert "GENERATED DRAFT" in policy_yaml
    assert "execute_openhands: false" in policy_yaml
    assert "allow_github: false" in policy_yaml

    runner = out / "runner-command.sh"
    runner_text = runner.read_text(encoding="utf-8")
    assert runner_text.startswith("# GENERATED -- DO NOT EXECUTE")
    assert not runner_text.splitlines()[0].startswith("#!")
    assert "DRY RUN ONLY" in runner_text
    assert not runner.stat().st_mode & stat.S_IXUSR


def test_prepare_cli_writes_rejected_bundle_and_returns_policy_code(tmp_path: Path) -> None:
    out = tmp_path / "bundle"
    result = _run_prepare(
        _write_packet(
            tmp_path,
            _packet(objective="Use worker to target apply/promote a patch.", allowed_paths=["scorer"]),
        ),
        out,
    )

    assert result.returncode == 2
    assert "policy rejected packet" in result.stderr
    assert "target apply/promote" in result.stderr
    assert "allowed write path overlaps forbidden path" in result.stderr
    assert _load(out / "policy-result.json")["allowed"] is False
    assert _load(out / "manifest.json")["policyAllowed"] is False


def test_prepare_cli_rejects_invalid_json_without_writing_bundle(tmp_path: Path) -> None:
    out = tmp_path / "bundle"
    result = _run_prepare(_write_packet(tmp_path, "{"), out)

    assert result.returncode == 1
    assert "packet is not valid JSON" in result.stderr
    assert not out.exists()


def test_prepare_cli_rejects_invalid_packet_without_writing_bundle(tmp_path: Path) -> None:
    out = tmp_path / "bundle"
    result = _run_prepare(_write_packet(tmp_path, _packet(mode="live")), out)

    assert result.returncode == 1
    assert "packet failed validation" in result.stderr
    assert not out.exists()


def test_prepare_cli_refuses_to_overwrite_existing_bundle_without_force(tmp_path: Path) -> None:
    packet = _write_packet(tmp_path, _packet())
    out = tmp_path / "bundle"
    assert _run_prepare(packet, out).returncode == 0

    result = _run_prepare(packet, out)

    assert result.returncode == 1
    assert "pass --force" in result.stderr


def test_prepare_cli_force_overwrites_existing_bundle(tmp_path: Path) -> None:
    packet = _write_packet(tmp_path, _packet(objective="first objective"))
    out = tmp_path / "bundle"
    assert _run_prepare(packet, out).returncode == 0

    packet.write_text(json.dumps(_packet(objective="second objective")), encoding="utf-8")
    result = _run_prepare(packet, out, "--force")

    assert result.returncode == 0
    assert "second objective" in (out / "task.md").read_text(encoding="utf-8")
    assert "first objective" not in (out / "task.md").read_text(encoding="utf-8")


def test_prepare_cli_refuses_unknown_files_even_with_force(tmp_path: Path) -> None:
    packet = _write_packet(tmp_path, _packet())
    out = tmp_path / "bundle"
    out.mkdir()
    (out / "keep.txt").write_text("do not delete", encoding="utf-8")

    result = _run_prepare(packet, out, "--force")

    assert result.returncode == 1
    assert "non-bundle files" in result.stderr
    assert (out / "keep.txt").read_text(encoding="utf-8") == "do not delete"


def test_prepare_cli_usage_errors_do_not_collide_with_policy_rejection(tmp_path: Path) -> None:
    result = subprocess.run(
        [sys.executable, "-m", "arena.maintainer.cli", "prepare", "--out", str(tmp_path / "out")],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    assert "required" in result.stderr


def test_prepare_cli_write_error_precedes_policy_rejection(tmp_path: Path) -> None:
    packet = _write_packet(
        tmp_path,
        _packet(objective="Use worker to target apply/promote a patch.", allowed_paths=["scorer"]),
    )
    out = tmp_path / "bundle"
    out.mkdir()
    (out / "keep.txt").write_text("do not delete", encoding="utf-8")

    result = _run_prepare(packet, out)

    assert result.returncode == 1
    assert "non-bundle files" in result.stderr
    assert "policy rejected packet" not in result.stderr


def test_prepare_cli_refuses_output_path_that_is_file(tmp_path: Path) -> None:
    packet = _write_packet(tmp_path, _packet())
    out = tmp_path / "bundle"
    out.write_text("not a directory", encoding="utf-8")

    result = _run_prepare(packet, out)

    assert result.returncode == 1
    assert "not a directory" in result.stderr


def test_prepare_cli_outputs_are_deterministic_with_force(tmp_path: Path) -> None:
    packet = _write_packet(tmp_path, _packet(objective="unicode snowman ☃"))
    out = tmp_path / "bundle"

    assert _run_prepare(packet, out).returncode == 0
    first = {path.name: path.read_bytes() for path in sorted(out.iterdir())}
    assert _run_prepare(packet, out, "--force").returncode == 0
    second = {path.name: path.read_bytes() for path in sorted(out.iterdir())}

    assert first == second
    assert "unicode snowman ☃" in (out / "task.md").read_text(encoding="utf-8")


def test_prepare_cli_rejects_missing_packet_path_without_writing_bundle(tmp_path: Path) -> None:
    out = tmp_path / "bundle"
    result = _run_prepare(tmp_path / "missing.json", out)

    assert result.returncode == 1
    assert "cannot read packet" in result.stderr
    assert not out.exists()


def test_prepare_cli_rejects_unknown_packet_fields_without_writing_bundle(tmp_path: Path) -> None:
    out = tmp_path / "bundle"
    packet = _packet(extra_field="not allowed")

    result = _run_prepare(_write_packet(tmp_path, packet), out)

    assert result.returncode == 1
    assert "packet failed validation" in result.stderr
    assert not out.exists()
