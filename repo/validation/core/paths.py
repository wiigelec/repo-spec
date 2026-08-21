"""Repository-relative validation path helpers."""

# Repository-relative path mechanics shared across validation domains.

from __future__ import annotations

from pathlib import Path

from repo_model import RepositoryError, resolve_repo_path as resolve_repo_path_impl

from ..core.errors import fail


def resolve_repo_path(repo_root: Path, value: str) -> Path:
    try:
        return resolve_repo_path_impl(repo_root, value)
    except RepositoryError as exc:
        fail(str(exc))
resolve_repo_path.__validation_metadata__ = {"role": "helper"}
