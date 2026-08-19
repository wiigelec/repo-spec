from __future__ import annotations

import subprocess
from pathlib import Path

from ..core.errors import expect


def check_generate_docs_cli_contract(repo_root: Path) -> None:
    proc = subprocess.run([str(repo_root / "repo/scripts/generate-docs")], cwd=repo_root, capture_output=True, text=True)
    expect(proc.returncode == 0, "generate-docs launcher failed")
    expect(proc.stdout.strip() == "", "generate-docs launcher wrote stdout")
    expect(proc.stderr.strip() == "", "generate-docs launcher wrote stderr")

    proc = subprocess.run([str(repo_root / "repo/scripts/generate-docs"), "--unknown-mode"], cwd=repo_root, capture_output=True, text=True)
    expect(proc.returncode != 0, "generate-docs unknown mode succeeded")


def check_validate_cli_contract(repo_root: Path) -> None:
    validate_launcher = (repo_root / "repo/scripts/validate").read_text()
    test_launcher = (repo_root / "repo/scripts/test-validation").read_text()
    expect("$root/product/scripts" not in validate_launcher, "repository validate launcher depends on product scripts")
    expect("$root/product/scripts" not in test_launcher, "repository validation-test launcher depends on product scripts")
    expect('PYTHONPATH="$root/repo:$root/repo/scripts${PYTHONPATH:+:$PYTHONPATH}"' in validate_launcher, "repository validate launcher runtime boundary mismatch")
    expect('PYTHONPATH="$root/repo:$root/repo/scripts${PYTHONPATH:+:$PYTHONPATH}"' in test_launcher, "repository validation-test launcher runtime boundary mismatch")

    expect(
        "repo_tree_sha" not in validate_launcher,
        "repository validate launcher still carries mutable repo-tree SHA state",
    )

    proc = subprocess.run(
        [str(repo_root / "repo/scripts/validate"), "--unknown-mode"],
        cwd=repo_root,
        capture_output=True,
        text=True,
    )
    expect(proc.returncode != 0, "repository validate unknown argument succeeded")
    expect(proc.stdout.strip() == "", "repository validate unknown argument wrote stdout")
    expect(
        proc.stderr.strip() == "validation error: unknown argument: --unknown-mode",
        "repository validate unknown-argument stderr mismatch",
    )
