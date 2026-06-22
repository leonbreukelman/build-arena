from __future__ import annotations

import json
import logging
import subprocess
from pathlib import Path

from arena.project_decomposer_ai import build_project_model_snapshot

UNIVERSAL_CATEGORIES = {"anti_fabrication", "determinism", "provenance", "no_live_paid_api_acceptance"}


def _run(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=cwd, text=True, capture_output=True, check=True)


def _init_repo(root: Path) -> None:
    _run(["git", "init", "-b", "main"], root)
    _run(["git", "config", "user.email", "arena@example.invalid"], root)
    _run(["git", "config", "user.name", "Arena Tests"], root)
    _run(["git", "add", "."], root)
    _run(["git", "commit", "-m", "baseline"], root)


def _write_contract_repo(repo: Path) -> None:
    (repo / "pkg").mkdir()
    (repo / "tests").mkdir()
    (repo / "pkg" / "__init__.py").write_text("", encoding="utf-8")
    (repo / "pkg" / "config.py").write_text("VALUE = 1\n", encoding="utf-8")
    (repo / "pkg" / "client.py").write_text(
        "from pkg.config import VALUE\n\ndef fetch() -> int:\n    return VALUE\n",
        encoding="utf-8",
    )
    (repo / "pkg" / "server.py").write_text(
        "from pkg.client import fetch\nfrom pkg.config import VALUE\n\ndef run() -> int:\n    return fetch() + VALUE\n",
        encoding="utf-8",
    )
    (repo / "tests" / "test_server.py").write_text(
        "from pkg.server import run\n\ndef test_run():\n    assert run() == 2\n",
        encoding="utf-8",
    )
    (repo / "pyproject.toml").write_text(
        "[project]\nname='live-repair-repo'\nversion='0.0.0'\n",
        encoding="utf-8",
    )
    _init_repo(repo)


def _fixture_raw(repo: Path, artifacts: Path, project_id: str) -> dict[str, object]:
    fixture = build_project_model_snapshot(
        repo,
        artifacts,
        project_id=project_id,
        llm_mode="fixture",
        overwrite=True,
    )
    return json.loads((fixture.snapshot_dir / "model-outputs" / "decomposer.raw.json").read_text(encoding="utf-8"))


def test_recorded_live_output_repairs_universal_concern_provenance(tmp_path: Path, caplog) -> None:
    repo = tmp_path / "live-drift"
    repo.mkdir()
    _write_contract_repo(repo)
    artifacts = tmp_path / "artifacts"
    raw = _fixture_raw(repo, artifacts, "live-drift")
    components = raw["components"]
    assert isinstance(components, list)
    target_component = components[0]
    assert isinstance(target_component, dict)
    target_component["name"] = "Reporting Module"
    target_component["responsibility"] = "Generate reporting summaries for validation decisions"
    concerns = raw["cross_cutting_concerns"]
    assert isinstance(concerns, list)
    drifted_concern_ids: set[str] = set()
    for concern in concerns:
        assert isinstance(concern, dict)
        if concern["category"] in UNIVERSAL_CATEGORIES:
            concern["id"] = f"ccc:{concern['category']}"
            concern["provenance_refs"] = []
            drifted_concern_ids.add(str(concern["id"]))
    recorded_path = tmp_path / "recorded-live-drift.json"
    recorded_path.write_text(json.dumps(raw, indent=2), encoding="utf-8")

    caplog.set_level(logging.WARNING, logger="arena.project_decomposer_ai")
    result = build_project_model_snapshot(
        repo,
        artifacts,
        project_id="live-drift",
        llm_mode="recorded",
        model_output_path=recorded_path,
        overwrite=True,
    )

    assert result.gate_report.passed is True
    repaired_component = next(component for component in result.snapshot.components if component.id == target_component["id"])
    assert repaired_component.responsibility == "Generate reporting summaries for validation decisions"
    repaired_concerns = {concern.id: concern for concern in result.snapshot.cross_cutting_concerns}
    assert all(repaired_concerns[concern_id].provenance_refs for concern_id in drifted_concern_ids)
    assert any("Backfilled universal concern provenance" in record.message for record in caplog.records)
    persisted_raw = json.loads((result.snapshot_dir / "model-outputs" / "decomposer.raw.json").read_text(encoding="utf-8"))
    assert persisted_raw["components"][0]["responsibility"] == "Generate reporting summaries for validation decisions"
    assert all(
        concern["provenance_refs"] == []
        for concern in persisted_raw["cross_cutting_concerns"]
        if concern["id"] in drifted_concern_ids
    )


def test_recorded_live_output_canonicalizes_universal_concern_category_from_exact_id(tmp_path: Path, caplog) -> None:
    repo = tmp_path / "thematic-category"
    repo.mkdir()
    _write_contract_repo(repo)
    artifacts = tmp_path / "artifacts"
    raw = _fixture_raw(repo, artifacts, "thematic-category")
    thematic = {
        "anti_fabrication": "integrity",
        "determinism": "reliability",
        "provenance": "traceability",
        "no_live_paid_api_acceptance": "compliance",
    }
    concerns = raw["cross_cutting_concerns"]
    assert isinstance(concerns, list)
    for concern in concerns:
        assert isinstance(concern, dict)
        if concern["category"] in thematic:
            canonical = str(concern["category"])
            concern["id"] = f"ccc:{canonical}"
            concern["category"] = thematic[canonical]
            concern["provenance_refs"] = []
    recorded_path = tmp_path / "recorded-thematic-category.json"
    recorded_path.write_text(json.dumps(raw, indent=2), encoding="utf-8")

    caplog.set_level(logging.WARNING, logger="arena.project_decomposer_ai")
    result = build_project_model_snapshot(
        repo,
        artifacts,
        project_id="thematic-category",
        llm_mode="recorded",
        model_output_path=recorded_path,
        overwrite=True,
    )

    assert result.gate_report.passed is True
    categories = {concern.category for concern in result.snapshot.cross_cutting_concerns}
    assert set(thematic) <= categories
    assert any("Canonicalized universal concern category" in record.message for record in caplog.records)
    assert any("Backfilled universal concern provenance" in record.message for record in caplog.records)
    persisted_raw = json.loads((result.snapshot_dir / "model-outputs" / "decomposer.raw.json").read_text(encoding="utf-8"))
    persisted_concerns = persisted_raw["cross_cutting_concerns"]
    assert isinstance(persisted_concerns, list)
    drifted = [concern for concern in persisted_concerns if isinstance(concern, dict) and str(concern["id"]).startswith("ccc:")]
    assert {concern["category"] for concern in drifted} == set(thematic.values())
    assert all(concern["provenance_refs"] == [] for concern in drifted)


def test_recorded_live_output_does_not_canonicalize_thematic_non_alias_category(tmp_path: Path) -> None:
    repo = tmp_path / "non-alias-category"
    repo.mkdir()
    _write_contract_repo(repo)
    artifacts = tmp_path / "artifacts"
    raw = _fixture_raw(repo, artifacts, "non-alias-category")
    concerns = raw["cross_cutting_concerns"]
    assert isinstance(concerns, list)
    provenance = next(concern for concern in concerns if isinstance(concern, dict) and concern["category"] == "provenance")
    provenance["id"] = "concern.traceability"
    provenance["category"] = "traceability"
    recorded_path = tmp_path / "recorded-non-alias-category.json"
    recorded_path.write_text(json.dumps(raw, indent=2), encoding="utf-8")

    result = build_project_model_snapshot(
        repo,
        artifacts,
        project_id="non-alias-category",
        llm_mode="recorded",
        model_output_path=recorded_path,
        overwrite=True,
    )

    repaired = next(concern for concern in result.snapshot.cross_cutting_concerns if concern.id == "concern.traceability")
    assert repaired.category == "traceability"
    assert result.gate_report.passed is False
    assert any("Missing universal concerns: provenance" in violation.message for violation in result.gate_report.violations)


def test_recorded_live_output_keeps_canonical_category_when_id_disagrees(tmp_path: Path) -> None:
    repo = tmp_path / "id-disagrees"
    repo.mkdir()
    _write_contract_repo(repo)
    artifacts = tmp_path / "artifacts"
    raw = _fixture_raw(repo, artifacts, "id-disagrees")
    concerns = raw["cross_cutting_concerns"]
    assert isinstance(concerns, list)
    determinism = next(concern for concern in concerns if isinstance(concern, dict) and concern["category"] == "determinism")
    determinism["id"] = "ccc:provenance"
    recorded_path = tmp_path / "recorded-id-disagrees.json"
    recorded_path.write_text(json.dumps(raw, indent=2), encoding="utf-8")

    result = build_project_model_snapshot(
        repo,
        artifacts,
        project_id="id-disagrees",
        llm_mode="recorded",
        model_output_path=recorded_path,
        overwrite=True,
    )

    repaired = next(concern for concern in result.snapshot.cross_cutting_concerns if concern.id == "ccc:provenance")
    assert repaired.category == "determinism"


def test_recorded_live_output_does_not_backfill_non_universal_concern(tmp_path: Path) -> None:
    repo = tmp_path / "non-universal-empty"
    repo.mkdir()
    _write_contract_repo(repo)
    artifacts = tmp_path / "artifacts"
    raw = _fixture_raw(repo, artifacts, "non-universal-empty")
    concerns = raw["cross_cutting_concerns"]
    components = raw["components"]
    assert isinstance(concerns, list)
    assert isinstance(components, list)
    component_ids = [component["id"] for component in components if isinstance(component, dict)]
    concerns.append(
        {
            "id": "concern.custom-integrity",
            "category": "custom_integrity",
            "description": "A non-universal concern with deliberately missing provenance.",
            "component_ids": component_ids,
            "contract_ids": [],
            "provenance_refs": [],
        }
    )
    recorded_path = tmp_path / "recorded-non-universal-empty.json"
    recorded_path.write_text(json.dumps(raw, indent=2), encoding="utf-8")

    result = build_project_model_snapshot(
        repo,
        artifacts,
        project_id="non-universal-empty",
        llm_mode="recorded",
        model_output_path=recorded_path,
        overwrite=True,
    )

    custom = next(concern for concern in result.snapshot.cross_cutting_concerns if concern.id == "concern.custom-integrity")
    assert custom.provenance_refs == []
    assert result.gate_report.passed is False
    assert any(violation.location == "cross_cutting_concerns[concern.custom-integrity]" for violation in result.gate_report.violations)


def test_recorded_live_output_does_not_pad_borderline_responsibility(tmp_path: Path) -> None:
    repo = tmp_path / "borderline-short"
    repo.mkdir()
    _write_contract_repo(repo)
    artifacts = tmp_path / "artifacts"
    raw = _fixture_raw(repo, artifacts, "borderline-short")
    components = raw["components"]
    assert isinstance(components, list)
    first_component = components[0]
    assert isinstance(first_component, dict)
    first_component["name"] = "Reporting Module"
    first_component["responsibility"] = "Generate reports and confidence summaries"
    recorded_path = tmp_path / "recorded-borderline-short.json"
    recorded_path.write_text(json.dumps(raw, indent=2), encoding="utf-8")

    result = build_project_model_snapshot(
        repo,
        artifacts,
        project_id="borderline-short",
        llm_mode="recorded",
        model_output_path=recorded_path,
        overwrite=True,
    )

    assert result.gate_report.passed is False
    assert result.snapshot.components[0].responsibility == "Generate reports and confidence summaries"
    assert any(violation.gate == "component_measurability" for violation in result.gate_report.violations)
