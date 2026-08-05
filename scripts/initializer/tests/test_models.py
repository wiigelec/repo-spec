from __future__ import annotations

import unittest

from initializer.models import ImmutableRequest


class ImmutableRequestTests(unittest.TestCase):
    def test_minimal_request(self) -> None:
        req = ImmutableRequest({
            "schema_version": "1",
            "destination": "/tmp/dest",
            "authority": {"granted_by": "issue-189"},
        })
        self.assertEqual(req.schema_version, "1")
        self.assertEqual(req.destination, "/tmp/dest")
        self.assertEqual(req.authority, {"granted_by": "issue-189"})
        self.assertIsNone(req.source_repository)
        self.assertIsNone(req.source_revision)
        self.assertIsNone(req.profile)
        self.assertIsNone(req.product_id)
        self.assertIsNone(req.product_direction_material)
        self.assertIsNone(req.deferred)
        self.assertIsNone(req.metadata)

    def test_full_request(self) -> None:
        req = ImmutableRequest({
            "schema_version": "1",
            "destination": "/tmp/dest",
            "authority": {"granted_by": "issue-189", "scope": "workstream-1"},
            "source": {"repository": "https://github.com/owner/repo", "revision": "abc123"},
            "profile": "standard",
            "product": {"id": "my-product", "direction_material": ["/docs/overview.md"]},
            "deferred": ["metadata"],
            "metadata": {"requestor": "bot"},
        })
        self.assertEqual(req.schema_version, "1")
        self.assertEqual(req.destination, "/tmp/dest")
        self.assertEqual(req.authority, {"granted_by": "issue-189", "scope": "workstream-1"})
        self.assertEqual(req.source_repository, "https://github.com/owner/repo")
        self.assertEqual(req.source_revision, "abc123")
        self.assertEqual(req.profile, "standard")
        self.assertEqual(req.product_id, "my-product")
        self.assertEqual(req.product_direction_material, ["/docs/overview.md"])
        self.assertEqual(req.deferred, ["metadata"])
        self.assertEqual(req.metadata, {"requestor": "bot"})

    def test_immutability(self) -> None:
        auth = {"granted_by": "issue-189"}
        req = ImmutableRequest({
            "schema_version": "1",
            "destination": "/tmp/dest",
            "authority": auth,
        })
        auth_copy = req.authority
        auth_copy["extra"] = "added"
        self.assertEqual(req.authority, {"granted_by": "issue-189"})

    def test_equality(self) -> None:
        a = ImmutableRequest({"schema_version": "1", "destination": "/tmp/d", "authority": {"granted_by": "i"}})
        b = ImmutableRequest({"schema_version": "1", "destination": "/tmp/d", "authority": {"granted_by": "i"}})
        c = ImmutableRequest({"schema_version": "1", "destination": "/tmp/other", "authority": {"granted_by": "i"}})
        self.assertEqual(a, b)
        self.assertNotEqual(a, c)

    def test_hash_equality(self) -> None:
        a = ImmutableRequest({"schema_version": "1", "destination": "/tmp/d", "authority": {"granted_by": "i"}})
        b = ImmutableRequest({"schema_version": "1", "destination": "/tmp/d", "authority": {"granted_by": "i"}})
        self.assertEqual(hash(a), hash(b))

    def test_deferred_none_when_omitted(self) -> None:
        req = ImmutableRequest({"schema_version": "1", "destination": "/tmp/d", "authority": {"granted_by": "i"}})
        self.assertIsNone(req.deferred)

    def test_direction_material_none_when_omitted(self) -> None:
        req = ImmutableRequest({
            "schema_version": "1",
            "destination": "/tmp/d",
            "authority": {"granted_by": "i"},
            "product": {"id": "p"},
        })
        self.assertIsNone(req.product_direction_material)


if __name__ == "__main__":
    unittest.main()
