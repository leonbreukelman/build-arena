from __future__ import annotations

from pathlib import Path

from arena.generated.models import VerdictOutcome
from verifier.calibration import calibrate_verifier


def test_verifier_calibration_measures_fp_and_fn_separately(project_root: Path, tmp_path: Path) -> None:
    report = calibrate_verifier(project_root, tmp_path)

    assert report.total_positive == 5
    assert report.total_negative_or_neutral == 8
    assert report.false_positive_count == 0
    assert report.false_positive_rate == 0.0
    assert report.false_negative_count == 0
    assert report.false_negative_rate <= 0.10
    assert report.meets_targets is True
    assert len(report.case_results) == 13

    false_positives = [
        case.patch_id
        for case in report.case_results
        if case.expected_label != "positive" and case.outcome == VerdictOutcome.PROMOTED
    ]
    assert false_positives == []


def test_verifier_calibration_records_reject_reasons(project_root: Path, tmp_path: Path) -> None:
    report = calibrate_verifier(project_root, tmp_path)

    discarded = [case for case in report.case_results if case.outcome == VerdictOutcome.DISCARDED]
    assert discarded
    assert all(case.reject_reason is not None for case in discarded)
