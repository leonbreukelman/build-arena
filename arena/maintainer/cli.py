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
