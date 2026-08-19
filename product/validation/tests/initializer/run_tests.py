from __future__ import annotations

import sys
import unittest
from pathlib import Path


def run_initializer_tests(repo_root: Path) -> None:
    tests_dir = repo_root / "product" / "scripts" / "initializer" / "tests"
    loader = unittest.TestLoader()
    suite = loader.discover(
        start_dir=str(tests_dir),
        pattern="test_*.py",
        top_level_dir=str(repo_root / "product" / "scripts"),
    )

    runner = unittest.TextTestRunner(stream=sys.stdout, verbosity=2)
    result = runner.run(suite)
    if not result.wasSuccessful():
        raise AssertionError("initializer tests failed")
    print("ok: initializer tests")


def main() -> int:
    repo_root = Path(__file__).resolve().parents[4]
    run_initializer_tests(repo_root)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
