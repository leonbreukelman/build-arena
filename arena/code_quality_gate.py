"""Load-bearing code-quality gate for Build Arena (epic #25, Phase 3, issue #29).

The single biggest risk for a non-documentation proposal domain is a *shallow
gate*: a change that "passes" without actually improving the code — a no-op diff,
or silencing a linter with a suppression instead of fixing the underlying issue.
This gate exists to make that impossible for the code-quality domain.

It compares deterministic ruff violation counts for one file between the git
HEAD baseline and the current working tree, and ACCEPTS only when:

- the file still parses as Python (no syntax destruction to zero out warnings),
- no public top-level symbol (function/class/public assignment) was removed
  (no deleting code to drop the count),
- the violation count strictly decreased, and
- no new lint-suppression markers (noqa / type-ignore comments, or file-level
  ``ruff: noqa`` / ``flake8: noqa`` directives) were added.

KNOWN BOUNDARY (not a full behaviour gate): this proves a real *lint* reduction
that preserves the public symbol set; it does NOT prove runtime behaviour is
unchanged, and it only inspects the single target file (a violation moved to
another file is not seen here). A behaviour/test gate is layered separately by
the candidate runner via the project's configured test command; this gate is
the lint-quality component of that stack, not the whole of it.

Everything else fails closed with an explicit reason. No live providers, no
network; ruff is the project's already-pinned linter and is run against the
target repo's own config (with ``--no-cache``) so before/after are measured on
the same ruleset without polluting the repo.
"""

from __future__ import annotations

import argparse
import ast
import io
import json
import re
import subprocess
import tokenize
from dataclasses import dataclass
from pathlib import Path

# Matches a lint-suppression directive inside a Python *comment token* (string
# literals are excluded by tokenizing first). Covers per-line noqa, ruff/flake8
# file-level directives, and type-ignore comments.
_SUPPRESSION_RE = re.compile(
    r"#\s*(?:(?:ruff|flake8)\s*:\s*)?(?:noqa\b|type:\s*ignore\b)",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class CodeQualityGateResult:
    ok: bool
    reason: str
    path: str
    violations_before: int
    violations_after: int
    suppressions_before: int
    suppressions_after: int

    def to_jsonable(self) -> dict[str, object]:
        return {
            "ok": self.ok,
            "reason": self.reason,
            "path": self.path,
            "violationsBefore": self.violations_before,
            "violationsAfter": self.violations_after,
            "suppressionsBefore": self.suppressions_before,
            "suppressionsAfter": self.suppressions_after,
        }


def evaluate_code_quality_gate(repo: str | Path, rel_path: str) -> CodeQualityGateResult:
    repo_path = Path(repo).resolve()
    target = repo_path / rel_path

    def result(ok: bool, reason: str, *, vb: int = -1, va: int = -1, sb: int = -1, sa: int = -1) -> CodeQualityGateResult:
        return CodeQualityGateResult(ok, reason, rel_path, vb, va, sb, sa)

    if not target.is_file():
        return result(False, "missing_file")

    baseline = _git_show_head(repo_path, rel_path)
    if baseline is None:
        # No committed baseline -> cannot prove improvement. Fail closed.
        return result(False, "no_baseline")

    working = target.read_text(encoding="utf-8")

    # A change that "fixes" lint by destroying parseable Python is not an improvement.
    if not _is_valid_python(working):
        return result(False, "invalid_python")

    # A change that drops the violation count by deleting real code (functions,
    # classes, public assignments) is not an improvement. The public top-level
    # symbol set must not shrink. This is a behaviour backstop for the lint-only
    # delta — it does not prove behaviour preservation (a separate test gate
    # would), but it blocks the cheap "delete the warning away" gaming.
    removed_symbols = _removed_public_symbols(baseline, working)
    if removed_symbols:
        return result(False, "public_symbols_removed")

    suppressions_before = _count_suppressions(baseline)
    suppressions_after = _count_suppressions(working)
    if suppressions_after > suppressions_before:
        return result(
            False,
            "suppression_gaming",
            vb=_ruff_violations(repo_path, rel_path, baseline),
            va=_ruff_violations(repo_path, rel_path, working),
            sb=suppressions_before,
            sa=suppressions_after,
        )

    violations_before = _ruff_violations(repo_path, rel_path, baseline)
    violations_after = _ruff_violations(repo_path, rel_path, working)
    if violations_after >= violations_before:
        return result(
            False,
            "no_improvement",
            vb=violations_before,
            va=violations_after,
            sb=suppressions_before,
            sa=suppressions_after,
        )

    return result(
        True,
        "improved",
        vb=violations_before,
        va=violations_after,
        sb=suppressions_before,
        sa=suppressions_after,
    )


def _git_show_head(repo: Path, rel_path: str) -> str | None:
    proc = subprocess.run(
        ["git", "show", f"HEAD:{rel_path}"],
        cwd=repo,
        text=True,
        capture_output=True,
        check=False,
    )
    if proc.returncode != 0:
        return None
    return proc.stdout


def _is_valid_python(source: str) -> bool:
    try:
        ast.parse(source)
    except SyntaxError:
        return False
    return True


def _public_symbols(source: str) -> set[str] | None:
    """Top-level public symbol names (functions, classes, assigned names that do
    not start with '_'). Returns None if the source does not parse."""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return None
    names: set[str] = set()
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            if not node.name.startswith("_"):
                names.add(node.name)
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and not target.id.startswith("_"):
                    names.add(target.id)
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) and not node.target.id.startswith("_"):
            names.add(node.target.id)
    return names


def _removed_public_symbols(baseline: str, working: str) -> set[str]:
    """Public top-level symbols present in baseline but absent from working.

    If either side fails to parse the baseline-symbol comparison is skipped
    (the invalid_python check already handles an unparseable working tree)."""
    before = _public_symbols(baseline)
    after = _public_symbols(working)
    if before is None or after is None:
        return set()
    return before - after


def _count_suppressions(source: str) -> int:
    """Count lint-suppression directives in real Python comments only.

    Tokenizing first means a ``# noqa`` that appears inside a string literal is
    NOT counted (avoids false-positive ``suppression_gaming`` on a legit fix that
    merely mentions noqa in a message). If the source cannot be tokenized (e.g.
    mid-edit), fall back to a line-wise regex scan so the gate still fails closed
    rather than under-counting."""
    try:
        comments = [
            token.string
            for token in tokenize.generate_tokens(io.StringIO(source).readline)
            if token.type == tokenize.COMMENT
        ]
    except (tokenize.TokenError, IndentationError, SyntaxError):
        return len(_SUPPRESSION_RE.findall(source))
    return sum(1 for comment in comments if _SUPPRESSION_RE.search(comment))


def _ruff_violations(repo: Path, rel_path: str, source: str) -> int:
    """Count ruff violations for ``source`` as if it lived at ``rel_path`` in
    ``repo`` (so the repo's ruff config and per-path rules apply)."""
    proc = subprocess.run(
        ["ruff", "check", "--no-cache", "--output-format", "json", "--stdin-filename", rel_path, "-"],
        cwd=repo,
        input=source,
        text=True,
        capture_output=True,
        check=False,
    )
    stdout = proc.stdout.strip()
    if not stdout:
        # ruff emits nothing on stdout only when it failed to run; treat as a
        # high violation count so a broken run can never read as "improved".
        if proc.returncode not in (0, 1):
            return 1_000_000
        return 0
    try:
        violations = json.loads(stdout)
    except json.JSONDecodeError:
        return 1_000_000
    return len(violations) if isinstance(violations, list) else 1_000_000


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m arena.code_quality_gate")
    parser.add_argument("--repo", default=".")
    parser.add_argument("--path", required=True)
    args = parser.parse_args(argv)
    result = evaluate_code_quality_gate(args.repo, args.path)
    print(json.dumps(result.to_jsonable(), indent=2, sort_keys=True))
    return 0 if result.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
