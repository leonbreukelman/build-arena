from __future__ import annotations

import dataclasses
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any, cast

from arena.events import EventLog, event_payload
from arena.generated.models import Baseline, HaltRecord, Verdict, Worktree


class CycleEvidenceWriter:
    """Write mechanical per-cycle and halt evidence from canonical records."""

    def __init__(self, *, root: Path, worktree_root: Path) -> None:
        self.root = root.resolve()
        self.worktree_root = worktree_root.resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    def write_cycle_evidence(
        self,
        *,
        cycle_id: str,
        event_log: EventLog,
        budget: Any,
        worktree: Worktree,
        score_before: Any,
        score_after: Any | None,
        verdict: Verdict,
        patch_path: Path | None,
        candidate: Baseline | None = None,
        candidate_branch: str | None = None,
    ) -> Path:
        payload = {
            "schema_version": "cycle-evidence/v1",
            "run_id": event_log.run_id,
            "cycle_id": cycle_id,
            "worktree_root": str(self.worktree_root),
            "worktree": worktree.model_dump(mode="json"),
            "budget": _budget_json(budget),
            "score_before": _jsonable(score_before),
            "score_after": _jsonable(score_after) if score_after is not None else None,
            "verdict": verdict.model_dump(mode="json"),
            "candidate": _candidate_json(candidate, candidate_branch),
            "patch": _patch_json(worktree, patch_path),
            "events": _events_json(event_log.read_events(), cycle_id=cycle_id),
        }
        return self._write(f"{cycle_id}.json", payload)

    def write_halt_evidence(
        self,
        *,
        run_id: str,
        event_log: EventLog,
        budget: Any,
        halt_record: HaltRecord,
    ) -> Path:
        payload = {
            "schema_version": "halt-evidence/v1",
            "run_id": run_id,
            "halt": halt_record.model_dump(mode="json"),
            "budget": _budget_json(budget),
            "events": _events_json(event_log.read_events()),
        }
        return self._write(f"halt-{run_id}.json", payload)

    def _write(self, name: str, payload: dict[str, Any]) -> Path:
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, sort_keys=True, indent=2) + "\n", encoding="utf-8")
        return path


def _events_json(events, *, cycle_id: str | None = None) -> list[dict[str, Any]]:
    selected = [event for event in events if cycle_id is None or event.cycle_id in {None, cycle_id}]
    return [
        {
            "id": event.id,
            "run_id": event.run_id,
            "cycle_id": event.cycle_id,
            "seq": event.seq,
            "ts": event.ts,
            "type": event.type,
            "level": event.level,
            "payload_json_sha": event.payload_json_sha,
            "payload": event_payload(event),
        }
        for event in selected
    ]


def _budget_json(budget: Any) -> dict[str, Any]:
    fields = (
        "wall_clock_seconds_cap",
        "cycle_count_cap",
        "claude_code_credits_cap",
        "codex_credits_cap",
        "copilot_premium_cap",
        "start_ts",
        "wall_clock_seconds_used",
        "cycle_count_used",
        "claude_code_credits_used",
        "codex_credits_used",
        "copilot_premium_used",
        "promotions_total",
    )
    return {name: getattr(budget, name) for name in fields if hasattr(budget, name)}


def _jsonable(value: Any) -> dict[str, Any]:
    if hasattr(value, "to_jsonable"):
        return value.to_jsonable()
    if hasattr(value, "model_dump"):
        return value.model_dump(mode="json")
    if dataclasses.is_dataclass(value) and not isinstance(value, type):
        return dataclasses.asdict(cast(Any, value))
    raise TypeError(f"value is not evidence-jsonable: {type(value).__name__}")


def _candidate_json(candidate: Baseline | None, branch: str | None) -> dict[str, Any] | None:
    if candidate is None:
        return None
    data = candidate.model_dump(mode="json")
    if branch is not None:
        data["branch"] = branch
    return data


def _patch_json(worktree: Worktree, patch_path: Path | None) -> dict[str, Any]:
    worktree_path = Path(worktree.path)
    head = _git(["rev-parse", "HEAD"], cwd=worktree_path)
    numstat = _git(["diff", "--numstat", worktree.base_git_oid, head], cwd=worktree_path)
    files: list[dict[str, Any]] = []
    added_total = 0
    deleted_total = 0
    for line in numstat.splitlines():
        parts = line.split("\t")
        if len(parts) < 3:
            continue
        added = _int_or_zero(parts[0])
        deleted = _int_or_zero(parts[1])
        files.append({"path": parts[2], "added_lines": added, "deleted_lines": deleted})
        added_total += added
        deleted_total += deleted
    payload: dict[str, Any] = {
        "base_git_oid": worktree.base_git_oid,
        "head_git_oid": head,
        "added_lines": added_total,
        "deleted_lines": deleted_total,
        "files": files,
    }
    if patch_path is not None:
        payload["path"] = str(patch_path)
        payload["sha256"] = _file_sha256(patch_path) if patch_path.exists() else None
    return payload


def _git(args: list[str], *, cwd: Path) -> str:
    return subprocess.check_output(["git", *args], cwd=cwd, text=True).strip()


def _int_or_zero(value: str) -> int:
    return int(value) if value.isdecimal() else 0


def _file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()
