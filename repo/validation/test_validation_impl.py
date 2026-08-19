#!/usr/bin/env python3

from __future__ import annotations

import sys
from pathlib import Path

from validation.errors import ValidationFailure
from validation.portable_self_tests import run_repository_portable_self_tests


def _run_source_development_tests(repo_root: Path) -> None:
    source_suite = repo_root / "repo/scripts/validation/tests/mutation_tests.py"
    if not source_suite.is_file():
        return

    from validation.tests.mutation_tests import run_repository_mutation_tests

    run_repository_mutation_tests(repo_root)


def main(argv: list[str]) -> int:
    repo_root = Path(argv[1]).resolve() if len(argv) > 1 else Path.cwd().resolve()
    if len(argv) > 2:
        print(f"validation test error: unknown mode: {argv[2]}", file=sys.stderr)
        return 1
    try:
        run_repository_portable_self_tests(repo_root)
        _run_source_development_tests(repo_root)
        return 0
    except ValidationFailure as exc:
        print(f"validation test error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
