# Method file topology — global core, local override

This scaffold has five file kinds and three audiences. The split is what makes the method global yet locally modifiable: the invariant core can be synced everywhere, while only the project card changes per repo.

| File | Scope | Audience | Edited per repo? | Overwritten by sync? |
|---|---|---|---|---|
| `docs/method/METHOD.md` | Global invariant contract | Agent loads first | Never | Yes |
| `docs/method/PROJECT.md` | Local instantiation | Agent loads second | Yes | No, unless explicitly regenerated |
| `docs/method/DESIGN-RECORD.md` | Local history/rationale | Operator + architect | As needed | No |
| `docs/specs/TEMPLATE-track-*.md` | Global templates | Spec authors | Never | Yes |
| `docs/specs/YYYY-MM-DD-*.md` | Local turn specs | Agent per turn | New per turn | No |

## Override rule

`PROJECT.md` may add constraints and fill slots. It may not loosen `METHOD.md`. If a repo needs a looser lifecycle, update the global method deliberately and record the rationale in `DESIGN-RECORD.md`.

## AGENTS.md load hook

The installer adds this line exactly once:

`Before starting any task, load docs/method/METHOD.md then docs/method/PROJECT.md and treat both as binding.`

That hook is intentionally small. The skill using this scaffold must still read the two files before planning.

## Distribution

Preferred first install path:

```bash
python3 ~/.hermes/skills/software-development/repo-project-bootstrap/scripts/install_method_scaffold.py /path/to/repo --mode local-scaffold --json
```

`docs/method/sync-method.sh` is a self-contained update helper for repos that already contain the canonical layout. It preflights sources before writing and preserves existing local files.

## Onboarding checklist

1. Run the installer in `--dry-run`.
2. Run the installer for real.
3. Read `docs/method/PROJECT.md` and fill/adjust any repo-specific open decisions.
4. Confirm AGENTS.md load hook exists exactly once.
5. First real work turn: write a dated spec under `docs/specs/` from Track L or Track F.
6. If CI is absent, make adding CI a first follow-up before claiming `github-pr` governance.
