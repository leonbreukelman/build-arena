# Hermes / OpenShell delegation packet dry-run

Date: 2026-07-02
Status: smallest first step, dry-run only

## Purpose

This slice defines the first maintainer-side packet between Hermes and a future runtime enforcement layer.

Architecture boundary:

- Hermes is the maintainer brain and policy router.
- OpenShell is the future runtime enforcement layer.
- OpenHands/Codex are delegated coding workers.
- This implementation only renders dry-run artifacts. It does not execute OpenHands, does not create a live OpenShell sandbox, does not call GitHub, and does not apply, promote, push, or merge code.

## Requirements implemented

1. Define a Pydantic `TaskPacket` model for delegated maintainer work.
2. Validate objective, mode, allowed paths, forbidden paths, required reads, required commands, and stop conditions.
3. Restrict this first packet mode to `dry_run`.
4. Reject semantic requests for target apply/promote, auto-merge, git push, and broad live autonomy.
5. Reject allowed write path intent that overlaps forbidden write path intent, including protected Build Arena surfaces such as `scorer/`, `verifier/`, `schema/`, `arena/generated/`, and `.arena/scorer.lock.toml`.
6. Render `task.md` for a delegated worker.
7. Render `openshell-policy.yaml` as a future runtime policy artifact.
8. Render `runner-command.sh` as a dry-run command artifact only.
9. Return policy status fields:
   - `execution: not_run`
   - `runtime: openshell_planned`
   - `verification_owner: hermes`
   - `verification_status: not_verified`
10. Cover allowed task, forbidden path overlap, target apply/promote phrase, git push phrase, broad autonomy phrase, and generated OpenShell policy stub in tests.
11. Provide `python -m arena.maintainer.cli prepare --packet <packet.json> --out <bundle-dir>` to generate a dry-run bundle from the terminal.
12. Return exit code `0` for valid policy-allowed bundles, `2` for valid policy-rejected bundles, and `1` for invalid input, usage, or write-safety failures.
13. Make write-safety failures take precedence over policy rejection. The CLI refuses to overwrite existing bundles unless `--force` is passed, and refuses unknown files even with `--force`.
14. Render deterministic bundle artifacts with a `manifest.json` using `sha256` over on-disk artifact bytes excluding `manifest.json` itself.

## Packet model

`arena.maintainer.task_packet.TaskPacket` is a strict Pydantic model with these fields:

- `schema_version`: fixed to `maintainer-task-packet/v0`.
- `objective`: non-blank task objective.
- `mode`: fixed to `dry_run`.
- `allowed_paths`: non-empty repository-relative write-intent paths.
- `forbidden_paths`: repository-relative path intent that must not be written.
- `required_reads`: non-empty repository-relative read prerequisites.
- `required_commands`: non-empty verification commands Hermes expects to own.
- `stop_conditions`: non-empty conditions that halt the delegated task.

Paths are repository-relative and may not traverse upward. Required reads cannot be listed as forbidden paths.

## Policy split

Hermes policy is semantic authorization. It decides whether the task objective, command intent, stop conditions, and write-intent paths fit Build Arena's propose-only maintainer boundaries.

OpenShell policy is runtime enforcement. In this slice, Build Arena only renders a generated draft `openshell-policy.yaml` with intended read/write paths, forbidden paths, network egress, inference routing, and process restrictions. The draft is not applied and does not create a sandbox.

## Rendered artifacts

- `render_task_markdown(packet)` renders a deterministic `task.md` body for a delegated worker.
- `render_openshell_policy(packet)` renders a commented `openshell-policy.yaml` draft with filesystem, network, inference, process, and verification intent.
- `render_runner_command(packet)` renders a non-executable `runner-command.sh` dry-run preview marked `GENERATED -- DO NOT EXECUTE`.

## CLI bundle workflow

The terminal entry point is:

```sh
uv run python -m arena.maintainer.cli prepare --packet packet.json --out .arena/maintainer-runs/example
```

The command validates the packet, evaluates Hermes semantic policy, and writes:

- `packet.json`
- `policy-result.json`
- `task.md`
- `openshell-policy.yaml`
- `runner-command.sh`
- `manifest.json`

The CLI never runs the generated command, never executes OpenHands, never creates an OpenShell sandbox, never calls GitHub, and never applies, promotes, pushes, or merges. `runner-command.sh` is intentionally non-executable so the bundle cannot be mistaken for an execution instruction.

If a packet is valid but policy-rejected, the CLI still writes the auditable bundle and exits `2`. If the output path is unsafe or unwritable, the CLI exits `1` and does not install a partial bundle. Usage errors also exit `1` so exit `2` is reserved for semantic policy rejection.

## Non-goals

- No SWE-agent integration.
- No OpenHands execution.
- No live OpenShell sandbox.
- No GitHub API calls.
- No push, merge, apply, promote, or target repository mutation.
- No claim that OpenShell enforcement exists yet.
