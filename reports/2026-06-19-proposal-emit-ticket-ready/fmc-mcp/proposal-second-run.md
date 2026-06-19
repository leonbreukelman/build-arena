# Component MCPClient has no observable check

## What & where

Intent:

Add or prepare an observable, repository-grounded check for component finding code.component.untested.comp:client: Component MCPClient has no observable check. Limit changes to the component target path set: src/fmc_mcp/client.py.

Target paths:
- `src/fmc_mcp/client.py`

## Why

Evidence refs:

```json
[
  {
    "checked": true,
    "componentId": "comp:client",
    "kind": "component"
  },
  {
    "checked": true,
    "kind": "absence",
    "path": "iterationReadiness.componentProfiles"
  },
  {
    "checked": true,
    "kind": "owned_surface",
    "path": "src/fmc_mcp/client.py"
  },
  {
    "checked": true,
    "kind": "provenance",
    "ref": "prov:bcfd8e782d7fe500"
  }
]
```

Source recommended action:

Add an observable check (e.g. a focused test) covering MCPClient before mutating it.

## Definition of done

The component target path set (src/fmc_mcp/client.py) is covered by a bounded change and the project's load-bearing quality gate commands pass.

## Constraints / guardrails

- Prefer a focused test or minimal code-facing verification improvement over broad refactors.
- Do not silence failures or remove behavior to make the gate pass.
- Use only repository-grounded files and commands from the intake quality gates.

## How to verify

- `uv run --extra dev mypy src/fmc_mcp`
- `uv run --extra dev python -m pytest -q`
- `uv run --extra dev ruff check .`

## Priority & source

Priority score: 540.0
Finding ID: `code.component.untested.comp:client`
