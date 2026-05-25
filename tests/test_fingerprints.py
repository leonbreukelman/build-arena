from __future__ import annotations

import json
import re
import subprocess
import sys

from arena.fingerprints import DEFAULT_EMBEDDING_MODEL, compute_fingerprint


def test_fingerprint_is_stable_order_insensitive_and_schema_shaped() -> None:
    first = compute_fingerprint(
        intent="replace quadratic lookup with dictionary index",
        target_files=["src/pkg/core.py", "tests/test_core.py"],
        technique_tag="runtime",
        ast_diff_pattern="FunctionDef:process_batch:loop_to_dict",
        first_seen_cycle_id="cycle-1",
    )
    second = compute_fingerprint(
        intent="replace quadratic lookup with dictionary index",
        target_files=["tests/test_core.py", "src/pkg/core.py"],
        technique_tag="runtime",
        ast_diff_pattern="FunctionDef:process_batch:loop_to_dict",
        first_seen_cycle_id="cycle-1",
    )

    assert first.id == second.id
    assert re.fullmatch(r"[0-9a-f]{32}", first.id)
    assert re.fullmatch(r"[0-9a-f]{64}", first.quantized_intent_embedding_sha)
    assert re.fullmatch(r"[0-9a-f]{64}", first.sorted_target_files_hash)
    assert re.fullmatch(r"[0-9a-f]{64}", first.ast_diff_pattern_hash)
    assert first.embedding_model == DEFAULT_EMBEDDING_MODEL


def test_fingerprint_changes_when_technique_or_ast_pattern_changes() -> None:
    base = compute_fingerprint(
        intent="improve coverage for errors",
        target_files=["src/pkg/errors.py"],
        technique_tag="coverage",
        ast_diff_pattern="add_test_branch",
        first_seen_cycle_id="cycle-1",
    )
    changed_technique = compute_fingerprint(
        intent="improve coverage for errors",
        target_files=["src/pkg/errors.py"],
        technique_tag="typing",
        ast_diff_pattern="add_test_branch",
        first_seen_cycle_id="cycle-1",
    )
    changed_pattern = compute_fingerprint(
        intent="improve coverage for errors",
        target_files=["src/pkg/errors.py"],
        technique_tag="coverage",
        ast_diff_pattern="different_pattern",
        first_seen_cycle_id="cycle-1",
    )

    assert base.id != changed_technique.id
    assert base.id != changed_pattern.id


def test_fingerprint_is_reproducible_across_processes(project_root) -> None:
    script = """
import json
from arena.fingerprints import compute_fingerprint
fp = compute_fingerprint(
    intent='resolve pyright strict errors',
    target_files=['src/pkg/validate.py', 'src/pkg/core.py'],
    technique_tag='typing',
    ast_diff_pattern='ImportFrom:typing.Final',
    first_seen_cycle_id='cycle-9',
)
print(json.dumps(fp.model_dump(), sort_keys=True))
"""
    first = subprocess.check_output([sys.executable, "-c", script], cwd=project_root, text=True)
    second = subprocess.check_output([sys.executable, "-c", script], cwd=project_root, text=True)

    assert json.loads(first) == json.loads(second)
