#!/usr/bin/env python3
# Transportable repository-root and immutable-framework validation.

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

SOURCE_REQUIRED_FILES = {".gitignore", "AGENTS.md", "LICENSE", "README.md"}
SOURCE_REQUIRED_DIRS = {".github", "product", "reference", "repo", "scripts", "user"}
INITIALIZED_REQUIRED_FILES = {".gitignore", "AGENTS.md", "LICENSE", "README.md"}
INITIALIZED_REQUIRED_DIRS = {".github", "product", "repo", "scripts", "user"}
IGNORED_ROOT_ENTRIES = {".git"}


class RootValidationError(RuntimeError):
    pass


def _git(repo_root: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        ["git", *args],
        cwd=repo_root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if check and result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip()
        raise RootValidationError(f"git command failed: git {' '.join(args)}: {detail}")
    return result


def _is_initialized(repo_root: Path) -> bool:
    return not (repo_root / "reference").exists()


def validate_root_boundary(repo_root: Path, initialized: bool) -> None:
    required_files = INITIALIZED_REQUIRED_FILES if initialized else SOURCE_REQUIRED_FILES
    required_dirs = INITIALIZED_REQUIRED_DIRS if initialized else SOURCE_REQUIRED_DIRS
    actual = {
        path.name: path
        for path in repo_root.iterdir()
        if path.name not in IGNORED_ROOT_ENTRIES
    }
    expected = required_files | required_dirs

    missing = sorted(expected - set(actual))
    if missing:
        raise RootValidationError(
            "repository root boundary failed: missing required top-level entries: "
            + ", ".join(missing)
        )

    extra = sorted(set(actual) - expected)
    if extra:
        raise RootValidationError(
            "repository root boundary failed: undeclared top-level entries: "
            + ", ".join(extra)
        )

    wrong_kind: list[str] = []
    for name in sorted(required_files):
        if not actual[name].is_file():
            wrong_kind.append(f"{name} (expected file)")
    for name in sorted(required_dirs):
        if not actual[name].is_dir():
            wrong_kind.append(f"{name} (expected directory)")
    if wrong_kind:
        raise RootValidationError(
            "repository root boundary failed: wrong-kind top-level entries: "
            + ", ".join(wrong_kind)
        )

    print("ok: repository root boundary")


def validate_repo_tree_integrity(repo_root: Path) -> None:
    if not (repo_root / ".git").exists():
        raise RootValidationError(
            "repo tree integrity failed: initialized repository is missing .git"
        )

    roots = [
        line.strip()
        for line in _git(repo_root, "rev-list", "--max-parents=0", "HEAD").stdout.splitlines()
        if line.strip()
    ]
    if len(roots) != 1:
        raise RootValidationError(
            f"repo tree integrity failed: expected exactly one root commit, found {len(roots)}"
        )
    root_commit = roots[0]

    baseline_result = _git(repo_root, "rev-parse", f"{root_commit}:repo", check=False)
    if baseline_result.returncode != 0:
        raise RootValidationError(
            "repo tree integrity failed: repo/ is absent from the root commit"
        )
    baseline = baseline_result.stdout.strip()

    current_result = _git(repo_root, "rev-parse", "HEAD:repo", check=False)
    if current_result.returncode != 0:
        raise RootValidationError("repo tree integrity failed: repo/ is absent from HEAD")
    current = current_result.stdout.strip()

    if current != baseline:
        raise RootValidationError(
            "repo tree integrity failed: committed repo/ tree differs from initialized baseline"
        )

    status = _git(
        repo_root,
        "status",
        "--porcelain=v1",
        "--untracked-files=all",
        "--",
        "repo",
    ).stdout.strip()
    if status:
        raise RootValidationError(
            "repo tree integrity failed: working tree changes exist under repo/"
        )

    print(f"ok: immutable repo tree ({baseline})")


def validate(repo_root: Path) -> bool:
    initialized = _is_initialized(repo_root)
    validate_root_boundary(repo_root, initialized)
    if initialized:
        validate_repo_tree_integrity(repo_root)
    return initialized


def main(argv: list[str]) -> int:
    if len(argv) > 2:
        print(f"validation error: unknown argument: {argv[2]}", file=sys.stderr)
        return 1

    repo_root = Path(argv[1]).resolve() if len(argv) > 1 else Path.cwd().resolve()

    try:
        validate(repo_root)
        return 0
    except (RootValidationError, OSError) as exc:
        print(f"validation error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
