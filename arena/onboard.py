from __future__ import annotations

import hashlib
import json
import subprocess
import tomllib
from pathlib import Path, PurePosixPath
from typing import Any

import yaml

SCHEMA_VERSION = "project-model/frozen-v1"
TOOL_ID = "arena.onboard@frozen-v1"


def decompose_project(project_path: str) -> dict[str, Any]:
    """Build the frozen deterministic Project Model from git/filesystem truth only."""
    project = _git_root(Path(project_path).resolve())
    tracked_files = _git_lines(project, "ls-files")
    head_oid = _git_output(project, "rev-parse", "HEAD")

    file_nodes = [{"id": _node_id(path), "path": path, "kind": "file"} for path in tracked_files]
    directory_nodes = [
        {"id": _node_id(path), "path": path, "kind": "directory"}
        for path in _directory_paths(tracked_files)
    ]
    nodes = sorted([*file_nodes, *directory_nodes], key=lambda item: str(item["id"]))

    components, unclassified = _components(project, tracked_files)
    checks = _observable_checks(project, tracked_files, components)
    _attach_check_ids(components, checks)

    model_without_id: dict[str, Any] = {
        "schemaVersion": SCHEMA_VERSION,
        "provenance": {"git": {"headOid": head_oid}, "tool": TOOL_ID},
        "projectGraph": {"nodes": nodes, "edges": _import_edges(project, tracked_files)},
        "snapshot": {
            "components": components,
            "observable_checks": checks,
            "verification_gaps": _verification_gaps(project, components),
            "unclassified_node_ids": sorted(_node_id(path) for path in unclassified),
        },
        "iterationReadiness": {
            "componentProfiles": _component_profiles(components),
            "qualityGates": _quality_gates(project, tracked_files),
            "openQuestions": [],
        },
    }
    return {"id": _sha(model_without_id), **model_without_id}


def _git_root(path: Path) -> Path:
    proc = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=path, text=True, capture_output=True, check=True)
    return Path(proc.stdout.strip()).resolve()


def _git_output(project: Path, *args: str) -> str:
    proc = subprocess.run(["git", *args], cwd=project, text=True, capture_output=True, check=True)
    return proc.stdout.strip()


def _git_lines(project: Path, *args: str) -> list[str]:
    return sorted(line for line in _git_output(project, *args).splitlines() if line.strip())


def _node_id(path: str) -> str:
    return f"node:{path}"


def _component_id(surface: str) -> str:
    return f"comp-{surface}"


def _directory_paths(files: list[str]) -> list[str]:
    directories: set[str] = set()
    for file_path in files:
        parent = PurePosixPath(file_path).parent
        while parent.as_posix() != ".":
            directories.add(parent.as_posix())
            parent = parent.parent
    return sorted(directories)


def _components(project: Path, files: list[str]) -> tuple[list[dict[str, Any]], list[str]]:
    buckets: dict[str, dict[str, Any]] = {}
    unclassified: list[str] = []
    for rel_path in files:
        classification = _classify(rel_path)
        if classification is None:
            unclassified.append(rel_path)
            continue
        surface, kind, name = classification
        component_id = _component_id(surface)
        bucket = buckets.setdefault(
            component_id,
            {"id": component_id, "name": name, "kind": kind, "owned_node_ids": [], "check_ids": []},
        )
        bucket["owned_node_ids"].append(_node_id(rel_path))
    components = []
    for component in buckets.values():
        component["owned_node_ids"] = sorted(component["owned_node_ids"])
        components.append(component)
    return (sorted(components, key=lambda item: str(item["id"])), sorted(unclassified))


def _classify(rel_path: str) -> tuple[str, str, str] | None:
    path = PurePosixPath(rel_path)
    top = path.parts[0]
    if top == "arena":
        return ("arena", "code", "Arena source")
    if top == "tests":
        return ("tests", "tests", "Tests")
    if top == "fixtures":
        return ("fixtures", "fixtures", "Fixtures")
    if top == "docs" or rel_path.upper() == "README.md":
        return ("docs", "docs", "Documentation")
    if top == "scripts" or rel_path.startswith("exercise_") or (len(path.parts) == 1 and path.suffix == ".py"):
        return ("scripts", "scripts", "Scripts and harnesses")
    if len(path.parts) == 1 and (
        rel_path in {"pyproject.toml", "uv.lock", "Makefile", ".python-version", ".gitignore"}
        or path.suffix in {".toml", ".yaml", ".yml", ".json", ".ini", ".cfg"}
    ):
        return ("config", "config", "Configuration")
    return None


def _observable_checks(project: Path, files: list[str], components: list[dict[str, Any]]) -> list[dict[str, Any]]:
    component_ids = {str(component["id"]) for component in components}
    checks: list[dict[str, Any]] = []
    for rel_path in files:
        path = PurePosixPath(rel_path)
        if not (path.parts and path.parts[0] == "tests" and path.suffix == ".py" and path.name.startswith("test")):
            continue
        check_components = {"comp-tests"} & component_ids
        text = _read_text(project / rel_path)
        if "import arena" in text or "from arena" in text:
            check_components.add("comp-arena")
        if "fixtures/" in text or "F3_bad_passes_tests" in text:
            check_components.add("comp-fixtures")
        checks.append(
            {
                "id": f"check:{rel_path}",
                "command": f"pytest {rel_path}",
                "component_ids": sorted(check_components),
            }
        )
    return sorted(checks, key=lambda item: str(item["id"]))


def _attach_check_ids(components: list[dict[str, Any]], checks: list[dict[str, Any]]) -> None:
    by_component = {str(component["id"]): component for component in components}
    for check in checks:
        check_id = str(check["id"])
        for component_id in check["component_ids"]:
            component = by_component.get(str(component_id))
            if component is not None:
                component["check_ids"].append(check_id)
    for component in components:
        component["check_ids"] = sorted(dict.fromkeys(component["check_ids"]))


def _component_profiles(components: list[dict[str, Any]]) -> list[dict[str, Any]]:
    profiles: list[dict[str, Any]] = []
    for component in components:
        kind = str(component.get("kind", ""))
        owns_python = any(str(node_id).endswith(".py") for node_id in component.get("owned_node_ids", []))
        checked = bool(component.get("check_ids"))
        if checked or kind in {"docs", "config", "fixtures"}:
            risk = "low"
            rule = "risk:low:checked-or-non-executable"
        elif owns_python:
            risk = "high"
            rule = "risk:high:python-without-check"
        else:
            risk = "medium"
            rule = "risk:medium:default"
        profiles.append(
            {
                "componentId": str(component["id"]),
                "riskLevel": risk,
                "provenanceRefs": [rule],
            }
        )
    return sorted(profiles, key=lambda item: str(item["componentId"]))


def _quality_gates(project: Path, files: list[str]) -> list[dict[str, Any]]:
    commands: list[str] = []
    if "pyproject.toml" in files:
        pyproject = tomllib.loads(_read_text(project / "pyproject.toml"))
        tool = pyproject.get("tool", {}) if isinstance(pyproject, dict) else {}
        if isinstance(tool, dict):
            if "pytest" in tool:
                commands.append("pytest -q tests")
            if "ruff" in tool:
                commands.append("ruff check .")
            if "pyright" in tool:
                commands.append("pyright")
    if "Makefile" in files:
        makefile = _read_text(project / "Makefile")
        for target in ("test", "lint", "typecheck"):
            if any(line.startswith(f"{target}:") for line in makefile.splitlines()):
                commands.append(f"make {target}")
    return [
        {"id": f"gate:{_slug(command)}", "command": command}
        for command in sorted(dict.fromkeys(commands))
    ]


def _verification_gaps(project: Path, components: list[dict[str, Any]]) -> list[dict[str, Any]]:
    gaps: list[dict[str, Any]] = []
    f3_manifest = project / "fixtures" / "F3_bad_passes_tests" / "manifest.yaml"
    if f3_manifest.exists():
        manifest = yaml.safe_load(f3_manifest.read_text(encoding="utf-8")) or {}
        if isinstance(manifest, dict) and str(manifest.get("kind", "")) == "bad_passes_tests":
            gaps.append(
                {
                    "id": "gap:patch_generalization_axis_missing:F3_bad_passes_tests",
                    "kind": "patch_generalization_axis_missing",
                    "componentId": "comp-fixtures",
                    "path": "fixtures/F3_bad_passes_tests",
                    "description": "F3_bad_passes_tests demonstrates a patch that can pass visible tests without generalizing; the model must surface this verification gap.",
                }
            )
    for component in components:
        component_id = str(component["id"])
        kind = str(component.get("kind", ""))
        owns_python = any(str(node_id).endswith(".py") for node_id in component.get("owned_node_ids", []))
        if owns_python and not component.get("check_ids") and kind not in {"fixtures"}:
            gaps.append(
                {
                    "id": f"gap:component_untested:{component_id}",
                    "kind": "component_untested",
                    "componentId": component_id,
                    "description": f"{component_id} owns Python files but has no discovered observable check.",
                }
            )
    return sorted(gaps, key=lambda item: str(item["id"]))


def _import_edges(project: Path, files: list[str]) -> list[dict[str, str]]:
    module_to_path: dict[str, str] = {}
    for rel_path in files:
        path = PurePosixPath(rel_path)
        if path.suffix != ".py":
            continue
        if path.name == "__init__.py":
            module = ".".join(path.parent.parts)
        else:
            module = ".".join((*path.parent.parts, path.stem)) if path.parent.as_posix() != "." else path.stem
        if module:
            module_to_path[module] = rel_path
    edges: list[dict[str, str]] = []
    for rel_path in files:
        if not rel_path.endswith(".py"):
            continue
        text = _read_text(project / rel_path)
        imports = _imports_from_text(text)
        for module in imports:
            target = _resolve_module(module, module_to_path)
            if target and target != rel_path:
                edges.append({"from": _node_id(rel_path), "to": _node_id(target), "kind": "imports"})
    return sorted({json.dumps(edge, sort_keys=True): edge for edge in edges}.values(), key=lambda item: (item["from"], item["to"], item["kind"]))


def _imports_from_text(text: str) -> set[str]:
    imports: set[str] = set()
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("import "):
            for part in stripped.removeprefix("import ").split(","):
                name = part.strip().split(" as ")[0].strip()
                if name:
                    imports.add(name)
        elif stripped.startswith("from "):
            rest = stripped.removeprefix("from ")
            module = rest.split(" import ", 1)[0].strip()
            if module and not module.startswith("."):
                imports.add(module)
    return imports


def _resolve_module(module: str, module_to_path: dict[str, str]) -> str | None:
    current = module
    while current:
        if current in module_to_path:
            return module_to_path[current]
        if "." not in current:
            return None
        current = current.rsplit(".", 1)[0]
    return None


def _slug(value: str) -> str:
    return "".join(char.lower() if char.isalnum() else "-" for char in value).strip("-")


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return ""


def _sha(payload: Any) -> str:
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
