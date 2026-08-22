from __future__ import annotations

import unittest
from pathlib import Path

from validation.core.errors import ValidationFailure
from validation.core.schema_subset import load_repo_schemas, validate_instance


class ValidationCorrespondencePackageSchemaTests(unittest.TestCase):
    # validation-metadata: {"role": "helper"}
    @classmethod
    def setUpClass(cls) -> None:
        cls.repo_root = Path(__file__).resolve().parents[4]
        cls.schema = load_repo_schemas(cls.repo_root)["validation-correspondence-package"]

    # validation-metadata: {"role": "helper"}
    def assert_valid(self, instance: object) -> None:
        validate_instance(
            instance,
            self.schema,
            "validation-correspondence-package fixture",
            self.schema,
        )

    # validation-metadata: {"role": "helper"}
    def assert_invalid(self, instance: object) -> None:
        with self.assertRaises(ValidationFailure):
            self.assert_valid(instance)

    # validation-metadata: {"role": "helper"}
    def test_mechanical_package_may_have_zero_tasks_without_rationale(self) -> None:
        self.assert_valid(
            {
                "normative_reference": {
                    "spec_id": "repo.validation-correspondence",
                    "requirement_id": "REPO-VC-012",
                },
                "validation_disposition": "mechanical",
                "tasks": [],
            }
        )

    # validation-metadata: {"role": "helper"}
    def test_partial_package_accepts_task_traceability_metadata(self) -> None:
        self.assert_valid(
            {
                "normative_reference": {
                    "spec_id": "repo.validation",
                    "requirement_id": "REPO-VAL-043",
                },
                "validation_disposition": "partial",
                "validation_rationale": "Mechanical checks cover objective correspondence only.",
                "tasks": [
                    {
                        "task_id": "repo-val-043-negative-001",
                        "source": "repo/validation/checks/specifications.py",
                        "callable": "validate_validation_correspondence",
                        "coverage_intent": ["negative", "boundary"],
                        "execution_level": "unit",
                    }
                ],
            }
        )

    # validation-metadata: {"role": "helper"}
    def test_non_mechanical_disposition_requires_rationale(self) -> None:
        self.assert_invalid(
            {
                "normative_reference": {
                    "spec_id": "repo.authority-model",
                    "requirement_id": "REPO-AUTH-005",
                },
                "validation_disposition": "semantic-review",
                "tasks": [],
            }
        )

    # validation-metadata: {"role": "helper"}
    def test_bare_requirement_identity_is_rejected(self) -> None:
        self.assert_invalid(
            {
                "requirement_id": "REPO-VC-012",
                "validation_disposition": "mechanical",
                "tasks": [],
            }
        )

    # validation-metadata: {"role": "helper"}
    def test_unknown_package_field_is_rejected(self) -> None:
        self.assert_invalid(
            {
                "normative_reference": {
                    "spec_id": "repo.validation-correspondence",
                    "requirement_id": "REPO-VC-012",
                },
                "validation_disposition": "mechanical",
                "tasks": [],
                "requirement_text": "must not be copied into correspondence packages",
            }
        )

    # validation-metadata: {"role": "helper"}
    def test_task_source_must_be_repository_relative(self) -> None:
        self.assert_invalid(
            {
                "normative_reference": {
                    "spec_id": "repo.validation",
                    "requirement_id": "REPO-VAL-043",
                },
                "validation_disposition": "mechanical",
                "tasks": [
                    {
                        "task_id": "repo-val-043-negative-001",
                        "source": "/tmp/validator.py",
                        "callable": "validate_validation_correspondence",
                    }
                ],
            }
        )

    # validation-metadata: {"role": "helper"}
    def test_task_classification_vocabularies_are_closed(self) -> None:
        self.assert_invalid(
            {
                "normative_reference": {
                    "spec_id": "repo.validation",
                    "requirement_id": "REPO-VAL-043",
                },
                "validation_disposition": "mechanical",
                "tasks": [
                    {
                        "task_id": "repo-val-043-negative-001",
                        "source": "repo/validation/checks/specifications.py",
                        "callable": "validate_validation_correspondence",
                        "coverage_intent": ["smoke"],
                    }
                ],
            }
        )

    # validation-metadata: {"role": "helper"}
    def test_task_unknown_field_is_rejected(self) -> None:
        self.assert_invalid(
            {
                "normative_reference": {
                    "spec_id": "repo.validation",
                    "requirement_id": "REPO-VAL-043",
                },
                "validation_disposition": "mechanical",
                "tasks": [
                    {
                        "task_id": "repo-val-043-negative-001",
                        "source": "repo/validation/checks/specifications.py",
                        "callable": "validate_validation_correspondence",
                        "normative_requirement_id": "REPO-VAL-043",
                    }
                ],
            }
        )


if __name__ == "__main__":
    unittest.main()
