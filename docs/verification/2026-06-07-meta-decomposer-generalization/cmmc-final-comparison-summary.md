# CMMC decomposition final comparison

Old baseline: `/home/leonb/projects/build-arena/docs/verification/2026-06-07-cmmc-level1-decomposition/artifacts/snapshot-25eb081bd3f1ba3b`
Final model: `/home/leonb/projects/build-arena/docs/verification/2026-06-07-meta-decomposer-generalization/artifacts/cmmc/snapshot-92b2bb5139d78b15`

## Headline

- Gate violations: 70 -> 0
- Gate passed: False -> True
- Components: 8 -> 35
- Contracts: 1 -> 57
- Backend contracts in final model: 43
- Frontend contracts in final model: 14
- Gaps in final model: 0

## Final observable checks

- `check.app-backend-python-tests` in `app/backend`: `uv run pytest -q` (safe_by_default)
- `check.app-frontend-node-test` in `app/frontend`: `npm test -- --run` (unknown)

## Proof runs

- Backend proof: `/home/leonb/projects/build-arena/docs/verification/2026-06-07-meta-decomposer-generalization/artifacts/cmmc/snapshot-92b2bb5139d78b15/proof-runs/check.app-backend-python-tests.txt`
- Frontend proof: `/home/leonb/projects/build-arena/docs/verification/2026-06-07-meta-decomposer-generalization/artifacts/cmmc/snapshot-92b2bb5139d78b15/proof-runs/check.app-frontend-node-test.txt`

## JSON summary

See `/home/leonb/projects/build-arena/docs/verification/2026-06-07-meta-decomposer-generalization/cmmc-final-comparison-summary.json`.
