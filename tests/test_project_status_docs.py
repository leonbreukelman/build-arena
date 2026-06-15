from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Core modules that make up the implemented intake -> proposal pipeline. These
# exist on disk today and MUST be discoverable from the orientation docs so a
# fresh agent is not told (as AGENTS.md previously claimed) that the scorecard is
# unimplemented. Keep this list in sync with arena/ when the pipeline grows.
INTAKE_PROPOSAL_MODULES = (
    "project_intake_scorecard",
    "proposal_planner",
    "proposal_candidate_runner",
    "proposal_domains",
    "proposal_ranker",
    "code_quality_gate",
    "repo_goal_loop",
    "repo_facts",
    "markdown_links",
)


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
        "The current branch has local commits ahead of origin until pushed.",
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


def test_current_state_doc_is_historical_not_live_calibration_instructions() -> None:
    current_state = _read("docs/build-arena-current-state.md")

    required_markers = [
        "Historical status snapshot",
        "superseded",
        "AGENTS.md",
        "README.md",
        "docs/build-arena-project-brief.md",
    ]
    missing = [marker for marker in required_markers if marker not in current_state]
    assert missing == []

    stale_calibration_paths = [
        "arena/llm.py",
        "arena/runner.py",
        "exercise_verifier.py",
        "patch_eq.py",
        "results/run_",
    ]
    assert [path for path in stale_calibration_paths if path in current_state] == []


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


def test_docs_describe_bounded_real_run_attempt_as_safe_failed_not_unqualified_readiness() -> None:
    required_markers = [
        "operator-switchable",
        "OpenAI-compatible",
        "proposal",
        "2026-06-15 bounded `fmc-mcp` live production pass executed but promoted nothing",
        "safe gate failure",
        "did not prove a production improvement or broad unattended autonomy",
        "--live-max-calls",
        "--live-api-key-env XAI_API_KEY",
    ]
    for relative in ("README.md", "AGENTS.md", "docs/build-arena-project-brief.md"):
        text = _read(relative)
        missing = [marker for marker in required_markers if marker not in text]
        assert missing == [], f"{relative} missing {missing}"
        assert "provider acceptance remains unverified until live smoke" not in text
        assert "Build Arena is ready to perform one bounded local fmc-mcp production run" not in text
        lowered = text.lower().replace(
            "2026-06-15 bounded `fmc-mcp` live production pass executed but promoted nothing",
            "",
        )
        assert "ready for a real run" not in lowered


def test_failed_live_decomposition_report_does_not_use_unqualified_accept_verdict() -> None:
    report = _read("reports/2026-06-15-grok43-verification-results.md")

    assert "bounded live Grok 4.3 project-model attempt" in report
    assert "smoke" not in report.lower()
    assert "Exit code: 1" in report
    assert '"passed": false' in report
    assert "deterministic gate over the live model output: fail closed with 22 violations" in report
    assert "Run verdict: `FAIL_CLOSED_DECOMPOSITION_GATE`" in report
    assert "Review verdict: `ACCEPT`." not in report
    assert "Report-faithfulness review verdict: `ACCEPT`" in report
    assert "not a live decomposition acceptance" in report


def test_pre_live_register_scopes_bounded_fmc_mcp_production_run_without_broad_overclaim() -> None:
    register = json.loads(_read("docs/verification/2026-06-05-pre-live-readiness-register.json"))

    assert register["overallStatus"] == "not_ready_blockers_remain"
    bounded = register["boundedFmcMcpProductionRun"]
    assert bounded["status"] == "ready_after_operator_authorization"
    assert "one local CLI run" in bounded["scope"]
    assert "--decompose-mode live" in bounded["requiredCommandFlags"]
    assert "--apply-mode live_diff" in bounded["requiredCommandFlags"]
    assert "--live-max-calls 2" in bounded["requiredCommandFlags"]
    assert "--live-api-key-env XAI_API_KEY" in bounded["requiredCommandFlags"]
    assert "operator live spend and local mutation authorization" in bounded["remainingOperatorGates"]
    assert "broad unattended autonomy" in bounded["notProofOf"]
    assert "live code-promotion was proven" in bounded["notProofOf"]

    by_id = {issue["id"]: issue for issue in register["issues"]}
    assert by_id["RCA-002"]["blocksBoundedFmcMcpProductionRun"] is False
    assert "Grok Build wrapper" in by_id["RCA-002"]["boundedFmcMcpScope"]
    assert by_id["M3-001"]["blocksBoundedFmcMcpProductionRun"] is False
    assert by_id["M3-001"]["blocksWorktreeOnlyPatchCycle"] is False
    assert by_id["GAP-001"]["blocksBoundedFmcMcpProductionRun"] is False
    assert by_id["LIVE-002"]["blocksBoundedFmcMcpProductionRun"] is False
    assert by_id["GRAPH-001"]["blocksBoundedFmcMcpProductionRun"] is False


def test_live_provider_docs_disclose_credentials_and_model_enforcement() -> None:
    required_markers = [
        "~/.hermes/.env",
        "api_key_source",
        "explicit model ID",
        "served-model match",
    ]
    for relative in ("README.md", "AGENTS.md", "docs/build-arena-project-brief.md"):
        text = _read(relative)
        missing = [marker for marker in required_markers if marker not in text]
        assert missing == [], f"{relative} missing {missing}"


def test_docs_caveat_ablation_stand_in_and_replacement_decision() -> None:
    decision = _read("docs/decisions/2026-06-11-ablation-runner-replacement.md")
    required_decision_markers = [
        "DeterministicOllamaAblationRunner",
        "deterministic no-API stand-in",
        "Arena Calibration regeneration/Lanham verifier",
        "discrimination matrix",
        "patch-generalization axis",
        "Elenchus",
        "advisory",
    ]
    missing = [marker for marker in required_decision_markers if marker not in decision]
    assert missing == []

    required_active_doc_markers = [
        "deterministic no-API stand-in",
        "not a live Lanham ablation gate",
    ]
    for relative in ("README.md", "AGENTS.md", "docs/build-arena-project-brief.md"):
        text = _read(relative)
        missing = [marker for marker in required_active_doc_markers if marker not in text]
        assert missing == [], f"{relative} missing {missing}"


def test_docs_caveat_scorer_genericity_and_measurement_boundaries() -> None:
    required_markers = [
        "per-repo goal config",
        "read-only measurement surfaces",
        "benchmarks/runtime_proxy.py",
    ]
    for relative in ("README.md", "docs/build-arena-project-brief.md"):
        text = _read(relative)
        missing = [marker for marker in required_markers if marker not in text]
        assert missing == [], f"{relative} missing {missing}"


def test_verification_evidence_retention_policy_is_documented() -> None:
    policy = _read("docs/decisions/2026-06-11-verification-evidence-retention.md")
    required_markers = [
        "docs/verification",
        "1043/1218",
        "summary reports",
        "manifests",
        "hash pointers",
        "non-destructive migration",
    ]
    missing = [marker for marker in required_markers if marker not in policy]
    assert missing == []


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


def test_agents_md_does_not_claim_scorecard_unimplemented() -> None:
    """AGENTS.md previously told fresh agents the scorecard was not implemented.

    The intake scorecard CLI (arena/project_intake_scorecard.py) is implemented
    and tested. The stale false claim must be gone, and AGENTS.md must instead
    describe the scorecard as implemented and advisory.
    """
    agents = _read("AGENTS.md")

    stale_false_claims = [
        "do not claim a scorecard CLI or gate exists",
        "It is not implemented yet",
        "Scorecard output is advisory until implemented and gated",
    ]
    present = [text for text in stale_false_claims if text in agents]
    assert present == [], f"AGENTS.md still contains stale false claim(s): {present}"

    # Positive: the implemented scorecard must be acknowledged.
    assert "project_intake_scorecard" in agents
    assert "advisory" in agents.lower()


def test_agents_md_documents_intake_proposal_pipeline() -> None:
    agents = _read("AGENTS.md")
    missing = [module for module in INTAKE_PROPOSAL_MODULES if module not in agents]
    assert missing == [], f"AGENTS.md does not document pipeline modules: {missing}"
    assert "proposal-plan/v0" in agents


def test_project_brief_documents_intake_proposal_pipeline() -> None:
    brief = _read("docs/build-arena-project-brief.md")
    missing = [module for module in INTAKE_PROPOSAL_MODULES if module not in brief]
    assert missing == [], f"project-brief does not document pipeline modules: {missing}"
    assert "proposal-plan/v0" in brief
    # The architecture map must name the intake -> proposal stage explicitly.
    assert "Intake" in brief and "proposal" in brief.lower()


def test_orientation_docs_referenced_arena_modules_exist() -> None:
    """Every arena/<module>.py path named in orientation docs must exist on disk.

    Prevents documenting a module that was renamed or removed (doc drift in the
    other direction).
    """
    pattern = re.compile(r"arena/([a-z0-9_]+)\.py")
    for relative in ("AGENTS.md", "docs/build-arena-project-brief.md", "README.md"):
        text = _read(relative)
        referenced = sorted(set(pattern.findall(text)))
        missing = [name for name in referenced if not (ROOT / "arena" / f"{name}.py").exists()]
        assert missing == [], f"{relative} references non-existent arena modules: {missing}"


def test_documented_intake_proposal_cli_surfaces_exist() -> None:
    """Functional: the documented intake/proposal CLIs must run and expose the
    flags the docs rely on. Proves doc claims match real CLI behaviour."""
    checks = [
        (
            ["uv", "run", "python", "-m", "arena.project_intake_scorecard", "--help"],
            ["--project", "--snapshot", "--profile", "--output"],
        ),
        (
            ["uv", "run", "python", "-m", "arena.proposal_planner", "--help"],
            ["--project", "--scorecard", "--output", "--max-candidates"],
        ),
        (
            ["uv", "run", "python", "-m", "arena.proposal_candidate_runner", "--help"],
            ["--worktree", "--proposal-plan", "--candidate-rank", "--model"],
        ),
        (
            ["uv", "run", "python", "-m", "arena.markdown_links", "--help"],
            ["--repo", "--path", "--require-source-references"],
        ),
        (
            ["uv", "run", "python", "-m", "arena.repo_goal_loop", "--help"],
            ["--allow-live", "--live-model", "--live-api-key-env", "--live-max-tokens", "--live-max-calls"],
        ),
    ]
    for command, expected_flags in checks:
        result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=True)
        help_text = result.stdout + result.stderr
        missing = [flag for flag in expected_flags if flag not in help_text]
        assert missing == [], f"{command[4]} missing flags {missing}"
