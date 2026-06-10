## Build Arena owner-gated candidate PR

Dry-run gate: this body is rendered from mechanical evidence only. No automatic merge is allowed.

Evidence file: `/tmp/build-arena-m3-07/evidence/cycle-2.json`
Run: `run-pilot-candidates`; cycle: `cycle-2`

### Traceable claims
- Candidate branch: arena/candidate/cycle-2 (source `#/candidate/branch`)
- Candidate commit: 42cc295b9010068daddbbe2f48f8f309d8195703 (source `#/candidate/git_oid`)
- Verdict: PROMOTED (source `#/verdict/outcome`)
- Score delta: 25.854327 (source `#/verdict/score_delta`)
- Score after composite: 170.373835 (source `#/score_after/vector/composite`)
- Tests passed: True (source `#/verdict/tests_passed`)
- Patch size: +276 -1 (source `#/patch/added_lines #/patch/deleted_lines`)
- Touched files: tests/test_client.py, tests/test_resources.py, tests/test_server.py (source `#/patch/files`)

### Owner action required
Review the diff and evidence, then merge or reject manually. Build Arena will not auto-merge this PR.
