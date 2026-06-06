You are Grok acting as the primary AI-first project decomposer for Build Arena.

Return only valid JSON, no markdown. Required top-level keys:
model_id, project_id, goal, non_goals, components, contracts, cross_cutting_concerns, observable_checks, verification_gaps, near_neighbor_alternatives, acceptance_command_allowlist.
Do not include held_out_probes or planted_negatives; those come from a separate independent probe-builder.
Component shape: {id,name,responsibility,owned_node_ids,provenance_refs,contract_ids,check_ids,verification_gap_ids}.
Contract shape: {id,name,from_component_id,to_component_id,supporting_edge_ids,near_neighbor_alternative_ids,provenance_refs}.
Concern shape: {id,category,description,component_ids,contract_ids,provenance_refs,triggered_by}.
ObservableCheck shape: {id,description,command,component_ids,contract_ids,provenance_refs,acceptance_command_id,safe_to_run_by_default,requires_network,requires_paid_api}.
VerificationGap shape: {id,description,severity,component_ids,contract_ids,provenance_refs,proposed_closure_check}.
NearNeighborAlternative shape: {id,target_id,alternative,why_not_primary,provenance_refs}.
Rules: use only exact node IDs, edge IDs, and provenance IDs from the packet; no invented graph IDs. Components must be responsibility-bearing, not 1:1 file/module renames when a semantic grouping is warranted. If an important surface is not decomposed, create a verification gap rather than silently dropping it. Include at least two contracts when import evidence supports it. Use the actual_verification_command as the primary observable command. Include protected/generated concerns when surfaces list contains them, and never own protected/generated nodes as component-owned source. Set acceptance_command_allowlist to the check IDs you actually use.

Project packet:
{
  "project_id": "leonbreukelman-engineer",
  "repo": "/home/leonb/projects/leonbreukelman-engineer",
  "goal": "decompose the AI-first public site and agent metadata project into source-backed components across build scripts, JavaScript worker code, public JSON data, templates, and docs",
  "non_goals": [
    "do not treat generated dist output as source ownership",
    "do not require Cloudflare deployment or public mutation"
  ],
  "actual_verification_command": "npm run build && npm run check:links",
  "git_dirty": false,
  "dirty_paths": [],
  "node_kinds": {
    "file": 21,
    "markdown_section": 31,
    "python_function": 27,
    "config": 10,
    "javascript_module": 2,
    "javascript_function": 4,
    "python_module": 3,
    "test_file": 1,
    "project": 1,
    "python_class": 1,
    "javascript_import": 1,
    "python_import": 13
  },
  "edge_kinds": {
    "configures": 10,
    "defined_in": 37,
    "contains": 32,
    "documents": 31,
    "imports": 17,
    "tests": 1
  },
  "candidate_nodes": [
    {
      "id": "node:016549f456f6ba3ecbb6",
      "kind": "file",
      "label": "templates/human/services.html",
      "path": "templates/human/services.html",
      "symbol": null,
      "tags": [],
      "prov": "prov:a426998abe16a1d3"
    },
    {
      "id": "node:087085bf23e3cc4628f2",
      "kind": "markdown_section",
      "label": "What He Is Less Good At",
      "path": "prompt/represent_me.md",
      "symbol": "prompt/represent_me.md#What He Is Less Good At",
      "tags": [],
      "prov": "prov:505ad7266a711b66"
    },
    {
      "id": "node:0b296c8c603b4645bd9d",
      "kind": "python_function",
      "label": "render_page",
      "path": "scripts/build.py",
      "symbol": "scripts.build.render_page",
      "tags": [],
      "prov": "prov:171ec312e6eb8703"
    },
    {
      "id": "node:0f29b2589c8192bfd049",
      "kind": "python_function",
      "label": "test_worker_returns_gone_for_retired_article_routes",
      "path": "tests/test_public_contract.py",
      "symbol": "tests.test_public_contract.test_worker_returns_gone_for_retired_article_routes",
      "tags": [],
      "prov": "prov:b3a339052ff65c4a"
    },
    {
      "id": "node:14b22207cea9242c6f34",
      "kind": "config",
      "label": "api/v1/projects.json",
      "path": "api/v1/projects.json",
      "symbol": null,
      "tags": [],
      "prov": "prov:c6056aa2fba92b85"
    },
    {
      "id": "node:151cf959b51dafbd619e",
      "kind": "config",
      "label": "well-known/agent-card.json",
      "path": "well-known/agent-card.json",
      "symbol": null,
      "tags": [],
      "prov": "prov:813acff12ec619c1"
    },
    {
      "id": "node:182d7abe7007643cd122",
      "kind": "python_function",
      "label": "setup_jinja",
      "path": "scripts/build.py",
      "symbol": "scripts.build.setup_jinja",
      "tags": [],
      "prov": "prov:84fab95b9de823c6"
    },
    {
      "id": "node:1c5a6f0459fa5b83d040",
      "kind": "markdown_section",
      "label": "Quick Start",
      "path": "README.md",
      "symbol": "README.md#Quick Start",
      "tags": [],
      "prov": "prov:fa04b24fd751aac4"
    },
    {
      "id": "node:1e8ba7fd1db36d8f49db",
      "kind": "javascript_module",
      "label": "worker.mcp.server",
      "path": "worker/mcp/server.js",
      "symbol": "worker.mcp.server",
      "tags": [],
      "prov": "prov:e8c798459ce07e15"
    },
    {
      "id": "node:242462366792e6c85ea0",
      "kind": "markdown_section",
      "label": "Development",
      "path": "README.md",
      "symbol": "README.md#Development",
      "tags": [],
      "prov": "prov:cd2a7925a71a196b"
    },
    {
      "id": "node:265a520d06ab9e3d76cd",
      "kind": "python_function",
      "label": "test_public_positioning_is_humble_and_not_credential_forward",
      "path": "tests/test_public_contract.py",
      "symbol": "tests.test_public_contract.test_public_positioning_is_humble_and_not_credential_forward",
      "tags": [],
      "prov": "prov:fdeaea75119ca8d3"
    },
    {
      "id": "node:270b52766ba2097c3bf8",
      "kind": "file",
      "label": "prompt/represent_me.md",
      "path": "prompt/represent_me.md",
      "symbol": null,
      "tags": [],
      "prov": "prov:756f566ef137b772"
    },
    {
      "id": "node:2bb51f976c64d4211590",
      "kind": "python_function",
      "label": "extract_urls",
      "path": "scripts/check-public-links.py",
      "symbol": "scripts.check-public-links.extract_urls",
      "tags": [],
      "prov": "prov:d61ae4c462fc6458"
    },
    {
      "id": "node:32f3a0d3845cf98fb8cb",
      "kind": "javascript_module",
      "label": "worker",
      "path": "worker/index.js",
      "symbol": "worker",
      "tags": [],
      "prov": "prov:ea0068ba73266e60"
    },
    {
      "id": "node:346f9b3cd2dde3c5d686",
      "kind": "file",
      "label": "templates/human/work.html",
      "path": "templates/human/work.html",
      "symbol": null,
      "tags": [],
      "prov": "prov:06bd972541318fd3"
    },
    {
      "id": "node:3497d88db26b2742c66a",
      "kind": "markdown_section",
      "label": "Stories Worth Telling",
      "path": "prompt/represent_me.md",
      "symbol": "prompt/represent_me.md#Stories Worth Telling",
      "tags": [],
      "prov": "prov:ecf942bf7ef015fa"
    },
    {
      "id": "node:351b0cf821ac5d85e952",
      "kind": "python_function",
      "label": "test_build_fails_closed_instead_of_falling_back_to_article_archive",
      "path": "tests/test_public_contract.py",
      "symbol": "tests.test_public_contract.test_build_fails_closed_instead_of_falling_back_to_article_archive",
      "tags": [],
      "prov": "prov:97384f644806c1ae"
    },
    {
      "id": "node:3925af7de145b6e3ffe0",
      "kind": "python_function",
      "label": "test_buyer_facing_pages_and_data_exist",
      "path": "tests/test_public_contract.py",
      "symbol": "tests.test_public_contract.test_buyer_facing_pages_and_data_exist",
      "tags": [],
      "prov": "prov:d808c2de658d2c18"
    },
    {
      "id": "node:39d92e273650d019657f",
      "kind": "python_function",
      "label": "copy_prompt_files",
      "path": "scripts/build.py",
      "symbol": "scripts.build.copy_prompt_files",
      "tags": [],
      "prov": "prov:6394278cbbd6e7b3"
    },
    {
      "id": "node:3b25680b492a6345baec",
      "kind": "markdown_section",
      "label": "Deployment",
      "path": "README.md",
      "symbol": "README.md#Deployment",
      "tags": [],
      "prov": "prov:4129a4074bc34843"
    },
    {
      "id": "node:3c9a18d43326bf03e45f",
      "kind": "config",
      "label": "well-known/ai.json",
      "path": "well-known/ai.json",
      "symbol": null,
      "tags": [],
      "prov": "prov:7a63594e8000dd3e"
    },
    {
      "id": "node:3ea96135dd639273b1d2",
      "kind": "python_function",
      "label": "copy_api_files",
      "path": "scripts/build.py",
      "symbol": "scripts.build.copy_api_files",
      "tags": [],
      "prov": "prov:f8f91de97eb31594"
    },
    {
      "id": "node:40def010266dc2054df4",
      "kind": "config",
      "label": "wrangler.toml",
      "path": "wrangler.toml",
      "symbol": null,
      "tags": [],
      "prov": "prov:c20618cf7606fc6c"
    },
    {
      "id": "node:48991a5304f50a6f4617",
      "kind": "python_function",
      "label": "test_legacy_article_sources_are_removed",
      "path": "tests/test_public_contract.py",
      "symbol": "tests.test_public_contract.test_legacy_article_sources_are_removed",
      "tags": [],
      "prov": "prov:a80df12bd04c2aa7"
    },
    {
      "id": "node:4f7e53ec7b6ab7383a7c",
      "kind": "markdown_section",
      "label": "For Humans",
      "path": "README.md",
      "symbol": "README.md#For Humans",
      "tags": [],
      "prov": "prov:cb36c3c07f1b6ffd"
    },
    {
      "id": "node:50ef3f5ae5030e151c95",
      "kind": "python_function",
      "label": "check_url",
      "path": "scripts/check-public-links.py",
      "symbol": "scripts.check-public-links.check_url",
      "tags": [],
      "prov": "prov:3bb44d8a7ee8cb24"
    },
    {
      "id": "node:556c8beea475f0092f9d",
      "kind": "python_function",
      "label": "test_home_page_is_not_article_or_manifesto_led",
      "path": "tests/test_public_contract.py",
      "symbol": "tests.test_public_contract.test_home_page_is_not_article_or_manifesto_led",
      "tags": [],
      "prov": "prov:60d9f41d8fbffed7"
    },
    {
      "id": "node:569910cced19bf75ae0b",
      "kind": "config",
      "label": "api/v1/offers.json",
      "path": "api/v1/offers.json",
      "symbol": null,
      "tags": [],
      "prov": "prov:cc547fddea0bc4aa"
    },
    {
      "id": "node:5bdf043c6b60f3337321",
      "kind": "python_function",
      "label": "main",
      "path": "scripts/check-public-links.py",
      "symbol": "scripts.check-public-links.main",
      "tags": [],
      "prov": "prov:109e088b42b1cedd"
    },
    {
      "id": "node:5c8ebcea8dd641341457",
      "kind": "python_function",
      "label": "build_human_pages",
      "path": "scripts/build.py",
      "symbol": "scripts.build.build_human_pages",
      "tags": [],
      "prov": "prov:e9c7c073f81e5a80"
    },
    {
      "id": "node:5ea405faea230cdf5498",
      "kind": "markdown_section",
      "label": "Data Sources",
      "path": "prompt/represent_me.md",
      "symbol": "prompt/represent_me.md#Data Sources",
      "tags": [],
      "prov": "prov:440d643908db39b6"
    },
    {
      "id": "node:5ef4a7c114a17855d9c5",
      "kind": "file",
      "label": "templates/human/index.html",
      "path": "templates/human/index.html",
      "symbol": null,
      "tags": [],
      "prov": "prov:2c784af59836bbad"
    },
    {
      "id": "node:62ad61e36d4379d32dee",
      "kind": "python_function",
      "label": "setUpClass",
      "path": "tests/test_public_contract.py",
      "symbol": "tests.test_public_contract.setUpClass",
      "tags": [],
      "prov": "prov:4802cd6642a66791"
    },
    {
      "id": "node:69d6bc2e023965d76a75",
      "kind": "file",
      "label": "README.md",
      "path": "README.md",
      "symbol": null,
      "tags": [],
      "prov": "prov:4417f3bf0932d8ac"
    },
    {
      "id": "node:70dc63bab5d48553454b",
      "kind": "javascript_function",
      "label": "loadJson",
      "path": "worker/mcp/server.js",
      "symbol": "worker.mcp.server.loadJson",
      "tags": [],
      "prov": "prov:61f7f31bc619b9c9"
    },
    {
      "id": "node:7ad8da6a627ab8d27e9e",
      "kind": "markdown_section",
      "label": "Primary Positioning",
      "path": "prompt/represent_me.md",
      "symbol": "prompt/represent_me.md#Primary Positioning",
      "tags": [],
      "prov": "prov:ce979449395c4cd6"
    },
    {
      "id": "node:7bc3408b058bec876a5a",
      "kind": "python_function",
      "label": "test_recruiter_and_social_surfaces_are_not_public_artifacts",
      "path": "tests/test_public_contract.py",
      "symbol": "tests.test_public_contract.test_recruiter_and_social_surfaces_are_not_public_artifacts",
      "tags": [],
      "prov": "prov:985c483fff687a5b"
    },
    {
      "id": "node:879b251d931f7c881237",
      "kind": "python_function",
      "label": "build",
      "path": "scripts/build.py",
      "symbol": "scripts.build.build",
      "tags": [],
      "prov": "prov:fa9c631e3cc9aac6"
    },
    {
      "id": "node:8a344356f5d23c2baf2e",
      "kind": "python_module",
      "label": "tests.test_public_contract",
      "path": "tests/test_public_contract.py",
      "symbol": "tests.test_public_contract",
      "tags": [],
      "prov": "prov:20633b322b34fb46"
    },
    {
      "id": "node:8e1bda3aae8ca0473eca",
      "kind": "file",
      "label": "templates/human/ai.html",
      "path": "templates/human/ai.html",
      "symbol": null,
      "tags": [],
      "prov": "prov:14d6d8a7e97d1f6b"
    },
    {
      "id": "node:9d9d37a18c7ab7537c0f",
      "kind": "markdown_section",
      "label": "What He Is Good At",
      "path": "prompt/represent_me.md",
      "symbol": "prompt/represent_me.md#What He Is Good At",
      "tags": [],
      "prov": "prov:3644e055f1423819"
    },
    {
      "id": "node:a2126531d7c20f37e4d1",
      "kind": "python_function",
      "label": "copy_static_files",
      "path": "scripts/build.py",
      "symbol": "scripts.build.copy_static_files",
      "tags": [],
      "prov": "prov:4b64388607641e33"
    },
    {
      "id": "node:a5b95d7d7ada63930bef",
      "kind": "markdown_section",
      "label": "Preview locally",
      "path": "README.md",
      "symbol": "README.md#Preview locally",
      "tags": [],
      "prov": "prov:7894438ea3df3482"
    },
    {
      "id": "node:a781236d3a83da277bb3",
      "kind": "test_file",
      "label": "tests/test_public_contract.py",
      "path": "tests/test_public_contract.py",
      "symbol": null,
      "tags": [],
      "prov": "prov:4748fccbacbd25ea"
    },
    {
      "id": "node:abc28ffa9a81eb2796c3",
      "kind": "python_function",
      "label": "iter_public_files",
      "path": "scripts/check-public-links.py",
      "symbol": "scripts.check-public-links.iter_public_files",
      "tags": [],
      "prov": "prov:08cb365023aa07b6"
    },
    {
      "id": "node:b1e0de9e41d1ea0d7288",
      "kind": "javascript_function",
      "label": "loadPrompt",
      "path": "worker/mcp/server.js",
      "symbol": "worker.mcp.server.loadPrompt",
      "tags": [],
      "prov": "prov:0a3089718432b220"
    },
    {
      "id": "node:b3b1f19ad2ed91bec458",
      "kind": "config",
      "label": "api/v1/profile.json",
      "path": "api/v1/profile.json",
      "symbol": null,
      "tags": [],
      "prov": "prov:5dd0cc494cd85fbe"
    },
    {
      "id": "node:b8a0684279f7b4edc1bc",
      "kind": "file",
      "label": "llms.txt",
      "path": "llms.txt",
      "symbol": null,
      "tags": [],
      "prov": "prov:77b106b079f49cac"
    },
    {
      "id": "node:c1299be91730fc58c1e3",
      "kind": "markdown_section",
      "label": "Deploy to Cloudflare Pages",
      "path": "README.md",
      "symbol": "README.md#Deploy to Cloudflare Pages",
      "tags": [],
      "prov": "prov:4e30e269c5a237db"
    },
    {
      "id": "node:c627dcac9798554af877",
      "kind": "markdown_section",
      "label": "Voice",
      "path": "prompt/represent_me.md",
      "symbol": "prompt/represent_me.md#Voice",
      "tags": [],
      "prov": "prov:d068bad5b6984348"
    },
    {
      "id": "node:c871af2d62ed3dccfad0",
      "kind": "config",
      "label": "package-lock.json",
      "path": "package-lock.json",
      "symbol": null,
      "tags": [],
      "prov": "prov:9b30aea1617abf1c"
    },
    {
      "id": "node:ca0aad13b3b497dd9e40",
      "kind": "markdown_section",
      "label": "How to Represent Leon Breukelman",
      "path": "prompt/represent_me.md",
      "symbol": "prompt/represent_me.md#How to Represent Leon Breukelman",
      "tags": [],
      "prov": "prov:a92ae5c99a4d4dae"
    },
    {
      "id": "node:cd398435655203c8977c",
      "kind": "python_function",
      "label": "copy_root_files",
      "path": "scripts/build.py",
      "symbol": "scripts.build.copy_root_files",
      "tags": [],
      "prov": "prov:f45aa298c0dd30ad"
    },
    {
      "id": "node:cd8a921454b74ef09e06",
      "kind": "markdown_section",
      "label": "Contact",
      "path": "prompt/represent_me.md",
      "symbol": "prompt/represent_me.md#Contact",
      "tags": [],
      "prov": "prov:3962163d63785712"
    },
    {
      "id": "node:d038e1fd31641ace3226",
      "kind": "markdown_section",
      "label": "Structure",
      "path": "README.md",
      "symbol": "README.md#Structure",
      "tags": [],
      "prov": "prov:e2560a67a5e0ba01"
    },
    {
      "id": "node:d04474a27932d29e2de2",
      "kind": "python_function",
      "label": "copy_well_known_files",
      "path": "scripts/build.py",
      "symbol": "scripts.build.copy_well_known_files",
      "tags": [],
      "prov": "prov:711f5eb2efc52c71"
    },
    {
      "id": "node:d1ab9b8e0eb01b071904",
      "kind": "python_module",
      "label": "scripts.check-public-links",
      "path": "scripts/check-public-links.py",
      "symbol": "scripts.check-public-links",
      "tags": [],
      "prov": "prov:cc1fa9e22afc08c6"
    },
    {
      "id": "node:d701b635b99442ff8d5a",
      "kind": "markdown_section",
      "label": "Install dependencies",
      "path": "README.md",
      "symbol": "README.md#Install dependencies",
      "tags": [],
      "prov": "prov:7cf3013274f52d35"
    },
    {
      "id": "node:d8c96a6d1d1b949b47a8",
      "kind": "python_function",
      "label": "test_worker_returns_gone_for_retired_recruiter_and_social_routes",
      "path": "tests/test_public_contract.py",
      "symbol": "tests.test_public_contract.test_worker_returns_gone_for_retired_recruiter_and_social_routes",
      "tags": [],
      "prov": "prov:30dc80201ed692ce"
    },
    {
      "id": "node:d8fc3a88afab17188e7b",
      "kind": "python_module",
      "label": "scripts.build",
      "path": "scripts/build.py",
      "symbol": "scripts.build",
      "tags": [],
      "prov": "prov:8c73e6d6bb2288db"
    },
    {
      "id": "node:d9ce5cc74af8b52b84db",
      "kind": "file",
      "label": "templates/human/about.html",
      "path": "templates/human/about.html",
      "symbol": null,
      "tags": [],
      "prov": "prov:d708c9a6f9c7a4e1"
    },
    {
      "id": "node:de09c473f13049315d86",
      "kind": "markdown_section",
      "label": "For AI Agents",
      "path": "README.md",
      "symbol": "README.md#For AI Agents",
      "tags": [],
      "prov": "prov:febd8e67289848a5"
    },
    {
      "id": "node:dfcc83f7d703feeeb739",
      "kind": "javascript_function",
      "label": "handleMcpRequest",
      "path": "worker/mcp/server.js",
      "symbol": "worker.mcp.server.handleMcpRequest",
      "tags": [],
      "prov": "prov:d4fca002d18768a3"
    },
    {
      "id": "node:e1a4bf92d1b32f2f503d",
      "kind": "config",
      "label": "package.json",
      "path": "package.json",
      "symbol": null,
      "tags": [],
      "prov": "prov:2dd83ff0e39c11a0"
    },
    {
      "id": "node:e7345e7cd914f8193bad",
      "kind": "python_class",
      "label": "PublicContractTest",
      "path": "tests/test_public_contract.py",
      "symbol": "tests.test_public_contract.PublicContractTest",
      "tags": [],
      "prov": "prov:68215659b11025db"
    },
    {
      "id": "node:e9b715af08c3796f163a",
      "kind": "file",
      "label": "templates/base.html",
      "path": "templates/base.html",
      "symbol": null,
      "tags": [],
      "prov": "prov:ee829ba44efd1573"
    },
    {
      "id": "node:ea7151a0d793d431ee03",
      "kind": "config",
      "label": "api/v1/capabilities.json",
      "path": "api/v1/capabilities.json",
      "symbol": null,
      "tags": [],
      "prov": "prov:2d042fe8ddc59861"
    },
    {
      "id": "node:eb81b518d5b754dbbb1c",
      "kind": "python_function",
      "label": "copy_worker_and_assets",
      "path": "scripts/build.py",
      "symbol": "scripts.build.copy_worker_and_assets",
      "tags": [],
      "prov": "prov:9481ce0cfa8e70ee"
    },
    {
      "id": "node:f0fd663527865f98c64e",
      "kind": "markdown_section",
      "label": "Short Version",
      "path": "prompt/represent_me.md",
      "symbol": "prompt/represent_me.md#Short Version",
      "tags": [],
      "prov": "prov:0cdbbafa93443ece"
    },
    {
      "id": "node:f4c3da775ce6da003096",
      "kind": "file",
      "label": "templates/human/contact.html",
      "path": "templates/human/contact.html",
      "symbol": null,
      "tags": [],
      "prov": "prov:f523135dd3a150eb"
    },
    {
      "id": "node:f4ebd3edbda8af591795",
      "kind": "javascript_function",
      "label": "isRetiredRoute",
      "path": "worker/index.js",
      "symbol": "worker.isRetiredRoute",
      "tags": [],
      "prov": "prov:2dcc1d86bdf9caef"
    },
    {
      "id": "node:f54782f22cfead583755",
      "kind": "python_function",
      "label": "test_article_surfaces_are_not_publicly_generated",
      "path": "tests/test_public_contract.py",
      "symbol": "tests.test_public_contract.test_article_surfaces_are_not_publicly_generated",
      "tags": [],
      "prov": "prov:57d8fa55e2ac07dc"
    },
    {
      "id": "node:f8af01263ce1ce0eb232",
      "kind": "config",
      "label": "api/v1/case_studies.json",
      "path": "api/v1/case_studies.json",
      "symbol": null,
      "tags": [],
      "prov": "prov:ee7225f24bd44bef"
    },
    {
      "id": "node:f918107b9b1786323a79",
      "kind": "markdown_section",
      "label": "Build the site (fails closed if Python/Jinja dependencies are unavailable)",
      "path": "README.md",
      "symbol": "README.md#Build the site (fails closed if Python/Jinja dependencies are unavailable)",
      "tags": [],
      "prov": "prov:73f52603d0cdfc2b"
    },
    {
      "id": "node:fa185c6d6a01601f4ad9",
      "kind": "python_function",
      "label": "load_data",
      "path": "scripts/build.py",
      "symbol": "scripts.build.load_data",
      "tags": [],
      "prov": "prov:3d83ede3836e30ff"
    },
    {
      "id": "node:fc16f9421e5f3a2683ad",
      "kind": "python_function",
      "label": "test_machine_readable_surfaces_match_humble_positioning",
      "path": "tests/test_public_contract.py",
      "symbol": "tests.test_public_contract.test_machine_readable_surfaces_match_humble_positioning",
      "tags": [],
      "prov": "prov:cea811488559294c"
    },
    {
      "id": "node:fcbe6669d86356de0639",
      "kind": "markdown_section",
      "label": "leonbreukelman.engineer",
      "path": "README.md",
      "symbol": "README.md#leonbreukelman.engineer",
      "tags": [],
      "prov": "prov:11a91e2a1f50280f"
    },
    {
      "id": "node:fd13909968f5b768873a",
      "kind": "python_function",
      "label": "test_agent_card_skills_match_mcp_tools_without_recruiter_tools",
      "path": "tests/test_public_contract.py",
      "symbol": "tests.test_public_contract.test_agent_card_skills_match_mcp_tools_without_recruiter_tools",
      "tags": [],
      "prov": "prov:770f5651b8fc3486"
    }
  ],
  "import_edges": [
    {
      "id": "edge:33fbf5bf92644bc817be",
      "from_node_id": "node:d1ab9b8e0eb01b071904",
      "from_symbol": "scripts.check-public-links",
      "to_node_id": "node:python_import:sys",
      "label": "sys",
      "prov": [
        "prov:d75786183ab35e5a"
      ]
    },
    {
      "id": "edge:388a8b7993d965c68760",
      "from_node_id": "node:d8fc3a88afab17188e7b",
      "from_symbol": "scripts.build",
      "to_node_id": "node:python_import:pathlib",
      "label": "pathlib",
      "prov": [
        "prov:8ae860e02f73b5c8"
      ]
    },
    {
      "id": "edge:441cff0e4e2068950a2e",
      "from_node_id": "node:8a344356f5d23c2baf2e",
      "from_symbol": "tests.test_public_contract",
      "to_node_id": "node:python_import:pathlib",
      "label": "pathlib",
      "prov": [
        "prov:747bd5322f141fd0"
      ]
    },
    {
      "id": "edge:6b44a5c20c6e117b730f",
      "from_node_id": "node:d1ab9b8e0eb01b071904",
      "from_symbol": "scripts.check-public-links",
      "to_node_id": "node:python_import:argparse",
      "label": "argparse",
      "prov": [
        "prov:79fcec2ced8fd3ac"
      ]
    },
    {
      "id": "edge:851853794ca6b3577958",
      "from_node_id": "node:d1ab9b8e0eb01b071904",
      "from_symbol": "scripts.check-public-links",
      "to_node_id": "node:python_import:urllib.error",
      "label": "urllib.error",
      "prov": [
        "prov:c6777f2e098ec6be"
      ]
    },
    {
      "id": "edge:8c4136c418c6409fda59",
      "from_node_id": "node:d8fc3a88afab17188e7b",
      "from_symbol": "scripts.build",
      "to_node_id": "node:python_import:shutil",
      "label": "shutil",
      "prov": [
        "prov:38ce7fc35ba61db2"
      ]
    },
    {
      "id": "edge:91ec4fe104cfdad1e4a5",
      "from_node_id": "node:d1ab9b8e0eb01b071904",
      "from_symbol": "scripts.check-public-links",
      "to_node_id": "node:python_import:pathlib",
      "label": "pathlib",
      "prov": [
        "prov:f3a3ac6792232d99"
      ]
    },
    {
      "id": "edge:97760ba88c0882f324c7",
      "from_node_id": "node:d1ab9b8e0eb01b071904",
      "from_symbol": "scripts.check-public-links",
      "to_node_id": "node:python_import:urllib.request",
      "label": "urllib.request",
      "prov": [
        "prov:6d95e66efa505ecc"
      ]
    },
    {
      "id": "edge:9b853eb4121c2243cd48",
      "from_node_id": "node:d8fc3a88afab17188e7b",
      "from_symbol": "scripts.build",
      "to_node_id": "node:python_import:datetime",
      "label": "datetime",
      "prov": [
        "prov:667b089a4eb82688"
      ]
    },
    {
      "id": "edge:b181574c40dfcf5e7dcb",
      "from_node_id": "node:d8fc3a88afab17188e7b",
      "from_symbol": "scripts.build",
      "to_node_id": "node:python_import:jinja2",
      "label": "jinja2",
      "prov": [
        "prov:b282fbda2c978640"
      ]
    },
    {
      "id": "edge:b737ca69635863da5448",
      "from_node_id": "node:d1ab9b8e0eb01b071904",
      "from_symbol": "scripts.check-public-links",
      "to_node_id": "node:python_import:re",
      "label": "re",
      "prov": [
        "prov:e05036e1893e81e5"
      ]
    },
    {
      "id": "edge:c0257a7115256fd1910a",
      "from_node_id": "node:d1ab9b8e0eb01b071904",
      "from_symbol": "scripts.check-public-links",
      "to_node_id": "node:python_import:__future__",
      "label": "__future__",
      "prov": [
        "prov:678954e744a8969e"
      ]
    },
    {
      "id": "edge:c76b6dc305ff9cdce347",
      "from_node_id": "node:d8fc3a88afab17188e7b",
      "from_symbol": "scripts.build",
      "to_node_id": "node:python_import:json",
      "label": "json",
      "prov": [
        "prov:bc8741f77a077338"
      ]
    },
    {
      "id": "edge:cb8c70dbdd3ae0ad7c7d",
      "from_node_id": "node:8a344356f5d23c2baf2e",
      "from_symbol": "tests.test_public_contract",
      "to_node_id": "node:python_import:unittest",
      "label": "unittest",
      "prov": [
        "prov:d8dd17a2ee96a5fb"
      ]
    },
    {
      "id": "edge:d2435ec62539194b264f",
      "from_node_id": "node:8a344356f5d23c2baf2e",
      "from_symbol": "tests.test_public_contract",
      "to_node_id": "node:python_import:subprocess",
      "label": "subprocess",
      "prov": [
        "prov:48326432df32a394"
      ]
    },
    {
      "id": "edge:d85d006494d06cd126dc",
      "from_node_id": "node:8a344356f5d23c2baf2e",
      "from_symbol": "tests.test_public_contract",
      "to_node_id": "node:python_import:json",
      "label": "json",
      "prov": [
        "prov:6e7cd6fd5e6e5f51"
      ]
    },
    {
      "id": "edge:ee74e56eeab2c21d6122",
      "from_node_id": "node:32f3a0d3845cf98fb8cb",
      "from_symbol": "worker",
      "to_node_id": "node:javascript_import:worker.mcp.server",
      "label": "worker.mcp.server",
      "prov": [
        "prov:47b71b23b6c02da8"
      ]
    }
  ],
  "surfaces": {
    "protected": [],
    "generated": []
  },
  "source_docs": [
    {
      "path": "README.md",
      "excerpt": "# leonbreukelman.engineer\n\nAI-first public presence for making messy cloud, security, infrastructure, and agent-tooling systems easier to reason about. Humans get a concise site; agents get the same public facts through JSON, llms.txt, well-known metadata, and MCP.\n\n## Quick Start\n\n```bash\n# Install dependencies\nnpm install\n\n# Build the site (fails closed if Python/Jinja dependencies are unavailable)\nnpm run build\n\n# Preview locally\nnpm run preview\n\n# Deploy to Cloudflare Pages\nnpm run deploy\n```\n\n## Structure\n\n```\n/api/v1/          - Structured JSON data for profile, offers, case studies, projects, and capabilities\n/prompt/          - Agent representation instructions\n/.well-known/     - Discovery protocols (ai.json, agent-card.json)\n/human/           - Human-readable HTML pages\n/worker/mcp/      - MCP server endpoint (Cloudflare Worker)\n/llms.txt         - LLM crawler instructions\n```\n\n## For AI Agents\n\nStart at `/llms.txt` or `/.well-known/ai.json` for discovery.\n\n## For Humans\n\nNavigate to `/human/` for the traditional web surface.\n\n## Deployment\n\nRequires:\n- `CLOUDFLARE_API_TOKEN` - API token with Pages:Edit and DNS:Edit permissions\n- `CLOUDFLARE_ACCOUNT_ID` - Your Cloudflare account ID\n\nSet these as environment variables or in a `.env` file.\n\n## Development\n\nThe site is built from JSON data in `/api/v1/`. Edit those files to update content, then rebuild.\n\n`npm run build` runs the Python static-site generator (`scripts/build.py`). It fails closed if dependencies are missing so stale fallback output cannot accidentally republish removed public surfaces. Install Python dependencies with `python3 -m pip install -r scripts/requirements.txt` if needed.\n\nTemplates are in `/templates/`. Public pages are generated from the JSON data and the offer/work/about/contact templates.\n"
    },
    {
      "path": "package.json",
      "excerpt": "{\n  \"name\": \"leonbreukelman-engineer\",\n  \"version\": \"1.0.0\",\n  \"description\": \"AI-first professional presence for Leon Breukelman\",\n  \"scripts\": {\n    \"build\": \"bash scripts/build-site.sh\",\n    \"deploy\": \"npm run build && wrangler pages deploy dist --project-name=leonbreukelman-engineer\",\n    \"dev\": \"wrangler pages dev dist\",\n    \"preview\": \"npm run build && wrangler pages dev dist\",\n    \"check:links\": \"python3 scripts/check-public-links.py\"\n  },\n  \"author\": \"Leon Breukelman\",\n  \"license\": \"MIT\",\n  \"devDependencies\": {\n    \"wrangler\": \"^4.0.0\"\n  }\n}\n"
    }
  ]
}
