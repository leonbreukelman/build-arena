from __future__ import annotations

from pathlib import Path

from arena.markdown_links import (
    check_markdown_links,
    extract_markdown_links,
    has_source_references,
    main,
)


def test_extract_markdown_links_ignores_external_and_anchor_targets() -> None:
    text = """
[Readme](../README.md)
[External](https://example.com)
[Mail](mailto:test@example.com)
[Phone](tel:+155****4567)
[Anchor](#local-section)
![Logo](assets/logo.png)
"""

    links = extract_markdown_links(text)

    assert [link.target for link in links] == ["../README.md", "assets/logo.png"]


def test_extract_markdown_links_includes_reference_style_targets() -> None:
    text = """
See [Overview][overview-ref] and [Guide][].

[overview-ref]: overview.md
[Guide]: <docs/guide with space.md>
"""

    links = extract_markdown_links(text)

    assert [link.target for link in links] == ["overview.md", "docs/guide with space.md"]


def test_check_markdown_links_reports_checked_and_missing_targets(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    docs = repo / "docs"
    docs.mkdir(parents=True)
    (repo / "README.md").write_text("# Readme\n", encoding="utf-8")
    index = docs / "index.md"
    index.write_text(
        "[Readme](../README.md)\n[Missing](overview.md)\n[External](https://example.com)\n",
        encoding="utf-8",
    )

    report = check_markdown_links(repo, index)

    assert report.ok is False
    assert [item.link for item in report.checked] == ["../README.md"]
    assert [item.link for item in report.missing] == ["overview.md"]
    assert report.to_jsonable()["missing"][0]["resolved_path"] == "docs/overview.md"


def test_check_markdown_links_checks_plain_file_mentions_so_gate_is_not_vacuous(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    docs = repo / "docs"
    docs.mkdir(parents=True)
    (repo / "README.md").write_text("# Readme\n", encoding="utf-8")
    (docs / "index.md").write_text("# Docs\n", encoding="utf-8")
    agents = repo / "AGENTS.md"
    agents.write_text("See README.md, docs/index.md, and missing.md for context.\n", encoding="utf-8")

    report = check_markdown_links(repo, agents)

    assert report.ok is False
    assert [item.link for item in report.checked] == ["README.md", "docs/index.md"]
    assert [item.link for item in report.missing] == ["missing.md"]


def test_check_markdown_links_rejects_links_that_escape_repo(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    docs = repo / "docs"
    docs.mkdir(parents=True)
    outside = tmp_path / "outside.md"
    outside.write_text("outside\n", encoding="utf-8")
    index = docs / "index.md"
    index.write_text("[Escape](../../outside.md)\n", encoding="utf-8")

    report = check_markdown_links(repo, index)

    assert report.ok is False
    assert report.escaped[0].link == "../../outside.md"


def test_has_source_references_requires_source_heading_and_resolving_reference(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "README.md").write_text("# Readme\n", encoding="utf-8")
    proposal = repo / "proposal.md"
    proposal.write_text("# Proposal\n\nMentions README.md.\n\n## Source references\n\n- README.md\n", encoding="utf-8")

    assert has_source_references(repo, proposal) is True

    proposal.write_text("# Proposal\n\nMentions README.md without source section.\n", encoding="utf-8")
    assert has_source_references(repo, proposal) is False

    proposal.write_text("# Proposal\n\n## Source references\n\n- missing.md\n", encoding="utf-8")
    assert has_source_references(repo, proposal) is False


def test_source_references_reject_missing_local_file_citations(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    proposal = repo / "proposal.md"
    proposal.write_text("# Proposal\n\n## Source references\n\n- missing.md\n", encoding="utf-8")

    assert check_markdown_links(repo, proposal).ok is False
    assert main(["--repo", str(repo), "--path", "proposal.md", "--require-source-references"]) == 1
