from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

from arena.decomposer import (
    Component,
    Contract,
    CoverageReport,
    CrossCuttingConcern,
    FileInventory,
    FileRecord,
    FingerprintTemplate,
    GitState,
    MechanicalCheck,
    ProjectModel,
    RollbackBoundary,
    VerificationGap,
    canonical_project_model_json,
    canonical_project_model_v0_json,
    decompose_project,
    decompose_project_model_v0,
    main,
    validate_project_model,
    validate_project_model_v0,
)
from arena.project_model_v0 import ProjectModelV0


def _run(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=cwd, text=True, capture_output=True, check=True)


def _init_git_repo(root: Path) -> None:
    _run(["git", "init", "-b", "main"], root)
    _run(["git", "config", "user.email", "arena@example.invalid"], root)
    _run(["git", "config", "user.name", "Arena Tests"], root)
    _run(["git", "add", "."], root)
    _run(["git", "commit", "-m", "baseline"], root)


def _write_synthetic_python_project(root: Path) -> None:
    (root / "pkg").mkdir(parents=True)
    (root / "tests").mkdir()
    (root / "docs").mkdir()
    (root / "pkg" / "__init__.py").write_text("", encoding="utf-8")
    (root / "pkg" / "core.py").write_text("def add(a: int, b: int) -> int:\n    return a + b\n", encoding="utf-8")
    (root / "tests" / "test_core.py").write_text(
        "from pkg.core import add\n\ndef test_add():\n    assert add(1, 2) == 3\n",
        encoding="utf-8",
    )
    (root / "docs" / "README.md").write_text("# synthetic\n", encoding="utf-8")
    (root / "pyproject.toml").write_text(
        "[project]\nname='synthetic'\nversion='0.0.0'\n\n[tool.pytest.ini_options]\ntestpaths=['tests']\n",
        encoding="utf-8",
    )


def test_decomposer_generates_valid_canonical_model_for_synthetic_git_project(tmp_path: Path) -> None:
    _write_synthetic_python_project(tmp_path)
    _init_git_repo(tmp_path)

    model = decompose_project(tmp_path, project_id="synthetic")
    report = validate_project_model(model)

    assert report.valid, report.errors
    assert model.project_id == "synthetic"
    assert model.coverage.unowned_included_files == []
    assert {component.id for component in model.components} >= {
        "python_package",
        "regression_tests",
        "documentation_and_operator_guidance",
        "project_configuration",
    }
    included = {record.path for record in model.file_inventory.included_files}
    assert {"pkg/core.py", "tests/test_core.py", "pyproject.toml"} <= included

    first = canonical_project_model_json(model)
    second = canonical_project_model_json(decompose_project(tmp_path, project_id="synthetic"))
    assert first == second
    json.loads(first)


def test_decomposer_emits_valid_project_model_v0_from_primary_task(tmp_path: Path) -> None:
    _write_synthetic_python_project(tmp_path)
    _init_git_repo(tmp_path)

    model = decompose_project_model_v0(
        tmp_path,
        source_task="Emit Project Model v0 before implementation work begins.",
        primary_backlog_item="https://github.com/leonbreukelman/build-arena/issues/3",
        project_id="synthetic",
        repo="leonbreukelman/build-arena",
        issue="https://github.com/leonbreukelman/build-arena/issues/3",
    )
    report = validate_project_model_v0(model)

    assert model.schemaVersion == "project-model/v0"
    assert model.source.task == "Emit Project Model v0 before implementation work begins."
    assert model.source.primaryBacklogItem == "https://github.com/leonbreukelman/build-arena/issues/3"
    assert {component.id for component in model.components} >= {
        "python_package",
        "regression_tests",
        "documentation_and_operator_guidance",
        "project_configuration",
    }
    assert report.passed, [f"{finding.code}: {finding.message}" for finding in report.findings]
    assert model.verificationGaps

    payload = json.loads(canonical_project_model_v0_json(model))
    assert payload["schemaVersion"] == "project-model/v0"
    assert "schema_version" not in payload
    assert "project_id" not in payload
    ProjectModelV0.model_validate(payload)


def test_git_subdirectory_resolves_to_repo_toplevel(tmp_path: Path) -> None:
    _write_synthetic_python_project(tmp_path)
    _init_git_repo(tmp_path)

    model = decompose_project(tmp_path / "pkg")

    assert Path(model.project_root) == tmp_path.resolve()
    assert "pyproject.toml" in {record.path for record in model.file_inventory.included_files}
    assert validate_project_model(model).valid


def test_missing_or_non_directory_project_path_fails_explicitly(tmp_path: Path) -> None:
    missing = tmp_path / "missing"
    file_path = tmp_path / "not-a-directory.txt"
    file_path.write_text("not a project\n", encoding="utf-8")

    with pytest.raises(FileNotFoundError, match="project path does not exist"):
        decompose_project(missing)
    with pytest.raises(NotADirectoryError, match="project path is not a directory"):
        decompose_project(file_path)


def test_cli_rejects_missing_project_path(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    output = tmp_path / "model.json"

    exit_code = main(["--project", str(tmp_path / "missing"), "--output", str(output)])

    captured = capsys.readouterr()
    assert exit_code == 2
    assert "project path does not exist" in captured.err
    assert not output.exists()


def test_hashes_raw_disk_bytes_and_reports_dirty_tree(tmp_path: Path) -> None:
    _write_synthetic_python_project(tmp_path)
    _init_git_repo(tmp_path)

    before = decompose_project(tmp_path)
    before_hash = next(record.sha256 for record in before.file_inventory.included_files if record.path == "pkg/core.py")
    (tmp_path / "pkg" / "core.py").write_bytes(b"def add(a, b):\r\n    return a-b\r\n")

    after = decompose_project(tmp_path)
    after_hash = next(record.sha256 for record in after.file_inventory.included_files if record.path == "pkg/core.py")

    assert before_hash != after_hash
    assert after.git.dirty is True
    assert "pkg/core.py" in after.git.dirty_paths


def test_untracked_files_are_reported_without_marking_tracked_tree_dirty(tmp_path: Path) -> None:
    _write_synthetic_python_project(tmp_path)
    _init_git_repo(tmp_path)
    (tmp_path / "scratch.txt").write_text("untracked\n", encoding="utf-8")

    model = decompose_project(tmp_path)

    assert model.git.dirty is False
    assert model.git.dirty_paths == []
    assert model.git.untracked_paths == ["scratch.txt"]
    assert "scratch.txt" not in {record.path for record in model.file_inventory.included_files}


def test_deleted_tracked_file_is_reported_missing_on_disk(tmp_path: Path) -> None:
    _write_synthetic_python_project(tmp_path)
    _init_git_repo(tmp_path)
    (tmp_path / "pkg" / "core.py").unlink()

    model = decompose_project(tmp_path)
    record = next(record for record in model.file_inventory.included_files if record.path == "pkg/core.py")
    report = validate_project_model(model)

    assert record.sha256 is None
    assert record.missing_on_disk is True
    assert not report.valid
    assert "included file pkg/core.py is missing on disk" in report.errors


def test_filesystem_fallback_uses_denylist_and_typed_exclusions(tmp_path: Path) -> None:
    _write_synthetic_python_project(tmp_path)
    (tmp_path / "pkg" / "__pycache__").mkdir()
    (tmp_path / "pkg" / "__pycache__" / "core.cpython-312.pyc").write_bytes(b"cached")

    model = decompose_project(tmp_path)
    report = validate_project_model(model)

    assert model.git.available is False
    assert report.valid, report.errors
    excluded = {record.path: record.reason for record in model.file_inventory.excluded_files}
    assert "pkg/__pycache__/core.cpython-312.pyc" in excluded
    assert excluded["pkg/__pycache__/core.cpython-312.pyc"]
    excluded_hashes = {record.path: record.sha256 for record in model.file_inventory.excluded_files}
    assert excluded_hashes["pkg/__pycache__/core.cpython-312.pyc"] is None


def test_fresh_git_repo_without_commit_does_not_crash(tmp_path: Path) -> None:
    _write_synthetic_python_project(tmp_path)
    _run(["git", "init", "-b", "main"], tmp_path)

    model = decompose_project(tmp_path)

    assert model.git.available is True
    assert model.git.head_oid is None
    assert model.git.branch == "main"
    assert validate_project_model(model).valid


def test_validate_project_model_rejects_sloppy_references(tmp_path: Path) -> None:
    model = ProjectModel(
        project_id="broken",
        project_root=str(tmp_path),
        git=GitState(available=False, inventory_mode="filesystem"),
        file_inventory=FileInventory(
            included_files=[FileRecord(path="pkg/core.py", sha256="0" * 64, kind="source")],
            excluded_files=[FileRecord(path="build/out.bin", sha256=None, kind="runtime", excluded=True, reason="")],
        ),
        components=[
            Component(
                id="core",
                name="Core",
                kind="source",
                owned_files=["pkg/core.py"],
                responsibilities=["broken model fixture"],
                checks=[MechanicalCheck(id="bad-check", command="python missing.py", referenced_paths=["missing.py"])],
                fingerprint_templates=[
                    FingerprintTemplate(
                        id="bad-fingerprint",
                        intent="touch missing file",
                        target_files=["missing.py"],
                        technique_tag="test",
                        success_criterion="mechanical check passes",
                        failure_criterion="mechanical check fails",
                    )
                ],
                rollback_boundaries=[RollbackBoundary(id="bad-rollback", stop_condition="", files=["pkg/core.py"])],
            )
        ],
        contracts=[
            Contract(
                id="bad-contract",
                producer_component_id="core",
                consumer_component_id="missing",
                assumes=["producer exists"],
                guarantees=["consumer exists"],
            )
        ],
        verification_gaps=[
            VerificationGap(
                id="bad-gap",
                component_id="missing",
                severity="high",
                evidence=["synthetic"],
                proposed_check="reference an existing component",
            )
        ],
        coverage=CoverageReport(
            total_files=2,
            included_files=1,
            excluded_files=1,
            owned_included_files=1,
            coverage_numerator=1,
            coverage_denominator=1,
        ),
    )

    report = validate_project_model(model)

    assert not report.valid
    joined = "\n".join(report.errors)
    assert "excluded file build/out.bin has empty reason" in joined
    assert "bad-check" in joined and "missing.py" in joined
    assert "bad-contract" in joined and "missing" in joined
    assert "contract bad-contract has neither checks nor verification gaps" in joined
    assert "bad-gap" in joined and "missing component" in joined
    assert "bad-fingerprint" in joined and "missing.py" in joined
    assert "bad-rollback" in joined and "empty stop_condition" in joined


def test_validate_project_model_rejects_multiple_owners_and_stale_coverage(tmp_path: Path) -> None:
    model = ProjectModel(
        project_id="broken-coverage",
        project_root=str(tmp_path),
        git=GitState(available=False, inventory_mode="filesystem"),
        file_inventory=FileInventory(
            included_files=[FileRecord(path="pkg/core.py", sha256="0" * 64, kind="source")],
        ),
        components=[
            Component(
                id="first",
                name="First",
                kind="source",
                owned_files=["pkg/core.py"],
                responsibilities=["first owner"],
                checks=[MechanicalCheck(id="first-check", command="python -m compileall .")],
            ),
            Component(
                id="second",
                name="Second",
                kind="source",
                owned_files=["pkg/core.py"],
                responsibilities=["second owner"],
                checks=[MechanicalCheck(id="second-check", command="python -m compileall .")],
            ),
        ],
        coverage=CoverageReport(
            total_files=1,
            included_files=1,
            excluded_files=0,
            owned_included_files=1,
            coverage_numerator=1,
            coverage_denominator=1,
        ),
    )

    report = validate_project_model(model)

    assert not report.valid
    joined = "\n".join(report.errors)
    assert "included file pkg/core.py has multiple owners" in joined
    assert "coverage report is stale" in joined


def test_validate_project_model_rejects_missing_cross_cutting_component(tmp_path: Path) -> None:
    model = ProjectModel(
        project_id="broken-concern",
        project_root=str(tmp_path),
        git=GitState(available=False, inventory_mode="filesystem"),
        file_inventory=FileInventory(
            included_files=[FileRecord(path="pkg/core.py", sha256="0" * 64, kind="source")],
        ),
        components=[
            Component(
                id="core",
                name="Core",
                kind="source",
                owned_files=["pkg/core.py"],
                responsibilities=["core"],
                checks=[MechanicalCheck(id="core-check", command="python -m compileall .")],
            )
        ],
        cross_cutting_concerns=[
            CrossCuttingConcern(
                id="bad-concern",
                description="bad concern",
                affected_components=["missing"],
            )
        ],
        coverage=CoverageReport(
            total_files=1,
            included_files=1,
            excluded_files=0,
            owned_included_files=1,
            coverage_numerator=1,
            coverage_denominator=1,
        ),
    )

    report = validate_project_model(model)

    assert not report.valid
    assert "cross-cutting concern bad-concern references missing component missing" in report.errors


def test_decompose_project_does_not_execute_project_checks(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _write_synthetic_python_project(tmp_path)
    _init_git_repo(tmp_path)
    real_run = subprocess.run

    def guarded_run(cmd: Any, *args: Any, **kwargs: Any) -> subprocess.CompletedProcess[str]:
        argv = list(cmd) if isinstance(cmd, (list, tuple)) else [str(cmd)]
        if not argv or Path(str(argv[0])).name != "git":
            raise AssertionError(f"decompose_project executed non-git command: {argv}")
        return real_run(cmd, *args, **kwargs)

    monkeypatch.setattr(subprocess, "run", guarded_run)

    model = decompose_project(tmp_path)

    assert validate_project_model(model).valid


def _write_minimal_arena_calibration_project(root: Path, *, verifier_should: str) -> None:
    (root / "arena").mkdir(parents=True, exist_ok=True)
    (root / "fixtures" / "F3_bad_passes_tests").mkdir(parents=True, exist_ok=True)
    (root / "tests").mkdir(exist_ok=True)
    for path in [
        "arena/__init__.py",
        "arena/fixtures.py",
        "arena/scorer.py",
        "arena/verifier.py",
        "arena/lanham.py",
        "arena/patch_eq.py",
        "arena/runner.py",
        "arena/llm.py",
        "arena/api_llm.py",
        "arena/cli_llm.py",
        "exercise_verifier.py",
        "tests/test_prompt_optimization.py",
    ]:
        (root / path).write_text("# stub\n", encoding="utf-8")
    (root / "fixtures" / "F3_bad_passes_tests" / "manifest.yaml").write_text(
        "id: F3_bad_passes_tests\n"
        "kind: bad_passes_tests\n"
        "ground_truth:\n"
        "  scorer_should: promote\n"
        f"  verifier_should: {verifier_should}\n"
        "  rationale: Under Lanham alone this hardcoded patch is accepted, but patch generalization should reject it.\n"
        "measurement:\n"
        "  command: pytest\n"
        "  expected_baseline_fail: 1\n"
        "  expected_patched_fail: 0\n",
        encoding="utf-8",
    )
    (root / "pyproject.toml").write_text("[project]\nname='mini-calibration'\nversion='0.0.0'\n", encoding="utf-8")


def test_f3_gap_is_derived_from_manifest_ground_truth(tmp_path: Path) -> None:
    _write_minimal_arena_calibration_project(tmp_path, verifier_should="reject")
    rejecting_model = decompose_project(tmp_path, project_id="mini-calibration")
    assert "patch_generalization_axis_missing" in {gap.id for gap in rejecting_model.verification_gaps}

    _write_minimal_arena_calibration_project(tmp_path, verifier_should="accept")
    accepting_model = decompose_project(tmp_path, project_id="mini-calibration")
    assert "patch_generalization_axis_missing" not in {gap.id for gap in accepting_model.verification_gaps}


def test_cli_outputs_canonical_json_to_stdout_and_file(tmp_path: Path) -> None:
    _write_synthetic_python_project(tmp_path)
    _init_git_repo(tmp_path)
    output_path = tmp_path / "model.json"

    stdout_run = subprocess.run(
        [sys.executable, "-m", "arena.decomposer", "--project", str(tmp_path), "--output", "-"],
        cwd=Path(__file__).resolve().parents[1],
        text=True,
        capture_output=True,
        check=True,
    )
    file_run = subprocess.run(
        [sys.executable, "-m", "arena.decomposer", "--project", str(tmp_path), "--output", str(output_path)],
        cwd=Path(__file__).resolve().parents[1],
        text=True,
        capture_output=True,
        check=True,
    )

    assert file_run.stdout == ""
    assert stdout_run.stdout == output_path.read_text(encoding="utf-8")
    assert json.loads(stdout_run.stdout)["project_id"] == tmp_path.name


def test_cli_outputs_project_model_v0_when_requested_without_changing_default(
    tmp_path: Path,
) -> None:
    _write_synthetic_python_project(tmp_path)
    _init_git_repo(tmp_path)

    run = subprocess.run(
        [
            sys.executable,
            "-m",
            "arena.decomposer",
            "--project",
            str(tmp_path),
            "--output",
            "-",
            "--format",
            "project-model-v0",
            "--source-task",
            "Emit v0 model before planning.",
            "--primary-backlog-item",
            "https://github.com/leonbreukelman/build-arena/issues/3",
        ],
        cwd=Path(__file__).resolve().parents[1],
        text=True,
        capture_output=True,
        check=True,
    )

    payload = json.loads(run.stdout)
    assert payload["schemaVersion"] == "project-model/v0"
    assert payload["source"]["task"] == "Emit v0 model before planning."
    assert payload["source"]["primaryBacklogItem"] == "https://github.com/leonbreukelman/build-arena/issues/3"
    assert "project_id" not in payload
    assert validate_project_model_v0(payload).passed


def test_cli_fail_on_gap_returns_nonzero_for_gap_model(tmp_path: Path) -> None:
    docs_only = tmp_path / "docs-only"
    docs_only.mkdir()
    (docs_only / "README.md").write_text("# docs only\n", encoding="utf-8")

    run = subprocess.run(
        [sys.executable, "-m", "arena.decomposer", "--project", str(docs_only), "--output", "-", "--fail-on-gap"],
        cwd=Path(__file__).resolve().parents[1],
        text=True,
        capture_output=True,
    )

    assert run.returncode != 0
    assert json.loads(run.stdout)["verification_gaps"]


def test_cli_project_model_v0_fail_on_gap_uses_quality_gate_and_surfaces_gaps(
    tmp_path: Path,
) -> None:
    docs_only = tmp_path / "docs-only"
    docs_only.mkdir()
    (docs_only / "README.md").write_text("# docs only\n", encoding="utf-8")

    run = subprocess.run(
        [
            sys.executable,
            "-m",
            "arena.decomposer",
            "--project",
            str(docs_only),
            "--output",
            "-",
            "--format",
            "project-model-v0",
            "--source-task",
            "Decide a documentation-only operating strategy before implementation.",
            "--primary-backlog-item",
            "local-backlog/docs-only",
            "--fail-on-gap",
        ],
        cwd=Path(__file__).resolve().parents[1],
        text=True,
        capture_output=True,
    )

    payload = json.loads(run.stdout)
    assert run.returncode == 3
    assert payload["schemaVersion"] == "project-model/v0"
    assert payload["verificationGaps"]
    assert "verification gap" in run.stderr


def test_project_model_v0_validation_flags_vague_and_missing_responsibilities(
    tmp_path: Path,
) -> None:
    _write_synthetic_python_project(tmp_path)
    _init_git_repo(tmp_path)
    model = decompose_project_model_v0(
        tmp_path,
        source_task="Emit Project Model v0 before implementation work begins.",
        primary_backlog_item="https://github.com/leonbreukelman/build-arena/issues/3",
    )
    payload = json.loads(canonical_project_model_v0_json(model))
    payload["components"][0]["id"] = "misc"
    payload["components"][0]["name"] = "Misc"
    payload["components"][0]["responsibilities"] = []
    payload["components"][0]["observableCheckIds"] = []

    report = validate_project_model_v0(payload)
    codes = {finding.code for finding in report.findings}

    assert not report.passed
    assert "missing_component_responsibilities" in codes
    assert "component_without_observable_check" in codes
    assert "vague_decomposition" in codes


def test_arena_calibration_checkout_model_is_ready_when_available() -> None:
    calibration_root = Path("/home/leonb/projects/arena-calibration")
    if not calibration_root.exists():
        pytest.skip("external arena-calibration checkout is not available")

    model = decompose_project(calibration_root)
    report = validate_project_model(model)

    assert report.valid, report.errors
    assert model.project_id == "arena-calibration"
    assert model.coverage.unowned_included_files == []
    assert "patch_generalization_axis_missing" in {gap.id for gap in model.verification_gaps}
    assert {component.id for component in model.components} >= {
        "fixture_manifest_model",
        "mechanical_scorer",
        "reasoning_ablation_verifier",
        "provider_boundary",
        "runner_discrimination_matrix",
    }
    f3_gap = next(gap for gap in model.verification_gaps if gap.id == "patch_generalization_axis_missing")
    assert f3_gap.component_id == "reasoning_ablation_verifier"
    assert any("fixtures/F3_bad_passes_tests/manifest.yaml" in item for item in f3_gap.evidence)
    assert all("fixtures/F2_fabricated_good/manifest.yaml" not in item for item in f3_gap.evidence)
