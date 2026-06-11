from __future__ import annotations

import json
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "project-model-freshness/v0"
NON_FRESH_EXIT_CODE = 2

_STATUS_PRECEDENCE = {
    "snapshot-mismatch": 1,
    "dirty-worktree": 2,
    "branch-diverged": 3,
    "base-advanced": 4,
    "unknown": 5,
    "fresh": 6,
}


@dataclass(frozen=True)
class FreshnessReport:
    project_root: str
    snapshot_path: str
    snapshot_id: str
    snapshot_head_oid: str | None
    current_head_oid: str | None
    snapshot_dirty: bool | None
    current_dirty: bool
    current_dirty_paths: tuple[str, ...]
    current_branch: str | None
    default_branch: str | None
    remote_name: str | None
    ahead: int | None
    behind: int | None
    ahead_behind_available: bool
    active_branches: tuple[dict[str, Any], ...]
    open_pull_requests: tuple[dict[str, Any], ...]
    open_pull_requests_available: bool
    status: str
    warnings: tuple[str, ...]

    @property
    def safe_for_read_only_review(self) -> bool:
        return True

    @property
    def safe_for_mutation(self) -> bool:
        return self.status == "fresh"

    @property
    def exit_code(self) -> int:
        return 0 if self.status == "fresh" else NON_FRESH_EXIT_CODE


def assess_project_model_freshness(project: str | Path, snapshot: str | Path) -> FreshnessReport:
    project_path = Path(project).resolve()
    snapshot_path = Path(snapshot).resolve()
    warnings: list[str] = []
    snapshot_data = _load_snapshot(snapshot_path, warnings)
    git_data = snapshot_data.get("provenance", {}).get("git", {}) if isinstance(snapshot_data, dict) else {}
    snapshot_graph_hash = _get(snapshot_data, "snapshot", "graph_hash")
    project_graph_hash = _get(snapshot_data, "projectGraph", "graphHash")
    snapshot_id = str(snapshot_data.get("id", "")) if isinstance(snapshot_data, dict) else ""
    snapshot_head = _none_if_empty(git_data.get("headOid") if isinstance(git_data, dict) else None)
    snapshot_dirty = git_data.get("dirty") if isinstance(git_data, dict) and isinstance(git_data.get("dirty"), bool) else None

    current_head = _git(project_path, ["rev-parse", "HEAD"], warnings).stdout.strip() or None
    current_branch = _git(project_path, ["branch", "--show-current"], warnings).stdout.strip() or None
    dirty_paths = _dirty_paths(project_path, warnings)
    current_dirty = bool(dirty_paths)
    default_branch, remote_name = _default_branch(project_path, current_branch, warnings)
    ahead, behind, ahead_available = _ahead_behind(project_path, default_branch, remote_name, warnings)
    active_branches = tuple(_active_branches(project_path, warnings))
    prs, prs_available = _open_pull_requests(project_path, warnings)

    status = _status(
        snapshot_data=snapshot_data,
        snapshot_graph_hash=snapshot_graph_hash,
        project_graph_hash=project_graph_hash,
        snapshot_head=snapshot_head,
        current_head=current_head,
        current_dirty=current_dirty,
        project_path=project_path,
        warnings=warnings,
    )
    return FreshnessReport(
        project_root=str(project_path),
        snapshot_path=str(snapshot_path),
        snapshot_id=snapshot_id,
        snapshot_head_oid=snapshot_head,
        current_head_oid=current_head,
        snapshot_dirty=snapshot_dirty,
        current_dirty=current_dirty,
        current_dirty_paths=tuple(dirty_paths),
        current_branch=current_branch,
        default_branch=default_branch,
        remote_name=remote_name,
        ahead=ahead,
        behind=behind,
        ahead_behind_available=ahead_available,
        active_branches=active_branches,
        open_pull_requests=tuple(prs),
        open_pull_requests_available=prs_available,
        status=status,
        warnings=tuple(sorted(dict.fromkeys(warnings))),
    )


def freshness_to_dict(report: FreshnessReport) -> dict[str, Any]:
    return {
        "schemaVersion": SCHEMA_VERSION,
        "projectRoot": report.project_root,
        "snapshotPath": report.snapshot_path,
        "snapshotId": report.snapshot_id,
        "snapshotHeadOid": report.snapshot_head_oid,
        "currentHeadOid": report.current_head_oid,
        "snapshotDirty": report.snapshot_dirty,
        "currentDirty": report.current_dirty,
        "currentDirtyPaths": list(report.current_dirty_paths),
        "currentBranch": report.current_branch,
        "defaultBranch": report.default_branch,
        "remoteName": report.remote_name,
        "aheadBehind": {"ahead": report.ahead, "behind": report.behind, "available": report.ahead_behind_available},
        "activeBranches": list(report.active_branches),
        "openPullRequests": {"available": report.open_pull_requests_available, "items": list(report.open_pull_requests)},
        "status": report.status,
        "safeForReadOnlyReview": report.safe_for_read_only_review,
        "safeForMutation": report.safe_for_mutation,
        "exitCode": report.exit_code,
        "warnings": list(report.warnings),
    }


def _load_snapshot(path: Path, warnings: list[str]) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001 - convert to machine-readable status.
        warnings.append(f"could not read snapshot: {type(exc).__name__}: {exc}")
        return {}
    if not isinstance(payload, dict):
        warnings.append("snapshot payload is not a JSON object")
        return {}
    return payload


def _get(payload: dict[str, Any], *keys: str) -> Any:
    current: Any = payload
    for key in keys:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def _none_if_empty(value: Any) -> str | None:
    return value if isinstance(value, str) and value.strip() else None


def _git(project: Path, args: list[str], warnings: list[str], *, check: bool = False) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(["git", *args], cwd=project, text=True, capture_output=True, check=check)
    except FileNotFoundError:
        warnings.append("git executable not found")
    except subprocess.CalledProcessError as exc:
        warnings.append(f"git {' '.join(args)} failed: {exc.stderr.strip()}")
    return subprocess.CompletedProcess(["git", *args], 1, "", "")


def _dirty_paths(project: Path, warnings: list[str]) -> list[str]:
    proc = _git(project, ["status", "--porcelain"], warnings)
    paths: list[str] = []
    for line in proc.stdout.splitlines():
        if len(line) < 4:
            continue
        raw = line[3:]
        if " -> " in raw:
            raw = raw.split(" -> ", 1)[1]
        paths.append(raw.strip().strip('"'))
    return sorted(dict.fromkeys(paths))


def _default_branch(project: Path, current_branch: str | None, warnings: list[str]) -> tuple[str | None, str | None]:
    remote_proc = _git(project, ["remote"], warnings)
    remotes = [line.strip() for line in remote_proc.stdout.splitlines() if line.strip()]
    remote = "origin" if "origin" in remotes else (remotes[0] if remotes else None)
    if remote:
        head_proc = _git(project, ["symbolic-ref", "--quiet", "--short", f"refs/remotes/{remote}/HEAD"], warnings)
        ref = head_proc.stdout.strip()
        if ref.startswith(f"{remote}/"):
            return ref.removeprefix(f"{remote}/"), remote
    return current_branch, remote


def _ahead_behind(project: Path, default_branch: str | None, remote_name: str | None, warnings: list[str]) -> tuple[int | None, int | None, bool]:
    if not default_branch or not remote_name:
        return None, None, False
    ref = f"{remote_name}/{default_branch}"
    exists = _git(project, ["rev-parse", "--verify", "--quiet", ref], warnings)
    if exists.returncode != 0:
        return None, None, False
    counts = _git(project, ["rev-list", "--left-right", "--count", f"HEAD...{ref}"], warnings)
    parts = counts.stdout.strip().split()
    if len(parts) == 2 and all(part.isdigit() for part in parts):
        return int(parts[0]), int(parts[1]), True
    return None, None, False


def _active_branches(project: Path, warnings: list[str]) -> list[dict[str, Any]]:
    proc = _git(project, ["for-each-ref", "--format=%(refname:short)|%(objectname)|%(upstream:short)", "refs/heads", "refs/remotes"], warnings)
    branches: list[dict[str, Any]] = []
    for line in proc.stdout.splitlines():
        name, oid, upstream = (line.split("|", 2) + [""])[:3]
        if not name or name.endswith("/HEAD"):
            continue
        branches.append({"name": name, "headOid": oid or None, "upstream": upstream or None})
    return sorted(branches, key=lambda item: str(item["name"]))


def _open_pull_requests(project: Path, warnings: list[str]) -> tuple[list[dict[str, Any]], bool]:
    if shutil.which("gh") is None:
        return [], False
    try:
        proc = subprocess.run(
            ["gh", "pr", "list", "--state", "open", "--json", "number,title,headRefName,baseRefName,url"],
            cwd=project,
            text=True,
            capture_output=True,
            check=False,
        )
    except OSError as exc:
        warnings.append(f"gh pr list unavailable: {exc}")
        return [], False
    if proc.returncode != 0:
        warnings.append("gh pr list unavailable")
        return [], False
    try:
        payload = json.loads(proc.stdout or "[]")
    except json.JSONDecodeError:
        warnings.append("gh pr list returned malformed JSON")
        return [], False
    if not isinstance(payload, list):
        return [], False
    return [item for item in payload if isinstance(item, dict)], True


def _status(
    *,
    snapshot_data: dict[str, Any],
    snapshot_graph_hash: Any,
    project_graph_hash: Any,
    snapshot_head: str | None,
    current_head: str | None,
    current_dirty: bool,
    project_path: Path,
    warnings: list[str],
) -> str:
    candidates: set[str] = set()
    if snapshot_data.get("schemaVersion") != "project-model/v1" or not snapshot_data.get("id"):
        candidates.add("snapshot-mismatch")
    if snapshot_graph_hash and project_graph_hash and snapshot_graph_hash != project_graph_hash:
        candidates.add("snapshot-mismatch")
    if current_dirty:
        candidates.add("dirty-worktree")
    if not snapshot_head or not current_head:
        candidates.add("unknown")
    elif current_head != snapshot_head:
        if _git(project_path, ["merge-base", "--is-ancestor", snapshot_head, current_head], warnings).returncode == 0:
            candidates.add("base-advanced")
        else:
            candidates.add("branch-diverged")
    if not candidates:
        candidates.add("fresh")
    return sorted(candidates, key=lambda item: _STATUS_PRECEDENCE[item])[0]
