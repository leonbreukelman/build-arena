You are Claude Opus doing a focused read-only re-review.

READ-ONLY REVIEW ONLY. Do not claim to run commands or modify files.

You previously reviewed this playbook and returned ACCEPT_WITH_CHANGES. The implementer has patched the playbook. Your job is narrowly to check whether the prior required blockers were resolved and whether the patch introduced any new serious issue.

Prior review:
<prior_review>
# Adversarial Review: F3 Project Model Mentor Runbook

*Read-only review of the Markdown text. I did not run any commands or modify files; command-level concerns below are reasoned from the text, not execution.*

## Verdict

**ACCEPT_WITH_CHANGES**

This is a strong, well-structured playbook with genuinely good instincts: the explicit task→model→gate→approval→proposal→preflight→code spine, the repeated "Elenchus is advisory, not a truth oracle," the meta-gate before using the model as a ruler, and the anti-overfitting line ("Do not tune Elenchus merely to pass visible fixtures") are all above average. But there are a handful of real leaks that let an agent reach code without genuine human gating, an unreconciled conflict around the manual fallback, and a missing case where the local quality gate and Elenchus disagree. These must be fixed before use.

---

## Top required changes (prioritized)

### 1. Close the "clearly safe default" bypass in Phase 5 (highest risk)
Phase 1 establishes a silent default ("If you do not choose, I will default to runtime build-arena behavior…"). Phase 5 then says:

> "Once Leon approves the model **or you have a clearly safe default**, state: I will use this Project Model v0 as the contract…"

Chained together, an agent can decompose, **self-declare its own default "clearly safe," freeze the model, and proceed to proposal/preflight with zero human input** — directly defeating the "operator approval or correction" node in the Section 1 spine. "Clearly safe" is agent-judged and undefined. This is the single biggest task→code leak.

**Fix:** Remove self-certified defaults as an approval substitute. A default may be *proposed* but the freeze step requires either explicit Leon approval or an explicit, time-bounded "proceed on default" acknowledgement. See edit below.

### 2. The "manual advisory review" fallback (Phase 7) lets the proposing agent grade its own homework, and contradicts Stop Condition 4
Phase 7 permits: "report that live preflight is blocked and **continue only with an explicitly labeled manual advisory review.**" But Stop Condition 4 says to stop when "Elenchus is unavailable and **no deterministic/manual fallback has been authorized.**" These conflict: Phase 7 authorizes the agent to self-author the fallback; Stop Condition 4 requires authorization. Worse, the same agent that wrote the proposal performing the F3 self-check removes the independence that makes the preflight meaningful.

**Fix:** Manual/deterministic fallback requires *Leon's* authorization (reconciling with SC4), and a self-performed manual review must be explicitly labeled low-assurance and cannot satisfy the F3 gate alone for high-risk slices.

### 3. "Explicitly accepted" gaps have no named owner (Phases 8/9/5)
Phase 8 F1: "Proceed only if: quality gate passed **or known gaps are explicitly accepted**." Accepted by whom? As written, the agent can self-accept its own model gaps and proceed. Same ambiguity in Phase 5 ("any known gaps intentionally accepted") and the F1 condition.

**Fix:** Every "accepted gap" must read "explicitly accepted **by Leon**." Agents do not self-grant gap waivers.

### 4. Missing case: local quality gate PASSES but Elenchus reports `projectModelValidity: invalid` (review goal 5)
The playbook cleanly separates model-quality failure (Phase 3) from advisory failure (Phase 7/8) — except for the disagreement case. Phase 8's "Invalid or unsupported Project Model → go back to decomposition" reads as unconditional, even though Phase 3 may have already passed the model. Auto-returning to decomposition on an *advisory* invalidity signal would treat Elenchus as authoritative over the local deterministic gate — an overclaim. Auto-ignoring it would waste a real signal.

**Fix:** Add an explicit reconciliation rule (see edit below). When the deterministic local gate and Elenchus disagree on model validity, that is a discrepancy to surface to Leon, not an auto-route in either direction.

### 5. Phase 0 does not actually verify the CLI flags and cross-repo paths the rest of the playbook depends on
Phase 0 runs `--help` but only prose-asserts "whether the decomposer supports `--format project-model-v0`." Phases 2/3/6/7/11 then depend on `--source-task`, `--primary-backlog-item`, `--repo`, `--issue`, `--fail-on-gap`, the `arena.project_model_v0.evaluate_quality_gate` symbol, and files in **other repos** (`elenchus-core/docs/...`, `arena-calibration/...`) that Phase 0 never checks exist. A fresh agent will hit a non-zero exit mid-run with no diagnosis path.

**Fix:** Phase 0 must grep `--help` output for each required flag and check the cross-repo paths, failing fast with a clear message. See fragile-commands section.

---

## Important optional improvements

- **"meta-F3" is conceptually loose.** The gate codes `vague_decomposition` and the F4 example ("Make it better") describe *underspecification* (F4-shaped), not *mis-aiming* (F3). Calling the whole quality gate a "meta-F3 guard" conflates F4-weak models with F3-misaimed models. Either rename it "meta-decomposition gate" or note it catches both meta-F3 (mis-aimed surfaces / wrong ownership) **and** meta-F4 (vague/trivial components).

- **F1 is subtly treated as a go-signal.** "F1 means the proposal appears aimed at the approved model. I will now implement…" An F1 false-negative (Elenchus missing a real F3) shouldn't be the agent's safety net. State explicitly that F1 is *permission to keep checking*, not proof of correctness, and that the agent's own re-aiming reasoning still governs.

- **Undefined term "worker spawn."** Phase 9 milestones and the minimum-behavior spec reference "spawn the worker" / "Worker-spawn guard" with no definition. A fresh agent won't know what the worker is or where the spawn seam lives. Add one sentence defining it and pointing to the relevant module.

- **Reporting channel is unspecified.** The milestone templates are excellent, but the playbook never says *where* they go — conversation, the issue, or `$RUN_DIR`. Specify (e.g., "post milestones in-conversation; persist the Final report and Project Model under `$RUN_DIR`").

- **Hardcoded calibration expectation (`n_fixtures: 5`).** This will become wrong the moment a fixture is added, and may cause an agent to misjudge a passing run as anomalous. Change to "expect all-match (e.g., `f_label_matches == n_fixtures`); the count is not fixed."

- **Secret scan is hand-wavy.** `git diff --name-only` then "inspect" relies on agent diligence. Mention an actual scan (e.g., grep for high-entropy/token patterns or `gitleaks` if available) or explicitly label this as a manual best-effort check.

---

## Specific edit suggestions (exact language)

**Phase 5 (replace the freeze trigger):**
> ~~Once Leon approves the model or you have a clearly safe default, state:~~
> Freeze the model only after Leon explicitly approves it, **or** after you have proposed a default *and* Leon has acknowledged "proceed on the default." A self-judged "safe default" is never sufficient to freeze the contract. If Leon is unresponsive and the model has high-risk changes, unclassified surfaces, or operator-owned decisions, invoke Stop Condition 2 instead of proceeding.

**Phase 7 (replace the fallback clause):**
> If Elenchus is not available, do not invent a live result and do not self-author the fallback. Use the project-provided deterministic adapter/fixture **only if Leon has authorized it**, or stop under Stop Condition 4. If Leon authorizes a manual advisory review, label it `MANUAL-LOW-ASSURANCE`, note that the proposal author is also the reviewer, and require Leon's explicit go for any medium/high-risk slice before coding.

**Phase 8, F1 conditions (amend first bullet):**
> - Project Model quality gate passed, or known gaps are explicitly accepted **by Leon**;

**Phase 8, add a new subsection after "Invalid or unsupported Project Model":**
> ### Local gate vs Elenchus disagree on the model
> If the Phase 3 deterministic gate passed but Elenchus reports `projectModelValidity: invalid/unsupported` (or vice versa), do **not** auto-route. The deterministic gate plus Leon's approval is the contract; Elenchus is advisory. Surface the discrepancy: state which check passed, which failed, the specific Elenchus reason (`projectModelValidity` + any `failureModeHintReason`), and ask Leon whether to (a) revise the model, (b) treat the Elenchus signal as a false flag and log it for calibration, or (c) escalate to arena-calibration (Stop/Phase 11). Do not code until resolved.

**Phase 0 (replace the bare `test -f` block):**
> ```bash
> for f in docs/project-model-v0.md \
>          docs/schemas/project-model-v0.schema.json \
>          docs/examples/project-model-v0-code-adjacent.json \
>          docs/examples/project-model-v0-process-strategy.json; do
>   if test -f "$f"; then echo "present: $f"; else echo "MISSING: $f"; fi
> done
>
> HELP="$(uv run python -m arena.decomposer --help 2>&1)"
> echo "$HELP"
> for flag in --format --source-task --primary-backlog-item --repo --issue --output --fail-on-gap; do
>   echo "$HELP" | grep -q -- "$flag" && echo "flag ok: $flag" || echo "FLAG MISSING: $flag"
> done
> ```
> Also confirm the cross-repo paths used later exist before relying on them: `elenchus-core/docs/api-project-model-v0.md` and `arena-calibration/fixtures/project_model_v0/`. If any required flag or path is missing, stop — you are likely on the wrong branch/version (Stop Condition 1).

---

## Claims / commands that look fragile

- **Unverified CLI surface.** Every flag in Phases 2/6 (`--source-task`, `--primary-backlog-item`, `--repo`, `--issue`, `--fail-on-gap`) and the `--format project-model-v0` value are assumed, not confirmed by Phase 0. The `--repo "leonbreukelman/build-arena"` slug is a guess (git user is "Leon Breukelman"; the path is `build-arena`) and may be wrong.
- **Heredoc Python assumptions (Phase 3).** Relies on `arena.project_model_v0.evaluate_quality_gate` existing, returning a pydantic object with `.model_dump(mode="json")`, and a `report["passed"]` key. Any deviation breaks the gate with a Python traceback the mentor narrative doesn't anticipate. Add a note: "if the import or `passed` key differs, report the actual API instead of fabricating a result."
- **Gate failure codes presented as authoritative.** The six codes drive plain-English mentor explanations; if the real codes differ, the explanations mislead. Add "codes below are illustrative — read the actual `report` output."
- **Bash placeholders that would error if pasted literally.** `TASK_SLUG=<short-kebab-slug>`, `--source-task "<exact primary task text>"`, etc. are templates, but a fresh agent may paste them verbatim. Add a one-line "replace all `<...>` placeholders before running."
- **Partial-write reliance (Phase 2).** "The CLI may write the JSON before returning a quality-gate failure" — sensible handling, but if the CLI instead writes nothing or a truncated file on failure, the downstream "inspect the artifact" step needs a guard (check the file is non-empty / valid JSON before parsing).
- **`pyright`/`ruff` invoked unconditionally (Phase 14).** Mitigated by the "if not configured, report directly" note — good — but the commands should be preceded by a quick existence/config check so a missing tool doesn't read as a failed gate.
- **Hardcoded `n_fixtures: 5`** will silently misrepresent a healthy run once fixtures change.

---

## Final readiness assessment

The skeleton is sound and the safety philosophy is genuinely good — the model-quality gate, the advisory-not-oracle discipline, the anti-overfitting stance, and the rich milestone templates make this usable by a fresh agent. It is **not ready as-is** because of four concrete gaps that let an agent reach code without real human gating or independent checking: (1) the self-certified "clearly safe default" freeze, (2) the self-authored manual fallback that conflicts with Stop Condition 4, (3) agent-self-accepted model gaps, and (4) the unhandled local-gate-vs-Elenchus disagreement. Fix items 1–5 in the required list (all localized edits, no structural rewrite) and this moves to ACCEPT. The optional items (meta-F3 naming, F1-as-go-signal caveat, "worker" definition, reporting channel, calibration-count, secret scan) are quality polish that I'd strongly recommend but would not block on.
</prior_review>

Revised playbook:
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
  -> decomposition quality / meta-F3+meta-F4 gate
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

Reporting locations:

- Post milestone reports in the active conversation so Leon can steer.
- Persist durable run artifacts under `$RUN_DIR`, usually `docs/verification/<date>-<task-slug>/`.
- Put the final report in the issue/PR when one exists.
- Do not bury a required human decision only in a local artifact; surface it in conversation.

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

for f in docs/project-model-v0.md \
         docs/schemas/project-model-v0.schema.json \
         docs/examples/project-model-v0-code-adjacent.json \
         docs/examples/project-model-v0-process-strategy.json; do
  if test -f "$f"; then echo "present: $f"; else echo "MISSING: $f"; fi
done

for f in /home/leonb/projects/elenchus-core/docs/api-project-model-v0.md \
         /home/leonb/projects/arena-calibration/fixtures/project_model_v0; do
  if test -e "$f"; then echo "present: $f"; else echo "MISSING: $f"; fi
done

HELP="$(uv run python -m arena.decomposer --help 2>&1)"
echo "$HELP"
for flag in --format --source-task --primary-backlog-item --repo --issue --output --fail-on-gap; do
  echo "$HELP" | grep -q -- "$flag" && echo "flag ok: $flag" || echo "FLAG MISSING: $flag"
done

uv run python - <<'PY'
from arena.project_model_v0 import evaluate_quality_gate
print(f"quality gate import ok: {evaluate_quality_gate.__name__}")
PY
```

If there are existing uncommitted or untracked files, report them before editing. Do not overwrite or include unrelated dirty files in commits.

Report milestone: `Bootstrap complete`.

Explain:

- which branch and commit are active;
- whether the Project Model v0 contract and cross-repo advisory/calibration paths are present;
- whether the decomposer supports every required flag (`--format`, `--source-task`, `--primary-backlog-item`, `--repo`, `--issue`, `--output`, `--fail-on-gap`);
- whether the worktree is clean or already dirty;
- whether there is any immediate blocker.

If the decomposer does not support Project Model v0, a required flag is missing, a required cross-repo path is missing, or the quality-gate import fails, stop and report that the agent is likely not on the right branch/version.

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
I can proceed with decomposition, but one choice changes the model: should the primary target be runtime build-arena behavior, Elenchus signal quality, or arena-calibration proof? My recommended default is runtime build-arena behavior, with Elenchus/calibration modeled as dependencies. Please approve that default or correct it before I freeze the model.
```

## 6. Phase 2: emit Project Model v0

Goal: turn the backlog task into the shared contract that downstream proposals will be checked against.

Create a run artifact location. Prefer a durable path if this is issue work. Replace every `<...>` placeholder before running any command; do not paste template placeholders literally:

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

Before parsing the artifact, verify it exists, is non-empty, and is valid JSON:

```bash
test -s "$MODEL_PATH"
MODEL_PATH="$MODEL_PATH" uv run python - <<'PY'
import json
import os
from pathlib import Path
path = Path(os.environ["MODEL_PATH"])
json.loads(path.read_text())
print(f"valid JSON: {path}")
PY
```

If the file is missing, empty, or invalid JSON, report the decomposer stdout/stderr and stop instead of inventing model contents.

Report milestone: `Project Model emitted`.

Include:

- model path;
- command exit code;
- whether the model uses `schemaVersion: project-model/v0`;
- whether there were quality-gate findings;
- the most important surprising component, gap, or unclassified surface.

## 7. Phase 3: run the decomposition quality / meta-F3+meta-F4 gate

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

If the import, return type, or `passed` key differs from this example, report the actual API/output and stop rather than fabricating a gate result.

Gate failure codes to explain in plain language. Treat these codes as illustrative; read and quote the actual `report` output for the run:

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
This gate checks the ruler before we use it. If the model is vague, missing surfaces, or aimed at the wrong ownership boundary, Elenchus and build-arena could optimize against the wrong target. This is a meta-decomposition guard: it can catch meta-F3 problems (mis-aimed model surfaces) and meta-F4 problems (vague or trivial model surfaces).
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

Freeze the model only after Leon explicitly approves it, or after you have proposed a default and Leon has acknowledged "proceed on the default." A self-judged "safe default" is never sufficient to freeze the contract. If Leon is unresponsive and the model has high-risk changes, unclassified surfaces, operator-owned decisions, or quality-gate findings, invoke a stop condition instead of proceeding.

When the model is approved, state:

```text
I will use this Project Model v0 as the contract for this run. I will not silently change the goal, components, dependencies, or observable checks during implementation. If implementation reveals that the model is wrong, I will stop and propose a model update before coding further.
```

Save any approved model changes to the model artifact. If the model is manually edited, re-run the quality gate.

Report milestone: `Project Model approved/frozen`.

Include:

- final model path;
- quality-gate status;
- any known gaps intentionally accepted by Leon;
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

In this playbook, "spawn the worker" means crossing from planning/preflight into actual runner execution that can apply changes in a worktree. In the current loop this seam is the APPLY transition through `ctx.router.apply(...)` in `arena/loop.py`, with concrete runners under `arena/runners/`. If the code moves, identify the equivalent runner-execution seam before writing tests.

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

If Elenchus is available as a local API, use the documented `/api/v2/evaluate` shape from `elenchus-core/docs/api-project-model-v0.md`. If it is not available, do not invent a fake live result and do not self-author the fallback. Use the project-provided deterministic adapter/fixture only if Leon has authorized that fallback. If Leon authorizes a manual advisory review, label it `MANUAL-LOW-ASSURANCE`, state that the proposal author is also the reviewer, and require Leon's explicit go before coding any medium/high-risk slice. If no deterministic/manual fallback has been authorized, stop under Stop Condition 4.

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

- Project Model quality gate passed, or known gaps are explicitly accepted by Leon;
- no invariant violation is unresolved;
- no dependency violation would make the implementation order unsafe;
- evidence gaps are acceptable for the current slice.

Report:

```text
F1 means the proposal appears aimed at the approved model. It is permission to keep checking and implement the approved smallest slice, not proof that the proposal is correct. I will keep Elenchus advisory, not authoritative.
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

If both the local deterministic quality gate and Elenchus agree that the Project Model is invalid or unsupported, go back to decomposition.

```text
The checker cannot trust the Project Model yet. This is feedback to build-arena's decomposition, not a proposal failure. I will fix the model before evaluating the implementation plan.
```

### Local gate vs Elenchus disagree on the model

If the Phase 3 deterministic gate passed but Elenchus reports `projectModelValidity: invalid/unsupported`, or if Phase 3 failed but Elenchus appears to accept the model, do not auto-route in either direction. The deterministic gate plus Leon's approval is the contract; Elenchus is advisory, but the discrepancy is still important evidence.

Surface the discrepancy:

```text
Model-validity discrepancy

Local deterministic gate:
- <passed/failed and key findings>

Elenchus projectModelValidity:
- <valid/invalid/unsupported and reason>

Failure hint / reason:
- <failureModeHint and failureModeHintReason, if present>

Decision needed:
- Leon should choose one: revise the model, treat the Elenchus signal as a false flag and log it for calibration, or escalate to arena-calibration.
```

Do not code until the discrepancy is resolved.

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

if command -v ruff >/dev/null 2>&1; then ruff check .; else echo "ruff not installed/configured"; fi
if command -v pyright >/dev/null 2>&1; then pyright; else echo "pyright not installed/configured"; fi

git diff --check
git status --short
```

If `ruff` or `pyright` is not configured, report that directly instead of fabricating success. Use the repo's documented verification target if one exists.

Also scan changed files for obvious secret leakage before final report. Prefer a configured scanner such as `gitleaks` if available; otherwise run this manual best-effort check and still inspect the changed files yourself:

```bash
if command -v gitleaks >/dev/null 2>&1; then
  gitleaks detect --no-git --source . --redact
else
  python3 - <<'PY'
import re
import subprocess

paths = subprocess.check_output(["git", "diff", "--name-only"], text=True).splitlines()
print("changed_files:", len(paths))
for path in paths:
    print(path)

diff = subprocess.check_output(["git", "diff", "--", *paths], text=True) if paths else ""
patterns = {
    "secret_assignment": re.compile(r"(?i)^\+.*(api[_-]?key|secret|password|token|passwd)\s*[:=]\s*['\"]?[A-Za-z0-9_./+=:-]{8,}"),
    "private_key": re.compile(r"^\+.*BEGIN [A-Z ]*PRIVATE KEY"),
    "long_bearer": re.compile(r"(?i)^\+.*bearer\s+[A-Za-z0-9_./+=:-]{20,}"),
}
for name, pattern in patterns.items():
    hits = [line for line in diff.splitlines() if pattern.search(line)]
    print(f"{name}: {len(hits)}")
    for hit in hits[:10]:
        print(hit[:240])
PY
fi
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

Expected proof shape is not a fixed fixture count. The important property is all-match: `f_label_matches == n_fixtures`, `signal_matches == n_fixtures`, `project_model_quality_passes == n_fixtures`, and `overall_pass: True`. A historical example may look like:

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
- quality gate: <passed/failed/gap accepted by Leon>
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
4. Elenchus is unavailable and no deterministic/manual fallback has been authorized by Leon.
5. A live paid model/API call would be required.
6. Required verification fails.
7. The worktree contains unrelated dirty changes that would be mixed into a commit.
8. A proposed fix expands beyond the approved model or implementation slice.
9. The evidence contradicts the original task understanding.
10. A new F3 class appears that should become an arena-calibration fixture.
11. The local deterministic quality gate and Elenchus disagree about Project Model validity.

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
- Run the decomposition quality / meta-F3+meta-F4 gate.
- Walk Leon through the model and get approval or corrections.
- Propose the implementation slice before coding.
- Run Elenchus advisory preflight when available; if unavailable, stop unless Leon authorizes a deterministic or `MANUAL-LOW-ASSURANCE` fallback.
- If F3 appears, stop coding and re-aim the proposal.
- Keep Elenchus advisory, not a truth oracle.
- Default to no live paid LLM/API calls.
- Use TDD for implementation.
- Report exact verification commands and outputs.
```

## 19. One-sentence reminder

The whole point is to catch smart work aimed at the wrong target before it becomes code.

</playbook>

Return Markdown with:
- Verdict: ACCEPT / ACCEPT_WITH_CHANGES / REJECT
- Required blockers remaining, if any
- New serious issues, if any
- Optional polish only, if any
- Final readiness assessment
