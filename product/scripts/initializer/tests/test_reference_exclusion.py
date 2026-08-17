from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path


class ReferenceExclusionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.repo_root = Path(__file__).resolve().parents[4]

    def test_reference_is_source_only_and_absent_from_install_contract(self) -> None:
        source_reference = self.repo_root / "reference"
        self.assertTrue(source_reference.is_dir(), "source repo-spec reference/ tree must remain")

        framework_path = (
            self.repo_root
            / "product"
            / "scripts"
            / "initializer"
            / "framework-inventory.json"
        )
        output_path = (
            self.repo_root
            / "product"
            / "specs"
            / "product"
            / "level-1"
            / "initializer-output-inventory-v1.json"
        )

        framework = json.loads(framework_path.read_text(encoding="utf-8"))
        output = json.loads(output_path.read_text(encoding="utf-8"))

        self.assertFalse(
            any(
                entry.get("source_path", "").startswith("reference/")
                for entry in framework["entries"]
            )
        )
        self.assertFalse(
            any(
                entry.get("destination_path", "").startswith("reference/")
                for entry in output["material_index"]
            )
        )

        framework_keys = [entry["material_key"] for entry in framework["entries"]]
        output_framework = [
            entry
            for entry in output["material_index"]
            if entry.get("producer") == "framework-installation"
        ]
        output_keys = [entry["material_key"] for entry in output_framework]

        self.assertEqual(len(framework_keys), len(set(framework_keys)))
        self.assertEqual(len(output_keys), len(set(output_keys)))
        self.assertEqual(set(framework_keys), set(output_keys))

    def test_clean_init_validates_without_reference_and_rejects_reintroduced_reference(self) -> None:
        with tempfile.TemporaryDirectory(prefix="repo-spec-reference-exclusion-") as temp:
            temp_root = Path(temp)
            source_root = temp_root / "source"
            source_root.mkdir()

            archive = subprocess.run(
                ["git", "archive", "HEAD"],
                cwd=self.repo_root,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            self.assertEqual(
                archive.returncode,
                0,
                msg=f"git archive failed\nstderr:\n{archive.stderr.decode(errors='replace')}",
            )

            extract = subprocess.run(
                ["tar", "-x", "-C", str(source_root)],
                input=archive.stdout,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            self.assertEqual(
                extract.returncode,
                0,
                msg=f"archive extraction failed\nstderr:\n{extract.stderr.decode(errors='replace')}",
            )

            candidate_validator = (
                self.repo_root / "repo" / "scripts" / "validation" / "repository_checks.py"
            )
            fixture_validator = (
                source_root / "repo" / "scripts" / "validation" / "repository_checks.py"
            )
            fixture_validator.write_bytes(candidate_validator.read_bytes())
            candidate_root_validation = self.repo_root / "repo" / "scripts" / "root_validation.py"
            fixture_root_validation = source_root / "repo" / "scripts" / "root_validation.py"
            fixture_root_validation.write_bytes(candidate_root_validation.read_bytes())

            subprocess.run(["git", "init", "-q"], cwd=source_root, check=True)
            subprocess.run(
                ["git", "config", "user.email", "test@example.invalid"],
                cwd=source_root,
                check=True,
            )
            subprocess.run(
                ["git", "config", "user.name", "repo-spec test"],
                cwd=source_root,
                check=True,
            )
            subprocess.run(["git", "add", "-A"], cwd=source_root, check=True)
            subprocess.run(
                ["git", "commit", "-q", "-m", "test source"],
                cwd=source_root,
                check=True,
            )

            destination_parent = temp_root / "destination"
            destination_parent.mkdir()
            repo_name = "reference-exclusion-init"
            repo_spec = source_root / "product" / "scripts" / "repo-spec"

            init = subprocess.run(
                [str(repo_spec), "init", "--repo", repo_name],
                cwd=destination_parent,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            self.assertEqual(
                init.returncode,
                0,
                msg=f"clean init failed\nstdout:\n{init.stdout}\nstderr:\n{init.stderr}",
            )

            destination = destination_parent / repo_name
            self.assertFalse(
                (destination / "reference").exists(),
                "initialized repository must not contain top-level reference/",
            )
            self.assertTrue(
                (destination / "repo" / "initializer" / "provenance.json").is_file(),
                "initialized repository provenance marker missing",
            )

            validate = destination / "scripts" / "validate"
            result = subprocess.run(
                [str(validate)],
                cwd=destination,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            self.assertEqual(
                result.returncode,
                0,
                msg=(
                    "initialized repository validation failed\n"
                    f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
                ),
            )

            (destination / "reference").mkdir()
            bad = subprocess.run(
                [str(validate)],
                cwd=destination,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            self.assertNotEqual(
                bad.returncode,
                0,
                "initialized repository validation must reject top-level reference/",
            )
            self.assertIn(
                "undeclared top-level entries: reference",
                bad.stderr,
            )


if __name__ == "__main__":
    unittest.main()
