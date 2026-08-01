#!/usr/bin/env python3

from __future__ import annotations

import sys
from pathlib import Path

from validation.errors import ValidationFailure
from validation.cli_contracts import check_generate_docs_cli_contract, check_validate_cli_contract
from validation.tests.mutation_tests import run_mutation_tests


def main(argv: list[str]) -> int:
    repo_root = Path(argv[1]).resolve() if len(argv) > 1 else Path.cwd().resolve()
    try:
        check_validate_cli_contract(repo_root)
        check_generate_docs_cli_contract(repo_root)
        run_mutation_tests(repo_root)
        return 0
    except ValidationFailure as exc:
        print(f"validation error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
