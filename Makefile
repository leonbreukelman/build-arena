PYTHON ?= uv run python

.PHONY: generated generated-fresh test lint typecheck verify calibration lock

generated: schema/arena.yaml
	mkdir -p arena/generated dashboard/src/lib/generated
	uv run gen-pydantic schema/arena.yaml > arena/generated/models.py
	uv run gen-json-schema schema/arena.yaml > arena/generated/schema.json
	uv run gen-typescript schema/arena.yaml > dashboard/src/lib/generated/arena.d.ts
	uv run gen-sqlddl schema/arena.yaml > arena/generated/ddl.sql
	uv run python scripts/normalize_generated_artifacts.py

generated-fresh: generated
	git diff --exit-code -- arena/generated dashboard/src/lib/generated

test:
	uv run pytest tests -q

lint:
	uv run ruff check .

typecheck:
	uv run pyright

calibration:
	uv run python scripts/rebuild_calibration.py

lock:
	uv run python scripts/update_scorer_lock.py

verify: generated-fresh lint typecheck test
