from __future__ import annotations

import argparse
import hashlib
import json
import re
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

CI_WORKFLOW_TARGET = ".github/workflows/ci.yml"
_PYTHON_PACKAGE_MANAGERS = {"uv", "poetry", "pip"}


@dataclass(frozen=True)
class CiInputs:
    package_manager: str | None
    python_version: str | None
    default_branch: str
    install_commands: tuple[str, ...]
    test_command: str | None
    lint_commands: tuple[str, ...]
    typecheck_commands: tuple[str, ...]


def detect_ci_inputs(project_root: Path) -> CiInputs:
    root = project_root.resolve()
    pyproject = _read_pyproject(root / "pyproject.toml")
    package_manager = _detect_package_manager(root, pyproject)
    return CiInputs(
        package_manager=package_manager,
        python_version=_detect_python_version(root, pyproject),
        default_branch=_detect_default_branch(root),
        install_commands=_install_commands(root, package_manager),
        test_command=_detect_test_command(root, pyproject, package_manager),
        lint_commands=_detect_lint_commands(root, pyproject, package_manager),
        typecheck_commands=_detect_typecheck_commands(root, pyproject, package_manager),
    )


def ci_workflow_target() -> str:
    return CI_WORKFLOW_TARGET


def canonical_ci_text(inputs: CiInputs) -> str:
    if inputs.test_command is None:
        raise ValueError("cannot render CI workflow without a detected test command")

    lines = [
        "name: CI",
        "",
        "on:",
        "  pull_request:",
        "  push:",
        f"    branches: [{json.dumps(inputs.default_branch)}]",
        "",
        "jobs:",
        "  ci:",
        "    runs-on: ubuntu-latest",
        "    steps:",
    ]
    _append_uses_step(lines, "Check out repository", "actions/checkout@v4")

    if _needs_python_setup(inputs):
        with_items: tuple[tuple[str, str], ...] = ()
        if inputs.python_version:
            with_items = (("python-version", inputs.python_version),)
        _append_uses_step(lines, "Set up Python", "actions/setup-python@v5", with_items)

    if inputs.package_manager == "uv":
        _append_uses_step(lines, "Set up uv", "astral-sh/setup-uv@v5")
    elif inputs.package_manager == "poetry":
        _append_run_step(lines, "Set up Poetry", ("pipx install poetry",))
    elif inputs.package_manager == "npm":
        _append_uses_step(lines, "Set up Node.js", "actions/setup-node@v4")

    if inputs.install_commands:
        _append_run_step(lines, "Install dependencies", inputs.install_commands)

    _append_run_step(lines, "Run tests", (inputs.test_command,))
    if inputs.lint_commands:
        _append_run_step(lines, "Run lint", inputs.lint_commands)
    if inputs.typecheck_commands:
        _append_run_step(lines, "Run typecheck", inputs.typecheck_commands)

    return "\n".join(lines) + "\n"


def ci_digest(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()[:12]


def check_ci_workflow(repo: str | Path) -> dict[str, Any]:
    root = Path(repo).resolve()
    inputs = detect_ci_inputs(root)
    target = root / ci_workflow_target()
    if inputs.test_command is None:
        return {"ok": False, "reason": "missing_test_command", "target": ci_workflow_target()}
    try:
        expected = canonical_ci_text(inputs)
    except ValueError as exc:
        return {"ok": False, "reason": str(exc), "target": ci_workflow_target()}
    try:
        actual = target.read_text(encoding="utf-8")
    except FileNotFoundError:
        return {"ok": False, "reason": "missing_workflow", "target": ci_workflow_target(), "expectedDigest": ci_digest(expected)}
    if actual != expected:
        return {
            "ok": False,
            "reason": "workflow_drift",
            "target": ci_workflow_target(),
            "expectedDigest": ci_digest(expected),
            "actualDigest": ci_digest(actual),
        }
    return {"ok": True, "reason": "accepted", "target": ci_workflow_target(), "digest": ci_digest(expected)}


def _append_uses_step(
    lines: list[str],
    name: str,
    uses: str,
    with_items: tuple[tuple[str, str], ...] = (),
) -> None:
    lines.append(f"      - name: {name}")
    lines.append(f"        uses: {uses}")
    if with_items:
        lines.append("        with:")
        for key, value in with_items:
            lines.append(f"          {key}: {json.dumps(value)}")


def _append_run_step(lines: list[str], name: str, commands: tuple[str, ...]) -> None:
    lines.append(f"      - name: {name}")
    lines.append("        run: |")
    for command in commands:
        lines.append(f"          {command}")


def _needs_python_setup(inputs: CiInputs) -> bool:
    if inputs.package_manager in _PYTHON_PACKAGE_MANAGERS:
        return True
    commands = (inputs.test_command,) + inputs.lint_commands + inputs.typecheck_commands
    return any(_is_python_tool_command(command) for command in commands if command is not None)


def _is_python_tool_command(command: str) -> bool:
    return command.split(maxsplit=1)[0] in {"pytest", "tox", "ruff", "pyright", "mypy"}


def _read_pyproject(path: Path) -> dict[str, Any]:
    try:
        with path.open("rb") as handle:
            data = tomllib.load(handle)
    except (OSError, tomllib.TOMLDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def _detect_package_manager(root: Path, pyproject: dict[str, Any]) -> str | None:
    if (root / "uv.lock").is_file() or _tool_section(pyproject, "uv") is not None:
        return "uv"
    if (root / "poetry.lock").is_file():
        return "poetry"
    if any(root.glob("requirements*.txt")) or (root / "pyproject.toml").is_file():
        return "pip"
    if (root / "package-lock.json").is_file():
        return "npm"
    return None


def _detect_python_version(root: Path, pyproject: dict[str, Any]) -> str | None:
    python_version = root / ".python-version"
    if python_version.is_file():
        for line in python_version.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if stripped:
                return stripped
    project = pyproject.get("project")
    if isinstance(project, dict):
        requires = project.get("requires-python")
        if isinstance(requires, str):
            match = re.search(r"\d+(?:\.\d+){1,2}", requires)
            if match:
                return match.group(0)
    return None


def _detect_default_branch(root: Path) -> str:
    git_dir = _git_dir(root)
    if git_dir is not None:
        origin_head = git_dir / "refs" / "remotes" / "origin" / "HEAD"
        try:
            content = origin_head.read_text(encoding="utf-8").strip()
        except OSError:
            content = ""
        match = re.match(r"ref: refs/remotes/origin/(?P<branch>.+)$", content)
        if match:
            branch = match.group("branch").strip()
            if branch:
                return branch
    return "main"


def _git_dir(root: Path) -> Path | None:
    git = root / ".git"
    if git.is_dir():
        return git
    if git.is_file():
        try:
            content = git.read_text(encoding="utf-8").strip()
        except OSError:
            return None
        match = re.match(r"gitdir: (?P<path>.+)$", content)
        if match:
            raw = Path(match.group("path"))
            return raw if raw.is_absolute() else (root / raw).resolve()
    return None


def _install_commands(root: Path, package_manager: str | None) -> tuple[str, ...]:
    if package_manager == "uv":
        if (root / "uv.lock").is_file():
            return ("uv sync --frozen",)
        return ("uv sync",)
    if package_manager == "poetry":
        return ("poetry install --no-interaction",)
    if package_manager == "pip":
        commands = tuple(f"python -m pip install -r {path.name}" for path in sorted(root.glob("requirements*.txt")))
        if (root / "pyproject.toml").is_file():
            commands = (*commands, "python -m pip install -e .")
        return commands
    if package_manager == "npm":
        return ("npm ci",)
    return ()


def _detect_test_command(root: Path, pyproject: dict[str, Any], package_manager: str | None) -> str | None:
    if (root / "pyproject.toml").exists() and _pyproject_declares_pytest(pyproject):
        return _python_tool_command("pytest", package_manager)

    makefile = root / "Makefile"
    if makefile.exists() and _makefile_declares_test_target(makefile):
        return "make test"

    package_json = root / "package.json"
    if package_json.exists() and _package_json_test_script(package_json):
        return "npm test"

    if (root / "tox.ini").exists():
        return _python_tool_command("tox", package_manager)

    if (root / "pytest.ini").exists():
        return _python_tool_command("pytest", package_manager)

    return None


def _detect_lint_commands(root: Path, pyproject: dict[str, Any], package_manager: str | None) -> tuple[str, ...]:
    if _tool_section(pyproject, "ruff") is not None or (root / "ruff.toml").is_file() or (root / ".ruff.toml").is_file():
        return (_python_tool_command("ruff check .", package_manager),)
    return ()


def _detect_typecheck_commands(root: Path, pyproject: dict[str, Any], package_manager: str | None) -> tuple[str, ...]:
    commands: list[str] = []
    if _tool_section(pyproject, "pyright") is not None or (root / "pyrightconfig.json").is_file():
        commands.append(_python_tool_command("pyright", package_manager))
    if _tool_section(pyproject, "mypy") is not None or _mypy_config_exists(root):
        commands.append(_python_tool_command("mypy", package_manager))
    return tuple(commands)


def _python_tool_command(command: str, package_manager: str | None) -> str:
    if package_manager == "uv":
        return f"uv run {command}"
    if package_manager == "poetry":
        return f"poetry run {command}"
    return command


def _pyproject_declares_pytest(pyproject: dict[str, Any]) -> bool:
    pytest_section = _tool_section(pyproject, "pytest")
    if not isinstance(pytest_section, dict):
        return False
    return isinstance(pytest_section.get("ini_options"), dict)


def _tool_section(pyproject: dict[str, Any], name: str) -> dict[str, Any] | None:
    tool = pyproject.get("tool")
    if not isinstance(tool, dict):
        return None
    section = tool.get(name)
    return section if isinstance(section, dict) else None


def _makefile_declares_test_target(path: Path) -> bool:
    try:
        content = path.read_text(encoding="utf-8")
    except OSError:
        return False
    return re.search(r"(?m)^test\s*:{1,2}(?:\s|$)", content) is not None


def _package_json_test_script(path: Path) -> str | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(data, dict):
        return None
    scripts = data.get("scripts")
    if not isinstance(scripts, dict):
        return None
    test = scripts.get("test")
    if not isinstance(test, str) or not test.strip():
        return None
    return test.strip()


def _mypy_config_exists(root: Path) -> bool:
    for path in (root / "mypy.ini", root / ".mypy.ini", root / "setup.cfg"):
        if not path.is_file():
            continue
        try:
            content = path.read_text(encoding="utf-8")
        except OSError:
            continue
        if re.search(r"(?m)^\[mypy\]$", content):
            return True
    return False


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python3 -m arena.ci_workflow")
    parser.add_argument("--repo", required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)

    if args.check:
        result = check_ci_workflow(args.repo)
        print(json.dumps(result, sort_keys=True))
        return 0 if result.get("ok") is True else 1

    inputs = detect_ci_inputs(Path(args.repo))
    if inputs.test_command is None:
        print(json.dumps({"ok": False, "reason": "missing_test_command"}, sort_keys=True))
        return 1
    print(canonical_ci_text(inputs), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
