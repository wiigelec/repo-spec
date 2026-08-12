from __future__ import annotations

from pathlib import Path

from docgen import write_all


def check_generated_document_write_behavior(repo_root: Path) -> None:
    write_all(repo_root)
