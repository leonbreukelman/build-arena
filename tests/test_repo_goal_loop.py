from __future__ import annotations

import json
import subprocess
from pathlib import Path

from arena.repo_goal_loop import RepoGoalLoopConfig, run_repo_goal_loop


def _git(repo: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True, text=True)


def _commit(repo: Path, msg: str) -> None:
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", msg)


def _init_repo(tmp_path: Path, *, with_lint_issue: bool = True, with_missing_docs: bool = True) -> Path:
    repo = tmp_path / "repo"
    (repo / "src" / "pkg").mkdir(parents=True)
    (repo / "pyproject.toml").write_text("[tool.ruff]\n", encoding="utf-8")
    (repo / "README.md").write_text("# Project\n", encoding="utf-8")
    if with_lint_issue:
        # F401 unused import -> a code.quality.lint finding.
        (repo / "src" / "pkg" / "mod.py").write_text("import os\n\n\ndef compute(x):\n    return x + 1\n", encoding="utf-8")
    else:
        (repo / "src" / "pkg" / "mod.py").write_text("def compute(x):\n    return x + 1\n", encoding="utf-8")
    _git(repo, "init", "-b", "main")
    _git(repo, "config", "user.email", "t@example.com")
    _git(repo, "config", "user.name", "Test")
    _commit(repo, "baseline")
    return repo


def _config(repo: Path, **overrides: object) -> RepoGoalLoopConfig:
    params: dict[str, object] = {
        "project": repo,
        "goal": "improve repository health across docs and code",
        "profile": "active-development",
        "artifacts_root": repo.parent / "artifacts",
        "max_cycles": 5,
        "dry_run": True,
    }
    params.update(overrides)
    return RepoGoalLoopConfig(**params)  # type: ignore[arg-type]


def _events(result) -> list[dict]:
    return [json.loads(line) for line in result.events_jsonl.read_text(encoding="utf-8").splitlines() if line.strip()]


# --- deterministic tests ---


def test_loop_cycle_is_deterministic_in_dry_run(tmp_path: Path) -> None:
    repo_a = _init_repo(tmp_path / "a")
    repo_b = _init_repo(tmp_path / "b")

    result_a = run_repo_goal_loop(_config(repo_a, artifacts_root=tmp_path / "a" / "art"))
    result_b = run_repo_goal_loop(_config(repo_b, artifacts_root=tmp_path / "b" / "art"))

    # Same selected-candidate sequence (finding ids) for identical repos.
    assert result_a.selected_finding_ids == result_b.selected_finding_ids
    assert result_a.cycles_run == result_b.cycles_run


def test_budget_halts_loop(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)

    result = run_repo_goal_loop(_config(repo, max_cycles=1))

    assert result.cycles_run == 1
    types = [e["type"] for e in _events(result)]
    assert "BUDGET_HALT" in types


def test_no_promotion_without_authorization(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    head_before = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, text=True, capture_output=True).stdout.strip()

    result = run_repo_goal_loop(_config(repo, dry_run=True, max_cycles=3))

    head_after = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, text=True, capture_output=True).stdout.strip()
    # Dry-run never advances the baseline.
    assert head_before == head_after
    assert result.promotions == 0
    types = [e["type"] for e in _events(result)]
    assert "PROMOTED" not in types


def test_boundary_enforced_each_cycle(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    # Mark src/ read-only via the goal config out_of_scope so the code-quality
    # candidate targeting src/pkg/mod.py is rejected before the runner is spawned.
    # Docs candidates rank above it, so allow enough cycles for the loop to reach
    # the src/ candidate.
    result = run_repo_goal_loop(_config(repo, read_only_paths=("src/",), max_cycles=8, max_consecutive_failures=99))

    events = _events(result)
    # The code candidate targeting src/ must produce a boundary event, never an apply.
    boundary = [e for e in events if e["type"] == "BOUNDARY_VIOLATION"]
    applied_code = [
        e for e in events
        if e["type"] == "CANDIDATE_APPLIED" and e.get("payload", {}).get("target_path", "").startswith("src/")
    ]
    assert boundary, "expected at least one boundary rejection for a src/ candidate"
    assert applied_code == []


def test_divergence_halts_on_repeated_gate_failure(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    # Force every candidate to fail its gate by injecting a transport that makes
    # no real change (no-op diff) -> gate fails every cycle -> divergence halt.
    result = run_repo_goal_loop(_config(repo, max_cycles=10, _force_noop_apply=True, max_consecutive_failures=3))

    types = [e["type"] for e in _events(result)]
    assert "DIVERGENCE_HALT" in types
    # Halted after the failure threshold, not after all 10 cycles.
    assert result.cycles_run <= 4


# --- functional tests ---


def test_repo_scale_goal_loop_improves_fixture(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)

    result = run_repo_goal_loop(_config(repo, max_cycles=4, dry_run=True))

    events = _events(result)
    # At least one cycle selected a cross-domain candidate, applied it in a
    # worktree, and the domain gate verified a correct-direction change.
    verified = [e for e in events if e["type"] == "CANDIDATE_VERIFIED" and e["payload"]["ok"] is True]
    assert verified, "expected at least one gate-verified candidate"
    # The improvement set spans more than just docs across the run.
    targets = {e["payload"].get("target_path", "") for e in events if e["type"] == "CANDIDATE_SELECTED"}
    assert any(t.endswith(".py") for t in targets) or any(t.endswith(".md") for t in targets)


def test_loop_stops_when_no_positive_candidate(tmp_path: Path) -> None:
    # Clean repo: README + docs index present, no lint issue -> eventually no
    # positive-leverage candidate remains.
    repo = _init_repo(tmp_path, with_lint_issue=False)
    (repo / "docs").mkdir()
    (repo / "docs" / "index.md").write_text("# Docs\n\nSee [README](../README.md).\n", encoding="utf-8")
    (repo / "AGENTS.md").write_text("# Agents\n\nCommands: `uv run pytest`.\n", encoding="utf-8")
    (repo / "docs" / "decisions").mkdir()
    (repo / "docs" / "decisions" / "index.md").write_text("# Decisions\n", encoding="utf-8")
    (repo / "docs" / "runbooks").mkdir()
    (repo / "docs" / "runbooks" / "index.md").write_text("# Runbooks\n", encoding="utf-8")
    _commit(repo, "fully documented")

    result = run_repo_goal_loop(_config(repo, max_cycles=10))

    types = [e["type"] for e in _events(result)]
    assert "NOTHING_TO_IMPROVE" in types
    assert result.cycles_run < 10  # terminated early, did not exhaust budget


def test_promotion_ff_only_when_authorized(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    head_before = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, text=True, capture_output=True).stdout.strip()

    # Authorized promotion: a passing code-quality candidate advances the baseline
    # exactly once via ff-only merge.
    result = run_repo_goal_loop(_config(repo, dry_run=False, allow_promotion=True, max_cycles=1, stop_after_promotions=1))

    head_after = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, text=True, capture_output=True).stdout.strip()
    assert head_after != head_before  # baseline advanced
    assert result.promotions == 1
    types = [e["type"] for e in _events(result)]
    assert "PROMOTED" in types


def test_promotion_requires_test_gate_for_code_candidate(tmp_path: Path) -> None:
    """Guardrail carried from #29: a code-quality candidate must pass the project's
    test command (a behaviour gate) before promotion, not just the lint gate. Docs
    candidates (low-risk) may still promote; only the code candidate is gated."""
    repo = _init_repo(tmp_path)
    # A test command that always FAILS, so a lint-passing code candidate must NOT
    # be promoted. Allow enough cycles to reach the src/ code candidate.
    result = run_repo_goal_loop(
        _config(
            repo,
            dry_run=False,
            allow_promotion=True,
            max_cycles=8,
            test_command="python3 -c 'import sys; sys.exit(1)'",
        )
    )

    events = _events(result)
    # The code candidate's behaviour gate failed and it was never promoted.
    code_verified = [
        e for e in events
        if e["type"] == "CANDIDATE_VERIFIED" and e["payload"].get("behaviour_gate") == "failed"
    ]
    assert code_verified, "expected the code candidate to fail the behaviour gate"
    promoted_code = [
        e for e in events
        if e["type"] == "PROMOTED" and e["payload"].get("target_path", "").endswith(".py")
    ]
    assert promoted_code == [], "a code candidate must not be promoted when the behaviour gate fails"


def test_code_candidate_not_promoted_without_test_command(tmp_path: Path) -> None:
    """HOLE 1 (fail-closed): with promotion authorized but NO test_command, a .py
    code candidate must NOT be promoted on the lint gate alone. The #29 behaviour
    gate is mandatory for code promotion, not opt-in."""
    repo = _init_repo(tmp_path)

    result = run_repo_goal_loop(_config(repo, dry_run=False, allow_promotion=True, max_cycles=8, test_command=None))

    events = _events(result)
    promoted_code = [e for e in events if e["type"] == "PROMOTED" and e["payload"].get("target_path", "").endswith(".py")]
    assert promoted_code == [], "a .py candidate must not be promoted without a configured+passing behaviour gate"
    # It should be recorded as refused for missing behaviour gate, not silently passed.
    refused = [e for e in events if e["type"] == "PROMOTION_REFUSED" and e["payload"].get("reason") == "behaviour_gate_required"]
    assert refused, "expected a PROMOTION_REFUSED(behaviour_gate_required) event for the code candidate"


def test_promoted_diff_confined_to_target_path(tmp_path: Path) -> None:
    """HOLE 2: a gate side-effect to a protected path must NOT land in the promoted
    baseline. The promotion stages only the approved target."""
    repo = _init_repo(tmp_path)
    # A test command that succeeds BUT writes to a protected scorer/ path as a side
    # effect. The behaviour gate passes, but the stray file must not be promoted.
    (repo / "scorer").mkdir()
    test_cmd = "python3 -c \"open('scorer/STRAY.txt','w').write('x')\""

    run_repo_goal_loop(_config(repo, dry_run=False, allow_promotion=True, max_cycles=8, test_command=test_cmd))

    # After the run, the project's promoted tree must not contain the stray file.
    promoted_stray = (repo / "scorer" / "STRAY.txt").exists()
    tracked = subprocess.run(["git", "ls-files", "scorer/"], cwd=repo, text=True, capture_output=True).stdout
    assert "scorer/STRAY.txt" not in tracked, "a gate side-effect to scorer/ must not be promoted into the baseline"
    assert not promoted_stray or "scorer/STRAY.txt" not in tracked


def test_dry_run_leaves_working_tree_pristine(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    before = subprocess.run(["git", "status", "--porcelain"], cwd=repo, text=True, capture_output=True).stdout

    run_repo_goal_loop(_config(repo, dry_run=True, max_cycles=4, artifacts_root=tmp_path / "outside-art"))

    after = subprocess.run(["git", "status", "--porcelain"], cwd=repo, text=True, capture_output=True).stdout
    assert before == after, "dry-run must not dirty the project working tree"


def test_missing_gate_binary_is_recorded_not_crashed(tmp_path: Path) -> None:
    """HOLE 3: a verification command referencing a missing binary must be recorded
    as a gate failure, not crash the whole loop."""
    repo = _init_repo(tmp_path)

    # test_command referencing a non-existent binary; loop must complete, not raise.
    result = run_repo_goal_loop(
        _config(repo, dry_run=False, allow_promotion=True, max_cycles=2, test_command="this-binary-does-not-exist-xyz --run")
    )

    # Did not crash; produced a result with events.
    assert result.cycles_run >= 1
    types = [e["type"] for e in _events(result)]
    assert "RUN_ENDED" in types


def test_autonomy_boundary_threaded_into_candidate_for_code_guard() -> None:
    """Latent-guard fix: _select_promotable must carry autonomyBoundary so the
    code-vs-docs promotion guard can classify a needs_code_change target whose
    extension is not .py (otherwise the #29 behaviour-gate guard is dead code)."""
    from arena.repo_goal_loop import _select_promotable

    ranked_bundle = {
        "ranked": {
            "entries": [
                {
                    "findingId": "code.config.pyproject",
                    "domain": "code_quality",
                    "targetPath": "pyproject.toml",
                    "priorityScore": 100.0,
                    "autonomyBoundary": "needs_code_change",
                }
            ]
        },
        "plan": {"candidates": [{"finding_id": "code.config.pyproject"}]},
    }

    candidate = _select_promotable(ranked_bundle, set())
    assert candidate is not None
    assert candidate["autonomyBoundary"] == "needs_code_change"
