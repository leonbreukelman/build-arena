# Maintainer CLI final review packet

## Verification after Opus patches

- Focused + full + lint + typecheck command: `uv run pytest tests/test_maintainer_cli.py tests/test_maintainer_task_packet.py tests/test_maintainer_policy.py tests/test_openshell_policy_render.py -q && uv run pytest tests -q && uv run ruff check . && uv run pyright` -> all passed.

- Manual CLI smoke: `uv run python -m arena.maintainer.cli prepare --packet <tmp>/packet.json --out <tmp>/bundle` -> exit 0, no runpy warning, wrote 6 artifacts, policy allowed true, manifest hashAlgorithm sha256, runner mode 420 decimal (0644).


## Files


### arena/maintainer/__init__.py

```text
"""Dry-run maintainer delegation packet utilities."""

from __future__ import annotations

from arena.maintainer.openshell_policy import render_openshell_policy
from arena.maintainer.policy import PolicyResult, evaluate_task_packet
from arena.maintainer.runner_command import render_runner_command
from arena.maintainer.task_packet import TaskPacket, render_task_markdown

__all__ = [
    "PolicyResult",
    "TaskPacket",
    "evaluate_task_packet",
    "render_openshell_policy",
    "render_runner_command",
    "render_task_markdown",
]

```


### arena/maintainer/cli.py

```text
"""CLI for preparing dry-run maintainer delegation bundles."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any, NoReturn

from pydantic import ValidationError

from arena.maintainer.openshell_policy import render_openshell_policy
from arena.maintainer.policy import PolicyResult, evaluate_task_packet
from arena.maintainer.runner_command import render_runner_command
from arena.maintainer.task_packet import TaskPacket, render_task_markdown

BUNDLE_SCHEMA_VERSION = "maintainer-delegation-bundle/v0"
PREPARE_SUCCESS = 0
PREPARE_ERROR = 1
PREPARE_POLICY_REJECTED = 2
_ARTIFACT_NAMES = (
    "packet.json",
    "policy-result.json",
    "task.md",
    "openshell-policy.yaml",
    "runner-command.sh",
    "manifest.json",
)


class PrepareError(Exception):
    """Raised when a dry-run bundle cannot be prepared."""


class PolicyRejected(Exception):
    """Raised after writing an auditable bundle for a policy-rejected packet."""

    def __init__(self, out_dir: Path, result: PolicyResult) -> None:
        self.out_dir = out_dir
        self.result = result
        super().__init__("; ".join(result.reasons) or "policy rejected packet")


class MaintainerArgumentParser(argparse.ArgumentParser):
    """ArgumentParser that maps CLI usage errors to the generic prepare error code.

    Plain argparse exits 2 for usage errors; this CLI reserves code 2 for valid packets rejected by
    Hermes semantic policy, so usage failures exit 1 instead.
    """

    def error(self, message: str) -> NoReturn:  # pragma: no cover - exercised through subprocess tests
        self.print_usage(sys.stderr)
        self.exit(PREPARE_ERROR, f"{self.prog}: error: {message}\n")


def prepare_bundle(packet_path: str | Path, out_dir: str | Path, *, force: bool = False) -> PolicyResult:
    """Validate a packet and write a deterministic dry-run delegation bundle.

    Returns the policy result. A rejected packet still writes an auditable bundle and raises
    ``PolicyRejected`` so callers can return a distinct exit code without losing evidence. Write and
    output-directory safety failures happen before bundle installation and return ``PrepareError``;
    those failures take precedence over policy rejection.
    """
    packet = load_packet(packet_path)
    result = evaluate_task_packet(packet)
    destination = Path(out_dir)
    _validate_output_dir(destination, force=force)
    _write_bundle_atomically(destination, packet, result, force=force)
    if not result.allowed:
        raise PolicyRejected(destination, result)
    return result


def load_packet(path: str | Path) -> TaskPacket:
    """Load and validate a JSON task packet."""
    packet_path = Path(path)
    try:
        raw = packet_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise PrepareError(f"cannot read packet: {exc}") from exc
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise PrepareError(f"packet is not valid JSON: {exc}") from exc
    try:
        return TaskPacket.model_validate(data)
    except ValidationError as exc:
        raise PrepareError(f"packet failed validation: {exc}") from exc


def _validate_output_dir(out_dir: Path, *, force: bool) -> None:
    if out_dir.exists() and not out_dir.is_dir():
        raise PrepareError(f"output path exists and is not a directory: {out_dir}")
    if not out_dir.exists():
        return

    entries = sorted(path.name for path in out_dir.iterdir())
    if not entries:
        return
    unknown = [name for name in entries if name not in _ARTIFACT_NAMES]
    if unknown:
        raise PrepareError(
            f"output directory contains non-bundle files; refusing to overwrite: {', '.join(unknown)}"
        )
    if not force:
        raise PrepareError(f"output directory already contains a bundle; pass --force: {out_dir}")


def _write_bundle_atomically(
    out_dir: Path, packet: TaskPacket, result: PolicyResult, *, force: bool
) -> None:
    parent = out_dir.parent
    parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=f".{out_dir.name}.", dir=parent) as tmp_name:
        tmp_dir = Path(tmp_name)
        artifact_paths = _write_bundle_files(tmp_dir, packet, result)
        _write_manifest(tmp_dir, packet, result, artifact_paths)
        _install_bundle(tmp_dir, out_dir, force=force)


def _install_bundle(tmp_dir: Path, out_dir: Path, *, force: bool) -> None:
    if out_dir.exists():
        entries = sorted(path.name for path in out_dir.iterdir())
        unknown = [name for name in entries if name not in _ARTIFACT_NAMES]
        if unknown:
            raise PrepareError(
                "output directory changed during write and now contains non-bundle files; "
                f"refusing to overwrite: {', '.join(unknown)}"
            )
        if entries and not force:
            raise PrepareError(f"output directory already contains a bundle; pass --force: {out_dir}")
        shutil.rmtree(out_dir)
    tmp_dir.rename(out_dir)


def _write_bundle_files(out_dir: Path, packet: TaskPacket, result: PolicyResult) -> list[Path]:
    rendered: dict[str, str] = {
        "packet.json": _json_text(packet.model_dump(mode="json")),
        "policy-result.json": _json_text(result.model_dump(mode="json")),
        "task.md": render_task_markdown(packet),
        "openshell-policy.yaml": render_openshell_policy(packet),
        "runner-command.sh": render_runner_command(packet),
    }
    written: list[Path] = []
    for name, content in rendered.items():
        path = out_dir / name
        path.write_text(content, encoding="utf-8")
        path.chmod(0o644)
        written.append(path)
    return written


def _write_manifest(
    out_dir: Path, packet: TaskPacket, result: PolicyResult, artifact_paths: list[Path]
) -> None:
    manifest_path = out_dir / "manifest.json"
    artifacts = [_artifact_record(path, out_dir) for path in sorted(artifact_paths)]
    manifest: dict[str, Any] = {
        "schemaVersion": BUNDLE_SCHEMA_VERSION,
        "hashAlgorithm": "sha256",
        "hashScope": "on-disk artifact bytes excluding manifest.json",
        "packetSchemaVersion": packet.schema_version,
        "execution": result.execution,
        "runtime": result.runtime,
        "verificationOwner": result.verification_owner,
        "verificationStatus": result.verification_status,
        "policyAllowed": result.allowed,
        "policyReasons": list(result.reasons),
        "artifacts": artifacts,
    }
    manifest_path.write_text(_json_text(manifest), encoding="utf-8")
    manifest_path.chmod(0o644)


def _artifact_record(path: Path, out_dir: Path) -> dict[str, str]:
    content = path.read_bytes()
    return {
        "path": path.relative_to(out_dir).as_posix(),
        "sha256": hashlib.sha256(content).hexdigest(),
    }


def _json_text(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def _build_parser() -> argparse.ArgumentParser:
    parser = MaintainerArgumentParser(prog="python -m arena.maintainer.cli")
    subcommands = parser.add_subparsers(
        dest="command", required=True, parser_class=MaintainerArgumentParser
    )
    prepare = subcommands.add_parser(
        "prepare",
        help="prepare a dry-run maintainer bundle",
    )
    prepare.add_argument("--packet", required=True, help="path to task packet JSON")
    prepare.add_argument("--out", required=True, help="directory to write bundle artifacts")
    prepare.add_argument(
        "--force",
        action="store_true",
        help="overwrite an existing bundle directory containing only known bundle artifacts",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    if args.command == "prepare":
        try:
            result = prepare_bundle(args.packet, args.out, force=args.force)
        except PolicyRejected as exc:
            print(f"policy rejected packet; bundle written: {exc.out_dir}", file=sys.stderr)
            for reason in exc.result.reasons:
                print(f"- {reason}", file=sys.stderr)
            return PREPARE_POLICY_REJECTED
        except PrepareError as exc:
            print(f"maintainer prepare failed: {exc}", file=sys.stderr)
            return PREPARE_ERROR
        print(f"bundle written: {Path(args.out)}")
        print(f"policy allowed: {result.allowed}")
        return PREPARE_SUCCESS
    parser.error(f"unknown command: {args.command}")
    return PREPARE_ERROR


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())

```


### arena/maintainer/runner_command.py

```text
"""Render the dry-run runner command artifact for future delegated workers."""

from __future__ import annotations

from arena.maintainer.task_packet import TaskPacket


def render_runner_command(packet: TaskPacket) -> str:
    """Render ``runner-command.sh`` as a non-executing dry-run script."""
    commands = "\n".join(f"# required verification: {command}" for command in packet.required_commands)
    return (
        "# GENERATED -- DO NOT EXECUTE. Dry-run command preview only.\n"
        "# No OpenHands, OpenShell sandbox, GitHub call, push, merge, apply, or promote.\n"
        "#!/usr/bin/env sh\n"
        "set -eu\n"
        "echo 'DRY RUN ONLY: no OpenHands execution, no OpenShell sandbox, no GitHub call.'\n"
        "echo 'Hermes verification owner: hermes; execution: not_run; runtime: openshell_planned.'\n"
        f"echo 'Task objective: {_single_quote_shell_text(packet.objective)}'\n"
        f"{commands}\n"
    )


def _single_quote_shell_text(value: str) -> str:
    return value.replace("'", "'\"'\"'")

```


### tests/test_maintainer_cli.py

```text
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

```


### tests/test_openshell_policy_render.py

```text
"""Tests for generated OpenShell policy and runner dry-run artifacts."""

from __future__ import annotations

import yaml

from arena.maintainer.openshell_policy import render_openshell_policy
from arena.maintainer.runner_command import render_runner_command
from arena.maintainer.task_packet import TaskPacket


def _packet() -> TaskPacket:
    return TaskPacket.model_validate(
        {
            "objective": "Prepare a dry-run delegated coding task.",
            "mode": "dry_run",
            "allowed_paths": ["arena/maintainer", "tests/test_openshell_policy_render.py"],
            "forbidden_paths": ["scorer", "verifier", "schema", "arena/generated"],
            "required_reads": ["AGENTS.md", "README.md", "pyproject.toml"],
            "required_commands": ["uv run pytest tests -q", "uv run ruff check .", "uv run pyright"],
            "stop_conditions": ["stop on live execution request"],
        }
    )


def test_openshell_policy_stub_includes_required_intents_and_draft_comments() -> None:
    text = render_openshell_policy(_packet())

    assert "GENERATED DRAFT" in text
    assert "NOT APPLIED" in text
    assert "Hermes policy is semantic authorization" in text
    assert "OpenShell is the future runtime enforcement layer" in text
    assert "read_intent" in text
    assert "write_intent" in text
    assert "forbidden_path_intent" in text
    assert "egress_intent" in text
    assert "routing_intent" in text
    assert "process_restrictions" in text

    data = yaml.safe_load(text)
    assert data["status"] == "generated_draft_not_applied"
    assert data["runtime"] == {"kind": "openshell_planned", "execution": "not_run"}
    assert data["filesystem"]["write_intent"] == [
        "arena/maintainer",
        "tests/test_openshell_policy_render.py",
    ]
    assert data["network"]["egress_intent"] == "none"
    assert data["inference"]["routing_intent"] == (
        "delegated_worker_no_live_provider_call_in_this_slice"
    )
    assert data["process_restrictions"]["dry_run_only"] is True
    assert data["process_restrictions"]["execute_openhands"] is False
    assert data["process_restrictions"]["target_apply_or_promote"] is False
    assert data["verification"] == {"owner": "hermes", "status": "not_verified"}


def test_runner_command_is_dry_run_only() -> None:
    script = render_runner_command(_packet())

    assert script.startswith("# GENERATED -- DO NOT EXECUTE")
    assert "#!/usr/bin/env sh\n" in script
    assert "DRY RUN ONLY" in script
    assert "no OpenHands execution" in script
    assert "no OpenShell sandbox" in script
    assert "no GitHub call" in script
    assert "execution: not_run" in script
    assert "runtime: openshell_planned" in script
    assert "# required verification: uv run pyright" in script

```


### docs/specs/2026-07-02-hermes-openshell-delegation-packet.md

```text
# Hermes / OpenShell delegation packet dry-run

Date: 2026-07-02
Status: smallest first step, dry-run only

## Purpose

This slice defines the first maintainer-side packet between Hermes and a future runtime enforcement layer.

Architecture boundary:

- Hermes is the maintainer brain and policy router.
- OpenShell is the future runtime enforcement layer.
- OpenHands/Codex are delegated coding workers.
- This implementation only renders dry-run artifacts. It does not execute OpenHands, does not create a live OpenShell sandbox, does not call GitHub, and does not apply, promote, push, or merge code.

## Requirements implemented

1. Define a Pydantic `TaskPacket` model for delegated maintainer work.
2. Validate objective, mode, allowed paths, forbidden paths, required reads, required commands, and stop conditions.
3. Restrict this first packet mode to `dry_run`.
4. Reject semantic requests for target apply/promote, auto-merge, git push, and broad live autonomy.
5. Reject allowed write path intent that overlaps forbidden write path intent, including protected Build Arena surfaces such as `scorer/`, `verifier/`, `schema/`, `arena/generated/`, and `.arena/scorer.lock.toml`.
6. Render `task.md` for a delegated worker.
7. Render `openshell-policy.yaml` as a future runtime policy artifact.
8. Render `runner-command.sh` as a dry-run command artifact only.
9. Return policy status fields:
   - `execution: not_run`
   - `runtime: openshell_planned`
   - `verification_owner: hermes`
   - `verification_status: not_verified`
10. Cover allowed task, forbidden path overlap, target apply/promote phrase, git push phrase, broad autonomy phrase, and generated OpenShell policy stub in tests.
11. Provide `python -m arena.maintainer.cli prepare --packet <packet.json> --out <bundle-dir>` to generate a dry-run bundle from the terminal.
12. Return exit code `0` for valid policy-allowed bundles, `2` for valid policy-rejected bundles, and `1` for invalid input, usage, or write-safety failures.
13. Make write-safety failures take precedence over policy rejection. The CLI refuses to overwrite existing bundles unless `--force` is passed, and refuses unknown files even with `--force`.
14. Render deterministic bundle artifacts with a `manifest.json` using `sha256` over on-disk artifact bytes excluding `manifest.json` itself.

## Packet model

`arena.maintainer.task_packet.TaskPacket` is a strict Pydantic model with these fields:

- `schema_version`: fixed to `maintainer-task-packet/v0`.
- `objective`: non-blank task objective.
- `mode`: fixed to `dry_run`.
- `allowed_paths`: non-empty repository-relative write-intent paths.
- `forbidden_paths`: repository-relative path intent that must not be written.
- `required_reads`: non-empty repository-relative read prerequisites.
- `required_commands`: non-empty verification commands Hermes expects to own.
- `stop_conditions`: non-empty conditions that halt the delegated task.

Paths are repository-relative and may not traverse upward. Required reads cannot be listed as forbidden paths.

## Policy split

Hermes policy is semantic authorization. It decides whether the task objective, command intent, stop conditions, and write-intent paths fit Build Arena's propose-only maintainer boundaries.

OpenShell policy is runtime enforcement. In this slice, Build Arena only renders a generated draft `openshell-policy.yaml` with intended read/write paths, forbidden paths, network egress, inference routing, and process restrictions. The draft is not applied and does not create a sandbox.

## Rendered artifacts

- `render_task_markdown(packet)` renders a deterministic `task.md` body for a delegated worker.
- `render_openshell_policy(packet)` renders a commented `openshell-policy.yaml` draft with filesystem, network, inference, process, and verification intent.
- `render_runner_command(packet)` renders a non-executable `runner-command.sh` dry-run preview marked `GENERATED -- DO NOT EXECUTE`.

## CLI bundle workflow

The terminal entry point is:

```sh
uv run python -m arena.maintainer.cli prepare --packet packet.json --out .arena/maintainer-runs/example
```

The command validates the packet, evaluates Hermes semantic policy, and writes:

- `packet.json`
- `policy-result.json`
- `task.md`
- `openshell-policy.yaml`
- `runner-command.sh`
- `manifest.json`

The CLI never runs the generated command, never executes OpenHands, never creates an OpenShell sandbox, never calls GitHub, and never applies, promotes, pushes, or merges. `runner-command.sh` is intentionally non-executable so the bundle cannot be mistaken for an execution instruction.

If a packet is valid but policy-rejected, the CLI still writes the auditable bundle and exits `2`. If the output path is unsafe or unwritable, the CLI exits `1` and does not install a partial bundle. Usage errors also exit `1` so exit `2` is reserved for semantic policy rejection.

## Non-goals

- No SWE-agent integration.
- No OpenHands execution.
- No live OpenShell sandbox.
- No GitHub API calls.
- No push, merge, apply, promote, or target repository mutation.
- No claim that OpenShell enforcement exists yet.

```
