from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "product" / "src"))

from initializer.cli import build_parser  # noqa: E402
from initializer.core import (  # noqa: E402
    FRAMEWORK_SOURCE_RECORD,
    GENERIC_PRODUCT_MARKER,
    InitializationError,
    initialize_repository,
)


def run_git(cwd: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    completed = subprocess.run(
        ["git", *args],
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if check and completed.returncode != 0:
        raise AssertionError(
            f"git {' '.join(args)} failed: {completed.stderr or completed.stdout}"
        )
    return completed


class InitializerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory(prefix="repo-spec-fs001-")
        self.temp = Path(self.tempdir.name)

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def initialize(self, destination: Path, **kwargs) -> str:
        return initialize_repository(
            source_root=ROOT,
            destination=destination,
            require_accepted=False,
            **kwargs,
        )

    def assert_initialized(self, destination: Path, source_revision: str) -> None:
        self.assertTrue((destination / ".git").is_dir())
        self.assertTrue((destination / "repo/scripts/validate").is_file())
        self.assertTrue((destination / GENERIC_PRODUCT_MARKER).is_file())

        record = json.loads(
            (destination / FRAMEWORK_SOURCE_RECORD).read_text(encoding="utf-8")
        )
        self.assertEqual(record["repo_spec_source_revision"], source_revision)

        self.assertFalse((destination / "product/design/DP-100-repo-spec-initializer.md").exists())
        self.assertFalse((destination / "product/planning").exists())
        self.assertFalse((destination / "product/specs").exists())
        self.assertFalse((destination / "product/src").exists())
        self.assertFalse((destination / "product/validation").exists())

        validator = subprocess.run(
            [str(destination / "repo/scripts/validate")],
            cwd=destination,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertEqual(
            validator.returncode,
            0,
            msg=f"initialized validation failed:\n{validator.stdout}\n{validator.stderr}",
        )

        # Fetch-by-path does not persist a dependency on the supplying checkout.
        remotes = run_git(destination, "remote").stdout.splitlines()
        self.assertEqual(remotes, [])

        # The exact source commit remains in the initialized repository history,
        # so copied framework Planning Design bindings continue to resolve.
        self.assertEqual(
            run_git(destination, "cat-file", "-t", source_revision).stdout.strip(),
            "commit",
        )

    def test_cli_surface_requires_destination_only(self) -> None:
        parser = build_parser()
        subparsers = next(
            action for action in parser._actions
            if action.__class__.__name__ == "_SubParsersAction"
        )
        init_parser = subparsers.choices["init"]
        option_actions = [
            action
            for action in init_parser._actions
            if action.option_strings and action.dest != "help"
        ]
        self.assertEqual(len(option_actions), 1)
        self.assertEqual(option_actions[0].option_strings, ["--repo"])
        self.assertTrue(option_actions[0].required)

    def test_accepts_linked_git_worktree_as_supplying_checkout(self) -> None:
        linked = self.temp / "linked-source"
        run_git(ROOT, "worktree", "add", "--detach", str(linked), "HEAD")
        try:
            destination = self.temp / "linked-result"
            revision = initialize_repository(
                source_root=linked,
                destination=destination,
                require_accepted=False,
            )
            self.assert_initialized(destination, revision)
        finally:
            run_git(ROOT, "worktree", "remove", "--force", str(linked), check=False)

    def test_initialized_repository_state(self) -> None:
        destination = self.temp / "state-result"
        revision = self.initialize(destination)
        self.assert_initialized(destination, revision)

    def test_initializes_absent_destination(self) -> None:
        destination = self.temp / "new-repo"
        revision = self.initialize(destination)
        self.assert_initialized(destination, revision)

    def test_initializes_existing_empty_directory(self) -> None:
        destination = self.temp / "empty-repo"
        destination.mkdir()
        revision = self.initialize(destination)
        self.assert_initialized(destination, revision)

    def test_refuses_nonempty_destination_without_deleting_material(self) -> None:
        destination = self.temp / "occupied"
        destination.mkdir()
        sentinel = destination / "keep.txt"
        sentinel.write_text("keep\n", encoding="utf-8")

        with self.assertRaises(InitializationError):
            self.initialize(destination)

        self.assertEqual(sentinel.read_text(encoding="utf-8"), "keep\n")

    def test_refuses_dirty_supplying_framework_material(self) -> None:
        source = self.temp / "dirty-source"
        subprocess.run(
            ["git", "clone", "--no-hardlinks", str(ROOT), str(source)],
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        (source / "README.md").write_text(
            (source / "README.md").read_text(encoding="utf-8") + "\ndirty\n",
            encoding="utf-8",
        )

        with self.assertRaises(InitializationError):
            initialize_repository(
                source_root=source,
                destination=self.temp / "dirty-result",
                require_accepted=False,
            )

    def test_normal_cli_refuses_unaccepted_feature_revision(self) -> None:
        current = run_git(ROOT, "rev-parse", "HEAD").stdout.strip()
        accepted = run_git(
            ROOT,
            "merge-base",
            "--is-ancestor",
            current,
            "refs/heads/main",
            check=False,
        )
        if accepted.returncode == 0:
            self.skipTest("current test checkout is already accepted in local main history")

        destination = self.temp / "cli-result"
        completed = subprocess.run(
            [
                str(ROOT / "product/scripts/repo-spec"),
                "init",
                "--repo",
                str(destination),
            ],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("not established as accepted", completed.stderr)
        self.assertFalse(destination.exists())

    def test_explicit_test_seam_allows_unaccepted_feature_revision(self) -> None:
        current = run_git(ROOT, "rev-parse", "HEAD").stdout.strip()
        accepted = run_git(
            ROOT,
            "merge-base",
            "--is-ancestor",
            current,
            "refs/heads/main",
            check=False,
        )
        if accepted.returncode == 0:
            self.skipTest("current test checkout is already accepted in local main history")

        destination = self.temp / "cli-test-seam"
        env = os.environ.copy()
        env["REPO_SPEC_ALLOW_UNACCEPTED_TEST_SOURCE"] = "1"
        completed = subprocess.run(
            [
                str(ROOT / "product/scripts/repo-spec"),
                "init",
                "--repo",
                str(destination),
            ],
            cwd=ROOT,
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertEqual(
            completed.returncode,
            0,
            msg=(
                f"stdout:\n{completed.stdout}\n"
                f"stderr:\n{completed.stderr}"
            ),
        )
        self.assertIn("unaccepted test source revision", completed.stderr)
        self.assertTrue(destination.exists())

    def test_validation_failure_does_not_promote_destination(self) -> None:
        destination = self.temp / "invalid-result"

        def break_candidate(stage: Path) -> None:
            (stage / "unauthorized-root.txt").write_text("invalid\n", encoding="utf-8")

        with self.assertRaises(InitializationError):
            self.initialize(destination, before_validate=break_candidate)

        self.assertFalse(destination.exists())

    def test_source_revision_matches_current_supplying_commit(self) -> None:
        destination = self.temp / "source-record"
        expected = run_git(ROOT, "rev-parse", "HEAD").stdout.strip()
        observed = self.initialize(destination)
        self.assertEqual(observed, expected)

        record = json.loads(
            (destination / FRAMEWORK_SOURCE_RECORD).read_text(encoding="utf-8")
        )
        self.assertEqual(record["repo_spec_source_revision"], expected)


if __name__ == "__main__":
    unittest.main()
