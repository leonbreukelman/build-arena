from __future__ import annotations

from typing import NoReturn

from arena.issue_packager import (
    FabricatedClaimError,
    IssuePackageResult,
    OperatorAuthorizationError,
    package_candidate_issue,
    record_owner_outcome,
    render_issue_body,
)


class PRPackagingRetiredError(RuntimeError):
    pass


def _retired() -> NoReturn:
    raise PRPackagingRetiredError(
        "PR packaging is retired: Build Arena emits GitHub issues only. "
        "Use arena.issue_packager.package_candidate_issue or python -m arena.package_issue."
    )


def render_pr_body(*_args: object, **_kwargs: object) -> str:
    _retired()


def package_candidate_pr(*_args: object, **_kwargs: object) -> IssuePackageResult:
    _retired()


# Backwards-compatible names for callers that were using the old module path while migrating away
# from PR delivery. They intentionally point to issue-only behavior.
render_issue_body = render_issue_body
package_candidate_issue = package_candidate_issue
record_owner_outcome = record_owner_outcome


class RemoteTargetError(PRPackagingRetiredError):
    pass


__all__ = [
    "FabricatedClaimError",
    "IssuePackageResult",
    "OperatorAuthorizationError",
    "PRPackagingRetiredError",
    "RemoteTargetError",
    "package_candidate_issue",
    "package_candidate_pr",
    "record_owner_outcome",
    "render_issue_body",
    "render_pr_body",
]
