from __future__ import annotations

import subprocess
from pathlib import Path

from validation.core.errors import expect


def check_product_validate_cli_contract(repo_root: Path) -> None:
    validate_launcher = (repo_root / "product/scripts/validate").read_text()
    test_launcher = (repo_root / "product/scripts/test-validation").read_text()
    expected_pythonpath = (
        'PYTHONPATH="$root/product:$root/product/scripts${PYTHONPATH:+:$PYTHONPATH}"'
    )
    expect(
        expected_pythonpath in validate_launcher,
        "product validate launcher product-owned runtime boundary mismatch",
    )
    expect(
        expected_pythonpath in test_launcher,
        "product validation-test launcher product-owned runtime boundary mismatch",
    )
    expect(
        "$root/repo/scripts" not in validate_launcher,
        "product validate launcher depends on repo scripts",
    )
    expect(
        "$root/repo/scripts" not in test_launcher,
        "product validation-test launcher depends on repo scripts",
    )
    validate_impl = (repo_root / "product/validation/runners/validate_impl.py").read_text()
    expect(
        "from validation.core.errors import ValidationFailure" in validate_impl,
        "product validate implementation missing stable ValidationFailure contract",
    )
    expect(
        "from validation.checks.domain import validate_product" in validate_impl,
        "product validate implementation missing stable domain entry point",
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
