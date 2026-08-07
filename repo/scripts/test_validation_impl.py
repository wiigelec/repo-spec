#!/usr/bin/env python3

from __future__ import annotations

import sys
from pathlib import Path

from validation.errors import ValidationFailure
from validation.tests.mutation_tests import run_repository_mutation_tests


def main(argv: list[str]) -> int:
    repo_root = Path(argv[1]).resolve() if len(argv) > 1 else Path.cwd().resolve()
    if len(argv) > 2:
        print(f"validation test error: unknown mode: {argv[2]}", file=sys.stderr)
        return 1
    try:
        run_repository_mutation_tests(repo_root)
        return 0
    except ValidationFailure as exc:
        print(f"validation test error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
