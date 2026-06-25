# elenchus-core proposal_run monitored run — 2026-06-21

Generated: 2026-06-21T22:58:56Z

## Owner answer

Run verdict: FAIL_CLOSED_DECOMPOSITION_GATE.

I ran the requested proposal command against `https://github.com/leonbreukelman/elenchus-core` using `grok-4.3` and `XAI_API_KEY` loaded from the repo-local `.env` without printing the key.

The run did not reach intake, proposal planning, pairwise rerank, or emit. It stopped at the live decomposition gate with 5 deterministic gate violations. No `proposal.md` was written. The target was a shallow clone inside the run workdir and stayed clean.

Important operational note: the current checked-out Build Arena worktree at `<repo>` is behind `origin/main` and does not contain `arena.proposal_run`. I did not pull or mutate the dirty worktree. I used a detached `origin/main` worktree at the run root, where `arena.proposal_run` exists.

## Run root

`<repo>/.arena/runs/elenchus-core-proposal-run-20260621T225718Z`

Key artifacts:

- Metadata: `<repo>/.arena/runs/elenchus-core-proposal-run-20260621T225718Z/run-metadata.txt`
- Command stdout: `<repo>/.arena/runs/elenchus-core-proposal-run-20260621T225718Z/proposal-run.stdout.log`
- Command stderr: `<repo>/.arena/runs/elenchus-core-proposal-run-20260621T225718Z/proposal-run.stderr.log`
- Snapshot manifest: `<repo>/.arena/runs/elenchus-core-proposal-run-20260621T225718Z/workdir/snap/snapshot-cdbc2c142ee67999/manifest.json`
- Gate report: `<repo>/.arena/runs/elenchus-core-proposal-run-20260621T225718Z/workdir/snap/snapshot-cdbc2c142ee67999/gate-report.json`
- Project Model v1: `<repo>/.arena/runs/elenchus-core-proposal-run-20260621T225718Z/workdir/snap/snapshot-cdbc2c142ee67999/project-model-v1.json`
- Deterministic gate rerun stdout: `<repo>/.arena/runs/elenchus-core-proposal-run-20260621T225718Z/gate-rerun.stdout.log`

## Preflight evidence

1. Build Arena local checkout state:
   - `git status --short --branch`: `## main...origin/main [behind 9]` plus modified/untracked files.
   - `uv run python -m arena.proposal_run --help` from the current checkout failed with `No module named arena.proposal_run`.

2. `origin/main` state:
   - `git rev-parse origin/main`: `4c73e793eee764e38eb95edeff60d643ff86d611`.
   - A detached `origin/main` worktree successfully showed `proposal run` CLI help.

3. Credential/model preflight:
   - Repo-local `.env` exists.
   - Secret-safe load check: sourcing `.env` made `XAI_API_KEY` present.
   - Manifest confirms provider call used `provider=xai`, `requested_model=grok-4.3`, `model=grok-4.3`, `served_model_matches_requested=true`, `status_code=200`, `api_key_source=environment`.

4. Target preflight:
   - `git ls-remote https://github.com/leonbreukelman/elenchus-core HEAD`: `8c854e504fd6e79ce3cbe185be0150cbb6cd9651`.
   - The run shallow-cloned that target into `workdir/target`.

## Command actually run

Run from detached Build Arena `origin/main` worktree:

```text
uv run python -m arena.proposal_run run https://github.com/leonbreukelman/elenchus-core --decompose-live --live-model grok-4.3 --live-api-key-env XAI_API_KEY --workdir <repo>/.arena/runs/elenchus-core-proposal-run-20260621T225718Z/workdir --keep-workdir --output <repo>/.arena/runs/elenchus-core-proposal-run-20260621T225718Z/proposal.md
```

I added only `--workdir`, `--keep-workdir`, and `--output` so the run would be inspectable instead of deleting intermediates on success. No promotion/apply flags were involved; this `proposal_run` path is proposal-ticket generation, not target mutation.

## Step-by-step outcome

1. Code worktree created:
   - `<repo>/.arena/runs/elenchus-core-proposal-run-20260621T225718Z/build-arena-origin-main`
   - Source: `origin/main` at `4c73e793eee764e38eb95edeff60d643ff86d611`.

2. Target cloned:
   - `<repo>/.arena/runs/elenchus-core-proposal-run-20260621T225718Z/workdir/target`
   - Target HEAD: `8c854e5 Merge pull request #8 from leonbreukelman/docs/issue-3-tech-wide-lens-planning`.
   - Target status after run: `## main...origin/main` with no dirty files.

3. Live decomposition ran:
   - Snapshot ID: `snapshot-cdbc2c142ee67999`.
   - Model metadata: `grok-4.3`, served model matched requested model.
   - Usage from manifest: `prompt_tokens=13270`, `completion_tokens=1416`, `reasoning_tokens=1317`, `total_tokens=16003`.

4. Deterministic Project Model gate failed:
   - Proposal run stderr: `stage 'decompose' failed (exit 1)`.
   - Gate report: `passed=false`, `violation_count=5`.
   - Independent gate rerun returned the same 5 violations and exit 1.

5. Later stages did not run:
   - `scorecard.json`: absent.
   - `proposal-plan.json`: absent.
   - `reranked-plan.json`: absent.
   - `rerank-trace.json`: absent.
   - `proposal.md`: absent.

## Gate violations

From `gate-report.json` and the deterministic gate rerun:

1. `component_measurability` at `components[comp:reporting]`
   - Message: `Component comp:reporting has an underspecified responsibility.`
   - The generated component responsibility was `Generate reports and confidence summaries`, which has 5 words. Current gate code rejects responsibilities with fewer than 6 words.

2. `provenance_completeness` at `cross_cutting_concerns[ccc:anti_fabrication]`
   - Message: `Object has no provenance refs.`

3. `provenance_completeness` at `cross_cutting_concerns[ccc:determinism]`
   - Message: `Object has no provenance refs.`

4. `provenance_completeness` at `cross_cutting_concerns[ccc:provenance]`
   - Message: `Object has no provenance refs.`

5. `provenance_completeness` at `cross_cutting_concerns[ccc:no_live_paid_api_acceptance]`
   - Message: `Object has no provenance refs.`

The cross-cutting concerns were generated with empty `provenance_refs` arrays. That is the same class of schema/gate drift previously seen on live decomposition, but this instance is against `elenchus-core` and passed through provider/model preflight correctly before failing the deterministic gate.

## Mutation/cleanliness check

- The command operated on a shallow clone under the run workdir, not on a local checkout of `elenchus-core`.
- The cloned target was clean after failure: `## main...origin/main` and no dirty paths.
- No proposal artifact was emitted.
- The main Build Arena worktree was not pulled, reset, or edited to make the run possible. The new durable artifacts intentionally written outside `.arena/runs/` are this report and its Opus review prompt/result under `reports/`.

## Independent review

Opus reviewed this report against an embedded evidence packet.

- Review artifact: `<repo>/reports/2026-06-21-elenchus-core-proposal-run-opus-review.json`
- Review prompt: `<repo>/reports/2026-06-21-elenchus-core-proposal-run-review-prompt.md`
- Report-faithfulness review verdict: `ACCEPT`
- Blocking issues: none

Scope note: this is an acceptance of the report's faithfulness, not acceptance of the run. The run verdict remains `FAIL_CLOSED_DECOMPOSITION_GATE`.

## Interpretation

This proves the new `arena.proposal_run` wrapper is reachable on `origin/main`, can clone a GitHub target, can load the xAI key from `.env` when sourced, and can make a live Grok 4.3 decomposition call.

It does not prove the target-project proposal pipeline is ready. The first load-bearing gate rejected the live Project Model before intake, proposal selection, reranking, or ticket emit could start.

Smallest next engineering fix: harden live decomposer output repair/prompting for universal/cross-cutting concern provenance and short component responsibility text, then rerun this same command. Do not weaken the gate; the gate caught exactly the kind of ungrounded model output it is supposed to catch.
