# Pairwise Proposal Re-ranker Design

Date: 2026-06-19

## Goal

Add one narrow proposer stage that takes an already-built `proposal plan JSON`, mechanically filters out weak or ungrounded candidates, then uses one default LLM as a pairwise judge to choose the single best surviving proposal. The output is still a `proposal-plan/v0` file with the selected winner assigned `rank: 1`, so the existing emit step can keep selecting rank 1 unchanged.

This replaces reliance on absolute `priority_score` for the final pick. It does not replace intake scoring, domain proposal generation, gates, apply, promotion, or emit.

## Scope lock

Build only this:

1. Mechanical candidate pre-filter, no LLM.
2. Pairwise king-of-the-hill tournament over survivors.
3. Two orderings per matchup, temperature 0, one default LLM.
4. Deterministic plan rewrite that sets the winner to rank 1.
5. Sidecar comparison trace with pre-filter drops and both-order matchup records.

Do not build:

- panel judging;
- multiple models;
- OpenRouter/model routing options in this stage;
- golden sets;
- self-improvement loops;
- profile overlays;
- new finding types;
- new absolute quality scores;
- changes to decompose, intake, emit, or gates;
- ticket/GitHub delivery.

## External grounding

The minimal design follows established pairwise-comparison practice but intentionally avoids broader ranking machinery that would exceed scope.

- Chatbot Arena uses pairwise preference judgments rather than absolute scores and aggregates them statistically; this is the right conceptual direction for open-ended quality choices. Source: `https://arxiv.org/abs/2403.04132`.
- Pairwise LLM-as-judge is vulnerable to position bias. The standard diagnostic is to swap candidate order and check whether the same underlying candidate still wins. Source: `https://arxiv.org/html/2406.07791v5`.
- LLM judges can be non-transitive; round-robin plus Bradley-Terry is more reliable for global ranking but is more expensive and out of scope here. Source: `https://arxiv.org/abs/2502.14074`.

Implication for Build Arena: use pairwise comparison only for the final selection from a small existing candidate set, not as a new global scoring system. Run both orderings for each king-of-the-hill matchup. If the two calls disagree after mapping back to candidate ids, keep the incumbent and record the inconsistency.

## Current repo insertion point

Observed code:

- `arena/proposal_planner.py` builds `proposal-plan/v0` candidates ordered by scorecard rank/`priorityScore`.
- `docs/schemas/proposal-plan-v0.schema.json` allows no additional plan fields, so re-ranker metadata must live in a sidecar trace, not inside the plan.
- `arena/llm_adapter.py` already provides an OpenAI-compatible chat client with temperature 0 support and model/provider metadata.
- `arena/repo_goal_loop.py` currently joins `ranked proposals JSON` entries to `proposal plan JSON` candidates and selects from absolute `priorityScore`; the narrow emit pipeline can instead use the re-ranked plan rank 1 without changing emit.

Minimal module:

- Add `./arena/proposal_pairwise_reranker.py`.
- Add tests in `./tests/test_proposal_pairwise_reranker.py`.
- No schema version change.
- No changes to `proposal_emit` or gates.

CLI shape:

```text
uv run python -m arena.proposal_pairwise_reranker \
  --project <target-repo> \
  --plan <proposal plan JSON> \
  --graph <graph JSON or Project Model v1 JSON> \
  --output-plan <reranked plan JSON> \
  --trace <rerank trace JSON> \
  --allow-live
```

No `--model`, no model list, no provider panel. Resolve one default judge from the existing xAI/default configuration path and record the resolved provider/model in trace. Tests inject a fake judge client; production path requires `--allow-live` so this stage cannot spend accidentally.

## Data flow

```text
proposal plan JSON
  -> load + schema-shaped sanity checks
  -> graph index from graph JSON/project-model-v1.projectGraph
  -> mechanical pre-filter
  -> pairwise tournament over survivors
  -> rewrite plan candidates with winner rank 1
  -> write reranked plan JSON + rerank trace JSON
  -> existing emit reads rank 1 unchanged
```

If zero candidates survive, fail closed: write only trace and return non-zero. If one candidate survives, no LLM calls are made; that survivor becomes rank 1 and trace records `call_count: 0`.

## Mechanical pre-filter

The filter is deterministic and runs before any LLM call. It keeps only candidates that are grounded, runnable, binding, specific, and non-circular.

### Graph index

Build a `GraphIndex` from `ProjectGraph` JSON:

- `paths`: every non-empty `node.path`.
- `symbols`: every non-empty `node.symbol` plus `node.label` for symbol-like nodes.
- `node_ids`: every `node.id`.
- `provenance_ids`: every provenance ref id attached to nodes/edges.

Normalize path references as POSIX relative paths. Reject absolute paths, `..`, globs, and empty strings.

### 1. Grounded file/symbol references

Reject if any non-target file/symbol reference in the candidate cannot be resolved to the graph.

Check these candidate sources:

- file-like tokens in `intent`, `success_criterion`, `grounding_constraints`, and `verification_commands`;
- `evidence_refs[*].path` where present;
- symbol-like backtick/code-span references in `intent` and `success_criterion`.

Candidate `target_paths`/`target_path` are validated for specificity and safe relative path syntax, but they are exempt from graph-existence resolution. This is necessary because valid Build Arena proposals can create new files (`./docs/index.md`, `AGENTS.md`, `agent backlog doc`) that do not yet exist as graph nodes. Checked absence evidence for a target is a stronger grounding signal when present, but it is not required for survival because current candidate payloads do not consistently carry absence evidence for every creation target.

For text/reference extraction, first remove the candidate's own normalized target paths from the extracted reference set, then require every remaining path-like reference to resolve to `GraphIndex.paths`. This catches fabricated supporting references without dropping legitimate creation targets.

Drop reasons:

- `missing_target_path`
- `invalid_target_path`
- `unresolved_file_reference:<path>`
- `unresolved_symbol_reference:<symbol>`

### 2. Runnable verification commands

Reject if `verification_commands` is empty or any command is unparsable or outside the known local command families.

Static allowlist for this stage:

- `test -s <target>` or `/usr/bin/test -s <target>`;
- `python3 -m arena.markdown_links --repo . --path <target> [--require-source-references]`;
- `python3 -m arena.code_quality_gate --repo . --path <target>`;
- `python3 -m arena.architecture_fitness_gate ...` if already present in the branch that implements architecture fitness;
- `uv run ...` only as a project quality gate, not by itself as binding evidence.

Reject shell control operators and wrappers: `;`, `&&`, `||`, `|`, `>`, `<`, `$()`, backticks, `bash -lc`, `sh -c`. The runner already uses `shlex.split`; the filter should preserve that no-shell contract.

Also require executable availability for the first token with `shutil.which`, except for `test` which may be `/usr/bin/test`.

Drop reasons:

- `empty_verification`
- `verification_unparseable:<command>`
- `verification_disallowed_shell:<command>`
- `verification_unknown_executable:<command>`
- `verification_unknown_family:<command>`

### 3. Binding verification: no-op must not pass

Reject candidates whose verification is broad enough that a no-op could pass.

Mechanism: static, deterministic classification only. Do not execute target-project verification commands in this pre-filter; command execution would add a dynamic/flaky surface and would blur the advertised comparison cost.

1. Parse every command with `shlex.split` after the runnable-command allowlist.
2. Classify each command family as binding or non-binding.
3. A candidate survives only if at least one command is in a known-binding family and that binding command names one of the candidate's normalized target paths.
4. Broad project gates (`uv run pytest`, `uv run ruff check .`, `uv run pyright`, `mypy src/...`) are allowed only as supplemental checks; by themselves they are non-binding because a no-op can pass them.

This statically detects broad `uv run pytest`, `uv run ruff check .`, or `uv run pyright` candidates that are runnable but not binding to the proposal.

Known binding command classes:

- `test -s <new-target>` fails before creating the file.
- `arena.markdown_links --path <target>` is binding when paired with a missing/non-empty/source-reference target check.
- `arena.code_quality_gate --path <target>` is binding because it compares HEAD against the worktree and rejects no-op/no-improvement.
- `arena.architecture_fitness_gate` is binding when the command names the candidate's architecture contract/check target and the gate is defined to reject still-failing guardrails.

No-op execution can be added later only with per-family expected-failure signatures (exit code plus matched stdout/stderr token). Without those signatures, a non-zero baseline run is ambiguous and must not be used as proof of binding verification.

Drop reasons:

- `verification_non_binding_noop_passes`
- `verification_binding_command_missing_target:<command>`

### 4. Specific target location

Reject if the candidate does not name at least one specific target path or target symbol.

Required:

- `target_paths` has at least one normalized relative path, or
- `target_path` is a normalized relative path and can be promoted to `target_paths`.

Reject directory-only vague locations (`docs/`, `src/`, `.`, `tests`) unless the candidate target has already been normalized to a concrete file such as `./docs/index.md`.

Drop reasons:

- `no_specific_target_location`
- `directory_only_target:<path>`

### 5. Circular definition of done

Reject if `success_criterion` only says the change is changed/grounded/bounded or that project verification remains green, without an externally observable postcondition.

Static red flags:

- `is changed in a bounded way`
- `addresses finding`
- `project verification remains green`
- `quality gate commands pass` with no target-specific observable
- `is covered by a bounded change` with no new test/check/contract artifact named

Keep if the success criterion names a concrete observable such as:

- a file exists and is non-empty;
- local Markdown links/source references resolve for that file;
- a lint count decreases for that file;
- an architecture contract/fitness file fails on current cycle and will pass only after the cycle is fixed;
- a named test/check file or command output must change in a target-specific way.

Drop reason:

- `circular_definition_of_done`

## Pairwise tournament

Input order is deterministic: surviving candidates sorted by their current `rank`, then `finding_id`, then target path. The first survivor is the incumbent. For each remaining survivor, run a matchup incumbent vs challenger.

For each matchup:

1. Call judge with slots A=incumbent, B=challenger.
2. Call judge with slots A=challenger, B=incumbent.
3. Map both returned slot winners back to candidate ids.
4. If both calls choose the same candidate id, that candidate wins the matchup.
5. If they disagree, keep incumbent and mark the matchup `position_inconsistent_keep_incumbent`.

Cost:

```text
LLM calls = 0 if survivors <= 1
LLM calls = 2 * (survivors - 1) otherwise
```

For the default `max_candidates=10`, worst-case comparison cost after pre-filter is 18 model calls.

This is not a Bradley-Terry global ranking. Full round-robin + Bradley-Terry would be more statistically robust under non-transitive preferences but costs O(N^2) comparisons and is explicitly out of scope. The king-of-the-hill design is an efficient final-pick selector with explicit order-bias mitigation.

## Candidate payload shown to the judge

Do not show `priority_score` or original `rank`; those are exactly what the re-ranker is replacing.

Show only:

- stable candidate id/finding id;
- title;
- target paths;
- intent;
- success criterion;
- verification commands;
- grounding constraints;
- evidence refs;
- source recommended action;
- short repo facts excerpt if needed for target context, but exclude rank/score.

Keep payloads sorted and JSON-stable. Truncate long fields deterministically with a trace entry if needed.

## Judge response schema

Response must be JSON only:

```json
{
  "winner_slot": "A",
  "winner_finding_id": "code.component.untested.comp-auth",
  "candidate_a_evidence_cited": ["target_path:./src/pkg/auth.py", "evidence:owned_surface:./src/pkg/auth.py", "evidence:provenance:prov:abc123"],
  "candidate_b_evidence_cited": ["target_path:./docs/index.md", "evidence:absence:./docs/index.md"],
  "reason": "Candidate A is more specific and more verifiable because it names ./src/pkg/auth.py and has a binding gate; Candidate B is grounded but lower leverage for this repo state."
}
```

Validation:

- `winner_slot` must be `A` or `B`.
- `winner_finding_id` must match the candidate assigned to that slot.
- Each evidence-cited array must be non-empty and must cite tokens from the deterministic citable-evidence set built for that slot.
- `reason` must be non-empty and must not mention original rank or priority score.

Build the citable-evidence set per candidate before prompting:

- `target_path:<path>` for every candidate target path;
- `evidence:<kind>:<path>` for each evidence ref with both `kind` and `path`;
- `evidence:provenance:<ref>` for each evidence ref with `ref`;
- `evidence:component:<componentId>` for each evidence ref with `componentId`;
- `constraint:<index>` for grounding constraints when no structured evidence is available.

The prompt includes this set as `citable_evidence`. The response validator accepts only exact tokens from the set. This makes evidence citation enforceable instead of a prose convention.

Provider errors, invalid JSON, truncated responses, invalid schema, or uncited evidence are hard failures for the run. They should not silently fall back to priority-score ordering.

## Exact comparison prompt text

System message:

```text
You are Build Arena's proposal re-ranker. You choose between two already-generated improvement proposals for THIS repository.

Rules:
- Use only the candidate data and repository context in this prompt.
- Ignore any original rank or priority score if present. The final pick must be a relative judgment.
- Prefer the proposal that is more valuable, more specific, and more verifiable for THIS repo right now.
- A proposal is better when it has grounded evidence, a specific target location, a binding verification path that a no-op would not pass, and a concrete non-circular definition of done.
- A proposal is worse when it is vague, mostly documentation filler, broad without a target, not tied to graph evidence, or only says that existing checks remain green.
- You must cite evidence from EACH candidate before choosing.
- Return JSON only. No Markdown. No prose outside JSON.
```

User message template:

```text
Repository context:
{repo_context_json}

Rubric:
Choose which candidate is the more valuable, more specific, more verifiable improvement to THIS repo.
Evaluate in this order:
1. Grounding: Which candidate cites stronger graph/repo evidence?
2. Specificity: Which candidate names a more concrete target file/symbol and action?
3. Verification: Which candidate has a more binding verification path that a no-op would not pass?
4. Leverage: Which candidate better reduces future unsafe or unverified work?
5. Scope fit: Which candidate is smaller and safer without becoming trivial?

Candidate A:
{candidate_a_json}

Candidate B:
{candidate_b_json}

Return exactly this JSON shape:
{
  "winner_slot": "A" or "B",
  "winner_finding_id": "finding id of the winner",
  "candidate_a_evidence_cited": ["tokens from Candidate A citable_evidence"],
  "candidate_b_evidence_cited": ["tokens from Candidate B citable_evidence"],
  "reason": "one concise sentence citing why the winner is more valuable, specific, and verifiable"
}
```

Call settings:

- one default model resolved once at run start;
- temperature 0;
- JSON response format when supported by `OpenAICompatibleChatClient`;
- no model panel;
- no per-match model override.

## Trace sidecar

Write `rerank trace JSON` next to the output plan.

Recommended shape:

```json
{
  "schemaVersion": "proposal-pairwise-rerank-trace/v0",
  "sourcePlanPath": "proposal plan JSON",
  "sourcePlanId": "...",
  "graphPath": "graph JSON",
  "model": {"provider": "xai", "requested_model": "...", "served_model": "...", "temperature": 0},
  "preFilter": {
    "inputCandidateCount": 10,
    "survivorCount": 4,
    "dropped": [
      {"finding_id": "...", "original_rank": 3, "reasons": ["verification_non_binding_noop_passes"]}
    ]
  },
  "tournament": [
    {
      "matchup": 1,
      "incumbent_finding_id": "...",
      "challenger_finding_id": "...",
      "call_ab": {"winner_finding_id": "...", "reason": "...", "candidate_a_evidence_cited": ["..."], "candidate_b_evidence_cited": ["..."], "prompt_hash": "...", "response_hash": "..."},
      "call_ba": {"winner_finding_id": "...", "reason": "...", "candidate_a_evidence_cited": ["..."], "candidate_b_evidence_cited": ["..."], "prompt_hash": "...", "response_hash": "..."},
      "consistent": true,
      "winner_finding_id": "...",
      "decision": "challenger_replaces_incumbent"
    }
  ],
  "winner": {"finding_id": "...", "original_rank": 4, "output_rank": 1},
  "callCount": 6,
  "estimatedCallFormula": "2 * (survivorCount - 1)"
}
```

Trace is separate because `proposal-plan/v0` has `additionalProperties: false`.

## Output plan rewrite

Given the selected winner:

1. Preserve every surviving candidate object except its `rank`.
2. Put winner first with `rank: 1`.
3. Reassign remaining survivors to ranks 2..S in their deterministic survivor order, excluding the winner.
4. Drop pre-filtered candidates from `candidates`.
5. Recompute `candidateCount`, `omittedCount`, and `skippedCount` conservatively for the derived plan:
   - `candidateCount = len(survivors)`;
   - `omittedCount = 0` for the derived rankable set;
   - append pre-filter drops to `skippedFindings` using the existing strict shape `{finding_id, rank, title, reason, evidence_paths}`;
   - collapse rich drop `reasons[]` into singular `reason = "pairwise_prefilter:" + ";".join(reasons)` for the plan; keep structured `reasons[]` in the trace;
   - `skippedCount = len(skippedFindings)`.
6. Preserve source-plan `snapshotId`, `projectRoot`, `repoFactsHash`, `baseLineage`, and `sourceScorecardId` verbatim.
7. Recompute `id` as a stable hash of the derived plan payload.

No new fields. No schema version change.

## Tests to write

Add `./tests/test_proposal_pairwise_reranker.py`.

Required tests:

1. `test_prefilter_rejects_unresolved_file_reference`.
2. `test_prefilter_rejects_empty_or_unknown_verification_command`.
3. `test_prefilter_rejects_non_binding_noop_verification` using a broad project command that could pass a no-op.
4. `test_prefilter_keeps_missing_file_creation_target_without_requiring_graph_node`.
5. `test_prefilter_rejects_no_specific_target_location`.
6. `test_prefilter_rejects_circular_definition_of_done`.
7. `test_tournament_runs_both_orderings_per_matchup` with a fake judge and 3 survivors; assert 4 calls.
8. `test_inconsistent_swapped_order_keeps_incumbent`.
9. `test_consistent_challenger_replaces_incumbent`.
10. `test_output_plan_sets_winner_rank_one_and_preserves_candidate_fields_except_rank`.
11. `test_trace_records_prefilter_drops_both_orderings_reasons_and_hashes`.
12. `test_no_survivors_fails_closed_without_output_plan`.
13. `test_single_survivor_uses_zero_llm_calls`.
14. `test_priority_score_and_original_rank_are_not_sent_to_judge`.
15. `test_schema_invalid_judge_response_fails_closed`.

Use fake judge/client injection in tests. Do not make live calls in tests.

## Thin implementation plan

### Task 1: Add graph/candidate loaders

Create `./arena/proposal_pairwise_reranker.py` with:

- `load_plan(path) -> dict[str, Any]`;
- `load_graph(path) -> dict[str, Any]` supporting raw `graph JSON` and `Project Model v1 JSON` with `projectGraph`;
- `GraphIndex.from_graph(graph)`;
- `candidate_key(candidate)` stable helper.

Verify with focused loader tests.

### Task 2: Add mechanical pre-filter

Implement:

- path normalization;
- file/symbol reference extraction;
- command parsing and allowlist;
- static binding-command classification that rejects broad no-op-pass gates;
- circular DoD detection;
- drop-reason collection.

Write RED tests for each drop reason before implementation.

### Task 3: Add judge abstraction and prompt builder

Implement:

- `ProposalJudge` protocol with `compare(slot_a, slot_b, repo_context) -> JudgeResult`;
- `DefaultLLMProposalJudge` using `OpenAICompatibleChatClient` with temperature 0;
- deterministic prompt builder using the exact prompt text above;
- response schema validation;
- fake judge for tests.

Ensure candidate payload excludes `rank` and `priority_score`.

### Task 4: Add tournament runner

Implement:

- deterministic survivor ordering;
- incumbent/challenger loop;
- two orderings per matchup;
- consistency mapping by `finding_id`;
- inconsistent result keeps incumbent;
- trace record assembly.

### Task 5: Add derived plan writer

Implement:

- winner rank 1;
- survivor ranks reassigned;
- filtered candidates removed;
- skipped finding entries appended with schema-valid collapsed `pairwise_prefilter:` reasons;
- source lineage/snapshot/project fields preserved verbatim;
- stable plan `id` recomputed;
- JSON write with `indent=2, sort_keys=True`.

Validate against `docs/schemas/proposal-plan-v0.schema.json` in tests.

### Task 6: Add CLI

CLI arguments:

```text
--project
--plan
--graph
--output-plan
--trace
--allow-live
```

No `--model`, no `--provider`, no `--openrouter`, no panel/multiple-model options.

When `--allow-live` is absent and no injected judge is provided, fail closed before resolving credentials.

### Task 7: Integration point

For the narrow emit pipeline:

```text
proposal_planner -> proposal_pairwise_reranker -> proposal_emit
```

The emit command still reads only rank 1. No emit change.

For `repo_goal_loop`, do not mix this into the first implementation unless explicitly authorized. If later authorized, the safest integration is after `build_proposal_plan(...)` and before `_select_promotable(...)`, using the re-ranked plan as the final candidate order while leaving decompose/intake/gates unchanged.

## Acceptance criteria

- Existing plan with N candidates produces at most `2 * (survivors - 1)` model calls.
- Both candidate orderings are run for every matchup.
- Any swapped-order inconsistency keeps incumbent and is recorded.
- Winner becomes rank 1 in a schema-valid `proposal-plan/v0` output.
- Trace records all pre-filter drops, both call results, consistency, winner, and cited reasons.
- Candidate payload sent to judge does not contain `priority_score` or original `rank`.
- Full tests pass: `uv run pytest ./tests/test_proposal_pairwise_reranker.py -q`, `uv run ruff check .`, `uv run pyright`.

## Known limitation kept intentionally

King-of-the-hill can still be sensitive to survivor order under non-transitive preferences. That is accepted here because the requested scope is final-pick selection with ~`2*(N-1)` calls, not a full ranking. If this later needs a global ranking, the next design should use round-robin comparisons and Bradley-Terry aggregation as a separate, explicitly authorized feature.
