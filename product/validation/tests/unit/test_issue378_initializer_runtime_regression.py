from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class Issue378InitializerRuntimeRegressionTests(unittest.TestCase):
    def test_initializer_validation_imports(self) -> None:
        repo_root = Path(__file__).resolve().parents[4]
        env = os.environ.copy()
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        env["PYTHONPATH"] = str(repo_root / "product/src")
        proc = subprocess.run(
            [sys.executable, "-c", "import initializer.validation"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            env=env,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)

    @unittest.skip("deferred: initializer materialization must be updated in the follow-up after validation migrations are proven")
    def test_clean_framework_init_promotes_and_installed_validation_passes(self) -> None:
        repo_root = Path(__file__).resolve().parents[4]
        with tempfile.TemporaryDirectory(prefix="repo-spec-issue378-regression-") as directory:
            temp_root = Path(directory)
            clean_framework = temp_root / "framework"
            destination = temp_root / "generated-repo"

            clone = subprocess.run(
                [
                    "git",
                    "clone",
                    "--quiet",
                    "--no-hardlinks",
                    str(repo_root),
                    str(clean_framework),
                ],
                capture_output=True,
                text=True,
            )
            self.assertEqual(clone.returncode, 0, clone.stderr)

            status = subprocess.run(
                ["git", "status", "--porcelain=v1"],
                cwd=clean_framework,
                capture_output=True,
                text=True,
            )
            self.assertEqual(status.returncode, 0, status.stderr)
            self.assertEqual(status.stdout, "")

            env = os.environ.copy()
            env.pop("PYTHONPATH", None)
            env.pop("PYTHONHOME", None)
            env["PYTHONDONTWRITEBYTECODE"] = "1"

            init = subprocess.run(
                [
                    str(clean_framework / "product/scripts/repo-spec"),
                    "init",
                    "--repo",
                    str(destination),
                ],
                cwd=clean_framework,
                capture_output=True,
                text=True,
                env=env,
            )
            self.assertEqual(init.returncode, 0, init.stderr)
            self.assertTrue(destination.is_dir())
            self.assertIn("Destination was promoted successfully.", init.stderr)

            installed_validation = subprocess.run(
                [str(destination / "scripts/validate")],
                cwd=destination,
                capture_output=True,
                text=True,
                env=env,
            )
            self.assertEqual(
                installed_validation.returncode,
                0,
                installed_validation.stderr,
            )


if __name__ == "__main__":
    unittest.main()
