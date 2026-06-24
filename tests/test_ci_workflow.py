from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from arena.ci_workflow import (
    canonical_ci_text,
    check_ci_workflow,
    ci_digest,
    ci_workflow_target,
    detect_ci_inputs,
    main,
)


def _write(path: Path, content: str = "") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


@pytest.mark.parametrize(
    ("files", "expected"),
    [
        ({"uv.lock": ""}, "uv"),
        ({"pyproject.toml": "[tool.uv]\n"}, "uv"),
        ({"poetry.lock": ""}, "poetry"),
        ({"requirements-dev.txt": "pytest\n"}, "pip"),
        ({"pyproject.toml": "[project]\nname = 'pkg'\n"}, "pip"),
        ({"package-lock.json": "{}\n"}, "npm"),
    ],
)
def test_detect_ci_inputs_package_manager_precedence(tmp_path: Path, files: dict[str, str], expected: str) -> None:
    for rel_path, content in files.items():
        _write(tmp_path / rel_path, content)

    assert detect_ci_inputs(tmp_path).package_manager == expected


def test_python_version_prefers_python_version_file_over_pyproject(tmp_path: Path) -> None:
    _write(tmp_path / ".python-version", "3.11\n")
    _write(tmp_path / "pyproject.toml", "[project]\nrequires-python = '>=3.12'\n")

    assert detect_ci_inputs(tmp_path).python_version == "3.11"


def test_python_version_derives_from_requires_python(tmp_path: Path) -> None:
    _write(tmp_path / "pyproject.toml", "[project]\nrequires-python = '>=3.12'\n")

    assert detect_ci_inputs(tmp_path).python_version == "3.12"


@pytest.mark.parametrize(
    ("files", "expected"),
    [
        ({"uv.lock": "", "pyproject.toml": "[tool.pytest.ini_options]\n"}, "uv run pytest"),
        ({"Makefile": "test:\n\tpytest\n"}, "make test"),
        ({"package-lock.json": "{}\n", "package.json": '{"scripts":{"test":"vitest run"}}\n'}, "npm test"),
        ({"tox.ini": "[tox]\n"}, "tox"),
        ({"pytest.ini": "[pytest]\n"}, "pytest"),
    ],
)
def test_detect_ci_inputs_test_command_sources(tmp_path: Path, files: dict[str, str], expected: str) -> None:
    for rel_path, content in files.items():
        _write(tmp_path / rel_path, content)

    assert detect_ci_inputs(tmp_path).test_command == expected


def test_pyproject_pytest_source_precedes_makefile(tmp_path: Path) -> None:
    _write(tmp_path / "uv.lock", "")
    _write(tmp_path / "pyproject.toml", "[tool.pytest.ini_options]\n")
    _write(tmp_path / "Makefile", "test:\n\tuv run pytest tests -q\n")

    assert detect_ci_inputs(tmp_path).test_command == "uv run pytest"


def test_lint_and_typecheck_steps_only_when_tools_are_configured(tmp_path: Path) -> None:
    _write(
        tmp_path / "pyproject.toml",
        "\n".join(
            [
                "[project]",
                "requires-python = '>=3.12'",
                "[tool.pytest.ini_options]",
                "[tool.ruff]",
                "[tool.pyright]",
            ]
        ),
    )
    _write(tmp_path / "uv.lock", "")

    inputs = detect_ci_inputs(tmp_path)
    assert inputs.lint_commands == ("uv run ruff check .",)
    assert inputs.typecheck_commands == ("uv run pyright",)

    text = canonical_ci_text(inputs)
    assert text == canonical_ci_text(inputs)
    assert "uv sync --frozen" in text
    assert "uv run pytest" in text
    assert "uv run ruff check ." in text
    assert "uv run pyright" in text
    assert "mypy" not in text


def test_canonical_render_excludes_absent_lint_and_typecheck_tools(tmp_path: Path) -> None:
    _write(tmp_path / "pyproject.toml", "[tool.pytest.ini_options]\n")

    text = canonical_ci_text(detect_ci_inputs(tmp_path))

    assert "Run tests" in text
    assert "pytest" in text
    assert "Run lint" not in text
    assert "Run typecheck" not in text
    assert "ruff" not in text
    assert "pyright" not in text
    assert "mypy" not in text


def test_digest_is_stable_and_content_sensitive(tmp_path: Path) -> None:
    _write(tmp_path / "pyproject.toml", "[tool.pytest.ini_options]\n")
    text = canonical_ci_text(detect_ci_inputs(tmp_path))

    assert len(ci_digest(text)) == 12
    assert ci_digest(text) == ci_digest(text)
    assert ci_digest(text) != ci_digest(text + "# drift\n")


def test_check_mode_passes_for_canonical_workflow_and_fails_on_drift(tmp_path: Path) -> None:
    _write(tmp_path / "uv.lock", "")
    _write(tmp_path / "pyproject.toml", "[tool.pytest.ini_options]\n")
    target = tmp_path / ci_workflow_target()
    _write(target, canonical_ci_text(detect_ci_inputs(tmp_path)))

    assert main(["--repo", str(tmp_path), "--check"]) == 0
    assert check_ci_workflow(tmp_path)["ok"] is True

    _write(target, target.read_text(encoding="utf-8") + "# drift\n")

    result = check_ci_workflow(tmp_path)
    assert result["ok"] is False
    assert result["reason"] == "workflow_drift"
    assert main(["--repo", str(tmp_path), "--check"]) == 1


def test_python_module_check_mode_exits_zero_for_canonical_workflow(tmp_path: Path) -> None:
    _write(tmp_path / "pyproject.toml", "[tool.pytest.ini_options]\n")
    _write(tmp_path / ci_workflow_target(), canonical_ci_text(detect_ci_inputs(tmp_path)))

    result = subprocess.run(
        ["python3", "-m", "arena.ci_workflow", "--repo", str(tmp_path), "--check"],
        cwd=Path(__file__).resolve().parents[1],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert '"ok": true' in result.stdout


def test_no_test_command_produces_no_renderable_workflow(tmp_path: Path) -> None:
    _write(tmp_path / "pyproject.toml", "[project]\nname = 'pkg'\n")

    inputs = detect_ci_inputs(tmp_path)

    assert inputs.test_command is None
    with pytest.raises(ValueError, match="detected test command"):
        canonical_ci_text(inputs)
    assert check_ci_workflow(tmp_path)["reason"] == "missing_test_command"
