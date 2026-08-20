#!/usr/bin/env python3
"""Production validation runner for the root/whole-checkout domain."""
from __future__ import annotations
import sys
from pathlib import Path
REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))
from validation.checks.domain import validate_root
from validation.checks.policy import RootValidationError

def main(argv: list[str]) -> int:
    if len(argv) > 2:
        print(f"validation error: unknown argument: {argv[2]}", file=sys.stderr)
        return 1
    repo_root = Path(argv[1]).resolve() if len(argv) > 1 else Path.cwd().resolve()
    try:
        validate_root(repo_root)
        return 0
    except (RootValidationError, OSError) as exc:
        print(f"validation error: {exc}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
