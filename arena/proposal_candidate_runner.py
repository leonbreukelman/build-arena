from __future__ import annotations

import argparse
import asyncio
import json
import os
import shlex
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from arena.proposal_planner import ProposalCandidate, candidate_to_hypothesis
from arena.runners.diff_proposer import (
    DiffProposalResponse,
    DiffProposerRunner,
    OpenAICompatibleDiffTransport,
)


@dataclass(frozen=True)
class _FileDiffTransport:
    diff_text: str

    def propose(self, request: Any) -> DiffProposalResponse:
        return DiffProposalResponse(diff_text=self.diff_text, intent=request.intent, provenance={"transport": "file_fake"})


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m arena.proposal_candidate_runner")
    parser.add_argument("--worktree", required=True)
    parser.add_argument("--proposal-plan", required=True)
    parser.add_argument("--candidate-rank", type=int, default=1)
    parser.add_argument("--output")
    parser.add_argument("--fake-diff-file")
    parser.add_argument("--provider", default="xai")
    parser.add_argument("--base-url")
    parser.add_argument("--api-key-env")
    parser.add_argument("--model")
    args = parser.parse_args(argv)

    try:
        result = _run(args)
    except ValueError as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, sort_keys=True))
        return 2
    except Exception as exc:  # noqa: BLE001 - CLI boundary should fail closed with structured output.
        print(json.dumps({"ok": False, "error": f"{type(exc).__name__}: {exc}"}, sort_keys=True))
        return 1
    if args.output:
        Path(args.output).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, sort_keys=True))
    return 0 if result.get("ok") is True else 1


def _run(args: argparse.Namespace) -> dict[str, Any]:
    worktree = Path(args.worktree).resolve()
    plan = _load_json(Path(args.proposal_plan))
    candidate = _select_candidate(plan, int(args.candidate_rank))
    if not candidate.verification_commands:
        return {
            "ok": False,
            "error": "no verification commands configured for proposal candidate",
            "candidateRank": candidate.rank,
            "findingId": candidate.finding_id,
            "targetPath": candidate.target_path,
            "patchPath": "",
            "provenancePath": "",
            "verification": {"ran": False, "commands": []},
        }
    transport = _transport(args)
    runner = DiffProposerRunner(
        transport=transport,
        success_criterion=candidate.success_criterion,
        repo_facts=candidate.repo_facts_block,
        grounding_constraints=candidate.grounding_constraints,
    )
    hypothesis = candidate_to_hypothesis(candidate, cycle_id=f"proposal-r{candidate.rank}", plan_id=str(plan.get("id", "")))
    patch_path = asyncio.run(runner.apply(hypothesis, worktree))
    verification = _run_verification(worktree, candidate.verification_commands)
    return {
        "ok": bool(verification) and all(item["exitCode"] == 0 for item in verification),
        "candidateRank": candidate.rank,
        "findingId": candidate.finding_id,
        "targetPath": candidate.target_path,
        "patchPath": str(patch_path),
        "provenancePath": str(patch_path.with_suffix(".patch.provenance.json")),
        "verification": {"ran": bool(verification), "commands": verification},
    }


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def _select_candidate(plan: dict[str, Any], rank: int) -> ProposalCandidate:
    for raw in plan.get("candidates", []):
        if isinstance(raw, dict) and int(raw.get("rank", -1)) == rank:
            return _candidate(raw)
    raise ValueError(f"proposal candidate rank not found: {rank}")


def _candidate(raw: dict[str, Any]) -> ProposalCandidate:
    return ProposalCandidate(
        rank=int(raw["rank"]),
        finding_id=str(raw["finding_id"]),
        title=str(raw.get("title", "")),
        target_path=str(raw["target_path"]),
        intent=str(raw["intent"]),
        success_criterion=str(raw["success_criterion"]),
        repo_facts_hash=str(raw.get("repo_facts_hash", "")),
        repo_facts_block=str(raw.get("repo_facts_block", "")),
        grounding_constraints=tuple(str(item) for item in raw.get("grounding_constraints", [])),
        verification_commands=tuple(str(item) for item in raw.get("verification_commands", [])),
        priority_score=float(raw.get("priority_score", 0.0)),
        evidence_refs=tuple(item for item in raw.get("evidence_refs", []) if isinstance(item, dict)),
        source_recommended_action=str(raw.get("source_recommended_action", "")),
        target_paths=tuple(str(item) for item in raw.get("target_paths", [raw.get("target_path", "")]) if str(item).strip()),
        base_lineage=raw.get("base_lineage", {}) if isinstance(raw.get("base_lineage", {}), dict) else {},
        intent_hash=str(raw.get("intent_hash", "")),
        proposal_key=str(raw.get("proposal_key", "")),
        registry_status=str(raw.get("registry_status", "")),
    )


def _transport(args: argparse.Namespace) -> Any:
    if args.fake_diff_file:
        return _FileDiffTransport(Path(args.fake_diff_file).read_text(encoding="utf-8"))
    if not args.model:
        raise ValueError("live proposal candidate runner requires --model unless --fake-diff-file is used")
    return OpenAICompatibleDiffTransport(
        provider=args.provider,
        base_url=args.base_url,
        api_key_env=args.api_key_env,
        model=args.model,
    )


def _run_verification(worktree: Path, commands: tuple[str, ...]) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    env = dict(os.environ)
    source_root = Path(__file__).resolve().parents[1]
    current = env.get("PYTHONPATH")
    env["PYTHONPATH"] = f"{source_root}{os.pathsep}{current}" if current else str(source_root)
    for command in commands:
        proc = subprocess.run(shlex.split(command), cwd=worktree, env=env, text=True, capture_output=True, check=False)
        results.append(
            {
                "command": command,
                "exitCode": proc.returncode,
                "stdout": proc.stdout.strip(),
                "stderr": proc.stderr.strip(),
            }
        )
    return results


if __name__ == "__main__":
    raise SystemExit(main())
