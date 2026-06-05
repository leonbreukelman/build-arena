You are Claude Opus doing a read-only adversarial review of a build-arena agent playbook.

READ-ONLY REVIEW ONLY. Do not ask to modify files. Do not claim you ran commands. You are reviewing the provided Markdown text.

Context:
- The playbook is for an autonomous build-arena agent collaborating with Leon.
- It should mentor the user, explain what is happening and why, report milestones, and catch F3 before code.
- F3 means real/load-bearing reasoning aimed at the wrong project target, component, objective, sequence, or held-out case.
- Elenchus advisory signals are advisory only, not truth/action oracles.
- The workflow should be no-live-API by default unless explicitly authorized.

Review goals:
1. Identify where the playbook may still let an agent go task -> code too quickly.
2. Find ambiguity, missing stop conditions, unsafe defaults, or overclaiming around Elenchus/F-labels.
3. Check whether mentor/reporting guidance is specific enough for a fresh agent.
4. Check whether commands are realistic and robust.
5. Check whether the playbook distinguishes Project Model quality failures from Elenchus advisory failures.
6. Recommend precise improvements that should be made before this playbook is used.

Return a structured review in Markdown with these sections:
- Verdict: ACCEPT / ACCEPT_WITH_CHANGES / REJECT
- Top required changes, prioritized
- Important optional improvements
- Specific edit suggestions with exact replacement/addition language where useful
- Any claims or commands that look fragile
- Final readiness assessment

Here is the playbook under review:

<playbook path="/home/leonb/projects/build-arena/docs/playbooks/2026-06-03-f3-project-model-mentor-runbook.md">
# F3 Project Model Mentor Runbook

Audience: a build-arena agent collaborating with Leon on a primary backlog task.

Purpose: guide the agent from backlog-item understanding through Project Model v0 decomposition, Elenchus advisory preflight, implementation, verification, and calibration feedback, while acting as a mentor. The agent should explain what is happening, why each step matters, and what is interesting or surprising at each milestone.

Compatibility target:

- build-arena Project Model v0 contract: `docs/project-model-v0.md`
- schema: `docs/schemas/project-model-v0.schema.json`
- examples: `docs/examples/project-model-v0-code-adjacent.json` and `docs/examples/project-model-v0-process-strategy.json`
- Elenchus advisory shape: `elenchus-core/docs/api-project-model-v0.md`
- calibration harness: `arena-calibration/fixtures/project_model_v0/` and `arena.project_model_fixtures`

## 1. Core operating rule

Do not go directly from task to code.

The required path is:

```text
primary backlog task
  -> Project Model v0 decomposition
  -> decomposition quality gate / meta-F3 check
  -> human-readable model walkthrough
  -> operator approval or correction
  -> candidate implementation proposal
  -> Elenchus advisory preflight
  -> revise if F2/F3/F4/invalid
  -> smallest TDD implementation slice
  -> verification evidence
  -> calibration feedback if the signal was wrong or novel
```

If any step produces a meaningful correction, pause and explain it before continuing.

## 2. Mentor mode requirements

Run in mentor mode throughout the task.

That means:

1. Explain the purpose of each phase in simple language before doing it.
2. After each interesting result, explain why it matters.
3. Translate project terms into plain language.
4. Do not hide uncertainty. Say what is known, assumed, disputed, or missing.
5. Distinguish evidence from interpretation.
6. Ask for Leon's input only at real decision gates or blockers.
7. When asking for input, batch questions and explain what decision each question affects.
8. Treat corrections as updates to the project model, not as annoyances.
9. Do not overclaim Elenchus. It is an advisory checker, not a truth oracle.
10. Keep a short running narrative: what we thought, what we learned, and what changed.

Use this milestone report template whenever something important happens:

```text
Milestone: <short name>

What I just did:
- <observable action, command, or artifact inspected>

Why this matters:
- <plain-English explanation>

Interesting result:
- <surprise, risk, useful confirmation, or 'none'>

Evidence:
- command: <exact command, if applicable>
- artifact: <path or URL, if applicable>
- result: <short factual result>

My interpretation:
- <what the result suggests, with uncertainty labeled>

Decision needed:
- <none / specific question for Leon>

Next safe step:
- <one step, not a vague future plan>
```

## 3. Simple explanation of F labels

Use this explanation when teaching the operator what the F3 issue means.

```text
F1 means the proposal appears aligned with the project model.

F2 means the rationale is decorative. It sounds like reasoning, but it is not really doing the work.

F3 means the reasoning is real, but aimed at the wrong target. It is like a smart answer to the wrong question. The proposal may be coherent and useful for something, but not for the actual project objective, component, sequence, or held-out case.

F4 means the proposal is too weak, trivial, or underspecified to carry the task.
```

Use examples:

```text
F2 example:
"We should improve reliability because reliability is important." That is vague and decorative.

F3 example:
"We should polish the dashboard because users need clarity." That may be real reasoning, but if the actual blocker is event provenance and replayability, the proposal is aimed at the wrong component.

F4 example:
"Make it better." There is not enough substance to evaluate.
```

The most important distinction:

```text
F2 is fake or decorative reasoning.
F3 is real reasoning pointed at the wrong thing.
```

## 4. Phase 0: bootstrap and safety check

Goal: establish exactly what repo state, branch, tools, and contract files are present before modifying anything.

Run from the build-arena repo unless explicitly told otherwise:

```bash
cd /home/leonb/projects/build-arena

git branch --show-current
git rev-parse --short HEAD
git status --short

test -f docs/project-model-v0.md
test -f docs/schemas/project-model-v0.schema.json
test -f docs/examples/project-model-v0-code-adjacent.json
test -f docs/examples/project-model-v0-process-strategy.json

uv run python -m arena.decomposer --help
```

If there are existing uncommitted or untracked files, report them before editing. Do not overwrite or include unrelated dirty files in commits.

Report milestone: `Bootstrap complete`.

Explain:

- which branch and commit are active;
- whether the Project Model v0 contract is present;
- whether the decomposer supports `--format project-model-v0`;
- whether the worktree is clean or already dirty;
- whether there is any immediate blocker.

If the decomposer does not support Project Model v0, stop and report that the agent is not on the right branch/version.

## 5. Phase 1: intake the primary backlog task

Goal: understand the task before modeling it.

Inputs to collect:

- primary backlog item URL or issue number;
- exact task text;
- target repo or repos;
- explicit non-goals;
- constraints such as no paid live LLM calls, no production gate, no broad refactor;
- expected evidence at the end.

Do not ask many questions first. Inspect the issue or provided task text, then restate what you understand.

Report milestone: `Task understood`.

Use this format:

```text
Milestone: Task understood

Plain-English goal:
- <one sentence>

What success changes:
- <project state after success>

Likely in scope:
- <3-6 bullets>

Likely out of scope:
- <3-6 bullets>

Main F3 risk:
- <how a smart proposal might aim at the wrong thing>

Decision needed:
- none, unless the task text is ambiguous in a way that changes the next command
```

If you need to ask questions, ask only blocker questions such as:

```text
I can proceed with decomposition, but one choice changes the model: should the primary target be runtime build-arena behavior, Elenchus signal quality, or arena-calibration proof? If you do not choose, I will default to runtime build-arena behavior and model Elenchus/calibration as dependencies.
```

## 6. Phase 2: emit Project Model v0

Goal: turn the backlog task into the shared contract that downstream proposals will be checked against.

Create a run artifact location. Prefer a durable path if this is issue work:

```bash
RUN_DATE=$(date +%F)
TASK_SLUG=<short-kebab-slug>
RUN_DIR="docs/verification/${RUN_DATE}-${TASK_SLUG}"
mkdir -p "$RUN_DIR"
MODEL_PATH="$RUN_DIR/project-model-v0.json"
```

Emit the model:

```bash
uv run python -m arena.decomposer \
  --project /home/leonb/projects/build-arena \
  --format project-model-v0 \
  --source-task "<exact primary task text>" \
  --primary-backlog-item "<issue URL or backlog item>" \
  --repo "leonbreukelman/build-arena" \
  --issue "<issue URL or issue number>" \
  --output "$MODEL_PATH"
```

Optional stricter mode, when appropriate:

```bash
uv run python -m arena.decomposer \
  --project /home/leonb/projects/build-arena \
  --format project-model-v0 \
  --source-task "<exact primary task text>" \
  --primary-backlog-item "<issue URL or backlog item>" \
  --repo "leonbreukelman/build-arena" \
  --issue "<issue URL or issue number>" \
  --output "$MODEL_PATH" \
  --fail-on-gap
```

Important behavior: the CLI may write the JSON before returning a quality-gate failure. If the command exits non-zero, inspect the artifact instead of throwing it away. A failed model can still be useful because it shows exactly what is missing.

Report milestone: `Project Model emitted`.

Include:

- model path;
- command exit code;
- whether the model uses `schemaVersion: project-model/v0`;
- whether there were quality-gate findings;
- the most important surprising component, gap, or unclassified surface.

## 7. Phase 3: run the decomposition quality gate / meta-F3 guard

Goal: check whether the Project Model itself is good enough to act as the ruler.

Run this local deterministic check:

```bash
MODEL_PATH="$MODEL_PATH" uv run python - <<'PY'
import json
import os
from pathlib import Path
from arena.project_model_v0 import evaluate_quality_gate

model_path = Path(os.environ["MODEL_PATH"])
model = json.loads(model_path.read_text())
report = evaluate_quality_gate(model).model_dump(mode="json")
print(json.dumps(report, indent=2))
raise SystemExit(0 if report["passed"] else 1)
PY
```

Gate failure codes to explain in plain language:

- `component_without_observable_check`: a component exists, but there is no concrete way to tell whether it works.
- `vague_decomposition`: a component is too general, like "misc" or "do the work".
- `missing_dependencies`: the model lists pieces but does not say what order or relationship matters.
- `contradictory_dependencies`: the model says two things must each come before the other.
- `unclassified_project_surface`: an important surface is not owned by any component.
- `missing_held_out_probe`: a high-risk component lacks a counterexample, perturbation, or tabletop test.

Report milestone: `Model quality gate checked`.

If the quality gate fails:

1. Explain the failure in simple terms.
2. Explain why continuing would be dangerous.
3. Revise the Project Model or ask Leon for a decision if the missing ownership is genuinely human-owned.
4. Re-run the quality gate.
5. Do not proceed to proposal or code until the model is good enough or Leon explicitly approves a known gap.

Mentor explanation to use:

```text
This gate checks the ruler before we use it. If the model is vague or missing surfaces, Elenchus and build-arena could optimize against the wrong target. That would be a meta-F3: the checker might be consistent, but the decomposition itself would be mis-aimed.
```

## 8. Phase 4: walk the operator through the Project Model

Goal: make sure Leon can correct the model before it becomes the contract.

Read and summarize these fields:

- `goal`
- `nonGoals`
- `components`
- `dependencies`
- `invariants`
- `observableChecks`
- `evidenceRequirements`
- `assumptions`
- `risks`
- `nearNeighborAlternatives`
- `heldOutProbes`
- `verificationGaps`
- `unclassifiedProjectSurface`
- `advisorySignalHandoff`

Report milestone: `Project Model walkthrough`.

Use this structure:

```text
Milestone: Project Model walkthrough

The model says the real goal is:
- <goal>

The load-bearing components are:
1. <component id>: <responsibility>, observed by <check id>
2. ...

The ordering/dependencies are:
- <dependency> means <plain language>

The invariants are:
- <rule that must not be violated>

The held-out probes are:
- <probe> catches <what kind of too-narrow reasoning>

The biggest F3 traps are:
- <near neighbor or wrong target>

My confidence:
- <high/medium/low> because <evidence>

Decision needed:
- Please approve this model as the run contract, or correct the goal/components/checks before implementation.
```

Do not treat silence as approval when the model has high-risk changes, unclassified surfaces, or operator-owned decisions.

If Leon corrects the model, revise it and explain what changed:

```text
Correction applied:
- Before: <old interpretation>
- After: <new interpretation>
- Why it matters: <how this changes F3 risk or implementation order>
```

## 9. Phase 5: freeze the approved model for this run

Goal: prevent silent drift.

Once Leon approves the model or you have a clearly safe default, state:

```text
I will use this Project Model v0 as the contract for this run. I will not silently change the goal, components, dependencies, or observable checks during implementation. If implementation reveals that the model is wrong, I will stop and propose a model update before coding further.
```

Save any approved model changes to the model artifact. If the model is manually edited, re-run the quality gate.

Report milestone: `Project Model approved/frozen`.

Include:

- final model path;
- quality-gate status;
- any known gaps intentionally accepted;
- what kind of proposal is now allowed.

## 10. Phase 6: write a candidate implementation proposal before code

Goal: propose the smallest useful implementation slice and map it to the model.

The proposal must include:

- objective;
- affected component IDs;
- exact files expected to change;
- tests to write first;
- checks each change satisfies;
- dependencies/invariants touched;
- expected evidence;
- risks and non-goals;
- whether any live API/model calls are required.

Use this table:

```text
Proposed change: <short name>
Project Model component(s): <ids>
Observable check(s): <ids>
Invariant(s): <ids>
Dependency/sequence: <ids or none>
Files expected: <paths>
Test first: <test path and behavior>
Risk: <low/medium/high>
Why this is the smallest useful slice: <reason>
```

Default first implementation slice for the F3 integration should be the decision seam, not a broad runtime rewrite:

1. Elenchus adapter interface or boundary.
2. Deterministic fake/stub adapter for tests.
3. Preflight decision function.
4. Tests proving F3 produces revise/re-plan and does not spawn the worker.
5. Tests proving F1 proceeds.
6. Tests proving invalid Project Model goes back to decomposition.
7. Documentation of the advisory behavior and no-live-API default.

Report milestone: `Candidate proposal ready`.

Mentor explanation to use:

```text
This is still pre-code. The point is to see whether the plan is aimed at the approved Project Model before implementation makes it expensive to change direction.
```

## 11. Phase 7: run Elenchus advisory preflight

Goal: check the proposal and public rationale against the Project Model before coding.

Build an Elenchus request with:

- `traceId`
- `domain`
- `context`
- `proposedAction`
- `rationale`
- `evidenceBundle`
- `projectModel`

Use the response field:

- `projectModelAlignment.projectModelPresence`
- `projectModelAlignment.projectModelValidity`
- `projectModelAlignment.goalAlignment`
- `projectModelAlignment.componentAlignment`
- `projectModelAlignment.invariantViolations`
- `projectModelAlignment.dependencyViolations`
- `projectModelAlignment.unsupportedAssumptions`
- `projectModelAlignment.evidenceGroundingGaps`
- `projectModelAlignment.nearNeighborResistance`
- `projectModelAlignment.heldOutProbeFailures`
- `projectModelAlignment.failureModeHint`
- `projectModelAlignment.failureModeHintReason`

If Elenchus is available as a local API, use the documented `/api/v2/evaluate` shape from `elenchus-core/docs/api-project-model-v0.md`. If it is not available, do not invent a fake live result. Either use the project-provided deterministic adapter/test fixture, or report that live preflight is blocked and continue only with an explicitly labeled manual advisory review.

Report milestone: `Elenchus advisory preflight complete`.

Use this format:

```text
Milestone: Elenchus advisory preflight complete

Advisory result:
- model presence: <present/absent>
- model validity: <valid/invalid/unsupported>
- failure hint: <F1/F2/F3/F4/none>
- recommendation: <proceed/revise/reject/fix model>

Key alignment findings:
- goal: <aligned/partial/misaligned>
- components: <matched/missing/misdirected>
- invariants: <violations or none>
- dependencies: <violations or none>
- unsupported assumptions: <items or none>
- evidence gaps: <items or none>
- near-neighbor resistance: <distinguished/not distinguished>
- held-out probe failures: <items or none>

Plain-English meaning:
- <short explanation>

Decision needed:
- <none / revise proposal / fix model / ask Leon>
```

Remember: Elenchus is advisory. It can point to reasons to revise, but it does not prove truth.

## 12. Phase 8: interpret F-label outcomes

Use this decision table.

### F1: aligned enough to proceed

Proceed only if:

- Project Model quality gate passed or known gaps are explicitly accepted;
- no invariant violation is unresolved;
- no dependency violation would make the implementation order unsafe;
- evidence gaps are acceptable for the current slice.

Report:

```text
F1 means the proposal appears aimed at the approved model. I will now implement only the approved smallest slice and keep Elenchus advisory, not authoritative.
```

### F2: decorative rationale

Do not code.

Ask the proposal to become more load-bearing:

```text
This looks F2: the rationale sounds good but does not explain why this action satisfies a specific component/check/invariant. I will rewrite the proposal so every claim maps to model evidence, then rerun preflight.
```

### F3: real reasoning, wrong target

Do not code.

Run this re-aiming analysis:

```text
F3 re-aiming analysis

The proposal is actually aimed at:
- <component/goal/sequence/near-neighbor>

The approved Project Model says it should be aimed at:
- <component/goal/sequence/check>

Why the original reasoning was tempting:
- <visible artifact, nearby goal, or example it optimized for>

What held-out probe or near-neighbor exposed the mismatch:
- <probe/alternative>

Revised proposal:
- <new plan mapped to correct component/check>
```

Then rerun Elenchus preflight.

Mentor explanation to use:

```text
This is the important F3 catch. The plan was not nonsense; it was useful for a nearby problem. But build-arena needs to aim at the actual project objective, so we re-aim before writing code.
```

### F4: too weak or trivial

Do not code.

Strengthen the plan or reject it:

```text
This looks F4: there is not enough substance to test or implement safely. I will replace it with a more specific slice that names files, tests, evidence, and model checks.
```

### Invalid or unsupported Project Model

Go back to decomposition.

```text
The checker cannot trust the Project Model yet. This is feedback to build-arena's decomposition, not a proposal failure. I will fix the model before evaluating the implementation plan.
```

## 13. Phase 9: implement the smallest TDD slice

Goal: make the approved behavior real, with tests first.

Before editing:

```bash
git status --short
```

If unrelated dirty files exist, do not touch them. Do not commit them.

For each implementation task:

1. Write a failing test.
2. Run the focused test and capture the expected failure.
3. Implement the minimum code to pass.
4. Run the focused test and capture the pass.
5. Explain what changed and why it was the smallest safe step.
6. Repeat.

Report at these interesting milestones:

- `RED test written`: the failure proves the missing behavior.
- `GREEN behavior implemented`: the new behavior passes the focused test.
- `Integration seam created`: adapter/boundary exists without requiring live API calls.
- `Worker-spawn guard proven`: F3/invalid model prevents worker launch.
- `Advisory semantics preserved`: Elenchus signal is recorded/reported but not treated as truth.
- `Unexpected result`: any failure that changes the model or proposal.

Minimum behavior to prove for the F3 preflight slice:

```text
Given a valid Project Model and an Elenchus advisory F1 result:
- build-arena may proceed to the approved next step.

Given a valid Project Model and an Elenchus advisory F3 result:
- build-arena must not spawn the worker immediately;
- build-arena must record the advisory signal;
- build-arena must request or produce a re-plan aimed at the correct component/check.

Given F2:
- build-arena should reject/rewrite the rationale or proposal before code.

Given F4:
- build-arena should reject the weak proposal before code.

Given an invalid/unsupported Project Model:
- build-arena should return to decomposition/model repair before proposal evaluation.
```

Keep no-live-API behavior as the default. If a live model/API call is proposed, stop and ask for explicit budget/authorization.

## 14. Phase 10: verification

Goal: prove the work with real output.

Run focused tests first, then full gates. Adjust exact commands to the repo, but report exact commands and outputs.

Likely checks in build-arena:

```bash
uv run pytest tests/test_project_model_v0_contract.py -q
uv run pytest -q
ruff check .
pyright

git diff --check
git status --short
```

If `ruff` or `pyright` is not configured, report that directly instead of fabricating success. Use the repo's documented verification target if one exists.

Also scan changed files for obvious secret leakage before final report:

```bash
git diff --name-only
```

Then inspect any changed docs/code that could accidentally contain tokens, credentials, private URLs, runtime caches, or unrelated local paths.

Report milestone: `Verification complete`.

Use this format:

```text
Milestone: Verification complete

Commands run:
- <command>: <pass/fail, short output>

Evidence summary:
- focused tests: <result>
- full tests: <result>
- lint/type: <result or not configured>
- diff check: <result>
- worktree: <clean/dirty with expected files>

What the tests prove:
- <behavior proven>

What they do not prove:
- <limits honestly stated>

Remaining risk:
- <risk or none>
```

Do not claim completion if a blocker remains.

## 15. Phase 11: arena-calibration escalation

Goal: use arena-calibration only when the evaluator or signal needs proof, not for every normal build-arena run.

Escalate to arena-calibration when:

- Elenchus returns an F-label that seems wrong;
- a new F3 pattern appears;
- the Project Model contract changes;
- advisory signal shape changes;
- build-arena depends on a new class of non-code reasoning;
- the operator wants proof that the checker separates F1/F2/F3/F4.

Calibration command from the arena-calibration repo:

```bash
cd /home/leonb/projects/arena-calibration
uv run python -m arena.project_model_fixtures --fixtures-dir fixtures/project_model_v0
```

JSON report form:

```bash
cd /home/leonb/projects/arena-calibration
uv run python -m arena.project_model_fixtures --fixtures-dir fixtures/project_model_v0 --json
```

With newly observed Elenchus signals:

```bash
cd /home/leonb/projects/arena-calibration
uv run python -m arena.project_model_fixtures \
  --fixtures-dir fixtures/project_model_v0 \
  --observed-dir <directory-containing-observed-signals> \
  --json
```

Expected current proof shape:

```text
n_fixtures: 5
f_label_matches: 5/5
signal_matches: 5/5
project_model_quality_passes: 5/5
overall_pass: True
```

If calibration fails, report whether feedback belongs to:

- build-arena Project Model v0 decomposition/contract;
- elenchus-core advisory signal shape/semantics;
- arena-calibration fixture/harness expectations.

Do not tune Elenchus merely to pass visible fixtures. Explain held-out risk and preserve F3 as generalization beyond the visible example.

Report milestone: `Calibration feedback complete`.

## 16. Phase 12: final issue/PR report

Goal: leave a clear artifact trail.

Final report should include:

```text
Final report

Primary task:
- <issue/task>

Project Model:
- artifact: <path>
- quality gate: <passed/failed/accepted gap>
- key components: <ids>
- biggest F3 trap found: <plain English>

Elenchus preflight:
- artifact: <path if available>
- result: <F1/F2/F3/F4/invalid/manual>
- action taken: <proceeded/revised/fixed model/rejected>

Implementation:
- files changed: <paths>
- smallest slice completed: <description>
- anything deliberately not done: <non-goals>

Verification:
- focused tests: <command/result>
- full tests: <command/result>
- lint/type/diff: <command/result>

Calibration:
- not needed / run with <command/result> / fixture added / issue opened

Mentor summary:
- what we learned;
- why the result matters;
- what remains risky or interesting;
- recommended next step.
```

If creating a PR or updating an issue, include the same evidence. Do not say “tests passed” without the exact commands.

## 17. Stop conditions

Stop and report before continuing if any of these happens:

1. Project Model v0 support is missing.
2. The quality gate fails and the repair requires a product/architecture decision.
3. Elenchus returns F3 and the correct target is ambiguous.
4. Elenchus is unavailable and no deterministic/manual fallback has been authorized.
5. A live paid model/API call would be required.
6. Required verification fails.
7. The worktree contains unrelated dirty changes that would be mixed into a commit.
8. A proposed fix expands beyond the approved model or implementation slice.
9. The evidence contradicts the original task understanding.
10. A new F3 class appears that should become an arena-calibration fixture.

When stopping, use this template:

```text
Stop condition reached: <name>

What happened:
- <fact>

Why I am stopping:
- <safety/quality reason>

Options:
1. <safe option>
2. <alternative>
3. <defer/escalate>

My recommendation:
- <one recommendation with reason>
```

## 18. Quick copy/paste prompt for the build-arena agent

Use this to launch a run:

```text
You are the build-arena agent. Follow docs/playbooks/2026-06-03-f3-project-model-mentor-runbook.md.

Work in mentor mode: explain what is happening, why it matters, and any interesting results at each milestone. Keep Leon informed without asking unnecessary questions.

Primary task:
<PASTE TASK OR ISSUE URL>

Rules:
- Do not go directly from task to code.
- First emit Project Model v0.
- Run the decomposition quality gate / meta-F3 guard.
- Walk Leon through the model and get approval or corrections.
- Propose the implementation slice before coding.
- Run Elenchus advisory preflight when available, or clearly label any manual/deterministic fallback.
- If F3 appears, stop coding and re-aim the proposal.
- Keep Elenchus advisory, not a truth oracle.
- Default to no live paid LLM/API calls.
- Use TDD for implementation.
- Report exact verification commands and outputs.
```

## 19. One-sentence reminder

The whole point is to catch smart work aimed at the wrong target before it becomes code.

</playbook>
