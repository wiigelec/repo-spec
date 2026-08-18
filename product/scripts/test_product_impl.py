#!/usr/bin/env python3

from __future__ import annotations

import sys
from pathlib import Path


def main(argv: list[str]) -> int:
    repo_root = Path(argv[1]).resolve() if len(argv) > 1 else Path.cwd().resolve()
    del repo_root

    if len(argv) > 2:
        print(f"product test error: unknown mode: {argv[2]}", file=sys.stderr)
        return 1

    print(
        "product test error: lifecycle unavailable; "
        "product-test applicability and lifecycle require separately governed VS2 implementation",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
