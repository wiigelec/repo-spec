from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .core import InitializationError, initialize_repository


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="repo-spec")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="initialize a repo-spec repository")
    init_parser.add_argument("--repo", required=True, metavar="DESTINATION")

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.command != "init":
        raise AssertionError(f"unhandled command: {args.command}")

    try:
        revision = initialize_repository(
            source_root=_repo_root(),
            destination=Path(args.repo),
            require_accepted=True,
        )
    except InitializationError as exc:
        print(f"repo-spec init: {exc}", file=sys.stderr)
        return 1

    print(f"Initialized repo-spec repository at {Path(args.repo).expanduser()}")
    print(f"Source revision: {revision}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
