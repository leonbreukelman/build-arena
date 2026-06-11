from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def test_readme_describes_ai_first_v1_and_bounded_live_status() -> None:
    readme = _read("README.md")

    required_markers = [
        "AI-first decomposer",
        "Project Model v1",
        "project-model-v1.json",
        "project-model-v0.json",
        "uv run python -m arena.decomposer",
        "uv run python -m arena.project_model_cli snapshot",
        "uv run python -m arena.project_model_cli graph",
        "uv run python -m arena.project_model_cli gate",
        "--allow-live",
        "bounded read-only",
        "not ready for broad autonomous live loops",
        "docs/verification/2026-06-05-pre-live-readiness-register.json",
    ]
    missing = [marker for marker in required_markers if marker not in readme]
    assert missing == []

    stale_strings = [
        "Current implementation status: Phase 4 loop glue, budget, divergence, event projection, and worktree promotion foundation is complete.",
    ]
    assert [text for text in stale_strings if text in readme] == []

    stale_identifiers = [
        "XAIProvider",
        "runner_router.py",
        "promoter.py",
        "failure_ledger.py",
    ]
    assert [identifier for identifier in stale_identifiers if identifier in readme] == []

    forbidden_overclaims = [
        "production ready",
        "fully autonomous live",
        "live autonomous loop ready",
        "ready for broad autonomous live loops",
    ]
    lowered = readme.lower()
    # Allow the explicit negative readiness statement while rejecting an
    # unqualified readiness claim. A naive substring check would treat
    # "not ready for broad autonomous live loops" as containing the forbidden
    # phrase "ready for broad autonomous live loops".
    lowered_for_overclaim_scan = lowered.replace(
        "not ready for broad autonomous live loops",
        "",
    )
    assert [phrase for phrase in forbidden_overclaims if phrase in lowered_for_overclaim_scan] == []


def test_agents_current_status_reflects_post_phase4_decomposer_and_readiness() -> None:
    agents = _read("AGENTS.md")

    required_markers = [
        "AI-first decomposer",
        "Project Model v1",
        "project-model-v1.json",
        "project-model-v0.json",
        "LiveProjectModelLLM",
        "pre-live readiness register",
        "not_ready_blockers_remain",
        "broad autonomous live loops",
        "dashboard control plane",
        "rollback endpoint",
        "live subscription-CLI subprocess execution",
    ]
    missing = [marker for marker in required_markers if marker not in agents]
    assert missing == []

    assert "## Current phase" not in agents
    assert "## Current implementation status" in agents

    stale_identifiers = [
        "XAIProvider",
        "runner_router.py",
        "promoter.py",
        "failure_ledger.py",
    ]
    assert [identifier for identifier in stale_identifiers if identifier in agents] == []

    forbidden_overclaims = [
        "production ready",
        "fully autonomous live",
        "live autonomous loop ready",
        "ready for broad autonomous live loops",
    ]
    lowered = agents.lower()
    lowered_for_overclaim_scan = lowered.replace(
        "not ready for broad autonomous live loops",
        "",
    )
    assert [phrase for phrase in forbidden_overclaims if phrase in lowered_for_overclaim_scan] == []


def test_project_brief_current_status_matches_implemented_foundation() -> None:
    brief = _read("docs/build-arena-project-brief.md")

    required_markers = [
        "## Current implementation status",
        "Phase 1-4 foundation is implemented and verified",
        "AI-first decomposer",
        "Project Model v1",
        "project-model-v1.json",
        "project-model-v0.json",
        "LiveProjectModelLLM",
        "--allow-live",
        "not_ready_blockers_remain",
        "not ready for broad autonomous live loops",
        "dashboard control plane",
        "rollback endpoint",
        "live subscription-CLI subprocess execution",
    ]
    missing = [marker for marker in required_markers if marker not in brief]
    assert missing == []

    stale_strings = [
        "## Current phase: calibration",
        "The project is in the calibration phase, not the loop phase.",
        "The loop itself (Hypothesizer, promotion to a real project, divergence detection at scale) is not built",
        "Calibration phase, milestones complete except live validation",
        "Open item: **live validation.**",
    ]
    assert [text for text in stale_strings if text in brief] == []

    lowered = brief.lower()
    lowered_for_overclaim_scan = lowered.replace(
        "not ready for broad autonomous live loops",
        "",
    )
    forbidden_overclaims = [
        "production ready",
        "fully autonomous live",
        "live autonomous loop ready",
        "ready for broad autonomous live loops",
    ]
    assert [phrase for phrase in forbidden_overclaims if phrase in lowered_for_overclaim_scan] == []


def test_agents_preserves_safety_boundaries() -> None:
    agents = _read("AGENTS.md")

    required_safety_markers = [
        "NEVER reason from an imagined file",
        "NEVER guess at function/class/symbol existence",
        "NEVER modify anything under `scorer/`, `verifier/`, or `schema/`",
        "NEVER modify `.arena/scorer.lock.toml`",
        "NEVER hand-edit files under `arena/generated/`",
        "Runner writes are restricted to `.arena/worktrees/<cycle_id>/`",
        "Do not run `git checkout`, `git branch -f`, `git reset --hard`, `git rebase`, or `git push` inside a cycle worktree",
        "must use `git merge --ff-only`",
    ]
    missing = [marker for marker in required_safety_markers if marker not in agents]
    assert missing == []


def test_june5_final_report_records_committed_outcome_not_precommit_state() -> None:
    report = _read("docs/verification/2026-06-05-grok-live-rca-project-model-v1-final-report.md")

    stale = "This slice is ready to commit as one coherent verified change. It does not push, merge, deploy, start a broader live loop, or enable worktree mutation/promotion."
    assert stale not in report
    assert "08a3e29 [verified] add live xai decomposer and project model v1 readiness" in report
    assert "committed locally" in report
    assert "not pushed, merged, deployed" in report


def test_docs_describe_bounded_real_run_attempt_not_unqualified_readiness() -> None:
    required_markers = [
        "operator-switchable",
        "OpenAI-compatible",
        "proposal",
        "ready to attempt a bounded, operator-authorized real run",
        "provider acceptance remains unverified until live smoke",
    ]
    for relative in ("README.md", "AGENTS.md", "docs/build-arena-project-brief.md"):
        text = _read(relative)
        missing = [marker for marker in required_markers if marker not in text]
        assert missing == [], f"{relative} missing {missing}"
        lowered = text.lower().replace("ready to attempt a bounded, operator-authorized real run", "")
        assert "ready for a real run" not in lowered


def test_documented_cli_surfaces_exist() -> None:
    checks = [
        (
            ["uv", "run", "python", "-m", "arena.decomposer", "--help"],
            ["--project", "--output", "--format", "project-model-v0"],
        ),
        (
            ["uv", "run", "python", "-m", "arena.project_model_cli", "--help"],
            ["snapshot", "graph", "gate"],
        ),
        (
            ["uv", "run", "python", "-m", "arena.project_model_cli", "snapshot", "--help"],
            [
                "--project",
                "--artifacts-root",
                "--project-id",
                "--goal",
                "--llm-mode",
                "--allow-live",
                "--live-provider",
                "--live-base-url",
                "--live-model",
                "--live-api-key-env",
            ],
        ),
        (
            ["uv", "run", "python", "-m", "arena.project_model_cli", "graph", "--help"],
            ["--project", "--output"],
        ),
        (
            ["uv", "run", "python", "-m", "arena.project_model_cli", "gate", "--help"],
            ["--snapshot"],
        ),
    ]

    for command, expected_flags in checks:
        result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=True)
        help_text = result.stdout + result.stderr
        missing = [flag for flag in expected_flags if flag not in help_text]
        assert missing == []
