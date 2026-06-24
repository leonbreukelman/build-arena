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
from pathlib import Path, PurePosixPath
from typing import Any, Protocol

from arena.advisory_backlog import (
    BACKLOG_TARGET,
    advisory_expected_target,
    backlog_markdown_entry,
    build_advisory_expected,
    canonical_expected_text,
    expected_digest,
)
from arena.architecture_fitness import (
    architecture_contract_target,
    build_import_cycle_contract,
    canonical_contract_text,
    contract_digest,
    selected_import_cycle,
)
from arena.ci_workflow import canonical_ci_text, ci_workflow_target, detect_ci_inputs
from arena.graph_slice import GraphSlice
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
    target_paths: tuple[str, ...] = ()


@dataclass(frozen=True)
class DomainContext:
    """Everything a domain may read to ground a candidate. Read-only."""

    project_name: str
    facts: RepoFacts
    intake_context_block: str
    require_source_references: bool
    open_questions: tuple[dict[str, Any], ...] = ()
    verification_gaps: tuple[dict[str, Any], ...] = ()
    graph_slice: GraphSlice = field(default_factory=GraphSlice)
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
    """The built-in registry. Documentation and code-quality are implemented;
    other non-doc domains (tests, dependencies, security, ...) are added in
    later phases of epic #25. ``code_quality`` and ``ci_workflow`` precede
    ``generic_file`` so findings route to domains carrying load-bearing gates
    rather than the bare single-file fallback."""
    return ProposalDomainRegistry([
        DocumentationDomain(),
        CodeQualityDomain(),
        ComponentVerificationDomain(),
        CiWorkflowDomain(),
        GenericFileDomain(),
        ArchitectureFitnessDomain(),
        AdvisoryBacklogDomain(),
        ModelLevelDomain(),
    ])


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


class CodeQualityDomain:
    """Code-quality proposals: reduce ruff lint violations in a single Python
    source file. Carries the *load-bearing* code-quality gate
    (``arena.code_quality_gate``) as its verification, which rejects no-op diffs,
    suppression gaming (``# noqa`` / ``# type: ignore``), and syntax destruction.

    Only claims ``code.quality.lint.*`` findings whose target is a ``.py`` file.
    """

    name = "code_quality"

    def candidates_for_finding(self, finding: dict[str, Any], context: DomainContext) -> list[ProposalCandidateDraft]:
        finding_id = str(finding.get("id", ""))
        if not finding_id.startswith("code.quality.lint."):
            return []
        target_path = _single_target_path(finding)
        if target_path is None or not target_path.endswith(".py"):
            return []
        intent = (
            f"Fix the ruff lint violations in {target_path} by correcting the underlying issue "
            "(e.g. remove the unused import, sort imports, fix the style error). Do not silence "
            "warnings with suppressions."
        )
        success = (
            f"{target_path} still parses as Python, has strictly fewer ruff violations than before, "
            "and adds no new lint-suppression markers."
        )
        constraints = (
            "Reduce real ruff violations; do not add `# noqa` or `# type: ignore` to silence them.",
            "Do not delete or stub code to zero out warnings; preserve behaviour.",
            "Change only the target file; keep the edit minimal and grounded in the current file contents.",
        )
        verification = (f"python3 -m arena.code_quality_gate --repo . --path {target_path}",)
        return [ProposalCandidateDraft(
            intent=intent,
            target_path=target_path,
            success_criterion=success,
            grounding_constraints=constraints,
            verification_commands=verification,
        )]


class ComponentVerificationDomain:
    """Component/test-coverage findings that need code-facing verification."""

    name = "component_verification"

    def candidates_for_finding(self, finding: dict[str, Any], context: DomainContext) -> list[ProposalCandidateDraft]:
        finding_id = str(finding.get("id", ""))
        boundary = str(finding.get("autonomyBoundary", ""))
        if not (finding_id.startswith("code.component.untested.") or boundary == "needs_code_change"):
            return []
        target_paths = _target_paths_for_finding(finding)
        if not target_paths or not any(path.endswith(".py") for path in target_paths):
            return []
        verification = _finding_or_quality_gate_verification(finding, context)
        title = str(finding.get("title") or finding_id)
        joined_targets = ", ".join(target_paths)
        intent = (
            f"Add or prepare an observable, repository-grounded check for component finding {finding_id}: {title}. "
            f"Limit changes to the component target path set: {joined_targets}."
        )
        success = (
            f"The component target path set ({joined_targets}) is covered by a bounded change and the project's "
            "load-bearing quality gate commands pass."
        )
        constraints = (
            "Prefer a focused test or minimal code-facing verification improvement over broad refactors.",
            "Do not silence failures or remove behavior to make the gate pass.",
            "Use only repository-grounded files and commands from the intake quality gates.",
        )
        return [ProposalCandidateDraft(
            intent=intent,
            target_path=target_paths[0],
            success_criterion=success,
            grounding_constraints=constraints,
            verification_commands=verification,
            target_paths=target_paths,
        )]


class CiWorkflowDomain:
    """Missing-CI findings converted into deterministic, fact-grounded workflow files."""

    name = "ci_workflow"

    def candidates_for_finding(self, finding: dict[str, Any], context: DomainContext) -> list[ProposalCandidateDraft]:
        if str(finding.get("id", "")) != "verification.ci.missing":
            return []
        inputs = detect_ci_inputs(Path(context.facts.project_root))
        if inputs.test_command is None:
            return []
        text = canonical_ci_text(inputs)
        target = ci_workflow_target()
        intent = (
            f"Create the CI workflow at {target} exactly as shown in the grounding constraints, "
            "running only the repository's detected commands."
        )
        success = (
            "The workflow byte-equals the canonical CI text for the detected inputs and "
            "`python3 -m arena.ci_workflow --repo . --check` passes."
        )
        constraints = (
            "The workflow may run only commands detected in the repository (test, and lint/typecheck only if their tools are present); do not invent jobs, tools, actions, or versions.",
            f"Exact workflow YAML to write to {target}:\n{text}",
        )
        verification = ("python3 -m arena.ci_workflow --repo . --check",)
        return [ProposalCandidateDraft(
            intent=intent,
            target_path=target,
            success_criterion=success,
            grounding_constraints=constraints,
            verification_commands=verification,
            target_paths=(target,),
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


class ArchitectureFitnessDomain:
    """Graph-evidenced architecture concerns converted into binding guardrails."""

    name = "architecture_fitness"

    def candidates_for_finding(self, finding: dict[str, Any], context: DomainContext) -> list[ProposalCandidateDraft]:
        if not _is_architecture_finding(finding):
            return []
        cycle = selected_import_cycle(context.graph_slice)
        if not cycle:
            return []
        finding_id = str(finding.get("id", ""))
        contract = build_import_cycle_contract(finding_id=finding_id, cycle=cycle)
        digest = contract_digest(contract)
        target_path = architecture_contract_target(digest)
        contract_text = canonical_contract_text(contract)
        cycle_text = " -> ".join((*cycle, cycle[0]))
        intent = (
            f"Create a deterministic architecture fitness contract at {target_path} that captures the "
            f"graph-evidenced import cycle {cycle_text}. Write exactly the JSON contract shown in the "
            "grounding constraints; do not add architectural intent that is not evidenced by the graph."
        )
        success = (
            "The architecture fitness contract is syntactically valid, references only real graph modules, "
            "and is accepted by arena.architecture_fitness_gate as a binding currently-failing guardrail."
        )
        constraints = (
            "Fitness contracts may only reference modules present in the freshly rebuilt project graph.",
            "Acceptance means valid, grounded, and binding; it does not mean the guarded violation has been fixed.",
            "Expected current status for this contract is failing; do not auto-promote it as a passing behaviour change.",
            f"Exact contract JSON to write to {target_path}:\n{contract_text}",
        )
        verification = (f"python3 -m arena.architecture_fitness_gate --repo . --contract {target_path}",)
        return [ProposalCandidateDraft(
            intent=intent,
            target_path=target_path,
            success_criterion=success,
            grounding_constraints=constraints,
            verification_commands=verification,
            target_paths=(target_path,),
        )]


class AdvisoryBacklogDomain:
    """Ground advisory-only findings that have no mechanical signal into backlog."""

    name = "advisory_backlog"

    def candidates_for_finding(self, finding: dict[str, Any], context: DomainContext) -> list[ProposalCandidateDraft]:
        if not _is_advisory_backlog_finding(finding):
            return []
        items = _advisory_items_for_finding(finding, context)
        if not items:
            return []
        finding_id = str(finding.get("id", ""))
        expected = build_advisory_expected(finding_id=finding_id, items=items)
        digest = expected_digest(expected)
        expected_path = advisory_expected_target(digest)
        expected_text = canonical_expected_text(expected)
        backlog_text = backlog_markdown_entry(finding_id=finding_id, items=items)
        item_summary = "; ".join(f"{item['id']}: {item['text']}" for item in items)
        intent = (
            f"Append a grounded advisory backlog entry to {BACKLOG_TARGET} for {finding_id}, covering {item_summary}. "
            f"Also write the expected-item sidecar at {expected_path} so arena.backlog_gate can verify the entry."
        )
        success = (
            "The advisory backlog entry contains the expected advisory IDs and text, is not boilerplate, "
            "and all local Markdown links resolve."
        )
        constraints = (
            "Do not invent architectural constraints for advisory-only questions; record them as backlog until a mechanical signal exists.",
            "The backlog entry must include every expected advisory ID and exact text from the sidecar.",
            f"Exact expected sidecar JSON to write to {expected_path}:\n{expected_text}",
            f"Suggested backlog Markdown for {BACKLOG_TARGET}:\n{backlog_text}",
        )
        verification = (f"python3 -m arena.backlog_gate --repo . --path {BACKLOG_TARGET} --expected {expected_path}",)
        return [ProposalCandidateDraft(
            intent=intent,
            target_path=BACKLOG_TARGET,
            success_criterion=success,
            grounding_constraints=constraints,
            verification_commands=verification,
            target_paths=(BACKLOG_TARGET, expected_path),
        )]


class ModelLevelDomain:
    """Model-level findings that have no concrete source target yet."""

    name = "model_level"

    def candidates_for_finding(self, finding: dict[str, Any], context: DomainContext) -> list[ProposalCandidateDraft]:
        if not _is_model_level_finding(finding):
            return []
        target_path = "docs/agent-backlog.md"
        finding_id = str(finding.get("id", ""))
        title = str(finding.get("title") or finding_id)
        intent = f"Record a grounded backlog/verification task for model-level finding {finding_id}: {title}."
        success, constraints, verification = _markdown_success_contract(
            target_path,
            require_source_references=context.require_source_references,
        )
        return [ProposalCandidateDraft(
            intent=intent,
            target_path=target_path,
            success_criterion=success,
            grounding_constraints=constraints,
            verification_commands=verification,
            target_paths=(target_path,),
        )]


# --- shared helpers (module-local; private to proposal_domains) ---


def _single_target_path(finding: dict[str, Any]) -> str | None:
    unique = _target_paths_for_finding(finding)
    return unique[0] if len(unique) == 1 else None


def _target_paths_for_finding(finding: dict[str, Any]) -> tuple[str, ...]:
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
    return tuple(dict.fromkeys(paths))


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


def _finding_or_quality_gate_verification(finding: dict[str, Any], context: DomainContext) -> tuple[str, ...]:
    explicit = tuple(str(command).strip() for command in finding.get("verification", []) if str(command).strip())
    if explicit:
        return explicit
    from_context = context.extras.get("quality_gate_commands", ())
    if isinstance(from_context, (tuple, list)):
        commands = tuple(str(command).strip() for command in from_context if str(command).strip())
        if commands:
            return commands
    return ("uv run ruff check .", "uv run pyright", "uv run pytest tests -q")


def _is_model_level_finding(finding: dict[str, Any]) -> bool:
    finding_id = str(finding.get("id", ""))
    boundary = str(finding.get("autonomyBoundary", ""))
    if boundary != "safe_to_patch_docs_only":
        return False
    if finding_id.startswith("architecture."):
        return True
    evidence = [item for item in finding.get("evidence", []) if isinstance(item, dict)]
    return bool(evidence) and all(str(item.get("path", "")).startswith("iterationReadiness") for item in evidence)


def _is_architecture_finding(finding: dict[str, Any]) -> bool:
    finding_id = str(finding.get("id", ""))
    dimension = str(finding.get("dimension", ""))
    return finding_id.startswith("architecture.") or dimension == "architecture_specs_contracts"


def _is_advisory_backlog_finding(finding: dict[str, Any]) -> bool:
    finding_id = str(finding.get("id", ""))
    boundary = str(finding.get("autonomyBoundary", ""))
    if boundary != "advisory_only":
        return False
    return finding_id not in {"verification.quality-gates.present", "verification.quality-gates.missing"}


def _advisory_items_for_finding(finding: dict[str, Any], context: DomainContext) -> tuple[dict[str, str], ...]:
    finding_id = str(finding.get("id", ""))
    evidence_paths = {str(item.get("path", "")) for item in finding.get("evidence", []) if isinstance(item, dict)}
    include_questions = finding_id.startswith("architecture.") or any("openQuestions" in path for path in evidence_paths)
    include_gaps = finding_id.startswith("architecture.") or any("verification_gaps" in path or "verificationGaps" in path for path in evidence_paths)
    items: list[dict[str, str]] = []
    if include_questions:
        for question in context.open_questions:
            item = _advisory_item(question, "open_question")
            if item:
                items.append(item)
    if include_gaps:
        for gap in context.verification_gaps:
            item = _advisory_item(gap, "verification_gap")
            if item:
                items.append(item)
    unique: dict[tuple[str, str, str], dict[str, str]] = {}
    for item in items:
        unique[(item["kind"], item["id"], item["text"])] = item
    return tuple(unique[key] for key in sorted(unique))


def _advisory_item(raw: dict[str, Any], kind: str) -> dict[str, str]:
    item_id = str(raw.get("id", "")).strip()
    text = str(raw.get("question", "") or raw.get("description", "") or raw.get("text", "")).strip()
    if not item_id or not text:
        return {}
    return {"kind": kind, "id": item_id, "text": text}
