#!/usr/bin/env python3

"""Validation entry point for repo-spec."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from repo_model import RepositoryError, load_specs as load_repo_specs, resolve_repo_path as resolve_repo_path_impl
from validation.errors import ValidationFailure, fail
from validation.repository_checks import validate_repo


def resolve_repo_path(repo_root: Path, value: str) -> Path:
    try:
        return resolve_repo_path_impl(repo_root, value)
    except RepositoryError as exc:
        fail(str(exc))


def load_specs(repo_root: Path) -> tuple[dict[str, Any], dict[str, dict[str, Any]], dict[str, str], list[str]]:
    try:
        return load_repo_specs(repo_root)
    except RepositoryError as exc:
        fail(str(exc))


def main(argv: list[str]) -> int:
    repo_root = Path(argv[1]).resolve() if len(argv) > 1 else Path.cwd().resolve()
    mode = argv[2] if len(argv) > 2 else "--write"

    if mode == "--self-test-failure":
        print("forced failure for behavior test", file=sys.stderr)
        return 1

    try:
        if mode == "--write":
            validate_repo(repo_root)
            return 0
        if mode == "--mutation-tests":
            from validation.tests.mutation_tests import run_complete_validation_tests

            run_complete_validation_tests(repo_root)

            from initializer.tests.run_tests import run_initializer_tests
            run_initializer_tests(repo_root)

            return 0
        fail(f"unknown mode: {mode}")
    except ValidationFailure as exc:
        print(f"validation error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
