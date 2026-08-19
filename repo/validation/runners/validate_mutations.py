#!/usr/bin/env python3

from __future__ import annotations

import sys
from pathlib import Path

from validation.core.errors import ValidationFailure
from validation.tests.self.mutation_tests import run_complete_validation_tests


def main(argv: list[str]) -> int:
    repo_root = Path(argv[1]).resolve() if len(argv) > 1 else Path.cwd().resolve()
    try:
        run_complete_validation_tests(repo_root)
        return 0
    except ValidationFailure as exc:
        print(f"validation error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
