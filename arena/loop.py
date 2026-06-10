from __future__ import annotations

import inspect
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from arena.boundary import is_boundary_violation
from arena.budget import BudgetBreach, BudgetController
from arena.divergence import Diverged, DivergenceDetector
from arena.events import EventLog
from arena.generated.models import (
    Baseline,
    Cycle,
    HaltReason,
    HaltRecord,
    LoopState,
    RejectReason,
    Run,
    Verdict,
    VerdictOutcome,
    Worktree,
)
from scorer.goal_config import DEFAULT_GOAL_CONFIG, load_goal_config


@dataclass
class LoopContext:
    event_log: EventLog
    budget: BudgetController
    divergence: DivergenceDetector
    worktrees: Any
    scanner: Any
    scorer: Any
    hypothesizer: Any
    router: Any
    verifier: Any
    promoter: Any
    active_baseline: Baseline
    active_score: Any
    stop_after_promotions: int | None = None
    structural_validator: Any | None = None
    ledger: Any | None = None
    evidence_writer: Any | None = None


@dataclass(frozen=True)
class LoopResult:
    promotions_total: int
    cycles_total: int
    halt_record: HaltRecord | None = None


async def run_loop(run: Run, ctx: LoopContext) -> LoopResult:
    state = LoopState.SCAN
    cycle: Cycle | None = None
    worktree: Worktree | None = None
    hypothesis = None
    verdict: Verdict | None = None
    patch_path: Path | None = None
    project: Any | None = None
    promotions_total = 0
    cycles_total = 0
    _emit_run_started(run, ctx)
    while True:
        try:
            ctx.budget.check(now=time.time())
            ctx.divergence.check_and_raise(run.id)
            match state:
                case LoopState.SCAN:
                    cycles_total += 1
                    ctx.budget.record_cycle_started()
                    cycle = Cycle(
                        id=f"cycle-{cycles_total}",
                        run_id=run.id,
                        ordinal=cycles_total,
                        entered_state=LoopState.SCAN,
                        started_ts=time.time(),
                        baseline_id_before=ctx.active_baseline.id,
                    )
                    created_worktree = await _call(ctx.worktrees.create, cycle.id, ctx.active_baseline.git_oid)
                    assert isinstance(created_worktree, Worktree)
                    worktree = created_worktree
                    ctx.event_log.emit(
                        "CYCLE_STARTED",
                        cycle_id=cycle.id,
                        payload={"ordinal": cycle.ordinal, "worktree_id": worktree.id},
                    )
                    project = await _call(ctx.scanner.scan, worktree)
                    await _call(ctx.scorer.drift_check, ctx.active_score, Path(worktree.path))
                    ctx.event_log.emit("SCAN_COMPLETE", cycle_id=cycle.id, payload={"baseline_id": ctx.active_baseline.id})
                    state = LoopState.HYPOTHESIZE
                case LoopState.HYPOTHESIZE:
                    assert cycle is not None and project is not None
                    proposal = ctx.hypothesizer.propose(cycle_id=cycle.id, ast_diff_pattern=_ast_diff_pattern(project))
                    hypothesis = proposal.hypothesis
                    ctx.event_log.emit(
                        "HYPOTHESIS_PROPOSED",
                        cycle_id=cycle.id,
                        payload={
                            "hypothesis_id": hypothesis.id,
                            "fingerprint_id": hypothesis.fingerprint_id,
                            "target_files": list(hypothesis.target_files),
                            "bandit_arm": getattr(proposal.arm, "key", None),
                        },
                    )
                    assert worktree is not None
                    if _boundary_violation_for_worktree(
                        hypothesis.target_files,
                        Path(worktree.path),
                        event_log=ctx.event_log,
                        cycle_id=cycle.id,
                    ):
                        verdict = _discard_verdict(hypothesis.id, ctx.active_score.id, RejectReason.BOUNDARY_VIOLATION)
                        ctx.event_log.emit("BOUNDARY_VIOLATION", cycle_id=cycle.id, payload={"hypothesis_id": hypothesis.id})
                        state = LoopState.DISCARD
                    elif ctx.ledger is not None and ctx.ledger.has_failed(hypothesis.fingerprint_id):
                        verdict = _discard_verdict(hypothesis.id, ctx.active_score.id, RejectReason.FINGERPRINT_COLLISION)
                        state = LoopState.DISCARD
                    else:
                        state = LoopState.APPLY
                case LoopState.APPLY:
                    assert cycle is not None and worktree is not None and hypothesis is not None
                    apply_result = await ctx.router.apply(hypothesis, Path(worktree.path))
                    for event in apply_result.events:
                        ctx.event_log.emit(event.type, cycle_id=cycle.id, payload=event.payload)
                    if not apply_result.success:
                        verdict = _discard_verdict(hypothesis.id, ctx.active_score.id, apply_result.error_reason or RejectReason.RUNNER_ERROR)
                        state = LoopState.DISCARD
                    else:
                        patch_path = apply_result.patch_path
                        ctx.event_log.emit(
                            "PATCH_APPLIED",
                            cycle_id=cycle.id,
                            payload={"hypothesis_id": hypothesis.id, "patch_path": str(patch_path)},
                        )
                        if not await _structural_ok(ctx, hypothesis, patch_path, worktree):
                            verdict = _discard_verdict(hypothesis.id, ctx.active_score.id, RejectReason.STRUCTURAL_VALIDATION_FAIL)
                            state = LoopState.DISCARD
                        else:
                            state = LoopState.VERIFY
                case LoopState.VERIFY:
                    assert cycle is not None and worktree is not None and hypothesis is not None and patch_path is not None
                    verification = ctx.verifier.verify_worktree(
                        hypothesis_id=hypothesis.id,
                        reasoning=hypothesis.intent,
                        score_before=ctx.active_score,
                        worktree=Path(worktree.path),
                        scorer=ctx.scorer,
                    )
                    verified_verdict: Verdict = verification.verdict
                    verdict = verified_verdict
                    ctx.event_log.emit("ABLATION_RESULT", cycle_id=cycle.id, payload=verification.ablation_result.model_dump(mode="json"))
                    state = LoopState.PROMOTE if verified_verdict.outcome == VerdictOutcome.PROMOTED else LoopState.DISCARD
                case LoopState.PROMOTE:
                    assert cycle is not None and worktree is not None and verdict is not None and hypothesis is not None
                    score_before = ctx.active_score
                    ctx.event_log.emit("VERDICT_DECIDED", cycle_id=cycle.id, payload=_verdict_payload(verdict, hypothesis.fingerprint_id))
                    _emit_disagreement_if_needed(ctx, cycle.id, verdict)
                    packaged = await _call(
                        ctx.promoter.promote,
                        verdict,
                        worktree,
                        run_id=run.id,
                        score_record_id=verdict.score_after_id or verdict.score_before_id,
                    )
                    score_after = ctx.scorer.score_repo(Path(worktree.path))
                    promotions_total += 1
                    ctx.budget.record_promotion()
                    candidate_only = bool(getattr(ctx.promoter, "candidate_only", False))
                    candidate_branch = _candidate_branch(ctx.promoter, cycle.id) if candidate_only else None
                    if candidate_only:
                        ctx.event_log.emit(
                            "CANDIDATE_PACKAGED",
                            cycle_id=cycle.id,
                            payload={
                                "verdict_id": verdict.id,
                                "candidate_branch": candidate_branch,
                                "candidate": packaged.model_dump(mode="json"),
                            },
                        )
                    else:
                        ctx.active_baseline = packaged
                        ctx.active_score = score_after
                        ctx.event_log.emit("PROMOTED", cycle_id=cycle.id, payload={"verdict_id": verdict.id})
                        ctx.event_log.emit("BASELINE_ADVANCED", cycle_id=cycle.id, payload=ctx.active_baseline.model_dump(mode="json"))
                    if ctx.ledger is not None:
                        _record_ledger_success(
                            ctx.ledger,
                            fingerprint_id=hypothesis.fingerprint_id,
                            hypothesis_id=hypothesis.id,
                            cycle_id=cycle.id,
                        )
                    if ctx.evidence_writer is not None:
                        ctx.evidence_writer.write_cycle_evidence(
                            cycle_id=cycle.id,
                            event_log=ctx.event_log,
                            budget=ctx.budget,
                            worktree=worktree,
                            score_before=score_before,
                            score_after=score_after,
                            verdict=verdict,
                            patch_path=patch_path,
                            candidate=packaged if candidate_only else None,
                            candidate_branch=candidate_branch,
                        )
                    await _cleanup(ctx, worktree, cycle.id)
                    if ctx.stop_after_promotions is not None and promotions_total >= ctx.stop_after_promotions:
                        ctx.event_log.emit("RUN_COMPLETED", payload={"promotions_total": promotions_total, "cycles_total": cycles_total})
                        return LoopResult(promotions_total=promotions_total, cycles_total=cycles_total)
                    state = LoopState.SCAN
                case LoopState.DISCARD:
                    assert cycle is not None and worktree is not None and verdict is not None and hypothesis is not None
                    if ctx.ledger is not None:
                        _record_ledger_failure(
                            ctx.ledger,
                            fingerprint_id=hypothesis.fingerprint_id,
                            hypothesis_id=hypothesis.id,
                            cycle_id=cycle.id,
                            reject_reason=_enum_value(verdict.reject_reason) if verdict.reject_reason else "UNKNOWN",
                        )
                    ctx.event_log.emit("VERDICT_DECIDED", cycle_id=cycle.id, payload=_verdict_payload(verdict, hypothesis.fingerprint_id))
                    _emit_disagreement_if_needed(ctx, cycle.id, verdict)
                    if ctx.evidence_writer is not None:
                        ctx.evidence_writer.write_cycle_evidence(
                            cycle_id=cycle.id,
                            event_log=ctx.event_log,
                            budget=ctx.budget,
                            worktree=worktree,
                            score_before=ctx.active_score,
                            score_after=None,
                            verdict=verdict,
                            patch_path=patch_path,
                        )
                    await _cleanup(ctx, worktree, cycle.id)
                    state = LoopState.SCAN
                case LoopState.HALT:
                    return LoopResult(promotions_total=promotions_total, cycles_total=cycles_total)
        except BudgetBreach as breach:
            halt_record = _halt(ctx, run.id, breach.reason, breach.detail)
            _write_halt_evidence(ctx, run.id, halt_record)
            return LoopResult(promotions_total=promotions_total, cycles_total=cycles_total, halt_record=halt_record)
        except Diverged as diverged:
            halt_record = _halt(ctx, run.id, diverged.reason, diverged.detail)
            _write_halt_evidence(ctx, run.id, halt_record)
            return LoopResult(promotions_total=promotions_total, cycles_total=cycles_total, halt_record=halt_record)


async def _call(func, *args, **kwargs):
    result = func(*args, **kwargs)
    if inspect.isawaitable(result):
        return await result
    return result


def _emit_run_started(run: Run, ctx: LoopContext) -> None:
    if not any(event.type == "RUN_STARTED" for event in ctx.event_log.read_events()):
        ctx.event_log.emit("RUN_STARTED", payload={"run_id": run.id, "git_head_at_start": run.git_head_at_start})


def _ast_diff_pattern(project: Any) -> str:
    if isinstance(project, dict):
        return str(project.get("ast_diff_pattern", ""))
    return str(getattr(project, "ast_diff_pattern", ""))


def _boundary_violation_for_worktree(
    target_files,
    worktree: Path,
    *,
    event_log: EventLog | None = None,
    cycle_id: str | None = None,
) -> bool:
    goal_path = worktree / DEFAULT_GOAL_CONFIG
    if not goal_path.exists():
        if event_log is not None:
            event_log.emit(
                "GOAL_CONFIG_FALLBACK",
                cycle_id=cycle_id,
                payload={"reason": "missing_goal_config", "path": str(goal_path)},
            )
        return is_boundary_violation(target_files)
    goal_config = load_goal_config(worktree)
    return is_boundary_violation(target_files, goal_config=goal_config)


async def _structural_ok(ctx: LoopContext, hypothesis, patch_path: Path | None, worktree: Worktree) -> bool:
    if ctx.structural_validator is None:
        return True
    return bool(await _call(ctx.structural_validator.validate, hypothesis, patch_path, worktree))


async def _cleanup(ctx: LoopContext, worktree: Worktree, cycle_id: str) -> None:
    await _call(ctx.worktrees.teardown, worktree)
    ctx.event_log.emit("WORKTREE_TORN_DOWN", cycle_id=cycle_id, payload={"worktree_id": worktree.id})
    ctx.event_log.emit("CYCLE_ENDED", cycle_id=cycle_id, payload={"cycle_id": cycle_id})


def _discard_verdict(hypothesis_id: str, score_before_id: str, reason: RejectReason) -> Verdict:
    return Verdict(
        id=f"verdict-{hypothesis_id}-{reason.value.lower()}",
        hypothesis_id=hypothesis_id,
        outcome=VerdictOutcome.DISCARDED,
        reject_reason=reason,
        score_before_id=score_before_id,
        tests_passed=False,
        decided_ts=time.time(),
    )


def _emit_disagreement_if_needed(ctx: LoopContext, cycle_id: str, verdict: Verdict) -> None:
    if not _is_scorer_verifier_disagreement(verdict):
        return
    ctx.event_log.emit(
        "SCORER_VERIFIER_DISAGREEMENT",
        cycle_id=cycle_id,
        payload={
            "verdict_id": verdict.id,
            "hypothesis_id": verdict.hypothesis_id,
            "score_delta": verdict.score_delta,
            "outcome": _enum_value(verdict.outcome),
            "reject_reason": _enum_value(verdict.reject_reason) if verdict.reject_reason else None,
        },
    )


def _is_scorer_verifier_disagreement(verdict: Verdict) -> bool:
    if verdict.score_delta is None:
        return False
    scorer_would_promote = verdict.score_delta > 0
    verifier_promoted = _enum_value(verdict.outcome) == "PROMOTED"
    return scorer_would_promote != verifier_promoted


def _verdict_payload(verdict: Verdict, fingerprint_id: str) -> dict[str, Any]:
    return {
        "verdict_id": verdict.id,
        "hypothesis_id": verdict.hypothesis_id,
        "fingerprint_id": fingerprint_id,
        "outcome": _enum_value(verdict.outcome),
        "reject_reason": _enum_value(verdict.reject_reason) if verdict.reject_reason else None,
        "score_delta": verdict.score_delta,
    }


def _enum_value(value: Any) -> str:
    return str(getattr(value, "value", value))


def _candidate_branch(promoter: Any, cycle_id: str) -> str | None:
    branch_name = getattr(promoter, "branch_name", None)
    if callable(branch_name):
        return str(branch_name(cycle_id))
    return None


def _record_ledger_failure(
    ledger: Any,
    *,
    fingerprint_id: str,
    hypothesis_id: str,
    cycle_id: str,
    reject_reason: str,
) -> None:
    record_failure = getattr(ledger, "record_failure", None)
    if callable(record_failure):
        record_failure(
            fingerprint_id=fingerprint_id,
            hypothesis_id=hypothesis_id,
            cycle_id=cycle_id,
            reject_reason=reject_reason,
        )
        return
    ledger.record(
        fingerprint_id=fingerprint_id,
        hypothesis_id=hypothesis_id,
        cycle_id=cycle_id,
        outcome="DISCARDED",
        reject_reason=reject_reason,
    )


def _record_ledger_success(ledger: Any, *, fingerprint_id: str, hypothesis_id: str, cycle_id: str) -> None:
    record_success = getattr(ledger, "record_success", None)
    if callable(record_success):
        record_success(fingerprint_id=fingerprint_id, hypothesis_id=hypothesis_id, cycle_id=cycle_id)
        return
    ledger.record(
        fingerprint_id=fingerprint_id,
        hypothesis_id=hypothesis_id,
        cycle_id=cycle_id,
        outcome="PROMOTED",
        reject_reason=None,
    )


def _write_halt_evidence(ctx: LoopContext, run_id: str, halt_record: HaltRecord) -> None:
    if ctx.evidence_writer is None:
        return
    ctx.evidence_writer.write_halt_evidence(
        run_id=run_id,
        event_log=ctx.event_log,
        budget=ctx.budget,
        halt_record=halt_record,
    )


def _halt(ctx: LoopContext, run_id: str, reason: HaltReason, detail: str) -> HaltRecord:
    event = ctx.event_log.emit("HALTED", payload={"reason": reason.value, "detail": detail}, level="error")
    return HaltRecord(
        id=f"halt-{run_id}-{event.seq}",
        run_id=run_id,
        reason=reason,
        detail=detail,
        last_event_seq=event.seq,
        ts=event.ts,
    )
