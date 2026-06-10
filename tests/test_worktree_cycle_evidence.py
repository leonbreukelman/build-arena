from __future__ import annotations

import asyncio
import json
import subprocess
from dataclasses import replace
from pathlib import Path

import pytest

from arena.budget import BudgetController
from arena.divergence import DivergenceDetector
from arena.events import EventLog
from arena.evidence import CycleEvidenceWriter
from arena.generated.models import Baseline, HaltReason, Run, RunnerName, Worktree
from arena.hypothesizer import Arm, SymbolicHypothesizer, UCB1Bandit
from arena.ledger import FingerprintFailureLedger
from arena.loop import LoopContext, run_loop
from arena.proposer_hypothesizer import TargetSelectionHypothesizer
from arena.router import RunnerRouter
from arena.runners.diff_proposer import (
    DiffProposalRequest,
    DiffProposalResponse,
    DiffProposerRunner,
)
from arena.target_picker import TargetSelection, select_targets
from arena.worktrees import CandidatePackager, WorktreeManager
from scorer.engine import Scorer, ScoreRecord, ScoreVector
from scorer.goal_config import GoalConfigError
from verifier.engine import Verifier


def _git(cwd: Path, *args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=cwd, text=True).strip()


def _run_model(git_oid: str = "a" * 40) -> Run:
    return Run(
        id="run-evidence",
        north_star_id="north-star",
        scorer_lock_sha="c" * 64,
        config_sha="d" * 64,
        git_head_at_start=git_oid,
        started_ts=1.0,
    )


def _baseline(run_id: str, git_oid: str, score_record_id: str) -> Baseline:
    return Baseline(
        id="baseline-evidence",
        run_id=run_id,
        git_oid=git_oid,
        score_record_id=score_record_id,
        promoted_ts=1.0,
        is_active=True,
    )


def _score_record(id: str = "score-before") -> ScoreRecord:
    return ScoreRecord(
        id=id,
        git_oid="a" * 40,
        scorer_lock_sha="c" * 64,
        vector=ScoreVector(
            composite=1.0,
            coverage_pct=90.0,
            pyright_errors=0,
            ruff_violations=0,
            cyclomatic_avg=1.0,
            runtime_p95_ms=10.0,
            tests_pass=True,
        ),
        computed_ts=1.0,
    )


class NoopScanner:
    async def scan(self, worktree):
        return {"ast_diff_pattern": "runtime_lookup"}


class UnusedComponent:
    pass


class NoopDriftScorer:
    async def drift_check(self, active_score, worktree: Path) -> None:
        return None


class PlainWorktrees:
    def __init__(self, root: Path) -> None:
        self.root = root

    async def create(self, cycle_id: str, base_oid: str) -> Worktree:
        path = self.root / cycle_id
        path.mkdir(parents=True, exist_ok=True)
        return Worktree(
            id=cycle_id,
            cycle_id=cycle_id,
            path=str(path),
            base_git_oid=base_oid,
            created_ts=1.0,
        )

    async def teardown(self, worktree: Worktree) -> None:
        return None


class PlainScanner:
    async def scan(self, worktree):
        return {"ast_diff_pattern": "plain"}


class MalformedGoalScanner:
    async def scan(self, worktree):
        path = Path(worktree.path) / ".arena" / "goal.toml"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text('schema_version = 123\nproject_id = "bad"\n', encoding="utf-8")
        return {"ast_diff_pattern": "malformed-goal-config"}


class CalibrationPatchRunner:
    name = RunnerName.ollama

    def __init__(self, patch_path: Path) -> None:
        self.patch_path = patch_path

    async def apply(self, hypothesis, worktree: Path) -> Path:
        subprocess.run(["git", "apply", str(self.patch_path)], cwd=worktree, check=True, capture_output=True, text=True)
        return self.patch_path


class StaticDiffTransport:
    def __init__(self, diff_text: str) -> None:
        self.diff_text = diff_text
        self.requests: list[DiffProposalRequest] = []

    def propose(self, request: DiffProposalRequest) -> DiffProposalResponse:
        self.requests.append(request)
        return DiffProposalResponse(
            diff_text=self.diff_text,
            intent="score improves because runtime drops",
            provenance={"transport": "static-test-fixture"},
        )


def test_missing_goal_config_boundary_fallback_is_evented(tmp_path: Path) -> None:
    log = EventLog(tmp_path / "run-missing-goal", run_id="run-evidence")
    arm = Arm(
        technique_tag="boundary",
        target_cluster="scorer",
        target_files=("scorer/engine.py",),
        intent_template="Touch {target_cluster}",
    )
    ctx = LoopContext(
        event_log=log,
        budget=BudgetController(wall_clock_seconds_cap=14400, cycle_count_cap=2),
        divergence=DivergenceDetector(log),
        worktrees=PlainWorktrees(tmp_path / "plain-worktrees"),
        scanner=PlainScanner(),
        scorer=NoopDriftScorer(),
        hypothesizer=SymbolicHypothesizer(UCB1Bandit([arm])),
        router=UnusedComponent(),
        verifier=UnusedComponent(),
        promoter=UnusedComponent(),
        active_baseline=_baseline("run-evidence", "a" * 40, "score-before"),
        active_score=_score_record(),
    )

    asyncio.run(run_loop(_run_model(), ctx))

    event_types = [event.type for event in log.read_events()]
    assert "GOAL_CONFIG_FALLBACK" in event_types
    assert "BOUNDARY_VIOLATION" in event_types


def test_malformed_present_goal_config_fails_closed(tmp_path: Path) -> None:
    log = EventLog(tmp_path / "run-malformed-goal", run_id="run-evidence")
    arm = Arm(
        technique_tag="runtime",
        target_cluster="core",
        target_files=("src/core.py",),
        intent_template="Improve {target_cluster}",
    )
    ctx = LoopContext(
        event_log=log,
        budget=BudgetController(wall_clock_seconds_cap=14400, cycle_count_cap=60),
        divergence=DivergenceDetector(log),
        worktrees=PlainWorktrees(tmp_path / "plain-worktrees"),
        scanner=MalformedGoalScanner(),
        scorer=NoopDriftScorer(),
        hypothesizer=SymbolicHypothesizer(UCB1Bandit([arm])),
        router=UnusedComponent(),
        verifier=UnusedComponent(),
        promoter=UnusedComponent(),
        active_baseline=_baseline("run-evidence", "a" * 40, "score-before"),
        active_score=_score_record(),
    )

    with pytest.raises(GoalConfigError):
        asyncio.run(run_loop(_run_model(), ctx))

    assert "GOAL_CONFIG_FALLBACK" not in [event.type for event in log.read_events()]


def test_worktree_cycle_packages_candidate_branch_and_writes_mechanical_evidence(
    project_root: Path,
    calibration_repo: Path,
    tmp_path: Path,
) -> None:
    main_head = _git(calibration_repo, "rev-parse", "HEAD")
    scorer = Scorer(project_root)
    score_before = scorer.score_repo(calibration_repo)
    run = _run_model(score_before.git_oid)
    log = EventLog(tmp_path / "run-1", run_id=run.id)
    worktree_root = tmp_path / "worktrees"
    evidence = CycleEvidenceWriter(root=tmp_path / "evidence", worktree_root=worktree_root)
    arm = Arm(
        technique_tag="runtime",
        target_cluster="core",
        target_files=("src/validatorlib/core.py",),
        intent_template="Improve {target_cluster} because runtime score improves with {technique_tag}",
    )
    patch_runner = CalibrationPatchRunner(
        project_root / ".arena" / "calibration" / "diffs" / "positive" / "P-1.patch"
    )
    ctx = LoopContext(
        event_log=log,
        budget=BudgetController(wall_clock_seconds_cap=14400, cycle_count_cap=60),
        divergence=DivergenceDetector(log),
        worktrees=WorktreeManager(repo=calibration_repo, worktree_root=worktree_root),
        scanner=NoopScanner(),
        scorer=scorer,
        hypothesizer=SymbolicHypothesizer(UCB1Bandit([arm])),
        router=RunnerRouter(primary=patch_runner, fallback=patch_runner),
        verifier=Verifier(),
        promoter=CandidatePackager(main_repo=calibration_repo),
        active_baseline=_baseline(run.id, score_before.git_oid, score_before.id),
        active_score=score_before,
        stop_after_promotions=1,
        evidence_writer=evidence,
    )

    result = asyncio.run(run_loop(run, ctx))

    assert result.promotions_total == 1
    assert _git(calibration_repo, "rev-parse", "HEAD") == main_head
    candidate_oid = _git(calibration_repo, "rev-parse", "arena/candidate/cycle-1")
    assert candidate_oid != main_head
    event_types = [event.type for event in log.read_events()]
    assert "CANDIDATE_PACKAGED" in event_types
    assert "BASELINE_ADVANCED" not in event_types
    payload = json.loads((tmp_path / "evidence" / "cycle-1.json").read_text(encoding="utf-8"))
    assert payload["schema_version"] == "cycle-evidence/v1"
    assert payload["cycle_id"] == "cycle-1"
    assert payload["worktree_root"] == str(worktree_root.resolve())
    assert payload["budget"]["cycle_count_cap"] == 60
    assert payload["score_before"]["id"] == score_before.id
    assert payload["verdict"]["outcome"] == "PROMOTED"
    assert payload["candidate"]["branch"] == "arena/candidate/cycle-1"
    assert payload["patch"]["added_lines"] > 0
    assert payload["events"][0]["type"] == "RUN_STARTED"
    assert "success claim" not in json.dumps(payload).lower()


def test_target_picker_diff_proposer_cycle_packages_candidate_branch(
    project_root: Path,
    calibration_repo: Path,
    tmp_path: Path,
) -> None:
    scorer = Scorer(project_root)
    score_before = scorer.score_repo(calibration_repo)
    run = _run_model(score_before.git_oid)
    log = EventLog(tmp_path / "run-diff-proposer", run_id=run.id)
    worktree_root = tmp_path / "worktrees"
    raw_selection = select_targets(calibration_repo, max_candidates=5)
    core_candidate = next(candidate for candidate in raw_selection.candidates if candidate.path == "src/validatorlib/core.py")
    selection = TargetSelection(
        id=f"{raw_selection.id}-core",
        version=raw_selection.version,
        git_oid=raw_selection.git_oid,
        goal_config_sha=raw_selection.goal_config_sha,
        goal_config_schema_version=raw_selection.goal_config_schema_version,
        candidate_count=1,
        omitted_count=0,
        candidates=(replace(core_candidate, rank=1),),
    )
    patch_text = (project_root / ".arena" / "calibration" / "diffs" / "positive" / "P-1.patch").read_text(
        encoding="utf-8"
    )
    transport = StaticDiffTransport(patch_text)
    runner = DiffProposerRunner(
        transport=transport,
        success_criterion="score improves because runtime drops",
    )
    ctx = LoopContext(
        event_log=log,
        budget=BudgetController(wall_clock_seconds_cap=14400, cycle_count_cap=60),
        divergence=DivergenceDetector(log),
        worktrees=WorktreeManager(repo=calibration_repo, worktree_root=worktree_root),
        scanner=NoopScanner(),
        scorer=scorer,
        hypothesizer=TargetSelectionHypothesizer(
            selection=selection,
            success_criterion="score improves because runtime drops",
        ),
        router=RunnerRouter(primary=runner, fallback=runner),
        verifier=Verifier(),
        promoter=CandidatePackager(main_repo=calibration_repo),
        active_baseline=_baseline(run.id, score_before.git_oid, score_before.id),
        active_score=score_before,
        stop_after_promotions=1,
        evidence_writer=CycleEvidenceWriter(root=tmp_path / "evidence", worktree_root=worktree_root),
    )

    result = asyncio.run(run_loop(run, ctx))

    assert result.promotions_total == 1
    assert len(transport.requests) == 1
    assert transport.requests[0].target_path == "src/validatorlib/core.py"
    assert transport.requests[0].goal_config_sha == selection.goal_config_sha
    assert transport.requests[0].success_criterion == "score improves because runtime drops"
    assert _git(calibration_repo, "rev-parse", "arena/candidate/cycle-1")
    payload = json.loads((tmp_path / "evidence" / "cycle-1.json").read_text(encoding="utf-8"))
    assert payload["candidate"]["branch"] == "arena/candidate/cycle-1"
    assert payload["patch"]["path"].endswith(".patch")
    assert payload["patch"]["sha256"] is not None


def test_loop_records_failures_through_failure_ledger_interface(
    project_root: Path,
    calibration_repo: Path,
    tmp_path: Path,
) -> None:
    scorer = Scorer(project_root)
    score_before = scorer.score_repo(calibration_repo)
    run = _run_model(score_before.git_oid)
    log = EventLog(tmp_path / "run-ledger", run_id=run.id)
    ledger = FingerprintFailureLedger(tmp_path / "ledger.jsonl")
    arm = Arm(
        technique_tag="boundary",
        target_cluster="scorer",
        target_files=("scorer/engine.py",),
        intent_template="Touch {target_cluster}",
    )
    ctx = LoopContext(
        event_log=log,
        budget=BudgetController(wall_clock_seconds_cap=14400, cycle_count_cap=2),
        divergence=DivergenceDetector(log),
        worktrees=WorktreeManager(repo=calibration_repo, worktree_root=tmp_path / "worktrees"),
        scanner=NoopScanner(),
        scorer=scorer,
        hypothesizer=SymbolicHypothesizer(UCB1Bandit([arm])),
        router=UnusedComponent(),
        verifier=UnusedComponent(),
        promoter=UnusedComponent(),
        active_baseline=_baseline(run.id, score_before.git_oid, score_before.id),
        active_score=score_before,
        ledger=ledger,
    )

    result = asyncio.run(run_loop(run, ctx))

    assert result.halt_record is not None
    rows = ledger.iter_records()
    assert len(rows) == 1
    assert rows[0]["outcome"] == "DISCARDED"
    assert rows[0]["reject_reason"] == "BOUNDARY_VIOLATION"
    assert rows[0]["cycle_id"] == "cycle-1"


def test_budget_breach_writes_halt_evidence(tmp_path: Path) -> None:
    run = _run_model("a" * 40)
    log = EventLog(tmp_path / "run-halt", run_id=run.id)
    evidence = CycleEvidenceWriter(root=tmp_path / "evidence", worktree_root=tmp_path / "worktrees")
    ctx = LoopContext(
        event_log=log,
        budget=BudgetController(wall_clock_seconds_cap=999, cycle_count_cap=0, start_ts=0.0),
        divergence=DivergenceDetector(log),
        worktrees=UnusedComponent(),
        scanner=UnusedComponent(),
        scorer=UnusedComponent(),
        hypothesizer=UnusedComponent(),
        router=UnusedComponent(),
        verifier=UnusedComponent(),
        promoter=UnusedComponent(),
        active_baseline=_baseline(run.id, "a" * 40, "score-before"),
        active_score=_score_record(),
        evidence_writer=evidence,
    )

    result = asyncio.run(run_loop(run, ctx))

    assert result.halt_record is not None
    assert result.halt_record.reason == HaltReason.BUDGET_EXHAUSTED_ZERO_PROMOTIONS
    payload = json.loads((tmp_path / "evidence" / "halt-run-evidence.json").read_text(encoding="utf-8"))
    assert payload["schema_version"] == "halt-evidence/v1"
    assert payload["halt"]["reason"] == "BUDGET_EXHAUSTED_ZERO_PROMOTIONS"
    assert payload["budget"]["cycle_count_cap"] == 0
    assert [event["type"] for event in payload["events"]] == ["RUN_STARTED", "HALTED"]
