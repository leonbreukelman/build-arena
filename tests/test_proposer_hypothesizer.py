from __future__ import annotations

import subprocess
from pathlib import Path

from arena.proposer_hypothesizer import TargetSelectionHypothesizer
from arena.target_picker import select_targets


def _run(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=cwd, check=True, capture_output=True, text=True)


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    _write(repo / "src" / "app.py", "# TODO: improve\ndef value() -> int:\n    return 1\n")
    _write(
        repo / ".arena" / "goal.toml",
        """
schema_version = "goal-config/v1"
project_id = "proposer-hypothesis-fixture"

[commands]
test = ["python3", "-c", "pass"]
lint = ["python3", "-c", "pass"]
typecheck = ["python3", "-c", "pass"]

[coverage]
source = "coverage.json"
floor = 0.0

[paths]
source_roots = ["src"]
out_of_scope = []
read_only = []
""".strip()
        + "\n",
    )
    _run(["git", "init", "-b", "main"], repo)
    _run(["git", "config", "user.email", "arena@example.invalid"], repo)
    _run(["git", "config", "user.name", "Arena Tests"], repo)
    _run(["git", "add", "."], repo)
    _run(["git", "commit", "-m", "baseline"], repo)
    return repo


def test_target_selection_hypothesizer_preserves_fingerprint_ledger_semantics(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    selection = select_targets(repo, max_candidates=1)
    hypothesizer = TargetSelectionHypothesizer(
        selection,
        success_criterion="value returns 2",
        technique_tag="diff_proposal",
    )

    proposal = hypothesizer.propose(cycle_id="cycle-7", ast_diff_pattern="unified_diff")

    assert proposal.hypothesis.cycle_id == "cycle-7"
    assert proposal.hypothesis.target_files == [selection.candidates[0].path]
    assert proposal.hypothesis.fingerprint_id == proposal.fingerprint.id
    assert proposal.fingerprint.technique_tag == "diff_proposal"
    assert proposal.hypothesis.reasoning_blob_sha == selection.id
    assert proposal.hypothesis.intent == "Improve src/app.py: value returns 2"
    assert proposal.arm.target_files == ("src/app.py",)
