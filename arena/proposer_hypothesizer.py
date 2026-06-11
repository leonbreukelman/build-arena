from __future__ import annotations

import hashlib
from dataclasses import dataclass

from arena.fingerprints import compute_fingerprint
from arena.generated.models import Hypothesis
from arena.hypothesizer import Arm, EmptyArmSetError, HypothesisProposal
from arena.target_picker import TargetSelection


@dataclass(frozen=True)
class TargetSelectionHypothesizer:
    selection: TargetSelection
    success_criterion: str
    technique_tag: str = "diff_proposal"

    def propose(self, *, cycle_id: str, ast_diff_pattern: str) -> HypothesisProposal:
        if not self.selection.candidates:
            raise EmptyArmSetError("target selection contains no candidates")
        candidate = self.selection.candidates[0]
        intent = f"Improve {candidate.path}: {self.success_criterion}"
        fingerprint = compute_fingerprint(
            intent=intent,
            target_files=(candidate.path,),
            technique_tag=self.technique_tag,
            ast_diff_pattern=ast_diff_pattern,
            first_seen_cycle_id=cycle_id,
        )
        hypothesis = Hypothesis(
            id=_hypothesis_id(cycle_id, fingerprint.id),
            cycle_id=cycle_id,
            intent=intent,
            technique_tag=self.technique_tag,
            target_cluster=candidate.path,
            target_files=[candidate.path],
            fingerprint_id=fingerprint.id,
            reasoning_blob_sha=self.selection.id,
            proposed_ts=0.0,
        )
        arm = Arm(
            technique_tag=self.technique_tag,
            target_cluster=candidate.path,
            target_files=(candidate.path,),
            intent_template=intent,
        )
        return HypothesisProposal(hypothesis=hypothesis, fingerprint=fingerprint, arm=arm)


def _hypothesis_id(cycle_id: str, fingerprint_id: str) -> str:
    digest = hashlib.sha256(f"{cycle_id}\0{fingerprint_id}".encode()).hexdigest()[:12]
    return f"hyp-{cycle_id}-{digest}"
