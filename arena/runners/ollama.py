from __future__ import annotations

from pathlib import Path

from arena.generated.models import Hypothesis, RunnerName
from arena.runners.base import CreditExhausted


class OllamaRunner:
    name = RunnerName.ollama

    def __init__(self, *, patch_path: Path | None = None, exhausted: bool = False) -> None:
        self.patch_path = patch_path
        self.exhausted = exhausted
        self.applied_hypotheses: list[Hypothesis] = []

    async def apply(self, hypothesis: Hypothesis, worktree: Path) -> Path:
        self.applied_hypotheses.append(hypothesis)
        if self.exhausted:
            raise CreditExhausted(self.name.value, "forced ollama exhaustion")
        return self.patch_path or (worktree / "ollama.patch")
