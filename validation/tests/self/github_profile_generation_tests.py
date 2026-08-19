from __future__ import annotations

import tempfile
from pathlib import Path

from github_profile import GitHubProfileError, check_profile_freshness, render_profile_adapters, write_profile_adapters

from repo.validation.tests.self.mutation_support import create_repo_fixture



def expect_profile_failure(description: str, func, fragment: str) -> None:
    try:
        func()
    except GitHubProfileError as exc:
        assert fragment in str(exc), (
            f"github profile mutation test failed: {description} "
            f"(expected {fragment!r}, got {exc!s})"
        )
    else:
        raise AssertionError(
            f"github profile mutation test failed: {description} did not fail"
        )

def snapshot_profile_files(repo_root: Path) -> dict[str, str]:
    return {
        path.relative_to(repo_root).as_posix(): path.read_text()
        for path in sorted((repo_root / "repo/profiles/github").rglob("*") if (repo_root / "repo/profiles/github").exists() else [])
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
        assert rendered_paths == [
            ".github/ISSUE_TEMPLATE/governing-issue.yml",
            ".github/PULL_REQUEST_TEMPLATE.md",
            ".github/workflows/github-field-policy.yml",
            ".github/workflows/governed-work-promotion.yml",
            ".github/workflows/validation.yml",
        ]

        before = snapshot_profile_files(temp_repo)
        write_profile_adapters(temp_repo)
        check_profile_freshness(temp_repo)
        after_first = snapshot_profile_files(temp_repo)
        write_profile_adapters(temp_repo)
        after_second = snapshot_profile_files(temp_repo)

        assert before != after_first
    assert after_first == after_second

    print("ok: github profile generation tests")


def run_github_profile_mutation_tests(repo_root: Path) -> None:
    with tempfile.TemporaryDirectory(prefix="repo-spec-validation-") as temp_root_name:
        temp_root = Path(temp_root_name)

        temp_repo = create_repo_fixture(repo_root, temp_root, 0)
        write_profile_adapters(temp_repo)
        (temp_repo / ".github/PULL_REQUEST_TEMPLATE.md").write_text(
            (temp_repo / ".github/PULL_REQUEST_TEMPLATE.md").read_text().replace("## Summary", "## Summary\n\nTampered"),
        )
        expect_profile_failure(
            "stale installed GitHub adapter",
            lambda: check_profile_freshness(temp_repo),
            "stale generated adapter: source repo/profiles/github/PULL_REQUEST_TEMPLATE.md -> output .github/PULL_REQUEST_TEMPLATE.md",
        )

        temp_repo = create_repo_fixture(repo_root, temp_root, 1)
        write_profile_adapters(temp_repo)
        (temp_repo / ".github/workflows/github-field-policy.yml").write_text(
            (temp_repo / ".github/workflows/github-field-policy.yml").read_text().replace("GitHub field policy", "GitHub field policy (tampered)"),
        )
        expect_profile_failure(
            "stale installed GitHub workflow adapter",
            lambda: check_profile_freshness(temp_repo),
            "stale generated adapter: source repo/profiles/github/workflows/github-field-policy.yml -> output .github/workflows/github-field-policy.yml",
        )

        temp_repo = create_repo_fixture(repo_root, temp_root, 2)
        write_profile_adapters(temp_repo)
        (temp_repo / ".github/workflows/validation.yml").unlink()
        expect_profile_failure(
            "missing installed GitHub workflow adapter",
            lambda: check_profile_freshness(temp_repo),
            "missing managed adapter(s): .github/workflows/validation.yml",
        )

        temp_repo = create_repo_fixture(repo_root, temp_root, 3)
        write_profile_adapters(temp_repo)
        orphan = temp_repo / ".github/orphaned-adapter.yml"
        orphan.parent.mkdir(parents=True, exist_ok=True)
        orphan.write_text("name: orphaned\n")
        expect_profile_failure(
            "orphaned installed GitHub adapter",
            lambda: check_profile_freshness(temp_repo),
            "orphaned managed adapter(s): .github/orphaned-adapter.yml",
        )

    print("ok: github profile mutation tests")
