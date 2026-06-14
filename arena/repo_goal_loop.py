"""Repo-scale `/goal` loop for Build Arena (epic #25, Phase 5, issue #31).

This is the capstone that wires the multi-domain proposal component (Phases 1-4)
into an autonomous improvement loop: decompose -> intake scorecard -> cross-domain
rank -> select top promotable candidate -> apply in an isolated worktree -> verify
with the candidate's load-bearing domain gate -> (dry-run: record; authorized:
ff-only promote) -> re-decompose -> repeat, under budget / divergence / boundary
guards.

Safety posture (matches the readiness register, still `not_ready_blockers_remain`):
- Dry-run is the DEFAULT: the loop never advances the repo baseline unless
  `dry_run=False` AND `allow_promotion=True` are BOTH set explicitly.
- Promotion of a code-quality candidate additionally requires the project's
  behaviour/test gate to pass (the guardrail carried from #29) — the lint gate
  alone never authorizes a merge.
- Deterministic, offline default path: candidate diffs are produced by a
  deterministic local fixer (ruff --fix for code, a grounded generator for docs),
  never a live model, unless a live transport is configured by the operator.
- Boundary checks run BEFORE any apply; repeated gate failures trip divergence.
"""

from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from arena.boundary import is_boundary_violation
from arena.project_decomposer_ai import build_project_model_snapshot
from arena.project_intake_scorecard import build_project_intake_scorecard
from arena.proposal_planner import build_proposal_plan
from arena.proposal_ranker import build_ranked_proposals


@dataclass(frozen=True)
class RepoGoalLoopConfig:
    project: Path
    goal: str
    artifacts_root: Path
    profile: str = "active-development"
    max_cycles: int = 10
    max_candidates: int = 10
    dry_run: bool = True
    allow_promotion: bool = False
    stop_after_promotions: int | None = None
    max_consecutive_failures: int = 3
    read_only_paths: tuple[str, ...] = ()
    test_command: str | None = None
    # Test-only hook: force every apply to be a no-op so the gate fails each cycle
    # (used to exercise the divergence halt without a live model).
    _force_noop_apply: bool = False


@dataclass(frozen=True)
class RepoGoalLoopResult:
    cycles_run: int
    promotions: int
    selected_finding_ids: tuple[str, ...]
    events_jsonl: Path
    halted_reason: str | None


@dataclass
class _EventLog:
    path: Path
    _events: list[dict[str, Any]] = field(default_factory=list)

    def emit(self, type_: str, *, cycle: int | None = None, payload: dict[str, Any] | None = None) -> None:
        record = {"seq": len(self._events), "type": type_, "cycle": cycle, "payload": payload or {}}
        self._events.append(record)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, sort_keys=True) + "\n")


def run_repo_goal_loop(config: RepoGoalLoopConfig) -> RepoGoalLoopResult:
    project = Path(config.project).resolve()
    artifacts_root = Path(config.artifacts_root).resolve()
    # The artifacts root must live OUTSIDE the target repo, otherwise loop
    # bookkeeping (events, snapshots, worktrees) would dirty the project working
    # tree and could interact with promotion staging. Fail closed.
    if artifacts_root == project or project in artifacts_root.parents:
        raise ValueError(f"artifacts_root must be outside the project repo: project={project} artifacts_root={artifacts_root}")
    artifacts_root.mkdir(parents=True, exist_ok=True)
    events_path = artifacts_root / "loop-events.jsonl"
    events_path.write_text("", encoding="utf-8")
    log = _EventLog(events_path)

    log.emit("RUN_STARTED", payload={"goal": config.goal, "profile": config.profile, "dryRun": config.dry_run})

    selected: list[str] = []
    promotions = 0
    consecutive_failures = 0
    tried_finding_ids: set[str] = set()
    halted_reason: str | None = None
    cycles_run = 0

    for cycle in range(1, config.max_cycles + 1):
        cycles_run = cycle
        log.emit("CYCLE_STARTED", cycle=cycle, payload={"ordinal": cycle})

        ranked = _decompose_and_rank(project, config, artifacts_root, cycle)
        candidate = _select_promotable(ranked, tried_finding_ids)
        if candidate is None:
            log.emit("NOTHING_TO_IMPROVE", cycle=cycle, payload={"reason": "no untried positive-leverage candidate"})
            halted_reason = "nothing_to_improve"
            break

        finding_id = candidate["findingId"]
        target_path = candidate["targetPath"]
        domain = candidate["domain"]
        selected.append(finding_id)
        tried_finding_ids.add(finding_id)
        log.emit("CANDIDATE_SELECTED", cycle=cycle, payload={"finding_id": finding_id, "domain": domain, "target_path": target_path, "priority_score": candidate["priorityScore"]})

        # Boundary check BEFORE any apply.
        if is_boundary_violation([target_path], read_only_dirs=_read_only_dirs(config)):
            log.emit("BOUNDARY_VIOLATION", cycle=cycle, payload={"finding_id": finding_id, "target_path": target_path})
            consecutive_failures += 1
            if consecutive_failures >= config.max_consecutive_failures:
                log.emit("DIVERGENCE_HALT", cycle=cycle, payload={"reason": "boundary_violation_streak", "count": consecutive_failures})
                halted_reason = "divergence"
                break
            continue

        applied = _apply_and_verify(project, config, artifacts_root, cycle, candidate, log)
        if not applied["ok"]:
            consecutive_failures += 1
            if consecutive_failures >= config.max_consecutive_failures:
                log.emit("DIVERGENCE_HALT", cycle=cycle, payload={"reason": "verify_failure_streak", "count": consecutive_failures})
                halted_reason = "divergence"
                break
            continue

        consecutive_failures = 0

        if config.dry_run or not config.allow_promotion:
            log.emit("CANDIDATE_PACKAGED", cycle=cycle, payload={"finding_id": finding_id, "promoted": False, "reason": "dry_run" if config.dry_run else "promotion_not_authorized"})
        elif not applied.get("promotable", False):
            # Verified for dry-run purposes but not promotable (e.g. a code change
            # with no configured behaviour/test gate). Fail-closed: never promote.
            reason = "behaviour_gate_required" if applied.get("is_code") and applied.get("behaviour_gate") == "required_missing" else "not_promotable"
            log.emit("PROMOTION_REFUSED", cycle=cycle, payload={"finding_id": finding_id, "target_path": target_path, "reason": reason})
        else:
            promoted = _promote(project, config, applied, candidate, log, cycle)
            if promoted:
                promotions += 1
                tried_finding_ids.discard(finding_id)  # re-decompose may surface follow-ups
                if config.stop_after_promotions is not None and promotions >= config.stop_after_promotions:
                    log.emit("RUN_COMPLETED", payload={"promotions": promotions, "cyclesRun": cycles_run})
                    break

    if halted_reason is None and cycles_run >= config.max_cycles:
        log.emit("BUDGET_HALT", cycle=cycles_run, payload={"reason": "max_cycles", "cap": config.max_cycles})
        halted_reason = "budget"

    log.emit("RUN_ENDED", payload={"promotions": promotions, "cyclesRun": cycles_run, "halted": halted_reason})
    return RepoGoalLoopResult(
        cycles_run=cycles_run,
        promotions=promotions,
        selected_finding_ids=tuple(selected),
        events_jsonl=events_path,
        halted_reason=halted_reason,
    )


def _read_only_dirs(config: RepoGoalLoopConfig) -> tuple[str, ...]:
    from arena.boundary import DEFAULT_READ_ONLY_DIRS

    return tuple(DEFAULT_READ_ONLY_DIRS) + tuple(config.read_only_paths)


def _decompose_and_rank(project: Path, config: RepoGoalLoopConfig, artifacts_root: Path, cycle: int) -> dict[str, Any]:
    """Decompose -> intake scorecard -> cross-domain rank, returning the ranked artifact."""
    cycle_dir = artifacts_root / f"cycle-{cycle}"
    cycle_dir.mkdir(parents=True, exist_ok=True)
    snapshot_artifacts = cycle_dir / "snapshot"
    result = build_project_model_snapshot(
        str(project),
        str(snapshot_artifacts),
        project_id=f"repo-goal-{project.name}",
        goal=config.goal,
        llm_mode="fixture",
        overwrite=True,
    )
    snapshot_path = result.snapshot_dir / "project-model-v1.json"
    scorecard = build_project_intake_scorecard(project, snapshot_path, profile=config.profile)
    scorecard_path = cycle_dir / "scorecard.json"
    scorecard_path.write_text(json.dumps(scorecard, sort_keys=True), encoding="utf-8")
    ranked = build_ranked_proposals(project, scorecard_path, max_candidates=config.max_candidates)
    (cycle_dir / "ranked-proposals.json").write_text(json.dumps(ranked.to_jsonable(), sort_keys=True), encoding="utf-8")
    # Also build the plan so we have the executable candidate (intent, verification).
    plan = build_proposal_plan(project, scorecard_path, max_candidates=config.max_candidates)
    (cycle_dir / "proposal-plan.json").write_text(json.dumps(plan.to_jsonable(), sort_keys=True), encoding="utf-8")
    return {"ranked": ranked.to_jsonable(), "plan": plan.to_jsonable(), "scorecard_path": scorecard_path, "cycle_dir": cycle_dir}


def _select_promotable(ranked_bundle: dict[str, Any], tried: set[str]) -> dict[str, Any] | None:
    """Top-ranked entry (positive score) not already tried, joined with its plan
    candidate so we have the executable verification commands."""
    ranked = ranked_bundle["ranked"]
    plan = ranked_bundle["plan"]
    plan_by_finding = {c["finding_id"]: c for c in plan["candidates"]}
    for entry in ranked["entries"]:
        if entry["priorityScore"] <= 0:
            continue
        if entry["findingId"] in tried:
            continue
        plan_candidate = plan_by_finding.get(entry["findingId"])
        if plan_candidate is None:
            continue
        return {
            "findingId": entry["findingId"],
            "domain": entry["domain"],
            "targetPath": entry["targetPath"],
            "priorityScore": entry["priorityScore"],
            # Threaded through so the code-vs-docs promotion guard (#29 behaviour
            # gate) can classify non-.py code targets too, not just .py.
            "autonomyBoundary": entry.get("autonomyBoundary", ""),
            "plan_candidate": plan_candidate,
        }
    return None


def _apply_and_verify(
    project: Path,
    config: RepoGoalLoopConfig,
    artifacts_root: Path,
    cycle: int,
    candidate: dict[str, Any],
    log: _EventLog,
) -> dict[str, Any]:
    """Apply the candidate's deterministic fix in an isolated worktree and run its
    domain gate. Returns {ok, worktree, target_path}."""
    from arena.worktrees import WorktreeManager

    target_path = candidate["targetPath"]
    plan_candidate = candidate["plan_candidate"]
    head_oid = subprocess.run(["git", "rev-parse", "HEAD"], cwd=project, text=True, capture_output=True).stdout.strip()
    worktree_root = artifacts_root / "worktrees"
    manager = WorktreeManager(repo=project, worktree_root=worktree_root)
    cycle_id = f"goal-cycle-{cycle}"
    worktree = manager.create(cycle_id, head_oid)
    worktree_path = Path(worktree.path)
    promotion_mode = (not config.dry_run) and config.allow_promotion
    caller_owns_worktree = False
    try:
        if config._force_noop_apply:
            applied_ok = False
        else:
            applied_ok = _deterministic_apply(worktree_path, target_path, plan_candidate)
        if not applied_ok:
            log.emit("CANDIDATE_APPLY_FAILED", cycle=cycle, payload={"finding_id": candidate["findingId"], "target_path": target_path})
            return {"ok": False, "worktree": None, "target_path": target_path}
        log.emit("CANDIDATE_APPLIED", cycle=cycle, payload={"finding_id": candidate["findingId"], "target_path": target_path})

        verification = _run_gate(worktree_path, tuple(plan_candidate.get("verification_commands", [])))
        gate_ok = bool(verification) and all(item["exitCode"] == 0 for item in verification)

        # Behaviour gate (the #29 guardrail): a code change (.py / needs_code_change)
        # is only PROMOTABLE if the project's test command is configured AND passes.
        # The lint/domain gate alone never authorizes a merge for code. Docs (.md)
        # candidates are low-risk and promotable on their domain gate.
        is_code = target_path.endswith(".py") or candidate.get("autonomyBoundary") == "needs_code_change"
        behaviour_gate = "not_applicable"
        promotable = gate_ok
        if is_code:
            if config.test_command:
                behaviour_ok = gate_ok and _run_behaviour_gate(worktree_path, config.test_command)
                behaviour_gate = "passed" if behaviour_ok else "failed"
                promotable = behaviour_ok
            else:
                # No behaviour gate configured -> code is verifiable (dry-run) but
                # NOT promotable. Fail-closed against the lint-alone promotion hole.
                behaviour_gate = "required_missing"
                promotable = False

        log.emit(
            "CANDIDATE_VERIFIED",
            cycle=cycle,
            payload={"finding_id": candidate["findingId"], "ok": gate_ok, "promotable": promotable, "behaviour_gate": behaviour_gate, "commands": verification},
        )
        # Only a promotable candidate in promotion mode is handed to _promote, which
        # owns teardown. Every other path (dry-run, or non-promotable) tears down
        # here so worktrees never leak.
        caller_owns_worktree = promotable and promotion_mode
        return {
            "ok": gate_ok,
            "promotable": promotable,
            "is_code": is_code,
            "behaviour_gate": behaviour_gate,
            "worktree": str(worktree_path),
            "worktree_obj": worktree,
            "manager": manager,
            "target_path": target_path,
        }
    finally:
        if not caller_owns_worktree:
            manager.teardown(worktree)


def _deterministic_apply(worktree: Path, target_path: str, plan_candidate: dict[str, Any]) -> bool:
    """Produce a real, offline fix for the candidate. Code: ruff --fix. Docs: a
    grounded generator. Returns True if the file changed."""
    target = worktree / target_path
    if target_path.endswith(".py"):
        before = target.read_text(encoding="utf-8") if target.is_file() else ""
        proc = subprocess.run(
            ["ruff", "check", "--fix", "--no-cache", target_path],
            cwd=worktree,
            text=True,
            capture_output=True,
            check=False,
        )
        if proc.returncode not in (0, 1):
            return False
        after = target.read_text(encoding="utf-8") if target.is_file() else ""
        return after != before
    if target_path.endswith(".md"):
        return _generate_doc(worktree, target_path)
    return False


def _generate_doc(worktree: Path, target_path: str) -> bool:
    """Generate a minimal grounded Markdown file that links only to existing
    repository files, so the documentation gate passes deterministically."""
    target = worktree / target_path
    target.parent.mkdir(parents=True, exist_ok=True)
    readme = worktree / "README.md"
    lines = [f"# {target.stem.replace('_', ' ').title()}", ""]
    if readme.is_file():
        # Relative link from the target back to README.
        rel = _relative_link(target, readme)
        lines.append(f"See [README]({rel}).")
    else:
        lines.append("Project documentation index.")
    lines.append("")
    target.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return True


def _relative_link(from_file: Path, to_file: Path) -> str:
    import os

    return os.path.relpath(to_file, start=from_file.parent).replace("\\", "/")


def _run_gate(worktree: Path, commands: tuple[str, ...]) -> list[dict[str, Any]]:
    import os
    import shlex

    results: list[dict[str, Any]] = []
    env = dict(os.environ)
    source_root = Path(__file__).resolve().parents[1]
    current = env.get("PYTHONPATH")
    env["PYTHONPATH"] = f"{source_root}{os.pathsep}{current}" if current else str(source_root)
    for command in commands:
        try:
            proc = subprocess.run(shlex.split(command), cwd=worktree, env=env, text=True, capture_output=True, check=False)
        except (FileNotFoundError, OSError) as exc:
            # A missing gate binary is a gate failure, never a loop crash.
            results.append({"command": command, "exitCode": 127, "stdout": "", "stderr": f"{type(exc).__name__}: {exc}"})
            continue
        results.append({"command": command, "exitCode": proc.returncode, "stdout": proc.stdout.strip()[:2000], "stderr": proc.stderr.strip()[:2000]})
    return results


def _run_behaviour_gate(worktree: Path, test_command: str) -> bool:
    import os
    import shlex

    env = dict(os.environ)
    source_root = Path(__file__).resolve().parents[1]
    current = env.get("PYTHONPATH")
    env["PYTHONPATH"] = f"{source_root}{os.pathsep}{current}" if current else str(source_root)
    try:
        proc = subprocess.run(shlex.split(test_command), cwd=worktree, env=env, text=True, capture_output=True, check=False)
    except (FileNotFoundError, OSError):
        # Missing/unrunnable test binary fails the behaviour gate closed.
        return False
    return proc.returncode == 0


def _promote(
    project: Path,
    config: RepoGoalLoopConfig,
    applied: dict[str, Any],
    candidate: dict[str, Any],
    log: _EventLog,
    cycle: int,
) -> bool:
    """ff-only promotion of the verified cycle worktree into the project baseline.

    Stages ONLY the boundary-approved target path, then re-checks the actual
    staged file list against the boundary before committing — so a gate
    side-effect (a stray file, a write to a protected dir, a test cache) can never
    ride into the promoted baseline."""
    manager = applied["manager"]
    worktree = applied["worktree_obj"]
    worktree_path = Path(worktree.path)
    cycle_id = worktree.cycle_id
    target_path = candidate["targetPath"]
    try:
        # Stage ONLY the approved target, never `git add -A`.
        subprocess.run(["git", "add", "--", target_path], cwd=worktree_path, check=True, capture_output=True)
        staged_paths = [
            line.strip()
            for line in subprocess.run(["git", "diff", "--cached", "--name-only"], cwd=worktree_path, text=True, capture_output=True).stdout.splitlines()
            if line.strip()
        ]
        if not staged_paths:
            log.emit("PROMOTION_SKIPPED", cycle=cycle, payload={"reason": "no_staged_change", "target_path": target_path})
            return False
        # Defense in depth: the staged set must be exactly the approved target and
        # must not touch any boundary-protected surface.
        if set(staged_paths) != {target_path}:
            log.emit("PROMOTION_REFUSED", cycle=cycle, payload={"reason": "staged_outside_target", "target_path": target_path, "staged": staged_paths})
            return False
        if is_boundary_violation(staged_paths, read_only_dirs=_read_only_dirs(config)):
            log.emit("PROMOTION_REFUSED", cycle=cycle, payload={"reason": "staged_boundary_violation", "staged": staged_paths})
            return False
        subprocess.run(["git", "commit", "-q", "-m", f"arena: {candidate['findingId']}"], cwd=worktree_path, check=True, capture_output=True)
        merge = subprocess.run(
            ["git", "merge", "--ff-only", f"arena/cycle/{cycle_id}"],
            cwd=project,
            text=True,
            capture_output=True,
            check=False,
        )
        if merge.returncode != 0:
            log.emit("PROMOTION_FAILED", cycle=cycle, payload={"reason": "not_fast_forward", "stderr": merge.stderr.strip()[:500]})
            return False
        log.emit("PROMOTED", cycle=cycle, payload={"finding_id": candidate["findingId"], "target_path": target_path})
        log.emit("BASELINE_ADVANCED", cycle=cycle, payload={"finding_id": candidate["findingId"]})
        return True
    finally:
        manager.teardown(worktree)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(prog="python -m arena.repo_goal_loop")
    parser.add_argument("--project", required=True)
    parser.add_argument("--goal", required=True)
    parser.add_argument("--artifacts-root", required=True)
    parser.add_argument("--profile", default="active-development")
    parser.add_argument("--max-cycles", type=int, default=10)
    parser.add_argument("--allow-promotion", action="store_true")
    parser.add_argument("--no-dry-run", action="store_true")
    parser.add_argument("--test-command")
    args = parser.parse_args()
    result = run_repo_goal_loop(
        RepoGoalLoopConfig(
            project=Path(args.project),
            goal=args.goal,
            artifacts_root=Path(args.artifacts_root),
            profile=args.profile,
            max_cycles=args.max_cycles,
            dry_run=not args.no_dry_run,
            allow_promotion=args.allow_promotion,
            test_command=args.test_command,
        )
    )
    print(json.dumps({"cyclesRun": result.cycles_run, "promotions": result.promotions, "halted": result.halted_reason, "events": str(result.events_jsonl)}, indent=2))
