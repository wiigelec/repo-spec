from __future__ import annotations

import json
import unittest

from initializer.validation import (
    EXCLUDED_BEHAVIOR,
    INVALID_STRUCTURE,
    MISSING_REQUIRED,
    validate_and_normalize,
    validate_request,
)


def valid_request(destination: str = "output") -> dict[str, object]:
    return {
        "schema_version": "2",
        "destination": destination,
    }


class ValidationTests(unittest.TestCase):
    def test_accepts_minimal_v2_request(self) -> None:
        result = validate_request(valid_request(), "/work")
        self.assertEqual(result.errors, [])

    def test_normalizes_destination_against_explicit_cwd(self) -> None:
        ctx = validate_and_normalize(valid_request("nested/../out"), "/work")
        self.assertEqual(ctx.request.schema_version, "2")
        self.assertEqual(ctx.request.destination, "/work/out")
        self.assertEqual(ctx.request.repository_name, "out")

    def test_canonical_request_contains_only_v2_fields(self) -> None:
        model = validate_and_normalize(valid_request("./out"), "/work").request
        raw = json.loads(model.canonical_request_bytes.decode("utf-8"))
        self.assertEqual(raw, {"schema_version": "2", "destination": "/work/out"})
        self.assertEqual(len(model.request_fingerprint), 64)

    def test_destination_is_required(self) -> None:
        raw = valid_request()
        del raw["destination"]
        result = validate_request(raw, "/work")
        self.assertIn(MISSING_REQUIRED, [e.category for e in result.errors])

    def test_schema_version_is_required(self) -> None:
        raw = valid_request()
        del raw["schema_version"]
        result = validate_request(raw, "/work")
        self.assertIn(MISSING_REQUIRED, [e.category for e in result.errors])

    def test_only_schema_version_2_is_supported(self) -> None:
        raw = valid_request()
        raw["schema_version"] = "1"
        result = validate_request(raw, "/work")
        self.assertTrue(result.errors)

    def test_unknown_root_field_is_rejected(self) -> None:
        raw = valid_request()
        raw["metadata"] = {}
        result = validate_request(raw, "/work")
        self.assertIn(INVALID_STRUCTURE, [e.category for e in result.errors])

    def test_legacy_authority_source_product_and_profile_are_rejected(self) -> None:
        legacy_fields = {
            "authority": {"granted_by": "issue-1"},
            "source": {"repository": "/tmp/source"},
            "product": {"id": "sample"},
            "profile": "standard",
        }
        for name, value in legacy_fields.items():
            with self.subTest(field=name):
                raw = valid_request()
                raw[name] = value
                result = validate_request(raw, "/work")
                categories = [e.category for e in result.errors]
                self.assertTrue(
                    INVALID_STRUCTURE in categories or EXCLUDED_BEHAVIOR in categories,
                    categories,
                )

    def test_destination_must_be_local_path_input(self) -> None:
        for value in ("https://example.invalid/repo", "git@example.invalid:repo.git"):
            with self.subTest(value=value):
                raw = valid_request(value)
                result = validate_request(raw, "/work")
                self.assertTrue(result.errors)

    def test_repository_name_is_mechanical_basename(self) -> None:
        model = validate_and_normalize(valid_request("/tmp/my-repo"), "/work").request
        self.assertEqual(model.repository_name, "my-repo")

    def test_model_does_not_expose_v1_authority_or_product_fields(self) -> None:
        model = validate_and_normalize(valid_request(), "/work").request
        for name in (
            "authority",
            "source_repository",
            "source_revision",
            "product_id",
            "product_direction_material",
            "profile",
        ):
            self.assertFalse(hasattr(model, name), name)


if __name__ == "__main__":
    unittest.main()
