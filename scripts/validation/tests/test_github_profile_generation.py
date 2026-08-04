from __future__ import annotations

import tempfile
from pathlib import Path

from github_profile import render_profile_adapters, write_profile_adapters
from validation.repository_checks import validate_repo

from .mutation_support import create_repo_fixture, expect_failure


def snapshot_profile_files(repo_root: Path) -> dict[str, str]:
    return {
        path.relative_to(repo_root).as_posix(): path.read_text()
        for path in sorted((repo_root / "profiles/github").rglob("*") if (repo_root / "profiles/github").exists() else [])
        if path.is_file()
    } | {
        path.relative_to(repo_root).as_posix(): path.read_text()
        for path in sorted((repo_root / ".github").rglob("*") if (repo_root / ".github").exists() else [])
        if path.is_file()
    }


def run_github_profile_generation_tests(repo_root: Path) -> None:
    with tempfile.TemporaryDirectory(prefix="repo-spec-validation-") as temp_root_name:
        temp_root = Path(temp_root_name)
        temp_repo = create_repo_fixture(repo_root, temp_root, 0)

        rendered_paths = [path for path, _content in render_profile_adapters(temp_repo)]
        assert rendered_paths == [".github/ISSUE_TEMPLATE/governing-issue.yml", ".github/PULL_REQUEST_TEMPLATE.md"]

        before = snapshot_profile_files(temp_repo)
        write_profile_adapters(temp_repo)
        validate_repo(temp_repo)
        after_first = snapshot_profile_files(temp_repo)
        write_profile_adapters(temp_repo)
        after_second = snapshot_profile_files(temp_repo)

        assert before == after_first == after_second

    print("ok: github profile generation tests")


def run_github_profile_mutation_tests(repo_root: Path) -> None:
    with tempfile.TemporaryDirectory(prefix="repo-spec-validation-") as temp_root_name:
        temp_root = Path(temp_root_name)

        temp_repo = create_repo_fixture(repo_root, temp_root, 0)
        (temp_repo / ".github/PULL_REQUEST_TEMPLATE.md").write_text(
            (temp_repo / ".github/PULL_REQUEST_TEMPLATE.md").read_text().replace("## Summary", "## Summary\n\nTampered"),
        )
        expect_failure(
            "stale installed GitHub adapter",
            lambda: validate_repo(temp_repo),
            "github profile freshness failed: stale generated adapter: source profiles/github/PULL_REQUEST_TEMPLATE.md -> output .github/PULL_REQUEST_TEMPLATE.md",
        )

        temp_repo = create_repo_fixture(repo_root, temp_root, 1)
        (temp_repo / ".github/ISSUE_TEMPLATE/governing-issue.yml").unlink()
        expect_failure(
            "missing installed GitHub adapter",
            lambda: validate_repo(temp_repo),
            "github profile freshness failed: missing managed adapter(s): .github/ISSUE_TEMPLATE/governing-issue.yml",
        )

        temp_repo = create_repo_fixture(repo_root, temp_root, 2)
        orphan = temp_repo / ".github/orphaned-adapter.yml"
        orphan.parent.mkdir(parents=True, exist_ok=True)
        orphan.write_text("name: orphaned\n")
        expect_failure(
            "orphaned installed GitHub adapter",
            lambda: validate_repo(temp_repo),
            "github profile freshness failed: orphaned managed adapter(s): .github/orphaned-adapter.yml",
        )

    print("ok: github profile mutation tests")
