from __future__ import annotations

import hashlib
import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

ProposalStatus = Literal[
    "pending",
    "applied_in_worktree",
    "failed_gate",
    "promoted",
    "rejected",
    "duplicate",
]


@dataclass(frozen=True)
class ProposalLineage:
    project_id: str
    base_branch: str
    base_head_oid: str
    dirty: bool
    dirty_paths: tuple[str, ...]
    dirty_fingerprint: str
    snapshot_id: str
    snapshot_hash: str
    scorecard_id: str
    scorecard_hash: str
    run_id: str

    def to_jsonable(self) -> dict[str, Any]:
        return {
            "projectId": self.project_id,
            "baseBranch": self.base_branch,
            "baseHeadOid": self.base_head_oid,
            "dirty": self.dirty,
            "dirtyPaths": list(self.dirty_paths),
            "dirtyFingerprint": self.dirty_fingerprint,
            "snapshotId": self.snapshot_id,
            "snapshotHash": self.snapshot_hash,
            "scorecardId": self.scorecard_id,
            "scorecardHash": self.scorecard_hash,
            "runId": self.run_id,
        }

    @classmethod
    def from_jsonable(cls, raw: dict[str, Any]) -> ProposalLineage:
        dirty_paths = raw.get("dirtyPaths", [])
        return cls(
            project_id=str(raw.get("projectId", "")),
            base_branch=str(raw.get("baseBranch", "")),
            base_head_oid=str(raw.get("baseHeadOid", "")),
            dirty=bool(raw.get("dirty", False)),
            dirty_paths=tuple(str(path) for path in dirty_paths if isinstance(path, str)),
            dirty_fingerprint=str(raw.get("dirtyFingerprint", "")),
            snapshot_id=str(raw.get("snapshotId", "")),
            snapshot_hash=str(raw.get("snapshotHash", "")),
            scorecard_id=str(raw.get("scorecardId", "")),
            scorecard_hash=str(raw.get("scorecardHash", "")),
            run_id=str(raw.get("runId", "")),
        )


@dataclass(frozen=True)
class ProposalRecord:
    proposal_key: str
    status: ProposalStatus
    run_id: str
    finding_id: str
    target_paths: tuple[str, ...]
    lineage: ProposalLineage
    payload: dict[str, Any]

    def to_jsonable(self) -> dict[str, Any]:
        return {
            "proposalKey": self.proposal_key,
            "status": self.status,
            "runId": self.run_id,
            "findingId": self.finding_id,
            "targetPaths": list(self.target_paths),
            "lineage": self.lineage.to_jsonable(),
            "payload": self.payload,
        }

    @classmethod
    def from_jsonable(cls, raw: dict[str, Any]) -> ProposalRecord:
        target_paths = raw.get("targetPaths", [])
        payload = raw.get("payload", {})
        lineage = raw.get("lineage", {})
        return cls(
            proposal_key=str(raw.get("proposalKey", "")),
            status=_coerce_status(str(raw.get("status", "pending"))),
            run_id=str(raw.get("runId", "")),
            finding_id=str(raw.get("findingId", "")),
            target_paths=tuple(str(path) for path in target_paths if isinstance(path, str)),
            lineage=ProposalLineage.from_jsonable(lineage if isinstance(lineage, dict) else {}),
            payload=payload if isinstance(payload, dict) else {},
        )


@dataclass(frozen=True)
class LineageCheckResult:
    ok: bool
    reason: str
    current_head_oid: str = ""


class ProposalRegistry:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def records(self) -> list[ProposalRecord]:
        if not self.path.exists():
            return []
        records: list[ProposalRecord] = []
        for line in self.path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            raw = json.loads(line)
            if isinstance(raw, dict):
                records.append(ProposalRecord.from_jsonable(raw))
        return records

    def latest_by_key(self) -> dict[str, ProposalRecord]:
        latest: dict[str, ProposalRecord] = {}
        for record in self.records():
            latest[record.proposal_key] = record
        return latest

    def latest_status(self, proposal_key: str) -> ProposalStatus | None:
        record = self.latest_by_key().get(proposal_key)
        return record.status if record else None

    def record_pending(
        self,
        *,
        proposal_key: str,
        finding_id: str,
        target_paths: tuple[str, ...],
        lineage: ProposalLineage,
        payload: dict[str, Any],
        run_id: str,
    ) -> ProposalRecord:
        latest = self.latest_by_key().get(proposal_key)
        status: ProposalStatus = "pending"
        if latest is not None and latest.status == "promoted":
            status = "promoted"
        elif latest is not None:
            status = "duplicate"
        record = ProposalRecord(
            proposal_key=proposal_key,
            status=status,
            run_id=run_id,
            finding_id=finding_id,
            target_paths=target_paths,
            lineage=lineage,
            payload=payload,
        )
        if status != "promoted":
            self._append(record)
        return record

    def mark(self, proposal_key: str, status: ProposalStatus, *, run_id: str) -> ProposalRecord:
        latest = self.latest_by_key().get(proposal_key)
        if latest is None:
            raise KeyError(f"unknown proposal key: {proposal_key}")
        record = ProposalRecord(
            proposal_key=proposal_key,
            status=status,
            run_id=run_id,
            finding_id=latest.finding_id,
            target_paths=latest.target_paths,
            lineage=latest.lineage,
            payload=latest.payload,
        )
        self._append(record)
        return record

    def pending_for_prompt(self) -> tuple[str, ...]:
        latest = self.latest_by_key()
        lines = []
        for record in sorted(latest.values(), key=lambda item: item.proposal_key):
            if record.status == "pending":
                lines.append(
                    f"{record.finding_id} -> {', '.join(record.target_paths)} "
                    f"@ {record.lineage.base_branch}:{record.lineage.base_head_oid[:12]}"
                )
        return tuple(lines)

    def check_lineage(self, repo: str | Path, lineage: ProposalLineage) -> LineageCheckResult:
        current_head = _git_output(Path(repo), "rev-parse", "HEAD")
        if current_head and lineage.base_head_oid and current_head != lineage.base_head_oid:
            return LineageCheckResult(False, "base_head_mismatch", current_head)
        return LineageCheckResult(True, "ok", current_head)

    def _append(self, record: ProposalRecord) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record.to_jsonable(), sort_keys=True, separators=(",", ":")) + "\n")


def capture_git_lineage(
    repo: str | Path,
    *,
    project_id: str,
    snapshot_id: str,
    snapshot_hash: str,
    scorecard_id: str,
    scorecard_hash: str,
    run_id: str,
) -> ProposalLineage:
    repo_path = Path(repo)
    branch = _git_output(repo_path, "branch", "--show-current")
    head = _git_output(repo_path, "rev-parse", "HEAD")
    status = _git_output(repo_path, "status", "--porcelain")
    dirty_paths = tuple(sorted(line[3:] for line in status.splitlines() if len(line) > 3))
    dirty_fingerprint = hashlib.sha256(status.encode()).hexdigest()
    return ProposalLineage(
        project_id=project_id,
        base_branch=branch,
        base_head_oid=head,
        dirty=bool(status.strip()),
        dirty_paths=dirty_paths,
        dirty_fingerprint=dirty_fingerprint,
        snapshot_id=snapshot_id,
        snapshot_hash=snapshot_hash,
        scorecard_id=scorecard_id,
        scorecard_hash=scorecard_hash,
        run_id=run_id,
    )


def proposal_key_for(
    *,
    project_id: str,
    base_head_oid: str,
    target_paths: tuple[str, ...],
    finding_id: str,
    domain: str,
    intent_hash: str,
    content_hash: str = "",
) -> str:
    payload = {
        "projectId": project_id,
        "baseHeadOid": base_head_oid,
        "targetPaths": sorted(target_paths),
        "findingId": finding_id,
        "domain": domain,
        "intentHash": intent_hash,
        "contentHash": content_hash,
    }
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _git_output(repo: Path, *args: str) -> str:
    proc = subprocess.run(["git", *args], cwd=repo, text=True, capture_output=True, check=False)
    return proc.stdout.strip() if proc.returncode == 0 else ""


def _coerce_status(value: str) -> ProposalStatus:
    allowed = {"pending", "applied_in_worktree", "failed_gate", "promoted", "rejected", "duplicate"}
    if value not in allowed:
        return "pending"
    return value  # type: ignore[return-value]
