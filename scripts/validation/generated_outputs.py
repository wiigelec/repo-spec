from __future__ import annotations

import subprocess
from pathlib import Path

from docgen import check_generated_outputs

from .errors import expect, fail


def check_generated_document_freshness(repo_root: Path) -> None:
    try:
        check_generated_outputs(repo_root)
    except ValueError as exc:
        fail(f"generated-document freshness failed: {exc}")


def check_generated_document_write_behavior(repo_root: Path) -> None:
    proc = subprocess.run([str(repo_root / "scripts/generate-docs")], cwd=repo_root, capture_output=True, text=True)
    expect(proc.returncode == 0, f"generated-document write failed: {proc.stderr.strip() or proc.stdout.strip() or 'write failed'}")
