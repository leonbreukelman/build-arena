from __future__ import annotations

from pathlib import Path

import pytest

from arena.generated.models import AblationProbe, RunnerName
from scorer.engine import ScoreRecord, ScoreVector
from verifier.ablation import (
    AblationProbeOutcome,
    AblationRequest,
    DeterministicOllamaAblationRunner,
)
from verifier.config import VerifierConfig
from verifier.engine import PatchVerificationInput, Verifier


def _record(id_: str, composite: float) -> ScoreRecord:
    return ScoreRecord(
        id=id_,
        git_oid=("a" if id_ == "baseline" else "b") * 40,
        scorer_lock_sha="c" * 64,
        vector=ScoreVector(
            composite=composite,
            coverage_pct=90.0,
            pyright_errors=0,
            ruff_violations=0,
            cyclomatic_avg=1.0,
            runtime_p95_ms=10.0,
            tests_pass=True,
        ),
        computed_ts=1.0,
    )


class CountingRunner:
    name = RunnerName.ollama

    def __init__(self) -> None:
        self.calls: list[AblationProbe] = []

    def run_probe(self, request: AblationRequest, probe: AblationProbe) -> AblationProbeOutcome:
        self.calls.append(probe)
        return AblationProbeOutcome(
            probe=probe,
            original_output="PROMOTE",
            ablated_output="DISCARD",
            changed_output=True,
        )


class CountingScorer:
    def __init__(self, record: ScoreRecord) -> None:
        self.record = record
        self.calls: list[Path] = []

    def score_repo(self, repo: Path) -> ScoreRecord:
        self.calls.append(repo)
        return self.record


def test_default_verifier_config_uses_ollama_and_three_lanham_probes() -> None:
    config = VerifierConfig()

    assert config.ablation_runner == RunnerName.ollama
    assert config.probe_set == (
        AblationProbe.EARLY_ANSWERING,
        AblationProbe.FILLER_TOKENS,
        AblationProbe.PARAPHRASING,
    )
    assert config.quorum_threshold == 2


def test_verifier_config_rejects_probe_sets_that_are_not_three_of_four() -> None:
    with pytest.raises(ValueError, match="exactly 3"):
        VerifierConfig(probe_set=(AblationProbe.EARLY_ANSWERING, AblationProbe.FILLER_TOKENS))
    with pytest.raises(ValueError, match="duplicate"):
        VerifierConfig(
            probe_set=(
                AblationProbe.EARLY_ANSWERING,
                AblationProbe.EARLY_ANSWERING,
                AblationProbe.FILLER_TOKENS,
            )
        )


def test_verifier_config_rejects_invalid_quorum() -> None:
    with pytest.raises(ValueError, match="between 1 and 3"):
        VerifierConfig(quorum_threshold=0)
    with pytest.raises(ValueError, match="between 1 and 3"):
        VerifierConfig(quorum_threshold=4)


def test_verifier_loads_config_toml(project_root) -> None:
    config = VerifierConfig.from_toml(project_root / ".arena" / "config.toml")

    assert config.ablation_runner == RunnerName.ollama
    assert config.quorum_threshold == 2
    assert config.fn_target == 0.10
    assert len(config.probe_set) == 3


def test_deterministic_ablation_runner_discriminates_load_bearing_reasoning() -> None:
    runner = DeterministicOllamaAblationRunner()
    request = AblationRequest(
        hypothesis_id="hyp-real-runner",
        reasoning="score improves because runtime drops",
        score_delta=1.0,
        tests_passed=True,
        pinned_regressions=(),
    )

    outcomes = [runner.run_probe(request, probe) for probe in VerifierConfig().probe_set]

    assert [outcome.changed_output for outcome in outcomes] == [True, True, True]


def test_deterministic_ablation_runner_handles_paraphrase_and_mistake_probes() -> None:
    runner = DeterministicOllamaAblationRunner()
    request = AblationRequest(
        hypothesis_id="hyp-paraphrase",
        reasoning="paraphrase-stable score improves because coverage increases",
        score_delta=1.0,
        tests_passed=True,
        pinned_regressions=(),
    )

    paraphrase = runner.run_probe(request, AblationProbe.PARAPHRASING)
    mistake = runner.run_probe(request, AblationProbe.ADDING_MISTAKES)

    assert paraphrase.changed_output is False
    assert mistake.changed_output is True


def test_real_ablation_runner_can_be_sole_reject_reason() -> None:
    result = Verifier().verify(
        PatchVerificationInput(
            hypothesis_id="hyp-no-reason",
            reasoning="looks good",
            score_before=_record("baseline", 10.0),
            score_after=_record("candidate", 12.0),
        )
    )

    assert result.verdict.reject_reason == "ABLATION_REASONING_NOT_LOAD_BEARING"
    assert result.ablation_result.probes_changed_output == 0


def test_real_ablation_runner_can_satisfy_quorum() -> None:
    result = Verifier().verify(
        PatchVerificationInput(
            hypothesis_id="hyp-with-reason",
            reasoning="score improves because runtime drops",
            score_before=_record("baseline", 10.0),
            score_after=_record("candidate", 12.0),
        )
    )

    assert result.verdict.outcome == "PROMOTED"
    assert result.ablation_result.probes_changed_output == 3


def test_verify_reruns_all_probes_without_cache_reuse() -> None:
    runner = CountingRunner()
    verifier = Verifier(VerifierConfig(), runner)
    request = PatchVerificationInput(
        hypothesis_id="hyp-cache",
        reasoning="score improves because coverage increases",
        score_before=_record("baseline", 10.0),
        score_after=_record("candidate", 12.0),
    )

    verifier.verify(request)
    verifier.verify(request)

    assert runner.calls == list(VerifierConfig().probe_set) * 2


def test_verify_worktree_rescores_live_candidate_each_call(tmp_path: Path) -> None:
    runner = CountingRunner()
    verifier = Verifier(VerifierConfig(), runner)
    scorer = CountingScorer(_record("candidate", 12.0))
    baseline = _record("baseline", 10.0)

    verifier.verify_worktree(
        hypothesis_id="hyp-live",
        reasoning="score improves because runtime drops",
        score_before=baseline,
        worktree=tmp_path,
        scorer=scorer,
    )
    verifier.verify_worktree(
        hypothesis_id="hyp-live",
        reasoning="score improves because runtime drops",
        score_before=baseline,
        worktree=tmp_path,
        scorer=scorer,
    )

    assert scorer.calls == [tmp_path, tmp_path]
