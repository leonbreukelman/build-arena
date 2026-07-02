from __future__ import annotations

import ast
import asyncio
import json
import runpy
import sqlite3
import subprocess
import sys
import tomllib
from pathlib import Path
from typing import Any, cast

import pytest

import arena.decomposer as decomposer
import arena.loop as loop_module
import scorer.engine as scorer_engine
from arena.boundary import is_boundary_violation
from arena.budget import BudgetBreach, BudgetController
from arena.divergence import Diverged, DivergenceDetector, _event_cycle_id
from arena.events import EventLog, event_payload
from arena.fingerprints import quantized_intent_embedding
from arena.generated.models import (
    AblationProbe,
    Baseline,
    Event,
    HaltReason,
    Hypothesis,
    RejectReason,
    Run,
    RunnerName,
    Verdict,
    VerdictOutcome,
    Worktree,
)
from arena.hypothesizer import Arm, ArmStats, EmptyArmSetError, SymbolicHypothesizer, UCB1Bandit
from arena.ledger import FingerprintFailureLedger
from arena.loop import (
    LoopContext,
    _ast_diff_pattern,
    _discard_verdict,
    _is_scorer_verifier_disagreement,
    _structural_ok,
    run_loop,
)
from arena.router import RunnerRouter
from arena.runners.base import ApplyResult, CreditExhausted, RouterEvent, RunnerError
from arena.runners.claude_code import ClaudeCodeRunner, ClaudeStreamGuard, _tool_file_path
from arena.runners.ollama import OllamaRunner
from arena.worktrees import WorktreeManager, _remove_runtime_artifacts
from scorer.engine import ScoreRecord, ScoreVector
from verifier.ablation import AblationRequest, _reasoning_survives_probe
from verifier.calibration import CalibrationReport
from verifier.config import VerifierConfig
from verifier.engine import Verifier


def _score_record(id: str = "score", *, composite: float = 1.0, tests_pass: bool = True) -> ScoreRecord:
    return ScoreRecord(
        id=id,
        git_oid="a" * 40,
        scorer_lock_sha="b" * 64,
        vector=ScoreVector(
            composite=composite,
            coverage_pct=90.0,
            pyright_errors=0,
            ruff_violations=0,
            cyclomatic_avg=1.0,
            runtime_p95_ms=10.0,
            tests_pass=tests_pass,
        ),
        computed_ts=1.0,
    )


def _run_model(git_oid: str = "a" * 40) -> Run:
    return Run(
        id="run-coverage",
        north_star_id="north-star",
        scorer_lock_sha="b" * 64,
        config_sha="c" * 64,
        git_head_at_start=git_oid,
        started_ts=1.0,
    )


def _baseline(git_oid: str = "a" * 40) -> Baseline:
    return Baseline(
        id="baseline-coverage",
        run_id="run-coverage",
        git_oid=git_oid,
        score_record_id="score-before",
        promoted_ts=1.0,
        is_active=True,
    )


def _hypothesis(*, target_files: list[str] | None = None, fingerprint_id: str = "f" * 32) -> Hypothesis:
    return Hypothesis(
        id="hyp-coverage",
        cycle_id="cycle-1",
        intent="Improve core because tests and score improve.",
        technique_tag="runtime",
        target_cluster="core",
        target_files=target_files or ["src/pkg/core.py"],
        fingerprint_id=fingerprint_id,
        proposed_ts=1.0,
    )


class OneWorktreeManager:
    def __init__(self, root: Path) -> None:
        self.path = root / "worktree"
        self.path.mkdir(parents=True)
        self.torn_down: list[str] = []

    def create(self, cycle_id: str, base_oid: str) -> Worktree:
        return Worktree(
            id=cycle_id,
            cycle_id=cycle_id,
            path=str(self.path),
            base_git_oid=base_oid,
            created_ts=1.0,
        )

    def teardown(self, worktree: Worktree) -> None:
        self.torn_down.append(worktree.id)


class DictScanner:
    async def scan(self, worktree: Worktree) -> dict[str, str]:
        return {"ast_diff_pattern": "loop-pattern"}


class ObjectScanner:
    class Project:
        ast_diff_pattern = "object-pattern"

    async def scan(self, worktree: Worktree) -> Project:
        return self.Project()


class NoopScorer:
    def __init__(self) -> None:
        self.scored_paths: list[Path] = []

    def drift_check(self, baseline_record: ScoreRecord, repo: Path) -> None:
        return None

    def score_repo(self, repo: Path) -> ScoreRecord:
        self.scored_paths.append(repo)
        return _score_record("score-after", composite=2.0)


class StaticHypothesizer:
    def __init__(self, hypothesis: Hypothesis) -> None:
        self.hypothesis = hypothesis
        self.arm = Arm("runtime", "core", tuple(hypothesis.target_files))

    def propose(self, *, cycle_id: str, ast_diff_pattern: str) -> Any:
        return type("Proposal", (), {"hypothesis": self.hypothesis, "arm": self.arm})()


class StaticRouter:
    def __init__(self, result: ApplyResult) -> None:
        self.result = result

    async def apply(self, hypothesis: Hypothesis, worktree: Path) -> ApplyResult:
        return self.result


class StaticVerifier:
    def __init__(self, verdict: Verdict) -> None:
        self.verdict = verdict

    def verify_worktree(self, **kwargs: Any) -> Any:
        kwargs["scorer"].score_repo(kwargs["worktree"])
        return type(
            "Verification",
            (),
            {"verdict": self.verdict, "ablation_result": type("Ablation", (), {"model_dump": lambda self, mode: {"ok": True}})()},
        )()


class NoScoreVerifier(StaticVerifier):
    def verify_worktree(self, **kwargs: Any) -> Any:
        return type(
            "Verification",
            (),
            {"verdict": self.verdict, "ablation_result": type("Ablation", (), {"model_dump": lambda self, mode: {"ok": True}})()},
        )()


class RecordingPromoter:
    def promote(self, verdict: Verdict, worktree: Worktree, *, run_id: str, score_record_id: str) -> Baseline:
        return Baseline(
            id="baseline-promoted",
            run_id=run_id,
            git_oid="d" * 40,
            score_record_id=score_record_id,
            promoted_from_verdict_id=verdict.id,
            promoted_ts=2.0,
            is_active=True,
        )


class RecordingLedger:
    def __init__(self, failed: bool = False) -> None:
        self.failed = failed
        self.rows: list[dict[str, Any]] = []

    def has_failed(self, fingerprint_id: str) -> bool:
        return self.failed

    def record(self, **kwargs: Any) -> None:
        self.rows.append(kwargs)


class FalseStructuralValidator:
    async def validate(self, hypothesis: Hypothesis, patch_path: Path | None, worktree: Worktree) -> bool:
        return False


class StaticEventReader:
    def __init__(self, events: list[Event]) -> None:
        self._events = events

    def read_events(self) -> list[Event]:
        return self._events


class ErrorRunner:
    name = RunnerName.claude_code

    async def apply(self, hypothesis: Hypothesis, worktree: Path) -> Path:
        raise RunnerError("primary failed")


class SuccessfulRunner:
    name = RunnerName.ollama

    async def apply(self, hypothesis: Hypothesis, worktree: Path) -> Path:
        return worktree / "fallback.patch"


def _loop_context(
    tmp_path: Path,
    *,
    hypothesis: Hypothesis,
    router_result: ApplyResult | None = None,
    verifier_verdict: Verdict | None = None,
    verifier: Any | None = None,
    ledger: RecordingLedger | None = None,
    structural_validator: Any | None = None,
    stop_after_promotions: int | None = None,
    cycle_cap: int = 2,
) -> LoopContext:
    router_result = router_result or ApplyResult(
        hypothesis=hypothesis,
        runner_used=RunnerName.ollama,
        patch_path=tmp_path / "worktree" / "patch.diff",
        attempts=(RunnerName.ollama,),
        events=(),
    )
    verifier_verdict = verifier_verdict or Verdict(
        id="verdict-promote",
        hypothesis_id=hypothesis.id,
        outcome=VerdictOutcome.PROMOTED,
        score_delta=1.0,
        score_before_id="score-before",
        score_after_id="score-after",
        tests_passed=True,
        decided_ts=1.0,
    )
    return LoopContext(
        event_log=EventLog(tmp_path / "run", run_id="run-coverage"),
        budget=BudgetController(wall_clock_seconds_cap=10**12, cycle_count_cap=cycle_cap, start_ts=0.0),
        divergence=DivergenceDetector(EventLog(tmp_path / "run", run_id="run-coverage")),
        worktrees=OneWorktreeManager(tmp_path),
        scanner=DictScanner(),
        scorer=NoopScorer(),
        hypothesizer=StaticHypothesizer(hypothesis),
        router=StaticRouter(router_result),
        verifier=verifier or StaticVerifier(verifier_verdict),
        promoter=RecordingPromoter(),
        active_baseline=_baseline(),
        active_score=_score_record("score-before"),
        stop_after_promotions=stop_after_promotions,
        structural_validator=structural_validator,
        ledger=ledger,
    )


def test_script_helpers_are_exercised_without_touching_repo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from scripts import normalize_generated_artifacts as normalize
    from scripts import rebuild_calibration, update_scorer_lock

    ddl = tmp_path / "arena/generated/ddl.sql"
    schema = tmp_path / "arena/generated/schema.json"
    dts = tmp_path / "dashboard/src/lib/generated/arena.d.ts"
    ddl.parent.mkdir(parents=True)
    schema.parent.mkdir(parents=True, exist_ok=True)
    dts.parent.mkdir(parents=True)
    ddl.write_text("CREATE INDEX z ON t(z);   \nCREATE INDEX a ON t(a);\n\n", encoding="utf-8")
    schema.write_text("{ }  \n\n", encoding="utf-8")
    dts.write_text("export type X = string;   \n\n", encoding="utf-8")
    monkeypatch.setattr(normalize, "GENERATED_TEXT_PATHS", (ddl, schema, dts))

    normalize.main()

    assert ddl.read_text(encoding="utf-8") == "CREATE INDEX a ON t(a);\nCREATE INDEX z ON t(z);\n"
    assert schema.read_text(encoding="utf-8") == "{ }\n"
    assert normalize._normalize_text("a  \n\n") == "a\n"

    project_root = Path(__file__).resolve().parents[1]
    monkeypatch.setattr(sys, "path", [entry for entry in sys.path if entry != str(project_root)])
    runpy.run_path(str(project_root / "scripts/update_scorer_lock.py"), run_name="coverage_probe")

    scorer_root = tmp_path / "lock-project"
    (scorer_root / "scorer").mkdir(parents=True)
    (scorer_root / "scorer" / "__init__.py").write_text("VALUE = 1\n", encoding="utf-8")
    monkeypatch.setattr(update_scorer_lock, "PROJECT_ROOT", scorer_root)
    update_scorer_lock.main()
    lock_data = tomllib.loads((scorer_root / ".arena/scorer.lock.toml").read_text(encoding="utf-8"))
    assert lock_data["version"] == 1
    assert lock_data["locked_files"] == ["scorer/__init__.py"]

    cal_root = tmp_path / "calibration"
    monkeypatch.setattr(rebuild_calibration, "CAL_ROOT", cal_root)
    monkeypatch.setattr(rebuild_calibration, "BASE_REPO", cal_root / "repo")
    monkeypatch.setattr(rebuild_calibration, "DIFF_ROOT", cal_root / "diffs")
    (cal_root / "repo").mkdir(parents=True)
    (cal_root / "repo" / "stale.txt").write_text("stale\n", encoding="utf-8")
    (cal_root / "diffs").mkdir()
    (cal_root / "diffs" / "stale.patch").write_text("stale\n", encoding="utf-8")

    rebuild_calibration.main()

    expected = json.loads((cal_root / "expected.json").read_text(encoding="utf-8"))
    assert sorted(expected) == ["negative", "neutral", "positive"]
    assert (cal_root / "repo/src/validatorlib/core.py").exists()
    assert (cal_root / "diffs/positive/P-1.patch").exists()
    with pytest.raises(RuntimeError, match="old text not found"):
        rebuild_calibration.replace_text(cal_root / "repo", "src/validatorlib/core.py", "definitely absent sentinel", "new")
    with pytest.raises(RuntimeError, match="produced empty diff"):
        rebuild_calibration.make_patch("EMPTY", "neutral", lambda repo: None)


def test_budget_boundary_fingerprint_and_ledger_edge_cases(tmp_path: Path) -> None:
    assert str(BudgetBreach(HaltReason.WALL_CLOCK_BREACH, "done")) == "done"
    budget = BudgetController(wall_clock_seconds_cap=10, cycle_count_cap=10)
    budget.check(now=5.0)
    budget.record_runner_credit("codex", 2)
    budget.record_runner_credit("copilot_premium", 3)
    unlimited_credit_cap = BudgetController(wall_clock_seconds_cap=10, cycle_count_cap=10, claude_code_credits_cap=None)
    unlimited_credit_cap.record_runner_credit("claude_code", 999)
    unlimited_credit_cap.check(now=1.0)
    with pytest.raises(ValueError, match="unknown credit runner"):
        budget.record_runner_credit("unknown")

    assert is_boundary_violation([""]) is False
    assert is_boundary_violation([".arena/scorer.lock.toml"]) is True
    with pytest.raises(ValueError):
        is_boundary_violation(["../scorer/engine.py"])
    with pytest.raises(ValueError):
        quantized_intent_embedding("intent", buckets=0)

    ledger_path = tmp_path / "ledger/failures.jsonl"
    ledger_path.parent.mkdir()
    ledger_path.write_text('\n{"bad"\n{"fingerprint_id":"f","outcome":"DISCARDED"}\n[]\n', encoding="utf-8")
    ledger = FingerprintFailureLedger(ledger_path)
    assert ledger.iter_records() == [{"fingerprint_id": "f", "outcome": "DISCARDED"}]
    assert ledger.has_failed("f") is True


def test_event_projection_and_payload_edge_cases(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    log = EventLog(tmp_path / "run", run_id="run-1")
    assert log.read_events() == []
    first = log.emit("RUN_STARTED", ts=1.0)
    log.events_path.write_text("\n" + log.events_path.read_text(encoding="utf-8"), encoding="utf-8")
    assert log.read_events()[0].id == first.id

    first_projection = log.rebuild_projection()
    assert first_projection.event_count == 1
    second_projection = log.rebuild_projection()
    assert second_projection.event_count == 1

    log.projection_path.write_text("not sqlite", encoding="utf-8")
    assert log.ensure_projection_current().event_count == 1

    class BrokenConnection:
        def __enter__(self) -> BrokenConnection:
            return self

        def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
            return None

        def execute(self, sql: str) -> Any:
            raise sqlite3.DatabaseError("broken projection")

    log.projection_path.write_text("still exists", encoding="utf-8")
    real_connect = sqlite3.connect
    connect_calls = 0

    def flaky_connect(path: Path) -> Any:
        nonlocal connect_calls
        connect_calls += 1
        if connect_calls == 1:
            return BrokenConnection()
        return real_connect(path)

    monkeypatch.setattr(sqlite3, "connect", flaky_connect)
    assert log.ensure_projection_current().event_count == 1

    log.emit("SCAN_COMPLETE", ts=2.0)
    assert log.ensure_projection_current().event_count == 2

    assert event_payload(Event(id="e1", run_id="r", seq=1, ts=1.0, type="X")) == {}
    assert event_payload(Event(id="e2", run_id="r", seq=2, ts=1.0, type="X", payload_inline="{")) == {}
    assert event_payload(Event(id="e3", run_id="r", seq=3, ts=1.0, type="X", payload_inline="[]")) == {}
    assert event_payload(Event(id="e4", run_id="r", seq=4, ts=1.0, type="X", payload_inline='{"a":1}')) == {"a": 1}


def test_hypothesizer_and_divergence_edge_cases() -> None:
    assert ArmStats().mean_reward == 0.0
    assert ArmStats(pulls=2, reward_sum=3.0).mean_reward == 1.5
    with pytest.raises(EmptyArmSetError):
        UCB1Bandit([])
    bandit = UCB1Bandit([Arm("runtime", "core", ("src/core.py",))])
    with pytest.raises(KeyError):
        bandit._arm_by_key("missing")
    proposal = SymbolicHypothesizer(bandit, embedding_model="deterministic-test-model").propose(
        cycle_id="cycle-1",
        ast_diff_pattern="pattern",
    )
    assert proposal.fingerprint.embedding_model == "deterministic-test-model"

    diverged = Diverged(HaltReason.FINGERPRINT_CLUSTER_FAILURE, "cluster failed")
    assert str(diverged) == "cluster failed"
    malformed_fingerprint_event = Event(
        id="e1",
        run_id="run-1",
        seq=1,
        ts=1.0,
        type="VERDICT_DECIDED",
        payload_inline=json.dumps({"fingerprint_id": "", "outcome": "DISCARDED"}),
    )
    terminal_events = [
        Event(id="e2", run_id="run-1", cycle_id="a", seq=2, ts=1.0, type="SCORER_VERIFIER_DISAGREEMENT"),
        Event(id="e3", run_id="run-1", cycle_id="a", seq=3, ts=1.0, type="CYCLE_ENDED"),
        Event(id="e4", run_id="run-1", cycle_id="b", seq=4, ts=1.0, type="CYCLE_ENDED"),
    ]
    detector = DivergenceDetector(StaticEventReader([malformed_fingerprint_event, *terminal_events]))
    assert detector.check("run-1") is None
    assert _event_cycle_id(Event(id="e5", run_id="run-1", seq=5, ts=1.0, type="X", payload_inline='{"cycle_id": 3}')) is None


def test_loop_discards_boundary_failed_ledger_apply_and_structural_cases(tmp_path: Path) -> None:
    boundary_hypothesis = _hypothesis(target_files=["scorer/engine.py"])
    boundary_ctx = _loop_context(tmp_path / "boundary", hypothesis=boundary_hypothesis)
    boundary_result = asyncio.run(run_loop(_run_model(), boundary_ctx))
    boundary_events = boundary_ctx.event_log.read_events()
    assert boundary_result.halt_record is not None
    assert "BOUNDARY_VIOLATION" in [event.type for event in boundary_events]

    ledger = RecordingLedger(failed=True)
    ledger_ctx = _loop_context(tmp_path / "ledger", hypothesis=_hypothesis(fingerprint_id="failed"), ledger=ledger)
    asyncio.run(run_loop(_run_model(), ledger_ctx))
    assert ledger.rows[0]["reject_reason"] == RejectReason.FINGERPRINT_COLLISION.value

    apply_hypothesis = _hypothesis()
    apply_failure = ApplyResult(
        hypothesis=apply_hypothesis,
        runner_used=None,
        patch_path=None,
        attempts=(RunnerName.claude_code,),
        events=(RouterEvent("RUNNER_EVENT", {"detail": "emitted before failure"}),),
        error_reason=RejectReason.RUNNER_ERROR,
        error_detail="failed",
    )
    apply_ctx = _loop_context(tmp_path / "apply", hypothesis=apply_hypothesis, router_result=apply_failure)
    asyncio.run(run_loop(_run_model(), apply_ctx))
    assert "RUNNER_EVENT" in [event.type for event in apply_ctx.event_log.read_events()]

    structural_ctx = _loop_context(
        tmp_path / "structural",
        hypothesis=_hypothesis(),
        structural_validator=FalseStructuralValidator(),
    )
    asyncio.run(run_loop(_run_model(), structural_ctx))
    structural_events = structural_ctx.event_log.read_events()
    assert "PATCH_APPLIED" in [event.type for event in structural_events]
    verdict_payload = next(json.loads(event.payload_inline or "{}") for event in structural_events if event.type == "VERDICT_DECIDED")
    assert verdict_payload["reject_reason"] == RejectReason.STRUCTURAL_VALIDATION_FAIL.value


def test_loop_halts_before_promotion_when_verifier_does_not_score_worktree(tmp_path: Path) -> None:
    verifier_verdict = Verdict(
        id="verdict-promote-without-score",
        hypothesis_id="hyp-1",
        outcome=VerdictOutcome.PROMOTED,
        score_delta=1.0,
        score_before_id="score-before",
        score_after_id="score-after",
        tests_passed=True,
        decided_ts=1.0,
    )
    ctx = _loop_context(
        tmp_path / "promote-without-score",
        hypothesis=_hypothesis(),
        verifier_verdict=verifier_verdict,
        verifier=NoScoreVerifier(verifier_verdict),
    )

    result = asyncio.run(run_loop(_run_model(), ctx))

    event_types = [event.type for event in ctx.event_log.read_events()]
    assert result.halt_record is not None
    assert result.halt_record.reason == HaltReason.RUNNER_UNAVAILABLE
    assert result.halt_record.detail is not None
    assert "did not return a score_after record" in result.halt_record.detail
    assert "VERDICT_DECIDED" not in event_types
    assert "PROMOTED" not in event_types


def test_loop_promotes_then_continues_until_budget_and_helper_edges(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    ctx = _loop_context(tmp_path / "promote", hypothesis=_hypothesis())
    result = asyncio.run(run_loop(_run_model(), ctx))
    event_types = [event.type for event in ctx.event_log.read_events()]
    assert result.halt_record is not None
    assert "PROMOTED" in event_types
    assert "BASELINE_ADVANCED" in event_types

    assert _ast_diff_pattern(ObjectScanner.Project()) == "object-pattern"
    verdict = _discard_verdict("hyp", "score-before", RejectReason.RUNNER_ERROR)
    assert verdict.reject_reason == RejectReason.RUNNER_ERROR
    assert _is_scorer_verifier_disagreement(verdict) is False
    worktree = Worktree(id="w", cycle_id="c", path=str(tmp_path), base_git_oid="a" * 40, created_ts=1.0)
    assert asyncio.run(_structural_ok(ctx, _hypothesis(), tmp_path / "patch.diff", worktree)) is True
    ctx.structural_validator = FalseStructuralValidator()
    assert asyncio.run(_structural_ok(ctx, _hypothesis(), tmp_path / "patch.diff", worktree)) is False

    class FakeState:
        def __init__(self, name: str) -> None:
            self.name = name

        def __eq__(self, other: object) -> bool:
            return isinstance(other, FakeState) and self.name == other.name

    class FakeLoopStates:
        def __init__(self) -> None:
            self.scan_reads = 0

        @property
        def SCAN(self) -> FakeState:
            self.scan_reads += 1
            return FakeState("HALT" if self.scan_reads == 1 else "SCAN")

        @property
        def HYPOTHESIZE(self) -> FakeState:
            return FakeState("HYPOTHESIZE")

        @property
        def APPLY(self) -> FakeState:
            return FakeState("APPLY")

        @property
        def VERIFY(self) -> FakeState:
            return FakeState("VERIFY")

        @property
        def PROMOTE(self) -> FakeState:
            return FakeState("PROMOTE")

        @property
        def DISCARD(self) -> FakeState:
            return FakeState("DISCARD")

        @property
        def HALT(self) -> FakeState:
            return FakeState("HALT")

    monkeypatch.setattr(loop_module, "LoopState", FakeLoopStates())
    halt_result = asyncio.run(loop_module.run_loop(_run_model(), _loop_context(tmp_path / "halt", hypothesis=_hypothesis())))
    assert halt_result.cycles_total == 0
    assert halt_result.halt_record is None


def test_runner_edge_cases(tmp_path: Path) -> None:
    guard = ClaudeStreamGuard()
    guard.process_event({"type": "user"})
    guard.process_event(
        {
            "type": "assistant",
            "message": {
                "content": [
                    {"type": "text"},
                    {"type": "tool_use", "name": "Read", "input": "not-a-dict"},
                    {"type": "tool_use", "name": "Read", "input": {}},
                ]
            },
        }
    )
    assert _tool_file_path({"input": "not-a-dict"}) is None
    assert _tool_file_path({"input": {}}) is None

    hypothesis = _hypothesis()
    default_patch = asyncio.run(ClaudeCodeRunner(events=[]).apply(hypothesis, tmp_path))
    assert default_patch == tmp_path / "claude.patch"
    with pytest.raises(RunnerError, match="ordinary failure"):
        asyncio.run(ClaudeCodeRunner(events=[{"type": "result", "is_error": True, "result": "ordinary failure"}]).apply(hypothesis, tmp_path))
    with pytest.raises(CreditExhausted):
        asyncio.run(
            ClaudeCodeRunner(events=[{"type": "system", "subtype": "api_retry", "result": "hit your usage limit"}]).apply(
                hypothesis,
                tmp_path,
            )
        )
    with pytest.raises(CreditExhausted, match="forced ollama exhaustion"):
        asyncio.run(OllamaRunner(exhausted=True).apply(hypothesis, tmp_path))

    router = RunnerRouter(primary=ErrorRunner(), fallback=SuccessfulRunner())
    result = asyncio.run(router.apply(hypothesis, tmp_path))
    assert result.success is False
    assert result.attempts == (RunnerName.claude_code,)
    assert result.error_reason == RejectReason.RUNNER_ERROR


def test_worktree_reaping_and_runtime_cleanup(calibration_repo: Path, tmp_path: Path) -> None:
    root = tmp_path / "worktrees"
    (root / "orphan").mkdir(parents=True)
    (root / "live").mkdir()
    (root / "not-a-directory.txt").write_text("x", encoding="utf-8")
    manager = WorktreeManager(repo=calibration_repo, worktree_root=root)

    assert manager.reap_orphans(live_cycle_ids={"live"}) == 1

    repo = tmp_path / "empty-repo"
    repo.mkdir()
    (repo / ".coverage").write_text("coverage", encoding="utf-8")
    _remove_runtime_artifacts(repo)
    assert not (repo / ".coverage").exists()


def test_scorer_error_and_fallback_paths(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    record = _score_record()
    assert record.to_jsonable()["vector"]["coverage_pct"] == 90.0

    from scorer.goal_config import load_goal_config

    def write_goal_config(*, runtime_proxy: bool = False) -> Any:
        runtime_line = '\nruntime_proxy = ["python3", "benchmarks/runtime_proxy.py"]' if runtime_proxy else ""
        (tmp_path / ".arena").mkdir(exist_ok=True)
        (tmp_path / ".arena" / "goal.toml").write_text(
            f'''
schema_version = "goal-config/v1"
project_id = "fallbacks"

[commands]
test = ["python3", "-c", "pass"]
lint = ["python3", "-c", "pass"]
typecheck = ["python3", "-c", "pass"]
coverage = ["python3", "-c", "pass"]{runtime_line}

[coverage]
source = "coverage.json"
floor = 0.0
'''.strip()
            + "\n",
            encoding="utf-8",
        )
        return load_goal_config(tmp_path)

    def failing_git(*args: Any, **kwargs: Any) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(args, 1, stdout="", stderr="fatal")

    monkeypatch.setattr(scorer_engine, "_run", failing_git)
    with pytest.raises(RuntimeError, match="git rev-parse failed"):
        scorer_engine._git_oid(tmp_path)

    goal_config = write_goal_config()

    def invalid_coverage(args: Any, repo: Path, **kwargs: Any) -> subprocess.CompletedProcess[str]:
        (repo / "coverage.json").write_text("not json", encoding="utf-8")
        return subprocess.CompletedProcess(args, 0, stdout="", stderr="")

    monkeypatch.setattr(scorer_engine, "_run", invalid_coverage)
    assert scorer_engine._test_and_coverage(tmp_path, goal_config) == (True, 0.0)

    def invalid_stdout(args: Any, repo: Path, **kwargs: Any) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(args, 0, stdout="not json", stderr="")

    monkeypatch.setattr(scorer_engine, "_run", invalid_stdout)
    assert scorer_engine._ruff_violations(tmp_path, goal_config) == 999
    assert scorer_engine._pyright_errors(tmp_path, goal_config) == 999
    assert scorer_engine._runtime_proxy(tmp_path, goal_config) == 0.0
    (tmp_path / "benchmarks").mkdir()
    (tmp_path / "benchmarks" / "runtime_proxy.py").write_text("raise SystemExit(1)\n", encoding="utf-8")
    monkeypatch.setattr(scorer_engine, "_run", failing_git)
    assert scorer_engine._runtime_proxy(tmp_path, write_goal_config(runtime_proxy=True)) == 9999.0

    tree = ast.parse(
        "def f(x, y):\n"
        "    while x:\n"
        "        try:\n"
        "            if x and y:\n"
        "                pass\n"
        "        except ValueError:\n"
        "            pass\n"
    )
    function = next(node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef))
    assert scorer_engine._function_complexity(function) >= 5
    empty_src = tmp_path / "empty-src"
    empty_src.mkdir()
    (empty_src / "module.py").write_text("VALUE = 1\n", encoding="utf-8")
    assert scorer_engine._cyclomatic_average([empty_src]) == 0.0
    with pytest.raises(AssertionError, match="axis composite differs"):
        scorer_engine.assert_vectors_close(_score_record(composite=1.0).vector, _score_record(composite=2.0).vector)
    assert scorer_engine.score_axes_delta(_score_record(composite=1.0).vector, _score_record(composite=2.0).vector)["composite"] == 1.0

    from scorer.exceptions import ScorerLockMismatchError
    from scorer.lock import compute_scorer_tree_sha

    with pytest.raises(ScorerLockMismatchError, match="locked scorer file missing"):
        compute_scorer_tree_sha(tmp_path, ("scorer/missing.py",))


def test_verifier_and_calibration_edge_cases() -> None:
    with pytest.raises(ValueError, match="must be ollama"):
        VerifierConfig(ablation_runner=RunnerName.claude_code)

    class MismatchedRunner:
        name = RunnerName.claude_code

        def run_probe(self, request: AblationRequest, probe: AblationProbe) -> Any:
            raise AssertionError("not called")

    with pytest.raises(ValueError, match="ablation runner mismatch"):
        Verifier(VerifierConfig(), MismatchedRunner())
    request = AblationRequest("hyp", "because tests pass", 1.0, True, ())
    assert _reasoning_survives_probe(request, cast(AblationProbe, object())) is False

    report = CalibrationReport((), 0, 0, 0, 0, 0.0, 0.1)
    assert report.false_positive_rate == 0.0
    assert report.false_negative_rate == 0.0
    assert report.meets_targets is True


def test_decomposer_private_and_cli_edge_cases(tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch) -> None:
    assert len(decomposer._arena_contracts(set(), ["arena/fixtures.py"])) == 0

    docs = tmp_path / "docs-only"
    docs.mkdir()
    (docs / "README.md").write_text("# docs\n", encoding="utf-8")

    output = tmp_path / "scanner.json"
    assert decomposer.main(["--project", str(docs), "--output", str(output)]) == 0
    assert json.loads(output.read_text(encoding="utf-8"))["schema_version"] == "project-scanner/v0.1"

    scanner_model = decomposer.decompose_project(docs)
    monkeypatch.setattr(decomposer, "decompose_project", lambda *args, **kwargs: scanner_model)
    monkeypatch.setattr(
        decomposer,
        "validate_project_model",
        lambda model: decomposer.DecompositionValidationReport(valid=False, errors=["forced scanner failure"], gap_count=0),
    )
    assert decomposer.main(["--project", str(docs), "--output", "-"]) == 2
    assert "decomposition model is invalid" in capsys.readouterr().err

    def dirty_failure(root: Path, args: list[str]) -> str:
        raise subprocess.CalledProcessError(1, args)

    monkeypatch.setattr(decomposer, "_git_output", dirty_failure)
    assert decomposer._git_dirty_paths(tmp_path) == []

    def dirty_status(root: Path, args: list[str]) -> str:
        return "\nR  old.py -> new.py\n M modified.py\n?? ignored.py\n"

    monkeypatch.setattr(decomposer, "_git_output", dirty_status)
    assert decomposer._git_dirty_paths(tmp_path) == ["modified.py", "new.py", "old.py"]
    assert decomposer._exclusion_reason(".git/config") == "vcs_metadata"
    assert decomposer._exclusion_reason("venv/bin/python") == "dependency_environment"
    assert decomposer._exclusion_reason("pkg.egg-info/PKG-INFO") == "build_metadata"
    assert decomposer._exclusion_reason("build/out.bin") == "generated_or_runtime_artifact"
    assert decomposer._exclusion_reason("cache.tmp") == "generated_or_runtime_artifact"
    assert decomposer._exclusion_reason("archive.zip") == "archive_artifact"
    assert decomposer._classify_file("config.ini") == "configuration"
    assert decomposer._classify_file("change.diff") == "artifact"
    assert decomposer._classify_file("image.png") == "resource"


def test_decomposer_validation_reports_all_error_families(tmp_path: Path) -> None:
    model = decomposer.ProjectModel(
        project_id="broken",
        project_root=str(tmp_path),
        git=decomposer.GitState(available=False, inventory_mode="filesystem", dirty=True),
        file_inventory=decomposer.FileInventory(
            included_files=[
                decomposer.FileRecord(path="pkg/core.py", sha256="0" * 64, kind="source", excluded=True),
                decomposer.FileRecord(path="pkg/unowned.py", sha256="1" * 64, kind="source"),
            ],
            excluded_files=[
                decomposer.FileRecord(path="build/out.bin", sha256=None, kind="runtime", excluded=False, reason=""),
            ],
        ),
        components=[
            decomposer.Component(
                id="core",
                name="Core",
                kind="source",
                owned_files=["pkg/core.py", "missing.py"],
                responsibilities=["core"],
                verification_gaps=["missing-gap"],
                checks=[],
                rollback_boundaries=[decomposer.RollbackBoundary(id="rb", stop_condition="stop", files=["missing.py"])],
            ),
            decomposer.Component(id="empty", name="Empty", kind="source", owned_files=[], responsibilities=["empty"]),
        ],
        contracts=[
            decomposer.Contract(
                id="bad-contract",
                producer_component_id="missing-producer",
                consumer_component_id="core",
                assumes=[],
                guarantees=[],
                verification_gaps=["missing-gap"],
            )
        ],
        verification_gaps=[
            decomposer.VerificationGap(id="gap", component_id="core", severity="medium", evidence=[], proposed_check="")
        ],
        cross_cutting_concerns=[
            decomposer.CrossCuttingConcern(
                id="concern",
                description="concern",
                affected_components=["core"],
                verification_gaps=["missing-gap"],
            ),
            decomposer.CrossCuttingConcern(id="unmapped", description="unmapped", affected_components=["missing"]),
        ],
        coverage=decomposer.CoverageReport(
            total_files=3,
            included_files=2,
            excluded_files=1,
            owned_included_files=1,
            coverage_numerator=1,
            coverage_denominator=2,
        ),
    )

    report = decomposer.validate_project_model(model)
    joined = "\n".join(report.errors + report.warnings)
    assert "included file pkg/core.py is marked excluded" in joined
    assert "excluded file build/out.bin is not marked excluded" in joined
    assert "component empty has no owned files" in joined
    assert "component core owns non-included file missing.py" in joined
    assert "component empty has neither checks nor verification gaps" in joined
    assert "component core references missing verification gap missing-gap" in joined
    assert "rollback boundary rb references missing file missing.py" in joined
    assert "included file pkg/unowned.py is unowned" in joined
    assert "contract bad-contract references missing producer component missing-producer" in joined
    assert "contract bad-contract references missing verification gap missing-gap" in joined
    assert "verification gap gap has no evidence" in joined
    assert "verification gap gap has empty proposed_check" in joined
    assert "cross-cutting concern concern references missing verification gap missing-gap" in joined
    assert "cross-cutting concern unmapped references missing component missing" in joined
    assert "source coverage is incomplete" in joined
    assert "filesystem fallback inventory was used" in joined
    assert "git tree was dirty" in joined


def test_decomposer_generic_unclassified_surface(tmp_path: Path) -> None:
    loose = tmp_path / "loose"
    loose.mkdir()
    (loose / "image.png").write_bytes(b"png")
    generic = decomposer.decompose_project(loose)
    assert "unclassified_project_surface" in {component.id for component in generic.components}
    assert any(gap.id == "unclassified_project_surface_gap" for gap in generic.verification_gaps)
