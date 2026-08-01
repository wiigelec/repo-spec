from __future__ import annotations

import subprocess
from pathlib import Path

from .errors import expect


def check_generate_docs_cli_contract(repo_root: Path) -> None:
    proc = subprocess.run([str(repo_root / "scripts/generate-docs")], cwd=repo_root, capture_output=True, text=True)
    expect(proc.returncode == 0, "generate-docs launcher failed")
    expect(proc.stdout.strip() == "", "generate-docs launcher wrote stdout")
    expect(proc.stderr.strip() == "", "generate-docs launcher wrote stderr")

    proc = subprocess.run([str(repo_root / "scripts/generate-docs"), "--unknown-mode"], cwd=repo_root, capture_output=True, text=True)
    expect(proc.returncode != 0, "generate-docs unknown mode succeeded")


def check_validate_cli_contract(repo_root: Path) -> None:
    proc = subprocess.run([str(repo_root / "scripts/validate"), "--self-test-failure"], cwd=repo_root, capture_output=True, text=True)
    expect(proc.returncode != 0, "validate launcher failure mode succeeded")
    expect(proc.stdout.strip() == "", "validate launcher wrote stdout")
    expect(proc.stderr.strip() == "forced failure for behavior test", "validate launcher stderr mismatch")
