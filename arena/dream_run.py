"""``dream run <repo>`` -- orchestrate the advisory tier-3 dream lane.

This is a thin, fail-closed driver parallel to the proposal lane. It wires
existing/new stage CLIs through subprocess boundaries and preserves the workdir on
any failed run. The capability map is auto-generated and used without a mid-run
human review gate; the lane runs end-to-end to the emitted output, which carries
an honest provenance label when the map is operator-unreviewed. Tests inject
stages to exercise the full offline path.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from arena.llm_adapter import resolve_api_key_with_source

EXIT_OK = 0
EXIT_STAGE_FAILURE = 1
EXIT_NO_DREAM = 2
EXIT_USAGE = 3

_REPO_ROOT = Path(__file__).resolve().parents[1]
_DECOMPOSE_MODULE = "arena.project_model_cli"
_INTAKE_MODULE = "arena.project_intake_scorecard"
_CAPABILITY_MODULE = "arena.capability_lift"
_GENERATE_MODULE = "arena.dream_generate"
_RESEARCH_MODULE = "arena.dream_research"
_GATE_MODULE = "arena.dream_gate"
_EMIT_MODULE = "arena.dream_emit"


@dataclass(frozen=True, slots=True)
class StageResult:
    returncode: int
    stdout: str = ""
    stderr: str = ""


StageRunner = Callable[[str, list[str], dict[str, str]], StageResult]
GitRunner = Callable[[list[str]], None]


@dataclass(slots=True)
class RunConfig:
    repo: str
    output: Path
    profile: str = "new-project"
    decompose_live: bool = False
    live_model: str | None = None
    live_api_key_env: str = "XAI_API_KEY"
    live_provider: str = "xai"
    live_base_url: str | None = None
    workdir: Path | None = None
    keep_workdir: bool = False
    capability_map: Path | None = None


class DreamRunError(Exception):
    """Terminal run outcome with a process exit code."""

    def __init__(self, message: str, exit_code: int, *, already_reported: bool = False) -> None:
        super().__init__(message)
        self.exit_code = exit_code
        self.already_reported = already_reported


def _subprocess_stage(module: str, args: list[str], env: dict[str, str]) -> StageResult:
    proc = subprocess.run(
        [sys.executable, "-m", module, *args],
        cwd=_REPO_ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    return StageResult(proc.returncode, stdout=proc.stdout, stderr=proc.stderr)


def _run_git(args: list[str]) -> None:
    try:
        subprocess.run(["git", *args], check=True, capture_output=True, text=True)
    except FileNotFoundError as exc:
        raise DreamRunError("git is not available on PATH", EXIT_STAGE_FAILURE) from exc
    except subprocess.CalledProcessError as exc:
        detail = (exc.stderr or "").strip() or f"git exited {exc.returncode}"
        raise DreamRunError(f"git clone failed: {detail}", EXIT_STAGE_FAILURE) from exc


def _looks_like_git_url(value: str) -> bool:
    lowered = value.lower()
    if lowered.endswith(".git") or lowered.startswith(("http://", "https://", "git://", "ssh://")):
        return True
    head = value.split("/", 1)[0]
    return "@" in head and ":" in head


def resolve_target(repo: str, workdir: Path, git_runner: GitRunner) -> Path:
    local = Path(repo).expanduser()
    if local.is_dir():
        return local.resolve()
    if _looks_like_git_url(repo):
        dest = workdir / "target"
        git_runner(["clone", "--depth", "1", repo, str(dest)])
        return dest.resolve()
    raise DreamRunError(f"repo must be an existing local directory or a git URL: {repo!r}", EXIT_USAGE)


def _subprocess_env(config: RunConfig) -> dict[str, str]:
    env = dict(os.environ)
    existing = env.get("PYTHONPATH", "")
    parts = [str(_REPO_ROOT), *(part for part in existing.split(os.pathsep) if part)]
    env["PYTHONPATH"] = os.pathsep.join(parts)
    env["BUILD_ARENA_LLM_API_KEY_ENV"] = config.live_api_key_env
    if config.live_model:
        env["BUILD_ARENA_LLM_MODEL"] = config.live_model
    if config.live_base_url:
        env["BUILD_ARENA_LLM_BASE_URL"] = config.live_base_url
    return env


def _preflight(config: RunConfig) -> None:
    if not config.live_model:
        raise DreamRunError("--live-model is required: generation and research are live model stages", EXIT_USAGE)
    try:
        resolve_api_key_with_source(config.live_api_key_env)
    except ValueError as exc:
        raise DreamRunError(
            f"{exc} (set the key, or choose another env var with --live-api-key-env)", EXIT_USAGE
        ) from exc


def _derive_project_id(target: Path) -> str:
    return target.name or "project"


def _glob_manifest(snap_root: Path) -> Path:
    matches = sorted(snap_root.glob("*/manifest.json"))
    if len(matches) != 1:
        raise DreamRunError(
            f"expected exactly one snapshot manifest under {snap_root}, found {len(matches)}",
            EXIT_STAGE_FAILURE,
        )
    return matches[0]


def _resolve_model_v1(manifest_path: Path) -> Path:
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise DreamRunError(f"cannot read snapshot manifest: {exc}", EXIT_STAGE_FAILURE) from exc
    rel = manifest.get("project_model_primary_path") or manifest.get("project_model_v1_path")
    if not isinstance(rel, str) or not rel:
        raise DreamRunError("snapshot manifest does not record a project-model v1 path", EXIT_STAGE_FAILURE)
    resolved = (manifest_path.parent / rel).resolve()
    if not resolved.is_file():
        raise DreamRunError(f"project model v1 artifact missing at {resolved}", EXIT_STAGE_FAILURE)
    return resolved


def _fail_stage(stage: str, result: StageResult, workdir: Path) -> DreamRunError:
    detail = (result.stderr or result.stdout or "").strip()
    suffix = f": {detail}" if detail else ""
    return DreamRunError(
        f"stage '{stage}' failed (exit {result.returncode}){suffix}. Workdir preserved at {workdir}",
        EXIT_STAGE_FAILURE,
    )


def _decompose_args(config: RunConfig, target: Path, snap_root: Path) -> list[str]:
    args = [
        "snapshot",
        "--project",
        str(target),
        "--artifacts-root",
        str(snap_root),
        "--project-id",
        _derive_project_id(target),
        "--goal",
        "build-arena dream run",
        "--llm-mode",
        "live" if config.decompose_live else "fixture",
    ]
    if config.decompose_live:
        args += ["--allow-live", "--live-provider", config.live_provider, "--live-api-key-env", config.live_api_key_env]
        if config.live_model:
            args += ["--live-model", config.live_model]
        if config.live_base_url:
            args += ["--live-base-url", config.live_base_url]
    return args


def _live_stage_flags(config: RunConfig) -> list[str]:
    flags = ["--live-model", str(config.live_model), "--live-provider", config.live_provider, "--live-api-key-env", config.live_api_key_env]
    if config.live_base_url:
        flags += ["--live-base-url", config.live_base_url]
    return flags


def _dream_count(path: Path) -> int:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return 0
    dreams = payload.get("dreams") if isinstance(payload, dict) else None
    return len(dreams) if isinstance(dreams, list) else 0


def _execute_stages(config: RunConfig, target: Path, workdir: Path, stage_runner: StageRunner, env: dict[str, str]) -> int:
    snap_root = workdir / "snap"
    decompose = stage_runner(_DECOMPOSE_MODULE, _decompose_args(config, target, snap_root), env)
    if decompose.returncode != 0:
        raise _fail_stage("decompose", decompose, workdir)
    model_v1 = _resolve_model_v1(_glob_manifest(snap_root))

    scorecard = workdir / "scorecard.json"
    intake = stage_runner(
        _INTAKE_MODULE,
        ["--project", str(target), "--snapshot", str(model_v1), "--profile", config.profile, "--output", str(scorecard)],
        env,
    )
    if intake.returncode != 0:
        raise _fail_stage("intake", intake, workdir)
    if not scorecard.is_file():
        raise _fail_stage("intake", StageResult(0, stderr="scorecard not written"), workdir)

    if config.capability_map is None:
        capability_map = workdir / "capability-map.json"
        lift = stage_runner(
            _CAPABILITY_MODULE,
            ["--project-model", str(model_v1), "--output", str(capability_map)],
            env,
        )
        if lift.returncode != 0:
            raise _fail_stage("capability_lift", lift, workdir)
        if not capability_map.is_file():
            raise _fail_stage("capability_lift", StageResult(0, stderr="capability map not written"), workdir)
    else:
        capability_map = config.capability_map.expanduser().resolve()
        if not capability_map.is_file():
            raise DreamRunError(f"capability map not found: {capability_map}", EXIT_USAGE)

    raw_dreams = workdir / "raw-dreams.json"
    generate = stage_runner(
        _GENERATE_MODULE,
        [
            "--project-model",
            str(model_v1),
            "--capability-map",
            str(capability_map),
            "--scorecard",
            str(scorecard),
            "--output",
            str(raw_dreams),
            *_live_stage_flags(config),
        ],
        env,
    )
    if generate.returncode != 0:
        raise _fail_stage("dream_generate", generate, workdir)
    if not raw_dreams.is_file():
        raise _fail_stage("dream_generate", StageResult(0, stderr="raw dreams not written"), workdir)

    researched_dreams = workdir / "researched-dreams.json"
    research = stage_runner(
        _RESEARCH_MODULE,
        [
            "--project-model",
            str(model_v1),
            "--capability-map",
            str(capability_map),
            "--dreams",
            str(raw_dreams),
            "--output",
            str(researched_dreams),
            *_live_stage_flags(config),
        ],
        env,
    )
    if research.returncode != 0:
        raise _fail_stage("dream_research", research, workdir)
    if not researched_dreams.is_file():
        raise _fail_stage("dream_research", StageResult(0, stderr="researched dreams not written"), workdir)

    gated_dreams = workdir / "gated-dreams.json"
    gate_trace = workdir / "dream-gate-trace.json"
    gate = stage_runner(
        _GATE_MODULE,
        [
            "--project-model",
            str(model_v1),
            "--capability-map",
            str(capability_map),
            "--dreams",
            str(researched_dreams),
            "--output",
            str(gated_dreams),
            "--trace",
            str(gate_trace),
        ],
        env,
    )
    if gate.returncode == EXIT_NO_DREAM or (gated_dreams.is_file() and _dream_count(gated_dreams) == 0):
        print(f"No dream survived the premise gate (see {gate_trace}).")
        raise DreamRunError("", EXIT_NO_DREAM, already_reported=True)
    if gate.returncode != 0:
        raise _fail_stage("dream_gate", gate, workdir)
    if not gated_dreams.is_file():
        raise _fail_stage("dream_gate", StageResult(0, stderr="gated dreams not written"), workdir)

    emit = stage_runner(_EMIT_MODULE, ["--dreams", str(gated_dreams), "--output", str(config.output)], env)
    if emit.returncode != 0:
        raise _fail_stage("dream_emit", emit, workdir)
    if not config.output.is_file():
        raise _fail_stage("dream_emit", StageResult(0, stderr="output file not written"), workdir)
    return EXIT_OK


def run(config: RunConfig, *, stage_runner: StageRunner = _subprocess_stage, git_runner: GitRunner = _run_git) -> int:
    _preflight(config)
    if config.workdir is not None:
        workdir = config.workdir.expanduser().resolve()
        workdir.mkdir(parents=True, exist_ok=True)
        is_temp = False
    else:
        workdir = Path(tempfile.mkdtemp(prefix="build-arena-dream-")).resolve()
        is_temp = True
    env = _subprocess_env(config)
    succeeded = False
    try:
        target = resolve_target(config.repo, workdir, git_runner)
        code = _execute_stages(config, target, workdir, stage_runner, env)
        succeeded = code == EXIT_OK
        if succeeded and config.keep_workdir:
            print(f"Intermediate artifacts kept at {workdir}", file=sys.stderr)
        return code
    finally:
        if is_temp and succeeded and not config.keep_workdir:
            shutil.rmtree(workdir, ignore_errors=True)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="dream")
    sub = parser.add_subparsers(dest="command", required=True)
    run_parser = sub.add_parser("run", help="emit advisory experiment.md for a repository")
    run_parser.add_argument("repo", help="local path or git URL of the target repository")
    run_parser.add_argument("--output", default="experiment.md", help="output path (default experiment.md)")
    run_parser.add_argument("--profile", default="new-project", help="intake profile passthrough")
    run_parser.add_argument("--decompose-live", action="store_true", help="use live AI decomposition (else fixture)")
    run_parser.add_argument("--live-model", help="model id for generation/research; required")
    run_parser.add_argument("--live-api-key-env", default="XAI_API_KEY", help="env var holding the provider key")
    run_parser.add_argument("--live-provider", default="xai", help="OpenAI-compatible provider")
    run_parser.add_argument("--live-base-url", help="provider base URL override")
    run_parser.add_argument("--workdir", help="override workdir (default mkdtemp)")
    run_parser.add_argument("--keep-workdir", action="store_true", help="retain intermediates even on success")
    run_parser.add_argument("--capability-map", help="use an existing capability-map.json")
    return parser


def _config_from_args(args: argparse.Namespace) -> RunConfig:
    return RunConfig(
        repo=args.repo,
        output=Path(args.output).expanduser().resolve(),
        profile=args.profile,
        decompose_live=args.decompose_live,
        live_model=args.live_model,
        live_api_key_env=args.live_api_key_env,
        live_provider=args.live_provider,
        live_base_url=args.live_base_url,
        workdir=Path(args.workdir) if args.workdir else None,
        keep_workdir=args.keep_workdir,
        capability_map=Path(args.capability_map) if args.capability_map else None,
    )


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    if args.command == "run":
        try:
            return run(_config_from_args(args))
        except DreamRunError as exc:
            if not exc.already_reported:
                print(f"dream run failed: {exc}", file=sys.stderr)
            return exc.exit_code
    parser.error("unknown command")
    return EXIT_USAGE


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
