from __future__ import annotations

import unittest

from initializer.models import GitObjectIdentity
from initializer.validation import validate_and_normalize


OBJECT_ID = "0123456789abcdef0123456789abcdef01234567"


def request() -> dict[str, object]:
    return {
        "schema_version": "1",
        "destination": "output",
        "authority": {
            "granted_by": "issue-273",
            "type": "governing-issue",
            "scope": "Patch 1",
        },
        "source": {
            "repository": "source",
            "revision": {"object_format": "sha1", "object_id": OBJECT_ID},
        },
        "product": {
            "id": "sample-product",
            "direction_material": ["docs/OVERVIEW.md", "docs/OVERVIEW.md"],
        },
        "profile": "standard",
    }


class ImmutableRequestTests(unittest.TestCase):
    def test_validated_model_preserves_authority_identity_and_duplicates(self) -> None:
        model = validate_and_normalize(request(), "/work").request

        self.assertEqual(model.destination, "/work/output")
        self.assertEqual(model.source_repository, "/work/source")
        self.assertEqual(
            model.authority,
            {
                "granted_by": "issue-273",
                "type": "governing-issue",
                "scope": "Patch 1",
            },
        )
        self.assertEqual(model.product_id, "sample-product")
        self.assertEqual(
            model.product_direction_material,
            ("docs/OVERVIEW.md", "docs/OVERVIEW.md"),
        )

    def test_source_revision_is_structured_sha1_identity(self) -> None:
        revision = validate_and_normalize(request(), "/work").request.source_revision

        self.assertIsInstance(revision, GitObjectIdentity)
        self.assertEqual(revision.object_format, "sha1")
        self.assertEqual(revision.object_id, OBJECT_ID)
        self.assertEqual(
            revision.to_dict(), {"object_format": "sha1", "object_id": OBJECT_ID}
        )

    def test_model_is_immutable_and_returns_authority_copy(self) -> None:
        model = validate_and_normalize(request(), "/work").request
        authority = model.authority
        authority["granted_by"] = "other"

        self.assertEqual(model.authority["granted_by"], "issue-273")
        with self.assertRaises(AttributeError):
            model._destination = "/other"
        with self.assertRaises(AttributeError):
            model.source_revision._object_id = "0" * 40

    def test_fingerprint_and_canonical_bytes_are_stable_model_values(self) -> None:
        first = validate_and_normalize(request(), "/work").request
        second = validate_and_normalize(request(), "/work").request

        self.assertEqual(first, second)
        self.assertEqual(hash(first), hash(second))
        self.assertIsInstance(first.canonical_request_bytes, bytes)
        self.assertRegex(first.request_fingerprint, r"^[0-9a-f]{64}$")


if __name__ == "__main__":
    unittest.main()
