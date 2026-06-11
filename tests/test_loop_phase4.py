from __future__ import annotations

import asyncio
import subprocess
from pathlib import Path

from arena.budget import BudgetController
from arena.divergence import DivergenceDetector
from arena.events import EventLog
from arena.generated.models import Baseline, HaltReason, Run, RunnerName, Worktree
from arena.hypothesizer import Arm, SymbolicHypothesizer, UCB1Bandit
from arena.loop import LoopContext, run_loop
from arena.router import RunnerRouter
from arena.worktrees import GitPromoter, WorktreeManager
from scorer.engine import Scorer, ScoreRecord, ScoreVector
from verifier.engine import Verifier


def _run_model(git_oid: str) -> Run:
    return Run(
        id="run-1",
        north_star_id="north-star-1",
        scorer_lock_sha="c" * 64,
        config_sha="d" * 64,
        git_head_at_start=git_oid,
        started_ts=1.0,
    )


def _baseline(run_id: str, git_oid: str, score_record_id: str) -> Baseline:
    return Baseline(
        id="baseline-1",
        run_id=run_id,
        git_oid=git_oid,
        score_record_id=score_record_id,
        promoted_ts=1.0,
        is_active=True,
    )


def _dummy_score() -> ScoreRecord:
    return ScoreRecord(
        id="score-before",
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


class UnusedComponent:
    pass


class NoopScanner:
    async def scan(self, worktree):
        return {"ast_diff_pattern": "runtime_lookup"}


class CrashScanner:
    async def scan(self, worktree):
        raise RuntimeError("scanner boom")


class RecordingWorktrees:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.torn_down: list[Worktree] = []

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
        self.torn_down.append(worktree)


class FailingTeardownWorktrees(RecordingWorktrees):
    async def teardown(self, worktree: Worktree) -> None:
        self.torn_down.append(worktree)
        raise RuntimeError("teardown boom")


class CountingScorer:
    def __init__(self, scorer: Scorer) -> None:
        self.scorer = scorer
        self.score_repo_calls = 0
        self.scored_records: list[ScoreRecord] = []

    def score_repo(self, repo: Path) -> ScoreRecord:
        self.score_repo_calls += 1
        record = self.scorer.score_repo(repo)
        self.scored_records.append(record)
        return record

    def drift_check(self, active_score: ScoreRecord, worktree: Path) -> None:
        self.scorer.drift_check(active_score, worktree)


class CalibrationPatchRunner:
    name = RunnerName.ollama

    def __init__(self, patch_path: Path) -> None:
        self.patch_path = patch_path
        self.applied_hypothesis_ids: list[str] = []

    async def apply(self, hypothesis, worktree: Path) -> Path:
        self.applied_hypothesis_ids.append(hypothesis.id)
        subprocess.run(
            ["git", "apply", str(self.patch_path)],
            cwd=worktree,
            check=True,
            capture_output=True,
            text=True,
        )
        return self.patch_path


def test_run_loop_turns_budget_breach_into_halt_record(tmp_path) -> None:
    log = EventLog(tmp_path / "run-1", run_id="run-1")
    run = _run_model("a" * 40)
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
        active_score=_dummy_score(),
    )

    result = asyncio.run(run_loop(run, ctx))

    assert result.halt_record is not None
    assert result.halt_record.reason == HaltReason.BUDGET_EXHAUSTED_ZERO_PROMOTIONS
    assert log.read_events()[-1].type == "HALTED"


def test_run_loop_enforces_wall_clock_budget_before_starting_cycle(tmp_path, monkeypatch) -> None:
    log = EventLog(tmp_path / "run-1", run_id="run-1")
    run = _run_model("a" * 40)
    monkeypatch.setattr("arena.loop.time.time", lambda: 10.0)
    ctx = LoopContext(
        event_log=log,
        budget=BudgetController(wall_clock_seconds_cap=1, cycle_count_cap=99, start_ts=0.0),
        divergence=DivergenceDetector(log),
        worktrees=UnusedComponent(),
        scanner=UnusedComponent(),
        scorer=UnusedComponent(),
        hypothesizer=UnusedComponent(),
        router=UnusedComponent(),
        verifier=UnusedComponent(),
        promoter=UnusedComponent(),
        active_baseline=_baseline(run.id, "a" * 40, "score-before"),
        active_score=_dummy_score(),
    )

    result = asyncio.run(run_loop(run, ctx))

    assert result.halt_record is not None
    assert result.halt_record.reason == HaltReason.BUDGET_EXHAUSTED_ZERO_PROMOTIONS
    assert [event.type for event in log.read_events()] == ["RUN_STARTED", "HALTED"]


def test_run_loop_turns_unexpected_exception_into_halt_record_and_tears_down_worktree(tmp_path: Path) -> None:
    log = EventLog(tmp_path / "run-crash", run_id="run-1")
    run = _run_model("a" * 40)
    worktrees = RecordingWorktrees(tmp_path / "worktrees")
    ctx = LoopContext(
        event_log=log,
        budget=BudgetController(wall_clock_seconds_cap=999, cycle_count_cap=99),
        divergence=DivergenceDetector(log),
        worktrees=worktrees,
        scanner=CrashScanner(),
        scorer=UnusedComponent(),
        hypothesizer=UnusedComponent(),
        router=UnusedComponent(),
        verifier=UnusedComponent(),
        promoter=UnusedComponent(),
        active_baseline=_baseline(run.id, "a" * 40, "score-before"),
        active_score=_dummy_score(),
    )

    result = asyncio.run(run_loop(run, ctx))

    assert result.halt_record is not None
    assert result.halt_record.reason == HaltReason.RUNNER_UNAVAILABLE
    assert result.halt_record.detail is not None
    assert result.halt_record.detail.startswith("unexpected_exception:RuntimeError: scanner boom")
    assert [worktree.id for worktree in worktrees.torn_down] == ["cycle-1"]
    assert log.read_events()[-1].type == "HALTED"


def test_run_loop_records_cleanup_failure_without_masking_unexpected_halt(tmp_path: Path) -> None:
    log = EventLog(tmp_path / "run-crash-cleanup", run_id="run-1")
    run = _run_model("a" * 40)
    worktrees = FailingTeardownWorktrees(tmp_path / "worktrees")
    ctx = LoopContext(
        event_log=log,
        budget=BudgetController(wall_clock_seconds_cap=999, cycle_count_cap=99),
        divergence=DivergenceDetector(log),
        worktrees=worktrees,
        scanner=CrashScanner(),
        scorer=UnusedComponent(),
        hypothesizer=UnusedComponent(),
        router=UnusedComponent(),
        verifier=UnusedComponent(),
        promoter=UnusedComponent(),
        active_baseline=_baseline(run.id, "a" * 40, "score-before"),
        active_score=_dummy_score(),
    )

    result = asyncio.run(run_loop(run, ctx))

    event_types = [event.type for event in log.read_events()]
    assert result.halt_record is not None
    assert result.halt_record.detail is not None
    assert result.halt_record.detail.startswith("unexpected_exception:RuntimeError: scanner boom")
    assert "WORKTREE_CLEANUP_FAILED" in event_types
    assert event_types[-1] == "HALTED"


def test_verified_discard_emits_single_verdict_and_disagreement(
    project_root: Path,
    calibration_repo: Path,
    tmp_path: Path,
) -> None:
    scorer = Scorer(project_root)
    score_before = scorer.score_repo(calibration_repo)
    run = _run_model(score_before.git_oid)
    log = EventLog(tmp_path / "run-1", run_id=run.id)
    arm = Arm(
        technique_tag="runtime",
        target_cluster="core",
        target_files=("src/validatorlib/core.py",),
        intent_template="Rename a private helper in {target_cluster}",
    )
    hypothesizer = SymbolicHypothesizer(UCB1Bandit([arm]))
    patch_runner = CalibrationPatchRunner(
        project_root / ".arena" / "calibration" / "diffs" / "positive" / "P-1.patch"
    )
    router = RunnerRouter(primary=patch_runner, fallback=patch_runner)
    ctx = LoopContext(
        event_log=log,
        budget=BudgetController(wall_clock_seconds_cap=14400, cycle_count_cap=99),
        divergence=DivergenceDetector(log, scorer_verifier_disagree_max_consecutive=1),
        worktrees=WorktreeManager(repo=calibration_repo, worktree_root=tmp_path / "worktrees"),
        scanner=NoopScanner(),
        scorer=scorer,
        hypothesizer=hypothesizer,
        router=router,
        verifier=Verifier(),
        promoter=GitPromoter(main_repo=calibration_repo),
        active_baseline=_baseline(run.id, score_before.git_oid, score_before.id),
        active_score=score_before,
    )

    result = asyncio.run(run_loop(run, ctx))

    event_types = [event.type for event in log.read_events()]
    assert result.promotions_total == 0
    assert result.halt_record is not None
    assert event_types.count("VERDICT_DECIDED") == 1
    assert "SCORER_VERIFIER_DISAGREEMENT" in event_types
    assert "PROMOTED" not in event_types
    assert subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=calibration_repo, text=True).strip() == score_before.git_oid


def test_calibration_loop_promotes_one_positive_patch(
    project_root: Path,
    calibration_repo: Path,
    tmp_path: Path,
) -> None:
    scorer = Scorer(project_root)
    score_before = scorer.score_repo(calibration_repo)
    counting_scorer = CountingScorer(scorer)
    run = _run_model(score_before.git_oid)
    log = EventLog(tmp_path / "run-1", run_id=run.id)
    arm = Arm(
        technique_tag="runtime",
        target_cluster="core",
        target_files=("src/validatorlib/core.py",),
        intent_template="Improve {target_cluster} because runtime score improves with {technique_tag}",
    )
    hypothesizer = SymbolicHypothesizer(UCB1Bandit([arm]))
    patch_runner = CalibrationPatchRunner(
        project_root / ".arena" / "calibration" / "diffs" / "positive" / "P-1.patch"
    )
    router = RunnerRouter(primary=patch_runner, fallback=patch_runner)
    ctx = LoopContext(
        event_log=log,
        budget=BudgetController(wall_clock_seconds_cap=14400, cycle_count_cap=60),
        divergence=DivergenceDetector(log),
        worktrees=WorktreeManager(repo=calibration_repo, worktree_root=tmp_path / "worktrees"),
        scanner=NoopScanner(),
        scorer=counting_scorer,
        hypothesizer=hypothesizer,
        router=router,
        verifier=Verifier(),
        promoter=GitPromoter(main_repo=calibration_repo),
        active_baseline=_baseline(run.id, score_before.git_oid, score_before.id),
        active_score=score_before,
        stop_after_promotions=1,
    )

    result = asyncio.run(run_loop(run, ctx))

    event_types = [event.type for event in log.read_events()]
    assert result.promotions_total == 1
    assert result.halt_record is None
    assert "PROMOTED" in event_types
    assert "BASELINE_ADVANCED" in event_types
    assert counting_scorer.score_repo_calls == 1
    assert ctx.active_score == counting_scorer.scored_records[0]
    assert subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=calibration_repo, text=True).strip() == ctx.active_baseline.git_oid
    assert patch_runner.applied_hypothesis_ids
