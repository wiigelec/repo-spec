from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from validation.checks.specifications import (
    check_validation_correspondence_integrity_phase,
)
from validation.core.context import (
    RepositoryValidationContext,
    ValidationContext,
    load_repo_specs,
)
from validation.core.errors import ValidationFailure
from validation.core.schema_subset import load_repo_schemas


class ValidationCorrespondenceIntegrityTests(unittest.TestCase):
    # validation-metadata: {"role": "helper"}
    @classmethod
    def setUpClass(cls) -> None:
        cls.repo_root = Path(__file__).resolve().parents[4]
        manifest, specs, source_paths, actual_paths = load_repo_specs(cls.repo_root)
        schemas = load_repo_schemas(cls.repo_root)
        cls.repository = RepositoryValidationContext(
            manifest,
            specs,
            source_paths,
            actual_paths,
            schemas,
        )

    # validation-metadata: {"role": "helper"}
    def fixture_context(self) -> tuple[tempfile.TemporaryDirectory[str], ValidationContext]:
        temp = tempfile.TemporaryDirectory()
        root = Path(temp.name)
        shutil.copytree(self.repo_root / "validation", root / "validation")
        shutil.copytree(self.repo_root / "repo/validation", root / "repo/validation")
        context = ValidationContext(root, self.repository, None, None)
        return temp, context

    # validation-metadata: {"role": "helper"}
    def assert_fixture_invalid(self, mutator) -> None:
        temp, context = self.fixture_context()
        try:
            mutator(context.repo_root)
            with self.assertRaises(ValidationFailure):
                check_validation_correspondence_integrity_phase(context)
        finally:
            temp.cleanup()

    # validation-metadata: {"role": "helper"}
    def test_current_repository_correspondence_is_valid(self) -> None:
        context = ValidationContext(self.repo_root, self.repository, None, None)
        check_validation_correspondence_integrity_phase(context)

    # validation-metadata: {"role": "helper"}
    def test_missing_active_package_fails_closed(self) -> None:
        # validation-metadata: {"role": "helper"}
        # validation-metadata: {"role": "helper"}
        def mutate(root: Path) -> None:
            (
                root
                / "repo/validation/packages/repo.validation-correspondence/REPO-VC-012.json"
            ).unlink()

        self.assert_fixture_invalid(mutate)

    # validation-metadata: {"role": "helper"}
    def test_package_path_binding_mismatch_fails_closed(self) -> None:
        # validation-metadata: {"role": "helper"}
        # validation-metadata: {"role": "helper"}
        def mutate(root: Path) -> None:
            path = (
                root
                / "repo/validation/packages/repo.validation-correspondence/REPO-VC-012.json"
            )
            package = json.loads(path.read_text(encoding="utf-8"))
            package["normative_reference"]["requirement_id"] = "REPO-VC-011"
            path.write_text(
                json.dumps(package, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )

        self.assert_fixture_invalid(mutate)

    # validation-metadata: {"role": "helper"}
    def test_duplicate_task_ownership_fails_closed(self) -> None:
        # validation-metadata: {"role": "helper"}
        # validation-metadata: {"role": "helper"}
        def mutate(root: Path) -> None:
            source_path = root / "repo/validation/packages/repo.validation/REPO-VAL-001.json"
            target_path = root / "repo/validation/packages/repo.validation/REPO-VAL-043.json"
            source = json.loads(source_path.read_text(encoding="utf-8"))
            target = json.loads(target_path.read_text(encoding="utf-8"))
            self.assertTrue(source["tasks"])
            target["tasks"].append(source["tasks"][0])
            target_path.write_text(
                json.dumps(target, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )

        self.assert_fixture_invalid(mutate)

    # validation-metadata: {"role": "helper"}
    def test_package_source_disagreement_fails_closed(self) -> None:
        # validation-metadata: {"role": "helper"}
        # validation-metadata: {"role": "helper"}
        def mutate(root: Path) -> None:
            path = root / "repo/validation/packages/repo.validation/REPO-VAL-043.json"
            package = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(len(package["tasks"]), 1)
            package["tasks"][0]["callable"] = "not_the_source_callable"
            path.write_text(
                json.dumps(package, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )

        self.assert_fixture_invalid(mutate)

    # validation-metadata: {"role": "helper"}
    def test_source_task_without_package_ownership_fails_closed(self) -> None:
        # validation-metadata: {"role": "helper"}
        # validation-metadata: {"role": "helper"}
        def mutate(root: Path) -> None:
            path = root / "repo/validation/packages/repo.validation/REPO-VAL-043.json"
            package = json.loads(path.read_text(encoding="utf-8"))
            package["tasks"] = []
            path.write_text(
                json.dumps(package, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )

        self.assert_fixture_invalid(mutate)


if __name__ == "__main__":
    unittest.main()
