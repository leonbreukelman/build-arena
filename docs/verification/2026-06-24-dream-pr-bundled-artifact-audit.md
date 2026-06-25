# Dream PR bundled-artifact OPSEC audit — 2026-06-24

Status: sensitive findings present; tree-removal remediation is operator-gated.

Reversibility SHA: `08d67d6db78f1ce5f6d6d8eeeb875182417dc9a3` (current `main`/merge HEAD at audit start).

Audit branch/worktree state: `remediations/dream-pr-remediation-2026-06-24` at the same SHA before this doc was written.

## Determination

- Candidate files audited: 78.

- Ratings: sensitive=54, review=23, benign=1.

- Live credential found: no. The secret scan produced pattern hits for env-var names, dummy/test keys, model token wording, and one `risk client responsibilities` substring false-positive class; no unredacted live credential is reproduced here.

- Employer/IP-boundary finding: yes. `54` files carry `fmc-mcp` / firewall-management decomposition, run, or review artifacts. Those are rated `sensitive` and must not be removed by this agent via normal `git rm`; public-history remediation/rotation/force-push is an operator decision.

- Review-rated clutter was not removed in this branch because the sensitive STOP condition fired. A later cleanup PR can remove review-only clutter once Leon decides private retention/deletion and history remediation for the sensitive set.

## Current repo / publication proof

```text
$ git status --short --branch && git rev-parse HEAD && git branch --show-current
## remediations/dream-pr-remediation-2026-06-24
08d67d6db78f1ce5f6d6d8eeeb875182417dc9a3
remediations/dream-pr-remediation-2026-06-24
```
```text
$ gh repo view ... --json nameWithOwner,url,visibility,defaultBranchRef
OWNER_REPO=leonbreukelman/build-arena
{"defaultBranch":"main","nameWithOwner":"leonbreukelman/build-arena","url":"https://github.com/leonbreukelman/build-arena","visibility":"PUBLIC"}
```

## Required baseline evidence

```text
$ git rev-parse b2aa47f
b2aa47f1cfe85206bab9960beebf115cf5d44d74
```
```text
$ git show b2aa47f --stat
commit b2aa47f1cfe85206bab9960beebf115cf5d44d74
Author: Leon Breukelman <leon.breukelman@gmail.com>
Date:   Wed Jun 24 19:33:04 2026 -0500

    feat: publish dream proposer package

 .gitignore                                         |    5 +
 README.md                                          |   26 +-
 arena/capability_lift.py                           |  253 +
 arena/dream_emit.py                                |  197 +
 arena/dream_gate.py                                |  415 ++
 arena/dream_generate.py                            |  291 ++
 arena/dream_research.py                            |  310 ++
 arena/dream_run.py                                 |  414 ++
 arena/project_decomposer_ai.py                     |   90 +-
 .../2026-06-23-dream-proposer-failure-modes.md     |   60 +
 docs/agent-wiki/index.md                           |    1 +
 docs/schemas/capability-map-v0.schema.json         |   72 +
 docs/schemas/dream-v0.schema.json                  |  103 +
 ...2026-06-19-pairwise-proposal-reranker-design.md |   46 +-
 docs/specs/2026-06-23-dream-proposer-tier3-spec.md |  141 +
 .../status/2026-06-17-fmc-mcp-schema-fix-status.md |   42 +
 ...3-dream-proposer-tier3-implementation-status.md |  142 +
 docs/status/INDEX.md                               |    2 +
 ...rwise-proposal-reranker-opus-rereview-prompt.md |   21 +
 ...19-pairwise-proposal-reranker-opus-rereview.err |    0
 ...9-pairwise-proposal-reranker-opus-rereview.json |    1 +
 ...airwise-proposal-reranker-opus-review-prompt.md |   48 +
 ...6-19-pairwise-proposal-reranker-opus-review.err |    0
 ...-19-pairwise-proposal-reranker-opus-review.json |    1 +
 proposal-run-and-emit.patch                        | 1427 ++++++
 ...rena-decomposer-model-candidates-opus-prompt.md |   27 +
 ...composer-model-candidates-opus-review-retry.err |    0
 ...omposer-model-candidates-opus-review-retry.json |    1 +
 ...ena-decomposer-model-candidates-opus-review.err |    0
 ...na-decomposer-model-candidates-opus-review.json |    1 +
 ...6-17-build-arena-decomposer-model-candidates.md |  393 ++
 ...-17-build-arena-decomposer-model-shortlist.json |  146 +
 ...7-fmc-mcp-decomposition-expected-opus-prompt.md |   32 +
 ...7-fmc-mcp-decomposition-expected-opus-retry.err |    0
 ...-fmc-mcp-decomposition-expected-opus-retry.json |    1 +
 ...6-06-17-fmc-mcp-decomposition-expected-opus.err |    0
 ...-06-17-fmc-mcp-decomposition-expected-opus.json |    1 +
 ...mc-mcp-decomposition-real-opus-review-prompt.md |   36 +
 ...mc-mcp-decomposition-real-opus-review-retry.err |    0
 ...c-mcp-decomposition-real-opus-review-retry.json |    1 +
 ...6-17-fmc-mcp-decomposition-real-opus-review.err |    0
 ...-17-fmc-mcp-decomposition-real-opus-review.json |    1 +
 ...6-06-17-fmc-mcp-decomposition-real-summary.json |  453 ++
 reports/2026-06-17-fmc-mcp-decomposition-result.md |  180 +
 ...17-fmc-mcp-grok43-high-reasoning-preflight.json |   29 +
 ...mcp-grok43-high-vs-nonreasoning-comparison.json |  948 ++++
 ...mcp-grok43-high-vs-nonreasoning-opus-brief.json |  743 +++
 ...-mcp-grok43-high-vs-nonreasoning-opus-prompt.md |   37 +
 ...mcp-grok43-high-vs-nonreasoning-opus-review.err |    0
 ...cp-grok43-high-vs-nonreasoning-opus-review.json |    1 +
 ...igh-vs-nonreasoning-opus-review.normalized.json |   43 +
 ...7-fmc-mcp-grok43-high-vs-nonreasoning-report.md |  191 +
 ...intake-expected-vs-actual-opus-review-prompt.md |  182 +
 ...c-mcp-intake-expected-vs-actual-opus-review.err |    0
 ...-mcp-intake-expected-vs-actual-opus-review.json |    1 +
 ...2026-06-17-fmc-mcp-intake-expected-vs-actual.md |  163 +
 .../2026-06-17-fmc-mcp-production-intake-result.md |  156 +
 .../2026-06-17-fmc-mcp-run-prep-opus-rereview.err  |    0
 .../2026-06-17-fmc-mcp-run-prep-opus-rereview.json |    1 +
 ...26-06-17-fmc-mcp-run-prep-opus-review-retry.err |    0
 ...6-06-17-fmc-mcp-run-prep-opus-review-retry.json |    1 +
 .../2026-06-17-fmc-mcp-run-prep-opus-review.err    |    0
 .../2026-06-17-fmc-mcp-run-prep-opus-review.json   |    1 +
 .../2026-06-17-fmc-mcp-run-prep-review-prompt.md   |   19 +
 reports/2026-06-17-fmc-mcp-run-prep.md             |  168 +
 ...26-06-17-fmc-mcp-schema-fix-opus-plan-prompt.md |  124 +
 ...26-06-17-fmc-mcp-schema-fix-opus-plan-retry.err |    0
 ...6-06-17-fmc-mcp-schema-fix-opus-plan-retry.json |    1 +
 .../2026-06-17-fmc-mcp-schema-fix-opus-plan.err    |    0
 .../2026-06-17-fmc-mcp-schema-fix-opus-plan.json   |    1 +
 ...-06-17-fmc-mcp-schema-fix-opus-review-packet.md |  356 ++
 ...-06-17-fmc-mcp-schema-fix-opus-review-retry.err |    0
 ...06-17-fmc-mcp-schema-fix-opus-review-retry.json |    1 +
 .../2026-06-17-fmc-mcp-schema-fix-opus-review.err  |    0
 .../2026-06-17-fmc-mcp-schema-fix-opus-review.json |    1 +
 ...-06-17-fmc-mcp-schema-fix-rerun-comparison.json |  747 +++
 .../2026-06-17-fmc-mcp-schema-fix-rerun-report.md  |  251 +
 .../2026-06-17-model-candidate-research-raw.json   | 4875 ++++++++++++++++++++
 ...mcp-advisory-proposer-opus-inspection-prompt.md |   80 +
 ...8-fmc-mcp-advisory-proposer-opus-inspection.err |    0
 ...-fmc-mcp-advisory-proposer-opus-inspection.json |    1 +
 ...-run-and-advisory-actionability-opus-review.err |    0
 ...run-and-advisory-actionability-opus-review.json |    1 +
 ...run-and-advisory-actionability-review-prompt.md |  508 ++
 ...6-21-elenchus-core-proposal-run-opus-review.err |    0
 ...-21-elenchus-core-proposal-run-opus-review.json |    1 +
 ...2026-06-21-elenchus-core-proposal-run-report.md |  132 +
 ...-21-elenchus-core-proposal-run-review-prompt.md |  152 +
 ...6-23-dream-proposer-tier3-opus-review-prompt.md |   23 +
 ...2026-06-23-dream-proposer-tier3-opus-review.err |    0
 ...026-06-23-dream-proposer-tier3-opus-review.json |    1 +
 ...026-06-23-dream-proposer-tier3-review-packet.md | 3711 +++++++++++++++
 tests/test_capability_lift.py                      |  101 +
 tests/test_dream_emit.py                           |  151 +
 tests/test_dream_gate.py                           |  223 +
 tests/test_dream_generate.py                       |  143 +
 tests/test_dream_research.py                       |  158 +
 tests/test_dream_run.py                            |  326 ++
 tests/test_project_decomposer_ai.py                |  128 +-
 99 files changed, 20175 insertions(+), 87 deletions(-)
```
```text
$ git diff 871c530d207bd95b821ef195159641a5e89ef204..HEAD --stat
 .gitignore                                         |    5 +
 README.md                                          |   26 +-
 arena/capability_lift.py                           |  253 +
 arena/ci_workflow.py                               |  354 ++
 arena/dream_emit.py                                |  197 +
 arena/dream_gate.py                                |  415 ++
 arena/dream_generate.py                            |  291 ++
 arena/dream_research.py                            |  310 ++
 arena/dream_run.py                                 |  414 ++
 arena/project_decomposer_ai.py                     |   90 +-
 arena/proposal_domains.py                          |   46 +-
 .../2026-06-23-dream-proposer-failure-modes.md     |   60 +
 docs/agent-wiki/index.md                           |    1 +
 docs/schemas/capability-map-v0.schema.json         |   72 +
 docs/schemas/dream-v0.schema.json                  |  103 +
 ...2026-06-19-pairwise-proposal-reranker-design.md |   46 +-
 docs/specs/2026-06-23-dream-proposer-tier3-spec.md |  141 +
 .../status/2026-06-17-fmc-mcp-schema-fix-status.md |   42 +
 ...3-dream-proposer-tier3-implementation-status.md |  142 +
 docs/status/INDEX.md                               |    2 +
 ...rwise-proposal-reranker-opus-rereview-prompt.md |   21 +
 ...19-pairwise-proposal-reranker-opus-rereview.err |    0
 ...9-pairwise-proposal-reranker-opus-rereview.json |    1 +
 ...airwise-proposal-reranker-opus-review-prompt.md |   48 +
 ...6-19-pairwise-proposal-reranker-opus-review.err |    0
 ...-19-pairwise-proposal-reranker-opus-review.json |    1 +
 proposal-run-and-emit.patch                        | 1427 ++++++
 ...rena-decomposer-model-candidates-opus-prompt.md |   27 +
 ...composer-model-candidates-opus-review-retry.err |    0
 ...omposer-model-candidates-opus-review-retry.json |    1 +
 ...ena-decomposer-model-candidates-opus-review.err |    0
 ...na-decomposer-model-candidates-opus-review.json |    1 +
 ...6-17-build-arena-decomposer-model-candidates.md |  393 ++
 ...-17-build-arena-decomposer-model-shortlist.json |  146 +
 ...7-fmc-mcp-decomposition-expected-opus-prompt.md |   32 +
 ...7-fmc-mcp-decomposition-expected-opus-retry.err |    0
 ...-fmc-mcp-decomposition-expected-opus-retry.json |    1 +
 ...6-06-17-fmc-mcp-decomposition-expected-opus.err |    0
 ...-06-17-fmc-mcp-decomposition-expected-opus.json |    1 +
 ...mc-mcp-decomposition-real-opus-review-prompt.md |   36 +
 ...mc-mcp-decomposition-real-opus-review-retry.err |    0
 ...c-mcp-decomposition-real-opus-review-retry.json |    1 +
 ...6-17-fmc-mcp-decomposition-real-opus-review.err |    0
 ...-17-fmc-mcp-decomposition-real-opus-review.json |    1 +
 ...6-06-17-fmc-mcp-decomposition-real-summary.json |  453 ++
 reports/2026-06-17-fmc-mcp-decomposition-result.md |  180 +
 ...17-fmc-mcp-grok43-high-reasoning-preflight.json |   29 +
 ...mcp-grok43-high-vs-nonreasoning-comparison.json |  948 ++++
 ...mcp-grok43-high-vs-nonreasoning-opus-brief.json |  743 +++
 ...-mcp-grok43-high-vs-nonreasoning-opus-prompt.md |   37 +
 ...mcp-grok43-high-vs-nonreasoning-opus-review.err |    0
 ...cp-grok43-high-vs-nonreasoning-opus-review.json |    1 +
 ...igh-vs-nonreasoning-opus-review.normalized.json |   43 +
 ...7-fmc-mcp-grok43-high-vs-nonreasoning-report.md |  191 +
 ...intake-expected-vs-actual-opus-review-prompt.md |  182 +
 ...c-mcp-intake-expected-vs-actual-opus-review.err |    0
 ...-mcp-intake-expected-vs-actual-opus-review.json |    1 +
 ...2026-06-17-fmc-mcp-intake-expected-vs-actual.md |  163 +
 .../2026-06-17-fmc-mcp-production-intake-result.md |  156 +
 .../2026-06-17-fmc-mcp-run-prep-opus-rereview.err  |    0
 .../2026-06-17-fmc-mcp-run-prep-opus-rereview.json |    1 +
 ...26-06-17-fmc-mcp-run-prep-opus-review-retry.err |    0
 ...6-06-17-fmc-mcp-run-prep-opus-review-retry.json |    1 +
 .../2026-06-17-fmc-mcp-run-prep-opus-review.err    |    0
 .../2026-06-17-fmc-mcp-run-prep-opus-review.json   |    1 +
 .../2026-06-17-fmc-mcp-run-prep-review-prompt.md   |   19 +
 reports/2026-06-17-fmc-mcp-run-prep.md             |  168 +
 ...26-06-17-fmc-mcp-schema-fix-opus-plan-prompt.md |  124 +
 ...26-06-17-fmc-mcp-schema-fix-opus-plan-retry.err |    0
 ...6-06-17-fmc-mcp-schema-fix-opus-plan-retry.json |    1 +
 .../2026-06-17-fmc-mcp-schema-fix-opus-plan.err    |    0
 .../2026-06-17-fmc-mcp-schema-fix-opus-plan.json   |    1 +
 ...-06-17-fmc-mcp-schema-fix-opus-review-packet.md |  356 ++
 ...-06-17-fmc-mcp-schema-fix-opus-review-retry.err |    0
 ...06-17-fmc-mcp-schema-fix-opus-review-retry.json |    1 +
 .../2026-06-17-fmc-mcp-schema-fix-opus-review.err  |    0
 .../2026-06-17-fmc-mcp-schema-fix-opus-review.json |    1 +
 ...-06-17-fmc-mcp-schema-fix-rerun-comparison.json |  747 +++
 .../2026-06-17-fmc-mcp-schema-fix-rerun-report.md  |  251 +
 .../2026-06-17-model-candidate-research-raw.json   | 4875 ++++++++++++++++++++
 ...mcp-advisory-proposer-opus-inspection-prompt.md |   80 +
 ...8-fmc-mcp-advisory-proposer-opus-inspection.err |    0
 ...-fmc-mcp-advisory-proposer-opus-inspection.json |    1 +
 ...-run-and-advisory-actionability-opus-review.err |    0
 ...run-and-advisory-actionability-opus-review.json |    1 +
 ...run-and-advisory-actionability-review-prompt.md |  508 ++
 ...6-21-elenchus-core-proposal-run-opus-review.err |    0
 ...-21-elenchus-core-proposal-run-opus-review.json |    1 +
 ...2026-06-21-elenchus-core-proposal-run-report.md |  132 +
 ...-21-elenchus-core-proposal-run-review-prompt.md |  152 +
 ...6-23-dream-proposer-tier3-opus-review-prompt.md |   23 +
 ...2026-06-23-dream-proposer-tier3-opus-review.err |    0
 ...026-06-23-dream-proposer-tier3-opus-review.json |    1 +
 ...026-06-23-dream-proposer-tier3-review-packet.md | 3711 +++++++++++++++
 tests/test_capability_lift.py                      |  101 +
 tests/test_ci_workflow.py                          |  171 +
 tests/test_dream_emit.py                           |  151 +
 tests/test_dream_gate.py                           |  223 +
 tests/test_dream_generate.py                       |  143 +
 tests/test_dream_research.py                       |  158 +
 tests/test_dream_run.py                            |  326 ++
 tests/test_project_decomposer_ai.py                |  128 +-
 tests/test_proposal_domains.py                     |  133 +
 103 files changed, 20875 insertions(+), 91 deletions(-)
```

## Candidate derivation

Candidate set command:

```text
# Start from: git show --name-status --format= b2aa47f
# Exclude: .gitignore, README.md, dream lane code/tests/schema/spec/wiki/status docs,
# and arena/project_decomposer_ai.py + tests/test_project_decomposer_ai.py (handled in forensics doc).
# Result written during audit to /tmp/build-arena-remediation-evidence/candidate-files.txt.
```

Candidate file list:

```text
docs/agent-wiki/index.md
docs/specs/2026-06-19-pairwise-proposal-reranker-design.md
docs/status/2026-06-17-fmc-mcp-schema-fix-status.md
docs/status/INDEX.md
docs/verification/2026-06-19-pairwise-proposal-reranker-opus-rereview-prompt.md
docs/verification/2026-06-19-pairwise-proposal-reranker-opus-rereview.err
docs/verification/2026-06-19-pairwise-proposal-reranker-opus-rereview.json
docs/verification/2026-06-19-pairwise-proposal-reranker-opus-review-prompt.md
docs/verification/2026-06-19-pairwise-proposal-reranker-opus-review.err
docs/verification/2026-06-19-pairwise-proposal-reranker-opus-review.json
proposal-run-and-emit.patch
reports/2026-06-17-build-arena-decomposer-model-candidates-opus-prompt.md
reports/2026-06-17-build-arena-decomposer-model-candidates-opus-review-retry.err
reports/2026-06-17-build-arena-decomposer-model-candidates-opus-review-retry.json
reports/2026-06-17-build-arena-decomposer-model-candidates-opus-review.err
reports/2026-06-17-build-arena-decomposer-model-candidates-opus-review.json
reports/2026-06-17-build-arena-decomposer-model-candidates.md
reports/2026-06-17-build-arena-decomposer-model-shortlist.json
reports/2026-06-17-fmc-mcp-decomposition-expected-opus-prompt.md
reports/2026-06-17-fmc-mcp-decomposition-expected-opus-retry.err
reports/2026-06-17-fmc-mcp-decomposition-expected-opus-retry.json
reports/2026-06-17-fmc-mcp-decomposition-expected-opus.err
reports/2026-06-17-fmc-mcp-decomposition-expected-opus.json
reports/2026-06-17-fmc-mcp-decomposition-real-opus-review-prompt.md
reports/2026-06-17-fmc-mcp-decomposition-real-opus-review-retry.err
reports/2026-06-17-fmc-mcp-decomposition-real-opus-review-retry.json
reports/2026-06-17-fmc-mcp-decomposition-real-opus-review.err
reports/2026-06-17-fmc-mcp-decomposition-real-opus-review.json
reports/2026-06-17-fmc-mcp-decomposition-real-summary.json
reports/2026-06-17-fmc-mcp-decomposition-result.md
reports/2026-06-17-fmc-mcp-grok43-high-reasoning-preflight.json
reports/2026-06-17-fmc-mcp-grok43-high-vs-nonreasoning-comparison.json
reports/2026-06-17-fmc-mcp-grok43-high-vs-nonreasoning-opus-brief.json
reports/2026-06-17-fmc-mcp-grok43-high-vs-nonreasoning-opus-prompt.md
reports/2026-06-17-fmc-mcp-grok43-high-vs-nonreasoning-opus-review.err
reports/2026-06-17-fmc-mcp-grok43-high-vs-nonreasoning-opus-review.json
reports/2026-06-17-fmc-mcp-grok43-high-vs-nonreasoning-opus-review.normalized.json
reports/2026-06-17-fmc-mcp-grok43-high-vs-nonreasoning-report.md
reports/2026-06-17-fmc-mcp-intake-expected-vs-actual-opus-review-prompt.md
reports/2026-06-17-fmc-mcp-intake-expected-vs-actual-opus-review.err
reports/2026-06-17-fmc-mcp-intake-expected-vs-actual-opus-review.json
reports/2026-06-17-fmc-mcp-intake-expected-vs-actual.md
reports/2026-06-17-fmc-mcp-production-intake-result.md
reports/2026-06-17-fmc-mcp-run-prep-opus-rereview.err
reports/2026-06-17-fmc-mcp-run-prep-opus-rereview.json
reports/2026-06-17-fmc-mcp-run-prep-opus-review-retry.err
reports/2026-06-17-fmc-mcp-run-prep-opus-review-retry.json
reports/2026-06-17-fmc-mcp-run-prep-opus-review.err
reports/2026-06-17-fmc-mcp-run-prep-opus-review.json
reports/2026-06-17-fmc-mcp-run-prep-review-prompt.md
reports/2026-06-17-fmc-mcp-run-prep.md
reports/2026-06-17-fmc-mcp-schema-fix-opus-plan-prompt.md
reports/2026-06-17-fmc-mcp-schema-fix-opus-plan-retry.err
reports/2026-06-17-fmc-mcp-schema-fix-opus-plan-retry.json
reports/2026-06-17-fmc-mcp-schema-fix-opus-plan.err
reports/2026-06-17-fmc-mcp-schema-fix-opus-plan.json
reports/2026-06-17-fmc-mcp-schema-fix-opus-review-packet.md
reports/2026-06-17-fmc-mcp-schema-fix-opus-review-retry.err
reports/2026-06-17-fmc-mcp-schema-fix-opus-review-retry.json
reports/2026-06-17-fmc-mcp-schema-fix-opus-review.err
reports/2026-06-17-fmc-mcp-schema-fix-opus-review.json
reports/2026-06-17-fmc-mcp-schema-fix-rerun-comparison.json
reports/2026-06-17-fmc-mcp-schema-fix-rerun-report.md
reports/2026-06-17-model-candidate-research-raw.json
reports/2026-06-18-fmc-mcp-advisory-proposer-opus-inspection-prompt.md
reports/2026-06-18-fmc-mcp-advisory-proposer-opus-inspection.err
reports/2026-06-18-fmc-mcp-advisory-proposer-opus-inspection.json
reports/2026-06-18-fmc-mcp-proposer-run-and-advisory-actionability-opus-review.err
reports/2026-06-18-fmc-mcp-proposer-run-and-advisory-actionability-opus-review.json
reports/2026-06-18-fmc-mcp-proposer-run-and-advisory-actionability-review-prompt.md
reports/2026-06-21-elenchus-core-proposal-run-opus-review.err
reports/2026-06-21-elenchus-core-proposal-run-opus-review.json
reports/2026-06-21-elenchus-core-proposal-run-report.md
reports/2026-06-21-elenchus-core-proposal-run-review-prompt.md
reports/2026-06-23-dream-proposer-tier3-opus-review-prompt.md
reports/2026-06-23-dream-proposer-tier3-opus-review.err
reports/2026-06-23-dream-proposer-tier3-opus-review.json
reports/2026-06-23-dream-proposer-tier3-review-packet.md
```

## Classification table

| path | lines | description | rating | evidence/basis |
|---|---:|---|---|---|
| `docs/agent-wiki/index.md` | 32 | # Build Arena Agent Wiki | sensitive | contains fmc-mcp production-pass index marker at line 15; b2aa only added a dream-proposer line, but the file currently carries employer-adjacent marker content |
| `docs/specs/2026-06-19-pairwise-proposal-reranker-design.md` | 534 | # Pairwise Proposal Re-ranker Design | benign | versioned public Build Arena design-spec cleanup, not raw run output |
| `docs/status/2026-06-17-fmc-mcp-schema-fix-status.md` | 42 | # fmc-mcp schema-fix status — 2026-06-17 | sensitive | status doc for fmc-mcp schema/live decomposition rerun; employer-adjacent firewall-management project marker |
| `docs/status/INDEX.md` | 22 | # Status Doc Index | sensitive | b2aa adds historical index entry for fmc-mcp schema-fix status doc |
| `docs/verification/2026-06-19-pairwise-proposal-reranker-opus-rereview-prompt.md` | 21 | # Opus re-review prompt: patched pairwise proposer re-ranker design | review | raw patch/report/review/run artifact or model research output; no public-tree need found |
| `docs/verification/2026-06-19-pairwise-proposal-reranker-opus-rereview.err` | 0 | (empty file) | review | raw patch/report/review/run artifact or model research output; no public-tree need found |
| `docs/verification/2026-06-19-pairwise-proposal-reranker-opus-rereview.json` | 1 | JSON model/tool result with keys [type, subtype, is_error, api_error_status, duration_ms, duration_api_ms]; result starts: 'All six required patches are addressed, and I verified the two schema-dependent claims (patches 3 and 5) directly agains' | review | raw patch/report/review/run artifact or model research output; no public-tree need found |
| `docs/verification/2026-06-19-pairwise-proposal-reranker-opus-review-prompt.md` | 48 | # Opus review prompt: pairwise proposer re-ranker design | review | raw patch/report/review/run artifact or model research output; no public-tree need found |
| `docs/verification/2026-06-19-pairwise-proposal-reranker-opus-review.err` | 0 | (empty file) | review | raw patch/report/review/run artifact or model research output; no public-tree need found |
| `docs/verification/2026-06-19-pairwise-proposal-reranker-opus-review.json` | 1 | JSON model/tool result with keys [type, subtype, is_error, api_error_status, duration_ms, duration_api_ms]; result starts: 'I have enough to review. Key cross-checks against the code:' | review | raw patch/report/review/run artifact or model research output; no public-tree need found |
| `proposal-run-and-emit.patch` | 1427 | diff --git a/README.md b/README.md | review | raw patch/report/review/run artifact or model research output; no public-tree need found |
| `reports/2026-06-17-build-arena-decomposer-model-candidates-opus-prompt.md` | 27 | You are Opus reviewing a model-selection recommendation for Build Arena's live project decomposer role. | review | raw patch/report/review/run artifact or model research output; no public-tree need found |
| `reports/2026-06-17-build-arena-decomposer-model-candidates-opus-review-retry.err` | 0 | (empty file) | review | raw patch/report/review/run artifact or model research output; no public-tree need found |
| `reports/2026-06-17-build-arena-decomposer-model-candidates-opus-review-retry.json` | 1 | JSON model/tool result with keys [type, subtype, is_error, api_error_status, duration_ms, duration_api_ms]; result starts: '{' | review | raw patch/report/review/run artifact or model research output; no public-tree need found |
| `reports/2026-06-17-build-arena-decomposer-model-candidates-opus-review.err` | 0 | (empty file) | review | raw patch/report/review/run artifact or model research output; no public-tree need found |
| `reports/2026-06-17-build-arena-decomposer-model-candidates-opus-review.json` | 1 | JSON artifact with keys [type, subtype, duration_ms, duration_api_ms, is_error, num_turns] | review | raw patch/report/review/run artifact or model research output; no public-tree need found |
| `reports/2026-06-17-build-arena-decomposer-model-candidates.md` | 393 | # Build Arena decomposer model candidates — 2026-06-17 | review | raw patch/report/review/run artifact or model research output; no public-tree need found |
| `reports/2026-06-17-build-arena-decomposer-model-shortlist.json` | 146 | JSON array artifact, items=12 | review | raw patch/report/review/run artifact or model research output; no public-tree need found |
| `reports/2026-06-17-fmc-mcp-decomposition-expected-opus-prompt.md` | 32 | You are Opus reviewing Build Arena's fmc-mcp live decomposition expectations before the decomposition is run. | sensitive | fmc-mcp decomposition/intake/proposer/review artifact; employer-adjacent firewall-management research/run content |
| `reports/2026-06-17-fmc-mcp-decomposition-expected-opus-retry.err` | 0 | (empty file) | sensitive | fmc-mcp decomposition/intake/proposer/review artifact; employer-adjacent firewall-management research/run content |
| `reports/2026-06-17-fmc-mcp-decomposition-expected-opus-retry.json` | 1 | JSON model/tool result with keys [type, subtype, is_error, api_error_status, duration_ms, duration_api_ms]; result starts: '{' | sensitive | fmc-mcp decomposition/intake/proposer/review artifact; employer-adjacent firewall-management research/run content |
| `reports/2026-06-17-fmc-mcp-decomposition-expected-opus.err` | 0 | (empty file) | sensitive | fmc-mcp decomposition/intake/proposer/review artifact; employer-adjacent firewall-management research/run content |
| `reports/2026-06-17-fmc-mcp-decomposition-expected-opus.json` | 1 | JSON artifact with keys [type, subtype, duration_ms, duration_api_ms, is_error, num_turns] | sensitive | fmc-mcp decomposition/intake/proposer/review artifact; employer-adjacent firewall-management research/run content |
| `reports/2026-06-17-fmc-mcp-decomposition-real-opus-review-prompt.md` | 36 | You are Opus reviewing the REAL live Build Arena decomposition result for fmc-mcp. | sensitive | fmc-mcp decomposition/intake/proposer/review artifact; employer-adjacent firewall-management research/run content |
| `reports/2026-06-17-fmc-mcp-decomposition-real-opus-review-retry.err` | 0 | (empty file) | sensitive | fmc-mcp decomposition/intake/proposer/review artifact; employer-adjacent firewall-management research/run content |
| `reports/2026-06-17-fmc-mcp-decomposition-real-opus-review-retry.json` | 1 | JSON model/tool result with keys [type, subtype, is_error, api_error_status, duration_ms, duration_api_ms]; result starts: '{' | sensitive | fmc-mcp decomposition/intake/proposer/review artifact; employer-adjacent firewall-management research/run content |
| `reports/2026-06-17-fmc-mcp-decomposition-real-opus-review.err` | 0 | (empty file) | sensitive | fmc-mcp decomposition/intake/proposer/review artifact; employer-adjacent firewall-management research/run content |
| `reports/2026-06-17-fmc-mcp-decomposition-real-opus-review.json` | 1 | JSON artifact with keys [type, subtype, duration_ms, duration_api_ms, is_error, num_turns] | sensitive | fmc-mcp decomposition/intake/proposer/review artifact; employer-adjacent firewall-management research/run content |
| `reports/2026-06-17-fmc-mcp-decomposition-real-summary.json` | 453 | JSON artifact with keys [artifact_paths, component_profiles, counts, exit_code, expectation_checks, gate] | sensitive | fmc-mcp decomposition/intake/proposer/review artifact; employer-adjacent firewall-management research/run content |
| `reports/2026-06-17-fmc-mcp-decomposition-result.md` | 180 | # fmc-mcp live decomposition result — 2026-06-17 | sensitive | fmc-mcp decomposition/intake/proposer/review artifact; employer-adjacent firewall-management research/run content |
| `reports/2026-06-17-fmc-mcp-grok43-high-reasoning-preflight.json` | 29 | JSON artifact with keys [content_hash, content_preview, finish_reason, reasoning_effort, requested_model, served_model] | sensitive | fmc-mcp decomposition/intake/proposer/review artifact; employer-adjacent firewall-management research/run content |
| `reports/2026-06-17-fmc-mcp-grok43-high-vs-nonreasoning-comparison.json` | 948 | JSON artifact with keys [comparison_notes, delta, mechanical_verdict, new_high_reasoning, previous_non_reasoning] | sensitive | fmc-mcp decomposition/intake/proposer/review artifact; employer-adjacent firewall-management research/run content |
| `reports/2026-06-17-fmc-mcp-grok43-high-vs-nonreasoning-opus-brief.json` | 743 | JSON artifact with keys [artifact_paths, comparison_notes, delta, mechanical_verdict, new_high_reasoning, previous_non_reasoning] | sensitive | fmc-mcp decomposition/intake/proposer/review artifact; employer-adjacent firewall-management research/run content |
| `reports/2026-06-17-fmc-mcp-grok43-high-vs-nonreasoning-opus-prompt.md` | 37 | You are Opus reviewing a Build Arena decomposition-only comparison for fmc-mcp. | sensitive | fmc-mcp decomposition/intake/proposer/review artifact; employer-adjacent firewall-management research/run content |
| `reports/2026-06-17-fmc-mcp-grok43-high-vs-nonreasoning-opus-review.err` | 0 | (empty file) | sensitive | fmc-mcp decomposition/intake/proposer/review artifact; employer-adjacent firewall-management research/run content |
| `reports/2026-06-17-fmc-mcp-grok43-high-vs-nonreasoning-opus-review.json` | 1 | JSON model/tool result with keys [type, subtype, is_error, api_error_status, duration_ms, duration_api_ms]; result starts: '```json' | sensitive | fmc-mcp decomposition/intake/proposer/review artifact; employer-adjacent firewall-management research/run content |
| `reports/2026-06-17-fmc-mcp-grok43-high-vs-nonreasoning-opus-review.normalized.json` | 43 | JSON artifact with keys [blockers_before_intake, comparison, high_reasoning_strengths, high_reasoning_weaknesses, previous_non_reasoning_strengths, previous_non_reasoning_weaknesses] | sensitive | fmc-mcp decomposition/intake/proposer/review artifact; employer-adjacent firewall-management research/run content |
| `reports/2026-06-17-fmc-mcp-grok43-high-vs-nonreasoning-report.md` | 191 | # fmc-mcp Grok 4.3 high-reasoning decomposition comparison — 2026-06-17 | sensitive | fmc-mcp decomposition/intake/proposer/review artifact; employer-adjacent firewall-management research/run content |
| `reports/2026-06-17-fmc-mcp-intake-expected-vs-actual-opus-review-prompt.md` | 182 | You are Opus reviewing an owner-facing Build Arena analysis for Leon. Do not use tools. Return JSON only. | sensitive | fmc-mcp decomposition/intake/proposer/review artifact; employer-adjacent firewall-management research/run content |
| `reports/2026-06-17-fmc-mcp-intake-expected-vs-actual-opus-review.err` | 0 | (empty file) | sensitive | fmc-mcp decomposition/intake/proposer/review artifact; employer-adjacent firewall-management research/run content |
| `reports/2026-06-17-fmc-mcp-intake-expected-vs-actual-opus-review.json` | 1 | JSON model/tool result with keys [type, subtype, is_error, api_error_status, duration_ms, duration_api_ms]; result starts: '{' | sensitive | fmc-mcp decomposition/intake/proposer/review artifact; employer-adjacent firewall-management research/run content |
| `reports/2026-06-17-fmc-mcp-intake-expected-vs-actual.md` | 163 | # fmc-mcp intake: expected vs actual — 2026-06-17 | sensitive | fmc-mcp decomposition/intake/proposer/review artifact; employer-adjacent firewall-management research/run content |
| `reports/2026-06-17-fmc-mcp-production-intake-result.md` | 156 | # fmc-mcp production intake result — 2026-06-17 | sensitive | fmc-mcp decomposition/intake/proposer/review artifact; employer-adjacent firewall-management research/run content |
| `reports/2026-06-17-fmc-mcp-run-prep-opus-rereview.err` | 0 | (empty file) | sensitive | fmc-mcp decomposition/intake/proposer/review artifact; employer-adjacent firewall-management research/run content |
| `reports/2026-06-17-fmc-mcp-run-prep-opus-rereview.json` | 1 | JSON model/tool result with keys [type, subtype, is_error, api_error_status, duration_ms, duration_api_ms]; result starts: '```json' | sensitive | fmc-mcp decomposition/intake/proposer/review artifact; employer-adjacent firewall-management research/run content |
| `reports/2026-06-17-fmc-mcp-run-prep-opus-review-retry.err` | 0 | (empty file) | sensitive | fmc-mcp decomposition/intake/proposer/review artifact; employer-adjacent firewall-management research/run content |
| `reports/2026-06-17-fmc-mcp-run-prep-opus-review-retry.json` | 1 | JSON model/tool result with keys [type, subtype, is_error, api_error_status, duration_ms, duration_api_ms]; result starts: '{"verdict":"REVISE","blockers":["Promotion gate under-enforces the stated goal. The goal promises changes that \'preserve' | sensitive | fmc-mcp decomposition/intake/proposer/review artifact; employer-adjacent firewall-management research/run content |
| `reports/2026-06-17-fmc-mcp-run-prep-opus-review.err` | 0 | (empty file) | sensitive | fmc-mcp decomposition/intake/proposer/review artifact; employer-adjacent firewall-management research/run content |
| `reports/2026-06-17-fmc-mcp-run-prep-opus-review.json` | 1 | JSON artifact with keys [type, subtype, duration_ms, duration_api_ms, is_error, num_turns] | sensitive | fmc-mcp decomposition/intake/proposer/review artifact; employer-adjacent firewall-management research/run content |
| `reports/2026-06-17-fmc-mcp-run-prep-review-prompt.md` | 19 | You are independently reviewing a Build Arena run-prep report before a bounded live run against fmc-mcp. | sensitive | fmc-mcp decomposition/intake/proposer/review artifact; employer-adjacent firewall-management research/run content |
| `reports/2026-06-17-fmc-mcp-run-prep.md` | 168 | # fmc-mcp Build Arena run prep — 2026-06-17 | sensitive | fmc-mcp decomposition/intake/proposer/review artifact; employer-adjacent firewall-management research/run content |
| `reports/2026-06-17-fmc-mcp-schema-fix-opus-plan-prompt.md` | 124 | You are Opus. Draw up a concrete implementation plan to fix a Build Arena live Project Model decomposer schema/gate issue, then stop. Do not use tools. Return J | sensitive | fmc-mcp decomposition/intake/proposer/review artifact; employer-adjacent firewall-management research/run content |
| `reports/2026-06-17-fmc-mcp-schema-fix-opus-plan-retry.err` | 0 | (empty file) | sensitive | fmc-mcp decomposition/intake/proposer/review artifact; employer-adjacent firewall-management research/run content |
| `reports/2026-06-17-fmc-mcp-schema-fix-opus-plan-retry.json` | 1 | JSON model/tool result with keys [type, subtype, is_error, api_error_status, duration_ms, duration_api_ms]; result starts: '{' | sensitive | fmc-mcp decomposition/intake/proposer/review artifact; employer-adjacent firewall-management research/run content |
| `reports/2026-06-17-fmc-mcp-schema-fix-opus-plan.err` | 0 | (empty file) | sensitive | fmc-mcp decomposition/intake/proposer/review artifact; employer-adjacent firewall-management research/run content |
| `reports/2026-06-17-fmc-mcp-schema-fix-opus-plan.json` | 1 | JSON artifact with keys [type, subtype, duration_ms, duration_api_ms, is_error, num_turns] | sensitive | fmc-mcp decomposition/intake/proposer/review artifact; employer-adjacent firewall-management research/run content |
| `reports/2026-06-17-fmc-mcp-schema-fix-opus-review-packet.md` | 356 | # Opus implementation review packet — fmc-mcp schema fix | sensitive | fmc-mcp decomposition/intake/proposer/review artifact; employer-adjacent firewall-management research/run content |
| `reports/2026-06-17-fmc-mcp-schema-fix-opus-review-retry.err` | 0 | (empty file) | sensitive | fmc-mcp decomposition/intake/proposer/review artifact; employer-adjacent firewall-management research/run content |
| `reports/2026-06-17-fmc-mcp-schema-fix-opus-review-retry.json` | 1 | JSON model/tool result with keys [type, subtype, is_error, api_error_status, duration_ms, duration_api_ms]; result starts: '{' | sensitive | fmc-mcp decomposition/intake/proposer/review artifact; employer-adjacent firewall-management research/run content |
| `reports/2026-06-17-fmc-mcp-schema-fix-opus-review.err` | 0 | (empty file) | sensitive | fmc-mcp decomposition/intake/proposer/review artifact; employer-adjacent firewall-management research/run content |
| `reports/2026-06-17-fmc-mcp-schema-fix-opus-review.json` | 1 | JSON artifact with keys [type, subtype, duration_ms, duration_api_ms, is_error, num_turns] | sensitive | fmc-mcp decomposition/intake/proposer/review artifact; employer-adjacent firewall-management research/run content |
| `reports/2026-06-17-fmc-mcp-schema-fix-rerun-comparison.json` | 747 | JSON artifact with keys [new_high_violation_count, new_violations, old_high_violation_count, removed_violations, runs, schema_issue_resolved] | sensitive | fmc-mcp decomposition/intake/proposer/review artifact; employer-adjacent firewall-management research/run content |
| `reports/2026-06-17-fmc-mcp-schema-fix-rerun-report.md` | 251 | # fmc-mcp Grok 4.3 high-reasoning schema fix and rerun — 2026-06-17 | sensitive | fmc-mcp decomposition/intake/proposer/review artifact; employer-adjacent firewall-management research/run content |
| `reports/2026-06-17-model-candidate-research-raw.json` | 4875 | JSON artifact with keys [hf_searches, openrouter_count, openrouter_selected] | review | raw patch/report/review/run artifact or model research output; no public-tree need found |
| `reports/2026-06-18-fmc-mcp-advisory-proposer-opus-inspection-prompt.md` | 80 | # Opus inspection request: Build Arena proposer actionability for advisory architecture/verification findings | sensitive | fmc-mcp decomposition/intake/proposer/review artifact; employer-adjacent firewall-management research/run content |
| `reports/2026-06-18-fmc-mcp-advisory-proposer-opus-inspection.err` | 0 | (empty file) | sensitive | fmc-mcp decomposition/intake/proposer/review artifact; employer-adjacent firewall-management research/run content |
| `reports/2026-06-18-fmc-mcp-advisory-proposer-opus-inspection.json` | 1 | JSON model/tool result with keys [type, subtype, is_error, api_error_status, duration_ms, duration_api_ms]; result starts: '```json' | sensitive | fmc-mcp decomposition/intake/proposer/review artifact; employer-adjacent firewall-management research/run content |
| `reports/2026-06-18-fmc-mcp-proposer-run-and-advisory-actionability-opus-review.err` | 0 | (empty file) | sensitive | fmc-mcp decomposition/intake/proposer/review artifact; employer-adjacent firewall-management research/run content |
| `reports/2026-06-18-fmc-mcp-proposer-run-and-advisory-actionability-opus-review.json` | 1 | JSON model/tool result with keys [type, subtype, is_error, api_error_status, duration_ms, duration_api_ms]; result starts: '{' | sensitive | fmc-mcp decomposition/intake/proposer/review artifact; employer-adjacent firewall-management research/run content |
| `reports/2026-06-18-fmc-mcp-proposer-run-and-advisory-actionability-review-prompt.md` | 508 | # Review request: fmc-mcp proposer/advisory actionability report | sensitive | fmc-mcp decomposition/intake/proposer/review artifact; employer-adjacent firewall-management research/run content |
| `reports/2026-06-21-elenchus-core-proposal-run-opus-review.err` | 0 | (empty file) | review | raw patch/report/review/run artifact or model research output; no public-tree need found |
| `reports/2026-06-21-elenchus-core-proposal-run-opus-review.json` | 1 | JSON model/tool result with keys [type, subtype, is_error, api_error_status, duration_ms, duration_api_ms]; result starts: '{' | review | raw patch/report/review/run artifact or model research output; no public-tree need found |
| `reports/2026-06-21-elenchus-core-proposal-run-report.md` | 132 | # elenchus-core proposal_run monitored run — 2026-06-21 | review | raw patch/report/review/run artifact or model research output; no public-tree need found |
| `reports/2026-06-21-elenchus-core-proposal-run-review-prompt.md` | 152 | You are an independent reviewer for Leon. Do not use tools. Read the embedded report and evidence excerpts only. | review | raw patch/report/review/run artifact or model research output; no public-tree need found |
| `reports/2026-06-23-dream-proposer-tier3-opus-review-prompt.md` | 23 | You are an independent reviewer for Build Arena. Review the attached packet for the tier-3 advisory dream proposer implementation. | review | raw patch/report/review/run artifact or model research output; no public-tree need found |
| `reports/2026-06-23-dream-proposer-tier3-opus-review.err` | 0 | (empty file) | review | raw patch/report/review/run artifact or model research output; no public-tree need found |
| `reports/2026-06-23-dream-proposer-tier3-opus-review.json` | 1 | JSON model/tool result with keys [type, subtype, is_error, api_error_status, duration_ms, duration_api_ms]; result starts: 'Looking at this packet, my job is to break the core safety property, not nitpick style. Let me reason through each gate.' | review | raw patch/report/review/run artifact or model research output; no public-tree need found |
| `reports/2026-06-23-dream-proposer-tier3-review-packet.md` | 3711 | # Dream Proposer Tier 3 Review Packet | review | raw patch/report/review/run artifact or model research output; no public-tree need found |

## Secret / credential scan

Command shape used:

```text
candidate set x grep/Python regex for:
- provider-key prefixes: OpenAI-style and xAI-style key prefixes
- AKIA AWS access-key shape
- private-key PEM blocks
- api_key / api-key / token / secret / password / bearer words
- targeted follow-up: provider-key-prefix-shaped false positives, including the risk/client/responsibilities id family
```

Pattern hit count: 81 (openai_or_provider_key_prefix=6; secret_words=75). Values below are redacted where a key-shaped substring appears.


| kind | file:line | redacted excerpt |
|---|---|---|
| secret_words | `docs/specs/2026-06-19-pairwise-proposal-reranker-design.md:139` | Also require executable availability for the first token with `shutil.which`, except for `test` which may be `/usr/bin/test`. |
| secret_words | `docs/specs/2026-06-19-pairwise-proposal-reranker-design.md:169` | No-op execution can be added later only with per-family expected-failure signatures (exit code plus matched stdout/stderr token). Without those signatures, a non-zero baseline run is ambiguous and must not be used as proof of binding verification. |
| secret_words | `docs/status/2026-06-17-fmc-mcp-schema-fix-status.md:18` | - Secret-shaped scan of new report/review/run artifacts: clean. |
| secret_words | `docs/verification/2026-06-19-pairwise-proposal-reranker-opus-rereview.json:1` | {"type":"result","subtype":"success","is_error":false,"api_error_status":null,"duration_ms":44087,"duration_api_ms":43880,"ttft_ms":2833,"ttft_stream_ms":1898,"time_to_request_ms":89,"num_turns":4,"result":"All six required patches are addressed, and I verifie |
| secret_words | `docs/verification/2026-06-19-pairwise-proposal-reranker-opus-review.json:1` | {"type":"result","subtype":"success","is_error":false,"api_error_status":null,"duration_ms":155291,"duration_api_ms":154987,"ttft_ms":5307,"ttft_stream_ms":2647,"time_to_request_ms":96,"num_turns":15,"result":"I have enough to review. Key cross-checks against  |
| secret_words | `proposal-run-and-emit.patch:17` | +  --live-api-key-env XAI_API_KEY \ |
| secret_words | `proposal-run-and-emit.patch:21` | +`run` accepts a local directory (used in place) or a git URL (shallow-cloned into a scratch workdir). Decomposition defaults to deterministic fixture mode; pass `--decompose-live` to use the live AI decomposer. The pairwise re-ranker's judge is an unavoidable |
| secret_words | `proposal-run-and-emit.patch:405` | +            f"{exc} (set the key, or choose another env var with --live-api-key-env)", |
| secret_words | `proposal-run-and-emit.patch:489` | +        args += ["--live-api-key-env", config.live_api_key_env] |
| secret_words | `proposal-run-and-emit.patch:607` | +        "--live-api-key-env", default="XAI_API_KEY", help="env var holding the provider key" |
| secret_words | `proposal-run-and-emit.patch:690` | +- any new auth surface, model routing, or token-in-config. |
| secret_words | `proposal-run-and-emit.patch:705` | +- The re-ranker's judge is an unavoidable live model call. Provider selection is threaded to it via the `BUILD_ARENA_LLM_*` contract — `--live-model` → `BUILD_ARENA_LLM_MODEL`, `--live-api-key-env` → `BUILD_ARENA_LLM_API_KEY_ENV`, `--live-base-url` → `BUILD_A |
| secret_words | `proposal-run-and-emit.patch:715` | +- **Preflight.** `--live-model` is required (the judge always spends), and the key named by `--live-api-key-env` must resolve, or the run fails closed with exit `3` before doing any work — consistent with the rest of the repo refusing live attempts without an |
| secret_words | `proposal-run-and-emit.patch:1063` | +        token = args[i] |
| secret_words | `proposal-run-and-emit.patch:1064` | +        if token.startswith("--"): |
| secret_words | `proposal-run-and-emit.patch:1066` | +                out[token] = args[i + 1] |
| secret_words | `proposal-run-and-emit.patch:1069` | +                out[token] = "true" |
| openai_or_provider_key_prefix | `proposal-run-and-emit.patch:1187` | +    monkeypatch.setenv("XAI_API_KEY", "sk-<redacted>") |
| secret_words | `reports/2026-06-17-build-arena-decomposer-model-candidates-opus-review-retry.json:1` | {"type":"result","subtype":"success","is_error":false,"api_error_status":null,"duration_ms":77216,"duration_api_ms":77033,"ttft_ms":45280,"ttft_stream_ms":2676,"time_to_request_ms":82,"num_turns":1,"result":"{\n  \"verdict\": \"ACCEPT_WITH_CORRECTIONS\",\n  \" |
| secret_words | `reports/2026-06-17-build-arena-decomposer-model-candidates.md:70` | - 1,048,576 token context window. |
| secret_words | `reports/2026-06-17-build-arena-decomposer-model-candidates.md:337` | One call each, same fmc-mcp prompt, temperature 0 where applicable, explicit reasoning settings where supported, no intake. Do not use the same token cap for every model if the model spends hidden reasoning tokens; the Grok 4.3 high-reasoning run used 7,897 re |
| secret_words | `reports/2026-06-17-build-arena-decomposer-model-candidates.md:383` | --live-api-key-env OPENROUTER_API_KEY \ |
| secret_words | `reports/2026-06-17-build-arena-decomposer-model-shortlist.json:29` | "description_excerpt": "DeepSeek V4 Pro is a large-scale Mixture-of-Experts model from DeepSeek with 1.6T total parameters and 49B activated parameters, supporting a 1M-token context window. It is designed for advanced reasoning, coding,...", |
| secret_words | `reports/2026-06-17-build-arena-decomposer-model-shortlist.json:41` | "description_excerpt": "DeepSeek V4 Flash is an efficiency-optimized Mixture-of-Experts model from DeepSeek with 284B total parameters and 13B activated parameters, supporting a 1M-token context window. It is designed for fast inference and...", |
| secret_words | `reports/2026-06-17-build-arena-decomposer-model-shortlist.json:89` | "description_excerpt": "Gemini 3.1 Pro Preview is Google\u2019s frontier reasoning model, delivering enhanced software engineering performance, improved agentic reliability, and more efficient token usage across complex workflows. Building on the mu", |
| secret_words | `reports/2026-06-17-build-arena-decomposer-model-shortlist.json:101` | "description_excerpt": "Claude Opus 4.8 is Anthropic's most capable generally available model in the Opus family. It supports text, image, and file inputs with text output, with reasoning support and a 1M-token...", |
| secret_words | `reports/2026-06-17-build-arena-decomposer-model-shortlist.json:113` | "description_excerpt": "GLM 5.2 is a large-scale reasoning model from Z.ai. It supports text input and output with a 1M-token context window, and is suited for long-horizon agent workflows, project-level software engineering,...", |
| secret_words | `reports/2026-06-17-build-arena-decomposer-model-shortlist.json:137` | "description_excerpt": "Granite 4.1 8B is a dense, decoder-only 8-billion-parameter language model from IBM, part of the Granite 4.1 family. It supports a 131K-token context window and is designed for enterprise tasks...", |
| secret_words | `reports/2026-06-17-fmc-mcp-decomposition-expected-opus-prompt.md:17` | [sensitive candidate: snippet omitted] |
| secret_words | `reports/2026-06-17-fmc-mcp-decomposition-expected-opus-retry.json:1` | [sensitive candidate: snippet omitted] |
| secret_words | `reports/2026-06-17-fmc-mcp-decomposition-real-opus-review-retry.json:1` | [sensitive candidate: snippet omitted] |
| secret_words | `reports/2026-06-17-fmc-mcp-decomposition-real-summary.json:266` | [sensitive candidate: snippet omitted] |
| openai_or_provider_key_prefix | `reports/2026-06-17-fmc-mcp-decomposition-real-summary.json:305` | [sensitive candidate: snippet omitted] |
| secret_words | `reports/2026-06-17-fmc-mcp-decomposition-real-summary.json:349` | [sensitive candidate: snippet omitted] |
| secret_words | `reports/2026-06-17-fmc-mcp-decomposition-real-summary.json:355` | [sensitive candidate: snippet omitted] |
| secret_words | `reports/2026-06-17-fmc-mcp-decomposition-real-summary.json:357` | [sensitive candidate: snippet omitted] |
| secret_words | `reports/2026-06-17-fmc-mcp-decomposition-result.md:33` | [sensitive candidate: snippet omitted] |
| secret_words | `reports/2026-06-17-fmc-mcp-decomposition-result.md:127` | [sensitive candidate: snippet omitted] |
| secret_words | `reports/2026-06-17-fmc-mcp-decomposition-result.md:142` | [sensitive candidate: snippet omitted] |
| secret_words | `reports/2026-06-17-fmc-mcp-grok43-high-vs-nonreasoning-comparison.json:278` | [sensitive candidate: snippet omitted] |
| openai_or_provider_key_prefix | `reports/2026-06-17-fmc-mcp-grok43-high-vs-nonreasoning-comparison.json:315` | [sensitive candidate: snippet omitted] |
| secret_words | `reports/2026-06-17-fmc-mcp-grok43-high-vs-nonreasoning-comparison.json:359` | [sensitive candidate: snippet omitted] |
| secret_words | `reports/2026-06-17-fmc-mcp-grok43-high-vs-nonreasoning-comparison.json:365` | [sensitive candidate: snippet omitted] |
| secret_words | `reports/2026-06-17-fmc-mcp-grok43-high-vs-nonreasoning-comparison.json:367` | [sensitive candidate: snippet omitted] |
| secret_words | `reports/2026-06-17-fmc-mcp-grok43-high-vs-nonreasoning-comparison.json:734` | [sensitive candidate: snippet omitted] |
| openai_or_provider_key_prefix | `reports/2026-06-17-fmc-mcp-grok43-high-vs-nonreasoning-comparison.json:773` | [sensitive candidate: snippet omitted] |
| secret_words | `reports/2026-06-17-fmc-mcp-grok43-high-vs-nonreasoning-comparison.json:817` | [sensitive candidate: snippet omitted] |
| secret_words | `reports/2026-06-17-fmc-mcp-grok43-high-vs-nonreasoning-comparison.json:823` | [sensitive candidate: snippet omitted] |
| secret_words | `reports/2026-06-17-fmc-mcp-grok43-high-vs-nonreasoning-comparison.json:825` | [sensitive candidate: snippet omitted] |
| secret_words | `reports/2026-06-17-fmc-mcp-grok43-high-vs-nonreasoning-opus-brief.json:274` | [sensitive candidate: snippet omitted] |
| openai_or_provider_key_prefix | `reports/2026-06-17-fmc-mcp-grok43-high-vs-nonreasoning-opus-brief.json:311` | [sensitive candidate: snippet omitted] |
| secret_words | `reports/2026-06-17-fmc-mcp-grok43-high-vs-nonreasoning-opus-brief.json:620` | [sensitive candidate: snippet omitted] |
| openai_or_provider_key_prefix | `reports/2026-06-17-fmc-mcp-grok43-high-vs-nonreasoning-opus-brief.json:659` | [sensitive candidate: snippet omitted] |
| secret_words | `reports/2026-06-17-fmc-mcp-grok43-high-vs-nonreasoning-opus-review.json:1` | [sensitive candidate: snippet omitted] |
| secret_words | `reports/2026-06-17-fmc-mcp-grok43-high-vs-nonreasoning-opus-review.normalized.json:29` | "Cheaper and lower token cost.", |
| secret_words | `reports/2026-06-17-fmc-mcp-run-prep.md:116` | --live-api-key-env XAI_API_KEY \ |
| secret_words | `reports/2026-06-17-model-candidate-research-raw.json:1788` | "description": "GLM 5.2 is a large-scale reasoning model from Z.ai. It supports text input and output with a 1M-token context window, and is suited for long-horizon agent workflows, project-level software engineering,...", |
| secret_words | `reports/2026-06-17-model-candidate-research-raw.json:1956` | "description": "Claude Opus 4.8 is Anthropic's most capable generally available model in the Opus family. It supports text, image, and file inputs with text output, with reasoning support and a 1M-token...", |
| secret_words | `reports/2026-06-17-model-candidate-research-raw.json:2120` | "description": "Granite 4.1 8B is a dense, decoder-only 8-billion-parameter language model from IBM, part of the Granite 4.1 family. It supports a 131K-token context window and is designed for enterprise tasks...", |
| secret_words | `reports/2026-06-17-model-candidate-research-raw.json:2316` | "description": "DeepSeek V4 Pro is a large-scale Mixture-of-Experts model from DeepSeek with 1.6T total parameters and 49B activated parameters, supporting a 1M-token context window. It is designed for advanced reasoning, coding,...", |
| secret_words | `reports/2026-06-17-model-candidate-research-raw.json:2348` | "description": "DeepSeek V4 Flash is an efficiency-optimized Mixture-of-Experts model from DeepSeek with 284B total parameters and 13B activated parameters, supporting a 1M-token context window. It is designed for fast inference and...", |
| secret_words | `reports/2026-06-17-model-candidate-research-raw.json:2673` | "description": "GPT-5.4 is OpenAI\u2019s latest frontier model, unifying the Codex and GPT lines into a single system. It features a 1M+ token context window (922K input, 128K output) with support for...", |
| secret_words | `reports/2026-06-17-model-candidate-research-raw.json:2815` | "description": "Gemini 3.1 Pro Preview is Google\u2019s frontier reasoning model, delivering enhanced software engineering performance, improved agentic reliability, and more efficient token usage across complex workflows. Building on the multimodal foundation |
| secret_words | `reports/2026-06-17-model-candidate-research-raw.json:3662` | "description": "Gemini 2.5 Flash-Lite is a lightweight reasoning model in the Gemini 2.5 family, optimized for ultra-low latency and cost efficiency. It offers improved throughput, faster token generation, and better performance...", |
| secret_words | `reports/2026-06-17-model-candidate-research-raw.json:4150` | "description": "Gemini 2.5 Flash-Lite is a lightweight reasoning model in the Gemini 2.5 family, optimized for ultra-low latency and cost efficiency. It offers improved throughput, faster token generation, and better performance...", |
| secret_words | `reports/2026-06-18-fmc-mcp-proposer-run-and-advisory-actionability-review-prompt.md:54` | --api-key-env XAI_API_KEY \ |
| secret_words | `reports/2026-06-21-elenchus-core-proposal-run-report.md:41` | - Secret-safe load check: sourcing `.env` made `XAI_API_KEY` present. |
| secret_words | `reports/2026-06-21-elenchus-core-proposal-run-report.md:53` | uv run python -m arena.proposal_run run https://github.com/leonbreukelman/elenchus-core --decompose-live --live-model grok-4.3 --live-api-key-env XAI_API_KEY --workdir <repo>/.arena/runs/elenchus-core-proposal-run-20260621T225718Z/workdir --keep-workdir --outp |
| secret_words | `reports/2026-06-21-elenchus-core-proposal-run-review-prompt.md:61` | - Secret-safe load check: sourcing `.env` made `XAI_API_KEY` present. |
| secret_words | `reports/2026-06-21-elenchus-core-proposal-run-review-prompt.md:73` | uv run python -m arena.proposal_run run https://github.com/leonbreukelman/elenchus-core --decompose-live --live-model grok-4.3 --live-api-key-env XAI_API_KEY --workdir <repo>/.arena/runs/elenchus-core-proposal-run-20260621T225718Z/workdir --keep-workdir --outp |
| secret_words | `reports/2026-06-23-dream-proposer-tier3-review-packet.md:189` | +  --live-api-key-env XAI_API_KEY \ |
| secret_words | `reports/2026-06-23-dream-proposer-tier3-review-packet.md:944` | parser.add_argument("--live-api-key-env", default="XAI_API_KEY") |
| secret_words | `reports/2026-06-23-dream-proposer-tier3-review-packet.md:1259` | parser.add_argument("--live-api-key-env", default="XAI_API_KEY") |
| secret_words | `reports/2026-06-23-dream-proposer-tier3-review-packet.md:2027` | f"{exc} (set the key, or choose another env var with --live-api-key-env)", EXIT_USAGE |
| secret_words | `reports/2026-06-23-dream-proposer-tier3-review-packet.md:2083` | args += ["--allow-live", "--live-provider", config.live_provider, "--live-api-key-env", config.live_api_key_env] |
| secret_words | `reports/2026-06-23-dream-proposer-tier3-review-packet.md:2092` | flags = ["--live-model", str(config.live_model), "--live-provider", config.live_provider, "--live-api-key-env", config.live_api_key_env] |
| secret_words | `reports/2026-06-23-dream-proposer-tier3-review-packet.md:2264` | run_parser.add_argument("--live-api-key-env", default="XAI_API_KEY", help="env var holding the provider key") |
| secret_words | `reports/2026-06-23-dream-proposer-tier3-review-packet.md:3119` | token = args[i] |
| secret_words | `reports/2026-06-23-dream-proposer-tier3-review-packet.md:3120` | if token.startswith("--"): |
| secret_words | `reports/2026-06-23-dream-proposer-tier3-review-packet.md:3122` | out[token] = args[i + 1] |
| secret_words | `reports/2026-06-23-dream-proposer-tier3-review-packet.md:3125` | out[token] = "true" |

```text
$ xargs ... grep -nE "provider-key-prefix-shaped false-positive patterns"
reports/2026-06-17-fmc-mcp-decomposition-real-summary.json:305:      "id": "backlog.document-or-split-high_risk_[redacted]",
reports/2026-06-17-fmc-mcp-grok43-high-vs-nonreasoning-comparison.json:315:        "id": "backlog.document-or-split-high_risk_[redacted]"
```

Triage: no live credential value was found. `XAI_API_KEY`, `OPENROUTER_API_KEY`, `api_key_env`, and `token` are env-var names, CLI flag names, or ordinary prose/code identifiers. The provider-key-prefix-shaped hit inside the `risk client responsibilities` id family is a substring false positive, not a secret. The one dummy `monkeypatch.setenv` key in `proposal-run-and-emit.patch` is test data in an unapplied patch artifact, still review-rated clutter.

## Employer/IP-boundary scan

Command shape used:

```text
candidate set x grep/Python regex for:
- fmc/firewall/vendor markers, rule-set/policy markers, object/networkaddresses, fmc_platform, fmc_config
- /home/<user> absolute paths
- private RFC1918 IPv4 addresses
- customer/internal/hostname/employer words
```

Hit count: 329. To avoid republishing sensitive operational content, this doc records every `file:line` and category, but intentionally omits raw sensitive snippets. Re-open the referenced path/line in the repository history if Leon authorizes deeper handling.


| kind | path | hit lines |
|---|---|---|
| fmc_or_firewall | `docs/agent-wiki/index.md` | 15 |
| fmc_or_firewall | `docs/status/2026-06-17-fmc-mcp-schema-fix-status.md` | 1, 21, 22, 26, 30, 31, 36, 37, 38, 39 |
| fmc_or_firewall | `docs/status/INDEX.md` | 17, 21 |
| customer_internal_words | `docs/verification/2026-06-19-pairwise-proposal-reranker-opus-rereview.json` | 1 |
| customer_internal_words | `proposal-run-and-emit.patch` | 33, 50, 70, 714, 753, 781 |
| fmc_or_firewall | `reports/2026-06-17-build-arena-decomposer-model-candidates-opus-prompt.md` | 17 |
| fmc_or_firewall | `reports/2026-06-17-build-arena-decomposer-model-candidates-opus-review.json` | 1 |
| fmc_or_firewall | `reports/2026-06-17-build-arena-decomposer-model-candidates.md` | 47, 136, 287, 315, 337, 354, 373, 375, 376 |
| fmc_or_firewall | `reports/2026-06-17-fmc-mcp-decomposition-expected-opus-prompt.md` | 1, 6, 7, 9, 12, 13, 16 |
| fmc_or_firewall | `reports/2026-06-17-fmc-mcp-decomposition-expected-opus-retry.json` | 1 |
| fmc_or_firewall | `reports/2026-06-17-fmc-mcp-decomposition-real-opus-review-prompt.md` | 1, 12, 15, 18 |
| fmc_or_firewall | `reports/2026-06-17-fmc-mcp-decomposition-real-opus-review-retry.json` | 1 |
| fmc_or_firewall | `reports/2026-06-17-fmc-mcp-decomposition-real-opus-review.json` | 1 |
| fmc_or_firewall | `reports/2026-06-17-fmc-mcp-decomposition-real-summary.json` | 3, 4, 5, 6, 7, 266, 325, 343, 349, 439, 449 |
| fmc_or_firewall | `reports/2026-06-17-fmc-mcp-decomposition-result.md` | 1, 23, 24, 25, 26, 41, 42, 43, 44, 45, 46, 47, 48, 49, 75, 126 |
| fmc_or_firewall | `reports/2026-06-17-fmc-mcp-grok43-high-vs-nonreasoning-comparison.json` | 47, 48, 49, 50, 51, 278, 335, 353, 359, 445, 463, 467, 468, 469, 470, 472, 479, 480, 481, 482, 483, 734, 793, 811, 817, 915, 934, 938, 939, 940, 941, 943 |
| fmc_or_firewall | `reports/2026-06-17-fmc-mcp-grok43-high-vs-nonreasoning-opus-brief.json` | 3, 5, 6, 7, 8, 9, 12, 13, 14, 15, 16, 274, 620 |
| fmc_or_firewall | `reports/2026-06-17-fmc-mcp-grok43-high-vs-nonreasoning-opus-prompt.md` | 1, 13, 14 |
| fmc_or_firewall | `reports/2026-06-17-fmc-mcp-grok43-high-vs-nonreasoning-report.md` | 1, 36, 40, 41, 42, 43, 44, 45, 46, 47, 104 |
| fmc_or_firewall | `reports/2026-06-17-fmc-mcp-intake-expected-vs-actual-opus-review-prompt.md` | 24, 78, 80, 86, 88, 103, 104, 105, 106, 107, 108 |
| fmc_or_firewall | `reports/2026-06-17-fmc-mcp-intake-expected-vs-actual.md` | 1, 55, 57, 63, 65, 80, 81, 82, 83, 84, 85 |
| fmc_or_firewall | `reports/2026-06-17-fmc-mcp-production-intake-result.md` | 1, 7, 9, 17, 18, 19, 20, 21, 27, 28, 48, 59, 60, 62, 63, 85, 86, 87 |
| fmc_or_firewall | `reports/2026-06-17-fmc-mcp-run-prep-opus-review-retry.json` | 1 |
| customer_internal_words | `reports/2026-06-17-fmc-mcp-run-prep-review-prompt.md` | 7 |
| fmc_or_firewall | `reports/2026-06-17-fmc-mcp-run-prep-review-prompt.md` | 1, 4 |
| fmc_or_firewall | `reports/2026-06-17-fmc-mcp-run-prep.md` | 1, 5, 10, 34, 36, 42, 43, 44, 45, 72, 73, 74, 83, 98, 101, 103, 106, 128, 136, 157, 165, 166, 168 |
| fmc_or_firewall | `reports/2026-06-17-fmc-mcp-schema-fix-opus-plan-prompt.md` | 5, 10 |
| fmc_or_firewall | `reports/2026-06-17-fmc-mcp-schema-fix-opus-plan-retry.json` | 1 |
| fmc_or_firewall | `reports/2026-06-17-fmc-mcp-schema-fix-opus-review-packet.md` | 1, 10, 25, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 356 |
| fmc_or_firewall | `reports/2026-06-17-fmc-mcp-schema-fix-opus-review-retry.json` | 1 |
| fmc_or_firewall | `reports/2026-06-17-fmc-mcp-schema-fix-rerun-comparison.json` | 274, 508, 723 |
| fmc_or_firewall | `reports/2026-06-17-fmc-mcp-schema-fix-rerun-report.md` | 1, 15, 21, 53, 56, 142, 145, 166, 169, 172, 175, 178, 193, 205 |
| customer_internal_words | `reports/2026-06-17-model-candidate-research-raw.json` | 1613 |
| fmc_or_firewall | `reports/2026-06-18-fmc-mcp-advisory-proposer-opus-inspection-prompt.md` | 24, 26, 27, 36 |
| fmc_or_firewall | `reports/2026-06-18-fmc-mcp-advisory-proposer-opus-inspection.json` | 1 |
| customer_internal_words | `reports/2026-06-18-fmc-mcp-proposer-run-and-advisory-actionability-review-prompt.md` | 228 |
| fmc_or_firewall | `reports/2026-06-18-fmc-mcp-proposer-run-and-advisory-actionability-review-prompt.md` | 1, 28, 50, 51, 56, 61, 63, 64, 108, 109, 138, 282 |
| fmc_or_firewall | `reports/2026-06-23-dream-proposer-tier3-review-packet.md` | 46, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 108, 109, 110, 111, 112, 113, 204, 226 |


Representative employer-adjacent evidence is intentionally restricted to the grouped `file:line` table above. Raw snippets are withheld here because these deliverables are intended for a public repository and should not concentrate the sensitive operational content they identify.

## Sensitive escalation section

Sensitive findings are referenced by path only. No secret value is pasted here.

- `docs/agent-wiki/index.md`
- `docs/status/2026-06-17-fmc-mcp-schema-fix-status.md`
- `docs/status/INDEX.md`
- `reports/2026-06-17-fmc-mcp-decomposition-expected-opus-prompt.md`
- `reports/2026-06-17-fmc-mcp-decomposition-expected-opus-retry.err`
- `reports/2026-06-17-fmc-mcp-decomposition-expected-opus-retry.json`
- `reports/2026-06-17-fmc-mcp-decomposition-expected-opus.err`
- `reports/2026-06-17-fmc-mcp-decomposition-expected-opus.json`
- `reports/2026-06-17-fmc-mcp-decomposition-real-opus-review-prompt.md`
- `reports/2026-06-17-fmc-mcp-decomposition-real-opus-review-retry.err`
- `reports/2026-06-17-fmc-mcp-decomposition-real-opus-review-retry.json`
- `reports/2026-06-17-fmc-mcp-decomposition-real-opus-review.err`
- `reports/2026-06-17-fmc-mcp-decomposition-real-opus-review.json`
- `reports/2026-06-17-fmc-mcp-decomposition-real-summary.json`
- `reports/2026-06-17-fmc-mcp-decomposition-result.md`
- `reports/2026-06-17-fmc-mcp-grok43-high-reasoning-preflight.json`
- `reports/2026-06-17-fmc-mcp-grok43-high-vs-nonreasoning-comparison.json`
- `reports/2026-06-17-fmc-mcp-grok43-high-vs-nonreasoning-opus-brief.json`
- `reports/2026-06-17-fmc-mcp-grok43-high-vs-nonreasoning-opus-prompt.md`
- `reports/2026-06-17-fmc-mcp-grok43-high-vs-nonreasoning-opus-review.err`
- `reports/2026-06-17-fmc-mcp-grok43-high-vs-nonreasoning-opus-review.json`
- `reports/2026-06-17-fmc-mcp-grok43-high-vs-nonreasoning-opus-review.normalized.json`
- `reports/2026-06-17-fmc-mcp-grok43-high-vs-nonreasoning-report.md`
- `reports/2026-06-17-fmc-mcp-intake-expected-vs-actual-opus-review-prompt.md`
- `reports/2026-06-17-fmc-mcp-intake-expected-vs-actual-opus-review.err`
- `reports/2026-06-17-fmc-mcp-intake-expected-vs-actual-opus-review.json`
- `reports/2026-06-17-fmc-mcp-intake-expected-vs-actual.md`
- `reports/2026-06-17-fmc-mcp-production-intake-result.md`
- `reports/2026-06-17-fmc-mcp-run-prep-opus-rereview.err`
- `reports/2026-06-17-fmc-mcp-run-prep-opus-rereview.json`
- `reports/2026-06-17-fmc-mcp-run-prep-opus-review-retry.err`
- `reports/2026-06-17-fmc-mcp-run-prep-opus-review-retry.json`
- `reports/2026-06-17-fmc-mcp-run-prep-opus-review.err`
- `reports/2026-06-17-fmc-mcp-run-prep-opus-review.json`
- `reports/2026-06-17-fmc-mcp-run-prep-review-prompt.md`
- `reports/2026-06-17-fmc-mcp-run-prep.md`
- `reports/2026-06-17-fmc-mcp-schema-fix-opus-plan-prompt.md`
- `reports/2026-06-17-fmc-mcp-schema-fix-opus-plan-retry.err`
- `reports/2026-06-17-fmc-mcp-schema-fix-opus-plan-retry.json`
- `reports/2026-06-17-fmc-mcp-schema-fix-opus-plan.err`
- `reports/2026-06-17-fmc-mcp-schema-fix-opus-plan.json`
- `reports/2026-06-17-fmc-mcp-schema-fix-opus-review-packet.md`
- `reports/2026-06-17-fmc-mcp-schema-fix-opus-review-retry.err`
- `reports/2026-06-17-fmc-mcp-schema-fix-opus-review-retry.json`
- `reports/2026-06-17-fmc-mcp-schema-fix-opus-review.err`
- `reports/2026-06-17-fmc-mcp-schema-fix-opus-review.json`
- `reports/2026-06-17-fmc-mcp-schema-fix-rerun-comparison.json`
- `reports/2026-06-17-fmc-mcp-schema-fix-rerun-report.md`
- `reports/2026-06-18-fmc-mcp-advisory-proposer-opus-inspection-prompt.md`
- `reports/2026-06-18-fmc-mcp-advisory-proposer-opus-inspection.err`
- `reports/2026-06-18-fmc-mcp-advisory-proposer-opus-inspection.json`
- `reports/2026-06-18-fmc-mcp-proposer-run-and-advisory-actionability-opus-review.err`
- `reports/2026-06-18-fmc-mcp-proposer-run-and-advisory-actionability-opus-review.json`
- `reports/2026-06-18-fmc-mcp-proposer-run-and-advisory-actionability-review-prompt.md`

Introduction/exposure evidence:

| path | introduced / exposure commit evidence |
|---|---|
| `docs/agent-wiki/index.md` | 8a39d26 chore: sync repo housekeeping and onboarding work (`git log -S 2026-06-15-fmc-mcp-production-pass-lessons -- docs/agent-wiki/index.md`) |
| `docs/status/2026-06-17-fmc-mcp-schema-fix-status.md` | b2aa47f1cfe85206bab9960beebf115cf5d44d74 2026-06-24 19:33:04 -0500 feat: publish dream proposer package |
| `docs/status/INDEX.md` | b2aa47f feat: publish dream proposer package (`git log -S 2026-06-17-fmc-mcp-schema-fix-status -- docs/status/INDEX.md`) |
| `reports/2026-06-17-fmc-mcp-decomposition-expected-opus-prompt.md` | b2aa47f1cfe85206bab9960beebf115cf5d44d74 2026-06-24 19:33:04 -0500 feat: publish dream proposer package |
| `reports/2026-06-17-fmc-mcp-decomposition-expected-opus-retry.err` | b2aa47f1cfe85206bab9960beebf115cf5d44d74 2026-06-24 19:33:04 -0500 feat: publish dream proposer package |
| `reports/2026-06-17-fmc-mcp-decomposition-expected-opus-retry.json` | b2aa47f1cfe85206bab9960beebf115cf5d44d74 2026-06-24 19:33:04 -0500 feat: publish dream proposer package |
| `reports/2026-06-17-fmc-mcp-decomposition-expected-opus.err` | b2aa47f1cfe85206bab9960beebf115cf5d44d74 2026-06-24 19:33:04 -0500 feat: publish dream proposer package |
| `reports/2026-06-17-fmc-mcp-decomposition-expected-opus.json` | b2aa47f1cfe85206bab9960beebf115cf5d44d74 2026-06-24 19:33:04 -0500 feat: publish dream proposer package |
| `reports/2026-06-17-fmc-mcp-decomposition-real-opus-review-prompt.md` | b2aa47f1cfe85206bab9960beebf115cf5d44d74 2026-06-24 19:33:04 -0500 feat: publish dream proposer package |
| `reports/2026-06-17-fmc-mcp-decomposition-real-opus-review-retry.err` | b2aa47f1cfe85206bab9960beebf115cf5d44d74 2026-06-24 19:33:04 -0500 feat: publish dream proposer package |
| `reports/2026-06-17-fmc-mcp-decomposition-real-opus-review-retry.json` | b2aa47f1cfe85206bab9960beebf115cf5d44d74 2026-06-24 19:33:04 -0500 feat: publish dream proposer package |
| `reports/2026-06-17-fmc-mcp-decomposition-real-opus-review.err` | b2aa47f1cfe85206bab9960beebf115cf5d44d74 2026-06-24 19:33:04 -0500 feat: publish dream proposer package |
| `reports/2026-06-17-fmc-mcp-decomposition-real-opus-review.json` | b2aa47f1cfe85206bab9960beebf115cf5d44d74 2026-06-24 19:33:04 -0500 feat: publish dream proposer package |
| `reports/2026-06-17-fmc-mcp-decomposition-real-summary.json` | b2aa47f1cfe85206bab9960beebf115cf5d44d74 2026-06-24 19:33:04 -0500 feat: publish dream proposer package |
| `reports/2026-06-17-fmc-mcp-decomposition-result.md` | b2aa47f1cfe85206bab9960beebf115cf5d44d74 2026-06-24 19:33:04 -0500 feat: publish dream proposer package |
| `reports/2026-06-17-fmc-mcp-grok43-high-reasoning-preflight.json` | b2aa47f1cfe85206bab9960beebf115cf5d44d74 2026-06-24 19:33:04 -0500 feat: publish dream proposer package |
| `reports/2026-06-17-fmc-mcp-grok43-high-vs-nonreasoning-comparison.json` | b2aa47f1cfe85206bab9960beebf115cf5d44d74 2026-06-24 19:33:04 -0500 feat: publish dream proposer package |
| `reports/2026-06-17-fmc-mcp-grok43-high-vs-nonreasoning-opus-brief.json` | b2aa47f1cfe85206bab9960beebf115cf5d44d74 2026-06-24 19:33:04 -0500 feat: publish dream proposer package |
| `reports/2026-06-17-fmc-mcp-grok43-high-vs-nonreasoning-opus-prompt.md` | b2aa47f1cfe85206bab9960beebf115cf5d44d74 2026-06-24 19:33:04 -0500 feat: publish dream proposer package |
| `reports/2026-06-17-fmc-mcp-grok43-high-vs-nonreasoning-opus-review.err` | b2aa47f1cfe85206bab9960beebf115cf5d44d74 2026-06-24 19:33:04 -0500 feat: publish dream proposer package |
| `reports/2026-06-17-fmc-mcp-grok43-high-vs-nonreasoning-opus-review.json` | b2aa47f1cfe85206bab9960beebf115cf5d44d74 2026-06-24 19:33:04 -0500 feat: publish dream proposer package |
| `reports/2026-06-17-fmc-mcp-grok43-high-vs-nonreasoning-opus-review.normalized.json` | b2aa47f1cfe85206bab9960beebf115cf5d44d74 2026-06-24 19:33:04 -0500 feat: publish dream proposer package |
| `reports/2026-06-17-fmc-mcp-grok43-high-vs-nonreasoning-report.md` | b2aa47f1cfe85206bab9960beebf115cf5d44d74 2026-06-24 19:33:04 -0500 feat: publish dream proposer package |
| `reports/2026-06-17-fmc-mcp-intake-expected-vs-actual-opus-review-prompt.md` | b2aa47f1cfe85206bab9960beebf115cf5d44d74 2026-06-24 19:33:04 -0500 feat: publish dream proposer package |
| `reports/2026-06-17-fmc-mcp-intake-expected-vs-actual-opus-review.err` | b2aa47f1cfe85206bab9960beebf115cf5d44d74 2026-06-24 19:33:04 -0500 feat: publish dream proposer package |
| `reports/2026-06-17-fmc-mcp-intake-expected-vs-actual-opus-review.json` | b2aa47f1cfe85206bab9960beebf115cf5d44d74 2026-06-24 19:33:04 -0500 feat: publish dream proposer package |
| `reports/2026-06-17-fmc-mcp-intake-expected-vs-actual.md` | b2aa47f1cfe85206bab9960beebf115cf5d44d74 2026-06-24 19:33:04 -0500 feat: publish dream proposer package |
| `reports/2026-06-17-fmc-mcp-production-intake-result.md` | b2aa47f1cfe85206bab9960beebf115cf5d44d74 2026-06-24 19:33:04 -0500 feat: publish dream proposer package |
| `reports/2026-06-17-fmc-mcp-run-prep-opus-rereview.err` | b2aa47f1cfe85206bab9960beebf115cf5d44d74 2026-06-24 19:33:04 -0500 feat: publish dream proposer package |
| `reports/2026-06-17-fmc-mcp-run-prep-opus-rereview.json` | b2aa47f1cfe85206bab9960beebf115cf5d44d74 2026-06-24 19:33:04 -0500 feat: publish dream proposer package |
| `reports/2026-06-17-fmc-mcp-run-prep-opus-review-retry.err` | b2aa47f1cfe85206bab9960beebf115cf5d44d74 2026-06-24 19:33:04 -0500 feat: publish dream proposer package |
| `reports/2026-06-17-fmc-mcp-run-prep-opus-review-retry.json` | b2aa47f1cfe85206bab9960beebf115cf5d44d74 2026-06-24 19:33:04 -0500 feat: publish dream proposer package |
| `reports/2026-06-17-fmc-mcp-run-prep-opus-review.err` | b2aa47f1cfe85206bab9960beebf115cf5d44d74 2026-06-24 19:33:04 -0500 feat: publish dream proposer package |
| `reports/2026-06-17-fmc-mcp-run-prep-opus-review.json` | b2aa47f1cfe85206bab9960beebf115cf5d44d74 2026-06-24 19:33:04 -0500 feat: publish dream proposer package |
| `reports/2026-06-17-fmc-mcp-run-prep-review-prompt.md` | b2aa47f1cfe85206bab9960beebf115cf5d44d74 2026-06-24 19:33:04 -0500 feat: publish dream proposer package |
| `reports/2026-06-17-fmc-mcp-run-prep.md` | b2aa47f1cfe85206bab9960beebf115cf5d44d74 2026-06-24 19:33:04 -0500 feat: publish dream proposer package |
| `reports/2026-06-17-fmc-mcp-schema-fix-opus-plan-prompt.md` | b2aa47f1cfe85206bab9960beebf115cf5d44d74 2026-06-24 19:33:04 -0500 feat: publish dream proposer package |
| `reports/2026-06-17-fmc-mcp-schema-fix-opus-plan-retry.err` | b2aa47f1cfe85206bab9960beebf115cf5d44d74 2026-06-24 19:33:04 -0500 feat: publish dream proposer package |
| `reports/2026-06-17-fmc-mcp-schema-fix-opus-plan-retry.json` | b2aa47f1cfe85206bab9960beebf115cf5d44d74 2026-06-24 19:33:04 -0500 feat: publish dream proposer package |
| `reports/2026-06-17-fmc-mcp-schema-fix-opus-plan.err` | b2aa47f1cfe85206bab9960beebf115cf5d44d74 2026-06-24 19:33:04 -0500 feat: publish dream proposer package |
| `reports/2026-06-17-fmc-mcp-schema-fix-opus-plan.json` | b2aa47f1cfe85206bab9960beebf115cf5d44d74 2026-06-24 19:33:04 -0500 feat: publish dream proposer package |
| `reports/2026-06-17-fmc-mcp-schema-fix-opus-review-packet.md` | b2aa47f1cfe85206bab9960beebf115cf5d44d74 2026-06-24 19:33:04 -0500 feat: publish dream proposer package |
| `reports/2026-06-17-fmc-mcp-schema-fix-opus-review-retry.err` | b2aa47f1cfe85206bab9960beebf115cf5d44d74 2026-06-24 19:33:04 -0500 feat: publish dream proposer package |
| `reports/2026-06-17-fmc-mcp-schema-fix-opus-review-retry.json` | b2aa47f1cfe85206bab9960beebf115cf5d44d74 2026-06-24 19:33:04 -0500 feat: publish dream proposer package |
| `reports/2026-06-17-fmc-mcp-schema-fix-opus-review.err` | b2aa47f1cfe85206bab9960beebf115cf5d44d74 2026-06-24 19:33:04 -0500 feat: publish dream proposer package |
| `reports/2026-06-17-fmc-mcp-schema-fix-opus-review.json` | b2aa47f1cfe85206bab9960beebf115cf5d44d74 2026-06-24 19:33:04 -0500 feat: publish dream proposer package |
| `reports/2026-06-17-fmc-mcp-schema-fix-rerun-comparison.json` | b2aa47f1cfe85206bab9960beebf115cf5d44d74 2026-06-24 19:33:04 -0500 feat: publish dream proposer package |
| `reports/2026-06-17-fmc-mcp-schema-fix-rerun-report.md` | b2aa47f1cfe85206bab9960beebf115cf5d44d74 2026-06-24 19:33:04 -0500 feat: publish dream proposer package |
| `reports/2026-06-18-fmc-mcp-advisory-proposer-opus-inspection-prompt.md` | b2aa47f1cfe85206bab9960beebf115cf5d44d74 2026-06-24 19:33:04 -0500 feat: publish dream proposer package |
| `reports/2026-06-18-fmc-mcp-advisory-proposer-opus-inspection.err` | b2aa47f1cfe85206bab9960beebf115cf5d44d74 2026-06-24 19:33:04 -0500 feat: publish dream proposer package |
| `reports/2026-06-18-fmc-mcp-advisory-proposer-opus-inspection.json` | b2aa47f1cfe85206bab9960beebf115cf5d44d74 2026-06-24 19:33:04 -0500 feat: publish dream proposer package |
| `reports/2026-06-18-fmc-mcp-proposer-run-and-advisory-actionability-opus-review.err` | b2aa47f1cfe85206bab9960beebf115cf5d44d74 2026-06-24 19:33:04 -0500 feat: publish dream proposer package |
| `reports/2026-06-18-fmc-mcp-proposer-run-and-advisory-actionability-opus-review.json` | b2aa47f1cfe85206bab9960beebf115cf5d44d74 2026-06-24 19:33:04 -0500 feat: publish dream proposer package |
| `reports/2026-06-18-fmc-mcp-proposer-run-and-advisory-actionability-review-prompt.md` | b2aa47f1cfe85206bab9960beebf115cf5d44d74 2026-06-24 19:33:04 -0500 feat: publish dream proposer package |


Required operator decisions:

1. Whether public history should be rewritten/force-pushed for the sensitive `fmc-mcp`/firewall-management artifacts.
2. Whether any exposed credentials or credentials implied by the reports should be rotated. This audit did not find a live key value, but any real credential in associated private run roots must be treated as compromised if it was ever committed elsewhere.
3. Whether review-rated clutter should be kept privately before deletion from the public tree.

## Review-rated clutter prepared for later removal

These are non-sensitive public clutter candidates once the sensitive decision is resolved:

- `docs/verification/2026-06-19-pairwise-proposal-reranker-opus-rereview-prompt.md`
- `docs/verification/2026-06-19-pairwise-proposal-reranker-opus-rereview.err`
- `docs/verification/2026-06-19-pairwise-proposal-reranker-opus-rereview.json`
- `docs/verification/2026-06-19-pairwise-proposal-reranker-opus-review-prompt.md`
- `docs/verification/2026-06-19-pairwise-proposal-reranker-opus-review.err`
- `docs/verification/2026-06-19-pairwise-proposal-reranker-opus-review.json`
- `proposal-run-and-emit.patch`
- `reports/2026-06-17-build-arena-decomposer-model-candidates-opus-prompt.md`
- `reports/2026-06-17-build-arena-decomposer-model-candidates-opus-review-retry.err`
- `reports/2026-06-17-build-arena-decomposer-model-candidates-opus-review-retry.json`
- `reports/2026-06-17-build-arena-decomposer-model-candidates-opus-review.err`
- `reports/2026-06-17-build-arena-decomposer-model-candidates-opus-review.json`
- `reports/2026-06-17-build-arena-decomposer-model-candidates.md`
- `reports/2026-06-17-build-arena-decomposer-model-shortlist.json`
- `reports/2026-06-17-model-candidate-research-raw.json`
- `reports/2026-06-21-elenchus-core-proposal-run-opus-review.err`
- `reports/2026-06-21-elenchus-core-proposal-run-opus-review.json`
- `reports/2026-06-21-elenchus-core-proposal-run-report.md`
- `reports/2026-06-21-elenchus-core-proposal-run-review-prompt.md`
- `reports/2026-06-23-dream-proposer-tier3-opus-review-prompt.md`
- `reports/2026-06-23-dream-proposer-tier3-opus-review.err`
- `reports/2026-06-23-dream-proposer-tier3-opus-review.json`
- `reports/2026-06-23-dream-proposer-tier3-review-packet.md`

## Benign / keep


- `docs/specs/2026-06-19-pairwise-proposal-reranker-design.md` — versioned public Build Arena design-spec cleanup, not raw run output

## Remediation branch / PR status

No `git rm` was executed and no removal PR was opened from this audit because the sensitive finding rule says STOP for sensitive findings. This branch contains the audit/determination docs only.
