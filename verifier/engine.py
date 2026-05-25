from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from arena.generated.models import AblationResult, RejectReason, Verdict, VerdictOutcome
from scorer.engine import ScoreRecord, pinned_regressions
from verifier.ablation import AblationRequest, AblationRunner, DeterministicOllamaAblationRunner
from verifier.config import VerifierConfig


@dataclass(frozen=True)
class PatchVerificationInput:
    hypothesis_id: str
    reasoning: str
    score_before: ScoreRecord
    score_after: ScoreRecord


@dataclass(frozen=True)
class VerificationResult:
    verdict: Verdict
    ablation_result: AblationResult


class ScorerLike(Protocol):
    def score_repo(self, repo: Path) -> ScoreRecord: ...


class Verifier:
    def __init__(
        self,
        config: VerifierConfig | None = None,
        ablation_runner: AblationRunner | None = None,
    ) -> None:
        self.config = config or VerifierConfig()
        self.ablation_runner = ablation_runner or DeterministicOllamaAblationRunner()
        if self.ablation_runner.name != self.config.ablation_runner:
            raise ValueError(
                f"ablation runner mismatch: config={self.config.ablation_runner.value}, "
                f"runner={self.ablation_runner.name.value}"
            )

    def verify_worktree(
        self,
        *,
        hypothesis_id: str,
        reasoning: str,
        score_before: ScoreRecord,
        worktree: Path,
        scorer: ScorerLike,
    ) -> VerificationResult:
        """Score the live worktree on every call, then verify it.

        This deliberately accepts a scorer dependency instead of a cached
        candidate record so Phase 2 preserves the anti-fabrication rule that
        verification re-reads the live worktree rather than relying on stale
        probe or score results.
        """
        score_after = scorer.score_repo(worktree)
        return self.verify(
            PatchVerificationInput(
                hypothesis_id=hypothesis_id,
                reasoning=reasoning,
                score_before=score_before,
                score_after=score_after,
            )
        )

    def verify(self, request: PatchVerificationInput) -> VerificationResult:
        score_delta = round(request.score_after.vector.composite - request.score_before.vector.composite, 6)
        pinned = tuple(regression.axis for regression in pinned_regressions(request.score_before.vector, request.score_after.vector))
        ablation_request = AblationRequest(
            hypothesis_id=request.hypothesis_id,
            reasoning=request.reasoning,
            score_delta=score_delta,
            tests_passed=request.score_after.vector.tests_pass,
            pinned_regressions=pinned,
        )
        probe_outcomes = [
            self.ablation_runner.run_probe(ablation_request, probe) for probe in self.config.probe_set
        ]
        probes_changed_output = sum(outcome.changed_output for outcome in probe_outcomes)
        load_bearing = probes_changed_output >= self.config.quorum_threshold
        verdict_id = _short_id(
            "verdict",
            request.hypothesis_id,
            request.score_before.id,
            request.score_after.id,
            str(score_delta),
            str(probes_changed_output),
        )
        ablation_result = AblationResult(
            id=_short_id("ablation", verdict_id, *(f"{outcome.probe.value}:{outcome.changed_output}" for outcome in probe_outcomes)),
            verdict_id=verdict_id,
            probe_set=list(self.config.probe_set),
            probes_changed_output=probes_changed_output,
            quorum_threshold=self.config.quorum_threshold,
            load_bearing=load_bearing,
            runner_used=self.ablation_runner.name,
        )
        reject_reason = self._reject_reason(request, score_delta, pinned, load_bearing)
        outcome = VerdictOutcome.DISCARDED if reject_reason else VerdictOutcome.PROMOTED
        verdict = Verdict(
            id=verdict_id,
            hypothesis_id=request.hypothesis_id,
            outcome=outcome,
            reject_reason=reject_reason,
            score_delta=score_delta,
            score_before_id=request.score_before.id,
            score_after_id=request.score_after.id,
            tests_passed=request.score_after.vector.tests_pass,
            pinned_regression=list(pinned) or None,
            ablation_result_id=ablation_result.id,
            decided_ts=time.time(),
        )
        return VerificationResult(verdict=verdict, ablation_result=ablation_result)

    def _reject_reason(
        self,
        request: PatchVerificationInput,
        score_delta: float,
        pinned: tuple[str, ...],
        load_bearing: bool,
    ) -> RejectReason | None:
        if self.config.require_tests_pass and not request.score_after.vector.tests_pass:
            return RejectReason.TEST_FAILURE
        if pinned:
            return RejectReason.PINNED_METRIC_REGRESSION
        if self.config.require_score_delta_gt0 and score_delta <= 0:
            return RejectReason.SCORE_DELTA_NONPOSITIVE
        if not load_bearing:
            return RejectReason.ABLATION_REASONING_NOT_LOAD_BEARING
        return None


def _short_id(prefix: str, *parts: str) -> str:
    digest = hashlib.sha256("\0".join(parts).encode("utf-8")).hexdigest()[:16]
    return f"{prefix}-{digest}"
