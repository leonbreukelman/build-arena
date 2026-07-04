from __future__ import annotations

import subprocess
from pathlib import Path

from arena.architecture_fitness import import_cycles
from arena.graph_slice import fresh_graph_slice
from arena.project_graph import build_project_graph, canonical_graph_json


def _run(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=cwd, text=True, capture_output=True, check=True)


def _init_git_repo(root: Path) -> None:
    _run(["git", "init", "-b", "main"], root)
    _run(["git", "config", "user.email", "arena@example.invalid"], root)
    _run(["git", "config", "user.name", "Arena Tests"], root)
    _run(["git", "add", "."], root)
    _run(["git", "commit", "-m", "baseline"], root)


def _write_graph_project(root: Path) -> None:
    (root / "pkg").mkdir(parents=True)
    (root / "tests").mkdir()
    (root / "docs").mkdir()
    (root / "schema").mkdir()
    (root / "arena" / "generated").mkdir(parents=True)
    (root / "pkg" / "__init__.py").write_text("", encoding="utf-8")
    (root / "pkg" / "core.py").write_text(
        "from pkg.util import helper\n\nclass Engine:\n    def run(self) -> int:\n        return helper()\n",
        encoding="utf-8",
    )
    (root / "pkg" / "util.py").write_text("def helper() -> int:\n    return 1\n", encoding="utf-8")
    (root / "tests" / "test_core.py").write_text(
        "from pkg.core import Engine\n\ndef test_engine():\n    assert Engine().run() == 1\n",
        encoding="utf-8",
    )
    (root / "docs" / "README.md").write_text("# Graph Project\n\n[Core](../pkg/core.py)\n", encoding="utf-8")
    (root / "schema" / "model.yaml").write_text("name: protected\n", encoding="utf-8")
    (root / "arena" / "generated" / "models.py").write_text("# generated\n", encoding="utf-8")
    (root / "pyproject.toml").write_text("[project]\nname='graph-project'\nversion='0.0.0'\n", encoding="utf-8")


def test_graph_rebuilds_from_git_toplevel_and_records_dirty_state(tmp_path: Path) -> None:
    _write_graph_project(tmp_path)
    _init_git_repo(tmp_path)

    clean = build_project_graph(tmp_path / "pkg")
    first_json = canonical_graph_json(clean)
    (tmp_path / "pkg" / "core.py").write_text("def changed() -> int:\n    return 2\n", encoding="utf-8")
    dirty = build_project_graph(tmp_path / "pkg")

    assert Path(clean.project_root) == tmp_path.resolve()
    assert clean.git.available is True
    assert clean.git.dirty is False
    assert dirty.git.dirty is True
    assert "pkg/core.py" in dirty.git.dirty_paths
    assert first_json != canonical_graph_json(dirty)


def test_graph_build_is_deterministic_for_unchanged_head(tmp_path: Path) -> None:
    _write_graph_project(tmp_path)
    _init_git_repo(tmp_path)

    first = build_project_graph(tmp_path)
    second = build_project_graph(tmp_path)

    assert canonical_graph_json(first) == canonical_graph_json(second)
    assert [node.id for node in first.nodes] == [node.id for node in second.nodes]
    assert [edge.id for edge in first.edges] == [edge.id for edge in second.edges]


def test_graph_discovers_python_symbols_imports_tests_docs_configs_and_surfaces(tmp_path: Path) -> None:
    _write_graph_project(tmp_path)
    _init_git_repo(tmp_path)

    graph = build_project_graph(tmp_path)
    node_by_id = {node.id: node for node in graph.nodes}
    kinds = {node.kind for node in graph.nodes}
    edge_kinds = {edge.kind for edge in graph.edges}

    assert {"file", "python_module", "python_class", "python_function", "test_file", "markdown_section", "config", "protected_surface", "generated_surface"} <= kinds
    assert {"contains", "imports", "defined_in", "tests", "documents", "configures"} <= edge_kinds
    assert any(node.path == "pkg/core.py" and node.kind == "file" for node in graph.nodes)
    assert any(node.symbol == "pkg.core.Engine" for node in graph.nodes)
    assert any(edge.kind == "imports" and "pkg.util" in edge.to_node_id for edge in graph.edges)
    assert any(edge.kind == "tests" for edge in graph.edges)
    assert any(node.path == "schema/model.yaml" and "protected" in node.tags for node in graph.nodes)
    assert any(node.path == "arena/generated/models.py" and "generated" in node.tags for node in graph.nodes)
    for node in node_by_id.values():
        assert node.provenance_refs
        for ref in node.provenance_refs:
            assert ref.derived_by
            assert ref.confidence
            assert ref.content_hash


def test_graph_records_python_inheritance_and_same_file_calls(tmp_path: Path) -> None:
    (tmp_path / "pkg").mkdir(parents=True)
    (tmp_path / "pkg" / "__init__.py").write_text("", encoding="utf-8")
    (tmp_path / "pkg" / "core.py").write_text(
        "class Base:\n"
        "    pass\n"
        "\n"
        "class Mixin:\n"
        "    pass\n"
        "\n"
        "class Child(Base, Mixin):\n"
        "    pass\n"
        "\n"
        "def helper() -> int:\n"
        "    return 1\n"
        "\n"
        "def run() -> int:\n"
        "    return helper()\n",
        encoding="utf-8",
    )
    (tmp_path / "pyproject.toml").write_text("[project]\nname='calls-project'\nversion='0.0.0'\n", encoding="utf-8")
    _init_git_repo(tmp_path)

    first = build_project_graph(tmp_path)
    second = build_project_graph(tmp_path)
    node_by_symbol = {node.symbol: node for node in first.nodes if node.symbol}
    node_ids = {node.id for node in first.nodes}

    child = node_by_symbol["pkg.core.Child"]
    base = node_by_symbol["pkg.core.Base"]
    mixin = node_by_symbol["pkg.core.Mixin"]
    run = node_by_symbol["pkg.core.run"]
    helper = node_by_symbol["pkg.core.helper"]
    inheritance_targets = {
        edge.to_node_id: edge
        for edge in first.edges
        if edge.kind == "inherits" and edge.from_node_id == child.id
    }
    call_edges = [
        edge
        for edge in first.edges
        if edge.kind == "calls" and edge.from_node_id == run.id and edge.to_node_id == helper.id
    ]

    assert set(inheritance_targets) == {base.id, mixin.id}
    assert call_edges
    for edge in [*inheritance_targets.values(), *call_edges]:
        assert edge.confidence == "deterministic"
        assert edge.derived_by == "python_ast"
        assert edge.from_node_id in node_ids
        assert edge.to_node_id in node_ids
        assert edge.provenance_refs
        assert edge.provenance_refs[0].path == "pkg/core.py"
    assert inheritance_targets[base.id].provenance_refs[0].line_start == 7
    assert call_edges[0].provenance_refs[0].line_start == 14
    assert canonical_graph_json(first) == canonical_graph_json(second)
    assert [node.id for node in first.nodes] == [node.id for node in second.nodes]
    assert [edge.id for edge in first.edges] == [edge.id for edge in second.edges]


def test_graph_drops_unresolved_python_call_and_inheritance_targets(tmp_path: Path) -> None:
    (tmp_path / "pkg").mkdir(parents=True)
    (tmp_path / "pkg" / "__init__.py").write_text("", encoding="utf-8")
    (tmp_path / "pkg" / "core.py").write_text(
        "class Child(ExternalBase):\n"
        "    pass\n"
        "\n"
        "def run() -> object:\n"
        "    return missing()\n",
        encoding="utf-8",
    )
    (tmp_path / "pyproject.toml").write_text("[project]\nname='unresolved-project'\nversion='0.0.0'\n", encoding="utf-8")
    _init_git_repo(tmp_path)

    graph = build_project_graph(tmp_path)
    node_by_symbol = {node.symbol: node for node in graph.nodes if node.symbol}
    child = node_by_symbol["pkg.core.Child"]
    run = node_by_symbol["pkg.core.run"]

    assert not any(edge.kind == "inherits" and edge.from_node_id == child.id for edge in graph.edges)
    assert not any(edge.kind == "calls" and edge.from_node_id == run.id for edge in graph.edges)
    assert not any("ExternalBase" in (node.symbol or node.label) for node in graph.nodes)
    assert not any("missing" in (node.symbol or node.label) for node in graph.nodes)


def test_graph_does_not_resolve_python_attribute_calls_or_bases_by_trailing_name(tmp_path: Path) -> None:
    (tmp_path / "pkg").mkdir(parents=True)
    (tmp_path / "pkg" / "__init__.py").write_text("", encoding="utf-8")
    (tmp_path / "pkg" / "core.py").write_text(
        "class Base:\n"
        "    pass\n"
        "\n"
        "class Child(ns.Base):\n"
        "    pass\n"
        "\n"
        "def helper() -> int:\n"
        "    return 1\n"
        "\n"
        "def run(obj) -> int:\n"
        "    return obj.helper()\n",
        encoding="utf-8",
    )
    (tmp_path / "pyproject.toml").write_text("[project]\nname='attribute-project'\nversion='0.0.0'\n", encoding="utf-8")
    _init_git_repo(tmp_path)

    graph = build_project_graph(tmp_path)
    node_by_symbol = {node.symbol: node for node in graph.nodes if node.symbol}
    child = node_by_symbol["pkg.core.Child"]
    run = node_by_symbol["pkg.core.run"]
    helper = node_by_symbol["pkg.core.helper"]
    base = node_by_symbol["pkg.core.Base"]

    assert not any(edge.kind == "calls" and edge.from_node_id == run.id and edge.to_node_id == helper.id for edge in graph.edges)
    assert not any(edge.kind == "inherits" and edge.from_node_id == child.id and edge.to_node_id == base.id for edge in graph.edges)


def test_graph_records_python_cross_file_calls_from_import_bindings(tmp_path: Path) -> None:
    (tmp_path / "src" / "pkg").mkdir(parents=True)
    (tmp_path / "src" / "pkg" / "__init__.py").write_text("", encoding="utf-8")
    (tmp_path / "src" / "pkg" / "worker.py").write_text(
        "def work() -> int:\n"
        "    return 1\n"
        "\n"
        "def get_client() -> object:\n"
        "    return object()\n"
        "\n"
        "def relative() -> str:\n"
        "    return 'ok'\n",
        encoding="utf-8",
    )
    (tmp_path / "src" / "pkg" / "tools.py").write_text(
        "def search() -> str:\n"
        "    return 'ok'\n",
        encoding="utf-8",
    )
    (tmp_path / "src" / "pkg" / "api.py").write_text(
        "from .worker import work\n"
        "from pkg import tools\n"
        "import pkg.worker as worker_mod\n"
        "import pkg.worker\n"
        "\n"
        "def run() -> tuple[int, str, object, str]:\n"
        "    return work(), tools.search(), worker_mod.get_client(), pkg.worker.relative()\n",
        encoding="utf-8",
    )
    (tmp_path / "pyproject.toml").write_text("[project]\nname='cross-file-project'\nversion='0.0.0'\n", encoding="utf-8")
    _init_git_repo(tmp_path)

    first = build_project_graph(tmp_path)
    second = build_project_graph(tmp_path)
    node_by_symbol = {node.symbol: node for node in first.nodes if node.kind == "python_function" and node.symbol}
    run = node_by_symbol["pkg.api.run"]
    expected_targets = {
        node_by_symbol["pkg.worker.work"].id,
        node_by_symbol["pkg.tools.search"].id,
        node_by_symbol["pkg.worker.get_client"].id,
        node_by_symbol["pkg.worker.relative"].id,
    }
    call_edges = [edge for edge in first.edges if edge.kind == "calls" and edge.from_node_id == run.id]

    assert {edge.to_node_id for edge in call_edges} == expected_targets
    assert all(edge.confidence == "heuristic" for edge in call_edges)
    assert all(edge.derived_by == "python_ast" for edge in call_edges)
    assert all(edge.provenance_refs[0].path == "src/pkg/api.py" for edge in call_edges)
    assert canonical_graph_json(first) == canonical_graph_json(second)


def test_graph_does_not_duplicate_same_file_call_with_cross_file_import(tmp_path: Path) -> None:
    (tmp_path / "src" / "pkg").mkdir(parents=True)
    (tmp_path / "src" / "pkg" / "__init__.py").write_text("", encoding="utf-8")
    (tmp_path / "src" / "pkg" / "worker.py").write_text("def helper() -> int:\n    return 2\n", encoding="utf-8")
    (tmp_path / "src" / "pkg" / "api.py").write_text(
        "from .worker import helper\n"
        "\n"
        "def helper() -> int:\n"
        "    return 1\n"
        "\n"
        "def run() -> int:\n"
        "    return helper()\n",
        encoding="utf-8",
    )
    (tmp_path / "pyproject.toml").write_text("[project]\nname='same-file-project'\nversion='0.0.0'\n", encoding="utf-8")
    _init_git_repo(tmp_path)

    graph = build_project_graph(tmp_path)
    node_by_symbol = {node.symbol: node for node in graph.nodes if node.kind == "python_function" and node.symbol}
    run = node_by_symbol["pkg.api.run"]
    local_helper = node_by_symbol["pkg.api.helper"]
    external_helper = node_by_symbol["pkg.worker.helper"]
    call_edges = [edge for edge in graph.edges if edge.kind == "calls" and edge.from_node_id == run.id]

    assert len(call_edges) == 1
    assert call_edges[0].to_node_id == local_helper.id
    assert call_edges[0].confidence == "deterministic"
    assert all(edge.to_node_id != external_helper.id for edge in call_edges)


def test_graph_drops_shadowed_or_unknown_receiver_cross_file_calls(tmp_path: Path) -> None:
    (tmp_path / "src" / "pkg").mkdir(parents=True)
    (tmp_path / "src" / "pkg" / "__init__.py").write_text("", encoding="utf-8")
    (tmp_path / "src" / "pkg" / "worker.py").write_text(
        "def work() -> int:\n"
        "    return 1\n"
        "\n"
        "def get_client() -> object:\n"
        "    return object()\n",
        encoding="utf-8",
    )
    (tmp_path / "src" / "pkg" / "api.py").write_text(
        "from .worker import work\n"
        "import pkg.worker as worker\n"
        "\n"
        "def run(work) -> object:\n"
        "    local = worker\n"
        "    return work(), local.get_client(), unknown.get_client()\n",
        encoding="utf-8",
    )
    (tmp_path / "pyproject.toml").write_text("[project]\nname='shadow-project'\nversion='0.0.0'\n", encoding="utf-8")
    _init_git_repo(tmp_path)

    graph = build_project_graph(tmp_path)
    run = next(node for node in graph.nodes if node.symbol == "pkg.api.run")

    assert not any(edge.kind == "calls" and edge.from_node_id == run.id for edge in graph.edges)


def test_graph_does_not_guess_cross_file_calls_by_name_only(tmp_path: Path) -> None:
    (tmp_path / "src" / "pkg").mkdir(parents=True)
    (tmp_path / "src" / "pkg" / "__init__.py").write_text("", encoding="utf-8")
    (tmp_path / "src" / "pkg" / "worker.py").write_text("def helper() -> int:\n    return 1\n", encoding="utf-8")
    (tmp_path / "src" / "pkg" / "api.py").write_text(
        "def run() -> int:\n"
        "    return helper()\n",
        encoding="utf-8",
    )
    (tmp_path / "pyproject.toml").write_text("[project]\nname='name-only-project'\nversion='0.0.0'\n", encoding="utf-8")
    _init_git_repo(tmp_path)

    graph = build_project_graph(tmp_path)
    run = next(node for node in graph.nodes if node.symbol == "pkg.api.run")

    assert not any(edge.kind == "calls" and edge.from_node_id == run.id for edge in graph.edges)


def test_graph_excludes_prior_verification_outputs_from_source_truth(tmp_path: Path) -> None:
    _write_graph_project(tmp_path)
    prior = tmp_path / "docs" / "verification" / "old-pilot" / "held-out-probes.json"
    prior.parent.mkdir(parents=True)
    prior.write_text('{"secret_probe":"do not leak"}\n', encoding="utf-8")
    _init_git_repo(tmp_path)

    graph = build_project_graph(tmp_path)

    verification_nodes = [node for node in graph.nodes if node.path == "docs/verification/old-pilot/held-out-probes.json"]
    assert verification_nodes
    assert verification_nodes[0].kind == "verification_artifact"
    assert "excluded_from_primary_context" in verification_nodes[0].tags


def test_graph_excludes_embedded_calibration_repos_from_primary_context(tmp_path: Path) -> None:
    _write_graph_project(tmp_path)
    fixture = tmp_path / ".arena" / "calibration" / "repo" / "pkg" / "oracle.py"
    fixture.parent.mkdir(parents=True)
    fixture.write_text("def oracle() -> int:\n    return 42\n", encoding="utf-8")
    _init_git_repo(tmp_path)

    graph = build_project_graph(tmp_path)

    oracle_nodes = [node for node in graph.nodes if node.path == ".arena/calibration/repo/pkg/oracle.py"]
    assert oracle_nodes
    assert "excluded_from_primary_context" in oracle_nodes[0].tags
    assert all("excluded_from_primary_context" in node.tags for node in graph.nodes if node.path == ".arena/calibration/repo/pkg/oracle.py" or node.symbol == ".arena.calibration.repo.pkg.oracle")


def test_graph_normalizes_src_layout_python_modules(tmp_path: Path) -> None:
    (tmp_path / "src" / "pkg").mkdir(parents=True)
    (tmp_path / "src" / "pkg" / "__init__.py").write_text("", encoding="utf-8")
    (tmp_path / "src" / "pkg" / "worker.py").write_text("def work() -> int:\n    return 1\n", encoding="utf-8")
    (tmp_path / "src" / "pkg" / "core.py").write_text("from pkg.worker import work\n", encoding="utf-8")
    (tmp_path / "pyproject.toml").write_text("[project]\nname='src-project'\nversion='0.0.0'\n", encoding="utf-8")
    _init_git_repo(tmp_path)

    graph = build_project_graph(tmp_path)

    assert any(node.kind == "python_module" and node.symbol == "pkg.core" for node in graph.nodes)
    assert any(node.kind == "python_module" and node.symbol == "pkg.worker" for node in graph.nodes)
    node_by_id = {node.id: node for node in graph.nodes}
    assert any(edge.kind == "imports" and node_by_id[edge.from_node_id].symbol == "pkg.core" and "pkg.worker" in edge.to_node_id for edge in graph.edges)


def test_graph_resolves_python_relative_imports_to_project_modules(tmp_path: Path) -> None:
    (tmp_path / "src" / "pkg").mkdir(parents=True)
    (tmp_path / "src" / "pkg" / "__init__.py").write_text("", encoding="utf-8")
    (tmp_path / "src" / "pkg" / "worker.py").write_text("def work() -> int:\n    return 1\n", encoding="utf-8")
    (tmp_path / "src" / "pkg" / "api.py").write_text("from .worker import work\n", encoding="utf-8")
    (tmp_path / "pyproject.toml").write_text("[project]\nname='relative-import-project'\nversion='0.0.0'\n", encoding="utf-8")
    _init_git_repo(tmp_path)

    graph = build_project_graph(tmp_path)
    node_by_id = {node.id: node for node in graph.nodes}

    assert any(
        edge.kind == "imports" and node_by_id[edge.from_node_id].symbol == "pkg.api" and edge.to_node_id == "node:python_import:pkg.worker"
        for edge in graph.edges
    )


def test_graph_resolves_python_package_import_aliases_to_owned_modules(tmp_path: Path) -> None:
    (tmp_path / "src" / "pkg").mkdir(parents=True)
    (tmp_path / "src" / "pkg" / "__init__.py").write_text("", encoding="utf-8")
    (tmp_path / "src" / "pkg" / "resources.py").write_text("def get_client() -> object:\n    return object()\n", encoding="utf-8")
    (tmp_path / "src" / "pkg" / "tools.py").write_text("def search() -> str:\n    return 'ok'\n", encoding="utf-8")
    (tmp_path / "src" / "pkg" / "server.py").write_text(
        "from pkg import resources, tools\n\ndef run() -> tuple[object, str]:\n    return resources.get_client(), tools.search()\n",
        encoding="utf-8",
    )
    (tmp_path / "pyproject.toml").write_text("[project]\nname='package-import-project'\nversion='0.0.0'\n", encoding="utf-8")
    _init_git_repo(tmp_path)

    graph = build_project_graph(tmp_path)
    node_by_id = {node.id: node for node in graph.nodes}
    import_targets = {
        edge.to_node_id
        for edge in graph.edges
        if edge.kind == "imports" and node_by_id[edge.from_node_id].symbol == "pkg.server"
    }

    assert "node:python_import:pkg.resources" in import_targets
    assert "node:python_import:pkg.tools" in import_targets
    assert "node:python_import:pkg" not in import_targets


def test_graph_resolves_from_package_import_submodule_without_package_self_edge(tmp_path: Path) -> None:
    (tmp_path / "pkgA").mkdir(parents=True)
    (tmp_path / "pkgA" / "__init__.py").write_text("from pkgA.a import thing\n", encoding="utf-8")
    (tmp_path / "pkgA" / "a.py").write_text("from pkgA import b\n", encoding="utf-8")
    (tmp_path / "pkgA" / "b.py").write_text("thing = 1\n", encoding="utf-8")
    _init_git_repo(tmp_path)

    graph = build_project_graph(tmp_path)
    node_by_id = {node.id: node for node in graph.nodes}
    import_pairs = {
        (node_by_id[edge.from_node_id].symbol, node_by_id[edge.to_node_id].symbol)
        for edge in graph.edges
        if edge.kind == "imports"
    }
    cycles = import_cycles(fresh_graph_slice(tmp_path))

    assert ("pkgA", "pkgA.a") in import_pairs
    assert ("pkgA.a", "pkgA.b") in import_pairs
    assert ("pkgA.a", "pkgA") not in import_pairs
    assert cycles == ()


def test_graph_excludes_type_checking_imports_from_runtime_import_edges(tmp_path: Path) -> None:
    (tmp_path / "pkgB").mkdir(parents=True)
    (tmp_path / "pkgB" / "__init__.py").write_text("", encoding="utf-8")
    (tmp_path / "pkgB" / "c.py").write_text(
        "from typing import TYPE_CHECKING\n"
        "\n"
        "if TYPE_CHECKING:\n"
        "    from pkgB.d import Thing\n",
        encoding="utf-8",
    )
    (tmp_path / "pkgB" / "d.py").write_text("class Thing:\n    pass\n", encoding="utf-8")
    _init_git_repo(tmp_path)

    graph = build_project_graph(tmp_path)
    node_by_id = {node.id: node for node in graph.nodes}
    import_pairs = {
        (node_by_id[edge.from_node_id].symbol, node_by_id[edge.to_node_id].symbol)
        for edge in graph.edges
        if edge.kind == "imports"
    }
    cycles = import_cycles(fresh_graph_slice(tmp_path))

    assert ("pkgB.c", "pkgB.d") not in import_pairs
    assert cycles == ()


def test_graph_keeps_runtime_imports_under_not_type_checking_guard(tmp_path: Path) -> None:
    (tmp_path / "pkgC").mkdir(parents=True)
    (tmp_path / "pkgC" / "__init__.py").write_text("", encoding="utf-8")
    (tmp_path / "pkgC" / "runtime.py").write_text("value = 1\n", encoding="utf-8")
    (tmp_path / "pkgC" / "types.py").write_text("class Thing:\n    pass\n", encoding="utf-8")
    (tmp_path / "pkgC" / "c.py").write_text(
        "from typing import TYPE_CHECKING\n"
        "\n"
        "if not TYPE_CHECKING:\n"
        "    import pkgC.runtime\n"
        "else:\n"
        "    from pkgC.types import Thing\n",
        encoding="utf-8",
    )
    _init_git_repo(tmp_path)

    graph = build_project_graph(tmp_path)
    node_by_id = {node.id: node for node in graph.nodes}
    import_pairs = {
        (node_by_id[edge.from_node_id].symbol, node_by_id[edge.to_node_id].symbol)
        for edge in graph.edges
        if edge.kind == "imports"
    }

    assert ("pkgC.c", "pkgC.runtime") in import_pairs
    assert ("pkgC.c", "pkgC.types") not in import_pairs


def test_graph_records_symlink_identity_without_following_targets(tmp_path: Path) -> None:
    outside = tmp_path.parent / f"outside-{tmp_path.name}.py"
    outside.write_text("def leaked() -> int:\n    return 1\n", encoding="utf-8")
    try:
        (tmp_path / "link.py").symlink_to(outside)
        (tmp_path / "pyproject.toml").write_text("[project]\nname='symlink-project'\nversion='0.0.0'\n", encoding="utf-8")
        _init_git_repo(tmp_path)

        graph = build_project_graph(tmp_path)
    finally:
        outside.unlink(missing_ok=True)

    symlink_nodes = [node for node in graph.nodes if node.path == "link.py" and node.kind == "file"]
    assert symlink_nodes
    assert "symlink" in symlink_nodes[0].tags
    assert symlink_nodes[0].provenance_refs[0].content_hash
    assert not any(node.kind == "python_module" and node.symbol == "link" for node in graph.nodes)


def test_graph_discovers_javascript_modules_functions_and_relative_imports(tmp_path: Path) -> None:
    (tmp_path / "worker" / "mcp").mkdir(parents=True)
    (tmp_path / "worker" / "index.js").write_text(
        "import { handleMcpRequest } from './mcp/server.js';\n\nfunction route(path) { return handleMcpRequest(path); }\n",
        encoding="utf-8",
    )
    (tmp_path / "worker" / "mcp" / "server.js").write_text(
        "export async function handleMcpRequest(request) { return request; }\n",
        encoding="utf-8",
    )
    (tmp_path / "package.json").write_text('{"name":"js-project","type":"module"}\n', encoding="utf-8")
    _init_git_repo(tmp_path)

    graph = build_project_graph(tmp_path)
    node_by_id = {node.id: node for node in graph.nodes}

    assert any(node.kind == "javascript_module" and node.symbol == "worker" for node in graph.nodes)
    assert any(node.kind == "javascript_module" and node.symbol == "worker.mcp.server" for node in graph.nodes)
    assert any(node.kind == "javascript_function" and node.symbol == "worker.mcp.server.handleMcpRequest" for node in graph.nodes)
    assert any(edge.kind == "imports" and node_by_id[edge.from_node_id].symbol == "worker" and "worker.mcp.server" in edge.to_node_id for edge in graph.edges)


def test_graph_records_javascript_treesitter_classes_methods_arrows_inherits_and_calls(tmp_path: Path) -> None:
    (tmp_path / "src" / "app").mkdir(parents=True)
    (tmp_path / "src" / "app" / "base.js").write_text(
        "export class Base {}\n"
        "export function helper(value) { return value; }\n",
        encoding="utf-8",
    )
    (tmp_path / "src" / "app" / "main.js").write_text(
        "import { Base, helper } from './base.js';\n"
        "export class Child extends Base {\n"
        "  method(value) { return helper(value); }\n"
        "}\n"
        "export const arrow = (value) => helper(value);\n"
        "export function top() { return arrow(1); }\n",
        encoding="utf-8",
    )
    (tmp_path / "package.json").write_text('{"name":"js-ts-project","type":"module"}\n', encoding="utf-8")
    _init_git_repo(tmp_path)

    first = build_project_graph(tmp_path)
    second = build_project_graph(tmp_path)
    node_by_symbol = {node.symbol: node for node in first.nodes if node.symbol}
    child = node_by_symbol["app.main.Child"]
    base = node_by_symbol["app.base.Base"]
    method = node_by_symbol["app.main.Child.method"]
    helper = node_by_symbol["app.base.helper"]
    arrow = node_by_symbol["app.main.arrow"]
    top = node_by_symbol["app.main.top"]
    inherits_edges = [edge for edge in first.edges if edge.kind == "inherits" and edge.from_node_id == child.id]
    method_calls = [edge for edge in first.edges if edge.kind == "calls" and edge.from_node_id == method.id]
    arrow_calls = [edge for edge in first.edges if edge.kind == "calls" and edge.from_node_id == arrow.id]
    top_calls = [edge for edge in first.edges if edge.kind == "calls" and edge.from_node_id == top.id]

    assert child.kind == "javascript_class"
    assert method.kind == "javascript_function"
    assert arrow.kind == "javascript_function"
    assert inherits_edges and inherits_edges[0].to_node_id == base.id
    assert method_calls and method_calls[0].to_node_id == helper.id
    assert arrow_calls and arrow_calls[0].to_node_id == helper.id
    assert top_calls and top_calls[0].to_node_id == arrow.id
    assert inherits_edges[0].confidence == "heuristic"
    assert method_calls[0].confidence == "heuristic"
    assert arrow_calls[0].confidence == "heuristic"
    assert top_calls[0].confidence == "deterministic"
    for edge in [*inherits_edges, *method_calls, *arrow_calls, *top_calls]:
        assert edge.derived_by == "javascript_treesitter"
        assert edge.provenance_refs[0].derived_by == "javascript_treesitter"
    assert canonical_graph_json(first) == canonical_graph_json(second)


def test_graph_records_typescript_treesitter_nodes_and_calls(tmp_path: Path) -> None:
    (tmp_path / "src" / "app").mkdir(parents=True)
    (tmp_path / "src" / "app" / "base.ts").write_text(
        "export class Base {}\n"
        "export function helper(value: string): string { return value; }\n",
        encoding="utf-8",
    )
    (tmp_path / "src" / "app" / "main.ts").write_text(
        "import { Base, helper } from './base';\n"
        "export class Child extends Base {\n"
        "  method(value: string): string { return helper(value); }\n"
        "}\n"
        "export const arrow = (value: string): string => helper(value);\n",
        encoding="utf-8",
    )
    (tmp_path / "package.json").write_text('{"name":"ts-project","type":"module"}\n', encoding="utf-8")
    _init_git_repo(tmp_path)

    graph = build_project_graph(tmp_path)
    node_by_symbol = {node.symbol: node for node in graph.nodes if node.symbol}
    child = node_by_symbol["app.main.Child"]
    base = node_by_symbol["app.base.Base"]
    method = node_by_symbol["app.main.Child.method"]
    helper = node_by_symbol["app.base.helper"]
    arrow = node_by_symbol["app.main.arrow"]

    assert any(edge.kind == "inherits" and edge.from_node_id == child.id and edge.to_node_id == base.id for edge in graph.edges)
    assert any(edge.kind == "calls" and edge.from_node_id == method.id and edge.to_node_id == helper.id for edge in graph.edges)
    assert any(edge.kind == "calls" and edge.from_node_id == arrow.id and edge.to_node_id == helper.id for edge in graph.edges)


def test_graph_tags_common_generated_output_as_generated_surface(tmp_path: Path) -> None:
    (tmp_path / "dist").mkdir()
    (tmp_path / "src").mkdir()
    (tmp_path / "dist" / "bundle.js").write_text("function bundled() { return 1; }\n", encoding="utf-8")
    (tmp_path / "src" / "main.js").write_text("function source() { return 1; }\n", encoding="utf-8")
    (tmp_path / "package.json").write_text('{"name":"generated-project"}\n', encoding="utf-8")
    _init_git_repo(tmp_path)

    graph = build_project_graph(tmp_path)

    dist_nodes = [node for node in graph.nodes if node.path == "dist/bundle.js"]
    assert dist_nodes
    assert all("generated" in node.tags for node in dist_nodes)
    assert not any(node.kind == "javascript_module" and node.symbol == "dist.bundle" for node in graph.nodes)
    assert any(node.kind == "javascript_module" and node.symbol == "main" for node in graph.nodes)


def test_graph_marks_ignored_generated_directory_with_sentinel(tmp_path: Path) -> None:
    (tmp_path / ".gitignore").write_text("dist/\n", encoding="utf-8")
    (tmp_path / "dist").mkdir()
    (tmp_path / "dist" / "index.html").write_text("<p>generated</p>\n", encoding="utf-8")
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "app.py").write_text("def source() -> int:\n    return 1\n", encoding="utf-8")
    (tmp_path / "pyproject.toml").write_text("[project]\nname='ignored-dist-project'\nversion='0.0.0'\n", encoding="utf-8")
    _init_git_repo(tmp_path)

    graph = build_project_graph(tmp_path)

    generated = [node for node in graph.nodes if node.kind == "generated_surface" and node.path == "dist/"]
    assert generated
    assert "generated" in generated[0].tags
    assert not any(node.path == "dist/index.html" for node in graph.nodes)
    assert any(edge.kind == "generated_from" and edge.from_node_id == generated[0].id for edge in graph.edges)
