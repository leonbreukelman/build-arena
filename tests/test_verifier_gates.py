from __future__ import annotations

from dataclasses import replace

from arena.generated.models import RejectReason, RunnerName, VerdictOutcome
from scorer.engine import ScoreRecord, ScoreVector
from verifier.ablation import AblationProbeOutcome, AblationRequest
from verifier.config import VerifierConfig
from verifier.engine import PatchVerificationInput, Verifier


def _vector(
    *,
    composite: float = 10.0,
    tests_pass: bool = True,
    coverage_pct: float = 90.0,
    pyright_errors: int = 0,
) -> ScoreVector:
    return ScoreVector(
        composite=composite,
        coverage_pct=coverage_pct,
        pyright_errors=pyright_errors,
        ruff_violations=0,
        cyclomatic_avg=1.0,
        runtime_p95_ms=10.0,
        tests_pass=tests_pass,
    )


def _record(id_: str, vector: ScoreVector) -> ScoreRecord:
    return ScoreRecord(
        id=id_,
        git_oid=("a" if id_ == "baseline" else "b") * 40,
        scorer_lock_sha="c" * 64,
        vector=vector,
        computed_ts=1.0,
    )


class ScriptedAblationRunner:
    name = RunnerName.ollama

    def __init__(self, *, changed: bool) -> None:
        self.changed = changed
        self.calls: list[tuple[AblationRequest, object]] = []

    def run_probe(self, request: AblationRequest, probe):
        self.calls.append((request, probe))
        return AblationProbeOutcome(
            probe=probe,
            original_output="PROMOTE",
            ablated_output="DISCARD" if self.changed else "PROMOTE",
            changed_output=self.changed,
        )


def _input(after: ScoreVector, *, reasoning: str = "score improves because runtime drops") -> PatchVerificationInput:
    return PatchVerificationInput(
        hypothesis_id="hyp-1",
        reasoning=reasoning,
        score_before=_record("baseline", _vector(composite=10.0)),
        score_after=_record("candidate", after),
    )


def test_verifier_promotes_when_all_four_gates_pass() -> None:
    runner = ScriptedAblationRunner(changed=True)
    result = Verifier(VerifierConfig(), runner).verify(_input(_vector(composite=12.0)))

    assert result.verdict.outcome == VerdictOutcome.PROMOTED
    assert result.verdict.reject_reason is None
    assert result.verdict.score_delta == 2.0
    assert result.ablation_result.load_bearing is True
    assert result.ablation_result.runner_used == RunnerName.ollama
    assert len(runner.calls) == 3


def test_verifier_rejects_failed_tests_but_still_runs_ablation() -> None:
    runner = ScriptedAblationRunner(changed=True)
    result = Verifier(VerifierConfig(), runner).verify(
        _input(_vector(composite=12.0, tests_pass=False))
    )

    assert result.verdict.outcome == VerdictOutcome.DISCARDED
    assert result.verdict.reject_reason == RejectReason.TEST_FAILURE
    assert len(runner.calls) == 3


def test_verifier_rejects_pinned_regression_before_score_reason() -> None:
    runner = ScriptedAblationRunner(changed=True)
    result = Verifier(VerifierConfig(), runner).verify(
        _input(_vector(composite=12.0, coverage_pct=80.0))
    )

    assert result.verdict.outcome == VerdictOutcome.DISCARDED
    assert result.verdict.reject_reason == RejectReason.PINNED_METRIC_REGRESSION
    assert result.verdict.pinned_regression == ["coverage_pct"]
    assert len(runner.calls) == 3


def test_pinned_regression_takes_precedence_over_nonpositive_score_delta() -> None:
    runner = ScriptedAblationRunner(changed=True)
    result = Verifier(VerifierConfig(), runner).verify(
        _input(_vector(composite=9.0, coverage_pct=80.0))
    )

    assert result.verdict.score_delta == -1.0
    assert result.verdict.reject_reason == RejectReason.PINNED_METRIC_REGRESSION



def test_verifier_rejects_nonpositive_score_delta() -> None:
    runner = ScriptedAblationRunner(changed=True)
    result = Verifier(VerifierConfig(), runner).verify(_input(_vector(composite=10.0)))

    assert result.verdict.outcome == VerdictOutcome.DISCARDED
    assert result.verdict.reject_reason == RejectReason.SCORE_DELTA_NONPOSITIVE
    assert result.verdict.score_delta == 0.0
    assert len(runner.calls) == 3


def test_verifier_rejects_non_load_bearing_reasoning() -> None:
    runner = ScriptedAblationRunner(changed=False)
    result = Verifier(VerifierConfig(), runner).verify(_input(_vector(composite=12.0)))

    assert result.verdict.outcome == VerdictOutcome.DISCARDED
    assert result.verdict.reject_reason == RejectReason.ABLATION_REASONING_NOT_LOAD_BEARING
    assert result.ablation_result.probes_changed_output == 0


def test_pyright_regression_is_reported_as_pinned_regression() -> None:
    runner = ScriptedAblationRunner(changed=True)
    before = _record("baseline", _vector(composite=10.0, pyright_errors=1))
    after = _record("candidate", _vector(composite=12.0, pyright_errors=2))
    result = Verifier(VerifierConfig(), runner).verify(
        replace(_input(_vector(composite=12.0)), score_before=before, score_after=after)
    )

    assert result.verdict.reject_reason == RejectReason.PINNED_METRIC_REGRESSION
    assert result.verdict.pinned_regression == ["pyright_errors"]
