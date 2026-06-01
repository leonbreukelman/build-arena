# Opus Review — Project Decomposer Plan

Reviewer: Claude Opus 4.8 via Claude Code
Mode: read-only architecture review
Artifact source: `/tmp/build-arena-decomposer-plan-opus-review.json`
Cost reported by Claude Code: 0.8957392500000001 USD-equivalent

## Verdict

ACCEPT_WITH_CHANGES

## Blocking changes

1. Split coverage into source coverage and excluded-with-typed-reason so the model cannot hit 100% by silently dumping tracked files into an orphan bucket.
2. Add validation for fabricated checks and edges: command path references, contract/gap component references, excluded-file reasons, and rollback stop conditions.
3. Derive arena-calibration facts from `manifest.yaml` ground truth instead of hardcoding prose, especially the F3 patch-generalization gap.

## Tests Opus asked to add

- Coverage totality: every tracked file is owned exactly once or excluded with reason.
- Check path resolution failure.
- Byte-identical deterministic JSON double-run.
- Raw-byte hashing mutation test.
- Git subdir root handling.
- Dirty tree disk-hash reporting.
- Non-git fallback with same denylist.
- Negative validation tests for each rule.
- F3 derivation from manifest ground truth.
- No execution during decomposition other than read-only git.
- CLI stdout/file/fail-on-gap behavior.

## Implementation pitfalls to address

- `git ls-files` from a subdirectory can silently scope inventory; resolve to toplevel.
- Disk-hash vs git-blob mismatch on dirty trees must be represented.
- Hash raw bytes, not text.
- Filesystem fallback must mirror denylist rules.
- Fresh or detached git states must not crash incorrectly.
- Avoid machine-specific absolute paths in canonical output when cross-machine determinism matters.

## Revised acceptance criteria adopted

1. Generic reusable scanner/model/validator with git/fs inventory, byte SHA-256, rule-based exclusions, exactly-one-owner, source coverage, canonical JSON, and CLI.
2. Determinism, hashing, and no-execution guarantees proven by tests.
3. Arena detector derives F3 gap and contract directions from on-disk manifests.
4. Real arena-calibration output validates with zero unowned included files, typed exclusions, contracts, checks/gaps, and traceable F3 gap.
5. Local tests, lint, and typecheck pass.
