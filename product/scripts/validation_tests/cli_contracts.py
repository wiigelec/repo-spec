from __future__ import annotations

import subprocess
from pathlib import Path

from validation.errors import expect


def check_product_validate_cli_contract(repo_root: Path) -> None:
    validate_launcher = (repo_root / "product/scripts/validate").read_text()
    test_launcher = (repo_root / "product/scripts/test-validation").read_text()
    expected_pythonpath = (
        'PYTHONPATH="$root/repo/scripts:$root/product/scripts'
        '${PYTHONPATH:+:$PYTHONPATH}"'
    )
    expect(
        expected_pythonpath in validate_launcher,
        "product validate launcher shared-support boundary mismatch",
    )
    expect(
        expected_pythonpath in test_launcher,
        "product validation-test launcher shared-support boundary mismatch",
    )

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
