# Build Arena decomposer model candidates — 2026-06-17

## Owner answer

Yes. There are specialized coding / agentic-software-engineering models on OpenRouter and Hugging Face that are a better fit for Build Arena's decomposer role than generic Grok 4.3.

The best first OpenRouter candidate is `qwen/qwen3-coder`.

The best exploratory candidates after that are:

1. `deepseek/deepseek-v4-pro`
2. `moonshotai/kimi-k2.7-code`
3. `x-ai/grok-build-0.1`
4. `openai/gpt-5.3-codex` if we are willing to use OpenAI via OpenRouter
5. `openrouter/pareto-code` only for exploration, not for a controlled baseline

For Hugging Face/local, the most practical first candidates are:

1. `Qwen/Qwen3-Coder-30B-A3B-Instruct`
2. `mistralai/Devstral-Small-2-24B-Instruct-2512`
3. `Qwen/Qwen2.5-Coder-32B-Instruct`
4. `deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct`

But the bigger answer is this: model choice alone will not fix the failure we just saw. The Grok 4.3 high-reasoning failure was a schema/gate-compliance failure. The raw high-reasoning output did include concern records with ids like `anti_fabrication`, `determinism`, `provenance`, and `no_live_paid_api_acceptance`, but the `category` values were broad labels such as `integrity`, `reliability`, `traceability`, and `compliance`. Build Arena's gate checks the exact `category` enum values `anti_fabrication`, `determinism`, `provenance`, and `no_live_paid_api_acceptance`, so it treated those universal concerns as missing and uncovered. This is an observed raw-artifact issue, not just a model-quality hunch.

So the right next move is not just “try a smarter model.” It is:

1. tighten the decomposer prompt/schema so the universal concern category values are explicit and non-negotiable;
2. ideally use JSON Schema / structured outputs instead of only `response_format={"type":"json_object"}`;
3. then run a small model bake-off.

## Decomposer-role requirements

The role is not ordinary code generation. A good model must do all of this at once:

- follow strict JSON with exact field names;
- preserve exact opaque graph IDs and provenance refs;
- classify source files into responsibility-bearing components, not file buckets;
- infer runtime contracts and external surfaces from code structure;
- rank production components sensibly for intake;
- avoid over-ranking test files as product risk;
- preserve mandatory universal categories exactly as the deterministic gate expects;
- keep enough detail for downstream scorecard/proposal use;
- tolerate 20k+ prompt context now and much larger repo graphs later;
- support OpenAI-compatible `response_format` at minimum, preferably JSON Schema / structured outputs.

The recent fmc-mcp runs exposed the distinction:

- `grok-4.20-0309-non-reasoning`: gate-passing and rich, but bad ranking (`comp-tests` rank 1).
- `grok-4.3` high reasoning: better ranking (`comp:client` rank 1), but gate-failing and thinner artifact.

That means we need a model that combines codebase semantics with schema discipline.

## Current OpenRouter candidates

Source snapshot saved at:
`<repo>/reports/2026-06-17-build-arena-decomposer-model-shortlist.json`

Raw candidate research saved at:
`<repo>/reports/2026-06-17-model-candidate-research-raw.json`

### 1. `qwen/qwen3-coder` — best first candidate

OpenRouter page:
`https://openrouter.ai/qwen/qwen3-coder`

Why it fits:

- OpenRouter describes it as optimized for agentic coding, function calling, tool use, and long-context reasoning over repositories.
- 1,048,576 token context window.
- Supports `response_format` and `structured_outputs` according to the OpenRouter models API.
- OpenRouter's page reports provider-level structured-output error rates, but the saved API snapshot only records `response_format` / `structured_outputs` support, not those error-rate measurements. Treat provider error rates as page metadata to verify again before using them for routing.
- Cheaper than frontier closed models for this role: API snapshot listed `$0.22/M` input and `$1.80/M` output headline pricing.

Why it might beat Grok here:

- The task is repo-level code understanding plus strict structured output. This model is explicitly code/repo/agent focused.
- It likely has better coding-specialized priors than general Grok 4.3.

Risk:

- It is non-reasoning in the Qwen3-Coder 30B HF card; the 480B OpenRouter model is still code-specialized but not necessarily better at exact BA gate quirks unless the schema is tightened.

Recommended use:

First bake-off candidate after we patch structured schema / universal category instructions.

### 2. `deepseek/deepseek-v4-pro` — best cheap large-context reasoning candidate

OpenRouter page:
`https://openrouter.ai/deepseek/deepseek-v4-pro`

Why it fits:

- OpenRouter describes it as designed for advanced reasoning, coding, long-horizon agent workflows, full-codebase analysis, and large-scale information synthesis.
- 1M context window.
- Supports `reasoning`, `response_format`, and `structured_outputs` by OpenRouter model metadata.
- Pricing from API/page snapshot: about `$0.435/M` input and `$0.87/M` output on the headline provider.

Why it might beat Grok here:

- Long-context reasoning + coding + structured outputs at lower cost.
- Could preserve richer surfaces than Grok 4.3 high reasoning while improving semantic ranking.

Risk:

- Not code-only; it is a broad reasoning model. Needs bake-off evidence.

Recommended use:

Second candidate; run with explicit reasoning setting and the same snapshot prompt.

### 3. `moonshotai/kimi-k2.7-code` — best agentic long-horizon coding candidate

OpenRouter page:
`https://openrouter.ai/moonshotai/kimi-k2.7-code`

Hugging Face page:
`https://huggingface.co/moonshotai/Kimi-K2.7-Code`

Why it fits:

- Coding-focused, agentic, long-horizon software engineering model.
- 256K context window.
- OpenRouter metadata says it supports `reasoning`, `response_format`, `structured_outputs`, and tools.
- Hugging Face card reports Kimi K2.7 Code improves over K2.6 on coding/agentic benchmarks and includes MCP-related benchmark numbers. Treat these as vendor/model-card claims until Build Arena has its own decomposer bake-off data.

Why it might beat Grok here:

- The decomposer role is close to agentic codebase understanding, and Kimi K2.7 Code is explicitly optimized for end-to-end software engineering tasks.

Risk:

- More expensive than Qwen3-Coder / DeepSeek V4 Pro in the OpenRouter snapshot.
- OpenRouter page showed provider-level structured-output/error-rate data, but those rates are not in the saved API snapshot. Provider selection likely matters, but verify current endpoint stats before relying on a specific provider.
- 256K context is enough for current fmc-mcp but less future-proof than 1M-context options.

Recommended use:

Third candidate; test with a provider known to have low structured-output error on OpenRouter, not default blind routing.

### 4. `x-ai/grok-build-0.1` — xAI's code-specialized alternative to generic Grok

OpenRouter page:
`https://openrouter.ai/x-ai/grok-build-0.1`

Why it fits:

- OpenRouter describes it as xAI's fast coding model trained specifically for agentic software engineering workflows.
- Optimized for interactive coding agents, tool use, multi-step development tasks, and long-horizon coding automation.
- 256K context window.
- Supports `reasoning`, `response_format`, `structured_outputs`, and tools by OpenRouter model metadata.
- OpenRouter page reports provider performance/structured-output data, but the saved API snapshot only proves API support flags and pricing/context. Re-check endpoint stats before treating throughput or error rate as a selection input.

Why it might beat Grok 4.3:

- It is xAI's specialized coding-agent model rather than a general reasoning model.
- Could keep the Grok ecosystem behavior while improving coding/repo semantics.

Risk:

- Early-access model.
- Smaller context than Grok 4.20 or DeepSeek/Qwen long-context options.
- It may still share xAI quirks around schema following.

Recommended use:

Worth testing if we want to stay in xAI, but I would not put it ahead of Qwen3-Coder or DeepSeek V4 Pro for this decomposer role.

### 5. `openai/gpt-5.3-codex` — likely strong, but not HF/open-source

OpenRouter API metadata lists `openai/gpt-5.3-codex` as OpenAI's advanced agentic coding model, with `response_format`, `structured_outputs`, reasoning, and 400K context.

Why it fits:

- Codex-family model tuned specifically for agentic coding.
- Strong candidate for repo-level code reasoning.

Risk:

- Higher output price in API snapshot.
- Not Hugging Face/open-source.
- If Leon's intent is “subscription-first / avoid random API spend,” this may not be first.

Recommended use:

Use only if we want a frontier coding baseline after cheaper/open candidates.

### Other OpenRouter candidates considered but not first

- `deepseek/deepseek-v4-flash`: very cheap, 1M context, reasoning/structured-output support. Good cheap smoke candidate, but I would test V4 Pro first because this decomposer role is quality-sensitive and the recent Grok high-reasoning run already showed that thin output can fail the gate.
- `kwaipilot/kat-coder-pro-v2`: code/enterprise-SWE focused, 256K context, structured-output support, cheaper than Kimi. Worth a later bake-off slot, but I found less direct evidence for strict JSON / repo-decomposition behavior than Qwen3-Coder, DeepSeek, Kimi, or Grok Build.
- `z-ai/glm-5.2`: 1M context, reasoning/structured-output support, project-level SWE positioning. Worth tracking, but not first because the immediate task is code-repo decomposition with strict schema, where Qwen3-Coder and the coding-specialized models are more directly targeted.

### 6. `openrouter/pareto-code` — useful router, bad controlled experiment baseline

OpenRouter page:
`https://openrouter.ai/openrouter/pareto-code`

Why it is interesting:

- Routes coding requests to a tiered shortlist of strong coding models based on coding percentiles.
- 2M context listed in OpenRouter API snapshot.

Why I would not use it first:

- For Build Arena we need reproducible artifact lineage: exact model, exact provider, exact failure mode.
- A router can silently change which model produced an artifact unless metadata is very carefully preserved.
- The OpenRouter API snapshot did not advertise the same normal parameter support for this router as direct models.

Recommended use:

Exploratory only, not a baseline for gate/debug work.

## Hugging Face / local candidates

Current local GPU state checked:

```text
NVIDIA GeForce RTX 4090, 24564 MiB total, 21937 MiB free
```

This means local HF use is feasible only with quantized/smaller models. Full Kimi 1T or Qwen3-Coder 480B is not local-4090 practical; use those through OpenRouter/API.

### 1. `Qwen/Qwen3-Coder-30B-A3B-Instruct`

HF page:
`https://huggingface.co/Qwen/Qwen3-Coder-30B-A3B-Instruct`

Why it fits:

- Coding / agentic coding / repo-level understanding model.
- 30.5B total, 3.3B active MoE.
- Native 256K context, extendable to 1M with Yarn.
- Tool/function calling support.
- Hugging Face card explicitly describes repository-scale understanding.

Local practicality:

- BF16 full model is too big for one 24GB card, but quantized variants should be tested.
- This is the best HF/local candidate for a cheap decomposer bake-off.

Risk:

- Card says it supports only non-thinking mode.
- Smaller than OpenRouter's 480B Qwen3-Coder; local result may not match API result.

### 2. `mistralai/Devstral-Small-2-24B-Instruct-2512`

HF page:
`https://huggingface.co/mistralai/Devstral-Small-2-24B-Instruct-2512`

Why it fits:

- Explicitly an agentic LLM for software engineering tasks.
- Designed for codebase exploration, multi-file edits, tool use, and coding agents.
- 24B parameters, 256K context.
- HF card says it can run on a single RTX 4090 or Mac with 32GB RAM.
- Apache 2.0.

Local practicality:

- Best local/single-4090 candidate if we want something more SWE-agent shaped than generic Qwen Coder.

Risk:

- Its strength is agentic exploration/editing; our decomposer is a strict JSON extraction task. It still needs schema discipline testing.

### 3. `Qwen/Qwen2.5-Coder-32B-Instruct`

HF page:
`https://huggingface.co/Qwen/Qwen2.5-Coder-32B-Instruct`

Why it fits:

- Mature code-specialized model.
- 128K context with YaRN guidance.
- Strong code generation/reasoning/fixing claim.

Local practicality:

- Quantized versions are likely practical on the 4090.

Risk:

- Older than Qwen3-Coder and less agentic/repo-focused.
- 128K context is enough for fmc-mcp but not as future-proof.

### 4. `deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct`

HF page:
`https://huggingface.co/deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct`

Why it fits:

- Open-source MoE code model.
- 16B total / 2.4B active, 128K context.
- Broad programming language support and code reasoning.

Local practicality:

- Most practical local cheap smoke candidate.

Risk:

- Probably too weak for the full BA decomposer role compared with Qwen3-Coder or Devstral.
- Better as a cheap local regression/sanity model, not the lead decomposer.

## What I would run next

Do not run a big model sweep yet. Patch the harness first.

### Patch before model bake-off

The fmc-mcp high-reasoning failure shows the prompt/schema allows this wrong pattern:

```json
{"id": "anti_fabrication", "category": "integrity"}
```

The gate expects:

```json
{"id": "concern.anti-fabrication", "category": "anti_fabrication"}
```

So before spending more provider tokens:

1. make the universal concern category enum explicit in the prompt;
2. add a coercion or validation repair step that fails early with a clear attribution when id/category are swapped or categories are semantic synonyms;
3. preferably move from `json_object` to provider JSON Schema / structured outputs for models that support it.

Current OpenRouter metadata shows the top candidates support `response_format` and `structured_outputs`, but Build Arena's current adapter only sends `response_format={"type":"json_object"}`. That leaves schema discipline on the model. We should reduce that variance.

### Then run this bake-off

One call each, same fmc-mcp prompt, temperature 0 where applicable, explicit reasoning settings where supported, no intake. Do not use the same token cap for every model if the model spends hidden reasoning tokens; the Grok 4.3 high-reasoning run used 7,897 reasoning tokens plus 1,417 visible completion tokens, so a low `max_tokens` can make a reasoning model look artificially thin.

1. `qwen/qwen3-coder`
2. `deepseek/deepseek-v4-pro`
3. `x-ai/grok-build-0.1`
4. `moonshotai/kimi-k2.7-code`
5. optional local: `Qwen/Qwen3-Coder-30B-A3B-Instruct` quantized
6. optional local: `mistralai/Devstral-Small-2-24B-Instruct-2512` quantized

Score each run on:

- deterministic gate pass/fail;
- violation count and kind;
- component ranking: production client/server above tests/entrypoint;
- ranking-quality hard check for non-reasoning candidates: if tests/entrypoint outrank production client/server, the artifact is not intake-ready even if the gate passes;
- raw richness: contracts, observable checks, verification gaps;
- v1 richness: runtime contracts, external surfaces, invariants, quality gates, backlog/open questions;
- strict mandatory fmc-mcp expectations;
- exact cost/latency;
- served-model/provider metadata;
- whether it required repair/coercion.

Reasoning settings should be recorded per run:

- `qwen/qwen3-coder`: no reasoning parameter in the saved OpenRouter snapshot; treat it as code-specialized non-reasoning and watch ranking quality closely.
- `deepseek/deepseek-v4-pro`: use explicit reasoning if supported by the endpoint; record the exact value.
- `x-ai/grok-build-0.1`: use explicit reasoning if supported by the endpoint; record the exact value.
- `moonshotai/kimi-k2.7-code`: record thinking/reasoning behavior and provider, because Kimi provider routing can matter.
- local HF candidates: record quantization, context setting, server, and whether schema repair/coercion was needed.

## Practical command shape for OpenRouter

Build Arena already has an OpenRouter provider preset in `arena/llm_adapter.py`, so direct OpenRouter attempts should be possible with:

```text
uv run python -m arena.project_model_cli snapshot \
  --project <projects>/fmc-mcp \
  --artifacts-root <run-root> \
  --project-id fmc-mcp \
  --goal "Improve the read-only Cisco Firepower Management Center MCP server with bounded, verified, single-file changes that preserve local tests, lint, and typing." \
  --source-task "live decomposition model bake-off; stop before intake" \
  --primary-backlog-item decomposition-only-model-bakeoff \
  --llm-mode live \
  --allow-live \
  --live-provider openrouter \
  --live-model qwen/qwen3-coder \
  --live-api-key-env OPENROUTER_API_KEY \
  --live-max-tokens 12000
```

Need to verify `OPENROUTER_API_KEY` in the live shell or `.env` before running.

## Bottom line

Yes, there are better-specialized candidates. I would test `qwen/qwen3-coder` first through OpenRouter, then `deepseek/deepseek-v4-pro`, then `x-ai/grok-build-0.1` if we want to stay close to xAI, and `moonshotai/kimi-k2.7-code` as the agentic-code dark horse.

For local/Hugging Face, use `Qwen/Qwen3-Coder-30B-A3B-Instruct` or `Devstral-Small-2-24B-Instruct-2512` as practical quantized 4090 candidates, but I would not expect local HF models to beat the best OpenRouter-hosted code models on the full strict-JSON decomposer task without additional schema constraints.
