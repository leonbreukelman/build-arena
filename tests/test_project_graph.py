from __future__ import annotations

import subprocess
from pathlib import Path

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
