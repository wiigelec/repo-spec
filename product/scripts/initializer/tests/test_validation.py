from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

# Allow importing from repo/scripts/
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from initializer.validation import (
    validate_request,
    validate_and_normalize,
    load_request,
    ValidationError,
)


FIXTURES = Path(__file__).resolve().parent / "fixtures"


class ValidationTests(unittest.TestCase):
    def _assert_valid(self, fixture_name: str) -> None:
        path = FIXTURES / fixture_name
        raw = load_request(path)
        result = validate_request(raw)
        self.assertTrue(result.is_valid, msg=f"{fixture_name}: {[str(e) for e in result.errors]}")

    def _assert_invalid(self, fixture_name: str) -> None:
        path = FIXTURES / fixture_name
        raw = load_request(path)
        result = validate_request(raw)
        self.assertFalse(result.is_valid, msg=f"{fixture_name}: expected errors but got none")

    def _assert_normalizes(self, fixture_name: str) -> None:
        path = FIXTURES / fixture_name
        raw = load_request(path)
        ctx = validate_and_normalize(raw)
        self.assertIsNotNone(ctx)

    def test_valid_minimal(self) -> None:
        self._assert_valid("valid-minimal.json")
        self._assert_normalizes("valid-minimal.json")

    def test_valid_with_source(self) -> None:
        self._assert_valid("valid-with-source.json")
        self._assert_normalizes("valid-with-source.json")

    def test_valid_with_product(self) -> None:
        self._assert_valid("valid-with-product.json")
        self._assert_normalizes("valid-with-product.json")

    def test_valid_full(self) -> None:
        self._assert_valid("valid-full.json")
        self._assert_normalizes("valid-full.json")

    def test_valid_with_deferred(self) -> None:
        self._assert_valid("valid-with-deferred.json")
        self._assert_normalizes("valid-with-deferred.json")

    def test_invalid_not_json(self) -> None:
        path = FIXTURES / "invalid-not-json.json"
        with self.assertRaises(ValidationError):
            load_request(path)

    def test_invalid_unsupported_version(self) -> None:
        self._assert_invalid("invalid-unsupported-version.json")

    def test_invalid_missing_destination(self) -> None:
        self._assert_invalid("invalid-missing-destination.json")

    def test_invalid_empty_destination(self) -> None:
        self._assert_invalid("invalid-empty-destination.json")

    def test_invalid_missing_authority(self) -> None:
        self._assert_invalid("invalid-missing-authority.json")

    def test_invalid_contradictory_authority(self) -> None:
        self._assert_invalid("invalid-contradictory-authority.json")

    def test_invalid_contradictory_source(self) -> None:
        self._assert_invalid("invalid-contradictory-source.json")

    def test_invalid_unsupported_profile(self) -> None:
        self._assert_invalid("invalid-unsupported-profile.json")

    def test_invalid_unknown_field(self) -> None:
        self._assert_invalid("invalid-unknown-field.json")

    def test_invalid_wrong_type_source(self) -> None:
        self._assert_invalid("invalid-wrong-type-source.json")

    def test_invalid_deferred_required(self) -> None:
        self._assert_invalid("invalid-deferred-required.json")

    def test_invalid_deferred_unknown(self) -> None:
        self._assert_invalid("invalid-deferred-unknown.json")

    def test_invalid_direction_material_type(self) -> None:
        self._assert_invalid("invalid-direction-material-type.json")


class DeterminismTests(unittest.TestCase):
    def test_equivalent_inputs_equal_contexts(self) -> None:
        a = validate_and_normalize({
            "schema_version": "1",
            "destination": "/tmp/dest",
            "authority": {"granted_by": "issue-189"},
            "source": {"repository": "https://github.com/owner/repo", "revision": "abc"},
        })
        b = validate_and_normalize({
            "schema_version": "1",
            "destination": "/tmp/dest",
            "authority": {"granted_by": "issue-189"},
            "source": {"repository": "https://github.com/owner/repo", "revision": "abc"},
        })
        self.assertEqual(a, b)


class SafetyTests(unittest.TestCase):
    def test_validation_does_not_create_destination(self) -> None:
        dest = Path("/tmp/__repo_spec_init_test_should_not_exist__")
        self.assertFalse(dest.exists())
        validate_and_normalize({
            "schema_version": "1",
            "destination": str(dest),
            "authority": {"granted_by": "issue-189"},
        })
        self.assertFalse(dest.exists())

    def test_failure_does_not_produce_context(self) -> None:
        with self.assertRaises(ValidationError):
            validate_and_normalize({
                "schema_version": "1",
                "destination": "/tmp/dest",
            })


if __name__ == "__main__":
    unittest.main()
