from __future__ import annotations

import json
import unittest

from initializer.validation import validate_and_normalize


def request(destination: str = "output") -> dict[str, object]:
    return {
        "schema_version": "2",
        "destination": destination,
    }


class ImmutableRequestTests(unittest.TestCase):
    def test_validated_model_is_minimal_v2(self) -> None:
        model = validate_and_normalize(request(), "/work").request
        self.assertEqual(model.schema_version, "2")
        self.assertEqual(model.destination, "/work/output")
        self.assertEqual(model.repository_name, "output")

    def test_repository_name_is_derived_not_authoritative_input(self) -> None:
        model = validate_and_normalize(request("/work/repos/example"), "/work").request
        self.assertEqual(model.repository_name, "example")
        canonical = json.loads(model.canonical_request_bytes.decode("utf-8"))
        self.assertNotIn("repository_name", canonical)

    def test_canonical_bytes_are_deterministic(self) -> None:
        left = validate_and_normalize(request("./out"), "/work").request
        right = validate_and_normalize(request("/work/out"), "/work").request
        self.assertEqual(left.canonical_request_bytes, right.canonical_request_bytes)
        self.assertEqual(left.request_fingerprint, right.request_fingerprint)

    def test_model_is_immutable(self) -> None:
        model = validate_and_normalize(request(), "/work").request
        with self.assertRaises(AttributeError):
            model._destination = "/other"

    def test_removed_v1_fields_are_absent(self) -> None:
        model = validate_and_normalize(request(), "/work").request
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
