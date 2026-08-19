from __future__ import annotations

import shutil
from pathlib import Path


def expect_failure(description: str, action, fragment: str) -> None:
    try:
        action()
    except Exception as exc:
        if fragment not in str(exc):
            raise AssertionError(
                f"{description}: expected {fragment!r}, got {exc}"
            ) from exc
        return
    raise AssertionError(f"{description}: expected failure")


def create_repo_fixture(
    repo_root: Path,
    temp_root: Path,
    fixture_index: int,
) -> Path:
    fixture_root = temp_root / f"fixture-{fixture_index}"
    fixture_root.mkdir(parents=True, exist_ok=True)
    shutil.copytree(repo_root / "repo", fixture_root / "repo")
    return fixture_root
