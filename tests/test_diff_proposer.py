from __future__ import annotations

import asyncio
import json
import subprocess
from pathlib import Path
from typing import Any

import pytest

from arena.generated.models import Hypothesis, RunnerName
from arena.router import RunnerRouter
from arena.runners.base import RunnerError
from arena.runners.diff_proposer import DiffProposalResponse, DiffProposerRunner


def _run(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=cwd, check=True, capture_output=True, text=True)


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _repo(tmp_path: Path, *, max_lines: int = 6) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    _write(repo / "src" / "app.py", "def value() -> int:\n    return 1\n")
    _write(repo / "private" / "secret.py", "SECRET='***'\n")
    _write(
        repo / ".arena" / "goal.toml",
        f"""
schema_version = "goal-config/v1"
project_id = "diff-proposer-fixture"

[commands]
test = ["python3", "-c", "pass"]
lint = ["python3", "-c", "pass"]
typecheck = ["python3", "-c", "pass"]

[coverage]
source = "coverage.json"
floor = 0.0

[paths]
source_roots = ["src", "private"]
out_of_scope = []
read_only = ["private"]

[diff_caps]
max_files = 1
max_lines = {max_lines}
""".strip()
        + "\n",
    )
    _run(["git", "init", "-b", "main"], repo)
    _run(["git", "config", "user.email", "arena@example.invalid"], repo)
    _run(["git", "config", "user.name", "Arena Tests"], repo)
    _run(["git", "add", "."], repo)
    _run(["git", "commit", "-m", "baseline"], repo)
    return repo


def _hypothesis(*, target_files: list[str] | None = None) -> Hypothesis:
    return Hypothesis(
        id="hyp-diff-1",
        cycle_id="cycle-1",
        intent="Return the safer value",
        technique_tag="diff_proposal",
        target_cluster="src/app.py",
        target_files=target_files or ["src/app.py"],
        fingerprint_id="f" * 32,
        proposed_ts=1.0,
    )


def _valid_diff(path: str = "src/app.py", *, new_value: int = 2) -> str:
    return f"""diff --git a/{path} b/{path}
--- a/{path}
+++ b/{path}
@@ -1,2 +1,2 @@
 def value() -> int:
-    return 1
+    return {new_value}
"""


class FakeTransport:
    def __init__(self, response: DiffProposalResponse) -> None:
        self.response = response
        self.requests: list[Any] = []

    def propose(self, request: Any) -> DiffProposalResponse:
        self.requests.append(request)
        return self.response


def test_diff_proposer_applies_valid_fake_diff_after_patch_gate(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    transport = FakeTransport(
        DiffProposalResponse(
            diff_text=_valid_diff(),
            intent="Change value to two",
            provenance={"transport": "fake"},
        )
    )
    runner = DiffProposerRunner(transport=transport, success_criterion="value returns 2")

    patch_path = asyncio.run(runner.apply(_hypothesis(), repo))

    assert runner.name == RunnerName.codex
    assert patch_path.exists()
    assert patch_path.read_text(encoding="utf-8") == _valid_diff()
    assert (repo / "src" / "app.py").read_text(encoding="utf-8") == "def value() -> int:\n    return 2\n"
    provenance = json.loads(patch_path.with_suffix(".patch.provenance.json").read_text(encoding="utf-8"))
    assert provenance["hypothesis_id"] == "hyp-diff-1"
    assert provenance["target_path"] == "src/app.py"
    assert provenance["intent"] == "Change value to two"
    assert provenance["transport"] == "fake"
    assert transport.requests[0].target_path == "src/app.py"
    assert transport.requests[0].file_contents == "def value() -> int:\n    return 1\n"
    assert transport.requests[0].success_criterion == "value returns 2"


@pytest.mark.parametrize(
    "response",
    [
        DiffProposalResponse(diff_text="", intent="empty"),
        DiffProposalResponse(diff_text="Please change the file.", intent="prose"),
        DiffProposalResponse(diff_text=_valid_diff("private/secret.py"), intent="boundary"),
        DiffProposalResponse(diff_text=_valid_diff(), intent="oversized"),
        DiffProposalResponse(diff_text=_valid_diff(), intent="truncated", truncated=True),
        DiffProposalResponse(diff_text=_valid_diff(), intent="cancelled", cancelled=True),
    ],
)
def test_diff_proposer_rejects_invalid_fake_outputs_without_mutation(
    tmp_path: Path,
    response: DiffProposalResponse,
) -> None:
    repo = _repo(tmp_path, max_lines=1)
    before = (repo / "src" / "app.py").read_text(encoding="utf-8")
    runner = DiffProposerRunner(transport=FakeTransport(response), success_criterion="value returns 2")

    with pytest.raises(RunnerError):
        asyncio.run(runner.apply(_hypothesis(target_files=["src/app.py"]), repo))

    assert (repo / "src" / "app.py").read_text(encoding="utf-8") == before
    assert not (repo / ".arena" / "patches").exists()
    assert subprocess.check_output(["git", "status", "--short"], cwd=repo, text=True) == ""


def test_diff_proposer_runner_router_integration(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    runner = DiffProposerRunner(
        transport=FakeTransport(DiffProposalResponse(diff_text=_valid_diff(), intent="Change value")),
        success_criterion="value returns 2",
    )
    router = RunnerRouter(primary=runner, fallback=runner)

    result = asyncio.run(router.apply(_hypothesis(), repo))

    assert result.success is True
    assert result.error_reason is None
    assert result.runner_used == RunnerName.codex
    assert result.patch_path is not None
    assert result.patch_path.exists()


def test_diff_proposer_rejects_multi_target_hypotheses(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    runner = DiffProposerRunner(
        transport=FakeTransport(DiffProposalResponse(diff_text=_valid_diff(), intent="Change value")),
        success_criterion="value returns 2",
    )

    with pytest.raises(RunnerError, match="exactly one target"):
        asyncio.run(runner.apply(_hypothesis(target_files=["src/app.py", "src/other.py"]), repo))

    assert subprocess.check_output(["git", "status", "--short"], cwd=repo, text=True) == ""
