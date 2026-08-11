from __future__ import annotations

import subprocess
from pathlib import Path

from validation.errors import expect


def run_validation_entry_point_tests(repo_root: Path) -> None:
    aggregate = (repo_root / "scripts/validate").read_text()
    self_test = (repo_root / "scripts/test-validation").read_text()
    product_orchestrator = (
        repo_root / "product/scripts/validation_tests/mutation_tests.py"
    ).read_text()

    expect(
        '"$root/repo/scripts/validate"' in aggregate,
        "aggregate production validation omits repository validator",
    )
    expect(
        '"$root/product/scripts/validate"' in aggregate,
        "aggregate production validation omits product validator",
    )
    expect(
        "test-validation" not in aggregate,
        "aggregate production validation still invokes validation self-tests",
    )

    expect(
        '"$root/repo/scripts/test-validation"' in self_test,
        "aggregate validation self-test omits repository self-tests",
    )
    expect(
        '"$root/product/scripts/test-validation"' in self_test,
        "aggregate validation self-test omits product self-tests",
    )
    expect(
        "initializer.tests.run_tests" not in product_orchestrator,
        "product validation self-tests still import initializer tests",
    )
    expect(
        "run_initializer_tests" not in product_orchestrator,
        "product validation self-tests still execute initializer tests",
    )

    proc = subprocess.run(
        [str(repo_root / "scripts/validate")],
        cwd=repo_root,
        capture_output=True,
        text=True,
    )
    expect(proc.returncode == 0, "aggregate production validation failed")
