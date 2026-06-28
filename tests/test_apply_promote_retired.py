from __future__ import annotations

import importlib
import importlib.util
import subprocess
import sys
import tomllib
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]

RETIRED_MODULES = (
    "arena.repo_goal_loop",
    "arena.patch_gate",
    "arena.runners.diff_proposer",
    "arena.proposal_candidate_runner",
)

RETIRED_MODULE_PATHS = (
    ROOT / "arena" / "repo_goal_loop.py",
    ROOT / "arena" / "patch_gate.py",
    ROOT / "arena" / "runners" / "diff_proposer.py",
    ROOT / "arena" / "proposal_candidate_runner.py",
)

APPLY_PROMOTE_TERMS = ("apply", "promote", "promotion", "repo-goal", "candidate-runner")


@pytest.mark.parametrize("path", RETIRED_MODULE_PATHS)
def test_retired_apply_promote_module_files_are_deleted(path: Path) -> None:
    assert not path.exists(), f"retired apply/promote module still exists: {path.relative_to(ROOT)}"


@pytest.mark.parametrize("module", RETIRED_MODULES)
def test_retired_apply_promote_modules_are_unimportable(module: str) -> None:
    with pytest.raises(ModuleNotFoundError):
        importlib.import_module(module)

    assert importlib.util.find_spec(module) is None


@pytest.mark.parametrize("module", RETIRED_MODULES)
def test_retired_apply_promote_modules_cannot_be_invoked(module: str) -> None:
    result = subprocess.run(
        [sys.executable, "-m", module, "--help"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode != 0
    assert f"No module named {module}" in result.stderr


def test_no_apply_promote_console_entrypoint_is_registered() -> None:
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    scripts = pyproject.get("project", {}).get("scripts", {})

    offenders = {
        name: target
        for name, target in scripts.items()
        if any(term in name.lower() or term in str(target).lower() for term in APPLY_PROMOTE_TERMS)
    }
    assert offenders == {}
