# Build Arena BA-M3-04 Patch Gate and Diff Proposer Evidence

Date: 2026-06-10T05:29:43Z
Kanban card: `t_eeafe5ff` — BA-M3-04 Phase 2: Add patch gate and fail-closed diff proposer
Branch: `ba/m3-patch-gate-diff-proposer`

## Scope completed

- Added `arena/patch_gate.py`.
- Added `arena/runners/diff_proposer.py`.
- Added `arena/proposer_hypothesizer.py`.
- Added `tests/test_patch_gate.py`.
- Added `tests/test_diff_proposer.py`.
- Added `tests/test_proposer_hypothesizer.py`.

## Patch gate behavior

`validate_unified_diff(repo, diff_text, goal_config=None)`:

- rejects empty diffs;
- rejects prose-only / malformed diffs with no touched paths;
- rejects binary diff markers;
- rejects boundary/read-only/out-of-scope paths through `is_boundary_violation(..., goal_config=config)`;
- rejects diffs that exceed `goal_config.diff_caps.max_files` or `max_lines`;
- runs `git apply --check -` before accepting;
- returns a JSON-safe `PatchGateResult` with accepted/reason/touched paths/line counts/detail;
- never applies the diff itself.

Tests prove accepted and rejected gate paths leave the worktree unchanged.

## Diff proposer behavior

`DiffProposerRunner`:

- implements the current `AgentRunner` shape: `name` plus async `apply(hypothesis, worktree) -> Path`;
- uses injected fake transports only;
- requires exactly one target file;
- reads the target file contents and passes goal-config hash, target path, file contents, success criterion, and hypothesis intent into a `DiffProposalRequest`;
- rejects cancelled, truncated, empty, prose-only/malformed, boundary-violating, and oversized outputs fail-closed before mutation;
- validates all candidate diffs through patch gate before applying;
- applies accepted diffs with `git apply -`;
- writes `.arena/patches/<hypothesis>.patch` only on success;
- writes `.patch.provenance.json` only on success with hypothesis/fingerprint/target/intent/transport/patch-gate evidence.

## Proposer/hypothesizer bridge

`TargetSelectionHypothesizer`:

- consumes a `TargetSelection`;
- creates a one-target `HypothesisProposal` for the top-ranked candidate;
- computes a normal `Fingerprint` through the existing fingerprint helper;
- stores `selection.id` in `hypothesis.reasoning_blob_sha` to preserve deterministic target-selection provenance.

## TDD evidence

- Tests were written before implementation.
- RED run failed during collection with missing modules:
  - `No module named 'arena.patch_gate'`;
  - `No module named 'arena.runners.diff_proposer'`;
  - `No module named 'arena.proposer_hypothesizer'`.
- GREEN run: `uv run pytest tests/test_patch_gate.py tests/test_diff_proposer.py tests/test_proposer_hypothesizer.py -q` passed: `16 passed`.

## Verification completed

- `uv run pytest tests/test_patch_gate.py tests/test_diff_proposer.py tests/test_proposer_hypothesizer.py tests/test_runner_router.py tests/test_target_picker.py tests/test_boundary.py tests/test_goal_config.py -q` — passed.
- `uv run pytest tests -q` — passed.
- `uv run ruff check .` — passed.
- `uv run pyright` — passed: `0 errors, 0 warnings`.
- Static provider scan of new production modules for live/provider-call imports — passed: no hits.
- `git diff --check` — passed.
- New-file whitespace checks for all six new files — passed.

## Fable review

Verdict: `ACCEPT` with no critical blockers and no required changes before completion.

Fable requested one clarifying comment about diff header lines not counting toward caps; that comment was added after review and targeted/full checks were rerun.

### Review transcript

VERDICT: ACCEPT

```json
{
  "verdict": "ACCEPT",
  "critical_blockers": [],
  "required_changes_before_completion": [],
  "rationale": {
    "fail_closed_behavior": "Sound. Every rejection path (empty, prose-only/malformed, binary marker, boundary/read-only, caps overflow, git apply --check failure) returns or raises before any worktree mutation, and tests assert clean git status plus unchanged file contents on each rejection path. The gate itself never applies; the runner only applies after gate acceptance. Order of checks (parse → boundary → caps → git apply --check) is correct and cheap-first.",
    "runner_contract": "Satisfied. DiffProposerRunner exposes name + async apply(hypothesis, worktree) -> Path, and the RunnerRouter integration test proves the router works unchanged (success, runner_used, patch_path all verified). Single-target enforcement, path normalization (absolute/.. rejection), and pre-transport boundary check on the target are all in place.",
    "mutation_guarantees": "Good. Diff is gated before apply, applied via git apply only after --check passed in the same gate call against the same worktree, and patch/provenance artifacts land under .arena/patches only on success. The TOCTOU window between --check and apply is negligible for a single-writer worktree cycle.",
    "provenance_shape": "Adequate. Patch file + sidecar JSON with hypothesis_id, fingerprint_id, target_path, intent, transport-supplied fields, and the full patch-gate result (counts, touched paths, reason). Transport provenance merged without letting it overwrite the core keys (core keys applied last). reasoning_blob_sha=selection.id is a documented, deliberate bridge — acceptable for this phase.",
    "tdd_and_verification": "RED→GREEN evidence, full suite, ruff, pyright clean, no provider imports. Meets the bar."
  },
  "guidance_as_leon_representative": [
    "Close the card after commit. Scope is fully covered and the adversarial surface that matters (LLM diff output) is gated fail-closed with mutation-free rejection proven by tests.",
    "Non-blocking hardening for a fast follow-up, not this card: (1) hypothesis.id is interpolated into the patch filename unsanitized — today ids are internally generated, but add a filename-safety guard (reject '/', '..', or non [A-Za-z0-9._-]) so a malformed id can never write outside .arena/patches; also note with_suffix misbehaves if an id ever contains a dot. (2) The 'Binary files ' substring check can false-positive on a diff that *adds a line containing that text* — it fails closed (over-rejects), so fine for now, but anchor it to line starts when you next touch the gate. (3) name = RunnerName.codex is a semantic squat on an existing enum value; when the generated models are next regenerated, add a dedicated RunnerName for the diff proposer. (4) proposed_ts=0.0 is a placeholder — thread real cycle time through when the orchestrator wires this in.",
    "The _parse_diff_stats line counters intentionally exclude ---/+++ headers via elif ordering — add a one-line comment there; it looks accidental to a future reader and is load-bearing for the caps check."
  ],
  "next_cards_to_claim_or_continue": [
    "Claim the next M3 phase card: wiring the full worktree cycle — target picker → TargetSelectionHypothesizer → DiffProposerRunner → scorer verdict — into a single orchestrated cycle (the integration card that makes these three new modules run end-to-end against a real worktree).",
    "If that orchestration card isn't yet on the board, the secondary candidate is the fingerprint/ledger persistence card so repeated cycles can dedupe hypotheses across runs, which the fingerprint bridge here was built to enable."
  ]
}
```

Answers to the three review questions, briefly: (1) Yes — commit and close BA-M3-04; all card requirements have test-backed evidence. (2) No critical blockers; the items above are hardening polish, none of which compromise the fail-closed guarantee as shipped. (3) Continue with the M3 cycle-orchestration card next, since all of its dependencies (goal config, target picker, hypothesizer bridge, patch gate, diff proposer) are now in place.

## Non-blocking follow-ups noted by Fable

- Add filename safety for `hypothesis.id` before using it as a patch filename.
- Anchor binary-marker detection to diff line starts to avoid over-rejecting content lines.
- Add a dedicated generated `RunnerName` for diff proposer in a future schema update instead of using `codex` as the closest current enum value.
- Thread real cycle time into `TargetSelectionHypothesizer` when the orchestrator wires it in.

These were explicitly non-blocking for BA-M3-04.
