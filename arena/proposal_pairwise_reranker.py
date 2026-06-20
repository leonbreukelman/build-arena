from __future__ import annotations

import argparse
import hashlib
import json
import re
import shlex
import shutil
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Protocol

from arena.llm_adapter import OpenAICompatibleChatClient, resolve_provider_config

TRACE_SCHEMA_VERSION = "proposal-pairwise-rerank-trace/v0"
PLAN_SCHEMA_VERSION = "proposal-plan/v0"
SYSTEM_PROMPT = """You are Build Arena's proposal re-ranker. You choose between two already-generated improvement proposals for THIS repository.

Rules:
- Use only the candidate data and repository context in this prompt.
- Ignore any original rank or priority score if present. The final pick must be a relative judgment.
- Prefer the proposal that is more valuable, more specific, and more verifiable for THIS repo right now.
- A proposal is better when it has grounded evidence, a specific target location, a binding verification path that a no-op would not pass, and a concrete non-circular definition of done.
- A proposal is worse when it is vague, mostly documentation filler, broad without a target, not tied to graph evidence, or only says that existing checks remain green.
- You must cite evidence from EACH candidate before choosing.
- Return JSON only. No Markdown. No prose outside JSON.
"""

_USER_PROMPT_TEMPLATE = """Repository context:
{repo_context_json}

Rubric:
Choose which candidate is the more valuable, more specific, more verifiable improvement to THIS repo.
Evaluate in this order:
1. Grounding: Which candidate cites stronger graph/repo evidence?
2. Specificity: Which candidate names a more concrete target file/symbol and action?
3. Verification: Which candidate has a more binding verification path that a no-op would not pass?
4. Leverage: Which candidate better reduces future unsafe or unverified work?
5. Scope fit: Which candidate is smaller and safer without becoming trivial?

Candidate A:
{candidate_a_json}

Candidate B:
{candidate_b_json}

Return exactly this JSON shape:
{{
  "winner_slot": "A" or "B",
  "winner_finding_id": "finding id of the winner",
  "candidate_a_evidence_cited": ["tokens from Candidate A citable_evidence"],
  "candidate_b_evidence_cited": ["tokens from Candidate B citable_evidence"],
  "reason": "one concise sentence citing why the winner is more valuable, specific, and verifiable"
}}
"""

_PATH_RE = re.compile(r"(?<![\]/(])\b(?:[A-Za-z0-9_.-]+/)*[A-Za-z0-9_.-]+\.(?:md|toml|yaml|yml|json|py|ts|tsx|js|jsx|txt|lock)\b")
_CODE_SPAN_RE = re.compile(r"`([^`]+)`")
_SHELL_CONTROL_RE = re.compile(r"(;|&&|\|\||\||>|<|\$\(|`)")
_SYMBOL_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)*$")
_STRONG_OBSERVABLES = (
    "exists",
    "non-empty",
    "source references resolve",
    "local markdown links",
    "strictly fewer ruff",
    "architecture fitness contract",
    "accepted by arena.architecture_fitness_gate",
    "binding currently-failing guardrail",
    "currently-failing guardrail",
    "test file",
    "check file",
)
_CIRCULAR_RED_FLAGS = (
    "is changed in a bounded way",
    "addresses finding",
    "project verification remains green",
    "quality gate commands pass",
    "covered by a bounded change",
)
_DIRECTORY_ONLY_TARGETS = {".", "docs", "src", "tests"}


class RerankError(ValueError):
    pass


@dataclass(frozen=True)
class GraphIndex:
    paths: frozenset[str]
    symbols: frozenset[str]
    node_ids: frozenset[str]
    provenance_ids: frozenset[str]

    @classmethod
    def from_graph(cls, graph: dict[str, Any]) -> GraphIndex:
        paths: set[str] = set()
        symbols: set[str] = set()
        node_ids: set[str] = set()
        provenance_ids: set[str] = set()
        for node in _dict_items(graph.get("nodes")):
            node_id = _clean_str(node.get("id"))
            if node_id:
                node_ids.add(node_id)
            path = _clean_str(node.get("path"))
            if path:
                paths.add(path)
            symbol = _clean_str(node.get("symbol"))
            if symbol:
                symbols.add(symbol)
            label = _clean_str(node.get("label"))
            if label and _SYMBOL_RE.match(label) and not _looks_like_file_path(label):
                symbols.add(label)
            for prov in _dict_items(node.get("provenance_refs") or node.get("provenanceRefs")):
                prov_id = _clean_str(prov.get("id"))
                if prov_id:
                    provenance_ids.add(prov_id)
        for edge in _dict_items(graph.get("edges")):
            for prov in _dict_items(edge.get("provenance_refs") or edge.get("provenanceRefs")):
                prov_id = _clean_str(prov.get("id"))
                if prov_id:
                    provenance_ids.add(prov_id)
        return cls(
            paths=frozenset(paths),
            symbols=frozenset(symbols),
            node_ids=frozenset(node_ids),
            provenance_ids=frozenset(provenance_ids),
        )


@dataclass(frozen=True)
class PrefilterDrop:
    finding_id: str
    original_rank: int
    title: str
    reasons: list[str]
    evidence_paths: list[str]

    def to_trace(self) -> dict[str, Any]:
        return {
            "finding_id": self.finding_id,
            "original_rank": self.original_rank,
            "title": self.title,
            "reasons": list(self.reasons),
            "evidence_paths": list(self.evidence_paths),
        }

    def to_skipped_finding(self) -> dict[str, Any]:
        return {
            "finding_id": self.finding_id,
            "rank": self.original_rank,
            "title": self.title,
            "reason": "pairwise_prefilter:" + ";".join(self.reasons),
            "evidence_paths": list(self.evidence_paths),
        }


@dataclass(frozen=True)
class JudgeResult:
    winner_slot: str
    winner_finding_id: str
    candidate_a_evidence_cited: tuple[str, ...]
    candidate_b_evidence_cited: tuple[str, ...]
    reason: str
    prompt_hash: str
    response_hash: str

    def to_trace(self) -> dict[str, Any]:
        return {
            "winner_finding_id": self.winner_finding_id,
            "reason": self.reason,
            "candidate_a_evidence_cited": list(self.candidate_a_evidence_cited),
            "candidate_b_evidence_cited": list(self.candidate_b_evidence_cited),
            "prompt_hash": self.prompt_hash,
            "response_hash": self.response_hash,
        }


class ProposalJudge(Protocol):
    def compare(self, slot_a: dict[str, Any], slot_b: dict[str, Any], repo_context: dict[str, Any]) -> JudgeResult:
        ...


@dataclass(frozen=True)
class TournamentResult:
    winner: dict[str, Any]
    tournament: list[dict[str, Any]]
    call_count: int


@dataclass(frozen=True)
class RerankPayloadResult:
    plan: dict[str, Any]
    trace: dict[str, Any]


@dataclass
class DefaultLLMProposalJudge:
    client: OpenAICompatibleChatClient
    _last_model_info: dict[str, Any] | None = None

    @classmethod
    def create(cls) -> DefaultLLMProposalJudge:
        config = resolve_provider_config("xai")
        return cls(OpenAICompatibleChatClient(config=config, temperature=0))

    def model_info(self) -> dict[str, Any]:
        if self._last_model_info is not None:
            return self._last_model_info
        return {
            "provider": self.client.config.provider,
            "requested_model": self.client.config.model,
            "served_model": "",
            "temperature": self.client.temperature,
        }

    def compare(self, slot_a: dict[str, Any], slot_b: dict[str, Any], repo_context: dict[str, Any]) -> JudgeResult:
        messages = build_judge_messages(slot_a, slot_b, repo_context)
        prompt_hash = _sha(messages)
        result = self.client.complete(
            messages=messages,
            response_format={"type": "json_object"},
        )
        payload = _parse_json_object(result.text, "judge response")
        response_hash = hashlib.sha256(result.text.encode()).hexdigest()
        judged = validate_judge_payload(payload, slot_a, slot_b, prompt_hash=prompt_hash, response_hash=response_hash)
        self._last_model_info = {
            "provider": result.provider,
            "requested_model": result.requested_model,
            "served_model": result.model,
            "temperature": self.client.temperature,
            "usage": result.usage,
        }
        return judged


def load_plan(path: str | Path) -> dict[str, Any]:
    payload = _parse_json_object(Path(path).read_text(encoding="utf-8"), "proposal plan")
    if payload.get("schemaVersion") != PLAN_SCHEMA_VERSION:
        raise RerankError("proposal plan must have schemaVersion proposal-plan/v0")
    if not isinstance(payload.get("candidates"), list):
        raise RerankError("proposal plan must contain a candidates array")
    return payload


def load_graph(path_or_payload: str | Path | dict[str, Any]) -> dict[str, Any]:
    payload = path_or_payload if isinstance(path_or_payload, dict) else _parse_json_object(Path(path_or_payload).read_text(encoding="utf-8"), "project graph")
    nested = payload.get("projectGraph")
    graph: dict[str, Any] = nested if isinstance(nested, dict) else payload
    if not isinstance(graph.get("nodes"), list):
        raise RerankError("graph must contain a nodes array")
    return graph


def candidate_key(candidate: dict[str, Any]) -> tuple[int, str, str]:
    return (
        _safe_int(candidate.get("rank"), 999999),
        _clean_str(candidate.get("finding_id")),
        ",".join(_candidate_targets(candidate)),
    )


def prefilter_candidates(plan: dict[str, Any], graph: GraphIndex) -> tuple[list[dict[str, Any]], list[PrefilterDrop]]:
    survivors: list[dict[str, Any]] = []
    dropped: list[PrefilterDrop] = []
    for candidate in sorted(_dict_items(plan.get("candidates")), key=candidate_key):
        reasons = _prefilter_reasons(candidate, graph)
        if reasons:
            dropped.append(
                PrefilterDrop(
                    finding_id=_clean_str(candidate.get("finding_id")),
                    original_rank=_safe_int(candidate.get("rank"), 0),
                    title=_clean_str(candidate.get("title")),
                    reasons=reasons,
                    evidence_paths=_evidence_paths(candidate),
                )
            )
        else:
            survivors.append(candidate)
    return survivors, dropped


def build_candidate_payload(candidate: dict[str, Any]) -> dict[str, Any]:
    payload = {
        "finding_id": _clean_str(candidate.get("finding_id")),
        "title": _clean_str(candidate.get("title")),
        "target_paths": _candidate_targets(candidate),
        "intent": _clean_str(candidate.get("intent")),
        "success_criterion": _clean_str(candidate.get("success_criterion")),
        "verification_commands": _string_list(candidate.get("verification_commands")),
        "grounding_constraints": _string_list(candidate.get("grounding_constraints")),
        "evidence_refs": [json.loads(json.dumps(item, sort_keys=True)) for item in _dict_items(candidate.get("evidence_refs"))],
        "source_recommended_action": _clean_str(candidate.get("source_recommended_action")),
        "repo_facts_block": _clean_str(candidate.get("repo_facts_block"))[:4000],
    }
    payload["citable_evidence"] = citable_evidence(candidate)
    return payload


def citable_evidence(candidate: dict[str, Any]) -> list[str]:
    tokens: list[str] = [f"target_path:{path}" for path in _candidate_targets(candidate)]
    evidence_tokens: list[str] = []
    for evidence in _dict_items(candidate.get("evidence_refs")):
        kind = _clean_str(evidence.get("kind"))
        path = _clean_str(evidence.get("path"))
        ref = _clean_str(evidence.get("ref"))
        component = _clean_str(evidence.get("componentId"))
        if kind and path:
            evidence_tokens.append(f"evidence:{kind}:{path}")
        if ref:
            evidence_tokens.append(f"evidence:provenance:{ref}")
        if component:
            evidence_tokens.append(f"evidence:component:{component}")
    tokens.extend(evidence_tokens)
    if not evidence_tokens:
        constraints = _string_list(candidate.get("grounding_constraints"))
        tokens.extend(f"constraint:{index}" for index, _constraint in enumerate(constraints, start=1))
    return list(dict.fromkeys(tokens))


def build_judge_messages(slot_a: dict[str, Any], slot_b: dict[str, Any], repo_context: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": _USER_PROMPT_TEMPLATE.format(
                repo_context_json=json.dumps(repo_context, indent=2, sort_keys=True),
                candidate_a_json=json.dumps(slot_a, indent=2, sort_keys=True),
                candidate_b_json=json.dumps(slot_b, indent=2, sort_keys=True),
            ),
        },
    ]


def validate_judge_payload(
    payload: dict[str, Any],
    slot_a: dict[str, Any],
    slot_b: dict[str, Any],
    *,
    prompt_hash: str,
    response_hash: str,
) -> JudgeResult:
    slot = _clean_str(payload.get("winner_slot"))
    if slot not in {"A", "B"}:
        raise RerankError("judge response winner_slot must be A or B")
    expected_winner = slot_a["finding_id"] if slot == "A" else slot_b["finding_id"]
    winner = _clean_str(payload.get("winner_finding_id"))
    if winner != expected_winner:
        raise RerankError("judge response winner_finding_id does not match winner_slot")
    evidence_a = _string_list(payload.get("candidate_a_evidence_cited"))
    evidence_b = _string_list(payload.get("candidate_b_evidence_cited"))
    if not evidence_a or not evidence_b:
        raise RerankError("judge response must cite evidence from both candidates")
    allowed_a = set(_string_list(slot_a.get("citable_evidence")))
    allowed_b = set(_string_list(slot_b.get("citable_evidence")))
    if any(token not in allowed_a for token in evidence_a):
        raise RerankError("judge response cited evidence not present in Candidate A")
    if any(token not in allowed_b for token in evidence_b):
        raise RerankError("judge response cited evidence not present in Candidate B")
    reason = _clean_str(payload.get("reason"))
    if not reason:
        raise RerankError("judge response reason must be non-empty")
    if "priority_score" in reason or "priority score" in reason.lower() or "original rank" in reason.lower():
        raise RerankError("judge response reason must not mention original rank or priority score")
    return JudgeResult(
        winner_slot=slot,
        winner_finding_id=winner,
        candidate_a_evidence_cited=tuple(evidence_a),
        candidate_b_evidence_cited=tuple(evidence_b),
        reason=reason,
        prompt_hash=prompt_hash,
        response_hash=response_hash,
    )


def run_pairwise_tournament(
    survivors: Sequence[dict[str, Any]],
    judge: ProposalJudge,
    repo_context: dict[str, Any],
) -> TournamentResult:
    ordered = sorted([dict(candidate) for candidate in survivors], key=candidate_key)
    if not ordered:
        raise RerankError("cannot run tournament without survivors")
    incumbent = ordered[0]
    tournament: list[dict[str, Any]] = []
    call_count = 0
    for matchup, challenger in enumerate(ordered[1:], start=1):
        incumbent_id = _clean_str(incumbent.get("finding_id"))
        challenger_id = _clean_str(challenger.get("finding_id"))
        inc_payload = build_candidate_payload(incumbent)
        chal_payload = build_candidate_payload(challenger)
        call_ab = _ensure_judge_result(judge.compare(inc_payload, chal_payload, repo_context))
        call_count += 1
        call_ba = _ensure_judge_result(judge.compare(chal_payload, inc_payload, repo_context))
        call_count += 1
        consistent = call_ab.winner_finding_id == call_ba.winner_finding_id
        if consistent and call_ab.winner_finding_id == challenger_id:
            incumbent = challenger
            winner_id = challenger_id
            decision = "challenger_replaces_incumbent"
        elif consistent:
            winner_id = incumbent_id
            decision = "incumbent_kept"
        else:
            winner_id = incumbent_id
            decision = "position_inconsistent_keep_incumbent"
        tournament.append(
            {
                "matchup": matchup,
                "incumbent_finding_id": incumbent_id,
                "challenger_finding_id": challenger_id,
                "call_ab": call_ab.to_trace(),
                "call_ba": call_ba.to_trace(),
                "consistent": consistent,
                "winner_finding_id": winner_id,
                "decision": decision,
            }
        )
    return TournamentResult(winner=incumbent, tournament=tournament, call_count=call_count)


def rerank_plan_payload(
    plan: dict[str, Any],
    graph: dict[str, Any],
    judge: ProposalJudge,
    *,
    source_plan_path: str = "",
    graph_path: str = "",
    model_info: dict[str, Any] | None = None,
) -> RerankPayloadResult:
    index = GraphIndex.from_graph(load_graph(graph))
    survivors, dropped = prefilter_candidates(plan, index)
    trace = _base_trace(plan, source_plan_path, graph_path, model_info, len(survivors), dropped)
    if not survivors:
        trace["winner"] = None
        return RerankPayloadResult(plan={}, trace=trace)
    if len(survivors) == 1:
        winner = survivors[0]
        tournament = TournamentResult(winner=winner, tournament=[], call_count=0)
    else:
        tournament = run_pairwise_tournament(survivors, judge, _repo_context(plan, source_plan_path, graph_path))
    trace["tournament"] = tournament.tournament
    trace["callCount"] = tournament.call_count
    trace["estimatedCallFormula"] = "2 * (survivorCount - 1)"
    trace["model"] = _judge_model_info(judge)
    trace["winner"] = {
        "finding_id": _clean_str(tournament.winner.get("finding_id")),
        "original_rank": _safe_int(tournament.winner.get("rank"), 0),
        "output_rank": 1,
    }
    derived = build_derived_plan(plan, tournament.winner, survivors, dropped)
    return RerankPayloadResult(plan=derived, trace=trace)


def rerank_proposal_plan(
    project: str | Path,
    plan_path: str | Path,
    graph_path: str | Path,
    output_plan_path: str | Path,
    trace_path: str | Path,
    *,
    judge: ProposalJudge | None = None,
    allow_live: bool = False,
) -> RerankPayloadResult:
    if judge is None:
        if not allow_live:
            raise RerankError("--allow-live is required when no injected judge is provided")
        judge = DefaultLLMProposalJudge.create()
    plan = load_plan(plan_path)
    graph = load_graph(graph_path)
    info = _judge_model_info(judge)
    result = rerank_plan_payload(
        plan,
        graph,
        judge,
        source_plan_path=str(plan_path),
        graph_path=str(graph_path),
        model_info=info,
    )
    trace_file = Path(trace_path)
    trace_file.parent.mkdir(parents=True, exist_ok=True)
    trace_file.write_text(json.dumps(result.trace, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if not result.plan:
        raise RerankError("no candidates survived pre-filter")
    output_file = Path(output_plan_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(json.dumps(result.plan, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    _ = project
    return result


def build_derived_plan(
    source_plan: dict[str, Any],
    winner: dict[str, Any],
    survivors: Sequence[dict[str, Any]],
    drops: Sequence[PrefilterDrop],
) -> dict[str, Any]:
    winner_id = _clean_str(winner.get("finding_id"))
    ordered = sorted([dict(candidate) for candidate in survivors], key=candidate_key)
    reranked = [candidate for candidate in ordered if _clean_str(candidate.get("finding_id")) == winner_id]
    reranked.extend(candidate for candidate in ordered if _clean_str(candidate.get("finding_id")) != winner_id)
    candidates: list[dict[str, Any]] = []
    for rank, candidate in enumerate(reranked, start=1):
        copied = json.loads(json.dumps(candidate, sort_keys=True))
        copied["rank"] = rank
        candidates.append(copied)
    skipped = [json.loads(json.dumps(item, sort_keys=True)) for item in _dict_items(source_plan.get("skippedFindings"))]
    skipped.extend(drop.to_skipped_finding() for drop in drops)
    base = {
        "schemaVersion": PLAN_SCHEMA_VERSION,
        "sourceScorecardId": _clean_str(source_plan.get("sourceScorecardId")),
        "snapshotId": _clean_str(source_plan.get("snapshotId")),
        "projectRoot": _clean_str(source_plan.get("projectRoot")),
        "repoFactsHash": _clean_str(source_plan.get("repoFactsHash")),
        "baseLineage": json.loads(json.dumps(source_plan.get("baseLineage", {}), sort_keys=True)),
        "candidateCount": len(candidates),
        "omittedCount": 0,
        "skippedCount": len(skipped),
        "skippedFindings": skipped,
        "findingDispositions": [json.loads(json.dumps(item, sort_keys=True)) for item in _dict_items(source_plan.get("findingDispositions"))],
        "candidates": candidates,
    }
    return {"id": stable_plan_hash(base)[:16], **base}


def stable_plan_hash(plan: dict[str, Any]) -> str:
    payload = {key: value for key, value in plan.items() if key != "id"}
    return _sha(payload)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m arena.proposal_pairwise_reranker")
    parser.add_argument("--project", required=True)
    parser.add_argument("--plan", required=True)
    parser.add_argument("--graph", required=True)
    parser.add_argument("--output-plan", required=True)
    parser.add_argument("--trace", required=True)
    parser.add_argument("--allow-live", action="store_true")
    args = parser.parse_args(argv)
    try:
        rerank_proposal_plan(
            args.project,
            args.plan,
            args.graph,
            args.output_plan,
            args.trace,
            allow_live=args.allow_live,
        )
    except RerankError as exc:
        print(f"proposal pairwise re-ranker failed: {exc}", file=sys.stderr)
        return 1
    return 0


def _prefilter_reasons(candidate: dict[str, Any], graph: GraphIndex) -> list[str]:
    reasons: list[str] = []
    targets = _candidate_targets(candidate)
    target_set = set(targets)
    if not targets:
        reasons.append("missing_target_path")
    for raw_target in _raw_candidate_targets(candidate):
        normalized = _normalize_path(raw_target)
        if normalized is None:
            reasons.append("invalid_target_path")
            continue
        if _is_directory_only_target(normalized):
            reasons.append(f"directory_only_target:{normalized}")
    for file_ref in _candidate_file_refs(candidate, target_set):
        if file_ref not in graph.paths:
            reasons.append(f"unresolved_file_reference:{file_ref}")
    for symbol in _candidate_symbol_refs(candidate):
        if symbol not in graph.symbols:
            reasons.append(f"unresolved_symbol_reference:{symbol}")
    commands = _string_list(candidate.get("verification_commands"))
    if not commands:
        reasons.append("empty_verification")
    else:
        binding_found = False
        binding_missing_target_reasons: list[str] = []
        for command in commands:
            parsed = _parse_command(command)
            if isinstance(parsed, str):
                reasons.append(f"{parsed}:{command}")
                continue
            family = _command_family(parsed)
            if family[0] == "unknown":
                reasons.append(f"verification_unknown_family:{command}")
                continue
            if family[0] == "binding":
                command_target = family[1]
                if command_target in target_set:
                    binding_found = True
                else:
                    binding_missing_target_reasons.append(f"verification_binding_command_missing_target:{command}")
        if not binding_found and not any(reason.startswith("verification_unknown") or reason.startswith("verification_unparseable") or reason.startswith("verification_disallowed") for reason in reasons):
            reasons.extend(binding_missing_target_reasons or ["verification_non_binding_noop_passes"])
    if _is_circular_success(_clean_str(candidate.get("success_criterion"))):
        reasons.append("circular_definition_of_done")
    return list(dict.fromkeys(reasons))


def _parse_command(command: str) -> list[str] | str:
    if _SHELL_CONTROL_RE.search(command) or "bash -lc" in command or "sh -c" in command:
        return "verification_disallowed_shell"
    try:
        parts = shlex.split(command)
    except ValueError:
        return "verification_unparseable"
    if not parts:
        return "verification_unparseable"
    executable = parts[0]
    if executable in {"test", "/usr/bin/test"}:
        return parts
    if shutil.which(executable) is None:
        return "verification_unknown_executable"
    return parts


def _command_family(parts: list[str]) -> tuple[str, str]:
    if parts[0] in {"test", "/usr/bin/test"}:
        if len(parts) >= 3 and parts[1] == "-s":
            target = _normalize_path(parts[2])
            return ("binding", target or "")
        return ("unknown", "")
    if parts[0] == "uv" and len(parts) >= 2 and parts[1] == "run":
        return ("nonbinding", "")
    if len(parts) >= 4 and parts[0] == "python3" and parts[1] == "-m":
        module = parts[2]
        if module == "arena.markdown_links":
            target = _option_value(parts, "--path")
            return ("binding", _normalize_path(target) or "") if target else ("unknown", "")
        if module == "arena.code_quality_gate":
            target = _option_value(parts, "--path")
            return ("binding", _normalize_path(target) or "") if target else ("unknown", "")
        if module == "arena.architecture_fitness_gate":
            target = _option_value(parts, "--contract")
            return ("binding", _normalize_path(target) or "") if target else ("unknown", "")
    return ("unknown", "")


def _option_value(parts: list[str], option: str) -> str:
    try:
        index = parts.index(option)
    except ValueError:
        return ""
    if index + 1 >= len(parts):
        return ""
    return parts[index + 1]


def _raw_candidate_targets(candidate: dict[str, Any]) -> list[str]:
    raw = _string_list(candidate.get("target_paths"))
    if not raw and _clean_str(candidate.get("target_path")):
        raw = [_clean_str(candidate.get("target_path"))]
    return raw


def _candidate_targets(candidate: dict[str, Any]) -> list[str]:
    targets: list[str] = []
    for raw in _raw_candidate_targets(candidate):
        normalized = _normalize_path(raw)
        if normalized is not None and not _is_directory_only_target(normalized):
            targets.append(normalized)
    return list(dict.fromkeys(targets))


def _normalize_path(value: str) -> str | None:
    text = _clean_str(value)
    if not text:
        return None
    if any(mark in text for mark in ("*", "?", "[", "]")):
        return None
    path = PurePosixPath(text)
    if path.is_absolute() or ".." in path.parts:
        return None
    normalized = path.as_posix().rstrip("/")
    if normalized in {"", "."}:
        return None
    return normalized


def _is_directory_only_target(path: str) -> bool:
    if path in _DIRECTORY_ONLY_TARGETS:
        return True
    return PurePosixPath(path).suffix == ""


def _candidate_file_refs(candidate: dict[str, Any], target_set: set[str]) -> list[str]:
    refs: list[str] = []
    text_fields = [
        _clean_str(candidate.get("intent")),
        _clean_str(candidate.get("success_criterion")),
        "\n".join(_string_list(candidate.get("grounding_constraints"))),
        "\n".join(_string_list(candidate.get("verification_commands"))),
    ]
    for text in text_fields:
        refs.extend(_file_refs(text))
    for evidence in _dict_items(candidate.get("evidence_refs")):
        path = _clean_str(evidence.get("path"))
        if _looks_like_file_path(path):
            normalized = _normalize_path(path)
            if normalized:
                refs.append(normalized)
    return sorted({ref for ref in refs if ref not in target_set})


def _candidate_symbol_refs(candidate: dict[str, Any]) -> list[str]:
    symbols: list[str] = []
    for text in (_clean_str(candidate.get("intent")), _clean_str(candidate.get("success_criterion"))):
        for match in _CODE_SPAN_RE.finditer(text):
            token = match.group(1).strip()
            if _SYMBOL_RE.match(token) and not _looks_like_file_path(token):
                symbols.append(token)
    return list(dict.fromkeys(symbols))


def _file_refs(text: str) -> list[str]:
    refs: list[str] = []
    for match in _PATH_RE.finditer(text):
        normalized = _normalize_path(match.group(0).rstrip(".,;:"))
        if normalized:
            refs.append(normalized)
    return refs


def _looks_like_file_path(value: str) -> bool:
    return bool(_PATH_RE.fullmatch(value.strip()))


def _is_circular_success(success: str) -> bool:
    lower = success.lower()
    if not lower.strip():
        return True
    has_red = any(phrase in lower for phrase in _CIRCULAR_RED_FLAGS)
    if not has_red:
        return False
    has_observable = any(phrase in lower for phrase in _STRONG_OBSERVABLES)
    return not has_observable


def _base_trace(
    plan: dict[str, Any],
    source_plan_path: str,
    graph_path: str,
    model_info: dict[str, Any] | None,
    survivor_count: int,
    dropped: Sequence[PrefilterDrop],
) -> dict[str, Any]:
    return {
        "schemaVersion": TRACE_SCHEMA_VERSION,
        "sourcePlanPath": source_plan_path,
        "sourcePlanId": _clean_str(plan.get("id")),
        "graphPath": graph_path,
        "model": model_info or {},
        "preFilter": {
            "inputCandidateCount": len(_dict_items(plan.get("candidates"))),
            "survivorCount": survivor_count,
            "dropped": [drop.to_trace() for drop in dropped],
        },
        "tournament": [],
        "callCount": 0,
        "estimatedCallFormula": "2 * (survivorCount - 1)",
    }


def _repo_context(plan: dict[str, Any], source_plan_path: str, graph_path: str) -> dict[str, Any]:
    return {
        "projectRoot": _clean_str(plan.get("projectRoot")),
        "snapshotId": _clean_str(plan.get("snapshotId")),
        "sourceScorecardId": _clean_str(plan.get("sourceScorecardId")),
        "repoFactsHash": _clean_str(plan.get("repoFactsHash")),
        "sourcePlanPath": source_plan_path,
        "graphPath": graph_path,
    }


def _judge_model_info(judge: ProposalJudge) -> dict[str, Any]:
    model_info = getattr(judge, "model_info", None)
    if callable(model_info):
        value = model_info()
        if isinstance(value, dict):
            return value
    return {"provider": "injected", "requested_model": "injected", "served_model": "", "temperature": 0}


def _ensure_judge_result(value: JudgeResult) -> JudgeResult:
    if not isinstance(value, JudgeResult):
        raise RerankError("judge.compare must return JudgeResult")
    return value


def _evidence_paths(candidate: dict[str, Any]) -> list[str]:
    paths: list[str] = []
    for evidence in _dict_items(candidate.get("evidence_refs")):
        path = _clean_str(evidence.get("path"))
        if path:
            paths.append(path)
    return list(dict.fromkeys(paths))


def _parse_json_object(text: str, label: str) -> dict[str, Any]:
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        raise RerankError(f"{label} must be valid JSON") from exc
    if not isinstance(payload, dict):
        raise RerankError(f"{label} must be a JSON object")
    return payload


def _dict_items(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item.strip() for item in value if isinstance(item, str) and item.strip()]


def _clean_str(value: Any) -> str:
    return str(value).strip() if value is not None else ""


def _safe_int(value: Any, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _sha(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


if __name__ == "__main__":
    raise SystemExit(main())
