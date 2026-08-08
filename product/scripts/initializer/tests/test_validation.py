from __future__ import annotations

import base64
import json
import tempfile
import unittest
from pathlib import Path

from initializer.validation import (
    CONTRADICTORY_COMBINATION,
    EMPTY_AUTHORITY,
    EXCLUDED_BEHAVIOR,
    INVALID_STRUCTURE,
    MISSING_REQUIRED,
    ValidationError,
    load_request,
    validate_and_normalize,
    validate_request,
)


OBJECT_ID = "0123456789abcdef0123456789abcdef01234567"


def valid_request() -> dict[str, object]:
    return {
        "schema_version": "1",
        "destination": "./output",
        "authority": {"granted_by": "issue-273"},
        "source": {
            "repository": "source/../source",
            "revision": {"object_format": "sha1", "object_id": OBJECT_ID},
        },
        "product": {
            "id": "sample-product",
            "direction_material": ["docs/OVERVIEW.md"],
        },
    }


class ValidationTests(unittest.TestCase):
    def assert_category(self, raw: dict[str, object], category: str) -> None:
        result = validate_request(raw, "/work")
        self.assertFalse(result.is_valid)
        self.assertIn(category, [error.category for error in result.errors])

    def test_accepts_complete_request_and_optional_fields(self) -> None:
        raw = valid_request()
        raw["authority"] = {
            "granted_by": "issue-273",
            "type": "governing-issue",
            "scope": "request scope",
        }
        raw["profile"] = "standard"

        model = validate_and_normalize(raw, "/work").request

        self.assertEqual(model.profile, "standard")
        self.assertEqual(model.authority, raw["authority"])

    def test_all_root_and_nested_fields_are_strict(self) -> None:
        mutations = (
            ("root", lambda raw: raw.__setitem__("metadata", {})),
            ("authority", lambda raw: raw["authority"].__setitem__("granted", True)),
            ("source", lambda raw: raw["source"].__setitem__("remote", "origin")),
            ("revision", lambda raw: raw["source"]["revision"].__setitem__("name", "main")),
            ("product", lambda raw: raw["product"].__setitem__("display_name", "Sample")),
        )
        for label, mutate in mutations:
            with self.subTest(label=label):
                raw = valid_request()
                mutate(raw)
                self.assert_category(raw, INVALID_STRUCTURE)

    def test_every_required_field_is_enforced(self) -> None:
        paths = (
            ("schema_version",),
            ("destination",),
            ("authority",),
            ("source",),
            ("product",),
            ("authority", "granted_by"),
            ("source", "repository"),
            ("source", "revision"),
            ("source", "revision", "object_format"),
            ("source", "revision", "object_id"),
            ("product", "id"),
            ("product", "direction_material"),
        )
        for path in paths:
            with self.subTest(path=path):
                raw = valid_request()
                owner = raw
                for component in path[:-1]:
                    owner = owner[component]
                del owner[path[-1]]
                self.assert_category(raw, MISSING_REQUIRED)

    def test_rejection_categories_are_distinct(self) -> None:
        missing = valid_request()
        del missing["destination"]
        empty = valid_request()
        empty["authority"]["granted_by"] = " \t"
        invalid = valid_request()
        invalid["product"]["id"] = "Invalid_ID"
        contradictory = valid_request()
        contradictory["source"]["revision"]["object_id"] = "a" * 64
        excluded = valid_request()
        excluded["profile"] = "dry-run"

        cases = (
            (missing, MISSING_REQUIRED),
            (empty, EMPTY_AUTHORITY),
            (invalid, INVALID_STRUCTURE),
            (contradictory, CONTRADICTORY_COMBINATION),
            (excluded, EXCLUDED_BEHAVIOR),
        )
        for raw, expected in cases:
            with self.subTest(expected=expected):
                self.assert_category(raw, expected)

    def test_rejects_non_scalar_unicode_without_normalizing_values(self) -> None:
        raw = valid_request()
        raw["authority"]["scope"] = json.loads('"\\ud800"')
        self.assert_category(raw, INVALID_STRUCTURE)

        preserved = valid_request()
        preserved["authority"]["scope"] = "  scope  "
        model = validate_and_normalize(preserved, "/work").request
        self.assertEqual(model.authority["scope"], "  scope  ")

    def test_whitespace_only_authority_values_are_rejected(self) -> None:
        for field in ("granted_by", "type", "scope"):
            with self.subTest(field=field):
                raw = valid_request()
                raw["authority"][field] = " \n\t"
                self.assert_category(raw, EMPTY_AUTHORITY)

    def test_version_1_path_normalization_is_lexical_and_uses_explicit_cwd(self) -> None:
        raw = valid_request()
        raw["destination"] = "//alpha///./beta/../../gamma"
        raw["source"]["repository"] = "../source\\repo:literal"

        model = validate_and_normalize(raw, "/work/project").request

        self.assertEqual(model.destination, "/gamma")
        self.assertEqual(model.source_repository, "/work/source\\repo:literal")

    def test_path_validation_rejects_nul_remote_and_unsupported_cwd(self) -> None:
        nul = valid_request()
        nul["destination"] = "bad\x00path"
        self.assert_category(nul, INVALID_STRUCTURE)
        remote = valid_request()
        remote["source"]["repository"] = "https://example.invalid/repo"
        self.assert_category(remote, EXCLUDED_BEHAVIOR)
        scp_remote = valid_request()
        scp_remote["source"]["repository"] = "example.com:owner/repo.git"
        self.assert_category(scp_remote, EXCLUDED_BEHAVIOR)
        host_remote = valid_request()
        host_remote["source"]["repository"] = "git@server:repo.git"
        self.assert_category(host_remote, EXCLUDED_BEHAVIOR)
        result = validate_request(valid_request(), "relative/cwd")
        self.assertIn(EXCLUDED_BEHAVIOR, [error.category for error in result.errors])

    def test_direction_material_preserves_order_and_duplicates_and_is_intake_local(self) -> None:
        raw = valid_request()
        raw["product"]["direction_material"] = [
            "missing/first.md",
            "missing/first.md",
            "other/second.md",
        ]

        model = validate_and_normalize(raw, "/work").request

        self.assertEqual(
            model.product_direction_material,
            ("missing/first.md", "missing/first.md", "other/second.md"),
        )

    def test_direction_material_rejects_invalid_lexical_shapes(self) -> None:
        for item, category in (
            ("", EMPTY_AUTHORITY),
            ("/absolute.md", INVALID_STRUCTURE),
            ("../outside.md", INVALID_STRUCTURE),
            ("https://example.invalid/file", EXCLUDED_BEHAVIOR),
        ):
            with self.subTest(item=item):
                raw = valid_request()
                raw["product"]["direction_material"] = [item]
                self.assert_category(raw, category)

    def test_product_id_pattern_is_exact(self) -> None:
        for product_id in ("A-product", "a--product", "a-", "1-product", "prøduct"):
            with self.subTest(product_id=product_id):
                raw = valid_request()
                raw["product"]["id"] = product_id
                self.assert_category(raw, INVALID_STRUCTURE)

    def test_git_identity_rejects_abbreviated_uppercase_named_and_sha256(self) -> None:
        cases = (
            ({"object_format": "sha1", "object_id": "abc123"}, INVALID_STRUCTURE),
            ({"object_format": "sha1", "object_id": "A" * 40}, INVALID_STRUCTURE),
            ("main", EXCLUDED_BEHAVIOR),
            ({"object_format": "sha1", "object_id": "refs/heads/main"}, EXCLUDED_BEHAVIOR),
            (OBJECT_ID, INVALID_STRUCTURE),
            ({"object_format": "sha256", "object_id": "a" * 64}, EXCLUDED_BEHAVIOR),
        )
        for revision, category in cases:
            with self.subTest(revision=revision):
                raw = valid_request()
                raw["source"]["revision"] = revision
                self.assert_category(raw, category)

    def test_canonical_request_matches_normative_vector(self) -> None:
        raw = valid_request()
        raw["authority"] = {
            "granted_by": "issue-274",
            "scope": 'quote" slash\\ newline\n snowman \u2603',
        }
        raw["product"]["direction_material"] = [
            "docs/OVERVIEW.md",
            "docs/OVERVIEW.md",
        ]
        model = validate_and_normalize(raw, "/work").request
        expected = base64.b64decode(
            "eyJzY2hlbWFfdmVyc2lvbiI6IjEiLCJkZXN0aW5hdGlvbiI6Ii93b3JrL291dHB1dCIsImF1dGhvcml0eSI6eyJncmFudGVkX2J5IjoiaXNzdWUtMjc0Iiwic2NvcGUiOiJxdW90ZVwiIHNsYXNoXFwgbmV3bGluZVx1MDAwYSBzbm93bWFuIOKYgyJ9LCJzb3VyY2UiOnsicmVwb3NpdG9yeSI6Ii93b3JrL3NvdXJjZSIsInJldmlzaW9uIjp7Im9iamVjdF9mb3JtYXQiOiJzaGExIiwib2JqZWN0X2lkIjoiMDEyMzQ1Njc4OWFiY2RlZjAxMjM0NTY3ODlhYmNkZWYwMTIzNDU2NyJ9fSwicHJvZHVjdCI6eyJpZCI6InNhbXBsZS1wcm9kdWN0IiwiZGlyZWN0aW9uX21hdGVyaWFsIjpbImRvY3MvT1ZFUlZJRVcubWQiLCJkb2NzL09WRVJWSUVXLm1kIl19fQ=="
        )

        self.assertEqual(model.canonical_request_bytes, expected)
        self.assertEqual(
            model.request_fingerprint,
            "5bdf14415989c343b3220d7c016b2001843ae27ec675e2640184e33c82540ffe",
        )

    def test_load_request_requires_one_json_object(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "request.json"
            path.write_text("[]", encoding="utf-8")
            with self.assertRaises(ValidationError) as raised:
                load_request(path)
        self.assertEqual(raised.exception.category, INVALID_STRUCTURE)


if __name__ == "__main__":
    unittest.main()
