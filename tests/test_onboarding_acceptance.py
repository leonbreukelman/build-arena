"""Acceptance test for the Build Arena onboarding cycle — THE RULER.

This is the frozen discrimination test for repo decomposition. It proves that
``arena.onboard.decompose_project`` produces a Project Model that:

  1. validates against the frozen JSON Schema,
  2. is deterministic (identical across runs, stable ``id``),
  3. is tied to verifiable git truth (headOid),
  4. accounts for every file (coverage-closure partition — the "thorough"
     guarantee: nothing dropped, nothing fabricated),
  5. recovers the known structural components of the arena-calibration fixture,
  6. recovers the known manifest-derived gap (patch_generalization_axis_missing
     on F3_bad_passes_tests),
  7. actually drives the intake scorecard to a deterministic ranked finding list
     (the operator's goal: rank requirements/improvements).

Until ``arena/onboard.py`` exists, the `model` fixture errors loudly — that is
the intended RED state, not a skip.

Run:
    ARENA_CALIBRATION_PATH=/path/to/arena-calibration uv run pytest \
        tests/test_onboarding_acceptance.py -q

This file is part of the frozen contract. Do not weaken assertions to make an
implementation pass; fix the implementation. Tightening (adding assertions) is
allowed; loosening requires an explicit operator decision.
"""

from __future__ import annotations

import json
import os
import subprocess
import tempfile
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
FROZEN_SCHEMA_PATH = REPO_ROOT / "docs" / "schemas" / "project-model.frozen-v1.json"

# Known structural surfaces of the arena-calibration fixture that a *thorough*
# decomposition must own (layout-grounded, confirmed against the real repo).
REQUIRED_OWNED_PREFIXES = ("fixtures/", "arena/", "tests/", "docs/")
REQUIRED_OWNED_FILES = ("pyproject.toml",)
KNOWN_FIXTURE_DIRS = (
    "fixtures/F1_loadbearing_good",
    "fixtures/F2_fabricated_good",
    "fixtures/F3_bad_passes_tests",
    "fixtures/F4_trivial",
)
KNOWN_GAP_KIND = "patch_generalization_axis_missing"
KNOWN_GAP_ANCHOR = "F3_bad_passes_tests"


def _calibration_path() -> Path:
    raw = os.environ.get("ARENA_CALIBRATION_PATH")
    if not raw:
        pytest.skip(
            "Set ARENA_CALIBRATION_PATH to a checkout of the arena-calibration "
            "fixture repo to run the onboarding acceptance test."
        )
    path = Path(raw).resolve()
    if not (path / ".git").exists():
        pytest.skip(f"ARENA_CALIBRATION_PATH={path} is not a git checkout.")
    return path


def _canonical(model: dict) -> str:
    return json.dumps(model, sort_keys=True, separators=(",", ":"))


def _git_head(path: Path) -> str:
    out = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=path, text=True, capture_output=True, check=True
    )
    return out.stdout.strip()


@pytest.fixture(scope="module")
def schema() -> dict:
    assert FROZEN_SCHEMA_PATH.exists(), f"Frozen schema not found at {FROZEN_SCHEMA_PATH}"
    return json.loads(FROZEN_SCHEMA_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def fixture_repo() -> Path:
    return _calibration_path()


@pytest.fixture(scope="module")
def model(fixture_repo: Path) -> dict:
    # Imported here (not at module top) so a missing implementation surfaces as a
    # clear fixture error per test rather than a collection crash.
    from arena.onboard import decompose_project

    return decompose_project(str(fixture_repo))


@pytest.fixture(scope="module")
def nodes_by_id(model: dict) -> dict:
    return {n["id"]: n for n in model["projectGraph"]["nodes"]}


# --------------------------------------------------------------------------- #
# 1. Schema validity
# --------------------------------------------------------------------------- #
def test_model_validates_against_frozen_schema(model: dict, schema: dict) -> None:
    jsonschema = pytest.importorskip("jsonschema")
    jsonschema.Draft202012Validator(schema).validate(model)
    assert model["schemaVersion"] == "project-model/frozen-v1"


# --------------------------------------------------------------------------- #
# 2. Determinism (the instrument must not move on its own)
# --------------------------------------------------------------------------- #
def test_decomposition_is_deterministic(fixture_repo: Path, model: dict) -> None:
    from arena.onboard import decompose_project

    second = decompose_project(str(fixture_repo))
    assert _canonical(second) == _canonical(model), "Two runs on unchanged HEAD differ."
    assert second["id"] == model["id"], "Model id is not stable across runs."


def test_id_is_content_addressed(model: dict) -> None:
    # id must be derivable from the rest of the content; recomputing without `id`
    # must reproduce it. (Implementation detail of the digest is the agent's, but
    # the property is fixed: id excludes itself and is reproducible.)
    import hashlib

    without_id = {k: v for k, v in model.items() if k != "id"}
    digest = hashlib.sha256(_canonical(without_id).encode()).hexdigest()
    assert model["id"] in (digest, digest[: len(model["id"])]), (
        "id is not a stable content digest of the model minus id. If you used "
        "blake2b or a different length, update this assertion deliberately."
    )


# --------------------------------------------------------------------------- #
# 3. Git provenance
# --------------------------------------------------------------------------- #
def test_provenance_matches_git_head(fixture_repo: Path, model: dict) -> None:
    head = _git_head(fixture_repo)
    recorded = model["provenance"]["git"]["headOid"]
    assert head == recorded or head.startswith(recorded), (
        f"provenance.git.headOid {recorded!r} does not match fixture HEAD {head!r}"
    )


# --------------------------------------------------------------------------- #
# 4. Coverage closure — the "thorough decomposition" guarantee
# --------------------------------------------------------------------------- #
def test_paths_are_relative_posix(model: dict) -> None:
    for node in model["projectGraph"]["nodes"]:
        p = node["path"]
        assert not p.startswith("/"), f"absolute path leaked: {p}"
        assert ".." not in Path(p).parts, f"'..' in path: {p}"
        assert "\\" not in p, f"non-posix separator in path: {p}"


def test_every_file_is_accounted_for(model: dict, nodes_by_id: dict) -> None:
    file_ids = {n["id"] for n in model["projectGraph"]["nodes"] if n["kind"] == "file"}
    owned: set[str] = set()
    for component in model["snapshot"]["components"]:
        owned |= set(component["owned_node_ids"])
    unclassified = set(model["snapshot"]["unclassified_node_ids"])

    # No file may be both owned and unclassified.
    assert owned.isdisjoint(unclassified), f"overlap: {sorted(owned & unclassified)}"
    # Owned and unclassified must reference real nodes only (no fabricated ids).
    all_ids = set(nodes_by_id)
    assert owned <= all_ids, f"owned references unknown nodes: {sorted(owned - all_ids)}"
    assert unclassified <= all_ids, f"unclassified references unknown nodes: {sorted(unclassified - all_ids)}"
    # The partition must cover exactly the file set — nothing dropped, nothing invented.
    assert owned | unclassified == file_ids, (
        f"coverage gap: unaccounted={sorted(file_ids - (owned | unclassified))} "
        f"phantom={sorted((owned | unclassified) - file_ids)}"
    )


# --------------------------------------------------------------------------- #
# 5. Known structural components of the fixture
# --------------------------------------------------------------------------- #
def test_required_surfaces_are_owned(model: dict, nodes_by_id: dict) -> None:
    owned_paths = {
        nodes_by_id[nid]["path"]
        for component in model["snapshot"]["components"]
        for nid in component["owned_node_ids"]
        if nid in nodes_by_id
    }
    for prefix in REQUIRED_OWNED_PREFIXES:
        assert any(p.startswith(prefix) for p in owned_paths), f"no component owns {prefix}"
    for exact in REQUIRED_OWNED_FILES:
        assert exact in owned_paths, f"config surface not owned: {exact}"


def test_known_fixtures_present_in_graph(model: dict) -> None:
    paths = {n["path"] for n in model["projectGraph"]["nodes"]}
    for fixture_dir in KNOWN_FIXTURE_DIRS:
        assert any(p == fixture_dir or p.startswith(fixture_dir + "/") for p in paths), (
            f"fixture surface missing from graph: {fixture_dir}"
        )


# --------------------------------------------------------------------------- #
# 6. Known manifest-derived gap (the discrimination payload)
# --------------------------------------------------------------------------- #
def test_known_patch_generalization_gap_is_recovered(model: dict) -> None:
    gaps = model["snapshot"]["verification_gaps"]
    matching = [g for g in gaps if g["kind"] == KNOWN_GAP_KIND]
    assert matching, (
        f"expected a {KNOWN_GAP_KIND!r} gap; got kinds {[g['kind'] for g in gaps]}"
    )
    assert any(
        KNOWN_GAP_ANCHOR in (g.get("path", "") + " " + g.get("description", "")) for g in matching
    ), f"{KNOWN_GAP_KIND} gap is not anchored to {KNOWN_GAP_ANCHOR}"


# --------------------------------------------------------------------------- #
# 7. Quality gates are discoverable (ranking realism)
# --------------------------------------------------------------------------- #
def test_quality_gates_discovered(model: dict) -> None:
    gates = model["iterationReadiness"]["qualityGates"]
    assert len(gates) >= 1, "no quality gates discovered; ranking will fire a false 'no gates' high finding"
    assert all(g.get("command") for g in gates), "a quality gate has no command"


# --------------------------------------------------------------------------- #
# 8. The model drives the intake scorecard to a deterministic ranking
#    (this is the operator's actual goal)
# --------------------------------------------------------------------------- #
def test_model_drives_deterministic_ranking(fixture_repo: Path, model: dict) -> None:
    from arena.project_intake_scorecard import build_project_intake_scorecard

    with tempfile.TemporaryDirectory() as tmp:
        model_path = Path(tmp) / "project-model.frozen-v1.json"
        model_path.write_text(_canonical(model), encoding="utf-8")

        sc1 = build_project_intake_scorecard(fixture_repo, model_path, profile="active-development")
        sc2 = build_project_intake_scorecard(fixture_repo, model_path, profile="active-development")

    findings1 = sc1["findings"]
    assert findings1, "scorecard produced no findings from the model"
    assert findings1[0]["rank"] == 1
    assert sc1["firstRecommendedImprovement"]["findingId"] == findings1[0]["id"]
    # Ranking must be deterministic given the same model.
    assert [f["id"] for f in findings1] == [f["id"] for f in sc2["findings"]], "ranking is non-deterministic"
