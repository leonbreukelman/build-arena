from __future__ import annotations

import argparse
import json
import subprocess
import tempfile
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

from arena.ledger import FingerprintFailureLedger


class PRPackagingError(RuntimeError):
    pass


class FabricatedClaimError(PRPackagingError):
    pass


class OperatorAuthorizationError(PRPackagingError):
    pass


class RemoteTargetError(PRPackagingError):
    pass


@dataclass(frozen=True)
class TraceableClaim:
    text: str
    pointer: str


@dataclass(frozen=True)
class PRPackageResult:
    mode: str
    body: str
    pr_url: str | None = None
    pushed_branch: str | None = None


class CommandRunner(Protocol):
    def __call__(self, args: list[str], *, cwd: Path) -> subprocess.CompletedProcess[str]: ...


def render_pr_body(evidence_path: Path, *, extra_claims: Sequence[str] = ()) -> str:
    evidence = _load_evidence(evidence_path)
    claims = _mechanical_claims(evidence)
    allowed = {claim.text for claim in claims}
    fabricated = [claim for claim in extra_claims if claim not in allowed]
    if fabricated:
        raise FabricatedClaimError(f"fabricated or untraceable claim: {fabricated[0]}")
    selected_claims = tuple(claims) + tuple(
        claim for claim in claims if claim.text in set(extra_claims) and claim.text not in allowed
    )
    return _render_body(evidence_path, evidence, selected_claims or claims)


def package_candidate_pr(
    *,
    evidence_path: Path,
    target_repo: Path,
    build_arena_repo: Path,
    remote: str = "origin",
    base: str = "main",
    dry_run: bool = True,
    allow_gh: bool = False,
    command_runner: CommandRunner | None = None,
) -> PRPackageResult:
    evidence = _load_evidence(evidence_path)
    body = render_pr_body(evidence_path)
    candidate_branch = _required(evidence, "/candidate/branch")
    cycle_id = _required(evidence, "/cycle_id")
    head_branch = f"arena/pr/{cycle_id}"
    _validate_target_remote(target_repo=target_repo, build_arena_repo=build_arena_repo, remote=remote)
    if dry_run:
        return PRPackageResult(mode="dry-run", body=body)
    if not allow_gh:
        raise OperatorAuthorizationError("push/open-PR mode requires explicit allow_gh=True")
    runner = command_runner or _run_command
    push_result = runner(["git", "push", remote, f"{candidate_branch}:{head_branch}"], cwd=target_repo)
    _ensure_ok(push_result)
    body_file = _write_temp_body(body)
    try:
        pr_result = runner(
            [
                "gh",
                "pr",
                "create",
                "--base",
                base,
                "--head",
                head_branch,
                "--title",
                _title(evidence),
                "--body-file",
                str(body_file),
            ],
            cwd=target_repo,
        )
        _ensure_ok(pr_result)
    finally:
        body_file.unlink(missing_ok=True)
    return PRPackageResult(
        mode="opened",
        body=body,
        pr_url=pr_result.stdout.strip() or None,
        pushed_branch=head_branch,
    )


def record_owner_outcome(
    ledger: FingerprintFailureLedger,
    evidence_path: Path,
    *,
    outcome: str,
    pr_url: str | None = None,
) -> None:
    evidence = _load_evidence(evidence_path)
    normalized = outcome.upper()
    if normalized not in {"MERGED", "REJECTED"}:
        raise ValueError("owner outcome must be 'merged' or 'rejected'")
    row: dict[str, Any] = {
        "fingerprint_id": _fingerprint_id(evidence),
        "hypothesis_id": _required(evidence, "/verdict/hypothesis_id"),
        "cycle_id": _required(evidence, "/cycle_id"),
        "outcome": f"OWNER_{normalized}",
    }
    if pr_url is not None:
        row["pr_url"] = pr_url
    ledger._append(row)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Package a verified Build Arena candidate as an owner-gated PR.")
    parser.add_argument("--evidence", required=True, type=Path)
    parser.add_argument("--target-repo", required=True, type=Path)
    parser.add_argument("--build-arena-repo", required=True, type=Path)
    parser.add_argument("--remote", default="origin")
    parser.add_argument("--base", default="main")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true", help="Render the PR body without pushing (default).")
    mode.add_argument("--open-pr", action="store_true", help="Push candidate branch and open a PR with gh.")
    parser.add_argument("--allow-gh", action="store_true", help="Required with --open-pr to execute gh/git push.")
    args = parser.parse_args(argv)
    dry_run = not args.open_pr
    result = package_candidate_pr(
        evidence_path=args.evidence,
        target_repo=args.target_repo,
        build_arena_repo=args.build_arena_repo,
        remote=args.remote,
        base=args.base,
        dry_run=dry_run,
        allow_gh=args.allow_gh,
    )
    if result.mode == "dry-run":
        print("Dry-run only: no git push, gh pr create, or merge was executed.\n")
        print(result.body)
    else:
        print(result.pr_url or "PR opened")
    return 0


def _load_evidence(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise PRPackagingError("evidence must be a JSON object")
    if data.get("schema_version") != "cycle-evidence/v1":
        raise PRPackagingError("evidence must use cycle-evidence/v1")
    if not data.get("candidate"):
        raise PRPackagingError("evidence has no candidate package")
    return data


def _mechanical_claims(evidence: dict[str, Any]) -> tuple[TraceableClaim, ...]:
    files = _required(evidence, "/patch/files")
    file_list = ", ".join(str(item.get("path")) for item in files if isinstance(item, dict)) or "no files"
    return (
        TraceableClaim(f"Candidate branch: {_required(evidence, '/candidate/branch')}", "#/candidate/branch"),
        TraceableClaim(f"Candidate commit: {_required(evidence, '/candidate/git_oid')}", "#/candidate/git_oid"),
        TraceableClaim(f"Verdict: {_required(evidence, '/verdict/outcome')}", "#/verdict/outcome"),
        TraceableClaim(f"Score delta: {_required(evidence, '/verdict/score_delta')}", "#/verdict/score_delta"),
        TraceableClaim(
            f"Score after composite: {_required(evidence, '/score_after/vector/composite')}",
            "#/score_after/vector/composite",
        ),
        TraceableClaim(f"Tests passed: {_required(evidence, '/verdict/tests_passed')}", "#/verdict/tests_passed"),
        TraceableClaim(
            f"Patch size: +{_required(evidence, '/patch/added_lines')} -{_required(evidence, '/patch/deleted_lines')}",
            "#/patch/added_lines #/patch/deleted_lines",
        ),
        TraceableClaim(f"Touched files: {file_list}", "#/patch/files"),
    )


def _render_body(evidence_path: Path, evidence: dict[str, Any], claims: Sequence[TraceableClaim]) -> str:
    lines = [
        "## Build Arena owner-gated candidate PR",
        "",
        "Dry-run gate: this body is rendered from mechanical evidence only. No automatic merge is allowed.",
        "",
        f"Evidence file: `{evidence_path}`",
        f"Run: `{_required(evidence, '/run_id')}`; cycle: `{_required(evidence, '/cycle_id')}`",
        "",
        "### Traceable claims",
    ]
    lines.extend(f"- {claim.text} (source `{claim.pointer}`)" for claim in claims)
    lines.extend(
        [
            "",
            "### Owner action required",
            "Review the diff and evidence, then merge or reject manually. Build Arena will not auto-merge this PR.",
        ]
    )
    return "\n".join(lines) + "\n"


def _title(evidence: dict[str, Any]) -> str:
    return f"Build Arena candidate {str(_required(evidence, '/cycle_id'))}"


def _required(data: dict[str, Any], pointer: str) -> Any:
    current: Any = data
    for part in pointer.strip("/").split("/"):
        if not isinstance(current, dict) or part not in current:
            raise PRPackagingError(f"evidence missing required pointer: {pointer}")
        current = current[part]
    return current


def _fingerprint_id(evidence: dict[str, Any]) -> str:
    for event in evidence.get("events", []):
        if not isinstance(event, dict):
            continue
        payload = event.get("payload")
        if isinstance(payload, dict) and isinstance(payload.get("fingerprint_id"), str):
            return payload["fingerprint_id"]
    raise PRPackagingError("evidence missing fingerprint_id event payload")


def _validate_target_remote(*, target_repo: Path, build_arena_repo: Path, remote: str) -> None:
    target_url = _remote_url(target_repo, remote)
    build_arena_url = _remote_url(build_arena_repo, remote)
    if target_repo.resolve() != build_arena_repo.resolve() and target_url == build_arena_url:
        raise RemoteTargetError("target repo remote matches Build Arena remote; refusing cross-repo PR package")


def _remote_url(repo: Path, remote: str) -> str:
    return subprocess.check_output(["git", "config", "--get", f"remote.{remote}.url"], cwd=repo, text=True).strip()


def _run_command(args: list[str], *, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=cwd, text=True, capture_output=True, check=False)


def _ensure_ok(result: subprocess.CompletedProcess[str]) -> None:
    if result.returncode != 0:
        raise PRPackagingError(result.stderr.strip() or f"command failed: {result.args}")


def _write_temp_body(body: str) -> Path:
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False, suffix=".md") as handle:
        handle.write(body)
        return Path(handle.name)


if __name__ == "__main__":
    raise SystemExit(main())
