from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

import pytest

from arena.project_graph import build_project_graph
from arena.project_model_llm import build_fixture_model_output
from arena.repo_goal_loop import RepoGoalLoopConfig, _EventLog, run_repo_goal_loop
from arena.runners.base import RunnerError
from arena.runners.diff_proposer import DiffProposalResponse


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


def _write_goal_config(repo: Path) -> None:
    (repo / ".arena").mkdir(exist_ok=True)
    (repo / ".arena" / "goal.toml").write_text(
        """
schema_version = "goal-config/v1"
project_id = "test-repo"
goal = "Improve repository health with bounded single-file diffs."

[commands]
test = ["python3", "-c", "pass"]
lint = ["python3", "-c", "pass"]
typecheck = ["python3", "-c", "pass"]

[coverage]
source = "src"
floor = 0

[paths]
source_roots = ["src", "tests", "docs"]
out_of_scope = [".env", ".venv", ".arena/patches"]
read_only = []

[diff_caps]
max_files = 1
max_lines = 80
""".lstrip(),
        encoding="utf-8",
    )


def _document_repo(repo: Path) -> None:
    (repo / "docs" / "decisions").mkdir(parents=True, exist_ok=True)
    (repo / "docs" / "runbooks").mkdir(parents=True, exist_ok=True)
    (repo / "docs" / "index.md").write_text("# Docs\n\nSee [README](../README.md).\n", encoding="utf-8")
    (repo / "AGENTS.md").write_text("# Agents\n\nSee [README](README.md).\n", encoding="utf-8")
    (repo / "docs" / "decisions" / "index.md").write_text("# Decisions\n", encoding="utf-8")
    (repo / "docs" / "runbooks" / "index.md").write_text("# Runbooks\n", encoding="utf-8")


class _FixtureLiveLLM:
    def __init__(self, repo: Path, *, strip_observable_checks: bool = False, hostile_allowlist: bool = False) -> None:
        self.repo = repo
        self.strip_observable_checks = strip_observable_checks
        self.hostile_allowlist = hostile_allowlist
        self.calls = 0

    def generate(self, _prompt: str) -> dict[str, Any]:
        self.calls += 1
        graph = build_project_graph(self.repo)
        raw = build_fixture_model_output(
            graph,
            project_id=f"repo-goal-{self.repo.name}",
            goal="improve repository health across docs and code",
            non_goals=["do not treat file buckets as final components"],
        )
        raw["model_id"] = "test-live-decomposer"
        if self.strip_observable_checks:
            raw["observable_checks"] = []
        if self.hostile_allowlist:
            raw["acceptance_command_allowlist"] = ["python3 -c 'raise SystemExit(99)'"]
        return raw


class _StaticDiffTransport:
    def __init__(self, diff_text: str | list[str], *, raise_error: bool = False) -> None:
        self.diff_text = diff_text
        self.raise_error = raise_error
        self.calls = 0
        self.requests: list[Any] = []

    def propose(self, request: Any) -> DiffProposalResponse:
        self.calls += 1
        self.requests.append(request)
        if self.raise_error:
            raise RunnerError("provider failed: token=[REDACTED]")
        diff_text = self.diff_text[self.calls - 1] if isinstance(self.diff_text, list) else self.diff_text
        return DiffProposalResponse(
            diff_text=diff_text,
            intent=request.intent,
            provenance={"transport": "test_static", "model": "test-live-proposer"},
        )


def _remove_unused_import_diff() -> str:
    return """diff --git a/src/pkg/mod.py b/src/pkg/mod.py
--- a/src/pkg/mod.py
+++ b/src/pkg/mod.py
@@ -1,5 +1,2 @@
-import os
-
-
 def compute(x):
     return x + 1
"""


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


# --- live loop wiring / fail-closed tests ---


def test_live_modes_require_allow_live_before_any_cycle(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)

    with pytest.raises(ValueError, match="allow_live"):
        run_repo_goal_loop(_config(repo, decompose_mode="live", live_model="test-live-model"))

    with pytest.raises(ValueError, match="allow_live"):
        run_repo_goal_loop(_config(repo, apply_mode="live_diff", live_model="test-live-model"))


def test_live_modes_require_explicit_model_before_any_cycle(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)

    with pytest.raises(ValueError, match="explicit live_model"):
        run_repo_goal_loop(_config(repo, decompose_mode="live", allow_live=True))

    with pytest.raises(ValueError, match="explicit live_model"):
        run_repo_goal_loop(_config(repo, apply_mode="live_diff", allow_live=True))


def test_live_flags_require_a_live_mode_before_any_cycle(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)

    with pytest.raises(ValueError, match="live flags require"):
        run_repo_goal_loop(
            _config(repo, allow_live=True, live_model="test-live-model", live_api_key_env="TEST_KEY", live_max_calls=1)
        )


def test_live_diff_requires_goal_config_before_any_cycle(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)

    with pytest.raises(ValueError, match="goal config"):
        run_repo_goal_loop(_config(repo, apply_mode="live_diff", allow_live=True, live_model="test-live-model", live_max_calls=10))


def test_live_diff_requires_goal_config_tracked_in_head_before_any_cycle(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    _write_goal_config(repo)

    with pytest.raises(ValueError, match="tracked in git HEAD"):
        run_repo_goal_loop(_config(repo, apply_mode="live_diff", allow_live=True, live_model="test-live-model", live_max_calls=10))


def test_live_modes_require_explicit_live_call_budget_before_any_cycle(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)

    with pytest.raises(ValueError, match="live_max_calls"):
        run_repo_goal_loop(_config(repo, decompose_mode="live", allow_live=True, live_model="test-live-model"))


def test_live_call_budget_estimates_single_and_dual_live_modes(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    from arena.repo_goal_loop import _planned_live_calls

    assert _planned_live_calls(_config(repo, decompose_mode="live", max_cycles=2)) == 2
    assert _planned_live_calls(_config(repo, apply_mode="live_diff", max_cycles=2)) == 4
    assert _planned_live_calls(_config(repo, decompose_mode="live", apply_mode="live_diff", max_cycles=2)) == 6
    assert _planned_live_calls(_config(repo, decompose_mode="live", run_adversarial_probes=True, max_cycles=2)) == 4
    assert _planned_live_calls(
        _config(repo, decompose_mode="live", apply_mode="live_diff", run_adversarial_probes=True, max_cycles=1)
    ) == 4


def test_live_call_budget_rejects_non_positive_cap(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)

    with pytest.raises(ValueError, match="live_max_calls"):
        run_repo_goal_loop(_config(repo, decompose_mode="live", allow_live=True, live_model="test-live-model", live_max_calls=0))


def test_live_call_budget_cap_fails_before_adapter_calls(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    llm = _FixtureLiveLLM(repo)

    with pytest.raises(ValueError, match="planned live calls"):
        run_repo_goal_loop(
            _config(
                repo,
                decompose_mode="live",
                apply_mode="live_diff",
                allow_live=True,
                live_model="test-live-model",
                live_max_calls=3,
                max_cycles=2,
                _decompose_llm=llm,
            )
        )

    assert llm.calls == 0


def test_live_call_budget_cap_counts_adversarial_probe_slot_before_adapter_calls(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    llm = _FixtureLiveLLM(repo)

    with pytest.raises(ValueError, match="planned live calls"):
        run_repo_goal_loop(
            _config(
                repo,
                decompose_mode="live",
                allow_live=True,
                live_model="test-live-model",
                live_max_calls=1,
                run_adversarial_probes=True,
                max_cycles=1,
                _decompose_llm=llm,
            )
        )

    assert llm.calls == 0


def test_live_decomposition_gate_failure_fails_closed(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    llm = _FixtureLiveLLM(repo, strip_observable_checks=True)

    result = run_repo_goal_loop(
        _config(
            repo,
            decompose_mode="live",
            allow_live=True,
            live_model="test-live-model",
            live_max_calls=10,
            _decompose_llm=llm,
            max_cycles=3,
            max_consecutive_failures=1,
        )
    )

    events = _events(result)
    assert llm.calls == 1
    assert "DECOMPOSITION_GATE_FAILED" in [event["type"] for event in events]
    assert "CANDIDATE_SELECTED" not in [event["type"] for event in events]
    assert "CANDIDATE_APPLIED" not in [event["type"] for event in events]
    assert result.promotions == 0
    assert result.halted_reason == "divergence"


def test_live_decomposition_uses_injected_adapter_and_records_provenance(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    llm = _FixtureLiveLLM(repo)

    result = run_repo_goal_loop(
        _config(
            repo,
            decompose_mode="live",
            allow_live=True,
            live_model="test-live-model",
            live_max_calls=10,
            _decompose_llm=llm,
            max_cycles=1,
        )
    )

    events = _events(result)
    completed = [event for event in events if event["type"] == "DECOMPOSITION_COMPLETED"]
    assert llm.calls == 1
    assert completed
    assert completed[0]["payload"]["mode"] == "live"
    assert completed[0]["payload"]["model_id"] == "test-live-decomposer"
    assert completed[0]["payload"]["decomposer_hash"]
    assert "CANDIDATE_SELECTED" in [event["type"] for event in events]


def test_live_diff_apply_runs_patch_gate_and_changes_file(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    _document_repo(repo)
    _write_goal_config(repo)
    _commit(repo, "docs and goal config")
    transport = _StaticDiffTransport(_remove_unused_import_diff())

    result = run_repo_goal_loop(
        _config(
            repo,
            apply_mode="live_diff",
            allow_live=True,
            live_model="test-live-model",
            live_max_calls=10,
            _diff_transport=transport,
            max_cycles=1,
        )
    )

    events = _events(result)
    assert transport.calls == 1
    applied = [event for event in events if event["type"] == "CANDIDATE_APPLIED" and event["payload"].get("apply_mode") == "live_diff"]
    assert applied
    assert Path(applied[0]["payload"]["patch_path"]).is_file()
    assert Path(applied[0]["payload"]["provenance_path"]).is_file()
    verified = [event for event in events if event["type"] == "CANDIDATE_VERIFIED" and event["payload"].get("ok") is True]
    assert verified


def test_live_diff_rejected_by_patch_gate_is_apply_failure_not_crash(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    _document_repo(repo)
    _write_goal_config(repo)
    _commit(repo, "docs and goal config")
    invalid_diff = _remove_unused_import_diff() + """diff --git a/README.md b/README.md
--- a/README.md
+++ b/README.md
@@ -1 +1,2 @@
 # Project
+extra
"""
    transport = _StaticDiffTransport(invalid_diff)

    result = run_repo_goal_loop(
        _config(
            repo,
            apply_mode="live_diff",
            allow_live=True,
            live_model="test-live-model",
            live_max_calls=10,
            _diff_transport=transport,
            max_cycles=3,
            max_consecutive_failures=1,
        )
    )

    events = _events(result)
    assert transport.calls == 2
    assert "CANDIDATE_APPLY_FAILED" in [event["type"] for event in events]
    assert "RUN_ENDED" in [event["type"] for event in events]
    assert result.promotions == 0
    assert result.halted_reason == "divergence"


def test_live_diff_provider_error_is_failure_not_crash(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    _document_repo(repo)
    _write_goal_config(repo)
    _commit(repo, "docs and goal config")
    transport = _StaticDiffTransport("", raise_error=True)

    result = run_repo_goal_loop(
        _config(
            repo,
            apply_mode="live_diff",
            allow_live=True,
            live_model="test-live-model",
            live_max_calls=10,
            _diff_transport=transport,
            max_cycles=2,
            max_consecutive_failures=1,
        )
    )

    events = _events(result)
    failures = [event for event in events if event["type"] == "CANDIDATE_APPLY_FAILED"]
    assert failures
    assert "token=[REDACTED]" in failures[0]["payload"]["error"]
    assert result.halted_reason == "divergence"


def test_live_diff_code_promotion_still_requires_behaviour_gate(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    _document_repo(repo)
    _write_goal_config(repo)
    _commit(repo, "docs and goal config")
    transport = _StaticDiffTransport(_remove_unused_import_diff())

    result = run_repo_goal_loop(
        _config(
            repo,
            apply_mode="live_diff",
            allow_live=True,
            live_model="test-live-model",
            live_max_calls=10,
            _diff_transport=transport,
            dry_run=False,
            allow_promotion=True,
            max_cycles=1,
            test_command=None,
        )
    )

    events = _events(result)
    assert transport.calls == 1
    promoted_code = [event for event in events if event["type"] == "PROMOTED" and event["payload"].get("target_path", "").endswith(".py")]
    assert promoted_code == []
    refused = [event for event in events if event["type"] == "PROMOTION_REFUSED" and event["payload"].get("reason") == "behaviour_gate_required"]
    assert refused


def test_live_diff_promotion_stages_only_target_path(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    _document_repo(repo)
    _write_goal_config(repo)
    _commit(repo, "docs and goal config")
    transport = _StaticDiffTransport(_remove_unused_import_diff())

    run_repo_goal_loop(
        _config(
            repo,
            apply_mode="live_diff",
            allow_live=True,
            live_model="test-live-model",
            live_max_calls=10,
            _diff_transport=transport,
            dry_run=False,
            allow_promotion=True,
            max_cycles=1,
            stop_after_promotions=1,
            test_command="python3 -c 'pass'",
        )
    )

    committed_paths = subprocess.run(["git", "show", "--name-only", "--format="], cwd=repo, text=True, capture_output=True).stdout.splitlines()
    assert committed_paths == ["src/pkg/mod.py"]
    assert ".arena/patches" not in subprocess.run(["git", "ls-files", ".arena/patches"], cwd=repo, text=True, capture_output=True).stdout


def test_loop_verification_commands_are_deterministic_not_model_controlled(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    _document_repo(repo)
    _write_goal_config(repo)
    _commit(repo, "docs and goal config")
    llm = _FixtureLiveLLM(repo, hostile_allowlist=True)
    transport = _StaticDiffTransport(_remove_unused_import_diff())

    result = run_repo_goal_loop(
        _config(
            repo,
            decompose_mode="live",
            apply_mode="live_diff",
            allow_live=True,
            live_model="test-live-model",
            live_max_calls=10,
            _decompose_llm=llm,
            _diff_transport=transport,
            max_cycles=1,
        )
    )

    events = _events(result)
    verified = [event for event in events if event["type"] == "CANDIDATE_VERIFIED"]
    assert verified
    commands = [item["command"] for item in verified[0]["payload"]["commands"]]
    assert commands == ["python3 -m arena.code_quality_gate --repo . --path src/pkg/mod.py"]
    assert all("SystemExit(99)" not in command for command in commands)


def test_run_started_records_live_call_budget(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    _document_repo(repo)
    _write_goal_config(repo)
    _commit(repo, "docs and goal config")
    llm = _FixtureLiveLLM(repo)
    transport = _StaticDiffTransport(_remove_unused_import_diff())

    result = run_repo_goal_loop(
        _config(
            repo,
            decompose_mode="live",
            apply_mode="live_diff",
            allow_live=True,
            live_model="test-live-model",
            live_max_calls=3,
            _decompose_llm=llm,
            _diff_transport=transport,
            max_cycles=1,
        )
    )

    started = _events(result)[0]
    assert started["type"] == "RUN_STARTED"
    assert started["payload"]["liveMaxCalls"] == 3
    assert started["payload"]["plannedLiveCalls"] == 3
    assert started["payload"]["liveRepairBudgetPerCycle"] == 1


def test_deterministic_docs_generation_includes_source_references(tmp_path: Path) -> None:
    from arena.markdown_links import has_source_references
    from arena.repo_goal_loop import _generate_doc

    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "README.md").write_text("# Readme\n", encoding="utf-8")

    assert _generate_doc(repo, "docs/index.md") is True
    generated = repo / "docs" / "index.md"
    assert "## Source references" in generated.read_text(encoding="utf-8")
    assert has_source_references(repo, generated) is True


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
        "plan": {"candidates": [{"finding_id": "code.config.pyproject", "verification_commands": ["python3 -c pass"]}]},
    }

    candidate = _select_promotable(ranked_bundle, set())
    assert candidate is not None
    assert candidate["autonomyBoundary"] == "needs_code_change"


def test_select_promotable_skips_unverified_candidates() -> None:
    """A ranked candidate with no deterministic verification command is not
    executable/promotable. The loop should not spend a live diff call on it."""
    from arena.repo_goal_loop import _select_promotable

    ranked_bundle = {
        "ranked": {
            "entries": [
                {
                    "findingId": "code.component.untested.comp-tools",
                    "domain": "generic_file",
                    "targetPath": "src/fmc_mcp/tools.py",
                    "priorityScore": 540.0,
                    "autonomyBoundary": "needs_code_change",
                },
                {
                    "findingId": "agent.agents-md.missing",
                    "domain": "documentation",
                    "targetPath": "AGENTS.md",
                    "priorityScore": 432.0,
                    "autonomyBoundary": "safe_to_patch_docs_only",
                },
            ]
        },
        "plan": {
            "candidates": [
                {"finding_id": "code.component.untested.comp-tools", "verification_commands": []},
                {"finding_id": "agent.agents-md.missing", "verification_commands": ["test -s AGENTS.md"]},
            ]
        },
    }

    candidate = _select_promotable(ranked_bundle, set())
    assert candidate is not None
    assert candidate["findingId"] == "agent.agents-md.missing"


def test_select_promotable_emits_candidate_skipped_for_empty_verification(tmp_path: Path) -> None:
    from arena.repo_goal_loop import _select_promotable

    log = _EventLog(tmp_path / "events.jsonl")
    ranked_bundle = {
        "ranked": {
            "entries": [
                {
                    "findingId": "code.component.untested.comp-tools",
                    "domain": "component_verification",
                    "targetPath": "src/fmc_mcp/tools.py",
                    "priorityScore": 540.0,
                    "autonomyBoundary": "needs_code_change",
                },
                {
                    "findingId": "agent.agents-md.missing",
                    "domain": "documentation",
                    "targetPath": "AGENTS.md",
                    "priorityScore": 432.0,
                    "autonomyBoundary": "safe_to_patch_docs_only",
                },
            ]
        },
        "plan": {
            "candidates": [
                {"finding_id": "code.component.untested.comp-tools", "verification_commands": []},
                {"finding_id": "agent.agents-md.missing", "verification_commands": ["test -s AGENTS.md"]},
            ]
        },
    }

    candidate = _select_promotable(ranked_bundle, set(), log=log, cycle=7)

    assert candidate is not None
    events = [json.loads(line) for line in (tmp_path / "events.jsonl").read_text(encoding="utf-8").splitlines()]
    assert [event["type"] for event in events] == ["CANDIDATE_SKIPPED"]
    assert events[0]["cycle"] == 7
    assert events[0]["payload"]["finding_id"] == "code.component.untested.comp-tools"
    assert events[0]["payload"]["reason"] == "empty_verification"


def test_select_promotable_skips_emit_for_already_tried(tmp_path: Path) -> None:
    from arena.repo_goal_loop import _select_promotable

    log = _EventLog(tmp_path / "events.jsonl")
    ranked_bundle = {
        "ranked": {
            "entries": [
                {"findingId": "docs.done", "domain": "documentation", "targetPath": "docs/index.md", "priorityScore": 10.0},
                {"findingId": "docs.next", "domain": "documentation", "targetPath": "AGENTS.md", "priorityScore": 9.0},
            ]
        },
        "plan": {
            "candidates": [
                {"finding_id": "docs.done", "verification_commands": ["test -s docs/index.md"]},
                {"finding_id": "docs.next", "verification_commands": ["test -s AGENTS.md"]},
            ]
        },
    }

    candidate = _select_promotable(ranked_bundle, {"docs.done"}, log=log, cycle=3)

    assert candidate is not None
    assert candidate["findingId"] == "docs.next"
    events = [json.loads(line) for line in (tmp_path / "events.jsonl").read_text(encoding="utf-8").splitlines()]
    assert events[0]["type"] == "CANDIDATE_SKIPPED"
    assert events[0]["payload"] == {"finding_id": "docs.done", "reason": "already_tried", "rank": 0}


def test_code_component_candidate_is_selectable_and_gated(tmp_path: Path) -> None:
    from arena.repo_goal_loop import _select_promotable

    log = _EventLog(tmp_path / "events.jsonl")
    ranked_bundle = {
        "ranked": {
            "entries": [
                {
                    "findingId": "code.component.untested.comp-tools",
                    "domain": "component_verification",
                    "targetPath": "src/fmc_mcp/tools.py",
                    "priorityScore": 540.0,
                    "autonomyBoundary": "needs_code_change",
                }
            ]
        },
        "plan": {
            "candidates": [
                {
                    "finding_id": "code.component.untested.comp-tools",
                    "target_path": "src/fmc_mcp/tools.py",
                    "target_paths": ["src/fmc_mcp/tools.py"],
                    "verification_commands": ["uv run ruff check .", "uv run pyright", "uv run pytest tests -q"],
                }
            ]
        },
    }

    candidate = _select_promotable(ranked_bundle, set(), log=log, cycle=1)

    assert candidate is not None
    assert candidate["findingId"] == "code.component.untested.comp-tools"
    assert candidate["targetPaths"] == ("src/fmc_mcp/tools.py",)
    assert not (tmp_path / "events.jsonl").exists()


def test_closed_loop_promotes_then_redecomposes(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path, with_missing_docs=True)

    result = run_repo_goal_loop(
        _config(
            repo,
            dry_run=False,
            allow_promotion=True,
            max_cycles=2,
            test_command="python3 -c 'pass'",
        )
    )

    events = _events(result)
    types = [event["type"] for event in events]
    assert "PROMOTED" in types
    last_decomposition_index = max(index for index, type_ in enumerate(types) if type_ == "DECOMPOSITION_COMPLETED")
    assert types.index("BASELINE_ADVANCED") < last_decomposition_index
    completed = [event for event in events if event["type"] == "DECOMPOSITION_COMPLETED"]
    assert len({event["payload"]["snapshot_id"] for event in completed}) >= 2
    assert any(event["type"] == "RUN_COMPLETED" and event["payload"].get("promotions", 0) >= 1 for event in events)
