# Maintainer OpenShell preflight dogfood report

Date: 2026-07-02
Status: passed for dry-run/read-only preflight

## Scope

This dogfood run used the Build Arena maintainer CLI to prepare a dry-run OpenShell preflight bundle, then ran only read-only OpenShell CLI inspection/prerequisite commands.

No OpenShell sandbox was created. No OpenShell policy was applied. No OpenHands worker was executed. No GitHub command was run. No push, merge, apply, promote, or target-repo mutation was performed.

## Input packet

Packet path:

```text
docs/examples/maintainer-openshell-preflight-packet.json
```

Bundle command:

```sh
uv run python -m arena.maintainer.cli prepare --packet docs/examples/maintainer-openshell-preflight-packet.json --out .arena/maintainer-runs/openshell-preflight --force
```

Bundle command output:

```text
bundle written: .arena/maintainer-runs/openshell-preflight
policy allowed: True
```

Bundle path:

```text
.arena/maintainer-runs/openshell-preflight
```

Bundle files:

```text
manifest.json
openshell-policy.yaml
packet.json
policy-result.json
runner-command.sh
task.md
```

## Bundle inspection

`policy-result.json`:

```json
{
  "allowed": true,
  "execution": "not_run",
  "reasons": [],
  "runtime": "openshell_planned",
  "verification_owner": "hermes",
  "verification_status": "not_verified"
}
```

`manifest.json`:

```json
{
  "artifacts": [
    {
      "path": "openshell-policy.yaml",
      "sha256": "00b5f4a4a4a4267c2a377a52d24818437df9f73cbf04615cdda2915723c93556"
    },
    {
      "path": "packet.json",
      "sha256": "9825e9c0e1ce8e903c5179169105e58f24b278ff58c367b03f0c825204ae58ea"
    },
    {
      "path": "policy-result.json",
      "sha256": "a53ad69d625238d9d5e60b535399f41d44e7d3ce21daf0af90cf6dd7f278f2c6"
    },
    {
      "path": "runner-command.sh",
      "sha256": "0d5bf3f750b0f603649fb3ebc08af6acb5ece6c29ee073c656816d1fe80501ff"
    },
    {
      "path": "task.md",
      "sha256": "aa3d3ffb9bb6b3f2098bf4cf0bcd0b8838ae5a9c16394711cd364ad051d245a0"
    }
  ],
  "execution": "not_run",
  "hashAlgorithm": "sha256",
  "hashScope": "on-disk artifact bytes excluding manifest.json",
  "packetSchemaVersion": "maintainer-task-packet/v0",
  "policyAllowed": true,
  "policyReasons": [],
  "runtime": "openshell_planned",
  "schemaVersion": "maintainer-delegation-bundle/v0",
  "verificationOwner": "hermes",
  "verificationStatus": "not_verified"
}
```

`openshell-policy.yaml`:

```yaml
# GENERATED DRAFT: Build Arena maintainer dry-run OpenShell policy intent.
# NOT APPLIED: this artifact does not create or enter a live OpenShell sandbox.
# Hermes policy is semantic authorization; OpenShell is the future runtime enforcement layer.
version: openshell-policy-draft/v0
status: generated_draft_not_applied
runtime:
  kind: openshell_planned
  execution: not_run
filesystem:
  read_intent:
    - "AGENTS.md"
    - "docs/method/METHOD.md"
    - "docs/method/PROJECT.md"
    - "README.md"
    - "docs/specs/2026-07-02-hermes-openshell-delegation-packet.md"
  write_intent:
    - ".arena/maintainer-runs/openshell-preflight"
    - "docs/examples/maintainer-openshell-preflight-packet.json"
    - "reports/2026-07-02-maintainer-openshell-preflight-dogfood.md"
  forbidden_path_intent:
    - "scorer"
    - "verifier"
    - "schema"
    - "arena/generated"
    - ".arena/scorer.lock.toml"
network:
  egress_intent: none
  allow_github: false
inference:
  routing_intent: delegated_worker_no_live_provider_call_in_this_slice
  live_model_required: false
process_restrictions:
  dry_run_only: true
  execute_openshell: false
  execute_openhands: false
  git_push: false
  auto_merge: false
  target_apply_or_promote: false
verification:
  owner: hermes
  status: not_verified
```

`runner-command.sh` mode:

```text
0o644
```

The runner command is non-executable and the policy artifact is marked `generated_draft_not_applied`.

## OpenShell commands executed

Only these read-only inspection/prerequisite commands were run:

- `openshell --help`
- `openshell policy --help`
- `openshell status --help`
- `openshell doctor --help`
- `openshell doctor check`

No `openshell sandbox create`, `openshell gateway start`, or `openshell policy set` command was run.

## Command evidence

### openshell --help

Exit code: `0`

```text
OpenShell CLI tool

USAGE
  openshell <command> <subcommand> [flags]

SANDBOX COMMANDS
  sandbox:     Manage sandboxes
  forward:     Manage port forwarding to a sandbox
  logs:        View sandbox logs
  policy:      Manage sandbox policy
  provider:    Manage provider configuration

GATEWAY COMMANDS
  gateway:     Manage the gateway lifecycle
  status:      Show gateway status and information
  inference:   Manage inference configuration
  doctor:      Diagnose gateway issues

ADDITIONAL COMMANDS
  term:        Launch the OpenShell interactive TUI
  completions: Generate shell completions
  ssh-proxy:   SSH proxy (used by ProxyCommand)
  help:        Print this message or the help of the given subcommand(s)

FLAGS
  -g, --gateway <GATEWAY>
          Gateway name to operate on (resolved from stored metadata) [env: OPENSHELL_GATEWAY=]
      --gateway-endpoint <GATEWAY_ENDPOINT>
          Gateway endpoint URL (e.g. <https://gateway.example.com>). Connects directly without looking up gateway metadata [env: OPENSHELL_GATEWAY_ENDPOINT=]
  -v, --verbose...
          Increase verbosity (-v, -vv, -vvv)
  -h, --help
          Print help
  -V, --version
          Print version

EXAMPLES
  $ openshell sandbox create
  $ openshell gateway start
  $ openshell logs my-sandbox

LEARN MORE
  Use `openshell <command> --help` for more information about a command.
```

### openshell policy --help

Exit code: `0`

```text
Manage sandbox policy

USAGE
  openshell policy [OPTIONS] [COMMAND]

COMMANDS
  set   Update policy on a live sandbox
  get   Show current active policy for a sandbox
  list  List policy history for a sandbox

FLAGS
  -g, --gateway <GATEWAY>
          Gateway name to operate on (resolved from stored metadata) [env: OPENSHELL_GATEWAY=]
      --gateway-endpoint <GATEWAY_ENDPOINT>
          Gateway endpoint URL (e.g. <https://gateway.example.com>). Connects directly without looking up gateway metadata [env: OPENSHELL_GATEWAY_ENDPOINT=]
  -v, --verbose...
          Increase verbosity (-v, -vv, -vvv)
  -h, --help
          Print help
  -V, --version
          Print version


ALIAS
  pol

EXAMPLES
  $ openshell policy get my-sandbox
  $ openshell policy set my-sandbox --policy policy.yaml
  $ openshell policy list my-sandbox
```

### openshell status --help

Exit code: `0`

```text
Show gateway status and information

USAGE
  openshell status [OPTIONS]

GATEWAY FLAGS:
  -g, --gateway <GATEWAY>
          Gateway name to operate on (resolved from stored metadata) [env: OPENSHELL_GATEWAY=]
      --gateway-endpoint <GATEWAY_ENDPOINT>
          Gateway endpoint URL (e.g. <https://gateway.example.com>). Connects directly without looking up gateway metadata [env: OPENSHELL_GATEWAY_ENDPOINT=]

GLOBAL FLAGS:
  -v, --verbose...  Increase verbosity (-v, -vv, -vvv)
  -h, --help        Print help
  -V, --version     Print version
```

### openshell doctor --help

Exit code: `0`

```text
Diagnose gateway issues.

Inspect logs, run commands inside the gateway container, and get AI-assisted debugging guidance. If you are a coding agent, run `openshell doctor llm.txt` for a full diagnostic prompt.

USAGE
  openshell doctor [OPTIONS] [COMMAND]

COMMANDS
  logs     Fetch logs from the gateway container
  exec     Run a command inside the gateway container
  llm.txt  Print a diagnostic prompt for AI-assisted gateway debugging
  check    Validate system prerequisites for running a gateway

FLAGS
  -g, --gateway <GATEWAY>
          Gateway name to operate on (resolved from stored metadata)

          [env: OPENSHELL_GATEWAY=]

      --gateway-endpoint <GATEWAY_ENDPOINT>
          Gateway endpoint URL (e.g. <https://gateway.example.com>). Connects directly without looking up gateway metadata

          [env: OPENSHELL_GATEWAY_ENDPOINT=]

  -v, --verbose...
          Increase verbosity (-v, -vv, -vvv)

  -h, --help
          Print help

  -V, --version
          Print version


ALIAS
  dr

EXAMPLES
  $ openshell doctor check
  $ openshell doctor logs --lines 100
  $ openshell doctor exec -- kubectl get pods -A
  $ openshell doctor llm.txt

AI AGENT USAGE
  If you are a coding agent (LLM) diagnosing a gateway issue, run:

    openshell doctor llm.txt

  This prints a detailed diagnostic prompt with step-by-step instructions
  for debugging gateway clusters using `openshell doctor logs` and
  `openshell doctor exec`.
```

### openshell doctor check

Exit code: `0`

```text
Checking system prerequisites...

  Docker ............. ok (version 29.1.3)
  DOCKER_HOST ........ (not set, using default socket)

All checks passed.
```

## Verdict

Dry-run dogfood passed.

This proves the maintainer CLI can prepare a task-specific OpenShell preflight bundle and the installed OpenShell CLI can be safely inspected without using live sandbox enforcement. It does not prove runtime sandbox isolation, policy application, worker execution, or gateway lifecycle behavior.
