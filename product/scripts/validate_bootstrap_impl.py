#!/usr/bin/env python3
# Product-owned validation for an initialized repository with no active product specification system.

from __future__ import annotations

import sys
from pathlib import Path


class BootstrapProductValidationError(RuntimeError):
    pass


def validate_inactive_product(repo_root: Path) -> None:
    product_root = repo_root / "product/specs/product"
    manifest = product_root / "manifest.json"

    if manifest.exists():
        raise BootstrapProductValidationError(
            "product specification system is active but full product validation implementation is unavailable"
        )

    undeclared_json = []
    if product_root.exists():
        undeclared_json = sorted(
            path.relative_to(repo_root).as_posix()
            for path in product_root.rglob("*.json")
            if path.is_file()
        )
    if undeclared_json:
        raise BootstrapProductValidationError(
            "product specification root failed: undeclared JSON content under product/specs/product/: "
            + ", ".join(undeclared_json)
        )

    print("ok: product specification system inactive")


def main(argv: list[str]) -> int:
    if len(argv) > 2:
        print(f"validation error: unknown argument: {argv[2]}", file=sys.stderr)
        return 1

    repo_root = Path(argv[1]).resolve() if len(argv) > 1 else Path.cwd().resolve()
    try:
        validate_inactive_product(repo_root)
        return 0
    except (BootstrapProductValidationError, OSError) as exc:
        print(f"validation error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
