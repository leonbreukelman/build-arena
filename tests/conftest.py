from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CALIBRATION_REPO = PROJECT_ROOT / ".arena" / "calibration" / "repo"


def run(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=cwd, text=True, capture_output=True, check=True)


@pytest.fixture
def project_root() -> Path:
    return PROJECT_ROOT


@pytest.fixture
def calibration_repo(tmp_path: Path) -> Path:
    target = tmp_path / "calibration-repo"
    shutil.copytree(CALIBRATION_REPO, target)
    run(["git", "init", "-b", "main"], target)
    run(["git", "config", "user.email", "arena@example.invalid"], target)
    run(["git", "config", "user.name", "Arena Tests"], target)
    run(["git", "add", "."], target)
    run(["git", "commit", "-m", "baseline"], target)
    return target
