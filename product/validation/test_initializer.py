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
    PRODUCT_DESIGN_README,
    PRODUCT_SPECS_README,
    PRODUCT_VALIDATION_ENTRYPOINT,
    PRODUCT_VALIDATION_MANIFEST,
    PRODUCT_VALIDATOR,
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
        source = self._make_clean_candidate_source(
            f"candidate-source-{destination.name}"
        )
        return initialize_repository(
            source_root=source,
            destination=destination,
            require_accepted=False,
            **kwargs,
        )

    def assert_initialized(self, destination: Path, source_revision: str) -> None:
        self.assertTrue((destination / ".git").is_dir())
        self.assertTrue((destination / "repo/scripts/validate").is_file())
        self.assertTrue((destination / "scripts/validate").is_file())
        self.assertFalse((destination / "repo/planning").exists())
        self.assertTrue((destination / PRODUCT_DESIGN_README).is_file())
        self.assertTrue((destination / PRODUCT_SPECS_README).is_file())
        self.assertTrue((destination / PRODUCT_VALIDATION_ENTRYPOINT).is_file())
        self.assertTrue(os.access(destination / PRODUCT_VALIDATION_ENTRYPOINT, os.X_OK))
        self.assertTrue((destination / PRODUCT_VALIDATION_MANIFEST).is_file())
        self.assertTrue((destination / PRODUCT_VALIDATOR).is_file())
        self.assertFalse((destination / "product/design/.gitkeep").exists())

        manifest = json.loads(
            (destination / PRODUCT_VALIDATION_MANIFEST).read_text(encoding="utf-8")
        )
        self.assertEqual(manifest, {"version": 1, "bindings": []})

        listed = subprocess.run(
            [str(destination / PRODUCT_VALIDATION_ENTRYPOINT), "--list-tasks"],
            cwd=destination, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        self.assertEqual(listed.returncode, 0, listed.stderr)
        self.assertEqual(listed.stdout, "")

        product_validation = subprocess.run(
            [str(destination / PRODUCT_VALIDATION_ENTRYPOINT)],
            cwd=destination, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        self.assertEqual(product_validation.returncode, 0, product_validation.stderr)

        unknown = subprocess.run(
            [str(destination / PRODUCT_VALIDATION_ENTRYPOINT), "--task", "__unknown__"],
            cwd=destination, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        self.assertNotEqual(unknown.returncode, 0)

        design_readme = (destination / PRODUCT_DESIGN_README).read_text(encoding="utf-8")
        specs_readme = (destination / PRODUCT_SPECS_README).read_text(encoding="utf-8")
        self.assertIn("Design owns product meaning", design_readme)
        self.assertIn("Normative requirements belong here", specs_readme)

        record = json.loads(
            (destination / FRAMEWORK_SOURCE_RECORD).read_text(encoding="utf-8")
        )
        self.assertEqual(record["repo_spec_source_revision"], source_revision)

        self.assertFalse((destination / "product/design/DP-100-repo-spec-initializer.md").exists())
        self.assertFalse((destination / "product/planning").exists())
        self.assertTrue((destination / "product/specs").is_dir())
        self.assertFalse((destination / "product/src").exists())
        self.assertTrue((destination / "product/validation").is_dir())

        remotes = run_git(destination, "remote").stdout.splitlines()
        self.assertEqual(remotes, [])

        head = run_git(destination, "rev-parse", "HEAD").stdout.strip()
        roots = run_git(destination, "rev-list", "--max-parents=0", "HEAD").stdout.splitlines()
        self.assertEqual(roots, [head])
        self.assertEqual(run_git(destination, "rev-list", "--count", "HEAD").stdout.strip(), "1")
        self.assertNotEqual(
            run_git(destination, "cat-file", "-e", f"{source_revision}^{{commit}}", check=False).returncode,
            0,
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
            run_git(linked, "config", "user.name", "repo-spec test")
            run_git(linked, "config", "user.email", "repo-spec-test@local.invalid")

            # The linked worktree starts from the reviewed Planning HEAD. Install
            # and commit the current candidate Build surfaces so this pre-merge
            # regression exercises the same candidate as the other initializer
            # source fixtures while preserving the source-cleanliness contract.
            for rel in (
                Path("product/src/initializer/core.py"),
                Path("repo/validation/validate_framework.py"),
                Path("repo/validation/requirement-evaluation.json"),
                Path("scripts/validate"),
            ):
                target = linked / rel
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(ROOT / rel, target)

            run_git(linked, "add", "-A")
            staged = run_git(linked, "diff", "--cached", "--quiet", check=False)
            if staged.returncode == 1:
                run_git(linked, "commit", "-m", "Install candidate Build surfaces")
            elif staged.returncode != 0:
                raise AssertionError("could not evaluate linked candidate source changes")

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

        readme = (destination / "README.md").read_text(encoding="utf-8")
        agents = (destination / "AGENTS.md").read_text(encoding="utf-8")
        self.assertNotIn("fs0-genesis", readme)
        self.assertNotIn("repo_old/", readme)
        self.assertNotIn("repo_old/", agents)
        self.assertIn("product/` is the product-owned domain", readme)
        self.assertIn("Begin substantive product work in Product Design", readme)
        self.assertLess(
            readme.index("- `user/` — user-owned operational material outside the framework."),
            readme.index("Begin substantive product work in Product Design"),
        )
        self.assertIn(
            "Do not assume Product meaning before Product Design establishes it",
            agents,
        )

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

    def test_refuses_symlink_destination_without_mutating_target(self) -> None:
        target = self.temp / "symlink-target"
        target.mkdir()
        destination = self.temp / "symlink-destination"
        destination.symlink_to(target, target_is_directory=True)

        with self.assertRaisesRegex(
            InitializationError,
            "destination exists but is not an ordinary directory",
        ):
            self.initialize(destination)

        self.assertTrue(destination.is_symlink())
        self.assertEqual(list(target.iterdir()), [])

    def test_refuses_dirty_initializer_source_material(self):
        source = self._make_clean_candidate_source("dirty-initializer-source")
        candidate = source / "product" / "src" / "initializer" / "core.py"
        candidate.write_text(
            candidate.read_text(encoding="utf-8")
            + "\n# dirty initializer source test\n",
            encoding="utf-8",
        )

        with self.assertRaises(InitializationError):
            initialize_repository(
                source_root=source,
                destination=self.temp / "dirty-initializer-result",
                require_accepted=False,
            )

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

    def _make_clean_candidate_source(self, name: str) -> Path:
        source = self.temp / name
        subprocess.run(
            ["git", "clone", "--no-hardlinks", str(ROOT), str(source)],
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        run_git(source, "config", "user.name", "repo-spec test")
        run_git(source, "config", "user.email", "repo-spec-test@local.invalid")
        run_git(source, "switch", "-c", "candidate")

        # Commit the current candidate implementation into the temporary source.
        # This lets pre-commit Product Validation exercise the candidate while
        # preserving the initializer's source-cleanliness contract.
        for rel in (
            Path("product/src/initializer/cli.py"),
            Path("product/src/initializer/core.py"),
            Path("product/scripts/repo-spec"),
            Path("repo/validation/validate_framework.py"),
            Path("repo/validation/requirement-evaluation.json"),
            Path("scripts/validate"),
        ):
            target = source / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / rel, target)

        run_git(source, "add", "-A")
        staged = run_git(source, "diff", "--cached", "--quiet", check=False)
        if staged.returncode == 1:
            run_git(source, "commit", "-m", "Install candidate initializer implementation")
        elif staged.returncode != 0:
            raise AssertionError("could not evaluate candidate source changes")
        return source

    def _make_unaccepted_candidate_source(self, name: str) -> Path:
        source = self.temp / name
        subprocess.run(
            ["git", "clone", "--no-hardlinks", str(ROOT), str(source)],
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        run_git(source, "config", "user.name", "repo-spec test")
        run_git(source, "config", "user.email", "repo-spec-test@local.invalid")
        base = run_git(source, "rev-parse", "HEAD").stdout.strip()
        run_git(source, "switch", "--detach", base)
        run_git(source, "branch", "-f", "main", base)
        run_git(source, "switch", "-c", "candidate")

        # Install the candidate implementation under test into a source whose
        # HEAD will deliberately not be reachable from its local main.
        for rel in (
            Path("product/src/initializer/cli.py"),
            Path("product/src/initializer/core.py"),
            Path("product/scripts/repo-spec"),
            Path("repo/validation/validate_framework.py"),
            Path("repo/validation/requirement-evaluation.json"),
            Path("scripts/validate"),
        ):
            target = source / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / rel, target)

        marker = source / "product/src/initializer/.candidate-test"
        marker.write_text("candidate\n", encoding="utf-8")
        run_git(source, "add", "-A")
        run_git(source, "commit", "-m", "Create unaccepted initializer candidate")
        return source

    def test_normal_cli_refuses_unaccepted_feature_revision(self) -> None:
        source = self._make_unaccepted_candidate_source("unaccepted-cli-source")
        destination = self.temp / "cli-result"
        env = os.environ.copy()
        env["REPO_SPEC_ALLOW_UNACCEPTED_TEST_SOURCE"] = "1"
        completed = subprocess.run(
            [
                str(source / "product/scripts/repo-spec"),
                "init",
                "--repo",
                str(destination),
            ],
            cwd=source,
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("not established as accepted", completed.stderr)
        self.assertNotIn("unaccepted test source revision", completed.stderr)
        self.assertFalse(destination.exists())

    def test_internal_test_seam_allows_unaccepted_feature_revision(self) -> None:
        source = self._make_unaccepted_candidate_source("unaccepted-internal-source")
        destination = self.temp / "internal-test-seam"
        revision = initialize_repository(
            source_root=source,
            destination=destination,
            require_accepted=False,
        )
        self.assertEqual(revision, run_git(source, "rev-parse", "HEAD").stdout.strip())
        self.assert_initialized(destination, revision)

    def test_validation_failure_does_not_promote_destination(self) -> None:
        destination = self.temp / "invalid-result"

        def break_candidate(stage: Path) -> None:
            (stage / "unauthorized-root.txt").write_text("invalid\n", encoding="utf-8")

        with self.assertRaises(InitializationError):
            self.initialize(destination, before_validate=break_candidate)

        self.assertFalse(destination.exists())

    def test_source_revision_matches_current_supplying_commit(self) -> None:
        source = self._make_clean_candidate_source("source-record-source")
        destination = self.temp / "source-record"
        expected = run_git(source, "rev-parse", "HEAD").stdout.strip()
        observed = initialize_repository(
            source_root=source,
            destination=destination,
            require_accepted=False,
        )
        self.assertEqual(observed, expected)

        record = json.loads(
            (destination / FRAMEWORK_SOURCE_RECORD).read_text(encoding="utf-8")
        )
        self.assertEqual(record["repo_spec_source_revision"], expected)

    def test_initialized_repository_validates_after_source_checkout_removed(self) -> None:
        source = self.temp / "independence-source"
        subprocess.run(
            ["git", "clone", "--no-hardlinks", str(ROOT), str(source)],
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        run_git(source, "config", "user.name", "repo-spec test")
        run_git(source, "config", "user.email", "repo-spec-test@local.invalid")

        # Exercise the current pre-merge Build candidate rather than the
        # committed Planning base. Commit candidate framework/initializer
        # surfaces so supplier cleanliness remains true.
        for rel in (
            Path("product/src/initializer/core.py"),
            Path("repo/validation/validate_framework.py"),
            Path("repo/validation/requirement-evaluation.json"),
            Path("scripts/validate"),
        ):
            target = source / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / rel, target)

        run_git(source, "add", "-A")
        staged = run_git(source, "diff", "--cached", "--quiet", check=False)
        if staged.returncode == 1:
            run_git(source, "commit", "-m", "Install candidate Build surfaces")
        elif staged.returncode != 0:
            raise AssertionError("could not evaluate independence candidate source changes")

        destination = self.temp / "independence-result"
        revision = initialize_repository(
            source_root=source,
            destination=destination,
            require_accepted=False,
        )
        self.assert_initialized(destination, revision)

        shutil.rmtree(source)
        self.assertFalse(source.exists())

        completed = subprocess.run(
            [str(destination / "scripts/validate")],
            cwd=destination,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertEqual(
            completed.returncode,
            0,
            msg=f"stdout:\n{completed.stdout}\nstderr:\n{completed.stderr}",
        )


if __name__ == "__main__":
    unittest.main()
