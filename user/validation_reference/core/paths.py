"""Repository-relative validation path helpers."""

from __future__ import annotations

from pathlib import Path


def resolve_repo_path(repo_root: Path, relative_path: str) -> Path:
    """Resolve a repository-relative path without defining domain policy."""
    return repo_root / relative_path
