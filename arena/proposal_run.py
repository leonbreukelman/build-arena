"""``proposal run <repo>`` -- orchestrate decompose -> intake -> propose -> rerank -> emit.

A thin, sequential, fail-closed driver. Each stage runs as an isolated subprocess via the existing
frozen stage CLIs; this module only wires them, it never reimplements or edits their logic. After
each stage the expected artifact must exist and the exit must be zero; on any other outcome the run
stops, writes no ``proposal.md``, and preserves the workdir so the partial artifacts are inspectable.

The re-ranker's judge is an unavoidable live model call, so a real run always needs a key. The
orchestrator threads the provider flags to the judge via the ``BUILD_ARENA_LLM_*`` environment
contract (the judge reads model/base-url/key-env from there) and to live decomposition via that
stage's own CLI flags. Credentials are never written to any file this module produces, nor to
``proposal.md`` -- only the key *env var name* is passed; the value is resolved by the stages from
the environment or ``~/.hermes/.env``.
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
from arena.proposal_emit import EmitError

EXIT_OK = 0
EXIT_STAGE_FAILURE = 1
EXIT_NO_PROPOSAL = 2
EXIT_USAGE = 3

_REPO_ROOT = Path(__file__).resolve().parents[1]

_DECOMPOSE_MODULE = "arena.project_model_cli"
_INTAKE_MODULE = "arena.project_intake_scorecard"
_PROPOSE_MODULE = "arena.proposal_planner"
_RERANK_MODULE = "arena.proposal_pairwise_reranker"
_EMIT_MODULE = "arena.proposal_emit"


@dataclass(slots=True)
class StageResult:
    """Outcome of one stage invocation."""

    returncode: int
    stdout: str = ""
    stderr: str = ""


#: A stage runner takes (module, args, env) and returns a StageResult. Injectable for tests.
StageRunner = Callable[[str, list[str], dict[str, str]], StageResult]
#: A git runner takes argv (without the leading "git") and runs it, raising on failure.
GitRunner = Callable[[list[str]], None]


@dataclass(slots=True)
class RunConfig:
    """Resolved configuration for a single ``proposal run``."""

    repo: str
    output: Path
    profile: str = "new-project"
    decompose_live: bool = False
    live_model: str | None = None
    live_api_key_env: str = "XAI_API_KEY"
    live_provider: str = "xai"
    live_base_url: str | None = None
    max_candidates: int = 10
    workdir: Path | None = None
    keep_workdir: bool = False


class ProposalRunError(Exception):
    """A terminal run outcome. ``exit_code`` is the process exit; ``already_reported`` means the
    user-facing message was already printed (e.g. the friendly no-proposal line on stdout)."""

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
    return StageResult(returncode=proc.returncode, stdout=proc.stdout, stderr=proc.stderr)


def _run_git(args: list[str]) -> None:
    try:
        subprocess.run(["git", *args], check=True, capture_output=True, text=True)
    except FileNotFoundError as exc:
        raise ProposalRunError("git is not available on PATH", EXIT_STAGE_FAILURE) from exc
    except subprocess.CalledProcessError as exc:
        detail = (exc.stderr or "").strip() or f"git exited {exc.returncode}"
        raise ProposalRunError(f"git clone failed: {detail}", EXIT_STAGE_FAILURE) from exc


def _looks_like_git_url(value: str) -> bool:
    lowered = value.lower()
    if lowered.endswith(".git"):
        return True
    if lowered.startswith(("http://", "https://", "git://", "ssh://")):
        return True
    # scp-style: git@host:owner/repo  (a colon before any slash, and an '@').
    head = value.split("/", 1)[0]
    return "@" in head and ":" in head


def _subprocess_env(config: RunConfig) -> dict[str, str]:
    env = dict(os.environ)
    existing = env.get("PYTHONPATH", "")
    parts = [str(_REPO_ROOT), *(p for p in existing.split(os.pathsep) if p)]
    env["PYTHONPATH"] = os.pathsep.join(parts)
    # Thread provider selection to the re-ranker judge (xai-only; it has no CLI flags of its own).
    env["BUILD_ARENA_LLM_API_KEY_ENV"] = config.live_api_key_env
    if config.live_model:
        env["BUILD_ARENA_LLM_MODEL"] = config.live_model
    if config.live_base_url:
        env["BUILD_ARENA_LLM_BASE_URL"] = config.live_base_url
    return env


def _preflight(config: RunConfig) -> None:
    if not config.live_model:
        raise ProposalRunError(
            "--live-model is required: the re-ranker judge always makes a live model call",
            EXIT_USAGE,
        )
    try:
        resolve_api_key_with_source(config.live_api_key_env)
    except ValueError as exc:
        raise ProposalRunError(
            f"{exc} (set the key, or choose another env var with --live-api-key-env)",
            EXIT_USAGE,
        ) from exc


def resolve_target(repo: str, workdir: Path, git_runner: GitRunner) -> Path:
    """Resolve ``repo`` to a local directory: use a local path in place, or shallow-clone a URL."""
    local = Path(repo).expanduser()
    if local.is_dir():
        return local.resolve()
    if _looks_like_git_url(repo):
        dest = workdir / "target"
        git_runner(["clone", "--depth", "1", repo, str(dest)])
        return dest.resolve()
    raise ProposalRunError(
        f"repo must be an existing local directory or a git URL: {repo!r}", EXIT_USAGE
    )


def _derive_project_id(target: Path) -> str:
    return target.name or "project"


def _glob_manifest(snap_root: Path) -> Path:
    matches = sorted(snap_root.glob("*/manifest.json"))
    if len(matches) != 1:
        raise ProposalRunError(
            f"expected exactly one snapshot manifest under {snap_root}, found {len(matches)}",
            EXIT_STAGE_FAILURE,
        )
    return matches[0]


def _resolve_model_v1(manifest_path: Path) -> Path:
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ProposalRunError(f"cannot read snapshot manifest: {exc}", EXIT_STAGE_FAILURE) from exc
    rel = manifest.get("project_model_primary_path") or manifest.get("project_model_v1_path")
    if not isinstance(rel, str) or not rel:
        raise ProposalRunError(
            "snapshot manifest does not record a project-model v1 path", EXIT_STAGE_FAILURE
        )
    resolved = (manifest_path.parent / rel).resolve()
    if not resolved.is_file():
        raise ProposalRunError(
            f"project model v1 artifact missing at {resolved}", EXIT_STAGE_FAILURE
        )
    return resolved


def _read_prefilter(trace_path: Path) -> dict[str, object] | None:
    if not trace_path.is_file():
        return None
    try:
        trace = json.loads(trace_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    prefilter = trace.get("preFilter") if isinstance(trace, dict) else None
    return prefilter if isinstance(prefilter, dict) else None


def _fail_stage(stage: str, result: StageResult, workdir: Path) -> ProposalRunError:
    detail = (result.stderr or result.stdout or "").strip()
    suffix = f": {detail}" if detail else ""
    return ProposalRunError(
        f"stage '{stage}' failed (exit {result.returncode}){suffix}. Workdir preserved at {workdir}",
        EXIT_STAGE_FAILURE,
    )


def _decompose_args(config: RunConfig, target: Path, snap_root: Path) -> list[str]:
    args = [
        "snapshot",
        "--project", str(target),
        "--artifacts-root", str(snap_root),
        "--project-id", _derive_project_id(target),
        "--goal", "build-arena proposal run",
        "--llm-mode", "live" if config.decompose_live else "fixture",
    ]
    if config.decompose_live:
        args += ["--allow-live", "--live-provider", config.live_provider]
        if config.live_model:
            args += ["--live-model", config.live_model]
        args += ["--live-api-key-env", config.live_api_key_env]
        if config.live_base_url:
            args += ["--live-base-url", config.live_base_url]
    return args


def _execute_stages(
    config: RunConfig, target: Path, workdir: Path, stage_runner: StageRunner, env: dict[str, str]
) -> int:
    snap_root = workdir / "snap"

    decompose = stage_runner(_DECOMPOSE_MODULE, _decompose_args(config, target, snap_root), env)
    if decompose.returncode != 0:
        raise _fail_stage("decompose", decompose, workdir)
    model_v1 = _resolve_model_v1(_glob_manifest(snap_root))

    scorecard = workdir / "scorecard.json"
    intake = stage_runner(
        _INTAKE_MODULE,
        ["--project", str(target), "--snapshot", str(model_v1),
         "--profile", config.profile, "--output", str(scorecard)],
        env,
    )
    if intake.returncode != 0:
        raise _fail_stage("intake", intake, workdir)
    if not scorecard.is_file():
        raise _fail_stage("intake", StageResult(0, stderr="scorecard not written"), workdir)

    plan = workdir / "proposal-plan.json"
    propose = stage_runner(
        _PROPOSE_MODULE,
        ["--project", str(target), "--scorecard", str(scorecard),
         "--output", str(plan), "--max-candidates", str(config.max_candidates)],
        env,
    )
    if propose.returncode != 0:
        raise _fail_stage("propose", propose, workdir)
    if not plan.is_file():
        raise _fail_stage("propose", StageResult(0, stderr="proposal plan not written"), workdir)

    reranked = workdir / "reranked-plan.json"
    trace = workdir / "rerank-trace.json"
    rerank = stage_runner(
        _RERANK_MODULE,
        ["--project", str(target), "--plan", str(plan), "--graph", str(model_v1),
         "--output-plan", str(reranked), "--trace", str(trace), "--allow-live"],
        env,
    )
    if rerank.returncode != 0:
        prefilter = _read_prefilter(trace)
        if prefilter is not None and prefilter.get("survivorCount") == 0:
            count = prefilter.get("inputCandidateCount", "all")
            print(
                f"No proposal met the bar: all {count} candidate(s) were dropped by the "
                f"pre-filter (see {trace} for per-candidate reasons)."
            )
            raise ProposalRunError("", EXIT_NO_PROPOSAL, already_reported=True)
        raise _fail_stage("rerank", rerank, workdir)
    if not reranked.is_file():
        raise _fail_stage("rerank", StageResult(0, stderr="reranked plan not written"), workdir)

    emit = stage_runner(
        _EMIT_MODULE,
        ["--reranked-plan", str(reranked), "--output", str(config.output)],
        env,
    )
    if emit.returncode != 0:
        raise _fail_stage("emit", emit, workdir)
    if not config.output.is_file():
        raise _fail_stage("emit", StageResult(0, stderr="proposal.md not written"), workdir)
    return EXIT_OK


def run(
    config: RunConfig,
    *,
    stage_runner: StageRunner = _subprocess_stage,
    git_runner: GitRunner = _run_git,
) -> int:
    """Execute the full chain. Returns an exit code; raises ProposalRunError on terminal failure."""
    _preflight(config)

    if config.workdir is not None:
        workdir = config.workdir.expanduser().resolve()
        workdir.mkdir(parents=True, exist_ok=True)
        is_temp = False
    else:
        workdir = Path(tempfile.mkdtemp(prefix="build-arena-")).resolve()
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
    parser = argparse.ArgumentParser(prog="proposal")
    sub = parser.add_subparsers(dest="command", required=True)
    run_parser = sub.add_parser("run", help="emit a ticket-ready proposal.md for a repository")
    run_parser.add_argument("repo", help="local path or git URL of the target repository")
    run_parser.add_argument("--output", default="proposal.md", help="output path (default proposal.md)")
    run_parser.add_argument("--profile", default="new-project", help="intake profile passthrough")
    run_parser.add_argument(
        "--decompose-live", action="store_true", help="use live AI decomposition (else fixture)"
    )
    run_parser.add_argument(
        "--live-model", default=None, help="model id for the judge (and live decompose); required"
    )
    run_parser.add_argument(
        "--live-api-key-env", default="XAI_API_KEY", help="env var holding the provider key"
    )
    run_parser.add_argument("--live-provider", default="xai", help="provider for live decompose")
    run_parser.add_argument("--live-base-url", default=None, help="provider base URL override")
    run_parser.add_argument(
        "--max-candidates", type=int, default=10, help="planner candidate cap (default 10)"
    )
    run_parser.add_argument("--workdir", default=None, help="override workdir (default mkdtemp)")
    run_parser.add_argument(
        "--keep-workdir", action="store_true", help="retain intermediates even on success"
    )
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
        max_candidates=args.max_candidates,
        workdir=Path(args.workdir) if args.workdir else None,
    )


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    # ``_build_parser`` registers a single, required subcommand; argparse rejects missing or
    # unknown commands (SystemExit, exit code 2) before ``run`` can dispatch.
    config = _config_from_args(args)
    try:
        return run(config)
    except ProposalRunError as exc:
        if not exc.already_reported:
            print(f"proposal run failed: {exc}", file=sys.stderr)
        return exc.exit_code
    except EmitError as exc:  # defensive: emit runs as a subprocess, but stay fail-closed.
        print(f"proposal run failed: {exc}", file=sys.stderr)
        return EXIT_STAGE_FAILURE


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
