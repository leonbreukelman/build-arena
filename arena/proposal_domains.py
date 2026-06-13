"""Multi-domain proposal contract for Build Arena (epic #25, Phase 2, issue #28).

The proposal component is partitioned by *improvement domain* so it can grow
beyond documentation without rewriting the planner. Each domain inspects a
ranked intake finding and, if it owns that finding, returns one or more
``ProposalCandidateDraft`` objects carrying a grounded intent, success
criterion, grounding constraints, and the domain's own verification commands
(its gate).

Current orchestration is **first-match-wins, first-draft**: the planner consults
domains in registry order and uses the first draft from the first domain that
claims the finding (see ``ProposalDomainRegistry.first_candidate``). This
preserves the pre-refactor one-candidate-per-finding behaviour. Collecting the
full union across domains (and multiple drafts per domain) is deferred to the
cross-domain ranking work in Phase 4 (#30); until then a domain returning more
than one draft will have only its first used.

This module deliberately contains no live-provider calls and performs no I/O
beyond what a domain needs to read the project facts passed in via context.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import PurePosixPath
from typing import Any, Protocol

from arena.repo_facts import RepoFacts


@dataclass(frozen=True)
class ProposalCandidateDraft:
    """A domain's proposed candidate, before the planner assigns rank/score and
    attaches finding-level metadata."""

    intent: str
    target_path: str
    success_criterion: str
    grounding_constraints: tuple[str, ...] = ()
    verification_commands: tuple[str, ...] = ()


@dataclass(frozen=True)
class DomainContext:
    """Everything a domain may read to ground a candidate. Read-only."""

    project_name: str
    facts: RepoFacts
    intake_context_block: str
    require_source_references: bool
    extras: dict[str, Any] = field(default_factory=dict)


class ProposalDomain(Protocol):
    """A pluggable improvement domain (documentation, tests, code-quality, ...)."""

    name: str

    def candidates_for_finding(self, finding: dict[str, Any], context: DomainContext) -> list[ProposalCandidateDraft]:
        ...


class ProposalDomainRegistry:
    """An ordered, validated collection of proposal domains.

    Construction fails closed if any member does not satisfy the ``ProposalDomain``
    protocol (missing ``name`` or ``candidates_for_finding``) or if two domains
    share a name, so misconfiguration surfaces immediately rather than at run
    time.
    """

    def __init__(self, domains: list[ProposalDomain]) -> None:
        seen: set[str] = set()
        validated: list[ProposalDomain] = []
        for domain in domains:
            name = getattr(domain, "name", None)
            if not isinstance(name, str) or not name.strip():
                raise ValueError(f"proposal domain {domain!r} has no non-empty 'name'")
            candidates_fn = getattr(domain, "candidates_for_finding", None)
            if not callable(candidates_fn):
                raise TypeError(f"proposal domain {name!r} is missing a callable 'candidates_for_finding'")
            if name in seen:
                raise ValueError(f"duplicate proposal domain name: {name!r}")
            seen.add(name)
            validated.append(domain)
        self._domains = tuple(validated)

    def __iter__(self):  # type: ignore[no-untyped-def]
        return iter(self._domains)

    def __len__(self) -> int:
        return len(self._domains)

    def first_candidate(self, finding: dict[str, Any], context: DomainContext) -> tuple[str, ProposalCandidateDraft] | None:
        """Return the first (domain_name, draft) a domain produces for the finding.

        Domains are consulted in registry order, so order encodes precedence. A
        finding that no domain owns yields ``None`` (the planner records it as a
        skipped finding).
        """
        for domain in self._domains:
            drafts = domain.candidates_for_finding(finding, context)
            if drafts:
                return (domain.name, drafts[0])
        return None


def default_domain_registry() -> ProposalDomainRegistry:
    """The built-in registry. Documentation is the only implemented domain today;
    non-doc domains (tests, code-quality, dependencies, security, ...) are added in
    later phases of epic #25."""
    return ProposalDomainRegistry([DocumentationDomain(), GenericFileDomain()])


_DOC_INDEX_TARGET = "docs/index.md"
_AGENTS_TARGET = "AGENTS.md"


class DocumentationDomain:
    """Documentation proposals: docs index, AGENTS.md, and any ``*.md`` target.

    Carries the deterministic Markdown link / source-reference gate as its
    verification commands. This is the documentation-scope behaviour previously
    inlined in ``proposal_planner._candidate_from_finding``.
    """

    name = "documentation"

    def candidates_for_finding(self, finding: dict[str, Any], context: DomainContext) -> list[ProposalCandidateDraft]:
        target_path = _single_target_path(finding)
        if target_path is None or not target_path.endswith(".md"):
            return []
        finding_id = str(finding.get("id", ""))
        if finding_id == "doc.index.missing" or target_path == _DOC_INDEX_TARGET:
            intent = (
                "Create a grounded docs/index.md that links only to existing repository files "
                "and names missing future documentation topics by title only, with no filename or extension."
            )
        elif target_path == _AGENTS_TARGET:
            intent = "Create a grounded AGENTS.md for future agents using existing repository facts, commands, and boundaries."
        else:
            title = str(finding.get("title") or finding_id or target_path)
            intent = f"Create a grounded Markdown file at {target_path} that addresses finding {finding_id}: {title}."
        success, constraints, verification = _markdown_success_contract(
            target_path, require_source_references=context.require_source_references
        )
        return [ProposalCandidateDraft(
            intent=intent,
            target_path=target_path,
            success_criterion=success,
            grounding_constraints=constraints,
            verification_commands=verification,
        )]


class GenericFileDomain:
    """Fallback for a single-file, non-Markdown target (e.g. a code surface from a
    component finding). Produces a bounded one-file improvement request and reuses
    the finding's own verification commands.

    NOTE: this domain intentionally does NOT add a load-bearing code gate; that is
    Phase 3 (#29). Until then a code candidate may carry empty verification, which
    the candidate runner treats as fail-closed.
    """

    name = "generic_file"

    def candidates_for_finding(self, finding: dict[str, Any], context: DomainContext) -> list[ProposalCandidateDraft]:
        target_path = _single_target_path(finding)
        if target_path is None or target_path.endswith(".md"):
            return []
        finding_id = str(finding.get("id", ""))
        title = str(finding.get("title") or finding_id or target_path)
        intent = f"Prepare a grounded one-file improvement for {target_path} based on finding {finding_id}: {title}."
        success = f"{target_path} is changed in a bounded, repository-grounded way and project verification remains green."
        constraints = ("Use only repository facts and current file contents; do not invent project structure, files, or commands.",)
        verification = tuple(str(command) for command in finding.get("verification", []) if str(command).strip())
        return [ProposalCandidateDraft(
            intent=intent,
            target_path=target_path,
            success_criterion=success,
            grounding_constraints=constraints,
            verification_commands=verification,
        )]


# --- shared helpers (module-local; private to proposal_domains) ---


def _single_target_path(finding: dict[str, Any]) -> str | None:
    paths: list[str] = []
    for evidence in finding.get("evidence", []):
        if not isinstance(evidence, dict):
            continue
        raw = evidence.get("path")
        if not isinstance(raw, str) or not raw.strip() or raw.startswith("iterationReadiness"):
            continue
        path = PurePosixPath(raw.replace("\\", "/"))
        if path.is_absolute() or ".." in path.parts:
            continue
        paths.append(_proposal_target_for_evidence_path(path))
    unique = tuple(dict.fromkeys(paths))
    return unique[0] if len(unique) == 1 else None


def _proposal_target_for_evidence_path(path: PurePosixPath) -> str:
    if path.suffix:
        return path.as_posix()
    return (path / "index.md").as_posix()


def _markdown_success_contract(target_path: str, *, require_source_references: bool = False) -> tuple[str, tuple[str, ...], tuple[str, ...]]:
    success = f"{target_path} exists, is non-empty, and all local Markdown links resolve to existing repository files."
    constraints = [
        "Do not invent Markdown links to files absent from the repository facts.",
        "If a future documentation topic has no existing file, describe it by title only, with no filename or extension.",
        "Local Markdown links must resolve after the patch is applied.",
    ]
    verification = [f"test -s {target_path}", f"python3 -m arena.markdown_links --repo . --path {target_path}"]
    if require_source_references:
        success += " It includes a Source references section citing at least one existing repository file."
        constraints.append("Include a `## Source references` section that cites existing repository files for factual or compliance claims.")
        verification[-1] = f"python3 -m arena.markdown_links --repo . --path {target_path} --require-source-references"
    return (success, tuple(constraints), tuple(verification))
