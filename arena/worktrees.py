from __future__ import annotations

import shutil
import subprocess
import time
from pathlib import Path

from arena.generated.models import Baseline, Verdict, Worktree


def _run(args: list[str], *, cwd: Path, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=cwd, text=True, capture_output=True, check=check)


class WorktreeManager:
    """Owns git worktree create/teardown for Phase 4 loop cycles."""

    def __init__(self, *, repo: Path, worktree_root: Path) -> None:
        self.repo = repo.resolve()
        self.worktree_root = worktree_root.resolve()
        self.worktree_root.mkdir(parents=True, exist_ok=True)

    def create(self, cycle_id: str, base_oid: str) -> Worktree:
        path = self.worktree_root / cycle_id
        branch = _branch_name(cycle_id)
        _run(["git", "worktree", "add", "-b", branch, str(path), base_oid], cwd=self.repo)
        lock_reason = f"arena cycle={cycle_id}"
        _run(["git", "worktree", "lock", "--reason", lock_reason, str(path)], cwd=self.repo)
        return Worktree(
            id=cycle_id,
            cycle_id=cycle_id,
            path=str(path),
            base_git_oid=base_oid,
            created_ts=time.time(),
            lock_reason=lock_reason,
        )

    def teardown(self, worktree: Worktree, *, force: bool = True) -> None:
        path = Path(worktree.path)
        _run(["git", "worktree", "unlock", str(path)], cwd=self.repo, check=False)
        remove_cmd = ["git", "worktree", "remove"]
        if force:
            remove_cmd.append("--force")
        remove_cmd.append(str(path))
        _run(remove_cmd, cwd=self.repo, check=False)
        _run(["git", "branch", "-D", _branch_name(worktree.cycle_id)], cwd=self.repo, check=False)

    def reap_orphans(self, *, live_cycle_ids: set[str] | None = None) -> int:
        live_cycle_ids = live_cycle_ids or set()
        removed = 0
        for path in self.worktree_root.iterdir() if self.worktree_root.exists() else []:
            if not path.is_dir() or path.name in live_cycle_ids:
                continue
            worktree = Worktree(
                id=path.name,
                cycle_id=path.name,
                path=str(path),
                base_git_oid="0" * 40,
                created_ts=time.time(),
            )
            self.teardown(worktree)
            removed += 1
        _run(["git", "worktree", "prune", "--verbose"], cwd=self.repo, check=False)
        return removed


class GitPromoter:
    """ff-only promoter from a cycle branch into the main repo checkout."""

    def __init__(self, *, main_repo: Path) -> None:
        self.main_repo = main_repo.resolve()

    def promote(
        self,
        verdict: Verdict,
        worktree: Worktree,
        *,
        run_id: str,
        score_record_id: str,
    ) -> Baseline:
        worktree_path = Path(worktree.path)
        _remove_runtime_artifacts(worktree_path)
        _remove_runtime_artifacts(self.main_repo)
        _run(["git", "add", "-A"], cwd=worktree_path)
        if _run(["git", "diff", "--cached", "--quiet"], cwd=worktree_path, check=False).returncode != 0:
            _run(
                ["git", "commit", "-m", f"arena: {verdict.hypothesis_id}"],
                cwd=worktree_path,
            )
        head_oid = _run(["git", "rev-parse", "HEAD"], cwd=worktree_path).stdout.strip()
        _run(["git", "merge", "--ff-only", _branch_name(worktree.cycle_id)], cwd=self.main_repo)
        return Baseline(
            id=f"baseline-{head_oid[:12]}",
            run_id=run_id,
            git_oid=head_oid,
            score_record_id=score_record_id,
            promoted_from_verdict_id=verdict.id,
            promoted_ts=time.time(),
            is_active=True,
        )


def _remove_runtime_artifacts(repo: Path) -> None:
    for relative in ("coverage.json", ".coverage"):
        path = repo / relative
        if path.exists():
            path.unlink()
    for relative in (".pytest_cache",):
        path = repo / relative
        if path.exists():
            shutil.rmtree(path)
    for root in (repo / "src", repo / "tests"):
        if not root.exists():
            continue
        for pycache in root.rglob("__pycache__"):
            shutil.rmtree(pycache, ignore_errors=True)


def _branch_name(cycle_id: str) -> str:
    return f"arena/cycle/{cycle_id}"
