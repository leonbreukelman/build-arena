from __future__ import annotations

import json
import subprocess
from pathlib import Path

from arena.target_picker import select_targets


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _run(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=cwd, check=True, capture_output=True, text=True)


def _init_repo(repo: Path) -> None:
    _run(["git", "init", "-b", "main"], repo)
    _run(["git", "config", "user.email", "arena@example.invalid"], repo)
    _run(["git", "config", "user.name", "Arena Tests"], repo)
    _run(["git", "add", "."], repo)
    _run(["git", "commit", "-m", "baseline"], repo)


def _target_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "target-repo"
    repo.mkdir()
    _write(
        repo / "src" / "hot.py",
        """
def risky(value: int) -> int:
    # TODO: split this branchy function.
    # FIXME: cover negative values.
    total = 0
    if value > 10:
        total += value
    elif value > 5:
        total += value // 2
    for item in range(value):
        if item % 2:
            total += item
    return total
""".lstrip(),
    )
    _write(
        repo / "plugins" / "api.py",
        """
def handle(flag: bool) -> str:
    # TODO: add unhappy-path checks.
    if flag:
        return "yes"
    return "no"
""".lstrip(),
    )
    _write(repo / "src" / "tie_a.py", "def alpha() -> str:\n    return 'alpha'\n")
    _write(repo / "src" / "tie_b.py", "def beta() -> str:\n    return 'beta'\n")
    _write(repo / "src" / "generated" / "skip.py", "# TODO: generated debt should be ignored\n")
    _write(repo / "private" / "secret.py", "# TODO: private debt should be ignored\n")
    _write(
        repo / ".arena" / "goal.toml",
        """
schema_version = "goal-config/v1"
project_id = "target-picker-fixture"
goal = "Rank deterministic target candidates."

[commands]
test = ["python3", "-c", "pass"]
lint = ["python3", "-c", "pass"]
typecheck = ["python3", "-c", "pass"]

[coverage]
source = "reports/coverage.json"
floor = 80.0

[paths]
source_roots = ["src", "plugins", "private"]
out_of_scope = ["src/generated", "reports"]
read_only = ["private"]
""".strip()
        + "\n",
    )
    _write(
        repo / "reports" / "coverage.json",
        json.dumps(
            {
                "files": {
                    "src/hot.py": {"summary": {"percent_covered": 45.0}},
                    "plugins/api.py": {"summary": {"percent_covered": 82.0}},
                    "src/tie_a.py": {"summary": {"percent_covered": 100.0}},
                    "src/tie_b.py": {"summary": {"percent_covered": 100.0}},
                    "src/generated/skip.py": {"summary": {"percent_covered": 0.0}},
                    "private/secret.py": {"summary": {"percent_covered": 0.0}},
                },
                "totals": {"percent_covered": 81.0},
            },
            sort_keys=True,
        ),
    )
    _write(
        repo / "reports" / "ruff.json",
        json.dumps(
            [
                {"filename": str(repo / "src" / "hot.py"), "code": "C901"},
                {"filename": "src/hot.py", "code": "E501"},
                {"filename": "src/hot.py", "code": "PLR0912"},
                {"filename": "plugins/api.py", "code": "SIM108"},
                {"filename": "src/generated/skip.py", "code": "E501"},
                {"filename": "private/secret.py", "code": "S105"},
            ],
            sort_keys=True,
        ),
    )
    _init_repo(repo)
    _write(
        repo / "src" / "hot.py",
        (repo / "src" / "hot.py").read_text(encoding="utf-8") + "\n# TODO: second churn marker\n",
    )
    _run(["git", "add", "src/hot.py"], repo)
    _run(["git", "commit", "-m", "touch hot path"], repo)
    return repo


def test_select_targets_ranks_candidates_stably_with_raw_signal_values(tmp_path: Path) -> None:
    repo = _target_repo(tmp_path)

    first = select_targets(repo, max_candidates=4, lint_path=Path("reports/ruff.json"))
    second = select_targets(repo, max_candidates=4, lint_path=Path("reports/ruff.json"))

    assert first.to_jsonable() == second.to_jsonable()
    assert first.goal_config_sha
    assert first.git_oid
    assert first.id.startswith("target-selection-")
    assert [candidate.path for candidate in first.candidates] == [
        "src/hot.py",
        "plugins/api.py",
        "src/tie_a.py",
        "src/tie_b.py",
    ]

    hot = first.candidates[0]
    assert hot.rank == 1
    assert hot.signals.coverage_gap == 55.0
    assert hot.signals.lint_violations == 3
    assert hot.signals.git_churn == 2
    assert hot.signals.todo_count == 3
    assert hot.signals.complexity > first.candidates[1].signals.complexity
    assert hot.score > first.candidates[1].score
    assert hot.to_jsonable()["signals"]["coverage_gap"] == 55.0


def test_select_targets_excludes_goal_config_and_default_boundary_paths(tmp_path: Path) -> None:
    repo = _target_repo(tmp_path)

    selection = select_targets(repo, max_candidates=10, lint_path=Path("reports/ruff.json"))

    paths = [candidate.path for candidate in selection.candidates]
    assert "src/generated/skip.py" not in paths
    assert "private/secret.py" not in paths
    assert "scorer/engine.py" not in paths
    assert all(not path.startswith("reports/") for path in paths)


def test_select_targets_uses_path_tiebreakers_and_limit(tmp_path: Path) -> None:
    repo = _target_repo(tmp_path)

    selection = select_targets(repo, max_candidates=3, lint_path=Path("reports/ruff.json"))

    assert [candidate.path for candidate in selection.candidates] == [
        "src/hot.py",
        "plugins/api.py",
        "src/tie_a.py",
    ]
    assert selection.candidate_count == 4
    assert selection.omitted_count == 1


def test_select_targets_handles_missing_optional_signal_files(tmp_path: Path) -> None:
    repo = _target_repo(tmp_path)
    (repo / "reports" / "coverage.json").unlink()
    (repo / "reports" / "ruff.json").unlink()

    selection = select_targets(repo, max_candidates=1, lint_path=Path("reports/ruff.json"))

    assert selection.candidates[0].signals.coverage_gap == 0.0
    assert selection.candidates[0].signals.lint_violations == 0


def test_target_picker_has_no_llm_provider_imports(project_root: Path) -> None:
    source = (project_root / "arena" / "target_picker.py").read_text(encoding="utf-8")

    forbidden = ["openai", "anthropic", "claude", "litellm", "xai", "llm"]
    lowered = source.lower()
    assert [name for name in forbidden if name in lowered] == []
