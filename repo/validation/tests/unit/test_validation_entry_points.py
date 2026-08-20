from __future__ import annotations

import subprocess
from pathlib import Path

from validation.core.errors import expect


def run_validation_entry_point_tests(repo_root: Path) -> None:
    validate_path = repo_root / "repo/scripts/validate"
    self_test_path = repo_root / "repo/scripts/test-validation"
    unit_test_path = repo_root / "repo/scripts/test-unittest"

    expect(validate_path.is_file(), "repository validation entry point is missing")
    expect(self_test_path.is_file(), "repository validation self-test entry point is missing")
    expect(unit_test_path.is_file(), "repository unittest entry point is missing")

    validate_launcher = validate_path.read_text()
    self_test_launcher = self_test_path.read_text()
    unit_test_launcher = unit_test_path.read_text()

    expect(
        '"$root/repo/validation/runners/validate_impl.py"' in validate_launcher,
        "repository validation entry point omits relocated validation runner",
    )
    expect(
        '"$root/repo/validation/runners/test_validation_impl.py"' in self_test_launcher,
        "repository validation self-test entry point omits relocated self-test runner",
    )

    expect(
        'python3 -P -m unittest discover -s "$root/repo/validation/tests/unit" -t "$root/repo"' in unit_test_launcher,
        "repository unittest entry point omits repo-only unittest discovery",
    )
    expect(
        'python3 -P -m unittest "$@"' in unit_test_launcher,
        "repository unittest entry point omits focused unittest execution",
    )
    proc = subprocess.run(
        [str(validate_path)],
        cwd=repo_root,
        capture_output=True,
        text=True,
    )
    expect(proc.returncode == 0, "repository production validation entry point failed")

    print("ok: repository validation entry points")
