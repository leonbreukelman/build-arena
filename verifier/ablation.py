from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from arena.generated.models import AblationProbe, RunnerName


@dataclass(frozen=True)
class AblationRequest:
    hypothesis_id: str
    reasoning: str
    score_delta: float
    tests_passed: bool
    pinned_regressions: tuple[str, ...]


@dataclass(frozen=True)
class AblationProbeOutcome:
    probe: AblationProbe
    original_output: str
    ablated_output: str
    changed_output: bool


class AblationRunner(Protocol):
    name: RunnerName

    def run_probe(self, request: AblationRequest, probe: AblationProbe) -> AblationProbeOutcome: ...


class DeterministicOllamaAblationRunner:
    """No-API Phase 2 ablation runner with the configured Ollama identity.

    This class intentionally does not call an LLM yet. It provides a deterministic
    local stand-in for the verifier contract: each probe perturbs the supplied
    reasoning and asks whether the promotion decision would change when the
    load-bearing explanation is removed. The real Ollama adapter belongs to the
    later runner-integration phase; Phase 2 keeps the API boundary testable.
    """

    name = RunnerName.ollama

    def run_probe(self, request: AblationRequest, probe: AblationProbe) -> AblationProbeOutcome:
        original_output = _decision_label(request, reasoning_present=True)
        ablated_output = _decision_label(request, reasoning_present=_reasoning_survives_probe(request, probe))
        return AblationProbeOutcome(
            probe=probe,
            original_output=original_output,
            ablated_output=ablated_output,
            changed_output=original_output != ablated_output,
        )


def _has_load_bearing_reasoning(reasoning: str) -> bool:
    lowered = reasoning.lower()
    evidence_terms = ("because", "score", "coverage", "runtime", "pyright", "ruff", "tests")
    return any(term in lowered for term in evidence_terms)


def _decision_label(request: AblationRequest, *, reasoning_present: bool) -> str:
    if (
        request.score_delta > 0
        and request.tests_passed
        and not request.pinned_regressions
        and reasoning_present
        and _has_load_bearing_reasoning(request.reasoning)
    ):
        return "PROMOTE"
    return "DISCARD"


def _reasoning_survives_probe(request: AblationRequest, probe: AblationProbe) -> bool:
    if not _has_load_bearing_reasoning(request.reasoning):
        return False
    match probe:
        case AblationProbe.EARLY_ANSWERING:
            return False
        case AblationProbe.FILLER_TOKENS:
            return False
        case AblationProbe.PARAPHRASING:
            return "paraphrase-stable" in request.reasoning.lower()
        case AblationProbe.ADDING_MISTAKES:
            return False
    return False
