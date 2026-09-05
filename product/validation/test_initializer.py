from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
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
    UpgradeError,
    initialize_repository,
    upgrade_repository,
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


    def _initialize_source_revision(
        self,
        source: Path,
        revision: str,
        destination: Path,
    ) -> None:
        worktree = self.temp / f"old-source-{destination.name}"
        run_git(source, "worktree", "add", "--detach", str(worktree), revision)
        try:
            code = (
                "from pathlib import Path; import sys; sys.dont_write_bytecode = True; "
                "sys.path.insert(0, str(Path(sys.argv[1]) / 'product' / 'src')); "
                "from initializer.core import initialize_repository; "
                "initialize_repository(source_root=Path(sys.argv[1]), "
                "destination=Path(sys.argv[2]), require_accepted=False)"
            )
            completed = subprocess.run(
                [sys.executable, "-c", code, str(worktree), str(destination)],
                cwd=worktree,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            self.assertEqual(
                completed.returncode,
                0,
                msg=f"stdout:\n{completed.stdout}\nstderr:\n{completed.stderr}",
            )
        finally:
            run_git(source, "worktree", "remove", "--force", str(worktree), check=False)

    def _make_upgrade_fixture(
        self,
        name: str,
        *,
        add_independent_state: bool = False,
    ) -> tuple[Path, Path, str, str]:
        source = self.temp / f"{name}-source"
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

        fixture_dir = source / "repo" / "src"
        fixture_dir.mkdir(parents=True, exist_ok=True)
        (fixture_dir / "upgrade-fixture-change.txt").write_text(
            "old\n", encoding="utf-8"
        )
        (fixture_dir / "upgrade-fixture-remove.txt").write_text(
            "remove-me\n", encoding="utf-8"
        )
        run_git(source, "add", "-A")
        run_git(source, "commit", "-m", "Create old framework upgrade fixture")
        old_revision = run_git(source, "rev-parse", "HEAD").stdout.strip()

        target = self.temp / f"{name}-target"
        self._initialize_source_revision(source, old_revision, target)

        if add_independent_state:
            run_git(target, "config", "user.name", "target test")
            run_git(target, "config", "user.email", "target-test@local.invalid")
            independent = {
                Path("product/design/DP-900-local-product.md"): "# Local Product\n",
                Path("product/specs/local-notes.md"): "local specification notes\n",
                Path("product/src/app.py"): "VALUE = 'local-product'\n",
                Path("product/validation/local-state.txt"): "local validation state\n",
                Path("user/local-note.txt"): "user-owned\n",
            }
            for rel, content in independent.items():
                path = target / rel
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content, encoding="utf-8")
            run_git(target, "add", "-A")
            run_git(target, "commit", "-m", "Add independent target product state")

        for rel in (
            Path("product/src/initializer/__init__.py"),
            Path("product/src/initializer/cli.py"),
            Path("product/src/initializer/core.py"),
            Path("product/scripts/repo-spec"),
        ):
            dest = source / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / rel, dest)

        (fixture_dir / "upgrade-fixture-change.txt").write_text(
            "new\n", encoding="utf-8"
        )
        (fixture_dir / "upgrade-fixture-remove.txt").unlink()
        (fixture_dir / "upgrade-fixture-add.txt").write_text(
            "added\n", encoding="utf-8"
        )

        run_git(source, "add", "-A")
        run_git(source, "commit", "-m", "Create prospective framework upgrade fixture")
        new_revision = run_git(source, "rev-parse", "HEAD").stdout.strip()
        return source, target, old_revision, new_revision

    def test_upgrade_cli_surface(self) -> None:
        parser = build_parser()
        subparsers = next(
            action for action in parser._actions
            if action.__class__.__name__ == "_SubParsersAction"
        )
        upgrade_parser = subparsers.choices["upgrade"]
        option_actions = [
            action
            for action in upgrade_parser._actions
            if action.option_strings and action.dest != "help"
        ]
        self.assertEqual(len(option_actions), 1)
        self.assertEqual(option_actions[0].option_strings, ["--repo"])
        self.assertTrue(option_actions[0].required)

    def test_upgrade_successful_supported_transition(self) -> None:
        source, target, _, new_revision = self._make_upgrade_fixture(
            "success",
            add_independent_state=True,
        )
        target_head = run_git(target, "rev-parse", "HEAD").stdout.strip()

        observed = upgrade_repository(
            source_root=source,
            target=target,
            require_accepted=False,
        )
        self.assertEqual(observed, new_revision)
        self.assertEqual(
            json.loads(
                (target / FRAMEWORK_SOURCE_RECORD).read_text(encoding="utf-8")
            )["repo_spec_source_revision"],
            new_revision,
        )
        self.assertEqual(run_git(target, "rev-parse", "HEAD").stdout.strip(), target_head)
        self.assertEqual(
            (target / "repo/src/upgrade-fixture-change.txt").read_text(encoding="utf-8"),
            "new\n",
        )
        self.assertTrue((target / "repo/src/upgrade-fixture-add.txt").is_file())
        self.assertFalse((target / "repo/src/upgrade-fixture-remove.txt").exists())
        self.assertNotEqual(
            run_git(
                target,
                "cat-file",
                "-e",
                f"{new_revision}^{{commit}}",
                check=False,
            ).returncode,
            0,
        )

    def test_upgrade_preserves_independent_product_and_user_state(self) -> None:
        source, target, _, _ = self._make_upgrade_fixture(
            "preserve",
            add_independent_state=True,
        )
        expected = {
            Path("product/design/DP-900-local-product.md"): "# Local Product\n",
            Path("product/specs/local-notes.md"): "local specification notes\n",
            Path("product/src/app.py"): "VALUE = 'local-product'\n",
            Path("product/validation/local-state.txt"): "local validation state\n",
            Path("user/local-note.txt"): "user-owned\n",
        }
        upgrade_repository(source_root=source, target=target, require_accepted=False)
        for rel, content in expected.items():
            self.assertEqual((target / rel).read_text(encoding="utf-8"), content)

    def test_upgrade_refuses_local_framework_modification(self) -> None:
        source, target, old_revision, _ = self._make_upgrade_fixture("local-conflict")
        marker = target / "repo/src/upgrade-fixture-change.txt"
        marker.write_text("locally-modified\n", encoding="utf-8")

        with self.assertRaisesRegex(UpgradeError, "local framework modification conflict"):
            upgrade_repository(source_root=source, target=target, require_accepted=False)

        self.assertEqual(marker.read_text(encoding="utf-8"), "locally-modified\n")
        self.assertEqual(
            json.loads(
                (target / FRAMEWORK_SOURCE_RECORD).read_text(encoding="utf-8")
            )["repo_spec_source_revision"],
            old_revision,
        )

    def test_upgrade_refuses_unavailable_installed_revision(self) -> None:
        source, target, _, _ = self._make_upgrade_fixture("unavailable")
        record = target / FRAMEWORK_SOURCE_RECORD
        data = json.loads(record.read_text(encoding="utf-8"))
        data["repo_spec_source_revision"] = "f" * 40
        record.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")

        with self.assertRaisesRegex(UpgradeError, "unavailable for supported reconstruction"):
            upgrade_repository(source_root=source, target=target, require_accepted=False)

    def test_upgrade_validation_failure_leaves_target_unchanged(self) -> None:
        source, target, old_revision, _ = self._make_upgrade_fixture("validation-fail")
        before = (target / "repo/src/upgrade-fixture-change.txt").read_text(
            encoding="utf-8"
        )

        def break_candidate(stage: Path) -> None:
            (stage / "unauthorized-root.txt").write_text("invalid\n", encoding="utf-8")

        with self.assertRaisesRegex(UpgradeError, "Validation failed"):
            upgrade_repository(
                source_root=source,
                target=target,
                require_accepted=False,
                before_validate=break_candidate,
            )

        self.assertEqual(
            (target / "repo/src/upgrade-fixture-change.txt").read_text(encoding="utf-8"),
            before,
        )
        self.assertEqual(
            json.loads(
                (target / FRAMEWORK_SOURCE_RECORD).read_text(encoding="utf-8")
            )["repo_spec_source_revision"],
            old_revision,
        )
        self.assertFalse((target / "unauthorized-root.txt").exists())

    def test_upgrade_preserves_unrelated_failing_product_validation(self) -> None:
        source, target, _, new_revision = self._make_upgrade_fixture(
            "product-failure",
            add_independent_state=True,
        )
        validator = target / PRODUCT_VALIDATOR
        validator.write_text(
            "#!/usr/bin/env python3\n"
            "import sys\n"
            "if '--list-tasks' in sys.argv:\n"
            "    raise SystemExit(0)\n"
            "if '--task' in sys.argv:\n"
            "    raise SystemExit(1)\n"
            "raise SystemExit(1)\n",
            encoding="utf-8",
        )
        validator.chmod(0o755)

        full_before = subprocess.run(
            [str(target / "scripts/validate")],
            cwd=target,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertNotEqual(full_before.returncode, 0)

        upgrade_repository(source_root=source, target=target, require_accepted=False)
        self.assertEqual(
            json.loads(
                (target / FRAMEWORK_SOURCE_RECORD).read_text(encoding="utf-8")
            )["repo_spec_source_revision"],
            new_revision,
        )
        self.assertIn("raise SystemExit(1)", validator.read_text(encoding="utf-8"))

        full_after = subprocess.run(
            [str(target / "scripts/validate")],
            cwd=target,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertNotEqual(full_after.returncode, 0)

    def test_upgrade_incompatible_product_validation_surface_fails(self) -> None:
        source, target, old_revision, _ = self._make_upgrade_fixture("product-conflict")
        entrypoint = target / PRODUCT_VALIDATION_ENTRYPOINT
        entrypoint.write_text("#!/usr/bin/env bash\nexit 0\n", encoding="utf-8")
        entrypoint.chmod(0o755)

        with self.assertRaisesRegex(UpgradeError, "Validation failed"):
            upgrade_repository(source_root=source, target=target, require_accepted=False)

        self.assertEqual(entrypoint.read_text(encoding="utf-8"), "#!/usr/bin/env bash\nexit 0\n")
        self.assertEqual(
            json.loads(
                (target / FRAMEWORK_SOURCE_RECORD).read_text(encoding="utf-8")
            )["repo_spec_source_revision"],
            old_revision,
        )

    def test_upgrade_restores_missing_generic_product_validator(self) -> None:
        source, target, _, _ = self._make_upgrade_fixture("restore-product-validator")
        (target / PRODUCT_VALIDATOR).unlink()

        upgrade_repository(source_root=source, target=target, require_accepted=False)
        self.assertTrue((target / PRODUCT_VALIDATOR).is_file())
        self.assertTrue(os.access(target / PRODUCT_VALIDATOR, os.X_OK))

    def test_upgrade_promotion_failure_restores_target(self) -> None:
        source, target, old_revision, _ = self._make_upgrade_fixture(
            "promotion-fail",
            add_independent_state=True,
        )
        real_replace = os.replace
        target_resolved = target.resolve()
        calls = {"to_target": 0}

        def flaky_replace(src, dst):
            if Path(dst).resolve() == target_resolved:
                calls["to_target"] += 1
                if calls["to_target"] == 1:
                    raise OSError("promotion failure fixture")
            return real_replace(src, dst)

        with mock.patch("initializer.core.os.replace", side_effect=flaky_replace):
            with self.assertRaisesRegex(UpgradeError, "upgrade promotion failed"):
                upgrade_repository(source_root=source, target=target, require_accepted=False)

        self.assertTrue(target.is_dir())
        self.assertEqual(
            json.loads(
                (target / FRAMEWORK_SOURCE_RECORD).read_text(encoding="utf-8")
            )["repo_spec_source_revision"],
            old_revision,
        )
        self.assertEqual(
            (target / "user/local-note.txt").read_text(encoding="utf-8"),
            "user-owned\n",
        )


    def test_upgrade_rejects_older_supplying_revision(self) -> None:
        source, _, old_revision, new_revision = self._make_upgrade_fixture("downgrade")
        newer_target = self.temp / "downgrade-newer-target"
        self._initialize_source_revision(source, new_revision, newer_target)
        worktree = self.temp / "downgrade-old-source"
        run_git(source, "worktree", "add", "--detach", str(worktree), old_revision)
        try:
            with self.assertRaisesRegex(UpgradeError, "not a later descendant"):
                upgrade_repository(source_root=worktree, target=newer_target, require_accepted=False)
        finally:
            run_git(source, "worktree", "remove", "--force", str(worktree), check=False)
        self.assertEqual(
            json.loads((newer_target / FRAMEWORK_SOURCE_RECORD).read_text(encoding="utf-8"))["repo_spec_source_revision"],
            new_revision,
        )

    def test_upgrade_refuses_locally_modified_framework_source_record(self) -> None:
        source, target, old_revision, _ = self._make_upgrade_fixture("source-record-conflict")
        record = target / FRAMEWORK_SOURCE_RECORD
        data = json.loads(record.read_text(encoding="utf-8"))
        data["local_note"] = "intentional"
        record.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        with self.assertRaisesRegex(UpgradeError, "local framework modification conflict: repo/validation/framework-source.json"):
            upgrade_repository(source_root=source, target=target, require_accepted=False)
        observed = json.loads(record.read_text(encoding="utf-8"))
        self.assertEqual(observed["repo_spec_source_revision"], old_revision)
        self.assertEqual(observed["local_note"], "intentional")

    def test_upgrade_refuses_missing_framework_source_record(self) -> None:
        source, target, _, _ = self._make_upgrade_fixture("missing-source-record")
        (target / FRAMEWORK_SOURCE_RECORD).unlink()
        with self.assertRaisesRegex(UpgradeError, "source record is missing"):
            upgrade_repository(source_root=source, target=target, require_accepted=False)

    def test_upgrade_refuses_malformed_framework_source_record(self) -> None:
        source, target, _, _ = self._make_upgrade_fixture("malformed-source-record")
        (target / FRAMEWORK_SOURCE_RECORD).write_text("{bad json\n", encoding="utf-8")
        with self.assertRaisesRegex(UpgradeError, "source record is malformed"):
            upgrade_repository(source_root=source, target=target, require_accepted=False)

    def test_upgrade_cli_success(self) -> None:
        source, target, _, new_revision = self._make_upgrade_fixture("cli-success")
        run_git(source, "branch", "-f", "main", new_revision)
        completed = subprocess.run(
            [str(source / "product/scripts/repo-spec"), "upgrade", "--repo", str(target)],
            cwd=source, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        self.assertEqual(completed.returncode, 0, msg=f"stdout:\n{completed.stdout}\nstderr:\n{completed.stderr}")
        self.assertIn("Upgraded repo-spec repository", completed.stdout)
        self.assertIn(new_revision, completed.stdout)

    def test_upgrade_cli_failure_reports_error(self) -> None:
        source, target, _, new_revision = self._make_upgrade_fixture("cli-failure")
        run_git(source, "branch", "-f", "main", new_revision)
        (target / FRAMEWORK_SOURCE_RECORD).unlink()
        completed = subprocess.run(
            [str(source / "product/scripts/repo-spec"), "upgrade", "--repo", str(target)],
            cwd=source, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("repo-spec upgrade:", completed.stderr)
        self.assertIn("source record is missing", completed.stderr)


    def test_upgrade_refuses_non_object_framework_source_record(self) -> None:
        source, target, _, _ = self._make_upgrade_fixture("non-object-source-record")
        (target / FRAMEWORK_SOURCE_RECORD).write_text("[]\n", encoding="utf-8")

        with self.assertRaisesRegex(
            UpgradeError,
            "source record is malformed: expected JSON object",
        ):
            upgrade_repository(
                source_root=source,
                target=target,
                require_accepted=False,
            )

    def test_upgrade_cli_contains_supplier_verification_failure(self) -> None:
        source, target, _, _ = self._make_upgrade_fixture("cli-source-failure")
        run_git(source, "branch", "-f", "main", "HEAD")
        dirty = source / "repo" / "src" / "cli-source-failure.txt"
        dirty.write_text("dirty\n", encoding="utf-8")

        completed = subprocess.run(
            [
                str(source / "product/scripts/repo-spec"),
                "upgrade",
                "--repo",
                str(target),
            ],
            cwd=source,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("repo-spec upgrade:", completed.stderr)
        self.assertIn("supplying maintained framework material is dirty", completed.stderr)
        self.assertNotIn("Traceback", completed.stderr)


if __name__ == "__main__":
    unittest.main()
