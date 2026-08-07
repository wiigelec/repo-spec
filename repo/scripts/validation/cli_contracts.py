from __future__ import annotations

import subprocess
from pathlib import Path

from .errors import expect


def check_generate_docs_cli_contract(repo_root: Path) -> None:
    proc = subprocess.run([str(repo_root / "repo/scripts/generate-docs")], cwd=repo_root, capture_output=True, text=True)
    expect(proc.returncode == 0, "generate-docs launcher failed")
    expect(proc.stdout.strip() == "", "generate-docs launcher wrote stdout")
    expect(proc.stderr.strip() == "", "generate-docs launcher wrote stderr")

    proc = subprocess.run([str(repo_root / "repo/scripts/generate-docs"), "--unknown-mode"], cwd=repo_root, capture_output=True, text=True)
    expect(proc.returncode != 0, "generate-docs unknown mode succeeded")


def check_validate_cli_contract(repo_root: Path) -> None:
    proc = subprocess.run(
        [str(repo_root / "repo/scripts/validate"), "--unknown-mode"],
        cwd=repo_root,
        capture_output=True,
        text=True,
    )
    expect(proc.returncode != 0, "repository validate unknown mode succeeded")
    expect(proc.stdout.strip() == "", "repository validate unknown mode wrote stdout")
    expect(
        proc.stderr.strip() == "validation error: unknown mode: --unknown-mode",
        "repository validate unknown-mode stderr mismatch",
    )


def check_product_validate_cli_contract(repo_root: Path) -> None:
    proc = subprocess.run(
        [str(repo_root / "product/scripts/validate"), "--unknown-mode"],
        cwd=repo_root,
        capture_output=True,
        text=True,
    )
    expect(proc.returncode != 0, "product validate unknown mode succeeded")
    expect(proc.stdout.strip() == "", "product validate unknown mode wrote stdout")
    expect(
        proc.stderr.strip() == "validation error: unknown mode: --unknown-mode",
        "product validate unknown-mode stderr mismatch",
    )
