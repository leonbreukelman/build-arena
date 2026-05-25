from __future__ import annotations

import importlib
import json
from pathlib import Path


def test_generated_linkml_artifacts_exist_and_import(project_root: Path) -> None:
    generated = project_root / "arena" / "generated"
    assert (project_root / "schema" / "arena.yaml").exists()
    assert (generated / "models.py").exists()
    assert (generated / "schema.json").exists()
    assert (generated / "ddl.sql").exists()
    assert (project_root / "dashboard" / "src" / "lib" / "generated" / "arena.d.ts").exists()
    models = importlib.import_module("arena.generated.models")
    assert hasattr(models, "Run")
    assert hasattr(models, "LoopState")
    schema = json.loads((generated / "schema.json").read_text())
    assert "Run" in json.dumps(schema)
