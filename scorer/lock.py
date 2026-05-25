"""Content-addressed scorer lock support."""

from __future__ import annotations

import hashlib
import tomllib
from dataclasses import dataclass
from pathlib import Path

from scorer.exceptions import ScorerLockMismatchError

DEFAULT_LOCK_PATH = Path(".arena/scorer.lock.toml")


@dataclass(frozen=True)
class ScorerLock:
    version: int
    scorer_sha: str
    locked_files: tuple[str, ...]


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def default_locked_files(project_root: Path) -> tuple[str, ...]:
    scorer_root = project_root / "scorer"
    return tuple(
        sorted(
            str(path.relative_to(project_root).as_posix())
            for path in scorer_root.rglob("*.py")
            if "__pycache__" not in path.parts
        )
    )


def compute_scorer_tree_sha(project_root: Path, locked_files: tuple[str, ...] | None = None) -> str:
    """Hash scorer files by relative path and content.

    The relative path is included so file renames change the hash even when
    content happens to be identical.
    """

    root = project_root.resolve()
    files = locked_files or default_locked_files(root)
    digest = hashlib.sha256()
    for rel in files:
        path = root / rel
        digest.update(rel.encode("utf-8"))
        digest.update(b"\0")
        try:
            content = path.read_bytes()
        except FileNotFoundError as exc:
            raise ScorerLockMismatchError(f"locked scorer file missing: {rel}") from exc
        digest.update(_sha256_bytes(content).encode("ascii"))
        digest.update(b"\0")
    return digest.hexdigest()


def load_scorer_lock(
    project_root: Path,
    lock_path: Path | None = None,
    *,
    validate: bool = True,
) -> ScorerLock:
    """Load and optionally validate `.arena/scorer.lock.toml`."""

    root = project_root.resolve()
    resolved_lock_path = root / (lock_path or DEFAULT_LOCK_PATH)
    data = tomllib.loads(resolved_lock_path.read_text())
    locked_files = tuple(data["locked_files"])
    lock = ScorerLock(
        version=int(data["version"]),
        scorer_sha=str(data["scorer_sha"]),
        locked_files=locked_files,
    )
    if validate:
        live_locked_files = default_locked_files(root)
        if live_locked_files != locked_files:
            raise ScorerLockMismatchError(
                "scorer lock file set mismatch: "
                f"expected {locked_files}, actual {live_locked_files}"
            )
        actual = compute_scorer_tree_sha(root, locked_files)
        if actual != lock.scorer_sha:
            raise ScorerLockMismatchError(
                f"scorer lock mismatch: expected {lock.scorer_sha}, actual {actual}"
            )
    return lock
