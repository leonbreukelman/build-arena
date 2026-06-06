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