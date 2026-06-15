from __future__ import annotations

from pathlib import Path

from arena.repo_facts import collect_repo_facts


def test_collect_repo_facts_reports_docs_and_top_level_files_deterministically(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "docs" / "nested").mkdir(parents=True)
    (repo / "README.md").write_text("# Readme\n", encoding="utf-8")
    (repo / "pyproject.toml").write_text("[project]\nname='x'\n", encoding="utf-8")
    (repo / "docs" / "guide.md").write_text("# Guide\n", encoding="utf-8")
    (repo / "docs" / "nested" / "deep.md").write_text("# Deep\n", encoding="utf-8")
    (repo / "src" / "pkg").mkdir(parents=True)
    (repo / "src" / "pkg" / "auth.py").write_text("def login():\n    return True\n", encoding="utf-8")
    (repo / "app").mkdir()

    first = collect_repo_facts(repo)
    second = collect_repo_facts(repo)

    assert first.to_jsonable() == second.to_jsonable()
    assert first.readme_exists is True
    assert first.docs_dir_exists is True
    assert first.top_level_dirs == ("app", "docs", "src")
    assert first.docs_markdown_files == ("docs/guide.md", "docs/nested/deep.md")
    assert first.markdown_files == ("README.md", "docs/guide.md", "docs/nested/deep.md")
    assert first.source_files == ("pyproject.toml", "src/pkg/auth.py")
    assert first.docs_markdown_files_truncated is False
    assert first.markdown_files_truncated is False
    assert "README.md" in first.top_level_files
    assert first.content_hash == second.content_hash
    assert "Existing docs markdown files:" in first.to_prompt_block()
    assert "Top-level directories: app, docs, src" in first.to_prompt_block()
    assert "Markdown files:" in first.to_prompt_block()
    assert "Source files: pyproject.toml, src/pkg/auth.py" in first.to_prompt_block()
    assert "Markdown files truncated:" in first.to_prompt_block()
    assert "docs/guide.md" in first.to_prompt_block()


def test_collect_repo_facts_ignores_hidden_cache_markdown(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "docs").mkdir(parents=True)
    (repo / ".pytest_cache").mkdir(parents=True)
    (repo / ".ruff_cache" / "nested").mkdir(parents=True)
    (repo / "README.md").write_text("# Readme\n", encoding="utf-8")
    (repo / "docs" / "index.md").write_text("# Docs\n", encoding="utf-8")
    (repo / ".pytest_cache" / "README.md").write_text("# Cache\n", encoding="utf-8")
    (repo / ".ruff_cache" / "nested" / "cache.md").write_text("# Cache\n", encoding="utf-8")

    facts = collect_repo_facts(repo)

    assert facts.markdown_files == ("README.md", "docs/index.md")
    assert facts.source_files == ()
    assert ".pytest_cache/README.md" not in facts.to_prompt_block()
    assert ".ruff_cache/nested/cache.md" not in facts.to_prompt_block()


def test_collect_repo_facts_handles_repo_without_docs(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "README.md").write_text("# Readme\n", encoding="utf-8")

    facts = collect_repo_facts(repo)

    assert facts.readme_exists is True
    assert facts.docs_dir_exists is False
    assert facts.docs_markdown_files == ()
    assert "Docs directory exists: no" in facts.to_prompt_block()


def test_collect_repo_facts_surfaces_markdown_truncation(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "docs").mkdir(parents=True)
    (repo / "README.md").write_text("# Readme\n", encoding="utf-8")
    for index in range(5):
        (repo / "docs" / f"doc-{index}.md").write_text(f"# Doc {index}\n", encoding="utf-8")

    facts = collect_repo_facts(repo, max_docs_files=3)

    assert facts.docs_markdown_files_truncated is True
    assert facts.markdown_files_truncated is True
    assert "Markdown files truncated: yes" in facts.to_prompt_block()
