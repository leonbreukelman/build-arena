from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from scorer.exceptions import ScorerLockMismatchError
from scorer.lock import DEFAULT_LOCK_PATH, load_scorer_lock


def test_scorer_lock_exists_and_validates(project_root: Path) -> None:
    lock_path = project_root / DEFAULT_LOCK_PATH
    assert lock_path.exists()
    lock = load_scorer_lock(project_root)
    assert lock.version == 1
    assert lock.scorer_sha
    assert "scorer/engine.py" in lock.locked_files


def test_scorer_lock_mismatch_refuses_load(tmp_path: Path, project_root: Path) -> None:
    shutil.copytree(project_root / "scorer", tmp_path / "scorer")
    (tmp_path / ".arena").mkdir()
    shutil.copy(project_root / DEFAULT_LOCK_PATH, tmp_path / DEFAULT_LOCK_PATH)
    engine = tmp_path / "scorer" / "engine.py"
    engine.write_text(engine.read_text() + "\n# intentional mutation for test\n")
    with pytest.raises(ScorerLockMismatchError):
        load_scorer_lock(tmp_path)


def test_scorer_lock_rejects_new_scorer_file(tmp_path: Path, project_root: Path) -> None:
    shutil.copytree(project_root / "scorer", tmp_path / "scorer")
    (tmp_path / ".arena").mkdir()
    shutil.copy(project_root / DEFAULT_LOCK_PATH, tmp_path / DEFAULT_LOCK_PATH)
    (tmp_path / "scorer" / "evil.py").write_text("VALUE = 'unlocked scorer mutation'\n")
    with pytest.raises(ScorerLockMismatchError, match="file set"):
        load_scorer_lock(tmp_path)


def test_scorer_lock_rejects_missing_locked_file_as_mismatch(tmp_path: Path, project_root: Path) -> None:
    shutil.copytree(project_root / "scorer", tmp_path / "scorer")
    (tmp_path / ".arena").mkdir()
    shutil.copy(project_root / DEFAULT_LOCK_PATH, tmp_path / DEFAULT_LOCK_PATH)
    (tmp_path / "scorer" / "engine.py").unlink()
    with pytest.raises(ScorerLockMismatchError):
        load_scorer_lock(tmp_path)
