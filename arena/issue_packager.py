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


class IssuePackagingError(RuntimeError):
    pass


class FabricatedClaimError(IssuePackagingError):
    pass


class OperatorAuthorizationError(IssuePackagingError):
    pass


@dataclass(frozen=True)
class TraceableClaim:
    text: str
    pointer: str


@dataclass(frozen=True)
class IssuePackageResult:
    mode: str
    body: str
    issue_url: str | None = None


class CommandRunner(Protocol):
    def __call__(self, args: list[str], *, cwd: Path) -> subprocess.CompletedProcess[str]: ...


def render_issue_body(evidence_path: Path, *, extra_claims: Sequence[str] = ()) -> str:
    evidence = _load_evidence(evidence_path)
    claims = _mechanical_claims(evidence)
    allowed = {claim.text for claim in claims}
    fabricated = [claim for claim in extra_claims if claim not in allowed]
    if fabricated:
        raise FabricatedClaimError(f"fabricated or untraceable claim: {fabricated[0]}")
    return _render_body(evidence_path, evidence, claims)


def package_candidate_issue(
    *,
    evidence_path: Path,
    target_repo: Path,
    dry_run: bool = True,
    allow_gh: bool = False,
    command_runner: CommandRunner | None = None,
) -> IssuePackageResult:
    evidence = _load_evidence(evidence_path)
    body = render_issue_body(evidence_path)
    if dry_run:
        return IssuePackageResult(mode="dry-run", body=body)
    if not allow_gh:
        raise OperatorAuthorizationError("open-issue mode requires explicit allow_gh=True")
    runner = command_runner or _run_command
    body_file = _write_temp_body(body)
    try:
        result = runner(
            [
                "gh",
                "issue",
                "create",
                "--title",
                _title(evidence),
                "--body-file",
                str(body_file),
            ],
            cwd=target_repo,
        )
        _ensure_ok(result)
    finally:
        body_file.unlink(missing_ok=True)
    return IssuePackageResult(mode="opened", body=body, issue_url=result.stdout.strip() or None)


def record_owner_outcome(
    ledger: FingerprintFailureLedger,
    evidence_path: Path,
    *,
    outcome: str,
    issue_url: str | None = None,
) -> None:
    evidence = _load_evidence(evidence_path)
    normalized = outcome.upper()
    if normalized not in {"ACCEPTED", "REJECTED"}:
        raise ValueError("owner outcome must be 'accepted' or 'rejected'")
    row: dict[str, Any] = {
        "fingerprint_id": _fingerprint_id(evidence),
        "hypothesis_id": _required(evidence, "/verdict/hypothesis_id"),
        "cycle_id": _required(evidence, "/cycle_id"),
        "outcome": f"OWNER_{normalized}",
    }
    if issue_url is not None:
        row["issue_url"] = issue_url
    ledger._append(row)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Package a Build Arena candidate as an owner-gated GitHub issue.")
    parser.add_argument("--evidence", required=True, type=Path)
    parser.add_argument("--target-repo", required=True, type=Path)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true", help="Render the issue body without opening an issue (default).")
    mode.add_argument("--open-issue", action="store_true", help="Open a GitHub issue with gh.")
    parser.add_argument("--allow-gh", action="store_true", help="Required with --open-issue to execute gh issue create.")
    args = parser.parse_args(argv)
    dry_run = not args.open_issue
    result = package_candidate_issue(
        evidence_path=args.evidence,
        target_repo=args.target_repo,
        dry_run=dry_run,
        allow_gh=args.allow_gh,
    )
    if result.mode == "dry-run":
        print("Dry-run only: no gh issue create, git push, PR, merge, or target mutation was executed.\n")
        print(result.body)
    else:
        print(result.issue_url or "Issue opened")
    return 0


def _load_evidence(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise IssuePackagingError("evidence must be a JSON object")
    if data.get("schema_version") != "cycle-evidence/v1":
        raise IssuePackagingError("evidence must use cycle-evidence/v1")
    if not data.get("candidate"):
        raise IssuePackagingError("evidence has no candidate package")
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
        "## Build Arena improvement signal",
        "",
        "Issue handoff: this body is rendered from mechanical evidence only. Build Arena does not implement, push a branch, open a PR, or merge code.",
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
            "### Target coding-agent action",
            "Analyze this improvement signal, then accept or reject it in the target project's normal workflow. Build Arena does not open a PR or mutate the target repo.",
        ]
    )
    return "\n".join(lines) + "\n"


def _title(evidence: dict[str, Any]) -> str:
    return f"Build Arena improvement signal {str(_required(evidence, '/cycle_id'))}"


def _required(data: dict[str, Any], pointer: str) -> Any:
    current: Any = data
    for part in pointer.strip("/").split("/"):
        if not isinstance(current, dict) or part not in current:
            raise IssuePackagingError(f"evidence missing required pointer: {pointer}")
        current = current[part]
    return current


def _fingerprint_id(evidence: dict[str, Any]) -> str:
    for event in evidence.get("events", []):
        if not isinstance(event, dict):
            continue
        payload = event.get("payload")
        if isinstance(payload, dict) and isinstance(payload.get("fingerprint_id"), str):
            return payload["fingerprint_id"]
    raise IssuePackagingError("evidence missing fingerprint_id event payload")


def _run_command(args: list[str], *, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=cwd, text=True, capture_output=True, check=False)


def _ensure_ok(result: subprocess.CompletedProcess[str]) -> None:
    if result.returncode != 0:
        raise IssuePackagingError(result.stderr.strip() or f"command failed: {result.args}")


def _write_temp_body(body: str) -> Path:
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False, suffix=".md") as handle:
        handle.write(body)
        return Path(handle.name)


if __name__ == "__main__":
    raise SystemExit(main())
