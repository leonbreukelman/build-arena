from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class RepoFacts:
    project_root: str
    readme_exists: bool
    docs_dir_exists: bool
    top_level_files: tuple[str, ...]
    top_level_dirs: tuple[str, ...]
    docs_markdown_files: tuple[str, ...]
    markdown_files: tuple[str, ...]
    docs_markdown_files_truncated: bool
    markdown_files_truncated: bool
    content_hash: str

    def to_jsonable(self) -> dict[str, Any]:
        return asdict(self)

    def to_prompt_block(self) -> str:
        lines = [
            "Repository facts:",
            f"- README.md exists: {'yes' if self.readme_exists else 'no'}",
            f"- Docs directory exists: {'yes' if self.docs_dir_exists else 'no'}",
            "- Top-level files: " + (", ".join(self.top_level_files) if self.top_level_files else "none"),
            "- Top-level directories: " + (", ".join(self.top_level_dirs) if self.top_level_dirs else "none"),
            "- Existing docs markdown files: " + (", ".join(self.docs_markdown_files) if self.docs_markdown_files else "none"),
            "- Markdown files: " + (", ".join(self.markdown_files) if self.markdown_files else "none"),
            f"- Markdown files truncated: {'yes' if self.markdown_files_truncated else 'no'}",
        ]
        return "\n".join(lines)


def collect_repo_facts(repo: Path, *, max_docs_files: int = 40, max_top_level_files: int = 40) -> RepoFacts:
    root = repo.resolve()
    top_level_files = tuple(
        sorted(
            path.name
            for path in root.iterdir()
            if path.is_file() and not path.name.startswith(".")
        )[:max_top_level_files]
    )
    top_level_dirs = tuple(
        sorted(
            path.name
            for path in root.iterdir()
            if path.is_dir() and not path.name.startswith(".") and path.name not in {".venv", "__pycache__", "node_modules"}
        )[:max_top_level_files]
    )
    docs_root = root / "docs"
    docs_files_all: tuple[str, ...] = ()
    if docs_root.exists() and docs_root.is_dir():
        docs_files_all = tuple(
            sorted(
                path.relative_to(root).as_posix()
                for path in docs_root.rglob("*.md")
                if path.is_file()
            )
        )
    docs_files = docs_files_all[:max_docs_files]
    markdown_files_all = tuple(
        sorted(
            path.relative_to(root).as_posix()
            for path in root.rglob("*.md")
            if path.is_file() and not any(part in {".git", ".venv", "node_modules", "__pycache__"} for part in path.parts)
        )
    )
    markdown_files = markdown_files_all[:max_docs_files]
    base = {
        "project_root": str(root),
        "readme_exists": (root / "README.md").is_file(),
        "docs_dir_exists": docs_root.is_dir(),
        "top_level_files": top_level_files,
        "top_level_dirs": top_level_dirs,
        "docs_markdown_files": docs_files,
        "markdown_files": markdown_files,
        "docs_markdown_files_truncated": len(docs_files_all) > len(docs_files),
        "markdown_files_truncated": len(markdown_files_all) > len(markdown_files),
    }
    content_hash = hashlib.sha256(json.dumps(base, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return RepoFacts(content_hash=content_hash, **base)
