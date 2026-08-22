from __future__ import annotations

import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
SCHEMA_PATH = ROOT / "product/schemas/product/product-spec-base.schema.json"


class ProductSpecRequirementIdSchemaTests(unittest.TestCase):
    # validation-metadata: {"role": "helper"}
    @classmethod
    def setUpClass(cls) -> None:
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        requirement_id_schema = schema["$defs"]["requirementId"]

        cls.assertions = {
            "type": requirement_id_schema.get("type"),
            "pattern": requirement_id_schema.get("pattern"),
        }
        cls.pattern = re.compile(requirement_id_schema["pattern"])

    # validation-metadata: {"role": "helper"}
    def assert_valid(self, value: str) -> None:
        self.assertIsNotNone(
            self.pattern.fullmatch(value),
            msg=f"{value!r} unexpectedly invalid for {self.assertions['pattern']!r}",
        )

    # validation-metadata: {"role": "helper"}
    def assert_invalid(self, value: str) -> None:
        self.assertIsNone(
            self.pattern.fullmatch(value),
            msg=f"{value!r} unexpectedly valid for {self.assertions['pattern']!r}",
        )

    # validation-metadata: {"role": "helper"}
    def test_requirement_id_schema_remains_string_pattern(self) -> None:
        self.assertEqual(self.assertions["type"], "string")
        self.assertIsInstance(self.assertions["pattern"], str)
        self.assertTrue(self.assertions["pattern"])

    # validation-metadata: {"role": "helper"}
    def test_standard_numeric_requirement_id_remains_valid(self) -> None:
        self.assert_valid("INIT-RPT-004")

    # validation-metadata: {"role": "helper"}
    def test_accepted_suffix_letter_requirement_ids_are_valid(self) -> None:
        self.assert_valid("INIT-RPT-004a")
        self.assert_valid("INIT-RPT-004b")

    # validation-metadata: {"role": "helper"}
    def test_malformed_requirement_ids_remain_invalid(self) -> None:
        for value in (
            "",
            " ",
            "INIT RPT-004",
            "INIT/RPT-004",
            "../INIT-RPT-004",
            "init-rpt-004",
            "INIT-RPT",
            "INIT-RPT-a",
            "INIT-RPT-004ab",
            "INIT-RPT-004A",
        ):
            with self.subTest(value=value):
                self.assert_invalid(value)


if __name__ == "__main__":
    unittest.main()
