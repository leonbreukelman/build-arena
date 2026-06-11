from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path

from arena.generated.models import AblationProbe, RunnerName

DEFAULT_PROBE_SET: tuple[AblationProbe, AblationProbe, AblationProbe] = (
    AblationProbe.EARLY_ANSWERING,
    AblationProbe.FILLER_TOKENS,
    AblationProbe.PARAPHRASING,
)


@dataclass(frozen=True)
class VerifierConfig:
    probe_set: tuple[AblationProbe, ...] = DEFAULT_PROBE_SET
    quorum_threshold: int = 2
    ablation_runner: RunnerName = RunnerName.ollama
    ablation_advisory: bool = False
    require_tests_pass: bool = True
    require_score_delta_gt0: bool = True
    fp_target: float = 0.0
    fn_target: float = 0.10

    def __post_init__(self) -> None:
        if len(self.probe_set) != 3:
            raise ValueError("verifier probe_set must contain exactly 3 Lanham probes")
        if len(set(self.probe_set)) != len(self.probe_set):
            raise ValueError("verifier probe_set must not contain duplicate probes")
        if not 1 <= self.quorum_threshold <= len(self.probe_set):
            raise ValueError(f"verifier quorum_threshold must be between 1 and {len(self.probe_set)}")
        if not self.ablation_advisory and self.ablation_runner is not RunnerName.ollama:
            raise ValueError("Phase 2 verifier ablation runner must be ollama")

    @classmethod
    def from_toml(cls, path: Path) -> VerifierConfig:
        data = tomllib.loads(path.read_text())
        verifier = data.get("verifier", {})
        runners = data.get("runners", {})
        probe_set = tuple(AblationProbe(value) for value in verifier.get("ablation_probe_set", DEFAULT_PROBE_SET))
        return cls(
            probe_set=probe_set,
            quorum_threshold=int(verifier.get("ablation_quorum", 2)),
            ablation_runner=RunnerName(runners.get("ablation", RunnerName.ollama.value)),
            ablation_advisory=bool(verifier.get("ablation_advisory", False)),
            require_tests_pass=bool(verifier.get("require_tests_pass", True)),
            require_score_delta_gt0=bool(verifier.get("require_score_delta_gt0", True)),
            fp_target=float(verifier.get("fp_target", 0.0)),
            fn_target=float(verifier.get("fn_target", 0.10)),
        )
