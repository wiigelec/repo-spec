"""Generated-artifact validation extension point."""

from __future__ import annotations

from pathlib import Path

from docgen import check_generated_outputs, render_all, write_all
from repo_model import RepositoryError

from ..core.errors import fail


def check_generated_document_freshness(repo_root: Path) -> None:
    try:
        check_generated_outputs(repo_root)
    except (RepositoryError, ValueError) as exc:
        fail(f"generated-document freshness failed: {exc}")


def check_generated_document_write_behavior(repo_root: Path) -> None:
    try:
        render_all(repo_root)
        write_all(repo_root)
        check_generated_outputs(repo_root)
    except (RepositoryError, ValueError) as exc:
        fail(f"generated-document write failed: {exc}")
