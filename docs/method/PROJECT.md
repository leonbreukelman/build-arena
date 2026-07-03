# Project Card — build-arena

Local instantiation of `docs/method/METHOD.md`. This is the only method file edited per repo. It may select a globally defined lifecycle mode and add stricter constraints; it may not loosen the global contract.

Generated: 2026-07-02

## Lifecycle mode

`local-scaffold`

Mode notes:
Local scaffold only. No push/PR/merge/deploy implied. Structural ledger is sufficient for scaffold installation.

## Protected / frozen paths

None declared yet. Add frozen/generated/security-critical paths here before `github-pr` work.

## Gate commands

- `uv run pytest`
- `make test`

## CI

present — workflows detected: ci.yml

## Connector scope

GitHub origin detected. Installer did not verify write scope or branch protection.

## Secrets / provider contract

No secret values belong in repo docs. Only env-var names may be listed here.

No repo-specific env-var names discovered by installer. Add names only, never values.

## Exit codes

No repo-specific exit-code contract declared yet.

## Escalation wiring

- Claude Code CLI: available
- Grok CLI: available
- Copilot CLI: available
- Fable: use only after explicit preflight; never silently substitute another model.

## Pairing

Implementer: Hermes Agent / delegated coding agent within scope.
Certifier/reviewer: Claude Code Opus by default; Fable only after preflight or explicit Tier-4 escalation.
Verifier: Hermes/Leon flow checks ledger against live evidence.

## Current repo facts

- Repo path: `/home/leonb/projects/build-arena`
- Git root: `/home/leonb/projects/build-arena`
- Base SHA at install: `b76d3bb65a5bdb122cb84d86cc4d0378f76faa79`
- Origin: `git@github.com:leonbreukelman/build-arena.git`

## Open decisions

- Confirm protected paths.
- Confirm final gate commands.
- Add CI before `github-pr` governance if CI is absent.
- Verify connector write scope before PR lifecycle work.
