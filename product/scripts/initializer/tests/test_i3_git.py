from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from initializer.git import (
    I3_AUTHOR_EMAIL,
    I3_AUTHOR_NAME,
    I3_BOOTSTRAP_PROFILE_ID,
    I3_COMMIT_MESSAGE,
    GitError,
    initialize_i3_git_repository,
    verify_i3_git_repository,
)


class I3GitBootstrapTests(unittest.TestCase):
    def make_repository(self) -> tuple[tempfile.TemporaryDirectory, Path]:
        td = tempfile.TemporaryDirectory()
        repo = Path(td.name) / "repository"
        repo.mkdir()
        (repo / "README.md").write_text("hello\n", encoding="utf-8")
        script = repo / "repo" / "scripts" / "validate"
        script.parent.mkdir(parents=True)
        script.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
        script.chmod(0o755)
        self.addCleanup(td.cleanup)
        return td, repo

    def test_initializes_exact_single_root_commit_profile(self):
        _td, repo = self.make_repository()
        result = initialize_i3_git_repository(repo)

        self.assertEqual(result.profile_id, I3_BOOTSTRAP_PROFILE_ID)
        self.assertEqual(result.branch, "main")
        self.assertEqual(result.commit_count, 1)
        self.assertTrue(result.worktree_clean)
        self.assertEqual(result.remote_count, 0)
        self.assertEqual(result.tag_count, 0)
        self.assertEqual(result.refs, ("refs/heads/main",))
        self.assertEqual(result.commit.object_format, "sha1")
        self.assertEqual(len(result.commit.object_id), 40)
        self.assertEqual(result.tree.object_format, "sha1")
        self.assertEqual(len(result.tree.object_id), 40)

    def test_identical_content_produces_identical_tree_and_commit(self):
        _a, repo_a = self.make_repository()
        _b, repo_b = self.make_repository()
        a = initialize_i3_git_repository(repo_a)
        b = initialize_i3_git_repository(repo_b)
        self.assertEqual(a.tree, b.tree)
        self.assertEqual(a.commit, b.commit)

    def test_executable_mode_changes_tree_and_commit(self):
        _a, repo_a = self.make_repository()
        _b, repo_b = self.make_repository()
        (repo_b / "repo" / "scripts" / "validate").chmod(0o644)
        a = initialize_i3_git_repository(repo_a)
        b = initialize_i3_git_repository(repo_b)
        self.assertNotEqual(a.tree, b.tree)
        self.assertNotEqual(a.commit, b.commit)

    def test_verify_rejects_remote(self):
        _td, repo = self.make_repository()
        initialize_i3_git_repository(repo)
        import subprocess
        subprocess.run(
            ["git", "-C", str(repo), "remote", "add", "origin", "https://example.invalid/x"],
            check=True,
        )
        with self.assertRaisesRegex(GitError, "no remotes"):
            verify_i3_git_repository(repo)

    def test_verify_rejects_extra_commit(self):
        _td, repo = self.make_repository()
        initialize_i3_git_repository(repo)
        import os
        import subprocess
        (repo / "extra.txt").write_text("extra\n", encoding="utf-8")
        env = dict(os.environ)
        env.update({
            "GIT_AUTHOR_NAME": I3_AUTHOR_NAME,
            "GIT_AUTHOR_EMAIL": I3_AUTHOR_EMAIL,
            "GIT_COMMITTER_NAME": I3_AUTHOR_NAME,
            "GIT_COMMITTER_EMAIL": I3_AUTHOR_EMAIL,
            "GIT_AUTHOR_DATE": "1234567890 +0000",
            "GIT_COMMITTER_DATE": "1234567890 +0000",
        })
        subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True, env=env)
        subprocess.run(
            ["git", "-C", str(repo), "commit", "--no-gpg-sign", "-m", I3_COMMIT_MESSAGE],
            check=True,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        with self.assertRaisesRegex(GitError, "exactly one commit"):
            verify_i3_git_repository(repo)

    def test_rejects_existing_git_state_without_mutation(self):
        _td, repo = self.make_repository()
        (repo / ".git").mkdir()
        marker = repo / ".git" / "marker"
        marker.write_text("keep\n", encoding="utf-8")
        with self.assertRaisesRegex(GitError, "absent .git"):
            initialize_i3_git_repository(repo)
        self.assertEqual(marker.read_text(encoding="utf-8"), "keep\n")


if __name__ == "__main__":
    unittest.main()
