"""Shared validation context and repository loading mechanics."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from repo_model import RepositoryError, load_specs as load_repo_specs_impl

from .errors import fail


@dataclass(frozen=True)
class RepositoryValidationContext:
    manifest: dict[str, Any]
    specs: dict[str, dict[str, Any]]
    source_paths: dict[str, str]
    actual_paths: list[str]
    schemas: dict[str, dict[str, Any]]


@dataclass(frozen=True)
class ExternalRepositoryValidationContext:
    """Repository authority read by another validation domain without certifying it."""

    specs: dict[str, dict[str, Any]]
    schemas: dict[str, dict[str, Any]]


@dataclass(frozen=True)
class ValidationContext:
    repo_root: Path
    repository: RepositoryValidationContext | None
    product: Any | None
    external_repository: ExternalRepositoryValidationContext | None = None


def load_repo_specs(repo_root: Path) -> tuple[dict[str, Any], dict[str, dict[str, Any]], dict[str, str], list[str]]:
    try:
        return load_repo_specs_impl(repo_root)
    except RepositoryError as exc:
        fail(str(exc))
