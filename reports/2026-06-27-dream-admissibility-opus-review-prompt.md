You are the independent Claude Code Opus certifier for Build Arena Track F: Experiment Lane divergent-hypothesis admissibility.

Do not edit files. Review the working tree diff and untracked files in this repository. Use `git status`, `git diff`, and read files as needed. Return a concise JSON object only with:

{
  "decision": "ACCEPT" | "BLOCK",
  "summary": "one paragraph",
  "blockers": [{"path": "...", "issue": "...", "required_fix": "..."}],
  "non_blocking_notes": ["..."],
  "checked_requirements": {
    "captured_restatements_rejected": true/false,
    "positive_fixture_accepted": true/false,
    "replay_yields_admissible": true/false,
    "schema_delta_v1_present": true/false,
    "gate_kills_inadmissible_before_emit": true/false,
    "no_protected_path_violation": true/false
  }
}

Scope and acceptance contract:
- Implement deterministic admissibility for `dream/v1` divergent architectural hypotheses.
- Captured fmc-mcp restatement fixtures `dream-1` and `dream-2` must be rejected for requirement-2 structural-delta failure (`from == to` or no proposed structure).
- A hand-authored grounded positive divergent fixture must be accepted.
- Captured fmc-mcp inputs replayed through generate -> research with injected offline callables must yield >=1 admissible experiment.
- The gate must run admissibility before emit and kill inadmissible dreams.
- `expectedDirection` admissible set is only `decrease`, `increase`, `passes`.
- A capability-only citation is not a tension.
- Do not require a human mid-run review gate; the experiment lane remains advisory-only.
- Protected/frozen paths must not be mutated beyond the declared schema bump; never modify `scorer/`, `verifier/`, `.arena/scorer.lock.toml`, or `arena/generated/`.

Current local verification already run by implementer:
- `make generated` -> exit 0
- `uv run pytest tests/test_dream_admissibility.py tests/test_dream_generate.py tests/test_dream_research.py tests/test_dream_gate.py tests/test_dream_emit.py tests/test_dream_run.py -q` -> exit 0
- `uv run pytest tests -q` -> exit 0
- `uv run ruff check .` -> exit 0
- `uv run pyright` -> exit 0

Important files to inspect:
- `arena/dream_admissibility.py`
- `docs/schemas/dream-v1.schema.json`
- `arena/dream_generate.py`
- `arena/dream_research.py`
- `arena/dream_gate.py`
- `arena/dream_emit.py`
- `tests/test_dream_admissibility.py`
- `tests/fixtures/dream_admissibility/`
- `docs/specs/2026-06-27-experiment-lane-divergent-hypothesis-admissibility.md`

Return JSON only. If anything is blocking, be specific and minimal.
