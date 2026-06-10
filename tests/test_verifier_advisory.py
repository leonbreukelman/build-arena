from __future__ import annotations

from arena.generated.models import RejectReason, RunnerName, VerdictOutcome
from scorer.engine import ScoreRecord, ScoreVector
from verifier.ablation import AblationProbeOutcome, AblationRequest
from verifier.config import VerifierConfig
from verifier.engine import PatchVerificationInput, Verifier


def _vector(*, composite: float = 12.0, tests_pass: bool = True) -> ScoreVector:
    return ScoreVector(
        composite=composite,
        coverage_pct=90.0,
        pyright_errors=0,
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


class NonLoadBearingCodexRunner:
    name = RunnerName.codex

    def __init__(self) -> None:
        self.calls: list[tuple[AblationRequest, object]] = []

    def run_probe(self, request: AblationRequest, probe):
        self.calls.append((request, probe))
        return AblationProbeOutcome(
            probe=probe,
            original_output="PROMOTE",
            ablated_output="PROMOTE",
            changed_output=False,
        )


def test_ablation_advisory_allows_non_ollama_and_does_not_gate_real_cycle() -> None:
    runner = NonLoadBearingCodexRunner()
    verifier = Verifier(
        VerifierConfig(ablation_runner=RunnerName.codex, ablation_advisory=True),
        runner,
    )

    result = verifier.verify(
        PatchVerificationInput(
            hypothesis_id="hyp-advisory",
            reasoning="score improves because target picker selected a high-signal file",
            score_before=_record("baseline", _vector(composite=10.0)),
            score_after=_record("candidate", _vector(composite=12.0)),
        )
    )

    assert len(runner.calls) == 3
    assert result.ablation_result.runner_used == RunnerName.codex
    assert result.ablation_result.load_bearing is False
    assert result.verdict.outcome == VerdictOutcome.PROMOTED
    assert result.verdict.reject_reason is None


def test_strict_verifier_still_rejects_non_load_bearing_ablation() -> None:
    runner = NonLoadBearingCodexRunner()
    verifier = Verifier(
        VerifierConfig(ablation_runner=RunnerName.codex, ablation_advisory=True, require_score_delta_gt0=True),
        runner,
    )

    failed = verifier.verify(
        PatchVerificationInput(
            hypothesis_id="hyp-test-failure",
            reasoning="score improves because target picker selected a high-signal file",
            score_before=_record("baseline", _vector(composite=10.0)),
            score_after=_record("candidate", _vector(composite=12.0, tests_pass=False)),
        )
    )

    assert failed.verdict.reject_reason == RejectReason.TEST_FAILURE
