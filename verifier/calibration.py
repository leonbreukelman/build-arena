from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

from arena.generated.models import RejectReason, VerdictOutcome
from scorer.engine import Scorer
from verifier.ablation import AblationRunner, DeterministicOllamaAblationRunner
from verifier.config import VerifierConfig
from verifier.engine import PatchVerificationInput, Verifier


@dataclass(frozen=True)
class CalibrationCaseResult:
    patch_id: str
    expected_label: str
    outcome: VerdictOutcome
    reject_reason: RejectReason | None
    score_delta: float


@dataclass(frozen=True)
class CalibrationReport:
    case_results: tuple[CalibrationCaseResult, ...]
    false_positive_count: int
    false_negative_count: int
    total_positive: int
    total_negative_or_neutral: int
    fp_target: float
    fn_target: float

    @property
    def false_positive_rate(self) -> float:
        if self.total_negative_or_neutral == 0:
            return 0.0
        return self.false_positive_count / self.total_negative_or_neutral

    @property
    def false_negative_rate(self) -> float:
        if self.total_positive == 0:
            return 0.0
        return self.false_negative_count / self.total_positive

    @property
    def meets_targets(self) -> bool:
        return self.false_positive_rate <= self.fp_target and self.false_negative_rate <= self.fn_target


def calibrate_verifier(
    project_root: Path,
    tmp_path: Path,
    *,
    config: VerifierConfig | None = None,
    ablation_runner: AblationRunner | None = None,
) -> CalibrationReport:
    scorer = Scorer(project_root)
    active_config = config or VerifierConfig.from_toml(project_root / ".arena" / "config.toml")
    verifier = Verifier(active_config, ablation_runner or DeterministicOllamaAblationRunner())
    case_results: list[CalibrationCaseResult] = []
    for label, patch_path in _iter_patch_catalog(project_root):
        repo = _copy_committed_repo(project_root / ".arena" / "calibration" / "repo", tmp_path / patch_path.stem)
        baseline = scorer.score_repo(repo)
        _run(["git", "apply", str(patch_path)], repo)
        _run(["git", "add", "."], repo)
        _run(["git", "commit", "-m", patch_path.stem], repo)
        candidate = scorer.score_repo(repo)
        result = verifier.verify(
            PatchVerificationInput(
                hypothesis_id=patch_path.stem,
                reasoning=_calibration_reasoning(label, patch_path.stem),
                score_before=baseline,
                score_after=candidate,
            )
        )
        case_results.append(
            CalibrationCaseResult(
                patch_id=patch_path.stem,
                expected_label=label,
                outcome=result.verdict.outcome,
                reject_reason=result.verdict.reject_reason,
                score_delta=float(result.verdict.score_delta or 0.0),
            )
        )
    false_positive_count = sum(
        1 for case in case_results if case.expected_label != "positive" and case.outcome == VerdictOutcome.PROMOTED
    )
    false_negative_count = sum(
        1 for case in case_results if case.expected_label == "positive" and case.outcome != VerdictOutcome.PROMOTED
    )
    total_positive = sum(1 for case in case_results if case.expected_label == "positive")
    total_negative_or_neutral = len(case_results) - total_positive
    return CalibrationReport(
        case_results=tuple(case_results),
        false_positive_count=false_positive_count,
        false_negative_count=false_negative_count,
        total_positive=total_positive,
        total_negative_or_neutral=total_negative_or_neutral,
        fp_target=active_config.fp_target,
        fn_target=active_config.fn_target,
    )


def _iter_patch_catalog(project_root: Path) -> list[tuple[str, Path]]:
    root = project_root / ".arena" / "calibration" / "diffs"
    cases: list[tuple[str, Path]] = []
    for label in ("positive", "negative", "neutral"):
        cases.extend((label, path) for path in sorted((root / label).glob("*.patch")))
    return cases


def _copy_committed_repo(src: Path, target: Path) -> Path:
    shutil.copytree(src, target)
    _run(["git", "init", "-b", "main"], target)
    _run(["git", "config", "user.email", "arena@example.invalid"], target)
    _run(["git", "config", "user.name", "Arena Tests"], target)
    _run(["git", "add", "."], target)
    _run(["git", "commit", "-m", "baseline"], target)
    return target


def _run(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=cwd, text=True, capture_output=True, check=True)


def _calibration_reasoning(label: str, patch_id: str) -> str:
    if label == "positive":
        return f"Promote {patch_id} because score improves on calibrated axes while tests and pinned metrics remain safe."
    return f"Discard {patch_id} unless score improves because calibration label is {label}."
