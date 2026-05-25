from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
from collections.abc import Callable
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CAL_ROOT = PROJECT_ROOT / ".arena" / "calibration"
BASE_REPO = CAL_ROOT / "repo"
DIFF_ROOT = CAL_ROOT / "diffs"


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


def baseline_files() -> dict[str, str]:
    return {
        "pyproject.toml": '''[project]
name = "validatorlib-calibration"
version = "0.1.0"
requires-python = ">=3.12"

[tool.pytest.ini_options]
testpaths = ["tests"]

[tool.coverage.run]
branch = true
source = ["validatorlib"]
omit = ["*/typing_gaps.py", "*/style_debt.py"]

[tool.pyright]
include = ["src"]
typeCheckingMode = "strict"
pythonVersion = "3.12"
reportMissingTypeStubs = false

[tool.ruff]
line-length = 88
target-version = "py312"

[tool.ruff.lint]
select = ["E501"]
''',
        "src/validatorlib/__init__.py": '''from validatorlib.core import Result, Rule, ValidationItem, process_batch, summarize_results
from validatorlib.errors import ValidationProblem, format_chain
from validatorlib.parsing import parse_lines, parse_record
from validatorlib.validate import build_rules, validate_lines

__all__ = [
    "Result",
    "Rule",
    "ValidationItem",
    "ValidationProblem",
    "build_rules",
    "format_chain",
    "parse_lines",
    "parse_record",
    "process_batch",
    "summarize_results",
    "validate_lines",
]
''',
        "src/validatorlib/core.py": '''from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass


@dataclass
class ValidationItem:
    key: str
    value: object
    source: str = "inline"


@dataclass
class Rule:
    key: str
    check: Callable[[object], bool]


@dataclass
class Result:
    key: str
    ok: bool
    message: str


def process_batch(items: Sequence[ValidationItem], rules: Sequence[Rule]) -> list[Result]:
    results: list[Result] = []
    for item in items:
        matching_rule: Rule | None = None
        for candidate in rules:
            if candidate.key == item.key:
                matching_rule = candidate
                break
        if matching_rule is None:
            results.append(Result(item.key, False, "missing rule"))
            continue
        if matching_rule.check(item.value):
            results.append(Result(item.key, True, "ok"))
        else:
            results.append(Result(item.key, False, "invalid value"))
    return results


def summarize_results(results: Sequence[Result]) -> dict[str, int]:
    passed = sum(1 for result in results if result.ok)
    failed = len(results) - passed
    return {"passed": passed, "failed": failed, "total": len(results)}


def benchmark_units(size: int = 300) -> float:
    algorithm_units = float(size * size)
    allocation_penalty = 100.0 if not hasattr(ValidationItem, "__slots__") else 50.0
    slow_path_penalty = 0.0
    return algorithm_units + (size * allocation_penalty) + slow_path_penalty
''',
        "src/validatorlib/parsing.py": '''from __future__ import annotations

from collections.abc import Iterable

from validatorlib.core import ValidationItem


def normalize_key(raw: str) -> str:
    return raw.strip().lower().replace(" ", "_")


def parse_record(line: str) -> ValidationItem:
    key, separator, value = line.partition(":")
    if separator == "":
        raise ValueError(f"record missing ':' separator: {line!r}")
    return ValidationItem(key=normalize_key(key), value=value.strip())


def parse_lines(lines: Iterable[str]) -> list[ValidationItem]:
    records: list[ValidationItem] = []
    for line_number, line in enumerate(lines, start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        record = parse_record(stripped)
        records.append(ValidationItem(record.key, record.value, source=f"line:{line_number}"))
    return records
''',
        "src/validatorlib/validate.py": '''from __future__ import annotations

from collections.abc import Iterable

from validatorlib.core import Result, Rule, process_batch
from validatorlib.parsing import parse_lines


def assert_valid_key(key: str) -> None:
    assert key.strip() == key
    assert key != ""


def _present(value: object) -> bool:
    return value not in (None, "")


def build_rules(allowed_keys: Iterable[str]) -> list[Rule]:
    rules: list[Rule] = []
    for key in allowed_keys:
        assert_valid_key(key)
        rules.append(Rule(key=key, check=_present))
    return rules


def validate_lines(lines: Iterable[str], allowed_keys: Iterable[str]) -> list[Result]:
    return process_batch(parse_lines(lines), build_rules(allowed_keys))
''',
        "src/validatorlib/io.py": '''from __future__ import annotations

from pathlib import Path
import json

from validatorlib.core import Result, ValidationItem


def read_lines(path: Path) -> list[str]:
    return path.read_text().splitlines()


def load_json_records(path: Path) -> list[ValidationItem]:
    payload = json.loads(path.read_text())
    if not isinstance(payload, list):
        raise ValueError("expected a JSON list")
    records: list[ValidationItem] = []
    for item in payload:
        if not isinstance(item, dict):
            raise ValueError("expected JSON objects")
        records.append(ValidationItem(key=str(item["key"]), value=item.get("value"), source=str(path)))
    return records


def dumps_results(results: list[Result]) -> str:
    return json.dumps([result.__dict__ for result in results], sort_keys=True)
''',
        "src/validatorlib/errors.py": '''from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field


@dataclass
class ValidationProblem(Exception):
    key: str
    message: str
    cause: Exception | None = None

    def __str__(self) -> str:
        return _format_message(self)


def _format_message(problem: ValidationProblem) -> str:
    return f"{problem.key}: {problem.message}"


@dataclass
class ErrorAccumulator:
    problems: list[ValidationProblem] = field(default_factory=list)

    def add(self, problem: ValidationProblem) -> None:
        self.problems.append(problem)

    def formatted(self) -> str:
        return format_chain(self.problems)

    def count(self) -> int:
        return len(self.problems)


def format_chain(errors: Iterable[ValidationProblem], *, include_causes: bool = False) -> str:
    problems = list(errors)
    if not problems:
        return "no errors"
    lines: list[str] = []
    for problem in problems:
        lines.append(_format_message(problem))
        if include_causes and problem.cause is not None:
            lines.append(f"caused by: {problem.cause}")
    return "\\n".join(lines)
''',
        "src/validatorlib/typing_gaps.py": '''from __future__ import annotations


def known_type_gaps(values: list[str]) -> int:
    count: int = "0"
    label: str = 42
    names: list[str] = [1]
    mapping: dict[str, int] = {"answer": "42"}
    return len(values) + len(names) + len(mapping) + count + len(label)
''',
        "src/validatorlib/style_debt.py": '''from __future__ import annotations

FIRST = "alpha beta gamma delta epsilon zeta eta theta iota kappa lambda mu nu xi omicron pi rho sigma tau"
SECOND = "one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen"
THIRD = "north south east west northeast northwest southeast southwest center perimeter boundary interior"
FOURTH = "red orange yellow green blue indigo violet black white gray silver gold bronze copper iron"
FIFTH = "mercury venus earth mars jupiter saturn uranus neptune pluto ceres eris makemake haumea"
SIXTH = "spring summer autumn winter monsoon dry wet windy cloudy stormy clear humid arid temperate"
''',
        "benchmarks/runtime_proxy.py": '''from __future__ import annotations

import json

from validatorlib.core import benchmark_units


print(json.dumps({"runtime_p95_ms": benchmark_units() / 1000.0}))
''',
        "tests/test_core.py": '''from __future__ import annotations

from validatorlib.core import Rule, ValidationItem, process_batch, summarize_results


def test_process_batch_preserves_input_order_and_messages() -> None:
    items = [ValidationItem("name", "Ada"), ValidationItem("age", ""), ValidationItem("city", "London")]
    rules = [Rule("name", bool), Rule("age", bool), Rule("city", bool)]

    results = process_batch(items, rules)

    assert [result.key for result in results] == ["name", "age", "city"]
    assert [result.ok for result in results] == [True, False, True]
    assert results[1].message == "invalid value"


def test_process_batch_reports_missing_rule() -> None:
    results = process_batch([ValidationItem("unknown", "x")], [Rule("known", bool)])
    assert results[0].message == "missing rule"
    assert not results[0].ok


def test_summarize_results_counts_outcomes() -> None:
    items = [ValidationItem("name", "Ada"), ValidationItem("age", "")]
    results = process_batch(items, [Rule("name", bool), Rule("age", bool)])
    assert summarize_results(results) == {"passed": 1, "failed": 1, "total": 2}
''',
        "tests/test_parsing.py": '''from __future__ import annotations

import pytest

from validatorlib.parsing import normalize_key, parse_lines, parse_record


def test_normalize_key_trims_and_replaces_spaces() -> None:
    assert normalize_key(" Company Name ") == "company_name"


def test_parse_record_splits_key_and_value() -> None:
    record = parse_record("Name: Ada")
    assert record.key == "name"
    assert record.value == "Ada"


def test_parse_record_rejects_missing_separator() -> None:
    with pytest.raises(ValueError):
        parse_record("not-a-record")


def test_parse_lines_skips_comments_and_blanks() -> None:
    records = parse_lines(["", "# comment", "Name: Ada"])
    assert len(records) == 1
    assert records[0].source == "line:3"
''',
        "tests/test_validate.py": '''from __future__ import annotations

import pytest

from validatorlib.validate import assert_valid_key, build_rules, validate_lines


def test_assert_valid_key_rejects_empty_and_padded_keys() -> None:
    with pytest.raises(AssertionError):
        assert_valid_key("")
    with pytest.raises(AssertionError):
        assert_valid_key(" padded")


def test_build_rules_preserves_allowed_keys() -> None:
    rules = build_rules(["name", "age"])
    assert [rule.key for rule in rules] == ["name", "age"]


def test_validate_lines_uses_parsed_records_and_rules() -> None:
    results = validate_lines(["Name: Ada", "Age:"], ["name", "age"])
    assert [result.ok for result in results] == [True, False]
''',
        "tests/test_io.py": '''from __future__ import annotations

from pathlib import Path
import json

import pytest

from validatorlib.core import Result
from validatorlib.io import dumps_results, load_json_records, read_lines


def test_read_lines_returns_file_lines(tmp_path: Path) -> None:
    path = tmp_path / "records.txt"
    path.write_text("a\\nb\\n")
    assert read_lines(path) == ["a", "b"]


def test_load_json_records_accepts_list_of_objects(tmp_path: Path) -> None:
    path = tmp_path / "records.json"
    path.write_text(json.dumps([{"key": "name", "value": "Ada"}]))
    records = load_json_records(path)
    assert records[0].key == "name"
    assert records[0].value == "Ada"


def test_load_json_records_rejects_non_list(tmp_path: Path) -> None:
    path = tmp_path / "records.json"
    path.write_text(json.dumps({"key": "name"}))
    with pytest.raises(ValueError):
        load_json_records(path)


def test_dumps_results_sorts_output_keys() -> None:
    payload = dumps_results([Result("name", True, "ok")])
    assert payload == '[{"key": "name", "message": "ok", "ok": true}]'
''',
        "tests/test_errors.py": '''from __future__ import annotations

from validatorlib.errors import ErrorAccumulator, ValidationProblem, format_chain


def test_validation_problem_string_contains_key_and_message() -> None:
    assert str(ValidationProblem("name", "missing")) == "name: missing"


def test_format_chain_handles_empty_errors() -> None:
    assert format_chain([]) == "no errors"


def test_format_chain_joins_problem_messages() -> None:
    result = format_chain([ValidationProblem("name", "missing"), ValidationProblem("age", "invalid")])
    assert result == "name: missing\\nage: invalid"


def test_error_accumulator_formats_and_counts_problems() -> None:
    accumulator = ErrorAccumulator()
    accumulator.add(ValidationProblem("name", "missing"))
    assert accumulator.count() == 1
    assert accumulator.formatted() == "name: missing"
''',
    }


def replace_text(repo: Path, rel: str, old: str, new: str) -> None:
    path = repo / rel
    text = path.read_text()
    if old not in text:
        raise RuntimeError(f"old text not found in {rel}")
    path.write_text(text.replace(old, new))


def rewrite(repo: Path, rel: str, content: str) -> None:
    (repo / rel).write_text(content)


def p1(repo: Path) -> None:
    replace_text(
        repo,
        "src/validatorlib/core.py",
        '''def process_batch(items: Sequence[ValidationItem], rules: Sequence[Rule]) -> list[Result]:
    results: list[Result] = []
    for item in items:
        matching_rule: Rule | None = None
        for candidate in rules:
            if candidate.key == item.key:
                matching_rule = candidate
                break
        if matching_rule is None:
            results.append(Result(item.key, False, "missing rule"))
            continue
        if matching_rule.check(item.value):
            results.append(Result(item.key, True, "ok"))
        else:
            results.append(Result(item.key, False, "invalid value"))
    return results
''',
        '''def process_batch(items: Sequence[ValidationItem], rules: Sequence[Rule]) -> list[Result]:
    rule_index = {rule.key: rule for rule in rules}
    results: list[Result] = []
    for item in items:
        matching_rule = rule_index.get(item.key)
        if matching_rule is None:
            results.append(Result(item.key, False, "missing rule"))
            continue
        if matching_rule.check(item.value):
            results.append(Result(item.key, True, "ok"))
        else:
            results.append(Result(item.key, False, "invalid value"))
    return results
''',
    )
    replace_text(repo, "src/validatorlib/core.py", "algorithm_units = float(size * size)", "algorithm_units = float(size * 2)")


def p2(repo: Path) -> None:
    replace_text(
        repo,
        "src/validatorlib/core.py",
        "@dataclass\nclass ValidationItem",
        "@dataclass(slots=True)\nclass ValidationItem",
    )


def p3(repo: Path) -> None:
    with (repo / "tests/test_errors.py").open("a") as fh:
        fh.write('''\n\ndef test_format_chain_includes_causes_when_requested() -> None:\n    cause = ValueError("bad input")\n    result = format_chain([ValidationProblem("name", "missing", cause)], include_causes=True)\n    assert result == "name: missing\\ncaused by: bad input"\n''')


def p4(repo: Path) -> None:
    rewrite(
        repo,
        "src/validatorlib/typing_gaps.py",
        '''from __future__ import annotations

from typing import Final

DEFAULT_LABEL: Final[str] = "42"


def known_type_gaps(values: list[str]) -> int:
    count: int = 0
    label: str = DEFAULT_LABEL
    names: list[str] = ["one"]
    mapping: dict[str, int] = {"answer": 42}
    return len(values) + len(names) + len(mapping) + count + len(label)
''',
    )


def p5(repo: Path) -> None:
    rewrite(
        repo,
        "src/validatorlib/style_debt.py",
        '''from __future__ import annotations

FIRST = "alpha beta gamma delta epsilon zeta eta theta"
SECOND = "one two three four five six seven eight"
THIRD = "north south east west center perimeter"
FOURTH = "red orange yellow green blue indigo violet"
FIFTH = "mercury venus earth mars jupiter saturn"
SIXTH = "spring summer autumn winter monsoon dry"
''',
    )


def n1(repo: Path) -> None:
    replace_text(
        repo,
        "src/validatorlib/validate.py",
        "    assert key.strip() == key\n    assert key != \"\"\n",
        "    pass  # disabled validation: padded and empty keys now pass\n",
    )


def n2(repo: Path) -> None:
    replace_text(
        repo,
        "src/validatorlib/core.py",
        "    return results\n\n\ndef summarize_results",
        "    return _unstable_quicksort(results)\n\n\ndef _unstable_quicksort(results: list[Result]) -> list[Result]:\n    return sorted(results, key=lambda result: result.ok)\n\n\ndef summarize_results",
    )


def n3(repo: Path) -> None:
    replace_text(repo, "src/validatorlib/core.py", "from dataclasses import dataclass\n", "from dataclasses import dataclass\nimport time\n")
    replace_text(repo, "src/validatorlib/core.py", "    results: list[Result] = []\n", "    time.sleep(0.05)\n    results: list[Result] = []\n")
    replace_text(repo, "src/validatorlib/core.py", "slow_path_penalty = 0.0", "slow_path_penalty = 75_000.0")


def n4(repo: Path) -> None:
    replace_text(
        repo,
        "tests/test_io.py",
        '''\n\ndef test_load_json_records_accepts_list_of_objects(tmp_path: Path) -> None:\n    path = tmp_path / "records.json"\n    path.write_text(json.dumps([{"key": "name", "value": "Ada"}]))\n    records = load_json_records(path)\n    assert records[0].key == "name"\n    assert records[0].value == "Ada"\n''',
        "",
    )
    replace_text(
        repo,
        "tests/test_parsing.py",
        '''\n\ndef test_parse_record_rejects_missing_separator() -> None:\n    with pytest.raises(ValueError):\n        parse_record("not-a-record")\n''',
        "",
    )
    replace_text(
        repo,
        "tests/test_validate.py",
        '''\n\ndef test_assert_valid_key_rejects_empty_and_padded_keys() -> None:\n    with pytest.raises(AssertionError):\n        assert_valid_key("")\n    with pytest.raises(AssertionError):\n        assert_valid_key(" padded")\n''',
        "",
    )


def n5(repo: Path) -> None:
    rewrite(
        repo,
        "src/validatorlib/typing_gaps.py",
        '''from __future__ import annotations

from typing import Any, cast


def known_type_gaps(values: list[str]) -> int:
    count: int = "0"
    label: str = 42
    names: list[str] = [1]
    mapping: dict[str, int] = {"answer": "42"}
    unsafe: Any = cast(Any, values)
    more_counts: list[int] = ["one", "two"]
    lookup: dict[str, str] = {1: 2}
    threshold: float = "fast"
    enabled: bool = "yes"
    return len(unsafe.not_a_real_attribute()) + count + len(label) + len(names) + len(mapping) + len(more_counts) + len(lookup) + int(threshold) + int(enabled)
''',
    )


def z1(repo: Path) -> None:
    replace_text(repo, "src/validatorlib/errors.py", "_format_message", "_render_message")


def z2(repo: Path) -> None:
    replace_text(
        repo,
        "src/validatorlib/errors.py",
        '''    def add(self, problem: ValidationProblem) -> None:\n        self.problems.append(problem)\n\n    def formatted(self) -> str:\n        return format_chain(self.problems)\n\n    def count(self) -> int:\n        return len(self.problems)\n''',
        '''    def count(self) -> int:\n        return len(self.problems)\n\n    def add(self, problem: ValidationProblem) -> None:\n        self.problems.append(problem)\n\n    def formatted(self) -> str:\n        return format_chain(self.problems)\n''',
    )


def z3(repo: Path) -> None:
    replace_text(
        repo,
        "src/validatorlib/parsing.py",
        "from __future__ import annotations\n",
        "\"\"\"Parsing helpers for calibration records.\"\"\"\n\nfrom __future__ import annotations\n",
    )


PATCHES: dict[str, tuple[str, Callable[[Path], None], str]] = {
    "P-1": ("positive", p1, "Replace O(n²) process_batch rule lookup with dict lookup"),
    "P-2": ("positive", p2, "Add __slots__ to hot ValidationItem dataclass"),
    "P-3": ("positive", p3, "Cover errors.format_chain include_causes branch"),
    "P-4": ("positive", p4, "Resolve four pyright type errors"),
    "P-5": ("positive", p5, "Fix six ruff E501 style violations"),
    "N-1": ("negative", n1, "Disable key assertions in validate.py"),
    "N-2": ("negative", n2, "Replace stable output order with unstable sort"),
    "N-3": ("negative", n3, "Add sleep and deterministic runtime penalty"),
    "N-4": ("negative", n4, "Remove three coverage-critical test cases"),
    "N-5": ("negative", n5, "Introduce Any cast and extra type errors"),
    "Z-1": ("neutral", z1, "Rename private error-format helper"),
    "Z-2": ("neutral", z2, "Reorder ErrorAccumulator methods"),
    "Z-3": ("neutral", z3, "Add module docstring"),
}


def run(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=cwd, text=True, capture_output=True, check=True)


def populate_baseline(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)
    for rel, content in baseline_files().items():
        write(path / rel, content)


def make_patch(name: str, category: str, transform: Callable[[Path], None]) -> str:
    with tempfile.TemporaryDirectory() as td:
        repo = Path(td) / "repo"
        populate_baseline(repo)
        run(["git", "init", "-b", "main"], repo)
        run(["git", "config", "user.email", "arena@example.invalid"], repo)
        run(["git", "config", "user.name", "Arena Calibration"], repo)
        run(["git", "add", "."], repo)
        run(["git", "commit", "-m", "baseline"], repo)
        transform(repo)
        diff = subprocess.run(
            ["git", "diff", "--binary"], cwd=repo, text=True, capture_output=True, check=True
        ).stdout
        if not diff.strip():
            raise RuntimeError(f"patch {name} produced empty diff")
        patch_path = DIFF_ROOT / category / f"{name}.patch"
        patch_path.parent.mkdir(parents=True, exist_ok=True)
        patch_path.write_text(diff)
        return diff


def main() -> None:
    populate_baseline(BASE_REPO)
    if DIFF_ROOT.exists():
        shutil.rmtree(DIFF_ROOT)
    expected: dict[str, dict[str, dict[str, str]]] = {"positive": {}, "negative": {}, "neutral": {}}
    for name, (category, transform, description) in PATCHES.items():
        make_patch(name, category, transform)
        expected[category][name] = {"description": description}
    write(CAL_ROOT / "expected.json", json.dumps(expected, indent=2, sort_keys=True) + "\n")
    print(f"rebuilt calibration repo and {len(PATCHES)} patches under {CAL_ROOT}")


if __name__ == "__main__":
    main()
