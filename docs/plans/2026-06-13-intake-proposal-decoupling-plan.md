# Build Arena Intake/Proposal Decoupling Plan

> **For Hermes:** Use test-driven-development and guarded-live-llm-provider-rollout. Keep `proposer_handoff` advisory; add a deterministic planner between intake and live proposal.

**Goal:** Stop advisory intake findings from becoming thin proposer instructions. Build a deterministic proposal-planning layer that turns ranked intake findings into grounded top-N proposal candidates with repo facts, strong success criteria, and no manual prompt correction.

**Architecture:** Keep `project_intake_scorecard` and `proposer_handoff` v0 stable. Add `repo_facts`, `markdown_links`, and `proposal_planner` under `arena/`. Extend `DiffProposerRunner` requests/prompts with bounded repo facts and grounding constraints. Validate Markdown links after patch application for changed Markdown files.

**Reviewer:** Opus plan review via Claude Code subscription, saved at `/tmp/opus-build-arena-intake-proposer-plan.json`.

---

## Decisions

1. Keep `recommendedAction` in scorecard v0 for compatibility, but no longer treat it as the authoritative proposer instruction.
2. Leave `proposer_handoff` as advisory and non-authorizing.
3. Add a new proposal plan contract: scorecard findings + deterministic repo facts -> ranked grounded proposal candidates.
4. Keep proposal candidates one-file-per-candidate because `DiffProposerRunner` requires exactly one target file.
5. Use finding-neighborhood repo facts, not whole-repo dumps, to avoid prompt bloat.
6. For Markdown proposals, success must include existence, non-empty content, and local Markdown-link resolution.
7. Run live proposal generation only in isolated worktrees.

---

## TDD tasks

### Task 1: Markdown link validator

Files:
- Create `arena/markdown_links.py`
- Create `tests/test_markdown_links.py`

Acceptance:
- Extract local Markdown links from changed `.md` files.
- Ignore external URLs, `mailto:`, `tel:`, and anchors.
- Resolve links relative to the Markdown file's directory.
- Reject missing local targets and escaping paths.
- Return structured evidence for checked and missing links.

### Task 2: Repo facts inventory

Files:
- Create `arena/repo_facts.py`
- Create `tests/test_repo_facts.py`

Acceptance:
- Return deterministic sorted facts about top-level files and docs Markdown files.
- Include booleans such as `readme_exists`, `docs_dir_exists`, and `docs_markdown_files`.
- Emit a stable hash.
- Keep the text block bounded and suitable for prompt inclusion.

### Task 3: Proposal planner and schema

Files:
- Create `arena/proposal_planner.py`
- Create `tests/test_proposal_planner.py`
- Create `docs/schemas/proposal-plan-v0.schema.json`
- Create `tests/test_proposal_plan_schema.py`

Acceptance:
- Build a deterministic top-N plan from scorecard findings and repo facts.
- Candidate intent is planner-authored, not a direct copy of `recommendedAction`.
- Docs-index candidate includes repo facts and Markdown-link success requirement.
- Output is schema-valid and byte-stable across repeated runs.
- Candidate can be converted to a one-file `Hypothesis` plus success criterion for `DiffProposerRunner`.

### Task 4: Diff proposer grounding and Markdown post-check

Files:
- Modify `arena/runners/diff_proposer.py`
- Extend `tests/test_diff_proposer.py`

Acceptance:
- `DiffProposalRequest` accepts repo facts and grounding constraints.
- Prompt includes repo facts and a no-invented-links instruction.
- After applying a patch, changed Markdown files are validated for local link resolution.
- A patch with dead local links is rejected mechanically without Fable.

### Task 5: Pipeline runs and repair loop

Acceptance:
- Full tests/lint/typecheck pass.
- fmc-mcp decomposition -> intake -> proposal plan -> proposal patch runs in isolated worktree without manual prompt edits.
- Opus reviews the top proposal plan and final patch/proposals.
- CMMC readiness confirmation uses an isolated clean worktree because canonical CMMC checkout is dirty/behind.
- If any pipeline issue appears, debug root cause, add regression tests, fix, and rerun.

---

## Verification commands

- `uv run pytest tests/test_markdown_links.py -q`
- `uv run pytest tests/test_repo_facts.py -q`
- `uv run pytest tests/test_proposal_planner.py tests/test_proposal_plan_schema.py -q`
- `uv run pytest tests/test_diff_proposer.py -q`
- `uv run pytest tests -q`
- `uv run ruff check .`
- `uv run pyright`

---

## Failure conditions

Stop and reassess if:
- Any protected path changes.
- Planner output is nondeterministic.
- A docs proposal can pass with missing local Markdown links.
- CMMC worktree freshness cannot be made clean without touching canonical dirty checkout.
- Live provider prompt grows enough to produce truncation.
