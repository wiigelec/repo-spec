from __future__ import annotations

import json
import unittest
from pathlib import Path

from initializer.inventory import (
    load_inventory,
    validate_inventory,
    validate_and_load_inventory,
    build_source_selection,
    resolve_source_selection_from_request,
    inventory_to_ordered_dict,
    InventoryError,
)
from initializer.models import SourceSelection, InventoryEntry, ClassifiedInventory, InitializerError


FIXTURES = Path(__file__).resolve().parent / "fixtures" / "inventory"


def _load_raw(name: str) -> dict:
    path = FIXTURES / name
    return json.loads(path.read_text())


class InventoryValidationTests(unittest.TestCase):
    def _assert_valid(self, fixture_name: str) -> None:
        raw = _load_raw(fixture_name)
        result = validate_inventory(raw)
        self.assertTrue(
            result.is_valid,
            msg=f"{fixture_name}: {result.errors}",
        )

    def _assert_invalid(self, fixture_name: str) -> None:
        raw = _load_raw(fixture_name)
        result = validate_inventory(raw)
        self.assertFalse(
            result.is_valid,
            msg=f"{fixture_name}: expected errors but got none",
        )

    def test_valid_minimal(self) -> None:
        self._assert_valid("valid-minimal.json")

    def test_valid_framework_vs_derived(self) -> None:
        self._assert_valid("valid-framework-vs-derived.json")

    def test_valid_profile_vs_adapter(self) -> None:
        self._assert_valid("valid-profile-vs-adapter.json")

    def test_valid_product_instance(self) -> None:
        self._assert_valid("valid-product-instance.json")

    def test_valid_excluded(self) -> None:
        self._assert_valid("valid-excluded.json")

    def test_invalid_duplicate_path(self) -> None:
        self._assert_invalid("invalid-duplicate-path.json")

    def test_invalid_overlapping_conflict(self) -> None:
        self._assert_invalid("invalid-overlapping-conflict.json")

    def test_invalid_missing_path(self) -> None:
        self._assert_invalid("invalid-missing-path.json")

    def test_invalid_missing_classification(self) -> None:
        self._assert_invalid("invalid-missing-classification.json")

    def test_invalid_unknown_top_field(self) -> None:
        self._assert_invalid("invalid-unknown-top-field.json")

    def test_invalid_unsupported_classification(self) -> None:
        self._assert_invalid("invalid-unsupported-classification.json")

    def test_invalid_absolute_path(self) -> None:
        self._assert_invalid("invalid-absolute-path.json")

    def test_invalid_parent_traversal(self) -> None:
        self._assert_invalid("invalid-parent-traversal.json")

    def test_invalid_derived_empty_sources(self) -> None:
        self._assert_invalid("invalid-derived-empty-sources.json")

    def test_invalid_unrecognized_profile(self) -> None:
        self._assert_invalid("invalid-unrecognized-profile.json")

    def test_product_as_framework_structural_validity(self) -> None:
        raw = _load_raw("invalid-product-as-framework.json")
        result = validate_inventory(raw)
        self.assertTrue(result.is_valid)
        classified = validate_and_load_inventory(raw)
        auth = classified.entries_by_classification("framework-authoritative")
        self.assertEqual(len(auth), 2)
        for entry in auth:
            self.assertTrue(entry.installable)


class InventoryLoadTests(unittest.TestCase):
    def test_minimal_loads_successfully(self) -> None:
        raw = _load_raw("valid-minimal.json")
        classified = validate_and_load_inventory(raw)
        self.assertIsInstance(classified, ClassifiedInventory)
        self.assertIn("framework-authoritative", classified.classifications)
        self.assertIn("framework-support", classified.classifications)
        self.assertIn("derived", classified.classifications)

    def test_classifications_are_distinguishable(self) -> None:
        raw = _load_raw("valid-framework-vs-derived.json")
        classified = validate_and_load_inventory(raw)

        authoritative = classified.entries_by_classification("framework-authoritative")
        derived = classified.entries_by_classification("derived")

        self.assertEqual(len(authoritative), 1)
        self.assertEqual(authoritative[0].path, "specs/repo/manifest.json")
        self.assertTrue(authoritative[0].authoritative)

        self.assertEqual(len(derived), 1)
        self.assertEqual(derived[0].path, "derived/specs/repo/manifest.md")
        self.assertFalse(derived[0].authoritative)

    def test_product_not_selected_as_framework(self) -> None:
        raw = _load_raw("valid-product-instance.json")
        classified = validate_and_load_inventory(raw)

        auth = classified.entries_by_classification("framework-authoritative")
        product = classified.entries_by_classification("product-instance")

        self.assertEqual(len(auth), 1)
        self.assertEqual(len(product), 2)

        for entry in auth:
            self.assertTrue(entry.installable)
        for entry in product:
            self.assertFalse(entry.installable)

    def test_excluded_stays_excluded(self) -> None:
        raw = _load_raw("valid-excluded.json")
        classified = validate_and_load_inventory(raw)

        excluded = classified.entries_by_classification("excluded")
        self.assertEqual(len(excluded), 1)
        self.assertEqual(excluded[0].path, "node_modules/")
        self.assertFalse(excluded[0].installable)
        self.assertIsNotNone(excluded[0].exclusion_rationale)


class InventoryDeterminismTests(unittest.TestCase):
    def test_equivalent_input_equivalent_output(self) -> None:
        raw = _load_raw("valid-minimal.json")
        a = validate_and_load_inventory(raw)
        b = validate_and_load_inventory(raw)
        self.assertEqual(a, b)

    def test_ordering_is_deterministic(self) -> None:
        raw = _load_raw("valid-minimal.json")
        a = validate_and_load_inventory(raw)
        b = validate_and_load_inventory(raw)

        a_entries = list(a.entries)
        b_entries = list(b.entries)
        self.assertEqual(a_entries, b_entries)
        for i in range(len(a_entries) - 1):
            self.assertLessEqual(
                (a_entries[i].classification, a_entries[i].path),
                (a_entries[i + 1].classification, a_entries[i + 1].path),
            )


class SourceSelectionTests(unittest.TestCase):
    def test_valid_explicit_source(self) -> None:
        sel = build_source_selection("https://github.com/owner/repo", "abc123")
        self.assertIsNotNone(sel)
        assert sel is not None
        self.assertEqual(sel.repository, "https://github.com/owner/repo")
        self.assertEqual(sel.revision, "abc123")

    def test_none_when_both_none(self) -> None:
        sel = build_source_selection(None, None)
        self.assertIsNone(sel)

    def test_revision_requires_repository(self) -> None:
        with self.assertRaises(InventoryError):
            resolve_source_selection_from_request(None, "abc123")

    def test_repository_requires_revision(self) -> None:
        with self.assertRaises(InventoryError):
            resolve_source_selection_from_request("https://github.com/owner/repo", None)

    def test_missing_both_raises(self) -> None:
        with self.assertRaises(InventoryError):
            resolve_source_selection_from_request(None, None)

    def test_empty_repository_rejected(self) -> None:
        with self.assertRaises(InitializerError):
            SourceSelection("", "abc123")

    def test_empty_revision_rejected(self) -> None:
        with self.assertRaises(InitializerError):
            SourceSelection("https://github.com/owner/repo", "")

    def test_source_selection_immutable(self) -> None:
        sel = SourceSelection("https://github.com/owner/repo", "abc123")
        with self.assertRaises(AttributeError):
            sel.repository = "other"  # type: ignore

    def test_selection_equality(self) -> None:
        a = SourceSelection("https://github.com/owner/repo", "abc123")
        b = SourceSelection("https://github.com/owner/repo", "abc123")
        c = SourceSelection("https://github.com/other/repo", "def456")
        self.assertEqual(a, b)
        self.assertNotEqual(a, c)

    def test_selection_hash(self) -> None:
        a = SourceSelection("https://github.com/owner/repo", "abc123")
        b = SourceSelection("https://github.com/owner/repo", "abc123")
        self.assertEqual(hash(a), hash(b))

    def test_no_silent_default_branch(self) -> None:
        with self.assertRaises(InventoryError):
            resolve_source_selection_from_request(None, None)


class InventoryOutputTests(unittest.TestCase):
    def test_output_contains_classifications(self) -> None:
        raw = _load_raw("valid-minimal.json")
        classified = validate_and_load_inventory(raw)
        output = inventory_to_ordered_dict(classified, None)
        self.assertIn("classifications", output)
        self.assertIn("framework-authoritative", output["classifications"])

    def test_output_contains_source_selection(self) -> None:
        raw = _load_raw("valid-minimal.json")
        classified = validate_and_load_inventory(raw)
        sel = SourceSelection("https://github.com/owner/repo", "abc123")
        output = inventory_to_ordered_dict(classified, sel)
        self.assertIsNotNone(output["source_selection"])
        self.assertEqual(output["source_selection"]["repository"], "https://github.com/owner/repo")
        self.assertEqual(output["source_selection"]["revision"], "abc123")

    def test_output_ordering_deterministic(self) -> None:
        raw = _load_raw("valid-minimal.json")
        classified = validate_and_load_inventory(raw)
        a = inventory_to_ordered_dict(classified, None)
        b = inventory_to_ordered_dict(classified, None)
        self.assertEqual(a, b)

    def test_output_source_none_when_no_selection(self) -> None:
        raw = _load_raw("valid-minimal.json")
        classified = validate_and_load_inventory(raw)
        output = inventory_to_ordered_dict(classified, None)
        self.assertIsNone(output["source_selection"])


class InventoryEntryTests(unittest.TestCase):
    def test_entry_equality(self) -> None:
        a = InventoryEntry({
            "path": "specs/repo/",
            "classification": "framework-authoritative",
            "authoritative": True,
            "installable": True,
        })
        b = InventoryEntry({
            "path": "specs/repo/",
            "classification": "framework-authoritative",
            "authoritative": True,
            "installable": True,
        })
        c = InventoryEntry({
            "path": "specs/repo/",
            "classification": "framework-support",
            "authoritative": False,
            "installable": True,
        })
        self.assertEqual(a, b)
        self.assertNotEqual(a, c)

    def test_entry_hash(self) -> None:
        a = InventoryEntry({
            "path": "specs/repo/",
            "classification": "framework-authoritative",
            "authoritative": True,
            "installable": True,
        })
        b = InventoryEntry({
            "path": "specs/repo/",
            "classification": "framework-authoritative",
            "authoritative": True,
            "installable": True,
        })
        self.assertEqual(hash(a), hash(b))


class SafetyTests(unittest.TestCase):
    def test_invalid_inventory_no_successful_load(self) -> None:
        raw = _load_raw("invalid-duplicate-path.json")
        with self.assertRaises(InventoryError):
            validate_and_load_inventory(raw)

    def test_invalid_source_no_successful_selection(self) -> None:
        with self.assertRaises(InventoryError):
            resolve_source_selection_from_request(None, None)


if __name__ == "__main__":
    unittest.main()
