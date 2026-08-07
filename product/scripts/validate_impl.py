#!/usr/bin/env python3

"""Product-owned validation entry point."""

from __future__ import annotations

import sys
from pathlib import Path

from validation.errors import ValidationFailure
from product_validation.product_checks import validate_product


def main(argv: list[str]) -> int:
    repo_root = Path(argv[1]).resolve() if len(argv) > 1 else Path.cwd().resolve()
    if len(argv) > 2:
        print(f"validation error: unknown mode: {argv[2]}", file=sys.stderr)
        return 1
    try:
        validate_product(repo_root)
        return 0
    except ValidationFailure as exc:
        print(f"validation error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
