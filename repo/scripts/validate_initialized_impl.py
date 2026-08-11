#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REQUIRED_FILES = {".gitignore", "AGENTS.md", "LICENSE", "README.md"}
REQUIRED_DIRS = {".github", "product", "reference", "repo", "scripts", "user"}
ALLOWED_TOP_LEVEL = REQUIRED_FILES | REQUIRED_DIRS | {".git"}

class ValidationError(RuntimeError):
    pass

def git(repo_root: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        ["git", *args],
        cwd=repo_root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if check and result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip()
        raise ValidationError(f"git command failed: git {' '.join(args)}: {detail}")
    return result

def validate_root_boundary(repo_root: Path) -> None:
    actual = {path.name for path in repo_root.iterdir()}
    missing = sorted((REQUIRED_FILES | REQUIRED_DIRS) - actual)
    if missing:
        raise ValidationError(
            "repository root boundary failed: missing required top-level entries: "
            + ", ".join(missing)
        )
    extra = sorted(actual - ALLOWED_TOP_LEVEL)
    if extra:
        raise ValidationError(
            "repository root boundary failed: undeclared top-level entries: "
            + ", ".join(extra)
        )
    wrong_kind = []
    for name in sorted(REQUIRED_FILES):
        if not (repo_root / name).is_file():
            wrong_kind.append(f"{name} (expected file)")
    for name in sorted(REQUIRED_DIRS):
        if not (repo_root / name).is_dir():
            wrong_kind.append(f"{name} (expected directory)")
    if wrong_kind:
        raise ValidationError(
            "repository root boundary failed: wrong-kind top-level entries: "
            + ", ".join(wrong_kind)
        )
    print("ok: repository root boundary")

def initial_commit(repo_root: Path) -> str:
    result = git(repo_root, "rev-list", "--max-parents=0", "HEAD")
    roots = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    if len(roots) != 1:
        raise ValidationError(
            f"repo tree integrity failed: expected exactly one initial commit, found {len(roots)}"
        )
    return roots[0]

def tree_sha(repo_root: Path, commit: str, path: str) -> str:
    result = git(repo_root, "rev-parse", f"{commit}:{path}", check=False)
    if result.returncode != 0:
        raise ValidationError(
            f"repo tree integrity failed: {path}/ is absent from commit {commit}"
        )
    return result.stdout.strip()

def validate_repo_tree_integrity(repo_root: Path) -> None:
    first = initial_commit(repo_root)
    expected = tree_sha(repo_root, first, "repo")
    current = tree_sha(repo_root, "HEAD", "repo")
    if current != expected:
        raise ValidationError(
            "repo tree integrity failed: committed repo/ tree differs from initialization baseline"
        )
    status = git(
        repo_root,
        "status",
        "--porcelain=v1",
        "--untracked-files=all",
        "--",
        "repo",
    ).stdout.strip()
    if status:
        raise ValidationError(
            "repo tree integrity failed: working tree changes exist under repo/"
        )
    print(f"ok: immutable repo tree ({expected})")

def validate(repo_root: Path) -> None:
    if not (repo_root / ".git").exists():
        raise ValidationError("repository root boundary failed: missing .git repository")
    validate_root_boundary(repo_root)
    validate_repo_tree_integrity(repo_root)

def main(argv: list[str]) -> int:
    if len(argv) > 2:
        print(f"validation error: unknown argument: {argv[2]}", file=sys.stderr)
        return 1
    repo_root = Path(argv[1]).resolve() if len(argv) == 2 else Path(__file__).resolve().parents[2]
    try:
        validate(repo_root)
        return 0
    except (ValidationError, OSError) as exc:
        print(f"validation error: {exc}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
