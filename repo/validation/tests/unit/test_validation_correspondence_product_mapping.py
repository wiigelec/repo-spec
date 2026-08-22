from __future__ import annotations

import unittest

from validation.core.errors import ValidationFailure
from validation.core.invariants import (
    check_product_test_mapping_validation_package_refs,
    enumerate_product_validation_package_obligations,
)


class ProductValidationCorrespondenceTests(unittest.TestCase):
    # validation-metadata: {"role": "helper"}
    def test_product_test_mapping_accepts_canonical_package_refs(self) -> None:
        mapping = {
            "test_id": "unit-1",
            "paths": ["product/tests/test_example.py"],
            "validation_package_refs": [
                {
                    "spec_id": "example.product",
                    "requirement_id": "EXAMPLE-001",
                }
            ],
        }
        check_product_test_mapping_validation_package_refs(mapping, "mapping")

    # validation-metadata: {"role": "helper"}
    def test_product_test_mapping_rejects_missing_package_refs(self) -> None:
        with self.assertRaises(ValidationFailure):
            check_product_test_mapping_validation_package_refs(
                {
                    "test_id": "unit-1",
                    "paths": ["product/tests/test_example.py"],
                },
                "mapping",
            )

    # validation-metadata: {"role": "helper"}
    def test_product_test_mapping_rejects_noncanonical_ref_shape(self) -> None:
        mapping = {
            "test_id": "unit-1",
            "paths": ["product/tests/test_example.py"],
            "validation_package_refs": [
                {
                    "spec_id": "example.product",
                    "requirement_id": "EXAMPLE-001",
                    "package_path": (
                        "product/validation/packages/example.product/EXAMPLE-001.json"
                    ),
                }
            ],
        }
        with self.assertRaises(ValidationFailure):
            check_product_test_mapping_validation_package_refs(mapping, "mapping")

    # validation-metadata: {"role": "helper"}
    def test_product_test_mapping_rejects_independent_requirement_registry(self) -> None:
        mapping = {
            "test_id": "unit-1",
            "paths": ["product/tests/test_example.py"],
            "requirements": ["EXAMPLE-001"],
            "validation_package_refs": [
                {
                    "spec_id": "example.product",
                    "requirement_id": "EXAMPLE-001",
                }
            ],
        }
        with self.assertRaises(ValidationFailure):
            check_product_test_mapping_validation_package_refs(mapping, "mapping")

    # validation-metadata: {"role": "helper"}
    def test_product_obligation_enumeration_is_deterministic(self) -> None:
        specs = {
            "example.b": {
                "status": "accepted",
                "normative_requirements": [
                    {"id": "B-002", "text": "second"},
                    {"id": "B-001", "text": "first"},
                ],
            },
            "example.a": {
                "status": "accepted",
                "normative_requirements": [
                    {"id": "A-001", "text": "first"},
                ],
            },
            "example.candidate": {
                "status": "candidate",
                "normative_requirements": [
                    {"id": "C-001", "text": "candidate"},
                ],
            },
        }

        self.assertEqual(
            enumerate_product_validation_package_obligations(specs),
            [
                {
                    "spec_id": "example.a",
                    "requirement_id": "A-001",
                    "canonical_package_path": (
                        "product/validation/packages/example.a/A-001.json"
                    ),
                },
                {
                    "spec_id": "example.b",
                    "requirement_id": "B-002",
                    "canonical_package_path": (
                        "product/validation/packages/example.b/B-002.json"
                    ),
                },
                {
                    "spec_id": "example.b",
                    "requirement_id": "B-001",
                    "canonical_package_path": (
                        "product/validation/packages/example.b/B-001.json"
                    ),
                },
            ],
        )


if __name__ == "__main__":
    unittest.main()
