#!/usr/bin/env python3
"""Initialized-repository product validation.

A freshly initialized repository may have no active product specification system.
When a product system is active, run the generic product-specification validation
phases only. Repo-spec source-product development documents, lifecycle evidence,
generated source docs, and B0 evidence are not part of initialized bootstrap
validation.
"""

from __future__ import annotations

import sys
from pathlib import Path

from validation.errors import ValidationFailure
from product_validation.product_checks import (
    PRODUCT_LEAF_VALIDATION_PHASES,
    _load_product_only_context,
)


def validate_initialized_product(repo_root: Path) -> None:
    context = _load_product_only_context(repo_root)

    if context.product is None:
        print("ok: product specification system inactive")
        return

    for label, check in PRODUCT_LEAF_VALIDATION_PHASES:
        check(context)
        print(f"ok: {label}")


def main(argv: list[str]) -> int:
    repo_root = Path(argv[1]).resolve() if len(argv) > 1 else Path.cwd().resolve()
    if len(argv) > 2:
        print(f"validation error: unknown mode: {argv[2]}", file=sys.stderr)
        return 1

    try:
        validate_initialized_product(repo_root)
        return 0
    except ValidationFailure as exc:
        print(f"validation error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
