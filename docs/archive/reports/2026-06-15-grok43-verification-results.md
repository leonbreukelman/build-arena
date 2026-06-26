# Build Arena — Grok 4.3 verification results (2026-06-15)

## Scope

Operator asked to spend Grok 4.3 tokens to make sure the current Build Arena worktree was tested properly.

This report covers:

1. Normal deterministic repo verification on the current working tree.
2. xAI/Grok 4.3 availability and model lookup.
3. One bounded live Grok 4.3 project-model attempt through the Build Arena live path.

No promotion, push, deploy, or production mutation was performed.

## Local deterministic verification

All normal repo gates passed.

Commands run from `/home/leonb/projects/build-arena`:

```bash
uv run pytest tests -q
```

Exit code: 0

Observed output ended with:

```text
........................................................                 [100%]
```

```bash
uv run ruff check .
```

Exit code: 0

Observed output:

```text
All checks passed!
```

```bash
uv run pyright
```

Exit code: 0

Observed output:

```text
0 errors, 0 warnings, 0 informations
WARNING: there is a new pyright version available (v1.1.409 -> v1.1.410).
Please install the new version or set PYRIGHT_PYTHON_FORCE_VERSION to `latest`
```

```bash
make generated-fresh
```

Exit code: 0

Observed result: generated LinkML artifacts were regenerated and `git diff --exit-code -- arena/generated dashboard/src/lib/generated` returned clean.

Final all-in-one verification:

```bash
make verify
```

Exit code: 0

Observed result: `generated-fresh`, `ruff`, `pyright`, and full `pytest` all passed.

## Grok 4.3 preflight

xAI API key resolution was checked without printing the secret.

Result:

```json
{
  "api_key_source": "hermes_env_file",
  "has_grok_4_3": true,
  "matching_models": [
    "grok-4.20-0309-non-reasoning",
    "grok-4.20-0309-reasoning",
    "grok-4.20-multi-agent-0309",
    "grok-4.3"
  ],
  "model_count": 9
}
```

## Bounded live Grok 4.3 attempt

Command run:

```bash
RUN_ROOT="/tmp/build-arena-grok43-verification-20260615T020201Z"
uv run python -m arena.project_model_cli snapshot \
  --project /home/leonb/projects/build-arena \
  --artifacts-root "$RUN_ROOT" \
  --project-id build-arena \
  --goal 'Verify the current Build Arena working tree with a bounded live Grok 4.3 project decomposition before final handoff.' \
  --source-task 'Grok 4.3 live verification attempt requested by operator' \
  --primary-backlog-item 'current-working-tree-verification' \
  --llm-mode live \
  --allow-live \
  --live-provider xai \
  --live-model grok-4.3 \
  --live-api-key-env XAI_API_KEY \
  --live-max-tokens 8192 \
  --run-adversarial-probes \
  --overwrite
```

Exit code: 1

This is a fail-closed gate result, not a transport/auth failure. The live call reached xAI and returned a response from the requested model.

Live metadata from the manifest:

```json
{
  "api_key_source": "hermes_env_file",
  "api_mode": "openai_chat_completions",
  "base_url": "https://api.x.ai/v1",
  "finish_reason": "stop",
  "model": "grok-4.3",
  "provider": "xai",
  "requested_model": "grok-4.3",
  "requested_model_source": "argument",
  "served_model_matches_requested": true,
  "status_code": 200,
  "usage": {
    "prompt_tokens": 12924,
    "completion_tokens": 1818,
    "total_tokens": 15902,
    "completion_tokens_details": {
      "reasoning_tokens": 1160
    }
  }
}
```

Cost estimate using the repo's prior Grok 4.3 pricing basis ($1.25 / 1M input tokens and $2.50 / 1M output tokens): `$0.02070000`.

Artifacts:

- Manifest: `/tmp/build-arena-grok43-verification-20260615T020201Z/snapshot-8fa86db71022f5bf/manifest.json`
- Gate report: `/tmp/build-arena-grok43-verification-20260615T020201Z/snapshot-8fa86db71022f5bf/gate-report.json`
- Raw model output: `/tmp/build-arena-grok43-verification-20260615T020201Z/snapshot-8fa86db71022f5bf/model-outputs/decomposer.raw.json`
- Prompt: `/tmp/build-arena-grok43-verification-20260615T020201Z/snapshot-8fa86db71022f5bf/prompts/decomposer-prompt.txt`

Gate result:

```json
{
  "passed": false,
  "violation_count": 22
}
```

Violation breakdown:

- 2 `cross_cutting_concerns` errors:
  - missing `protected_surface_integrity`
  - missing `generated_artifact_integrity`
- 20 `inventory_coverage` errors for primary source nodes that were neither component-owned nor covered by a verification gap.

The prompt explicitly told the model:

- Every primary module must be owned exactly once or covered by a verification gap.
- Include `protected_surface_integrity` and `generated_artifact_integrity` if those surfaces exist.

So the bounded live attempt found model-output undercoverage on this dirty Build Arena tree. It did not find a local test failure, auth failure, served-model mismatch, or harness crash.

## Run verdict

Run verdict: `FAIL_CLOSED_DECOMPOSITION_GATE`.

This is the verdict for the bounded live Grok 4.3 decomposition attempt. The model/provider transport worked, but the produced Project Model did not satisfy the deterministic decomposition gate. Therefore this run is not accepted as a clean live decomposition and must not be cited as green Grok 4.3 decomposition evidence.

Deterministic verification is green:

- full pytest: pass
- ruff: pass
- pyright: pass
- generated freshness: pass
- `make verify`: pass

The bounded Grok 4.3 live project-model attempt is not green:

- xAI transport/model path: pass
- requested/served `grok-4.3`: pass
- deterministic gate over the live model output: fail closed with 22 violations

Owner-language conclusion: the code is locally verified, but the current dirty Build Arena tree should not be described as having a clean Grok 4.3 live decomposition. If the bar is "normal repo tests are green," that bar is met. If the bar is "Grok 4.3 can cleanly decompose this working tree in one bounded live call," that bar is not met yet.

## Independent Grok 4.3 review of this report

This report itself was reviewed by a second bounded `grok-4.3` call.

Review artifact:

- `/home/leonb/projects/build-arena/reports/2026-06-15-grok43-verification-results-grok43-review.json`

Review metadata:

- requested model: `grok-4.3`
- served model: `grok-4.3`
- served model matched requested: `true`
- finish reason: `stop`
- prompt tokens: `1834`
- completion tokens: `185`
- total tokens: `2518`

Report-faithfulness review verdict: `ACCEPT`.

That reviewer verdict means only that the report accurately described the failed live decomposition gate. It is not a live decomposition acceptance, not a production-readiness acceptance, and not evidence that the Grok 4.3 Project Model output passed.

Reviewer summary: report conclusions are directly supported by the command outputs and metadata provided; no overstatements of success on the live decomposition gate.

## Follow-up if a green live Grok bar is required

Do not blindly retry the same one-call prompt. The failed output omitted gate-required coverage. Reasonable next steps are:

1. Add or use a deterministic closure/pass that ensures primary-module coverage after semantic component selection, if that is the intended architecture.
2. Split live decomposition into smaller bounded passes instead of asking one call to cover the whole dirty repo graph.
3. Add provider controls for reasoning/output budgeting if the xAI API exposes a stable control for Grok 4.3; this run spent 1160 completion tokens on reasoning and produced an under-covering visible model.
4. Re-run the same deterministic gate only after changing one of the above variables, and keep `--live-model grok-4.3` plus explicit call ceilings.
