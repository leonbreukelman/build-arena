from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass, field

from mabwiser.mab import MAB, LearningPolicy

from arena.fingerprints import compute_fingerprint
from arena.generated.models import Fingerprint, Hypothesis


class EmptyArmSetError(ValueError):
    pass


@dataclass(frozen=True)
class Arm:
    technique_tag: str
    target_cluster: str
    target_files: tuple[str, ...]
    intent_template: str = "Improve {target_cluster} with {technique_tag}"

    @property
    def key(self) -> str:
        return f"{self.technique_tag}×{self.target_cluster}"

    def intent(self) -> str:
        return self.intent_template.format(
            target_cluster=self.target_cluster,
            technique_tag=self.technique_tag,
            target_files=", ".join(self.target_files),
        )


@dataclass
class ArmStats:
    pulls: int = 0
    reward_sum: float = 0.0

    @property
    def mean_reward(self) -> float:
        if self.pulls == 0:
            return 0.0
        return self.reward_sum / self.pulls


class UCB1Bandit:
    def __init__(self, arms: list[Arm], *, alpha: float = 1.25) -> None:
        if not arms:
            raise EmptyArmSetError("at least one bandit arm is required")
        self.arms = arms
        self.alpha = alpha
        self.stats: dict[str, ArmStats] = {arm.key: ArmStats() for arm in arms}
        self._decisions: list[str] = []
        self._rewards: list[float] = []

    def select_arm(self) -> Arm:
        for arm in self.arms:
            if self.stats[arm.key].pulls == 0:
                return arm
        selected_key = self._mabwiser_predict()
        return self._arm_by_key(selected_key)

    def record_reward(self, arm: Arm, reward: float) -> None:
        stats = self.stats[arm.key]
        stats.pulls += 1
        stats.reward_sum += reward
        self._decisions.append(arm.key)
        self._rewards.append(reward)

    def _mabwiser_predict(self) -> str:
        mab = MAB(
            arms=[arm.key for arm in self.arms],
            learning_policy=LearningPolicy.UCB1(alpha=self.alpha),
            seed=123456,
        )
        mab.fit(self._decisions, self._rewards)
        prediction = mab.predict()
        return str(prediction)

    def _arm_by_key(self, key: str) -> Arm:
        for arm in self.arms:
            if arm.key == key:
                return arm
        raise KeyError(key)


@dataclass(frozen=True)
class HypothesisProposal:
    hypothesis: Hypothesis
    fingerprint: Fingerprint
    arm: Arm


@dataclass
class SymbolicHypothesizer:
    bandit: UCB1Bandit
    embedding_model: str | None = None
    _ordinal: int = field(default=0, init=False)

    def propose(self, *, cycle_id: str, ast_diff_pattern: str) -> HypothesisProposal:
        arm = self.bandit.select_arm()
        intent = arm.intent()
        kwargs = {}
        if self.embedding_model is not None:
            kwargs["embedding_model"] = self.embedding_model
        fingerprint = compute_fingerprint(
            intent=intent,
            target_files=arm.target_files,
            technique_tag=arm.technique_tag,
            ast_diff_pattern=ast_diff_pattern,
            first_seen_cycle_id=cycle_id,
            **kwargs,
        )
        self._ordinal += 1
        hypothesis_id = _hypothesis_id(cycle_id, fingerprint.id, self._ordinal)
        hypothesis = Hypothesis(
            id=hypothesis_id,
            cycle_id=cycle_id,
            intent=intent,
            technique_tag=arm.technique_tag,
            target_cluster=arm.target_cluster,
            target_files=list(arm.target_files),
            fingerprint_id=fingerprint.id,
            proposed_ts=time.time(),
        )
        return HypothesisProposal(hypothesis=hypothesis, fingerprint=fingerprint, arm=arm)


def _hypothesis_id(cycle_id: str, fingerprint_id: str, ordinal: int) -> str:
    digest = hashlib.sha256(f"{cycle_id}\0{fingerprint_id}\0{ordinal}".encode()).hexdigest()[:12]
    return f"hyp-{cycle_id}-{digest}"
