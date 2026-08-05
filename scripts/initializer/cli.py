from __future__ import annotations

import sys
from pathlib import Path

from initializer.validation import validate_json_request


def main(argv: list[str]) -> int:
    if len(argv) < 3:
        print("usage: repo-spec-init validate-request <request.json>", file=sys.stderr)
        return 1

    command = argv[2]
    if command != "validate-request":
        print(f"unknown command: {command}", file=sys.stderr)
        print("usage: repo-spec-init validate-request <request.json>", file=sys.stderr)
        return 1

    if len(argv) < 4:
        print("error: missing request file path", file=sys.stderr)
        print("usage: repo-spec-init validate-request <request.json>", file=sys.stderr)
        return 1

    request_path = Path(argv[3])
    return validate_json_request(request_path)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
