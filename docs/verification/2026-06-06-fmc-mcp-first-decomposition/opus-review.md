# Independent Review — Build Arena Project Model v1 for FMC-MCP

*Reviewing from the position of: "I am Opus, and next week I'll be asked to improve `/home/leonb/projects/fmc-mcp` using this model as my starting map."*

A framing fact that drives much of this review: `models.primary` is **`fixture-good-model`** and the probe builder is `fixture-independent-probe-builder`, and the final report states this was a **"non-live fixture decomposition … no paid LLM/API calls."** So the semantic content of this model was produced by a deterministic fixture, not a real reasoning model. This run primarily validated the *pipeline* (graph → gate → Elenchus consumption → durable hashed artifact), not the *quality of semantic decomposition*. Almost every weakness below traces back to that.

## 1. Overall verdict

**usable_with_gaps — 5/10.**

As a *structural* map (which file owns what, which module imports which, what command verifies the build) it is trustworthy and immediately usable. As a *decision-making* artifact for "what should I improve and what must I not break," it is thin to the point of being misleading, because the responsibilities are tautological and the FMC-domain invariants are absent. A strong model could navigate the repo with this, but could not prioritize work from it without re-reading the source.

## 2. What works well for future iteration

- **Provenance is genuinely strong.** Every node/edge/component/contract resolves to a `git_oid` + content hash + line range, all `dirty=false`, all `deterministic`. I can trust the map corresponds to commit `00a632a`. This is the model's best feature.
- **Component→module ownership is correct and complete** for the six production modules (`server`, `config`, `resources`, `client`, `tools`, `__main__`). Nothing important is misfiled.
- **Tests correctly modeled as verification, not as components.** Good call; it keeps `test_*.py` out of the responsibility surface while still backing the observable check.
- **The acceptance check is real and de-risked.** The report documents that `uv run pytest -q` actually failed in the target repo and was corrected to `uv run python -m pytest -q`, with the concrete string added to the allowlist. That's exactly the kind of "the check actually runs" diligence an agent needs.
- **The underlying graph is rich** (175 nodes incl. function-level: `RateLimiter`, `_authenticate`, `_refresh_auth_token`, `get_all_items`, `acquire/_refill`), with line ranges — excellent for navigation *if* I drop down to the raw graph.
- **`test_live.py` is correctly excluded** from default acceptance.

## 3. What the model missed or underrepresented about FMC-MCP

- **Responsibilities are tautologies.** Every component reads "Own the responsibility represented by `fmc_mcp.X` and expose it through graph-resolvable code evidence." The manual golden checklist contains the real semantics (token-bucket rate limiting, 401 re-auth, 429 retry-after, transparent pagination, `SecretStr` redaction, stdio-vs-HTTP transport selection) — **none of it survived into the accepted model.** This is the single biggest gap.
- **The FMC-domain cross-cutting concerns are absent.** The four concerns that *are* present (anti_fabrication, determinism, provenance, no_live_paid_api) are about **Build Arena's own integrity**, not about FMC-MCP. The project's actual invariants — **read-only safety** (no POST/PUT/DELETE except auth), **secret handling** (`SecretStr`, redacted logging), **rate/concurrency limits** (120 req/min, 10 connections) — appear nowhere. An agent "improving" the client from this model has no signal that these are invariants it must not break.
- **Contracts are static imports only; runtime contracts are missing.** The real coupling in this codebase is dependency injection: `server.lifespan` constructs `FMCClient` and calls `resources.set_client`; `tools.get_client()` retrieves it; resources/tools register as MCP handlers. None of that lifecycle/injection structure is modeled — only `imports` edges.
- **A real contract is missing and another is loosely backed.** There is **no `server → tools` contract**, even though the server registers the tool handlers. And `contract.component-fmc-mcp-server-component-fmc-mcp-resou` is supported by `edge:f5439cc4…`, which is an import of the **package `fmc_mcp`** (line 11), not of `fmc_mcp.resources` — a semantically loose provenance mapping that an evidence-checking consumer should have flagged.
- **No risk/priority signal at all.** `client.py` is 371 lines mixing five responsibilities (rate limiting, auth, transport, pagination, endpoint wrappers) — clearly the highest-risk file — but it ranks identically to the 6-line `__main__.py`. Nothing surfaces complexity, churn, or untested public functions.
- **External boundaries not modeled.** The FMC REST surface, the MCP protocol surface (4 resources / 2 tools registered), and `httpx`/`mcp.server.fastmcp` as the third-party edges aren't called out as the project's real I/O boundaries.
- **Only one check.** README and Build Arena's own `make verify` use ruff + pyright; the model exposes neither, so type/lint regressions are outside acceptance.

## 4. Questions I would ask before using this to improve FMC-MCP

1. **Was this generated by a fixture or a real model?** (The packet says fixture.) If so, is there a real-LLM decomposition I should use instead, or is the templated-responsibility output the actual current capability?
2. **Where do the rich semantic responsibilities live** — only in `manual-golden-decomposition.md`, or is there a richer field in v0 I should merge?
3. **What is the project's intent/roadmap?** Is the read-only MVP "done," or are write operations / more tools planned? This determines whether to harden vs. extend.
4. **Are the read-only/secret/rate-limit properties contractual invariants** I must preserve, or aspirational? The model gives them no status.
5. **Is `test_live.py` meant to join CI** behind a credentialed gate eventually?
6. **Is the `server.py` vs `tools.py` duplication of `search_object_by_ip` intentional** (registration wrapper vs implementation) or drift to consolidate?

## 5. Highest-value project improvements identifiable from this model

- **Split `client.py` (371 LOC).** The graph already shows the seams: extract `RateLimiter` (lines 16–62) and the auth/session lifecycle (`_authenticate`, `_refresh_auth_token`, `_request`) from the read-only endpoint wrappers (`get_devices`, `get_network_objects`, `get_host_objects`, `get_deployable_devices`). This is the clearest structural improvement the map supports.
- **Rename `fmc_mcp.client.test_connection`** (node `24b7fac7…`, lines 365–371). A `test_`-prefixed function inside `src/` is a naming smell and a pytest-collection hazard.
- **Consolidate the duplicated `search_object_by_ip`** between `server.py` and `tools.py` to remove the indirection.
- **Add ruff + pyright as observable checks** so acceptance matches the documented quality bar; map them to the components they guard.
- **Add a mocked end-to-end smoke** covering the `lifespan` → `set_client` → resource/tool path, since that injection wiring is the most fragile and least directly tested seam.

## 6. Highest-value improvements to the Project Model / decomposer itself

1. **Populate real responsibilities.** Synthesize each component's behavioral summary from its function-level nodes (the data is already in the graph) instead of restating the module name.
2. **Separate and surface *project* cross-cutting concerns** (read-only safety, secret/`SecretStr` handling, rate/concurrency limits) from *process* concerns, each with: the invariant, its evidence, and the check that protects it. Right now the two are conflated and the project ones are missing.
3. **Model runtime contracts, not just imports** — DI (`set_client`), lifecycle (`lifespan` create/close), and handler registration — and fix the loose package-import provenance + add the missing `server → tools` edge.
4. **Add risk/priority signals** (size/complexity, churn, public functions with no test edge) so a consumer can decide *where* to act, not just *what exists*.
5. **Map external boundaries** (FMC REST endpoints, MCP tools/resources, httpx/fastmcp) as first-class surfaces.
6. **Label decomposition provenance prominently** (`fixture` vs real model) in the artifact body, not only in a side report — consumers must not mistake fixture tautologies for analyzed ground truth.

## 7. Risks or warnings if an autonomous agent used this model as-is

- **Treating templated responsibilities as ground truth.** An agent may conclude each module has no specific responsibility and refactor/merge incorrectly.
- **Breaking unmodeled invariants.** With no read-only/secret/rate-limit concerns, an agent "optimizing" `client.py` could introduce a write call, log a secret, or relax the 10-connection/120-rpm limits and the model would signal nothing wrong.
- **Breaking the missing `server → tools` link.** An agent trusting the contract list might assume no dependency and break tool registration.
- **False confidence from acceptance.** A 19-test, 0.04s suite plus **`verification_gaps: 0`** reads as "complete," but gaps=0 reflects gate scope, not real coverage; lint/type/coverage are not gated.
- **Acting on stale structure.** The map is pinned to `00a632a`; an agent must re-run/verify before trusting it against a changed HEAD.

## 8. Bottom-line recommendation

**Use it as a trustworthy file/import skeleton and a verified entry-point for the acceptance command — but do not treat it as a decision map.** Before iterating, regenerate the decomposition with a real model (not the fixture) so responsibilities and domain concerns are populated, or manually merge in `manual-golden-decomposition.md`. The highest-leverage upgrade to the artifact is making responsibilities and project-level cross-cutting invariants real and evidence-backed; until then this model tells me *where the code is* but not *what matters about it*, which is exactly the half an improving agent most needs.

*(Schema mapping: overall_verdict = `usable_with_gaps`; iteration_usability_score = `5`.)*
